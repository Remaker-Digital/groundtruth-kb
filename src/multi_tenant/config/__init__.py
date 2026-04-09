# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
Config package — re-exports all public config classes and functions.

All existing imports via ``from src.multi_tenant.tenant_config_processor import X``
continue to work unchanged via the re-export barrel in tenant_config_processor.py.
Direct imports from this package are also supported:

    from src.multi_tenant.config import TenantConfigProcessor
    from src.multi_tenant.config.processor import get_config_processor

R4 refactoring — session 34.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

# Result models
# Audit
from src.multi_tenant.config.audit import _log_config_change

# Cache
from src.multi_tenant.config.cache import (
    CACHE_TTL_SECONDS,
    _CacheEntry,
)

# Field mapping
from src.multi_tenant.config.field_mapping import (
    _PREFS_DIRECT_FIELDS,
    _WIDGET_APPEARANCE_FIELDS,
    _config_to_preferences,
    _preferences_to_config,
)
from src.multi_tenant.config.models import (
    ConfigReadResult,
    ConfigRollbackResult,
    ConfigUpdateResult,
    ConfigVersionInfo,
    NamedConfigSummary,
)

# Processor + singleton
from src.multi_tenant.config.processor import (
    TenantConfigProcessor,
    get_config_processor,
)

__all__ = [
    # Models
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
    # Processor
    "TenantConfigProcessor",
    "get_config_processor",
]
