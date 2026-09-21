"""Served-authority behavior for D31/M25 doctor readers on disposable PostgreSQL.

The authority and each script subprocess read the same native schema. SQLite is
refused in the checker process and an inert file is preserved. Fixtures arrange
one implementation-active row through the kernel fixture writer; the reader's
membership request itself is a real HTTP GET, recorded without mocking its result.
"""

from __future__ import annotations

import importlib.util
import json
import socket
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from groundtruth_kb.authority_api import create_authority_app
from groundtruth_kb.authority_client import AuthorityClient
from groundtruth_kb.project.doctor import (
    _check_application_scope_alignment,
    _check_authority_readiness,
    _check_canonical_terms_registry,
    _check_obsolete_reference_purge,
    _check_standing_backlog_health,
    check_standing_backlog_health,
)

from platform_tests.groundtruth_kb.native_fixtures import _serve_authority, put, seed, work_fields
from platform_tests.groundtruth_kb.native_fixtures import native as native

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]
REPO_ROOT = Path(__file__).resolve().parents[2]
SENTINEL = b"Never opened by a doctor check"


@pytest.fixture
def served(native, tmp_path, monkeypatch):
    service, _client, *_ = native
    # Native project creation validates the selected platform checkout. The
    # fixture must supply that real repository before seeding project rows.
    subprocess.run(["git", "init", "--quiet", str(tmp_path)], check=True, capture_output=True, timeout=15)
    slot = tmp_path / "applications" / "Agent_Red"
    slot.mkdir(parents=True)
    (slot.parent / "registry.toml").write_text('[applications.Agent_Red]\nslot="Agent_Red"\n', encoding="utf-8")
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    process, env = _serve_authority(tmp_path, port)
    try:
        monkeypatch.delenv("GT_AUTHORITY_URL", raising=False)
        root = tmp_path / "project"
        root.mkdir()
        url = f"http://127.0.0.1:{port}"
        (root / "groundtruth.toml").write_text(f'[groundtruth]\nauthority_url="{url}"\n', encoding="utf-8")
        sentinel = root / "groundtruth.db"
        sentinel.write_bytes(SENTINEL)

        def refuse(*args, **kwargs):
            pytest.fail("Doctor checks cannot open SQLite")

        monkeypatch.setattr("sqlite3.connect", refuse)
        with TestClient(create_authority_app(service, project_root=tmp_path)) as client:
            yield service, client, root, url, env
        assert sentinel.read_bytes() == SENTINEL
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=15)


def test_authority_readiness_reads_the_served_status(served):
    _, _, root, url, _ = served
    result = _check_authority_readiness(root)
    assert result.status == "pass", result.message
    assert result.required is True and result.found is True
    assert result.message.startswith(f"Authority {url} ready (schema ")


def test_application_scope_alignment_reads_the_served_pages(served):
    _, client, root, _, _ = served
    result = put(
        client,
        "specifications",
        "SPEC-SCOPE-ALIGNED",
        {
            "title": "Aligned application specification",
            "description": "Application evidence",
            "status": "active",
            "source_paths": ["applications/Agent_Red/app/main.py"],
            "application_scope": "application:Agent_Red",
        },
    )
    assert result.status_code == 200, result.text
    result = put(
        client,
        "tests",
        "TEST-SCOPE-ALIGNED",
        {
            "title": "Aligned platform test",
            "spec_id": "SPEC-SCOPE-ALIGNED",
            "test_type": "unit",
            "test_file": "platform_tests/scripts/test_platform.py",
            "expected_outcome": "Alignment observed",
            "application_scope": "gtkb_platform",
        },
    )
    assert result.status_code == 200, result.text
    check = _check_application_scope_alignment(root)
    assert check.status == "pass", check.message
    assert check.message.startswith("Application-scope alignment OK (1 specifications, 1 tests)")


