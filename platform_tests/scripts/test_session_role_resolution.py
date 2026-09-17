"""Native role resolution without file, registry or inherited-context fallbacks.

Current formal fitness and disposable native behavior replace the retired marker
resolver tests. Contexts on one harness remain independent; no test qualifies a
real host or assigns a production agent role.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from groundtruth_kb.assertion_schema import validate_assertion_list
from groundtruth_kb.assertions import run_spec_assertions

from platform_tests.groundtruth_kb.specs.conftest import formal_record as formal_record
from platform_tests.groundtruth_kb.test_native_authority_service import history_count, put
from platform_tests.groundtruth_kb.test_native_authority_service import native as native
from platform_tests.groundtruth_kb.test_native_bridge import bridge as bridge
from platform_tests.groundtruth_kb.test_native_bridge import claim, deliver

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]


def test_current_role_contract_requires_one_immutable_native_binding(formal_record):
    role = formal_record("DCL-SESSION-ROLE-RESOLUTION-001")
    constraints = role["constraints"]
    for key in (
        "role_immutable",
        "role_in_binding",
        "interactive_override_forbidden",
        "registry_fallback_forbidden",
        "role_attestation_forbidden",
        "same_context_terminal_review_forbidden",
    ):
        assert constraints[key] is True
    assert "groundtruth-kb/src/groundtruth_kb/bridge/native.py" in role["source_paths"]
    identity = formal_record("DCL-INIT-BOUND-SESSION-IDENTITY-001")
    assert identity["constraints"]["fallback_resolution_forbidden"] is True
    assert identity["constraints"]["persistent_activity_record_forbidden"] is True
    assert identity["constraints"]["single_binding"] is True


def test_superseded_role_policies_never_supply_current_authority(formal_record):
    for identifier, status in (
        ("GOV-SESSION-ROLE-AUTHORITY-001", "retired"),
        ("ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001", "retired"),
        ("DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001", "superseded"),
        ("ADR-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-001", "superseded"),
    ):
        assert formal_record(identifier, expected_status=status)["status"] == status


def test_ending_a_context_never_retires_or_rebinds_its_identity(formal_record):
    adr = formal_record("ADR-SESSION-MARKER-AND-ACTIVITY-RECORD-MODEL-001")
    body = " ".join(adr["description"].split()).lower()
    assert "ending a process or context does not retire or delete its binding" in body
    assert "retiring a binding ends that context" not in body
    gov = formal_record("GOV-SESSION-SELF-INITIALIZATION-001")
    assert "retired binding" not in gov["description"].lower()
    assert gov["constraints"]["conflicting_marker_zero_effect"] is True


@pytest.mark.parametrize(
    "identifier",
    [
        "DCL-SESSION-ROLE-RESOLUTION-001",
        "GOV-SESSION-SELF-INITIALIZATION-001",
        "ADR-SESSION-MARKER-AND-ACTIVITY-RECORD-MODEL-001",
        "SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001",
    ],
)
def test_current_assertions_resolve_without_claiming_behavioral_completion(formal_record, identifier):
    record = formal_record(identifier)
    assert record["assertions"] and not validate_assertion_list(record["assertions"])
    # The read-only evaluator needs no database handle. Structural discovery
    # must resolve current tests while leaving behavioral qualification open.
    result = run_spec_assertions(None, record, "session-role-test", Path(__file__).resolve().parents[2])
    assert result["evaluation_result"] == "PARTIAL" and result["overall_passed"] is False
    structural = [item for item in result["results"] if item["type"] != "behavioral_validation"]
    assert structural and all(item["status"] == "PASS" for item in structural)
    assert any(item["type"] == "behavioral_validation" for item in result["results"])


@pytest.mark.parametrize("token,role", [("pb", "prime-builder"), ("lo", "loyal-opposition")])
@pytest.mark.parametrize("subject", ["gtkb", "application"])
@pytest.mark.parametrize("form", ["standalone", "multiline", "repeated"])
def test_exact_prompt_binding_returns_only_the_selected_immutable_role(native, token, role, subject, form):
    service, client, *_ = native
    marker = f"::init {subject} {token}"
    prompt = {
        "standalone": marker,
        "multiline": "Owner-selected work\n" + marker + "\n::open build\nContinue.",
        "repeated": marker + "\n" + marker,
    }[form]
    native_id = f"opaque-context:{subject}:{token}:{form}"
    request = {"native_context_id": native_id, "init_command": prompt}
    first = client.post("/v1/sessions/bind", json=request)
    assert first.status_code == 200, first.text
    assert first.json()["status"] == "init_requested"
    binding = first.json()["binding"]
    assert set(binding) == {
        "native_context_id",
        "session_context_id",
        "subject",
        "role",
        "created_at",
        "minimum_idempotency_identity",
    }
    assert binding["role"] == role and binding["subject"] == subject
    assert binding["native_context_id"] == native_id
    assert client.get("/v1/sessions/binding", params={"native_context_id": native_id}).json() == binding
    before = history_count(service)
    assert client.post("/v1/sessions/bind", json={**request, "init_command": marker}).json() == {
        "status": "already_initialized_idempotent",
        "binding": binding,
    }
    conflict = client.post(
        "/v1/sessions/bind",
        json={**request, "init_command": f"::init {subject} " + ("lo" if token == "pb" else "pb")},
    )
    assert conflict.status_code == 422 and conflict.json()["error"]["code"] == "session_init_conflict"
    assert client.get("/v1/sessions/binding", params={"native_context_id": native_id}).json() == binding
    assert history_count(service) == before


@pytest.mark.parametrize(
    "identifier",
    [
        "DCL-SESSION-STARTUP-TOKEN-BUDGET-001",
        "DCL-SESSION-WRAP-UP-AUTOMATION-SAFETY-001",
        "PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001",
        "PB-SESSION-WRAP-UP-PROACTIVE-001",
    ],
)
def test_current_startup_guidance_preserves_input_without_claiming_runtime_qualification(formal_record, identifier):
    record = formal_record(identifier)
    constraints = record["constraints"]
    assert constraints["owner_input_discard_forbidden"] is True
    assert constraints["mutable_session_state_forbidden"] is True
    assert constraints["behavioral_validation_required"] is True
    assert ".harness-baseline-configuration/rules/session-bootstrap.md" in record["source_paths"]
    assert "scripts/session_self_initialization.py" not in record["source_paths"]
    result = run_spec_assertions(None, record, "startup-contract-test", Path(__file__).resolve().parents[2])
    assert result["overall_passed"] is False
    assert result["evaluation_result"] in {"UNASSESSED", "PARTIAL"}


def test_first_prompt_discard_contract_is_retired_without_reviving_predecessors(formal_record):
    assert formal_record("SPEC-CODEX-STARTUP-INPUT-GATE-TRIGGER-001", expected_status="retired")["retired_at"]
    for identifier in (
        "DCL-STARTUP-GATE-FRESH-START-ONLY-001",
        "DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001",
        "DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001",
    ):
        assert formal_record(identifier, expected_status="superseded")["status"] == "superseded"


def test_files_and_inherited_identifiers_cannot_resolve_a_missing_context(bridge, monkeypatch):
    service, client, contexts, root = bridge
    candidates = [
        root / ".claude/session/active-session-role.json",
        root / ".claude/session/role-unbound.json",
        root / "harness-state/claude/session-envelopes/current.json",
        root / "harness-state/harness-registry.json",
    ]
    payload = json.dumps(
        {
            "session_id": "unbound",
            "role": "loyal-opposition",
            "status": "open",
            "harnesses": [{"id": "HARNESS-1", "role": ["loyal-opposition"]}],
        }
    ).encode()
    for path in candidates:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    for variable in ("GTKB_SESSION_ID", "GTKB_INHERITED_SESSION_ID", "CODEX_THREAD_ID", "CLAUDE_CODE_SESSION_ID"):
        monkeypatch.setenv(variable, "lo1")
    before = history_count(service)
    absent = client.get("/v1/sessions/binding", params={"native_context_id": "unbound"})
    assert absent.status_code == 422 and absent.json()["error"]["code"] == "no_session_binding"
    assert client.get("/v1/sessions/binding").status_code == 422
    selected = client.get("/v1/sessions/binding", params={"native_context_id": "pb1"})
    assert selected.json() == contexts["pb1"] and selected.json()["role"] == "prime-builder"
    assert all(path.read_bytes() == payload for path in candidates)
    assert history_count(service) == before


def test_harness_lifecycle_does_not_change_context_roles_or_cancel_an_initiated_chain(bridge):
    _, client, contexts, _ = bridge
    deliver(client, contexts, "role-lifecycle", "pb1", 1, "NEW")
    assert put(client, "harnesses", "HARNESS-2", {"harness_name": "other", "harness_type": "test"}).status_code == 200
    assert put(client, "harnesses", "HARNESS-2", {"status": "active"}, expected_version=1).status_code == 200
    assert put(client, "harnesses", "HARNESS-1", {"status": "active"}, expected_version=1).status_code == 200
    assert put(client, "harnesses", "HARNESS-1", {"status": "suspended"}, expected_version=2).status_code == 200
    for name in ("pb1", "lo1", "pb2"):
        assert client.get("/v1/sessions/binding", params={"native_context_id": name}).json() == contexts[name]
    deliver(client, contexts, "role-lifecycle", "lo1", 2, "GO")
    deliver(client, contexts, "role-lifecycle", "pb2", 3, "READY")
    assert client.get("/v1/bridge/role-lifecycle/show").json()["attempt"]["head_version"] == 3


def test_role_remains_a_real_gate_even_when_harness_metadata_cannot_assign_it(bridge):
    _, client, contexts, _ = bridge
    deliver(client, contexts, "independence", "pb1", 1, "NEW")
    rejected = claim(client, "independence", "pb1", 1, "GO")
    assert rejected.status_code == 422
    assert client.get("/v1/bridge/independence/show").json()["attempt"]["head_version"] == 1
    assert (
        client.post(
            "/v1/sessions/bind", json={"native_context_id": "pb1", "init_command": "::init gtkb lo"}
        ).status_code
        == 422
    )
    deliver(client, contexts, "independence", "lo1", 2, "GO")
    assert client.get("/v1/bridge/independence/show").json()["attempt"]["head_version"] == 2
