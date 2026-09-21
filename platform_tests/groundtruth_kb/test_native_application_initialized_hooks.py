"""Applications initialized by the native scaffold commit through their installed hook and emitted harness hooks.

Two applications on two differently located host roots are initialized with
``gt project init``, receive their reference-transaction hook and projected
harness registrations from the host baseline, and then run the ordinary
bridge lifecycle: a fresh proposal context, an independent reviewer, a
successor implementation context in its registered worktree, independent
verification and the complete project commit through the ordinary CLI. The
emitted native effect gate is executed with real hook payloads, and the
installed reference-transaction hook is observed performing the authority
callback. Presence checks and rendered bytes alone prove nothing here.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path
from uuid import uuid4

import groundtruth_kb
import pytest
import uvicorn
from groundtruth_kb.authority_api import create_authority_app
from groundtruth_kb.authority_client import AuthorityClient
from groundtruth_kb.postgres_kernel import TABLE_SPECS
from groundtruth_kb.project.native_finalization import NativeProjectFinalization

from platform_tests.groundtruth_kb.bridge_fixtures import authored
from platform_tests.groundtruth_kb.native_fixtures import native as native
from platform_tests.groundtruth_kb.native_fixtures import put, seed, work_fields


class _Response:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
        self.text = json.dumps(payload)

    def json(self):
        return self._payload


class _HttpClient:
    """The existing seed helpers speak the TestClient shape; route them over real HTTP."""

    def __init__(self, client: AuthorityClient) -> None:
        self.client = client

    def put(self, path, json=None):
        from groundtruth_kb.authority_client import AuthorityClientError

        try:
            return _Response(self.client.request("PUT", path, body=json))
        except AuthorityClientError as error:
            return _Response({"error": {"code": error.code, "message": str(error)}}, status_code=422)


ROOT = Path(__file__).resolve().parents[2]
pytestmark = [pytest.mark.integration, pytest.mark.timeout(300)]
HOST_LOCATIONS = ("host", "nested location/second host")


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "-c",
            "user.name=Qualification",
            "-c",
            "user.email=qualification@example.invalid",
            *args,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def _cli_env() -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith(("PG", "GT_POSTGRES_", "GIT_"))}
    for key in ("GT_AUTHORITY_URL", "GT_PROJECT_ROOT", "GTKB_PROJECT_ROOT"):
        env.pop(key, None)
    env.update(
        PYTHONPATH=str(Path(groundtruth_kb.__file__).resolve().parent.parent),
        PYTHONIOENCODING="utf-8",
        PYTHONDONTWRITEBYTECODE="1",
    )
    return env


def _cli(*args: str, cwd: Path, env: dict[str, str] | None = None, timeout: int = 120) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-P", "-m", "groundtruth_kb", *args],
        env=env or _cli_env(),
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=timeout,
    )


def _stage_baseline(host: Path) -> None:
    shutil.copytree(
        ROOT / ".harness-baseline-configuration",
        host / ".harness-baseline-configuration",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.lock"),
    )
    # D15: the one skills source lives beside the baseline; the projector fails closed without it.
    shutil.copytree(
        ROOT / ".agents/skills",
        host / ".agents/skills",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    shutil.copytree(
        ROOT / "scripts/harness_projection",
        host / "scripts/harness_projection",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    for script in sorted(ROOT.glob("scripts/*_hook_adapter.py")) + [ROOT / "scripts/implementation_start_gate.py"]:
        shutil.copyfile(script, host / "scripts" / script.name)
    shutil.copyfile(ROOT / "pyproject.toml", host / "pyproject.toml")
    (host / ".githooks").mkdir()
    shutil.copyfile(ROOT / ".githooks/reference-transaction", host / ".githooks/reference-transaction")
    controls = host / "config/governance/operational-controls.toml"
    controls.parent.mkdir(parents=True)
    shutil.copyfile(ROOT / "config/governance/operational-controls.toml", controls)


@pytest.fixture(params=HOST_LOCATIONS, ids=["plain-host", "nested-host-with-space"])
def hosted(native, tmp_path, request, monkeypatch):
    """Native HTTP service for a host at the parametrized location with two initialized applications."""
    service, _test_client, _schema, _service_name = native
    host = tmp_path / request.param
    host.mkdir(parents=True)
    _git(host, "init", "-q", "-b", "develop")
    (host / "README.md").write_text("# Platform host\n", encoding="utf-8")
    (host / ".gitignore").write_text(".worktrees/\napplications/*/\n", encoding="utf-8")
    _stage_baseline(host)
    _git(host, "add", "-A")
    _git(host, "commit", "-qm", "Platform host preimage")
    row = {column: None for column in TABLE_SPECS["harnesses"].columns}
    from datetime import UTC, datetime

    row.update(
        id="HARNESS-1",
        version=1,
        harness_name="qualification",
        harness_type="test",
        status="registered",
        changed_at=datetime.now(UTC).isoformat(),
        changed_by="qualification",
        change_reason="Isolated harness",
    )
    service.kernel.mutate_current(
        table="harnesses",
        identity={"id": row["id"]},
        expected_version=0,
        new_state=row,
        actor="qualification",
        reason="Test setup",
    )
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen()
    port = listener.getsockname()[1]
    server = uvicorn.Server(
        uvicorn.Config(create_authority_app(service, project_root=host), log_level="error", lifespan="off")
    )
    worker = threading.Thread(target=server.run, kwargs={"sockets": [listener]}, daemon=True)
    worker.start()
    deadline = time.monotonic() + 10
    while not server.started and worker.is_alive() and time.monotonic() < deadline:
        time.sleep(0.01)
    assert server.started
    client = AuthorityClient(f"http://127.0.0.1:{port}")
    config = host / "groundtruth.toml"
    config.write_text(
        f'[groundtruth]\nproject_root="{host.as_posix()}"\nauthority_url="{client.url}"\n', encoding="utf-8"
    )
    try:
        http = _HttpClient(client)
        seed(http)
        apps = {}
        for name in ("Alpha", "Beta"):
            registration = _cli("application", "register", name, "--host-root", str(host), "--json", cwd=host)
            assert registration.returncode == 0, registration.stdout + registration.stderr
            project_id, work_id = "PROJECT-" + name, "WI-" + name
            root = host / "applications" / name
            _git(root, "init", "-q", "-b", "develop")
            client.request(
                "PUT",
                f"/v1/projects/{project_id}",
                body={
                    "expected_version": 0,
                    "actor": "qualification",
                    "reason": "application project",
                    "kind": "project",
                    "fields": {"name": name + " App", "repository_ref": "application:" + name},
                },
            )
            initialized = _cli(
                "--config",
                str(config),
                "project",
                "init",
                name,
                "--project-id",
                project_id,
                "--host-root",
                str(host),
                "--owner",
                "Qualification",
                "--no-include-ci",
                "--harness",
                "claude",
                "--harness",
                "codex",
                "--opt-out-core-spec-intake",
                "--json",
                cwd=host,
            )
            assert initialized.returncode == 0, initialized.stdout + initialized.stderr
            created = json.loads(initialized.stdout)
            (root / "code.py").write_text("value = 1\n", encoding="utf-8")
            (root / "tests").mkdir(exist_ok=True)
            (root / "tests/test_effect.py").write_text("def test_effect(): assert 1 == 1\n", encoding="utf-8")
            _git(root, "add", "-A")
            _git(root, "commit", "-qm", "Initialized application preimage")
            response = put(http, "work-items", work_id, work_fields(title=name + " effect"), project_id=project_id)
            assert response.status_code == 200, response.text
            contexts = {}
            for label in ("pb1", "lo1", "pb2", "lo2", "lo3"):
                binding = client.request(
                    "POST",
                    "/v1/sessions/bind",
                    body={"native_context_id": f"{name}-{label}", "init_command": "::init application " + label[:2]},
                )
                contexts[label] = binding["binding"]
            apps[name] = {
                "root": root,
                "project": project_id,
                "work": work_id,
                "contexts": contexts,
                "document": "chain-" + name,
                "created": created,
                "head": _git(root, "rev-parse", "HEAD"),
            }
        yield {"service": service, "client": client, "host": host, "config": config, "apps": apps}
    finally:
        server.should_exit = True
        worker.join(timeout=10)
        assert not worker.is_alive()


def _message(app, role, version, status, **extra):
    return authored(
        app["contexts"][role],
        app["document"],
        version,
        status,
        **{"Project": app["project"], "Work Item": app["work"], **extra},
    ).replace("::init gtkb ", "::init application ", 1)


def _claim(client, app, role, version, status):
    result = client.request(
        "POST",
        f"/v1/bridge/{app['document']}/claim",
        body={
            "native_context_id": app["contexts"][role]["native_context_id"],
            "work_item_id": app["work"],
            "expected_version": version,
            "intended_status": status,
            "request_id": str(uuid4()),
        },
    )
    return {"native_context_id": app["contexts"][role]["native_context_id"], "fence": result["fence"]}


def _send(client, app, role, version, status, **extra):
    fence = _claim(client, app, role, version - 1, status)
    client.request(
        "POST",
        f"/v1/bridge/{app['document']}/deliver",
        body={**fence, "content": _message(app, role, version, status, **extra)},
    )


def _ready(client, app, during_claim=None):
    """NEW by a fresh context, GO by an independent reviewer, READY from a successor's registered worktree."""
    _send(client, app, "pb1", 1, "NEW")
    _send(client, app, "lo1", 2, "GO")
    fence = _claim(client, app, "pb2", 2, "READY")
    opened = client.request("POST", f"/v1/bridge/{app['document']}/worktree", body=fence)
    checkout = Path(opened["path"])
    if during_claim is not None:
        during_claim(checkout, fence)
    (checkout / "code.py").write_text("value = 7\n", encoding="utf-8")
    checked = client.request(
        "POST",
        "/v1/bridge/check-effects",
        body={"native_context_id": fence["native_context_id"], "cwd": str(checkout), "paths": ["code.py"]},
    )
    assert checked["status"] == "current", checked
    client.request(
        "POST",
        f"/v1/bridge/{app['document']}/publish-work",
        body={**fence, "expected_artifacts": opened["artifact_preimages"]},
    )
    client.request(
        "POST", f"/v1/bridge/{app['document']}/deliver", body={**fence, "content": _message(app, "pb2", 3, "READY")}
    )
    artifacts = client.request("GET", f"/v1/bridge/{app['document']}/artifacts")
    _send(client, app, "lo2", 4, "VERIFIED", verified_artifacts=json.dumps(artifacts))
    return checkout, fence


