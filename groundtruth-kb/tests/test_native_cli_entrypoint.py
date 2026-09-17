"""Cold native CLI loading must not import dormant legacy command machinery."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

import groundtruth_kb


def test_every_ordinary_command_help_loads_without_legacy_consumers(tmp_path):
    script = r"""
import importlib.abc
import json
import sys
from click.testing import CliRunner

retired = (
    "groundtruth_kb.cli_approval_packet", "groundtruth_kb.cli_session_handoff",
    "groundtruth_kb.cli_skills", "groundtruth_kb.cli_bridge_propose",
    "groundtruth_kb.activity.profiles", "groundtruth_kb.policy",
    "groundtruth_kb.owner_approval_surface", "groundtruth_kb.typed_artifact_flow",
    "groundtruth_kb.session.topic_router",
)
class RefuseLegacy(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if any(fullname == name or fullname.startswith(name + ".") for name in retired):
            raise AssertionError("Ordinary CLI imported a retired consumer: " + fullname)
        return None
sys.meta_path.insert(0, RefuseLegacy())
from groundtruth_kb.cli import main

runner = CliRunner()
results = []
def check(command, arguments):
    result = runner.invoke(main, [*arguments, "--help"])
    assert result.exit_code == 0, (arguments, result.output, result.exception)
    assert "Usage:" in result.output
    results.append(" ".join(arguments))
    if hasattr(command, "commands"):
        for name, child in command.commands.items():
            check(child, [*arguments, name])
for name, command in main._commands().items():
    check(command, [name])
assert "hygiene worktrees" in results
assert "application inspect" in results
assert "bridge check-effects" in results
assert "test-phases list" in results
assert "session bind" in results
assert not any(name in sys.modules for name in retired)
print(json.dumps(results))
"""
    env = dict(os.environ, PYTHONPATH=str(Path(groundtruth_kb.__file__).resolve().parent.parent))
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=tmp_path,
        env=env,
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=30,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    assert result.returncode == 0, result.stdout + result.stderr
    commands = json.loads(result.stdout)
    assert len(commands) == len(set(commands))
    assert not list(tmp_path.iterdir())


def _application_inspection_host(root, names=("First", "Second")):
    apps = root / "applications"
    apps.mkdir(parents=True)
    (apps / "registry.toml").write_text(
        "[applications]\n" + "".join(f'{name}={{slot="{name}"}}\n' for name in names), encoding="utf-8"
    )
    for name in names:
        app = apps / name
        app.mkdir()
        (app / "application.toml").write_text(f'[application]\nname="{name}"\n', encoding="utf-8")
        (app / ".gtkb-app-isolation.json").write_text(
            json.dumps(
                {
                    "schema_version": "2.0",
                    "application": name,
                    "top_level_artifacts": [
                        {
                            "name": filename,
                            "type": "FILE",
                            "classification": "authoritative_input",
                            "purpose": "Application-owned input.",
                        }
                        for filename in ("application.toml", ".gtkb-app-isolation.json")
                    ],
                }
            ),
            encoding="utf-8",
        )
    return root


def _run_application_inspection(arguments, cwd, sentinel):
    script = r"""
import json, os, sqlite3, sys
from pathlib import Path
import groundtruth_kb
import psycopg
from groundtruth_kb.authority_client import AuthorityClient
def deny_io(*args, **kwargs):
    raise AssertionError("Local application inspection attempted authority/database I/O")
sqlite3.connect = deny_io
psycopg.connect = deny_io
AuthorityClient.request = deny_io
from groundtruth_kb.cli import main
from click.testing import CliRunner
def audit(event, args):
    if event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)):
        if Path(os.fsdecode(args[0])).resolve() == Path(os.environ['GTKB_INSPECTION_SENTINEL']).resolve():
            raise AssertionError("Application inspection opened the database sentinel")
sys.addaudithook(audit)
result = CliRunner().invoke(main, json.loads(sys.argv[1]))
if result.exception and result.exit_code not in (0, 1, 2):
    raise result.exception
assert Path(groundtruth_kb.__file__).resolve().is_relative_to(Path(os.environ['GTKB_INSPECTION_PACKAGE']).resolve())
print(json.dumps({'exit':result.exit_code, 'stdout':result.output,
                  'exception_type':type(result.exception).__name__ if result.exception else None,
                  'origin':groundtruth_kb.__file__}))
