"""Behavioral regression tests for DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001.

These tests exercise the runtime, not documentation. The constraint was recorded
2026-06-18 with five ``grep_absent`` assertions over documentation surfaces, which
pass whether or not the mandated behavior exists; the behavior was in fact absent
and a SessionStart-like boundary silently replaced an owner-declared interactive
role with the durable registry role. Every test below asserts a runtime outcome so
the constraint can no longer report green while unimplemented.

Clause coverage:

* ``CLAUSE-PERSISTENCE-ACROSS-BOUNDARIES`` -- a transcript-declared role survives a
  re-issue of the worker session document, including a re-issue that re-creates the
  document and a re-issue that follows an earlier fallback overwrite.
* ``CLAUSE-AGENT-HINT-NOT-LOCK`` -- the registry role is a fallback hint; it applies
  only when the session context carries no owner-declared role.
* ``CLAUSE-NO-DURABLE-REGISTRY-MUTATION`` -- resolution never writes the registry.
* ``CLAUSE-DISPATCHER-SOT-FOR-DISPATCH`` -- dispatcher composition is unaffected.

Owner authorization for the emergency repair: ``DELIB-202667742``.
"""

from __future__ import annotations

import json
from pathlib import Path

from groundtruth_kb.session.envelope import (
    ensure_worker_session,
    load_worker_session,
    resolve_worker_role_provenance,
    transcript_declared_role,
    worker_session_envelope_path,
)

REGISTRY_ROLE = "loyal-opposition"
TRANSCRIPT_ROLE = "prime-builder"
FALLBACK_SOURCE = "session_resolver_fallback"
TRANSCRIPT_SOURCE = "transcript_init_keyword"
SESSION_ID = "bba2e933-5d36-4c5b-ad04-08a653c8700f"


def _seed_harness(root: Path) -> Path:
    """Seed one harness whose durable registry role is the LOSING role.

    The registry role is deliberately the opposite of the transcript role so any
    reversion to the registry is unambiguous in an assertion failure.
    """
    state = root / "harness-state"
    state.mkdir(parents=True, exist_ok=True)
    (state / "harness-identities.json").write_text(
        json.dumps({"schema_version": 1, "harnesses": {"claude": {"id": "B"}}}),
        encoding="utf-8",
    )
    registry = state / "harness-registry.json"
    registry.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": [{"id": "B", "harness_name": "claude", "role": [REGISTRY_ROLE]}],
            }
        ),
        encoding="utf-8",
    )
    return registry


def _write_role_marker(
    root: Path,
    session_id: str,
    role: str,
    *,
    source: str = "init_keyword",
    body: dict[str, object] | None = None,
    raw: str | None = None,
) -> Path:
    """Write the per-session role marker the init-keyword surfaces produce."""
    marker_dir = root / ".claude" / "session"
    marker_dir.mkdir(parents=True, exist_ok=True)
    marker_path = marker_dir / f"role-{session_id}.json"
    if raw is not None:
        marker_path.write_text(raw, encoding="utf-8")
        return marker_path
    payload = (
        body
        if body is not None
        else {
            "role": role,
            "session_id": session_id,
            "session_id_source": "payload",
            "source": source,
            "written_at": "2026-07-31T06:21:41.857780Z",
        }
    )
    marker_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return marker_path


def _declare_transcript_role(root: Path, session_id: str = SESSION_ID, role: str = TRANSCRIPT_ROLE) -> dict:
    """Establish an owner-declared interactive role the way ``::init gtkb pb`` does."""
    _write_role_marker(root, session_id, role)
    return ensure_worker_session(
        root,
        harness_name="claude",
        session_id=session_id,
        role=role,
        role_source=TRANSCRIPT_SOURCE,
        init_keyword="::init gtkb pb",
    )


def _reissue_at_session_start(root: Path, session_id: str = SESSION_ID) -> dict:
    """Re-issue the worker document the way a SessionStart boundary does.

    The producer passes the durable registry role with a fallback source because no
    dispatch composition and no fresh init keyword are present on this boundary.
    """
    return ensure_worker_session(
        root,
        harness_name="claude",
        session_id=session_id,
        role=REGISTRY_ROLE,
        role_source=FALLBACK_SOURCE,
    )


