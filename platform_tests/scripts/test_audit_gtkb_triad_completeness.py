"""Current native triad facts, non-inference of owner origin, and read refusals."""

from __future__ import annotations

import copy
import json
import socket

import pytest
from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError

from platform_tests.groundtruth_kb.native_fixtures import (
    _serve_authority,
    history_count,
    put,
)
from platform_tests.groundtruth_kb.native_fixtures import native as native
from scripts import audit_gtkb_triad_completeness as audit


def spec(record_id="SPEC-1", **fields):
    return {
        "id": record_id,
        "version": 1,
        "status": "active",
        "title": "Current requirement",
        "type": "requirement",
        "implementation_verified_at": "2026-09-01T12:00:00+00:00",
        "description": "Current normative content",
        **fields,
    }


def binding(**fields):
    return {
        "id": "TEST-1",
        "version": 1,
        "spec_id": "SPEC-1",
        "test_file": "platform_tests/test_native.py",
        "last_result": "pass",
        "last_executed_at": "2026-09-01T12:00:00+00:00",
        "last_executed_on": None,
        **fields,
    }


def records(*, specs=None, tests=None, active_plan=True):
    return {
        "specifications": specs if specs is not None else [spec(source_paths=["scripts/native.py"])],
        "tests": tests if tests is not None else [binding()],
        "test-plans": [
            {
                "id": "PLAN-1",
                "version": 1,
                "status": "active" if active_plan else "retired",
            }
        ],
        "test-phases": [{"id": "PHASE-1", "version": 1, "plan_id": "PLAN-1", "test_ids": ["TEST-1"]}],
    }


def client_for(monkeypatch, state, *, page_size=1000):
    calls = []

    def request(self, method, path, *, query=None, **kwargs):
        assert method == "GET" and not kwargs
        assert path.startswith("/v1/") and path.removeprefix("/v1/") in audit.DOMAINS
        calls.append((method, path, copy.deepcopy(query)))
        rows = sorted(state[path.removeprefix("/v1/")], key=lambda row: row["id"])
        after = (query or {}).get("after")
        rows = [row for row in rows if after is None or row["id"] > after]
        page = rows[:page_size]
        return {
            "records": copy.deepcopy(page),
            "next_after": page[-1]["id"] if len(rows) > page_size else None,
        }

    monkeypatch.setattr(AuthorityClient, "request", request)
    return AuthorityClient("http://127.0.0.1:12345"), calls


def inspect(monkeypatch, tmp_path, state):
    client, calls = client_for(monkeypatch, state)
    return audit.run_audit(tmp_path, client=client), calls


def test_audit_flags_verified_implementation_without_test_or_implementation(monkeypatch, tmp_path):
    report, _ = inspect(monkeypatch, tmp_path, records(specs=[spec()], tests=[]))
    assert set(report["by_kind"]) == {
        "verified_implementation_without_implementation_evidence",
        "verified_implementation_without_active_test_binding",
    }
    assert report["implementation_claims"] == 1
    assert report["assessment_complete"] is False


def test_audit_records_complete_triad_without_claiming_owner_origin(monkeypatch, tmp_path):
    report, calls = inspect(monkeypatch, tmp_path, records())
    assert report["gap_count"] == 0 and report["implementation_claims"] == 1
    assert "owner_origin_reviews" not in report and report["assessment_complete"] is True
    assert {path for _, path, _ in calls} == {"/v1/" + domain for domain in audit.DOMAINS}
    assert len(calls) == 8


@pytest.mark.parametrize("fields", [{"test_file": None}, {"spec_id": "SPEC-OTHER"}])
def test_audit_requires_current_executable_spec_binding(monkeypatch, tmp_path, fields):
    report, _ = inspect(monkeypatch, tmp_path, records(tests=[binding(**fields)]))
    assert report["by_kind"] == {"verified_implementation_without_active_test_binding": 1}


def test_audit_requires_membership_in_an_active_test_plan(monkeypatch, tmp_path):
    report, _ = inspect(monkeypatch, tmp_path, records(active_plan=False))
    assert report["by_kind"] == {"verified_implementation_without_active_test_binding": 1}


@pytest.mark.parametrize(
    "fields",
    [
        {"last_result": None},
        {"last_result": "historical_agent_red"},
        {"last_result": "fail"},
        {"last_executed_at": None},
        {"last_executed_at": "not-a-time"},
        {"last_executed_at": "2026-09-01T12:00:00"},
        {"last_executed_on": "2026-09-01"},
    ],
)
def test_audit_does_not_credit_undated_historical_or_invalid_execution(monkeypatch, tmp_path, fields):
    report, _ = inspect(monkeypatch, tmp_path, records(tests=[binding(**fields)]))
    assert report["by_kind"] == {"verified_implementation_without_passing_test_execution": 1}


def test_audit_accepts_recorded_date_precision_without_creating_execution(monkeypatch, tmp_path):
    state = records(tests=[binding(last_executed_at=None, last_executed_on="2026-09-01")])
    before = copy.deepcopy(state)
    report, _ = inspect(monkeypatch, tmp_path, state)
    assert report["gap_count"] == 0 and state == before
    assert "not a new execution" in report["limitations"][1]


