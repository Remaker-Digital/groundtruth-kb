"""Shared fixtures and helpers of the registry CLI qualification (c102, Q-3, owner ruling D23).

Moved verbatim from ``test_registry_current_mutation_cli.py`` (``record``, ``_control_fixture``,
the ``project`` fixture, ``invoke``) so that no test module imports another test module. Kept
in ``cli/`` so ``_control_fixture`` keeps resolving the repository root at the same depth. Not
collected; defines no test.
"""

from __future__ import annotations

import json
import socket
import sqlite3
import subprocess
import threading
import time
from pathlib import Path

import pytest
import tomlkit
import uvicorn
from click.testing import CliRunner
from groundtruth_kb.cli import main
from groundtruth_kb.project import registry_control_plane as registry
from groundtruth_kb.project.operational_control_config import CATALOG_RELATIVE_PATH
from groundtruth_kb.project.sot_registry import SoTArtifact
from psycopg import sql

from platform_tests.groundtruth_kb.native_fixtures import put


def record(ident: str, path: str, **changes) -> SoTArtifact:
    return SoTArtifact(
        **{
            "id": ident,
            "domain": "control_surface",
            "lifecycle": "active",
            "storage_path": path,
            "authority_spec_id": "GOV-REGISTRY",
            "mutation_api": "gt registry amend",
            "versioning_policy": "git_tracked",
            "backup_policy": "git_tracked",
            "health_check_function": "",
            "owner_role": "shared",
            "restore_action": "git_restore",
            "coverage_mode": "exact",
            **changes,
        }
    )


def _control_fixture(root: Path, timeout: float | None = None):
    source = Path(__file__).resolve().parents[3] / CATALOG_RELATIVE_PATH
    target = root / CATALOG_RELATIVE_PATH
    document = tomlkit.parse(source.read_text(encoding="utf-8"))
    if timeout is not None:
        for row in document["controls"]:
            if row["id"] == "registry.lock.acquire_seconds":
                row["value"] = str(timeout)
            elif row["id"] == "registry.lock.max_backoff_seconds":
                row["value"] = "0.01"
            elif row["id"] == "registry.lock.initial_backoff_seconds":
                row["value"] = "0.001"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(tomlkit.dumps(document), encoding="utf-8")
    return registry._registry_controls(root)


@pytest.fixture
def project(tmp_path: Path, native):
    service, client, _, _ = native
    _control_fixture(tmp_path)
    response = put(
        client,
        "specifications",
        "GOV-REGISTRY",
        {"title": "Current native registry contract", "status": "active", "source_paths": ["keep.txt"]},
    )
    assert response.status_code == 200, response.text
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, capture_output=True)
    config = tmp_path / "groundtruth.toml"
    declaration = tmp_path / "config/registry/sot-artifacts.toml"
    declaration.parent.mkdir(parents=True)
    declaration.write_bytes(registry.serialize_registry([record("registry", "config/registry/sot-artifacts.toml")]))
    with sqlite3.connect(tmp_path / "groundtruth.db") as connection:
        connection.execute("CREATE TABLE historical_marker (value TEXT)")
        connection.execute("INSERT INTO historical_marker VALUES ('inert local database must remain unchanged')")
    (tmp_path / "keep.txt").write_text("unrelated work", encoding="utf-8")

    def canonical_snapshot():
        with service.kernel.transaction(read_only=True) as tx:
            tx.cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname=%s ORDER BY tablename", (tx.schema,))
            tables = [r["tablename"] for r in tx.cursor.fetchall()]
            rows = {}
            for table in tables:
                tx.cursor.execute(
                    sql.SQL("SELECT * FROM {}.{}").format(sql.Identifier(tx.schema), sql.Identifier(table))
                )
                rows[table] = sorted(json.dumps(dict(row), default=str, sort_keys=True) for row in tx.cursor.fetchall())
            return rows

    before = canonical_snapshot()
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
        config.write_text(
            f'[groundtruth]\nproject_root="."\ndb_path="groundtruth.db"\nauthority_url="http://127.0.0.1:{port}"\n',
            encoding="utf-8",
        )
        server = uvicorn.Server(uvicorn.Config(client.app, host="127.0.0.1", port=port, log_level="error"))
        worker = threading.Thread(target=lambda: server.run(sockets=[listener]), daemon=True)
        worker.start()
        deadline = time.monotonic() + 10
        try:
            while not server.started and worker.is_alive() and time.monotonic() < deadline:
                time.sleep(0.01)
            assert server.started
            yield tmp_path, config, declaration
        finally:
            server.should_exit = True
            worker.join(10)
            assert not worker.is_alive()
            assert canonical_snapshot() == before


def invoke(project, *args):
    return CliRunner().invoke(main, ["--config", str(project[1]), "registry", *args])