# --- CLAUSE-PERSISTENCE-ACROSS-BOUNDARIES ---------------------------------------


def test_transcript_role_survives_session_start_reissue(tmp_path: Path) -> None:
    """The defect case: a fallback re-issue must not revert the declared role."""
    _seed_harness(tmp_path)
    _declare_transcript_role(tmp_path)

    reissued = _reissue_at_session_start(tmp_path)

    assert reissued["role"] == TRANSCRIPT_ROLE
    assert reissued["role_resolved"] == TRANSCRIPT_ROLE
    assert reissued["role_asserted"] == TRANSCRIPT_ROLE
    provenance = reissued["worker_role_provenance"]
    assert provenance["role"] == TRANSCRIPT_ROLE
    assert provenance["role_resolution_source"] != FALLBACK_SOURCE
    assert provenance["role_resolution_source"] in {TRANSCRIPT_SOURCE, "owner_init_keyword"}


def test_transcript_role_survives_document_recreation(tmp_path: Path) -> None:
    """A boundary that re-creates the document still resolves the declared role.

    Deleting the worker document models compaction/resume paths that rebuild it. The
    per-session role marker is the only surviving evidence, so a guard that inspects
    only the existing document cannot satisfy the clause here.
    """
    _seed_harness(tmp_path)
    _declare_transcript_role(tmp_path)
    worker_session_envelope_path(tmp_path, "claude", SESSION_ID).unlink()

    reissued = _reissue_at_session_start(tmp_path)

    assert reissued["role"] == TRANSCRIPT_ROLE
    assert reissued["worker_role_provenance"]["role"] == TRANSCRIPT_ROLE
    assert reissued["worker_role_provenance"]["role_resolution_source"] == TRANSCRIPT_SOURCE


def test_transcript_role_is_recovered_after_a_fallback_overwrite(tmp_path: Path) -> None:
    """Reproduces the live artifact state and asserts recovery.

    The worker document already carries the registry role from a prior fallback
    overwrite while the marker still records the owner-declared role; the next
    re-issue must restore the declared role rather than ratify the overwrite.
    """
    _seed_harness(tmp_path)
    _write_role_marker(tmp_path, SESSION_ID, TRANSCRIPT_ROLE)
    ensure_worker_session(
        tmp_path,
        harness_name="claude",
        session_id=SESSION_ID,
        role=REGISTRY_ROLE,
        role_source=FALLBACK_SOURCE,
    )
    overwritten = load_worker_session(tmp_path, "claude", SESSION_ID)
    assert overwritten is not None

    reissued = _reissue_at_session_start(tmp_path)

    assert reissued["role"] == TRANSCRIPT_ROLE
    resolved = resolve_worker_role_provenance(
        tmp_path,
        current_session_id=SESSION_ID,
        harness_name="claude",
    )
    assert resolved["role"] == TRANSCRIPT_ROLE
    assert resolved["role_resolution_source"] == TRANSCRIPT_SOURCE


def test_persistence_holds_across_repeated_boundaries(tmp_path: Path) -> None:
    """Persistence is not a one-shot: N consecutive boundaries keep the role."""
    _seed_harness(tmp_path)
    _declare_transcript_role(tmp_path)

    for _ in range(3):
        reissued = _reissue_at_session_start(tmp_path)
        assert reissued["role"] == TRANSCRIPT_ROLE


# --- CLAUSE-AGENT-HINT-NOT-LOCK (negative direction) ----------------------------


def test_registry_fallback_still_applies_without_a_transcript_role(tmp_path: Path) -> None:
    """The negative: no owner declaration means the registry role is still used."""
    _seed_harness(tmp_path)

    issued = ensure_worker_session(
        tmp_path,
        harness_name="claude",
        session_id="session-without-transcript-role",
        role=REGISTRY_ROLE,
        role_source=FALLBACK_SOURCE,
    )

    assert issued["role"] == REGISTRY_ROLE
    assert issued["worker_role_provenance"]["role"] == REGISTRY_ROLE
    assert issued["worker_role_provenance"]["role_resolution_source"] == FALLBACK_SOURCE


