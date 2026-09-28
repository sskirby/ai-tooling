"""Build the session-transcript records a replayed eval case resumes from.

`claude plugin eval` runs a case with `context.history_file` as
`claude -p <prompt> --resume <file>`, so the file must read as a real saved
session. Record shapes are copied from a natural-load session saved by CLI
2.1.283; transcripts with these shapes resumed in every spike run.
"""

from __future__ import annotations

import json
import re
import uuid
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

# A transcript record's shape varies by record type (user/assistant/tool-result/last-prompt);
# TypedDicts per shape would just re-describe the CLI's own session format field for field.
Record = dict[str, Any]

CLI_VERSION = "2.1.283"
MODEL = "claude-opus-5-5"

# A fixed namespace and clock make an unchanged source regenerate byte-identical files.
_NAMESPACE = uuid.UUID("6f1c2b3e-9a4d-4e57-8b21-5d0c7e9f1a22")
_BASE_TIME = datetime(2026, 1, 1, tzinfo=timezone.utc)
_FRONTMATTER = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)


@dataclass(frozen=True)
class SkillLoad:
    name: str  # "<plugin>:<skill>", as the Skill tool takes it
    args: str


@dataclass(frozen=True)
class Message:
    role: str  # "user" or "assistant"
    content: str
    skill: SkillLoad | None = None  # set on the assistant turn that ran after the skill loaded


def skill_message_text(skill_md: str, skill_dir: str, args: str) -> str:
    """The text Claude Code injects when the Skill tool loads a skill.

    Pinned byte-for-byte by test/evals/fixtures/natural-skill-load.json.
    """
    text = skill_md.replace("\r\n", "\n")
    match = _FRONTMATTER.match(text)
    body = text[match.end():] if match else text
    return f"Base directory for this skill: {skill_dir}\n{body}\n\nARGUMENTS: {args}"


class _Builder:
    def __init__(self, seed: str, cwd: str) -> None:
        self._seed = seed
        self._cwd = cwd
        self.session_id = self._uuid("session")
        self._prompt_id = self._uuid("prompt")
        self.records: list[Record] = []
        self._parent: str | None = None

    def _uuid(self, label: str) -> str:
        return str(uuid.uuid5(_NAMESPACE, f"{self._seed}:{label}"))

    def _hex(self, label: str, length: int) -> str:
        return uuid.uuid5(_NAMESPACE, f"{self._seed}:{label}").hex[:length]

    def _append(self, fields: Record) -> str:
        n = len(self.records)
        record_uuid = self._uuid(f"record-{n}")
        self.records.append({
            "parentUuid": self._parent,
            "isSidechain": False,
            "userType": "external",
            "entrypoint": "sdk-cli",
            "cwd": self._cwd,
            "sessionId": self.session_id,
            "version": CLI_VERSION,
            "gitBranch": "HEAD",
            **fields,
            "uuid": record_uuid,
            "timestamp": (_BASE_TIME + timedelta(seconds=n)).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        })
        self._parent = record_uuid
        return record_uuid

    def _assistant(self, content: list[Record], stop_reason: str) -> Record:
        n = len(self.records)
        return {
            "message": {
                "model": MODEL,
                "id": "msg_" + self._hex(f"msg-{n}", 24),
                "type": "message",
                "role": "assistant",
                "content": content,
                "container": None,
                "stop_reason": stop_reason,
                "stop_sequence": None,
                "stop_details": None,
                "usage": {"input_tokens": 0, "output_tokens": 0,
                          "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0},
                "input_transformations": [],
                "diagnostics": None,
                "context_management": None,
            },
            "apiBlockIndex": 0,
            "requestId": "req_" + self._hex(f"req-{n}", 24),
            "type": "assistant",
            "advisorModel": MODEL,
            "effort": "medium",
            "perTurnEffort": "medium",
        }

    def user_text(self, text: str) -> str:
        return self._append({
            "promptId": self._prompt_id,
            "type": "user",
            "message": {"role": "user", "content": text},
            "permissionMode": "auto",
            "promptSource": "sdk",
            "turnOrigin": "sdk",
        })

    def assistant_text(self, text: str, skill_name: str | None = None) -> str:
        fields = self._assistant([{"type": "text", "text": text}], "end_turn")
        if skill_name:
            fields["attributionSkill"] = skill_name
            fields["attributionPlugin"] = skill_name.split(":")[0]
        return self._append(fields)

    def skill_call(self, skill: SkillLoad) -> tuple[str, str]:
        tool_id = "toolu_" + self._hex(f"tool-{len(self.records)}", 22)
        tool_input = {"skill": skill.name, "args": skill.args}
        fields = self._assistant(
            [{"type": "tool_use", "id": tool_id, "name": "Skill", "input": tool_input,
              "caller": {"type": "direct"}}],
            "tool_use")
        fields["wireToolInputs"] = {tool_id: tool_input}
        return self._append(fields), tool_id

    def tool_result(self, tool_id: str, call_uuid: str, skill_name: str) -> str:
        return self._append({
            "promptId": self._prompt_id,
            "type": "user",
            "message": {"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": tool_id, "content": f"Launching skill: {skill_name}"}]},
            "toolUseResult": {"success": True, "commandName": skill_name},
            "sourceToolAssistantUUID": call_uuid,
        })

    def skill_injection(self, text: str, tool_id: str) -> str:
        return self._append({
            "promptId": self._prompt_id,
            "type": "user",
            "message": {"role": "user", "content": [{"type": "text", "text": text}]},
            "isMeta": True,
            "turnCompanion": True,
            "sourceToolUseID": tool_id,
        })

    def last_prompt(self, text: str) -> None:
        # Session-list bookkeeping, not part of the parentUuid chain.
        self.records.append({"type": "last-prompt", "lastPrompt": text,
                             "leafUuid": self._parent, "sessionId": self.session_id})


def build_records(seed: str, messages: Sequence[Message], *, cwd: str, skill_md: str,
                  skill_dir: str, with_skill: bool) -> list[Record]:
    """Transcript records for `messages`. `seed` fixes every generated id."""
    builder = _Builder(seed, cwd)
    for message in messages:
        if message.role == "user":
            builder.user_text(message.content)
        elif message.skill and with_skill:
            call_uuid, tool_id = builder.skill_call(message.skill)
            builder.tool_result(tool_id, call_uuid, message.skill.name)
            builder.skill_injection(skill_message_text(skill_md, skill_dir, message.skill.args), tool_id)
            builder.assistant_text(message.content, skill_name=message.skill.name)
        else:
            builder.assistant_text(message.content)
    builder.last_prompt(next(m.content for m in reversed(messages) if m.role == "user"))
    return builder.records


def write_jsonl(path: Path, records: list[Record]) -> None:
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records), encoding="utf-8")
