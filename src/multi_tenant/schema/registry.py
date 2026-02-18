"""Schema registry -- YAML-driven field registry with lazy singleton.

Loads 78 field definitions from fields.yaml and provides accessor functions
for querying fields by step, tier, and prompt injection status.

R3 refactoring -- extracted from tenant_config_schema.py (session 39).
(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml

from src.multi_tenant.cosmos_schema import TenantTier, TIER_DEFAULTS
from src.multi_tenant.schema.models import (
    ConfigFieldDefinition,
    ConfigFieldType,
    OnboardingStep,
    SUPPORTED_LANGUAGES,
    TierGate,
    ValidationRule,
)

logger = logging.getLogger(__name__)

# Path to the YAML field definitions (sibling of this file)
_FIELDS_YAML_PATH = Path(__file__).parent / "fields.yaml"


# ---------------------------------------------------------------------------
# YAML loading
# ---------------------------------------------------------------------------


def _resolve_sentinel(value: Any) -> Any:
    """Replace $SUPPORTED_LANGUAGES sentinel with the actual list."""
    if isinstance(value, list):
        if len(value) == 1 and value[0] == "$SUPPORTED_LANGUAGES":
            return list(SUPPORTED_LANGUAGES)
        return [_resolve_sentinel(item) for item in value]
    return value


def _load_fields_from_yaml(
    path: Path | None = None,
) -> dict[str, ConfigFieldDefinition]:
    """Load field definitions from the YAML file and build the registry.

    Args:
        path: Optional override path for testing. Defaults to fields.yaml.

    Returns:
        Dict of field_name to ConfigFieldDefinition.
    """
    yaml_path = path or _FIELDS_YAML_PATH

    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    raw_fields = data.get("fields", [])
    registry: dict[str, ConfigFieldDefinition] = {}

    for raw in raw_fields:
        # Resolve sentinels in validation.allowed_values
        validation_data = raw.get("validation", {})
        if "allowed_values" in validation_data:
            validation_data["allowed_values"] = _resolve_sentinel(
                validation_data["allowed_values"]
            )

        validation = ValidationRule(**validation_data)

        field = ConfigFieldDefinition(
            field_name=raw["field_name"],
            display_name=raw["display_name"],
            field_type=ConfigFieldType(raw["field_type"]),
            validation=validation,
            platform_default=raw.get("platform_default"),
            tier_defaults=raw.get("tier_defaults", {}),
            tier_gate=TierGate(raw.get("tier_gate", "all")),
            onboarding_step=OnboardingStep(raw["onboarding_step"]),
            step_order=raw.get("step_order", 0),
            tooltip=raw.get("tooltip", ""),
            description=raw.get("description", ""),
            placeholder=raw.get("placeholder"),
            doc_link=raw.get("doc_link"),
            affects_agents=raw.get("affects_agents", []),
            pii_classification=raw.get("pii_classification", "none"),
            injected_in_prompt=raw.get("injected_in_prompt", False),
        )
        registry[field.field_name] = field

    return registry


# ---------------------------------------------------------------------------
# Registry singleton
# ---------------------------------------------------------------------------

_field_registry: dict[str, ConfigFieldDefinition] | None = None


def _build_field_registry() -> dict[str, ConfigFieldDefinition]:
    """Build the field registry from YAML. Called by get_field_registry()."""
    return _load_fields_from_yaml()


def get_field_registry() -> dict[str, ConfigFieldDefinition]:
    """Return the field registry singleton (lazy-built on first call)."""
    global _field_registry  # noqa: PLW0603
    if _field_registry is None:
        _field_registry = _build_field_registry()
        logger.info(
            "TenantConfigSchema: %d fields registered across %d onboarding steps",
            len(_field_registry),
            len(set(f.onboarding_step for f in _field_registry.values())),
        )
    return _field_registry


def reset_field_registry() -> None:
    """Reset the singleton for testing purposes."""
    global _field_registry  # noqa: PLW0603
    _field_registry = None


# ---------------------------------------------------------------------------
# Convenience accessors
# ---------------------------------------------------------------------------


def get_fields_by_step(step: OnboardingStep) -> list[ConfigFieldDefinition]:
    """Return all fields for a given onboarding step, sorted by step_order."""
    registry = get_field_registry()
    return sorted(
        [f for f in registry.values() if f.onboarding_step == step],
        key=lambda f: f.step_order,
    )


def get_fields_for_tier(tier: TenantTier) -> dict[str, ConfigFieldDefinition]:
    """Return all fields available at the given tier."""
    registry = get_field_registry()
    tier_rank = {
        TenantTier.STARTER: 0,
        TenantTier.PROFESSIONAL: 1,
        TenantTier.ENTERPRISE: 2,
    }
    gate_rank = {
        TierGate.ALL: 0,
        TierGate.PROFESSIONAL_PLUS: 1,
        TierGate.ENTERPRISE_ONLY: 2,
    }
    rank = tier_rank.get(tier, 0)
    return {
        name: field
        for name, field in registry.items()
        if gate_rank.get(field.tier_gate, 0) <= rank
    }


def get_prompt_injected_fields() -> list[ConfigFieldDefinition]:
    """Return fields that are injected into AI system prompts."""
    registry = get_field_registry()
    return [f for f in registry.values() if f.injected_in_prompt]


# ---------------------------------------------------------------------------
# Default resolution -- platform -> tier -> tenant override
# ---------------------------------------------------------------------------


def resolve_defaults(tier: TenantTier) -> dict[str, Any]:
    """Compute the fully resolved defaults for a given tier.

    Inheritance: platform_default -> tier_defaults[tier] -> (tenant override later).
    This returns the base layer before any tenant-specific overrides.

    Args:
        tier: The subscription tier to resolve defaults for.

    Returns:
        Dict of field_name to default value for every field available at this tier.
    """
    tier_fields = get_fields_for_tier(tier)
    result: dict[str, Any] = {}

    for name, field in tier_fields.items():
        # Tier-specific default takes priority over platform default
        if tier.value in field.tier_defaults:
            result[name] = field.tier_defaults[tier.value]
        else:
            result[name] = field.platform_default

    return result


# ---------------------------------------------------------------------------
# Schema export -- for API metadata responses
# ---------------------------------------------------------------------------


def export_schema_for_api(tier: TenantTier) -> dict[str, Any]:
    """Export the config schema as a JSON-serializable structure for API responses.

    Used by the Configuration API (#65) to return field metadata so that
    clients (including the Merchant UI) can render forms dynamically.

    Args:
        tier: The tenant's tier (filters fields by tier gate).

    Returns:
        Dict with steps, fields (tier-filtered), and defaults.
    """
    tier_fields = get_fields_for_tier(tier)
    defaults = resolve_defaults(tier)

    steps: list[dict[str, Any]] = []
    for step in OnboardingStep:
        step_fields = get_fields_by_step(step)
        # Filter to fields available at this tier
        available = [f for f in step_fields if f.field_name in tier_fields]
        if not available:
            continue

        steps.append({
            "step_number": step.value,
            "step_name": step.name.lower().replace("_", " ").title(),
            "fields": [
                {
                    "field_name": f.field_name,
                    "display_name": f.display_name,
                    "field_type": f.field_type.value,
                    "default": defaults.get(f.field_name),
                    "validation": {
                        k: v
                        for k, v in f.validation.model_dump().items()
                        if v is not None
                    },
                    "tooltip": f.tooltip,
                    "description": f.description,
                    "placeholder": f.placeholder,
                    "doc_link": f.doc_link,
                    "affects_agents": f.affects_agents,
                    "injected_in_prompt": f.injected_in_prompt,
                    "tier_gate": f.tier_gate.value,
                }
                for f in available
            ],
        })

    return {
        "tier": tier.value,
        "total_fields": len(tier_fields),
        "steps": steps,
    }
