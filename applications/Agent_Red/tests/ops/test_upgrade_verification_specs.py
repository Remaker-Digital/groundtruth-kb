"""Tests for upgrade_verification.py — 9 OPS specs (SPEC-1456..1464).

Covers:
  SPEC-1456: upgrade_verification A: + Phase C
  SPEC-1457: upgrade_verification A: Pre-deployment snapshot
  SPEC-1458: upgrade_verification A: phase header "Pre-Deployment Snapshot"
  SPEC-1459: upgrade_verification C: Post-deployment verification
  SPEC-1460: upgrade_verification C: makes ~30 authenticated calls
  SPEC-1461: upgrade_verification C: phase header "Post-Deployment Verification"
  SPEC-1462: upgrade_verification A: snapshot JSON (for phase-c)
  SPEC-1463: upgrade_verification A: iterates all tenants
  SPEC-1464: upgrade_verification C: iterates all tenants

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import inspect
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure scripts/ is importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from upgrade_verification import (  # noqa: E402
    ENVIRONMENTS,
    TENANTS,
    _all_tenants,
    _resolve_env,
    api_call,
    phase_a,
    phase_c,
    widget_call,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mock_response(status: int = 200, body: dict | str = "",
                        headers: list[tuple[str, str]] | None = None):
    """Create a mock urllib response object."""
    mock_resp = MagicMock()
    mock_resp.status = status
    if isinstance(body, dict):
        mock_resp.read.return_value = json.dumps(body).encode()
    else:
        mock_resp.read.return_value = body.encode()
    mock_resp.getheaders.return_value = headers or []
    mock_resp.__enter__ = MagicMock(return_value=mock_resp)
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


# ---------------------------------------------------------------------------
# SPEC-1456: upgrade_verification provides Phase A + Phase C
# ---------------------------------------------------------------------------
class TestPhaseAAndC:
    """SPEC-1456: Script provides both phase_a and phase_c functions."""

    def test_phase_a_function_exists(self):
        assert callable(phase_a)

    def test_phase_c_function_exists(self):
        assert callable(phase_c)

    def test_phase_a_signature(self):
        params = list(inspect.signature(phase_a).parameters.keys())
        assert params == ["env"]

    def test_phase_c_signature(self):
        params = list(inspect.signature(phase_c).parameters.keys())
        assert params == ["env", "snapshot", "new_version"]


# ---------------------------------------------------------------------------
# SPEC-1457: Phase A captures pre-deployment snapshot
# ---------------------------------------------------------------------------
class TestPhaseASnapshot:
    """SPEC-1457: phase_a returns a dict snapshot with A1-A11 keys."""

    @patch("upgrade_verification.urlopen")
    def test_phase_a_returns_dict(self, mock_urlopen):
        mock_resp = _make_mock_response(
            200,
            {"state": "active", "is_active": True, "is_configured": True,
             "has_pending_changes": False, "active_version": 1,
             "totalCount": 5, "status_breakdown": {},
             "members": [{"displayName": "Admin", "role": "superadmin"}]},
            [("x-product-version", "1.60.0"), ("content-type", "application/json")],
        )
        mock_urlopen.return_value = mock_resp
        env = ENVIRONMENTS["staging"].copy()
        result = phase_a(env)
        assert isinstance(result, dict)

    @patch("upgrade_verification.urlopen")
    def test_phase_a_snapshot_has_expected_keys(self, mock_urlopen):
        mock_resp = _make_mock_response(
            200,
            {"state": "active", "is_active": True, "is_configured": True,
             "has_pending_changes": False, "active_version": 1,
             "totalCount": 5, "status_breakdown": {},
             "members": [{"displayName": "Admin", "role": "superadmin"}]},
            [("x-product-version", "1.60.0"), ("content-type", "application/json")],
        )
        mock_urlopen.return_value = mock_resp
        env = ENVIRONMENTS["staging"].copy()
        result = phase_a(env)
        expected_keys = {
            "A1_version", "A2_status", "A3_activation", "A4_conversation_count",
            "A5_status_breakdown", "A6_kb_count", "A7_team_count",
            "A8_team_members", "A9_draft_status", "A10_config_keys",
            "A11_widget_key_exists",
        }
        assert expected_keys.issubset(set(result.keys()))


# ---------------------------------------------------------------------------
# SPEC-1458: Phase A prints header "Pre-Deployment Snapshot"
# ---------------------------------------------------------------------------
class TestPhaseAHeader:
    """SPEC-1458: phase_a prints 'Pre-Deployment Snapshot' header."""

    @patch("upgrade_verification.urlopen")
    def test_phase_a_prints_header(self, mock_urlopen, capsys):
        mock_resp = _make_mock_response(
            200,
            {"state": "active", "is_active": True, "is_configured": True,
             "has_pending_changes": False, "active_version": 1,
             "totalCount": 0, "status_breakdown": {},
             "members": []},
            [("x-product-version", "1.60.0")],
        )
        mock_urlopen.return_value = mock_resp
        env = ENVIRONMENTS["staging"].copy()
        phase_a(env)
        captured = capsys.readouterr()
        assert "Pre-Deployment Snapshot" in captured.out


# ---------------------------------------------------------------------------
# SPEC-1459: Phase C performs post-deployment verification
# ---------------------------------------------------------------------------
class TestPhaseCVerification:
    """SPEC-1459: phase_c returns a list of result dicts."""

    @patch("upgrade_verification.time.sleep")  # skip rate limit sleeps
    @patch("upgrade_verification.urlopen")
    def test_phase_c_returns_list(self, mock_urlopen, mock_sleep):
        mock_resp = _make_mock_response(
            200,
            {"state": "active", "is_active": True, "is_configured": True,
             "has_pending_changes": False, "totalCount": 5,
             "status_breakdown": {}, "members": [],
             "total": 1, "overallStatus": "healthy",
             "tenantId": "staging-001", "totalPlatformCost": 0,
             "totalTenantsScanned": 0, "current_tier": "starter",
             "addons": [1, 2, 3, 4], "total_vectors": 0,
             "memory_enabled": False, "etag": "x", "fcrRate": 0,
             "direction": "up"},
            [("x-product-version", "1.60.0")],
        )
        mock_urlopen.return_value = mock_resp
        _make_mock_response(201, {"conversation_id": "c1"})
        # widget_call uses urlopen too — it will get the same mock
        env = ENVIRONMENTS["staging"].copy()
        snapshot = {
            "A1_version": "1.59.0",
            "A2_status": "active",
            "A3_activation": {"is_active": True, "is_configured": True, "has_pending_changes": False},
            "A4_conversation_count": 5,
            "A5_status_breakdown": {},
            "A6_kb_count": 5,
            "A7_team_count": 0,
            "A8_team_members": [],
            "A9_draft_status": 200,
            "A10_config_keys": [],
            "A11_widget_key_exists": True,
        }
        result = phase_c(env, snapshot, "1.60.0")
        assert isinstance(result, list)

    @patch("upgrade_verification.time.sleep")
    @patch("upgrade_verification.urlopen")
    def test_phase_c_results_have_expected_shape(self, mock_urlopen, mock_sleep):
        mock_resp = _make_mock_response(
            200,
            {"state": "active", "is_active": True, "is_configured": True,
             "has_pending_changes": False, "totalCount": 5,
             "status_breakdown": {}, "members": [],
             "total": 1, "overallStatus": "healthy",
             "tenantId": "staging-001", "totalPlatformCost": 0,
             "totalTenantsScanned": 0, "current_tier": "starter",
             "addons": [1, 2, 3, 4], "total_vectors": 0,
             "memory_enabled": False, "etag": "x", "fcrRate": 0,
             "direction": "up"},
            [("x-product-version", "1.60.0")],
        )
        mock_urlopen.return_value = mock_resp
        env = ENVIRONMENTS["staging"].copy()
        snapshot = {
            "A2_status": "active",
            "A3_activation": {"is_active": True, "is_configured": True, "has_pending_changes": False},
            "A4_conversation_count": 5,
            "A5_status_breakdown": {},
            "A6_kb_count": 5,
            "A7_team_count": 0,
            "A8_team_members": [],
            "A9_draft_status": 200,
            "A10_config_keys": [],
        }
        result = phase_c(env, snapshot, "1.60.0")
        assert len(result) > 0
        for r in result:
            assert "id" in r
            assert "description" in r
            assert "status" in r
            assert r["status"] in ("PASS", "FAIL")


# ---------------------------------------------------------------------------
# SPEC-1460: Phase C makes ~30 authenticated calls
# ---------------------------------------------------------------------------
class TestPhaseCCallCount:
    """SPEC-1460: phase_c makes approximately 30 authenticated API calls."""

    @patch("upgrade_verification.time.sleep")
    @patch("upgrade_verification.urlopen")
    def test_phase_c_makes_many_calls(self, mock_urlopen, mock_sleep):
        mock_resp = _make_mock_response(
            200,
            {"state": "active", "is_active": True, "is_configured": True,
             "has_pending_changes": False, "totalCount": 5,
             "status_breakdown": {}, "members": [],
             "total": 1, "overallStatus": "healthy",
             "tenantId": "staging-001", "totalPlatformCost": 0,
             "totalTenantsScanned": 0, "current_tier": "starter",
             "addons": [1, 2, 3, 4], "total_vectors": 0,
             "memory_enabled": False, "etag": "x", "fcrRate": 0,
             "direction": "up"},
            [("x-product-version", "1.60.0")],
        )
        mock_urlopen.return_value = mock_resp
        env = ENVIRONMENTS["staging"].copy()
        snapshot = {
            "A2_status": "active",
            "A3_activation": {"is_active": True, "is_configured": True, "has_pending_changes": False},
            "A4_conversation_count": 5,
            "A5_status_breakdown": {},
            "A6_kb_count": 5,
            "A7_team_count": 0,
            "A8_team_members": [],
            "A9_draft_status": 200,
            "A10_config_keys": [],
        }
        phase_c(env, snapshot, "1.60.0")
        # Phase C has 35 checks (C.1 through C.35).
        # Each non-SKIP check makes at least one urlopen call.
        # The function also uses a rate-limited wrapper.
        # We expect at least 20 calls (some are SKIPs).
        assert mock_urlopen.call_count >= 20, (
            f"Expected ~30 API calls, got {mock_urlopen.call_count}"
        )


# ---------------------------------------------------------------------------
# SPEC-1461: Phase C prints header "Post-Deployment Verification"
# ---------------------------------------------------------------------------
class TestPhaseCHeader:
    """SPEC-1461: phase_c prints 'Post-Deployment Verification' header."""

    @patch("upgrade_verification.time.sleep")
    @patch("upgrade_verification.urlopen")
    def test_phase_c_prints_header(self, mock_urlopen, mock_sleep, capsys):
        mock_resp = _make_mock_response(
            200,
            {"state": "active", "is_active": True, "is_configured": True,
             "has_pending_changes": False, "totalCount": 5,
             "status_breakdown": {}, "members": [],
             "total": 1, "overallStatus": "healthy",
             "tenantId": "staging-001", "totalPlatformCost": 0,
             "totalTenantsScanned": 0, "current_tier": "starter",
             "addons": [1, 2, 3, 4], "total_vectors": 0,
             "memory_enabled": False, "etag": "x", "fcrRate": 0,
             "direction": "up"},
            [("x-product-version", "1.60.0")],
        )
        mock_urlopen.return_value = mock_resp
        env = ENVIRONMENTS["staging"].copy()
        snapshot = {
            "A2_status": "active",
            "A3_activation": {"is_active": True, "is_configured": True, "has_pending_changes": False},
            "A4_conversation_count": 5,
            "A5_status_breakdown": {},
            "A6_kb_count": 5,
            "A7_team_count": 0,
            "A8_team_members": [],
            "A9_draft_status": 200,
            "A10_config_keys": [],
        }
        phase_c(env, snapshot, "1.60.0")
        captured = capsys.readouterr()
        assert "Post-Deployment Verification" in captured.out


# ---------------------------------------------------------------------------
# SPEC-1462: Phase A snapshot saved as JSON for Phase C consumption
# ---------------------------------------------------------------------------
class TestPhaseASnapshotJSON:
    """SPEC-1462: Phase A snapshot is serializable JSON for Phase C."""

    @patch("upgrade_verification.urlopen")
    def test_snapshot_is_json_serializable(self, mock_urlopen):
        mock_resp = _make_mock_response(
            200,
            {"state": "active", "is_active": True, "is_configured": True,
             "has_pending_changes": False, "active_version": 1,
             "totalCount": 5, "status_breakdown": {},
             "members": [{"displayName": "Admin", "role": "superadmin"}]},
            [("x-product-version", "1.60.0")],
        )
        mock_urlopen.return_value = mock_resp
        env = ENVIRONMENTS["staging"].copy()
        result = phase_a(env)
        # Must be serializable to JSON for phase-c --snapshot
        serialized = json.dumps(result)
        deserialized = json.loads(serialized)
        assert deserialized == result


# ---------------------------------------------------------------------------
# SPEC-1463: Phase A (multi-a) iterates all tenants
# ---------------------------------------------------------------------------
class TestPhaseAIteratesTenants:
    """SPEC-1463: _all_tenants returns default + extra tenants for multi-a."""

    def test_all_tenants_includes_default(self):
        tenants = _all_tenants("staging")
        tenant_ids = [t["tenant_id"] for t in tenants]
        assert "staging-001" in tenant_ids

    def test_all_tenants_includes_extras(self):
        tenants = _all_tenants("staging")
        tenant_ids = [t["tenant_id"] for t in tenants]
        assert "staging-002" in tenant_ids

    def test_all_tenants_count(self):
        tenants = _all_tenants("staging")
        # Default (test-customer-001) + extra staging-001 + extra staging-002 = 3
        assert len(tenants) == 3

    def test_all_tenants_production_has_no_extras(self):
        tenants = _all_tenants("production")
        # Production has no extra tenants in TENANTS dict
        assert len(tenants) == 1
        assert tenants[0]["tenant_id"] == "remaker-digital-001"


# ---------------------------------------------------------------------------
# SPEC-1464: Phase C (multi-c) iterates all tenants
# ---------------------------------------------------------------------------
class TestPhaseCIteratesTenants:
    """SPEC-1464: multi-c uses _all_tenants to iterate all tenants."""

    def test_all_tenants_preserves_fqdn(self):
        """Each env dict from _all_tenants shares the base fqdn."""
        tenants = _all_tenants("staging")
        for t in tenants:
            assert t["fqdn"] == ENVIRONMENTS["staging"]["fqdn"]

    def test_all_tenants_has_unique_credentials(self):
        """Each tenant with credentials has distinct api_key and widget_key.

        In container environments, extra tenant env vars (STAGING_001_TENANT_KEY
        etc.) may not be set, producing empty strings. We filter those out —
        the real assertion is that *configured* tenants have unique credentials.
        """
        tenants = _all_tenants("staging")
        api_keys = [t["api_key"] for t in tenants if t["api_key"]]
        widget_keys = [t["widget_key"] for t in tenants if t["widget_key"]]
        assert len(set(api_keys)) == len(api_keys), "Duplicate api_keys among configured tenants"
        assert len(set(widget_keys)) == len(widget_keys), "Duplicate widget_keys among configured tenants"


# ---------------------------------------------------------------------------
# Additional structural tests
# ---------------------------------------------------------------------------
class TestEnvironmentsStructure:
    """Structural validation of ENVIRONMENTS and TENANTS dicts."""

    def test_environments_has_staging(self):
        assert "staging" in ENVIRONMENTS

    def test_environments_has_production(self):
        assert "production" in ENVIRONMENTS

    @pytest.mark.parametrize("env_name", ["staging", "production"])
    def test_environment_has_required_keys(self, env_name):
        required = {"fqdn", "container_app", "tenant_id", "api_key",
                     "widget_key", "resource_group"}
        assert required.issubset(set(ENVIRONMENTS[env_name].keys()))

    def test_tenants_has_staging_002(self):
        assert "staging:staging-002" in TENANTS

    def test_resolve_env_default_tenant(self):
        env = _resolve_env("staging")
        assert env["tenant_id"] == "remaker-digital-001"  # default staging tenant

    def test_resolve_env_override_tenant(self):
        env = _resolve_env("staging", "staging-002")
        assert env["tenant_id"] == "staging-002"
        assert env["api_key"] == TENANTS["staging:staging-002"]["api_key"]


class TestFunctionSignatures:
    """Validate function signatures match expected parameters."""

    def test_api_call_params(self):
        params = list(inspect.signature(api_call).parameters.keys())
        assert params == ["fqdn", "path", "api_key", "method", "body", "timeout"]

    def test_widget_call_params(self):
        params = list(inspect.signature(widget_call).parameters.keys())
        assert params == ["fqdn", "widget_key", "timeout"]
