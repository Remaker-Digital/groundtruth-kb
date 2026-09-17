"""
Shared test fixtures for groundtruth-kb.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.gates import GateRegistry


@pytest.fixture()
def runner() -> CliRunner:
    """Click CLI test runner."""
    return CliRunner()


@pytest.fixture()
def project_dir(tmp_path: Path) -> Path:
    """Create a project dir with groundtruth.toml and sample files."""
    toml = tmp_path / "groundtruth.toml"
    toml.write_text(
        f'[groundtruth]\ndb_path = "{(tmp_path / "groundtruth.db").as_posix()}"\n'
        f'project_root = "{tmp_path.as_posix()}"\napp_title = "Test Project"\n',
        encoding="utf-8",
    )
    src = tmp_path / "src"
    src.mkdir()
    (src / "main.py").write_text("def hello():\n    return 'world'\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Test\n", encoding="utf-8")
    return tmp_path


@pytest.fixture()
def db(tmp_path: Path) -> KnowledgeDB:
    """Fresh KnowledgeDB with builtin gates in a temp directory."""
    db_path = tmp_path / "test.db"
    registry = GateRegistry.from_config([], include_builtins=True)
    return KnowledgeDB(db_path=db_path, gate_registry=registry)


@pytest.fixture()
def db_no_gates(tmp_path: Path) -> KnowledgeDB:
    """KnowledgeDB without any governance gates."""
    db_path = tmp_path / "test_nogates.db"
    return KnowledgeDB(db_path=db_path)


@pytest.fixture()
def native_app_authority(tmp_path, monkeypatch, request):
    """Real native HTTP and two applications on the explicitly disposable database."""
    import os
    import socket
    import subprocess
    import threading
    import time
    from uuid import uuid4

    import psycopg
    import uvicorn
    from psycopg import sql

    from groundtruth_kb.authority_api import create_authority_app
    from groundtruth_kb.authority_client import AuthorityClient
    from groundtruth_kb.config import PostgreSQLConfig
    from groundtruth_kb.native_authority import AuthorityService
    from groundtruth_kb.postgres_kernel import PostgresKernel

    assert os.environ.get("GTKB_RUN_POSTGRES_INTEGRATION") == "1"
    service_name = os.environ["GTKB_TEST_POSTGRES_SERVICE"]
    schema = "gtkb_test_" + uuid4().hex
    with psycopg.connect(service=service_name, autocommit=True) as connection:
        address, port, database = connection.execute(
            "SELECT inet_server_addr()::text, inet_server_port(), current_database()"
        ).fetchone()
        assert address in {"127.0.0.1", "127.0.0.1/32"} and port == 55434 and database == "postgres"
        connection.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))

    def drop_schema():
        with psycopg.connect(service=service_name, autocommit=True) as connection:
            connection.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema)))

    request.addfinalizer(drop_schema)
    monkeypatch.setenv("PGOPTIONS", "-c search_path=" + schema)
    host = tmp_path / getattr(request, "param", "host")
    host.mkdir(parents=True)
    subprocess.run(["git", "init", str(host)], capture_output=True, check=True)
    applications = host / "applications"
    applications.mkdir()
    (applications / "registry.toml").write_text(
        '[applications]\nAlpha={slot="Alpha"}\nBeta={slot="Beta"}\n', encoding="utf-8"
    )
    for name in ("Alpha", "Beta"):
        target = applications / name
        target.mkdir()
        (target / "application.toml").write_text(f'[application]\nname="{name}"\n', encoding="utf-8")
        subprocess.run(["git", "init", str(target)], capture_output=True, check=True)
    listener = socket.socket()
    request.addfinalizer(listener.close)
    listener.bind(("127.0.0.1", 0))
    listen_port = listener.getsockname()[1]
    listener.listen()
    server = None
    thread = None
    try:
        kernel = PostgresKernel(PostgreSQLConfig(service=service_name))
        kernel.initialize()
        service = AuthorityService(kernel)
        server = uvicorn.Server(
            uvicorn.Config(create_authority_app(service, project_root=host), log_level="error", lifespan="off")
        )
        thread = threading.Thread(target=server.run, kwargs={"sockets": [listener]}, daemon=True)
        thread.start()
        deadline = time.monotonic() + 10
        while not server.started and thread.is_alive() and time.monotonic() < deadline:
            time.sleep(0.01)
        assert server.started
        client = AuthorityClient(f"http://127.0.0.1:{listen_port}")
        assert client.request("GET", "/v1/status")["ready"]
        for name in ("Alpha", "Beta"):
            client.request(
                "PUT",
                "/v1/projects/PROJECT-" + name,
                body={
                    "expected_version": 0,
                    "actor": "qualification",
                    "reason": "Explicit application fixture",
                    "kind": "project",
                    "fields": {"name": name + " App", "repository_ref": "application:" + name},
                },
            )
        config = host / "groundtruth.toml"
        config.write_text(
            f'[groundtruth]\nproject_root="{host.as_posix()}"\nauthority_url="{client.url}"\n', encoding="utf-8"
        )
        yield {"client": client, "host": host, "config": config, "service": service, "schema": schema}
    finally:
        if server is not None:
            server.should_exit = True
        if thread is not None:
            thread.join(timeout=10)
            assert not thread.is_alive()


class NativeApplicationHost:
    """One disposable host with registered Alpha/Beta slots and the native commit hook installed."""

    def __init__(self, item: dict, runner: CliRunner) -> None:
        self.item = item
        self.runner = runner
        self.client = item["client"]
        self.host: Path = item["host"]
        self.config: Path = item["config"]
        hook = self.host / ".githooks/reference-transaction"
        hook.parent.mkdir(exist_ok=True)
        source = Path(__file__).resolve().parents[2] / ".githooks/reference-transaction"
        hook.write_bytes(source.read_bytes())

    def target(self, name: str = "Alpha") -> Path:
        return self.host / "applications" / name

    def stage_baseline(self) -> Path:
        """Copy the checkout's neutral baseline, projector and adapters so projections can render here."""
        import shutil

        checkout = Path(__file__).resolve().parents[2]
        if (self.host / ".harness-baseline-configuration").is_dir():
            return self.host
        shutil.copytree(
            checkout / ".harness-baseline-configuration",
            self.host / ".harness-baseline-configuration",
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.lock"),
        )
        shutil.copytree(
            checkout / "scripts/harness_projection",
            self.host / "scripts/harness_projection",
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
        for script in sorted(checkout.glob("scripts/*_hook_adapter.py")) + [
            checkout / "scripts/implementation_start_gate.py"
        ]:
            if script.is_file():
                shutil.copyfile(script, self.host / "scripts" / script.name)
        shutil.copyfile(checkout / "pyproject.toml", self.host / "pyproject.toml")
        return self.host

    def options(self, name: str = "Alpha", **overrides):
        from groundtruth_kb.project.scaffold import ScaffoldOptions

        values = {
            "project_name": name + " App",
            "profile": "local-only",
            "owner": "Qualification",
            "target_dir": self.target(name),
            "gt_kb_root": self.host,
            "project_id": "PROJECT-" + name,
            "authority_url": self.client.url,
            "seed_example": False,
            "include_ci": False,
        }
        values.update(overrides)
        return ScaffoldOptions(**values)

    def scaffold(self, name: str = "Alpha", **overrides) -> Path:
        from groundtruth_kb.project.scaffold import scaffold_project

        return scaffold_project(self.options(name, **overrides))

    def invoke(self, *args: str, config: Path | None = None):
        from groundtruth_kb.cli import main

        return self.runner.invoke(main, ["--config", str(config or self.config), *args])

    def init(self, name: str = "Alpha", *extra: str, expect_exit: int = 0) -> dict:
        import json

        result = self.invoke(
            "project",
            "init",
            name,
            "--project-id",
            "PROJECT-" + name,
            "--host-root",
            str(self.host),
            "--owner",
            "Qualification",
            "--no-include-ci",
            "--json",
            *extra,
        )
        assert result.exit_code == expect_exit, result.output
        return json.loads(result.output)

    def files(self, root: Path | None = None) -> dict[str, bytes]:
        base = root or self.host
        return {
            p.relative_to(base).as_posix(): p.read_bytes()
            for p in base.rglob("*")
            if p.is_file() and ".git" not in p.parts
        }

    def facts(self) -> tuple:
        return (
            self.client.request("GET", "/v1/projects"),
            self.client.request("GET", "/v1/specifications"),
        )

    def commit_all(self, root: Path, message: str = "Initial application files") -> str:
        import subprocess

        for args in (
            ["config", "user.email", "qualification@example.invalid"],
            ["config", "user.name", "Qualification"],
            ["config", "commit.gpgsign", "false"],
            ["add", "-A"],
            ["commit", "-qm", message],
        ):
            subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)
        return subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"], check=True, capture_output=True, text=True
        ).stdout.strip()


@pytest.fixture()
def native_application(native_app_authority, runner):
    """Native host helper: registered applications, installed commit hook, ordinary CLI access."""
    return NativeApplicationHost(native_app_authority, runner)