def test_audit_uses_native_verification_marker_not_active_status_as_completion(monkeypatch, tmp_path):
    report, _ = inspect(
        monkeypatch,
        tmp_path,
        records(specs=[spec(implementation_verified_at=None)], tests=[]),
    )
    assert report["implementation_claims"] == report["gap_count"] == 0
    assert "owner_origin_reviews" not in report


@pytest.mark.parametrize("status", ["implemented", "verified", "specified"])
def test_audit_flags_noncanonical_status_without_treating_it_as_verification(monkeypatch, tmp_path, status):
    report, _ = inspect(monkeypatch, tmp_path, records(specs=[spec(status=status)], tests=[]))
    assert report["by_kind"] == {"noncanonical_spec_status": 1}
    assert report["implementation_claims"] == 0


def test_audit_ignores_retired_and_superseded_authority(monkeypatch, tmp_path):
    report, _ = inspect(
        monkeypatch,
        tmp_path,
        records(
            specs=[
                spec("SPEC-OLD", status="retired"),
                spec("SPEC-REPLACED", status="superseded"),
            ],
            tests=[],
        ),
    )
    assert report["gap_count"] == 0 and report["assessment_complete"] is True


def test_audit_flags_agent_red_specs_for_reclassification_review(monkeypatch, tmp_path):
    report, _ = inspect(
        monkeypatch,
        tmp_path,
        records(
            specs=[
                spec(
                    application_scope="application:Agent_Red",
                    source_paths=["native.py"],
                )
            ]
        ),
    )
    assert report["by_kind"] == {"agent_red_scoped_spec_candidate_for_gtkb_reclassification": 1}
    assert report["gaps"][0]["artifact_id"] == "SPEC-1"


def test_audit_respects_current_platform_scope_despite_adopter_example(monkeypatch, tmp_path):
    report, _ = inspect(
        monkeypatch,
        tmp_path,
        records(
            specs=[
                spec(
                    application_scope="gtkb_platform",
                    title="Platform behavior with Agent Red example",
                    source_paths=["native.py"],
                )
            ]
        ),
    )
    assert report["gap_count"] == 0


def test_audit_refers_unclassified_adopter_text_without_reclassifying(monkeypatch, tmp_path):
    row = spec(application_scope=None, title="Agent Red origin", source_paths=["native.py"])
    state = records(specs=[row])
    before = copy.deepcopy(state)
    report, _ = inspect(monkeypatch, tmp_path, state)
    assert report["by_kind"] == {"agent_red_scoped_spec_candidate_for_gtkb_reclassification": 1}
    assert state == before


def test_audit_leaves_owner_origin_to_canonical_specification_review(monkeypatch, tmp_path):
    report, calls = inspect(monkeypatch, tmp_path, records(specs=[spec(implementation_verified_at=None)]))
    assert report["gap_count"] == 0 and report["assessment_complete"] is True
    assert "owner_origin_reviews" not in report
    assert "current canonical specification" in report["limitations"][2]
    assert "unclear cases go to the owner" in report["limitations"][2]
    assert "neither approves nor rejects owner origin" in report["limitations"][2]
    assert all("deliberation" not in path and "bridge" not in path for _, path, _ in calls)


def test_audit_does_not_infer_owner_origin_from_authority_provenance_or_prose(monkeypatch, tmp_path):
    row = spec(
        authority="stated",
        changed_by="owner",
        change_reason="Owner approved",
        description="Owner conversation: approved requirement",
        constraints={"owner_origin": "claimed"},
    )
    report, calls = inspect(monkeypatch, tmp_path, records(specs=[row]))
    assert "owner_origin_reviews" not in report
    assert "owner_origin_review_count" not in report
    assert report["assessment_complete"] is False
    assert all("deliberation" not in path and "bridge" not in path for _, path, _ in calls)


def test_audit_reads_all_pages_without_local_store_or_bridge_payload(monkeypatch, tmp_path):
    sentinel = tmp_path / "groundtruth.db"
    sentinel.write_bytes(b"inert, never opened")
    bridge = tmp_path / "bridge"
    bridge.mkdir()
    message = bridge / "historical-001.md"
    message.write_text("Not an audit input", encoding="utf-8")

    def refuse(*args, **kwargs):
        pytest.fail("Native triad inspection cannot open a local authority store")

    monkeypatch.setattr("sqlite3.connect", refuse)
    state = records(
        specs=[
            spec("SPEC-1", implementation_verified_at=None),
            spec("SPEC-2", implementation_verified_at=None),
        ]
    )
    client, calls = client_for(monkeypatch, state, page_size=1)
    report = audit.run_audit(tmp_path, client=client)
    assert report["records_read"]["specifications"] == 2
    assert [query["after"] for _, path, query in calls if path == "/v1/specifications"] == [
        None,
        "SPEC-1",
        None,
        "SPEC-1",
    ]
    assert (
        sentinel.read_bytes() == b"inert, never opened" and message.read_text(encoding="utf-8") == "Not an audit input"
    )


