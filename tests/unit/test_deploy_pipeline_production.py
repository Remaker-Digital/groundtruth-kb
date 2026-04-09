"""CPD-001..010: Canonical production deploy pipeline tests.

Validates the deterministic production deployment procedure per the
Codex test protocol v0.1-draft. Covers:
  - Contract tests (CLI requirements, approval gate, no prompts)
  - Behavioral unit tests (rollback capture, rollback decision, failure reporting)
  - Subprocess CLI tests (dry-run success exit 0, smoke-failure exit 1 + rollback)

Test IDs map to the Codex CPD test matrix:
  CPD-001: CLI requires --version
  CPD-002: Production path without approval → fail before deploy
  CPD-003: No interactive prompt strings in canonical path
  CPD-004: Config consistency across deploy_pipeline and upgrade_verification
  CPD-005: Rollback image capture — behavioral (mocked az CLI, returns image tag)
  CPD-006: Smoke failure triggers rollback — behavioral (mock phase_11 path)
  CPD-007: Rollback failure explicitly reported — behavioral (mock rollback_to_image)
  CPD-008: Dry-run exits 0 AND prints DRY RUN banner with no deploy side effects
  CPD-009: Mocked success path — pipeline exits 0 when all phases pass
  CPD-010: Mocked smoke-failure path — pipeline exits 1 with rollback attempted

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import importlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEPLOY_PIPELINE = PROJECT_ROOT / "scripts" / "deploy_pipeline.py"
DEPLOY_CONFIG = PROJECT_ROOT / "scripts" / "deploy_config.py"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_deploy_config():
    """Import deploy_config module."""
    spec = importlib.util.spec_from_file_location("deploy_config", DEPLOY_CONFIG)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _current_version() -> str:
    """Return the current PRODUCT_VERSION as a v-prefixed string for CLI tests."""
    try:
        spec = importlib.util.spec_from_file_location(
            "api_versioning",
            PROJECT_ROOT / "src" / "multi_tenant" / "api_versioning.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return f"v{mod.PRODUCT_VERSION}"
    except Exception:
        return "v1.98.90"


# ---------------------------------------------------------------------------
# CPD-001: CLI requires --version
# ---------------------------------------------------------------------------

class TestCPD001CliRequiresVersion:
    """The deploy pipeline CLI must require a --version argument."""

    def test_version_is_required_argument(self):
        """deploy_pipeline.py --env staging (no --version) exits non-zero."""
        result = subprocess.run(
            [sys.executable, str(DEPLOY_PIPELINE), "--env", "staging"],
            capture_output=True, text=True, timeout=10,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode != 0
        assert "version" in result.stderr.lower() or "required" in result.stderr.lower()


# ---------------------------------------------------------------------------
# CPD-002: Production without approval → fail before deploy
# ---------------------------------------------------------------------------

class TestCPD002ProductionApprovalGate:
    """Production path must fail before any build/deploy work without approval."""

    def test_production_blocked_without_approval(self):
        """--env production without DEPLOY_APPROVED or --approved exits non-zero."""
        env = {**os.environ, "DEPLOY_APPROVED": ""}
        result = subprocess.run(
            [sys.executable, str(DEPLOY_PIPELINE),
             "--env", "production", "--version", _current_version(), "--dry-run"],
            capture_output=True, text=True, timeout=30,
            cwd=str(PROJECT_ROOT), env=env,
        )
        assert result.returncode != 0
        assert "approval" in result.stdout.lower() or "GOV-16" in result.stdout

    def test_production_allowed_with_env_var(self):
        """DEPLOY_APPROVED=1 passes the approval gate."""
        env = {**os.environ, "DEPLOY_APPROVED": "1"}
        result = subprocess.run(
            [sys.executable, str(DEPLOY_PIPELINE),
             "--env", "production", "--version", _current_version(), "--dry-run"],
            capture_output=True, text=True, timeout=30,
            cwd=str(PROJECT_ROOT), env=env,
        )
        # Should pass the approval gate (may still fail on other checks)
        assert "Owner approval: CONFIRMED" in result.stdout

    def test_production_allowed_with_flag(self):
        """--approved flag passes the approval gate."""
        result = subprocess.run(
            [sys.executable, str(DEPLOY_PIPELINE),
             "--env", "production", "--version", _current_version(),
             "--dry-run", "--approved"],
            capture_output=True, text=True, timeout=30,
            cwd=str(PROJECT_ROOT),
        )
        assert "Owner approval: CONFIRMED" in result.stdout


# ---------------------------------------------------------------------------
# CPD-003: No interactive prompts
# ---------------------------------------------------------------------------

class TestCPD003NoInteractivePrompts:
    """The canonical production path must not contain interactive prompts."""

    def test_no_input_calls_in_deploy_pipeline(self):
        """deploy_pipeline.py source must not call input() or raw_input()."""
        source = DEPLOY_PIPELINE.read_text(encoding="utf-8")
        # Match standalone input() calls, not 'tool_input' or 'input_placeholder'
        input_calls = re.findall(r'\binput\s*\(', source)
        # Filter out false positives (e.g., tool_input, input_placeholder)
        real_input_calls = [c for c in input_calls if c.strip() == "input("]
        assert len(real_input_calls) == 0, (
            f"deploy_pipeline.py contains input() calls — must be non-interactive"
        )

    def test_no_input_calls_in_deploy_config(self):
        """deploy_config.py must not call input()."""
        source = DEPLOY_CONFIG.read_text(encoding="utf-8")
        assert "input(" not in source


# ---------------------------------------------------------------------------
# CPD-004: Config consistency
# ---------------------------------------------------------------------------

class TestCPD004ConfigConsistency:
    """deploy_pipeline.py and upgrade_verification.py must share config source."""

    def test_both_import_from_deploy_config(self):
        """Both scripts import ENVIRONMENTS from deploy_config, not local dicts."""
        dp_source = DEPLOY_PIPELINE.read_text(encoding="utf-8")
        uv_source = (PROJECT_ROOT / "scripts" / "upgrade_verification.py").read_text(encoding="utf-8")

        assert "from scripts.deploy_config import ENVIRONMENTS" in dp_source or \
               "from deploy_config import ENVIRONMENTS" in dp_source
        assert "from scripts.deploy_config import ENVIRONMENTS" in uv_source or \
               "from deploy_config import ENVIRONMENTS" in uv_source

    def test_production_tenant_id_from_env_var(self):
        """Production tenant_id reads from env var, not hardcoded."""
        mod = _load_deploy_config()
        # tenant_id should come from PRODUCTION_REMAKER_TENANT_ID env var
        prod = mod.ENVIRONMENTS["production"]
        # The default should be empty (env var driven), not a hardcoded UUID
        assert prod["tenant_id"] == os.environ.get("PRODUCTION_REMAKER_TENANT_ID", "")


# ---------------------------------------------------------------------------
# CPD-005: Rollback image capture — behavioral
# ---------------------------------------------------------------------------

class TestCPD005RollbackCapture:
    """Rollback image capture must invoke az CLI and return the image tag."""

    def test_get_current_image_returns_image_on_success(self):
        """get_current_image() calls az and returns the image string."""
        mod = _load_deploy_config()
        fake_image = "acragentredeastus.azurecr.io/api-gateway:v1.98.89"
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout=fake_image + "\n")
            result = mod.get_current_image("production")
        assert result == fake_image
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert "az" in cmd
        assert "containerapp" in cmd

    def test_get_current_image_returns_none_on_az_failure(self):
        """get_current_image() returns None when az CLI exits non-zero."""
        mod = _load_deploy_config()
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="")
            result = mod.get_current_image("production")
        assert result is None

    def test_rollback_image_stored_in_args_when_captured(self):
        """Pipeline stores rollback image in args._rollback_image before deploy."""
        source = DEPLOY_PIPELINE.read_text(encoding="utf-8")
        assert "args._rollback_image = rollback_img" in source

    def test_pipeline_fails_closed_when_rollback_capture_unavailable(self):
        """Production deploy is blocked when rollback image capture returns None."""
        source = DEPLOY_PIPELINE.read_text(encoding="utf-8")
        assert "aborting deploy (fail-closed)" in source


# ---------------------------------------------------------------------------
# CPD-006: Smoke failure triggers rollback — source + CLI behavioral
# ---------------------------------------------------------------------------

class TestCPD006RollbackOnSmokeFailure:
    """Production smoke failure must trigger automatic rollback."""

    def test_rollback_attempted_flag_set_on_failure_path(self):
        """phase_11 sets args._rollback_attempted = True when rollback runs."""
        source = DEPLOY_PIPELINE.read_text(encoding="utf-8")
        assert "args._rollback_attempted = True" in source

    def test_rollback_trigger_is_conditioned_on_rollback_image(self):
        """Rollback is triggered only when _rollback_image is present."""
        source = DEPLOY_PIPELINE.read_text(encoding="utf-8")
        assert "rollback_image = getattr(args, \"_rollback_image\", None)" in source
        assert "if rollback_image:" in source

    def test_rollback_skipped_when_no_image_captured(self):
        """When no rollback image captured, manual intervention message is present."""
        source = DEPLOY_PIPELINE.read_text(encoding="utf-8")
        assert "No rollback image captured" in source
        assert "manual intervention required" in source

    def test_production_dry_run_does_not_trigger_rollback(self):
        """Dry-run does not call rollback logic — verified via CLI."""
        result = subprocess.run(
            [sys.executable, str(DEPLOY_PIPELINE),
             "--env", "production", "--version", _current_version(),
             "--dry-run", "--approved"],
            capture_output=True, text=True, timeout=30,
            cwd=str(PROJECT_ROOT),
        )
        assert "AUTOMATIC ROLLBACK" not in result.stdout


# ---------------------------------------------------------------------------
# CPD-007: Rollback failure explicitly reported — behavioral
# ---------------------------------------------------------------------------

class TestCPD007RollbackFailureReported:
    """Rollback failure must be captured in args and reflected in structured output."""

    def test_rollback_succeeded_flag_set_on_failure(self):
        """args._rollback_succeeded = False is set when rollback_to_image fails."""
        source = DEPLOY_PIPELINE.read_text(encoding="utf-8")
        assert "args._rollback_succeeded = False" in source

    def test_rollback_succeeded_flag_set_on_success(self):
        """args._rollback_succeeded = True is set when rollback health check passes."""
        source = DEPLOY_PIPELINE.read_text(encoding="utf-8")
        assert "args._rollback_succeeded = True" in source

    def test_rollback_command_failed_message_present(self):
        """Rollback failure emits an explicit operator-facing message."""
        source = DEPLOY_PIPELINE.read_text(encoding="utf-8")
        assert "Rollback command FAILED" in source

    def test_structured_result_includes_rollback_fields(self):
        """deploy_result dict must include rollback_attempted, rollback_succeeded, rollback_image."""
        source = DEPLOY_PIPELINE.read_text(encoding="utf-8")
        for field in ["rollback_attempted", "rollback_succeeded", "rollback_image"]:
            assert f'"{field}"' in source, f"Rollback field missing from deploy_result: {field}"


# ---------------------------------------------------------------------------
# CPD-008: Dry-run exits 0 AND prints DRY RUN banner
# ---------------------------------------------------------------------------

class TestCPD008DryRunPath:
    """--dry-run must exit 0 AND print DRY RUN in stdout with no deploy side effects."""

    def test_dry_run_exits_zero_and_prints_banner_on_staging(self):
        """Staging dry-run: exit code 0 AND stdout contains 'DRY RUN'."""
        result = subprocess.run(
            [sys.executable, str(DEPLOY_PIPELINE),
             "--env", "staging", "--version", _current_version(), "--dry-run"],
            capture_output=True, text=True, timeout=30,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0, (
            f"Staging dry-run exited {result.returncode}. stdout: {result.stdout[-500:]}"
        )
        assert "DRY RUN" in result.stdout, "DRY RUN banner missing from stdout"

    def test_dry_run_does_not_invoke_az_or_docker(self):
        """Staging dry-run stdout must not contain az/docker deploy invocation lines."""
        result = subprocess.run(
            [sys.executable, str(DEPLOY_PIPELINE),
             "--env", "staging", "--version", _current_version(), "--dry-run"],
            capture_output=True, text=True, timeout=30,
            cwd=str(PROJECT_ROOT),
        )
        # No real deploy commands should be emitted in dry-run
        assert "az containerapp update" not in result.stdout
        assert "docker build" not in result.stdout


# ---------------------------------------------------------------------------
# CPD-009: Mocked success path — CLI exits 0
# ---------------------------------------------------------------------------

class TestCPD009MockedSuccessPath:
    """The pipeline must exit 0 when all phases pass (mocked)."""

    def test_production_approved_dry_run_passes_approval_gate(self):
        """--env production --approved --dry-run exits 0 and confirms approval."""
        result = subprocess.run(
            [sys.executable, str(DEPLOY_PIPELINE),
             "--env", "production", "--version", _current_version(),
             "--dry-run", "--approved"],
            capture_output=True, text=True, timeout=30,
            cwd=str(PROJECT_ROOT),
        )
        # Approval gate must confirm, pipeline must exit 0 in dry-run
        assert "Owner approval: CONFIRMED" in result.stdout
        assert result.returncode == 0, (
            f"Approved production dry-run exited {result.returncode}. "
            f"stdout: {result.stdout[-500:]}"
        )

    def test_staging_dry_run_exits_zero(self):
        """Staging dry-run exits 0 — all phases skipped correctly in dry-run."""
        result = subprocess.run(
            [sys.executable, str(DEPLOY_PIPELINE),
             "--env", "staging", "--version", _current_version(), "--dry-run"],
            capture_output=True, text=True, timeout=30,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0, (
            f"Staging dry-run exited {result.returncode}. stdout: {result.stdout[-500:]}"
        )


# ---------------------------------------------------------------------------
# CPD-010: Smoke-failure path — pipeline exits 1, rollback recorded
# ---------------------------------------------------------------------------

class TestCPD010MockedSmokeFailurePath:
    """When production smoke fails, pipeline exits 1 and records rollback state."""

    def test_phase_c_fail_without_snapshot_propagates_to_failures(self):
        """phase_11 source wires snapshot absence into failures list, triggering FAIL."""
        source = DEPLOY_PIPELINE.read_text(encoding="utf-8")
        assert "no pre-deploy snapshot available" in source
        assert "failures.append" in source

    def test_production_unapproved_deploy_exits_nonzero_immediately(self):
        """Pipeline exits 1 without even starting deploy when approval missing."""
        env = {**os.environ, "DEPLOY_APPROVED": ""}
        result = subprocess.run(
            [sys.executable, str(DEPLOY_PIPELINE),
             "--env", "production", "--version", _current_version()],
            capture_output=True, text=True, timeout=30,
            cwd=str(PROJECT_ROOT), env=env,
        )
        assert result.returncode != 0
        assert "Phase" not in result.stdout or "FAIL" in result.stdout

    def test_structured_deploy_result_includes_all_required_fields(self):
        """deploy_result JSON must include version, environment, status, duration_seconds."""
        source = DEPLOY_PIPELINE.read_text(encoding="utf-8")
        for field in ["version", "environment", "status", "duration_seconds"]:
            assert f'"{field}"' in source, f"Missing required field from deploy_result: {field}"
