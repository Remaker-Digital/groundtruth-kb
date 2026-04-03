"""Schema validation -- field-level and config-level validation functions.

R3 refactoring -- extracted from tenant_config_schema.py (session 39).
(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import re
from typing import Any

from src.multi_tenant.cosmos_schema import TenantTier
from src.multi_tenant.schema.models import (
    ConfigFieldType,
    ConfigValidationResult,
    TierGate,
    ValidationRule,
)


# ---------------------------------------------------------------------------
# Tier ranking helpers (shared between validate_field and validate_config)
# ---------------------------------------------------------------------------

_TIER_RANK = {
    TenantTier.STARTER: 0,
    TenantTier.PROFESSIONAL: 1,
    TenantTier.ENTERPRISE: 2,
}

_GATE_RANK = {
    TierGate.ALL: 0,
    TierGate.PROFESSIONAL_PLUS: 1,
    TierGate.PROFESSIONAL: 1,       # YAML alias — same rank as pro+
    TierGate.ENTERPRISE_ONLY: 2,
}


# ---------------------------------------------------------------------------
# Field-level validation
# ---------------------------------------------------------------------------


def validate_field(
    field_name: str,
    value: Any,
    tier: TenantTier,
) -> tuple[bool, str | None, Any]:
    """Validate a single config field value.

    Args:
        field_name: The field to validate.
        value: The proposed value.
        tier: The tenant's tier (for tier gating and tier-specific rules).

    Returns:
        Tuple of (is_valid, error_message_or_none, sanitized_value).
    """
    from src.multi_tenant.schema.registry import get_field_registry

    registry = get_field_registry()

    if field_name not in registry:
        return False, f"Unknown configuration field: {field_name}", None

    field = registry[field_name]

    # Tier gate check
    if _GATE_RANK.get(field.tier_gate, 0) > _TIER_RANK.get(tier, 0):
        return (
            False,
            f"Field '{field_name}' requires {field.tier_gate.value} tier or higher",
            None,
        )

    rules = field.validation

    # Null / None handling
    if value is None:
        if rules.required:
            return False, f"Field '{field_name}' is required", None
        return True, None, None

    # Type-specific validation
    if field.field_type == ConfigFieldType.STRING:
        return _validate_string(field_name, value, rules)

    if field.field_type == ConfigFieldType.TEXT:
        return _validate_string(field_name, value, rules)

    if field.field_type == ConfigFieldType.INTEGER:
        return _validate_integer(field_name, value, rules)

    if field.field_type == ConfigFieldType.FLOAT:
        return _validate_float(field_name, value, rules)

    if field.field_type == ConfigFieldType.BOOLEAN:
        return _validate_boolean(field_name, value)

    if field.field_type in (ConfigFieldType.ENUM, ConfigFieldType.SELECT):
        return _validate_enum(field_name, value, rules)

    if field.field_type == ConfigFieldType.STRING_LIST:
        return _validate_string_list(field_name, value, rules)

    if field.field_type == ConfigFieldType.OBJECT:
        # Object fields are passed through with basic type check
        if not isinstance(value, dict):
            return False, f"Field '{field_name}' must be a JSON object", None
        return True, None, value

    return False, f"Unsupported field type: {field.field_type}", None


# ---------------------------------------------------------------------------
# Config-level validation
# ---------------------------------------------------------------------------


def validate_config(
    config: dict[str, Any],
    tier: TenantTier,
) -> ConfigValidationResult:
    """Validate an entire tenant config payload.

    Validates each provided field, checks tier gating, enforces required
    fields, and returns a comprehensive result with sanitized values.

    Args:
        config: Dict of field_name to value to validate.
        tier: The tenant's subscription tier.

    Returns:
        ConfigValidationResult with validation outcomes.
    """
    from src.multi_tenant.schema.registry import get_field_registry, get_fields_for_tier

    result = ConfigValidationResult(valid=True)
    registry = get_field_registry()
    tier_fields = get_fields_for_tier(tier)

    for field_name, value in config.items():
        if field_name not in registry:
            result.warnings.append({
                "field_name": field_name,
                "message": f"Unknown field '{field_name}' -- ignored",
            })
            continue

        is_valid, error, sanitized = validate_field(field_name, value, tier)

        if not is_valid:
            result.valid = False
            result.errors.append({
                "field_name": field_name,
                "message": error or "Validation failed",
            })
        elif field_name not in tier_fields:
            result.warnings.append({
                "field_name": field_name,
                "message": (
                    f"Field '{field_name}' is not available at "
                    f"{tier.value} tier -- ignored"
                ),
            })
        else:
            result.sanitized[field_name] = sanitized

    # Check required fields that are missing from the payload
    for field_name, field in tier_fields.items():
        if field.validation.required and field_name not in config:
            # Only error if there's no platform/tier default
            default = (
                field.tier_defaults.get(tier.value)
                if tier.value in field.tier_defaults
                else field.platform_default
            )
            if default is None:
                result.valid = False
                result.errors.append({
                    "field_name": field_name,
                    "message": f"Required field '{field_name}' is missing",
                })

    return result


# ---------------------------------------------------------------------------
# Type-specific validators
# ---------------------------------------------------------------------------


def _validate_string(
    field_name: str,
    value: Any,
    rules: ValidationRule,
) -> tuple[bool, str | None, Any]:
    """Validate a string field."""
    if not isinstance(value, str):
        return False, f"Field '{field_name}' must be a string", None

    # Strip whitespace
    sanitized = value.strip()

    if rules.min_length is not None and len(sanitized) < rules.min_length:
        return (
            False,
            f"Field '{field_name}' must be at least {rules.min_length} characters",
            None,
        )

    if rules.max_length is not None and len(sanitized) > rules.max_length:
        return (
            False,
            f"Field '{field_name}' must be at most {rules.max_length} characters",
            None,
        )

    if rules.pattern is not None:
        if not re.match(rules.pattern, sanitized):
            return (
                False,
                f"Field '{field_name}' does not match required format",
                None,
            )

    return True, None, sanitized


def _validate_integer(
    field_name: str,
    value: Any,
    rules: ValidationRule,
) -> tuple[bool, str | None, Any]:
    """Validate an integer field."""
    if isinstance(value, bool):
        return False, f"Field '{field_name}' must be an integer", None
    if not isinstance(value, int):
        return False, f"Field '{field_name}' must be an integer", None

    if rules.min_value is not None and value < rules.min_value:
        return (
            False,
            f"Field '{field_name}' must be >= {rules.min_value}",
            None,
        )

    if rules.max_value is not None and value > rules.max_value:
        return (
            False,
            f"Field '{field_name}' must be <= {rules.max_value}",
            None,
        )

    return True, None, value


def _validate_float(
    field_name: str,
    value: Any,
    rules: ValidationRule,
) -> tuple[bool, str | None, Any]:
    """Validate a float field."""
    if isinstance(value, bool):
        return False, f"Field '{field_name}' must be a number", None
    if not isinstance(value, (int, float)):
        return False, f"Field '{field_name}' must be a number", None

    num = float(value)

    if rules.min_value is not None and num < rules.min_value:
        return (
            False,
            f"Field '{field_name}' must be >= {rules.min_value}",
            None,
        )

    if rules.max_value is not None and num > rules.max_value:
        return (
            False,
            f"Field '{field_name}' must be <= {rules.max_value}",
            None,
        )

    return True, None, num


def _validate_boolean(
    field_name: str,
    value: Any,
) -> tuple[bool, str | None, Any]:
    """Validate a boolean field."""
    if not isinstance(value, bool):
        return False, f"Field '{field_name}' must be a boolean", None
    return True, None, value


def _validate_enum(
    field_name: str,
    value: Any,
    rules: ValidationRule,
) -> tuple[bool, str | None, Any]:
    """Validate an enum field."""
    if not isinstance(value, str):
        return False, f"Field '{field_name}' must be a string", None

    stripped = value.strip()

    if rules.allowed_values:
        # Case-insensitive match, but return the canonical form from allowed_values
        # to preserve casing like zh-TW (WI-1493)
        lookup = {v.lower(): v for v in rules.allowed_values}
        canonical = lookup.get(stripped.lower())
        if canonical is None:
            allowed = ", ".join(rules.allowed_values)
            return (
                False,
                f"Field '{field_name}' must be one of: {allowed}",
                None,
            )
        return True, None, canonical

    return True, None, stripped.lower()


def _validate_string_list(
    field_name: str,
    value: Any,
    rules: ValidationRule,
) -> tuple[bool, str | None, Any]:
    """Validate a string list field."""
    if not isinstance(value, list):
        return False, f"Field '{field_name}' must be a list", None

    if rules.max_items is not None and len(value) > rules.max_items:
        return (
            False,
            f"Field '{field_name}' can have at most {rules.max_items} items",
            None,
        )

    sanitized: list[str] = []
    for i, item in enumerate(value):
        if not isinstance(item, str):
            return (
                False,
                f"Field '{field_name}[{i}]' must be a string",
                None,
            )
        stripped = item.strip()
        if not stripped:
            continue  # Skip empty strings

        if rules.max_length is not None and len(stripped) > rules.max_length:
            return (
                False,
                f"Field '{field_name}[{i}]' exceeds max length of {rules.max_length}",
                None,
            )

        # If allowed_values is set, validate each item
        if rules.allowed_values and stripped.lower() not in rules.allowed_values:
            allowed = ", ".join(rules.allowed_values[:10])
            return (
                False,
                f"Field '{field_name}[{i}]' ({stripped}) is not a valid option. "
                f"Valid: {allowed}",
                None,
            )

        sanitized.append(stripped)

    return True, None, sanitized
