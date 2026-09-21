"""One native authority routes independent application repositories through real Git."""

from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest
import uvicorn
from fastapi.testclient import TestClient
from groundtruth_kb.authority_api import create_authority_app
from groundtruth_kb.postgres_kernel import (
    CURRENT_FORMAT,
    MIGRATION_TABLES,
    TABLE_SPECS,
    PostgresKernelError,
    canonical_json_bytes,
    normalize_manifest,
)
from groundtruth_kb.project.native_finalization import NativeProjectFinalization
from groundtruth_kb.session.worktree import project_worktree
from psycopg import sql

from platform_tests.groundtruth_kb.bridge_fixtures import authored, claim
from platform_tests.groundtruth_kb.bridge_fixtures import bridge as bridge
from platform_tests.groundtruth_kb.finalization_fixtures import base, git, integration
from platform_tests.groundtruth_kb.native_fixtures import native as native
from platform_tests.groundtruth_kb.native_fixtures import put, work_fields

ROOT = Path(__file__).resolve().parents[2]
pytestmark = [pytest.mark.integration, pytest.mark.timeout(180)]


@pytest.fixture
def scope_host(native, tmp_path):
    service, _client, _schema, _service_name = native
    host = tmp_path / "scope-host"
    (host / "applications").mkdir(parents=True)
    (host / "applications/registry.toml").write_text(
        '[applications]\nAlpha={slot="Alpha"}\nBeta={slot="Beta"}\n', encoding="utf-8"
    )
    with TestClient(create_authority_app(service, project_root=host)) as client:
        yield service, client, host


def scope_fields(client, domain, **fields):
    if domain == "tests":
        result = put(client, "specifications", "SPEC-SCOPE-ROOT", {"title": "Scope fixture root"})
        assert result.status_code == 200, result.text
        fields.update(spec_id="SPEC-SCOPE-ROOT", test_type="integration", expected_outcome="Scoped behavior passes")
    return fields


def scope_history(service):
    with service.kernel.transaction(read_only=True) as tx:
        tx.cursor.execute(
            sql.SQL("SELECT * FROM {}.record_history ORDER BY history_id").format(sql.Identifier(tx.schema))
        )
        return tx.cursor.fetchall()


@pytest.mark.parametrize("domain", ["specifications", "tests"])
@pytest.mark.parametrize("name", ["Alpha", "Beta"])
def test_catalog_application_scope_create_amend_and_filter(scope_host, domain, name):
    service, client, _host = scope_host
    scope = "application:" + name
    record_id = "SCOPE-" + name
    fields = scope_fields(client, domain, title="Scoped behavior", application_scope=scope)
    result = put(client, domain, record_id, fields)
    assert result.status_code == 200, result.text
    assert result.json()["application_scope"] == scope
    shown = client.get(f"/v1/{domain}/{record_id}").json()
    assert shown["application_scope"] == scope and shown["version"] == 1
    listed = client.get(f"/v1/{domain}", params={"application_scope": scope}).json()["records"]
    assert [row["id"] for row in listed] == [record_id]
    other = "application:" + ("Beta" if name == "Alpha" else "Alpha")
    assert client.get(f"/v1/{domain}", params={"application_scope": other}).json()["records"] == []
    result = put(client, domain, record_id, {"title": "Amended scoped behavior"}, expected_version=1)
    assert result.status_code == 200 and result.json()["application_scope"] == scope
    history = scope_history(service)
    refused = put(client, domain, record_id, {"application_scope": other}, expected_version=1)
    assert refused.status_code == 409
    assert client.get(f"/v1/{domain}/{record_id}").json() == result.json()
    assert scope_history(service) == history


