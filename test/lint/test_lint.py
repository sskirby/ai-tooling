import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from lint import Checker  # noqa: E402


def write(root, path, body):
    full = root / path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(body)


def build(overrides=None):
    root = Path(tempfile.mkdtemp())
    write(root, ".claude-plugin/marketplace.json", json.dumps({
        "name": "ai-tooling",
        "owner": {"name": "Sean Kirby"},
        "plugins": [{"name": "what-the-heck", "source": "./plugins/what-the-heck"}],
    }, indent=2))
    write(root, "plugins/what-the-heck/.claude-plugin/plugin.json", json.dumps({
        "name": "what-the-heck", "version": "0.1.0", "description": "Teach one idea at a time.",
    }, indent=2))
    write(root, "plugins/what-the-heck/skills/what-the-heck/SKILL.md",
          "---\nname: what-the-heck\ndescription: Use when the user wants to understand something.\n---\n\n# What The Heck\n")
    write(root, "plugins/what-the-heck/evals/opening/prompt.md",
          "---\nruns: 3\nmodel: claude-opus-5-5\nallowed_tools: [Skill]\n---\n\nwhat the heck is a CTE?\n")
    write(root, "plugins/what-the-heck/evals/opening/graders/no-make-sense.md",
          "---\ntype: regex\ntarget: last_message\nmatch: not_contains\nflags: i\n---\n\nmake sense\n")
    for path, body in (overrides or {}).items():
        if body is None:
            (root / path).unlink(missing_ok=True)
        else:
            write(root, path, body)
    return root


def lint(root):
    return Checker(str(root)).run()


class LintTest(unittest.TestCase):
    def tearDown(self):
        for root in getattr(self, "_roots", []):
            shutil.rmtree(root, ignore_errors=True)

    def build(self, overrides=None):
        root = build(overrides)
        self._roots = getattr(self, "_roots", [])
        self._roots.append(root)
        return root

    def test_clean_tree_passes(self):
        self.assertEqual(lint(self.build()), [])

    def test_grader_without_frontmatter_is_caught(self):
        errors = lint(self.build({"plugins/what-the-heck/evals/opening/graders/no-make-sense.md": "make sense\n"}))
        self.assertIn("silently skips", "\n".join(errors))

    def test_unknown_grader_type_is_caught(self):
        errors = lint(self.build({
            "plugins/what-the-heck/evals/opening/graders/no-make-sense.md":
                "---\ntype: regexp\n---\n\nmake sense\n",
        }))
        self.assertIn("is not one of regex | tool_order", "\n".join(errors))

    def test_unknown_prompt_frontmatter_key_is_caught(self):
        errors = lint(self.build({
            "plugins/what-the-heck/evals/opening/prompt.md":
                "---\ncontext:\n  history_file: x.jsonl\n---\n\nwhat the heck is a CTE?\n",
        }))
        self.assertIn('unknown frontmatter key "context"', "\n".join(errors))

    def test_case_without_a_pinned_model_is_caught(self):
        errors = lint(self.build({
            "plugins/what-the-heck/evals/opening/prompt.md":
                "---\nruns: 3\nallowed_tools: [Skill]\n---\n\nwhat the heck is a CTE?\n",
        }))
        self.assertIn("pins no model", "\n".join(errors))

    def test_bad_match_value_is_caught(self):
        errors = lint(self.build({
            "plugins/what-the-heck/evals/opening/graders/no-make-sense.md":
                "---\ntype: regex\nmatch: absent\n---\n\nmake sense\n",
        }))
        self.assertIn("is not contains | not_contains | count:N", "\n".join(errors))

    def test_must_not_call_needs_min_zero_and_arm_both(self):
        errors = lint(self.build({
            "plugins/what-the-heck/evals/opening/graders/no-skill.md":
                "---\ntype: tool_used\ntool: Skill\nmax: 0\n---\n",
        }))
        self.assertIn("needs min: 0, max: 0 AND arm: both", "\n".join(errors))

    def test_broken_marketplace_json_is_caught(self):
        errors = lint(self.build({".claude-plugin/marketplace.json": "{ not json"}))
        self.assertIn("invalid JSON", "\n".join(errors))

    def test_case_yaml_missing_schema_version_is_caught(self):
        errors = lint(self.build({
            "plugins/what-the-heck/evals/no-trigger-task-ask/case.yaml":
                "name: no-trigger-task-ask\nexecution:\n  prompt: |\n    how do I add an index?\n"
                "graders:\n  - name: x\n    type: llm\n    criteria: it answers\n",
        }))
        self.assertIn("missing schema_version", "\n".join(errors))

    def test_valid_case_yaml_passes(self):
        errors = lint(self.build({
            "plugins/what-the-heck/evals/no-trigger-task-ask/case.yaml":
                'schema_version: "1.1"\nname: no-trigger-task-ask\nexecution:\n'
                "  model: claude-opus-5-5\n  prompt: |\n    how do I add an index?\n"
                "  allowed_tools: [Skill]\nruns: 3\ngraders:\n"
                "  - name: skill-did-not-fire\n    type: tool_used\n    tool: Skill\n"
                "    min: 0\n    max: 0\n    arm: both\n",
        }))
        self.assertEqual(errors, [])

    def test_skill_name_must_match_directory(self):
        errors = lint(self.build({
            "plugins/what-the-heck/skills/what-the-heck/SKILL.md":
                "---\nname: whattheheck\ndescription: x\n---\n\nbody\n",
        }))
        self.assertIn("does not match its directory", "\n".join(errors))

    def test_absolute_path_in_prompt_is_caught(self):
        errors = lint(self.build({
            "plugins/what-the-heck/evals/opening/prompt.md":
                "---\nruns: 3\n---\n\nread ~/.claude/skills/what-the-heck/SKILL.md\n",
        }))
        self.assertIn("sandbox cwd", "\n".join(errors))

    def test_missing_evals_directory_is_caught(self):
        root = self.build()
        shutil.rmtree(root / "plugins/what-the-heck/evals")
        errors = lint(root)
        self.assertIn("holds no eval cases", "\n".join(errors))


if __name__ == "__main__":
    unittest.main()