def test_owner_may_explicitly_change_the_persisted_role(tmp_path: Path) -> None:
    """The role "changes only when the owner explicitly changes it" -- so it must change."""
    _seed_harness(tmp_path)
    _declare_transcript_role(tmp_path)

    changed = ensure_worker_session(
        tmp_path,
        harness_name="claude",
        session_id=SESSION_ID,
        role="loyal-opposition",
        role_source=TRANSCRIPT_SOURCE,
        init_keyword="::init gtkb lo",
    )

    assert changed["role"] == "loyal-opposition"
    assert changed["worker_role_provenance"]["role"] == "loyal-opposition"


def test_a_marker_from_another_session_is_ignored(tmp_path: Path) -> None:
    """Persistence is per session context; a foreign marker grants nothing."""
    _seed_harness(tmp_path)
    _write_role_marker(
        tmp_path,
        "other-session",
        TRANSCRIPT_ROLE,
        body={
            "role": TRANSCRIPT_ROLE,
            "session_id": "a-different-session-id",
            "source": "init_keyword",
        },
    )

    assert transcript_declared_role(tmp_path, "other-session") is None


# --- CLAUSE-DISPATCHER-SOT-FOR-DISPATCH -----------------------------------------


def test_dispatcher_composition_is_not_deflected_by_a_marker(tmp_path: Path) -> None:
    """Headless dispatch keeps registry-composed authority regardless of markers."""
    _seed_harness(tmp_path)
    _write_role_marker(tmp_path, "dispatch-session", TRANSCRIPT_ROLE)

    dispatched = ensure_worker_session(
        tmp_path,
        harness_name="claude",
        session_id="dispatch-session",
        role=REGISTRY_ROLE,
        role_source="dispatcher_composition",
        dispatch_run_id="run-emergency-repair",
    )

    assert dispatched["role"] == REGISTRY_ROLE
    assert dispatched["worker_role_provenance"]["role_resolution_source"] == "dispatcher_composition"
    assert dispatched["worker_role_provenance"]["dispatch_run_id"] == "run-emergency-repair"


# --- CLAUSE-NO-DURABLE-REGISTRY-MUTATION ----------------------------------------


def test_persistence_never_mutates_the_durable_registry(tmp_path: Path) -> None:
    registry = _seed_harness(tmp_path)
    before = registry.read_bytes()
    _declare_transcript_role(tmp_path)

    _reissue_at_session_start(tmp_path)

    assert registry.read_bytes() == before
    assert json.loads(before)["harnesses"][0]["role"] == [REGISTRY_ROLE]


# --- fail-safe ------------------------------------------------------------------


def test_a_corrupt_marker_falls_back_instead_of_raising(tmp_path: Path) -> None:
    """A role-resolution repair must never make a session unstartable."""
    _seed_harness(tmp_path)
    _write_role_marker(tmp_path, SESSION_ID, TRANSCRIPT_ROLE, raw="{not json at all")

    issued = _reissue_at_session_start(tmp_path)

    assert issued["role"] == REGISTRY_ROLE
    assert transcript_declared_role(tmp_path, SESSION_ID) is None


def test_a_marker_with_an_unknown_role_is_ignored(tmp_path: Path) -> None:
    _seed_harness(tmp_path)
    _write_role_marker(
        tmp_path,
        SESSION_ID,
        "not-a-role",
        body={"role": "not-a-role", "session_id": SESSION_ID, "source": "init_keyword"},
    )

    assert transcript_declared_role(tmp_path, SESSION_ID) is None
    assert _reissue_at_session_start(tmp_path)["role"] == REGISTRY_ROLE


def test_a_marker_without_a_transcript_source_is_ignored(tmp_path: Path) -> None:
    """Only owner-declared marker sources carry role authority."""
    _seed_harness(tmp_path)
    _write_role_marker(
        tmp_path,
        SESSION_ID,
        TRANSCRIPT_ROLE,
        body={"role": TRANSCRIPT_ROLE, "session_id": SESSION_ID, "source": "sweeper_backfill"},
    )

    assert transcript_declared_role(tmp_path, SESSION_ID) is None
