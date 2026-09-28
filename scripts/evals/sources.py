"""Load and validate replay case sources: plugins/<plugin>/replays/<case>/case.yaml.

A source is Claude Code's case.yaml plus `context.messages` (the turns before
execution.prompt) and a `skill` key on the assistant turn that ran after the
skill loaded.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, NoReturn

import yaml

from evals.transcript import Message, SkillLoad

BASELINE_SUFFIX = "-baseline"
STUB_NAME = "replay-baseline-stub"
_TOP_KEYS = {"schema_version", "name", "description", "tags", "context", "execution", "runs", "graders"}
_META_KEYS = ("schema_version", "description", "tags")
# Which key a grader file's body fills, per type; evals/lint.py reads bodies the same way.
_BODY_KEYS = {"llm": "criteria", "baseline": "criteria", "regex": "pattern"}

# `fail` never returns, so calling it lets mypy narrow types in the branch that follows it.
Fail = Callable[[str], NoReturn]


class SourceError(Exception):
    """A replay source that cannot produce a faithful case pair."""


@dataclass(frozen=True)
class Source:
    path: Path
    name: str
    messages: tuple[Message, ...]
    execution: dict[str, Any]
    runs: int | None
    graders: tuple[dict[str, Any], ...]
    meta: dict[str, Any]

    @property
    def baseline_name(self) -> str:
        return self.name + BASELINE_SUFFIX

    @property
    def skill(self) -> SkillLoad:
        return next(m.skill for m in self.messages if m.skill)

    @property
    def with_only(self) -> frozenset[str]:
        return frozenset(g["name"] for g in self.graders if g.get("arm") == "with-only")


def split_frontmatter(text: str) -> tuple[dict[str, Any], str] | None:
    """(frontmatter, body) for a `---`-fenced file, or None when there is no fence."""
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 3)
    if end == -1:
        return None
    return yaml.safe_load(text[4:end]) or {}, text[end + 5:]


def load_sources(plugin_dir: Path) -> list[Source]:
    return [load_source(p) for p in sorted(plugin_dir.glob("replays/*/case.yaml"))]


def load_source(path: Path) -> Source:
    def fail(message: str) -> NoReturn:
        raise SourceError(f"{path}: {message}")

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        fail("must be a YAML mapping")
    unknown = set(data) - _TOP_KEYS
    if unknown:
        fail(f"unsupported keys {sorted(unknown)}; the generator writes plugins: and context.history_file itself")
    name = data.get("name")
    if not isinstance(name, str) or not name:
        fail("name must be a non-empty string")
    if name.endswith(BASELINE_SUFFIX):
        fail(f"name must not end with {BASELINE_SUFFIX!r}; the generator adds it to the baseline")
    context = data.get("context")
    if not isinstance(context, dict) or set(context) != {"messages"}:
        fail("context must hold exactly one key, messages")
    messages = _messages(context["messages"], fail)
    execution = data.get("execution")
    if not isinstance(execution, dict) or not isinstance(execution.get("prompt"), str) \
            or not execution["prompt"].strip():
        fail("execution.prompt must be the live next user turn")
    # evals/lint.py enforces this for every other case, but it never sees the generated replay cases.
    if not isinstance(execution.get("model"), str) or not execution["model"].strip():
        fail("execution.model must pin a model; an unpinned case runs on whatever the CLI's default alias is")
    graders = _graders(data.get("graders") or [], path.parent / "graders", fail)
    meta = {k: data[k] for k in _META_KEYS if k in data}
    return Source(path, name, messages, dict(execution), data.get("runs"), graders, meta)


def _messages(raw: Any, fail: Fail) -> tuple[Message, ...]:
    if not isinstance(raw, list) or not raw:
        fail("context.messages must be a non-empty list")
    messages = []
    for i, item in enumerate(raw):
        where = f"context.messages[{i}]"
        expected = "user" if i % 2 == 0 else "assistant"
        if not isinstance(item, dict) or set(item) - {"role", "content", "skill"}:
            fail(f"{where} takes role, content and (on one assistant turn) skill")
        if item.get("role") != expected:
            fail(f"{where} must be role {expected}: turns alternate, starting with user")
        content = item.get("content")
        if not isinstance(content, str) or not content.strip():
            fail(f"{where}.content must be non-empty text")
        skill = None
        if "skill" in item:
            if expected != "assistant":
                fail(f"{where}: skill goes on the assistant turn that ran after the skill loaded")
            raw_skill = item["skill"]
            if not isinstance(raw_skill, dict) or set(raw_skill) != {"name", "args"} \
                    or not all(isinstance(v, str) and v for v in raw_skill.values()):
                fail(f"{where}.skill needs string name and args")
            skill = SkillLoad(raw_skill["name"], raw_skill["args"])
        # A YAML block scalar ends in a newline that the real turn did not have.
        messages.append(Message(expected, content.rstrip("\n"), skill))
    if messages[-1].role != "assistant":
        fail("context.messages must end with an assistant turn; the next user turn is execution.prompt")
    loads = sum(1 for m in messages if m.skill)
    if loads != 1:
        fail(f"exactly one assistant turn must carry skill (found {loads})")
    return tuple(messages)


def _graders(inline: Any, graders_dir: Path, fail: Fail) -> tuple[dict[str, Any], ...]:
    if not isinstance(inline, list):
        fail("graders must be a list")
    graders = [dict(g) for g in inline if isinstance(g, dict)]
    if len(graders) != len(inline):
        fail("every inline grader must be a mapping")
    if graders_dir.is_dir():
        graders += [_grader_file(p, fail) for p in sorted(graders_dir.glob("*.md"))]
    if not graders:
        fail("needs at least one grader")
    names = set()
    for grader in graders:
        name = grader.get("name")
        if not isinstance(name, str) or not isinstance(grader.get("type"), str):
            fail(f"every grader needs a name and a type: {grader!r}")
        if name in names:
            fail(f"duplicate grader name {name!r}")
        names.add(name)
        if _checks_for_skill_call(grader):
            fail(f"grader {name!r} checks for a Skill call; a replay never calls Skill "
                 "because the load is already in the history, so it could never pass")
    if all(g.get("arm") == "with-only" for g in graders):
        fail("the baseline needs at least one grader without arm: with-only")
    return tuple(graders)


def _grader_file(path: Path, fail: Fail) -> dict[str, Any]:
    parsed = split_frontmatter(path.read_text(encoding="utf-8"))
    if parsed is None:
        fail(f"graders/{path.name} must start with --- frontmatter")
    front, body = parsed
    grader = {"name": path.stem, **front}
    if body.strip():
        grader_type = grader.get("type")
        key = _BODY_KEYS.get(grader_type) if isinstance(grader_type, str) else None
        if key is None:
            fail(f"graders/{path.name}: a {grader.get('type')} grader takes no body")
        if key in grader:
            fail(f"graders/{path.name}: {key} is given twice, as a key and as the body")
        grader[key] = body.strip() + "\n" if key == "criteria" else body.strip()
    return grader


def _checks_for_skill_call(grader: dict[str, Any]) -> bool:
    if grader.get("type") != "tool_used":
        return False
    tool = grader.get("tool")
    tool_name = tool.get("tool") if isinstance(tool, dict) else tool
    return tool_name == "Skill" and (grader.get("min") is None or grader["min"] >= 1)
