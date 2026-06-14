# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Per-entry dispatch-starvation telemetry (WI-4480 Slice A).

This module is a **zero-risk observational detector**. It records, per
recipient, how many consecutive dispatch rounds each actionable bridge entry
has gone *un-selected* while the cap-limited selector chose other (older)
entries. It exists to quantify the cap-2 oldest-first starvation hazard
documented in WI-4480 — and to size the deferred Slice-B selection-fairness
fix — WITHOUT changing dispatch selection, the byte-identical actionable
``_signature`` invariant, or any dispatch decision.

The cross-harness trigger calls :func:`record_starvation` immediately after it
has computed (and signed) the ``filtered`` and ``selected`` lists. The call is
exception-swallowed at the call site, and :func:`record_starvation` is itself
fail-safe: any load/parse/write error returns silently. Telemetry must never
perturb the thing it observes.

Authority: ``bridge/gtkb-wi4480-dispatch-starvation-telemetry-001.md`` (Codex
GO at ``-002``); ``GOV-STANDING-BACKLOG-001`` (WI-4480);
``PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-1``.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import sys
import uuid
from pathlib import Path
from typing import Any

# Telemetry lives in the in-root bridge-poller dispatch-state directory,
# separate from ``dispatch-state.json`` so it never shares the
# signature-bearing dispatch state.
TELEMETRY_STATE_SUBDIR = (".gtkb-state", "bridge-poller")
TELEMETRY_FILENAME = "starvation-telemetry.json"
SCHEMA_VERSION = 1

# Default consecutive-non-selection count at which an entry is flagged as
# starved. Overridable via ``GTKB_DISPATCH_STARVATION_THRESHOLD``.
DEFAULT_THRESHOLD = 5
THRESHOLD_ENV_VAR = "GTKB_DISPATCH_STARVATION_THRESHOLD"


def _now_iso() -> str:
    return dt.datetime.now(dt.UTC).isoformat(timespec="seconds")


def resolve_threshold(explicit: int | None = None) -> int:
    """Resolve the starvation threshold from an explicit value or the env var.

    Falls back to :data:`DEFAULT_THRESHOLD` when neither is a usable positive
    integer. Never raises.
    """
    if isinstance(explicit, int) and explicit > 0:
        return explicit
    raw = os.environ.get(THRESHOLD_ENV_VAR)
    if raw is not None and raw.strip():
        try:
            parsed = int(raw.strip())
        except (TypeError, ValueError):
            parsed = 0
        if parsed > 0:
            return parsed
    return DEFAULT_THRESHOLD


def _empty_telemetry() -> dict[str, Any]:
    return {"schema_version": SCHEMA_VERSION, "recipients": {}}


def _coerce_telemetry(raw: Any) -> dict[str, Any]:
    """Return a well-formed telemetry dict from possibly-malformed input."""
    if not isinstance(raw, dict):
        return _empty_telemetry()
    recipients = raw.get("recipients")
    if not isinstance(recipients, dict):
        recipients = {}
    return {"schema_version": SCHEMA_VERSION, "recipients": recipients}


