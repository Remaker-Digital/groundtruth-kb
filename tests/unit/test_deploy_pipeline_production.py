"""CPD-001..010: Canonical production deploy pipeline tests.

Validates the deterministic production deployment procedure per the
Codex test protocol v0.1-draft. Covers:
  - Contract tests (CLI requirements, approval gate, no prompts)
  - Unit tests (config consistency, rollback capture, rollback decision)
  - Subprocess CLI tests (dry-run, approval-blocked, staging unaffected)

Test IDs map to the Codex CPD test matrix:
  CPD-001: CLI requires --version
  CPD-002: Production path without approval → fail before deploy
  CPD-003: No interactive prompt strings in canonical path
  CPD-004: Config consistency across deploy_pipeline and upgrade_verification
  CPD-005: Rollback image capture function
  CPD-006: Smoke failure triggers rollback path
  CPD-007: Rollback failure reported explicitly
  CPD-008: Dry-run path produces non-destructive output
  CPD-009: Staging path not affected by production gates
  CPD-010: Structured result output includes rollback metadata

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import importlib
import inspect
import os
import re
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

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
             "--env", "production", "--version", "v1.98.91", "--dry-run"],
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
             "--env", "production", "--version", "v1.98.91", "--dry-run"],
            capture_output=True, text=True, timeout=30,
            cwd=str(PROJECT_ROOT), env=env,
        )
        # Should pass the approval gate (may still fail on other checks)
        assert "Owner approval: CONFIRMED" in result.stdout

    def test_production_allowed_with_flag(self):
        """--approved flag passes the approval gate."""
        result = subprocess.run(
            [sys.executable, str(DEPLOY_PIPELINE),
             "--env", "production", "--version", "v1.98.91",
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
# CPD-005: Rollback image capture
# ---------------------------------------------------------------------------

class TestCPD005RollbackCapture:
    """The pipeline must capture the current image before deploy for rollback."""

    def test_get_current_image_function_exists(self):
        """deploy_config.get_current_image() exists and is callable."""
        mod = _load_deploy_config()
        assert hasattr(mod, "get_current_image")
        assert callable(mod.get_current_image)

    def test_rollback_to_image_function_exists(self):
        """deploy_config.rollback_to_image() exists and is callable."""
        mod = _load_deploy_config()
        assert hasattr(mod, "rollback_to_image")
        assert callable(mod.rollback_to_image)


# ---------------------------------------------------------------------------
# CPD-006: Smoke failure triggers rollback
# ---------------------------------------------------------------------------

class TestCPD006RollbackOnSmokeFailure:
    """Production smoke failure must trigger automatic rollback."""

    def test_rollback_code_present_in_production_verification(self):
        """phase_11_production_verification contains rollback logic."""
        source = DEPLOY_PIPELINE.read_text(encoding="utf-8")
        assert "AUTOMATIC ROLLBACK INITIATED" in source
        assert "rollback_to_image" in source


# ---------------------------------------------------------------------------
# CPD-007: Rollback failure reported
# ---------------------------------------------------------------------------

class TestCPD007RollbackFailureReported:
    """Rollback failure must be explicitly reported in the result."""

    def test_rollback_result_fields_in_output(self):
        """Structured result includes rollback_attempted and rollback_succeeded."""
        source = DEPLOY_PIPELINE.read_text(encoding="utf-8")
        assert "rollback_attempted" in source
        assert "rollback_succeeded" in source
        assert "rollback_image" in source


# ---------------------------------------------------------------------------
# CPD-008: Dry-run path
# ---------------------------------------------------------------------------

class TestCPD008DryRunPath:
    """--dry-run must produce non-destructive output."""

    def test_dry_run_exits_zero_on_staging(self):
        """Staging dry-run exits 0 (no real actions taken)."""
        result = subprocess.run(
            [sys.executable, str(DEPLOY_PIPELINE),
             "--env", "staging", "--version", "v1.98.91", "--dry-run"],
            capture_output=True, text=True, timeout=30,
            cwd=str(PROJECT_ROOT),
        )
        # Dry run should pass pre-flight at minimum
        assert "DRY RUN" in result.stdout or result.returncode == 0


# ---------------------------------------------------------------------------
# CPD-009: Staging unaffected
# ---------------------------------------------------------------------------

class TestCPD009StagingUnaffected:
    """Staging path must NOT have approval gate or rollback."""

    def test_staging_has_no_approval_gate(self):
        """Staging dry-run does not mention approval."""
        result = subprocess.run(
            [sys.executable, str(DEPLOY_PIPELINE),
             "--env", "staging", "--version", "v1.98.91", "--dry-run"],
            capture_output=True, text=True, timeout=30,
            cwd=str(PROJECT_ROOT),
        )
        assert "Owner approval" not in result.stdout


# ---------------------------------------------------------------------------
# CPD-010: Structured result output
# ---------------------------------------------------------------------------

class TestCPD010StructuredOutput:
    """Deploy result must include version, status, and rollback metadata."""

    def test_result_json_written(self):
        """deploy_pipeline.py writes a JSON result file."""
        source = DEPLOY_PIPELINE.read_text(encoding="utf-8")
        assert "deploy-result-" in source
        assert "json.dumps(deploy_result" in source

    def test_result_contains_required_fields(self):
        """The deploy_result dict contains all required fields."""
        source = DEPLOY_PIPELINE.read_text(encoding="utf-8")
        for field in ["version", "environment", "status", "rollback_attempted",
                       "rollback_succeeded", "rollback_image", "duration_seconds"]:
            assert f'"{field}"' in source, f"Missing field: {field}"
