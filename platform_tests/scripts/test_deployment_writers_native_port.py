"""The deployment automation writers record through the native authority (WI-7860, owner ruling D17).

Until this increment `scripts/_defect_reporter.py::create_defect` and `scripts/test_pipeline.py::_record_phase_result`
took the warn-and-continue path accepted by owner ruling D3 (the retired `tools/knowledge-db` shim; TEST-12701 v1
proved that state). The port replaces that evidence: `create_defect` builds an `AuthorityClient` from the configured
`authority_url`, chooses `WI-NNNN` from a paged listing, creates with CAS under PROJECT-GTKB-NATIVE-APPLICATION-LIFECYCLE
with an explicit actor and reason and the pipeline's own evidence pair, reads the record back exactly, and raises
`DefectReportError` on every failure; `_record_phase_result` is retired (no native execution-result route). The cases
run over the disposable native authority (the `native` fixture of native_fixtures.py served over HTTP).
"""

from __future__ import annotations

import argparse
import ast
import importlib
import socket
import subprocess
import time
from contextlib import contextmanager
from pathlib import Path
from threading import Thread
from unittest.mock import patch

import pytest
import uvicorn
from groundtruth_kb.authority_api import create_authority_app
from groundtruth_kb.authority_client import AuthorityClient

from platform_tests.groundtruth_kb.native_fixtures import history_count, put
from platform_tests.groundtruth_kb.native_fixtures import native as native
from scripts import _defect_reporter as reporter

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]

ROOT = Path(__file__).resolve().parents[2]
PROJECT_ID = "PROJECT-GTKB-NATIVE-APPLICATION-LIFECYCLE"
# Each pipeline's governing specification and its own executable test (the constants the scripts carry).
PIPELINES = {
    "scripts/test_pipeline.py": ("SPEC-1616", "TEST-8253", "test-pipeline"),
    "scripts/deploy_pipeline.py": ("SPEC-1615", "TEST-2941", "deploy-pipeline"),
    "applications/Agent_Red/scripts/deploy_pipeline.py": ("SPEC-1615", "TEST-2941", "deploy-pipeline"),
    "scripts/deploy_orchestrator.py": ("SPEC-1825", "TEST-DEPLOY-ORCHESTRATOR-001", "deploy-orchestrator"),
}
RETIRED_CALL_SITE = "scripts/pre_flight_checklist.py"  # cited the retired SPEC-1617; retired with it (D17)
SHIM_LINE = 'sys.path.insert(0, str(PROJECT_ROOT / "tools" / "knowledge-db"))'
HELPER_TEST = {"test_type": "unit", "expected_outcome": "Refusal evidence"}


@contextmanager
def _serve(service):
    """The disposable authority over a loopback HTTP listener, as the ported writer reaches it."""
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen()
    url = f"http://127.0.0.1:{listener.getsockname()[1]}"
    server = uvicorn.Server(uvicorn.Config(create_authority_app(service), log_level="error", lifespan="off"))
    thread = Thread(target=lambda: server.run(sockets=[listener]), daemon=True)
    thread.start()
    try:
        deadline = time.monotonic() + 10
        while not server.started:
            assert thread.is_alive() and time.monotonic() < deadline, "Disposable HTTP service did not start"
            time.sleep(0.02)
        yield url
    finally:
        server.should_exit = True
        thread.join(timeout=10)
        listener.close()
        assert not thread.is_alive(), "Disposable HTTP service did not stop"


