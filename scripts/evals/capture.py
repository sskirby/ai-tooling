"""Capture the model's reply to the last user turn of a capture file, through the eval sandbox.

Usage: uv run replay-capture <plugin dir> <capture.yaml>

The first turn runs with no history, so the skill loads naturally; later turns
resume a with-skill transcript of the turns so far. The sandbox keeps the
operator's own CLAUDE.md and settings out of the captured replies.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import yaml

from evals.transcript import MODEL, Message, SkillLoad, build_records, write_jsonl

CAPTURE_DIR = "replay-capture"
CASE_NAME = "capture-turn"
ATTEMPTS = 3


class _BlockDumper(yaml.SafeDumper):
    pass


def _str(dumper: yaml.SafeDumper, value: str) -> yaml.ScalarNode:
    return dumper.represent_scalar("tag:yaml.org,2002:str", value, style="|" if "\n" in value else None)


_BlockDumper.add_representer(str, _str)


def dump_yaml(data: dict[str, Any]) -> str:
    return yaml.dump(data, Dumper=_BlockDumper, sort_keys=False, allow_unicode=True, width=100)


def _assistant_events(lines: list[str]) -> Iterator[list[dict[str, Any]]]:
    for line in lines:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "assistant":
            yield event["message"].get("content", [])


def reply_from_trace(lines: list[str]) -> str:
    texts: list[str] = []
    for blocks in _assistant_events(lines):
        if any(b.get("type") == "tool_use" for b in blocks):
            texts = []
        texts += [b["text"] for b in blocks if b.get("type") == "text"]
    return "\n\n".join(texts)


def skill_args_from_trace(lines: list[str], skill: str) -> str | None:
    for blocks in _assistant_events(lines):
        for b in blocks:
            if b.get("type") == "tool_use" and b.get("name") == "Skill" and b["input"].get("skill") == skill:
                return str(b["input"].get("args", ""))
    return None


def _messages(raw: list[dict[str, Any]]) -> list[Message]:
    messages = []
    for item in raw:
        skill = item.get("skill")
        messages.append(Message(item["role"], item["content"].rstrip("\n"),
                                SkillLoad(skill["name"], skill["args"]) if skill else None))
    return messages


def _run_turn(plugin: Path, capture: dict[str, Any]) -> list[str]:
    """Run one child for the capture file's last user turn; return its trace lines."""
    case_dir = plugin / CAPTURE_DIR / CASE_NAME
    shutil.rmtree(plugin / CAPTURE_DIR, ignore_errors=True)
    case_dir.mkdir(parents=True)
    prior, prompt = capture["messages"][:-1], capture["messages"][-1]["content"]
    case: dict[str, Any] = {
        "schema_version": "1.1",
        "name": CASE_NAME,
        "execution": {"model": capture.get("model", MODEL), "prompt": prompt, "max_turns": 6,
                      "timeout_seconds": 300, "allowed_tools": ["Skill"]},
        "runs": 1,
        "graders": [{"name": "replied", "type": "regex", "pattern": "\\S"}],
    }
    if prior:
        skill_path = plugin / "skills" / capture["skill"].partition(":")[2] / "SKILL.md"
        records = build_records(CASE_NAME, _messages(prior), cwd=str(case_dir.resolve()),
                                skill_md=skill_path.read_text(encoding="utf-8"),
                                skill_dir=str(skill_path.parent.resolve()), with_skill=True)
        write_jsonl(case_dir / "history.jsonl", records)
        case["context"] = {"history_file": "history.jsonl"}
    (case_dir / "case.yaml").write_text(json.dumps(case, indent=2, ensure_ascii=False) + "\n")
    result_path = plugin / CAPTURE_DIR / "result.json"
    subprocess.run([os.environ.get("CLAUDE_BIN", "claude"), "plugin", "eval", str(plugin),
                    "--eval-dir", CAPTURE_DIR, "--ablation", "none", "--runs", "1", "--trust-plugin",
                    "--no-publish", "--keep-temp", "--max-cost-usd", "1", "--json", str(result_path)], check=False)
    run = read_run(result_path)
    return Path(run["tracePath"]).read_text(encoding="utf-8").splitlines()


def read_run(result_path: Path) -> dict[str, Any]:
    """The one run a capture child produced, or RuntimeError when it did not produce a usable one."""
    if not result_path.is_file():
        raise RuntimeError(f"capture run wrote no result at {result_path}; see the eval output above")
    run: dict[str, Any] = json.loads(result_path.read_text())["cases"][0]["arms"]["with"][0]
    if run.get("error") or not run.get("tracePath"):
        raise RuntimeError(f"capture run failed: error={run.get('error')!r} tracePath={run.get('tracePath')!r}")
    return run


def main(argv: list[str] | None = None) -> int:
    plugin_arg, capture_arg = (sys.argv[1:] if argv is None else argv)
    plugin, capture_path = Path(plugin_arg).resolve(), Path(capture_arg)
    capture = yaml.safe_load(capture_path.read_text(encoding="utf-8"))
    messages = capture["messages"]
    if not messages or messages[-1]["role"] != "user":
        print("error: messages must end with the user turn to capture a reply to", file=sys.stderr)
        return 1
    first_turn = len(messages) == 1
    for attempt in range(1, ATTEMPTS + 1):
        lines = _run_turn(plugin, capture)
        args = skill_args_from_trace(lines, capture["skill"]) if first_turn else None
        if not first_turn or args is not None:
            break
        print(f"attempt {attempt}: the skill did not load; retrying", file=sys.stderr)
    else:
        print(f"error: the skill did not load in {ATTEMPTS} attempts", file=sys.stderr)
        return 1
    reply: dict[str, Any] = {"role": "assistant"}
    if first_turn:
        reply["skill"] = {"name": capture["skill"], "args": args}
    reply["content"] = reply_from_trace(lines)
    messages.append(reply)
    capture_path.write_text(dump_yaml(capture), encoding="utf-8")
    print(reply["content"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