@pytest.mark.parametrize("domain", ["specifications", "tests"])
@pytest.mark.parametrize(
    "scope", ["application:Missing", "application:alpha", "application:../Alpha", "agent_red_application"]
)
def test_unknown_or_retired_application_scope_refuses_without_mutation(scope_host, domain, scope):
    service, client, _host = scope_host
    fields = scope_fields(client, domain, title="Invalid scope", application_scope=scope)
    before = scope_history(service)
    result = put(client, domain, "SCOPE-INVALID", fields)
    assert result.status_code == 422, result.text
    if scope in {"application:Missing", "application:alpha"}:
        assert result.json()["error"]["code"] == "invalid_application_scope"
    else:
        assert result.json()["code"] == "invalid_request"
    assert client.get(f"/v1/{domain}/SCOPE-INVALID").status_code == 404
    assert scope_history(service) == before


@pytest.mark.parametrize("domain", ["specifications", "tests"])
def test_scope_amendment_rereads_catalog_and_preserves_unresolved_null(scope_host, domain):
    service, client, host = scope_host
    fields = scope_fields(client, domain, title="Explicitly unresolved")
    result = put(client, domain, "SCOPE-NULL", fields)
    assert result.status_code == 200 and result.json()["application_scope"] is None
    result = put(client, domain, "SCOPE-NULL", {"application_scope": "gtkb_platform"}, expected_version=1)
    assert result.status_code == 200 and result.json()["application_scope"] == "gtkb_platform"
    result = put(
        client, domain, "SCOPE-APP", {**fields, "title": "Application", "application_scope": "application:Alpha"}
    )
    assert result.status_code == 200, result.text
    before = scope_history(service)
    (host / "applications/registry.toml").write_text('[applications]\nBeta={slot="Beta"}\n', encoding="utf-8")
    refused = put(client, domain, "SCOPE-APP", {"title": "Changed"}, expected_version=1)
    assert refused.status_code == 422 and refused.json()["error"]["code"] == "invalid_application_scope"
    assert client.get(f"/v1/{domain}/SCOPE-APP").json() == result.json()
    assert scope_history(service) == before


def application_scope_manifest():
    manifest = {"format": CURRENT_FORMAT, "schema_version": 1, "tables": {table: [] for table in MIGRATION_TABLES}}
    for name in ("Alpha", "Beta"):
        for table, prefix in (("specifications", "SPEC"), ("tests", "TEST")):
            row = {column: None for column in TABLE_SPECS[table].columns}
            row.update(
                id=prefix + "-" + name,
                version=1,
                title="Scoped " + name,
                application_scope="application:" + name,
                changed_at="2026-09-14T00:00:00+00:00",
                changed_by="qualification",
                change_reason="Scoped import",
            )
            if table == "specifications":
                row["status"] = "active"
            else:
                row["spec_id"] = "SPEC-" + name
                row["test_type"] = "integration"
                row["expected_outcome"] = "Scoped imported behavior passes"
            manifest["tables"][table].append(row)
    return normalize_manifest(manifest)


def test_scoped_import_requires_catalog_before_writing_and_reads_back_exactly(scope_host, tmp_path):
    service, _client, host = scope_host
    manifest = application_scope_manifest()
    path = tmp_path / "scoped-current.json"
    path.write_bytes(canonical_json_bytes(manifest))
    before = scope_history(service)
    with pytest.raises(PostgresKernelError) as missing_host:
        service.kernel.import_current(input_path=path, actor="qualification", reason="Require scope host")
    assert missing_host.value.code == "invalid_application_scope"
    (host / "applications/registry.toml").write_text('[applications]\nAlpha={slot="Alpha"}\n', encoding="utf-8")
    with pytest.raises(PostgresKernelError) as missing_name:
        service.kernel.import_current(
            input_path=path, actor="qualification", reason="Require catalog", project_root=host
        )
    assert missing_name.value.code == "invalid_application_scope"
    assert scope_history(service) == before
    assert service.list_records("specifications")["records"] == []
    (host / "applications/registry.toml").write_text(
        '[applications]\nAlpha={slot="Alpha"}\nBeta={slot="Beta"}\n', encoding="utf-8"
    )
    result = service.kernel.import_current(
        input_path=path, actor="qualification", reason="Generic import", project_root=host
    )
    assert result["status"] == "imported" and result["row_count"] == 4
    readback = tmp_path / "scoped-readback.json"
    service.kernel.readback_current(output=readback)
    assert readback.read_bytes() == path.read_bytes()
    assert len(scope_history(service)) == 4
    assert (
        service.kernel.import_current(
            input_path=path, actor="qualification", reason="Exact readback", project_root=host
        )["status"]
        == "already_current"
    )


