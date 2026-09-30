"""Regenerate replay cases, run `claude plugin eval` once, and print one Δ table.

Usage: uv run replay-eval <plugin dir> --model <model id> [claude plugin eval options, except --ablation]
"""

from __future__ import annotations

import fnmatch
import json
import os
import subprocess
import sys
from pathlib import Path

from evals.eval_types import EvalResult
from evals.generate import REPLAY_DIR, generate
from evals.pairing import pair_results, render_markdown, results_problems
from evals.sources import BASELINE_SUFFIX, SourceError, load_sources

EXIT_RESULTS = 3
EXIT_REFUSED = 4
DEFAULT_JUDGE = "claude-opus-5-5"


class UsageError(Exception):
    pass


def _take_flag(argv: list[str], flag: str) -> tuple[str | None, list[str]]:
    """Remove `flag VALUE` or `flag=VALUE` from argv. Returns (value, remaining argv)."""
    value, rest, i = None, [], 0
    while i < len(argv):
        arg = argv[i]
        if arg == flag:
            if i + 1 >= len(argv):
                raise UsageError(f"{flag} needs a value")
            value, i = argv[i + 1], i + 2
        elif arg.startswith(flag + "="):
            value, i = arg[len(flag) + 1:], i + 1
        else:
            rest.append(arg)
            i += 1
    return value, rest


def _refuse_ablation(argv: list[str]) -> None:
    if any(a == "--ablation" or a.startswith("--ablation=") for a in argv):
        raise UsageError("--ablation is refused: replay cases must run one arm each, which only the default "
                         "(auto) gives; with-without adds an arm that resumes the skill-bearing transcript")


def _require_model(argv: list[str]) -> None:
    model, _ = _take_flag(argv, "--model")
    if not model:
        raise UsageError("--model is required: give the model under test as a full model ID")


def _with_default_judge(argv: list[str]) -> list[str]:
    judge, _ = _take_flag(argv, "--judge-model")
    return argv if judge else [*argv, "--judge-model", DEFAULT_JUDGE]


def _split_target(argv: list[str]) -> tuple[Path, list[str]]:
    if not argv or argv[0].startswith("-") or not Path(argv[0]).is_dir():
        raise UsageError("the first argument must be the plugin directory (a path, not a plugin name: "
                         "a name switches history cases to two arms)")
    return Path(argv[0]).resolve(), argv[1:]


def _refuse_split_pair(argv: list[str], replay_names: set[str]) -> None:
    pattern, _ = _take_flag(argv, "--case")
    if pattern is None:
        return
    for name in sorted(replay_names):
        baseline = name + BASELINE_SUFFIX
        if fnmatch.fnmatchcase(name, pattern) != fnmatch.fnmatchcase(baseline, pattern):
            raise UsageError(f"--case {pattern!r} matches only one of {name} and {baseline}; "
                             f"a replay case needs its baseline for a Δ (try {name + '*'!r})")


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        _refuse_ablation(argv)
        target, rest = _split_target(argv)
        _require_model(rest)
        rest = _with_default_judge(rest)
        json_arg, rest = _take_flag(rest, "--json")
        sources = load_sources(target)
        replay_names = {s.name for s in sources}
        _refuse_split_pair(rest, replay_names)
        generate(target)
    except (UsageError, SourceError) as error:
        print(f"error: {error}", file=sys.stderr)
        return EXIT_REFUSED

    json_path = Path(json_arg) if json_arg else target / "evals" / REPLAY_DIR / "last-result.json"
    # A result left from an earlier run must never be reported as this run's.
    json_path.unlink(missing_ok=True)
    command = [os.environ.get("CLAUDE_BIN", "claude"), "plugin", "eval", str(target), *rest, "--json", str(json_path)]
    code = subprocess.run(command).returncode
    if not json_path.is_file():
        print(f"error: no results at {json_path}", file=sys.stderr)
        return code or 1

    result: EvalResult = json.loads(json_path.read_text())
    table = render_markdown(pair_results(result, {s.name: s.with_only for s in sources}))
    (json_path.parent / "delta.md").write_text(table)
    print(table, end="")
    problems = results_problems(result, replay_names)
    for problem in problems:
        print(f"error: {problem}", file=sys.stderr)
    return EXIT_RESULTS if problems else code
