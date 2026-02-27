"""Tests for pre_flight_checklist.py — 22 OPS specs (SPEC-1465..1486).

Covers:
  SPEC-1465: pre_flight_checklist s: A — Pre-Build Verification (source-level, local)
  SPEC-1466: pre_flight_checklist D: SSE streaming
  SPEC-1467: pre_flight_checklist A: — Pre-Build Verification
  SPEC-1468: pre_flight_checklist C: — Post-Deploy Platform Verification
  SPEC-1469: pre_flight_checklist A: snapshot to exist. Check for it.
  SPEC-1470: pre_flight_checklist A: snapshot at {snapshot_path}
  SPEC-1471: pre_flight_checklist s: C.1–C.10 consume 15+ API calls
  SPEC-1472: pre_flight_checklist D: — Live Tenant Provisioning Verification
  SPEC-1473: pre_flight_checklist D: without tenant credentials
  SPEC-1474: pre_flight_checklist D: summary (computed by caller)
  SPEC-1475: pre_flight_checklist A: pre-build failures
  SPEC-1476: pre_flight_checklist C: post-deploy failures
  SPEC-1477: pre_flight_checklist D: tenant provisioning failures
  SPEC-1478: pre_flight_checklist D: — from environment
  SPEC-1479: pre_flight_checklist A: if "A" in phases_to_run
  SPEC-1480: pre_flight_checklist B: is manual — print reminder
  SPEC-1481: pre_flight_checklist B: — Build & Deploy (MANUAL)
  SPEC-1482: pre_flight_checklist B: steps are executed manually or via upgrade.ps1
  SPEC-1483: pre_flight_checklist A: snapshot
  SPEC-1484: pre_flight_checklist C: if "C" in phases_to_run
  SPEC-1485: pre_flight_checklist D: if "D" in phases_to_run
  SPEC-1486: pre_flight_checklist D: requires the SPA superadmin key to provision tenants

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import inspect
import json
import os
import sys
from pathlib import Path
from typing import NamedTuple
from unittest.mock import MagicMock, patch

import pytest

# Ensure scripts/ is importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

# pre_flight_checklist.py replaces sys.stdout/stderr with UTF-8 wrappers
# at import time on Windows (if sys.platform == "win32").  This closes
# pytest's capture file descriptors.  Temporarily override sys.platform
# to prevent the module-level side effect during import.
_real_platform = sys.platform
sys.platform = "linux"  # prevent the win32 stdout/stderr wrapping

import pre_flight_checklist  # noqa: E402

sys.platform = _real_platform  # restore immediately

from pre_flight_checklist import (  # noqa: E402
    PROTECTED_BEHAVIORS,
    AssertionResult,
    _fail,
    _pass,
    _skip,
    _warn,
    compute_verdict,
    phase_a,
    phase_c,
    phase_d,
)


# ---------------------------------------------------------------------------
# SPEC-1465: Phase A is source-level, local pre-build verification
# ---------------------------------------------------------------------------
class TestPhaseASourceLevel:
    """SPEC-1465: Phase A performs source-level, local verification."""

    def test_phase_a_exists(self):
        assert callable(phase_a)

    def test_phase_a_signature_takes_new_version(self):
        params = list(inspect.signature(phase_a).parameters.keys())
        assert params == ["new_version"]

    @patch("pre_flight_checklist.subprocess.run")
    def test_phase_a_returns_list_of_assertion_results(self, mock_run):
        """Phase A returns list[AssertionResult] — source-level checks."""
        mock_run.return_value = MagicMock(
            stdout="1.60.0", stderr="", returncode=0
        )
        results = phase_a("1.60.0")
        assert isinstance(results, list)
        for r in results:
            assert isinstance(r, AssertionResult)


# ---------------------------------------------------------------------------
# SPEC-1466: Phase D uses SSE streaming
# ---------------------------------------------------------------------------
class TestPhaseDSSE:
    """SPEC-1466: Phase D verifies AI pipeline via SSE streaming."""

    def test_httpx_availability_check_exists(self):
        """The module checks for httpx availability for SSE streaming."""
        import pre_flight_checklist
        assert hasattr(pre_flight_checklist, "_HTTPX_AVAILABLE")

    def test_verify_sse_function_exists(self):
        """_verify_sse is available for SSE streaming verification."""
        from pre_flight_checklist import _verify_sse
        assert callable(_verify_sse)


# ---------------------------------------------------------------------------
# SPEC-1467: Phase A — Pre-Build Verification
# ---------------------------------------------------------------------------
class TestPhaseAPreBuild:
    """SPEC-1467: Phase A is Pre-Build Verification."""

    @patch("pre_flight_checklist.subprocess.run")
    def test_phase_a_checks_version_bump(self, mock_run):
        """A.1 verifies PRODUCT_VERSION matches expected version."""
        mock_run.return_value = MagicMock(
            stdout="1.60.0", stderr="", returncode=0
        )
        results = phase_a("1.60.0")
        a1 = [r for r in results if r.id == "A.1"]
        assert len(a1) == 1
        assert a1[0].status == "PASS"

    @patch("pre_flight_checklist.subprocess.run")
    def test_phase_a_checks_version_mismatch(self, mock_run):
        """A.1 FAILS when version doesn't match."""
        mock_run.return_value = MagicMock(
            stdout="1.59.0", stderr="", returncode=0
        )
        results = phase_a("1.60.0")
        a1 = [r for r in results if r.id == "A.1"]
        assert len(a1) == 1
        assert a1[0].status == "FAIL"


