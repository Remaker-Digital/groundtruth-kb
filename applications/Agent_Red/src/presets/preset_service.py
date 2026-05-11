# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Preset Service — G6 Vertical Template Starter Kits (SPEC-1878).

Loads vertical presets from YAML files and applies them to tenants
through existing config/QA/KB surfaces. Presets pre-fill configuration
draft, seed quick actions, create starter KB articles, and provision
agent overlays + skill bindings (v2 — WI-3025).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

_PRESETS_DIR = Path(__file__).parent

# Explicit allowlist of fields that can be saved via PUT /api/config.
# These are all in the config field registry and flow through the
# existing draft lifecycle (activation_service.save_draft).
CONFIG_SAVE_FIELDS: frozenset[str] = frozenset({
    "brand_voice",
    "formality_level",
    "response_length",
    "escalation_threshold",
    "escalation_keywords",
    "custom_instructions",
    "widget_greeting_message",
    "widget_input_placeholder",
})


class PresetSummary:
    """Preset metadata for list endpoints (no full content)."""

    __slots__ = ("id", "display_name", "description", "icon",
                 "quick_action_count", "article_count", "agents_recommended")

    def __init__(self, data: dict[str, Any]) -> None:
        self.id: str = data["id"]
        self.display_name: str = data["display_name"]
        self.description: str = data["description"]
        self.icon: str = data.get("icon", "")
        self.quick_action_count: int = len(data.get("quick_actions", []))
        self.article_count: int = len(data.get("knowledge_seed", []))
        self.agents_recommended: list[dict[str, str]] = data.get(
            "agents_recommended", [],
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "display_name": self.display_name,
            "description": self.description,
            "icon": self.icon,
            "quick_action_count": self.quick_action_count,
            "article_count": self.article_count,
            "agents_recommended": self.agents_recommended,
        }


class ApplyResult:
    """Result of applying a preset to a tenant."""

    __slots__ = ("draft_created", "quick_actions_created",
                 "assignments_created", "articles_created",
                 "agents_recommended", "agents_enabled", "agents_skipped")

    def __init__(
        self,
        *,
        draft_created: bool = False,
        quick_actions_created: int = 0,
        assignments_created: bool = False,
        articles_created: int = 0,
        agents_recommended: list[dict[str, str]] | None = None,
        agents_enabled: list[str] | None = None,
        agents_skipped: list[str] | None = None,
    ) -> None:
        self.draft_created = draft_created
        self.quick_actions_created = quick_actions_created
        self.assignments_created = assignments_created
        self.articles_created = articles_created
        self.agents_recommended = agents_recommended or []
        self.agents_enabled = agents_enabled or []
        self.agents_skipped = agents_skipped or []

    def to_dict(self) -> dict[str, Any]:
        return {
            "draft_created": self.draft_created,
            "quick_actions_created": self.quick_actions_created,
            "assignments_created": self.assignments_created,
            "articles_created": self.articles_created,
            "agents_recommended": self.agents_recommended,
            "agents_enabled": self.agents_enabled,
            "agents_skipped": self.agents_skipped,
        }


