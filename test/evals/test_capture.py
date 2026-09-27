import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "evals"))

import yaml  # noqa: E402

from capture import dump_yaml, reply_from_trace, skill_args_from_trace  # noqa: E402


def event(*blocks):
    return json.dumps({"type": "assistant", "message": {"content": list(blocks)}})


TURN_ZERO = [
    json.dumps({"type": "system", "subtype": "init"}),
    event({"type": "thinking", "thinking": "", "signature": "x"}),
    event({"type": "text", "text": "Let me load the skill."}),
    event({"type": "tool_use", "name": "Skill", "input": {"skill": "demo:teach", "args": "CTEs"}}),
    json.dumps({"type": "user", "message": {"content": [{"type": "tool_result"}]}}),
    event({"type": "text", "text": "A CTE is a named subquery."}, {"type": "text", "text": "Here's the route:"}),
    json.dumps({"type": "result"}),
]


class Trace(unittest.TestCase):
    def test_reply_is_text_after_last_tool_call(self):
        self.assertEqual(reply_from_trace(TURN_ZERO), "A CTE is a named subquery.\n\nHere's the route:")

    def test_reply_without_tool_call(self):
        self.assertEqual(reply_from_trace([event({"type": "text", "text": "Step 2 of 5"})]), "Step 2 of 5")

    def test_skill_args(self):
        self.assertEqual(skill_args_from_trace(TURN_ZERO, "demo:teach"), "CTEs")
        self.assertIsNone(skill_args_from_trace(TURN_ZERO, "other:skill"))


class Dump(unittest.TestCase):
    def test_multiline_strings_are_blocks_and_round_trip(self):
        data = {"messages": [{"role": "assistant", "content": "line one\n\n- item — “quoted”"}]}
        text = dump_yaml(data)
        self.assertIn("content: |", text)
        self.assertEqual(yaml.safe_load(text), data)


if __name__ == "__main__":
    unittest.main()
