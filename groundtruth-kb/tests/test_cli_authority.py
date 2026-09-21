"""Ordinary authority/terminology CLI reads one native source and refuses fallback."""

from __future__ import annotations

import json
import subprocess

import pytest
from click.testing import CliRunner

from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError
from groundtruth_kb.cli import main


@pytest.fixture
def configured(tmp_path, monkeypatch):
    monkeypatch.delenv("GT_AUTHORITY_URL", raising=False)
    config = tmp_path / "groundtruth.toml"
    config.write_text('[groundtruth]\nauthority_url="http://127.0.0.1:12345"\nproject_root="."\n', encoding="utf-8")
    sentinel = tmp_path / "groundtruth.db"
    sentinel.write_bytes(b"SQLite is not a fallback")
    old_map = tmp_path / "config/agent-control/system-interface-map.toml"
    old_map.parent.mkdir(parents=True)
    old_map.write_text("must not be loaded", encoding="utf-8")
    calls = []
    record = {
        "id": "PROJECT",
        "version": 2,
        "canonical_term": "project",
        "definition": "A complete usable result.",
        "scope": "platform",
        "lifecycle_status": "active",
        "source_authority": "ADR-PROJECT",
    }

    def request(self, method, path, **kwargs):
        calls.append((method, path, kwargs))
        if path.endswith("/resolve"):
            return {"status": "resolved", "message": "Current term resolved.", "record": record}
        if path.endswith("/status"):
            return {"status": "pass", "records": 1, "active_records": 1, "source_issues": []}
        if path == "/v1/terms":
            return {"records": [record], "next_after": None}
        return record

    monkeypatch.setattr(AuthorityClient, "request", request)
    yield config, calls, record
    assert sentinel.read_bytes() == b"SQLite is not a fallback"
    assert old_map.read_text(encoding="utf-8") == "must not be loaded"


def invoke(config, *args):
    return CliRunner().invoke(main, ["--config", str(config), *args])


@pytest.mark.parametrize("command,domain", [("spec", "specifications"), ("tests", "tests")])
def test_native_scope_filter_uses_exact_catalog_reference(configured, monkeypatch, command, domain):
    config, calls, _record = configured

    def request(self, method, path, **kwargs):
        calls.append((method, path, kwargs))
        return {"records": [], "next_after": None}

    monkeypatch.setattr(AuthorityClient, "request", request)
    result = invoke(config, command, "list", "--application-scope", "application:Beta", "--json")
    assert result.exit_code == 0, result.output
    assert calls[-1][0:2] == ("GET", f"/v1/{domain}")
    assert calls[-1][2]["query"]["application_scope"] == "application:Beta"
    assert json.loads(result.output) == []


def test_authority_resolves_current_record_through_native_service(configured):
    config, calls, record = configured
    result = invoke(config, "authority", "resolve", "work group", "--scope", "platform", "--json")
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["record"] == record
    assert calls == [("GET", "/v1/authority/resolve", {"query": {"subject": "work group", "scope": "platform"}})]
    human = invoke(config, "authority", "resolve", "project")
    assert "PROJECT v2: project" in human.output and record["definition"] in human.output
    assert "ADR-PROJECT" in human.output


@pytest.mark.parametrize("status", ["not_found", "ambiguous"])
def test_unresolved_authority_is_nonzero(configured, monkeypatch, status):
    config, _, _ = configured
    monkeypatch.setattr(AuthorityClient, "request", lambda *a, **kw: {"status": status, "candidates": ["project"]})
    result = invoke(config, "authority", "resolve", "bridge index", "--json")
    assert result.exit_code == 1
    assert json.loads(result.output)["status"] == status


