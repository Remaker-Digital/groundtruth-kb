"""Tests for the WI-4466 ``gt`` CLI availability doctor check.

Per ``bridge/gtkb-wi4466-gt-cli-availability-doctor-check-001.md`` (NEW) and
``-002`` (Codex GO). Covers the GO's required evidence: PATH-present pass,
missing-PATH + canonical in-root venv fallback warning, genuinely-unavailable
fail, dynamic registry discovery, and fallback-path consistency with
``scripts.install_gt_path_shim.resolve_venv_gt_exe``.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import install_gt_path_shim  # noqa: E402
from groundtruth_kb.project.checks import get_registered_checks  # noqa: E402
from groundtruth_kb.project.checks import gt_cli_availability as helper  # noqa: E402


def test_gt_on_path_passes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """gt resolvable on PATH yields a deterministic pass naming the path."""
    fake = str(tmp_path / "onpath" / "gt")
    monkeypatch.setattr(shutil, "which", lambda name: fake if name == "gt" else None)
    result = helper.check_gt_cli_availability(tmp_path)
    assert result.status == "pass"
    assert result.found is True
    assert fake in result.message


def test_venv_fallback_warns(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Not on PATH but canonical in-root venv launcher present -> warning."""
    monkeypatch.setattr(shutil, "which", lambda name: None)
    venv_gt = install_gt_path_shim.resolve_venv_gt_exe(tmp_path, sys.platform)
    venv_gt.parent.mkdir(parents=True, exist_ok=True)
    venv_gt.write_text("launcher", encoding="utf-8")
    result = helper.check_gt_cli_availability(tmp_path)
    assert result.status == "warning"
    assert result.found is True
    assert "not on PATH" in result.message
    assert "python -m groundtruth_kb" in result.message


def test_unavailable_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Neither on PATH nor an in-root venv launcher -> fail (missing CLI caught)."""
    monkeypatch.setattr(shutil, "which", lambda name: None)
    result = helper.check_gt_cli_availability(tmp_path)
    assert result.status == "fail"
    assert result.found is False
    assert "unavailable" in result.message


def test_check_is_registered() -> None:
    """The check is auto-discovered by the doctor registry (ADR-REGISTRY-DISCOVERY-001)."""
    assert "gt_cli_availability" in get_registered_checks()


def test_fallback_path_matches_shim_generator(tmp_path: Path) -> None:
    """The check's fallback path equals the WI-4530 generator's venv path (no drift)."""
    assert helper._venv_gt_path(tmp_path, sys.platform) == install_gt_path_shim.resolve_venv_gt_exe(
        tmp_path, sys.platform
    )


def test_check_is_advisory_required_false(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The check is required=False (developer-environment quality, not a hard gate)."""
    monkeypatch.setattr(shutil, "which", lambda name: None)
    result = helper.check_gt_cli_availability(tmp_path)
    assert result.required is False
    assert result.name
