"""Free pre-merge gate: both manifests parse, every case matches the eval schema,
every grader names a real type. Runs on a fork PR with no secrets.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

GRADER_TYPES = ["regex", "tool_order", "tool_used", "file_exists", "llm", "baseline"]
FOCI = ["trace", "last_message", "files", "mock_calls"]
MATCHES = ["contains", "not_contains"]
ARMS = ["with-only", "both"]
PROMPT_KEYS = [
    "name", "description", "tags", "plugins", "runs", "expected_outcome",
    "model", "max_turns", "timeout_seconds", "allowed_tools", "artifact_publish",
    "growthbook_overrides", "append_system_prompt", "env",
]
TEMPLATE_MARKERS = ["TODO: describe what", "TODO: replace"]
# replay/ holds cases generated at run time; their sources live in replays/.
SKIP_DIRS = {"results", "mocks", "replay"}

_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)^---\s*\n(.*)\Z", re.DOTALL | re.MULTILINE)
_ABS_PATH_RE = re.compile(r"(?:\A|[\s(])(?:~/|/(?:Users|home|private|tmp|var)/)")
_COUNT_RE = re.compile(r"\Acount:\d+\Z")


def _inspect(value: object) -> str:
    """Ruby's String#inspect / Object#inspect, close enough for error text parity."""
    if isinstance(value, str):
        return json.dumps(value)
    if value is None:
        return "nil"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, dict):
        return "{" + ", ".join(f"{_inspect(k)}=>{_inspect(v)}" for k, v in value.items()) + "}"
    if isinstance(value, list):
        return "[" + ", ".join(_inspect(v) for v in value) + "]"
    return str(value)