def test_unavailable_authority_never_reads_legacy_map_or_sqlite(configured, monkeypatch):
    config, _, _ = configured

    def unavailable(*args, **kwargs):
        raise AuthorityClientError("authority_unavailable", "Unavailable fixture authority")

    monkeypatch.setattr(AuthorityClient, "request", unavailable)
    result = invoke(config, "authority", "resolve", "project", "--json")
    assert result.exit_code == 1 and "authority_unavailable" in result.output
    assert "complete usable result" not in result.output


def test_authority_requires_configured_service_even_when_legacy_map_exists(configured):
    config, calls, _ = configured
    config.write_text('[groundtruth]\nproject_root="."\n', encoding="utf-8")
    result = invoke(config, "authority", "resolve", "project", "--json")
    assert result.exit_code == 1 and "No authority_url is configured" in result.output
    assert not calls


def test_terms_list_and_show_use_the_same_domain_with_visible_definitions(configured):
    config, calls, record = configured
    result = invoke(
        config,
        "terms",
        "list",
        "--status",
        "active",
        "--scope",
        "platform",
        "--authority-level",
        "platform_core",
        "--search",
        "project",
        "--limit",
        "1",
    )
    assert result.exit_code == 0, result.output
    assert record["definition"] in result.output and "PROJECT v2: project" in result.output
    method, path, kwargs = calls[-1]
    assert (method, path) == ("GET", "/v1/terms")
    assert {k: v for k, v in kwargs["query"].items() if v is not None} == {
        "scope": "platform",
        "authority_level": "platform_core",
        "search": "project",
        "lifecycle_status": "active",
        "limit": 1,
    }
    result = invoke(config, "terms", "show", "PROJECT", "--json")
    assert result.exit_code == 0 and json.loads(result.output) == record
    assert calls[-1][1] == "/v1/terms/PROJECT"


@pytest.mark.parametrize("status,exit_code", [("pass", 0), ("fail", 1)])
def test_authority_status_reports_current_corpus_result(configured, monkeypatch, status, exit_code):
    config, calls, _ = configured
    report = {"status": status, "source": "canonical_terms", "active_records": 1, "records": 1}
    monkeypatch.setattr(AuthorityClient, "request", lambda *a, **kw: report)
    result = invoke(config, "authority", "status", "--scope", "platform", "--json")
    assert result.exit_code == exit_code and json.loads(result.output) == report


@pytest.mark.parametrize("domain", ["spec", "tests", "projects", "backlog", "terms", "test-plans", "test-phases"])
def test_missing_authority_url_never_reactivates_sqlite_commands(configured, monkeypatch, domain):
    config, calls, _ = configured
    config.write_text('[groundtruth]\nproject_root="."\n', encoding="utf-8")

    def forbidden(*args, **kwargs):
        pytest.fail("Ordinary knowledge commands must never open SQLite")

    monkeypatch.setattr("sqlite3.connect", forbidden)
    result = invoke(config, domain, "list", "--json")
    assert result.exit_code == 1 and "No authority_url is configured" in result.output
    assert not calls


def test_lost_environment_authority_refuses_mutation_before_opening_legacy_database(configured, monkeypatch):
    config, calls, _ = configured
    config.write_text('[groundtruth]\nproject_root="."\n', encoding="utf-8")
    fields = config.parent / "spec.json"
    fields.write_text('{"title":"Must not land","status":"active"}', encoding="utf-8")
    monkeypatch.setenv("GT_AUTHORITY_URL", "http://127.0.0.1:12345")
    assert invoke(config, "authority", "resolve", "project", "--json").exit_code == 0
    calls.clear()
    monkeypatch.delenv("GT_AUTHORITY_URL")
    result = invoke(
        config,
        "spec",
        "record",
        "--id",
        "SPEC-NEW",
        "--fields-file",
        str(fields),
        "--expected-version",
        "0",
        "--actor",
        "qualification",
        "--change-reason",
        "Missing authority test",
        "--json",
    )
    assert result.exit_code == 1 and "No authority_url is configured" in result.output
    assert not calls