def test_audit_refuses_observed_canonical_drift(monkeypatch, tmp_path):
    client, _ = client_for(monkeypatch, records())
    original = AuthorityClient.request
    seen = 0

    def changed(self, method, path, **kwargs):
        nonlocal seen
        value = original(self, method, path, **kwargs)
        if path == "/v1/specifications":
            seen += 1
            if seen == 2:
                value["records"][0]["version"] = 2
        return value

    monkeypatch.setattr(AuthorityClient, "request", changed)
    with pytest.raises(AuthorityClientError) as error:
        audit.run_audit(tmp_path, client=client)
    assert error.value.code == "source_changed"


def test_audit_refuses_duplicate_current_rows(monkeypatch, tmp_path):
    with pytest.raises(AuthorityClientError) as error:
        inspect(monkeypatch, tmp_path, records(specs=[spec(), spec()]))
    assert error.value.code == "invalid_response"


def test_cli_separates_unavailable_authority_from_complete_inspection(monkeypatch, tmp_path, capsys):
    def unavailable(_root):
        raise AuthorityClientError("authority_unavailable", "Restore the configured authority")

    monkeypatch.setattr(audit, "configured_authority_client", unavailable)
    assert audit.main(["--project-root", str(tmp_path), "--json"]) == 2
    output = capsys.readouterr()
    assert output.out == "" and json.loads(output.err)["error"]["code"] == "authority_unavailable"


def test_cli_accepts_complete_triad_without_an_origin_archive(monkeypatch, tmp_path, capsys):
    client, _ = client_for(monkeypatch, records())
    monkeypatch.setattr(audit, "configured_authority_client", lambda _root: client)
    assert audit.main(["--project-root", str(tmp_path), "--json", "--fail-on-gaps"]) == 0
    output = capsys.readouterr()
    report = json.loads(output.out)
    assert output.err == "" and report["gap_count"] == 0 and report["assessment_complete"] is True
    assert "owner_origin_reviews" not in report
    assert "neither approves nor rejects owner origin" in report["limitations"][2]


@pytest.mark.parametrize("obsolete", ["--db", "--bridge-dir"])
def test_cli_rejects_retired_local_authority_inputs(obsolete, tmp_path):
    with pytest.raises(SystemExit) as error:
        audit.main([obsolete, str(tmp_path)])
    assert error.value.code == 2


@pytest.mark.integration
@pytest.mark.timeout(120)
def test_audit_reads_real_native_binding_and_plan_without_canonical_effects(native, tmp_path, monkeypatch):
    service, client, *_ = native
    assert (
        put(
            client,
            "specifications",
            "SPEC-TRIAD",
            {
                "title": "Native triad",
                "source_paths": ["scripts/audit_gtkb_triad_completeness.py"],
            },
        ).status_code
        == 200
    )
    assert (
        put(
            client,
            "tests",
            "TEST-TRIAD",
            {
                "title": "Native binding",
                "spec_id": "SPEC-TRIAD",
                "test_type": "integration",
                "test_file": "platform_tests/scripts/test_audit_gtkb_triad_completeness.py",
                "expected_outcome": "Native inspection",
            },
        ).status_code
        == 200
    )
    assert (
        put(
            client,
            "test-plans",
            "PLAN-TRIAD",
            {"title": "Triad plan", "status": "active"},
        ).status_code
        == 200
    )
    assert (
        put(
            client,
            "test-phases",
            "PHASE-TRIAD",
            {
                "plan_id": "PLAN-TRIAD",
                "phase_order": 1,
                "title": "Native phase",
                "gate_criteria": "Inspect current native associations without canonical mutation",
                "test_ids": ["TEST-TRIAD"],
            },
        ).status_code
        == 200
    )
    assert (
        put(
            client,
            "specifications",
            "SPEC-TRIAD",
            {"implementation_verified_at": True},
            expected_version=1,
        ).status_code
        == 200
    )
    before = history_count(service)
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    process, _ = _serve_authority(tmp_path, port)
    try:
        monkeypatch.setenv("GT_AUTHORITY_URL", f"http://127.0.0.1:{port}")
        calls = []
        original = AuthorityClient.request

        def observed(self, method, path, **kwargs):
            calls.append((method, path))
            return original(self, method, path, **kwargs)

        monkeypatch.setattr(AuthorityClient, "request", observed)
        report = audit.run_audit(tmp_path)
        assert report["implementation_claims"] == 1
        assert report["by_kind"] == {"verified_implementation_without_passing_test_execution": 1}
        assert "owner_origin_reviews" not in report and report["assessment_complete"] is False
        assert len(calls) == 8 and all(method == "GET" for method, _ in calls)
        assert history_count(service) == before
        assert not (tmp_path / "groundtruth.db").exists() and not (tmp_path / "bridge").exists()
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=15)
