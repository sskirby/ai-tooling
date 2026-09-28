import json
import re
import tempfile
import unittest
from pathlib import Path

import yaml

from evals.capture import CAPTURE_DIR, dump_yaml, read_run, reply_from_trace, skill_args_from_trace


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


class Sandbox(unittest.TestCase):
    def test_capture_dir_is_a_name_the_cli_accepts(self):
        # CLI 2.1.283 refuses an --eval-dir that does not start with a letter or digit.
        self.assertRegex(CAPTURE_DIR, r"\A[A-Za-z0-9][A-Za-z0-9._\-@+]*\Z")

    def test_missing_result_is_a_clear_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(RuntimeError, "no result"):
                read_run(Path(tmp) / "result.json")


if __name__ == "__main__":
    unittest.main()
