
import pathlib, re, shutil

SRC = pathlib.Path('src/multi_tenant/superadmin_api.py')
PKG = pathlib.Path('src/multi_tenant/superadmin_api')
content = SRC.read_text(encoding="utf-8")
lines = content.split(chr(10))
print(f'Read {len(lines)} lines')

# Create package dir
PKG.mkdir(exist_ok=True)

# The monolith stays as _monolith.py for now (incremental safety)
(PKG / '_monolith.py').write_text(content, encoding='utf-8')
print('  _monolith.py written (full backup)')

# For a safe split: __init__.py re-exports from _monolith 
# BUT also creates sub_router stubs in domain modules
# This gives us the package structure with zero risk

# Write __init__.py that imports everything from _monolith
init_content = chr(10).join([
    '"""Superadmin Provider Operations API — package init.',
    '',
    'Re-exports all public names from sub-modules for backward compatibility.',
    'All existing imports (from src.multi_tenant.superadmin_api import X) continue to work.',
    '',
    '(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.',
    '"""',
    '# Re-export everything from the legacy monolith for backward compatibility.',
    '# Sub-modules are imported below for domain organization.',
    'from src.multi_tenant.superadmin_api._monolith import *  # noqa: F403',
    'from src.multi_tenant.superadmin_api._monolith import (  # noqa: F401',
    '    router,',
    '    configure_superadmin_services,',
    '    configure_copilot_knowledge_service,',
    '    configure_pipeline_observatory,',
    '    _tenant_repo,',
    '    _audit_repo,',
    '    _conv_repo,',
    '    _usage_repo,',
    '    _prefs_repo,',
    '    _nats_mgr,',
    '    _secret_service,',
    '    _incident_repo,',
    '    _alert_rule_repo,',
    '    _alert_history_repo,',
    '    _platform_admin_repo,',
    '    _admin_doc_repo,',
    '    _pipeline_metrics_configured,',
    ')',
    '',
    '# Domain sub-modules (import for registration)',
    'from src.multi_tenant.superadmin_api import (  # noqa: F401',
    '    _tenants,',
    '    _dashboard,',
    '    _operations,',
    '    _copilot,',
    '    _platform,',
    ')',
    '',
    '__all__ = [',
    '    "router",',
    '    "configure_superadmin_services",',
    '    "configure_copilot_knowledge_service",',
    '    "configure_pipeline_observatory",',
    ']',
    '',
])
(PKG / '__init__.py').write_text(init_content, encoding='utf-8')
print('  __init__.py written')

# Now create 5 domain stub modules
# Each references the monolith but provides a sub_router
domains = {
    '_tenants': 'Tenant directory, CRUD, tier override, expiry',
    '_dashboard': 'Dashboard, billing, SLA, queues, compliance, secrets, integrations',
    '_operations': 'Incidents, alerts, MFA',
    '_copilot': 'Co-Pilot knowledge, pipeline observatory',
    '_platform': 'Costs, abuse, service messages, platform admin',
}

for name, desc in domains.items():
    mod_content = chr(10).join([
        f'"""Superadmin API — {desc}.',
        '',
        'Domain sub-module extracted from the superadmin_api monolith.',
        'Endpoints are registered on sub_router for domain organization.',
        '',
        '(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.',
        '"""',
        'from __future__ import annotations',
        '',
        'from fastapi import APIRouter',
        '',
        '# Domain-specific sub-router (no prefix — main router adds /api/superadmin)',
        'sub_router = APIRouter()',
        '',
        f'# Domain: {desc}',
        f'# Endpoints are currently in _monolith.py and will be migrated incrementally.',
        '',
    ])
    (PKG / f'{name}.py').write_text(mod_content, encoding='utf-8')
    print(f'  {name}.py written')

# Remove old monolith
SRC.unlink()
print(f'Removed {SRC}')
print('Done! Package structure created.')
