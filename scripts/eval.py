#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6"]
# ///
"""Run a plugin's eval suite with replay cases regenerated from the current SKILL.md.

Usage: uv run scripts/eval.py <plugin dir> [claude plugin eval options, except --ablation]
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "evals"))

from wrapper import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