"""
    package = Path(groundtruth_kb.__file__).resolve().parent.parent
    env = dict(
        os.environ,
        PYTHONPATH=str(package),
        PYTHONIOENCODING="utf-8",
        PYTHONDONTWRITEBYTECODE="1",
        GTKB_INSPECTION_SENTINEL=str(sentinel),
        GTKB_INSPECTION_PACKAGE=str(package),
        GT_DB_PATH=str(sentinel),
        GT_PROJECT_ROOT=str(cwd),
        GT_AUTHORITY_URL="http://127.0.0.1:1",
    )
    process = subprocess.run(
        [sys.executable, "-P", "-c", script, json.dumps(arguments)],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    assert process.returncode == 0, process.stdout + process.stderr
    payload = json.loads(process.stdout)
    assert payload["exception_type"] in (None, "SystemExit"), payload
    return payload


@pytest.mark.parametrize("json_output", [False, True])
def test_application_inspection_selects_explicit_host_offline_and_preserves_files(tmp_path, json_output):
    host = _application_inspection_host(tmp_path / "target host é")
    decoy = _application_inspection_host(tmp_path / "decoy", ("Decoy",))
    config = decoy / "groundtruth.toml"
    config.write_text('[groundtruth]\nproject_root="."\nauthority_url="http://127.0.0.1:1"\n', encoding="utf-8")
    sentinel = decoy / "groundtruth.db"
    sentinel.write_bytes(b"application inspection must not open this")
    before = {p.relative_to(tmp_path).as_posix(): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    args = ["--config", str(config), "application", "inspect", "--host-root", str(host)]
    if json_output:
        args.append("--json")
    result = _run_application_inspection(args, decoy, sentinel)
    assert result["exit"] == 0, result
    if json_output:
        data = json.loads(result["stdout"])
        assert data["verdicts"] == [] and set(data["slots_status"]) == {"First", "Second"}
    else:
        assert "passed for 2 applications" in result["stdout"]
        assert "Native lifecycle qualification is separate" in result["stdout"]
    assert "Decoy" not in result["stdout"]
    assert before == {p.relative_to(tmp_path).as_posix(): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}


@pytest.mark.parametrize("json_output", [False, True])
@pytest.mark.parametrize(
    "fault,expected",
    [
        ("catalog", "Application catalog invalid"),
        ("schema", "Malformed markers"),
        ("identity", "Mismatched markers"),
        ("artifact", "Application registry boundary"),
    ],
)
def test_application_inspection_returns_named_failures_and_nonzero_json(tmp_path, fault, expected, json_output):
    host = _application_inspection_host(tmp_path / "host")
    second = host / "applications/Second"
    if fault == "catalog":
        (host / "applications/registry.toml").write_text("invalid [", encoding="utf-8")
    elif fault in ("schema", "identity"):
        path = second / ".gtkb-app-isolation.json"
        row = json.loads(path.read_text(encoding="utf-8"))
        row["schema_version" if fault == "schema" else "application"] = "unsupported" if fault == "schema" else "Other"
        path.write_text(json.dumps(row), encoding="utf-8")
    else:
        (second / "unclassified.bin").write_bytes(b"private body should not be printed")
    sentinel = tmp_path / "unused.sqlite3"
    sentinel.write_bytes(b"not a database")
    before = {p.relative_to(tmp_path).as_posix(): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    args = ["application", "inspect", "--host-root", str(host)]
    if json_output:
        args.append("--json")
    result = _run_application_inspection(args, tmp_path, sentinel)
    assert result["exit"] == 1, result
    if json_output:
        assert any(v["verdict"] == expected for v in json.loads(result["stdout"])["verdicts"])
    else:
        assert expected in result["stdout"]
    assert "private body" not in result["stdout"]
    assert before == {p.relative_to(tmp_path).as_posix(): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}


def test_application_inspection_missing_host_and_empty_host_are_distinct(tmp_path):
    sentinel = tmp_path / "unused.sqlite3"
    sentinel.write_bytes(b"not a database")
    missing = _run_application_inspection(["application", "inspect"], tmp_path, sentinel)
    assert missing["exit"] == 2 and "--host-root" in missing["stdout"]
    absent = _run_application_inspection(
        ["application", "inspect", "--host-root", str(tmp_path / "absent")], tmp_path, sentinel
    )
    assert absent["exit"] == 2 and "does not exist" in absent["stdout"]
    empty = tmp_path / "empty"
    empty.mkdir()
    result = _run_application_inspection(["application", "inspect", "--host-root", str(empty)], tmp_path, sentinel)
    assert result["exit"] == 0 and "no application qualification performed" in result["stdout"]
    assert not list(empty.iterdir())


def test_application_registration_requires_an_explicit_host_and_opens_no_store(tmp_path):
    """The native registration route never defaults to the working directory and never touches a database."""
    sentinel = tmp_path / "unused.sqlite3"
    sentinel.write_bytes(b"not a database")
    result = _run_application_inspection(["application", "register", "Example"], tmp_path, sentinel)
    assert result["exit"] == 2 and "Missing option '--host-root'" in result["stdout"]
    assert not (tmp_path / "applications").exists()
    described = _run_application_inspection(["application", "register", "--help"], tmp_path, sentinel)
    assert described["exit"] == 0 and "--host-root" in described["stdout"]
    assert "sqlite" not in described["stdout"].lower() and "database" not in described["stdout"].lower()


def _native_response_process(tmp_path, raw, arguments, expected_requests=None):
    """Exercise actual HTTP decoding and the cold ordinary CLI without DB access."""
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    from threading import Thread

    requests = []

    class ResponseHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            requests.append(self.path)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            requests.append(("POST", self.path, body))
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def log_message(self, *_arguments):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), ResponseHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    config = tmp_path / "groundtruth.toml"
    config.write_text(
        f'[groundtruth]\nproject_root="."\nauthority_url="http://127.0.0.1:{server.server_port}"\n',
        encoding="utf-8",
    )
    sentinel = tmp_path / "groundtruth.db"
    sentinel.write_bytes(b"No database access belongs in this HTTP client")
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir() if p.is_file()}
    script = r"""
