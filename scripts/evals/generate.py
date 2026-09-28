"""Write every replay source's case pair under <plugin>/evals/replay/.

replay-eval runs this before every eval run. --check validates every
source into a temp dir and leaves the plugin untouched (the PR gate).
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

import yaml

from evals.sources import STUB_NAME, Source, SourceError, load_sources, split_frontmatter
from evals.transcript import build_records, write_jsonl

REPO = Path(__file__).resolve().parents[2]
REPLAY_DIR = "replay"
_NOT_CASES = {REPLAY_DIR, "results", "mocks"}
_STUB_MANIFEST = {
    "name": STUB_NAME,
    "version": "0.0.0",
    "description": "No skills. Stands in for the plugin under test in a replay baseline.",
}


def existing_case_names(evals_dir: Path) -> set[str]:
    names = set()
    for case_file in [*evals_dir.rglob("case.yaml"), *evals_dir.rglob("prompt.md")]:
        if _NOT_CASES & set(case_file.relative_to(evals_dir).parts[:-1]):
            continue
        text = case_file.read_text(encoding="utf-8")
        if case_file.name == "case.yaml":
            front = yaml.safe_load(text) or {}
        else:
            front = (split_frontmatter(text) or ({}, ""))[0]
        names.add(front.get("name") or case_file.parent.name)
    return names


def case_dict(source: Source, *, baseline: bool) -> dict[str, Any]:
    case = {
        **source.meta,
        "name": source.baseline_name if baseline else source.name,
        "context": {"history_file": "history.jsonl"},
        "execution": source.execution,
    }
    if source.runs is not None:
        case["runs"] = source.runs
    case["graders"] = [g for g in source.graders if not (baseline and g.get("arm") == "with-only")]
    if baseline:
        case["plugins"] = ["stub"]
    return case


def _skill_file(plugin_dir: Path, source: Source) -> Path:
    plugin = json.loads((plugin_dir / ".claude-plugin" / "plugin.json").read_text())["name"]
    prefix, _, skill = source.skill.name.partition(":")
    if prefix != plugin or not skill:
        raise SourceError(f"{source.path}: {source.skill.name!r} is not a skill of plugin {plugin!r}")
    path = plugin_dir / "skills" / skill / "SKILL.md"
    if not path.is_file():
        raise SourceError(f"{source.path}: {path} not found")
    return path


def _check_names(sources: list[Source], existing: set[str]) -> None:
    seen: set[str] = set()
    for source in sources:
        for name in (source.name, source.baseline_name):
            if name in existing:
                raise SourceError(f"{source.path}: case name {name!r} is already used by a case under evals/")
            if name in seen:
                raise SourceError(f"{source.path}: case name {name!r} is generated twice")
            seen.add(name)


def _write_pair(source: Source, skill_path: Path, out_root: Path) -> None:
    skill_md = skill_path.read_text(encoding="utf-8")
    skill_dir = str(skill_path.parent.resolve())
    for baseline in (False, True):
        case = case_dict(source, baseline=baseline)
        case_dir = out_root / case["name"]
        case_dir.mkdir(parents=True)
        (case_dir / "case.yaml").write_text(json.dumps(case, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        write_jsonl(case_dir / "history.jsonl",
                    build_records(case["name"], source.messages, cwd=str(case_dir.resolve()),
                                  skill_md=skill_md, skill_dir=skill_dir, with_skill=not baseline))
    stub = out_root / source.baseline_name / "stub" / ".claude-plugin"
    stub.mkdir(parents=True)
    (stub / "plugin.json").write_text(json.dumps(_STUB_MANIFEST, indent=2) + "\n")


def generate(plugin_dir: Path, out_root: Path | None = None) -> list[Source]:
    """Validate every source, then replace out_root with freshly generated pairs."""
    plugin_dir = plugin_dir.resolve()
    evals_dir = plugin_dir / "evals"
    out_root = out_root or evals_dir / REPLAY_DIR
    sources = load_sources(plugin_dir)
    _check_names(sources, existing_case_names(evals_dir))
    skill_paths = [_skill_file(plugin_dir, s) for s in sources]
    # Validation is complete before the wipe, so a broken source leaves the last good set in place.
    if out_root.exists():
        shutil.rmtree(out_root)
    out_root.mkdir(parents=True)
    for source, skill_path in zip(sources, skill_paths):
        _write_pair(source, skill_path, out_root)
    return sources


def _plugins_with_replays() -> list[Path]:
    return sorted({p.parents[2] for p in REPO.glob("plugins/*/replays/*/case.yaml")})


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("plugins", nargs="*", type=Path, help="plugin dirs (default: every plugin with replays/)")
    parser.add_argument("--check", action="store_true", help="validate into a temp dir; leave the plugin untouched")
    args = parser.parse_args(argv)
    try:
        for plugin in args.plugins or _plugins_with_replays():
            if args.check:
                with tempfile.TemporaryDirectory() as tmp:
                    sources = generate(plugin, Path(tmp) / REPLAY_DIR)
            else:
                sources = generate(plugin)
            print(f"{plugin}: {len(sources)} replay pair(s) {'checked' if args.check else 'written'}")
    except SourceError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
