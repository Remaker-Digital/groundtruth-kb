# Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Managed-artifact drift checks for ``gt project doctor``."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from groundtruth_kb.project import doctor
from groundtruth_kb.project.managed_registry import (
    FileArtifact,
    GitignorePattern,
    OwnershipMeta,
    SettingsHookRegistration,
)


def _ownership(policy: str = "warn") -> OwnershipMeta:
    return OwnershipMeta(
        ownership="gt-kb-managed",
        upgrade_policy="overwrite",
        adopter_divergence_policy=policy,  # type: ignore[arg-type]
        notes="test ownership",
    )


def _file_artifact(policy: str = "warn") -> FileArtifact:
    return FileArtifact(
        class_="hook",
        id=f"hook.sample.{policy}",
        template_path="hooks/sample.py",
        target_path=".claude/hooks/sample.py",
        initial_profiles=("dual-agent",),
        managed_profiles=("dual-agent",),
        doctor_required_profiles=("dual-agent",),
        ownership=_ownership(policy),
    )


def _patch_registry(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, artifacts: list[object]) -> Path:
    templates = tmp_path / "templates"
    monkeypatch.setattr(doctor, "get_templates_dir", lambda: templates)
    monkeypatch.setattr(doctor, "artifacts_for_doctor", lambda _profile, class_=None: artifacts)
    return templates


def test_clean_managed_artifacts_report_pass(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    artifact = _file_artifact()
    templates = _patch_registry(monkeypatch, tmp_path, [artifact])
    templates.joinpath("hooks").mkdir(parents=True)
    templates.joinpath("hooks/sample.py").write_text("print('ok')\n", encoding="utf-8")
    tmp_path.joinpath(".claude/hooks").mkdir(parents=True)
    tmp_path.joinpath(".claude/hooks/sample.py").write_text("print('ok')\n", encoding="utf-8")

    check = doctor._check_managed_artifact_drift(tmp_path, "dual-agent")

    assert check.status == "pass"
    assert "current=1" in check.message


def test_missing_managed_file_reports_fail(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    artifact = _file_artifact()
    templates = _patch_registry(monkeypatch, tmp_path, [artifact])
    templates.joinpath("hooks").mkdir(parents=True)
    templates.joinpath("hooks/sample.py").write_text("print('ok')\n", encoding="utf-8")

    check = doctor._check_managed_artifact_drift(tmp_path, "dual-agent")

    assert check.status == "fail"
    assert "missing=1" in check.message
    assert ".claude/hooks/sample.py missing" in check.message


def test_modified_file_with_warn_policy_reports_warning(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    artifact = _file_artifact(policy="warn")
    templates = _patch_registry(monkeypatch, tmp_path, [artifact])
    templates.joinpath("hooks").mkdir(parents=True)
    templates.joinpath("hooks/sample.py").write_text("print('template')\n", encoding="utf-8")
    tmp_path.joinpath(".claude/hooks").mkdir(parents=True)
    tmp_path.joinpath(".claude/hooks/sample.py").write_text("print('adopter')\n", encoding="utf-8")

    check = doctor._check_managed_artifact_drift(tmp_path, "dual-agent")

    assert check.status == "warning"
    assert "drifted=1" in check.message


def test_modified_file_with_error_policy_reports_fail(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    artifact = _file_artifact(policy="error")
    templates = _patch_registry(monkeypatch, tmp_path, [artifact])
    templates.joinpath("hooks").mkdir(parents=True)
    templates.joinpath("hooks/sample.py").write_text("print('template')\n", encoding="utf-8")
    tmp_path.joinpath(".claude/hooks").mkdir(parents=True)
    tmp_path.joinpath(".claude/hooks/sample.py").write_text("print('adopter')\n", encoding="utf-8")

    check = doctor._check_managed_artifact_drift(tmp_path, "dual-agent")

    assert check.status == "fail"
    assert "drifted=1" in check.message


def test_missing_settings_hook_registration_is_included(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    registration = SettingsHookRegistration(
        class_="settings-hook-registration",
        id="settings.hook.sample.pretooluse",
        event="PreToolUse",
        hook_filename="sample.py",
        target_settings_path=".claude/settings.json",
        initial_profiles=("dual-agent",),
        managed_profiles=("dual-agent",),
        doctor_required_profiles=("dual-agent",),
        ownership=_ownership("warn"),
    )
    _patch_registry(monkeypatch, tmp_path, [registration])
    tmp_path.joinpath(".claude").mkdir()
    tmp_path.joinpath(".claude/settings.json").write_text(json.dumps({"hooks": {}}), encoding="utf-8")

    check = doctor._check_managed_artifact_drift(tmp_path, "dual-agent")

    assert check.status == "warning"
    assert "registration-missing=1" in check.message
    assert "sample.py missing" in check.message


def test_missing_gitignore_pattern_is_included(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pattern = GitignorePattern(
        class_="gitignore-pattern",
        id="gitignore.hook-logs",
        pattern=".claude/hooks/*.log",
        comment="Ignore hook logs.",
        initial_profiles=("dual-agent",),
        managed_profiles=("dual-agent",),
        doctor_required_profiles=("dual-agent",),
        ownership=_ownership("warn"),
    )
    _patch_registry(monkeypatch, tmp_path, [pattern])
    tmp_path.joinpath(".gitignore").write_text("# project ignores\n", encoding="utf-8")

    check = doctor._check_managed_artifact_drift(tmp_path, "dual-agent")

    assert check.status == "warning"
    assert "gitignore-missing=1" in check.message
    assert ".claude/hooks/*.log" in check.message


def test_registry_load_failure_is_explicit_fail(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_registry(_profile: str, class_: str | None = None) -> list[object]:
        raise ValueError("bad registry")

    monkeypatch.setattr(doctor, "artifacts_for_doctor", fail_registry)

    check = doctor._check_managed_artifact_drift(tmp_path, "dual-agent")

    assert check.status == "fail"
    assert check.found is False
    assert "bad registry" in check.message


def test_profile_with_no_doctor_required_artifacts_reports_info(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_registry(monkeypatch, tmp_path, [])

    check = doctor._check_managed_artifact_drift(tmp_path, "custom")

    assert check.status == "info"
    assert check.required is False
    assert "no doctor-required managed artifacts" in check.message


def test_managed_artifact_drift_crlf_normalized_passes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """CRLF live file and LF template with identical content must not be reported as drift."""
    artifact = _file_artifact()
    templates = _patch_registry(monkeypatch, tmp_path, [artifact])
    templates.joinpath("hooks").mkdir(parents=True)
    lf_content = b"print('ok')\nprint('line2')\n"
    templates.joinpath("hooks/sample.py").write_bytes(lf_content)
    tmp_path.joinpath(".claude/hooks").mkdir(parents=True)
    crlf_content = lf_content.replace(b"\n", b"\r\n")
    tmp_path.joinpath(".claude/hooks/sample.py").write_bytes(crlf_content)

    check = doctor._check_managed_artifact_drift(tmp_path, "dual-agent")

    assert check.status == "pass"
    assert "current=1" in check.message