def update_starvation_telemetry(
    prev: dict[str, Any] | None,
    recipient: str,
    actionable_keys: list[str],
    selected_keys: list[str],
    now_iso: str,
    threshold: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Pure update of the starvation telemetry for one recipient.

    No I/O. Given the prior telemetry and the current dispatch round's
    ``actionable_keys`` (the dispatchable ``filtered`` entries) and
    ``selected_keys`` (the cap-selected ``selected`` entries), returns
    ``(new_telemetry, starved)`` where:

    - each ``actionable ∧ ¬selected`` key's ``consecutive_non_selection``
      counter is incremented (and ``first_starved_at`` is stamped once, on
      first starvation);
    - each ``selected`` key's record is reset (dropped);
    - records for keys no longer in ``actionable_keys`` are pruned;
    - ``starved`` lists the recipient's keys whose counter ``>= threshold``,
      sorted by descending count then key, each as
      ``{document_name, consecutive_non_selection, first_starved_at}``.

    Other recipients' records are carried forward untouched.
    """
    telemetry = _coerce_telemetry(prev)
    recipients = dict(telemetry["recipients"])

    prior_recipient = recipients.get(recipient)
    prior_entries = prior_recipient.get("entries") if isinstance(prior_recipient, dict) else None
    entries: dict[str, Any] = dict(prior_entries) if isinstance(prior_entries, dict) else {}

    actionable_set = set(actionable_keys)
    selected_set = set(selected_keys)

    for key in actionable_keys:
        if key in selected_set:
            # Selection resets the starvation counter.
            entries.pop(key, None)
            continue
        rec = entries.get(key)
        rec = dict(rec) if isinstance(rec, dict) else {}
        count = rec.get("consecutive_non_selection", 0)
        rec["consecutive_non_selection"] = (int(count) if isinstance(count, int) else 0) + 1
        if not rec.get("first_starved_at"):
            rec["first_starved_at"] = now_iso
        entries[key] = rec

    # Prune records for entries that are no longer actionable (resolved,
    # withdrawn, verified, or otherwise dropped from the dispatchable set).
    for key in list(entries):
        if key not in actionable_set:
            del entries[key]

    recipients[recipient] = {"entries": entries}
    telemetry["recipients"] = recipients

    starved = [
        {
            "document_name": key,
            "consecutive_non_selection": int(rec.get("consecutive_non_selection", 0)),
            "first_starved_at": rec.get("first_starved_at"),
        }
        for key, rec in entries.items()
        if isinstance(rec, dict) and int(rec.get("consecutive_non_selection", 0)) >= threshold
    ]
    starved.sort(key=lambda r: (-r["consecutive_non_selection"], r["document_name"]))
    return telemetry, starved


def _telemetry_path(project_root: Path) -> Path:
    return project_root.joinpath(*TELEMETRY_STATE_SUBDIR, TELEMETRY_FILENAME)


def _load_telemetry(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError, ValueError):
        return _empty_telemetry()
    return _coerce_telemetry(raw)


def _atomic_write(path: Path, payload: dict[str, Any]) -> None:
    """Atomically write ``payload`` as JSON to ``path``."""
    path.parent.mkdir(parents=True, exist_ok=True)
    unique = f"{os.getpid()}-{uuid.uuid4().hex[:8]}"
    tmp = path.with_suffix(path.suffix + f".{unique}.tmp")
    try:
        tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        os.replace(tmp, path)
    finally:
        try:
            if tmp.exists():
                tmp.unlink()
        except OSError:
            pass


def record_starvation(
    recipient: str,
    actionable_keys: list[str],
    selected_keys: list[str],
    *,
    project_root: Path,
    now_iso: str | None = None,
    threshold: int | None = None,
) -> list[dict[str, Any]]:
    """Load, update, and persist starvation telemetry for one dispatch round.

    **Fail-safe.** Any error (load/parse/write/permission) is swallowed and an
    empty list is returned. This function MUST NOT raise into the dispatch
    flow: telemetry can never affect dispatch selection, the actionable
    ``_signature``, or any dispatch decision.

    Returns the list of currently-starved entries for ``recipient`` (those at
    or above the resolved threshold) on success, or ``[]`` on any failure.
    """
    try:
        path = _telemetry_path(Path(project_root))
        resolved_threshold = resolve_threshold(threshold)
        stamp = now_iso or _now_iso()
        prev = _load_telemetry(path)
        telemetry, starved = update_starvation_telemetry(
            prev,
            recipient,
            list(actionable_keys),
            list(selected_keys),
            stamp,
            resolved_threshold,
        )
        _atomic_write(path, telemetry)
        return starved
    except Exception:  # noqa: BLE001 - telemetry must never break dispatch
        return []


def report_starved(project_root: Path, threshold: int | None = None) -> dict[str, Any]:
    """Return currently-starved entries per recipient for owner/swarm visibility.

    Read-only. Returns ``{"threshold": int, "recipients": {recipient: [..]}}``
    where each list contains the recipient's entries at or above the threshold,
    sorted by descending count then key.
    """
    resolved_threshold = resolve_threshold(threshold)
    path = _telemetry_path(Path(project_root))
    telemetry = _load_telemetry(path)
    out: dict[str, list[dict[str, Any]]] = {}
    recipients = telemetry.get("recipients", {})
    if isinstance(recipients, dict):
        for recipient, rec in recipients.items():
            entries = rec.get("entries") if isinstance(rec, dict) else None
            if not isinstance(entries, dict):
                continue
            starved = [
                {
                    "document_name": key,
                    "consecutive_non_selection": int(entry.get("consecutive_non_selection", 0)),
                    "first_starved_at": entry.get("first_starved_at"),
                }
                for key, entry in entries.items()
                if isinstance(entry, dict) and int(entry.get("consecutive_non_selection", 0)) >= resolved_threshold
            ]
            if starved:
                starved.sort(key=lambda r: (-r["consecutive_non_selection"], r["document_name"]))
                out[recipient] = starved
    return {"threshold": resolved_threshold, "recipients": out}


def _resolve_project_root(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).resolve()
    return Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Report currently-starved bridge dispatch entries (WI-4480 detector).",
    )
    parser.add_argument(
        "--project-root",
        default=None,
        help="GT-KB project root. Default: the repo containing this script.",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=None,
        help=f"Starvation threshold. Default: ${THRESHOLD_ENV_VAR} or {DEFAULT_THRESHOLD}.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of human-readable text.",
    )
    args = parser.parse_args(argv)

    project_root = _resolve_project_root(args.project_root)
    report = report_starved(project_root, args.threshold)

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0

    threshold = report["threshold"]
    recipients = report["recipients"]
    if not recipients:
        print(f"No starved dispatch entries (threshold={threshold}).")
        return 0

    print(f"Starved dispatch entries (threshold={threshold}):")
    for recipient in sorted(recipients):
        print(f"\n  recipient: {recipient}")
        for entry in recipients[recipient]:
            print(
                f"    - {entry['document_name']}: "
                f"un-selected x{entry['consecutive_non_selection']} "
                f"since {entry['first_starved_at']}"
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