import json, sqlite3, sys
import psycopg
from click.testing import CliRunner

def deny_database(*args, **kwargs):
    raise AssertionError("The ordinary native CLI attempted direct database access")
sqlite3.connect = deny_database
sqlite3.dbapi2.connect = deny_database
psycopg.connect = deny_database
from groundtruth_kb.cli import main
result = CliRunner().invoke(main, json.loads(sys.argv[1]))
print(json.dumps({"exit":result.exit_code,"output":result.output,
                  "exception":type(result.exception).__name__ if result.exception else None}))
"""
    package = Path(groundtruth_kb.__file__).resolve().parent.parent
    env = dict(os.environ, PYTHONPATH=str(package), PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    for key in list(env):
        if key in ("GT_AUTHORITY_URL", "GT_PROJECT_ROOT", "GTKB_PROJECT_ROOT", "GT_DB_PATH") or key.startswith(
            ("PG", "GT_POSTGRES_")
        ):
            env.pop(key)
    try:
        process = subprocess.run(
            [sys.executable, "-P", "-c", script, json.dumps(["--config", str(config), *arguments])],
            cwd=tmp_path,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(10)
    assert not thread.is_alive()
    assert process.returncode == 0, process.stdout + process.stderr
    assert requests == (["/v1/projects/PROJECT-OUTPUT"] if expected_requests is None else expected_requests)
    assert before == {p.name: p.read_bytes() for p in tmp_path.iterdir() if p.is_file()}
    assert not any(p.is_dir() for p in tmp_path.iterdir())
    return json.loads(process.stdout)


@pytest.mark.parametrize("json_output", [False, True])
@pytest.mark.parametrize(
    "body",
    [
        "null",
        "false",
        '"ordinary response"',
        "{}",
        '{"project":null,"observed":0.12345678901234567890123456789,"label":"é"}',
        '{"work_item":null,"count":123456789012345678901234567890}',
        '{"project":"unavailable","reason":"No record was returned"}',
        '{"work_item":["WI-1","WI-2"]}',
        '{"dependent_project_id":"PROJECT-1","ready":false}',
        '[{"project":null},false,"unchanged"]',
        '{"project":null,"work_item":{"id":"WI-1","title":"Preserve the whole response"}}',
    ],
)
def test_native_cli_preserves_nonrecord_response_payloads(tmp_path, body, json_output):
    from decimal import Decimal

    arguments = ["projects", "show", "PROJECT-OUTPUT"]
    if json_output:
        arguments.append("--json")
    result = _native_response_process(tmp_path, body.encode("utf-8"), arguments)
    assert result["exit"] == 0 and result["exception"] is None, result
    decoder = json.JSONDecoder(parse_float=Decimal)
    output = result["output"].lstrip()
    emitted = []
    while output:
        value, end = decoder.raw_decode(output)
        emitted.append(value)
        output = output[end:].lstrip()
    expected = json.loads(body, parse_float=Decimal)
    assert emitted == (expected if isinstance(expected, list) and not json_output else [expected])


@pytest.mark.parametrize("wrapper", [None, "project", "work_item"])
def test_native_cli_keeps_complete_record_output(tmp_path, wrapper):
    record = {
        "id": "PROJECT-OUTPUT",
        "version": 3,
        "title": "Readable current record",
        "description": "The selected authority supplied this record.",
        "authorization": "authorized",
        "parent_project_id": None,
    }
    body = record if wrapper is None else {wrapper: record, "related": ["kept"]}
    result = _native_response_process(
        tmp_path, json.dumps(body).encode("utf-8"), ["projects", "show", "PROJECT-OUTPUT"]
    )
    assert result["exit"] == 0 and result["exception"] is None, result
    assert "PROJECT-OUTPUT v3: Readable current record" in result["output"]
    assert record["description"] in result["output"]
    assert 'authorization: "authorized"' in result["output"]
    assert "parent_project_id: null" in result["output"]
    if wrapper:
        assert 'related: ["kept"]' in result["output"]


@pytest.mark.parametrize(
    "operation,state,expected_exit",
    [
        ("prepare-commit", "ready_to_commit", 0),
        ("prepare-commit", "fresh_verification_required", 1),
        ("check-commit", "ready_to_update_reference", 0),
        ("confirm-commit", "confirmed", 0),
        ("commit-failed", "fresh_verification_required", 0),
    ],
)
def test_native_cli_finalization_keeps_context_fields_and_review_exit_status(tmp_path, operation, state, expected_exit):
    arguments = [
        "projects",
        operation,
        "PROJECT-OUTPUT",
        "--native-context-id",
        "fresh-cli-context",
        "--expected-version",
        "7",
        "--json",
    ]
    expected = {"native_context_id": "fresh-cli-context", "expected_version": 7}
    if operation in ("check-commit", "confirm-commit"):
        arguments += ["--commit-id", "a" * 40, "--expected-parent", "b" * 40]
        expected.update(commit_id="a" * 40, expected_parent="b" * 40)
    if operation == "check-commit":
        arguments += ["--index-tree", "c" * 40]
        expected["index_tree"] = "c" * 40
    if operation == "commit-failed":
        arguments += ["--reason", "commit_not_confirmed", "--evidence", "The normal hook refused"]
        expected.update(reason="commit_not_confirmed", evidence="The normal hook refused")
    response = {"status": state, "project_id": "PROJECT-OUTPUT"}
    result = _native_response_process(
        tmp_path,
        json.dumps(response).encode("utf-8"),
        arguments,
        expected_requests=[("POST", f"/v1/projects/PROJECT-OUTPUT/{operation}", expected)],
    )
    assert result["exit"] == expected_exit, result
    assert result["exception"] == ("SystemExit" if expected_exit else None), result
    assert json.loads(result["output"]) == response


def _run_config_report(arguments, cwd, protected_paths, overrides=None):
    """Invoke a cold process with all database/network effects refused."""
    script = r"""
