# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Integration Registry — singleton registry for plugin management (SPEC-1761).

The registry is the central coordination point for all integrations.
It manages manifest registration, per-tenant adapter instances, and
capability queries.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from typing import Any, Protocol

from src.integrations.manifest import (
    Capability,
    IntegrationCategory,
    IntegrationManifest,
    IntegrationStatus,
)
from src.integrations.models import IntegrationError

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Adapter factory type
# ---------------------------------------------------------------------------


class AdapterFactory(Protocol):
    """Callable that creates an adapter instance for a tenant."""

    def __call__(self, tenant_id: str) -> Any:
        ...


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


class IntegrationRegistry:
    """Singleton registry for integration plugins.

    Manages manifest registration, per-tenant adapter instance lifecycle,
    and capability queries.
    """

    _instance: IntegrationRegistry | None = None

    def __init__(self) -> None:
        self._manifests: dict[str, IntegrationManifest] = {}
        self._factories: dict[str, AdapterFactory] = {}
        self._instances: dict[tuple[str, str], Any] = {}  # (tenant_id, integration_id) -> adapter

    @classmethod
    def get_instance(cls) -> IntegrationRegistry:
        """Return the singleton registry instance."""
        if cls._instance is None:
            cls._instance = IntegrationRegistry()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton (testing only)."""
        cls._instance = None

    # -- Registration -------------------------------------------------------

    def register(
        self,
        manifest: IntegrationManifest,
        factory: AdapterFactory,
    ) -> None:
        """Register an integration manifest and its adapter factory."""
        if manifest.integration_id in self._manifests:
            logger.warning(
                "Re-registering integration %s (replacing existing)",
                manifest.integration_id,
            )
        self._manifests[manifest.integration_id] = manifest
        self._factories[manifest.integration_id] = factory
        logger.info(
            "Registered integration: %s (%s) category=%s capabilities=%d",
            manifest.integration_id,
            manifest.display_name,
            manifest.category.value,
            len(manifest.capabilities),
        )

    def unregister(self, integration_id: str) -> None:
        """Remove an integration from the registry."""
        self._manifests.pop(integration_id, None)
        self._factories.pop(integration_id, None)
        # Clean up all tenant instances
        keys_to_remove = [
            k for k in self._instances if k[1] == integration_id
        ]
        for k in keys_to_remove:
            self._instances.pop(k, None)

    # -- Queries ------------------------------------------------------------

    def get_manifest(self, integration_id: str) -> IntegrationManifest | None:
        """Get the manifest for a registered integration."""
        return self._manifests.get(integration_id)

    def list_available(
        self,
        *,
        category: IntegrationCategory | None = None,
        capability: Capability | None = None,
        tier: str | None = None,
    ) -> list[IntegrationManifest]:
        """List available integrations, optionally filtered."""
        results = []
        tier_order = {"free": 0, "starter": 1, "professional": 2, "enterprise": 3}

        for manifest in self._manifests.values():
            if manifest.status in (
                IntegrationStatus.DISABLED,
                IntegrationStatus.DEPRECATED,
            ):
                continue
            if category and manifest.category != category:
                continue
            if capability and not manifest.has_capability(capability):
                continue
            if tier:
                tenant_level = tier_order.get(tier, 0)
                required_level = tier_order.get(manifest.tier_gate, 0)
                if tenant_level < required_level:
                    continue
            results.append(manifest)

        return sorted(results, key=lambda m: m.display_name)

    def get_capabilities(
        self, integration_id: str
    ) -> frozenset[Capability]:
        """Get capabilities for an integration."""
        manifest = self._manifests.get(integration_id)
        if manifest is None:
            return frozenset()
        return manifest.capabilities

    # -- Instance Management ------------------------------------------------

    def get_adapter(self, tenant_id: str, integration_id: str) -> Any:
        """Get or lazily create an adapter instance for a tenant.

        Raises IntegrationError if the integration is not registered.
        """
        key = (tenant_id, integration_id)
        if key in self._instances:
            return self._instances[key]

        factory = self._factories.get(integration_id)
        if factory is None:
            raise IntegrationError(
                f"Integration {integration_id} not registered",
                integration_id=integration_id,
            )

        adapter = factory(tenant_id)
        self._instances[key] = adapter
        logger.debug(
            "Created adapter instance: tenant=%s integration=%s",
            tenant_id,
            integration_id,
        )
        return adapter

    def cleanup_tenant(self, tenant_id: str) -> int:
        """Remove all adapter instances for a tenant. Returns count removed."""
        keys_to_remove = [k for k in self._instances if k[0] == tenant_id]
        for k in keys_to_remove:
            self._instances.pop(k, None)
        return len(keys_to_remove)

    async def health_check(
        self, tenant_id: str, integration_id: str
    ) -> bool:
        """Check if an integration is healthy for a tenant."""
        try:
            adapter = self.get_adapter(tenant_id, integration_id)
            if hasattr(adapter, "health_check"):
                return await adapter.health_check(tenant_id)
            return True
        except Exception:
            return False

    # -- Stats --------------------------------------------------------------

    @property
    def registered_count(self) -> int:
        """Number of registered integrations."""
        return len(self._manifests)

    @property
    def active_instance_count(self) -> int:
        """Number of active adapter instances across all tenants."""
        return len(self._instances)
