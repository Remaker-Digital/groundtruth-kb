"""Cross-session resolution signals for pending owner-decision ledger entries.

The helper is deliberately read-only. It classifies whether a pending
``DECISION-NNNN`` entry is stale because a fresh Deliberation Archive row or a
live bridge thread has already carried the decision forward.
"""

from __future__ import annotations

import re
import sqlite3
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

RESOLVING_BRIDGE_STATUSES = frozenset({"GO", "VERIFIED", "WITHDRAWN"})
NON_RESOLVING_BRIDGE_STATUSES = frozenset({"NEW", "REVISED", "NO-GO", "ADVISORY", "DEFERRED"})

_DECISION_ID_RE = re.compile(r"^DECISION-\d+$", re.IGNORECASE)
_BRIDGE_FILE_RE = re.compile(
    r"(?:^|[\s(<>'\"`])bridge[/\\](?P<slug>[A-Za-z0-9][A-Za-z0-9_.-]*?)-\d{3,}\.md"
    r"(?=$|[\s)>,'\"`.;:])",
    re.IGNORECASE,
)
_BRIDGE_SLUG_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*[A-Za-z0-9]$")
_LIKELY_SLUG_TOKEN_RE = re.compile(
    r"(?<![A-Za-z0-9_.-])"
    r"(?P<slug>(?:gtkb|agent-red|commercial-readiness|harness-equivalence|antigravity|architecture)"
    r"[a-z0-9_.-]*-[a-z0-9_.-]+)"
    r"(?![A-Za-z0-9_.-])",
    re.IGNORECASE,
)

DeliberationReader = Callable[[], Iterable[Mapping[str, Any]]]
BridgeStatusReader = Callable[[str], str | None]


@dataclass(frozen=True)
class ResolutionSignal:
    """A durable artifact signal that resolves one pending decision."""

    decision_id: str
    resolved_via: str
    answer: str
    note: str
    evidence_id: str
    evidence_status: str = ""


def find_resolution_signal(
    entry: Any,
    *,
    deliberations: Sequence[Mapping[str, Any]],
    bridge_status_reader: BridgeStatusReader,
) -> ResolutionSignal | None:
    """Return a resolution signal for ``entry`` when exact fresh evidence exists.

    Ambiguous prose matches are intentionally ignored. A Deliberation Archive row
    resolves only when it is an ``owner_decision`` row whose structured
    ``source_ref`` or ``auq_id`` exactly owns the pending decision id.
    """

    decision_id = _normalize_decision_id(getattr(entry, "id", ""))
    if decision_id is None:
        return None

    for row in deliberations:
        signal = _signal_from_deliberation(decision_id, row)
        if signal is not None:
            return signal

    for slug in extract_bridge_slugs(entry):
        try:
            status = bridge_status_reader(slug)
        except Exception:  # noqa: BLE001 - fail closed for hook callers
            return None
        normalized_status = str(status or "").strip().upper()
        if normalized_status in RESOLVING_BRIDGE_STATUSES:
            return ResolutionSignal(
                decision_id=decision_id,
                resolved_via="cross_session_bridge_resolution",
                answer=f"Resolved via bridge/{slug} latest status {normalized_status}",
                note=(
                    "Cross-session owner-decision cleanup: explicit bridge "
                    f"thread {slug} is latest status {normalized_status}."
                ),
                evidence_id=slug,
                evidence_status=normalized_status,
            )
    return None


def resolve_pending_entries(
    entries: Iterable[Any],
    *,
    deliberation_reader: DeliberationReader,
    bridge_status_reader: BridgeStatusReader,
) -> dict[str, ResolutionSignal]:
    """Classify pending entries, returning ``{decision_id: signal}``.

    If the Deliberation Archive read fails, the whole pass returns no
    resolutions. Bridge-read failures fail closed for the affected entry.
    """

    try:
        deliberations = tuple(deliberation_reader())
    except Exception:  # noqa: BLE001 - hook must leave entries pending
        return {}

    signals: dict[str, ResolutionSignal] = {}
    for entry in entries:
        signal = find_resolution_signal(
            entry,
            deliberations=deliberations,
            bridge_status_reader=bridge_status_reader,
        )
        if signal is not None:
            signals[signal.decision_id] = signal
    return signals


