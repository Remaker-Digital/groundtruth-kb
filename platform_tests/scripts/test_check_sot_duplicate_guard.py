# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for the duplicate-SoT doctor guard (WI-5015)."""

from __future__ import annotations

import dataclasses
import inspect
import json
from pathlib import Path

import groundtruth_kb.project.doctor as doctor_mod
import groundtruth_kb.project.sot_audit as sot_audit
import pytest
from groundtruth_kb.project.doctor import _check_sot_duplicate_guard
from groundtruth_kb.project.sot_audit import run_duplicate_sot_audit


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


def _write_registry(root: Path, records: str) -> None:
    registry = root / "config" / "registry" / "sot-artifacts.toml"
    registry.parent.mkdir(parents=True, exist_ok=True)
    registry.write_text(records, encoding="utf-8")


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


def _violations(root: Path) -> dict[str, sot_audit.AuditCandidate]:
    report = run_duplicate_sot_audit(root)
    return {c.candidate_id: c for c in report.candidates if c.classification != "registered_sot"}


def _guard_with_complete_membership(root: Path, monkeypatch: pytest.MonkeyPatch):
    """The doctor's translation of the engine's report once registry membership is complete.

    Membership completeness needs a whole project (baseline root, authority, Git inventory); the engine's
    classification of these fixtures is measured directly above, and here the same report is handed to the doctor
    with membership declared complete so its pass/fail translation is exercised.
    """
    report = dataclasses.replace(run_duplicate_sot_audit(root), registry_membership_complete=True)
    monkeypatch.setattr(sot_audit, "run_duplicate_sot_audit", lambda target: report)
    return _check_sot_duplicate_guard(root)


def test_duplicate_guard_passes_with_complete_clean_baseline(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write_registry(tmp_path, _registry_record("authority-json", "authority.json"))
    (tmp_path / "authority.json").write_text('{"answer": 42}\n', encoding="utf-8")

    assert _violations(tmp_path) == {}
    result = _guard_with_complete_membership(tmp_path, monkeypatch)

    assert result.status == "pass", result.message
    assert "coverage complete" in result.message
    assert "no duplicate-SoT violations" in result.message


def test_duplicate_guard_reports_incomplete_membership_before_any_verdict(tmp_path: Path) -> None:
    """A minimal fixture has no complete registry membership; the guard says so instead of judging duplicates."""
    _write_registry(tmp_path, _registry_record("authority-json", "authority.json"))
    (tmp_path / "authority.json").write_text('{"answer": 42}\n', encoding="utf-8")

    result = _check_sot_duplicate_guard(tmp_path)

    assert result.status == "fail" and result.required is True
    assert "baseline incomplete" in result.message and "registered_file_count=" in result.message


def test_duplicate_guard_fails_when_baseline_is_unavailable(tmp_path: Path) -> None:
    result = _check_sot_duplicate_guard(tmp_path)

    assert result.status == "fail"
    assert result.required is True
    assert "baseline unavailable" in result.message


def test_duplicate_guard_accepts_machine_checkable_derived_cache(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
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

    assert _violations(tmp_path)["permitted-derived-cache:cache.json"].classification == "permitted_derived_cache"
    result = _guard_with_complete_membership(tmp_path, monkeypatch)

    assert result.status == "pass", result.message


def test_duplicate_guard_fails_uncovered_invalid_derived_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
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

    violation = _violations(tmp_path)["invalid-derived-cache:cache.json"]
    assert violation.classification == "duplicate_sot_violation" and "read_only" in violation.duplicated_fields
    result = _guard_with_complete_membership(tmp_path, monkeypatch)

    assert result.status == "fail"
    assert "persistent duplicate-SoT violation" in result.message
    assert "invalid-derived-cache:cache.json" in result.message
    assert "read_only" in result.message


def test_duplicate_guard_fails_on_known_covered_dispatch_duplicate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_registry(
        tmp_path,
        _registry_record("harness-registry", "harness-state/harness-registry.json", domain="harness_state"),
    )
    _write_dispatch_duplicate(tmp_path)

    violation = _violations(tmp_path)["duplicate-dispatch-harness-fields"]
    assert violation.classification == "duplicate_sot_violation"
    assert set(violation.paths) == {"config/dispatcher/rules.toml", "harness-state/harness-registry.json"}
    result = _guard_with_complete_membership(tmp_path, monkeypatch)

    assert result.status == "fail"
    assert result.required is True
    assert "persistent duplicate-SoT violation" in result.message
    assert "duplicate-dispatch-harness-fields" in result.message


def test_run_doctor_bridge_profile_wires_duplicate_guard() -> None:
    source = inspect.getsource(doctor_mod.run_doctor)

    assert "_check_sot_duplicate_guard(target)" in source
