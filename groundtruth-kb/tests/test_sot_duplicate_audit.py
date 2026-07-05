from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from groundtruth_kb.cli import main
from groundtruth_kb.project.sot_audit import run_duplicate_sot_audit


def _registry_record(record_id: str, storage_path: str, *, domain: str = "control_surface") -> str:
    return f"""
[[artifacts]]
id = "{record_id}"
domain = "{domain}"
lifecycle = "active"
storage_path = "{storage_path}"
authority_spec_id = "GOV-X"
mutation_api = "test fixture"
versioning_policy = "git_tracked"
backup_policy = "git_tracked"
health_check_function = ""
owner_role = "shared"
""".lstrip()


def _write_registry(root: Path, extra_records: str = "") -> None:
    registry = root / "config" / "registry" / "sot-artifacts.toml"
    registry.parent.mkdir(parents=True, exist_ok=True)
    registry.write_text(
        _registry_record("sot-registry-toml", "config/registry/sot-artifacts.toml") + extra_records,
        encoding="utf-8",
    )


def _write_groundtruth_toml(root: Path) -> Path:
    config = root / "groundtruth.toml"
    config.write_text(
        f'[groundtruth]\ndb_path = "{(root / "groundtruth.db").as_posix()}"\nproject_root = "{root.as_posix()}"\n',
        encoding="utf-8",
    )
    return config


def _write_dispatch_duplicate(root: Path) -> None:
    (root / "config" / "dispatcher").mkdir(parents=True, exist_ok=True)
    (root / "harness-state").mkdir(parents=True, exist_ok=True)
    (root / "config" / "dispatcher" / "rules.toml").write_text(
        """
[harnesses.A]
can_fire_events = true
can_receive_dispatch = true
dispatch_availability = 75
dispatch_cost = 20
dispatch_quality = 95
""".lstrip(),
        encoding="utf-8",
    )
    (root / "harness-state" / "harness-registry.json").write_text(
        json.dumps(
            {
                "harnesses": [
                    {
                        "id": "A",
                        "can_fire_events": True,
                        "can_receive_dispatch": True,
                        "dispatch_availability": 75,
                        "dispatch_cost": 20,
                        "dispatch_quality": 95,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )


def test_audit_classifies_dispatch_duplicate_as_existing_wi5012_violation(tmp_path: Path) -> None:
    _write_registry(
        tmp_path,
        _registry_record("harness-registry", "harness-state/harness-registry.json", domain="harness_state"),
    )
    _write_dispatch_duplicate(tmp_path)

    report = run_duplicate_sot_audit(tmp_path)

    assert report.coverage_complete is True
    duplicate = next(
        candidate for candidate in report.candidates if candidate.candidate_id == "duplicate-dispatch-harness-fields"
    )
    assert duplicate.classification == "duplicate_sot_violation"
    assert duplicate.remediation_work_item_id == "WI-5012"
    assert duplicate.remediation_status == "existing_covering_work_item"
    assert duplicate.duplicated_fields == (
        "can_fire_events",
        "can_receive_dispatch",
        "dispatch_availability",
        "dispatch_cost",
        "dispatch_quality",
    )


def test_audit_accepts_machine_checkable_derived_cache(tmp_path: Path) -> None:
    _write_registry(tmp_path, _registry_record("authority-json", "authority.json"))
    (tmp_path / "authority.json").write_text('{"answer": 42}\n', encoding="utf-8")
    (tmp_path / "cache.json").write_text(
        json.dumps(
            {
                "cache_kind": "derived_sot_cache",
                "derived_from": "authority-json",
                "generated_by": "pytest",
                "generated_at": "2026-07-05T00:00:00Z",
                "ttl_seconds": 300,
                "expires_at": "2026-07-05T00:05:00Z",
                "source_hash": "sha256:source",
                "cache_hash": "sha256:cache",
                "usage_context": "unit test read path",
                "read_only": True,
                "non_authoritative": True,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    report = run_duplicate_sot_audit(tmp_path)

    cache = next(
        candidate for candidate in report.candidates if candidate.candidate_id == "permitted-derived-cache:cache.json"
    )
    assert cache.classification == "permitted_derived_cache"
    assert cache.registry_ids == ("authority-json",)


def test_audit_rejects_incomplete_derived_cache_contract(tmp_path: Path) -> None:
    _write_registry(tmp_path, _registry_record("authority-json", "authority.json"))
    (tmp_path / "authority.json").write_text('{"answer": 42}\n', encoding="utf-8")
    (tmp_path / "cache.json").write_text(
        json.dumps(
            {
                "cache_kind": "derived_sot_cache",
                "derived_from": "authority-json",
                "generated_by": "pytest",
                "generated_at": "2026-07-05T00:00:00Z",
                "ttl_seconds": 300,
                "expires_at": "2026-07-05T00:05:00Z",
                "cache_hash": "sha256:cache",
                "usage_context": "unit test read path",
                "non_authoritative": True,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    report = run_duplicate_sot_audit(tmp_path)

    cache = next(
        candidate for candidate in report.candidates if candidate.candidate_id == "invalid-derived-cache:cache.json"
    )
    assert cache.classification == "duplicate_sot_violation"
    assert "read_only" in cache.duplicated_fields
    assert cache.remediation_work_item_id is None


def test_registry_audit_duplicates_cli_emits_json(tmp_path: Path) -> None:
    _write_groundtruth_toml(tmp_path)
    _write_registry(
        tmp_path,
        _registry_record("harness-registry", "harness-state/harness-registry.json", domain="harness_state"),
    )
    _write_dispatch_duplicate(tmp_path)

    result = CliRunner().invoke(
        main,
        ["--config", str(tmp_path / "groundtruth.toml"), "registry", "audit-duplicates", "--json", "--no-write"],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["coverage_complete"] is True
    assert payload["violation_count"] == 1
    assert payload["uncovered_violation_count"] == 0
