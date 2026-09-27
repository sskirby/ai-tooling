import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "evals"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from helpers import make_plugin  # noqa: E402
from wrapper import EXIT_REFUSED, EXIT_RESULTS, main  # noqa: E402

# Stands in for `claude`: records its argv, writes the canned result to --json, exits with $FAKE_EXIT.
FAKE_CLAUDE = """#!/usr/bin/env python3
import json, os, sys
argv = sys.argv[1:]
with open(os.environ["FAKE_ARGV"], "w") as f:
    json.dump(argv, f)
canned = os.environ.get("FAKE_RESULT")
if canned:
    out = argv[argv.index("--json") + 1]
    with open(canned) as src, open(out, "w") as dst:
        dst.write(src.read())
sys.exit(int(os.environ.get("FAKE_EXIT", "0")))
"""


def run_(graders_passed):
    graders = [{"name": n, "passed": p, "weight": 1, "scored": True, "withOnly": False} for n, p in graders_passed]
    return {"score": sum(p for _, p in graders_passed) / len(graders_passed), "error": None, "costUsd": 0.1,
            "judgeCostUsd": 0.0, "skippedPaidGraders": False, "tracePath": None, "graders": graders}


def result(replay_arms=("with",)):
    replay_run = run_([("one-step", True), ("step-heading", False)])
    return {"cases": [
        {"name": "lesson-replay", "aggregates": {}, "arms": {arm: [replay_run] for arm in replay_arms}},
        {"name": "lesson-replay-baseline", "aggregates": {}, "arms": {"with": [run_([("one-step", False)])]}},
    ]}


class Wrapper(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.plugin = make_plugin(root)
        fake = root / "claude"
        fake.write_text(FAKE_CLAUDE)
        fake.chmod(0o755)
        self.argv_file = root / "argv.json"
        self.result_file = root / "canned.json"
        self.env = {"CLAUDE_BIN": str(fake), "FAKE_ARGV": str(self.argv_file), "FAKE_RESULT": str(self.result_file)}
        self.old_env = {k: os.environ.get(k) for k in [*self.env, "FAKE_EXIT"]}
        os.environ.update(self.env)
        self.result_file.write_text(json.dumps(result()))

    def tearDown(self):
        for key, value in self.old_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        self.tmp.cleanup()

    def call(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main([str(self.plugin), *args])
        return code, out.getvalue(), err.getvalue()

    def claude_argv(self):
        return json.loads(self.argv_file.read_text())

    def test_runs_eval_once_and_prints_delta(self):
        code, out, _ = self.call("--judge-model", "claude-opus-5-5", "--runs", "1")
        self.assertEqual(code, 0)
        argv = self.claude_argv()
        self.assertEqual(argv[:3], ["plugin", "eval", str(self.plugin.resolve())])
        self.assertIn("--judge-model", argv)
        self.assertNotIn("--ablation", argv)
        self.assertIn("| lesson-replay | replay | 1.00 | 0.00 | +1.00 | 1 |", out)
        delta_md = self.plugin / "evals" / "replay" / "delta.md"
        self.assertEqual(delta_md.read_text(), out)
        self.assertTrue((self.plugin / "evals" / "replay" / "lesson-replay" / "history.jsonl").is_file())

    def test_user_json_path_is_used(self):
        target = Path(self.tmp.name) / "out" / "r.json"
        target.parent.mkdir()
        code, _, _ = self.call("--json", str(target))
        self.assertEqual(code, 0)
        argv = self.claude_argv()
        self.assertEqual(argv[argv.index("--json") + 1], str(target))
        self.assertEqual(argv.count("--json"), 1)
        self.assertTrue((target.parent / "delta.md").is_file())

    def test_refuses_ablation(self):
        for args in (["--ablation", "with-without"], ["--ablation=none"]):
            code, _, err = self.call(*args)
            self.assertEqual(code, EXIT_REFUSED)
            self.assertIn("--ablation", err)
        self.assertFalse(self.argv_file.exists())

    def test_refuses_missing_target(self):
        err = io.StringIO()
        with redirect_stderr(err):
            self.assertEqual(main(["what-the-heck@ai-tooling"]), EXIT_REFUSED)
            self.assertEqual(main(["--runs", "1"]), EXIT_REFUSED)
        self.assertIn("plugin directory", err.getvalue())

    def test_refuses_glob_that_splits_a_pair(self):
        code, _, err = self.call("--case", "lesson-replay")
        self.assertEqual(code, EXIT_REFUSED)
        self.assertIn("lesson-replay*", err)
        code, _, _ = self.call("--case=lesson-replay*")
        self.assertEqual(code, 0)

    def test_results_guard(self):
        self.result_file.write_text(json.dumps(result(replay_arms=("with", "without"))))
        code, _, err = self.call()
        self.assertEqual(code, EXIT_RESULTS)
        self.assertIn("must run only 'with'", err)

    def test_no_json_means_no_table(self):
        os.environ["FAKE_RESULT"] = ""
        os.environ["FAKE_EXIT"] = "2"
        code, out, err = self.call()
        self.assertEqual(code, 2)
        self.assertIn("no results", err)
        self.assertEqual(out, "")

    def test_stale_user_json_is_removed_first(self):
        target = Path(self.tmp.name) / "r.json"
        target.write_text(json.dumps(result()))
        os.environ["FAKE_RESULT"] = ""
        code, out, err = self.call("--json", str(target))
        self.assertEqual(code, 1)
        self.assertIn("no results", err)
        self.assertEqual(out, "")

    def test_passes_through_cli_exit_code(self):
        os.environ["FAKE_EXIT"] = "1"
        code, _, _ = self.call()
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
