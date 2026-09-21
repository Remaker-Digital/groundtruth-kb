"""Native diagnostic reads, exact context provenance and truthful coverage.

These tests qualify the shared report/CLI on disposable PostgreSQL. They do not
qualify real harness hosts, supply run telemetry or grant parity exemptions.
"""

from __future__ import annotations

import json
import socket
import subprocess
import sys

import pytest
from groundtruth_kb.authority_client import AuthorityClientError
from groundtruth_kb.harness_diagnostic import SCHEMA_ID, collect_harness_diagnostic, diagnose_harness

from platform_tests.groundtruth_kb.native_fixtures import _serve_authority, bind, history_count, put, register
from platform_tests.groundtruth_kb.native_fixtures import native as native

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]


class ReadClient:
    def __init__(self, client):
        self.client = client
        self.calls = []

    def request(self, method, path, *, query=None):
        assert method == "GET", "A diagnostic must not write"
        assert path.startswith("/v1/harnesses/") or path == "/v1/sessions/binding", "No provider or state discovery"
        self.calls.append((method, path, query))
        result = self.client.get(path, params=query)
        if result.status_code != 200:
            error = result.json()["error"]
            raise AuthorityClientError(error["code"], error["message"])
        return result.json()


def test_unknown_harness_returns_structured_error_without_mutation(native):
    service, client, *_ = native
    register(client)
    before = history_count(service)
    reader = ReadClient(client)
    result = collect_harness_diagnostic(reader, "Z")
    assert result["status"] == "error" and result["errors"] == ["harness_not_registered"]
    assert reader.calls == [("GET", "/v1/harnesses/Z", None)]
    assert history_count(service) == before


def test_registry_inventory_has_the_same_contract_without_claiming_host_parity(native):
    service, client, *_ = native
    for identifier in "ABCDEFGHI":
        register(client, identifier, active=identifier != "I")
    assert put(client, "harnesses", "D", {"status": "suspended"}, expected_version=2).status_code == 200
    inventory = client.get("/v1/harnesses").json()["records"]
    before = history_count(service)
    for row in inventory:
        reader = ReadClient(client)
        result = collect_harness_diagnostic(reader, row["id"])
        assert result["schema_id"] == SCHEMA_ID
        assert result["status"] == "partial" and result["parity"]["status"] == "unqualified"
        assert result["harness"]["record_version"] == row["version"]
        assert result["harness"]["lifecycle_status"] == row["status"]
        assert result["role"]["role"] is None and len(reader.calls) == 1
        assert result["checks"]["hooks"]["status"] == "unavailable"
        assert result["checks"]["adapter_readiness"]["status"] == "unavailable"
        assert result["harness"]["capabilities"]["observed"] is None
        assert all(value is None for value in result["measurements"].values())
        assert result["recent_runs"] == []
        assert result["recent_runs_bounds"] == {"record_limit": 50, "records_returned": 0}
        assert result["field_status"]["telemetry"]["status"] == "unavailable"
    assert client.get("/v1/harnesses").json()["records"] == inventory
    assert history_count(service) == before


def test_role_comes_only_from_the_exact_selected_binding(native, monkeypatch):
    service, client, *_ = native
    register(client)
    first = bind(client, "first-context", "pb")
    successor = bind(client, "successor-context", "lo")
    monkeypatch.setenv("GTKB_NATIVE_CONTEXT_ID", "successor-context")
    before = history_count(service)
    reader = ReadClient(client)
    first_report = collect_harness_diagnostic(reader, "A", native_context_id="first-context")
    assert first_report["role"]["role"] == "prime-builder"
    assert first_report["role"]["session_context_id"] == first["session_context_id"]
    assert first_report["role"]["source"] == "native_session_binding"
    assert "no_harness_association_asserted" in first_report["role"]["scope"]
    second_report = collect_harness_diagnostic(reader, "A", native_context_id="successor-context")
    assert second_report["role"]["role"] == "loyal-opposition"
    assert second_report["role"]["session_context_id"] == successor["session_context_id"]
    unselected = collect_harness_diagnostic(reader, "A")
    assert unselected["role"]["role"] is None
    assert unselected["role"]["unavailable_reason"] == "native_context_not_selected"
    missing = collect_harness_diagnostic(reader, "A", native_context_id="unbound")
    assert missing["role"]["role"] is None and missing["role"]["unavailable_reason"] == "no_session_binding"
    assert missing["correlation"]["session_id"] is None
    assert client.get("/v1/sessions/binding", params={"native_context_id": "first-context"}).json() == first
    assert client.get("/v1/sessions/binding", params={"native_context_id": "successor-context"}).json() == successor
    assert history_count(service) == before


def test_privacy_excludes_invocation_values_and_fingerprint_is_metadata_only(native):
    _, client, *_ = native
    register(client)
    first = collect_harness_diagnostic(ReadClient(client), "A")
    assert "private-" not in json.dumps(first)
    assert first["harness"]["provider_identity"] is None and first["harness"]["model_identity"] is None
    assert first["provider_health"]["mode"] == "local" and first["provider_health"]["status"] == "unavailable"
    assert (
        put(
            client, "harnesses", "A", {"invocation_surfaces": {"private-new-key": "private-secret"}}, expected_version=2
        ).status_code
        == 200
    )
    second = collect_harness_diagnostic(ReadClient(client), "A")
    assert "private-" not in json.dumps(second)
    assert first["harness"]["configuration_fingerprint"] == second["harness"]["configuration_fingerprint"]
    assert second["harness"]["configuration_fingerprint_scope"] == "canonical_installation_metadata_only"


