"""WI-6069: session ids must name exactly one session.

``author_session_context_id`` is the review-independence boundary under
``GOV-FILE-BRIDGE-AUTHORITY-001``. Measured evidence (eight Goose LO transcripts,
2026-08-08) showed two distinct sessions sharing id ``20260808_2`` (697 vs 771
messages), so ``open_session`` must fail closed rather than silently overwrite
the prior session's envelope.
"""

from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest
from groundtruth_kb.session.envelope import (
    EnvelopeError,
    _guard_session_id_collision,
    open_session,
    worker_session_envelope_path,
)

HARNESS = "goose"
SESSION_ID = "20260808_2"
OPENED_A = "2026-08-08T01:00:00Z"
OPENED_B = "2026-08-08T05:30:00Z"


def _seed_worker_envelope(project_root: Path, session_id: str, opened_at: str) -> Path:
    """Write an authoritative worker-session envelope for one session id."""
    path = worker_session_envelope_path(project_root, HARNESS, session_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "session_id": session_id,
                "harness_name": HARNESS,
                "opened_at": opened_at,
                "status": "open",
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return path


def test_guard_rejects_id_reuse_by_a_distinct_session(tmp_path: Path) -> None:
    """A different session opening under a held id must fail closed."""
    _seed_worker_envelope(tmp_path, SESSION_ID, OPENED_A)
    incoming = {"session_id": SESSION_ID, "opened_at": OPENED_B}

    with pytest.raises(EnvelopeError) as excinfo:
        _guard_session_id_collision(tmp_path, HARNESS, incoming)

    message = str(excinfo.value)
    assert SESSION_ID in message
    # The diagnostic must name both timestamps so the operator can tell the
    # sessions apart without reading the envelope store by hand.
    assert OPENED_A in message
    assert OPENED_B in message


def test_guard_allows_idempotent_reopen_of_the_same_session(tmp_path: Path) -> None:
    """Resume of the same session is unchanged behaviour."""
    _seed_worker_envelope(tmp_path, SESSION_ID, OPENED_A)
    incoming = {"session_id": SESSION_ID, "opened_at": OPENED_A}

    _guard_session_id_collision(tmp_path, HARNESS, incoming)


def test_guard_noops_when_no_prior_envelope_exists(tmp_path: Path) -> None:
    """A first open for an unseen id is not a collision."""
    incoming = {"session_id": "20260808_9", "opened_at": OPENED_A}

    _guard_session_id_collision(tmp_path, HARNESS, incoming)


def test_guard_noops_on_blank_session_id(tmp_path: Path) -> None:
    """A missing session id is a separate defect class; the guard stays silent."""
    _guard_session_id_collision(tmp_path, HARNESS, {"session_id": "", "opened_at": OPENED_A})
    _guard_session_id_collision(tmp_path, HARNESS, {"opened_at": OPENED_A})


def test_distinct_session_ids_are_unaffected(tmp_path: Path) -> None:
    """Control: two different ids for one harness both pass."""
    _seed_worker_envelope(tmp_path, "20260808_2", OPENED_A)
    _seed_worker_envelope(tmp_path, "20260808_3", OPENED_A)

    _guard_session_id_collision(tmp_path, HARNESS, {"session_id": "20260808_2", "opened_at": OPENED_A})
    _guard_session_id_collision(tmp_path, HARNESS, {"session_id": "20260808_3", "opened_at": OPENED_A})


def test_open_session_invokes_the_guard_before_persisting() -> None:
    """Wiring: the guard must run before the envelope is written.

    Ordering matters -- guarding after ``write_current`` would already have
    overwritten the prior session's envelope.
    """
    source = inspect.getsource(open_session)
    assert "_guard_session_id_collision(" in source
    assert source.index("_guard_session_id_collision(") < source.index("write_current(")
