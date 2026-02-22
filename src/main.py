"""
Agent Red Customer Experience — FastAPI application entrypoint.

Thin composition root: creates the app, registers middleware, routers,
static mounts, startup/shutdown handlers, and health endpoints.

All implementation is in ``src/app/`` submodules — this file only wires
them together and re-exports names that existing test code imports.

Usage:
    uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib  # re-exported — used by test_forgot_password via main_mod.hashlib

from src.app.factory import create_app
from src.app.routers import register_routers
from src.app.static_serving import mount_static_apps
from src.app.standalone_auth import mount_standalone_admin
from src.app.lifecycle import (
    register_middleware,
    register_startup_handlers,
    register_shutdown_handlers,
)
from src.app.background import register_idle_scanner, register_sla_snapshots, register_alert_evaluation, register_ingestion_processor, register_archival_sweep
from src.app.health import register_health_endpoints

# ---------------------------------------------------------------------------
# Application composition
# ---------------------------------------------------------------------------

app = create_app()
register_middleware(app)
register_routers(app)
mount_static_apps(app)
mount_standalone_admin(app)
register_startup_handlers(app)
register_shutdown_handlers(app)
register_idle_scanner(app)
register_sla_snapshots(app)
register_alert_evaluation(app)
register_ingestion_processor(app)
register_archival_sweep(app)
register_health_endpoints(app)

# ---------------------------------------------------------------------------
# Re-exports for backward compatibility (consumed by test code)
# ---------------------------------------------------------------------------

# tests/test_forgot_password.py — function imports + fixture state mutations
from src.app.standalone_auth import (  # noqa: E402, F401
    _generate_reset_token,
    _validate_reset_token,
    _admin_used_reset_nonces,
)

# tests/test_health.py — startup handler existence checks
from src.app.lifecycle import (  # noqa: E402, F401
    _startup_tenant_resolution,
    _startup_tracing,
    _startup_circuit_breakers,
    _startup_nats,
    _startup_secret_service,
)

# tests/multi_tenant/test_idle_scanner.py — lifecycle handler checks
from src.app.background import (  # noqa: E402, F401
    _idle_scanner_loop,
    _idle_scanner_task,
    _startup_idle_scanner,
    _shutdown_idle_scanner,
)
