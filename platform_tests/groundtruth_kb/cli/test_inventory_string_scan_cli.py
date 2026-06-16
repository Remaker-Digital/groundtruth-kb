from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner
from groundtruth_kb.cli import main


def _write_project(root: Path) -> Path:
    (root / "config" / "registry").mkdir(parents=True)
    (root / "docs").mkdir()
    (root / "docs" / "rule.md").write_text("bridge/INDEX.md\n", encoding="utf-8")
    (root / "config" / "registry" / "sot-artifacts.toml").write_text(
        """
[[artifacts]]
id = "rule"
domain = "narrative_authority"
lifecycle = "active"
storage_path = "docs/rule.md"
""".strip()
        + "\n",
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
