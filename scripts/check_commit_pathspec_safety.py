#!/usr/bin/env python3
"""Detect the bridge+source staged-index contamination signature (WI-4464).

Background governance hooks can stage bridge audit files into the git index
between tool calls. A plain ``git commit`` *without* an explicit ``-- <pathspec>``
then commits whatever the index holds rather than the intended files. On
2026-06-11 this produced mislabeled commit ``772a186b`` — a FAB-20 commit
message carrying unrelated backlog-triage + prefix-split contents while the
intended FAB-20 files stayed uncommitted. Full forensics:
``memory/recovery-2026-06-11-fab20-commit-collision.md``.

This is Slice A of WI-4464 mitigation (a): the *tested detection mechanism*.
It classifies the staged index and flags the contamination signature — a
staged set that mixes bridge-queue files with non-bridge ``other`` files,
which is also a standing protocol violation per
``.claude/rules/bridge-essential.md`` ("Scoped commits only").

Slice A performs NO commit-path / hook / config wiring. It is a self-contained,
independently runnable + unit-tested mechanism. Advisory mode (the default)
NEVER blocks a commit (exit 0); ``--strict`` is the opt-in enforcement mode
(exit 3 on contamination) reserved for future wiring / CI use.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys

# Bridge-queue match rule (documented module constant so the deferred wiring
# slice and any future tuning are explicit). The canonical bridge queue evidence
# surface is top-level status-bearing numbered markdown files. The matcher is
# deliberately conservative: nested paths, non-markdown paths, and unversioned
# bridge markdown are classified as ``other`` so the detector never accepts a
# resurrected retired aggregate as valid review evidence.
BRIDGE_QUEUE_PATTERN = re.compile(r"^bridge/[^/]+-\d{3}\.md$")

# Distinct non-zero exit code for --strict contamination (kept stable so future
# wiring / CI can branch on it without colliding with argparse's exit 2).
STRICT_CONTAMINATION_EXIT = 3


def _normalize(name: str) -> str:
    """Normalize a staged path: strip whitespace, backslashes -> forward."""

    return name.strip().replace("\\", "/")


def classify_staged(names: list[str]) -> dict:
    """Partition staged path names into bridge-queue vs other (pure function).

    No git, no I/O. Returns a dict with sorted, de-duplicated partitions:

        {"mixed": bool, "bridge_queue": [...], "other": [...]}

    ``mixed`` is True iff BOTH partitions are non-empty — the contamination
    signature the detector targets.
    """

    bridge_queue: set[str] = set()
    other: set[str] = set()
    for raw in names:
        rel = _normalize(raw)
        if not rel:
            continue
        if BRIDGE_QUEUE_PATTERN.match(rel):
            bridge_queue.add(rel)
        else:
            other.add(rel)

    return {
        "mixed": bool(bridge_queue) and bool(other),
        "bridge_queue": sorted(bridge_queue),
        "other": sorted(other),
    }


def _staged_names() -> list[str]:
    """Return staged path names via ``git diff --cached`` (read-only).

    Isolated in its own function so tests can bypass git entirely. Fail-open:
    any subprocess error, missing git, or non-repo returns ``[]`` so the
    detector can never break a commit.
    """

    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    return [line for line in (ln.strip() for ln in result.stdout.splitlines()) if line]


def _format_warning(result: dict) -> str:
    """Build the multi-line advisory warning for a contaminated staged set."""

    lines = [
        "WARNING: commit pathspec-safety — staged index mixes bridge-queue and source files.",
        "",
        "  Bridge-queue files staged:",
    ]
    lines.extend(f"    - {path}" for path in result["bridge_queue"])
    lines.append("  Other (non-bridge) files staged:")
    lines.extend(f"    - {path}" for path in result["other"])
    lines.extend(
        [
            "",
            "  Background governance hooks auto-stage bridge-queue files between tool",
            "  calls. A plain `git commit` (no pathspec) would commit this mixed set,",
            "  producing a mislabeled / wrongly-scoped commit.",
            "  Commit with an explicit pathspec instead, e.g.:",
            '    git commit -- <your-intended-files> -m "..."',
            "  See: memory/recovery-2026-06-11-fab20-commit-collision.md",
            '  Protocol: .claude/rules/bridge-essential.md ("Scoped commits only").',
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    raw_argv = sys.argv[1:] if argv is None else list(argv)
    parser = argparse.ArgumentParser(description="Detect bridge+source staged-index contamination (WI-4464).")
    parser.add_argument(
        "--staged",
        action="store_true",
        help="Read staged path names from `git diff --cached` (read-only).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help=f"Exit {STRICT_CONTAMINATION_EXIT} on contamination instead of exit 0 (opt-in enforcement).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON to stdout; always exit 0.",
    )
    args = parser.parse_args(raw_argv)

    names = _staged_names() if args.staged else []
    result = classify_staged(names)

    if args.json:
        sys.stdout.write(json.dumps(result, indent=2, sort_keys=True))
        sys.stdout.write("\n")
        return 0

    if not result["mixed"]:
        # Clean / empty staged set: silent, fail-open.
        return 0

    sys.stderr.write(_format_warning(result))
    sys.stderr.write("\n")

    if args.strict:
        return STRICT_CONTAMINATION_EXIT
    return 0


if __name__ == "__main__":
    sys.exit(main())
