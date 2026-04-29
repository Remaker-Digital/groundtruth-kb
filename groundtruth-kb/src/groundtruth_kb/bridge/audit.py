# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Smart-poller audit log: append-only JSON-lines record of detector events.

Per ``bridge/gtkb-bridge-poller-p1-detector-003.md`` section 3.6, the audit
log captures every event the detector observes: bootstrap baselines,
routable transitions, unroutable transitions, corrupt-checkpoint recovery,
and parse warnings. The log is append-only at ``state_dir/audit.jsonl``;
each line is a complete JSON object with ``kind``, ``ts``, and event-specific
payload fields.

Out of scope for this module: parsing (see detector.py),
diff/checkpoint (see checkpoint.py), routing (see routing.py),
P3 invoker (gated on P2.5 spike per umbrella -007).
"""

from __future__ import annotations

import datetime as dt
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

AUDIT_FILENAME = "audit.jsonl"


@dataclass(frozen=True)
class AuditEvent:
    """A single audit-log event."""

    kind: str
    ts: str
    payload: dict[str, Any] = field(default_factory=dict)


def _now_iso() -> str:
    return dt.datetime.now(dt.UTC).isoformat(timespec="seconds")


def _audit_path(state_dir: Path) -> Path:
    return state_dir / AUDIT_FILENAME


def emit_audit_event(state_dir: Path, kind: str, payload: dict[str, Any] | None = None) -> AuditEvent:
    """Append a new audit event to ``state_dir/audit.jsonl``.

    The event is timestamped at emission time. Returns the constructed event
    so callers can inspect ``ts`` immediately.
    """
    state_dir.mkdir(parents=True, exist_ok=True)
    event = AuditEvent(kind=kind, ts=_now_iso(), payload=dict(payload or {}))
    line = json.dumps(
        {"kind": event.kind, "ts": event.ts, **event.payload},
        ensure_ascii=False,
    )
    with _audit_path(state_dir).open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    return event


def read_audit_log(state_dir: Path) -> tuple[AuditEvent, ...]:
    """Read all events from the audit log in append order.

    Returns an empty tuple if the log file does not exist. Malformed lines
    are skipped silently — the audit log is intended to be tail-readable
    even if individual events are partially corrupted.
    """
    path = _audit_path(state_dir)
    if not path.is_file():
        return ()
    events: list[AuditEvent] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            continue
        kind = obj.pop("kind", None)
        ts = obj.pop("ts", None)
        if not isinstance(kind, str) or not isinstance(ts, str):
            continue
        events.append(AuditEvent(kind=kind, ts=ts, payload=obj))
    return tuple(events)


def emit_bootstrap_event(
    state_dir: Path,
    *,
    documents_seen: int,
    corrupt_checkpoint_recovered: bool = False,
    detail: str = "",
) -> AuditEvent:
    """Record a bootstrap event per design section 3.7."""
    payload: dict[str, Any] = {
        "documents_seen": documents_seen,
        "transitions_routable": 0,
        "corrupt_checkpoint_recovered": corrupt_checkpoint_recovered,
    }
    if detail:
        payload["detail"] = detail
    return emit_audit_event(state_dir, "bootstrap", payload)


def emit_transition_event(
    state_dir: Path,
    *,
    outcome: str,
    document_name: str,
    from_status: str | None,
    to_status: str,
    to_file: str,
    recipient: str | None,
    detail: str = "",
) -> AuditEvent:
    """Record a transition event tagged by routing outcome."""
    payload: dict[str, Any] = {
        "outcome": outcome,
        "document_name": document_name,
        "from_status": from_status,
        "to_status": to_status,
        "to_file": to_file,
        "recipient": recipient,
    }
    if detail:
        payload["detail"] = detail
    return emit_audit_event(state_dir, "transition", payload)
