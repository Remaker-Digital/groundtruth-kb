"""Planning amendments preserve evidence gaps without granting implementation."""

from __future__ import annotations

import json

import pytest

from platform_tests.groundtruth_kb.test_native_authority_service import history_count, put, seed, work_fields
from platform_tests.groundtruth_kb.test_native_authority_service import native as native
from platform_tests.groundtruth_kb.test_native_bridge import authored, claim
from platform_tests.groundtruth_kb.test_native_bridge import bridge as bridge
from platform_tests.groundtruth_kb.test_project_association_consistency import membership_cli as membership_cli

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]


def _fixture_work(service, client, **updates):
    """Model legacy imported state in the disposable database, never through intake."""
    current = client.get("/v1/work-items/WI-1").json()["work_item"]
    service.kernel.mutate_current(
        table="work_items",
        identity={"id": "WI-1"},
        expected_version=current["version"],
        new_state={**current, **updates},
        actor="qualification",
        reason="Imported-state fixture",
    )
    return client.get("/v1/work-items/WI-1").json()


@pytest.mark.parametrize("missing", ["links", "executable", "phase"])
def test_planning_amendments_preserve_existing_evidence_gaps_and_cas(native, missing):
    service, client, _, _ = native
    seed(client)
    for item in ("WI-1", "WI-2"):
        assert put(client, "work-items", item, work_fields(), project_id="PROJECT-1").status_code == 200
    if missing == "links":
        _fixture_work(service, client, source_spec_id=None, source_test_id=None)
    elif missing == "executable":
        assert put(client, "tests", "TEST-1", {"test_file": None}, expected_version=1).status_code == 200
    else:
        assert put(client, "test-plans", "PLAN-1", {"status": "retired"}, expected_version=1).status_code == 200
    before = client.get("/v1/work-items/WI-1").json()
    project = client.get("/v1/projects/PROJECT-1").content
    count = history_count(service)
    # Echoing an unchanged source link is not an evidence-link replacement.
    fields = {
        "status_detail": "Partial observation; qualification remains open",
        "priority": "P1",
        "depends_on_work_items": ["WI-2"],
        "source_test_id": before["work_item"]["source_test_id"],
    }
    version = before["work_item"]["version"]
    changed = put(client, "work-items", "WI-1", fields, expected_version=version)
    assert changed.status_code == 200, changed.text
    after = client.get("/v1/work-items/WI-1").json()
    assert after == changed.json()
    assert history_count(service) == count + 1
    assert after["membership"] == before["membership"]
    assert after["memberships"] == before["memberships"]
    assert client.get("/v1/projects/PROJECT-1").content == project
    for name in ("source_spec_id", "source_test_id", "resolution_status", "stage", "completion_evidence"):
        assert after["work_item"][name] == before["work_item"][name]
    assert after["work_item"]["depends_on_work_items"] == ["WI-2"]
    assert after["work_item"]["status_detail"] == fields["status_detail"]
    assert after["work_item"]["version"] == version + 1
    stale = put(client, "work-items", "WI-1", {"status_detail": "stale"}, expected_version=version)
    assert stale.json()["error"]["code"] == "cas_conflict"
    assert client.get("/v1/work-items/WI-1").json() == after
    assert history_count(service) == count + 1
    refused = put(client, "work-items", "WI-1", {"depends_on_work_items": ["MISSING"]}, expected_version=version + 1)
    assert refused.json()["error"]["code"] == "missing_work_item_dependency"
    assert client.get("/v1/work-items/WI-1").json() == after
    assert history_count(service) == count + 1


@pytest.mark.parametrize("creating", [False, True])
@pytest.mark.parametrize(
    "bad_fields,code",
    [
        ({"source_spec_id": None}, "work_evidence_required"),
        ({"source_test_id": None}, "work_evidence_required"),
        ({"source_test_id": "TEST-UNKNOWN"}, "not_found"),
        ({"source_spec_id": "SPEC-RETIRED"}, "inactive_evidence"),
        ({"source_test_id": "TEST-NO-EXEC"}, "executable_test_required"),
        ({"source_test_id": "TEST-NO-PHASE"}, "test_phase_required"),
    ],
)
def test_creation_and_actual_evidence_changes_still_require_complete_evidence(native, creating, bad_fields, code):
    service, client, _, _ = native
    seed(client)
    assert (
        put(client, "specifications", "SPEC-RETIRED", {"title": "Historical", "status": "retired"}).status_code == 200
    )
    for name, path in (("TEST-NO-EXEC", None), ("TEST-NO-PHASE", "tests/test_other.py")):
        fixture = put(
            client,
            "tests",
            name,
            {
                "title": name,
                "spec_id": "SPEC-1",
                "test_type": "integration",
                "test_file": path,
                "expected_outcome": "Evidence qualification",
            },
        )
        assert fixture.status_code == 200, fixture.text
    if not creating:
        assert put(client, "work-items", "WI-1", work_fields(), project_id="PROJECT-1").status_code == 200
    before = client.get("/v1/work-items/WI-1").content
    count = history_count(service)
    result = put(
        client,
        "work-items",
        "WI-1",
        work_fields(**bad_fields) if creating else bad_fields,
        expected_version=0 if creating else 1,
        project_id="PROJECT-1",
    )
    assert result.json()["error"]["code"] == code, result.text
    assert client.get("/v1/work-items/WI-1").content == before
    assert history_count(service) == count


