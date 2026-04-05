"""Async email-bridge escalation — send transcript emails to customer and agent.

When the AI escalates a conversation, this module sends two emails:

1. **Customer email:** Confirms the escalation, includes the transcript,
   and sets expectations for response time.
2. **Agent email:** Full transcript with Reply-To set to the customer's
   email so the agent can simply hit Reply.

The chat continues after escalation — this is a fork, not a handoff.

WI-3030 / S259 D16/D17.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime, timezone
from html import escape
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Transcript formatting
# ---------------------------------------------------------------------------


def _format_transcript_html(messages: list[dict[str, Any]]) -> str:
    """Render conversation messages as an HTML transcript for email."""
    rows: list[str] = []
    for msg in messages:
        role = msg.get("role", "system")
        content = msg.get("content", "")
        ts = msg.get("timestamp", "")

        if role == "system":
            continue

        label = "Customer" if role in ("user", "customer") else "AI Agent"
        color = "#1a73e8" if role in ("user", "customer") else "#555555"
        time_str = ""
        if ts:
            try:
                dt = datetime.fromisoformat(ts)
                time_str = dt.strftime("%I:%M %p")
            except (ValueError, TypeError):
                time_str = ""

        rows.append(
            f'<tr>'
            f'<td style="padding:8px 12px;vertical-align:top;color:{color};'
            f'font-weight:600;white-space:nowrap;font-size:13px;">'
            f'{escape(label)}'
            f'{"&nbsp;<span style=&quot;color:#999;font-weight:400;&quot;>" + escape(time_str) + "</span>" if time_str else ""}'
            f'</td>'
            f'<td style="padding:8px 12px;font-size:13px;color:#333;">'
            f'{escape(content)}'
            f'</td>'
            f'</tr>'
        )

    return (
        '<table style="width:100%;border-collapse:collapse;'
        'border:1px solid #e0e0e0;border-radius:8px;overflow:hidden;">'
        f'{"".join(rows)}'
        '</table>'
    )


# ---------------------------------------------------------------------------
# Customer escalation email
# ---------------------------------------------------------------------------


def _build_customer_email_html(
    store_name: str,
    transcript_html: str,
    response_hours: int = 24,
) -> str:
    """Build HTML body for the customer escalation notification."""
    return f"""\
<div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;max-width:600px;margin:0 auto;color:#333;">
  <h2 style="color:#222;margin-bottom:4px;">{escape(store_name)}</h2>
  <p style="color:#666;margin-top:0;">Your support request has been escalated</p>
  <hr style="border:none;border-top:1px solid #e0e0e0;margin:16px 0;">
  <p>A member of our team will review your request and respond directly via email
  within <strong>{response_hours} hours</strong>.</p>
  <p style="color:#888;font-size:13px;">If you don't see a reply, please check your spam folder.</p>
  <h3 style="color:#444;font-size:14px;margin-bottom:8px;">Conversation transcript</h3>
  {transcript_html}
  <hr style="border:none;border-top:1px solid #e0e0e0;margin:16px 0;">
  <p style="color:#999;font-size:11px;">This email was sent by {escape(store_name)} via Agent Red Customer Experience.</p>
</div>"""


# ---------------------------------------------------------------------------
# Agent escalation email
# ---------------------------------------------------------------------------


def _build_agent_email_html(
    store_name: str,
    customer_email: str,
    transcript_html: str,
    reason: str,
    category: str,
    urgency: str,
    conversation_id: str,
) -> str:
    """Build HTML body for the agent escalation notification."""
    urgency_color = {"high": "#d32f2f", "medium": "#f57c00", "low": "#388e3c"}.get(
        urgency, "#666"
    )
    return f"""\
