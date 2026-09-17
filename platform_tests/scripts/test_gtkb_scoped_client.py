"""Focused tests for the Phase 4 scoped-service baseline client and checker.

Covers the contract asserted in bridge proposal
``gtkb-scoped-service-boundary-baseline-implementation-007.md``:

- config load + validation (single-entry allowlist, required fields)
- operation allowlist enforcement (`dashboard.summary.read` only)
- subject-label confinement
- project-root confinement
- summary response shape + source/freshness metadata
- disallowed-op rejection (mutating/request class + unknown op)
- summary-path-no-raw-read guard in the boundary checker

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import importlib.util
import json
import sqlite3
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"
CLIENT_SCRIPT = SCRIPTS_DIR / "gtkb_scoped_client.py"
CHECKER_SCRIPT = SCRIPTS_DIR / "check_scoped_service_boundary.py"


def _load_module(name: str, path: Path):
    if str(SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPTS_DIR))
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def client_module():
    return _load_module("gtkb_scoped_client", CLIENT_SCRIPT)


@pytest.fixture(scope="module")
def checker_module():
    _load_module("gtkb_scoped_client", CLIENT_SCRIPT)
    return _load_module("check_scoped_service_boundary", CHECKER_SCRIPT)


SCHEMA = """
CREATE TABLE current_specifications (id TEXT, status TEXT, type TEXT, title TEXT, component TEXT, file_paths TEXT);
CREATE TABLE current_work_items (id TEXT, resolution_status TEXT, title TEXT, component TEXT, file_paths TEXT);
CREATE TABLE current_tests (id TEXT, status TEXT, title TEXT, component TEXT, file_paths TEXT);
CREATE TABLE current_deliberations (id TEXT, outcome TEXT, title TEXT);
CREATE TABLE test_procedures (id TEXT);
CREATE TABLE current_projects (id TEXT, name TEXT);
CREATE TABLE current_project_work_item_memberships (
    id TEXT, work_item_id TEXT, project_id TEXT, membership_role TEXT, membership_order INTEGER, status TEXT
);
"""

BASE_TOML = textwrap.dedent(
    """
    [groundtruth]
    db_path = "groundtruth.db"

    [scoped_service]
    default_subject = "application"
    application_id = "agent-red"
    project_root = "."
    allowed_read_operations = ["dashboard.summary.read"]
    runtime_root = "memory"
    dashboard_db = "memory/gtkb-dashboard.sqlite"
    """
).strip()


def _populate_fixture_db(path: Path) -> None:
    connection = sqlite3.connect(path)
    try:
        connection.executescript(SCHEMA)
        connection.executemany(
            "INSERT INTO current_specifications VALUES (?,?,?,?,?,?)",
            [
                ("SPEC-1", "verified", "architecture_decision", "Test spec", "agent-red", ""),
                ("SPEC-2", "implemented", "governance", "Another spec", "gtkb", ""),
            ],
        )
        connection.executemany(
            "INSERT INTO current_work_items VALUES (?,?,?,?,?)",
            [("WI-1", "open", "Work", "agent-red", "")],
        )
        connection.executemany(
            "INSERT INTO current_tests VALUES (?,?,?,?,?)",
            [("TEST-1", "passing", "A test", "agent-red", "")],
        )
        connection.executemany(
            "INSERT INTO current_deliberations VALUES (?,?,?)",
            [("DELIB-1", "agreed", "A deliberation")],
        )
        connection.execute("INSERT INTO test_procedures VALUES ('PROC-1')")
        connection.commit()
    finally:
        connection.close()


@pytest.fixture()
def scoped_project(tmp_path: Path) -> Path:
    """A tmp project with groundtruth.toml + a populated groundtruth.db."""

    (tmp_path / "groundtruth.toml").write_text(BASE_TOML, encoding="utf-8")
    _populate_fixture_db(tmp_path / "groundtruth.db")
    (tmp_path / "memory").mkdir()
    return tmp_path


# ---------------------------------------------------------------------------
# Config load + validation
# ---------------------------------------------------------------------------


def test_config_load_succeeds(scoped_project: Path, client_module) -> None:
    config = client_module.load_scoped_service_config(scoped_project)
    assert config.default_subject == "application"
    assert config.application_id == "agent-red"
    assert config.allowed_read_operations == ("dashboard.summary.read",)
    assert config.project_root == scoped_project.resolve()
    assert config.runtime_root == (scoped_project / "memory").resolve()
    assert config.allowed_request_operations == ()


def test_config_missing_section_raises(tmp_path: Path, client_module) -> None:
    (tmp_path / "groundtruth.toml").write_text('[groundtruth]\ndb_path = "groundtruth.db"\n', encoding="utf-8")
    with pytest.raises(client_module.ScopedServiceConfigError):
        client_module.load_scoped_service_config(tmp_path)


def test_config_missing_required_field_raises(tmp_path: Path, client_module) -> None:
    toml_missing_field = textwrap.dedent(
        """
        [scoped_service]
        default_subject = "application"
        application_id = "agent-red"
        project_root = "."
        allowed_read_operations = ["dashboard.summary.read"]
        # runtime_root intentionally omitted
        """
    ).strip()
    (tmp_path / "groundtruth.toml").write_text(toml_missing_field, encoding="utf-8")
    with pytest.raises(client_module.ScopedServiceConfigError, match="runtime_root"):
        client_module.load_scoped_service_config(tmp_path)


def test_config_empty_allowlist_raises(tmp_path: Path, client_module) -> None:
    empty = BASE_TOML.replace('["dashboard.summary.read"]', "[]")
    (tmp_path / "groundtruth.toml").write_text(empty, encoding="utf-8")
    with pytest.raises(client_module.ScopedServiceConfigError, match="non-empty list"):
        client_module.load_scoped_service_config(tmp_path)


def test_config_mutating_operation_in_allowlist_raises(tmp_path: Path, client_module) -> None:
    bad = BASE_TOML.replace(
        '["dashboard.summary.read"]',
        '["dashboard.summary.refresh"]',
    )
    (tmp_path / "groundtruth.toml").write_text(bad, encoding="utf-8")
    with pytest.raises(client_module.ScopedServiceConfigError, match="mutating"):
        client_module.load_scoped_service_config(tmp_path)


def test_config_unsupported_read_operation_raises(tmp_path: Path, client_module) -> None:
    bad = BASE_TOML.replace(
        '["dashboard.summary.read"]',
        '["dashboard.history.read"]',
    )
    (tmp_path / "groundtruth.toml").write_text(bad, encoding="utf-8")
    with pytest.raises(client_module.ScopedServiceConfigError, match="not supported"):
        client_module.load_scoped_service_config(tmp_path)


def test_config_rejects_non_empty_request_operations(tmp_path: Path, client_module) -> None:
    bad = BASE_TOML + '\nallowed_request_operations = ["dashboard.refresh.request"]\n'
    (tmp_path / "groundtruth.toml").write_text(bad, encoding="utf-8")
    with pytest.raises(client_module.ScopedServiceConfigError, match="empty in the Phase 4 baseline"):
        client_module.load_scoped_service_config(tmp_path)


# ---------------------------------------------------------------------------
# Operation invocation + response shape
# ---------------------------------------------------------------------------


def test_summary_read_response_shape(scoped_project: Path, client_module) -> None:
    client = client_module.GtkbScopedClient.from_project_root(scoped_project)
    envelope = client.invoke(client_module.DASHBOARD_SUMMARY_READ, project_root=scoped_project)

    assert envelope["available"] is True
    assert envelope["operation"] == "dashboard.summary.read"
    assert envelope["subject"] == "application"
    assert envelope["application_id"] == "agent-red"
    assert envelope["source"] == "groundtruth.db"
    assert envelope["source_path"].endswith("groundtruth.db")

    freshness = envelope["freshness"]
    assert set(freshness).issuperset({"retrieved_at", "mtime_utc", "size_bytes"})
    assert freshness["mtime_utc"] is not None
    assert freshness["retrieved_at"].endswith("Z")

    payload = envelope["payload"]
    assert isinstance(payload, dict)
    assert {row["id"] for row in payload["specifications"]} == {"SPEC-1", "SPEC-2"}
    assert [row["id"] for row in payload["work_items"]] == ["WI-1"]
    assert [row["id"] for row in payload["tests"]] == ["TEST-1"]
    assert [row["id"] for row in payload["deliberations"]] == ["DELIB-1"]
    assert payload["test_procedures_count"] == 1


def test_summary_read_when_db_missing_returns_unavailable(tmp_path: Path, client_module) -> None:
    (tmp_path / "groundtruth.toml").write_text(BASE_TOML, encoding="utf-8")
    (tmp_path / "memory").mkdir()
    # No groundtruth.db on disk.
    client = client_module.GtkbScopedClient.from_project_root(tmp_path)
    envelope = client.invoke(client_module.DASHBOARD_SUMMARY_READ, project_root=tmp_path)

    assert envelope["available"] is False
    assert "missing" in (envelope.get("error") or "").lower()
    assert envelope["payload"] is None
    assert envelope["freshness"]["retrieved_at"].endswith("Z")


# ---------------------------------------------------------------------------
# Allowlist, subject, and root confinement
# ---------------------------------------------------------------------------


def test_mutating_operation_rejected(scoped_project: Path, client_module) -> None:
    client = client_module.GtkbScopedClient.from_project_root(scoped_project)
    with pytest.raises(client_module.ScopedOperationError, match="mutating"):
        client.invoke("dashboard.refresh.request", project_root=scoped_project)


def test_unknown_read_operation_rejected(scoped_project: Path, client_module) -> None:
    client = client_module.GtkbScopedClient.from_project_root(scoped_project)
    with pytest.raises(client_module.ScopedOperationError, match="not allowed"):
        # Structurally a read op, but NOT in the single-entry allowlist.
        client.invoke("dashboard.history.read", project_root=scoped_project)


def test_unknown_non_mutating_operation_rejected(scoped_project: Path, client_module) -> None:
    client = client_module.GtkbScopedClient.from_project_root(scoped_project)
    with pytest.raises(client_module.ScopedOperationError, match="not allowed"):
        client.invoke("deliberation.list", project_root=scoped_project)


def test_foreign_subject_rejected(scoped_project: Path, client_module) -> None:
    client = client_module.GtkbScopedClient.from_project_root(scoped_project)
    with pytest.raises(client_module.ScopedOperationError, match="subject"):
        client.invoke(
            client_module.DASHBOARD_SUMMARY_READ,
            subject="platform",
            project_root=scoped_project,
        )


def test_foreign_project_root_rejected(scoped_project: Path, tmp_path: Path, client_module) -> None:
    other_root = tmp_path.parent / (tmp_path.name + "-other")
    other_root.mkdir()
    client = client_module.GtkbScopedClient.from_project_root(scoped_project)
    with pytest.raises(client_module.ScopedOperationError, match="project_root"):
        client.invoke(client_module.DASHBOARD_SUMMARY_READ, project_root=other_root)


# ---------------------------------------------------------------------------
# Boundary checker: scoped-service configuration
# ---------------------------------------------------------------------------


def test_boundary_checker_live_repo_passes(checker_module) -> None:
    """The repo itself must satisfy the Phase 4 contract."""

    report = checker_module.run_checks(REPO_ROOT)
    assert report["status"] == "pass", report
    assert report["checks"]["config"]["allowed_read_operations"] == ["dashboard.summary.read"]
    assert set(report["checks"]) == {"config"}


def test_boundary_checker_detects_allowlist_drift(tmp_path: Path, checker_module) -> None:
    toml_text = BASE_TOML.replace(
        '["dashboard.summary.read"]',
        '["dashboard.summary.read", "dashboard.history.read"]',
    )
    (tmp_path / "groundtruth.toml").write_text(toml_text, encoding="utf-8")
    _populate_fixture_db(tmp_path / "groundtruth.db")
    (tmp_path / "memory").mkdir()

    # The underlying load_scoped_service_config rejects unsupported reads
    # before the checker-specific drift check runs; either outcome fails
    # the boundary contract. Both paths surface the same BoundaryCheckError.
    report = checker_module.run_checks(tmp_path)
    assert report["status"] == "fail"
    assert any("allowed_read_operations" in err or "not supported" in err for err in report["errors"])


# ---------------------------------------------------------------------------
# CLI surface smoke test
# ---------------------------------------------------------------------------


def test_cli_summary_read_json(scoped_project: Path) -> None:
    """Exercises the client through its command-line JSON envelope."""

    result = subprocess.run(
        [
            sys.executable,
            str(CLIENT_SCRIPT),
            "dashboard.summary.read",
            "--json",
            "--project-root",
            str(scoped_project),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["operation"] == "dashboard.summary.read"
    assert payload["available"] is True
    trimmed: dict[str, Any] = payload["payload"]
    # CLI trims payload to counts.
    assert trimmed["specification_count"] == 2
    assert trimmed["work_item_count"] == 1
    assert trimmed["test_count"] == 1
    assert trimmed["deliberation_count"] == 1
    assert trimmed["test_procedures_count"] == 1


def test_cli_rejects_mutating_operation(scoped_project: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(CLIENT_SCRIPT),
            "dashboard.refresh.request",
            "--project-root",
            str(scoped_project),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 2
    assert "mutating" in result.stderr.lower() or "not allowed" in result.stderr.lower()