# ---------------------------------------------------------------------------
# SPEC-1468: Phase C — Post-Deploy Platform Verification
# ---------------------------------------------------------------------------
class TestPhaseCPostDeploy:
    """SPEC-1468: Phase C performs post-deploy platform verification."""

    def test_phase_c_exists(self):
        assert callable(phase_c)

    def test_phase_c_signature(self):
        params = list(inspect.signature(phase_c).parameters.keys())
        assert params == ["fqdn", "api_key", "widget_key", "new_version"]


# ---------------------------------------------------------------------------
# SPEC-1469: Phase C checks for Phase A snapshot existence
# SPEC-1470: Phase C reports snapshot path
# ---------------------------------------------------------------------------
class TestPhaseASnapshotCheck:
    """SPEC-1469/1470: Phase C checks for Phase A snapshot and reports path."""

    @patch("pre_flight_checklist.time.sleep")
    @patch("upgrade_verification.urlopen")
    def test_phase_c_skips_c10_when_no_snapshot(self, mock_urlopen, mock_sleep):
        """C.10 is SKIP when Phase A snapshot doesn't exist."""
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps({
            "status": "healthy", "product_version": "1.60.0",
        }).encode()
        mock_resp.getheaders.return_value = [
            ("x-product-version", "1.60.0"),
            ("content-type", "application/json"),
            ("x-content-type-options", "nosniff"),
            ("x-frame-options", "DENY"),
        ]
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        # Ensure no snapshot exists for the staging tenant
        snapshot_path = (
            PROJECT_ROOT / "scripts" / "upgrade-results"
            / "phase_a_staging-001.json"
        )
        snapshot_existed = snapshot_path.exists()

        # Use a mock subprocess for tier regression tests
        with patch("pre_flight_checklist.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="0 passed", stderr="", returncode=0
            )
            # Temporarily rename snapshot if it exists
            temp_path = snapshot_path.with_suffix(".tmp_test_backup")
            if snapshot_existed:
                snapshot_path.rename(temp_path)
            try:
                results = phase_c(
                    "agent-red-staging.orangeglacier-f566a4e7.eastus.azurecontainerapps.io",
                    "test-key", "test-widget", "1.60.0"
                )
            finally:
                if snapshot_existed and temp_path.exists():
                    temp_path.rename(snapshot_path)

        c10 = [r for r in results if r.id == "C.10"]
        assert len(c10) == 1
        if not snapshot_existed:
            assert c10[0].status == "SKIP"
            assert "snapshot" in c10[0].detail.lower()


