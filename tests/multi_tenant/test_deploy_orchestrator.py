"""Tests for deploy_orchestrator.py — deploy-verify-rollback pipeline.

Validates the DeployResult dataclass, step sequencing, dry-run behavior,
health polling, rollback logic, and error handling. All Azure CLI and
network calls are mocked.

WI-1433 / SPEC-1825
(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import json
import subprocess
from unittest.mock import MagicMock, patch


from scripts.deploy_orchestrator import (
    DeployResult,
    _validate_image,
    _health_poll,
    run_deploy,
)


# ---------------------------------------------------------------------------
# DeployResult tests
# ---------------------------------------------------------------------------
class TestDeployResult:
    def test_default_state(self):
        r = DeployResult()
        assert r.status == "pending"
        assert r.environment == ""
        assert r.rollback_performed is False
        assert r.steps == []

    def test_to_json(self):
        r = DeployResult(status="succeeded", environment="staging", version="v1.90.0")
        data = json.loads(r.to_json())
        assert data["status"] == "succeeded"
        assert data["environment"] == "staging"
        assert data["rollback_performed"] is False


# ---------------------------------------------------------------------------
# Validation tests
# ---------------------------------------------------------------------------
class TestValidateImage:
    def test_invalid_version_format(self):
        result = DeployResult()
        ok = _validate_image(result, "1.90.0", False)
        assert not ok
        assert "vX.Y.Z" in result.error

    def test_dry_run_skips_acr_check(self):
        result = DeployResult()
        ok = _validate_image(result, "v1.90.0", True)
        assert ok
        assert any(s["status"] == "skipped" for s in result.steps)

    @patch("scripts.deploy_orchestrator._run")
    def test_image_found_in_acr(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="v1.90.0\n", stderr=""
        )
        result = DeployResult()
        ok = _validate_image(result, "v1.90.0", False)
        assert ok
        assert "v1.90.0" in result.image

    @patch("scripts.deploy_orchestrator._run")
    def test_image_not_found_in_acr(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="\n", stderr=""
        )
        result = DeployResult()
        ok = _validate_image(result, "v1.90.0", False)
        assert not ok
        assert "not found" in result.error


# ---------------------------------------------------------------------------
# Health poll tests
# ---------------------------------------------------------------------------
class TestHealthPoll:
    def test_dry_run_skips_poll(self):
        result = DeployResult()
        ok = _health_poll(result, "staging", "v1.90.0", True)
        assert ok

    @patch("scripts.deploy_orchestrator.HEALTH_TIMEOUT_S", 5)
    @patch("scripts.deploy_orchestrator.HEALTH_POLL_INTERVAL_S", 1)
    @patch("scripts.deploy_orchestrator.urlopen")
    def test_health_timeout(self, mock_urlopen):
        mock_urlopen.side_effect = OSError("Connection refused")
        result = DeployResult()
        ok = _health_poll(result, "staging", "v1.90.0", False)
        assert not ok
        assert "timeout" in result.error.lower()

    @patch("scripts.deploy_orchestrator.urlopen")
    def test_health_success(self, mock_urlopen):
        response = MagicMock()
        response.status = 200
        response.read.return_value = json.dumps({"product_version": "1.90.0"}).encode()
        response.__enter__ = MagicMock(return_value=response)
        response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = response

        result = DeployResult()
        ok = _health_poll(result, "staging", "v1.90.0", False)
        assert ok
        assert any(s["name"] == "health_poll" and s["status"] == "passed"
                    for s in result.steps)


# ---------------------------------------------------------------------------
# Full pipeline tests (dry-run)
# ---------------------------------------------------------------------------
class TestRunDeployDryRun:
    def test_dry_run_succeeds(self):
        result = run_deploy("staging", "v1.90.0", dry_run=True)
        assert result.status == "succeeded"
        assert result.dry_run is True
        assert result.environment == "staging"
        assert result.version == "v1.90.0"
        assert result.duration_s >= 0

    def test_dry_run_production(self):
        result = run_deploy("production", "v1.88.1", dry_run=True)
        assert result.status == "succeeded"
        assert result.environment == "production"

    def test_dry_run_invalid_version(self):
        result = run_deploy("staging", "bad", dry_run=True)
        assert result.status == "failed"

    def test_dry_run_with_e2e(self):
        result = run_deploy("staging", "v1.90.0", dry_run=True, run_e2e=True)
        assert result.status == "succeeded"
        # E2E should be skipped in dry-run
        assert any(s["name"] == "e2e_regression" for s in result.steps)

    def test_dry_run_skip_snapshot(self):
        result = run_deploy("staging", "v1.90.0", dry_run=True, skip_snapshot=True)
        assert result.status == "succeeded"
        # Should NOT have a pre_deploy_snapshot step
        assert not any(s["name"] == "pre_deploy_snapshot" for s in result.steps)


# ---------------------------------------------------------------------------
# Rollback tests
# ---------------------------------------------------------------------------
class TestRollback:
    @patch("scripts.deploy_orchestrator._write_log_file")
    @patch("scripts.deploy_orchestrator._run")
    def test_health_failure_triggers_rollback(self, mock_run, mock_log):
        mock_log.return_value = "test.log"
        call_count = [0]

        def side_effect(cmd, timeout=600):
            call_count[0] += 1
            stdout = ""
            rc = 0

            cmd_str = " ".join(str(c) for c in cmd)

            # show-tags → image found
            if "show-tags" in cmd_str:
                stdout = "v1.90.0\n"
            # upgrade_verification.py phase-a → succeed (for snapshot)
            elif "upgrade_verification" in cmd_str:
                stdout = "Phase A complete\n"
            # containerapp show → current image (for rollback reference)
            elif "containerapp" in cmd_str and "show" in cmd_str:
                stdout = "acragentredeastus.azurecr.io/api-gateway:v1.88.1\n"
            # containerapp update (deploy) → succeed
            elif "containerapp" in cmd_str and "update" in cmd_str:
                stdout = "Updated\n"

            return subprocess.CompletedProcess(args=cmd, returncode=rc, stdout=stdout, stderr="")

        mock_run.side_effect = side_effect

        # Make health poll fail by patching urlopen
        with patch("scripts.deploy_orchestrator.urlopen", side_effect=OSError), \
             patch("scripts.deploy_orchestrator.HEALTH_TIMEOUT_S", 2), \
             patch("scripts.deploy_orchestrator.HEALTH_POLL_INTERVAL_S", 1), \
             patch("scripts.deploy_orchestrator.Path.exists", return_value=True):
            result = run_deploy("staging", "v1.90.0", skip_snapshot=True)

        # Should have attempted rollback
        assert result.status in ("rolled_back", "failed")
        assert any(s["name"] == "rollback" for s in result.steps)


# ---------------------------------------------------------------------------
# JSON serialization tests
# ---------------------------------------------------------------------------
class TestDeployResultSerialization:
    def test_json_roundtrip(self):
        result = DeployResult(
            status="succeeded",
            environment="staging",
            version="v1.90.0",
            verification_pass=70,
            verification_fail=0,
        )
        data = json.loads(result.to_json())
        assert data["verification_pass"] == 70
        assert data["verification_fail"] == 0
        assert data["rollback_performed"] is False

    def test_rolled_back_json(self):
        result = DeployResult(
            status="rolled_back",
            rollback_performed=True,
            rollback_status="succeeded",
            previous_image="acragentredeastus.azurecr.io/api-gateway:v1.88.1",
        )
        data = json.loads(result.to_json())
        assert data["status"] == "rolled_back"
        assert data["rollback_performed"] is True
        assert data["previous_image"].endswith("v1.88.1")


# ---------------------------------------------------------------------------
# Step recording tests
# ---------------------------------------------------------------------------
class TestStepRecording:
    def test_dry_run_records_all_steps(self):
        result = run_deploy("staging", "v1.90.0", dry_run=True)
        step_names = [s["name"] for s in result.steps]
        assert "validate_image" in step_names
        assert "deploy" in step_names
        assert "health_poll" in step_names

    def test_failed_validation_records_step(self):
        result = run_deploy("staging", "bad-version", dry_run=True)
        assert len(result.steps) >= 1
        assert result.steps[0]["status"] == "failed"
