# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Smart-poller checkpoint persistence + diff (bootstrap-safe).

Per ``bridge/gtkb-bridge-poller-p1-detector-003.md`` sections 3.4 and 3.7,
the checkpoint persists each document's current top status so subsequent
runs can detect transitions. Bootstrap mode: first run with no checkpoint
writes a baseline and emits zero transitions. Corrupt checkpoints recover
into bootstrap mode with a warning.

Out of scope for this module: parsing (see detector.py),
routing/transitions classification (see routing.py),
audit emission (see audit.py).
"""

from __future__ import annotations

import datetime as dt
import json
from dataclasses import dataclass
from pathlib import Path

from groundtruth_kb.bridge.detector import BridgeDocument

CHECKPOINT_FILENAME = "checkpoint.json"
CHECKPOINT_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class CheckpointEntry:
    document_name: str
    current_top_status: str
    current_top_file: str


@dataclass(frozen=True)
class Checkpoint:
    schema_version: int
    captured_at: str
    documents: tuple[CheckpointEntry, ...]


@dataclass(frozen=True)
class Transition:
    """A detected change between previous checkpoint and current parse."""

    document_name: str
    from_status: str | None  # None means "document did not exist in checkpoint"
    from_file: str | None
    to_status: str
    to_file: str


@dataclass(frozen=True)
class CheckpointLoadResult:
    """Outcome of attempting to load a checkpoint.

    Either returns the parsed checkpoint, signals bootstrap (no checkpoint),
    or signals corrupt-recovery (checkpoint existed but failed to parse, so
    bootstrap behavior should be applied with a warning).
    """

    checkpoint: Checkpoint | None
    is_bootstrap: bool
    corrupt_checkpoint_recovered: bool
    detail: str = ""


def _checkpoint_path(state_dir: Path) -> Path:
    return state_dir / CHECKPOINT_FILENAME


def _now_iso() -> str:
    return dt.datetime.now(dt.UTC).isoformat(timespec="seconds")


def load_checkpoint(state_dir: Path) -> CheckpointLoadResult:
    """Attempt to load the checkpoint at ``state_dir/checkpoint.json``.

    Returns a ``CheckpointLoadResult`` describing one of three cases:
    - No checkpoint file: ``is_bootstrap=True``, ``corrupt_checkpoint_recovered=False``.
    - Corrupt/malformed checkpoint: ``is_bootstrap=True``, ``corrupt_checkpoint_recovered=True``.
    - Valid checkpoint: ``checkpoint`` populated, both flags False.
    """
    path = _checkpoint_path(state_dir)
    if not path.is_file():
        return CheckpointLoadResult(
            checkpoint=None,
            is_bootstrap=True,
            corrupt_checkpoint_recovered=False,
            detail="No checkpoint file present; bootstrap mode.",
        )
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        documents = tuple(
            CheckpointEntry(
                document_name=str(d["document_name"]),
                current_top_status=str(d["current_top_status"]),
                current_top_file=str(d["current_top_file"]),
            )
            for d in raw["documents"]
        )
        cp = Checkpoint(
            schema_version=int(raw["schema_version"]),
            captured_at=str(raw["captured_at"]),
            documents=documents,
        )
        if cp.schema_version != CHECKPOINT_SCHEMA_VERSION:
            return CheckpointLoadResult(
                checkpoint=None,
                is_bootstrap=True,
                corrupt_checkpoint_recovered=True,
                detail=(
                    f"Checkpoint schema_version={cp.schema_version} != "
                    f"expected {CHECKPOINT_SCHEMA_VERSION}; treating as bootstrap."
                ),
            )
        return CheckpointLoadResult(
            checkpoint=cp,
            is_bootstrap=False,
            corrupt_checkpoint_recovered=False,
            detail="",
        )
    except (json.JSONDecodeError, KeyError, ValueError, TypeError) as exc:
        return CheckpointLoadResult(
            checkpoint=None,
            is_bootstrap=True,
            corrupt_checkpoint_recovered=True,
            detail=f"Checkpoint parse error: {type(exc).__name__}: {exc}",
        )


def write_checkpoint(state_dir: Path, current_documents: tuple[BridgeDocument, ...]) -> Checkpoint:
    """Write a fresh checkpoint capturing each document's current top status."""
    state_dir.mkdir(parents=True, exist_ok=True)
    entries = tuple(
        CheckpointEntry(
            document_name=doc.name,
            current_top_status=str(doc.versions[0].status),
            current_top_file=doc.versions[0].file_path,
        )
        for doc in current_documents
        if doc.versions
    )
    cp = Checkpoint(
        schema_version=CHECKPOINT_SCHEMA_VERSION,
        captured_at=_now_iso(),
        documents=entries,
    )
    path = _checkpoint_path(state_dir)
    path.write_text(
        json.dumps(
            {
                "schema_version": cp.schema_version,
                "captured_at": cp.captured_at,
                "documents": [
                    {
                        "document_name": e.document_name,
                        "current_top_status": e.current_top_status,
                        "current_top_file": e.current_top_file,
                    }
                    for e in entries
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return cp


def diff_against_checkpoint(
    current_documents: tuple[BridgeDocument, ...],
    checkpoint: Checkpoint | None,
    *,
    is_bootstrap: bool,
) -> tuple[Transition, ...]:
    """Compute transitions between the checkpoint and current parse state.

    When ``is_bootstrap`` is True, returns an empty tuple regardless of input
    (per design section 3.7: bootstrap emits zero routable transitions).

    When ``is_bootstrap`` is False, ``checkpoint`` MUST be non-None. Each
    document whose current top status or file differs from the checkpoint
    produces a Transition. Documents present in the current parse but absent
    from the checkpoint produce a Transition with ``from_status=None``.
    """
    if is_bootstrap:
        return ()
    if checkpoint is None:
        raise ValueError("diff_against_checkpoint called with is_bootstrap=False but checkpoint is None; caller bug.")
    prev = {e.document_name: (e.current_top_status, e.current_top_file) for e in checkpoint.documents}
    transitions: list[Transition] = []
    for doc in current_documents:
        if not doc.versions:
            continue
        top = doc.versions[0]
        top_status_str = str(top.status)
        if doc.name not in prev:
            transitions.append(
                Transition(
                    document_name=doc.name,
                    from_status=None,
                    from_file=None,
                    to_status=top_status_str,
                    to_file=top.file_path,
                )
            )
            continue
        prev_status, prev_file = prev[doc.name]
        if prev_status != top_status_str or prev_file != top.file_path:
            transitions.append(
                Transition(
                    document_name=doc.name,
                    from_status=prev_status,
                    from_file=prev_file,
                    to_status=top_status_str,
                    to_file=top.file_path,
                )
            )
    return tuple(transitions)