def test_standing_backlog_health_reads_real_implementation_membership(served, monkeypatch):
    service, client, root, _, _ = served
    seed(client)
    result = put(client, "work-items", "WI-OPEN", work_fields(), project_id="PROJECT-1")
    assert result.status_code == 200, result.text
    row = result.json()["work_item"]
    service.kernel.mutate_current(
        table="work_items",
        identity={"id": row["id"]},
        expected_version=row["version"],
        new_state={**row, "stage": "implementing"},
        actor="qualification",
        reason="Arrange implementation-active doctor fixture",
    )
    calls = []
    request = AuthorityClient.request

    def observed(self, method, path, **kwargs):
        calls.append((method, path))
        return request(self, method, path, **kwargs)

    monkeypatch.setattr(AuthorityClient, "request", observed)
    payload = check_standing_backlog_health(root)
    assert payload["status"] == "pass", payload["findings"]
    assert payload["summary"]["non_implementation_open_count"] == 0
    assert calls.count(("GET", "/v1/work-items/WI-OPEN")) == 1
    assert client.get("/v1/work-items/WI-OPEN").json()["membership"]["project_id"] == "PROJECT-1"
    assert _check_standing_backlog_health(root).status == "pass"
    assert not (root / "bridge").exists()
    assert ("GET", "/v1/bridge/state-report") in calls
    # Exercise the production consumer with the real doctor and real HTTP reads.
    gate_spec = importlib.util.spec_from_file_location(
        "doctor_native_release_gate", REPO_ROOT / "scripts/release_candidate_gate.py"
    )
    assert gate_spec and gate_spec.loader
    gate = importlib.util.module_from_spec(gate_spec)
    gate_spec.loader.exec_module(gate)
    monkeypatch.setattr(gate, "PROJECT_ROOT", root)
    gate._check_standing_backlog_health()
    bridge = root / "bridge"
    bridge.mkdir()
    (bridge / "INDEX.md").write_text("NO-GO: contradictory obsolete file index", encoding="utf-8")
    (bridge / "stale-001.md").write_text("NO-GO\nDate: 1999-01-01\n", encoding="utf-8")
    assert check_standing_backlog_health(root) == payload
    gate._check_standing_backlog_health()
    # Configured transport failure is read through the same real consumer.
    with socket.socket() as unavailable:
        unavailable.bind(("127.0.0.1", 0))
        unavailable_port = unavailable.getsockname()[1]
        (root / "groundtruth.toml").write_text(
            f'[groundtruth]\nauthority_url="http://127.0.0.1:{unavailable_port}"\n', encoding="utf-8"
        )
        with pytest.raises(gate.GateFailure, match="authority_unavailable"):
            gate._check_standing_backlog_health()


def test_purge_pairing_reads_native_changes_without_creating_a_store(served, monkeypatch):
    _, client, root, _, _ = served
    monkeypatch.syspath_prepend(str(REPO_ROOT / "scripts"))
    seed(client)
    target = "RETIRE-SPEC-NATIVE-FIXTURE"
    result = put(
        client,
        "specifications",
        target,
        {"title": "Retirement fixture", "description": "Purge obligation", "status": "active"},
    )
    assert result.status_code == 200, result.text
    before = _check_obsolete_reference_purge(root)
    assert before.status == "warning" and target in before.message
    result = put(client, "projects", "PROJECT-PURGE", {"name": "OBSOLETE-REFERENCE-PURGE fixture"})
    assert result.status_code == 200, result.text
    result = put(
        client,
        "work-items",
        "WI-PURGE",
        work_fields(description=f"Remove {target} references"),
        project_id="PROJECT-PURGE",
    )
    assert result.status_code == 200, result.text
    after = _check_obsolete_reference_purge(root)
    assert after.status == "pass", after.message


def test_orphan_script_cli_uses_native_ids_and_ignores_missing_bridge_files(served):
    _, client, root, _, env = served
    seed(client)
    src = root / "src"
    src.mkdir()
    sample = src / "sample.py"
    command = [
        sys.executable,
        str(REPO_ROOT / "scripts/orphan_citation_audit.py"),
        "--root",
        str(root),
        "--scan-dir",
        "src",
    ]
    sample.write_text("# SPEC-MISSING-001\n", encoding="utf-8")
    failed = subprocess.run(command, env=env, cwd=root, capture_output=True, text=True, encoding="utf-8", timeout=30)
    assert failed.returncode == 1, failed.stderr
    assert json.loads(failed.stdout)["orphans"][0]["anchor"] == "SPEC-MISSING-001"
    sample.write_text("# SPEC-1 bridge/absent-thread-001.md\n", encoding="utf-8")
    passed = subprocess.run(command, env=env, cwd=root, capture_output=True, text=True, encoding="utf-8", timeout=30)
    assert passed.returncode == 0, passed.stderr
    assert json.loads(passed.stdout)["orphans"] == []
    assert not (root / "bridge").exists()


def test_native_terminology_diagnostics_ignore_local_definitions(served):
    _, client, root, _, _ = served
    seed(client)
    result = put(
        client,
        "terms",
        "TERM-NATIVE",
        {
            "canonical_term": "Native example",
            "definition": "Current native definition",
            "authority_level": "platform_core",
            "scope": "platform",
            "accepted_synonyms": [],
            "lifecycle_status": "active",
            "source_authority": "SPEC-1",
        },
    )
    assert result.status_code == 200, result.text
    rules = root / ".claude/rules"
    rules.mkdir(parents=True)
    glossary = rules / "canonical-terminology.md"
    glossary.write_text("Conflicting local definition", encoding="utf-8")
    check = _check_canonical_terms_registry(root)
    assert check.status == "pass", check.message
    result = put(client, "specifications", "SPEC-1", {"status": "retired"}, expected_version=1)
    assert result.status_code == 200, result.text
    failed = _check_canonical_terms_registry(root)
    assert failed.status == "fail" and "source_issues=1" in failed.message
    assert glossary.read_text(encoding="utf-8") == "Conflicting local definition"