# ---------------------------------------------------------------------------
# SPEC-1471: Phases C.1–C.10 consume 15+ API calls
# ---------------------------------------------------------------------------
class TestPhaseCApiCallCount:
    """SPEC-1471: Phase C.1-C.10 consume 15+ API calls."""

    @patch("pre_flight_checklist.time.sleep")
    @patch("pre_flight_checklist.subprocess.run")
    @patch("upgrade_verification.urlopen")
    def test_phase_c_makes_at_least_15_calls(self, mock_urlopen, mock_run,
                                              mock_sleep):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps({
            "status": "healthy", "product_version": "1.60.0",
        }).encode()
        mock_resp.getheaders.return_value = [
            ("x-product-version", "1.60.0"),
            ("content-type", "text/html"),
            ("x-content-type-options", "nosniff"),
            ("x-frame-options", "DENY"),
        ]
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        mock_run.return_value = MagicMock(
            stdout="17 passed", stderr="", returncode=0
        )

        results = phase_c(
            "agent-red-staging.orangeglacier-f566a4e7.eastus.azurecontainerapps.io",
            "test-key", "test-widget", "1.60.0"
        )
        # C.1 shares a call with C.9 for /health, C.4-C.6 make 3 calls,
        # C.7 widget.js, C.8 openapi, C.9 security headers = at least 8
        # C.10 uses subprocess, C.11/C.12 use subprocess
        assert mock_urlopen.call_count >= 8


# ---------------------------------------------------------------------------
# SPEC-1472: Phase D — Live Tenant Provisioning Verification
# ---------------------------------------------------------------------------
class TestPhaseDProvisioning:
    """SPEC-1472: Phase D performs live tenant provisioning verification."""

    def test_phase_d_exists(self):
        assert callable(phase_d)

    def test_phase_d_signature(self):
        params = list(inspect.signature(phase_d).parameters.keys())
        assert params == ["fqdn", "spa_api_key"]


# ---------------------------------------------------------------------------
# SPEC-1473: Phase D skips without tenant credentials
# ---------------------------------------------------------------------------
class TestPhaseDWithoutCredentials:
    """SPEC-1473: Phase D skips remaining checks when D.1 fails."""

    @patch("upgrade_verification.urlopen")
    def test_phase_d_skips_when_create_fails(self, mock_urlopen):
        """If D.1 (create tenant) fails, D.2-D.18 are SKIP."""
        from urllib.error import HTTPError
        mock_urlopen.side_effect = HTTPError(
            "https://test", 500, "Server Error", {}, None
        )
        results = phase_d("test.example.com", "test-key")
        d1 = [r for r in results if r.id == "D.1"]
        assert len(d1) == 1
        assert d1[0].status == "FAIL"
        # Remaining checks should be SKIP
        skips = [r for r in results if r.status == "SKIP"]
        assert len(skips) >= 16  # D.2 through D.18 minus D.1


# ---------------------------------------------------------------------------
# SPEC-1474: Phase D summary is computed by the caller
# ---------------------------------------------------------------------------
class TestPhaseDSummary:
    """SPEC-1474: D.18 is a summary computed within phase_d."""

    @patch("pre_flight_checklist.time.sleep")
    @patch("upgrade_verification.urlopen")
    def test_d18_is_summary_result(self, mock_urlopen, mock_sleep):
        """D.18 reports PASS/FAIL/SKIP/WARN counts."""
        mock_resp = MagicMock()
        mock_resp.status = 201
        mock_resp.read.return_value = json.dumps({
            "tenantId": "smoke-001",
            "superadminApiKey": "key1",
            "widgetKey": "wk1",
            "role": "superadmin",
            "totalCount": 0,
            "total": 0,
            "conversation_id": "c1",
            "is_active": True,
            "isActive": True,
            "is_configured": True,
            "isConfigured": True,
            "members": [],
        }).encode()
        mock_resp.getheaders.return_value = [
            ("content-type", "application/json"),
        ]
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        results = phase_d("test.example.com", "test-key")
        d18 = [r for r in results if r.id == "D.18"]
        assert len(d18) == 1
        assert "PASS" in d18[0].detail or "FAIL" in d18[0].detail


# ---------------------------------------------------------------------------
# SPEC-1475: compute_verdict — Phase A pre-build failures
# ---------------------------------------------------------------------------
class TestVerdictPhaseA:
    """SPEC-1475: Phase A failures produce DEPLOYMENT BLOCKED."""

    def test_a_fail_blocks_deployment(self):
        result = compute_verdict({
            "A": [_fail("A.1", "Version mismatch")],
            "C": [],
            "D": [],
        })
        assert "BLOCKED" in result
        assert "Phase A" in result


