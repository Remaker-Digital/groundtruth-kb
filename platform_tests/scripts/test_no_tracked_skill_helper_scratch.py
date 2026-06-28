"""Regression guard: skill helper directories must not carry tracked scratch artifacts.

WI-3459 closure guard: completed verdict/report scratch files must not remain in
the git index under canonical or Codex skill helper surfaces.

Spec-to-test mapping:
  GOV-FILE-BRIDGE-AUTHORITY-001:
      Durable lifecycle evidence for bridge-governed skill adapter hygiene.
  DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001:
      Tests derive from the WI-3459 bridge verification plan.
  ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 / DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001:
      Completed scratch artifacts must not masquerade as reusable helper source.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

HELPER_ROOTS = (
    ".claude/skills/",
    ".codex/skills/",
)

SCRATCH_PATTERN = re.compile(r"/helpers/gtkb-[^/]+-(?:body|draft|final)\.md$")


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _tracked_helper_paths() -> list[str]:
    project_root = _project_root()
    result = subprocess.run(
        ["git", "ls-files"],
        capture_output=True,
        text=True,
        cwd=project_root,
    )
    assert result.returncode == 0, result.stderr
    tracked: list[str] = []
    for line in result.stdout.splitlines():
        normalized = line.replace("\\", "/")
        if not any(normalized.startswith(root) for root in HELPER_ROOTS):
            continue
        if "/helpers/" not in normalized:
            continue
        tracked.append(normalized)
    return tracked


def test_no_tracked_skill_helper_scratch_artifacts() -> None:
    """Tracked helper paths must not match verdict-body/draft/final/temp scratch patterns."""
    offenders = [path for path in _tracked_helper_paths() if SCRATCH_PATTERN.search(path)]
    assert offenders == [], (
        "Tracked skill-helper scratch artifacts found in the git index. "
        "Remove them with `git rm --cached <path>` after deleting the workspace copy. "
        "Offending paths:\n  " + "\n  ".join(offenders)
    )