# Registration, scaffold, intake, upgrade and recovery run for two applications at both host locations (M04).
both_host_locations = pytest.mark.parametrize("bridge", ["first-host", "relocated location/second host"], indirect=True)


@pytest.fixture
def applications(bridge):
    service, client, platform_contexts, platform_work = bridge
    host = integration(platform_work)
    controls = host / "config/governance/operational-controls.toml"
    controls.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "config/governance/operational-controls.toml", controls)
    registration_env = {
        key: value for key, value in os.environ.items() if not key.upper().startswith(("PG", "GT_POSTGRES_", "GIT_"))
    }
    rows = {}
    for name in ("Alpha", "Beta"):
        registration = subprocess.run(
            [
                sys.executable,
                "-P",
                "-m",
                "groundtruth_kb",
                "application",
                "register",
                name,
                "--host-root",
                str(host),
                "--json",
            ],
            env=registration_env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
        )
        assert registration.returncode == 0, (registration.stdout, registration.stderr)
        assert json.loads(registration.stdout)["repository_ref"] == "application:" + name
        root = host / "applications" / name
        assert (root / "application.toml").read_text(encoding="utf-8") == f'[application]\nname = "{name}"\n'
        git(root, "init", "-q", "-b", "develop")
        git(root, "config", "user.name", "Application qualification")
        git(root, "config", "user.email", "qualification@example.invalid")
        git(root, "config", "commit.gpgsign", "false")
        (root / ".gitignore").write_text(".githooks/\n", encoding="utf-8")
        (root / "code.py").write_text("value = 1\n", encoding="utf-8")
        (root / "tests").mkdir()
        (root / "tests/test_effect.py").write_text("def test_effect(): assert 1 == 1\n", encoding="utf-8")
        git(root, "add", "--", "application.toml", ".gitignore", "code.py", "tests/test_effect.py")
        git(root, "commit", "-qm", "Independent application preimage")
        hooks = root / ".githooks"
        hooks.mkdir()
        shutil.copyfile(ROOT / ".githooks/reference-transaction", hooks / "reference-transaction")
        (hooks / "reference-transaction").chmod(0o755)
        git(root, "config", "core.hooksPath", ".githooks")
        project_id, work_id = "PROJECT-" + name, "WI-" + name
        response = put(client, "projects", project_id, {"name": name, "repository_ref": "application:" + name})
        assert response.status_code == 200, response.text
        response = put(client, "work-items", work_id, work_fields(title=name + " effect"), project_id=project_id)
        assert response.status_code == 200, response.text
        contexts = {}
        for label in ("pb1", "lo1", "pb2", "lo2", "lo3"):
            response = client.post(
                "/v1/sessions/bind",
                json={"native_context_id": name + "-" + label, "init_command": "::init application " + label[:2]},
            )
            assert response.status_code == 200, response.text
            contexts[label] = response.json()["binding"]
        rows[name] = {
            "root": root,
            "project": project_id,
            "work": work_id,
            "contexts": contexts,
            "document": "chain-" + name,
        }
    return service, client, host, rows, platform_contexts


def message(app, role, version, status, **extra):
    return authored(
        app["contexts"][role],
        app["document"],
        version,
        status,
        **{"Project": app["project"], "Work Item": app["work"], **extra},
    ).replace("::init gtkb ", "::init application ", 1)


