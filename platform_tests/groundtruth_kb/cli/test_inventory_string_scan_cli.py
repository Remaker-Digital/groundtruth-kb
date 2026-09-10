from __future__ import annotations

import json
import subprocess
from pathlib import Path

from click.testing import CliRunner
from groundtruth_kb.cli import main
from groundtruth_kb.db import KnowledgeDB


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


def _prepare_database(root: Path) -> None:
    db = KnowledgeDB(db_path=root / "groundtruth.db")
    db.close()


def _write_project(root: Path) -> Path:
    (root / "config" / "registry").mkdir(parents=True)
    (root / "docs").mkdir()
    (root / "docs" / "rule.md").write_text("bridge/INDEX.md\n", encoding="utf-8")
    (root / "config" / "registry" / "sot-artifacts.toml").write_text(
        _artifact_toml("rule", "narrative_authority", "active", "docs/rule.md"),
        encoding="utf-8",
    )
    _prepare_database(root)
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
        ["--config", str(config), "admin", "inventory", "scan-strings", "--match", "bridge/INDEX.md", "--json"],
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
            "admin",
            "inventory",
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

    result = CliRunner().invoke(main, ["--config", str(config), "admin", "inventory", "refresh", "--json"])

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
    _prepare_database(tmp_path)
    (tmp_path / ".gitignore").write_text(".env.local\n", encoding="utf-8")
    (tmp_path / ".env.local").write_text("REGISTERED_LOCAL_SENTINEL\n", encoding="utf-8")
    _git(tmp_path, "init")
    _git(tmp_path, "add", ".gitignore", "config/registry/sot-artifacts.toml", "docs/rule.md")

    result = CliRunner().invoke(main, ["--config", str(config), "admin", "inventory", "refresh", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["summary"]["artifact_count"] == 2
    assert payload["summary"]["scanned_file_count"] == 2


def test_inventory_refresh_reports_compact_path_classes_and_blockers(tmp_path: Path) -> None:
    config = _write_project(tmp_path)
    generated = tmp_path / ".gtkb-state"
    generated.mkdir(exist_ok=True)
    for index in range(25):
        (generated / f"runtime-{index}.json").write_text("{}\n", encoding="utf-8")
    registry = tmp_path / "config" / "registry" / "sot-artifacts.toml"
    registry.write_text(
        registry.read_text(encoding="utf-8")
        + "\n"
        + _artifact_toml("generated-state", "runtime_state", "generated", ".gtkb-state/")
        + "\n"
        + _artifact_toml("missing-active", "control_surface", "active", "config/missing.toml"),
        encoding="utf-8",
    )
    _prepare_database(tmp_path)

    result = CliRunner().invoke(main, ["--config", str(config), "admin", "inventory", "refresh", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    by_id = {item["artifact_id"]: item for item in payload["artifact_statuses"]}
    assert payload["summary"]["scanned_file_count"] == 1
    assert payload["summary"]["blocking_finding_count"] == 1
    assert payload["summary"]["path_class_counts"] == {"file": 2, "generated": 1}
    assert by_id["generated-state"]["expanded_file_count"] == 0
    assert by_id["missing-active"]["blocking"] is True

    human = CliRunner().invoke(main, ["--config", str(config), "admin", "inventory", "refresh"])
    assert human.exit_code == 0, human.output
    assert "blocking findings: 1" in human.output
    assert "path classes: file=2, generated=1" in human.output
