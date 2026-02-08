"""
TestModeService — Controlled rollout engine for AI configuration testing (C2).

Routes X% of visitor sessions to a test AI configuration while the
remaining sessions use Production config. Uses deterministic SHA-256
assignment (same pattern as fine_tuning_pipeline.py ABExperimentConfig)
so a given session always gets the same variant.

Lifecycle:
    activate(overrides, percentage)  → enable test mode
    deactivate(action="rollout"|"abandon")
      - rollout: merge test overrides into production config
      - abandon: discard test overrides
    should_use_test_config(session_id)  → bool
    get_test_overrides()  → dict of field deltas

Architecture:
    - Stored on PreferencesDocument (test_mode_* fields)
    - Pipeline reads TestModeService at message-handling time
    - ConversationDocument tagged with is_test_mode=True for analytics
    - Only AI behavior fields are overridable (not widget, integrations, etc.)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import logging
import random
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# AI behaviour fields eligible for test-mode overrides.
# Widget appearance, integrations, and infrastructure fields are excluded.
# ---------------------------------------------------------------------------
_AI_BEHAVIOR_FIELDS: frozenset[str] = frozenset({
    # Brand & tone
    "brand_voice",
    # Response style
    "response_length",
    "formality_level",
    # Escalation rules
    "escalation_threshold",
    "escalation_keywords",
    # Custom instructions
    "custom_instructions",
    # Memory
    "memory_enabled",
    # Retrieval tuning
    "retrieval_top_k",
    "retrieval_vector_weight",
    "retrieval_bm25_weight",
    "retrieval_min_score",
    # Intent routing
    "intent_source_mapping",
    # Citation
    "cite_sources_in_response",
})


class TestModeService:
    """Manages test mode lifecycle: activate, route, rollout/abandon."""

    def __init__(self) -> None:
        self._processor: Any = None
        self._repo: Any = None

    def configure(
        self,
        processor: Any = None,
        repo: Any = None,
    ) -> None:
        """Wire dependencies (called at startup)."""
        self._processor = processor
        self._repo = repo

    # ------------------------------------------------------------------
    # Session assignment (deterministic, same pattern as A/B experiments)
    # ------------------------------------------------------------------

    @staticmethod
    def should_use_test_config(
        session_id: str,
        seed: int,
        percentage: int,
    ) -> bool:
        """Deterministic assignment: returns True if session is in test group.

        Uses SHA-256 hash of ``seed:session_id`` mod 100.  Same session_id +
        seed always produces the same result.
        """
        if percentage <= 0:
            return False
        if percentage >= 100:
            return True
        digest = hashlib.sha256(f"{seed}:{session_id}".encode()).hexdigest()
        bucket = int(digest[:8], 16) % 100
        return bucket < percentage

    # ------------------------------------------------------------------
    # Status helpers
    # ------------------------------------------------------------------

    async def get_status(self, tenant_id: str) -> dict[str, Any]:
        """Return the current test mode state for a tenant."""
        if self._repo is None:
            return {"enabled": False}

        doc = await self._repo.get_current(tenant_id)
        if doc is None:
            return {"enabled": False}

        return {
            "enabled": doc.get("test_mode_enabled", False),
            "percentage": doc.get("test_mode_percentage", 10),
            "overrides": doc.get("test_mode_overrides", {}),
            "assignment_seed": doc.get("test_mode_assignment_seed", 0),
            "activated_at": doc.get("test_mode_activated_at"),
            "override_field_count": len(doc.get("test_mode_overrides", {})),
        }

    # ------------------------------------------------------------------
    # Activate
    # ------------------------------------------------------------------

    async def activate(
        self,
        tenant_id: str,
        tier: str,
        overrides: dict[str, Any],
        percentage: int = 10,
        actor: str = "admin",
    ) -> dict[str, Any]:
        """Activate Test Mode with AI-behaviour field overrides.

        Args:
            tenant_id: tenant partition key
            tier: tenant tier (for config processor)
            overrides: dict of AI-behaviour field deltas
            percentage: session routing percentage (1-50)
            actor: who activated (for audit)

        Returns:
            Status dict with ``success`` flag.
        """
        # Validate percentage
        percentage = max(1, min(50, percentage))

        # Filter to only AI behaviour fields
        valid_overrides: dict[str, Any] = {
            k: v for k, v in overrides.items() if k in _AI_BEHAVIOR_FIELDS
        }
        rejected = set(overrides.keys()) - set(valid_overrides.keys())
        if rejected:
            logger.warning(
                "Test mode: rejected non-AI-behaviour override fields: %s",
                rejected,
            )

        if not valid_overrides:
            return {
                "success": False,
                "error": "No valid AI behaviour overrides provided. "
                         "Only AI behaviour fields can be overridden in Test Mode.",
                "allowed_fields": sorted(_AI_BEHAVIOR_FIELDS),
            }

        # Generate assignment seed
        seed = random.randint(100_000, 999_999)

        # Update via processor
        if self._processor is not None:
            update_fields = {
                "test_mode_enabled": True,
                "test_mode_percentage": percentage,
                "test_mode_overrides": valid_overrides,
                "test_mode_assignment_seed": seed,
                "test_mode_activated_at": datetime.now(timezone.utc).isoformat(),
            }
            await self._processor.update_config(
                tenant_id=tenant_id,
                tier=tier,
                updates=update_fields,
                actor=actor,
            )

        logger.info(
            "Test Mode activated for tenant=%s percentage=%d overrides=%d seed=%d",
            tenant_id, percentage, len(valid_overrides), seed,
        )

        return {
            "success": True,
            "percentage": percentage,
            "override_count": len(valid_overrides),
            "rejected_fields": sorted(rejected) if rejected else [],
            "seed": seed,
        }

    # ------------------------------------------------------------------
    # Deactivate (rollout or abandon)
    # ------------------------------------------------------------------

    async def deactivate(
        self,
        tenant_id: str,
        tier: str,
        action: str = "abandon",
        actor: str = "admin",
    ) -> dict[str, Any]:
        """Deactivate Test Mode.

        Args:
            action: "rollout" merges test overrides into Production config.
                    "abandon" discards them.
        """
        if self._repo is None:
            return {"success": False, "error": "Repository not configured"}

        doc = await self._repo.get_current(tenant_id)
        if doc is None:
            return {"success": False, "error": "No config found"}

        if not doc.get("test_mode_enabled", False):
            return {"success": False, "error": "Test Mode is not active"}

        overrides = doc.get("test_mode_overrides", {})

        if action == "rollout" and overrides and self._processor is not None:
            # Merge test overrides into production config
            await self._processor.update_config(
                tenant_id=tenant_id,
                tier=tier,
                updates={
                    **overrides,
                    "test_mode_enabled": False,
                    "test_mode_overrides": {},
                    "test_mode_activated_at": None,
                },
                actor=actor,
            )
            logger.info(
                "Test Mode rolled out for tenant=%s — %d fields merged into production",
                tenant_id, len(overrides),
            )
            return {
                "success": True,
                "action": "rollout",
                "merged_fields": sorted(overrides.keys()),
            }
        else:
            # Abandon: discard test overrides
            if self._processor is not None:
                await self._processor.update_config(
                    tenant_id=tenant_id,
                    tier=tier,
                    updates={
                        "test_mode_enabled": False,
                        "test_mode_overrides": {},
                        "test_mode_activated_at": None,
                    },
                    actor=actor,
                )
            logger.info(
                "Test Mode abandoned for tenant=%s — %d overrides discarded",
                tenant_id, len(overrides),
            )
            return {
                "success": True,
                "action": "abandon",
                "discarded_fields": sorted(overrides.keys()),
            }

    # ------------------------------------------------------------------
    # Update percentage
    # ------------------------------------------------------------------

    async def update_percentage(
        self,
        tenant_id: str,
        tier: str,
        percentage: int,
        actor: str = "admin",
    ) -> dict[str, Any]:
        """Change the test routing percentage while test mode is active."""
        percentage = max(1, min(50, percentage))

        if self._processor is not None:
            await self._processor.update_config(
                tenant_id=tenant_id,
                tier=tier,
                updates={"test_mode_percentage": percentage},
                actor=actor,
            )

        logger.info(
            "Test Mode percentage updated for tenant=%s to %d%%",
            tenant_id, percentage,
        )
        return {"success": True, "percentage": percentage}

    # ------------------------------------------------------------------
    # Resolve test config overrides for pipeline
    # ------------------------------------------------------------------

    def apply_test_overrides(
        self,
        config: dict[str, Any],
        overrides: dict[str, Any],
    ) -> dict[str, Any]:
        """Return a new config dict with test overrides applied.

        Does NOT mutate the original config.
        """
        merged = dict(config)
        for key, value in overrides.items():
            if key in _AI_BEHAVIOR_FIELDS:
                merged[key] = value
        return merged


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_service: TestModeService | None = None


def get_test_mode_service() -> TestModeService:
    """Return the module-level TestModeService singleton."""
    global _service
    if _service is None:
        _service = TestModeService()
    return _service
