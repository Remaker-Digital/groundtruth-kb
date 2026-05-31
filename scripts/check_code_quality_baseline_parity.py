#!/usr/bin/env python3
"""Fallback verifier for Code Quality Baseline tables in bridge proposals."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from groundtruth_kb.hooks.code_quality_baseline_proposal_check import validate  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--since", default=None)
    parser.add_argument("--since-tag", default=None)
    parser.add_argument("paths", nargs="*", default=["bridge"])
    args = parser.parse_args()
    findings: list[str] = []
    for raw_path in args.paths:
        path = PROJECT_ROOT / raw_path
        files = [path] if path.is_file() else sorted(path.rglob("*.md"))
        for file_path in files:
            text = file_path.read_text(encoding="utf-8")
            if "bridge_kind: implementation_proposal" not in text:
                continue
            for finding in validate(text):
                findings.append(f"{file_path.relative_to(PROJECT_ROOT)}: {finding.code}: {finding.message}")
    if findings:
        print("\n".join(findings))
        return 1
    print("Code Quality Baseline parity clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
