"""Stale work-tree and stash stray detector (Slice A of WI-4356).

Read-only classifier module: accepts dataclass inputs and a clock value,
returns JSON-serializable findings describing stale workspace edits and
stale stash entries. Performs NO subprocess execution, NO git or stash
mutation, NO filesystem traversal. Callers supply fresh state per
GOV-SOURCE-OF-TRUTH-FRESHNESS-001; the detector consumes what it is
given and renders a verdict.

Owner directive (WI-4356, DELIB-20260867): agents cannot be expected to
return after twelve hours, so work older than the twelve-hour threshold
is stale and a candidate for triage by a different agent.

Bridge: bridge/gtkb-work-tree-hygiene-slice-a-detector-002.md (GO).
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-AUTHORIZE-WI-4356-IMPLEMENTATION.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

STALE_THRESHOLD_HOURS: int = 12
"""Owner-set stale-work threshold; see WI-4356 and DELIB-20260867."""


# ---------------------------------------------------------------------------
# Input dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class WorkspaceEntry:
    """A single workspace path the caller has observed.

    `path` is repo-relative; `last_modified` is a timezone-aware UTC datetime;
    `tracked` distinguishes tracked edits from untracked strays;
    `content_hash` is optional and enables uniqueness flagging.
    """

    path: str
    last_modified: datetime
    tracked: bool
    content_hash: str | None = None


@dataclass(frozen=True)
class StashEntry:
    """A single stash record the caller has observed."""

    stash_ref: str
    created_at: datetime
    subject: str = ""


@dataclass(frozen=True)
class WorktreeEntry:
    """A single working-tree directory the caller has observed.

    FAB-04 (HYG-057): harness-spawned ``.claude/worktrees/*`` detached
    checkouts accumulate as orphans that are not registered with
    ``git worktree`` and pollute repo-wide greps. ``path`` is repo-relative;
    ``last_modified`` is a timezone-aware UTC datetime; ``git_registered``
    distinguishes a live, git-tracked worktree (never a reap candidate) from
    an orphaned detached checkout. The caller supplies fresh state per
    GOV-SOURCE-OF-TRUTH-FRESHNESS-001; this detector never inspects the
    repository itself.
    """

    path: str
    last_modified: datetime
    git_registered: bool


@dataclass(frozen=True)
class ActiveSessionContext:
    """Paths and stash refs currently held by an active session.

    Workspace paths in `workspace_paths` and stash refs in `stash_refs` are
    excluded from staleness classification regardless of age, because they
    are still in use by a live session.
    """

    workspace_paths: frozenset[str] = field(default_factory=frozenset)
    stash_refs: frozenset[str] = field(default_factory=frozenset)


# ---------------------------------------------------------------------------
# Classification result dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class WorkspaceFinding:
    """Classification of a single workspace entry."""

    path: str
    age_hours: float
    classification: str  # "stale" | "recent" | "active_session"
    tracked: bool
    triage_reason: str
    candidate_action: str
    unique_content: bool | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "age_hours": round(self.age_hours, 4),
            "classification": self.classification,
            "tracked": self.tracked,
            "triage_reason": self.triage_reason,
            "candidate_action": self.candidate_action,
            "unique_content": self.unique_content,
        }


@dataclass(frozen=True)
class StashFinding:
    """Classification of a single stash entry."""

    stash_ref: str
    age_hours: float
    classification: str  # "stale" | "recent" | "active_session"
    triage_reason: str
    candidate_action: str
    subject: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "stash_ref": self.stash_ref,
            "age_hours": round(self.age_hours, 4),
            "classification": self.classification,
            "triage_reason": self.triage_reason,
            "candidate_action": self.candidate_action,
            "subject": self.subject,
        }


@dataclass(frozen=True)
class WorktreeFinding:
    """Classification of a single working-tree directory."""

    path: str
    age_hours: float
    classification: str  # "stale" | "recent" | "active_session" | "registered"
    git_registered: bool
    triage_reason: str
    candidate_action: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "age_hours": round(self.age_hours, 4),
            "classification": self.classification,
            "git_registered": self.git_registered,
            "triage_reason": self.triage_reason,
            "candidate_action": self.candidate_action,
        }


# ---------------------------------------------------------------------------
# Classification helpers
# ---------------------------------------------------------------------------


def _ensure_utc(value: datetime) -> datetime:
    """Reject naive datetimes; the detector is fail-closed on missing tz info."""
    if value.tzinfo is None:
        raise ValueError(
            "datetime values must be timezone-aware; "
            "supply UTC-anchored timestamps per GOV-SOURCE-OF-TRUTH-FRESHNESS-001"
        )
    return value.astimezone(UTC)


def _hours_between(later: datetime, earlier: datetime) -> float:
    delta = _ensure_utc(later) - _ensure_utc(earlier)
    return delta.total_seconds() / 3600.0


def _is_stale_age(age_hours: float, threshold_hours: int = STALE_THRESHOLD_HOURS) -> bool:
    """At-or-over the threshold is stale; strictly under is recent.

    Boundary policy: an entry exactly at the threshold is stale, so the
    owner directive ("after twelve hours") includes the twelve-hour mark
    itself.
    """
    return age_hours >= float(threshold_hours)


# ---------------------------------------------------------------------------
# Workspace classification
# ---------------------------------------------------------------------------


def classify_workspace_entry(
    entry: WorkspaceEntry,
    *,
    now: datetime,
    active_session: ActiveSessionContext | None = None,
    threshold_hours: int = STALE_THRESHOLD_HOURS,
    content_hash_counts: dict[str, int] | None = None,
) -> WorkspaceFinding:
    """Classify one workspace entry without mutating any external state."""
    age_hours = _hours_between(now, entry.last_modified)
    unique_content: bool | None = None
    if entry.content_hash is not None and content_hash_counts is not None:
        unique_content = content_hash_counts.get(entry.content_hash, 0) <= 1

    if active_session is not None and entry.path in active_session.workspace_paths:
        return WorkspaceFinding(
            path=entry.path,
            age_hours=age_hours,
            classification="active_session",
            tracked=entry.tracked,
            triage_reason="active_session_holds_path",
            candidate_action="skip",
            unique_content=unique_content,
        )

    if _is_stale_age(age_hours, threshold_hours):
        if entry.tracked:
            triage_reason = "stale_tracked_edit_over_threshold"
            candidate_action = "owner_review_stale_tracked_edit"
        else:
            triage_reason = "stale_untracked_stray_over_threshold"
            candidate_action = "owner_review_stale_untracked_file"
        return WorkspaceFinding(
            path=entry.path,
            age_hours=age_hours,
            classification="stale",
            tracked=entry.tracked,
            triage_reason=triage_reason,
            candidate_action=candidate_action,
            unique_content=unique_content,
        )

    return WorkspaceFinding(
        path=entry.path,
        age_hours=age_hours,
        classification="recent",
        tracked=entry.tracked,
        triage_reason="below_stale_threshold",
        candidate_action="skip",
        unique_content=unique_content,
    )


def classify_workspace_entries(
    entries: list[WorkspaceEntry],
    *,
    now: datetime,
    active_session: ActiveSessionContext | None = None,
    threshold_hours: int = STALE_THRESHOLD_HOURS,
) -> list[WorkspaceFinding]:
    """Classify a list of workspace entries.

    Pre-computes content-hash counts across the input set so each finding
    carries a stable `unique_content` flag without inspecting any other
    finding.
    """
    counts: dict[str, int] = {}
    for entry in entries:
        if entry.content_hash is not None:
            counts[entry.content_hash] = counts.get(entry.content_hash, 0) + 1

    return [
        classify_workspace_entry(
            entry,
            now=now,
            active_session=active_session,
            threshold_hours=threshold_hours,
            content_hash_counts=counts,
        )
        for entry in entries
    ]


# ---------------------------------------------------------------------------
# Stash classification
# ---------------------------------------------------------------------------


def classify_stash_entry(
    entry: StashEntry,
    *,
    now: datetime,
    active_session: ActiveSessionContext | None = None,
    threshold_hours: int = STALE_THRESHOLD_HOURS,
) -> StashFinding:
    """Classify one stash entry without mutating stash state."""
    age_hours = _hours_between(now, entry.created_at)

    if active_session is not None and entry.stash_ref in active_session.stash_refs:
        return StashFinding(
            stash_ref=entry.stash_ref,
            age_hours=age_hours,
            classification="active_session",
            triage_reason="active_session_holds_stash",
            candidate_action="skip",
            subject=entry.subject,
        )

    if _is_stale_age(age_hours, threshold_hours):
        return StashFinding(
            stash_ref=entry.stash_ref,
            age_hours=age_hours,
            classification="stale",
            triage_reason="stale_stash_over_threshold",
            candidate_action="owner_review_stale_stash",
            subject=entry.subject,
        )

    return StashFinding(
        stash_ref=entry.stash_ref,
        age_hours=age_hours,
        classification="recent",
        triage_reason="below_stale_threshold",
        candidate_action="skip",
        subject=entry.subject,
    )


def classify_stash_entries(
    entries: list[StashEntry],
    *,
    now: datetime,
    active_session: ActiveSessionContext | None = None,
    threshold_hours: int = STALE_THRESHOLD_HOURS,
) -> list[StashFinding]:
    return [
        classify_stash_entry(
            entry,
            now=now,
            active_session=active_session,
            threshold_hours=threshold_hours,
        )
        for entry in entries
    ]


# ---------------------------------------------------------------------------
# Worktree classification (FAB-04, HYG-057)
# ---------------------------------------------------------------------------


def classify_worktree_entry(
    entry: WorktreeEntry,
    *,
    now: datetime,
    active_session: ActiveSessionContext | None = None,
    threshold_hours: int = STALE_THRESHOLD_HOURS,
) -> WorktreeFinding:
    """Classify one working-tree directory without inspecting the repository.

    Precedence: an active-session hold wins over everything (a live session's
    worktree is never reaped); a git-registered worktree is always preserved
    (reaping a registered worktree would corrupt git's worktree administration);
    only an *orphaned* (non-registered) worktree over the staleness threshold is
    flagged for prune-and-delete. This encodes the HYG-057 recurrence-prevention
    invariant: harness-spawned ``.claude/worktrees/*`` detached checkouts that
    are no longer registered and no longer fresh are reap candidates.
    """
    age_hours = _hours_between(now, entry.last_modified)

    if active_session is not None and entry.path in active_session.workspace_paths:
        return WorktreeFinding(
            path=entry.path,
            age_hours=age_hours,
            classification="active_session",
            git_registered=entry.git_registered,
            triage_reason="active_session_holds_worktree",
            candidate_action="skip",
        )

    if entry.git_registered:
        return WorktreeFinding(
            path=entry.path,
            age_hours=age_hours,
            classification="registered",
            git_registered=True,
            triage_reason="git_registered_worktree",
            candidate_action="skip",
        )

    if _is_stale_age(age_hours, threshold_hours):
        return WorktreeFinding(
            path=entry.path,
            age_hours=age_hours,
            classification="stale",
            git_registered=False,
            triage_reason="stale_orphaned_worktree_over_threshold",
            candidate_action="prune_and_delete_orphaned_worktree",
        )

    return WorktreeFinding(
        path=entry.path,
        age_hours=age_hours,
        classification="recent",
        git_registered=False,
        triage_reason="below_stale_threshold",
        candidate_action="skip",
    )


def classify_worktree_entries(
    entries: list[WorktreeEntry],
    *,
    now: datetime,
    active_session: ActiveSessionContext | None = None,
    threshold_hours: int = STALE_THRESHOLD_HOURS,
) -> list[WorktreeFinding]:
    return [
        classify_worktree_entry(
            entry,
            now=now,
            active_session=active_session,
            threshold_hours=threshold_hours,
        )
        for entry in entries
    ]


# ---------------------------------------------------------------------------
# Top-level detector entry point
# ---------------------------------------------------------------------------


def detect_strays(
    *,
    now: datetime,
    workspace_entries: list[WorkspaceEntry],
    stash_entries: list[StashEntry],
    worktree_entries: list[WorktreeEntry] | None = None,
    active_session: ActiveSessionContext | None = None,
    threshold_hours: int = STALE_THRESHOLD_HOURS,
) -> dict[str, Any]:
    """Compute the full detector report as a JSON-serializable dict.

    The return shape is the durable Slice A artifact: callers (later
    CLI/doctor/hook slices) can route it to triage records, work-item
    creation, or owner-AUQ surfaces without re-parsing.

    ``worktree_entries`` is optional and defaults to none, so existing
    callers that predate the FAB-04 worktree-staleness extension keep their
    behavior; when supplied, orphaned stale ``.claude/worktrees/*`` checkouts
    are surfaced as a distinct finding category.
    """
    workspace_findings = classify_workspace_entries(
        workspace_entries,
        now=now,
        active_session=active_session,
        threshold_hours=threshold_hours,
    )
    stash_findings = classify_stash_entries(
        stash_entries,
        now=now,
        active_session=active_session,
        threshold_hours=threshold_hours,
    )
    worktree_findings = classify_worktree_entries(
        worktree_entries or [],
        now=now,
        active_session=active_session,
        threshold_hours=threshold_hours,
    )

    return {
        "generated_at": _ensure_utc(now).isoformat(),
        "threshold_hours": threshold_hours,
        "counts": {
            "workspace_total": len(workspace_findings),
            "workspace_stale": sum(1 for f in workspace_findings if f.classification == "stale"),
            "workspace_recent": sum(1 for f in workspace_findings if f.classification == "recent"),
            "workspace_active_session": sum(1 for f in workspace_findings if f.classification == "active_session"),
            "stash_total": len(stash_findings),
            "stash_stale": sum(1 for f in stash_findings if f.classification == "stale"),
            "stash_recent": sum(1 for f in stash_findings if f.classification == "recent"),
            "stash_active_session": sum(1 for f in stash_findings if f.classification == "active_session"),
            "worktree_total": len(worktree_findings),
            "worktree_stale": sum(1 for f in worktree_findings if f.classification == "stale"),
            "worktree_recent": sum(1 for f in worktree_findings if f.classification == "recent"),
            "worktree_registered": sum(1 for f in worktree_findings if f.classification == "registered"),
            "worktree_active_session": sum(1 for f in worktree_findings if f.classification == "active_session"),
        },
        "workspace_findings": [finding.to_dict() for finding in workspace_findings],
        "stash_findings": [finding.to_dict() for finding in stash_findings],
        "worktree_findings": [finding.to_dict() for finding in worktree_findings],
    }
