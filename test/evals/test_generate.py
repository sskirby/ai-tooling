import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

import yaml

from evals.generate import existing_case_names, generate, main
from evals.sources import SourceError
from helpers import LESSON, make_plugin


def history(case_dir):
    return [json.loads(line) for line in (case_dir / "history.jsonl").read_text().splitlines()]


class Generate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.plugin = make_plugin(Path(self.tmp.name))
        self.replay = self.plugin / "evals" / "replay"

    def tearDown(self):
        self.tmp.cleanup()

    def test_writes_the_pair(self):
        generate(self.plugin)
        with_case = yaml.safe_load((self.replay / "lesson-replay" / "case.yaml").read_text())
        base_case = yaml.safe_load((self.replay / "lesson-replay-baseline" / "case.yaml").read_text())
        self.assertEqual(with_case["name"], "lesson-replay")
        self.assertEqual(with_case["context"], {"history_file": "history.jsonl"})
        self.assertNotIn("plugins", with_case)
        self.assertEqual(with_case["execution"]["prompt"], "next\n")
        self.assertEqual(with_case["runs"], 2)
        self.assertEqual(with_case["tags"], ["replay"])
        self.assertEqual(base_case["name"], "lesson-replay-baseline")
        self.assertEqual(base_case["plugins"], ["stub"])
        stub = json.loads((self.replay / "lesson-replay-baseline" / "stub" / ".claude-plugin" / "plugin.json").read_text())
        self.assertEqual(stub["name"], "replay-baseline-stub")

    def test_case_yaml_is_json(self):
        generate(self.plugin)
        json.loads((self.replay / "lesson-replay" / "case.yaml").read_text())

    def test_with_only_graders_only_in_replay_case(self):
        generate(self.plugin)
        names = lambda d: [g["name"] for g in yaml.safe_load((self.replay / d / "case.yaml").read_text())["graders"]]
        self.assertEqual(names("lesson-replay"), ["one-step", "step-heading"])
        self.assertEqual(names("lesson-replay-baseline"), ["one-step"])

    def test_histories_differ_only_by_the_skill_load(self):
        generate(self.plugin)
        with_types = [r["type"] for r in history(self.replay / "lesson-replay")]
        base_types = [r["type"] for r in history(self.replay / "lesson-replay-baseline")]
        self.assertEqual(len(with_types) - len(base_types), 3)
        self.assertTrue(any(r.get("isMeta") for r in history(self.replay / "lesson-replay")))
        self.assertFalse(any(r.get("isMeta") for r in history(self.replay / "lesson-replay-baseline")))

    def test_history_follows_the_current_skill_md(self):
        generate(self.plugin)
        skill_md = self.plugin / "skills" / "teach" / "SKILL.md"
        skill_md.write_text(skill_md.read_text().replace("One step per reply.", "Two steps per reply."))
        generate(self.plugin)
        injected = next(r for r in history(self.replay / "lesson-replay") if r.get("isMeta"))
        self.assertIn("Two steps per reply.", injected["message"]["content"][0]["text"])

    def test_same_input_same_bytes(self):
        generate(self.plugin)
        first = (self.replay / "lesson-replay" / "history.jsonl").read_bytes()
        generate(self.plugin)
        self.assertEqual(first, (self.replay / "lesson-replay" / "history.jsonl").read_bytes())

    def test_wipes_cases_whose_source_is_gone(self):
        (self.replay / "renamed-replay").mkdir(parents=True)
        generate(self.plugin)
        self.assertFalse((self.replay / "renamed-replay").exists())

    def test_refuses_name_used_by_existing_case(self):
        source = self.plugin / "replays" / "lesson" / "case.yaml"
        source.write_text(LESSON.replace("name: lesson-replay", "name: old-case"))
        with self.assertRaisesRegex(SourceError, "already used"):
            generate(self.plugin)

    def test_refuses_skill_of_another_plugin_without_wiping(self):
        (self.replay / "keep-me").mkdir(parents=True)
        source = self.plugin / "replays" / "lesson" / "case.yaml"
        source.write_text(LESSON.replace("demo:teach", "other:teach"))
        with self.assertRaisesRegex(SourceError, "not a skill of plugin"):
            generate(self.plugin)
        self.assertTrue((self.replay / "keep-me").exists())

    def test_existing_names_skip_replay_dir(self):
        generate(self.plugin)
        self.assertEqual(existing_case_names(self.plugin / "evals"), {"old-case"})

    def test_check_leaves_plugin_untouched(self):
        self.assertEqual(main([str(self.plugin), "--check"]), 0)
        self.assertFalse(self.replay.exists())

    def test_main_reports_a_bad_source(self):
        (self.plugin / "replays" / "lesson" / "case.yaml").write_text(LESSON + "plugins: [x]\n")
        err = io.StringIO()
        with redirect_stderr(err):
            self.assertEqual(main([str(self.plugin), "--check"]), 1)
        self.assertIn("unsupported keys", err.getvalue())


if __name__ == "__main__":
    unittest.main()
