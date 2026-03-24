"""
Conversation repository — conversations collection lifecycle and billing queries.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from src.multi_tenant.cosmos_schema import (
    COLLECTION_CONVERSATIONS,
    ConversationStatus,
)
from src.multi_tenant.repositories.base import TenantScopedRepository


class ConversationRepository(TenantScopedRepository):
    """Repository for the conversations collection.

    Supports conversation lifecycle management and billing queries
    needed by the ConversationMeter (Work Items #71-72).
    """

    # SPEC-1843 / WI-1627: Fields encrypted at rest with tenant DEK
    _encryption_fields = frozenset({
        "messages", "customer_intent", "escalation_reason", "transcript",
    })

    def __init__(self) -> None:
        super().__init__(COLLECTION_CONVERSATIONS)

    async def list_billable(
        self,
        tenant_id: str,
        since: str,
        until: str | None = None,
    ) -> list[dict[str, Any]]:
        """List billable conversations in a date range.

        Args:
            tenant_id: Tenant partition key.
            since: Start timestamp (ISO 8601, inclusive).
            until: End timestamp (ISO 8601, exclusive). None = now.
        """
        query_text = (
            "SELECT * FROM c "
            "WHERE c.is_billable = true "
            "AND c.started_at >= @since"
        )
        params: list[dict[str, Any]] = [
            {"name": "@since", "value": since},
        ]
        if until:
            query_text += " AND c.started_at < @until"
            params.append({"name": "@until", "value": until})

        query_text += " ORDER BY c.started_at DESC"

        return await self.query(tenant_id, query_text, params)

    async def count_billable(
        self, tenant_id: str, since: str, until: str | None = None,
    ) -> int:
        """Count billable conversations in a date range."""
        query_text = (
            "SELECT VALUE COUNT(1) FROM c "
            "WHERE c.is_billable = true "
            "AND c.started_at >= @since"
        )
        params: list[dict[str, Any]] = [
            {"name": "@since", "value": since},
        ]
        if until:
            query_text += " AND c.started_at < @until"
            params.append({"name": "@until", "value": until})

        return await self.query_count(tenant_id, query_text, params)

    async def list_by_customer(
        self,
        tenant_id: str,
        customer_id: str,
        max_items: int = 50,
    ) -> list[dict[str, Any]]:
        """List conversations for a specific customer, newest first."""
        return await self.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT * FROM c "
                "WHERE c.customer_id = @customer_id "
                "ORDER BY c.started_at DESC"
            ),
            parameters=[{"name": "@customer_id", "value": customer_id}],
            max_items=max_items,
        )

    async def find_active(
        self, tenant_id: str, customer_id: str,
    ) -> dict[str, Any] | None:
        """Find the active conversation for a customer (at most one)."""
        results = await self.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT * FROM c "
                "WHERE c.customer_id = @customer_id "
                "AND c.status = @status"
            ),
            parameters=[
                {"name": "@customer_id", "value": customer_id},
                {"name": "@status", "value": ConversationStatus.ACTIVE.value},
            ],
            max_items=1,
        )
        return results[0] if results else None

    async def append_message(
        self,
        tenant_id: str,
        conversation_id: str,
        message: dict[str, Any],
    ) -> dict[str, Any]:
        """Append a message to a conversation's transcript.

        Uses patch operations for atomic append without read-modify-write.
        """
        now = datetime.now(timezone.utc).isoformat()
        return await self.patch(
            tenant_id=tenant_id,
            document_id=conversation_id,
            operations=[
                {"op": "add", "path": "/messages/-", "value": message},
                {"op": "incr", "path": "/message_count", "value": 1},
                {"op": "set", "path": "/last_activity_at", "value": now},
            ],
        )

    async def end_conversation(
        self,
        tenant_id: str,
        conversation_id: str,
        status: ConversationStatus,
    ) -> dict[str, Any]:
        """Mark a conversation as ended."""
        now = datetime.now(timezone.utc).isoformat()
        return await self.patch(
            tenant_id=tenant_id,
            document_id=conversation_id,
            operations=[
                {"op": "set", "path": "/status", "value": status.value},
                {"op": "set", "path": "/ended_at", "value": now},
                {"op": "set", "path": "/last_activity_at", "value": now},
            ],
        )

    # --- Admin inbox queries (WI #171) ---

    async def list_filtered(
        self,
        tenant_id: str,
        *,
        status: ConversationStatus | None = None,
        customer_id: str | None = None,
        since: str | None = None,
        until: str | None = None,
        assigned_to: str | None = None,
        include_archived: bool = False,
        archived_only: bool = False,
        offset: int = 0,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """List conversations with optional filters for admin inbox.

        Args:
            tenant_id: Tenant partition key.
            status: Filter by conversation status (active, escalated, etc.).
            customer_id: Filter by customer identifier.
            since: Start timestamp (ISO 8601, inclusive).
            until: End timestamp (ISO 8601, exclusive).
            assigned_to: Filter by assigned human agent ID.
            include_archived: If True, include archived conversations.
            archived_only: If True, return only archived conversations.
            offset: Pagination offset.
            limit: Page size.
        """
        # SPEC-1607: always exclude zero-message conversations from inbox
        conditions: list[str] = ["c.message_count > 0"]
        params: list[dict[str, Any]] = []

        if status is not None:
            conditions.append("c.status = @status")
            params.append({"name": "@status", "value": status.value})

        if customer_id is not None:
            conditions.append("c.customer_id = @customer_id")
            params.append({"name": "@customer_id", "value": customer_id})

        if since is not None:
            conditions.append("c.started_at >= @since")
            params.append({"name": "@since", "value": since})

        if until is not None:
            conditions.append("c.started_at < @until")
            params.append({"name": "@until", "value": until})

        if assigned_to is not None:
            conditions.append("c.assigned_to = @assigned_to")
            params.append({"name": "@assigned_to", "value": assigned_to})

        # Archival filter: exclude archived by default
        if archived_only:
            conditions.append("IS_DEFINED(c.archived_at) AND c.archived_at != null")
        elif not include_archived:
            conditions.append("(NOT IS_DEFINED(c.archived_at) OR c.archived_at = null)")

        where_clause = " AND ".join(conditions)
        params.append({"name": "@offset", "value": offset})
        params.append({"name": "@limit", "value": limit})

        query_text = (
            f"SELECT * FROM c WHERE {where_clause} "
            "ORDER BY c.last_activity_at DESC "
            "OFFSET @offset LIMIT @limit"
        )

        return await self.query(tenant_id, query_text, params)

    async def count_filtered(
        self,
        tenant_id: str,
        *,
        status: ConversationStatus | None = None,
        customer_id: str | None = None,
        since: str | None = None,
        until: str | None = None,
        assigned_to: str | None = None,
        include_archived: bool = False,
        archived_only: bool = False,
    ) -> int:
        """Count conversations matching filters (for pagination metadata)."""
        # SPEC-1607: always exclude zero-message conversations from inbox
        conditions: list[str] = ["c.message_count > 0"]
        params: list[dict[str, Any]] = []

        if status is not None:
            conditions.append("c.status = @status")
            params.append({"name": "@status", "value": status.value})

        if customer_id is not None:
            conditions.append("c.customer_id = @customer_id")
            params.append({"name": "@customer_id", "value": customer_id})

        if since is not None:
            conditions.append("c.started_at >= @since")
            params.append({"name": "@since", "value": since})

        if until is not None:
            conditions.append("c.started_at < @until")
            params.append({"name": "@until", "value": until})

        if assigned_to is not None:
            conditions.append("c.assigned_to = @assigned_to")
            params.append({"name": "@assigned_to", "value": assigned_to})

        # Archival filter: exclude archived by default
        if archived_only:
            conditions.append("IS_DEFINED(c.archived_at) AND c.archived_at != null")
        elif not include_archived:
            conditions.append("(NOT IS_DEFINED(c.archived_at) OR c.archived_at = null)")

        where_clause = " AND ".join(conditions)
        query_text = f"SELECT VALUE COUNT(1) FROM c WHERE {where_clause}"

        return await self.query_count(tenant_id, query_text, params)

    async def assign_agent(
        self,
        tenant_id: str,
        conversation_id: str,
        agent_id: str,
    ) -> dict[str, Any]:
        """Assign a human agent to a conversation (post-escalation)."""
        now = datetime.now(timezone.utc).isoformat()
        return await self.patch(
            tenant_id=tenant_id,
            document_id=conversation_id,
            operations=[
                {"op": "set", "path": "/assigned_to", "value": agent_id},
                {"op": "set", "path": "/last_activity_at", "value": now},
            ],
        )

    async def add_internal_note(
        self,
        tenant_id: str,
        conversation_id: str,
        note: dict[str, Any],
    ) -> dict[str, Any]:
        """Append an internal merchant note to a conversation."""
        now = datetime.now(timezone.utc).isoformat()
        return await self.patch(
            tenant_id=tenant_id,
            document_id=conversation_id,
            operations=[
                {"op": "add", "path": "/internal_notes/-", "value": note},
                {"op": "set", "path": "/last_activity_at", "value": now},
            ],
        )

    # --- Analytics aggregation queries (WI #176-178) ---

    async def count_by_status(
        self,
        tenant_id: str,
        since: str,
        until: str | None = None,
        is_test_mode: bool | None = None,
        billable_only: bool = False,
    ) -> list[dict[str, Any]]:
        """Count conversations grouped by status in a date range.

        Args:
            tenant_id: Tenant partition key.
            since: Start timestamp (ISO 8601, inclusive).
            until: End timestamp (ISO 8601, exclusive).
            is_test_mode: Filter by test mode flag (None = all,
                True = test only, False = production only).
            billable_only: If True, only count billable conversations
                (SPEC-1593..1600 — dashboard excludes non-billable).

        Returns list of {status, count} dicts.
        """
        query_text = (
            "SELECT c.status, COUNT(1) AS count FROM c "
            "WHERE c.started_at >= @since"
        )
        params: list[dict[str, Any]] = [{"name": "@since", "value": since}]

        if until is not None:
            query_text += " AND c.started_at < @until"
            params.append({"name": "@until", "value": until})

        if is_test_mode is True:
            query_text += " AND c.is_test_mode = true"
        elif is_test_mode is False:
            query_text += " AND (NOT IS_DEFINED(c.is_test_mode) OR c.is_test_mode = false)"

        if billable_only:
            query_text += " AND c.is_billable = true"

        query_text += " GROUP BY c.status"

        return await self.query(tenant_id, query_text, params)

    async def aggregate_metrics(
        self,
        tenant_id: str,
        since: str,
        until: str | None = None,
        is_test_mode: bool | None = None,
        billable_only: bool = False,
    ) -> dict[str, Any]:
        """Compute aggregate conversation metrics for a date range.

        Args:
            tenant_id: Tenant partition key.
            since: Start timestamp (ISO 8601, inclusive).
            until: End timestamp (ISO 8601, exclusive).
            is_test_mode: Filter by test mode flag (None = all,
                True = test only, False = production only).
            billable_only: If True, only aggregate billable conversations
                (SPEC-1593..1600 — dashboard excludes non-billable).

        Returns a dict with total, billable, avg_turns, avg_messages,
        escalated, critic_passed, critic_failed counts.
        """
        query_text = (
            "SELECT "
            "COUNT(1) AS total, "
            "SUM(c.is_billable ? 1 : 0) AS billable, "
            "AVG(c.turn_count) AS avg_turns, "
            "AVG(c.message_count) AS avg_messages, "
            "SUM(c.status = 'escalated' ? 1 : 0) AS escalated, "
            "SUM(c.critic_passed = true ? 1 : 0) AS critic_passed, "
            "SUM(c.critic_passed = false ? 1 : 0) AS critic_failed "
            "FROM c WHERE c.started_at >= @since"
        )
        params: list[dict[str, Any]] = [{"name": "@since", "value": since}]

        if until is not None:
            query_text += " AND c.started_at < @until"
            params.append({"name": "@until", "value": until})

        if is_test_mode is True:
            query_text += " AND c.is_test_mode = true"
        elif is_test_mode is False:
            query_text += " AND (NOT IS_DEFINED(c.is_test_mode) OR c.is_test_mode = false)"

        if billable_only:
            query_text += " AND c.is_billable = true"

        results = await self.query(tenant_id, query_text, params)
        if results:
            return results[0]
        return {
            "total": 0, "billable": 0, "avg_turns": 0,
            "avg_messages": 0, "escalated": 0,
            "critic_passed": 0, "critic_failed": 0,
            "avg_response_time": 0, "customer_satisfaction": 0,
        }

    async def list_agents_invoked(
        self,
        tenant_id: str,
        since: str,
        until: str | None = None,
        is_test_mode: bool | None = None,
        billable_only: bool = False,
    ) -> list[dict[str, Any]]:
        """List all conversations with their agents_invoked for intent analysis.

        Args:
            tenant_id: Tenant partition key.
            since: Start timestamp (ISO 8601, inclusive).
            until: End timestamp (ISO 8601, exclusive).
            is_test_mode: Filter by test mode flag (None = all,
                True = test only, False = production only).
            billable_only: If True, only list billable conversations
                (SPEC-1598 — top topics excludes non-billable).

        Returns conversation docs with only the fields needed for
        agent/intent frequency analysis: conversation_id, agents_invoked,
        status, started_at.
        """
        query_text = (
            "SELECT c.tenant_id, c.conversation_id, c.agents_invoked, c.status, "
            "c.started_at FROM c "
            "WHERE c.started_at >= @since"
        )
        params: list[dict[str, Any]] = [{"name": "@since", "value": since}]

        if until is not None:
            query_text += " AND c.started_at < @until"
            params.append({"name": "@until", "value": until})

        if is_test_mode is True:
            query_text += " AND c.is_test_mode = true"
        elif is_test_mode is False:
            query_text += " AND (NOT IS_DEFINED(c.is_test_mode) OR c.is_test_mode = false)"

        if billable_only:
            query_text += " AND c.is_billable = true"

        return await self.query(tenant_id, query_text, params)

    async def list_gap_conversations(
        self,
        tenant_id: str,
        since: str,
        until: str | None = None,
        limit: int = 50,
        is_test_mode: bool | None = None,
        billable_only: bool = False,
    ) -> list[dict[str, Any]]:
        """List conversations that represent potential knowledge gaps.

        Args:
            tenant_id: Tenant partition key.
            since: Start timestamp (ISO 8601, inclusive).
            until: End timestamp (ISO 8601, exclusive).
            limit: Maximum number of results.
            is_test_mode: Filter by test mode flag (None = all,
                True = test only, False = production only).
            billable_only: If True, only list billable gap conversations
                (SPEC-1597 — escalation rate excludes non-billable).

        Returns conversations with escalated or error status — these
        indicate the AI couldn't resolve the customer's issue.
        """
        query_text = (
            "SELECT c.tenant_id, c.conversation_id, c.status, c.customer_id, "
            "c.turn_count, c.message_count, c.agents_invoked, "
            "c.critic_passed, c.started_at, c.ended_at "
            "FROM c "
            "WHERE (c.status = 'escalated' OR c.status = 'error') "
            "AND c.started_at >= @since"
        )
        params: list[dict[str, Any]] = [{"name": "@since", "value": since}]

        if until is not None:
            query_text += " AND c.started_at < @until"
            params.append({"name": "@until", "value": until})

        if is_test_mode is True:
            query_text += " AND c.is_test_mode = true"
        elif is_test_mode is False:
            query_text += " AND (NOT IS_DEFINED(c.is_test_mode) OR c.is_test_mode = false)"

        if billable_only:
            query_text += " AND c.is_billable = true"

        query_text += " ORDER BY c.started_at DESC"
        params.append({"name": "@limit", "value": limit})
        query_text += " OFFSET 0 LIMIT @limit"

        return await self.query(tenant_id, query_text, params)

    # --- Auto-archival (WI-A7) ---

    async def count_non_archived(self, tenant_id: str) -> int:
        """Count non-archived conversations for a tenant."""
        return await self.query_count(
            tenant_id,
            "SELECT VALUE COUNT(1) FROM c "
            "WHERE (NOT IS_DEFINED(c.archived_at) OR c.archived_at = null)",
            [],
        )

    async def list_oldest_archivable(
        self,
        tenant_id: str,
        *,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """List oldest resolved/timed-out non-archived conversations.

        Returns conversations eligible for auto-archival, ordered by
        last_activity_at ascending (oldest first).
        """
        return await self.query(
            tenant_id,
            "SELECT c.id, c.conversation_id, c.status, c.last_activity_at "
            "FROM c "
            "WHERE c.status IN ('resolved', 'timed_out') "
            "AND (NOT IS_DEFINED(c.archived_at) OR c.archived_at = null) "
            "ORDER BY c.last_activity_at ASC "
            "OFFSET 0 LIMIT @limit",
            [{"name": "@limit", "value": limit}],
        )

    # --- Layer 2 Memory Vectorization (WI #87) ---

    async def list_unvectorized_ended(
        self,
        tenant_id: str,
        *,
        limit: int = 50,
        min_messages: int = 2,
    ) -> list[dict[str, Any]]:
        """List ended conversations that haven't been vectorized yet.

        Returns conversations eligible for Layer 2 memory vectorization,
        ordered by ended_at ascending (oldest first).

        Filters:
            - Status: resolved, timed_out, or escalated (not active/error)
            - At least ``min_messages`` messages (skip empty/greeting-only)
            - Not yet vectorized (vectorized_at is null/undefined)
            - Has customer_id (anonymous conversations can't be linked)
        """
        return await self.query(
            tenant_id,
            "SELECT * FROM c "
            "WHERE c.status IN ('resolved', 'timed_out', 'escalated') "
            "AND c.message_count >= @min_messages "
            "AND (NOT IS_DEFINED(c.vectorized_at) OR c.vectorized_at = null) "
            "AND c.customer_id != null "
            "ORDER BY c.ended_at ASC "
            "OFFSET 0 LIMIT @limit",
            [
                {"name": "@min_messages", "value": min_messages},
                {"name": "@limit", "value": limit},
            ],
        )

    # --- First Contact Resolution (CQ-5) ---

    async def count_fcr(
        self,
        tenant_id: str,
        since: str,
        until: str | None = None,
        is_test_mode: bool | None = None,
        billable_only: bool = False,
    ) -> dict[str, Any]:
        """Count First Contact Resolution conversations.

        FCR proxy: resolved conversations where the same customer_id
        did not start another conversation within 72 hours of resolution.

        Uses a two-query approach for Cosmos DB compatibility (no self-joins):
        1. Fetch all resolved conversations in the date range.
        2. Fetch all conversations that started within the 72h follow-up
           window and group by customer_id.
        3. Compute FCR in Python by checking overlap.

        Args:
            tenant_id: Tenant partition key.
            since: Start timestamp (ISO 8601, inclusive).
            until: End timestamp (ISO 8601, exclusive). None = now.
            is_test_mode: Filter by test mode flag (None = all,
                True = test only, False = production only).
            billable_only: If True, only count billable resolved conversations
                (SPEC-1593 — resolution rate excludes non-billable).

        Returns:
            Dict with resolved_count, fcr_count, fcr_rate.
        """
        # Step 1: Get all resolved conversations in range
        resolved_query = (
            "SELECT c.conversation_id, c.customer_id, c.ended_at "
            "FROM c "
            "WHERE c.status = 'resolved' "
            "AND c.started_at >= @since"
        )
        resolved_params: list[dict[str, Any]] = [
            {"name": "@since", "value": since},
        ]

        if until is not None:
            resolved_query += " AND c.started_at < @until"
            resolved_params.append({"name": "@until", "value": until})

        if is_test_mode is True:
            resolved_query += " AND c.is_test_mode = true"
        elif is_test_mode is False:
            resolved_query += " AND (NOT IS_DEFINED(c.is_test_mode) OR c.is_test_mode = false)"

        if billable_only:
            resolved_query += " AND c.is_billable = true"

        resolved_conversations = await self.query(
            tenant_id, resolved_query, resolved_params,
        )

        resolved_count = len(resolved_conversations)
        if resolved_count == 0:
            return {"resolved_count": 0, "fcr_count": 0, "fcr_rate": 0.0}

        # Step 2: Determine the follow-up window — find the latest ended_at
        # among resolved conversations, then add 72 hours.
        customer_ids: set[str] = set()
        resolved_by_customer: dict[str, list[str]] = {}  # customer_id -> [ended_at, ...]
        for conv in resolved_conversations:
            cid = conv.get("customer_id")
            if cid:
                customer_ids.add(cid)
                resolved_by_customer.setdefault(cid, []).append(
                    conv.get("ended_at", "")
                )

        if not customer_ids:
            # All resolved conversations lack customer_id — treat as all FCR
            return {
                "resolved_count": resolved_count,
                "fcr_count": resolved_count,
                "fcr_rate": 1.0,
            }

        # Find the earliest resolution to set the follow-up window start,
        # and latest resolution + 72h for the window end.
        all_ended_ats = [
            ea
            for ends in resolved_by_customer.values()
            for ea in ends
            if ea
        ]
        if not all_ended_ats:
            # No ended_at timestamps — cannot determine follow-ups
            return {
                "resolved_count": resolved_count,
                "fcr_count": resolved_count,
                "fcr_rate": 1.0,
            }

        earliest_end = min(all_ended_ats)
        latest_end = max(all_ended_ats)

        # Parse latest_end and add 72 hours for the follow-up window
        try:
            latest_end_dt = datetime.fromisoformat(latest_end.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            latest_end_dt = datetime.now(timezone.utc)

        followup_window_end = (latest_end_dt + timedelta(hours=72)).isoformat()

        # Step 3: Query all conversations started by those customers
        # in the follow-up window (from earliest resolution onward).
        followup_query = (
            "SELECT c.conversation_id, c.customer_id, c.started_at "
            "FROM c "
            "WHERE c.started_at >= @window_start "
            "AND c.started_at <= @window_end"
        )
        followup_params: list[dict[str, Any]] = [
            {"name": "@window_start", "value": earliest_end},
            {"name": "@window_end", "value": followup_window_end},
        ]

        if is_test_mode is True:
            followup_query += " AND c.is_test_mode = true"
        elif is_test_mode is False:
            followup_query += " AND (NOT IS_DEFINED(c.is_test_mode) OR c.is_test_mode = false)"

        followup_conversations = await self.query(
            tenant_id, followup_query, followup_params,
        )

        # Build a map of customer_id -> list of follow-up started_at timestamps
        # (excluding the resolved conversations themselves)
        resolved_conv_ids = {
            conv.get("conversation_id") for conv in resolved_conversations
        }
        followups_by_customer: dict[str, list[str]] = {}
        for conv in followup_conversations:
            if conv.get("conversation_id") in resolved_conv_ids:
                continue  # Skip the resolved conversation itself
            cid = conv.get("customer_id")
            if cid and cid in customer_ids:
                followups_by_customer.setdefault(cid, []).append(
                    conv.get("started_at", "")
                )

        # Step 4: For each resolved conversation, check if the customer
        # had a follow-up within 72 hours of its ended_at.
        fcr_count = 0
        for conv in resolved_conversations:
            cid = conv.get("customer_id")
            ended_at = conv.get("ended_at", "")

            if not cid or not ended_at:
                # No customer_id or ended_at — count as FCR (conservative)
                fcr_count += 1
                continue

            # Parse the resolution time
            try:
                ended_dt = datetime.fromisoformat(ended_at.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                fcr_count += 1
                continue

            # 72-hour window: follow-up must start STRICTLY BEFORE
            # ended_at + 72 hours to count as a repeat (< not <=).
            cutoff = ended_dt + timedelta(hours=72)

            customer_followups = followups_by_customer.get(cid, [])
            has_followup = False
            for fu_started in customer_followups:
                if not fu_started:
                    continue
                try:
                    fu_dt = datetime.fromisoformat(fu_started.replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    continue
                # Follow-up must be AFTER resolution and STRICTLY BEFORE cutoff
                if fu_dt > ended_dt and fu_dt < cutoff:
                    has_followup = True
                    break

            if not has_followup:
                fcr_count += 1

        fcr_rate = (fcr_count / resolved_count) if resolved_count > 0 else 0.0

        return {
            "resolved_count": resolved_count,
            "fcr_count": fcr_count,
            "fcr_rate": round(fcr_rate, 4),
        }
