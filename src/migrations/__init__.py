"""Schema migration framework for Agent Red Customer Experience.

Forward-only migrations for Cosmos DB schema changes. Migrations are
tracked in the `_migrations` container so each migration runs exactly once.

Usage:
    from src.migrations.apply import MigrationRunner
    runner = MigrationRunner(cosmos_manager)
    await runner.check_pending()   # Returns list of unapplied migrations
    await runner.apply_all()       # Applies all pending migrations

Design constraints:
    - Forward-only: no down() methods (Cosmos DB not safely reversible)
    - Backward-compatible: new fields must have defaults, no field removal
    - Startup warning only: unapplied migrations log a warning, no auto-apply
    - Idempotent: re-running a migration on an already-migrated doc is safe

Architecture references:
    - Phase 6A: Schema Migration Framework (upgrade plan)
    - Decision #18: Cosmos DB continuous 7-day backup (PITR safety net)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from src.migrations.apply import MigrationRunner

__all__ = ["MigrationRunner"]