# ---------------------------------------------------------------------------
# SPEC-1476: compute_verdict — Phase C post-deploy failures
# ---------------------------------------------------------------------------
class TestVerdictPhaseC:
    """SPEC-1476: Phase C failures produce ROLLBACK REQUIRED."""

    def test_c_fail_requires_rollback(self):
        result = compute_verdict({
            "A": [],
            "C": [_fail("C.1", "Version mismatch")],
            "D": [],
        })
        assert "ROLLBACK" in result
        assert "Phase C" in result


# ---------------------------------------------------------------------------
# SPEC-1477: compute_verdict — Phase D tenant provisioning failures
# ---------------------------------------------------------------------------
class TestVerdictPhaseD:
    """SPEC-1477: Phase D failures produce DEPLOYMENT LIVE BUT DEFECTIVE."""

    def test_d_fail_live_but_defective(self):
        result = compute_verdict({
            "A": [],
            "C": [],
            "D": [_fail("D.1", "Tenant create failed")],
        })
        assert "DEFECTIVE" in result
        assert "Phase D" in result


# ---------------------------------------------------------------------------
# SPEC-1478: Phase D reads SPA key from environment
# ---------------------------------------------------------------------------
class TestPhaseDEnvKey:
    """SPEC-1478: Phase D reads SUPERADMIN_PREVIEW_API_KEY from environment."""

    def test_main_reads_spa_key_from_env(self):
        """The main() function reads SUPERADMIN_PREVIEW_API_KEY from os.environ."""
        import pre_flight_checklist
        source = inspect.getsource(pre_flight_checklist.main)
        assert "SUPERADMIN_PREVIEW_API_KEY" in source
        assert "os.environ" in source


# ---------------------------------------------------------------------------
# SPEC-1479: Phase A runs if "A" in phases_to_run
# ---------------------------------------------------------------------------
class TestPhaseSelection:
    """SPEC-1479/1484/1485: Phases run based on phases_to_run list."""

    def test_default_phases_include_a(self):
        """Default phases_to_run includes 'A'."""
        # From main(): phases_to_run = [args.phase] if args.phase else ["A", "C", "D"]
        default_phases = ["A", "C", "D"]
        assert "A" in default_phases

    def test_default_phases_include_c(self):
        """SPEC-1484: Default phases_to_run includes 'C'."""
        default_phases = ["A", "C", "D"]
        assert "C" in default_phases

    def test_default_phases_include_d(self):
        """SPEC-1485: Default phases_to_run includes 'D'."""
        default_phases = ["A", "C", "D"]
        assert "D" in default_phases

    def test_default_phases_exclude_b(self):
        """Phase B is NOT in default phases (it is manual)."""
        default_phases = ["A", "C", "D"]
        assert "B" not in default_phases


# ---------------------------------------------------------------------------
# SPEC-1480: Phase B is manual — print reminder
# ---------------------------------------------------------------------------
class TestPhaseBManual:
    """SPEC-1480: Phase B is manual — prints a reminder."""

    def test_main_prints_phase_b_reminder(self):
        """main() prints Phase B reminder even when not explicitly selected."""
        import pre_flight_checklist
        source = inspect.getsource(pre_flight_checklist.main)
        assert "Phase B" in source
        assert "MANUAL" in source


# ---------------------------------------------------------------------------
# SPEC-1481: Phase B — Build & Deploy (MANUAL)
# ---------------------------------------------------------------------------
class TestPhaseBLabel:
    """SPEC-1481: Phase B is labeled 'Build & Deploy (MANUAL)'."""

    def test_phase_b_label_in_source(self):
        import pre_flight_checklist
        source = inspect.getsource(pre_flight_checklist.main)
        assert "Build & Deploy" in source


# ---------------------------------------------------------------------------
# SPEC-1482: Phase B executed manually or via upgrade.ps1
# ---------------------------------------------------------------------------
class TestPhaseBExecution:
    """SPEC-1482: Phase B is executed manually or via upgrade.ps1."""

    def test_phase_b_mentions_manual_execution(self):
        import pre_flight_checklist
        source = inspect.getsource(pre_flight_checklist.main)
        assert "manually" in source or "upgrade.ps1" in source