class PresetService:
    """Loads and applies vertical presets from YAML files.

    Presets are cached in memory after first load.
    """

    def __init__(self) -> None:
        self._cache: dict[str, dict[str, Any]] = {}
        self._loaded = False

    def _ensure_loaded(self) -> None:
        """Load all preset YAML files from the presets directory."""
        if self._loaded:
            return
        for path in _PRESETS_DIR.glob("*.yaml"):
            if path.name.startswith("_"):
                continue
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8"))
                if data and isinstance(data, dict) and "id" in data:
                    self._cache[data["id"]] = data
            except Exception:
                logger.warning("Failed to load preset %s", path.name, exc_info=True)
        self._loaded = True
        logger.info("Loaded %d presets", len(self._cache))

    def list_presets(self) -> list[PresetSummary]:
        """Return metadata for all available presets."""
        self._ensure_loaded()
        return [PresetSummary(d) for d in self._cache.values()]

    def get_preset(self, preset_id: str) -> dict[str, Any] | None:
        """Load a full preset by ID."""
        self._ensure_loaded()
        return self._cache.get(preset_id)

    async def apply_preset(
        self,
        tenant_id: str,
        preset_id: str,
        *,
        tier: str = "starter",
        actor: str = "preset_service",
    ) -> ApplyResult:
        """Apply a preset to a tenant through existing write surfaces.

        1. Config-save fields → activation_service.save_draft()
        2. Quick-action prompts → repository quick-action upsert
        3. Quick-action assignments → repository assignment upsert
        4. KB articles → direct creation (additive, no dedupe in v1)
        """
        preset = self.get_preset(preset_id)
        if preset is None:
            raise ValueError(f"Preset not found: {preset_id}")

        result = ApplyResult(
            agents_recommended=preset.get("agents_recommended", []),
        )

        # Step 1: Config-save fields → existing draft surface
        config_fields = self._extract_config_fields(preset)
        if config_fields:
            await self._save_config_draft(tenant_id, tier, config_fields, actor)
            result.draft_created = True

        # Step 2: Quick-action prompts → existing QA surface (draft-first)
        created_action_ids = await self._create_quick_actions(
            tenant_id, preset.get("quick_actions", []), tier, actor,
        )
        result.quick_actions_created = len(created_action_ids)

        # Step 3: Quick-action assignments → slot first 2 actions on all pages
        if created_action_ids:
            await self._create_assignments(tenant_id, created_action_ids, tier, actor)
            result.assignments_created = True

        # Step 4: KB articles → direct creation (additive)
        articles_created = await self._seed_kb_articles(
            tenant_id, preset.get("knowledge_seed", []), preset_id,
        )
        result.articles_created = articles_created

        # Step 5: Agent overlays + bindings (v2 — WI-3025)
        # Create-if-absent: only provision agents that don't have existing overlays.
        enabled, skipped = await self._provision_agents(
            tenant_id, preset.get("agents_recommended", []), tier,
        )
        result.agents_enabled = enabled
        result.agents_skipped = skipped

        logger.info(
            "Applied preset '%s' to tenant %s: draft=%s, qa=%d, kb=%d, agents=%d (skipped=%d)",
            preset_id, tenant_id[:8], result.draft_created,
            result.quick_actions_created, result.articles_created,
            len(enabled), len(skipped),
        )
        return result

    @staticmethod
    def _extract_config_fields(preset: dict[str, Any]) -> dict[str, Any]:
        """Extract config-save fields from preset, including widget overrides."""
        fields: dict[str, Any] = {}

        # Preferences section
        for key, value in preset.get("preferences", {}).items():
            if key in CONFIG_SAVE_FIELDS:
                fields[key] = value

        # Widget section → mapped to config field names
        widget = preset.get("widget", {})
        if "greeting_message" in widget:
            fields["widget_greeting_message"] = widget["greeting_message"]
        if "input_placeholder" in widget:
            fields["widget_input_placeholder"] = widget["input_placeholder"]

        return fields

    @staticmethod
    async def _save_config_draft(
        tenant_id: str,
        tier: str,
        fields: dict[str, Any],
        actor: str,
    ) -> None:
        """Save config fields to draft via activation_service."""
        from src.multi_tenant.activation_service import get_activation_service
        from src.multi_tenant.cosmos_schema import TenantTier

        svc = get_activation_service()
        tenant_tier = TenantTier(tier) if tier else TenantTier.STARTER
        await svc.save_draft(
            tenant_id=tenant_id,
            tier=tenant_tier,
            changes=fields,
            actor=actor,
        )

    @staticmethod
    async def _create_quick_actions(
        tenant_id: str,
        quick_actions: list[dict[str, Any]],
        tier: str,
        actor: str,
    ) -> list[str]:
        """Create quick-action prompts via repository."""
        if not quick_actions:
            return []

        from src.multi_tenant.activation_service import get_activation_service
        from src.multi_tenant.cosmos_schema import TenantTier

        # Ensure draft exists before QA writes (same pattern as admin_quick_action_api)
        svc = get_activation_service()
        tenant_tier = TenantTier(tier) if tier else TenantTier.STARTER
        await svc.ensure_draft_for_signal(
            tenant_id=tenant_id,
            tier=tenant_tier,
            signal_field="qa_modified_at",
            actor=actor,
        )

        from src.multi_tenant.admin_quick_action_api import _get_repo

        repo = _get_repo()
        now = datetime.now(UTC).isoformat()
        created_ids: list[str] = []

        for qa in quick_actions:
            action_id = str(uuid.uuid4())
            action_dict = {
                "id": action_id,
                "label": qa.get("label", ""),
                "prompt_template": qa.get("message", ""),
                "icon": qa.get("icon", ""),
                "is_active": True,
                "sort_order": len(created_ids) * 10,
                "created_at": now,
                "updated_at": now,
            }
            await repo.upsert_quick_action(tenant_id, action_dict)
            created_ids.append(action_id)

        return created_ids

    @staticmethod
    async def _create_assignments(
        tenant_id: str,
        action_ids: list[str],
        tier: str,
        actor: str,
    ) -> None:
        """Assign first 2 quick actions to all pages."""
        from src.multi_tenant.admin_quick_action_api import _get_repo

        repo = _get_repo()
        assignment: dict[str, Any] = {
            "page_type": "all",
            "page_handle": None,
            "auto_open": False,
            "auto_open_delay_ms": 3000,
        }
        if len(action_ids) >= 1:
            assignment["slot_1_action_id"] = action_ids[0]
        if len(action_ids) >= 2:
            assignment["slot_2_action_id"] = action_ids[1]

        await repo.upsert_page_assignment(tenant_id, assignment)

    @staticmethod
    async def _seed_kb_articles(
        tenant_id: str,
        articles: list[dict[str, Any]],
        preset_id: str,
    ) -> int:
        """Seed KB articles from preset (additive, no dedupe in v1)."""
        if not articles:
            return 0

        from src.multi_tenant.cosmos_schema import KnowledgeBaseDocument
        from src.multi_tenant.repositories.knowledge import KnowledgeBaseRepository

        repo = KnowledgeBaseRepository()
        now = datetime.now(UTC).isoformat()
        created = 0

        for article in articles:
            try:
                entry_id = str(uuid.uuid4())
                doc = KnowledgeBaseDocument(
                    id=entry_id,
                    tenant_id=tenant_id,
                    entry_type="article",
                    title=article.get("title", ""),
                    content=article.get("content", ""),
                    metadata={
                        "preset_source": preset_id,
                    },
                    tags=[],
                    language="en",
                    category=article.get("category", "general"),
                    status="published",
                    is_active=True,
                    source_type="preset",
                    created_at=now,
                    updated_at=now,
                )
                await repo.create(tenant_id, doc)
                created += 1
            except Exception:
                logger.warning(
                    "Failed to create preset KB article: %s",
                    article.get("title", "unknown")[:50],
                    exc_info=True,
                )

        return created


    @staticmethod
    async def _provision_agents(
        tenant_id: str,
        agents_recommended: list[dict[str, Any]],
        tier: str,
    ) -> tuple[list[str], list[str]]:
        """Provision agent overlays + skill bindings for recommended agents.

        Create-if-absent: only creates overlays/bindings that don't already
        exist, so re-applying a preset never overwrites admin customizations.
        Binding mode comes from the registry skill definition, not hardcoded.
        Tier gating uses the registry tier_gate (authoritative), not the
        preset YAML tier_required (advisory display-only).

        Returns (agents_enabled, agents_skipped).
        """
        if not agents_recommended:
            return [], []

        from src.agents.plugins.bindings import SkillBindingService
        from src.agents.plugins.overlay import clear_resolution_cache
        from src.agents.plugins.registry import PluginAgentRegistry
        from src.multi_tenant.repositories.agent_bindings import (
            AgentSkillBindingRepository,
        )
        from src.multi_tenant.repositories.agent_overlays import (
            TenantAgentOverlayRepository,
        )

        registry = PluginAgentRegistry.get_instance()
        overlay_repo = TenantAgentOverlayRepository()
        binding_repo = AgentSkillBindingRepository()

        tier_order = {"free": 0, "starter": 1, "professional": 2, "enterprise": 3}
        tenant_tier_level = tier_order.get(tier.lower(), 0)

        enabled: list[str] = []
        skipped: list[str] = []
        wrote_any = False

        for rec in agents_recommended:
            agent_id = rec.get("agent_id", "")
            if not agent_id:
                continue

            # Look up agent in registry for authoritative tier_gate and skills
            agent_def = registry.get(agent_id)
            if agent_def is None:
                logger.warning(
                    "Preset agent %r not found in registry, skipping", agent_id,
                )
                continue

            # Tier gate from registry (authoritative source)
            required_level = tier_order.get(agent_def.tier_gate.lower(), 0)
            if tenant_tier_level < required_level:
                logger.info(
                    "Preset agent %s tier-gated: tenant=%s, required=%s",
                    agent_id, tier, agent_def.tier_gate,
                )
                skipped.append(agent_id)
                continue

            # Create-if-absent: check for existing overlay before creating
            existing_overlay = await overlay_repo.get_overlay(tenant_id, agent_id)
            if existing_overlay is not None:
                logger.info(
                    "Preset agent %s already has overlay for tenant %s, skipping",
                    agent_id, tenant_id[:8],
                )
                skipped.append(agent_id)
                continue

            # Create overlay (enabled=True, no customizations)
            await overlay_repo.upsert_overlay(
                tenant_id, agent_id, enabled=True,
            )
            wrote_any = True

            # Create bindings for each skill (create-if-absent, registry mode)
            for skill_def in agent_def.skills:
                existing_binding = await binding_repo.get_binding(
                    tenant_id, skill_def.skill_id,
                )
                if existing_binding is not None:
                    continue
                await binding_repo.upsert_binding(
                    tenant_id,
                    agent_id,
                    skill_def.skill_id,
                    mode=skill_def.mode,  # from registry, not hardcoded
                    enabled=True,
                )

            enabled.append(agent_id)

        # Invalidate caches if any writes occurred (same pattern as admin API)
        if wrote_any:
            clear_resolution_cache()
            svc = SkillBindingService.get_instance()
            svc.invalidate(tenant_id)

        return enabled, skipped


# ---------------------------------------------------------------------------
# Singleton access
# ---------------------------------------------------------------------------

_preset_service: PresetService | None = None


def get_preset_service() -> PresetService:
    """Get or create the singleton PresetService."""
    global _preset_service  # noqa: PLW0603
    if _preset_service is None:
        _preset_service = PresetService()
    return _preset_service
