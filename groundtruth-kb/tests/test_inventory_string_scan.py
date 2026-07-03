from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from groundtruth_kb.inventory import InventoryScanError, emit_markdown_ledger, load_match_file, scan_inventory_strings


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)


def _write_project(root: Path) -> None:
    (root / "config" / "registry").mkdir(parents=True)
    (root / "docs").mkdir()
    (root / "runtime").mkdir()
    (root / "docs" / "rule.md").write_text("Legacy bridge/INDEX.md reference\n", encoding="utf-8")
    (root / "runtime" / "state.txt").write_text("runtime bridge/INDEX.md reference\n", encoding="utf-8")
    (root / "config" / "registry" / "sot-artifacts.toml").write_text(
        """
[[artifacts]]
id = "critical-rule"
domain = "narrative_authority"
lifecycle = "active"
storage_path = "docs/rule.md"

[[artifacts]]
id = "runtime-state"
domain = "runtime_state"
lifecycle = "active"
storage_path = "runtime/*.txt"
""".strip()
        + "\n",
        encoding="utf-8",
    )


def test_scan_inventory_strings_includes_gitignored_registered_artifact(tmp_path: Path) -> None:
    _write_project(tmp_path)
    registry = tmp_path / "config" / "registry" / "sot-artifacts.toml"
    registry.write_text(
        registry.read_text(encoding="utf-8")
        + """

[[artifacts]]
id = "owner-local-env"
domain = "runtime_state"
lifecycle = "active"
storage_path = ".env.local"
""",
        encoding="utf-8",
    )
    (tmp_path / ".gitignore").write_text(".env.local\n", encoding="utf-8")
    (tmp_path / ".env.local").write_text("REGISTERED_LOCAL_SENTINEL\n", encoding="utf-8")
    _git(tmp_path, "init")
    _git(tmp_path, "add", ".gitignore", "config/registry/sot-artifacts.toml", "docs/rule.md", "runtime/state.txt")

    payload = scan_inventory_strings(tmp_path, ["REGISTERED_LOCAL_SENTINEL"])

    assert payload["summary"]["total_hits"] == 1
    assert payload["hits"][0]["path"] == ".env.local"
    assert payload["hits"][0]["artifact_id"] == "owner-local-env"


def test_scan_inventory_strings_reports_critical_and_warn_hits(tmp_path: Path) -> None:
    _write_project(tmp_path)

    payload = scan_inventory_strings(tmp_path, ["bridge/INDEX.md"])

    assert payload["mutated"] is False
    assert payload["summary"] == {"critical": 1, "total_hits": 2, "warn": 1}
    paths = {(hit["path"], hit["severity"], hit["remediation_status"]) for hit in payload["hits"]}
    assert ("docs/rule.md", "critical", "untriaged") in paths
    assert ("runtime/state.txt", "warn", "untriaged") in paths
    assert {hit["matched_string_id"] for hit in payload["hits"]} == {"M001"}


def test_scan_inventory_strings_accepts_path_and_class_overrides(tmp_path: Path) -> None:
    _write_project(tmp_path)

    payload = scan_inventory_strings(
        tmp_path,
        ["runtime"],
        critical_classes={"runtime_state"},
        warn_paths=("docs/*",),
    )

    assert payload["summary"]["critical"] == 1
    assert payload["hits"][0]["artifact_id"] == "runtime-state"


def test_match_file_supports_json_and_newline_lists(tmp_path: Path) -> None:
    json_file = tmp_path / "matches.json"
    json_file.write_text(json.dumps({"matches": ["one", "two"]}), encoding="utf-8")
    txt_file = tmp_path / "matches.txt"
    txt_file.write_text("# comment\nthree\n\nfour\n", encoding="utf-8")

    assert load_match_file(json_file) == ["one", "two"]
    assert load_match_file(txt_file) == ["three", "four"]


def test_scan_inventory_strings_requires_match_input(tmp_path: Path) -> None:
    _write_project(tmp_path)

    with pytest.raises(InventoryScanError, match="at least one"):
        scan_inventory_strings(tmp_path, [])


def test_markdown_ledger_groups_hits_by_severity(tmp_path: Path) -> None:
    _write_project(tmp_path)
    payload = scan_inventory_strings(tmp_path, ["bridge/INDEX.md"])

    ledger = emit_markdown_ledger(payload)

    assert "## Critical Hits" in ledger
    assert "## Warn Hits" in ledger
    assert "docs/rule.md:1:8 [M001]" in ledger
