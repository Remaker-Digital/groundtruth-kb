# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
TenantConfigProcessor — backward-compatible re-export barrel.

All processor classes now live in ``src.multi_tenant.config.*``.
This file re-exports every public name so that existing imports like:

    from src.multi_tenant.tenant_config_processor import get_config_processor

continue to work without modification.

For new code, prefer importing from the package directly:

    from src.multi_tenant.config import TenantConfigProcessor
    from src.multi_tenant.config.processor import get_config_processor

Architecture reference: Decision #22 (TenantConfigProcessor)
R4 refactoring — session 34.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

# Re-export everything from the config package
from src.multi_tenant.config import (  # noqa: F401
    _PREFS_DIRECT_FIELDS,
    _WIDGET_APPEARANCE_FIELDS,
    CACHE_TTL_SECONDS,
    ConfigReadResult,
    ConfigRollbackResult,
    ConfigUpdateResult,
    ConfigVersionInfo,
    NamedConfigSummary,
    TenantConfigProcessor,
    _CacheEntry,
    _config_to_preferences,
    _log_config_change,
    _preferences_to_config,
    get_config_processor,
)

# Transitive re-export: ConfigValidationResult was importable from
# the old monolithic module via its `from tenant_config_schema import ...`
from src.multi_tenant.tenant_config_schema import (  # noqa: F401
    ConfigValidationResult,
)

__all__ = [
    # Result models
    "ConfigUpdateResult",
    "ConfigReadResult",
    "ConfigVersionInfo",
    "NamedConfigSummary",
    "ConfigRollbackResult",
    # Cache
    "CACHE_TTL_SECONDS",
    "_CacheEntry",
    # Field mapping
    "_PREFS_DIRECT_FIELDS",
    "_WIDGET_APPEARANCE_FIELDS",
    "_config_to_preferences",
    "_preferences_to_config",
    # Audit
    "_log_config_change",
    # Processor + singleton
    "TenantConfigProcessor",
    "get_config_processor",
    # Transitive
    "ConfigValidationResult",
]
