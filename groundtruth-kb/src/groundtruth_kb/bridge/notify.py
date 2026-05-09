# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Bridge dispatch notification artifacts (RETIRED smart-poller substrate).

RETIRED (2026-05-09): This module belongs to the retired smart-poller
runtime. The smart-poller scheduled task and runner script have been
archived to ``archive/smart-poller-2026-05-09/``; bridge dispatch is now
governed by the cross-harness event-driven trigger
(``scripts/cross_harness_bridge_trigger.py``) registered as PostToolUse +
Stop hooks in ``.claude/settings.json`` and ``.codex/hooks.json``. The
notification-artifact API below is retained for compatibility and historical
reference; the trigger writes its own dispatch state at
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

- ``NEW`` / ``REVISED`` top status → Codex (Loyal Opposition reviews).
  Always dispatchable; kind classification is informational only.
- ``NO-GO`` top status → Prime Builder (Prime revises). Always dispatchable
  because NO-GO is "proposal requires changes before approval", regardless
  of bridge_kind.
- ``GO`` top status → Prime Builder (Prime acts). Dispatchable iff the
  bridge_kind classification is NOT terminal — terminal kinds (scoping,
  closure, parking, index_reconciliation, thread_reconciliation,
  operational_state_change, candidate_spec_intake) have no Prime follow-up
  after a GO verdict.
- ``VERIFIED`` top status → not actionable for either.

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
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from groundtruth_kb.bridge.detector import BridgeDocument, BridgeStatus, BridgeVersion, ParseResult
from groundtruth_kb.bridge.routing import BridgeAgent

NOTIFY_SUBDIR: Final[str] = "notifications"
NOTIFY_SCHEMA_VERSION: Final[int] = 3

# Per AGENTS.md:153-159 + DELIB-S319-SMART-POLLER-OBJECTIVE-CLARIFICATION.
# VERIFIED is closure for both Prime and Codex (not actionable).
ACTIONABLE_STATUSES_FOR_PRIME: Final[frozenset[str]] = frozenset({BridgeStatus.GO.value, BridgeStatus.NO_GO.value})
ACTIONABLE_STATUSES_FOR_CODEX: Final[frozenset[str]] = frozenset({BridgeStatus.NEW.value, BridgeStatus.REVISED.value})

# Feature flag for kind-aware routing. =0 disables filtering and matches
# pre-refinement behavior (all entries dispatchable=True via fallback).
KIND_AWARE_ROUTING_ENV_VAR: Final[str] = "GTKB_NOTIFY_KIND_AWARE_ROUTING"

# Bridge-kind substring tokens. Matched against the lowercased + kebab-to-snake-
# normalized bridge_kind value. Order matters: terminal is checked first so the
# more-specific tokens (e.g., "scoping" inside "implementation_scoping") win
# before broader matches. Per smart-poller-kind-aware-routing-2026-04-30-009
# REVISED-4 §1.1.
_KIND_TERMINAL_TOKENS: Final[tuple[str, ...]] = (
    "scoping",                  # implementation_scoping, governance_scoping_proposal, scoping_proposal, scoping_addendum
    "closure",
    "parking",                  # parking_acknowledgement
    "index_reconciliation",
    "thread_reconciliation",
    "operational_state_change",
    "candidate_spec_intake",
)

_KIND_DISPATCHABLE_TOKENS: Final[tuple[str, ...]] = (
    "implementation_proposal",
    "implementation_slice",
    "multiphase_implementation",
    "fix",
    "governance_proposal",
    "architecture_proposal",
    "post_implementation",      # catches post_implementation_report, post_implementation_report_revision, post-implementation-report (after kebab-norm)
    "post_impl",                # catches post_impl_report
    "implementation_report",
)

# Bare "proposal", "review", "verification", and unrecognized kinds → ambiguous
# → status-only fallback. Ambiguous entries are dispatched on actionable
# statuses (preserving legacy behavior for un-migrated bridges).

