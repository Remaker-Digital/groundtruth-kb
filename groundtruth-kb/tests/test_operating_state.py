"""Tests for deterministic operating-state collection."""

from __future__ import annotations

import inspect
import json
import sqlite3
from pathlib import Path

import pytest
from click.testing import CliRunner

import groundtruth_kb.operating_state as operating_state
from groundtruth_kb.cli import main
from groundtruth_kb.config import GTConfig
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.operating_state import collect_operating_state, format_startup_operating_state


def _config(project_dir: Path) -> GTConfig:
    return GTConfig.load(project_dir / "groundtruth.toml")


def test_collect_operating_state_reports_project_and_db(project_dir: Path) -> None:
    KnowledgeDB(project_dir / "groundtruth.db").close()
    state = collect_operating_state(project_dir, config=_config(project_dir), components=("project", "db"))
    by_name = {component.name: component for component in state.components}

    assert state.schema_version == 1
    assert by_name["project"].status == "PASS"
    assert by_name["db"].status == "PASS"
    assert by_name["db"].evidence["integrity_check"] == "ok"


def test_bridge_probe_counts_latest_role_actionable_statuses(project_dir: Path) -> None:
    bridge_dir = project_dir / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "INDEX.md").write_text(
        "\n".join(
            [
                "Document: first",
                "GO: bridge/first-002.md",
                "NEW: bridge/first-001.md",
                "",
                "Document: second",
                "NEW: bridge/second-001.md",
                "",
                "Document: third",
                "VERIFIED: bridge/third-002.md",
                "NEW: bridge/third-001.md",
            ]
        ),
        encoding="utf-8",
    )
    for name in ("first-001", "first-002", "second-001", "third-001", "third-002"):
        (bridge_dir / f"{name}.md").write_text("bridge_kind: implementation_proposal\n", encoding="utf-8")

    for name, status in {
        "first-001": "NEW",
        "first-002": "GO",
        "second-001": "NEW",
        "third-001": "NEW",
        "third-002": "VERIFIED",
    }.items():
        (bridge_dir / f"{name}.md").write_text(f"{status}\n", encoding="utf-8")

    state = collect_operating_state(project_dir, config=_config(project_dir), components=("bridge",))
    bridge = state.components[0]

    assert bridge.status == "PASS"
    assert bridge.evidence["threads"] == 3
    assert bridge.evidence["prime_actionable_count"] == 1
    assert bridge.evidence["loyal_opposition_actionable_count"] == 1
    assert bridge.evidence["status_counts"]["VERIFIED"] == 1


def test_archive_path_is_rejected(tmp_path: Path) -> None:
    archive = tmp_path / "Claude-Playground" / "archived-project"
    archive.mkdir(parents=True)
    config = GTConfig(project_root=archive, db_path=archive / "groundtruth.db")

    with pytest.raises(ValueError, match="archive path"):
        collect_operating_state(archive, config=config)