def _seed_pipeline_evidence(client) -> None:
    """The ruled project and every pipeline's evidence pair, all in one active test-plan phase."""
    rows = [
        ("projects", PROJECT_ID, {"name": "Native application lifecycle"}, {}),
        ("specifications", "SPEC-1615", {"title": "Automated build/deploy pipeline"}, {}),
        ("specifications", "SPEC-1616", {"title": "Automated test pipeline"}, {}),
        ("specifications", "SPEC-1825", {"title": "Self-service deployment pipeline"}, {}),
        ("specifications", "SPEC-RETIRED", {"title": "A retired requirement", "status": "retired"}, {}),
        (
            "tests",
            "TEST-2941",
            {
                "title": "Automated build/deploy pipeline verification",
                "spec_id": "SPEC-1615",
                "test_type": "unit",
                "test_file": "tests/unit/test_deploy_pipeline_production.py",
                "test_function": "test_mocked_success_path_cli_exits_zero",
                "expected_outcome": "The mocked success path exits 0",
            },
            {},
        ),
        (
            "tests",
            "TEST-8253",
            {
                "title": "test_pipeline.py exists",
                "spec_id": "SPEC-1616",
                "test_type": "unit",
                "test_file": "tests/multi_tenant/test_s153_batch2_spec_verification.py",
                "test_function": "test_pipeline_script_exists",
                "expected_outcome": "scripts/test_pipeline.py is a file",
            },
            {},
        ),
        (
            "tests",
            "TEST-DEPLOY-ORCHESTRATOR-001",
            {
                "title": "Deploy orchestrator deploy-verify-rollback pipeline",
                "spec_id": "SPEC-1825",
                "test_type": "unit",
                "test_file": "applications/Agent_Red/tests/multi_tenant/test_deploy_orchestrator.py",
                "expected_outcome": "Rollback, health polling and dry-run behave with mocked Azure CLI",
            },
            {},
        ),
        (
            "tests",
            "TEST-RETIRED-SPEC",
            {**HELPER_TEST, "title": "Test of a retired spec", "spec_id": "SPEC-RETIRED", "test_file": "tests/x.py"},
            {},
        ),
        ("tests", "TEST-NOFILE", {**HELPER_TEST, "title": "Not executable", "spec_id": "SPEC-1615"}, {}),
        (
            "tests",
            "TEST-UNPHASED",
            {**HELPER_TEST, "title": "Outside every plan phase", "spec_id": "SPEC-1615", "test_file": "tests/y.py"},
            {},
        ),
        ("test-plans", "PLAN-1", {"title": "Pipeline evidence"}, {}),
        (
            "test-phases",
            "PHASE-1",
            {
                "title": "Pipeline tests",
                "plan_id": "PLAN-1",
                "phase_order": 1,
                "gate_criteria": "Executable",
                "test_ids": [
                    "TEST-2941",
                    "TEST-8253",
                    "TEST-DEPLOY-ORCHESTRATOR-001",
                    "TEST-RETIRED-SPEC",
                    "TEST-NOFILE",
                ],
            },
            {},
        ),
    ]
    for domain, record_id, fields, extra in rows:
        result = put(client, domain, record_id, fields, **extra)
        assert result.status_code == 200, result.text


def _work_item_ids(client) -> list[str]:
    return sorted(row["id"] for row in client.get("/v1/work-items", params={"limit": 1000}).json()["records"])


def _defect(url: str, **overrides) -> str:
    fields = {
        "title": "Deploy pipeline failure: Phase 7 (ACR Docker Build)",
        "description": "Build failed with exit code 1",
        "source_spec_id": "SPEC-1615",
        "source_test_id": "TEST-2941",
        "actor": "deploy-pipeline",
        "reason": "Automated deploy pipeline (SPEC-1615) failed Phase 7 (ACR Docker Build) for staging v1.99.0",
        "client": AuthorityClient(url),
    }
    fields.update(overrides)
    return reporter.create_defect(**fields)


def _closed_port_url() -> str:
    """A loopback URL nothing listens on (the port was bound and released)."""
    probe = socket.socket()
    probe.bind(("127.0.0.1", 0))
    port = probe.getsockname()[1]
    probe.close()
    return f"http://127.0.0.1:{port}"


