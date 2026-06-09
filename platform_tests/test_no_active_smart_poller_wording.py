# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Package-wide regression grep: no current-use smart-poller wording.

Per Slice 4 D6 step 32 (proposal
``bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-015.md``),
this test scans the repository source tree for live-instruction smart-poller
wording outside an explicit archive-context allowlist and fails if any
current-use match remains.

The forbidden patterns describe the smart poller as if it were the active
mechanism; post-Slice-4, that wording is misleading because the smart poller
was retired in favor of the cross-harness event-driven trigger.

REVISED-7 allowlist:
- ``groundtruth-kb/release-notes-*.md`` — frozen release evidence.
- ``groundtruth-kb/evidence/**`` — frozen historical evidence.
- ``groundtruth-kb/docs/reports/**`` — frozen historical reports.
- bridge package runtime modules (notify/paths/detector/routing/audit/
  checkpoint/registry/__init__) — retained for compatibility with adopters
  that still consume the symbols; docstrings preface with retirement note.
- ``bridge-os-poller-setup-prompt.md`` (template), ``rules/bridge-poller-canonical.md``
  (template) — DEPRECATED stubs.
- ``bridge-smart-poller.md``, ``bridge-smart-poller-activation.md``,
  ``bridge-os-scheduler.md`` (tutorials) — DEPRECATED stubs.
- ``test_bridge_poller_runner.py``, ``test_bridge_notify.py`` — historical
  test surfaces.
- ``bridge/**`` — proposal narrative artifacts (frozen by design).
- ``docs/``, ``MEMORY.md``, ``memory/**`` — historical documentation.
- ``archive/smart-poller-2026-05-09/**`` — explicit archive directory.
- ``tests/test_no_active_smart_poller_wording.py`` — this test file itself.
- ``tests/scripts/test_cross_harness_bridge_trigger.py`` — references the
  retired smart-poller's signature scheme as historical comparison.

REMOVED from allowlist (these files MUST be grep-clean post-Slice-4):
- ``groundtruth-kb/src/groundtruth_kb/project/doctor.py`` (D4 option (c) refactor).
- ``groundtruth-kb/scripts/bridge_poller_runner.py`` (D1: archived).
- ``groundtruth-kb/tests/test_doctor_smart_poller.py`` (D4: archived).
- ``groundtruth-kb/tests/test_doctor_bridge_poller.py`` (D4: renamed to
  test_doctor_bridge_dispatch_liveness.py per REVISED-7).

HISTORICAL-prefix tolerance: a comment line beginning with ``# HISTORICAL:``
or ``# HISTORICAL :`` is accepted as a deliberate historical-context marker.
The prefix must be present at the start of the comment line; bare prose
mentioning "smart poller" remains forbidden.

Maps to T-4-grep-allowlist-narrowed.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]

_PRUNE_DIRNAMES = frozenset(
    {
        ".git",
        ".groundtruth-chroma",
        ".gtkb-state",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".venv",
        "venv",
        "node_modules",
        "__pycache__",
        ".tmp",
        ".test-tmp",
        "applications",
        "worktrees",  # under .claude/worktrees
        "archive",
        ".groundtruth",
        "gtkb-state",
        ".vscode",
        ".idea",
        ".automation-tmp",
        "tools",
        "bridge",
        "docs",
        "memory",
        "independent-progress-assessments",
        "chroma",
    }
)

# Suffixes scanned. Restricting to text/source files keeps the walk fast.
_SCAN_SUFFIXES = frozenset({".py", ".md", ".toml", ".yml", ".yaml", ".json", ".txt", ".sh", ".ps1"})

# Single compiled regex covering all forbidden patterns. Each pattern is
# escaped because we want literal substring matching.

# Forbidden current-use smart-poller wording. Each pattern describes the
# smart poller as if it were active; post-Slice-4 this wording is wrong.
_FORBIDDEN_PATTERNS = (
    "verified smart poller",
    "smart-poller liveness",
    "Configure the smart poller",
    "configure the smart poller",
    "smart poller is unavailable",
    "smart poller when available",
    "smart-poller setup",
    "Smart-Poller Hook Samples",
)

# Files / paths where historical smart-poller wording is acceptable.
# Each entry is a path-suffix or path-fragment matched against the relative
# path under the repo root.
_ALLOWLIST_PATH_FRAGMENTS = (
    # Frozen release/evidence/report artifacts.
    "groundtruth-kb/release-notes-",
    "groundtruth-kb/evidence/",
    "groundtruth-kb/docs/reports/",
    # Bridge package runtime modules (compatibility-retained).
    "groundtruth-kb/src/groundtruth_kb/bridge/__init__.py",
    "groundtruth-kb/src/groundtruth_kb/bridge/audit.py",
    "groundtruth-kb/src/groundtruth_kb/bridge/checkpoint.py",
    "groundtruth-kb/src/groundtruth_kb/bridge/detector.py",
    "groundtruth-kb/src/groundtruth_kb/bridge/notify.py",
    "groundtruth-kb/src/groundtruth_kb/bridge/paths.py",
    "groundtruth-kb/src/groundtruth_kb/bridge/registry.py",
    "groundtruth-kb/src/groundtruth_kb/bridge/routing.py",
    # DEPRECATED stub templates and tutorials.
    "templates/bridge-os-poller-setup-prompt.md",
    "templates/rules/bridge-poller-canonical.md",
    "tutorials/bridge-smart-poller.md",
    "tutorials/bridge-smart-poller-activation.md",
    "tutorials/bridge-os-scheduler.md",
    # Historical test surfaces.
    "groundtruth-kb/tests/test_bridge_notify.py",
    "groundtruth-kb/tests/test_doctor_bridge_dispatch_liveness.py",
    "groundtruth-kb/tests/test_doctor_cross_harness_trigger.py",
    "groundtruth-kb/tests/test_doctor_cli_no_smart_poller_guidance.py",
    "groundtruth-kb/tests/test_slice_4_doctor_test_layout.py",
    # Bridge proposal narratives (frozen).
    "bridge/",
    # Historical documentation.
    "docs/",
    "MEMORY.md",
    "memory/",
    # Explicit archive directory.
    "archive/smart-poller-2026-05-09/",
    # Self-references (this test + the cross-harness trigger test).
    "tests/test_no_active_smart_poller_wording.py",
    "tests/scripts/test_cross_harness_bridge_trigger.py",
    # Worktree root (out-of-scope tree).
    ".claude/worktrees/",
    ".tmp/",
    "__pycache__",
    "scaffold_golden/",  # generated golden fixtures pull from templates
    # Narrative-authority files — handled by D5 (AUQ-required edits).
    "AGENTS.md",
    ".claude/rules/bridge-essential.md",
    ".claude/rules/canonical-terminology.md",
    ".claude/rules/codex-session-bootstrap.md",
    ".claude/rules/codex-way-of-working.md",
    "knowledge-export-",
    # Generated runtime cache files.
    ".claude/hooks/last-session-start.json",
    ".codex/gtkb-hooks/last-session-start.json",
    # Generated mkdocs site (build artifact).
    "groundtruth-kb/site/",
    # Historical Loyal Opposition reports + Codex bootstrap docs (frozen evidence).
    "independent-progress-assessments/",
    # System-interface-map: smart-poller entry retained with retired
    # lifecycle_state by design (provides alias resolution for historical text).
    "config/agent-control/system-interface-map.toml",
    # Cross-harness dispatcher test references retired smart-poller as
    # historical-comparison reference; the test docstring is explicit.
    "tests/scripts/test_claude_session_start_dispatcher.py",
)

# Files we don't want to scan at all (binary, compiled, generated).
_EXCLUDED_SUFFIXES = (
    ".pyc",
    ".pyo",
    ".pyd",
    ".so",
    ".dll",
    ".db",
    ".sqlite",
    ".png",
    ".jpg",
    ".gif",
    ".pdf",
    ".zip",
)

_HISTORICAL_PREFIX_RE = re.compile(r"^\s*#\s*HISTORICAL\s*:")


def _is_allowlisted(rel_path_posix: str) -> bool:
    return any(fragment in rel_path_posix for fragment in _ALLOWLIST_PATH_FRAGMENTS)


def _scannable(path: Path) -> bool:
    if path.name.lower() in {"nul", "con", "prn", "aux", "com1", "lpt1"}:
        return False
    if path.suffix.lower() not in _SCAN_SUFFIXES:
        return False
    try:
        if not path.is_file():
            return False
    except OSError:
        return False
    return True


def test_no_current_use_smart_poller_wording_in_repo() -> None:
    """No live-instruction smart-poller wording outside the allowlist."""
    offenses: list[str] = []
    for dirpath, dirnames, filenames in os.walk(_REPO_ROOT):
        # Prune large/irrelevant subtrees in-place.
        dirnames[:] = [
            d
            for d in dirnames
            if d not in _PRUNE_DIRNAMES
            and not d.startswith(".pytest")
            and not d.startswith(".tmp")
            and not d.startswith("tmp")
            and not d.startswith(".uv")
            and not d.startswith(".hypothesis")
            and "agentred" not in d.lower()
            and not d.startswith("C\uf03a")
        ]
        for fname in filenames:
            path = Path(dirpath) / fname
            if not _scannable(path):
                continue
            try:
                rel = path.relative_to(_REPO_ROOT)
            except ValueError:
                continue
            rel_posix = rel.as_posix()
            if _is_allowlisted(rel_posix):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue

            for line_no, line in enumerate(text.splitlines(), start=1):
                if _HISTORICAL_PREFIX_RE.match(line):
                    continue
                for pattern in _FORBIDDEN_PATTERNS:
                    if pattern in line:
                        offenses.append(f"{rel_posix}:{line_no}: {pattern!r} -- {line.strip()[:120]}")

    assert not offenses, (
        "Live-instruction smart-poller wording found outside the Slice 4 "
        "allowlist. Either: (a) update the offending line to reference the "
        "cross-harness event-driven trigger; (b) add an explicit "
        "'# HISTORICAL: ...' comment prefix when the historical reference is "
        "deliberate; or (c) widen the allowlist if the file is a frozen "
        "historical artifact.\n\nOffenses:\n" + "\n".join(offenses)
    )