def extract_bridge_slugs(entry: Any) -> tuple[str, ...]:
    """Extract explicit bridge-thread slugs from a pending ledger entry."""

    slugs: list[str] = []
    thread_ref = _normalize_bridge_slug(getattr(entry, "thread_ref", ""))
    if thread_ref:
        slugs.append(thread_ref)

    text = " ".join(
        str(part or "")
        for part in (
            getattr(entry, "question", ""),
            getattr(entry, "notes", ""),
        )
    )
    for match in _BRIDGE_FILE_RE.finditer(text):
        slug = _normalize_bridge_slug(match.group("slug"))
        if slug:
            slugs.append(slug)
    for match in _LIKELY_SLUG_TOKEN_RE.finditer(text):
        slug = _normalize_bridge_slug(match.group("slug"))
        if slug:
            slugs.append(slug)

    return tuple(dict.fromkeys(slugs))


def read_owner_decision_deliberations(project_root: Path) -> list[dict[str, Any]]:
    """Read fresh owner-decision deliberation rows without mutating MemBase."""

    db_path = project_root / "groundtruth.db"
    if not db_path.is_file():
        return []
    uri = db_path.resolve().as_uri() + "?mode=ro"
    conn = sqlite3.connect(uri, uri=True, timeout=1)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute("SELECT * FROM current_deliberations WHERE outcome = ?", ("owner_decision",)).fetchall()
    finally:
        conn.close()
    return [dict(row) for row in rows]


def build_live_bridge_status_reader(project_root: Path) -> BridgeStatusReader:
    """Return a reader backed by the live numbered bridge-file chain."""

    from groundtruth_kb.bridge.read_commands import show_thread

    def _read(slug: str) -> str | None:
        payload = show_thread(project_root, slug, compact=True)
        if payload is None:
            return None
        return str(payload.get("latest_status") or "")

    return _read


def _signal_from_deliberation(decision_id: str, row: Mapping[str, Any]) -> ResolutionSignal | None:
    if str(row.get("outcome") or "").strip() != "owner_decision":
        return None
    source_ref = _normalize_decision_id(row.get("source_ref", ""))
    auq_id = _normalize_decision_id(row.get("auq_id", ""))
    if source_ref != decision_id and auq_id != decision_id:
        return None
    delib_id = str(row.get("id") or "").strip()
    if not delib_id:
        return None
    return ResolutionSignal(
        decision_id=decision_id,
        resolved_via="cross_session_deliberation_resolution",
        answer=f"Resolved via Deliberation Archive owner_decision row {delib_id}",
        note=(
            f"Cross-session owner-decision cleanup: exact owner_decision deliberation {delib_id} owns {decision_id}."
        ),
        evidence_id=delib_id,
        evidence_status="owner_decision",
    )


def _normalize_decision_id(value: Any) -> str | None:
    text = str(value or "").strip().upper()
    if _DECISION_ID_RE.fullmatch(text):
        return text
    return None


def _normalize_bridge_slug(value: Any) -> str | None:
    text = str(value or "").strip().strip("<>()[]{}'\"`.,;:")
    if not text:
        return None
    text = text.replace("\\", "/")
    if "/" in text:
        parts = [part for part in text.split("/") if part]
        text = parts[-1]
    if text.lower().endswith(".md"):
        text = text[:-3]
    versioned = re.match(r"^(?P<slug>.+)-\d{3,}$", text)
    if versioned is not None:
        text = versioned.group("slug")
    if "-" not in text or _BRIDGE_SLUG_RE.fullmatch(text) is None:
        return None
    return text.lower()
