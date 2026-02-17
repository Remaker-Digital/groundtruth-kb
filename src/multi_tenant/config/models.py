"""
Configuration result models.

Pydantic models returned by TenantConfigProcessor operations.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from src.multi_tenant.tenant_config_schema import ConfigValidationResult


class ConfigUpdateResult(BaseModel):
    """Result of a config update operation."""

    success: bool = Field(default=False, description="Whether the update was persisted")
    version: int = Field(default=0, description="New config version number")
    validation: ConfigValidationResult = Field(
        default_factory=lambda: ConfigValidationResult(valid=True),
        description="Validation result with errors/warnings",
    )
    changes: dict[str, Any] = Field(
        default_factory=dict,
        description="Fields that actually changed (old → new)",
    )
    resolved_config: dict[str, Any] = Field(
        default_factory=dict,
        description="The fully resolved config after the update",
    )


class ConfigReadResult(BaseModel):
    """Result of reading the current resolved config."""

    tenant_id: str = Field(description="Tenant identifier")
    tier: str = Field(description="Current tier")
    version: int = Field(description="Current config version")
    config: dict[str, Any] = Field(description="Fully resolved config values")
    from_cache: bool = Field(default=False, description="Whether this came from cache")


class ConfigVersionInfo(BaseModel):
    """Summary of a config version."""

    version: int = Field(description="Version number")
    is_current: bool = Field(description="Whether this is the active version")
    created_at: str = Field(description="When this version was created")
    created_by: str | None = Field(default=None, description="Who created it")
    field_count: int = Field(default=0, description="Number of configured fields")
    config_name: str | None = Field(default=None, description="Named configuration label")


class NamedConfigSummary(BaseModel):
    """Summary of a named configuration."""

    name: str = Field(description="Configuration name")
    version: int = Field(description="Version number this name points to")
    is_active: bool = Field(description="Whether this is the currently active named config")
    is_default: bool = Field(description="Whether this is the undeletable Default config")
    created_at: str = Field(description="When this named config was created")
    created_by: str | None = Field(default=None, description="Who created it")
    field_count: int = Field(default=0, description="Number of configured fields")


class ConfigRollbackResult(BaseModel):
    """Result of a rollback operation."""

    success: bool = Field(description="Whether the rollback was completed")
    from_version: int = Field(description="Version before rollback")
    to_version: int = Field(description="Version rolled back to")
    new_version: int = Field(description="New version created by rollback")
    message: str = Field(default="", description="Status message")