def _no_warning(capsys) -> None:
    captured = capsys.readouterr()
    assert "[WARN]" not in captured.out + captured.err
    assert "WARN" not in captured.err


def test_create_defect_records_a_work_item_under_the_ruled_project_with_exact_readback(
    native, monkeypatch, tmp_path, capsys
):
    service, client, _, _ = native
    _seed_pipeline_evidence(client)
    for number in (3, 7):  # existing work: the next identifier is the highest numeric id + 1, not a count
        row = {"title": f"Existing {number}", "source_spec_id": "SPEC-1615", "source_test_id": "TEST-2941"}
        assert put(client, "work-items", f"WI-{number:04d}", row, project_id=PROJECT_ID).status_code == 200
    assert (
        put(
            client,
            "work-items",
            "WORKLIST-LEGACY",
            {"title": "Non-numeric", "source_spec_id": "SPEC-1615", "source_test_id": "TEST-2941"},
            project_id=PROJECT_ID,
        ).status_code
        == 200
    )
    monkeypatch.setattr(reporter, "PAGE_LIMIT", 1)  # every listing page holds one record: the read must page
    before = history_count(service)
    with _serve(service) as url:
        # The configured route: authority_url from GT_AUTHORITY_URL over a selected groundtruth.toml.
        monkeypatch.setenv("GT_AUTHORITY_URL", url)
        config = tmp_path / "groundtruth.toml"
        config.write_text('[groundtruth]\nproject_root = "."\n', encoding="utf-8")
        assert reporter.authority_client(config).url == url
        work_item_id = _defect(url, client=reporter.authority_client(config))
    assert work_item_id == "WI-0008"
    shown = client.get(f"/v1/work-items/{work_item_id}")
    assert shown.status_code == 200, shown.text
    row = shown.json()["work_item"]
    assert row["title"] == "Deploy pipeline failure: Phase 7 (ACR Docker Build)"
    assert row["description"] == "Build failed with exit code 1"
    assert (row["source_spec_id"], row["source_test_id"]) == ("SPEC-1615", "TEST-2941")
    assert (row["origin"], row["component"]) == ("defect", "infrastructure_automation")
    assert (row["resolution_status"], row["stage"], row["version"]) == ("open", "created", 1)
    assert row["changed_by"] == "deploy-pipeline"
    assert (
        row["change_reason"]
        == "Automated deploy pipeline (SPEC-1615) failed Phase 7 (ACR Docker Build) for staging v1.99.0"
    )
    membership = shown.json()["membership"]
    assert (membership["project_id"], membership["status"]) == (PROJECT_ID, "active")
    assert history_count(service) == before + 2  # the work item and its membership, nothing else
    assert _work_item_ids(client) == ["WI-0003", "WI-0007", "WI-0008", "WORKLIST-LEGACY"]
    _no_warning(capsys)


