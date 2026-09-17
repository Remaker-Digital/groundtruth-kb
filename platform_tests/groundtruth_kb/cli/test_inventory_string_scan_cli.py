from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner
from groundtruth_kb.cli import main


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)


def _artifact_toml(artifact_id: str, domain: str, lifecycle: str, storage_path: str) -> str:
    versioning = "regenerated_from_source" if lifecycle == "generated" else "git_tracked"
    backup = "regenerable_from_source" if lifecycle == "generated" else "git_tracked"
    restore = "regenerate_from_source" if lifecycle == "generated" else "git_restore"
    coverage = "opaque_container" if storage_path.endswith("/") else "exact"
    return f'''[[artifacts]]
id = "{artifact_id}"
domain = "{domain}"
lifecycle = "{lifecycle}"
storage_path = "{storage_path}"
coverage_mode = "{coverage}"
authority_spec_id = "GOV-PLATFORM-SOT-REGISTRY-001"
mutation_api = "approved test mutation"
versioning_policy = "{versioning}"
backup_policy = "{backup}"
restore_action = "{restore}"
health_check_function = ""
owner_role = "shared"
'''


def _write_project(root: Path) -> Path:
    (root / "config" / "registry").mkdir(parents=True)
    (root / "docs").mkdir()
    (root / "docs" / "rule.md").write_text("bridge/INDEX.md\n", encoding="utf-8")
    (root / "config" / "registry" / "sot-artifacts.toml").write_text(
        _artifact_toml("rule", "narrative_authority", "active", "docs/rule.md"),
        encoding="utf-8",
    )
    config = root / "groundtruth.toml"
    config.write_text(
        f'[groundtruth]\ndb_path = "{(root / "groundtruth.db").as_posix()}"\nproject_root = "{root.as_posix()}"\n',
        encoding="utf-8",
    )
    return config


def test_scan_strings_json_exits_nonzero_on_critical_hit(tmp_path: Path) -> None:
    config = _write_project(tmp_path)

    result = CliRunner().invoke(
        main,
        ["--config", str(config), "registry", "scan-strings", "--match", "bridge/INDEX.md", "--json"],
    )

    assert result.exit_code == 1
    payload = json.loads(result.output)
    assert payload["summary"]["critical"] == 1
    assert payload["hits"][0]["path"] == "docs/rule.md"
    assert payload["hits"][0]["remediation_status"] == "untriaged"


def test_scan_strings_report_only_keeps_success_exit(tmp_path: Path) -> None:
    config = _write_project(tmp_path)

    result = CliRunner().invoke(
        main,
        [
            "--config",
            str(config),
            "registry",
            "scan-strings",
            "--match",
            "bridge/INDEX.md",
            "--report-only",
        ],
    )

    assert result.exit_code == 0
    assert "Inventory String Scan Ledger" in result.output