@both_host_locations
def test_catalog_scopes_match_two_application_repository_references(applications):
    _service, client, host, apps, _contexts = applications
    heads = {name: base(app["root"]) for name, app in apps.items()}
    platform_head = base(host)
    for name, app in apps.items():
        scope = "application:" + name
        project = client.get(f"/v1/projects/{app['project']}").json()
        assert project["project"]["repository_ref"] == scope
        spec_id = "SPEC-SCOPED-" + name
        test_id = "TEST-SCOPED-" + name
        result = put(client, "specifications", spec_id, {"title": name + " behavior", "application_scope": scope})
        assert result.status_code == 200, result.text
        result = put(
            client,
            "tests",
            test_id,
            {
                "title": name + " test",
                "test_type": "integration",
                "expected_outcome": "Application behavior passes",
                "spec_id": spec_id,
                "application_scope": scope,
                "test_file": "tests/test_effect.py",
                "test_function": "test_effect",
            },
        )
        assert result.status_code == 200, result.text
        assert (app["root"] / result.json()["test_file"]).is_file()
        listed = client.get("/v1/tests", params={"application_scope": scope}).json()["records"]
        assert [row["id"] for row in listed] == [test_id]
    assert {name: base(app["root"]) for name, app in apps.items()} == heads
    assert base(host) == platform_head


def reserve(client, app, role, version, status):
    result = claim(
        client, app["document"], app["contexts"][role]["native_context_id"], version, status, work_item_id=app["work"]
    )
    assert result.status_code == 200, result.text
    return {"native_context_id": app["contexts"][role]["native_context_id"], "fence": result.json()["fence"]}


def send(client, app, role, version, status, **extra):
    fence = reserve(client, app, role, version - 1, status)
    result = client.post(
        f"/v1/bridge/{app['document']}/deliver", json={**fence, "content": message(app, role, version, status, **extra)}
    )
    assert result.status_code == 200, result.text


def ready(client, app):
    send(client, app, "pb1", 1, "NEW")
    send(client, app, "lo1", 2, "GO")
    fence = reserve(client, app, "pb2", 2, "READY")
    opened = client.post(f"/v1/bridge/{app['document']}/worktree", json=fence)
    assert opened.status_code == 200, opened.text
    checkout = Path(opened.json()["path"])
    (checkout / "code.py").write_text("value = 7\n", encoding="utf-8")
    checked = client.post(
        "/v1/bridge/check-effects",
        json={"native_context_id": fence["native_context_id"], "cwd": str(checkout), "paths": ["code.py"]},
    )
    assert checked.status_code == 200, checked.text
    published = client.post(
        f"/v1/bridge/{app['document']}/publish-work",
        json={**fence, "expected_artifacts": opened.json()["artifact_preimages"]},
    )
    assert published.status_code == 200, published.text
    result = client.post(
        f"/v1/bridge/{app['document']}/deliver", json={**fence, "content": message(app, "pb2", 3, "READY")}
    )
    assert result.status_code == 200, result.text
    artifacts = client.get(f"/v1/bridge/{app['document']}/artifacts").json()
    send(client, app, "lo2", 4, "VERIFIED", verified_artifacts=json.dumps(artifacts))
    return checkout


