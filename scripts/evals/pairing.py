"""Pair each replay case with its baseline and compute Δ from `claude plugin eval --json` output."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from statistics import mean

from evals.eval_types import CaseResult, EvalResult, RunResult
from evals.sources import BASELINE_SUFFIX, STUB_NAME


@dataclass
class Row:
    case: str
    kind: str  # "ablation": the CLI's own Δ; "replay": paired Δ; "single": no Δ
    score: float | None
    baseline: float | None
    delta: float | None
    runs: int
    cost_usd: float
    indicators: dict[str, str] = field(default_factory=dict)
    note: str = ""


def run_score(run: RunResult, exclude: frozenset[str] = frozenset()) -> float | None:
    """The CLI's run score (weighted share of scored graders that passed), leaving out `exclude`.

    None when no grader is left to score: the CLI's own score would then come from the excluded graders.
    """
    if run.get("error"):
        return run["score"]
    graders = [g for g in run.get("graders", []) if g.get("scored", True) and g["name"] not in exclude]
    total = sum(g["weight"] for g in graders)
    if total == 0:
        return None
    return sum(g["weight"] for g in graders if g["passed"]) / total


def _runs(case: CaseResult | None) -> list[RunResult]:
    return case.get("arms", {}).get("with", []) if case else []


def _cost(case: CaseResult | None) -> float:
    # A run's costUsd already includes its judge calls; judgeCostUsd is a breakdown, not an extra.
    if case is None:
        return 0
    return sum(r.get("costUsd", 0) for runs in case.get("arms", {}).values() for r in runs)


def _mean_score(runs: list[RunResult], exclude: frozenset[str] = frozenset()) -> float | None:
    scores = [s for s in (run_score(r, exclude) for r in runs) if s is not None]
    return mean(scores) if scores else None


def _unscorable(runs: list[RunResult], exclude: frozenset[str] = frozenset()) -> int:
    return sum(1 for r in runs if run_score(r, exclude) is None)


def _notes(*cases: CaseResult | None) -> list[str]:
    runs = [r for c in cases for r in _runs(c)]
    notes = []
    if not runs:
        notes.append("no runs")
    errored = sum(1 for r in runs if r.get("error"))
    if errored:
        notes.append(f"{errored} run{'s' if errored > 1 else ''} errored")
    if any(r.get("skippedPaidGraders") for r in runs):
        notes.append("paid graders skipped")
    return notes


def _passes(runs: list[RunResult], grader_name: str) -> int:
    return sum(1 for r in runs if any(g["name"] == grader_name and g["passed"] for g in r.get("graders", [])))


def pair_results(result: EvalResult, with_only: dict[str, frozenset[str]]) -> list[Row]:
    cases = {c["name"]: c for c in result["cases"]}
    # A baseline stands in for its replay case, so a pair missing its replay side still gets a row.
    names = dict.fromkeys(
        n[: -len(BASELINE_SUFFIX)] if n.endswith(BASELINE_SUFFIX) and n[: -len(BASELINE_SUFFIX)] in with_only else n
        for n in cases)
    rows = []
    for name in names:
        case = cases.get(name)
        runs = _runs(case)
        if name in with_only:
            base = cases.get(name + BASELINE_SUFFIX)
            base_runs = _runs(base)
            score = _mean_score(runs, with_only[name])
            baseline = _mean_score(base_runs)
            if case is None:
                side_notes = ["replay missing"]
            elif base is None:
                side_notes = ["baseline missing"]
            elif runs and not base_runs:
                side_notes = ["baseline: no runs"]
            elif base_runs and not runs:
                side_notes = ["replay: no runs"]
            else:
                side_notes = []
            unscorable = _unscorable(runs, with_only[name]) + _unscorable(base_runs)
            if unscorable:
                side_notes.append(f"{unscorable} run{'s' if unscorable > 1 else ''} with no comparable graders")
            notes = side_notes + _notes(case, base)
            rows.append(Row(
                name, "replay", score, baseline,
                None if score is None or baseline is None else score - baseline,
                len(runs), _cost(case) + _cost(base),
                {g: f"{_passes(runs, g)}/{len(runs)}" for g in sorted(with_only[name])},
                "; ".join(notes)))
        else:
            assert case is not None  # `name` came from `cases`, so only the with_only branch sees a missing case
            aggregates = case.get("aggregates", {})
            delta = aggregates.get("delta")
            rows.append(Row(
                name, "ablation" if delta is not None else "single",
                aggregates.get("score") if runs else None, aggregates.get("scoreWithout"), delta,
                len(runs), _cost(case), note="; ".join(_notes(case))))
    return rows


def loaded_plugins(trace: Path) -> list[str]:
    """Plugins other than built-ins that the child reported loading in its init event."""
    for line in trace.read_text(encoding="utf-8").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "system" and event.get("subtype") == "init":
            return [p["name"] for p in event.get("plugins", [])
                    if not str(p.get("source", "")).endswith("@builtin")]
    return []


def results_problems(result: EvalResult, replay_names: set[str]) -> list[str]:
    """Ways a finished run broke the one-arm, stub-only assumptions the paired Δ rests on."""
    problems = []
    for case in result["cases"]:
        name = case["name"]
        is_baseline = name.endswith(BASELINE_SUFFIX) and name[: -len(BASELINE_SUFFIX)] in replay_names
        if name not in replay_names and not is_baseline:
            continue
        arms = sorted(case.get("arms", {}))
        if arms != ["with"]:
            problems.append(f"{name}: ran arms {arms}; a replay case must run only 'with' "
                            "(was --ablation passed, or a plugin name given as the target?)")
        if not is_baseline:
            continue
        for run in _runs(case):
            trace = run.get("tracePath")
            if trace and Path(trace).is_file():
                extra = [p for p in loaded_plugins(Path(trace)) if p != STUB_NAME]
                if extra:
                    problems.append(f"{name}: a baseline run loaded {extra}; it must load only {STUB_NAME}")
    return problems


def _number(value: float | None) -> str:
    return "—" if value is None else f"{value:.2f}"


def _signed(value: float | None) -> str:
    return "—" if value is None else f"{value:+.2f}"


def render_markdown(rows: list[Row]) -> str:
    lines = ["| case | kind | with | baseline | Δ | runs | cost | with-only indicators | note |",
             "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |"]
    for r in rows:
        indicators = ", ".join(f"{name} {count}" for name, count in r.indicators.items())
        lines.append(f"| {r.case} | {r.kind} | {_number(r.score)} | {_number(r.baseline)} | {_signed(r.delta)} "
                     f"| {r.runs} | ${r.cost_usd:.2f} | {indicators} | {r.note} |")
    return "\n".join(lines) + "\n"
