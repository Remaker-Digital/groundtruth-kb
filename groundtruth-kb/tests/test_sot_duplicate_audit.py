from __future__ import annotations

import json
from pathlib import Path

import pytest

from groundtruth_kb.project import sot_audit
from groundtruth_kb.project.sot_audit import run_duplicate_sot_audit


@pytest.fixture(autouse=True)
def _complete_registry_membership(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        sot_audit,
        "reconcile_artifact_membership",
        lambda _root: {
            "membership_complete": True,
            "counts": {
                "registered": 3,
                "unregistered_load_bearing": 0,
                "unregistered_disposable": 0,
                "invalid_unknown": 0,
            },
        },
    )


def _registry_record(record_id: str, storage_path: str, *, domain: str = "control_surface") -> str:
    return f"""
[[artifacts]]
id = "{record_id}"
domain = "{domain}"
lifecycle = "active"
storage_path = "{storage_path}"
coverage_mode = "exact"
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


@pytest.mark.parametrize("storage", ["ordinary-missing.json", ".gtkb-state/missing.json"])
def test_unresolved_registered_artifact_makes_coverage_incomplete(tmp_path, storage):
    _write_registry(tmp_path, _registry_record("missing", storage))
    report = run_duplicate_sot_audit(tmp_path)
    assert report.registry_membership_complete is True
    assert report.coverage_complete is False
    assert report.missing_registry_artifacts[0]["storage_path"] == storage
    assert not (tmp_path / storage).exists()


def test_retired_audit_output_has_no_census_exemption(tmp_path):
    path = tmp_path / ".gtkb-state/sot-singleton-audit/report.json"
    path.parent.mkdir(parents=True)
    path.write_text("{}", encoding="utf-8")
    assert path.relative_to(tmp_path).as_posix() in sot_audit._iter_persistent_files(tmp_path)
