import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "evals"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from helpers import LESSON, make_plugin  # noqa: E402
from sources import SourceError, load_source, load_sources  # noqa: E402
from transcript import SkillLoad  # noqa: E402


class LoadSource(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def load(self, text, grader_files=None):
        plugin = make_plugin(self.root, text)
        for name, body in (grader_files or {}).items():
            graders = plugin / "replays" / "lesson" / "graders"
            graders.mkdir(exist_ok=True)
            (graders / name).write_text(body)
        return load_source(plugin / "replays" / "lesson" / "case.yaml")

    def assertRefused(self, text, fragment, grader_files=None):
        with self.assertRaises(SourceError) as caught:
            self.load(text, grader_files)
        self.assertIn(fragment, str(caught.exception))

    def test_loads_the_lesson(self):
        source = self.load(LESSON)
        self.assertEqual(source.name, "lesson-replay")
        self.assertEqual(source.baseline_name, "lesson-replay-baseline")
        self.assertEqual([m.role for m in source.messages], ["user", "assistant", "user", "assistant"])
        self.assertEqual(source.skill, SkillLoad("demo:teach", "X"))
        self.assertEqual(source.messages[1].content, "X is a thing.")  # block scalar's newline dropped
        self.assertEqual(source.execution["prompt"], "next\n")
        self.assertEqual(source.runs, 2)
        self.assertEqual(source.with_only, frozenset({"step-heading"}))
        self.assertEqual(source.meta, {"schema_version": "1.1", "tags": ["replay"]})

    def test_grader_files_are_read(self):
        source = self.load(LESSON, {"judge.md": "---\ntype: llm\nfocus: last_message\n---\n\nPass if kind.\n"})
        judge = next(g for g in source.graders if g["name"] == "judge")
        self.assertEqual(judge, {"name": "judge", "type": "llm", "focus": "last_message", "criteria": "Pass if kind.\n"})

    def test_refuses_skill_tool_used_grader_inline(self):
        text = LESSON + "  - name: skill-fired\n    type: tool_used\n    tool: Skill\n    min: 1\n    arm: with-only\n"
        self.assertRefused(text, "skill-fired")

    def test_refuses_skill_tool_used_grader_in_file(self):
        self.assertRefused(LESSON, "skill-fired",
                           {"skill-fired.md": "---\ntype: tool_used\ntool: Skill\ninput_match: teach\nmin: 1\n---\n"})

    def test_allows_skill_did_not_fire_grader(self):
        text = LESSON + "  - name: no-skill\n    type: tool_used\n    tool: Skill\n    min: 0\n    max: 0\n"
        self.assertIn("no-skill", [g["name"] for g in self.load(text).graders])

    def test_refuses_body_on_non_llm_grader_file(self):
        self.assertRefused(LESSON, "only llm graders", {"x.md": "---\ntype: regex\npattern: a\n---\n\nbody\n"})

    def test_refuses_all_with_only(self):
        text = LESSON.replace("    criteria: Pass if the reply teaches exactly one step.\n",
                              "    criteria: Pass if the reply teaches exactly one step.\n    arm: with-only\n")
        self.assertRefused(text, "at least one grader without arm: with-only")

    def test_refuses_no_skill_message(self):
        self.assertRefused(LESSON.replace("      skill: {name: demo:teach, args: X}\n", ""), "exactly one")

    def test_refuses_two_skill_messages(self):
        text = LESSON.replace("      content: Step 1 of 2", "      skill: {name: demo:teach, args: X}\n      content: Step 1 of 2")
        self.assertRefused(text, "exactly one")

    def test_refuses_skill_on_user_turn(self):
        text = LESSON.replace("      content: what is X?", "      skill: {name: demo:teach, args: X}\n      content: what is X?")
        self.assertRefused(text, "skill goes on the assistant turn")

    def test_refuses_turns_out_of_order(self):
        text = LESSON.replace("    - role: user\n      content: I use it daily.\n", "")
        self.assertRefused(text, "must be role user")

    def test_refuses_ending_on_user_turn(self):
        text = LESSON.replace("    - role: assistant\n      content: Step 1 of 2 — X does Y.\n", "")
        self.assertRefused(text, "must end with an assistant turn")

    def test_refuses_plugins_key(self):
        self.assertRefused(LESSON + "plugins: [stub]\n", "unsupported keys")

    def test_refuses_history_file(self):
        self.assertRefused(LESSON.replace("context:\n", "context:\n  history_file: h.jsonl\n"), "exactly one key")

    def test_refuses_baseline_suffix_in_name(self):
        self.assertRefused(LESSON.replace("name: lesson-replay", "name: lesson-baseline"), "must not end with")

    def test_refuses_missing_prompt(self):
        self.assertRefused(LESSON.replace("  prompt: |\n    next\n", ""), "execution.prompt")

    def test_load_sources_finds_every_source(self):
        plugin = make_plugin(self.root)
        self.assertEqual([s.name for s in load_sources(plugin)], ["lesson-replay"])


if __name__ == "__main__":
    unittest.main()
