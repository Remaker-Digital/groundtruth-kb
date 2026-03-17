"""Tests for build_orchestrator.py — ACR build + tag + verify pipeline.

Validates the BuildResult dataclass, step sequencing, dry-run behavior,
and error handling. All Azure CLI calls are mocked.

WI-1437 / SPEC-1825
(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import json
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from scripts.build_orchestrator import (
    BuildResult,
    _get_git_sha,
    _validate_prerequisites,
    run_build,
)


# ---------------------------------------------------------------------------
# BuildResult tests
# ---------------------------------------------------------------------------
class TestBuildResult:
    def test_default_state(self):
        r = BuildResult()
        assert r.status == "pending"
        assert r.version == ""
        assert r.steps == []

    def test_to_json(self):
        r = BuildResult(status="succeeded", version="v1.90.0")
        data = json.loads(r.to_json())
        assert data["status"] == "succeeded"
        assert data["version"] == "v1.90.0"
        assert isinstance(data["steps"], list)


# ---------------------------------------------------------------------------
# Validation tests
# ---------------------------------------------------------------------------
class TestValidatePrerequisites:
    def test_invalid_version_format(self):
        result = BuildResult()
        ok = _validate_prerequisites(result, "1.90.0", False)
        assert not ok
        assert "vX.Y.Z" in result.error

    def test_invalid_version_format_alpha(self):
        result = BuildResult()
        ok = _validate_prerequisites(result, "v1.90.0-beta", False)
        assert not ok

    @patch("scripts.build_orchestrator.DOCKERFILE")
    def test_missing_dockerfile(self, mock_dockerfile):
        mock_dockerfile.is_file.return_value = False
        result = BuildResult()
        ok = _validate_prerequisites(result, "v1.90.0", False)
        assert not ok
        assert "Dockerfile" in result.error

    @patch("scripts.build_orchestrator.DOCKERFILE")
    def test_valid_prerequisites(self, mock_dockerfile):
        mock_dockerfile.is_file.return_value = True
        result = BuildResult()
        ok = _validate_prerequisites(result, "v1.90.0", False)
        assert ok
        assert result.error == ""


# ---------------------------------------------------------------------------
# Git SHA tests
# ---------------------------------------------------------------------------
class TestGetGitSha:
    @patch("scripts.build_orchestrator.subprocess.run")
    def test_returns_sha(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="a1b2c3d4\n"
        )
        assert _get_git_sha() == "a1b2c3d4"

    @patch("scripts.build_orchestrator.subprocess.run")
    def test_returns_empty_on_failure(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=1, stdout=""
        )
        assert _get_git_sha() == ""

    @patch("scripts.build_orchestrator.subprocess.run", side_effect=OSError)
    def test_returns_empty_on_exception(self, mock_run):
        assert _get_git_sha() == ""


# ---------------------------------------------------------------------------
# Full pipeline tests (dry-run)
# ---------------------------------------------------------------------------
class TestRunBuildDryRun:
    @patch("scripts.build_orchestrator.DOCKERFILE")
    def test_dry_run_succeeds(self, mock_dockerfile):
        mock_dockerfile.is_file.return_value = True
        result = run_build("v1.90.0", dry_run=True)
        assert result.status == "succeeded"
        assert result.dry_run is True
        assert result.version == "v1.90.0"
        assert result.duration_s >= 0
        assert len(result.steps) >= 3  # validate, acr_access, acr_build at minimum

    @patch("scripts.build_orchestrator.DOCKERFILE")
    def test_dry_run_sets_timestamps(self, mock_dockerfile):
        mock_dockerfile.is_file.return_value = True
        result = run_build("v1.90.0", dry_run=True)
        assert result.started_at != ""
        assert result.completed_at != ""

    def test_dry_run_invalid_version_fails(self):
        result = run_build("bad-version", dry_run=True)
        assert result.status == "failed"
        assert "vX.Y.Z" in result.error


# ---------------------------------------------------------------------------
# Full pipeline tests (mocked Azure CLI)
# ---------------------------------------------------------------------------
class TestRunBuildMocked:
    @patch("scripts.build_orchestrator._get_git_sha", return_value="abc12345")
    @patch("scripts.build_orchestrator._run")
    @patch("scripts.build_orchestrator.DOCKERFILE")
    def test_full_success(self, mock_dockerfile, mock_run, mock_sha):
        mock_dockerfile.is_file.return_value = True

        def side_effect(cmd, timeout=600):
            stdout = ""
            # ACR show → name
            if "acr" in cmd and "show" in cmd:
                stdout = "acragentredeastus\n"
            # ACR build
            elif "acr" in cmd and "build" in cmd:
                stdout = "Build succeeded\n"
            # list-runs status
            elif "list-runs" in cmd and "status" in str(cmd):
                stdout = "Succeeded\n"
            # list-runs runId
            elif "list-runs" in cmd and "runId" in str(cmd):
                stdout = "ca99\n"
            # show-tags
            elif "show-tags" in cmd:
                stdout = "v1.90.0\n"
            # acr import (SHA tag)
            elif "import" in cmd:
                stdout = ""
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout=stdout, stderr="")

        mock_run.side_effect = side_effect
        result = run_build("v1.90.0")
        assert result.status == "succeeded"
        assert result.acr_run_id == "ca99"
        assert result.git_sha == "abc12345"

    @patch("scripts.build_orchestrator._run")
    @patch("scripts.build_orchestrator.DOCKERFILE")
    def test_acr_access_failure(self, mock_dockerfile, mock_run):
        mock_dockerfile.is_file.return_value = True
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=1, stdout="", stderr=""
        )
        result = run_build("v1.90.0")
        assert result.status == "failed"
        assert "ACR access" in result.error

    @patch("scripts.build_orchestrator._run")
    @patch("scripts.build_orchestrator.DOCKERFILE")
    def test_build_failure_status_not_succeeded(self, mock_dockerfile, mock_run):
        mock_dockerfile.is_file.return_value = True
        call_count = [0]

        def side_effect(cmd, timeout=600):
            call_count[0] += 1
            # First call: acr show → success
            if call_count[0] == 1:
                return subprocess.CompletedProcess(
                    args=cmd, returncode=0, stdout="acragentredeastus\n", stderr=""
                )
            # Second call: acr build → returns ok
            if call_count[0] == 2:
                return subprocess.CompletedProcess(
                    args=cmd, returncode=0, stdout="", stderr=""
                )
            # Third call: list-runs status → Failed
            if call_count[0] == 3:
                return subprocess.CompletedProcess(
                    args=cmd, returncode=0, stdout="Failed\n", stderr=""
                )
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

        mock_run.side_effect = side_effect
        result = run_build("v1.90.0")
        assert result.status == "failed"
        assert "ACR build status" in result.error


# ---------------------------------------------------------------------------
# JSON serialization tests
# ---------------------------------------------------------------------------
class TestBuildResultSerialization:
    def test_json_roundtrip(self):
        result = BuildResult(
            status="succeeded",
            version="v1.90.0",
            image="acragentredeastus.azurecr.io/api-gateway:v1.90.0",
            acr_run_id="ca99",
            git_sha="abc12345",
        )
        data = json.loads(result.to_json())
        assert data["status"] == "succeeded"
        assert data["image"].endswith("v1.90.0")
        assert data["acr_run_id"] == "ca99"

    def test_steps_in_json(self):
        result = BuildResult()
        result.steps.append({"name": "test", "status": "passed"})
        data = json.loads(result.to_json())
        assert len(data["steps"]) == 1
        assert data["steps"][0]["name"] == "test"