@pytest.mark.parametrize("response", [None, {}, {"id": "other"}])
def test_malformed_harness_response_is_not_an_empty_successful_inventory(response):
    class Client:
        def request(self, *args, **kwargs):
            return response

    result = collect_harness_diagnostic(Client(), "A")
    assert result["errors"] == ["invalid_harness_response"] and result["status"] == "error"


@pytest.mark.parametrize(
    "binding",
    [
        None,
        {},
        {"native_context_id": "other", "role": "prime-builder"},
        {"native_context_id": "selected", "role": "loyal-opposition"},
    ],
)
def test_malformed_binding_never_supplies_role_or_correlation(binding):
    class Client:
        def request(self, method, path, **kwargs):
            return {"id": "A", "status": "active"} if path.startswith("/v1/harnesses/") else binding

    result = collect_harness_diagnostic(Client(), "A", native_context_id="selected")
    assert result["role"]["role"] is None and result["role"]["unavailable_reason"] == "invalid_session_response"
    assert result["correlation"]["session_id"] is None


def test_service_failure_has_no_private_body_and_does_not_fall_back():
    class Client:
        def request(self, *args, **kwargs):
            raise AuthorityClientError("authority_unavailable", "private-body", details={"secret": "private-value"})

    result = collect_harness_diagnostic(Client(), "A")
    assert result["status"] == "error" and result["errors"] == ["harness_authority_unavailable"]
    assert "private-" not in json.dumps(result)


def test_invalid_selected_configuration_returns_a_private_structured_error(tmp_path, monkeypatch):
    monkeypatch.delenv("GT_AUTHORITY_URL", raising=False)
    (tmp_path / "groundtruth.toml").write_text(
        '[groundtruth]\nauthority_url="http://private-credential@127.0.0.1:1"\n', encoding="utf-8"
    )
    result = diagnose_harness(tmp_path, "A")
    assert result["errors"] == ["native_authority_configuration_invalid"]
    assert "private-" not in json.dumps(result)


def test_explicit_root_does_not_discover_configuration_from_the_callers_directory(tmp_path, monkeypatch):
    monkeypatch.delenv("GT_AUTHORITY_URL", raising=False)
    other = tmp_path / "other"
    other.mkdir()
    (other / "groundtruth.toml").write_text('[groundtruth]\nauthority_url="http://127.0.0.1:1"\n', encoding="utf-8")
    selected = tmp_path / "selected"
    selected.mkdir()
    monkeypatch.chdir(other)
    result = diagnose_harness(selected, "A")
    assert result["errors"] == ["native_authority_not_configured"]
    assert list(selected.iterdir()) == []


def test_ordinary_cli_and_direct_adapter_read_the_same_native_authority(native, tmp_path, monkeypatch):
    service, client, *_ = native
    register(client)
    selected = bind(client, "cli-context", "pb")
    before = history_count(service)
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    process, env = _serve_authority(tmp_path, port)
    try:
        config = tmp_path / "groundtruth.toml"
        config.write_text(f'[groundtruth]\nauthority_url="http://127.0.0.1:{port}"\n', encoding="utf-8")
        foreign = tmp_path / "unrelated.bin"
        foreign.write_bytes(b"independent local work\x00")
        local_before = {path: path.read_bytes() for path in (config, foreign)}
        paths_before = {path.relative_to(tmp_path) for path in tmp_path.rglob("*") if path.is_file()}
        env = dict(env, PYTHONIOENCODING="utf-8")
        env.pop("GT_AUTHORITY_URL", None)

        def gt(identifier):
            return subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "groundtruth_kb",
                    "--config",
                    str(config),
                    "harness",
                    "diagnostic",
                    "--harness-id",
                    identifier,
                    "--native-context-id",
                    "cli-context",
                    "--json",
                ],
                cwd=tmp_path,
                env=env,
                capture_output=True,
                encoding="utf-8",
                timeout=30,
            )

        completed = gt("A")
        assert completed.returncode == 0, completed.stderr
        report = json.loads(completed.stdout)
        assert report["role"]["session_context_id"] == selected["session_context_id"]
        monkeypatch.delenv("GT_AUTHORITY_URL", raising=False)
        direct = diagnose_harness(tmp_path, "A", native_context_id="cli-context")
        for output in (report, direct):
            output.pop("generated_at")
        assert report == direct
        unknown = gt("missing")
        assert unknown.returncode == 1 and json.loads(unknown.stdout)["errors"] == ["harness_not_registered"]
        assert history_count(service) == before
        process.terminate()
        process.wait(timeout=15)
        offline = gt("A")
        assert offline.returncode == 1 and json.loads(offline.stdout)["errors"] == ["harness_authority_unavailable"]
        assert {path: path.read_bytes() for path in local_before} == local_before
        assert {path.relative_to(tmp_path) for path in tmp_path.rglob("*") if path.is_file()} == paths_before
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=15)
