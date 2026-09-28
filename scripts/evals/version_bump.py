"""PR gate: a change to what a plugin ships must change its plugin.json version.

Claude Code detects an update only when the version string changes, so a
shipped change without a bump never reaches users on the GitHub marketplace.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path, PurePosixPath

# Paths inside a plugin that do not change what users run.
DEV_ONLY = {"evals", "replays", "README.md"}


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True).stdout


def _version_at(root: Path, rev: str, manifest: str) -> str | None:
    try:
        data = json.loads(_git(root, "show", f"{rev}:{manifest}"))
    except subprocess.CalledProcessError:
        return None
    version = data.get("version")
    return version if isinstance(version, str) else None


def check(root: str | Path, base: str) -> list[str]:
    root = Path(root)
    # The merge base, not the base tip: a bump landing on main after the branch
    # point says nothing about whether this branch bumped.
    fork = _git(root, "merge-base", base, "HEAD").strip()
    marketplace = json.loads((root / ".claude-plugin" / "marketplace.json").read_text())
    errors = []
    for entry in marketplace["plugins"]:
        source = PurePosixPath(entry["source"])
        manifest = str(source / ".claude-plugin" / "plugin.json")
        old = _version_at(root, fork, manifest)
        if old is None:
            continue
        changed = [
            str(PurePosixPath(p).relative_to(source))
            for p in _git(root, "diff", "--name-only", fork, "HEAD", "--", str(source)).splitlines()
        ]
        shipped = [p for p in changed if PurePosixPath(p).parts[0] not in DEV_ONLY]
        if shipped and _version_at(root, "HEAD", manifest) == old:
            listed = ", ".join(shipped[:3]) + (", ..." if len(shipped) > 3 else "")
            errors.append(f"{entry['name']}: {listed} changed but version is still {old}; bump it in {manifest}")
    return errors


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    base = argv[0] if argv else "origin/main"
    errors = check(".", base)
    if not errors:
        print("version check: ok")
        return 0
    for e in errors:
        print(e, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
