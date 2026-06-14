"""Tests for the WI-4495 (re-cast) TAFE live implementation-flow pilot.

Covers the module's pure logic and its service-driven runtime behavior:

* index-status parsing (``parse_index_thread_status``) including the post-impl
  ``NEW`` disambiguation signal (``has_prior_go``);
* canonical-status -> stage mapping (``expected_stage_for_thread``);
* legal-transition enforcement (``is_legal_transition``);
* full enforcement evaluation (``evaluate_enforcement``) — legal drive (parity
  MATCH), required-role violation, never-self-review violation (parity
  DIVERGENCE), and the unmappable-status path;
* the live driver (``run_live_pilot``) — flow/stage instantiation, the recorded
  ``flow_event`` parity verdict, the non-authoritative preview, parity MATCH and
  DIVERGENCE on real TAFE state, and the missing-thread error; and
* an AST structural guard that the pilot module never writes ``bridge/INDEX.md``
  and carries no file-write or canonical-path-literal surface.

Spec mapping:
- ``SPEC-TAFE-R1`` (Controlled Artifact Routing) -> transition + role +
  never-self-review enforcement tests.
- ``GOV-FILE-BRIDGE-AUTHORITY-001`` -> no-``INDEX.md``-write structural guard +
  divergence-favors-canonical (the verdict records the divergence and the
  module never mutates the canonical index).
- ``SPEC-TAFE-R7`` (Interface Principle) -> service-API-only mutation; injected
  read-only ``index_text``.
- ``DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`` -> each linked spec maps to
  executed evidence here.

NOTE (partial-delivery scope): the GO'd proposal (bridge/
gtkb-tafe-live-impl-flow-pilot-004.md) also adds a ``gt flow pilot`` CLI command
in ``cli.py`` plus its CLI tests + a CLI AST refusal-token guard. That edit is
deferred because ``cli.py`` is a contested ``target_path`` (also claimed by the
concurrent pending NEW thread ``gtkb-tafe-slice-c-ingestion-consolidated``), which
trips the bridge-compliance ask-checkpoint. The CLI tests are added here once the
``cli.py`` overlap is de-conflicted; this module-level suite verifies the
uncontested core.
"""

from __future__ import annotations

import ast
from datetime import UTC, datetime
from pathlib import Path

import pytest

import groundtruth_kb.tafe_live_pilot as pilot_module
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.tafe_index_preview import NON_AUTHORITATIVE_HEADER
from groundtruth_kb.tafe_live_pilot import (
    BRIDGE_STATUS_TO_STAGE,
    POST_IMPL_NEW,
    EnforcementResult,
    LivePilotResult,
    evaluate_enforcement,
    expected_stage_for_thread,
    is_legal_transition,
    parse_index_thread_status,
    run_live_pilot,
)
from groundtruth_kb.typed_artifact_flow import TypedArtifactFlowService

FIXED_NOW = datetime(2026, 6, 14, 1, 0, 0, tzinfo=UTC)

IMPLEMENTATION_SEQUENCE = ["propose", "review", "implement", "verify", "complete"]
IMPLEMENTATION_ROLES = {
    "propose": "prime-builder",
    "review": "loyal-opposition",
    "implement": "prime-builder",
    "verify": "loyal-opposition",
    "complete": "prime-builder",
}
NEVER_SELF_REVIEW = ["review", "verify"]


# --------------------------------------------------------------------------- #
# Index fixtures
# --------------------------------------------------------------------------- #


def _index(*lines: str) -> str:
    """Wrap a single Document block (latest-first) as a canonical INDEX text."""
    return "\n".join(["Document: gtkb-demo", *lines, ""])


INDEX_NEW = _index("NEW: bridge/gtkb-demo-001.md")
INDEX_NO_GO = _index(
    "NO-GO: bridge/gtkb-demo-002.md",
    "NEW: bridge/gtkb-demo-001.md",
)
INDEX_GO = _index(
    "GO: bridge/gtkb-demo-002.md",
    "NEW: bridge/gtkb-demo-001.md",
)
INDEX_POST_IMPL_NEW = _index(
    "NEW: bridge/gtkb-demo-005.md",
    "GO: bridge/gtkb-demo-004.md",
    "REVISED: bridge/gtkb-demo-003.md",
    "NO-GO: bridge/gtkb-demo-002.md",
    "NEW: bridge/gtkb-demo-001.md",
)
INDEX_VERIFIED = _index(
    "VERIFIED: bridge/gtkb-demo-006.md",
    "NEW: bridge/gtkb-demo-005.md",
    "GO: bridge/gtkb-demo-004.md",
    "NEW: bridge/gtkb-demo-001.md",
)
INDEX_WITHDRAWN = _index(
    "WITHDRAWN: bridge/gtkb-demo-003.md",
    "NO-GO: bridge/gtkb-demo-002.md",
    "NEW: bridge/gtkb-demo-001.md",
)


# --------------------------------------------------------------------------- #
# parse_index_thread_status
# --------------------------------------------------------------------------- #