class Checker:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).expanduser().resolve()
        self.errors: list[str] = []

    def run(self) -> list[str]:
        marketplace = self.root / ".claude-plugin" / "marketplace.json"
        data = self._read_json(marketplace)
        if data is None:
            return self.errors

        for key in ("name", "owner", "plugins"):
            if key not in data:
                self._err(marketplace, f"missing required key {_inspect(key)}")
        entries = data.get("plugins")
        if not isinstance(entries, list) or not entries:
            self._err(marketplace, '"plugins" must be a non-empty array')
            return self.errors

        for i, entry in enumerate(entries):
            if not (isinstance(entry, dict) and isinstance(entry.get("name"), str) and isinstance(entry.get("source"), str)):
                self._err(marketplace, f'plugins[{i}] needs string "name" and "source"')
                continue
            plugin_dir = (self.root / entry["source"]).expanduser().resolve()
            if not plugin_dir.is_dir():
                self._err(marketplace, f"plugins[{i}].source {_inspect(entry['source'])} is not a directory")
                continue
            self._check_plugin(plugin_dir, entry["name"])

        return self.errors

    # -- helpers ---------------------------------------------------------

    def _rel(self, path: str | Path) -> str:
        p = Path(path).resolve()
        try:
            return str(p.relative_to(self.root))
        except ValueError:
            return str(p)

    def _err(self, path: str | Path, message: str) -> None:
        self.errors.append(f"{self._rel(path)}: {message}")

    def _read_json(self, path: Path) -> Any:
        if not Path(path).is_file():
            self._err(path, "not found")
            return None
        try:
            return json.loads(Path(path).read_text())
        except json.JSONDecodeError as e:
            self._err(path, f"invalid JSON: {str(e).splitlines()[0].strip()}")
            return None

    def _load_yaml(self, text: str, path: Path, what: str) -> Any:
        try:
            return yaml.safe_load(text)
        except yaml.YAMLError as e:
            self._err(path, f"invalid {what}: {str(e).splitlines()[0].strip()}")
            return None

    def _split_frontmatter(self, text: str, path: Path) -> tuple[dict[str, Any] | None, str]:
        """Returns (frontmatter_or_none, body). None frontmatter means none was present."""
        m = _FRONTMATTER_RE.match(text)
        if not m:
            return None, text
        fm = self._load_yaml(m.group(1), path, "YAML frontmatter")
        return (fm if isinstance(fm, dict) else {}), m.group(2)

    def _check_plugin(self, plugin_dir: Path, entry_name: str) -> None:
        manifest = plugin_dir / ".claude-plugin" / "plugin.json"
        data = self._read_json(manifest)
        if data is None:
            return

        for key in ("name", "version", "description"):
            if not isinstance(data.get(key), str):
                self._err(manifest, f"missing required key {_inspect(key)}")
        if isinstance(data.get("name"), str) and data["name"] != entry_name:
            self._err(manifest, f"name {_inspect(data['name'])} does not match the marketplace entry {_inspect(entry_name)}")
        experimental = data.get("experimental")
        if isinstance(experimental, dict) and "evals" in experimental:
            self._err(manifest, "experimental.evals restates the evals/ default — remove it")

        for skill_file in sorted((plugin_dir / "skills").glob("*/SKILL.md")):
            self._check_skill(skill_file)
        self._check_evals(plugin_dir / "evals")

    def _check_skill(self, path: Path) -> None:
        fm, body = self._split_frontmatter(path.read_text(), path)
        if fm is None:
            self._err(path, "no YAML frontmatter")
            return
        if not isinstance(fm.get("name"), str):
            self._err(path, 'frontmatter needs a string "name"')
        if not isinstance(fm.get("description"), str):
            self._err(path, 'frontmatter needs a string "description"')
        expected = path.parent.name
        if isinstance(fm.get("name"), str) and fm["name"] != expected:
            self._err(path, f"frontmatter name {_inspect(fm['name'])} does not match its directory {_inspect(expected)}")
        if not body.strip():
            self._err(path, "body is empty")

    def _check_evals(self, evals_dir: Path) -> None:
        if not evals_dir.is_dir():
            self._err(evals_dir, "holds no eval cases")
            return

        case_dirs = sorted(
            d for d in evals_dir.rglob("*")
            if d.is_dir() and not (SKIP_DIRS & set(d.relative_to(evals_dir).parts))
        )
        case_dirs = [evals_dir, *case_dirs]
        case_dirs = [d for d in case_dirs if (d / "case.yaml").is_file() or (d / "prompt.md").is_file()]
        if not case_dirs:
            self._err(evals_dir, "holds no eval cases")
        for d in case_dirs:
            self._check_case(d)

    def _check_case(self, directory: Path) -> None:
        yaml_path = directory / "case.yaml"
        prompt_path = directory / "prompt.md"
        prompt_body: Any = None
        model: Any = None
        graders: list[tuple[str, dict[str, Any], Path]] = []

        if yaml_path.is_file():
            spec = self._load_yaml(yaml_path.read_text(), yaml_path, "YAML")
            if not isinstance(spec, dict):
                self._err(yaml_path, "must be a YAML object")
                return
            if not isinstance(spec.get("schema_version"), str):
                self._err(yaml_path, 'missing schema_version (e.g. "1.1")')
            if not (isinstance(spec.get("name"), str) and spec["name"]):
                self._err(yaml_path, 'missing a non-empty "name"')
            execution = spec.get("execution")
            if not isinstance(execution, dict):
                self._err(yaml_path, 'missing "execution"')
            else:
                prompt_body = execution.get("prompt")
                model = execution.get("model")
            if isinstance(spec.get("graders"), list):
                for i, g in enumerate(spec["graders"]):
                    if not isinstance(g, dict):
                        self._err(yaml_path, f"graders[{i}] must be a mapping")
                        continue
                    name = g["name"] if isinstance(g.get("name"), str) else f"graders[{i}]"
                    graders.append((name, g, yaml_path))
            elif not (directory / "graders").is_dir():
                self._err(yaml_path, '"graders" must be a non-empty array')

        if prompt_path.is_file():
            fm, body = self._split_frontmatter(prompt_path.read_text(), prompt_path)
            fm = fm or {}
            for key in fm:
                if str(key) not in PROMPT_KEYS:
                    self._err(prompt_path, f"unknown frontmatter key {_inspect(str(key))}")
            prompt_body = body
            if model is None:
                model = fm.get("model")

        # Unpinned, the session model is whatever the user's default alias
        # resolves to in the installed CLI, which can change between two runs.
        if not (isinstance(model, str) and model.strip()):
            self._err(directory, "pins no model — set model: in prompt.md or execution.model in case.yaml")

        prompt_report_path = prompt_path if prompt_path.is_file() else yaml_path
        if prompt_body is None or not str(prompt_body).strip():
            self._err(directory, "no prompt (write it in prompt.md's body or case.yaml's execution.prompt)")
        else:
            self._check_prose(prompt_report_path, str(prompt_body))

        graders_dir = directory / "graders"
        if graders_dir.is_dir():
            for file in sorted(graders_dir.glob("*.md")):
                fm, body = self._split_frontmatter(file.read_text(), file)
                if fm is None:
                    self._err(file, "no YAML frontmatter — the harness silently skips this grader")
                    continue
                g = dict(fm)
                if not g.get("name"):
                    g["name"] = file.stem
                # Which key a grader file's body fills, per type; evals/sources.py reads bodies the same way.
                gtype = g.get("type")
                body_key = {"llm": "criteria", "baseline": "criteria", "regex": "pattern"}.get(gtype) if isinstance(gtype, str) else None
                if body_key and g.get(body_key) is None and body.strip():
                    g[body_key] = body.strip()
                graders.append((g["name"], g, file))

        if not graders:
            self._err(directory, "no graders")

        seen: set[str] = set()
        for name, g, path in graders:
            if name in seen:
                self._err(path, f"duplicate grader name {_inspect(name)}")
            seen.add(name)
            self._check_grader(name, g, path)

    def _check_prose(self, path: Path, text: str) -> None:
        for marker in TEMPLATE_MARKERS:
            if marker in text:
                self._err(path, f"still holds the `init` template text {_inspect(marker)}")
        if _ABS_PATH_RE.search(text):
            self._err(path, "absolute path or ~/ in the prompt — cases run in a sandbox cwd")

    def _check_grader(self, name: str, g: dict[str, Any], path: Path) -> None:
        gtype = g.get("type")
        if gtype not in GRADER_TYPES:
            self._err(path, f"grader {_inspect(name)}: type {_inspect(gtype)} is not one of {' | '.join(GRADER_TYPES)}")
            return
        if "arm" in g and g["arm"] not in ARMS:
            self._err(path, f"grader {_inspect(name)}: arm {_inspect(g['arm'])} is not {' | '.join(ARMS)}")

        if gtype == "regex":
            pattern = g.get("pattern")
            if not (isinstance(pattern, str) and pattern.strip()):
                self._err(path, f"grader {_inspect(name)}: regex needs a pattern (the file body, or a pattern: key)")
            else:
                try:
                    re.compile(pattern)
                except re.error as e:
                    self._err(path, f"grader {_inspect(name)}: pattern does not compile: {e}")
            self._check_focus(name, g.get("target"), path)
            self._check_match(name, g.get("match"), path)
        elif gtype == "llm":
            if not (isinstance(g.get("criteria"), str) and g["criteria"].strip()):
                self._err(path, f"grader {_inspect(name)}: llm needs criteria (the file body, or a criteria: key)")
            self._check_focus(name, g.get("focus"), path)
        elif gtype == "baseline":
            if not isinstance(g.get("baseline_file"), str):
                self._err(path, f"grader {_inspect(name)}: baseline needs baseline_file")
            if not isinstance(g.get("criteria"), str):
                self._err(path, f"grader {_inspect(name)}: baseline needs criteria")
        elif gtype == "tool_used":
            if not isinstance(g.get("tool"), str):
                self._err(path, f"grader {_inspect(name)}: tool_used needs a string \"tool\"")
            for k in ("min", "max"):
                if k in g and not (isinstance(g[k], int) and not isinstance(g[k], bool) and g[k] >= 0):
                    self._err(path, f"grader {_inspect(name)}: {k} must be a non-negative integer")
            if g.get("max") == 0 and (g.get("min") != 0 or g.get("arm") != "both"):
                self._err(path, f"grader {_inspect(name)}: a must-not-call check needs min: 0, max: 0 AND arm: both")
        elif gtype == "tool_order":
            for k in ("before", "after"):
                if g.get(k) is None:
                    self._err(path, f"grader {_inspect(name)}: tool_order needs {k}")
        elif gtype == "file_exists":
            if not isinstance(g.get("path"), str):
                self._err(path, f"grader {_inspect(name)}: file_exists needs a string \"path\"")

    def _check_focus(self, name: str, value: Any, path: Path) -> None:
        if value is None:
            return
        if isinstance(value, str) and value in FOCI:
            return
        if isinstance(value, dict) and value.get("source") == "file" and isinstance(value.get("path"), str):
            return
        self._err(path, f"grader {_inspect(name)}: target/focus {_inspect(value)} is not {' | '.join(FOCI)} or {{source: file, path: …}}")

    def _check_match(self, name: str, value: Any, path: Path) -> None:
        if value is None:
            return
        if value in MATCHES:
            return
        if isinstance(value, str) and _COUNT_RE.match(value):
            return
        self._err(path, f"grader {_inspect(name)}: match {_inspect(value)} is not contains | not_contains | count:N")


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    root = argv[0] if argv else "."
    errors = Checker(root).run()
    if not errors:
        print("lint: ok")
        return 0
    plural = "" if len(errors) == 1 else "s"
    print(f"lint: {len(errors)} problem{plural}", file=sys.stderr)
    for e in errors:
        print(f"  {e}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
