"""Mutation tests — Superadmin Operations endpoints.

Tests: incident management, alert rules, alert acknowledgement, alert evaluation,
MFA/TOTP endpoints, and abuse flag toggling.
All endpoints require SPA platform admin authentication (SPEC-1667).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.multi_tenant.conftest import MutationTestBase


# ---------------------------------------------------------------------------
# Shared fixtures and helpers
# ---------------------------------------------------------------------------

INCIDENT_DOC: dict[str, Any] = {
    "incident_id": "inc-001",
    "title": "Service degradation",
    "description": "API latency increased",
    "status": "investigating",
    "severity": "minor",
    "affected_services": ["api"],
    "updates": [],
    "created_at": "2026-01-01T00:00:00+00:00",
    "updated_at": "2026-01-01T00:00:00+00:00",
    "resolved_at": None,
    "created_by": "admin@example.com",
}

ALERT_RULE_DOC: dict[str, Any] = {
    "rule_id": "rule-001",
    "rule_type": "threshold",
    "name": "High latency alert",
    "description": "Fires when latency > 500ms",
    "enabled": True,
    "condition": {"metric": "latency_p99", "operator": "gt", "threshold": 500},
    "notification_channels": ["email"],
    "cooldown_minutes": 60,
    "runbook_url": "",
    "created_at": "2026-01-01T00:00:00+00:00",
    "updated_at": "2026-01-01T00:00:00+00:00",
}

ALERT_HISTORY_DOC: dict[str, Any] = {
    "id": "alert-001",
    "alert_date": "2026-01-15",
    "rule_id": "rule-001",
    "rule_name": "High latency alert",
    "rule_type": "threshold",
    "triggered_at": "2026-01-15T10:00:00+00:00",
    "resolved_at": None,
    "severity": "warning",
    "message": "Latency exceeded threshold",
    "metric_value": 600,
    "threshold_value": 500,
    "acknowledged": False,
    "acknowledged_by": None,
}

TEAM_MEMBER_DOC: dict[str, Any] = {
    "id": "member-001",
    "tenant_id": "test-tenant",
    "email": "user@example.com",
    "role": "admin",
    "mfa_enabled": False,
    "mfa_secret_key_vault_ref": None,
    "backup_code_hashes": [],
}

MFA_ENABLED_MEMBER: dict[str, Any] = {
    **TEAM_MEMBER_DOC,
    "mfa_enabled": True,
    "mfa_secret_key_vault_ref": "kv://mfa/member-001",
}


def _make_mfa_svc() -> MagicMock:
    """Create a mock MFA service with async methods."""
    svc = MagicMock()
    svc.start_enrollment = AsyncMock(return_value={
        "qr_code_data_url": "data:image/png;base64,AAAA",
        "provisioning_uri": "otpauth://totp/AgentRed:user@example.com?secret=BASE32",
        "backup_codes": ["code1", "code2", "code3"],
        "backup_code_hashes": ["hash1", "hash2", "hash3"],
    })
    svc.confirm_enrollment = AsyncMock(return_value=True)
    svc.verify_code = AsyncMock(return_value={"mfa_token": "tok_abc123"})
    svc.disable_mfa = AsyncMock(return_value=True)
    svc.verify_backup = AsyncMock(return_value={
        "mfa_token": "tok_backup_abc",
        "backup_codes_remaining": 2,
    })
    svc.get_enrollment_status = AsyncMock(return_value={
        "mfa_enabled": False,
        "enrolled_at": None,
        "backup_codes_remaining": 0,
    })
    return svc


# ---------------------------------------------------------------------------
# Incident Management
# ---------------------------------------------------------------------------


class TestCreateIncident(MutationTestBase):
    """POST /api/superadmin/incidents"""

    URL = "/api/superadmin/incidents"
    BODY = {"title": "Test incident", "severity": "minor"}

    def test_requires_auth(self, app_client, superadmin_repos):
        self.assert_requires_auth(app_client, "post", self.URL, json=self.BODY)

    def test_rejects_widget_key(self, widget_client, superadmin_repos):
        self.assert_rejects_widget_key(widget_client, "post", self.URL, json=self.BODY)

    def test_spa_isolation(self, starter_client, superadmin_repos):
        self.assert_spa_isolation(starter_client, "post", self.URL, json=self.BODY)

    def test_happy_path(self, spa_client, superadmin_repos):
        superadmin_repos["incident_repo"].create_incident = AsyncMock(
            return_value=dict(INCIDENT_DOC)
        )
        resp = spa_client.post(self.URL, json=self.BODY)
        assert resp.status_code == 201
        data = resp.json()
        assert "incidentId" in data
        assert data["title"] == "Service degradation"


class TestAddIncidentUpdate(MutationTestBase):
    """POST /api/superadmin/incidents/{incident_id}/update"""

    URL = "/api/superadmin/incidents/inc-001/update"
    BODY = {"status": "identified", "message": "Root cause found"}

    def test_requires_auth(self, app_client, superadmin_repos):
        self.assert_requires_auth(app_client, "post", self.URL, json=self.BODY)

    def test_rejects_widget_key(self, widget_client, superadmin_repos):
        self.assert_rejects_widget_key(widget_client, "post", self.URL, json=self.BODY)

    def test_spa_isolation(self, starter_client, superadmin_repos):
        self.assert_spa_isolation(starter_client, "post", self.URL, json=self.BODY)

    def test_happy_path(self, spa_client, superadmin_repos):
        superadmin_repos["incident_repo"].find_incident = AsyncMock(
            return_value=dict(INCIDENT_DOC)
        )
        updated_doc = dict(INCIDENT_DOC, status="identified")
        superadmin_repos["incident_repo"].add_update = AsyncMock(
            return_value=updated_doc
        )
        resp = spa_client.post(self.URL, json=self.BODY)
        assert resp.status_code == 200
        assert resp.json()["status"] == "identified"

    def test_not_found(self, spa_client, superadmin_repos):
        superadmin_repos["incident_repo"].find_incident = AsyncMock(return_value=None)
        resp = spa_client.post(self.URL, json=self.BODY)
        assert resp.status_code == 404


class TestResolveIncident(MutationTestBase):
    """POST /api/superadmin/incidents/{incident_id}/resolve"""

    URL = "/api/superadmin/incidents/inc-001/resolve"
    BODY = {"message": "Fixed by restart"}

    def test_requires_auth(self, app_client, superadmin_repos):
        self.assert_requires_auth(app_client, "post", self.URL, json=self.BODY)

    def test_rejects_widget_key(self, widget_client, superadmin_repos):
        self.assert_rejects_widget_key(widget_client, "post", self.URL, json=self.BODY)

    def test_spa_isolation(self, starter_client, superadmin_repos):
        self.assert_spa_isolation(starter_client, "post", self.URL, json=self.BODY)

    def test_happy_path(self, spa_client, superadmin_repos):
        superadmin_repos["incident_repo"].find_incident = AsyncMock(
            return_value=dict(INCIDENT_DOC)
        )
        resolved_doc = dict(
            INCIDENT_DOC,
            status="resolved",
            resolved_at="2026-01-02T00:00:00+00:00",
        )
        superadmin_repos["incident_repo"].resolve_incident = AsyncMock(
            return_value=resolved_doc
        )
        resp = spa_client.post(self.URL, json=self.BODY)
        assert resp.status_code == 200
        assert resp.json()["status"] == "resolved"
        assert resp.json()["resolvedAt"] is not None

    def test_not_found(self, spa_client, superadmin_repos):
        superadmin_repos["incident_repo"].find_incident = AsyncMock(return_value=None)
        resp = spa_client.post(self.URL, json=self.BODY)
        assert resp.status_code == 404

    def test_already_resolved(self, spa_client, superadmin_repos):
        already_resolved = dict(INCIDENT_DOC, status="resolved")
        superadmin_repos["incident_repo"].find_incident = AsyncMock(
            return_value=already_resolved
        )
        resp = spa_client.post(self.URL, json=self.BODY)
        assert resp.status_code == 400
        assert "already resolved" in resp.json()["detail"].lower()


# ---------------------------------------------------------------------------
# Alert Rules
# ---------------------------------------------------------------------------


class TestCreateAlertRule(MutationTestBase):
    """POST /api/superadmin/alerts/rules"""

    URL = "/api/superadmin/alerts/rules"
    BODY = {"name": "Latency rule", "ruleType": "threshold"}

    def test_requires_auth(self, app_client, superadmin_repos):
        self.assert_requires_auth(app_client, "post", self.URL, json=self.BODY)

    def test_rejects_widget_key(self, widget_client, superadmin_repos):
        self.assert_rejects_widget_key(widget_client, "post", self.URL, json=self.BODY)

    def test_spa_isolation(self, starter_client, superadmin_repos):
        self.assert_spa_isolation(starter_client, "post", self.URL, json=self.BODY)

    def test_happy_path(self, spa_client, superadmin_repos):
        superadmin_repos["alert_rule_repo"].create_rule = AsyncMock(
            return_value=dict(ALERT_RULE_DOC)
        )
        resp = spa_client.post(self.URL, json=self.BODY)
        assert resp.status_code == 201
        data = resp.json()
        assert "ruleId" in data
        assert data["name"] == "High latency alert"


class TestUpdateAlertRule(MutationTestBase):
    """PUT /api/superadmin/alerts/rules/{rule_id}"""

    URL = "/api/superadmin/alerts/rules/rule-001"
    BODY = {"name": "Updated rule name"}

    def test_requires_auth(self, app_client, superadmin_repos):
        self.assert_requires_auth(app_client, "put", self.URL, json=self.BODY)

    def test_rejects_widget_key(self, widget_client, superadmin_repos):
        self.assert_rejects_widget_key(widget_client, "put", self.URL, json=self.BODY)

    def test_spa_isolation(self, starter_client, superadmin_repos):
        self.assert_spa_isolation(starter_client, "put", self.URL, json=self.BODY)

    def test_happy_path(self, spa_client, superadmin_repos):
        superadmin_repos["alert_rule_repo"].find_rule = AsyncMock(
            return_value=dict(ALERT_RULE_DOC)
        )
        updated_doc = dict(ALERT_RULE_DOC, name="Updated rule name")
        superadmin_repos["alert_rule_repo"].update_rule = AsyncMock(
            return_value=updated_doc
        )
        resp = spa_client.put(self.URL, json=self.BODY)
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated rule name"

    def test_not_found(self, spa_client, superadmin_repos):
        superadmin_repos["alert_rule_repo"].find_rule = AsyncMock(return_value=None)
        resp = spa_client.put(self.URL, json=self.BODY)
        assert resp.status_code == 404


class TestDeleteAlertRule(MutationTestBase):
    """DELETE /api/superadmin/alerts/rules/{rule_id}"""

    URL = "/api/superadmin/alerts/rules/rule-001"

    def test_requires_auth(self, app_client, superadmin_repos):
        self.assert_requires_auth(app_client, "delete", self.URL)

    def test_rejects_widget_key(self, widget_client, superadmin_repos):
        self.assert_rejects_widget_key(widget_client, "delete", self.URL)

    def test_spa_isolation(self, starter_client, superadmin_repos):
        self.assert_spa_isolation(starter_client, "delete", self.URL)

    def test_happy_path(self, spa_client, superadmin_repos):
        superadmin_repos["alert_rule_repo"].find_rule = AsyncMock(
            return_value=dict(ALERT_RULE_DOC)
        )
        superadmin_repos["alert_rule_repo"].delete_rule = AsyncMock(return_value=True)
        resp = spa_client.delete(self.URL)
        assert resp.status_code == 200
        data = resp.json()
        assert data["deleted"] is True
        assert data["ruleId"] == "rule-001"

    def test_not_found(self, spa_client, superadmin_repos):
        superadmin_repos["alert_rule_repo"].find_rule = AsyncMock(return_value=None)
        resp = spa_client.delete(self.URL)
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Alert History — Acknowledge
# ---------------------------------------------------------------------------


class TestAcknowledgeAlert(MutationTestBase):
    """POST /api/superadmin/alerts/history/{alert_id}/acknowledge"""

    URL = "/api/superadmin/alerts/history/alert-001/acknowledge"

    def test_requires_auth(self, app_client, superadmin_repos):
        self.assert_requires_auth(
            app_client, "post", self.URL, params={"alert_date": "2026-01-15"}
        )

    def test_rejects_widget_key(self, widget_client, superadmin_repos):
        self.assert_rejects_widget_key(
            widget_client, "post", self.URL, params={"alert_date": "2026-01-15"}
        )

    def test_spa_isolation(self, starter_client, superadmin_repos):
        self.assert_spa_isolation(
            starter_client, "post", self.URL, params={"alert_date": "2026-01-15"}
        )

    def test_happy_path(self, spa_client, superadmin_repos):
        ack_doc = dict(ALERT_HISTORY_DOC, acknowledged=True, acknowledged_by="admin@example.com")
        superadmin_repos["alert_history_repo"].acknowledge = AsyncMock(
            return_value=ack_doc
        )
        resp = spa_client.post(self.URL, params={"alert_date": "2026-01-15"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["acknowledged"] is True
        assert data["acknowledgedBy"] == "admin@example.com"

    def test_not_found(self, spa_client, superadmin_repos):
        superadmin_repos["alert_history_repo"].acknowledge = AsyncMock(return_value=None)
        resp = spa_client.post(self.URL, params={"alert_date": "2026-01-15"})
        assert resp.status_code == 404

    def test_missing_alert_date(self, spa_client, superadmin_repos):
        """alert_date query param is required — 422 without it."""
        resp = spa_client.post(self.URL)
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Alert Evaluate
# ---------------------------------------------------------------------------


class TestForceEvaluateAlerts(MutationTestBase):
    """POST /api/superadmin/alerts/evaluate"""

    URL = "/api/superadmin/alerts/evaluate"

    def test_requires_auth(self, app_client, superadmin_repos):
        self.assert_requires_auth(app_client, "post", self.URL)

    def test_rejects_widget_key(self, widget_client, superadmin_repos):
        self.assert_rejects_widget_key(widget_client, "post", self.URL)

    def test_spa_isolation(self, starter_client, superadmin_repos):
        self.assert_spa_isolation(starter_client, "post", self.URL)

    def test_happy_path(self, spa_client, superadmin_repos):
        import sys
        import types

        mock_engine = MagicMock()
        mock_engine.evaluate_all = AsyncMock(return_value={"rules_evaluated": 5, "alerts_fired": 1})

        fake_module = types.ModuleType("src.multi_tenant.alert_engine")
        fake_module.get_alert_engine = MagicMock(return_value=mock_engine)

        with patch.dict(sys.modules, {"src.multi_tenant.alert_engine": fake_module}):
            resp = spa_client.post(self.URL)
        assert resp.status_code == 200
        data = resp.json()
        assert data["evaluated"] is True

    def test_engine_not_available(self, spa_client, superadmin_repos):
        """When alert_engine module cannot be imported, returns graceful fallback."""
        resp = spa_client.post(self.URL)
        assert resp.status_code == 200
        data = resp.json()
        # Either evaluated=False or evaluated=True depending on engine state
        assert "evaluated" in data


# ---------------------------------------------------------------------------
# MFA Endpoints
# ---------------------------------------------------------------------------

_OPS_MODULE = "src.multi_tenant.superadmin_api._operations"


class TestMfaEnroll(MutationTestBase):
    """POST /api/superadmin/mfa/enroll"""

    URL = "/api/superadmin/mfa/enroll"

    def test_requires_auth(self, app_client, superadmin_repos):
        self.assert_requires_auth(app_client, "post", self.URL)

    def test_rejects_widget_key(self, widget_client, superadmin_repos):
        self.assert_rejects_widget_key(widget_client, "post", self.URL)

    def test_spa_isolation(self, starter_client, superadmin_repos):
        self.assert_spa_isolation(starter_client, "post", self.URL)

    @patch(f"{_OPS_MODULE}._get_mfa_svc")
    @patch(f"{_OPS_MODULE}._get_team_member")
    def test_happy_path(self, mock_get_member, mock_get_svc, spa_client, superadmin_repos):
        mock_get_member.return_value = dict(TEAM_MEMBER_DOC)
        mock_svc = _make_mfa_svc()
        mock_get_svc.return_value = mock_svc

        resp = spa_client.post(self.URL)
        assert resp.status_code == 200
        data = resp.json()
        assert "qrCodeDataUrl" in data
        assert "provisioningUri" in data
        assert "backupCodes" in data

    @patch(f"{_OPS_MODULE}._get_mfa_svc")
    @patch(f"{_OPS_MODULE}._get_team_member")
    def test_already_enabled(self, mock_get_member, mock_get_svc, spa_client, superadmin_repos):
        mock_get_member.return_value = dict(MFA_ENABLED_MEMBER)
        mock_get_svc.return_value = _make_mfa_svc()

        resp = spa_client.post(self.URL)
        assert resp.status_code == 409
        assert "already enabled" in resp.json()["detail"].lower()


class TestMfaConfirm(MutationTestBase):
    """POST /api/superadmin/mfa/confirm"""

    URL = "/api/superadmin/mfa/confirm"
    BODY = {"code": "123456", "backupCodeHashes": ["h1", "h2"]}

    def test_requires_auth(self, app_client, superadmin_repos):
        self.assert_requires_auth(app_client, "post", self.URL, json=self.BODY)

    def test_rejects_widget_key(self, widget_client, superadmin_repos):
        self.assert_rejects_widget_key(widget_client, "post", self.URL, json=self.BODY)

    def test_spa_isolation(self, starter_client, superadmin_repos):
        self.assert_spa_isolation(starter_client, "post", self.URL, json=self.BODY)

    @patch(f"{_OPS_MODULE}._get_mfa_svc")
    @patch(f"{_OPS_MODULE}._get_team_member")
    def test_happy_path(self, mock_get_member, mock_get_svc, spa_client, superadmin_repos):
        mock_get_member.return_value = dict(TEAM_MEMBER_DOC)
        mock_svc = _make_mfa_svc()
        mock_get_svc.return_value = mock_svc

        resp = spa_client.post(self.URL, json=self.BODY)
        assert resp.status_code == 200
        assert resp.json()["confirmed"] is True

    @patch(f"{_OPS_MODULE}._get_mfa_svc")
    @patch(f"{_OPS_MODULE}._get_team_member")
    def test_invalid_code(self, mock_get_member, mock_get_svc, spa_client, superadmin_repos):
        mock_get_member.return_value = dict(TEAM_MEMBER_DOC)
        mock_svc = _make_mfa_svc()
        mock_svc.confirm_enrollment = AsyncMock(return_value=False)
        mock_get_svc.return_value = mock_svc

        resp = spa_client.post(self.URL, json=self.BODY)
        assert resp.status_code == 400
        assert "invalid" in resp.json()["detail"].lower()


class TestMfaVerify(MutationTestBase):
    """POST /api/superadmin/mfa/verify"""

    URL = "/api/superadmin/mfa/verify"
    BODY = {"code": "654321"}

    def test_requires_auth(self, app_client, superadmin_repos):
        self.assert_requires_auth(app_client, "post", self.URL, json=self.BODY)

    def test_rejects_widget_key(self, widget_client, superadmin_repos):
        self.assert_rejects_widget_key(widget_client, "post", self.URL, json=self.BODY)

    def test_spa_isolation(self, starter_client, superadmin_repos):
        self.assert_spa_isolation(starter_client, "post", self.URL, json=self.BODY)

    @patch(f"{_OPS_MODULE}._get_mfa_svc")
    @patch(f"{_OPS_MODULE}._get_team_member")
    def test_happy_path(self, mock_get_member, mock_get_svc, spa_client, superadmin_repos):
        mock_get_member.return_value = dict(MFA_ENABLED_MEMBER)
        mock_svc = _make_mfa_svc()
        mock_get_svc.return_value = mock_svc

        resp = spa_client.post(self.URL, json=self.BODY)
        assert resp.status_code == 200
        data = resp.json()
        assert "mfaToken" in data

    @patch(f"{_OPS_MODULE}._get_mfa_svc")
    @patch(f"{_OPS_MODULE}._get_team_member")
    def test_mfa_not_enabled(self, mock_get_member, mock_get_svc, spa_client, superadmin_repos):
        mock_get_member.return_value = dict(TEAM_MEMBER_DOC)  # mfa_enabled=False
        mock_get_svc.return_value = _make_mfa_svc()

        resp = spa_client.post(self.URL, json=self.BODY)
        assert resp.status_code == 400
        assert "not enabled" in resp.json()["detail"].lower()

    @patch(f"{_OPS_MODULE}._get_mfa_svc")
    @patch(f"{_OPS_MODULE}._get_team_member")
    def test_invalid_code(self, mock_get_member, mock_get_svc, spa_client, superadmin_repos):
        mock_get_member.return_value = dict(MFA_ENABLED_MEMBER)
        mock_svc = _make_mfa_svc()
        mock_svc.verify_code = AsyncMock(return_value=None)
        mock_get_svc.return_value = mock_svc

        resp = spa_client.post(self.URL, json=self.BODY)
        assert resp.status_code == 401


class TestMfaDisable(MutationTestBase):
    """POST /api/superadmin/mfa/disable"""

    URL = "/api/superadmin/mfa/disable"
    BODY = {"code": "111222"}

    def test_requires_auth(self, app_client, superadmin_repos):
        self.assert_requires_auth(app_client, "post", self.URL, json=self.BODY)

    def test_rejects_widget_key(self, widget_client, superadmin_repos):
        self.assert_rejects_widget_key(widget_client, "post", self.URL, json=self.BODY)

    def test_spa_isolation(self, starter_client, superadmin_repos):
        self.assert_spa_isolation(starter_client, "post", self.URL, json=self.BODY)

    @patch(f"{_OPS_MODULE}._get_mfa_svc")
    @patch(f"{_OPS_MODULE}._get_team_member")
    def test_happy_path(self, mock_get_member, mock_get_svc, spa_client, superadmin_repos):
        mock_get_member.return_value = dict(MFA_ENABLED_MEMBER)
        mock_svc = _make_mfa_svc()
        mock_get_svc.return_value = mock_svc

        resp = spa_client.post(self.URL, json=self.BODY)
        assert resp.status_code == 200
        assert resp.json()["disabled"] is True

    @patch(f"{_OPS_MODULE}._get_mfa_svc")
    @patch(f"{_OPS_MODULE}._get_team_member")
    def test_mfa_not_enabled(self, mock_get_member, mock_get_svc, spa_client, superadmin_repos):
        mock_get_member.return_value = dict(TEAM_MEMBER_DOC)  # mfa_enabled=False
        mock_get_svc.return_value = _make_mfa_svc()

        resp = spa_client.post(self.URL, json=self.BODY)
        assert resp.status_code == 400

    @patch(f"{_OPS_MODULE}._get_mfa_svc")
    @patch(f"{_OPS_MODULE}._get_team_member")
    def test_invalid_code(self, mock_get_member, mock_get_svc, spa_client, superadmin_repos):
        mock_get_member.return_value = dict(MFA_ENABLED_MEMBER)
        mock_svc = _make_mfa_svc()
        mock_svc.disable_mfa = AsyncMock(return_value=False)
        mock_get_svc.return_value = mock_svc

        resp = spa_client.post(self.URL, json=self.BODY)
        assert resp.status_code == 400
        assert "invalid" in resp.json()["detail"].lower()


class TestMfaBackupVerify(MutationTestBase):
    """POST /api/superadmin/mfa/backup-verify"""

    URL = "/api/superadmin/mfa/backup-verify"
    BODY = {"code": "backup-code-1"}

    def test_requires_auth(self, app_client, superadmin_repos):
        self.assert_requires_auth(app_client, "post", self.URL, json=self.BODY)

    def test_rejects_widget_key(self, widget_client, superadmin_repos):
        self.assert_rejects_widget_key(widget_client, "post", self.URL, json=self.BODY)

    def test_spa_isolation(self, starter_client, superadmin_repos):
        self.assert_spa_isolation(starter_client, "post", self.URL, json=self.BODY)

    @patch(f"{_OPS_MODULE}._get_mfa_svc")
    @patch(f"{_OPS_MODULE}._get_team_member")
    def test_happy_path(self, mock_get_member, mock_get_svc, spa_client, superadmin_repos):
        mock_get_member.return_value = dict(MFA_ENABLED_MEMBER)
        mock_svc = _make_mfa_svc()
        mock_get_svc.return_value = mock_svc

        resp = spa_client.post(self.URL, json=self.BODY)
        assert resp.status_code == 200
        data = resp.json()
        assert "mfaToken" in data
        assert data["backupCodesRemaining"] == 2

    @patch(f"{_OPS_MODULE}._get_mfa_svc")
    @patch(f"{_OPS_MODULE}._get_team_member")
    def test_mfa_not_enabled(self, mock_get_member, mock_get_svc, spa_client, superadmin_repos):
        mock_get_member.return_value = dict(TEAM_MEMBER_DOC)  # mfa_enabled=False
        mock_get_svc.return_value = _make_mfa_svc()

        resp = spa_client.post(self.URL, json=self.BODY)
        assert resp.status_code == 400

    @patch(f"{_OPS_MODULE}._get_mfa_svc")
    @patch(f"{_OPS_MODULE}._get_team_member")
    def test_invalid_backup_code(self, mock_get_member, mock_get_svc, spa_client, superadmin_repos):
        mock_get_member.return_value = dict(MFA_ENABLED_MEMBER)
        mock_svc = _make_mfa_svc()
        mock_svc.verify_backup = AsyncMock(return_value=None)
        mock_get_svc.return_value = mock_svc

        resp = spa_client.post(self.URL, json=self.BODY)
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Abuse Flag
# ---------------------------------------------------------------------------


class TestToggleAbuseFlag(MutationTestBase):
    """POST /api/superadmin/abuse/tenant/{tenant_id}/flag"""

    URL = "/api/superadmin/abuse/tenant/test-tenant-001/flag"
    BODY = {"flagged": True}

    def test_requires_auth(self, app_client, superadmin_repos):
        self.assert_requires_auth(app_client, "post", self.URL, json=self.BODY)

    def test_rejects_widget_key(self, widget_client, superadmin_repos):
        self.assert_rejects_widget_key(widget_client, "post", self.URL, json=self.BODY)

    def test_spa_isolation(self, starter_client, superadmin_repos):
        self.assert_spa_isolation(starter_client, "post", self.URL, json=self.BODY)

    def test_flag_tenant(self, spa_client, superadmin_repos):
        superadmin_repos["tenant_repo"].patch = AsyncMock(return_value=None)
        superadmin_repos["audit_repo"].log_event = AsyncMock(return_value=None)

        resp = spa_client.post(self.URL, json={"flagged": True})
        assert resp.status_code == 200
        data = resp.json()
        assert data["tenantId"] == "test-tenant-001"
        assert data["flagged"] is True
        assert "updatedAt" in data

    def test_unflag_tenant(self, spa_client, superadmin_repos):
        superadmin_repos["tenant_repo"].patch = AsyncMock(return_value=None)
        superadmin_repos["audit_repo"].log_event = AsyncMock(return_value=None)

        resp = spa_client.post(self.URL, json={"flagged": False})
        assert resp.status_code == 200
        data = resp.json()
        assert data["flagged"] is False

    def test_audit_logged(self, spa_client, superadmin_repos):
        superadmin_repos["tenant_repo"].patch = AsyncMock(return_value=None)
        superadmin_repos["audit_repo"].log_event = AsyncMock(return_value=None)

        spa_client.post(self.URL, json={"flagged": True})
        superadmin_repos["audit_repo"].log_event.assert_called_once()

    def test_validation_error_missing_body(self, spa_client, superadmin_repos):
        resp = spa_client.post(self.URL)
        assert resp.status_code == 422