def test_parse_index_thread_status_reads_latest_and_chain() -> None:
    status = parse_index_thread_status(INDEX_NO_GO, "gtkb-demo")
    assert status is not None
    assert status.latest_status == "NO-GO"
    assert status.latest_version == 2
    assert status.version_statuses == ("NO-GO", "NEW")
    assert status.has_prior_go is False


def test_parse_index_thread_status_detects_prior_go() -> None:
    status = parse_index_thread_status(INDEX_POST_IMPL_NEW, "gtkb-demo")
    assert status is not None
    assert status.latest_status == "NEW"
    assert status.has_prior_go is True


def test_parse_index_thread_status_missing_slug_returns_none() -> None:
    assert parse_index_thread_status(INDEX_NEW, "gtkb-absent") is None


# --------------------------------------------------------------------------- #
# expected_stage_for_thread
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    ("index_text", "expected_stage"),
    [
        (INDEX_NEW, "propose"),
        (INDEX_NO_GO, "review"),
        (INDEX_GO, "implement"),
        (INDEX_POST_IMPL_NEW, "verify"),
        (INDEX_VERIFIED, "complete"),
        (INDEX_WITHDRAWN, None),
    ],
)
def test_expected_stage_for_thread(index_text: str, expected_stage: str | None) -> None:
    status = parse_index_thread_status(index_text, "gtkb-demo")
    assert status is not None
    assert expected_stage_for_thread(status) == expected_stage


def test_initial_new_maps_to_propose_not_verify() -> None:
    status = parse_index_thread_status(INDEX_NEW, "gtkb-demo")
    assert status is not None
    assert status.has_prior_go is False
    assert expected_stage_for_thread(status) == "propose"


def test_bridge_status_to_stage_table_shape() -> None:
    # The table covers every logical implementation status and only those.
    assert BRIDGE_STATUS_TO_STAGE == {
        "NEW": "propose",
        "REVISED": "propose",
        "NO-GO": "review",
        "GO": "implement",
        POST_IMPL_NEW: "verify",
        "VERIFIED": "complete",
    }


# --------------------------------------------------------------------------- #
# is_legal_transition
# --------------------------------------------------------------------------- #


def test_legal_transition_start_and_adjacent() -> None:
    assert is_legal_transition(None, "propose", stage_sequence=IMPLEMENTATION_SEQUENCE)
    assert is_legal_transition("propose", "review", stage_sequence=IMPLEMENTATION_SEQUENCE)
    assert is_legal_transition("verify", "complete", stage_sequence=IMPLEMENTATION_SEQUENCE)


def test_illegal_transition_skip_backward_and_unknown() -> None:
    # Skip ahead.
    assert not is_legal_transition("propose", "implement", stage_sequence=IMPLEMENTATION_SEQUENCE)
    # Backward.
    assert not is_legal_transition("review", "propose", stage_sequence=IMPLEMENTATION_SEQUENCE)
    # Entering a non-first stage from the start.
    assert not is_legal_transition(None, "review", stage_sequence=IMPLEMENTATION_SEQUENCE)
    # Unknown target / source.
    assert not is_legal_transition("propose", "bogus", stage_sequence=IMPLEMENTATION_SEQUENCE)
    assert not is_legal_transition("bogus", "review", stage_sequence=IMPLEMENTATION_SEQUENCE)


# --------------------------------------------------------------------------- #
# evaluate_enforcement
# --------------------------------------------------------------------------- #


def _evaluate(expected_stage: str | None, actors: dict[str, str], actor_roles=None) -> EnforcementResult:
    return evaluate_enforcement(
        stage_sequence=IMPLEMENTATION_SEQUENCE,
        required_roles_by_stage=IMPLEMENTATION_ROLES,
        never_self_review_stages=NEVER_SELF_REVIEW,
        expected_stage=expected_stage,
        actors=actors,
        actor_roles=actor_roles,
    )


def test_enforcement_legal_drive_parity_match() -> None:
    result = _evaluate("review", {"propose": "alice", "review": "bob"})
    assert result.reachable_stage == "review"
    assert result.parity_ok is True
    assert result.divergences == ()
    assert result.never_self_review_violations == ()
    assert result.role_violations == ()


def test_enforcement_never_self_review_blocks_and_diverges() -> None:
    # Same actor proposed and reviewed -> review stage is blocked.
    result = _evaluate("review", {"propose": "alice", "review": "alice"})
    assert result.reachable_stage == "propose"
    assert result.parity_ok is False
    assert result.never_self_review_violations
    assert "never-self-review" in result.never_self_review_violations[0]
    assert result.divergences  # expected review, reached propose


def test_enforcement_role_violation_blocks() -> None:
    result = _evaluate(
        "review",
        {"propose": "alice", "review": "carol"},
        actor_roles={"alice": "prime-builder", "carol": "prime-builder"},
    )
    # carol holds prime-builder but review requires loyal-opposition.
    assert result.reachable_stage == "propose"
    assert result.parity_ok is False
    assert result.role_violations
    assert "requires role" in result.role_violations[0]


def test_enforcement_unmappable_status_is_divergence() -> None:
    result = _evaluate(None, {})
    assert result.reachable_stage is None
    assert result.parity_ok is False
    assert result.divergences == ("bridge status maps to no implementation-flow stage",)