@pytest.mark.parametrize("with_authority", [False, True])
def test_local_secret_scan_and_configuration_remain_usable_without_authority_io(
    configured, monkeypatch, with_authority
):
    config, calls, _ = configured
    if not with_authority:
        config.write_text('[groundtruth]\nproject_root="."\n', encoding="utf-8")
    monkeypatch.chdir(config.parent)
    subprocess.run(["git", "init", "-q"], check=True, capture_output=True)
    (config.parent / "plain.txt").write_text("A harmless local work product.\n", encoding="utf-8")
    result = invoke(config, "secrets", "scan", "--paths", "--redacted", "--json", "plain.txt")
    assert result.exit_code == 0, result.output
    assert not json.loads(result.output)["findings"]
    result = invoke(config, "config")
    assert result.exit_code == 0 and "Authority URL:" in result.output
    assert "runtime fallback" not in result.output
    assert invoke(config, "hygiene", "worktrees", "--help").exit_code == 0
    assert not calls


def test_help_and_unknown_commands_do_not_select_a_database(configured):
    config, calls, _ = configured
    config.write_text('[groundtruth]\nproject_root="."\n', encoding="utf-8")
    help_result = invoke(config, "--help")
    assert help_result.exit_code == 0 and "secrets" in help_result.output and "service" in help_result.output
    retired = invoke(config, "seed")
    assert retired.exit_code == 1 and "SQLite fallback is disabled" in retired.output
    assert invoke(config, "db", "postgres", "--help").exit_code == 0
    assert invoke(config, "db", "snapshot", "--help").exit_code != 0
    assert not calls


@pytest.mark.parametrize("command", ["iac", "cicd"])
@pytest.mark.parametrize("with_authority", [False, True])
def test_file_scaffolds_work_offline_and_preserve_adopter_changes(configured, monkeypatch, command, with_authority):
    config, calls, _ = configured
    if not with_authority:
        config.write_text('[groundtruth]\nproject_root="."\n', encoding="utf-8")
    monkeypatch.chdir(config.parent)

    def reject_database(*args, **kwargs):
        pytest.fail("File scaffolding must not open a database")

    monkeypatch.setattr("sqlite3.connect", reject_database)
    monkeypatch.setattr("groundtruth_kb.postgres_kernel.PostgresKernel._connect", reject_database)
    target = config.parent / "scaffold-target"
    args = ("scaffold", command, "--target-dir", str(target))
    dry = invoke(config, *args)
    assert dry.exit_code == 0 and "DRY RUN" in dry.output, dry.output
    assert not target.exists()
    applied = invoke(config, *args, "--apply")
    assert applied.exit_code == 0 and "APPLIED" in applied.output, applied.output
    files = sorted(path for path in target.rglob("*") if path.is_file())
    assert len(files) == (45 if command == "iac" else 12)
    files[0].write_bytes(b"Adopter changes must survive.\n")
    before = {path: path.read_bytes() for path in files}
    repeated = invoke(config, *args, "--apply")
    assert repeated.exit_code == 0, repeated.output
    assert {path: path.read_bytes() for path in target.rglob("*") if path.is_file()} == before
    assert not calls


def test_file_scaffold_route_does_not_expose_legacy_database_writers(configured, monkeypatch):
    """The retired ADR scaffold has no route; starter specifications go through the native authority only."""
    config, calls, _ = configured

    def reject_database(*args, **kwargs):
        pytest.fail("Retired database scaffold must not open SQLite")

    monkeypatch.setattr("sqlite3.connect", reject_database)
    help_result = invoke(config, "scaffold", "--help")
    assert help_result.exit_code == 0 and "iac" in help_result.output and "cicd" in help_result.output
    assert "adrs" not in help_result.output and "specs" in help_result.output
    rejected = invoke(config, "scaffold", "adrs", "--apply")
    assert rejected.exit_code != 0 and "No such command" in rejected.output
    assert not calls
    specs_help = invoke(config, "scaffold", "specs", "--help")
    assert specs_help.exit_code == 0 and "--project-id" in specs_help.output and "--apply" in specs_help.output
    assert "sqlite" not in specs_help.output.lower() and "database" not in specs_help.output.lower()


