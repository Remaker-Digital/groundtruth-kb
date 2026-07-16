"""Regression guard: skill helper directories must not track scratch artifacts.

WI-3459 release hygiene removes completed bridge/verdict working drafts from
canonical and generated skill helper directories. Helper directories are loaded
as reusable capability surfaces, so tracked one-off report bodies, draft
verdicts, temporary verdict bodies, and Python cache files create
canonical-looking non-authoritative context.

Spec-to-test mapping:
  GOV-FILE-BRIDGE-AUTHORITY-001:
      This test and the WI-3459 implementation report form durable evidence
      for the governed helper cleanup.
  DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001:
      The bridge proposal requires an executed guard against recurring tracked
      helper scratch artifacts.
  ADR-CROSS-HARNESS-PARITY-001 / DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001:
      The guard covers both canonical Claude skill helpers and generated Codex
      mirrors so parity surfaces stay clean.
  ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001:
      Completed one-off bridge/verdict working material belongs in bridge
      artifacts or implementation reports, not reusable skill helper paths.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

HELPER_ROOTS = (".claude/skills/", ".codex/skills/")
SCRATCH_NAME_PATTERN = re.compile(
    r"(^|/)(?:"
    r"draft-[^/]+\.md|"
    r"_temp[^/]*\.md|"
    r"[^/]+-(?:body|draft|final)\.md|"
    r"__pycache__(?:/|$)|"
    r"[^/]+\.pyc$"
    r")"
)


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_no_tracked_skill_helper_scratch_artifacts() -> None:
    """Tracked helper paths must not include one-off drafts or cache files."""
    project_root = _project_root()
    result = subprocess.run(
        ["git", "ls-files"],
        capture_output=True,
        text=True,
        cwd=project_root,
    )
    assert result.returncode == 0, f"git ls-files failed with exit {result.returncode}: {result.stderr}"

    offenders = []
    for path in result.stdout.splitlines():
        normalized = path.replace("\\", "/")
        if "/helpers/" not in normalized:
            continue
        if not normalized.startswith(HELPER_ROOTS):
            continue
        if SCRATCH_NAME_PATTERN.search(normalized):
            offenders.append(normalized)

    assert offenders == [], (
        "Tracked scratch artifacts found under skill helper directories. "
        "Move reusable helper code to a stable helper filename, and keep "
        "one-off bridge/verdict drafts in governed bridge/report artifacts. "
        "Offending paths:\n  " + "\n  ".join(sorted(offenders))
    )
