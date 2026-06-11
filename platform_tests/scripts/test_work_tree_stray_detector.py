"""Tests for scripts.hygiene.stray_detector (Slice A of WI-4356).

Covers the eight test categories required by the Slice A GO verdict at
bridge/gtkb-work-tree-hygiene-slice-a-detector-002.md:

1. stale tracked edits
2. stale untracked files
3. recent work below the threshold
4. active-session exclusions
5. stash age boundaries around the twelve-hour threshold
6. unique-content flags
7. JSON-serializable output
8. no subprocess execution and no repository/stash mutation API

Tests inject deterministic clocks and synthetic inputs; nothing in this
module touches git, subprocess, the real filesystem, or the live stash.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import ast
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from scripts.hygiene.stray_detector import (
    STALE_THRESHOLD_HOURS,
    ActiveSessionContext,
    StashEntry,
    WorkspaceEntry,
    WorktreeEntry,
    classify_stash_entries,
    classify_stash_entry,
    classify_workspace_entries,
    classify_workspace_entry,
    classify_worktree_entries,
    classify_worktree_entry,
    detect_strays,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def now() -> datetime:
    return datetime(2026, 6, 5, 12, 0, 0, tzinfo=UTC)


def _hours_ago(now: datetime, hours: float) -> datetime:
    return now - timedelta(hours=hours)


# ---------------------------------------------------------------------------
# Category 1: stale tracked edits
# ---------------------------------------------------------------------------


def test_stale_tracked_edit_is_classified_stale(now: datetime) -> None:
    entry = WorkspaceEntry(
        path="src/feature.py",
        last_modified=_hours_ago(now, 24),
        tracked=True,
    )

    finding = classify_workspace_entry(entry, now=now)

    assert finding.classification == "stale"
    assert finding.tracked is True
    assert finding.triage_reason == "stale_tracked_edit_over_threshold"
    assert finding.candidate_action == "owner_review_stale_tracked_edit"
    assert finding.age_hours == pytest.approx(24.0)


# ---------------------------------------------------------------------------
# Category 2: stale untracked files
# ---------------------------------------------------------------------------


def test_stale_untracked_file_is_classified_stale(now: datetime) -> None:
    entry = WorkspaceEntry(
        path="scratch/temp_notes.md",
        last_modified=_hours_ago(now, 13),
        tracked=False,
    )

    finding = classify_workspace_entry(entry, now=now)

    assert finding.classification == "stale"
    assert finding.tracked is False
    assert finding.triage_reason == "stale_untracked_stray_over_threshold"
    assert finding.candidate_action == "owner_review_stale_untracked_file"


# ---------------------------------------------------------------------------
# Category 3: recent work below the threshold
# ---------------------------------------------------------------------------


def test_recent_tracked_edit_is_classified_recent(now: datetime) -> None:
    entry = WorkspaceEntry(
        path="src/feature.py",
        last_modified=_hours_ago(now, 6),
        tracked=True,
    )

    finding = classify_workspace_entry(entry, now=now)

    assert finding.classification == "recent"
    assert finding.triage_reason == "below_stale_threshold"
    assert finding.candidate_action == "skip"


def test_workspace_boundary_just_under_threshold_is_recent(now: datetime) -> None:
    entry = WorkspaceEntry(
        path="src/edge.py",
        last_modified=now - timedelta(hours=11, minutes=59, seconds=59),
        tracked=True,
    )

    finding = classify_workspace_entry(entry, now=now)

    assert finding.classification == "recent"


def test_workspace_boundary_exactly_at_threshold_is_stale(now: datetime) -> None:
    """Boundary policy: at-or-over threshold = stale, strictly under = recent."""
    entry = WorkspaceEntry(
        path="src/edge.py",
        last_modified=now - timedelta(hours=STALE_THRESHOLD_HOURS),
        tracked=True,
    )

    finding = classify_workspace_entry(entry, now=now)

    assert finding.classification == "stale"


# ---------------------------------------------------------------------------
# Category 4: active-session exclusions
# ---------------------------------------------------------------------------


def test_active_session_workspace_path_excluded_from_stale(now: datetime) -> None:
    entry = WorkspaceEntry(
        path="src/in_use.py",
        last_modified=_hours_ago(now, 48),  # Very old
        tracked=True,
    )
    active = ActiveSessionContext(workspace_paths=frozenset({"src/in_use.py"}))

    finding = classify_workspace_entry(entry, now=now, active_session=active)

    assert finding.classification == "active_session"
    assert finding.triage_reason == "active_session_holds_path"
    assert finding.candidate_action == "skip"


def test_active_session_stash_ref_excluded_from_stale(now: datetime) -> None:
    entry = StashEntry(
        stash_ref="stash@{0}",
        created_at=_hours_ago(now, 72),
        subject="WIP: in-progress session work",
    )
    active = ActiveSessionContext(stash_refs=frozenset({"stash@{0}"}))

    finding = classify_stash_entry(entry, now=now, active_session=active)

    assert finding.classification == "active_session"
    assert finding.triage_reason == "active_session_holds_stash"
    assert finding.candidate_action == "skip"


# ---------------------------------------------------------------------------
# Category 5: stash age boundaries around the twelve-hour threshold
# ---------------------------------------------------------------------------


def test_stash_just_under_threshold_is_recent(now: datetime) -> None:
    entry = StashEntry(
        stash_ref="stash@{1}",
        created_at=now - timedelta(hours=11, minutes=59, seconds=59),
        subject="recent work",
    )

    finding = classify_stash_entry(entry, now=now)

    assert finding.classification == "recent"


def test_stash_exactly_at_threshold_is_stale(now: datetime) -> None:
    entry = StashEntry(
        stash_ref="stash@{2}",
        created_at=now - timedelta(hours=STALE_THRESHOLD_HOURS),
        subject="boundary",
    )

    finding = classify_stash_entry(entry, now=now)

    assert finding.classification == "stale"
    assert finding.triage_reason == "stale_stash_over_threshold"
    assert finding.candidate_action == "owner_review_stale_stash"


def test_stash_well_past_threshold_is_stale(now: datetime) -> None:
    entry = StashEntry(
        stash_ref="stash@{3}",
        created_at=_hours_ago(now, 100),
        subject="ancient",
    )

    finding = classify_stash_entry(entry, now=now)

    assert finding.classification == "stale"


# ---------------------------------------------------------------------------
# Category 5b: orphaned worktree staleness (FAB-04, HYG-057)
# ---------------------------------------------------------------------------


def test_stale_orphaned_worktree_is_detected(now: datetime) -> None:
    """A non-registered .claude/worktrees/* dir over threshold is a reap candidate."""
    entry = WorktreeEntry(
        path=".claude/worktrees/stale-checkout",
        last_modified=_hours_ago(now, 30),
        git_registered=False,
    )

    finding = classify_worktree_entry(entry, now=now)

    assert finding.classification == "stale"
    assert finding.git_registered is False
    assert finding.triage_reason == "stale_orphaned_worktree_over_threshold"
    assert finding.candidate_action == "prune_and_delete_orphaned_worktree"


def test_git_registered_worktree_is_never_reaped(now: datetime) -> None:
    """A live, git-registered worktree is preserved regardless of age."""
    entry = WorktreeEntry(
        path="../external-registered-worktree",
        last_modified=_hours_ago(now, 500),
        git_registered=True,
    )

    finding = classify_worktree_entry(entry, now=now)

    assert finding.classification == "registered"
    assert finding.triage_reason == "git_registered_worktree"
    assert finding.candidate_action == "skip"


def test_active_session_worktree_excluded_from_stale(now: datetime) -> None:
    entry = WorktreeEntry(
        path=".claude/worktrees/in-use",
        last_modified=_hours_ago(now, 48),
        git_registered=False,
    )
    active = ActiveSessionContext(workspace_paths=frozenset({".claude/worktrees/in-use"}))

    finding = classify_worktree_entry(entry, now=now, active_session=active)

    assert finding.classification == "active_session"
    assert finding.triage_reason == "active_session_holds_worktree"
    assert finding.candidate_action == "skip"


def test_recent_orphaned_worktree_is_recent(now: datetime) -> None:
    entry = WorktreeEntry(
        path=".claude/worktrees/fresh",
        last_modified=_hours_ago(now, 2),
        git_registered=False,
    )

    finding = classify_worktree_entry(entry, now=now)

    assert finding.classification == "recent"
    assert finding.candidate_action == "skip"


def test_worktree_boundary_exactly_at_threshold_is_stale(now: datetime) -> None:
    entry = WorktreeEntry(
        path=".claude/worktrees/boundary",
        last_modified=now - timedelta(hours=STALE_THRESHOLD_HOURS),
        git_registered=False,
    )

    finding = classify_worktree_entry(entry, now=now)

    assert finding.classification == "stale"


def test_classify_worktree_entries_preserves_order(now: datetime) -> None:
    entries = [
        WorktreeEntry(
            path=f".claude/worktrees/w{i}",
            last_modified=_hours_ago(now, 24),
            git_registered=False,
        )
        for i in range(4)
    ]

    findings = classify_worktree_entries(entries, now=now)

    assert [f.path for f in findings] == [f".claude/worktrees/w{i}" for i in range(4)]


def test_detect_strays_surfaces_stale_worktree(now: datetime) -> None:
    """detect_strays carries the worktree category and counts a stale orphan."""
    worktrees = [
        WorktreeEntry(
            path=".claude/worktrees/orphan",
            last_modified=_hours_ago(now, 30),
            git_registered=False,
        ),
        WorktreeEntry(
            path="../registered",
            last_modified=_hours_ago(now, 30),
            git_registered=True,
        ),
        WorktreeEntry(
            path=".claude/worktrees/fresh",
            last_modified=_hours_ago(now, 1),
            git_registered=False,
        ),
    ]

    report = detect_strays(
        now=now,
        workspace_entries=[],
        stash_entries=[],
        worktree_entries=worktrees,
    )

    # Round-trips through json and reports the stale orphan distinctly.
    restored = json.loads(json.dumps(report))
    assert restored["counts"]["worktree_total"] == 3
    assert restored["counts"]["worktree_stale"] == 1
    assert restored["counts"]["worktree_registered"] == 1
    assert restored["counts"]["worktree_recent"] == 1
    stale = [f for f in restored["worktree_findings"] if f["classification"] == "stale"]
    assert len(stale) == 1
    assert stale[0]["path"] == ".claude/worktrees/orphan"
    assert stale[0]["candidate_action"] == "prune_and_delete_orphaned_worktree"


def test_detect_strays_worktree_param_defaults_empty(now: datetime) -> None:
    """Existing callers that omit worktree_entries keep working (backward compat)."""
    report = detect_strays(now=now, workspace_entries=[], stash_entries=[])

    assert report["counts"]["worktree_total"] == 0
    assert report["worktree_findings"] == []


# ---------------------------------------------------------------------------
# Category 6: unique-content flags
# ---------------------------------------------------------------------------


def test_unique_content_flag_true_when_hash_appears_once(now: datetime) -> None:
    entries = [
        WorkspaceEntry(
            path="src/unique.py",
            last_modified=_hours_ago(now, 24),
            tracked=False,
            content_hash="sha256:aaa",
        ),
        WorkspaceEntry(
            path="src/other.py",
            last_modified=_hours_ago(now, 24),
            tracked=False,
            content_hash="sha256:bbb",
        ),
    ]

    findings = classify_workspace_entries(entries, now=now)

    by_path = {f.path: f for f in findings}
    assert by_path["src/unique.py"].unique_content is True
    assert by_path["src/other.py"].unique_content is True


def test_unique_content_flag_false_when_hash_duplicated(now: datetime) -> None:
    entries = [
        WorkspaceEntry(
            path="src/a.py",
            last_modified=_hours_ago(now, 24),
            tracked=False,
            content_hash="sha256:dup",
        ),
        WorkspaceEntry(
            path="src/b.py",
            last_modified=_hours_ago(now, 24),
            tracked=False,
            content_hash="sha256:dup",
        ),
    ]

    findings = classify_workspace_entries(entries, now=now)

    assert all(f.unique_content is False for f in findings)


def test_unique_content_flag_none_when_no_hash_supplied(now: datetime) -> None:
    entry = WorkspaceEntry(
        path="src/no_hash.py",
        last_modified=_hours_ago(now, 24),
        tracked=False,
        content_hash=None,
    )

    finding = classify_workspace_entry(entry, now=now)

    assert finding.unique_content is None


# ---------------------------------------------------------------------------
# Category 7: JSON-serializable output
# ---------------------------------------------------------------------------


def test_detect_strays_output_is_json_serializable(now: datetime) -> None:
    workspace = [
        WorkspaceEntry(
            path="src/stale.py",
            last_modified=_hours_ago(now, 18),
            tracked=True,
            content_hash="sha256:xyz",
        ),
        WorkspaceEntry(
            path="src/recent.py",
            last_modified=_hours_ago(now, 1),
            tracked=True,
        ),
    ]
    stashes = [
        StashEntry(
            stash_ref="stash@{0}",
            created_at=_hours_ago(now, 24),
            subject="stale stash",
        ),
    ]
    active = ActiveSessionContext(workspace_paths=frozenset(), stash_refs=frozenset())

    report = detect_strays(
        now=now,
        workspace_entries=workspace,
        stash_entries=stashes,
        active_session=active,
    )

    # Must round-trip through json without TypeError.
    serialized = json.dumps(report)
    restored = json.loads(serialized)

    assert restored["threshold_hours"] == STALE_THRESHOLD_HOURS
    assert restored["counts"]["workspace_total"] == 2
    assert restored["counts"]["workspace_stale"] == 1
    assert restored["counts"]["workspace_recent"] == 1
    assert restored["counts"]["stash_total"] == 1
    assert restored["counts"]["stash_stale"] == 1
    assert isinstance(restored["workspace_findings"], list)
    assert isinstance(restored["stash_findings"], list)
    # generated_at carries timezone information.
    assert restored["generated_at"].endswith("+00:00")


def test_detect_strays_handles_empty_input(now: datetime) -> None:
    report = detect_strays(
        now=now,
        workspace_entries=[],
        stash_entries=[],
    )

    json.dumps(report)  # Round-trip without error.
    assert report["counts"]["workspace_total"] == 0
    assert report["counts"]["stash_total"] == 0
    assert report["workspace_findings"] == []
    assert report["stash_findings"] == []


# ---------------------------------------------------------------------------
# Category 8: no subprocess execution and no repository/stash mutation API
# ---------------------------------------------------------------------------


_DETECTOR_SOURCE = Path(__file__).resolve().parents[2] / "scripts" / "hygiene" / "stray_detector.py"

_FORBIDDEN_MODULES = frozenset(
    {
        "subprocess",
        "shutil",
        "shlex",
        "pexpect",
        "fabric",
        "invoke",
        "git",
        "pygit2",
        "dulwich",
    }
)

_FORBIDDEN_OS_ATTRS = frozenset(
    {
        "remove",
        "unlink",
        "removedirs",
        "rmdir",
        "system",
        "popen",
        "execv",
        "execvp",
        "execve",
        "execvpe",
        "spawnl",
        "spawnle",
        "spawnv",
        "spawnvp",
        "spawnve",
        "spawnvpe",
    }
)


def test_detector_source_imports_no_subprocess_or_git_modules() -> None:
    tree = ast.parse(_DETECTOR_SOURCE.read_text(encoding="utf-8"))

    forbidden_imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in _FORBIDDEN_MODULES:
                    forbidden_imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if root in _FORBIDDEN_MODULES:
                forbidden_imports.append(node.module or "")

    assert forbidden_imports == [], f"Detector must remain read-only; forbidden imports detected: {forbidden_imports}"


def test_detector_source_uses_no_mutating_os_or_path_calls() -> None:
    tree = ast.parse(_DETECTOR_SOURCE.read_text(encoding="utf-8"))

    forbidden_calls: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr in _FORBIDDEN_OS_ATTRS:
            forbidden_calls.append(node.attr)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in {"open"}:
                # `open` is permitted only if absent; the detector has none.
                forbidden_calls.append("open")

    assert forbidden_calls == [], (
        f"Detector must remain read-only; mutation-shaped or IO calls detected: {forbidden_calls}"
    )


def test_detector_rejects_naive_datetimes(now: datetime) -> None:
    """Naive timestamps could mask UTC drift; the detector fails closed."""
    naive_now = datetime(2026, 6, 5, 12, 0, 0)  # No tzinfo.

    with pytest.raises(ValueError, match="timezone-aware"):
        classify_workspace_entry(
            WorkspaceEntry(
                path="src/x.py",
                last_modified=_hours_ago(now, 1),
                tracked=True,
            ),
            now=naive_now,
        )


# ---------------------------------------------------------------------------
# List-level classifiers cover ordering and pass-through of context.
# ---------------------------------------------------------------------------


def test_classify_workspace_entries_preserves_order(now: datetime) -> None:
    entries = [WorkspaceEntry(path=f"src/f{i}.py", last_modified=_hours_ago(now, 24), tracked=False) for i in range(5)]

    findings = classify_workspace_entries(entries, now=now)

    assert [f.path for f in findings] == [f"src/f{i}.py" for i in range(5)]


def test_classify_stash_entries_preserves_order(now: datetime) -> None:
    entries = [StashEntry(stash_ref=f"stash@{{{i}}}", created_at=_hours_ago(now, 24)) for i in range(3)]

    findings = classify_stash_entries(entries, now=now)

    assert [f.stash_ref for f in findings] == [f"stash@{{{i}}}" for i in range(3)]
