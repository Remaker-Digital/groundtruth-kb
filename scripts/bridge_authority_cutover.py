# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Bridge authority-direction switch + cutover/revert tooling (WI-4510 Phase 3).

This module is the canonical home for the *bridge authority direction* — the
switch that selects whether ``bridge/INDEX.md`` is the directly-written authority
(``index_canonical``, the default / rollback direction) or a byte-faithful
generated view of the TAFE shadow (``tafe_canonical``, the post-flip direction).

It ships the **default-OFF** half of the WI-4510 Phase-3 implementation:

- :func:`read_authority_direction` — the safe-default reader (absent state file or
  any read error -> ``index_canonical``) that the ``atomic_index_update``
  chokepoint consults under ``DCL-INDEX-GENERATED-VIEW-001`` #3.
- :func:`freeze_index` / :func:`flip_to_tafe_canonical` /
  :func:`revert_to_index_canonical` — the reversibility backstop (a timestamped
  immutable frozen INDEX copy + a coded revert) under
  ``DCL-INDEX-GENERATED-VIEW-001`` #4.

Because the default direction is ``index_canonical`` and the reader fails safe to
it, importing or installing this module changes no runtime behavior: the system
stays byte-identical to today until a *separate* gate-2 owner decision sets
``tafe_canonical``. The CLI ``flip`` subcommand is guarded behind
``--confirm-irreversible`` and is only ever invoked inside the gate-2,
swarm-quiesced execution window.

Deferred to the focused follow-on slice (NOT in this module yet): the
``atomic_index_update`` authority-direction branch, the ``insert_bridge_thread_atomic``
DB transaction helper, and the publish-reconcile guard (``DCL-INDEX-GENERATED-VIEW-001``
#10 / #11). Those touch the hot ``db.py`` write surface and the INDEX chokepoint and
are implemented separately.

Authority: ``bridge/gtkb-wi4510-phase-3-authority-flip-003.md`` (Loyal Opposition
GO at ``-004``); ``ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001``;
``DCL-INDEX-GENERATED-VIEW-001`` (proposed).
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

DIRECTION_INDEX_CANONICAL = "index_canonical"
DIRECTION_TAFE_CANONICAL = "tafe_canonical"
VALID_DIRECTIONS = (DIRECTION_INDEX_CANONICAL, DIRECTION_TAFE_CANONICAL)

# The safe default. Absence of the state file, a malformed file, or an
# unrecognized value all resolve to index_canonical so a corrupt or missing
# switch can never silently engage the post-flip write path.
DEFAULT_DIRECTION = DIRECTION_INDEX_CANONICAL

_STATE_RELATIVE_PATH = Path("harness-state") / "bridge-authority-direction.json"
_FROZEN_DIR_RELATIVE = Path("bridge") / ".authority-cutover"
_INDEX_RELATIVE_PATH = Path("bridge") / "INDEX.md"

_PROVENANCE = "bridge/gtkb-wi4510-phase-3-authority-flip-003.md (GO -004)"


def direction_state_path(project_root: str | os.PathLike[str]) -> Path:
    """Return the single canonical authority-direction state surface."""
    return Path(project_root) / _STATE_RELATIVE_PATH


def _utc_stamp(now: datetime | None = None) -> str:
    """Compact UTC stamp (``YYYYMMDDTHHMMSSZ``) for frozen-copy filenames."""
    moment = now or datetime.now(UTC)
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=UTC)
    return moment.astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")


def _utc_iso(now: datetime | None = None) -> str:
    moment = now or datetime.now(UTC)
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=UTC)
    return moment.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_authority_direction(project_root: str | os.PathLike[str]) -> str:
    """Return the current bridge authority direction.

    Absence of the state file == ``index_canonical`` (safe default per
    ``DCL-INDEX-GENERATED-VIEW-001`` #3). Any malformed / unreadable state, or an
    unrecognized ``authority_direction`` value, also fails safe to
    ``index_canonical`` so a corrupt switch never engages the post-flip path.
    """
    path = direction_state_path(project_root)
    try:
        raw = path.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return DEFAULT_DIRECTION
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return DEFAULT_DIRECTION
    if not isinstance(data, dict):
        return DEFAULT_DIRECTION
    direction = data.get("authority_direction")
    if direction not in VALID_DIRECTIONS:
        return DEFAULT_DIRECTION
    return direction


def _atomic_write_text(target: Path, text: str) -> None:
    """Atomic write via a sibling temp file plus ``os.replace``.

    Mirrors ``scripts/bridge_index_writer._atomic_write`` so the cutover tooling
    and the INDEX chokepoint share identical durability semantics.
    """
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(f"{target.name}.{uuid.uuid4().hex}.tmp")
    try:
        tmp.write_text(text, encoding="utf-8")
        os.replace(str(tmp), str(target))
    except BaseException:
        with contextlib.suppress(FileNotFoundError, OSError):
            tmp.unlink()
        raise