def test_enforcement_full_sequence_to_complete() -> None:
    actors = {
        "propose": "alice",
        "review": "bob",
        "implement": "alice",
        "verify": "bob",
        "complete": "alice",
    }
    result = _evaluate("complete", actors)
    assert result.reachable_stage == "complete"
    assert result.parity_ok is True


# --------------------------------------------------------------------------- #
# run_live_pilot (service-driven)
# --------------------------------------------------------------------------- #


def _service(tmp_path: Path) -> tuple[KnowledgeDB, TypedArtifactFlowService]:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    return db, TypedArtifactFlowService(db)


def test_run_live_pilot_parity_match_records_verdict(tmp_path: Path) -> None:
    db, service = _service(tmp_path)
    try:
        result = run_live_pilot(
            "gtkb-demo",
            service=service,
            index_text=INDEX_NO_GO,
            now=FIXED_NOW,
            actors={"propose": "alice", "review": "bob"},
        )
        assert isinstance(result, LivePilotResult)
        assert result.latest_status == "NO-GO"
        assert result.expected_stage == "review"
        assert result.actual_stage == "review"
        assert result.parity_ok is True
        assert result.never_self_review_violations == ()

        # A flow instance + stage instances exist for the thread.
        flows = service.list_flow_instances()
        assert any(f["subject_id"] == "gtkb-demo" for f in flows)
        stages = service.list_stage_instances(flow_instance_id=result.flow_instance_id)
        assert {s["stage_id"] for s in stages} == {"propose", "review"}

        # The verdict was recorded as an append-only flow event.
        events = service.list_flow_events(flow_instance_id=result.flow_instance_id)
        assert len(events) == 1
        payload = events[0]["event_payload_parsed"]
        assert payload["parity_ok"] is True
        assert payload["canonical_wins"] is True
        assert payload["expected_stage"] == "review"

        # The preview is non-authoritative.
        assert result.preview_text.splitlines()[0] == NON_AUTHORITATIVE_HEADER
        assert "Document: gtkb-demo" in result.preview_text
    finally:
        db.close()


def test_run_live_pilot_self_review_divergence(tmp_path: Path) -> None:
    db, service = _service(tmp_path)
    try:
        result = run_live_pilot(
            "gtkb-demo",
            service=service,
            index_text=INDEX_NO_GO,
            now=FIXED_NOW,
            actors={"propose": "alice", "review": "alice"},
        )
        assert result.expected_stage == "review"
        assert result.actual_stage == "propose"
        assert result.parity_ok is False
        assert result.never_self_review_violations

        events = service.list_flow_events(flow_instance_id=result.flow_instance_id)
        payload = events[0]["event_payload_parsed"]
        assert payload["parity_ok"] is False
        assert payload["never_self_review_violations"]
        # Canonical still wins; the divergence is recorded, not overridden.
        assert payload["canonical_wins"] is True
    finally:
        db.close()


def test_run_live_pilot_is_idempotent_on_rerun(tmp_path: Path) -> None:
    db, service = _service(tmp_path)
    try:
        actors = {"propose": "alice", "review": "bob"}
        first = run_live_pilot("gtkb-demo", service=service, index_text=INDEX_NO_GO, now=FIXED_NOW, actors=actors)
        second = run_live_pilot("gtkb-demo", service=service, index_text=INDEX_NO_GO, now=FIXED_NOW, actors=actors)
        assert first.flow_instance_id == second.flow_instance_id
        # Stage instances are not duplicated on rerun (deterministic IDs).
        stages = service.list_stage_instances(flow_instance_id=second.flow_instance_id)
        assert len({s["id"] for s in stages}) == 2
    finally:
        db.close()


def test_run_live_pilot_missing_thread_raises(tmp_path: Path) -> None:
    db, service = _service(tmp_path)
    try:
        with pytest.raises(ValueError, match="not found"):
            run_live_pilot("gtkb-absent", service=service, index_text=INDEX_NO_GO, now=FIXED_NOW)
    finally:
        db.close()


# --------------------------------------------------------------------------- #
# Structural (AST) guard — module never writes bridge/INDEX.md
# --------------------------------------------------------------------------- #

_FILE_WRITE_ATTRS = {"write_text", "write_bytes", "writelines", "write"}
_MEMBASE_DIRECT_PATH = "bridge/INDEX.md"


def test_pilot_module_has_no_canonical_write_surface() -> None:
    """The pilot module performs no file I/O, no subprocess, and never carries
    the canonical bridge-index path literal (GOV-FILE-BRIDGE-AUTHORITY-001)."""
    source = Path(pilot_module.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name != "subprocess", "pilot must not import subprocess"
        if isinstance(node, ast.ImportFrom):
            assert node.module != "subprocess", "pilot must not import from subprocess"
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            assert node.value != _MEMBASE_DIRECT_PATH, "pilot must not carry the canonical bridge-index path literal"
        if isinstance(node, ast.Attribute):
            assert node.attr not in _FILE_WRITE_ATTRS, f"pilot must not call file-write attr {node.attr!r}"
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id != "open", "pilot must not call open()"