@pytest.mark.parametrize("status,exit_code", [("removed", 0), ("absent", 0), ("partial", 1)])
def test_session_scratch_teardown_posts_the_bound_context_and_exits_nonzero_on_partial(
    configured, monkeypatch, status, exit_code
):
    config, calls, _record = configured
    report = {
        "status": status,
        "session_context_id": "SENV-1",
        "scratch_directory": "scratchpad/SENV-1",
        "removed": [],
        "surviving": [{"path": "held.log", "kind": "file", "reason": "PermissionError"}] if status == "partial" else [],
    }
    monkeypatch.setattr(AuthorityClient, "request", lambda self, method, path, **kwargs: report)
    result = invoke(config, "session", "scratch-teardown", "--native-context-id", "ctx-1", "--json")
    assert result.exit_code == exit_code, result.output
    assert json.loads(result.output) == report
    assert calls == []
    calls_seen = []

    def capture(self, method, path, **kwargs):
        calls_seen.append((method, path, kwargs))
        return report

    monkeypatch.setattr(AuthorityClient, "request", capture)
    assert invoke(config, "session", "scratch-teardown", "--native-context-id", "ctx-1").exit_code == exit_code
    assert calls_seen == [("POST", "/v1/sessions/scratch-teardown", {"body": {"native_context_id": "ctx-1"}})]
    assert invoke(config, "session", "scratch-teardown").exit_code == 2


def test_harness_metadata_cli_uses_native_reads_and_has_no_role_mutator(configured, monkeypatch):
    config, calls, _ = configured
    records = [{"id": "H", "harness_name": "installation", "status": "active"}]

    def request(self, method, path, **kwargs):
        calls.append((method, path, kwargs))
        return {"records": records, "next_after": None} if path == "/v1/harnesses" else records[0]

    monkeypatch.setattr(AuthorityClient, "request", request)
    result = invoke(config, "harness", "list", "--status", "active", "--json")
    assert result.exit_code == 0 and json.loads(result.output) == records, result.output
    result = invoke(config, "harness", "show", "H", "--json")
    assert result.exit_code == 0 and json.loads(result.output) == records[0], result.output
    assert [(method, path) for method, path, _ in calls] == [("GET", "/v1/harnesses"), ("GET", "/v1/harnesses/H")]
    assert calls[0][2]["query"]["status"] == "active"
    for command in ("set-role", "register", "record"):
        assert invoke(config, "harness", command).exit_code != 0
    assert len(calls) == 2
    assert invoke(config, "harness", "project", "--help").exit_code == 0


@pytest.mark.parametrize(
    "payload",
    [
        None,
        [],
        "private-text",
        {"error": None},
        {"error": []},
        {"error": False},
        {"error": "private-nested-text"},
        {"error": {"code": []}},
        {"error": {"message": {"private": "body"}}},
        {"code": 42},
        {"message": False},
    ],
)
def test_native_client_malformed_http_error_is_typed_and_not_retried(tmp_path, payload):
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    from threading import Thread

    requests = []
    sentinel = tmp_path / "groundtruth.db"
    sentinel.write_bytes(b"never fall back or write locally")

    class Handler(BaseHTTPRequestHandler):
        def do_PUT(self):
            requests.append((self.path, self.rfile.read(int(self.headers["Content-Length"]))))
            body = json.dumps(payload).encode("utf-8")
            self.send_response(422)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        client = AuthorityClient(f"http://127.0.0.1:{server.server_port}", timeout=2)
        with pytest.raises(AuthorityClientError) as caught:
            client.request("PUT", "/v1/projects/PROJECT-1", body={"intent": "preserve"})
        assert caught.value.code == "authority_error"
        assert str(caught.value) == "Authority returned HTTP 422"
        assert caught.value.details is None
        assert len(requests) == 1
        assert requests[0][0] == "/v1/projects/PROJECT-1"
        assert json.loads(requests[0][1]) == {"intent": "preserve"}
        assert sentinel.read_bytes() == b"never fall back or write locally"
        assert list(tmp_path.iterdir()) == [sentinel]
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()
    assert not thread.is_alive()


