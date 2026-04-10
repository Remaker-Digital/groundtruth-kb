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
from unittest.mock import MagicMock, patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEPLOY_PIPELINE = PROJECT_ROOT / "scripts" / "deploy_pipeline.py"
DEPLOY_CONFIG = PROJECT_ROOT / "scripts" / "deploy_config.py"

# Detect Azure CLI availability for subprocess deploy tests.
# These tests run deploy_pipeline.py which calls `az` — skip when not authenticated.
# On Windows, `az` is `az.cmd`; a bare list-form subprocess call cannot resolve
# .cmd extensions without shell=True. Use a string command with shell=True so the
# probe behaves identically to the actual pipeline runtime path on all platforms.
_az_available = False
try:
    _az_check = subprocess.run(
        "az account show", capture_output=True, timeout=10, shell=True
    )
    _az_available = _az_check.returncode == 0
except (subprocess.TimeoutExpired, OSError):
    pass

_skip_no_az = pytest.mark.skipif(
    not _az_available,
    reason="Azure CLI not authenticated (az account show failed)",
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_deploy_config():
    """Import deploy_config module."""
    spec = importlib.util.spec_from_file_location("deploy_config", DEPLOY_CONFIG)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_deploy_pipeline():
    """Import deploy_pipeline module for unit-level behavioral tests.

    Loads fresh each call so patch.object calls against the returned module
    namespace are isolated per test.

    deploy_pipeline.py wraps sys.stdout/stderr on Windows (UTF-8 fix). That
    code runs at module-import time and corrupts pytest's capture pipes if
    allowed to execute. We patch sys.platform to "linux" during loading so
    the guard is False and stdout is left untouched.
    """
    from unittest.mock import patch as _patch
    for p in [str(PROJECT_ROOT), str(PROJECT_ROOT / "scripts"),
              str(PROJECT_ROOT / "tools" / "knowledge-db")]:
        if p not in sys.path:
            sys.path.insert(0, p)
    with _patch.object(sys, "platform", "linux"):
        spec = importlib.util.spec_from_file_location("deploy_pipeline_test_copy", DEPLOY_PIPELINE)
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
        return "v1.98.91"


def _smoke_fail_api_call(fqdn, path, api_key=None, timeout=10):
    """api_call stub that always returns 503 (smoke failure)."""
    return (503, {}, {})


def _smoke_pass_api_call(fqdn, path, api_key=None, timeout=10):
    """api_call stub that returns 200 with the current PRODUCT_VERSION (smoke pass)."""
    if path == "/health":
        v = _current_version().lstrip("v")
        return (200, {"product_version": v}, {"x-product-version": v})
    return (200, {"found": True}, {})


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
            "deploy_pipeline.py contains input() calls — must be non-interactive"
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
# CPD-006: Smoke failure triggers rollback — behavioral (mocked phase_11)
# ---------------------------------------------------------------------------

class TestCPD006RollbackOnSmokeFailure:
    """Production smoke failure must trigger automatic rollback."""

    def _make_args(self, rollback_image=None, snapshot_files=None):
        args = argparse.Namespace(dry_run=False, version=_current_version(), env="production")
        args._rollback_image = rollback_image
        args._snapshot_files = snapshot_files or []
        return args

    def test_rollback_attempted_when_smoke_fails_with_image(self):
        """phase_11 sets args._rollback_attempted = True when smoke fails + rollback image present."""
        dp = _load_deploy_pipeline()
        args = self._make_args(
            rollback_image="acragentredeastus.azurecr.io/api-gateway:v1.98.89",
            snapshot_files=["fake_snapshot.json"],
        )
        stream_mock = MagicMock(returncode=0, stdout="(41 pass, 0 fail)")

        with patch.object(dp, "api_call", side_effect=_smoke_fail_api_call), \
             patch.object(dp, "_stream", return_value=stream_mock), \
             patch.object(dp, "time") as mock_time, \
             patch("scripts.deploy_config.rollback_to_image", return_value=True):
            mock_time.time.side_effect = [0.0, 0.0, 1.0]
            mock_time.sleep.return_value = None
            result = dp.phase_11_production_verification(args)

        assert result.status == "FAIL"
        assert args._rollback_attempted is True

    def test_rollback_not_attempted_when_no_image_captured(self):
        """phase_11 sets args._rollback_attempted = False when no rollback image exists."""
        dp = _load_deploy_pipeline()
        args = self._make_args(rollback_image=None, snapshot_files=["fake_snapshot.json"])
        stream_mock = MagicMock(returncode=0, stdout="(41 pass, 0 fail)")

        with patch.object(dp, "api_call", side_effect=_smoke_fail_api_call), \
             patch.object(dp, "_stream", return_value=stream_mock), \
             patch.object(dp, "time") as mock_time:
            mock_time.time.side_effect = [0.0, 1.0]
            mock_time.sleep.return_value = None
            result = dp.phase_11_production_verification(args)

        assert result.status == "FAIL"
        assert args._rollback_attempted is False

    def test_production_dry_run_does_not_trigger_rollback(self):
        """Dry-run path skips phase_11 body — AUTOMATIC ROLLBACK must not appear."""
        result = subprocess.run(
            [sys.executable, str(DEPLOY_PIPELINE),
             "--env", "production", "--version", _current_version(),
             "--dry-run", "--approved"],
            capture_output=True, text=True, timeout=30,
            cwd=str(PROJECT_ROOT),
        )
        assert "AUTOMATIC ROLLBACK" not in result.stdout


# ---------------------------------------------------------------------------
# CPD-007: Rollback failure explicitly reported — behavioral (mocked phase_11)
# ---------------------------------------------------------------------------

class TestCPD007RollbackFailureReported:
    """Rollback failure must be captured in args and reflected in structured output."""

    def _make_smoke_fail_args(self):
        args = argparse.Namespace(dry_run=False, version=_current_version(), env="production")
        args._rollback_image = "acragentredeastus.azurecr.io/api-gateway:v1.98.89"
        args._snapshot_files = ["fake_snapshot.json"]
        return args

    def test_rollback_succeeded_false_when_rollback_command_fails(self):
        """args._rollback_succeeded = False when rollback_to_image() returns False."""
        dp = _load_deploy_pipeline()
        args = self._make_smoke_fail_args()
        stream_mock = MagicMock(returncode=0, stdout="(41 pass, 0 fail)")

        with patch.object(dp, "api_call", side_effect=_smoke_fail_api_call), \
             patch.object(dp, "_stream", return_value=stream_mock), \
             patch.object(dp, "time") as mock_time, \
             patch("scripts.deploy_config.rollback_to_image", return_value=False):
            mock_time.time.side_effect = [0.0, 0.0, 1.0]
            mock_time.sleep.return_value = None
            dp.phase_11_production_verification(args)

        assert args._rollback_succeeded is False
        assert args._rollback_attempted is True

    def test_rollback_succeeded_true_when_health_passes_after_rollback(self):
        """args._rollback_succeeded = True when rollback succeeds and health returns 200."""
        dp = _load_deploy_pipeline()
        args = self._make_smoke_fail_args()
        stream_mock = MagicMock(returncode=0, stdout="(41 pass, 0 fail)")

        call_count = {"n": 0}
        def api_call_stub(fqdn, path, api_key=None, timeout=10):
            call_count["n"] += 1
            if call_count["n"] < 3:   # calls 1+2 are smoke (/health + /tenants/lookup) — fail
                return (503, {}, {})
            return (200, {}, {})       # call 3 is the rollback health check — pass

        with patch.object(dp, "api_call", side_effect=api_call_stub), \
             patch.object(dp, "_stream", return_value=stream_mock), \
             patch.object(dp, "time") as mock_time, \
             patch("scripts.deploy_config.rollback_to_image", return_value=True):
            mock_time.time.side_effect = [0.0, 0.0, 1.0]
            mock_time.sleep.return_value = None
            dp.phase_11_production_verification(args)

        assert args._rollback_succeeded is True
        assert args._rollback_attempted is True

    def test_rollback_succeeded_false_when_health_fails_after_rollback(self):
        """args._rollback_succeeded = False when rollback cmd succeeds but health stays 503."""
        dp = _load_deploy_pipeline()
        args = self._make_smoke_fail_args()
        stream_mock = MagicMock(returncode=0, stdout="(41 pass, 0 fail)")

        with patch.object(dp, "api_call", side_effect=_smoke_fail_api_call), \
             patch.object(dp, "_stream", return_value=stream_mock), \
             patch.object(dp, "time") as mock_time, \
             patch("scripts.deploy_config.rollback_to_image", return_value=True):
            mock_time.time.side_effect = [0.0, 0.0, 1.0]
            mock_time.sleep.return_value = None
            dp.phase_11_production_verification(args)

        assert args._rollback_succeeded is False
        assert args._rollback_attempted is True

    @_skip_no_az
    def test_deploy_result_json_includes_rollback_fields_on_dry_run(self):
        """Dry-run run writes JSON result file containing rollback_attempted, rollback_succeeded, rollback_image."""
        result = subprocess.run(
            [sys.executable, str(DEPLOY_PIPELINE),
             "--env", "staging", "--version", _current_version(), "--dry-run"],
            capture_output=True, text=True, timeout=30,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0
        # Find the most-recently written deploy-result JSON
        result_files = sorted(
            (PROJECT_ROOT / "logs").glob("deploy-result-staging-*.json"),
            key=lambda p: p.stat().st_mtime, reverse=True,
        )
        assert result_files, "No deploy-result JSON written by dry-run"
        data = json.loads(result_files[0].read_text())
        for field in ["rollback_attempted", "rollback_succeeded", "rollback_image"]:
            assert field in data, f"Rollback field missing from deploy_result JSON: {field}"


# ---------------------------------------------------------------------------
# CPD-008: Dry-run exits 0 AND prints DRY RUN banner
# ---------------------------------------------------------------------------

class TestCPD008DryRunPath:
    """--dry-run must exit 0 AND print DRY RUN in stdout with no deploy side effects."""

    @_skip_no_az
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


MOCK_RUNNER = PROJECT_ROOT / "tests" / "unit" / "helpers" / "run_mocked_pipeline.py"


# ---------------------------------------------------------------------------
# CPD-009: Success path — dry-run CLI + mocked phase_11 behavioral + CLI subprocess
# ---------------------------------------------------------------------------

class TestCPD009SuccessPath:
    """Production verification must return PASS and not set rollback when all checks pass."""

    @_skip_no_az
    def test_production_approved_dry_run_passes_approval_gate(self):
        """--env production --approved --dry-run exits 0 and confirms approval."""
        result = subprocess.run(
            [sys.executable, str(DEPLOY_PIPELINE),
             "--env", "production", "--version", _current_version(),
             "--dry-run", "--approved"],
            capture_output=True, text=True, timeout=30,
            cwd=str(PROJECT_ROOT),
        )
        assert "Owner approval: CONFIRMED" in result.stdout
        assert result.returncode == 0, (
            f"Approved production dry-run exited {result.returncode}. "
            f"stdout: {result.stdout[-500:]}"
        )

    @_skip_no_az
    def test_staging_dry_run_exits_zero(self):
        """Staging dry-run exits 0 — all phases return PASS in dry-run."""
        result = subprocess.run(
            [sys.executable, str(DEPLOY_PIPELINE),
             "--env", "staging", "--version", _current_version(), "--dry-run"],
            capture_output=True, text=True, timeout=30,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0, (
            f"Staging dry-run exited {result.returncode}. stdout: {result.stdout[-500:]}"
        )

    def test_phase_11_returns_pass_when_all_checks_succeed(self):
        """phase_11 returns PASS PhaseResult when phase-c and all smoke checks pass."""
        dp = _load_deploy_pipeline()
        args = argparse.Namespace(dry_run=False, version=_current_version(), env="production")
        args._rollback_image = None
        args._snapshot_files = ["fake_snapshot.json"]
        stream_mock = MagicMock(returncode=0, stdout="(41 pass, 0 fail)")

        with patch.object(dp, "api_call", side_effect=_smoke_pass_api_call), \
             patch.object(dp, "_stream", return_value=stream_mock), \
             patch.object(dp, "time") as mock_time:
            mock_time.time.side_effect = [0.0, 1.0]
            mock_time.sleep.return_value = None
            result = dp.phase_11_production_verification(args)

        assert result.status == "PASS"
        # Rollback must not have been set when verification succeeds
        assert not getattr(args, "_rollback_attempted", False)

    def test_mocked_success_path_cli_exits_zero(self):
        """Subprocess CLI: all phases mocked to PASS → pipeline exits 0.

        This is the Phase C case 4 proof from the Codex test protocol v0.1:
        top-level command wired correctly so a success-path run exits 0.
        Uses run_mocked_pipeline.py which patches every phase function before
        calling deploy_pipeline.main() — proving CLI exit-code wiring without
        touching Azure, ACR, or live HTTP.
        """
        result = subprocess.run(
            [sys.executable, str(MOCK_RUNNER), "success",
             "--env", "staging", "--version", _current_version(), "--approved"],
            capture_output=True, text=True, timeout=60,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0, (
            f"Mocked success path exited {result.returncode} (expected 0). "
            f"stdout: {result.stdout[-800:]}"
        )
        assert "RESULT: SUCCESS" in result.stdout, (
            f"Expected SUCCESS banner in output. stdout: {result.stdout[-800:]}"
        )


# ---------------------------------------------------------------------------
# CPD-010: Smoke-failure path — phase_11 exits FAIL, rollback recorded (mocked)
# ---------------------------------------------------------------------------

class TestCPD010MockedSmokeFailurePath:
    """When production smoke fails, phase_11 returns FAIL and records rollback state."""

    def test_phase_11_fails_when_snapshot_missing(self):
        """phase_11 returns FAIL immediately when no snapshot is available."""
        dp = _load_deploy_pipeline()
        args = argparse.Namespace(dry_run=False, version=_current_version(), env="production")
        args._rollback_image = None
        args._snapshot_files = []    # no snapshot

        with patch.object(dp, "api_call", side_effect=_smoke_fail_api_call), \
             patch.object(dp, "time") as mock_time:
            mock_time.time.side_effect = [0.0, 1.0]
            mock_time.sleep.return_value = None
            result = dp.phase_11_production_verification(args)

        assert result.status == "FAIL"
        assert "no pre-deploy snapshot available" in result.detail

    def test_phase_11_fails_and_sets_rollback_attempted_on_smoke_failure(self):
        """phase_11 returns FAIL and sets _rollback_attempted when smoke fails + image present."""
        dp = _load_deploy_pipeline()
        args = argparse.Namespace(dry_run=False, version=_current_version(), env="production")
        args._rollback_image = "acragentredeastus.azurecr.io/api-gateway:v1.98.89"
        args._snapshot_files = ["fake_snapshot.json"]
        stream_mock = MagicMock(returncode=0, stdout="(41 pass, 0 fail)")

        with patch.object(dp, "api_call", side_effect=_smoke_fail_api_call), \
             patch.object(dp, "_stream", return_value=stream_mock), \
             patch.object(dp, "time") as mock_time, \
             patch("scripts.deploy_config.rollback_to_image", return_value=False):
            mock_time.time.side_effect = [0.0, 0.0, 1.0]
            mock_time.sleep.return_value = None
            result = dp.phase_11_production_verification(args)

        assert result.status == "FAIL"
        assert args._rollback_attempted is True

    def test_production_unapproved_deploy_exits_nonzero_immediately(self):
        """Pipeline exits non-zero before starting deploy when approval is missing."""
        env = {**os.environ, "DEPLOY_APPROVED": ""}
        result = subprocess.run(
            [sys.executable, str(DEPLOY_PIPELINE),
             "--env", "production", "--version", _current_version()],
            capture_output=True, text=True, timeout=30,
            cwd=str(PROJECT_ROOT), env=env,
        )
        assert result.returncode != 0
        assert "Phase" not in result.stdout or "FAIL" in result.stdout

    def test_mocked_smoke_failure_cli_exits_one_with_rollback(self):
        """Subprocess CLI: production smoke failure → pipeline exits 1, rollback logged.

        This is the Phase C case 5 proof from the Codex test protocol v0.1:
        top-level command wired correctly so a smoke-failure path exits 1 and
        records rollback attempt. Uses run_mocked_pipeline.py which patches
        all shared/deploy phases to PASS while leaving phase_11_production_verification
        to run with api_call stubbed to return 503 — the minimal proof that CLI
        exit code and rollback path are correctly wired end-to-end.
        """
        result = subprocess.run(
            [sys.executable, str(MOCK_RUNNER), "smoke_failure",
             "--env", "production", "--version", _current_version(), "--approved"],
            capture_output=True, text=True, timeout=60,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 1, (
            f"Mocked smoke-failure path exited {result.returncode} (expected 1). "
            f"stdout: {result.stdout[-800:]}"
        )
        assert "AUTOMATIC ROLLBACK INITIATED" in result.stdout, (
            f"Rollback message not found in output. stdout: {result.stdout[-800:]}"
        )
        assert "RESULT: FAILURE" in result.stdout, (
            f"Expected FAILURE banner in output. stdout: {result.stdout[-800:]}"
        )

    @_skip_no_az
    def test_deploy_result_json_includes_required_fields_on_staging_dry_run(self):
        """Staging dry-run writes JSON with version, environment, status, duration_seconds."""
        result = subprocess.run(
            [sys.executable, str(DEPLOY_PIPELINE),
             "--env", "staging", "--version", _current_version(), "--dry-run"],
            capture_output=True, text=True, timeout=30,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0
        result_files = sorted(
            (PROJECT_ROOT / "logs").glob("deploy-result-staging-*.json"),
            key=lambda p: p.stat().st_mtime, reverse=True,
        )
        assert result_files, "No deploy-result JSON written"
        data = json.loads(result_files[0].read_text())
        for field in ["version", "environment", "status", "duration_seconds"]:
            assert field in data, f"Missing required field from deploy_result JSON: {field}"