def test_inventory_refresh_is_read_only_json(tmp_path: Path) -> None:
    config = _write_project(tmp_path)

    result = CliRunner().invoke(main, ["--config", str(config), "registry", "inventory", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["mutated"] is False
    assert payload["summary"]["artifact_count"] == 1


def test_inventory_refresh_counts_gitignored_registered_artifact(tmp_path: Path) -> None:
    config = _write_project(tmp_path)
    registry = tmp_path / "config" / "registry" / "sot-artifacts.toml"
    registry.write_text(
        registry.read_text(encoding="utf-8")
        + "\n"
        + _artifact_toml("owner-local-env", "runtime_state", "active", ".env.local"),
        encoding="utf-8",
    )
    (tmp_path / ".gitignore").write_text(".env.local\n", encoding="utf-8")
    (tmp_path / ".env.local").write_text("REGISTERED_LOCAL_SENTINEL\n", encoding="utf-8")
    _git(tmp_path, "init")
    _git(tmp_path, "add", ".gitignore", "config/registry/sot-artifacts.toml", "docs/rule.md")

    result = CliRunner().invoke(main, ["--config", str(config), "registry", "inventory", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["summary"]["artifact_count"] == 2
    assert payload["summary"]["scanned_file_count"] == 2


def test_inventory_refresh_reports_compact_path_classes_and_blockers(tmp_path: Path) -> None:
    config = _write_project(tmp_path)
    generated = tmp_path / "derived-fixture"
    generated.mkdir(exist_ok=True)
    for index in range(25):
        (generated / f"runtime-{index}.json").write_text("{}\n", encoding="utf-8")
    registry = tmp_path / "config" / "registry" / "sot-artifacts.toml"
    registry.write_text(
        registry.read_text(encoding="utf-8")
        + "\n"
        + _artifact_toml("generated-state", "runtime_state", "generated", "derived-fixture/")
        + "\n"
        + _artifact_toml("missing-active", "control_surface", "active", "config/missing.toml"),
        encoding="utf-8",
    )

    result = CliRunner().invoke(main, ["--config", str(config), "registry", "inventory", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    by_id = {item["artifact_id"]: item for item in payload["artifact_statuses"]}
    assert payload["summary"]["scanned_file_count"] == 1
    assert payload["summary"]["blocking_finding_count"] == 1
    assert payload["summary"]["path_class_counts"] == {"file": 2, "generated": 1}
    assert by_id["generated-state"]["expanded_file_count"] == 0
    assert by_id["missing-active"]["blocking"] is True

    human = CliRunner().invoke(main, ["--config", str(config), "registry", "inventory"])
    assert human.exit_code == 0, human.output
    assert "blocking findings: 1" in human.output
    assert "path classes: file=2, generated=1" in human.output


@pytest.fixture(autouse=True)
def _deny_database_and_network_for_local_inventory(monkeypatch):
    import socket
    import sqlite3

    import psycopg

    def deny(*_args, **_kwargs):
        raise AssertionError("Local registry inventory must not access a database or network")

    monkeypatch.setattr(sqlite3, "connect", deny)
    monkeypatch.setattr(sqlite3.dbapi2, "connect", deny)
    monkeypatch.setattr(psycopg, "connect", deny)
    monkeypatch.setattr(socket.socket, "connect", deny)


def _cold_inventory_cli(root, arguments, *, cwd=None):
    import os
    import sys

    import groundtruth_kb

    script = r"""
import json, socket, sqlite3, sys
import psycopg
def deny(*args, **kwargs):
    raise AssertionError("Local registry inventory attempted database or network access")
sqlite3.connect = deny
sqlite3.dbapi2.connect = deny
psycopg.connect = deny
socket.socket.connect = deny
from click.testing import CliRunner
from groundtruth_kb.cli import main
result = CliRunner().invoke(main, json.loads(sys.argv[1]))
print(json.dumps({"exit": result.exit_code, "output": result.output,
                  "exception": type(result.exception).__name__ if result.exception else None}))
"""
    package = Path(groundtruth_kb.__file__).resolve().parent.parent
    env = dict(os.environ, PYTHONPATH=str(package), PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    for key in list(env):
        if key in ("GT_AUTHORITY_URL", "GT_PROJECT_ROOT", "GTKB_PROJECT_ROOT", "GT_DB_PATH") or key.startswith(
            ("PG", "GT_POSTGRES_")
        ):
            env.pop(key)
    before = {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    directories = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_dir()}
    process = subprocess.run(
        [
            sys.executable,
            "-P",
            "-c",
            script,
            json.dumps(["--config", str(root / "groundtruth.toml"), "registry", *arguments]),
        ],
        cwd=cwd or root,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    assert process.returncode == 0, process.stdout + process.stderr
    assert before == {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    assert directories == {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_dir()}
    return json.loads(process.stdout)


@pytest.mark.parametrize("command", ["inventory", "scan-strings"])
def test_cold_registry_inventory_uses_selected_root_without_database_or_network(tmp_path, command):
    _write_project(tmp_path)
    (tmp_path / "groundtruth.db").write_bytes(b"This is not a knowledge database")
    foreign = tmp_path / "caller"
    foreign.mkdir()
    (foreign / "groundtruth.toml").write_text('[groundtruth]\nproject_root="wrong-root"\n', encoding="utf-8")
    args = (
        ["inventory", "--json"] if command == "inventory" else ["scan-strings", "--match", "bridge/INDEX.md", "--json"]
    )
    result = _cold_inventory_cli(tmp_path, args, cwd=foreign)
    assert result["exit"] == (0 if command == "inventory" else 1), result
    payload = json.loads(result["output"])
    assert payload["mutated"] is False
    assert payload["artifact_count"] == payload["scanned_file_count"] == 1
    if command == "scan-strings":
        assert payload["summary"]["critical"] == 1
        assert payload["hits"][0]["path"] == "docs/rule.md"


@pytest.mark.parametrize("report_only", [False, True])
def test_cold_registry_scan_reports_missing_members_and_controls_finding_exit(tmp_path, report_only):
    _write_project(tmp_path)
    registry = tmp_path / "config/registry/sot-artifacts.toml"
    registry.write_text(
        registry.read_text(encoding="utf-8") + _artifact_toml("missing", "control_surface", "active", "missing.py"),
        encoding="utf-8",
    )
    args = ["scan-strings", "--match", "not-present", "--json"] + (["--report-only"] if report_only else [])
    result = _cold_inventory_cli(tmp_path, args)
    assert result["exit"] == (0 if report_only else 1), result
    payload = json.loads(result["output"])
    assert payload["summary"]["critical"] == payload["summary"]["total_hits"] == 0
    assert [r["artifact_id"] for r in payload["missing_artifacts"]] == ["missing"]


@pytest.mark.parametrize("contents", ['["bridge/INDEX.md"]', '{"matches":["bridge/INDEX.md"]}', "bridge/INDEX.md\n"])
def test_cold_registry_scan_accepts_existing_match_file_formats(tmp_path, contents):
    _write_project(tmp_path)
    match_file = tmp_path / "matches.txt"
    match_file.write_text(contents, encoding="utf-8")
    result = _cold_inventory_cli(tmp_path, ["scan-strings", "--match-file", str(match_file), "--json"])
    assert result["exit"] == 1, result
    payload = json.loads(result["output"])
    assert payload["summary"]["critical"] == 1
    assert payload["matches"] == [{"id": "M001", "literal": "bridge/INDEX.md"}]


@pytest.mark.parametrize("problem", ["no-matches", "invalid-match-json", "missing-coverage"])
def test_cold_registry_scan_report_only_does_not_hide_invalid_inputs(tmp_path, problem):
    _write_project(tmp_path)
    args = ["scan-strings", "--json", "--report-only"]
    if problem == "invalid-match-json":
        path = tmp_path / "matches.json"
        path.write_text("[invalid", encoding="utf-8")
        args += ["--match-file", str(path)]
    elif problem == "missing-coverage":
        registry = tmp_path / "config/registry/sot-artifacts.toml"
        registry.write_text(
            registry.read_text(encoding="utf-8").replace('coverage_mode = "exact"\n', ""), encoding="utf-8"
        )
        args += ["--match", "bridge/INDEX.md"]
    result = _cold_inventory_cli(tmp_path, args)
    assert result["exit"] == 1 and result["exception"] == "SystemExit", result
    assert result["output"].startswith("Error:")
    assert "has no native authority route" not in result["output"]


@pytest.mark.parametrize(
    "severity_args",
    [[], ["--critical-class", "rule"], ["--critical-class", "runtime_state"], ["--critical-path", "docs/*.md"]],
)
def test_cold_registry_scan_applies_explicit_critical_class_and_path(tmp_path, severity_args):
    _write_project(tmp_path)
    registry = tmp_path / "config/registry/sot-artifacts.toml"
    registry.write_text(
        registry.read_text(encoding="utf-8").replace('domain = "narrative_authority"', 'domain = "runtime_state"'),
        encoding="utf-8",
    )
    result = _cold_inventory_cli(tmp_path, ["scan-strings", "--match", "bridge/INDEX.md", "--json", *severity_args])
    expected = 1 if severity_args else 0
    assert result["exit"] == expected, result
    payload = json.loads(result["output"])
    assert payload["summary"] == {"critical": expected, "total_hits": 1, "warn": 1 - expected}


@pytest.mark.parametrize("report_only", [False, True])
def test_registry_scan_read_failure_is_not_reported_as_no_hits(tmp_path, monkeypatch, report_only):
    config = _write_project(tmp_path)
    member = tmp_path / "docs/rule.md"
    original_read = Path.read_text

    def read_error(path, *args, **kwargs):
        if path == member:
            raise PermissionError("controlled read refusal")
        return original_read(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", read_error)
    args = ["--config", str(config), "registry", "scan-strings", "--match", "bridge/INDEX.md", "--json"]
    if report_only:
        args.append("--report-only")
    result = CliRunner().invoke(main, args)
    assert result.exit_code == 1
    assert "Cannot read registered artifact docs/rule.md" in result.output
    assert '"hits"' not in result.output


@pytest.mark.parametrize("report_only", [False, True])
def test_cold_registry_scan_text_keeps_coverage_findings_without_hits(tmp_path, report_only):
    _write_project(tmp_path)
    registry = tmp_path / "config/registry/sot-artifacts.toml"
    registry.write_text(
        registry.read_text(encoding="utf-8") + _artifact_toml("missing", "control_surface", "active", "missing.py"),
        encoding="utf-8",
    )
    args = ["scan-strings", "--match", "not-present"] + (["--report-only"] if report_only else [])
    result = _cold_inventory_cli(tmp_path, args)
    assert result["exit"] == (0 if report_only else 1), result
    assert "## Coverage Findings" in result["output"]
    assert "missing (missing.py): missing_active_file" in result["output"]
    assert "coverage findings remain" in result["output"]