def test_existing_evidence_links_can_be_repaired_with_a_complete_valid_pair(native):
    service, client, _, _ = native
    seed(client)
    assert put(client, "work-items", "WI-1", work_fields(), project_id="PROJECT-1").status_code == 200
    before = _fixture_work(service, client, source_spec_id=None, source_test_id=None)
    result = put(client, "work-items", "WI-1", work_fields(), expected_version=before["work_item"]["version"])
    assert result.status_code == 200, result.text
    assert result.json()["work_item"]["source_test_id"] == "TEST-1"
    assert result.json()["membership"] == before["membership"]


@pytest.mark.parametrize("resolution", ["resolved", "verified"])
def test_planning_amendment_cannot_reopen_frozen_work(native, resolution):
    service, client, _, _ = native
    seed(client)
    assert put(client, "work-items", "WI-1", work_fields(), project_id="PROJECT-1").status_code == 200
    before = _fixture_work(service, client, resolution_status=resolution, source_spec_id=None, source_test_id=None)
    count = history_count(service)
    result = put(
        client, "work-items", "WI-1", {"status_detail": "changed"}, expected_version=before["work_item"]["version"]
    )
    assert result.json()["error"]["code"] == "work_item_frozen"
    assert client.get("/v1/work-items/WI-1").json() == before
    assert history_count(service) == count


@pytest.mark.parametrize(
    "missing,code",
    [
        ("links", "work_evidence_required"),
        ("executable", "executable_test_required"),
        ("phase", "test_phase_required"),
    ],
)
def test_progress_amendment_does_not_make_a_proposal_executable(bridge, missing, code):
    service, client, contexts, _ = bridge
    if missing == "links":
        _fixture_work(service, client, source_spec_id=None, source_test_id=None)
    elif missing == "executable":
        assert put(client, "tests", "TEST-1", {"test_file": None}, expected_version=1).status_code == 200
    else:
        assert put(client, "test-plans", "PLAN-1", {"status": "retired"}, expected_version=1).status_code == 200
    version = client.get("/v1/work-items/WI-1").json()["work_item"]["version"]
    progress = put(
        client,
        "work-items",
        "WI-1",
        {"status_detail": "Planning updated; executable evidence still incomplete"},
        expected_version=version,
    )
    assert progress.status_code == 200, progress.text
    reservation = claim(client, "planning-only", "pb1", 0, "NEW").json()
    request = {
        "native_context_id": "pb1",
        "fence": reservation["fence"],
        "content": authored(contexts["pb1"], "planning-only", 1, "NEW", work_item_version=version + 1),
    }
    before = client.get("/v1/bridge/planning-only/show", params={"include_content": True}).json()
    count = history_count(service)
    refused = client.post("/v1/bridge/planning-only/deliver", json=request)
    assert refused.json()["error"]["code"] == code
    assert client.get("/v1/bridge/planning-only/show", params={"include_content": True}).json() == before
    assert history_count(service) == count
    assert (
        client.post(
            "/v1/bridge/planning-only/check", json={"native_context_id": "pb1", "fence": reservation["fence"]}
        ).status_code
        == 200
    )
    if missing == "links":
        fixed = put(client, "work-items", "WI-1", work_fields(), expected_version=version + 1)
        assert fixed.status_code == 200, fixed.text
        stale = client.post("/v1/bridge/planning-only/deliver", json=request)
        assert stale.json()["error"]["code"] == "scope_changed"
        request["content"] = authored(contexts["pb1"], "planning-only", 1, "NEW", work_item_version=version + 2)
    elif missing == "executable":
        assert (
            put(client, "tests", "TEST-1", {"test_file": "tests/test_effect.py"}, expected_version=2).status_code == 200
        )
    else:
        assert put(client, "test-plans", "PLAN-1", {"status": "active"}, expected_version=2).status_code == 200
    assert client.post("/v1/bridge/planning-only/deliver", json=request).status_code == 200


def test_ordinary_cli_can_amend_imported_planning_without_database_credentials(membership_cli, tmp_path):
    service, client, cli, _ = membership_cli
    assert put(client, "work-items", "WI-1", work_fields(), project_id="PROJECT-1").status_code == 200
    before = _fixture_work(service, client, source_spec_id=None, source_test_id=None)
    fields = tmp_path / "planning.json"
    fields.write_text(json.dumps({"status_detail": "Observed only: café", "priority": "P1"}), encoding="utf-8")
    count = history_count(service)
    result = cli(
        "backlog",
        "record",
        "--id",
        "WI-1",
        "--fields-file",
        str(fields),
        "--expected-version",
        str(before["work_item"]["version"]),
        "--actor",
        "qualification",
        "--change-reason",
        "Planning amendment",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    after = json.loads(result.stdout)
    readback = cli("backlog", "show", "WI-1", "--json")
    assert readback.returncode == 0 and json.loads(readback.stdout) == after
    assert after["work_item"]["status_detail"] == "Observed only: café"
    assert after["work_item"]["source_spec_id"] is None
    assert after["work_item"]["source_test_id"] is None
    assert after["work_item"]["resolution_status"] == "open"
    assert after["membership"] == before["membership"]
    assert history_count(service) == count + 1