def test_create_defect_surfaces_an_unavailable_authority_as_an_error(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(reporter.DefectReportError) as refused:
        _defect(_closed_port_url())
    assert refused.value.code == "authority_unavailable"
    assert refused.value.details["method"] == "GET" and refused.value.details["path"] == "/v1/work-items"
    assert sorted(p.name for p in tmp_path.iterdir()) == [], "nothing is recorded anywhere else"
    _no_warning(capsys)


def test_create_defect_refuses_without_a_configured_authority_url(monkeypatch, tmp_path):
    monkeypatch.delenv("GT_AUTHORITY_URL", raising=False)
    config = tmp_path / "groundtruth.toml"
    config.write_text('[groundtruth]\nproject_root = "."\n', encoding="utf-8")
    with pytest.raises(reporter.DefectReportError) as refused:
        reporter.authority_client(config)
    assert refused.value.code == "authority_url_required"
    with pytest.raises(reporter.DefectReportError) as missing:
        reporter.authority_client(tmp_path / "absent.toml")
    assert missing.value.code == "authority_configuration_invalid"
    assert not list(tmp_path.glob("*.db")), "no local database is opened as a fallback"


@pytest.mark.parametrize(
    ("overrides", "code"),
    [
        ({"source_spec_id": "SPEC-RETIRED", "source_test_id": "TEST-RETIRED-SPEC"}, "inactive_evidence"),
        ({"source_test_id": "TEST-NOFILE"}, "executable_test_required"),
        ({"source_test_id": "TEST-UNPHASED"}, "test_phase_required"),
        ({"source_test_id": "TEST-ABSENT"}, "not_found"),
        ({"title": ""}, "invalid_request"),
    ],
    ids=["retired-spec", "test-without-file", "test-outside-phase", "absent-test", "contract"],
)
def test_create_defect_surfaces_refusal_envelopes_as_errors_without_partial_writes(native, capsys, overrides, code):
    service, client, _, _ = native
    _seed_pipeline_evidence(client)
    before = (history_count(service), _work_item_ids(client))
    with _serve(service) as url, pytest.raises(reporter.DefectReportError) as refused:
        _defect(url, **overrides)
    assert refused.value.code == code
    assert (history_count(service), _work_item_ids(client)) == before
    _no_warning(capsys)


def test_create_defect_refuses_when_the_ruled_project_is_absent(native, monkeypatch):
    service, client, _, _ = native
    _seed_pipeline_evidence(client)
    monkeypatch.setattr(reporter, "DEFECT_PROJECT_ID", "PROJECT-ABSENT")
    before = (history_count(service), _work_item_ids(client))
    with _serve(service) as url, pytest.raises(reporter.DefectReportError) as refused:
        _defect(url)
    assert refused.value.code == "not_found"
    assert (history_count(service), _work_item_ids(client)) == before


def test_create_defect_retries_a_taken_identifier_within_a_bounded_window(native, monkeypatch):
    service, client, _, _ = native
    _seed_pipeline_evidence(client)
    taken = {"title": "Taken", "source_spec_id": "SPEC-1615", "source_test_id": "TEST-2941"}
    assert put(client, "work-items", "WI-0003", taken, project_id=PROJECT_ID).status_code == 200
    real = reporter.next_work_item_id
    reads: list[str] = []

    def stale_then_current(authority):
        chosen = "WI-0003" if not reads else real(authority)  # the first read is stale: WI-0003 exists
        reads.append(chosen)
        return chosen

    monkeypatch.setattr(reporter, "next_work_item_id", stale_then_current)
    with _serve(service) as url:
        assert _defect(url) == "WI-0004"
    assert reads == ["WI-0003", "WI-0004"]
    assert client.get("/v1/work-items/WI-0003").json()["work_item"]["title"] == "Taken"  # never overwritten

    monkeypatch.setattr(reporter, "next_work_item_id", lambda authority: "WI-0003")  # every read collides
    puts: list[str] = []
    original = AuthorityClient.request

    def counting(self, method, path, *, body=None, query=None):
        if method == "PUT":
            puts.append(path)
        return original(self, method, path, body=body, query=query)

    monkeypatch.setattr(AuthorityClient, "request", counting)
    before = history_count(service)
    with _serve(service) as url, pytest.raises(reporter.DefectReportError) as refused:
        _defect(url)
    assert refused.value.code == "cas_conflict"
    assert puts == ["/v1/work-items/WI-0003"] * reporter.ID_ALLOCATION_ATTEMPTS
    assert history_count(service) == before


def test_create_defect_refuses_a_readback_that_differs_from_the_accepted_record(native):
    service, client, _, _ = native
    _seed_pipeline_evidence(client)

    class Altered(AuthorityClient):
        def request(self, method, path, *, body=None, query=None):
            result = super().request(method, path, body=body, query=query)
            if method == "GET" and path.startswith("/v1/work-items/WI-"):
                result["work_item"]["title"] = "Something else"
            return result

    with _serve(service) as url, pytest.raises(reporter.DefectReportError) as refused:
        _defect(url, client=Altered(url))
    assert refused.value.code == "readback_mismatch"


def _create_defect_calls(script: str) -> list[ast.Call]:
    tree = ast.parse((ROOT / script).read_text(encoding="utf-8"))
    return [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "create_defect"
    ]


def _module_constants(script: str) -> tuple[str, str, str]:
    """The evidence-pair constants as the script states them (read, not imported: the scripts have import effects)."""
    tree = ast.parse((ROOT / script).read_text(encoding="utf-8"))
    values = {
        node.targets[0].id: node.value.value
        for node in tree.body
        if isinstance(node, ast.Assign)
        and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name)
        and isinstance(node.value, ast.Constant)
    }
    return values["DEFECT_SOURCE_SPEC_ID"], values["DEFECT_SOURCE_TEST_ID"], values["DEFECT_ACTOR"]