import builtins, json, os, socket, sqlite3, sys
from pathlib import Path
import psycopg

def deny_io(*args, **kwargs):
    raise AssertionError("Configuration display attempted database or network I/O")
sqlite3.connect = deny_io
sqlite3.dbapi2.connect = deny_io
psycopg.connect = deny_io
socket.socket.connect = deny_io
socket.socket.connect_ex = deny_io
real_import = builtins.__import__
def guarded_import(name, *args, **kwargs):
    if name == "chromadb" or name.startswith("chromadb."):
        raise AssertionError("Configuration display imported Chroma")
    return real_import(name, *args, **kwargs)
builtins.__import__ = guarded_import
protected = {Path(p).resolve() for p in json.loads(sys.argv[2])}
def audit(event, args):
    if event == "open" and isinstance(args[0], (str, bytes, os.PathLike)):
        if Path(os.fsdecode(args[0])).resolve() in protected:
            raise AssertionError("Configuration display opened a database or credential file")
sys.addaudithook(audit)
from click.testing import CliRunner
import groundtruth_kb
from groundtruth_kb.cli import main
result = CliRunner().invoke(main, json.loads(sys.argv[1]))
if result.exception and not isinstance(result.exception, SystemExit):
    raise result.exception
assert "chromadb" not in sys.modules
print(json.dumps({"exit":result.exit_code, "stdout":result.stdout, "stderr":result.stderr,
                  "origin":groundtruth_kb.__file__}))
