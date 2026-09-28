import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from evals.version_bump import check

PLUGIN = "plugins/what-the-heck"


def git(root, *args):
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


def write(root, path, body):
    full = root / path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(body)


def manifest(version):
    return json.dumps({"name": "what-the-heck", "version": version})


def commit(root, files, message):
    for path, body in files.items():
        write(root, path, body)
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", message)


class VersionBumpTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        git(self.root, "init", "-q", "-b", "main")
        git(self.root, "config", "user.email", "test@example.com")
        git(self.root, "config", "user.name", "Test")
        commit(self.root, {
            ".claude-plugin/marketplace.json": json.dumps({
                "name": "ai-tooling",
                "plugins": [{"name": "what-the-heck", "source": f"./{PLUGIN}"}],
            }),
            f"{PLUGIN}/.claude-plugin/plugin.json": manifest("0.1.0"),
            f"{PLUGIN}/skills/what-the-heck/SKILL.md": "v1\n",
            f"{PLUGIN}/evals/opening/prompt.md": "v1\n",
            f"{PLUGIN}/replays/closing/case.yaml": "v1\n",
            f"{PLUGIN}/README.md": "v1\n",
        }, "base")
        git(self.root, "branch", "base")

    def check(self):
        return check(self.root, "base")

    def test_skill_change_without_bump_fails(self):
        commit(self.root, {f"{PLUGIN}/skills/what-the-heck/SKILL.md": "v2\n"}, "edit skill")
        errors = self.check()
        self.assertEqual(len(errors), 1)
        self.assertIn("what-the-heck", errors[0])
        self.assertIn("0.1.0", errors[0])
        self.assertIn("skills/what-the-heck/SKILL.md", errors[0])

    def test_skill_change_with_bump_passes(self):
        commit(self.root, {
            f"{PLUGIN}/skills/what-the-heck/SKILL.md": "v2\n",
            f"{PLUGIN}/.claude-plugin/plugin.json": manifest("0.1.1"),
        }, "edit skill and bump")
        self.assertEqual(self.check(), [])

    def test_manifest_change_without_bump_fails(self):
        commit(self.root, {
            f"{PLUGIN}/.claude-plugin/plugin.json":
                json.dumps({"name": "what-the-heck", "version": "0.1.0", "description": "new"}),
        }, "edit description")
        self.assertEqual(len(self.check()), 1)

    def test_dev_only_changes_pass(self):
        commit(self.root, {
            f"{PLUGIN}/evals/opening/prompt.md": "v2\n",
            f"{PLUGIN}/replays/closing/case.yaml": "v2\n",
            f"{PLUGIN}/README.md": "v2\n",
        }, "edit evals and docs")
        self.assertEqual(self.check(), [])

    def test_changes_outside_plugins_pass(self):
        commit(self.root, {"README.md": "top-level\n"}, "edit repo readme")
        self.assertEqual(self.check(), [])

    def test_new_plugin_passes(self):
        commit(self.root, {
            ".claude-plugin/marketplace.json": json.dumps({
                "name": "ai-tooling",
                "plugins": [
                    {"name": "what-the-heck", "source": f"./{PLUGIN}"},
                    {"name": "other", "source": "./plugins/other"},
                ],
            }),
            "plugins/other/.claude-plugin/plugin.json": json.dumps({"name": "other", "version": "0.1.0"}),
            "plugins/other/skills/other/SKILL.md": "v1\n",
        }, "add plugin")
        self.assertEqual(self.check(), [])

    def test_compares_against_merge_base(self):
        # base moving ahead with its own bump must not satisfy, or break, the branch's check.
        git(self.root, "checkout", "-q", "-b", "feature")
        commit(self.root, {f"{PLUGIN}/skills/what-the-heck/SKILL.md": "v2\n"}, "edit skill")
        git(self.root, "checkout", "-q", "base")
        commit(self.root, {f"{PLUGIN}/.claude-plugin/plugin.json": manifest("0.2.0")}, "bump on base")
        git(self.root, "checkout", "-q", "feature")
        self.assertEqual(len(self.check()), 1)


if __name__ == "__main__":
    unittest.main()