def _gate(app, host, payload: dict, *, context: str) -> dict:
    """Execute the projected native effect gate exactly as the emitted registration names it."""
    settings = json.loads((app["root"] / ".claude/settings.json").read_text(encoding="utf-8"))
    commands = [entry["command"] for group in settings["hooks"]["PreToolUse"] for entry in group["hooks"]]
    command = next(command for command in commands if "implementation_start_gate.py" in command)
    script = command.split('" -B "', 1)[1].split('"', 1)[0].replace("$CLAUDE_PROJECT_DIR", str(app["root"]))
    assert Path(script).is_file(), script
    env = _cli_env()
    env.update(GTKB_NATIVE_CONTEXT_ID=context, GTKB_PROJECT_ROOT=str(app["root"]))
    result = subprocess.run(
        [sys.executable, "-P", script],
        input=json.dumps(payload),
        cwd=app["root"],
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout) if result.stdout.strip() else {}


def test_initialized_applications_carry_installed_hooks_that_resolve_from_their_roots(hosted) -> None:
    host, apps = hosted["host"], hosted["apps"]
    for name, app in apps.items():
        root = app["root"]
        assert (root / ".githooks/reference-transaction").read_bytes() == (
            host / ".githooks/reference-transaction"
        ).read_bytes()
        assert _git(root, "config", "--get", "core.hooksPath") == ".githooks"
        assert {".claude/settings.json", ".codex/hooks.json"} <= set(app["created"]["generated_paths"])
        settings = json.loads((root / ".claude/settings.json").read_text(encoding="utf-8"))
        for group in settings["hooks"]["PreToolUse"]:
            for entry in group["hooks"]:
                script = (
                    entry["command"].split('" -B "', 1)[1].split('"', 1)[0].replace("$CLAUDE_PROJECT_DIR", str(root))
                )
                assert Path(script).resolve().is_file(), script
                assert Path(script).resolve().is_relative_to(host.resolve())
        codex = json.loads((root / ".codex/hooks.json").read_text(encoding="utf-8"))
        assert codex["hooks"], name
        assert app["created"]["commits"] == 0 and app["created"]["canonical_writes"] == 0


