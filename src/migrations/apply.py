"""Migration runner for Agent Red schema migrations.

Discovers migration modules in src/migrations/, tracks applied migrations
in the `_migrations` Cosmos DB container, and applies pending migrations
in sequence order.

Design:
    - Each migration is a Python module named NNN_description.py
    - Module must define: VERSION (str), DESCRIPTION (str), async up(cosmos_manager)
    - Applied migrations are recorded as documents in the _migrations container
    - Forward-only: no rollback (Cosmos DB PITR is the safety net)
    - Startup check: check_pending() returns unapplied migrations for logging

Usage at app startup (main.py):
    runner = MigrationRunner(cosmos_manager)
    pending = await runner.check_pending()
    if pending:
        logger.warning("Unapplied migrations: %s", [m.VERSION for m in pending])

Manual apply (scripts/apply_migrations.py):
    runner = MigrationRunner(cosmos_manager)
    results = await runner.apply_all()

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import importlib
import logging
import pkgutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Protocol

logger = logging.getLogger(__name__)

# Container for tracking applied migrations
MIGRATIONS_CONTAINER = "_migrations"
MIGRATIONS_PARTITION_KEY = "/version"


# ---------------------------------------------------------------------------
# Protocol for migration modules
# ---------------------------------------------------------------------------


class MigrationModule(Protocol):
    """Protocol that each migration module must satisfy."""

    VERSION: str
    DESCRIPTION: str

    async def up(self, cosmos_manager: Any) -> None: ...


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class MigrationRecord:
    """Tracks a single applied migration."""

    version: str
    description: str
    applied_at: str
    applied_by: str = "migration-runner"
    success: bool = True
    error: str | None = None


@dataclass
class MigrationResult:
    """Result of applying a single migration."""

    version: str
    description: str
    success: bool
    duration_ms: float
    error: str | None = None


@dataclass
class ApplyResults:
    """Aggregate results of applying all pending migrations."""

    applied: list[MigrationResult] = field(default_factory=list)
    failed: list[MigrationResult] = field(default_factory=list)

    @property
    def all_succeeded(self) -> bool:
        return len(self.failed) == 0 and len(self.applied) > 0

    @property
    def total(self) -> int:
        return len(self.applied) + len(self.failed)


# ---------------------------------------------------------------------------
# Migration Runner
# ---------------------------------------------------------------------------


class MigrationRunner:
    """Discovers, tracks, and applies schema migrations."""

    def __init__(self, cosmos_manager: Any) -> None:
        self._cosmos = cosmos_manager
        self._container: Any | None = None

    async def _ensure_container(self) -> Any:
        """Get or create the _migrations tracking container."""
        if self._container is not None:
            return self._container

        database = self._cosmos._client.get_database_client(
            self._cosmos._database_name
        )

        # Create container if not exists
        try:
            self._container = database.get_container_client(MIGRATIONS_CONTAINER)
            # Verify it exists by reading properties
            await self._container.read()
        except Exception:
            # Create the container
            await database.create_container_if_not_exists(
                id=MIGRATIONS_CONTAINER,
                partition_key={"paths": [MIGRATIONS_PARTITION_KEY], "kind": "Hash"},
            )
            self._container = database.get_container_client(MIGRATIONS_CONTAINER)

        return self._container

    def _discover_migrations(self) -> list[MigrationModule]:
        """Discover all migration modules in src/migrations/ directory.

        Returns modules sorted by VERSION (lexicographic).
        Excludes __init__.py, apply.py, and any non-migration files.
        """
        import src.migrations as migrations_pkg

        modules: list[MigrationModule] = []

        for importer, modname, ispkg in pkgutil.iter_modules(
            migrations_pkg.__path__, prefix="src.migrations."
        ):
            # Skip non-migration modules
            short_name = modname.split(".")[-1]
            if short_name in ("__init__", "apply") or ispkg:
                continue

            # Must match _NNN_description pattern (underscore + digits)
            stripped = short_name.lstrip("_")
            if not stripped or not stripped[0].isdigit():
                continue

            try:
                mod = importlib.import_module(modname)

                # Validate migration module interface
                if not hasattr(mod, "VERSION"):
                    logger.warning("Migration %s missing VERSION, skipping", modname)
                    continue
                if not hasattr(mod, "DESCRIPTION"):
                    logger.warning(
                        "Migration %s missing DESCRIPTION, skipping", modname
                    )
                    continue
                if not hasattr(mod, "up"):
                    logger.warning("Migration %s missing up(), skipping", modname)
                    continue

                modules.append(mod)  # type: ignore[arg-type]
            except Exception as e:
                logger.error("Failed to import migration %s: %s", modname, e)

        # Sort by VERSION string (lexicographic — 000 < 001 < 002)
        modules.sort(key=lambda m: m.VERSION)
        return modules

    async def _get_applied_versions(self) -> set[str]:
        """Get set of already-applied migration versions from Cosmos DB."""
        container = await self._ensure_container()

        try:
            query = "SELECT c.version FROM c WHERE c.success = true"
            items = container.query_items(
                query=query,
            )

            versions: set[str] = set()
            async for item in items:
                versions.add(item["version"])
            return versions
        except Exception as e:
            logger.warning("Could not read migration history: %s", e)
            return set()

    async def check_pending(self) -> list[MigrationModule]:
        """Return list of unapplied migrations (for startup warning).

        Does NOT apply them — call apply_all() for that.
        """
        all_migrations = self._discover_migrations()
        if not all_migrations:
            return []

        applied = await self._get_applied_versions()
        pending = [m for m in all_migrations if m.VERSION not in applied]

        if pending:
            versions = [m.VERSION for m in pending]
            logger.warning(
                "Found %d unapplied migration(s): %s. "
                "Run 'python -m src.migrations.apply' to apply.",
                len(pending),
                versions,
            )

        return pending

    async def apply_all(self) -> ApplyResults:
        """Apply all pending migrations in order.

        Each migration is:
        1. Checked against _migrations container
        2. Executed via up(cosmos_manager)
        3. Recorded in _migrations container on success
        4. Logged and recorded on failure (stops further migrations)

        Returns ApplyResults with applied/failed lists.
        """
        import time

        results = ApplyResults()
        pending = await self.check_pending()

        if not pending:
            logger.info("No pending migrations to apply.")
            return results

        container = await self._ensure_container()

        for migration in pending:
            version = migration.VERSION
            description = migration.DESCRIPTION

            logger.info(
                "Applying migration %s: %s ...",
                version,
                description,
            )

            start = time.monotonic()
            try:
                await migration.up(self._cosmos)
                duration_ms = (time.monotonic() - start) * 1000

                # Record success
                record = {
                    "id": f"migration-{version}",
                    "version": version,
                    "description": description,
                    "applied_at": datetime.now(timezone.utc).isoformat(),
                    "applied_by": "migration-runner",
                    "success": True,
                    "duration_ms": round(duration_ms, 1),
                }
                await container.upsert_item(record)

                result = MigrationResult(
                    version=version,
                    description=description,
                    success=True,
                    duration_ms=round(duration_ms, 1),
                )
                results.applied.append(result)

                logger.info(
                    "Migration %s applied successfully (%.1fms)",
                    version,
                    duration_ms,
                )

            except Exception as e:
                duration_ms = (time.monotonic() - start) * 1000
                error_msg = str(e)

                # Record failure
                record = {
                    "id": f"migration-{version}",
                    "version": version,
                    "description": description,
                    "applied_at": datetime.now(timezone.utc).isoformat(),
                    "applied_by": "migration-runner",
                    "success": False,
                    "error": error_msg,
                    "duration_ms": round(duration_ms, 1),
                }
                try:
                    await container.upsert_item(record)
                except Exception:
                    pass  # Don't fail on recording the failure

                result = MigrationResult(
                    version=version,
                    description=description,
                    success=False,
                    duration_ms=round(duration_ms, 1),
                    error=error_msg,
                )
                results.failed.append(result)

                logger.error(
                    "Migration %s FAILED after %.1fms: %s. "
                    "Stopping migration runner. Fix and retry.",
                    version,
                    duration_ms,
                    error_msg,
                )
                break  # Stop on first failure

        return results


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


async def _main() -> None:
    """CLI entry point: python -m src.migrations.apply"""
    import sys

    from src.multi_tenant.cosmos_client import get_cosmos_manager

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    cosmos = get_cosmos_manager()
    try:
        await cosmos.initialize()
    except Exception as e:
        logger.error("Failed to connect to Cosmos DB: %s", e)
        sys.exit(1)

    runner = MigrationRunner(cosmos)
    results = await runner.apply_all()

    if results.total == 0:
        print("No pending migrations.")
        sys.exit(0)
    elif results.all_succeeded:
        print(f"Successfully applied {len(results.applied)} migration(s).")
        sys.exit(0)
    else:
        print(
            f"Migration failed: {len(results.applied)} applied, "
            f"{len(results.failed)} failed."
        )
        for f in results.failed:
            print(f"  FAILED: {f.version} — {f.error}")
        sys.exit(1)


if __name__ == "__main__":
    import asyncio

    asyncio.run(_main())
