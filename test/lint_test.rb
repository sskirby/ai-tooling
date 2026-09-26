# frozen_string_literal: true

require "minitest/autorun"
require "tmpdir"
require "fileutils"
require "json"
require_relative "../scripts/lint"

class LintTest < Minitest::Test
  def build(overrides = {})
    root = Dir.mktmpdir
    write(root, ".claude-plugin/marketplace.json", JSON.pretty_generate(
      "name" => "ai-tooling",
      "owner" => { "name" => "Sean Kirby" },
      "plugins" => [{ "name" => "what-the-heck", "source" => "./plugins/what-the-heck" }]
    ))
    write(root, "plugins/what-the-heck/.claude-plugin/plugin.json", JSON.pretty_generate(
      "name" => "what-the-heck", "version" => "0.1.0", "description" => "Teach one idea at a time."
    ))
    write(root, "plugins/what-the-heck/skills/what-the-heck/SKILL.md",
          "---\nname: what-the-heck\ndescription: Use when the user wants to understand something.\n---\n\n# What The Heck\n")
    write(root, "plugins/what-the-heck/evals/opening/prompt.md",
          "---\nruns: 3\nmodel: claude-opus-5-5\nallowed_tools: [Skill]\n---\n\nwhat the heck is a CTE?\n")
    write(root, "plugins/what-the-heck/evals/opening/graders/no-make-sense.md",
          "---\ntype: regex\ntarget: last_message\nmatch: not_contains\nflags: i\n---\n\nmake sense\n")
    overrides.each { |path, body| body.nil? ? FileUtils.rm_f(File.join(root, path)) : write(root, path, body) }
    root
  end

  def write(root, path, body)
    full = File.join(root, path)
    FileUtils.mkdir_p(File.dirname(full))
    File.write(full, body)
  end

  def lint(root) = Lint::Checker.new(root).run

  def test_clean_tree_passes
    assert_empty lint(build)
  end

  def test_grader_without_frontmatter_is_caught
    errors = lint(build("plugins/what-the-heck/evals/opening/graders/no-make-sense.md" => "make sense\n"))
    assert_includes errors.join("\n"), "silently skips"
  end

  def test_unknown_grader_type_is_caught
    errors = lint(build("plugins/what-the-heck/evals/opening/graders/no-make-sense.md" =>
      "---\ntype: regexp\n---\n\nmake sense\n"))
    assert_includes errors.join("\n"), "is not one of regex | tool_order"
  end

  def test_unknown_prompt_frontmatter_key_is_caught
    errors = lint(build("plugins/what-the-heck/evals/opening/prompt.md" =>
      "---\ncontext:\n  history_file: x.jsonl\n---\n\nwhat the heck is a CTE?\n"))
    assert_includes errors.join("\n"), "unknown frontmatter key \"context\""
  end

  def test_case_without_a_pinned_model_is_caught
    errors = lint(build("plugins/what-the-heck/evals/opening/prompt.md" =>
      "---\nruns: 3\nallowed_tools: [Skill]\n---\n\nwhat the heck is a CTE?\n"))
    assert_includes errors.join("\n"), "pins no model"
  end

  def test_bad_match_value_is_caught
    errors = lint(build("plugins/what-the-heck/evals/opening/graders/no-make-sense.md" =>
      "---\ntype: regex\nmatch: absent\n---\n\nmake sense\n"))
    assert_includes errors.join("\n"), "is not contains | not_contains | count:N"
  end

  def test_must_not_call_needs_min_zero_and_arm_both
    errors = lint(build("plugins/what-the-heck/evals/opening/graders/no-skill.md" =>
      "---\ntype: tool_used\ntool: Skill\nmax: 0\n---\n"))
    assert_includes errors.join("\n"), "needs min: 0, max: 0 AND arm: both"
  end

  def test_broken_marketplace_json_is_caught
    errors = lint(build(".claude-plugin/marketplace.json" => "{ not json"))
    assert_includes errors.join("\n"), "invalid JSON"
  end

  def test_case_yaml_missing_schema_version_is_caught
    errors = lint(build("plugins/what-the-heck/evals/no-trigger-task-ask/case.yaml" =>
      "name: no-trigger-task-ask\nexecution:\n  prompt: |\n    how do I add an index?\ngraders:\n  - name: x\n    type: llm\n    criteria: it answers\n"))
    assert_includes errors.join("\n"), "missing schema_version"
  end

  def test_valid_case_yaml_passes
    assert_empty lint(build("plugins/what-the-heck/evals/no-trigger-task-ask/case.yaml" =>
      "schema_version: \"1.1\"\nname: no-trigger-task-ask\nexecution:\n  model: claude-opus-5-5\n  prompt: |\n    how do I add an index?\n  allowed_tools: [Skill]\nruns: 3\ngraders:\n  - name: skill-did-not-fire\n    type: tool_used\n    tool: Skill\n    min: 0\n    max: 0\n    arm: both\n"))
  end

  def test_skill_name_must_match_directory
    errors = lint(build("plugins/what-the-heck/skills/what-the-heck/SKILL.md" =>
      "---\nname: whattheheck\ndescription: x\n---\n\nbody\n"))
    assert_includes errors.join("\n"), "does not match its directory"
  end

  def test_absolute_path_in_prompt_is_caught
    errors = lint(build("plugins/what-the-heck/evals/opening/prompt.md" =>
      "---\nruns: 3\n---\n\nread ~/.claude/skills/what-the-heck/SKILL.md\n"))
    assert_includes errors.join("\n"), "sandbox cwd"
  end

  def test_missing_evals_directory_is_caught
    root = build
    FileUtils.rm_rf(File.join(root, "plugins/what-the-heck/evals"))
    errors = lint(root)
    assert_includes errors.join("\n"), "holds no eval cases"
  end
end
