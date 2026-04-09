# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
Scheduled job: Widget canary health monitor (WI-3028).

Invoked by Azure Container App Job (cron: every 5 minutes).
Probes the production API gateway to verify the widget transport
path is functioning:

  1. GET /health — gateway alive
  2. GET /widget.js — widget bundle served
  3. POST /api/chat/conversations — conversation creation via widget key
  4. GET /api/chat/stream/{id} — SSE stream delivers events

On failure, sends an alert email via the existing SMTP infrastructure.
Exits with code 0 (all checks pass) or 1 (any check failed).

Usage:
    python -m src.jobs.run_widget_canary

Environment variables:
    CANARY_TARGET_URL: Production gateway URL (required)
    CANARY_WIDGET_KEY: Widget key for conversation test (required)
    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD: Email alert config
    CANARY_ALERT_EMAIL: Recipient for failure alerts (default: ADMIN_RESET_EMAIL)

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import os
import sys

import httpx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)


def check_health(client: httpx.Client) -> tuple[bool, str]:
    """Check GET /health returns 200."""
    try:
        r = client.get("/health", timeout=15)
        if r.status_code == 200:
            version = r.json().get("product_version", "?")
            return True, f"v{version}"
        return False, f"HTTP {r.status_code}"
    except Exception as e:
        return False, str(e)


def check_widget_js(client: httpx.Client) -> tuple[bool, str]:
    """Check GET /widget.js returns 200 with correct content-type."""
    try:
        r = client.get("/widget.js", timeout=15)
        if r.status_code != 200:
            return False, f"HTTP {r.status_code}"
        ct = r.headers.get("content-type", "")
        if "javascript" not in ct:
            return False, f"wrong content-type: {ct}"
        size = len(r.content)
        if size < 1000:
            return False, f"suspiciously small: {size} bytes"
        return True, f"{size} bytes"
    except Exception as e:
        return False, str(e)


def check_conversation(client: httpx.Client, widget_key: str) -> tuple[bool, str]:
    """Check POST /api/chat/conversations creates a conversation."""
    try:
        r = client.post(
            "/api/chat/conversations",
            headers={"X-Widget-Key": widget_key, "Content-Type": "application/json"},
            json={"message": "Canary health check - please ignore."},
            timeout=30,
        )
        if r.status_code not in (200, 201):
            return False, f"HTTP {r.status_code}: {r.text[:200]}"
        data = r.json()
        conv_id = data.get("conversationId") or data.get("conversation_id")
        if not conv_id:
            return False, f"no conversation_id: {list(data.keys())}"
        return True, conv_id
    except Exception as e:
        return False, str(e)


def check_sse_stream(client: httpx.Client, widget_key: str, conv_id: str) -> tuple[bool, str]:
    """Check GET /api/chat/stream/{id} delivers SSE events."""
    try:
        # Send a follow-up message to trigger a new turn
        msg_r = client.post(
            "/api/chat/message",
            headers={"X-Widget-Key": widget_key, "Content-Type": "application/json"},
            json={"conversation_id": conv_id, "content": "Canary stream test."},
            timeout=30,
        )
        if msg_r.status_code != 200:
            return False, f"message send failed: HTTP {msg_r.status_code}"

        events = []
        with client.stream(
            "GET",
            f"/api/chat/stream/{conv_id}",
            headers={"X-Widget-Key": widget_key, "Accept": "text/event-stream"},
            timeout=60,
        ) as stream:
            ct = stream.headers.get("content-type", "")
            if "text/event-stream" not in ct:
                return False, f"wrong content-type: {ct} (HTTP {stream.status_code})"
            for line in stream.iter_lines():
                if line.startswith("event:"):
                    events.append(line.split(":", 1)[1].strip())
                if events and events[-1] == "done":
                    break

        if "token" not in events:
            return False, f"no token events: {events}"
        if events[-1] != "done":
            return False, f"no done event: {events[-5:]}"
        return True, f"{len(events)} events"
    except Exception as e:
        return False, str(e)


def send_alert(subject: str, body: str) -> None:
    """Send failure alert via SMTP."""
    try:
        import smtplib
        from email.mime.text import MIMEText

        host = os.environ.get("SMTP_HOST", "")
        port = int(os.environ.get("SMTP_PORT", "465"))
        user = os.environ.get("SMTP_USER", "") or os.environ.get("SMTP_USERNAME", "")
        password = os.environ.get("SMTP_PASSWORD", "")
        sender = os.environ.get("SMTP_FROM", user)
        recipient = os.environ.get("CANARY_ALERT_EMAIL", "") or os.environ.get("ADMIN_RESET_EMAIL", "")

        if not all([host, user, password, recipient]):
            logger.warning("SMTP not configured - cannot send alert email")
            return

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = recipient

        with smtplib.SMTP_SSL(host, port) as smtp:
            smtp.login(user, password)
            smtp.send_message(msg)
        logger.info("Alert sent to %s", recipient)
    except Exception:
        logger.error("Failed to send alert email", exc_info=True)


def main() -> int:
    """Run all canary checks and return exit code."""
    target_url = os.environ.get("CANARY_TARGET_URL", "")
    widget_key = os.environ.get("CANARY_WIDGET_KEY", "")

    if not target_url:
        logger.error("CANARY_TARGET_URL not set")
        return 1
    if not widget_key:
        logger.error("CANARY_WIDGET_KEY not set")
        return 1

    client = httpx.Client(base_url=target_url, follow_redirects=True)
    failures: list[str] = []

    # Check 1: /health
    ok, detail = check_health(client)
    logger.info("health: %s (%s)", "PASS" if ok else "FAIL", detail)
    if not ok:
        failures.append(f"/health: {detail}")

    # Check 2: /widget.js
    ok, detail = check_widget_js(client)
    logger.info("widget.js: %s (%s)", "PASS" if ok else "FAIL", detail)
    if not ok:
        failures.append(f"/widget.js: {detail}")

    # Check 3: POST /api/chat/conversations
    ok, detail = check_conversation(client, widget_key)
    logger.info("conversation: %s (%s)", "PASS" if ok else "FAIL", detail)
    conv_id = detail if ok else None
    if not ok:
        failures.append(f"conversation: {detail}")

    # Check 4: SSE stream (only if conversation succeeded)
    if conv_id:
        ok, detail = check_sse_stream(client, widget_key, conv_id)
        logger.info("sse_stream: %s (%s)", "PASS" if ok else "FAIL", detail)
        if not ok:
            failures.append(f"sse_stream: {detail}")
    else:
        logger.warning("sse_stream: SKIP (no conversation)")
        failures.append("sse_stream: skipped (conversation failed)")

    client.close()

    if failures:
        logger.error("CANARY FAILED: %d checks failed", len(failures))
        alert_body = (
            f"Widget canary failed on {target_url}\n\n"
            + "\n".join(f"  - {f}" for f in failures)
            + "\n\nImmediate investigation required."
        )
        send_alert(
            f"[P0] Widget Canary FAILED - {len(failures)} checks",
            alert_body,
        )
        return 1

    logger.info("CANARY PASSED: all 4 checks OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
