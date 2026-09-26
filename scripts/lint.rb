#!/usr/bin/env ruby
# frozen_string_literal: true

# Free pre-merge gate: both manifests parse, every case matches the eval schema,
# every grader names a real type. Ruby stdlib only, so it runs on a fork PR with
# no secrets and no install step.

require "json"
require "yaml"

module Lint
  GRADER_TYPES = %w[regex tool_order tool_used file_exists llm baseline].freeze
  FOCI = %w[trace last_message files mock_calls].freeze
  MATCHES = %w[contains not_contains].freeze
  ARMS = %w[with-only both].freeze
  PROMPT_KEYS = %w[
    name description tags plugins runs expected_outcome
    model max_turns timeout_seconds allowed_tools artifact_publish
    growthbook_overrides append_system_prompt env
  ].freeze
  TEMPLATE_MARKERS = ["TODO: describe what", "TODO: replace"].freeze
  SKIP_DIRS = %w[results mocks].freeze

  class Checker
    attr_reader :errors

    def initialize(root)
      @root = File.expand_path(root)
      @errors = []
    end

    def run
      marketplace = File.join(@root, ".claude-plugin", "marketplace.json")
      data = read_json(marketplace)
      return @errors if data.nil?

      %w[name owner plugins].each do |key|
        err(marketplace, "missing required key #{key.inspect}") unless data.key?(key)
      end
      entries = data["plugins"]
      unless entries.is_a?(Array) && !entries.empty?
        err(marketplace, "\"plugins\" must be a non-empty array")
        return @errors
      end

      entries.each_with_index do |entry, i|
        unless entry.is_a?(Hash) && entry["name"].is_a?(String) && entry["source"].is_a?(String)
          err(marketplace, "plugins[#{i}] needs string \"name\" and \"source\"")
          next
        end
        dir = File.expand_path(entry["source"], @root)
        unless File.directory?(dir)
          err(marketplace, "plugins[#{i}].source #{entry['source'].inspect} is not a directory")
          next
        end
        check_plugin(dir, entry["name"])
      end

      @errors
    end

    private

    def rel(path)
      p = File.expand_path(path)
      p.start_with?(@root) ? p[(@root.length + 1)..] : p
    end

    def err(path, message)
      @errors << "#{rel(path)}: #{message}"
    end

    def read_json(path)
      unless File.file?(path)
        err(path, "not found")
        return nil
      end
      JSON.parse(File.read(path))
    rescue JSON::ParserError => e
      err(path, "invalid JSON: #{e.message.lines.first.to_s.strip}")
      nil
    end

    def load_yaml(text, path, what)
      YAML.safe_load(text, aliases: false)
    rescue Psych::Exception => e
      err(path, "invalid #{what}: #{e.message.lines.first.to_s.strip}")
      nil
    end

    # Returns [frontmatter_or_nil, body]. nil frontmatter means none was present.
    def split_frontmatter(text, path)
      m = text.match(/\A---\s*\n(.*?)^---\s*\n(.*)\z/m)
      return [nil, text] unless m

      fm = load_yaml(m[1], path, "YAML frontmatter")
      [fm.is_a?(Hash) ? fm : {}, m[2]]
    end

    def check_plugin(dir, entry_name)
      manifest = File.join(dir, ".claude-plugin", "plugin.json")
      data = read_json(manifest)
      return if data.nil?

      %w[name version description].each do |key|
        err(manifest, "missing required key #{key.inspect}") unless data[key].is_a?(String)
      end
      if data["name"].is_a?(String) && data["name"] != entry_name
        err(manifest, "name #{data['name'].inspect} does not match the marketplace entry #{entry_name.inspect}")
      end
      if data.key?("experimental") && data["experimental"].is_a?(Hash) && data["experimental"].key?("evals")
        err(manifest, "experimental.evals restates the evals/ default — remove it")
      end

      Dir.glob(File.join(dir, "skills", "*", "SKILL.md")).sort.each { |f| check_skill(f) }
      check_evals(File.join(dir, "evals"))
    end

    def check_skill(path)
      fm, body = split_frontmatter(File.read(path), path)
      if fm.nil?
        err(path, "no YAML frontmatter")
        return
      end
      err(path, "frontmatter needs a string \"name\"") unless fm["name"].is_a?(String)
      err(path, "frontmatter needs a string \"description\"") unless fm["description"].is_a?(String)
      expected = File.basename(File.dirname(path))
      if fm["name"].is_a?(String) && fm["name"] != expected
        err(path, "frontmatter name #{fm['name'].inspect} does not match its directory #{expected.inspect}")
      end
      err(path, "body is empty") if body.strip.empty?
    end

    def check_evals(evals_dir)
      unless File.directory?(evals_dir)
        err(evals_dir, "holds no eval cases")
        return
      end

      case_dirs = Dir.glob(File.join(evals_dir, "**", "")).sort.reject do |d|
        d.split(File::SEPARATOR).any? { |seg| SKIP_DIRS.include?(seg) }
      end
      case_dirs = case_dirs.select do |d|
        File.file?(File.join(d, "case.yaml")) || File.file?(File.join(d, "prompt.md"))
      end
      err(evals_dir, "holds no eval cases") if case_dirs.empty?
      case_dirs.each { |d| check_case(d.chomp(File::SEPARATOR)) }
    end

    def check_case(dir)
      yaml_path = File.join(dir, "case.yaml")
      prompt_path = File.join(dir, "prompt.md")
      spec = nil
      prompt_body = nil
      model = nil
      graders = []

      if File.file?(yaml_path)
        spec = load_yaml(File.read(yaml_path), yaml_path, "YAML")
        unless spec.is_a?(Hash)
          err(yaml_path, "must be a YAML object")
          return
        end
        err(yaml_path, "missing schema_version (e.g. \"1.1\")") unless spec["schema_version"].is_a?(String)
        err(yaml_path, "missing a non-empty \"name\"") unless spec["name"].is_a?(String) && !spec["name"].empty?
        exec = spec["execution"]
        err(yaml_path, "missing \"execution\"") unless exec.is_a?(Hash)
        if exec.is_a?(Hash)
          prompt_body = exec["prompt"]
          model = exec["model"]
        end
        if spec["graders"].is_a?(Array)
          spec["graders"].each_with_index do |g, i|
            unless g.is_a?(Hash)
              err(yaml_path, "graders[#{i}] must be a mapping")
              next
            end
            name = g["name"].is_a?(String) ? g["name"] : "graders[#{i}]"
            graders << [name, g, yaml_path]
          end
        elsif !File.directory?(File.join(dir, "graders"))
          err(yaml_path, "\"graders\" must be a non-empty array")
        end
      end

      if File.file?(prompt_path)
        fm, body = split_frontmatter(File.read(prompt_path), prompt_path)
        fm ||= {}
        fm.each_key do |key|
          err(prompt_path, "unknown frontmatter key #{key.inspect}") unless PROMPT_KEYS.include?(key.to_s)
        end
        prompt_body = body
        model ||= fm["model"]
      end

      # Unpinned, the session model is whatever the user's default alias
      # resolves to in the installed CLI, which can change between two runs.
      unless model.is_a?(String) && !model.strip.empty?
        err(dir, "pins no model — set model: in prompt.md or execution.model in case.yaml")
      end

      if prompt_body.nil? || prompt_body.to_s.strip.empty?
        err(dir, "no prompt (write it in prompt.md's body or case.yaml's execution.prompt)")
      else
        check_prose(prompt_path_for(dir), prompt_body.to_s)
      end

      graders_dir = File.join(dir, "graders")
      if File.directory?(graders_dir)
        Dir.glob(File.join(graders_dir, "*.md")).sort.each do |file|
          fm, body = split_frontmatter(File.read(file), file)
          if fm.nil?
            err(file, "no YAML frontmatter — the harness silently skips this grader")
            next
          end
          g = fm.dup
          g["name"] ||= File.basename(file, ".md")
          key = { "llm" => "criteria", "baseline" => "criteria", "regex" => "pattern" }[g["type"]]
          g[key] = body.strip if key && g[key].nil? && !body.strip.empty?
          graders << [g["name"], g, file]
        end
      end

      err(dir, "no graders") if graders.empty?

      seen = {}
      graders.each do |name, g, path|
        err(path, "duplicate grader name #{name.inspect}") if seen[name]
        seen[name] = true
        check_grader(name, g, path)
      end
    end

    def prompt_path_for(dir)
      File.file?(File.join(dir, "prompt.md")) ? File.join(dir, "prompt.md") : File.join(dir, "case.yaml")
    end

    def check_prose(path, text)
      TEMPLATE_MARKERS.each do |marker|
        err(path, "still holds the `init` template text #{marker.inspect}") if text.include?(marker)
      end
      if text.match?(%r{(?:\A|[\s(])(?:~/|/(?:Users|home|private|tmp|var)/)})
        err(path, "absolute path or ~/ in the prompt — cases run in a sandbox cwd")
      end
    end

    def check_grader(name, g, path)
      type = g["type"]
      unless GRADER_TYPES.include?(type)
        err(path, "grader #{name.inspect}: type #{type.inspect} is not one of #{GRADER_TYPES.join(' | ')}")
        return
      end
      if g.key?("arm") && !ARMS.include?(g["arm"])
        err(path, "grader #{name.inspect}: arm #{g['arm'].inspect} is not #{ARMS.join(' | ')}")
      end

      case type
      when "regex"
        pattern = g["pattern"]
        if !pattern.is_a?(String) || pattern.strip.empty?
          err(path, "grader #{name.inspect}: regex needs a pattern (the file body, or a pattern: key)")
        else
          begin
            Regexp.new(pattern)
          rescue RegexpError => e
            err(path, "grader #{name.inspect}: pattern does not compile: #{e.message}")
          end
        end
        check_focus(name, g["target"], path)
        check_match(name, g["match"], path)
      when "llm"
        if !g["criteria"].is_a?(String) || g["criteria"].strip.empty?
          err(path, "grader #{name.inspect}: llm needs criteria (the file body, or a criteria: key)")
        end
        check_focus(name, g["focus"], path)
      when "baseline"
        err(path, "grader #{name.inspect}: baseline needs baseline_file") unless g["baseline_file"].is_a?(String)
        err(path, "grader #{name.inspect}: baseline needs criteria") unless g["criteria"].is_a?(String)
      when "tool_used"
        err(path, "grader #{name.inspect}: tool_used needs a string \"tool\"") unless g["tool"].is_a?(String)
        %w[min max].each do |k|
          next unless g.key?(k)
          err(path, "grader #{name.inspect}: #{k} must be a non-negative integer") unless g[k].is_a?(Integer) && g[k] >= 0
        end
        if g["max"] == 0 && (g["min"] != 0 || g["arm"] != "both")
          err(path, "grader #{name.inspect}: a must-not-call check needs min: 0, max: 0 AND arm: both")
        end
      when "tool_order"
        %w[before after].each do |k|
          err(path, "grader #{name.inspect}: tool_order needs #{k}") if g[k].nil?
        end
      when "file_exists"
        err(path, "grader #{name.inspect}: file_exists needs a string \"path\"") unless g["path"].is_a?(String)
      end
    end

    def check_focus(name, value, path)
      return if value.nil?
      return if value.is_a?(String) && FOCI.include?(value)
      return if value.is_a?(Hash) && value["source"] == "file" && value["path"].is_a?(String)

      err(path, "grader #{name.inspect}: target/focus #{value.inspect} is not #{FOCI.join(' | ')} or {source: file, path: …}")
    end

    def check_match(name, value, path)
      return if value.nil?
      return if MATCHES.include?(value)
      return if value.is_a?(String) && value.match?(/\Acount:\d+\z/)

      err(path, "grader #{name.inspect}: match #{value.inspect} is not contains | not_contains | count:N")
    end
  end
end

if $PROGRAM_NAME == __FILE__
  root = ARGV[0] || Dir.pwd
  errors = Lint::Checker.new(root).run
  if errors.empty?
    puts "lint: ok"
    exit 0
  end
  warn "lint: #{errors.length} problem#{'s' unless errors.length == 1}"
  errors.each { |e| warn "  #{e}" }
  exit 1
end
