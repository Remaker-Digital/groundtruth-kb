"""Tests for SPEC-1611: Issue report triggers escalation alert (WI-0933).

Verifies that when a customer submits an issue report, the report_issue
endpoint calls send_escalation_alert() with the issue type as reason and
the details as context summary.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Source inspection: verify the wiring exists in endpoints.py
# ---------------------------------------------------------------------------


class TestIssueReportEscalationWiring:
    """Source inspection tests — verify endpoints.py has the escalation call."""

    def test_report_issue_imports_send_escalation_alert(self):
        """endpoints.py references send_escalation_alert in report_issue."""
        from pathlib import Path

        src = Path("src/chat/endpoints.py").read_text(encoding="utf-8")
        # Find the report_issue function and check it contains escalation
        idx = src.find("async def report_issue(")
        assert idx != -1, "report_issue function not found"
        # Look at the function body (until the next top-level function)
        body = src[idx:idx + 5000]
        assert "send_escalation_alert" in body, (
            "report_issue must call send_escalation_alert (SPEC-1611)"
        )

    def test_escalation_reason_contains_issue_type(self):
        """Escalation reason must reference the issue type."""
        from pathlib import Path

        src = Path("src/chat/endpoints.py").read_text(encoding="utf-8")
        idx = src.find("async def report_issue(")
        body = src[idx:idx + 5000]
        # The reason should format the issue_type
        assert "issue_type" in body and "reason=" in body, (
            "Escalation reason must include the issue type"
        )

    def test_escalation_context_includes_details(self):
        """Escalation context_summary must include the issue details."""
        from pathlib import Path

        src = Path("src/chat/endpoints.py").read_text(encoding="utf-8")
        idx = src.find("async def report_issue(")
        body = src[idx:idx + 5000]
        assert "context_summary=" in body and "details" in body, (
            "Escalation context_summary must include issue details"
        )

    def test_escalation_is_fire_and_forget(self):
        """Escalation call uses asyncio.ensure_future (non-blocking)."""
        from pathlib import Path

        src = Path("src/chat/endpoints.py").read_text(encoding="utf-8")
        idx = src.find("async def report_issue(")
        body = src[idx:idx + 5000]
        assert "ensure_future" in body, (
            "Escalation must be fire-and-forget via ensure_future"
        )


# ---------------------------------------------------------------------------
# Integration: verify the actual function behavior
# ---------------------------------------------------------------------------


class TestIssueReportEscalation:
    """Integration tests — verify the escalation alert is actually called."""

    @pytest.mark.asyncio
    async def test_report_issue_calls_escalation_alert(self):
        """report_issue calls send_escalation_alert with correct args."""
        from src.chat.endpoints import report_issue, IssueReportRequest

        mock_session = MagicMock()
        mock_session.get_state = AsyncMock(return_value=MagicMock())
        mock_session._conversation_repo = None

        mock_ctx = MagicMock()
        mock_ctx.tenant_id = "test-tenant"

        request = IssueReportRequest(
            issue_type="wrong_information",
            details="The AI gave incorrect pricing for product X",
        )

        captured_calls = []
        AsyncMock()

        async def capture_escalation(**kwargs):
            captured_calls.append(kwargs)

        with patch("src.chat.endpoints._get_session", return_value=mock_session), \
             patch("src.multi_tenant.alert_delivery.send_escalation_alert", side_effect=capture_escalation) as mock_esc, \
             patch("src.multi_tenant.repository.AuditLogRepository"):
            result = await report_issue(
                conversation_id="conv-test-123",
                request=request,
                ctx=mock_ctx,
            )
            # Let the fire-and-forget task run
            await asyncio.sleep(0.1)

        assert result.accepted is True
        assert mock_esc.called or len(captured_calls) > 0

    @pytest.mark.asyncio
    async def test_escalation_reason_includes_issue_type(self):
        """The escalation reason includes a human-readable issue type."""
        from src.chat.endpoints import report_issue, IssueReportRequest

        mock_session = MagicMock()
        mock_session.get_state = AsyncMock(return_value=MagicMock())
        mock_session._conversation_repo = None

        mock_ctx = MagicMock()
        mock_ctx.tenant_id = "test-tenant"

        request = IssueReportRequest(
            issue_type="rude_response",
            details="The AI was dismissive",
        )

        escalation_kwargs = {}

        async def capture(**kw):
            escalation_kwargs.update(kw)

        with patch("src.chat.endpoints._get_session", return_value=mock_session), \
             patch("src.multi_tenant.alert_delivery.send_escalation_alert", side_effect=capture), \
             patch("src.multi_tenant.repository.AuditLogRepository"):
            await report_issue("conv-456", request, mock_ctx)
            await asyncio.sleep(0.1)

        assert "Rude Response" in escalation_kwargs.get("reason", ""), (
            f"Reason should contain human-readable issue type, got: {escalation_kwargs}"
        )

    @pytest.mark.asyncio
    async def test_escalation_context_includes_details(self):
        """The escalation context_summary includes the customer's details."""
        from src.chat.endpoints import report_issue, IssueReportRequest

        mock_session = MagicMock()
        mock_session.get_state = AsyncMock(return_value=MagicMock())
        mock_session._conversation_repo = None

        mock_ctx = MagicMock()
        mock_ctx.tenant_id = "test-tenant"

        details_text = "The pricing shown was $50 but the actual price is $75"
        request = IssueReportRequest(
            issue_type="wrong_information",
            details=details_text,
        )

        escalation_kwargs = {}

        async def capture(**kw):
            escalation_kwargs.update(kw)

        with patch("src.chat.endpoints._get_session", return_value=mock_session), \
             patch("src.multi_tenant.alert_delivery.send_escalation_alert", side_effect=capture), \
             patch("src.multi_tenant.repository.AuditLogRepository"):
            await report_issue("conv-789", request, mock_ctx)
            await asyncio.sleep(0.1)

        assert details_text in escalation_kwargs.get("context_summary", ""), (
            f"Context should include details, got: {escalation_kwargs}"
        )

    @pytest.mark.asyncio
    async def test_escalation_failure_does_not_block_response(self):
        """If send_escalation_alert raises, the response is still returned."""
        from src.chat.endpoints import report_issue, IssueReportRequest

        mock_session = MagicMock()
        mock_session.get_state = AsyncMock(return_value=MagicMock())
        mock_session._conversation_repo = None

        mock_ctx = MagicMock()
        mock_ctx.tenant_id = "test-tenant"

        request = IssueReportRequest(
            issue_type="not_helpful",
            details="Didn't answer my question",
        )

        # Make the import itself raise to trigger the except branch
        with patch("src.chat.endpoints._get_session", return_value=mock_session), \
             patch.dict("sys.modules", {"src.multi_tenant.alert_delivery": None}), \
             patch("src.multi_tenant.repository.AuditLogRepository"):
            result = await report_issue("conv-fail", request, mock_ctx)

        assert result.accepted is True, "Response must succeed even if escalation fails"