def write_authority_direction(
    project_root: str | os.PathLike[str],
    direction: str,
    *,
    reason: str | None = None,
    now: datetime | None = None,
) -> Path:
    """Set the canonical authority direction (atomic). Rejects invalid values."""
    if direction not in VALID_DIRECTIONS:
        raise ValueError(f"invalid authority direction {direction!r}; expected one of {VALID_DIRECTIONS}")
    payload = {
        "authority_direction": direction,
        "updated_at": _utc_iso(now),
        "reason": reason or "",
        "authority": _PROVENANCE,
    }
    path = direction_state_path(project_root)
    _atomic_write_text(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return path


def freeze_index(project_root: str | os.PathLike[str], *, now: datetime | None = None) -> Path:
    """Write a timestamped, immutable (read-only) frozen copy of ``bridge/INDEX.md``.

    The frozen copy is the disaster-recovery floor for an ``index_canonical``
    revert (``DCL-INDEX-GENERATED-VIEW-001`` #4). Returns the frozen copy path.
    """
    root = Path(project_root)
    index_path = root / _INDEX_RELATIVE_PATH
    if not index_path.is_file():
        raise FileNotFoundError(f"cannot freeze: bridge INDEX not found at {index_path}")
    frozen_dir = root / _FROZEN_DIR_RELATIVE
    frozen_dir.mkdir(parents=True, exist_ok=True)
    frozen_path = frozen_dir / f"INDEX.frozen-{_utc_stamp(now)}.md"
    frozen_path.write_text(index_path.read_text(encoding="utf-8"), encoding="utf-8")
    # Best-effort immutability: mark the frozen copy read-only.
    with contextlib.suppress(OSError):
        os.chmod(frozen_path, 0o444)
    return frozen_path


def flip_to_tafe_canonical(
    project_root: str | os.PathLike[str],
    *,
    reason: str | None = None,
    now: datetime | None = None,
) -> Path:
    """Freeze the current INDEX, then set ``authority_direction = tafe_canonical``.

    This is the irreversible authority flip (the ``cutover`` mutation class). It is
    gate-2 owner-authorized; this function is only the coded mechanism, invoked
    inside the swarm-quiesced gate-2 execution window. Returns the frozen INDEX path.
    """
    frozen_path = freeze_index(project_root, now=now)
    write_authority_direction(
        project_root,
        DIRECTION_TAFE_CANONICAL,
        reason=reason or "WI-4510 Phase-3 authority flip (gate-2 owner-authorized)",
        now=now,
    )
    return frozen_path


def revert_to_index_canonical(
    project_root: str | os.PathLike[str],
    *,
    restore_frozen: str | os.PathLike[str] | None = None,
    reason: str | None = None,
    now: datetime | None = None,
) -> Path | None:
    """Revert authority to ``index_canonical`` (the documented rollback).

    Optionally restore a frozen INDEX copy if the post-flip INDEX is suspect
    (``DCL-INDEX-GENERATED-VIEW-001`` #4). Returns the restored INDEX path, or
    ``None`` when no frozen restore was requested.
    """
    write_authority_direction(
        project_root,
        DIRECTION_INDEX_CANONICAL,
        reason=reason or "WI-4510 Phase-3 revert to index_canonical",
        now=now,
    )
    if restore_frozen is None:
        return None
    frozen = Path(restore_frozen)
    if not frozen.is_file():
        raise FileNotFoundError(f"frozen INDEX copy not found: {frozen}")
    index_path = Path(project_root) / _INDEX_RELATIVE_PATH
    _atomic_write_text(index_path, frozen.read_text(encoding="utf-8"))
    return index_path


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="GT-KB project root (defaults to the repository root).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="Print the current bridge authority direction.")
    sub.add_parser("freeze", help="Write a timestamped immutable frozen copy of bridge/INDEX.md.")

    flip = sub.add_parser("flip", help="Freeze INDEX then set tafe_canonical (gate-2 only).")
    flip.add_argument(
        "--confirm-irreversible",
        action="store_true",
        help="Required acknowledgement that the flip is gate-2 owner-authorized and irreversible.",
    )
    flip.add_argument("--reason", default=None)

    revert = sub.add_parser("revert", help="Revert authority to index_canonical (rollback).")
    revert.add_argument("--restore-frozen", type=Path, default=None, help="Frozen INDEX copy to restore.")
    revert.add_argument("--reason", default=None)

    sub.add_parser(
        "reconcile",
        help="Heal a TAFE-ahead publish split (republish INDEX from the shadow) or quarantine INDEX-ahead.",
    )

    args = parser.parse_args(argv)
    root = args.project_root

    if args.command == "status":
        print(read_authority_direction(root))
        return 0
    if args.command == "freeze":
        print(str(freeze_index(root)))
        return 0
    if args.command == "flip":
        if not args.confirm_irreversible:
            print(
                "refusing to flip: the authority flip is irreversible and gate-2 owner-authorized; "
                "pass --confirm-irreversible to proceed inside the quiesced execution window.",
                file=sys.stderr,
            )
            return 2
        frozen = flip_to_tafe_canonical(root, reason=args.reason)
        print(f"flipped to {DIRECTION_TAFE_CANONICAL}; frozen INDEX backstop at {frozen}")
        return 0
    if args.command == "revert":
        restored = revert_to_index_canonical(root, restore_frozen=args.restore_frozen, reason=args.reason)
        msg = f"reverted to {DIRECTION_INDEX_CANONICAL}"
        if restored is not None:
            msg += f"; restored INDEX from frozen copy -> {restored}"
        print(msg)
        return 0
    if args.command == "reconcile":
        result = _reconcile_publish(root)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 1 if result.get("state") == "index_ahead" else 0
    return 1


def _reconcile_publish(project_root: str | os.PathLike[str]) -> dict:
    """Run the publish-reconcile guard (shared with ``gt flow publish-reconcile``).

    Delegates to ``scripts/bridge_index_writer.reconcile_publish`` (the lock-holding
    implementation): heals a TAFE-ahead split by republishing INDEX from the
    append-only shadow, or quarantines an INDEX-ahead state. Returns the verdict
    dict. WI-4510 Phase 3 (``DCL-INDEX-GENERATED-VIEW-001`` #10/#11).
    """
    try:
        from scripts.bridge_index_writer import reconcile_publish
    except ModuleNotFoundError:  # pragma: no cover - direct script execution fallback
        from bridge_index_writer import reconcile_publish
    return reconcile_publish(project_root)


if __name__ == "__main__":
    raise SystemExit(_main())
