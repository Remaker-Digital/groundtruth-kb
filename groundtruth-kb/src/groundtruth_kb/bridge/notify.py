# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Bridge dispatch notification artifacts (RETIRED smart-poller substrate).

RETIRED (2026-05-09): This module belongs to the retired smart-poller
runtime. The smart-poller scheduled task and runner script have been
archived to ``archive/smart-poller-2026-05-09/``; bridge dispatch is now
governed by the dispatcher daemon. The notification-artifact API below is
retained for compatibility and historical reference; the daemon writes its
dispatch state at
``.gtkb-state/bridge-poller/dispatch-state.json``.

Per ``bridge/gtkb-bridge-poller-p3-notify-2026-04-29-008.md`` GO at REVISED-3,
this module owns the (now-retired) notification artifact lifecycle.

Per ``bridge/smart-poller-kind-aware-routing-2026-04-30-009.md`` REVISED-4
(GO at -010), the routing is now kind-aware: each ``ActionablePending`` carries
``dispatchable`` + ``classification`` fields, and dispatch consumers filter
on ``dispatchable`` to suppress spurious harness spawns for terminal-kind GO
verdicts (scoping/closure/parking/index_reconciliation/thread_reconciliation/
operational_state_change/candidate_spec_intake).

- ``compute_actionable_pending(parse_result, *, project_root)`` derives
  per-recipient actionable lists from the CURRENT TOP STATUSES of parsed
  ``BridgeDocument`` entries — NOT from checkpoint diffs. The checkpoint is
  audit-only in the notify path. Each entry now carries kind classification
  + dispatch eligibility.
- ``update_notification(state_dir, recipient, items)`` writes (non-empty) or
  removes (empty) the recipient's notification artifact under
  ``<state_dir>/notifications/pending-bridge-action-{recipient}.{json,md}``.
- ``read_notification(state_dir, recipient)`` returns the parsed artifact or
  ``None`` if absent.
- ``clear_notification(state_dir, recipient)`` removes both the JSON and
  markdown companion files.

Routing contract (per ``AGENTS.md:153-159`` + DELIB-S319-SMART-POLLER-OBJECTIVE-CLARIFICATION
+ smart-poller-kind-aware-routing-2026-04-30-009 REVISED-4):

- ``NEW`` / ``REVISED`` / ``READY`` / ``VERDICT-REJECTED`` top status → Loyal
  Opposition (reviews). Always dispatchable; kind classification is
  informational only.
- ``NO-GO`` top status → Prime Builder (Prime revises). Always dispatchable
  because NO-GO is "proposal requires changes before approval", regardless
  of bridge_kind, except when the latest verdict explicitly marks the thread
  as ``Hold for Owner Decision``. Owner-hold threads remain Prime-visible but
  are manual-only for headless dispatch.
- ``GO`` top status → Prime Builder (Prime acts). Dispatchable iff the
  bridge_kind classification is NOT terminal — terminal kinds (scoping,
  closure, parking, index_reconciliation, thread_reconciliation,
  operational_state_change, candidate_spec_intake, implementation_report) or
  explicit ``Hold for Owner Decision`` latest verdicts have no headless Prime
  follow-up after a GO verdict.
- ``ADVISORY`` top status -> not actionable for either role. It is
  owner-visible informational input only: never assigned, dispatched, or
  placed in a role queue.
- ``VERIFIED`` / ``WITHDRAWN`` / ``SUPERSEDED`` / ``BLOCKED`` top status ->
  not actionable for either role.

Phase-2 Ollama dispatch wiring keeps this module role-actionability-only.
Harness-local readiness (Ollama shim, daemon, route/tool subset) is applied
downstream by the dispatcher daemon when a role-actionable entry resolves to
harness D.

Schema v3 (bumped from v2 per kind-aware-routing slice): ``pending_actions[]``
entries now carry ``dispatchable`` (bool) + ``classification`` (str:
"dispatchable"/"terminal"/"ambiguous") fields in addition to the v2 fields.
v1's transition-shaped ``pending_transitions[]`` is NOT produced or read.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import sqlite3
import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from groundtruth_kb.bridge.detector import BridgeDocument, BridgeStatus, BridgeVersion, ParseResult
from groundtruth_kb.bridge.disposition import (
    BRIDGE_KIND_DISPATCHABLE_TOKENS,
    BRIDGE_KIND_TERMINAL_TOKENS,
    CLASSIFICATION_HEADLESS_INELIGIBLE,
    CLASSIFICATION_OWNER_HOLD,
    LOYAL_OPPOSITION_ACTIONABLE_STATUSES,
    PRIME_ACTIONABLE_STATUSES,
    dispatchable_for_status,
    is_actionable_status_for_role,
)
from groundtruth_kb.bridge.routing import BridgeAgent