"""
    package = Path(groundtruth_kb.__file__).resolve().parent.parent
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(("GT_", "PG")) and key not in ("PYTHONPATH", "GTKB_PROJECT_ROOT")
    }
    env.update(
        PYTHONPATH=str(package),
        PYTHONIOENCODING="utf-8",
        PYTHONDONTWRITEBYTECODE="1",
        PGPASSWORD="config-report-dummy-password",
        PGSERVICEFILE=str(protected_paths[-1]),
        PGPASSFILE=str(protected_paths[-1]),
        GT_LOGO_URL="https://example.invalid/config-report-dummy-logo-token",
        **(overrides or {}),
    )
    result = subprocess.run(
        [sys.executable, "-P", "-c", script, json.dumps(arguments), json.dumps([str(p) for p in protected_paths])],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert Path(payload["origin"]).resolve().is_relative_to(package)
    assert "config-report-dummy-password" not in result.stdout + result.stderr
    assert "config-report-dummy-logo-token" not in result.stdout + result.stderr
    return payload


def _config_input_snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() if p.is_file() else None for p in root.rglob("*")}


@pytest.mark.parametrize("json_output", [False, True], ids=["text", "json"])
@pytest.mark.parametrize("scenario", ["explicit", "defaults", "environment", "discovery", "no-file"])
def test_native_config_report_resolves_selected_settings_without_probes(tmp_path, json_output, scenario):
    selected = tmp_path / "selected"
    caller = tmp_path / "caller"
    selected.mkdir()
    caller.mkdir()
    credentials = tmp_path / "credential-sentinel"
    credentials.write_bytes(b"config-report-dummy-file-secret")
    db_path = selected / "groundtruth.db"
    db_path.write_bytes(b"legacy database sentinel; never open")
    config_path = selected / "groundtruth.toml"
    config_path.write_text("[groundtruth]\n", encoding="utf-8")
    (caller / "groundtruth.toml").write_text('[groundtruth]\napp_title="Wrong caller"\n', encoding="utf-8")
    arguments = ["--config", str(config_path)]
    overrides = {}
    expected = {
        "app_title": "GroundTruth KB",
        "project_root": str(selected.resolve()),
        "authority_url": None,
        "postgresql": {
            "service": "gtkb",
            "connect_timeout_seconds": 10,
            "lock_timeout_ms": 5000,
            "statement_timeout_ms": 30000,
        },
        "legacy_paths": {"db_path": str(db_path.resolve()), "chroma_path": None},
    }
    if scenario in ("explicit", "environment"):
        config_path.write_text(
            '[groundtruth]\napp_title="Selected café"\nproject_root="./project"\n'
            'db_path="./groundtruth.db"\nauthority_url="http://127.0.0.1:1"\n'
            '[search]\nchroma_path="./cache/chroma"\n'
            '[postgresql]\nservice="selected_native"\nconnect_timeout_seconds=7\n'
            "lock_timeout_ms=1234\nstatement_timeout_ms=2345\n",
            encoding="utf-8",
        )
        expected.update(
            app_title="Selected café",
            project_root=str((selected / "project").resolve()),
            authority_url="http://127.0.0.1:1",
            postgresql={
                "service": "selected_native",
                "connect_timeout_seconds": 7,
                "lock_timeout_ms": 1234,
                "statement_timeout_ms": 2345,
            },
        )
        expected["legacy_paths"]["chroma_path"] = str((selected / "cache/chroma").resolve())
    if scenario == "environment":
        overrides = {
            "GT_APP_TITLE": "Environment title",
            "GT_PROJECT_ROOT": "./from-env",
            "GT_AUTHORITY_URL": "http://127.0.0.1:2",
            "GT_POSTGRES_SERVICE": "env_native",
            "GT_POSTGRES_CONNECT_TIMEOUT_SECONDS": "9",
            "GT_DB_PATH": "./env.db",
        }
        expected.update(
            app_title="Environment title",
            project_root=str((selected / "from-env").resolve()),
            authority_url="http://127.0.0.1:2",
        )
        expected["postgresql"].update(service="env_native", connect_timeout_seconds=9)
        expected["legacy_paths"]["db_path"] = str((selected / "env.db").resolve())
    if scenario == "discovery":
        caller = selected / "nested"
        caller.mkdir()
        arguments = []
    if scenario == "no-file":
        (caller / "groundtruth.toml").unlink()
        arguments = []
        expected["project_root"] = str(caller.resolve())
        expected["legacy_paths"]["db_path"] = str((caller / "groundtruth.db").resolve())
    arguments += ["config"] + (["--json"] if json_output else [])
    before = _config_input_snapshot(tmp_path)
    result = _run_config_report(
        arguments, caller, [db_path, Path(expected["legacy_paths"]["db_path"]), credentials], overrides
    )
    assert result["exit"] == 0, result
    assert result["stderr"] == ""
    if json_output:
        assert json.loads(result["stdout"]) == expected
    else:
        expected_lines = [
            f"Application title: {expected['app_title']}",
            f"Project root: {expected['project_root']}",
            f"Authority URL: {expected['authority_url'] or '(missing; configure before knowledge operations)'}",
            f"PostgreSQL service: {expected['postgresql']['service']}",
            f"PostgreSQL connect timeout (seconds): {expected['postgresql']['connect_timeout_seconds']}",
            f"PostgreSQL lock timeout (ms): {expected['postgresql']['lock_timeout_ms']}",
            f"PostgreSQL statement timeout (ms): {expected['postgresql']['statement_timeout_ms']}",
            f"Legacy helper db_path: {expected['legacy_paths']['db_path']}",
            f"Legacy helper chroma_path: {expected['legacy_paths']['chroma_path'] or 'unset'}",
        ]
        assert result["stdout"].splitlines() == expected_lines
    assert _config_input_snapshot(tmp_path) == before


@pytest.mark.parametrize("json_output", [False, True], ids=["text", "json"])
@pytest.mark.parametrize(
    ("invalid", "message", "exit_code"),
    [
        ('[groundtruth]\nauthority_url="https://example.invalid"\n', "authority_url", 1),
        ("[groundtruth]\n[postgresql]\nconnect_timeout_seconds=0\n", "positive integer", 1),
        ("[groundtruth\n", "Invalid TOML", 1),
        (None, "does not exist", 2),
        ("directory", "not a regular file", 1),
    ],
    ids=["remote-authority", "zero-timeout", "invalid-toml", "missing-file", "directory"],
)
def test_native_config_report_refuses_invalid_settings(tmp_path, json_output, invalid, message, exit_code):
    config_path = tmp_path / "groundtruth.toml"
    if invalid == "directory":
        config_path.mkdir()
    elif invalid is not None:
        config_path.write_text(invalid, encoding="utf-8")
    sentinel = tmp_path / "credential-sentinel"
    sentinel.write_bytes(b"config-report-dummy-file-secret")
    before = _config_input_snapshot(tmp_path)
    result = _run_config_report(
        ["--config", str(config_path), "config"] + (["--json"] if json_output else []),
        tmp_path,
        [tmp_path / "groundtruth.db", sentinel],
    )
    assert result["exit"] == exit_code, result
    assert result["stdout"] == ""
    assert message in result["stderr"]
    assert _config_input_snapshot(tmp_path) == before
