"""A throwaway plugin with one replay source, for tests."""

import json
from pathlib import Path

LESSON = """\
schema_version: "1.1"
name: lesson-replay
tags: [replay]
context:
  messages:
    - role: user
      content: what is X?
    - role: assistant
      skill: {name: demo:teach, args: X}
      content: |
        X is a thing.
    - role: user
      content: I use it daily.
    - role: assistant
      content: Step 1 of 2 — X does Y.
execution:
  model: claude-opus-5-5
  prompt: |
    next
  max_turns: 6
  timeout_seconds: 300
  allowed_tools: [Skill]
runs: 2
graders:
  - name: one-step
    type: llm
    focus: last_message
    criteria: Pass if the reply teaches exactly one step.
  - name: step-heading
    type: regex
    pattern: Step 2 of 2
    arm: with-only
"""

SKILL_BODY = "---\nname: teach\ndescription: Teach one step at a time.\n---\n\n# Teach\n\nOne step per reply.\n"


def make_plugin(root: Path, source_yaml: str = LESSON, skill_body: str = SKILL_BODY) -> Path:
    plugin = root / "demo"
    (plugin / ".claude-plugin").mkdir(parents=True)
    (plugin / ".claude-plugin" / "plugin.json").write_text(json.dumps({"name": "demo", "version": "0.1.0"}))
    (plugin / "skills" / "teach").mkdir(parents=True)
    (plugin / "skills" / "teach" / "SKILL.md").write_text(skill_body)
    (plugin / "evals" / "old-case").mkdir(parents=True)
    (plugin / "evals" / "old-case" / "prompt.md").write_text("---\nruns: 1\n---\n\nhello\n")
    source_dir = plugin / "replays" / "lesson"
    source_dir.mkdir(parents=True)
    (source_dir / "case.yaml").write_text(source_yaml)
    return plugin
