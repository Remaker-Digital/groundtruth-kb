"""Tests for the ``gt authority`` CLI."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from groundtruth_kb.authority import resolve_subject
from groundtruth_kb.cli import main

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "groundtruth.toml"


def test_authority_resolve_bridge_index_json_includes_authority_fields() -> None:
    result = CliRunner().invoke(
        main,
        ["--config", str(CONFIG_PATH), "authority", "resolve", "bridge index", "--json"],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    system = payload["system"]
    assert payload["status"] == "resolved"
    assert system["id"] == "bridge-queue"
    assert system["authoritative_source"] == "bridge/INDEX.md"
    assert system["concept_vs_artifact"]
    assert system["read_method"]
    assert system["mutation_method"]
    assert system["role_permissions"]
    assert isinstance(system["related_specs"], list)


def test_authority_resolves_required_owner_facing_terms() -> None:
    expected = {
        "bridge": "file-bridge",
        "bridge index": "bridge-queue",
        "bridge status": "bridge-status",
        "parked draft": "parked-draft",
        "project root": "project-root",
        "role assignment": "role-assignment-record",
        "canonical glossary": "canonical-glossary",
        "doctor": "doctor-check",
        "work item": "work-item",
        "MemBase": "membase",
    }

    for term, system_id in expected.items():
        result = resolve_subject(term, project_root=PROJECT_ROOT)
        assert result["status"] == "resolved", result
        assert result["system"]["id"] == system_id


def test_authority_resolve_unknown_subject_suggests_candidates() -> None:
    result = CliRunner().invoke(
        main,
        ["--config", str(CONFIG_PATH), "authority", "resolve", "bridge indx", "--json"],
    )

    assert result.exit_code == 1
    payload = json.loads(result.output)
    assert payload["status"] == "not_found"
    assert payload["candidates"]


def test_authority_status_json_passes_live_map() -> None:
    result = CliRunner().invoke(main, ["--config", str(CONFIG_PATH), "authority", "status", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "pass"
    assert payload["first_reconciliation_case"] == "backlog"
    assert payload["systems"] >= 1