def test_the_shim_paths_and_the_phase_result_writer_are_gone():
    assert not (ROOT / "tools" / "knowledge-db").exists()
    for script in (*PIPELINES, RETIRED_CALL_SITE, "scripts/_defect_reporter.py"):
        text = (ROOT / script).read_text(encoding="utf-8")
        assert SHIM_LINE not in text and "knowledge-db" not in text, script
        assert "KnowledgeDB" not in text and "next_wi_id" not in text, script
    pipeline = importlib.import_module("scripts.test_pipeline")
    assert not hasattr(pipeline, "_record_phase_result")
    assert "_record_phase_result" not in (ROOT / "scripts/test_pipeline.py").read_text(encoding="utf-8")
    assert not hasattr(reporter, "next_wi_id")


def test_every_call_site_passes_its_own_evidence_pair_and_the_retired_site_is_gone():
    for script, (spec_id, test_id, actor) in PIPELINES.items():
        calls = _create_defect_calls(script)
        assert len(calls) == 1, script
        keywords = {keyword.arg for keyword in calls[0].keywords}
        assert {"title", "description", "source_spec_id", "source_test_id", "actor", "reason"} <= keywords, script
        assert "changed_by" not in keywords, script
        assert _module_constants(script) == (spec_id, test_id, actor), script
    assert _create_defect_calls(RETIRED_CALL_SITE) == []
    assert "from scripts._defect_reporter" not in (ROOT / RETIRED_CALL_SITE).read_text(encoding="utf-8")


def test_test_pipeline_summary_records_each_failed_phase_and_propagates_a_refusal(native, monkeypatch, tmp_path):
    service, client, _, _ = native
    _seed_pipeline_evidence(client)
    pipeline = importlib.import_module("scripts.test_pipeline")
    args = argparse.Namespace(env="staging", version="1.99.0")
    results = [
        pipeline.PhaseResult(0, "Pre-check", "FAIL", 0.1, "not a numbered phase"),
        pipeline.PhaseResult(1, "Pre-flight Checks", "PASS", 0.1),
        pipeline.PhaseResult(3, "Live E2E", "FAIL", 0.1, "2 failed"),
    ]
    with _serve(service) as url:
        monkeypatch.setenv("GT_AUTHORITY_URL", url)
        pipeline.run_summary(results, args, time.time(), tmp_path / "run.log")
    ids = _work_item_ids(client)
    assert ids == ["WI-0001"]
    row = client.get("/v1/work-items/WI-0001").json()["work_item"]
    assert row["title"] == "Test pipeline failure: Phase 3 (Live E2E)"
    assert (row["source_spec_id"], row["source_test_id"], row["changed_by"]) == (
        "SPEC-1616",
        "TEST-8253",
        "test-pipeline",
    )
    assert (
        row["change_reason"]
        == "Automated test pipeline (PLAN-001, SPEC-1616) failed Phase 3 (Live E2E) for staging v1.99.0"
    )
    assert any("Created DEFECT: WI-0001 (Phase 3)" in line for line in pipeline._log_lines)
    assert not any("KB phase update" in line or "[WARN " in line for line in pipeline._log_lines)

    monkeypatch.setenv("GT_AUTHORITY_URL", _closed_port_url())
    before = history_count(service)
    with pytest.raises(reporter.DefectReportError) as refused:
        pipeline.run_summary(results, args, time.time(), tmp_path / "again.log")
    assert refused.value.code == "authority_unavailable"
    assert history_count(service) == before