def test_missing_chromadb_is_unknown_not_crash(project_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(operating_state._db_module, "HAS_CHROMADB", False)

    state = collect_operating_state(project_dir, config=_config(project_dir), components=("chroma",))

    assert state.components[0].status == "UNKNOWN"
    assert "not installed" in state.components[0].detail


def test_absent_dashboard_cache_is_unknown_with_regeneration_guidance(project_dir: Path) -> None:
    dashboard_db = project_dir / ".groundtruth" / "dashboard" / "gtkb-dashboard.sqlite"
    assert not dashboard_db.exists()

    state = collect_operating_state(project_dir, config=_config(project_dir), components=("dashboard",))
    dashboard = state.components[0]

    assert dashboard.status == "UNKNOWN"
    assert "regenerated" in dashboard.detail
    assert "gt dashboard refresh" in dashboard.detail
    assert dashboard.detail != "dashboard SQLite database not generated"


def test_absent_dashboard_cache_does_not_crash_and_keeps_source_path(project_dir: Path) -> None:
    dashboard_db = project_dir / ".groundtruth" / "dashboard" / "gtkb-dashboard.sqlite"

    state = collect_operating_state(project_dir, config=_config(project_dir), components=("dashboard",))
    dashboard = state.components[0]

    assert dashboard.status == "UNKNOWN"
    assert dashboard.source == str(dashboard_db)
    assert dashboard.evidence == {}


def test_present_dashboard_cache_reports_pass_with_table_count(project_dir: Path) -> None:
    dashboard_db = project_dir / ".groundtruth" / "dashboard" / "gtkb-dashboard.sqlite"
    dashboard_db.parent.mkdir(parents=True)
    with sqlite3.connect(dashboard_db) as conn:
        conn.execute("CREATE TABLE sample_metric (id INTEGER PRIMARY KEY)")

    state = collect_operating_state(project_dir, config=_config(project_dir), components=("dashboard",))
    dashboard = state.components[0]

    assert dashboard.status == "PASS"
    assert dashboard.detail == "dashboard SQLite database readable"
    assert dashboard.evidence["tables"] == 1


def test_resource_registry_probe_reports_compact_health(project_dir: Path) -> None:
    registry = project_dir / "config" / "agent-control" / "project-resource-aliases.toml"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        "\n".join(
            [
                "schema_version = 1",
                "[project]",
                'canonical_name = "GroundTruth-KB"',
                "",
                "[[resources]]",
                'id = "gtkb.github.repo"',
                'kind = "github_repository"',
                'name = "GroundTruth-KB GitHub repository"',
                'url = "https://github.com/Remaker-Digital/groundtruth-kb"',
                'identity = "Remaker-Digital/groundtruth-kb"',
                'aliases = ["repo"]',
                'status = "canonical"',
                "",
                "[[resources]]",
                'id = "gtkb.sonarcloud.project"',
                'kind = "sonarcloud_project"',
                'name = "GroundTruth-KB SonarCloud project"',
                'url = "https://sonarcloud.io/project/overview?id=Remaker-Digital_groundtruth-kb"',
                'identity = "Remaker-Digital_groundtruth-kb"',
                'aliases = ["SonarCloud"]',
                'status = "canonical_unverified_url"',
                "",
                "[[resources]]",
                'id = "agentred.github.repo"',
                'kind = "github_repository"',
                'name = "Agent Red repository"',
                'url = "https://github.com/mike-remakerdigital/agent-red"',
                'identity = "mike-remakerdigital/agent-red"',
                'aliases = ["Agent Red repo"]',
                'status = "separate_project_not_gtkb"',
            ]
        ),
        encoding="utf-8",
    )
    pointer = project_dir / ".claude" / "rules" / "project-resource-aliases.toml"
    pointer.parent.mkdir(parents=True)
    pointer.write_text(
        "\n".join(
            [
                "schema_version = 1",
                'registry_path = "config/agent-control/project-resource-aliases.toml"',
                'status = "delegated"',
            ]
        ),
        encoding="utf-8",
    )

    state = collect_operating_state(project_dir, config=_config(project_dir), components=("resource-registry",))
    component = state.components[0]

    assert component.status == "WARN"
    assert component.evidence["resources"] == 3
    assert component.evidence["unverified_canonical"] == ["gtkb.sonarcloud.project"]
    assert component.evidence["separate_project"] == 1
    assert component.evidence["pointer_status"] == "delegated"


def test_system_interface_map_probe_reports_compact_health(project_dir: Path) -> None:
    map_path = project_dir / "config" / "agent-control" / "system-interface-map.toml"
    map_path.parent.mkdir(parents=True)
    companion = project_dir / "docs" / "gtkb-systems-and-tools.md"
    companion.parent.mkdir(parents=True)
    companion.write_text("# Systems\n", encoding="utf-8")
    map_path.write_text(
        "\n".join(
            [
                "schema_version = 1",
                'human_companion = "docs/gtkb-systems-and-tools.md"',
                "",
                "[[systems]]",
                'id = "backlog"',
                'canonical_name = "backlog"',
                'accepted_aliases = ["backlog"]',
                'authoritative_source = "MemBase table: current_work_items"',
                'read_method = "current_work_items, work_items, versioned bridge files"',
                'harness_caveats = "dashboard summaries are non-authoritative"',
                "",
                "[[systems]]",
                'id = "bridge-queue"',
                'canonical_name = "bridge queue"',
                'accepted_aliases = ["bridge queue"]',
                'authoritative_source = "bridge/INDEX.md"',
            ]
        ),
        encoding="utf-8",
    )

    state = collect_operating_state(project_dir, config=_config(project_dir), components=("system-interface-map",))
    component = state.components[0]

    assert component.status == "PASS"
    assert component.evidence["systems"] == 2
    assert component.evidence["human_companion_exists"] is True
    assert component.evidence["first_reconciliation_case"] == "backlog"
    assert component.evidence["backlog_case"] == "ok"


def test_status_cli_json_and_startup_use_same_collector(project_dir: Path, runner: CliRunner) -> None:
    KnowledgeDB(project_dir / "groundtruth.db").close()

    result = runner.invoke(
        main,
        ["--config", str(project_dir / "groundtruth.toml"), "status", "--startup", "--json"],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema_version"] == 1
    assert payload["startup"] is True
    assert {component["name"] for component in payload["components"]} >= {
        "project",
        "db",
        "bridge",
        "resource-registry",
        "system-interface-map",
    }
    db_component = next(component for component in payload["components"] if component["name"] == "db")
    assert db_component["evidence"]["quick_check"] is True

    state = collect_operating_state(project_dir, config=_config(project_dir), startup=True)
    rendered = format_startup_operating_state(state)
    assert "Operating State" in rendered
    assert str(project_dir.resolve()) in rendered


def test_operating_state_module_has_no_llm_or_network_dependency() -> None:
    source = inspect.getsource(operating_state)

    assert "openai" not in source.lower()
    assert "anthropic" not in source.lower()
    assert "api_key" not in source.lower()
    assert "urllib" not in source.lower()