@pytest.mark.parametrize("nested", [False, True])
def test_native_client_preserves_valid_error_fields_and_context(monkeypatch, nested):
    from io import BytesIO
    from urllib.error import HTTPError

    result = {"code": "cas_conflict", "message": "Read current state", "details": {"actual": 7}}
    payload = {"error": result} if nested else result
    client = AuthorityClient("http://127.0.0.1:12345")
    calls = []

    def refused(request, *, timeout):
        calls.append(request)
        raise HTTPError(request.full_url, 409, "Conflict", {}, BytesIO(json.dumps(payload).encode()))

    monkeypatch.setattr(client._opener, "open", refused)
    with pytest.raises(AuthorityClientError) as caught:
        client.request("PUT", "/v1/projects/PROJECT-1", body={"expected_version": 6})
    assert caught.value.code == result["code"]
    assert str(caught.value) == result["message"]
    assert caught.value.details == result["details"]
    assert len(calls) == 1


@pytest.mark.parametrize("status", [301, 302, 303, 307, 308])
def test_native_client_does_not_follow_redirects_or_replay_write_body(status):
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    from threading import Thread

    calls = []

    class Handler(BaseHTTPRequestHandler):
        def do_PUT(self):
            self.rfile.read(int(self.headers.get("Content-Length", "0")))
            calls.append((self.command, self.path))
            self.send_response(status)
            self.send_header("Location", f"http://127.0.0.1:{self.server.server_port}/destination")
            self.send_header("Content-Length", "0")
            self.end_headers()

        def do_GET(self):
            calls.append((self.command, self.path))
            self.send_response(200)
            self.send_header("Content-Length", "2")
            self.end_headers()
            self.wfile.write(b"{}")

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        client = AuthorityClient(f"http://127.0.0.1:{server.server_port}", timeout=2)
        with pytest.raises(AuthorityClientError) as caught:
            client.request("PUT", "/v1/projects/PROJECT-1", body={"private": "write intent"})
        assert caught.value.code == "authority_error"
        assert str(caught.value) == f"Authority returned HTTP {status}"
        assert calls == [("PUT", "/v1/projects/PROJECT-1")]
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()
    assert not thread.is_alive()


def test_formal_links_list_passes_artifact_type_to_the_native_service(configured, monkeypatch):
    config, calls, _record = configured

    def request(self, method, path, **kwargs):
        calls.append((method, path, kwargs))
        return {"records": [], "next_after": None}

    monkeypatch.setattr(AuthorityClient, "request", request)
    result = invoke(
        config, "projects", "formal-links", "list", "--project-id", "P", "--artifact-type", "bridge_thread", "--json"
    )
    assert result.exit_code == 0, result.output
    assert calls[-1][0:2] == ("GET", "/v1/project-formal-links")
    assert calls[-1][2]["query"]["project_id"] == "P" and calls[-1][2]["query"]["artifact_type"] == "bridge_thread"
    assert json.loads(result.output) == []
    plain = invoke(config, "projects", "formal-links", "list", "--json")
    assert plain.exit_code == 0 and calls[-1][2]["query"]["artifact_type"] is None
    assert invoke(config, "projects", "formal-links", "list", "--artifact-type", "git_commit").exit_code == 2
    assert len(calls) == 2
    # The option is visible on formal-links only; other domains keep it hidden and the service refuses it.
    assert "--artifact-type" in invoke(config, "projects", "formal-links", "list", "--help").output
    assert "--artifact-type" not in invoke(config, "spec", "list", "--help").output