def test_deploy_pipeline_records_the_first_failed_phase_through_the_native_writer(native, monkeypatch):
    service, client, _, _ = native
    _seed_pipeline_evidence(client)
    pipeline = importlib.import_module("scripts.deploy_pipeline")
    args = argparse.Namespace(env="staging", version="v1.99.0")
    results = [
        pipeline.PhaseResult(1, "Preflight", "PASS", 0.1),
        pipeline.PhaseResult(7, "ACR Docker Build", "FAIL", 0.1, "exit 1"),
        pipeline.PhaseResult(8, "Deploy", "FAIL", 0.1, "skipped"),
    ]
    with _serve(service) as url:
        monkeypatch.setenv("GT_AUTHORITY_URL", url)
        assert pipeline._create_defect_work_item(results, args) == "WI-0001"
    row = client.get("/v1/work-items/WI-0001").json()["work_item"]
    assert row["title"] == "Deploy pipeline failure: Phase 7 (ACR Docker Build)"
    assert (row["source_spec_id"], row["source_test_id"], row["changed_by"]) == (
        "SPEC-1615",
        "TEST-2941",
        "deploy-pipeline",
    )
    assert (
        row["change_reason"]
        == "Automated deploy pipeline (SPEC-1615) failed Phase 7 (ACR Docker Build) for staging v1.99.0"
    )
    assert "Phase 8 (Deploy): skipped" in row["description"]
    assert pipeline._create_defect_work_item([pipeline.PhaseResult(1, "Preflight", "PASS", 0.1)], args) is None


def test_deploy_orchestrator_rollback_records_a_defect_or_fails_loudly(native, monkeypatch):
    service, client, _, _ = native
    _seed_pipeline_evidence(client)
    orchestrator = importlib.import_module("scripts.deploy_orchestrator")
    rolled_back = subprocess.CompletedProcess(args=["az"], returncode=0, stdout="", stderr="")

    def result():
        row = orchestrator.DeployResult(environment="staging", version="v1.99.0", previous_image="acr/api:v1.98.0")
        row.verification_pass, row.verification_fail, row.error = 3, 2, "health check failed"
        return row

    with _serve(service) as url, patch.object(orchestrator, "_run", return_value=rolled_back):
        monkeypatch.setenv("GT_AUTHORITY_URL", url)
        outcome = result()
        orchestrator._rollback(outcome, "staging")
    assert outcome.rollback_performed and outcome.rollback_status == "succeeded"
    row = client.get("/v1/work-items/WI-0001").json()["work_item"]
    assert row["title"] == "Deploy rollback: staging v1.99.0 → acr/api:v1.98.0"
    assert (row["source_spec_id"], row["source_test_id"]) == ("SPEC-1825", "TEST-DEPLOY-ORCHESTRATOR-001")
    assert row["changed_by"] == "deploy-orchestrator"
    assert (
        row["change_reason"]
        == "Deploy orchestrator (SPEC-1825) rolled staging back from v1.99.0 to acr/api:v1.98.0 after failed verification"
    )

    monkeypatch.setenv("GT_AUTHORITY_URL", _closed_port_url())
    with patch.object(orchestrator, "_run", return_value=rolled_back), pytest.raises(reporter.DefectReportError):
        orchestrator._rollback(result(), "staging")
    assert not any("Could not create DEFECT" in line for line in orchestrator._log_lines)
