# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Smart-poller notification artifacts (current-state).

Per ``bridge/gtkb-bridge-poller-p3-notify-2026-04-29-008.md`` GO at REVISED-3,
this module owns the current-state notification artifact lifecycle:

- ``compute_actionable_pending(parse_result, *, project_root)`` derives
  per-recipient actionable lists from the CURRENT TOP STATUSES of parsed
  ``BridgeDocument`` entries — NOT from checkpoint diffs. The checkpoint is
  audit-only in the notify path.
- ``update_notification(state_dir, recipient, items)`` writes (non-empty) or
  removes (empty) the recipient's notification artifact under
  ``<state_dir>/notifications/pending-bridge-action-{recipient}.{json,md}``.
- ``read_notification(state_dir, recipient)`` returns the parsed artifact or
  ``None`` if absent.
- ``clear_notification(state_dir, recipient)`` removes both the JSON and
  markdown companion files.

Routing contract (per ``AGENTS.md:153-159`` + DELIB-S319-SMART-POLLER-OBJECTIVE-CLARIFICATION):

- ``NEW`` / ``REVISED`` top status → Codex (Loyal Opposition reviews).
- ``GO`` / ``NO-GO`` top status → Prime Builder (Prime acts).
- ``VERIFIED`` top status → not actionable for either.

Schema v2 with ``pending_actions[]``; v1's transition-shaped ``pending_transitions[]``
is NOT produced or read.
"""

from __future__ import annotations

import datetime as dt
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from groundtruth_kb.bridge.detector import BridgeStatus, ParseResult
from groundtruth_kb.bridge.routing import BridgeAgent

NOTIFY_SUBDIR: Final[str] = "notifications"
NOTIFY_SCHEMA_VERSION: Final[int] = 2

# Per AGENTS.md:153-159 + DELIB-S319-SMART-POLLER-OBJECTIVE-CLARIFICATION.
# VERIFIED is closure for both Prime and Codex (not actionable).
ACTIONABLE_STATUSES_FOR_PRIME: Final[frozenset[str]] = frozenset({BridgeStatus.GO.value, BridgeStatus.NO_GO.value})
ACTIONABLE_STATUSES_FOR_CODEX: Final[frozenset[str]] = frozenset({BridgeStatus.NEW.value, BridgeStatus.REVISED.value})


@dataclass(frozen=True)
class ActionablePending:
    """One document's currently-actionable top status for a specific recipient."""

    document_name: str
    top_status: str
    top_file: str
    index_line_number: int


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
        entry = ActionablePending(
            document_name=doc.name,
            top_status=str(top.status.value),
            top_file=top.file_path,
            index_line_number=top.line_number,
        )
        status_str = str(top.status.value)
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
        lines.append("| Document | Top status | Top file | INDEX line |")
        lines.append("|---|---|---|---|")
        for item in artifact.pending_actions:
            lines.append(f"| {item.document_name} | {item.top_status} | {item.top_file} | {item.index_line_number} |")
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
    actions = tuple(
        ActionablePending(
            document_name=str(a["document_name"]),
            top_status=str(a["top_status"]),
            top_file=str(a["top_file"]),
            index_line_number=int(a["index_line_number"]),
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