# Frontmatter parser: bridge_kind: <value> at start-of-line, allows whitespace.
_BRIDGE_KIND_RE: Final[re.Pattern[str]] = re.compile(r"^bridge_kind:\s*(\S+)", re.MULTILINE)

# Header read budget (bytes). bridge_kind is always in the header section.
_HEADER_READ_BUDGET_BYTES: Final[int] = 4096


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
      spec intake)
    - "ambiguous" — bridge_kind missing, bare "proposal", "review",
      "verification", or unrecognized; falls back to status-only routing
      via the dispatchable invariant in `_derive_dispatchable`
    """
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

    - NEW / REVISED → True (Codex reviews regardless of kind classification;
      terminal-kind means "no Prime follow-up", not "no Codex review")
    - NO-GO → True (Prime revises regardless of kind, per
      file-bridge-protocol.md:92,104-107: "proposal requires changes before
      approval")
    - GO → ``classification != "terminal"`` (Prime filters terminal kinds,
      keeps everything else)
    - VERIFIED + others → False (not actionable)
    """
    if top_status in ACTIONABLE_STATUSES_FOR_CODEX:
        return True
    if top_status == BridgeStatus.NO_GO.value:
        return True
    if top_status == BridgeStatus.GO.value:
        return classification != "terminal"
    return False


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
        return status in ACTIONABLE_STATUSES_FOR_PRIME
    if recipient is BridgeAgent.CODEX:
        return status in ACTIONABLE_STATUSES_FOR_CODEX
    return False


def compute_actionable_pending(
    parse_result: ParseResult,
    *,
    project_root: Path,
) -> tuple[list[ActionablePending], list[ActionablePending]]:
    """Compute current-state actionable pending entries from the parsed INDEX.

    Returns ``(actionable_for_prime, actionable_for_codex)``. Each list contains
    one entry per document whose CURRENT TOP STATUS is actionable for that
    recipient.

    - ``GO`` / ``NO-GO`` → Prime list.
    - ``NEW`` / ``REVISED`` → Codex list.
    - ``VERIFIED`` → excluded (closure for both per AGENTS.md role contract).
    - Documents whose top file is missing on disk are excluded (UNROUTABLE_FILE_MISSING
      semantic from P1 routing).

    Order preserved from ``parse_result.documents`` (INDEX-file order, most-recent at top).

    Audit-only: the checkpoint is NOT consulted by this function. Same parse_result
    + same on-disk file presence → same output. Deterministic.
    """
    actionable_for_prime: list[ActionablePending] = []
    actionable_for_codex: list[ActionablePending] = []

    for doc in parse_result.documents:
        if not doc.versions:
            continue
        top = doc.versions[0]
        if not (project_root / top.file_path).is_file():
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
        )
        if status_str in ACTIONABLE_STATUSES_FOR_PRIME:
            actionable_for_prime.append(entry)
        elif status_str in ACTIONABLE_STATUSES_FOR_CODEX:
            actionable_for_codex.append(entry)
        # VERIFIED + anything else: not actionable, skip.

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
        lines.append("| Document | Top status | Top file | INDEX line | Dispatchable | Classification |")
        lines.append("|---|---|---|---|---|---|")
        for item in artifact.pending_actions:
            dispatchable_marker = "yes" if item.dispatchable else "no"
            # `(terminal)` prefix shown only when classification is terminal AND
            # the entry's status is GO — i.e., where terminal classification
            # actually suppresses Prime dispatch. NO-GO terminal-kind entries
            # show classification in the column but no prefix because Prime
            # revision is preserved.
            prefix = "(terminal) " if item.classification == "terminal" and item.top_status == BridgeStatus.GO.value else ""
            lines.append(
                f"| {prefix}{item.document_name} | {item.top_status} | {item.top_file} | "
                f"{item.index_line_number} | {dispatchable_marker} | {item.classification} |"
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
