"""The native harness record path: a harness installation row is created as `registered` through the authority
and moves only along the lifecycle transition graph (registered -> active -> suspended -> active | retired -> registered),
the last active harness cannot be suspended or retired, every refusal is typed and leaves the record and its history
untouched, and the ordinary CLI (`gt harness record`) reaches the same path through a served authority. Roles are not
harness fields (they bind to contexts). Re-covers the lifecycle, invalid-transition and last-active obligations of the
retired legacy harness CLI tests; the cross-harness diagnostic mode remains a separate open obligation."""

from __future__ import annotations

import json
import socket
import subprocess
import sys

import pytest

from platform_tests.groundtruth_kb.native_fixtures import _serve_authority, harness_fields, history_count, put
from platform_tests.groundtruth_kb.native_fixtures import native as native

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]


def test_harness_is_created_registered_and_follows_the_lifecycle_graph(native):
    service, client, *_ = native
    created = put(client, "harnesses", "H-1", harness_fields())
    assert created.status_code == 200, created.text
    assert created.json()["status"] == "registered" and created.json()["version"] == 1
    assert put(client, "harnesses", "H-1", {"status": "active"}, expected_version=1).json()["status"] == "active"
    before = history_count(service)
    for illegal in ("registered", "retired"):
        refused = put(client, "harnesses", "H-1", {"status": illegal}, expected_version=2)
        assert refused.status_code == 422, refused.text
        assert refused.json()["error"]["code"] == "invalid_harness_transition"
    assert client.get("/v1/harnesses/H-1").json()["version"] == 2 and history_count(service) == before
    assert put(client, "harnesses", "H-2", harness_fields(harness_name="second")).status_code == 200
    assert put(client, "harnesses", "H-2", {"status": "active"}, expected_version=1).status_code == 200
    suspended = put(client, "harnesses", "H-1", {"status": "suspended"}, expected_version=2)
    assert suspended.status_code == 200 and suspended.json()["status"] == "suspended"
    retired = put(client, "harnesses", "H-1", {"status": "retired"}, expected_version=3)
    assert retired.status_code == 200 and retired.json()["status"] == "retired"
    assert put(client, "harnesses", "H-1", {"status": "active"}, expected_version=4).status_code == 422
    reregistered = put(client, "harnesses", "H-1", {"status": "registered"}, expected_version=4)
    assert reregistered.status_code == 200 and reregistered.json()["version"] == 5


def test_the_last_active_harness_cannot_be_suspended_or_retired(native):
    service, client, *_ = native
    assert put(client, "harnesses", "H-1", harness_fields()).status_code == 200
    assert put(client, "harnesses", "H-1", {"status": "active"}, expected_version=1).status_code == 200
    before = history_count(service)
    refused = put(client, "harnesses", "H-1", {"status": "suspended"}, expected_version=2)
    assert refused.status_code == 422 and refused.json()["error"]["code"] == "last_active_harness", refused.text
    assert client.get("/v1/harnesses/H-1").json()["status"] == "active" and history_count(service) == before
    assert put(client, "harnesses", "H-2", harness_fields(harness_name="second")).status_code == 200
    assert put(client, "harnesses", "H-2", {"status": "active"}, expected_version=1).status_code == 200
    assert put(client, "harnesses", "H-1", {"status": "suspended"}, expected_version=2).status_code == 200


def test_a_new_harness_needs_its_identity_and_starts_registered(native):
    service, client, *_ = native
    before = history_count(service)
    missing = put(client, "harnesses", "H-X", {"harness_type": "test"})
    assert missing.status_code == 422 and missing.json()["error"]["code"] == "harness_fields_required"
    early = put(client, "harnesses", "H-X", harness_fields(status="active"))
    assert early.status_code == 422 and early.json()["error"]["code"] == "invalid_harness_transition"
    unknown = put(client, "harnesses", "H-X", harness_fields(status="paused"))
    assert unknown.status_code == 422
    unexpected = put(client, "harnesses", "H-X", harness_fields(role="prime-builder"))
    assert unexpected.status_code == 422  # roles bind to contexts, never to installations
    assert client.get("/v1/harnesses/H-X").status_code == 404 and history_count(service) == before


def test_the_ordinary_cli_records_a_harness_through_a_served_authority(native, tmp_path):
    _service, client, *_ = native
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    process, env = _serve_authority(tmp_path, port)
    try:
        config = tmp_path / "client.toml"
        config.write_text(
            f'[groundtruth]\nproject_root = "{tmp_path.as_posix()}"\nauthority_url = "http://127.0.0.1:{port}"\n',
            encoding="utf-8",
        )
        fields = tmp_path / "fields.json"
        fields.write_text(json.dumps(harness_fields(harness_name="cli-recorded")), encoding="utf-8")
        env = dict(env, PYTHONIOENCODING="utf-8")
        env.pop("GT_AUTHORITY_URL", None)

        def gt(*arguments):
            return subprocess.run(
                [sys.executable, "-m", "groundtruth_kb", "--config", str(config), *arguments, "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=tmp_path,
                env=env,
                timeout=120,
            )

        recorded = gt(
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
            "Record through the ordinary CLI",
        )
        assert recorded.returncode == 0, recorded.stderr
        assert json.loads(recorded.stdout)["status"] == "registered"
        fields.write_text(json.dumps({"status": "retired"}), encoding="utf-8")
        refused = gt(
            "harness",
            "record",
            "--id",
            "H-CLI",
            "--fields-file",
            str(fields),
            "--expected-version",
            "1",
            "--actor",
            "qualification",
            "--change-reason",
            "Illegal transition",
        )
        assert refused.returncode != 0 and "invalid_harness_transition" in refused.stderr
        shown = gt("harness", "show", "H-CLI")
        assert shown.returncode == 0 and json.loads(shown.stdout)["version"] == 1
        current = client.get("/v1/harnesses/H-CLI").json()
        assert current["harness_name"] == "cli-recorded"
        assert current["capabilities_ref"] == harness_fields()["capabilities_ref"]
        assert not (tmp_path / "harness-state").exists()
        assert not (tmp_path / "groundtruth.db").exists()
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=15)