@both_host_locations
@pytest.mark.parametrize("name", ["Alpha", "Beta"])
def test_application_fresh_successor_and_normal_cli_commit_use_one_authority_and_its_repository(
    applications, name, tmp_path, monkeypatch
):
    _service, client, host, apps, _contexts = applications
    app = apps[name]
    initial = {key: base(value["root"]) for key, value in apps.items()}
    platform_head = base(host)
    implementation = ready(client, app)
    assert implementation.is_relative_to(host / ".worktrees")
    assert not implementation.is_relative_to(app["root"])
    callbacks = []
    original = NativeProjectFinalization._check_commit_locked

    def observed(self, tx, project_id, request):
        result = original(self, tx, project_id, request)
        callbacks.append((project_id, result["status"]))
        return result

    monkeypatch.setattr(NativeProjectFinalization, "_check_commit_locked", observed)
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
        server = uvicorn.Server(uvicorn.Config(client.app, host="127.0.0.1", port=port, log_level="error"))
        worker = threading.Thread(target=lambda: server.run(sockets=[listener]), daemon=True)
        worker.start()
        deadline = time.monotonic() + 10
        while not server.started and worker.is_alive() and time.monotonic() < deadline:
            time.sleep(0.01)
        assert server.started
        config = tmp_path / "native-client.toml"
        config.write_text(f'[groundtruth]\nauthority_url="http://127.0.0.1:{port}"\n', encoding="utf-8")
        body = tmp_path / "message.txt"
        body.write_text("Complete application outcome (" + app["work"] + ")\n", encoding="utf-8")
        env = {
            key: value
            for key, value in os.environ.items()
            if not key.startswith(("PG", "GT_POSTGRES_", "GIT_"))
            and key not in {"GT_AUTHORITY_URL", "GT_PROJECT_ROOT", "GTKB_PROJECT_ROOT"}
        }
        try:
            for reference, expected in [("application:" + name, [app["project"]]), ("application:Missing", [])]:
                listed = subprocess.run(
                    [
                        sys.executable,
                        "-P",
                        "-m",
                        "groundtruth_kb",
                        "--config",
                        str(config),
                        "projects",
                        "list",
                        "--repository-ref",
                        reference,
                        "--json",
                    ],
                    env=env,
                    cwd=tmp_path,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    timeout=30,
                )
                assert listed.returncode == 0, (listed.stdout, listed.stderr)
                records = json.loads(listed.stdout)
                assert [row["id"] for row in records] == expected
                assert all(row["repository_ref"] == reference for row in records)
            result = subprocess.run(
                [
                    sys.executable,
                    "-P",
                    "-m",
                    "groundtruth_kb",
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
                ],
                env=env,
                cwd=tmp_path,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=120,
            )
            assert result.returncode == 0, (result.stdout, result.stderr)
            committed = json.loads(result.stdout)
            assert committed["status"] == "confirmed", committed
        finally:
            server.should_exit = True
            worker.join(10)
            assert not worker.is_alive()
    assert callbacks == [(app["project"], "ready_to_update_reference")]
    assert base(app["root"]) == committed["commit_id"] != initial[name]
    assert base(host) == platform_head
    assert all(base(other["root"]) == initial[key] for key, other in apps.items() if key != name)
    assert git(app["root"], "diff", "--name-only", initial[name], "HEAD").stdout.splitlines() == ["code.py"]
    assert client.get("/v1/projects/" + app["project"]).json()["project"]["status"] == "verified"
    assert (app["root"] / "code.py").read_text() == "value = 7\n"
    assert not (app["root"] / ".worktrees").exists()
    assert not (app["root"] / "groundtruth.db").exists()
    assert not (app["root"] / "bridge").exists()


@both_host_locations
def test_repository_reference_rejects_missing_unknown_and_program_associations(applications):
    _service, client, _host, _apps, _contexts = applications
    for fields, kind, code in [
        ({"name": "Missing"}, "project", "project_repository_required"),
        ({"name": "Unknown", "repository_ref": "application:Unknown"}, "project", "invalid_repository_ref"),
        ({"name": "Program", "repository_ref": "platform"}, "program", "program_has_no_repository"),
    ]:
        result = client.put(
            "/v1/projects/PROJECT-INVALID",
            json={
                "expected_version": 0,
                "actor": "qualification",
                "reason": "Invalid reference refusal",
                "kind": kind,
                "fields": fields,
            },
        )
        assert result.status_code != 200
        assert result.json()["error"]["code"] == code, result.text
        assert client.get("/v1/projects/PROJECT-INVALID").status_code == 404


