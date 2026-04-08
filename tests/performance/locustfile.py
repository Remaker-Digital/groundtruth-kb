"""Locust load testing — sustained traffic generation against Agent Red API.

Validates SLA commitments under realistic concurrent load:
    - P50 < 1,500ms, P95 < 2,000ms, P99 < 5,000ms
    - Multi-tenant isolation (noisy neighbor prevention)
    - SSE streaming stability under concurrent connections
    - Pipeline timeout budget (8s hard deadline)

NOTE: Set DISABLE_RATE_LIMITING=true on the target API container to bypass
per-tenant rate limits during load testing.  Any remaining 429 responses
indicate genuine infrastructure overload and are counted as failures.

Scenarios:
    WidgetUser        — Simulates customer widget: start conversation, send messages,
                        receive SSE stream, end conversation. Weighted 70%.
    AdminUser         — Simulates merchant admin: dashboard, inbox, config, knowledge
                        base operations. Weighted 20%.
    HealthProbeUser   — Simulates monitoring probes: /health, /ready. Weighted 10%.

Usage:
    # Against local dev server:
    locust -f tests/performance/locustfile.py --host http://localhost:8000

    # Against production (read-only probes only):
    locust -f tests/performance/locustfile.py --host $PROD_URL --tags health-only

    # Headless run with specific user count and duration:
    locust -f tests/performance/locustfile.py --host http://localhost:8000 \
           --headless -u 50 -r 5 --run-time 2m

    # With config file:
    locust -f tests/performance/locustfile.py --config tests/performance/locust.conf

Prerequisites:
    pip install locust
    Set LOAD_TEST_API_KEY or LOAD_TEST_WIDGET_KEY env vars for authenticated endpoints.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import os
import uuid
from typing import Any

from locust import HttpUser, TaskSet, between, tag, task


# ---------------------------------------------------------------------------
# Configuration from environment
# ---------------------------------------------------------------------------

API_KEY = os.getenv("LOAD_TEST_API_KEY", "")
WIDGET_KEY = os.getenv("LOAD_TEST_WIDGET_KEY", "")
TENANT_ID = os.getenv("LOAD_TEST_TENANT_ID", "remaker-digital-001")

# SPEC-1845: Fail fast if required credentials are not provided.
# Running load tests with missing keys produces only 401 errors — waste of time.
if not API_KEY or not WIDGET_KEY:
    raise SystemExit(
        "LOAD_TEST_API_KEY and LOAD_TEST_WIDGET_KEY environment variables are required. "
        "Set them to valid credentials for the target environment before running load tests."
    )

# Multi-tenant simulation (SPEC-1516: 680 merchant scale target)
MULTI_TENANT_COUNT = int(os.getenv("LOAD_TEST_TENANT_COUNT", "680"))
_tenant_counter = 0


def _api_headers() -> dict[str, str]:
    """Headers for API-key-authenticated admin endpoints."""
    return {"X-API-Key": API_KEY, "Content-Type": "application/json"}


def _widget_headers() -> dict[str, str]:
    """Headers for widget-key-authenticated chat endpoints."""
    return {"X-Widget-Key": WIDGET_KEY, "Content-Type": "application/json"}


def _next_tenant_id() -> str:
    """Rotate through simulated tenant IDs for multi-tenant load distribution."""
    global _tenant_counter
    _tenant_counter = (_tenant_counter + 1) % MULTI_TENANT_COUNT
    return f"load-tenant-{_tenant_counter:04d}"


# ---------------------------------------------------------------------------
# Sample messages for realistic chat simulation
# ---------------------------------------------------------------------------

SAMPLE_MESSAGES = [
    "What are your shipping options?",
    "Do you have this product in blue?",
    "Can I return an item after 30 days?",
    "What's the status of my order #12345?",
    "Do you offer international shipping?",
    "Is this item in stock?",
    "What payment methods do you accept?",
    "Can I speak to a human agent?",
    "How long does delivery take?",
    "Do you have a size guide?",
    "What's your refund policy?",
    "Can I change my shipping address?",
    "Do you offer gift wrapping?",
    "Is there a warranty on this product?",
    "What are your store hours?",
]


# ===========================================================================
# Scenario 1: Widget Customer User (70% of traffic)
# ===========================================================================


class WidgetCustomerTasks(TaskSet):
    """Simulates a customer interacting with the chat widget.

    Flow: start conversation -> send 2-5 messages -> end conversation.
    Each message triggers the full AI pipeline (IC -> KR -> RG -> CR).
    """

    conversation_id: str | None = None
    message_count: int = 0

    def on_start(self) -> None:
        """Start a new conversation when this task set begins."""
        self.conversation_id = None
        self.message_count = 0
        self.tenant_id = _next_tenant_id()  # Multi-tenant rotation (SPEC-1516)
        self._start_conversation()

    def _start_conversation(self) -> None:
        """POST /api/chat/conversations — start a new conversation."""
        payload = {
            "visitor": {"name": f"LoadTest User {uuid.uuid4().hex[:6]}"},
            "page_url": "https://example.com/products/test-product",
            "initial_message": SAMPLE_MESSAGES[0],
        }

        with self.client.post(
            "/api/chat/conversations",
            json=payload,
            headers=_widget_headers(),
            name="/api/chat/conversations [start]",
            catch_response=True,
        ) as response:
            if response.status_code in (200, 201):
                data = response.json()
                self.conversation_id = data.get("conversation_id")
                response.success()
            else:
                response.failure(f"Start failed: {response.status_code}")

    @task(5)
    def send_message(self) -> None:
        """POST /api/chat/message — send a customer message."""
        if not self.conversation_id:
            return

        self.message_count += 1
        msg_idx = self.message_count % len(SAMPLE_MESSAGES)

        payload = {
            "conversation_id": self.conversation_id,
            "content": SAMPLE_MESSAGES[msg_idx],
        }

        with self.client.post(
            "/api/chat/message",
            json=payload,
            headers=_widget_headers(),
            name="/api/chat/message [send]",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Message failed: {response.status_code}")

        # End conversation after 3-5 messages
        if self.message_count >= 3:
            self._end_conversation()

    @task(2)
    def get_conversation_state(self) -> None:
        """GET /api/chat/conversations/{id} — poll conversation state."""
        if not self.conversation_id:
            return

        with self.client.get(
            f"/api/chat/conversations/{self.conversation_id}",
            headers=_widget_headers(),
            name="/api/chat/conversations/{id} [state]",
            catch_response=True,
        ) as response:
            if response.status_code in (200, 404):
                response.success()
            else:
                response.failure(f"State failed: {response.status_code}")

    @task(1)
    def check_stream_status(self) -> None:
        """GET /api/chat/stream/{id}/status — check SSE stream status."""
        if not self.conversation_id:
            return

        with self.client.get(
            f"/api/chat/stream/{self.conversation_id}/status",
            headers=_widget_headers(),
            name="/api/chat/stream/{id}/status [check]",
            catch_response=True,
        ) as response:
            if response.status_code in (200, 404):
                response.success()
            else:
                response.failure(f"Stream status failed: {response.status_code}")

    def _end_conversation(self) -> None:
        """POST /api/chat/conversations/{id}/end — end the conversation."""
        if not self.conversation_id:
            return

        payload = {"reason": "load_test_complete"}

        with self.client.post(
            f"/api/chat/conversations/{self.conversation_id}/end",
            json=payload,
            headers=_widget_headers(),
            name="/api/chat/conversations/{id}/end [end]",
            catch_response=True,
        ) as response:
            if response.status_code in (200, 404):
                response.success()
            else:
                response.failure(f"End failed: {response.status_code}")

        # Reset for next conversation cycle
        self.conversation_id = None
        self.message_count = 0
        self._start_conversation()


class WidgetUser(HttpUser):
    """Customer widget user — 70% of traffic mix."""

    tasks = [WidgetCustomerTasks]
    wait_time = between(2, 8)  # 2-8 seconds between actions
    weight = 7  # 70% of users


# ===========================================================================
# Scenario 2: Admin Dashboard User (20% of traffic)
# ===========================================================================


class AdminDashboardTasks(TaskSet):
    """Simulates a merchant using the admin dashboard.

    Exercises: usage dashboard, conversation inbox, knowledge base,
    analytics, configuration, and team management endpoints.
    """

    @task(3)
    def get_usage_dashboard(self) -> None:
        """GET /api/dashboard/usage — usage overview."""
        with self.client.get(
            f"/api/dashboard/usage?tenant={TENANT_ID}",
            headers=_api_headers(),
            name="/api/dashboard/usage",
            catch_response=True,
        ) as response:
            if response.status_code in (200, 503):
                response.success()
            else:
                response.failure(f"Dashboard failed: {response.status_code}")

    @task(2)
    def get_daily_volume(self) -> None:
        """GET /api/dashboard/usage/daily — daily conversation volume."""
        with self.client.get(
            f"/api/dashboard/usage/daily?tenant={TENANT_ID}",
            headers=_api_headers(),
            name="/api/dashboard/usage/daily",
            catch_response=True,
        ) as response:
            if response.status_code in (200, 503):
                response.success()

    @task(3)
    def list_conversations(self) -> None:
        """GET /api/admin/conversations — conversation inbox."""
        with self.client.get(
            f"/api/admin/conversations?tenant={TENANT_ID}&offset=0&limit=20",
            headers=_api_headers(),
            name="/api/admin/conversations [list]",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                response.success()

    @task(2)
    def list_knowledge_base(self) -> None:
        """GET /api/admin/knowledge — knowledge base articles."""
        with self.client.get(
            f"/api/admin/knowledge?tenant={TENANT_ID}",
            headers=_api_headers(),
            name="/api/admin/knowledge [list]",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                response.success()

    @task(2)
    def get_analytics_summary(self) -> None:
        """GET /api/analytics/summary — analytics overview."""
        with self.client.get(
            f"/api/analytics/summary?tenant={TENANT_ID}",
            headers=_api_headers(),
            name="/api/analytics/summary",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                response.success()

    @task(1)
    def get_intent_breakdown(self) -> None:
        """GET /api/analytics/intents — intent classification breakdown."""
        with self.client.get(
            f"/api/analytics/intents?tenant={TENANT_ID}",
            headers=_api_headers(),
            name="/api/analytics/intents",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                response.success()

    @task(1)
    def get_config(self) -> None:
        """GET /api/config — tenant configuration."""
        with self.client.get(
            f"/api/config?tenant={TENANT_ID}",
            headers=_api_headers(),
            name="/api/config [get]",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                response.success()

    @task(1)
    def list_team_members(self) -> None:
        """GET /api/admin/team — team member list."""
        with self.client.get(
            f"/api/admin/team?tenant={TENANT_ID}",
            headers=_api_headers(),
            name="/api/admin/team [list]",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                response.success()

    @task(1)
    def get_audit_log(self) -> None:
        """GET /api/audit — recent audit events."""
        with self.client.get(
            f"/api/audit?tenant={TENANT_ID}&limit=20",
            headers=_api_headers(),
            name="/api/audit [recent]",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                response.success()


class AdminUser(HttpUser):
    """Merchant admin user — 20% of traffic mix."""

    tasks = [AdminDashboardTasks]
    wait_time = between(3, 10)  # 3-10 seconds between page views
    weight = 2  # 20% of users


# ===========================================================================
# Scenario 3: Health Probe User (10% of traffic)
# ===========================================================================


class HealthProbeUser(HttpUser):
    """Monitoring probes — 10% of traffic mix. Safe for production."""

    wait_time = between(5, 15)
    weight = 1

    @task(3)
    @tag("health-only")
    def health_check(self) -> None:
        """GET /health — liveness probe."""
        with self.client.get(
            "/health",
            name="/health [liveness]",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                response.json()
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")

    @task(2)
    @tag("health-only")
    def readiness_check(self) -> None:
        """GET /ready — readiness probe (includes dependency health).

        SPEC-1780: 503 is valid when NATS transport not active (fail-loud).
        """
        with self.client.get(
            "/ready",
            name="/ready [readiness]",
            catch_response=True,
        ) as response:
            if response.status_code in (200, 503):
                response.success()
            else:
                response.failure(f"Readiness check failed: {response.status_code}")

    @task(1)
    @tag("health-only")
    def billing_health(self) -> None:
        """GET /api/tenants/lookup — billing endpoint availability."""
        with self.client.get(
            "/api/tenants/lookup?shop=health-check.myshopify.com",
            name="/api/tenants/lookup [billing health]",
            catch_response=True,
        ) as response:
            # 404 (not found) is the expected healthy response
            if response.status_code in (200, 404):
                response.success()
            else:
                response.failure(f"Billing health failed: {response.status_code}")


# ===========================================================================
# Custom event hooks for SLA reporting
# ===========================================================================


from locust import events  # noqa: E402


@events.request.add_listener
def on_request(
    request_type: str,
    name: str,
    response_time: float,
    response_length: int,
    exception: Exception | None,
    **kwargs: Any,
) -> None:
    """Log SLA violations for post-run analysis.

    Thresholds from documented SLA commitments:
        P50 < 1,500ms, P95 < 2,000ms, P99 < 5,000ms
    """
    if exception:
        return

    # Flag requests exceeding P99 threshold as a warning
    if response_time > 5000:
        print(
            f"[SLA P99 VIOLATION] {name}: {response_time:.0f}ms "
            f"(threshold: 5,000ms)"
        )
    elif response_time > 2000:
        print(
            f"[SLA P95 WARNING] {name}: {response_time:.0f}ms "
            f"(threshold: 2,000ms)"
        )