<div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;max-width:600px;margin:0 auto;color:#333;">
  <h2 style="color:#222;margin-bottom:4px;">Escalation — {escape(store_name)}</h2>
  <p style="color:#666;margin-top:0;">A customer conversation has been escalated to you.</p>
  <hr style="border:none;border-top:1px solid #e0e0e0;margin:16px 0;">

  <table style="font-size:13px;margin-bottom:16px;">
    <tr><td style="padding:2px 12px 2px 0;color:#888;">Customer</td>
        <td><strong>{escape(customer_email)}</strong></td></tr>
    <tr><td style="padding:2px 12px 2px 0;color:#888;">Category</td>
        <td>{escape(category)}</td></tr>
    <tr><td style="padding:2px 12px 2px 0;color:#888;">Urgency</td>
        <td style="color:{urgency_color};font-weight:600;">{escape(urgency)}</td></tr>
    <tr><td style="padding:2px 12px 2px 0;color:#888;">Reason</td>
        <td>{escape(reason)}</td></tr>
    <tr><td style="padding:2px 12px 2px 0;color:#888;">Conversation</td>
        <td style="font-family:monospace;font-size:12px;">{escape(conversation_id[:12])}…</td></tr>
  </table>

  <p><strong>Reply directly to this email</strong> to respond to the customer.</p>

  <h3 style="color:#444;font-size:14px;margin-bottom:8px;">Conversation transcript</h3>
  {transcript_html}

  <hr style="border:none;border-top:1px solid #e0e0e0;margin:16px 0;">
  <p style="color:#999;font-size:11px;">Agent Red Customer Experience — {escape(store_name)}</p>
</div>"""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def send_escalation_emails(
    *,
    tenant_id: str,
    conversation_id: str,
    customer_email: str,
    agent_email: str,
    messages: list[dict[str, Any]],
    store_name: str,
    reason: str,
    category: str,
    urgency: str,
    response_hours: int = 24,
) -> dict[str, str]:
    """Send escalation emails to both customer and agent.

    Returns dict with delivery status for each: {"customer": "...", "agent": "..."}.
    Failures are logged but do not raise — escalation should not fail because
    email delivery is down.
    """
    from src.multi_tenant.alert_delivery import SENDER_ADDRESS, send_acs_email

    conn_str = os.environ.get("ACS_CONNECTION_STRING", "")
    if not conn_str:
        logger.warning("ACS_CONNECTION_STRING not set — escalation emails skipped")
        return {"customer": "skipped", "agent": "skipped"}

    transcript_html = _format_transcript_html(messages)
    results: dict[str, str] = {}

    # --- Customer email ---
    try:
        customer_html = _build_customer_email_html(
            store_name=store_name,
            transcript_html=transcript_html,
            response_hours=response_hours,
        )
        status = await send_acs_email(
            conn_str=conn_str,
            to_email=customer_email,
            subject=f"{store_name} — Your support request has been escalated",
            html_body=customer_html,
        )
        results["customer"] = status
        logger.info(
            "Escalation email to customer: tenant=%s conv=%s to=%s status=%s",
            tenant_id, conversation_id[:8], customer_email, status,
        )
    except Exception:
        results["customer"] = "failed"
        logger.warning(
            "Failed to send customer escalation email: tenant=%s conv=%s",
            tenant_id, conversation_id[:8], exc_info=True,
        )

    # --- Agent email (with Reply-To: customer) ---
    try:
        agent_html = _build_agent_email_html(
            store_name=store_name,
            customer_email=customer_email,
            transcript_html=transcript_html,
            reason=reason,
            category=category,
            urgency=urgency,
            conversation_id=conversation_id,
        )
        # Use _send_acs_email_sync directly to add replyTo field
        from src.multi_tenant.alert_delivery import _send_acs_email_sync, SENDER_ADDRESS
        from azure.core.pipeline.policies import RetryPolicy
        from azure.communication.email import EmailClient

        retry_policy = RetryPolicy(
            retry_total=2, retry_backoff_factor=1, retry_backoff_max=5,
        )
        client = EmailClient.from_connection_string(conn_str, retry_policy=retry_policy)
        message = {
            "senderAddress": SENDER_ADDRESS,
            "recipients": {"to": [{"address": agent_email}]},
            "content": {
                "subject": f"[Escalation] [{category}] — Customer: {customer_email}",
                "html": agent_html,
            },
            "replyTo": [{"address": customer_email}],
        }

        def _send() -> str:
            poller = client.begin_send(message)
            result = poller.result(timeout=60)
            return getattr(result, "status", "unknown")

        status = await asyncio.to_thread(_send)
        results["agent"] = status
        logger.info(
            "Escalation email to agent: tenant=%s conv=%s to=%s reply_to=%s status=%s",
            tenant_id, conversation_id[:8], agent_email, customer_email, status,
        )
    except Exception:
        results["agent"] = "failed"
        logger.warning(
            "Failed to send agent escalation email: tenant=%s conv=%s",
            tenant_id, conversation_id[:8], exc_info=True,
        )

    return results