@both_host_locations
def test_application_and_platform_contexts_cannot_claim_each_others_project(applications):
    _service, client, _host, apps, _contexts = applications
    app = apps["Alpha"]
    result = claim(client, "wrong-platform", "pb1", 0, "NEW", work_item_id=app["work"])
    assert result.json()["error"]["code"] == "project_subject_mismatch", result.text
    result = claim(client, "wrong-application", app["contexts"]["pb1"]["native_context_id"], 0, "NEW")
    assert result.json()["error"]["code"] == "project_subject_mismatch", result.text
    for document in ("wrong-platform", "wrong-application"):
        assert client.get("/v1/bridge/" + document + "/show").status_code == 404


@both_host_locations
def test_identical_relative_paths_in_independent_applications_do_not_conflict(applications):
    _service, client, _host, apps, _contexts = applications
    for app in apps.values():
        send(client, app, "pb1", 1, "NEW")
        send(client, app, "lo1", 2, "GO")
    reservations = [reserve(client, app, "pb2", 2, "READY") for app in apps.values()]
    assert len({row["fence"] for row in reservations}) == 2
    assert all(row["fence"] > 0 for row in reservations)


@both_host_locations
def test_active_attempt_prevents_repository_reassignment_without_changing_project(applications):
    _service, client, _host, apps, _contexts = applications
    app = apps["Alpha"]
    reserve(client, app, "pb1", 0, "NEW")
    before = client.get("/v1/projects/" + app["project"]).json()
    result = put(client, "projects", app["project"], {"repository_ref": "application:Beta"}, expected_version=1)
    assert result.json()["error"]["code"] == "project_repository_frozen", result.text
    assert client.get("/v1/projects/" + app["project"]).json() == before


@both_host_locations
def test_catalog_removal_refuses_application_effect_without_publishing_files(applications):
    _service, client, host, apps, _contexts = applications
    app = apps["Alpha"]
    send(client, app, "pb1", 1, "NEW")
    send(client, app, "lo1", 2, "GO")
    fence = reserve(client, app, "pb2", 2, "READY")
    opened = client.post(f"/v1/bridge/{app['document']}/worktree", json=fence).json()
    checkout = Path(opened["path"])
    destination = project_worktree(host, app["project"], create=False, repository_root=app["root"])
    before = (destination / "code.py").read_bytes()
    assert (destination / "code.py").read_text() == "value = 1\n"
    (checkout / "code.py").write_text("value = 9\n", encoding="utf-8")
    (host / "applications/registry.toml").write_text('[applications]\nBeta={slot="Beta"}\n', encoding="utf-8")
    result = client.post(
        f"/v1/bridge/{app['document']}/publish-work", json={**fence, "expected_artifacts": opened["artifact_preimages"]}
    )
    assert result.json()["error"]["code"] == "invalid_repository_ref", result.text
    assert (destination / "code.py").read_bytes() == before
    assert (app["root"] / "code.py").read_text() == "value = 1\n"
    assert (checkout / "code.py").read_text() == "value = 9\n"


@both_host_locations
def test_application_dispatch_envelope_cannot_redirect_the_successor_subject(applications):
    _service, client, _host, apps, _contexts = applications
    app = apps["Alpha"]
    fence = reserve(client, app, "pb1", 0, "NEW")
    content = message(app, "pb1", 1, "NEW").replace("::init application lo", "::init gtkb lo", 1)
    result = client.post(f"/v1/bridge/{app['document']}/deliver", json={**fence, "content": content})
    assert result.json()["error"]["code"] == "project_subject_mismatch", result.text
    assert client.get(f"/v1/bridge/{app['document']}/show").json()["attempt"]["head_version"] == 0


