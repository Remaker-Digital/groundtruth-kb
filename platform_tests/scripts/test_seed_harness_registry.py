"""Native registration replaces the retired projection-to-SQLite seeder.

These tests preserve identity, invocation, explicit registered state, stale-write
refusal, readback and input isolation obligations. Role-bearing projection
import, implicit activation and projection regeneration are retired behavior.
No result here qualifies an installation or its runtime capabilities.
"""

from __future__ import annotations

import json
import socket
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from groundtruth_kb.authority_api import create_authority_app

from platform_tests.groundtruth_kb.test_deepseek_sdk_harness import _serve_authority
from platform_tests.groundtruth_kb.test_native_authority_service import native as native
from platform_tests.groundtruth_kb.test_native_authority_service import put
from platform_tests.groundtruth_kb.test_native_harness_records import harness_fields
from platform_tests.groundtruth_kb.test_native_session_context import (
    database_contents,
    files,
)

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]
ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def registration(native, tmp_path):
    service, _, *_ = native
    # Deliberately obsolete input canaries, not generated or valid configuration.
    old = tmp_path / "harness-state"
    old.mkdir()
    (old / "harness-registry.json").write_text(
        json.dumps({"harnesses": [{"id": "UNREQUESTED", "role": ["prime-builder"], "status": "active"}]}),
        encoding="utf-8",
    )
    (old / "role-assignments.json").write_text('{"role":"prime-builder"}', encoding="utf-8")
    (tmp_path / "groundtruth.db").write_bytes(b"No SQLite fallback or import")
    with TestClient(create_authority_app(service, project_root=tmp_path)) as client:
        yield service, client, tmp_path


@pytest.mark.parametrize("explicit_status", [False, True])
def test_registration_starts_registered_without_importing_projection_state(registration, explicit_status):
    service, client, root = registration
    disk = files(root)
    fields = harness_fields(harness_name="explicit-installation")
    if explicit_status:
        fields["status"] = "registered"
    result = put(client, "harnesses", "H-1", fields)
    assert result.status_code == 200, result.text
    assert result.json()["status"] == "registered" and result.json()["version"] == 1
    assert {r["id"] for r in client.get("/v1/harnesses").json()["records"]} == {"H-1"}
    assert client.get("/v1/harnesses/UNREQUESTED").status_code == 404
    assert database_contents(service)["session_init_bindings"] == []
    assert files(root) == disk


def test_registration_round_trips_declared_identity_and_invocation_metadata(
    registration,
):
    _, client, root = registration
    disk = files(root)
    invocation = {"headless": {"argv": ["fixture-harness", "exec", "{{PROMPT}}"]}}
    fields = harness_fields(
        harness_name="declared-name",
        harness_type="declared-kind",
        invocation_surfaces=invocation,
    )
    result = put(client, "harnesses", "H-DECLARED", fields)
    assert result.status_code == 200, result.text
    record = client.get("/v1/harnesses/H-DECLARED").json()
    assert all(record[key] == value for key, value in fields.items())
    assert record["status"] == "registered" and "role" not in record
    assert files(root) == disk


def test_repeated_create_and_stale_update_refuse_without_altering_existing_records(
    registration,
):
    service, client, root = registration
    assert put(client, "harnesses", "H-1", harness_fields()).status_code == 200
    before, disk = database_contents(service), files(root)
    for fields in (harness_fields(), harness_fields(harness_name="must-not-overwrite")):
        refused = put(client, "harnesses", "H-1", fields)
        assert refused.status_code == 409 and refused.json()["error"]["code"] == "cas_conflict"
        assert database_contents(service) == before and files(root) == disk
    updated = put(
        client,
        "harnesses",
        "H-1",
        {"harness_name": "explicit-update"},
        expected_version=1,
    )
    assert updated.status_code == 200 and updated.json()["version"] == 2
    assert updated.json()["status"] == "registered"
    assert files(root) == disk


