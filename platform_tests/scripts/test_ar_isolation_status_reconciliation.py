"""Current application registry facts; historical measurements are not authority."""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_REGISTRY = REPO_ROOT / "applications/Agent_Red/.gtkb-app-isolation.json"


def _registry():
    return json.loads(APP_REGISTRY.read_text(encoding="utf-8"))


def _artifact_entry(name):
    matches = [e for e in _registry()["top_level_artifacts"] if e["name"] == name]
    assert len(matches) == 1
    return matches[0]


def test_claude_registry_entry_describes_independent_application_configuration():
    entry = _artifact_entry(".claude")
    assert entry["type"] == "DIR"
    assert entry["classification"] == "authoritative_input"
    assert entry["tool"] == "Claude Code"
    assert "Application-owned" in entry["purpose"]
    assert "No GT-KB platform projection" in entry["purpose"]
    assert "freshly measured" not in entry["purpose"]


def test_agent_red_registry_uses_current_classifications_without_retired_authority_claims():
    registry = _registry()
    assert registry["application"] == "Agent_Red" and registry["schema_version"] == "2.0"
    assert registry["isolation_contract_adr"] == "ADR-APPLICATION-ISOLATION-CONTRACT-001"
    assert registry["minimization_principle_dcl"] == "DCL-APP-ROOT-MINIMIZATION-001"
    entries = registry["top_level_artifacts"]
    for entry in entries:
        assert entry["name"] and entry["type"] in {"FILE", "DIR"} and entry["purpose"]
        assert entry["classification"] in {
            "authoritative_input",
            "generated_output",
            "runtime_data",
            "bounded_temporary_output",
        }
        assert "bucket" not in entry
    assert {"assets", "terraform"} <= {e["name"] for e in entries}
    assert not {".vscode", "harness-state"} & {e["name"] for e in entries}
    assert _artifact_entry("assets")["classification"] == "generated_output"
    assert _artifact_entry("terraform")["classification"] == "authoritative_input"
    assert (
        not {
            "established_by",
            "last_updated",
            "out_of_scope_for_sub_slice_1",
            "known_limitations",
            "validator_contract",
        }
        & registry.keys()
    )


def test_codex_registry_entry_retains_independent_application_configuration():
    entry = _artifact_entry(".codex")
    assert entry == {
        "name": ".codex",
        "type": "DIR",
        "classification": "authoritative_input",
        "purpose": "Application-owned Codex configuration. No GT-KB platform projection is supplied by this entry.",
        "tool": "Codex CLI",
    }