@both_host_locations
def test_artifact_read_does_not_create_a_missing_application_project_worktree(applications):
    _service, client, host, apps, _contexts = applications
    app = apps["Alpha"]
    send(client, app, "pb1", 1, "NEW")
    destination = project_worktree(host, app["project"], create=False, repository_root=app["root"])
    assert destination.resolve().is_relative_to((host / ".worktrees/projects").resolve())
    branch = git(destination, "branch", "--show-current").stdout.strip()
    assert branch.startswith("project/")
    # Simulate loss of an otherwise clean disposable checkout and its branch.
    # A GET must not silently reconstruct either resource.
    git(app["root"], "worktree", "remove", str(destination))
    git(app["root"], "branch", "-D", branch)
    assert not destination.exists()
    before = client.get(f"/v1/bridge/{app['document']}/show").json()
    worktrees = git(app["root"], "worktree", "list", "--porcelain").stdout
    branches = git(app["root"], "show-ref").stdout
    paths = set((host / ".worktrees").rglob("*"))
    result = client.get(f"/v1/bridge/{app['document']}/artifacts")
    assert result.status_code != 200
    assert result.json()["error"]["code"] == "project_checkout_missing", result.text
    assert client.get(f"/v1/bridge/{app['document']}/show").json() == before
    assert git(app["root"], "worktree", "list", "--porcelain").stdout == worktrees
    assert git(app["root"], "show-ref").stdout == branches
    assert set((host / ".worktrees").rglob("*")) == paths


@both_host_locations
def test_overlapping_ready_effects_in_the_same_application_repository_are_refused(applications):
    _service, client, _host, apps, _contexts = applications
    app = apps["Alpha"]
    other = {**app, "project": "PROJECT-AlphaOther", "work": "WI-AlphaOther", "document": "chain-AlphaOther"}
    created = put(
        client, "projects", other["project"], {"name": "Second Alpha outcome", "repository_ref": "application:Alpha"}
    )
    assert created.status_code == 200, created.text
    created = put(
        client, "work-items", other["work"], work_fields(title="Competing effect"), project_id=other["project"]
    )
    assert created.status_code == 200, created.text
    for selected in (app, other):
        send(client, selected, "pb1", 1, "NEW")
        send(client, selected, "lo1", 2, "GO")
    retained = reserve(client, app, "pb2", 2, "READY")
    before = client.get(f"/v1/bridge/{app['document']}/show").json()
    result = claim(
        client, other["document"], other["contexts"]["pb2"]["native_context_id"], 2, "READY", work_item_id=other["work"]
    )
    assert result.status_code != 200
    assert result.json()["error"]["code"] == "artifact_effect_conflict", result.text
    assert client.get(f"/v1/bridge/{app['document']}/show").json() == before
    opened = client.post(f"/v1/bridge/{app['document']}/worktree", json=retained)
    assert opened.status_code == 200, opened.text


@both_host_locations
def test_missing_application_commit_hook_refuses_before_any_repository_head_advances(applications):
    _service, client, host, apps, _contexts = applications
    app = apps["Alpha"]
    ready(client, app)
    request = {"native_context_id": app["contexts"]["lo3"]["native_context_id"], "expected_version": 1}
    prepared = client.post(f"/v1/projects/{app['project']}/prepare-commit", json=request)
    assert prepared.status_code == 200, prepared.text
    assert prepared.json()["status"] == "ready_to_commit"
    (app["root"] / ".githooks/reference-transaction").unlink()
    roots = [host, *(row["root"] for row in apps.values())]
    before = {str(root): git(root, "show-ref").stdout for root in roots}
    result = client.post(
        f"/v1/projects/{app['project']}/commit",
        json={**request, "message": "Complete application outcome (" + app["work"] + ")\n"},
    )
    assert result.status_code == 200, result.text
    assert result.json()["status"] == "fresh_verification_required", result.text
    assert "commit_hook_missing" in result.text, result.text
    assert {str(root): git(root, "show-ref").stdout for root in roots} == before
    assert client.get("/v1/projects/" + app["project"]).json()["project"]["status"] != "verified"