@pytest.mark.parametrize(
    "field,value",
    [("role", "prime-builder"), ("role", ["loyal-opposition"]), ("schema_version", 1)],
)
def test_projection_and_role_fields_are_rejected_without_partial_registration(registration, field, value):
    service, client, root = registration
    before, disk = database_contents(service), files(root)
    response = put(client, "harnesses", "H-BAD", harness_fields(**{field: value}))
    assert response.status_code == 422, response.text
    assert response.json()["code"] == "invalid_request"
    assert database_contents(service) == before and files(root) == disk


def test_new_registration_cannot_copy_an_active_status_from_old_input(registration):
    service, client, root = registration
    before, disk = database_contents(service), files(root)
    response = put(client, "harnesses", "H-BAD", harness_fields(status="active"))
    assert response.status_code == 422 and response.json()["error"]["code"] == "invalid_harness_transition"
    assert database_contents(service) == before and files(root) == disk


def test_registry_reads_leave_projection_canaries_and_canonical_history_unchanged(registration, monkeypatch):
    service, client, root = registration
    assert put(client, "harnesses", "H-1", harness_fields()).status_code == 200
    monkeypatch.setenv("GTKB_HARNESS_REGISTRY_PATH", str(root / "harness-state/harness-registry.json"))
    before, disk = database_contents(service), files(root)
    for _ in range(2):
        assert client.get("/v1/harnesses/H-1").json()["status"] == "registered"
        assert len(client.get("/v1/harnesses").json()["records"]) == 1
    assert database_contents(service) == before and files(root) == disk


def test_retired_seed_entrypoint_is_absent_and_cannot_import_old_files(registration):
    service, _, root = registration
    entry = ROOT / "scripts/seed_harness_registry.py"
    assert not entry.exists()
    before, disk = database_contents(service), files(root)
    result = subprocess.run(
        [sys.executable, str(entry)],
        cwd=root,
        capture_output=True,
        encoding="utf-8",
        timeout=10,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    assert result.returncode != 0 and not result.stdout
    assert database_contents(service) == before and files(root) == disk


def test_ordinary_cli_registration_reads_selected_authority_and_refuses_outage(
    registration,
):
    service, client, root = registration
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    process, env = _serve_authority(root, port)
    cwd = root / "client"
    cwd.mkdir()
    config = cwd / "client.toml"
    config.write_text(
        f'[groundtruth]\nproject_root="."\nauthority_url="http://127.0.0.1:{port}"\ndb_path="sentinel.db"\n',
        encoding="utf-8",
    )
    (cwd / "sentinel.db").write_bytes(b"Selected service only")
    fields = cwd / "fields.json"
    fields.write_text(json.dumps(harness_fields(harness_name="cli-selected")), encoding="utf-8")
    env = {k: v for k, v in env.items() if not k.startswith(("PG", "GT_POSTGRES_"))}
    env.pop("GT_PROJECT_ROOT", None)
    env["PYTHONIOENCODING"] = "utf-8"
    env["GTKB_HARNESS_REGISTRY_PATH"] = str(root / "harness-state/harness-registry.json")

    def gt(*arguments):
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "groundtruth_kb",
                "--config",
                str(config),
                *arguments,
                "--json",
            ],
            cwd=cwd,
            env=env,
            capture_output=True,
            encoding="utf-8",
            timeout=20,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )

    try:
        disk = files(cwd)
        record = gt(
            "harness",
            "record",
            "--id",
            "H-CLI",
            "--fields-file",
            str(fields),
            "--expected-version",
            "0",
            "--actor",
            "qualification",
            "--change-reason",
            "Explicit native registration",
        )
        assert record.returncode == 0, record.stderr
        assert json.loads(record.stdout)["status"] == "registered"
        shown = gt("harness", "show", "H-CLI")
        assert shown.returncode == 0 and json.loads(shown.stdout)["harness_name"] == "cli-selected"
        assert client.get("/v1/harnesses/UNREQUESTED").status_code == 404
        assert files(cwd) == disk
        before = database_contents(service)
        process.terminate()
        process.wait(timeout=10)
        failed = gt("harness", "list")
        assert failed.returncode != 0 and "authority_unavailable" in failed.stderr and not failed.stdout
        assert database_contents(service) == before and files(cwd) == disk
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=10)