@pytest.mark.parametrize("name", ["Alpha", "Beta"])
def test_emitted_effect_gate_denies_unclaimed_writes_and_admits_the_successor_worktree(hosted, name) -> None:
    client, host, apps = hosted["client"], hosted["host"], hosted["apps"]
    app = apps[name]
    payload = {
        "cwd": str(app["root"]),
        "project_root": str(app["root"]),
        "session_id": app["contexts"]["pb2"]["native_context_id"],
        "tool_name": "Write",
        "tool_input": {"file_path": str(app["root"] / "code.py"), "content": "value = 2\n"},
    }
    denied = _gate(app, host, payload, context=app["contexts"]["pb2"]["native_context_id"])
    assert denied["hookSpecificOutput"]["permissionDecision"] == "deny", denied
    observed = {}

    def while_claimed(checkout, _fence):
        observed["checkout"] = checkout
        observed["allowed"] = _gate(
            app,
            host,
            {
                **payload,
                "cwd": str(checkout),
                "project_root": str(checkout),
                "tool_input": {"file_path": str(checkout / "code.py"), "content": "x"},
            },
            context=app["contexts"]["pb2"]["native_context_id"],
        )
        observed["outside_claim_paths"] = _gate(
            app,
            host,
            {
                **payload,
                "cwd": str(checkout),
                "project_root": str(checkout),
                "tool_input": {"file_path": str(checkout / "second.py"), "content": "x"},
            },
            context=app["contexts"]["pb2"]["native_context_id"],
        )
        observed["foreign"] = _gate(
            app,
            host,
            {
                **payload,
                "cwd": str(checkout),
                "project_root": str(checkout),
                "session_id": app["contexts"]["lo1"]["native_context_id"],
                "tool_input": {"file_path": str(checkout / "code.py"), "content": "x"},
            },
            context=app["contexts"]["lo1"]["native_context_id"],
        )

    checkout, _fence = _ready(client, app, during_claim=while_claimed)
    assert observed["checkout"] == checkout
    assert checkout.is_relative_to(host / ".worktrees") and not checkout.is_relative_to(app["root"])
    assert observed["allowed"] == {}, observed["allowed"]
    assert observed["outside_claim_paths"]["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert observed["foreign"]["hookSpecificOutput"]["permissionDecision"] == "deny"
    released = _gate(
        app,
        host,
        {
            **payload,
            "cwd": str(checkout),
            "project_root": str(checkout),
            "tool_input": {"file_path": str(checkout / "code.py"), "content": "x"},
        },
        context=app["contexts"]["pb2"]["native_context_id"],
    )
    assert released["hookSpecificOutput"]["permissionDecision"] == "deny", "a delivered claim admits nothing further"
    assert (app["root"] / "code.py").read_text(encoding="utf-8") == "value = 1\n"


def test_emitted_gate_ignores_loose_bridge_files_and_admits_only_own_scratch(hosted) -> None:
    """Retired scaffold-gate duties: no loose file or local store grants an effect; own scratch is admitted."""
    host, apps = hosted["host"], hosted["apps"]
    app = apps["Alpha"]
    baseline = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in app["root"].rglob("*") if p.is_file()}
    loose = app["root"] / "bridge"
    loose.mkdir()
    loose_file = loose / "pretend-002.md"
    loose_file.write_text('GO\n\ntarget_paths: ["code.py"]\n', encoding="utf-8")
    pb2 = app["contexts"]["pb2"]
    lo1 = app["contexts"]["lo1"]

    def write(path, context):
        return _gate(
            app,
            host,
            {
                "cwd": str(app["root"]),
                "project_root": str(app["root"]),
                "session_id": context["native_context_id"],
                "tool_name": "Write",
                "tool_input": {"file_path": str(path), "content": "This content does not execute or grant permission."},
            },
            context=context["native_context_id"],
        )

    assert write(app["root"] / "code.py", pb2)["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert write(app["root"] / "bridge/forged-001.md", pb2)["hookSpecificOutput"]["permissionDecision"] == "deny"
    own = host / "scratchpad" / pb2["session_context_id"] / "draft.md"
    assert write(own, pb2) == {}
    assert (
        write(host / "scratchpad" / lo1["session_context_id"] / "draft.md", pb2)["hookSpecificOutput"][
            "permissionDecision"
        ]
        == "deny"
    )
    assert not own.exists(), "the gate decides; it never writes"
    assert not (app["root"] / ".gtkb-state").exists() and not (app["root"] / "groundtruth.db").exists()
    assert loose_file.read_text(encoding="utf-8").startswith("GO\n")
    assert all(hashlib.sha256(p.read_bytes()).hexdigest() == h for p, h in baseline.items())


@pytest.mark.parametrize("name", ["Alpha", "Beta"])
def test_installed_reference_transaction_hook_performs_the_commit_callback(hosted, name, monkeypatch, tmp_path) -> None:
    client, host, apps, config = hosted["client"], hosted["host"], hosted["apps"], hosted["config"]
    app = apps[name]
    initial = {key: value["head"] for key, value in apps.items()}
    platform_head = _git(host, "rev-parse", "HEAD")
    checkout, _fence = _ready(client, app)
    callbacks = []
    original = NativeProjectFinalization._check_commit_locked

    def observed(self, tx, project_id, request):
        result = original(self, tx, project_id, request)
        callbacks.append((project_id, result["status"]))
        return result

    monkeypatch.setattr(NativeProjectFinalization, "_check_commit_locked", observed)
    body = tmp_path / "message.txt"
    body.write_text(f"Complete application outcome ({app['work']})\n", encoding="utf-8")
    result = _cli(
        "--config",
        str(config),
        "projects",
        "commit",
        app["project"],
        "--native-context-id",
        app["contexts"]["lo3"]["native_context_id"],
        "--expected-version",
        "1",
        "--message-file",
        str(body),
        "--json",
        cwd=tmp_path,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    committed = json.loads(result.stdout)
    assert committed["status"] == "confirmed", committed
    assert callbacks == [(app["project"], "ready_to_update_reference")]
    assert _git(app["root"], "rev-parse", "HEAD") == committed["commit_id"] != initial[name]
    assert _git(app["root"], "diff", "--name-only", initial[name], "HEAD").splitlines() == ["code.py"]
    assert (app["root"] / "code.py").read_text(encoding="utf-8") == "value = 7\n"
    assert _git(host, "rev-parse", "HEAD") == platform_head
    assert all(_git(other["root"], "rev-parse", "HEAD") == initial[key] for key, other in apps.items() if key != name)
    assert client.request("GET", "/v1/projects/" + app["project"])["project"]["status"] == "verified"
    assert not (app["root"] / "groundtruth.db").exists() and not (app["root"] / "bridge").exists()
    assert (
        hashlib.sha256((app["root"] / ".githooks/reference-transaction").read_bytes()).hexdigest()
        == hashlib.sha256((host / ".githooks/reference-transaction").read_bytes()).hexdigest()
    )


def test_missing_installed_hook_refuses_before_any_head_advances(hosted, tmp_path) -> None:
    client, apps, config = hosted["client"], hosted["apps"], hosted["config"]
    app = apps["Beta"]
    _ready(client, app)
    (app["root"] / ".githooks/reference-transaction").unlink()
    body = tmp_path / "message.txt"
    body.write_text(f"Complete application outcome ({app['work']})\n", encoding="utf-8")
    result = _cli(
        "--config",
        str(config),
        "projects",
        "commit",
        app["project"],
        "--native-context-id",
        app["contexts"]["lo3"]["native_context_id"],
        "--expected-version",
        "1",
        "--message-file",
        str(body),
        "--json",
        cwd=tmp_path,
    )
    assert result.returncode != 0
    assert "commit_hook_missing" in result.stdout + result.stderr
    assert _git(app["root"], "rev-parse", "HEAD") == app["head"]
    assert client.request("GET", "/v1/projects/" + app["project"])["project"]["status"] != "verified"
