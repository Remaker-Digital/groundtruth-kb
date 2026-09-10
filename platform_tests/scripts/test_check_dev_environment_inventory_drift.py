"""Inventory comparison is operational information, not commit permission."""

from __future__ import annotations

import importlib.util
import json
from copy import deepcopy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "inventory_diagnostic", ROOT / "scripts/check_dev_environment_inventory_drift.py"
)
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


def setup_inventory(root, payload):
    config = root / checker.DEFAULT_REGISTRY_RELATIVE_PATH
    config.parent.mkdir(parents=True)
    config.write_bytes((ROOT / checker.DEFAULT_REGISTRY_RELATIVE_PATH).read_bytes())
    inventory = root / checker.DEFAULT_INVENTORY_RELATIVE_PATH
    inventory.parent.mkdir(parents=True)
    inventory.write_text(json.dumps(payload), encoding="utf-8")
    return config, inventory


def payload():
    return {
        "schema_version": 1,
        "generated_at": "before",
        "toolchain": {
            "git": {"version": "1", "status": "verified", "classification": "verified", "evidence": "git --version"}
        },
        "installation": "current",
    }


def test_clean_inventory_requires_no_review_or_staged_test_evidence(tmp_path):
    current = payload()
    config, inventory = setup_inventory(tmp_path, current)
    before = (config.read_bytes(), inventory.read_bytes(), deepcopy(current))
    result = checker.evaluate_drift(tmp_path, current_inventory=current)
    assert result["status"] == "pass"
    assert result["outcome"] == "clean"
    assert before == (config.read_bytes(), inventory.read_bytes(), current)


@pytest.mark.parametrize("field", ["version", "status", "classification"])
def test_volatile_tool_availability_does_not_change_inventory_identity(tmp_path, field):
    current = payload()
    setup_inventory(tmp_path, current)
    current["toolchain"]["git"][field] = "changed"
    current["generated_at"] = "after"
    assert checker.evaluate_drift(tmp_path, current_inventory=current)["status"] == "pass"


def test_wildcard_volatile_fields_preserve_other_data_and_inputs():
    original = {
        "generated_at": "now",
        "toolchain": {"one": {"version": "1", "evidence": "one"}, "two": {"version": "2", "evidence": "two"}},
        "other": {"version": "kept"},
    }
    before = deepcopy(original)
    normalized = checker.normalize_inventory(original, ["generated_at", "toolchain.*.version"])
    assert normalized == {
        "toolchain": {"one": {"evidence": "one"}, "two": {"evidence": "two"}},
        "other": {"version": "kept"},
    }
    assert original == before


@pytest.mark.parametrize(
    "evidence_name",
    ["bridge/GO.md", "platform_tests/test_changed.py", ".groundtruth/formal-artifact-approvals/permission.md"],
)
def test_material_drift_cannot_be_cleared_by_permission_or_test_presence(tmp_path, evidence_name):
    current = payload()
    setup_inventory(tmp_path, current)
    current["toolchain"]["git"]["evidence"] = "a different probe"
    evidence = tmp_path / evidence_name
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.write_text("not authority", encoding="utf-8")
    result = checker.evaluate_drift(tmp_path, current_inventory=current)
    assert result["status"] == "fail"
    assert result["diff_keys"] == ["toolchain"]
    assert result["blocking"][0]["reason"] == "normalized_inventory_drift"
    assert evidence.read_text() == "not authority"


def test_recording_matching_operational_output_clears_actual_drift(tmp_path):
    current = payload()
    _, inventory = setup_inventory(tmp_path, current)
    current["installation"] = "changed"
    assert checker.evaluate_drift(tmp_path, current_inventory=current)["material_inventory_drift"]
    inventory.write_text(json.dumps(current), encoding="utf-8")
    assert checker.evaluate_drift(tmp_path, current_inventory=current)["status"] == "pass"


@pytest.mark.parametrize(
    "config_text",
    [
        "invalid =",
        "schema_version=2",
        'schema_version=1\nvolatile_inventory_paths="not-list"',
        "schema_version=1\nprotected_artifacts=[]",
    ],
)
def test_malformed_or_permission_routing_configuration_refuses(tmp_path, config_text):
    config, _ = setup_inventory(tmp_path, payload())
    config.write_text(config_text, encoding="utf-8")
    with pytest.raises(checker.DriftCheckError):
        checker.evaluate_drift(tmp_path, current_inventory=payload())


@pytest.mark.parametrize("data", [b"{", b"[]", b"\xff"])
def test_unreadable_operational_inventory_returns_typed_failure(tmp_path, capsys, data):
    _, inventory = setup_inventory(tmp_path, payload())
    inventory.write_bytes(data)
    assert checker.main(["--project-root", str(tmp_path), "--json"]) == 1
    assert json.loads(capsys.readouterr().out)["outcome"] == "checker_error"


def test_removed_review_permission_flags_are_not_accepted():
    with pytest.raises(SystemExit) as error:
        checker.main(["--allow-review-evidence", "--staged"])
    assert error.value.code == 2


def test_explicit_empty_volatile_set_preserves_all_fields():
    assert checker.normalize_inventory({"generated_at": "now"}, []) == {"generated_at": "now"}


def test_missing_field_and_explicit_null_are_distinct_inventory_states():
    assert checker.inventory_diff_summary({}, {"installation": None}) == ["installation"]
    assert checker.inventory_diff_summary({"installation": None}, {}) == ["installation"]