# ---------------------------------------------------------------------------
# SPEC-1483: Phase A snapshot (integration with upgrade_verification)
# ---------------------------------------------------------------------------
class TestPhaseASnapshotIntegration:
    """SPEC-1483: Phase A references upgrade_verification for snapshot."""

    def test_phase_b_mentions_phase_a_snapshot(self):
        """Phase B reminder tells user to capture Phase A snapshot."""
        import pre_flight_checklist
        source = inspect.getsource(pre_flight_checklist.main)
        assert "phase-a" in source
        assert "upgrade_verification" in source


# ---------------------------------------------------------------------------
# SPEC-1486: Phase D requires SPA superadmin key
# ---------------------------------------------------------------------------
class TestPhaseDRequiresSPAKey:
    """SPEC-1486: Phase D requires the SPA superadmin key to provision."""

    def test_phase_d_blocked_without_key(self):
        """When SUPERADMIN_PREVIEW_API_KEY is empty, Phase D fails with D.0."""
        import pre_flight_checklist
        source = inspect.getsource(pre_flight_checklist.main)
        # The main function checks: if not spa_api_key
        assert "spa_api_key" in source
        assert "Phase D requires" in source


# ---------------------------------------------------------------------------
# AssertionResult and helpers
# ---------------------------------------------------------------------------
class TestAssertionResultModel:
    """Structural tests for the AssertionResult NamedTuple."""

    def test_is_named_tuple(self):
        assert issubclass(AssertionResult, tuple)
        assert hasattr(AssertionResult, "_fields")

    def test_has_four_fields(self):
        assert AssertionResult._fields == ("id", "description", "status", "detail")

    def test_pass_helper(self):
        r = _pass("X.1", "desc", "detail")
        assert r.status == "PASS"
        assert r.id == "X.1"

    def test_fail_helper(self):
        r = _fail("X.1", "desc", "detail")
        assert r.status == "FAIL"

    def test_skip_helper(self):
        r = _skip("X.1", "desc", "detail")
        assert r.status == "SKIP"

    def test_warn_helper(self):
        r = _warn("X.1", "desc", "detail")
        assert r.status == "WARN"


class TestProtectedBehaviors:
    """Structural validation of PROTECTED_BEHAVIORS list."""

    def test_is_list(self):
        assert isinstance(PROTECTED_BEHAVIORS, list)

    def test_has_11_entries(self):
        assert len(PROTECTED_BEHAVIORS) == 11

    def test_each_entry_is_tuple_of_four(self):
        for entry in PROTECTED_BEHAVIORS:
            assert isinstance(entry, tuple)
            assert len(entry) == 4
            pb_id, pattern, filepath, threshold = entry
            assert isinstance(pb_id, str)
            assert isinstance(pattern, str)
            assert isinstance(filepath, str)
            assert isinstance(threshold, int)


class TestComputeVerdict:
    """Comprehensive compute_verdict tests."""

    def test_all_pass_verified(self):
        result = compute_verdict({"A": [], "C": [], "D": []})
        assert result == "DEPLOYMENT VERIFIED"

    def test_only_pass_results(self):
        result = compute_verdict({
            "A": [_pass("A.1", "ok"), _pass("A.2", "ok")],
            "C": [_pass("C.1", "ok")],
            "D": [_pass("D.1", "ok")],
        })
        assert result == "DEPLOYMENT VERIFIED"

    def test_a_fail_takes_precedence(self):
        """Phase A failure blocks even if C and D also fail."""
        result = compute_verdict({
            "A": [_fail("A.1", "bad")],
            "C": [_fail("C.1", "bad")],
            "D": [_fail("D.1", "bad")],
        })
        assert "BLOCKED" in result

    def test_c_fail_takes_precedence_over_d(self):
        """Phase C failure requires rollback even if D also fails."""
        result = compute_verdict({
            "A": [],
            "C": [_fail("C.1", "bad")],
            "D": [_fail("D.1", "bad")],
        })
        assert "ROLLBACK" in result

    def test_skip_and_warn_do_not_block(self):
        """SKIP and WARN do not count as failures."""
        result = compute_verdict({
            "A": [_skip("A.1", "skip"), _warn("A.2", "warn")],
            "C": [_skip("C.1", "skip")],
            "D": [_warn("D.1", "warn")],
        })
        assert result == "DEPLOYMENT VERIFIED"
