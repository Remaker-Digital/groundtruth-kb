from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from groundtruth_kb.inventory import (
    InventoryScanError,
    build_refresh_report,
    emit_markdown_ledger,
    load_match_file,
    scan_inventory_strings,
)


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)


def _artifact_toml(
    artifact_id: str,
    domain: str,
    lifecycle: str,
    storage_path: str,
    *,
    mutation_api: str = "approved test mutation",
) -> str:
    versioning = (
        "immutable_archive"
        if lifecycle == "archive"
        else "regenerated_from_source"
        if lifecycle == "generated"
        else "git_tracked"
    )
    backup = "regenerable_from_source" if lifecycle == "generated" else "git_tracked"
    restore = (
        "regenerate_from_source" if lifecycle == "generated" else "noop" if lifecycle == "archive" else "git_restore"
    )
    return f'''[[artifacts]]
id = "{artifact_id}"
domain = "{domain}"
lifecycle = "{lifecycle}"
storage_path = "{storage_path}"
authority_spec_id = "GOV-PLATFORM-SOT-REGISTRY-001"
mutation_api = "{mutation_api}"
versioning_policy = "{versioning}"
backup_policy = "{backup}"
restore_action = "{restore}"
health_check_function = ""
owner_role = "shared"
'''


def _write_project(root: Path) -> None:
    (root / "config" / "registry").mkdir(parents=True)
    (root / "docs").mkdir()
    (root / "runtime").mkdir()
    (root / "docs" / "rule.md").write_text("Legacy bridge/INDEX.md reference\n", encoding="utf-8")
    (root / "runtime" / "state.txt").write_text("runtime bridge/INDEX.md reference\n", encoding="utf-8")
    (root / "config" / "registry" / "sot-artifacts.toml").write_text(
        _artifact_toml("critical-rule", "narrative_authority", "active", "docs/rule.md")
        + "\n"
        + _artifact_toml("runtime-state", "runtime_state", "active", "runtime/*.txt"),
        encoding="utf-8",
    )


def test_scan_inventory_strings_includes_gitignored_registered_artifact(tmp_path: Path) -> None:
    _write_project(tmp_path)
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


def test_refresh_is_lifecycle_aware_and_does_not_expand_generated_tree(tmp_path: Path) -> None:
    registry_dir = tmp_path / "config" / "registry"
    registry_dir.mkdir(parents=True)
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "rule.md").write_text("canonical\n", encoding="utf-8")
    generated = tmp_path / ".gtkb-state"
    generated.mkdir()
    for index in range(50):
        (generated / f"large-{index}.json").write_text("{}\n", encoding="utf-8")
    registry_dir.joinpath("sot-artifacts.toml").write_text(
        "\n".join(
            (
                _artifact_toml("specs", "specifications", "active", "membase:specifications"),
                _artifact_toml(
                    "dispatcher-task",
                    "runtime_state",
                    "active",
                    "windows-scheduled-task:GTKB-DispatcherDaemon",
                ),
                _artifact_toml("retired-index", "retired", "archive", "bridge/INDEX.md", mutation_api=""),
                _artifact_toml("generated-state", "runtime_state", "generated", ".gtkb-state/"),
                _artifact_toml("docs-tree", "narrative_authority", "active", "docs/"),
                _artifact_toml("missing-active", "control_surface", "active", "config/missing.toml"),
            )
        ),
        encoding="utf-8",
    )

    report = build_refresh_report(tmp_path)

    by_id = {item["artifact_id"]: item for item in report["artifact_statuses"]}
    assert report["mutated"] is False
    assert report["scanned_file_count"] == 1
    assert report["blocking"] is True
    assert report["summary"]["blocking_finding_count"] == 1
    assert report["summary"]["path_class_counts"] == {
        "archive": 1,
        "directory": 1,
        "external": 1,
        "file": 1,
        "generated": 1,
        "membase": 1,
    }
    assert by_id["generated-state"]["expanded_file_count"] == 0
    assert by_id["generated-state"]["status"] == "generated_present"
    assert by_id["dispatcher-task"]["status"] == "declared_external"
    assert by_id["retired-index"]["blocking"] is False
    assert by_id["missing-active"]["status"] == "missing_active_file"
    assert report["missing_artifacts"] == [by_id["missing-active"]]


def test_typed_registry_rejects_incomplete_records(tmp_path: Path) -> None:
    registry_dir = tmp_path / "config" / "registry"
    registry_dir.mkdir(parents=True)
    registry_dir.joinpath("sot-artifacts.toml").write_text(
        '[[artifacts]]\nid = "broken"\ndomain = "runtime_state"\n',
        encoding="utf-8",
    )

    with pytest.raises(InventoryScanError, match="missing required field"):
        build_refresh_report(tmp_path)