NOTIFY_SUBDIR: Final[str] = "notifications"
NOTIFY_SCHEMA_VERSION: Final[int] = 3

# Feature flag for kind-aware routing. =0 disables filtering and matches
# pre-refinement behavior (all entries dispatchable=True via fallback).
KIND_AWARE_ROUTING_ENV_VAR: Final[str] = "GTKB_NOTIFY_KIND_AWARE_ROUTING"

# Bridge-kind substring tokens. Matched against the lowercased + kebab-to-snake-
# normalized bridge_kind value. Order matters: terminal is checked first so the
# more-specific tokens (e.g., "scoping" inside "implementation_scoping") win
# before broader matches. Per smart-poller-kind-aware-routing-2026-04-30-009
# REVISED-4 §1.1.
_KIND_TERMINAL_TOKENS: Final[tuple[str, ...]] = BRIDGE_KIND_TERMINAL_TOKENS
_KIND_DISPATCHABLE_TOKENS: Final[tuple[str, ...]] = BRIDGE_KIND_DISPATCHABLE_TOKENS

# Bare "proposal", "review", "verification", and unrecognized kinds → ambiguous
# → status-only fallback. Ambiguous entries are dispatched on actionable
# statuses (preserving legacy behavior for un-migrated bridges).

# Frontmatter parser: bridge_kind: <value> at start-of-line, allows whitespace.
_BRIDGE_KIND_RE: Final[re.Pattern[str]] = re.compile(r"^bridge_kind:\s*(\S+)", re.MULTILINE)
_OWNER_HOLD_RE: Final[re.Pattern[str]] = re.compile(
    r"^\s*(?:[-*+]|\d+[.)])?\s*(?:#{1,6}\s*)?(?:\*\*)?"
    r"hold\s+for\s+owner\s+decision(?::)?(?:\*\*)?\s*(?::|\b)",
    re.IGNORECASE | re.MULTILINE,
)
_HEADLESS_INELIGIBLE_RE: Final[re.Pattern[str]] = re.compile(
    r"\bdispatch\s+loop\s+must\s+be\s+broken\b"
    r"|\bdo\s+not\s+re-?dispatch\s+to\s+codex\s+headless\b"
    r"|\bno\s+further\s+(?:codex\s+)?headless\s+(?:auto-?)?re-?dispatch(?:es)?\b",
    re.IGNORECASE,
)
_WORK_ITEM_RE: Final[re.Pattern[str]] = re.compile(
    r"^\s*(?:[-*+]\s*)?Work Item:\s*`?(?P<work_item_id>WI-\d+)\b",
    re.IGNORECASE | re.MULTILINE,
)
_COMMIT_SUBJECT_WORK_ITEM_RE: Final[re.Pattern[str]] = re.compile(r"\((WI-\d+)\)\s*$", re.IGNORECASE)
_COMMIT_TRAILER_WORK_ITEM_RE: Final[re.Pattern[str]] = re.compile(
    r"^(?:Retired-Work-Item|Work-Item):\s*(WI-\d+)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
_TERMINAL_WORK_ITEM_STAGES: Final[frozenset[str]] = frozenset(
    {"complete", "completed", "resolved", "retired", "terminal"}
)
_TERMINAL_RESOLUTION_STATUSES: Final[frozenset[str]] = frozenset({"resolved", "retired", "superseded", "wont_fix"})

# Header read budget (bytes). bridge_kind is always in the header section.
_HEADER_READ_BUDGET_BYTES: Final[int] = 4096

# Latest verdict owner-hold markers can appear after metadata and review notes.
_OWNER_HOLD_READ_BUDGET_BYTES: Final[int] = 65536


def _kind_aware_routing_enabled() -> bool:
    """Return True if kind-aware routing is enabled via env var (default True).

    `=0` disables filtering; any other value (or unset) enables. Matches
    the safe-rollback contract from smart-poller-kind-aware-routing -009 §1.6.
    """
    return os.environ.get(KIND_AWARE_ROUTING_ENV_VAR, "1") != "0"


def _extract_bridge_kind(header_text: str) -> str | None:
    """Extract the value of ``bridge_kind: <value>`` from a markdown header.

    Returns the trimmed value or None if not found. Tolerant of whitespace
    and YAML-frontmatter or freeform-header placement.
    """
    match = _BRIDGE_KIND_RE.search(header_text)
    return match.group(1).strip() if match else None


def find_operative_prime_version(doc: BridgeDocument) -> BridgeVersion | None:
    """Return the latest Prime-authored version (NEW or REVISED) in the document.

    ``BridgeDocument.versions`` is ordered most-recent-first. NEW and REVISED
    are Prime-authored; GO, NO-GO, VERIFIED are Codex-authored verdict files
    that typically do NOT carry ``bridge_kind:`` metadata. Reading bridge_kind
    requires finding the Prime proposal version — per
    smart-poller-kind-aware-routing-2026-04-30-007 (REVISED-3) F1 fix.

    Returns None if the document has no NEW/REVISED versions (rare).
    """
    for version in doc.versions:
        if version.status in (BridgeStatus.NEW, BridgeStatus.REVISED):
            return version
    return None


def _latest_verdict_declares_owner_hold(project_root: Path, doc: BridgeDocument) -> bool:
    """Return True when the latest Prime-actionable verdict is owner-held."""
    if not doc.versions:
        return False
    top = doc.versions[0]
    if top.status not in (BridgeStatus.GO, BridgeStatus.NO_GO):
        return False

    full_path = project_root / top.file_path
    try:
        with full_path.open("r", encoding="utf-8") as fh:
            head = fh.read(_OWNER_HOLD_READ_BUDGET_BYTES)
    except (OSError, UnicodeDecodeError):
        return False

    return _OWNER_HOLD_RE.search(head) is not None


def _latest_verdict_declares_headless_ineligible(project_root: Path, doc: BridgeDocument) -> bool:
    """Return True when the latest verdict explicitly blocks headless redispatch.

    The match surface is intentionally narrow and imperative: "dispatch loop
    must be broken", "do not re-dispatch to Codex headless", or "no further
    Codex/headless redispatch". General historical discussion of headless
    dispatch remains dispatchable.
    """
    if not doc.versions:
        return False
    top = doc.versions[0]
    if top.status not in (BridgeStatus.GO, BridgeStatus.NO_GO):
        return False

    full_path = project_root / top.file_path
    try:
        with full_path.open("r", encoding="utf-8") as fh:
            head = fh.read(_OWNER_HOLD_READ_BUDGET_BYTES)
    except (OSError, UnicodeDecodeError):
        return False

    return _HEADLESS_INELIGIBLE_RE.search(head) is not None


def classify_document_dispatchability(
    project_root: Path,
    doc: BridgeDocument,
) -> str:
    """Classify the document's bridge_kind into a routing category.

    Reads ``bridge_kind:`` from the operative Prime proposal version (latest
    NEW or REVISED), NOT from the top file (which is typically a Codex verdict
    file without ``bridge_kind:``). Per smart-poller-kind-aware-routing-2026-04-30
    -007 F1 fix.

    Returns one of:
    - "dispatchable" — bridge_kind matches a dispatchable token (impl proposals,
      slices, fixes, governance/architecture proposals, post-impl reports)
    - "terminal" — bridge_kind matches a terminal token (scoping, closure,
      parking, index/thread reconciliation, operational state change, candidate
      spec intake, implementation report)
    - "owner_hold" — latest GO/NO-GO verdict explicitly says Hold for Owner
      Decision; action remains visible to Prime but headless dispatch is
      suppressed
    - "headless_ineligible" — latest GO/NO-GO verdict explicitly says headless
      redispatch must stop; action remains visible to Prime but headless
      dispatch is suppressed
    - "ambiguous" — bridge_kind missing, bare "proposal", "review",
      "verification", or unrecognized; falls back to status-only routing
      via the dispatchable invariant in `_derive_dispatchable`
    """
    if _latest_verdict_declares_owner_hold(project_root, doc):
        return CLASSIFICATION_OWNER_HOLD
    if _latest_verdict_declares_headless_ineligible(project_root, doc):
        return CLASSIFICATION_HEADLESS_INELIGIBLE

    operative = find_operative_prime_version(doc)
    if operative is None:
        return "ambiguous"

    full_path = project_root / operative.file_path
    try:
        with full_path.open("r", encoding="utf-8") as fh:
            head = fh.read(_HEADER_READ_BUDGET_BYTES)
    except (OSError, UnicodeDecodeError):
        return "ambiguous"

    bridge_kind = _extract_bridge_kind(head)
    if not bridge_kind:
        return "ambiguous"

    # Lowercase + kebab-to-snake normalization. Catches post-implementation-report
    # (3 occurrences in inventory) which bare underscore matching would miss.
    bk_normalized = bridge_kind.lower().replace("-", "_")

    for token in _KIND_TERMINAL_TOKENS:
        if token in bk_normalized:
            return "terminal"

    for token in _KIND_DISPATCHABLE_TOKENS:
        if token in bk_normalized:
            return "dispatchable"

    return "ambiguous"


def _derive_dispatchable(top_status: str, classification: str) -> bool:
    """Compute whether this entry should be auto-dispatched given top status.

    Per smart-poller-kind-aware-routing-2026-04-30-009 REVISED-4 §1.1:

    - NEW / REVISED / READY / VERDICT-REJECTED → True (Loyal Opposition reviews
      regardless of kind classification; terminal-kind means "no Prime
      follow-up", not "no Loyal Opposition review")
    - NO-GO → True unless the latest verdict explicitly declares owner-hold
      (Prime revises regardless of kind, per file-bridge-protocol.md:92,
      104-107: "proposal requires changes before approval")
    - GO → ``classification != "terminal"`` (Prime filters terminal kinds,
      keeps everything else, unless latest-verdict owner-hold suppresses it)
    - ADVISORY + others -> False (owner-visible informational input only)
    - VERIFIED / WITHDRAWN / SUPERSEDED / BLOCKED + others -> False (not actionable)
    """
    return dispatchable_for_status(top_status, classification)


@dataclass(frozen=True)
class WorkItemTerminality:
    """Fail-visible checked-in Git terminality for one work item."""

    state: str
    commit: str | None = None
    diagnostic: str | None = None


@dataclass(frozen=True)
class WorkItemActionabilityAnnotation:
    """Advisory work-item context attached to one visible bridge thread."""

    work_item_id: str | None = None
    stage: str | None = None
    resolution_status: str | None = None
    status_detail: str | None = None
    git_terminality: str = "ambiguous"
    terminal_commit: str | None = None
    terminality_diagnostic: str | None = "work_item_id_unresolved"


@dataclass(frozen=True)
class ActionablePending:
    """One document's currently-actionable top status for a specific recipient.

    Per smart-poller-kind-aware-routing-2026-04-30-009 REVISED-4: ``dispatchable``
    + ``classification`` fields support kind-aware dispatch consumer filtering.
    """

    document_name: str
    top_status: str
    top_file: str
    index_line_number: int
    dispatchable: bool = True
    classification: str = "ambiguous"
    work_item_id: str | None = None
    work_item_stage: str | None = None
    work_item_resolution_status: str | None = None
    work_item_status_detail: str | None = None
    git_terminality: str = "ambiguous"
    terminal_commit: str | None = None
    terminality_diagnostic: str | None = None


@dataclass(frozen=True)
class NotificationArtifact:
    """Parsed contents of a recipient's notification file."""

    schema_version: int
    recipient: str
    written_at: str
    poller_run_id: str
    pending_actions: tuple[ActionablePending, ...]
    summary: str


def _recipient_str(recipient: BridgeAgent | str) -> str:
    return recipient.value if isinstance(recipient, BridgeAgent) else recipient


def _notify_dir(state_dir: Path) -> Path:
    out = state_dir / NOTIFY_SUBDIR
    out.mkdir(parents=True, exist_ok=True)
    return out


def _json_path(state_dir: Path, recipient: BridgeAgent | str) -> Path:
    return _notify_dir(state_dir) / f"pending-bridge-action-{_recipient_str(recipient)}.json"


def _md_path(state_dir: Path, recipient: BridgeAgent | str) -> Path:
    return _notify_dir(state_dir) / f"pending-bridge-action-{_recipient_str(recipient)}.md"


def _atomic_write_text(target: Path, content: str) -> None:
    tmp = target.with_suffix(target.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(target)


def _is_actionable_for(status: str, recipient: BridgeAgent) -> bool:
    if recipient is BridgeAgent.PRIME:
        return is_actionable_status_for_role(status, "prime-builder")
    if recipient is BridgeAgent.CODEX:
        return is_actionable_status_for_role(status, "loyal-opposition")
    return False


_SCOPING_SUFFIX = "-scoping"
_IMPLEMENTATION_SUFFIX = "-implementation"


def _scoping_terminal_with_successor(doc_name: str, parse_result: ParseResult) -> bool:
    """Return True if ``doc_name`` is a scoping thread whose successor exists.

    A scoping thread is identified by the ``-scoping`` slug suffix. Its
    successor is the document at the same slug with the suffix stripped.
    When the successor exists in ``parse_result.documents`` (at any canonical
    bridge status), the scoping thread is terminal-for-scoping and no longer
    actionable for either role.

    Per WI-3442 + bridge/gtkb-axis-2-scoping-terminal-classifier-fix-002 (GO).
    """
    if not doc_name.endswith(_SCOPING_SUFFIX):
        return False
    successor_name = doc_name[: -len(_SCOPING_SUFFIX)]
    if not successor_name:
        return False
    return any(d.name == successor_name for d in parse_result.documents)


def _has_verified_implementation_sibling(doc_name: str, parse_result: ParseResult) -> bool:
    """Return True if ``<doc_name>-implementation`` exists at VERIFIED.

    A proposal or umbrella thread frequently terminates at ``GO`` while its
    implementation work completes on a separate ``<slug>-implementation``
    sibling thread that reaches ``VERIFIED``. Once that sibling is VERIFIED the
    parent thread's work is complete and the parent is no longer actionable for
    either role.

    Parallel to :func:`_scoping_terminal_with_successor`. Per WI-4549
    (umbrella/proposal threads stuck at GO polluting the prime-actionable
    surface).
    """
    sibling_name = doc_name + _IMPLEMENTATION_SUFFIX
    for doc in parse_result.documents:
        if doc.name == sibling_name and doc.versions:
            if str(doc.versions[0].status.value) == "VERIFIED":
                return True
    return False


def _work_item_id_from_thread_files(project_root: Path, files: Sequence[str | Path]) -> str | None:
    """Return the first exact Work Item header found, newest file first."""

    for raw_path in files:
        path = Path(raw_path)
        if not path.is_absolute():
            path = project_root / path
        try:
            with path.open("r", encoding="utf-8") as handle:
                text = handle.read(_OWNER_HOLD_READ_BUDGET_BYTES)
        except (OSError, UnicodeDecodeError):
            continue
        match = _WORK_ITEM_RE.search(text)
        if match:
            return match.group("work_item_id").upper()
    return None


def _read_work_item_rows(
    project_root: Path,
    work_item_ids: set[str],
) -> tuple[dict[str, dict[str, str | None]], str | None]:
    """Read current work-item annotation fields without creating a database."""

    if not work_item_ids:
        return {}, None
    db_path = project_root / "groundtruth.db"
    if not db_path.is_file():
        return {}, "work_item_database_missing"
    placeholders = ", ".join("?" for _ in work_item_ids)
    try:
        connection = sqlite3.connect(f"{db_path.resolve().as_uri()}?mode=ro", uri=True)
        connection.row_factory = sqlite3.Row
        try:
            connection.execute("PRAGMA query_only = ON")
            rows = connection.execute(
                "SELECT id, stage, resolution_status, status_detail "
                f"FROM current_work_items WHERE id IN ({placeholders})",
                tuple(sorted(work_item_ids)),
            ).fetchall()
        finally:
            connection.close()
    except (OSError, sqlite3.Error, ValueError):
        return {}, "work_item_database_unreadable"
    return {
        str(row["id"]).upper(): {
            "stage": str(row["stage"]) if row["stage"] is not None else None,
            "resolution_status": (str(row["resolution_status"]) if row["resolution_status"] is not None else None),
            "status_detail": str(row["status_detail"]) if row["status_detail"] is not None else None,
        }
        for row in rows
    }, None


def _checked_in_work_item_commit_index(
    project_root: Path,
) -> tuple[dict[str, tuple[str, ...]], set[str], str | None]:
    """Index exact terminal-commit metadata from commits reachable from HEAD."""

    if not (project_root / ".git").exists():
        return {}, set(), "git_repository_unavailable"
    try:
        result = subprocess.run(
            ["git", "-C", str(project_root), "log", "--format=%H%x1f%B%x1e", "HEAD"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return {}, set(), "git_log_unavailable"
    if result.returncode != 0:
        return {}, set(), "git_log_failed"

    commits: dict[str, list[str]] = {}
    ambiguous_ids: set[str] = set()
    for raw_record in result.stdout.split("\x1e"):
        record = raw_record.strip("\r\n")
        if not record:
            continue
        commit, separator, message = record.partition("\x1f")
        if not separator or not commit:
            continue
        subject = message.splitlines()[0] if message.splitlines() else ""
        subject_match = _COMMIT_SUBJECT_WORK_ITEM_RE.search(subject)
        work_item_ids = {subject_match.group(1).upper()} if subject_match else set()
        work_item_ids.update(match.upper() for match in _COMMIT_TRAILER_WORK_ITEM_RE.findall(message))
        if len(work_item_ids) != 1:
            ambiguous_ids.update(work_item_ids)
            continue
        work_item_id = next(iter(work_item_ids))
        commits.setdefault(work_item_id, []).append(commit)
    return {work_item_id: tuple(values) for work_item_id, values in commits.items()}, ambiguous_ids, None


def _resolve_terminality_from_evidence(
    work_item_id: str,
    *,
    work_item_row: Mapping[str, str | None] | None,
    commit_index: Mapping[str, tuple[str, ...]],
    ambiguous_commit_ids: set[str],
    git_error: str | None,
) -> WorkItemTerminality:
    if git_error is not None:
        return WorkItemTerminality(state="ambiguous", diagnostic=git_error)
    commits = commit_index.get(work_item_id, ())
    if work_item_id in ambiguous_commit_ids or len(commits) > 1:
        return WorkItemTerminality(state="ambiguous", diagnostic="multiple_or_non_singleton_commit_metadata")
    if len(commits) == 1:
        return WorkItemTerminality(state="confirmed", commit=commits[0])
    if work_item_row is None:
        return WorkItemTerminality(state="ambiguous", diagnostic="work_item_row_missing")
    stage = str(work_item_row.get("stage") or "").lower()
    resolution_status = str(work_item_row.get("resolution_status") or "").lower()
    if stage in _TERMINAL_WORK_ITEM_STAGES or resolution_status in _TERMINAL_RESOLUTION_STATUSES:
        return WorkItemTerminality(
            state="ambiguous",
            diagnostic="work_item_terminal_without_checked_in_commit",
        )
    return WorkItemTerminality(state="not_confirmed", diagnostic="no_checked_in_terminal_commit")


def resolve_work_item_terminality(work_item_id: str, *, project_root: Path) -> WorkItemTerminality:
    """Resolve one work item; ambiguity is explicit and never suppressive."""

    normalized = work_item_id.upper()
    rows, _ = _read_work_item_rows(project_root, {normalized})
    commit_index, ambiguous_ids, git_error = _checked_in_work_item_commit_index(project_root)
    return _resolve_terminality_from_evidence(
        normalized,
        work_item_row=rows.get(normalized),
        commit_index=commit_index,
        ambiguous_commit_ids=ambiguous_ids,
        git_error=git_error,
    )


def resolve_thread_actionability_annotations(
    project_root: Path,
    thread_files: Mapping[str, Sequence[str | Path]],
) -> dict[str, WorkItemActionabilityAnnotation]:
    """Batch-resolve advisory work-item fields and checked-in terminality."""

    thread_work_items = {
        slug: _work_item_id_from_thread_files(project_root, files) for slug, files in thread_files.items()
    }
    work_item_ids = {work_item_id for work_item_id in thread_work_items.values() if work_item_id}
    rows, db_error = _read_work_item_rows(project_root, work_item_ids)
    commit_index, ambiguous_ids, git_error = _checked_in_work_item_commit_index(project_root)

    annotations: dict[str, WorkItemActionabilityAnnotation] = {}
    for slug, work_item_id in thread_work_items.items():
        if work_item_id is None:
            annotations[slug] = WorkItemActionabilityAnnotation()
            continue
        row = rows.get(work_item_id)
        terminality = _resolve_terminality_from_evidence(
            work_item_id,
            work_item_row=row,
            commit_index=commit_index,
            ambiguous_commit_ids=ambiguous_ids,
            git_error=git_error,
        )
        diagnostic = terminality.diagnostic
        if db_error is not None and row is None:
            diagnostic = ";".join(part for part in (diagnostic, db_error) if part)
        annotations[slug] = WorkItemActionabilityAnnotation(
            work_item_id=work_item_id,
            stage=row.get("stage") if row else None,
            resolution_status=row.get("resolution_status") if row else None,
            status_detail=row.get("status_detail") if row else None,
            git_terminality=terminality.state,
            terminal_commit=terminality.commit,
            terminality_diagnostic=diagnostic,
        )
    return annotations


def compute_actionable_pending(
    parse_result: ParseResult,
    *,
    project_root: Path,
) -> tuple[list[ActionablePending], list[ActionablePending]]:
    """Compute current-state actionable pending entries from the parsed INDEX.

    Returns ``(actionable_for_prime, actionable_for_codex)``. Each list contains
    one entry per document whose CURRENT TOP STATUS is actionable for that
    recipient.

    - ``GO`` / ``NO-GO`` / ``NOT-READY`` → Prime list
      (``PRIME_ACTIONABLE_STATUSES``).
    - ``NEW`` / ``REVISED`` / ``READY`` / ``VERDICT-REJECTED`` → Loyal
      Opposition list (``LOYAL_OPPOSITION_ACTIONABLE_STATUSES``).
    - ``ADVISORY`` -> excluded from BOTH lists. It is owner-visible
      informational input, never assigned or dispatched to a role.
    - ``VERIFIED`` / ``WITHDRAWN`` / ``SUPERSEDED`` / ``BLOCKED`` -> excluded
      (non-actionable for both per bridge protocol).
    - Documents whose top file is missing on disk are excluded (UNROUTABLE_FILE_MISSING
      semantic from P1 routing).

    Order preserved from ``parse_result.documents`` (INDEX-file order, most-recent at top).

    Audit-only: the checkpoint is NOT consulted by this function. Same parse_result
    + same on-disk file presence → same output. Deterministic.
    """
    actionable_for_prime: list[ActionablePending] = []
    actionable_for_codex: list[ActionablePending] = []
    annotations = resolve_thread_actionability_annotations(
        project_root,
        {doc.name: tuple(version.file_path for version in doc.versions) for doc in parse_result.documents},
    )

    for doc in parse_result.documents:
        if not doc.versions:
            continue
        top = doc.versions[0]
        if not (project_root / top.file_path).is_file():
            continue

        # Suppress scoping-terminal threads whose successor implementation
        # bridge exists. The scoping conversation's work has moved to the
        # successor slug; the scoping thread itself is not actionable for
        # either role (per WI-3442 + classifier-fix GO -002).
        if _scoping_terminal_with_successor(doc.name, parse_result):
            continue

        # Suppress proposal/umbrella threads whose implementation sibling has
        # reached VERIFIED. The parent thread's work is complete; it is not
        # actionable for either role (per WI-4549; parallel to the scoping-
        # terminal suppression above).
        if _has_verified_implementation_sibling(doc.name, parse_result):
            continue

        annotation = annotations[doc.name]
        if annotation.git_terminality == "confirmed":
            continue

        # Kind-aware classification per smart-poller-kind-aware-routing
        # -2026-04-30-009 REVISED-4. Read bridge_kind from the operative
        # Prime proposal (latest NEW/REVISED), classify, then derive
        # dispatchable from status + classification.
        classification = classify_document_dispatchability(project_root, doc)
        status_str = str(top.status.value)
        dispatchable = _derive_dispatchable(status_str, classification)

        entry = ActionablePending(
            document_name=doc.name,
            top_status=status_str,
            top_file=top.file_path,
            index_line_number=top.line_number,
            dispatchable=dispatchable,
            classification=classification,
            work_item_id=annotation.work_item_id,
            work_item_stage=annotation.stage,
            work_item_resolution_status=annotation.resolution_status,
            work_item_status_detail=annotation.status_detail,
            git_terminality=annotation.git_terminality,
            terminal_commit=annotation.terminal_commit,
            terminality_diagnostic=annotation.terminality_diagnostic,
        )
        if status_str in PRIME_ACTIONABLE_STATUSES:
            actionable_for_prime.append(entry)
        elif status_str in LOYAL_OPPOSITION_ACTIONABLE_STATUSES:
            actionable_for_codex.append(entry)
        # VERIFIED/WITHDRAWN/SUPERSEDED/BLOCKED + anything else: not
        # actionable, skip. ADVISORY falls here too: it is in neither
        # PRIME_ACTIONABLE_STATUSES nor LOYAL_OPPOSITION_ACTIONABLE_STATUSES.

    return actionable_for_prime, actionable_for_codex


def _summarize(recipient_str: str, items: list[ActionablePending]) -> str:
    if not items:
        return f"No pending action for {recipient_str}."
    if len(items) == 1:
        only = items[0]
        return f"1 {only.top_status} item awaits {recipient_str} action: {only.document_name}"
    by_status: dict[str, int] = {}
    for item in items:
        by_status[item.top_status] = by_status.get(item.top_status, 0) + 1
    counts = ", ".join(f"{count} {status}" for status, count in sorted(by_status.items()))
    return f"{len(items)} items await {recipient_str} action: {counts}"


def _now_iso() -> str:
    return dt.datetime.now(dt.UTC).isoformat(timespec="seconds")


def _render_markdown(artifact: NotificationArtifact) -> str:
    lines: list[str] = []
    lines.append(
        f"# Pending Bridge Actions for {artifact.recipient.capitalize()} ({len(artifact.pending_actions)} item{'s' if len(artifact.pending_actions) != 1 else ''})\n"
    )
    lines.append(f"Generated by smart poller at {artifact.written_at} (run `{artifact.poller_run_id}`).\n")
    lines.append(f"Summary: {artifact.summary}\n")
    if artifact.pending_actions:
        # Schema v3 columns: kind classification + dispatchability per
        # smart-poller-kind-aware-routing-2026-04-30-009 REVISED-4.
        lines.append(
            "| Document | Top status | Top file | INDEX line | Dispatchable | Classification | "
            "Work item | Work-item state | Git terminality |"
        )
        lines.append("|---|---|---|---|---|---|---|---|---|")
        for item in artifact.pending_actions:
            dispatchable_marker = "yes" if item.dispatchable else "no"
            # `(terminal)` prefix shown only when classification is terminal AND
            # the entry's status is GO — i.e., where terminal classification
            # actually suppresses Prime dispatch. NO-GO terminal-kind entries
            # show classification in the column but no prefix because Prime
            # revision is preserved.
            prefix = (
                "(terminal) " if item.classification == "terminal" and item.top_status == BridgeStatus.GO.value else ""
            )
            lines.append(
                f"| {prefix}{item.document_name} | {item.top_status} | {item.top_file} | "
                f"{item.index_line_number} | {dispatchable_marker} | {item.classification} | "
                f"{item.work_item_id or '(unresolved)'} | "
                f"{item.work_item_stage or '(unknown)'}/{item.work_item_resolution_status or '(unknown)'} | "
                f"{item.git_terminality} |"
            )
    return "\n".join(lines) + "\n"


def update_notification(
    state_dir: Path,
    recipient: BridgeAgent | str,
    items: list[ActionablePending],
    *,
    poller_run_id: str = "manual",
) -> NotificationArtifact | None:
    """Write or remove the recipient's notification artifact.

    - Non-empty ``items``: atomically write JSON + markdown companion. Returns the
      written ``NotificationArtifact``.
    - Empty ``items``: atomically remove both files if they exist. Returns ``None``.

    File-absent represents "no pending action" (per Codex GO at -008 watchpoint #3).
    """
    recipient_str = _recipient_str(recipient)
    json_path = _json_path(state_dir, recipient)
    md_path = _md_path(state_dir, recipient)

    if not items:
        json_path.unlink(missing_ok=True)
        md_path.unlink(missing_ok=True)
        return None

    artifact = NotificationArtifact(
        schema_version=NOTIFY_SCHEMA_VERSION,
        recipient=recipient_str,
        written_at=_now_iso(),
        poller_run_id=poller_run_id,
        pending_actions=tuple(items),
        summary=_summarize(recipient_str, items),
    )
    payload = {
        "schema_version": artifact.schema_version,
        "recipient": artifact.recipient,
        "written_at": artifact.written_at,
        "poller_run_id": artifact.poller_run_id,
        "pending_actions": [
            {
                "document_name": item.document_name,
                "top_status": item.top_status,
                "top_file": item.top_file,
                "index_line_number": item.index_line_number,
                "dispatchable": item.dispatchable,
                "classification": item.classification,
                "work_item_id": item.work_item_id,
                "work_item_stage": item.work_item_stage,
                "work_item_resolution_status": item.work_item_resolution_status,
                "work_item_status_detail": item.work_item_status_detail,
                "git_terminality": item.git_terminality,
                "terminal_commit": item.terminal_commit,
                "terminality_diagnostic": item.terminality_diagnostic,
            }
            for item in artifact.pending_actions
        ],
        "summary": artifact.summary,
    }
    _atomic_write_text(json_path, json.dumps(payload, indent=2))
    _atomic_write_text(md_path, _render_markdown(artifact))
    return artifact


def read_notification(state_dir: Path, recipient: BridgeAgent | str) -> NotificationArtifact | None:
    """Return the recipient's parsed notification artifact, or ``None`` if absent.

    Returns ``None`` if the JSON file does not exist or fails to parse.
    """
    path = _json_path(state_dir, recipient)
    if not path.is_file():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    # Read schema-v3 fields with backward-compatible defaults so a v2 artifact
    # on disk (no production v2 instances; only test fixtures) still parses.
    actions = tuple(
        ActionablePending(
            document_name=str(a["document_name"]),
            top_status=str(a["top_status"]),
            top_file=str(a["top_file"]),
            index_line_number=int(a["index_line_number"]),
            dispatchable=bool(a.get("dispatchable", True)),
            classification=str(a.get("classification", "ambiguous")),
            work_item_id=str(a["work_item_id"]) if a.get("work_item_id") is not None else None,
            work_item_stage=str(a["work_item_stage"]) if a.get("work_item_stage") is not None else None,
            work_item_resolution_status=(
                str(a["work_item_resolution_status"]) if a.get("work_item_resolution_status") is not None else None
            ),
            work_item_status_detail=(
                str(a["work_item_status_detail"]) if a.get("work_item_status_detail") is not None else None
            ),
            git_terminality=str(a.get("git_terminality", "ambiguous")),
            terminal_commit=str(a["terminal_commit"]) if a.get("terminal_commit") is not None else None,
            terminality_diagnostic=(
                str(a["terminality_diagnostic"]) if a.get("terminality_diagnostic") is not None else None
            ),
        )
        for a in raw.get("pending_actions", [])
    )
    return NotificationArtifact(
        schema_version=int(raw.get("schema_version", 0)),
        recipient=str(raw.get("recipient", _recipient_str(recipient))),
        written_at=str(raw.get("written_at", "")),
        poller_run_id=str(raw.get("poller_run_id", "")),
        pending_actions=actions,
        summary=str(raw.get("summary", "")),
    )


def clear_notification(state_dir: Path, recipient: BridgeAgent | str) -> None:
    """Remove the recipient's notification artifact (both JSON and markdown)."""
    _json_path(state_dir, recipient).unlink(missing_ok=True)
    _md_path(state_dir, recipient).unlink(missing_ok=True)
