"""Tests for protected dev-environment inventory drift control."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "check_dev_environment_inventory_drift.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("check_dev_environment_inventory_drift", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_dev_environment_inventory_drift"] = module
    spec.loader.exec_module(module)
    return module


def _write_registry(root: Path) -> Path:
    path = root / "config" / "governance" / "protected-artifact-inventory-drift.toml"
    path.parent.mkdir(parents=True)
    path.write_text(
        "\n".join(
            [
                "schema_version = 1",
                'volatile_inventory_paths = ["generated_at", "redaction.sensitive_environment_entry_count"]',
                "",
                "[[protected_artifacts]]",
                'id = "inventory"',
                (
                    'patterns = [".groundtruth/inventory/dev-environment-inventory.json", '
                    '"scripts/check_dev_environment_inventory_drift.py"]'
                ),
                'severity = "accepted_baseline_update"',
                'route = "accepted_baseline_update"',
                "accept_with_inventory_baseline_update = true",
                'required_evidence = ["inventory regenerated"]',
                "",
                "[[protected_artifacts]]",
                'id = "hooks"',
                'patterns = [".githooks/**"]',
                'severity = "compatibility_tests"',
                'route = "compatibility_tests"',
                "accept_with_inventory_baseline_update = false",
                'required_evidence = ["hook parity test"]',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def _write_inventory(root: Path, payload: dict) -> Path:
    path = root / ".groundtruth" / "inventory" / "dev-environment-inventory.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _payload(*, generated_at: str = "2026-05-06T00:00:00Z", python_version: str = "3.14.0") -> dict:
    return {
        "schema_version": 1,
        "generated_at": generated_at,
        "toolchain": {"python": {"version": python_version}},
        "redaction": {"status": "pass", "sensitive_environment_entry_count": 1},
    }


def test_normalize_inventory_ignores_configured_volatile_fields() -> None:
    module = _load_module()
    first = _payload(generated_at="2026-05-06T00:00:00Z")
    second = _payload(generated_at="2026-05-06T01:00:00Z")
    second["redaction"]["sensitive_environment_entry_count"] = 99

    assert module.normalize_inventory(first, ["generated_at", "redaction.sensitive_environment_entry_count"]) == (
        module.normalize_inventory(second, ["generated_at", "redaction.sensitive_environment_entry_count"])
    )


def test_registry_loads_and_classifies_protected_paths(tmp_path: Path) -> None:
    module = _load_module()
    registry = module.load_registry(_write_registry(tmp_path))

    matches = module.classify_changed_paths(registry, [".githooks/pre-commit", "README.md"])

    assert matches == [
        {
            "path": ".githooks/pre-commit",
            "entry_id": "hooks",
            "route": "compatibility_tests",
            "severity": "compatibility_tests",
            "accept_with_inventory_baseline_update": False,
            "required_evidence": ["hook parity test"],
        }
    ]


def test_clean_inventory_and_no_protected_changes_passes(tmp_path: Path) -> None:
    module = _load_module()
    _write_registry(tmp_path)
    baseline = _payload()
    _write_inventory(tmp_path, baseline)

    result = module.evaluate_drift(tmp_path, changed_paths=[], current_inventory=baseline)

    assert result["status"] == "pass"
    assert result["outcome"] == "clean"
    assert result["blocking"] == []


def test_material_inventory_drift_fails_without_baseline_update(tmp_path: Path) -> None:
    module = _load_module()
    _write_registry(tmp_path)
    _write_inventory(tmp_path, _payload(python_version="3.12.0"))

    result = module.evaluate_drift(tmp_path, changed_paths=[], current_inventory=_payload(python_version="3.14.0"))

    assert result["status"] == "fail"
    assert result["blocking"][0]["reason"] == "normalized_inventory_drift"
    assert result["diff_keys"] == ["toolchain"]


def test_inventory_baseline_update_passes_when_current_matches_new_baseline(tmp_path: Path) -> None:
    module = _load_module()
    _write_registry(tmp_path)
    current = _payload(python_version="3.14.0")
    _write_inventory(tmp_path, current)

    result = module.evaluate_drift(
        tmp_path,
        changed_paths=[".groundtruth/inventory/dev-environment-inventory.json"],
        current_inventory=current,
    )

    assert result["status"] == "pass"
    assert result["outcome"] == "accepted_baseline_update"


def test_protected_hook_change_fails_without_review_evidence(tmp_path: Path) -> None:
    module = _load_module()
    _write_registry(tmp_path)
    current = _payload()
    _write_inventory(tmp_path, current)

    result = module.evaluate_drift(tmp_path, changed_paths=[".githooks/pre-commit"], current_inventory=current)

    assert result["status"] == "fail"
    assert result["blocking"][0]["path"] == ".githooks/pre-commit"
    assert result["blocking"][0]["route"] == "compatibility_tests"


def test_protected_hook_change_passes_for_precommit_when_bridge_evidence_is_present(tmp_path: Path) -> None:
    module = _load_module()
    _write_registry(tmp_path)
    current = _payload()
    _write_inventory(tmp_path, current)

    result = module.evaluate_drift(
        tmp_path,
        changed_paths=[".githooks/pre-commit", "bridge/INDEX.md", "bridge/example-003.md"],
        current_inventory=current,
        allow_review_evidence=True,
    )

    assert result["status"] == "pass"
    assert result["outcome"] == "review_evidence_present"
    assert result["review_evidence_present"] is True


def test_changed_path_must_stay_inside_project_root(tmp_path: Path) -> None:
    module = _load_module()
    _write_registry(tmp_path)
    current = _payload()
    _write_inventory(tmp_path, current)

    with pytest.raises(module.DriftCheckError, match="escapes project root"):
        module.evaluate_drift(tmp_path, changed_paths=["../outside.txt"], current_inventory=current)


def test_normalize_inventory_wildcard_strips_all_toolchain_versions() -> None:
    """toolchain.*.version deletes the version key from every tool sub-dict
    while preserving non-version fields; payloads differing only in toolchain
    versions normalize equal (WI-3449 / DELIB-2504)."""
    module = _load_module()
    first = {
        "toolchain": {
            "python": {"version": "3.14.0", "status": "verified"},
            "pytest": {"version": "9.0.3", "status": "verified"},
            "ruff": {"version": "0.15.12", "status": "verified"},
        },
    }
    second = {
        "toolchain": {
            "python": {"version": "3.14.0", "status": "verified"},
            "pytest": {"version": "9.0.2", "status": "verified"},
            "ruff": {"version": "0.15.5", "status": "verified"},
        },
    }
    normalized_first = module.normalize_inventory(first, ["toolchain.*.version"])
    normalized_second = module.normalize_inventory(second, ["toolchain.*.version"])

    for tool in ("python", "pytest", "ruff"):
        assert "version" not in normalized_first["toolchain"][tool]
        assert normalized_first["toolchain"][tool]["status"] == "verified"
    assert normalized_first == normalized_second


def test_exact_volatile_paths_unaffected_by_wildcard_support() -> None:
    """The wildcard extension must preserve exact-match deletion for the
    existing non-wildcard volatile paths (generated_at, redaction.*)."""
    module = _load_module()
    payload = {
        "generated_at": "2026-05-29T00:00:00Z",
        "toolchain": {"python": {"version": "3.14.0"}},
        "redaction": {"status": "pass", "sensitive_environment_entry_count": 7},
    }
    normalized = module.normalize_inventory(payload, ["generated_at", "redaction.sensitive_environment_entry_count"])
    assert "generated_at" not in normalized
    assert "sensitive_environment_entry_count" not in normalized["redaction"]
    assert normalized["redaction"]["status"] == "pass"
    # A non-volatile path is untouched.
    assert normalized["toolchain"]["python"]["version"] == "3.14.0"


def _write_toolchain_volatile_registry(root: Path) -> Path:
    path = root / "config" / "governance" / "protected-artifact-inventory-drift.toml"
    path.parent.mkdir(parents=True)
    path.write_text(
        "\n".join(
            [
                "schema_version = 1",
                'volatile_inventory_paths = ["generated_at", "toolchain.*.version"]',
                "",
                "[[protected_artifacts]]",
                'id = "inventory"',
                'patterns = [".groundtruth/inventory/dev-environment-inventory.json"]',
                'severity = "accepted_baseline_update"',
                'route = "accepted_baseline_update"',
                "accept_with_inventory_baseline_update = true",
                'required_evidence = ["inventory regenerated"]',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def _write_toolchain_availability_volatile_registry(root: Path) -> Path:
    path = root / "config" / "governance" / "protected-artifact-inventory-drift.toml"
    path.parent.mkdir(parents=True)
    path.write_text(
        "\n".join(
            [
                "schema_version = 1",
                (
                    'volatile_inventory_paths = ["generated_at", "toolchain.*.version", '
                    '"toolchain.*.status", "toolchain.*.classification"]'
                ),
                "",
                "[[protected_artifacts]]",
                'id = "inventory"',
                'patterns = [".groundtruth/inventory/dev-environment-inventory.json"]',
                'severity = "accepted_baseline_update"',
                'route = "accepted_baseline_update"',
                "accept_with_inventory_baseline_update = true",
                'required_evidence = ["inventory regenerated"]',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def test_toolchain_version_difference_is_not_material_drift(tmp_path: Path) -> None:
    """End-to-end: with toolchain.*.version volatile, a baseline and a current
    inventory that differ ONLY in toolchain version strings produce no material
    drift (the interpreter-split commit-freeze defect is fixed). WI-3449."""
    module = _load_module()
    _write_toolchain_volatile_registry(tmp_path)
    baseline = {
        "schema_version": 1,
        "generated_at": "2026-05-29T00:00:00Z",
        "toolchain": {
            "pytest": {"version": "9.0.3", "status": "verified"},
            "ruff": {"version": "0.15.12", "status": "verified"},
        },
    }
    current = {
        "schema_version": 1,
        "generated_at": "2026-05-29T01:00:00Z",
        "toolchain": {
            "pytest": {"version": "9.0.2", "status": "verified"},
            "ruff": {"version": "0.15.5", "status": "verified"},
        },
    }
    _write_inventory(tmp_path, baseline)

    result = module.evaluate_drift(tmp_path, changed_paths=[], current_inventory=current)

    assert result["material_inventory_drift"] is False
    assert result["diff_keys"] == []


def test_non_version_toolchain_change_still_gates(tmp_path: Path) -> None:
    """toolchain.*.version must NOT broaden to non-version fields: a status
    change is still material drift. WI-3449."""
    module = _load_module()
    _write_toolchain_volatile_registry(tmp_path)
    baseline = {
        "schema_version": 1,
        "generated_at": "2026-05-29T00:00:00Z",
        "toolchain": {"pytest": {"version": "9.0.3", "status": "verified"}},
    }
    current = {
        "schema_version": 1,
        "generated_at": "2026-05-29T01:00:00Z",
        "toolchain": {"pytest": {"version": "9.0.3", "status": "missing"}},
    }
    _write_inventory(tmp_path, baseline)

    result = module.evaluate_drift(tmp_path, changed_paths=[], current_inventory=current)

    assert result["material_inventory_drift"] is True
    assert result["diff_keys"] == ["toolchain"]


def test_toolchain_availability_flux_with_same_public_probe_evidence_is_not_material_drift(tmp_path: Path) -> None:
    module = _load_module()
    _write_toolchain_availability_volatile_registry(tmp_path)
    baseline = {
        "schema_version": 1,
        "generated_at": "2026-06-02T00:00:00Z",
        "toolchain": {
            "gh": {
                "version": "2.83.2",
                "status": "verified",
                "classification": "verified",
                "evidence": "gh --version",
            }
        },
    }
    current = {
        "schema_version": 1,
        "generated_at": "2026-06-02T01:00:00Z",
        "toolchain": {
            "gh": {
                "version": "unknown",
                "status": "unsupported",
                "classification": "unsupported",
                "evidence": "gh --version",
            }
        },
    }
    _write_inventory(tmp_path, baseline)

    result = module.evaluate_drift(tmp_path, changed_paths=[], current_inventory=current)

    assert result["material_inventory_drift"] is False
    assert result["diff_keys"] == []


def test_toolchain_public_probe_evidence_change_still_gates(tmp_path: Path) -> None:
    module = _load_module()
    _write_toolchain_availability_volatile_registry(tmp_path)
    baseline = {
        "schema_version": 1,
        "generated_at": "2026-06-02T00:00:00Z",
        "toolchain": {
            "gh": {
                "version": "2.83.2",
                "status": "verified",
                "classification": "verified",
                "evidence": "gh --version",
            }
        },
    }
    current = {
        "schema_version": 1,
        "generated_at": "2026-06-02T01:00:00Z",
        "toolchain": {
            "gh": {
                "version": "unknown",
                "status": "unsupported",
                "classification": "unsupported",
                "evidence": "gh version",
            }
        },
    }
    _write_inventory(tmp_path, baseline)

    result = module.evaluate_drift(tmp_path, changed_paths=[], current_inventory=current)

    assert result["material_inventory_drift"] is True
    assert result["diff_keys"] == ["toolchain"]
