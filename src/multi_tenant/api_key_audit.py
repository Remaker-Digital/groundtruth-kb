"""API key usage audit trail (SPEC-1832).

Records which API key (or auth method) was used for every authenticated
request, creating a forensic trail for security investigations.

Uses an in-memory buffer that flushes to Cosmos DB audit_log in batches
to avoid per-request write latency. Buffer flushed on interval or when
full (whichever comes first).

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import asyncio
import logging
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Audit record
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ApiKeyUsageRecord:
    """A single API key usage event."""

    tenant_id: str
    auth_method: str  # "api_key", "widget_key", "shopify", "spa_key", "magic_link", "user_api_key"
    key_suffix: str  # Last 8 chars of key hash (or "n/a" for non-key auth)
    path: str
    method: str
    status_code: int
    timestamp: str
    client_ip: str = ""
    team_member_id: str | None = None


# ---------------------------------------------------------------------------
# Audit buffer (in-memory, flushed periodically)
# ---------------------------------------------------------------------------


_FLUSH_INTERVAL_SECONDS = 60  # Flush every 60 seconds
_BUFFER_SIZE = 500  # Flush when buffer reaches this size


class ApiKeyAuditBuffer:
    """In-memory buffer for API key usage records.

    Batches audit writes to Cosmos DB to minimize per-request overhead.
    Thread-safe via asyncio (single-threaded event loop).
    """

    def __init__(self, flush_interval: float = _FLUSH_INTERVAL_SECONDS,
                 buffer_size: int = _BUFFER_SIZE) -> None:
        self._buffer: deque[ApiKeyUsageRecord] = deque(maxlen=buffer_size * 2)
        self._flush_interval = flush_interval
        self._buffer_size = buffer_size
        self._flush_task: asyncio.Task | None = None
        self._audit_repo: Any = None

    def configure(self, audit_repo: Any) -> None:
        """Wire the audit log repository at app startup."""
        self._audit_repo = audit_repo

    def record(self, record: ApiKeyUsageRecord) -> None:
        """Add a usage record to the buffer (non-blocking)."""
        self._buffer.append(record)

        # Flush if buffer is full
        if len(self._buffer) >= self._buffer_size:
            self._schedule_flush()

    def start(self) -> None:
        """Start the periodic flush task."""
        if self._flush_task is None or self._flush_task.done():
            self._flush_task = asyncio.ensure_future(self._periodic_flush())

    def stop(self) -> None:
        """Stop the periodic flush task."""
        if self._flush_task and not self._flush_task.done():
            self._flush_task.cancel()

    @property
    def pending_count(self) -> int:
        """Number of records waiting to be flushed."""
        return len(self._buffer)

    async def flush(self) -> int:
        """Flush all pending records to Cosmos DB. Returns count flushed."""
        if not self._buffer:
            return 0

        if not self._audit_repo:
            logger.debug("API key audit: no audit repo configured, discarding %d records", len(self._buffer))
            self._buffer.clear()
            return 0

        # Drain buffer
        records = list(self._buffer)
        self._buffer.clear()

        flushed = 0
        for record in records:
            try:
                from src.multi_tenant.cosmos_schema import AuditEventType
                await self._audit_repo.log_event(
                    tenant_id=record.tenant_id,
                    event_type=AuditEventType.SECURITY_EVENT,
                    actor_id=f"key:{record.key_suffix}",
                    resource_type="api_request",
                    resource_id=f"{record.method} {record.path}",
                    details={
                        "action": "api_key_usage",
                        "auth_method": record.auth_method,
                        "key_suffix": record.key_suffix,
                        "path": record.path,
                        "method": record.method,
                        "status_code": record.status_code,
                        "client_ip": record.client_ip,
                        "team_member_id": record.team_member_id,
                    },
                )
                flushed += 1
            except Exception:
                logger.debug("API key audit flush failed for %s %s", record.method, record.path)

        if flushed > 0:
            logger.debug("API key audit: flushed %d/%d records", flushed, len(records))

        return flushed

    def _schedule_flush(self) -> None:
        """Schedule an immediate async flush."""
        try:
            asyncio.ensure_future(self.flush())
        except RuntimeError:
            pass  # No event loop — ignore

    async def _periodic_flush(self) -> None:
        """Background task that flushes the buffer periodically."""
        while True:
            try:
                await asyncio.sleep(self._flush_interval)
                await self.flush()
            except asyncio.CancelledError:
                # Final flush on shutdown
                await self.flush()
                break
            except Exception:
                logger.debug("API key audit periodic flush error", exc_info=True)


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_audit_buffer: ApiKeyAuditBuffer | None = None


def get_api_key_audit_buffer() -> ApiKeyAuditBuffer:
    """Get or create the global API key audit buffer."""
    global _audit_buffer
    if _audit_buffer is None:
        _audit_buffer = ApiKeyAuditBuffer()
    return _audit_buffer


def record_api_key_usage(
    tenant_id: str,
    auth_method: str,
    key_suffix: str,
    path: str,
    method: str,
    status_code: int = 200,
    client_ip: str = "",
    team_member_id: str | None = None,
) -> None:
    """Convenience function to record API key usage (SPEC-1832).

    Called from TenantAuthMiddleware.dispatch() after successful auth.
    Non-blocking — appends to in-memory buffer.
    """
    buf = get_api_key_audit_buffer()
    buf.record(ApiKeyUsageRecord(
        tenant_id=tenant_id,
        auth_method=auth_method,
        key_suffix=key_suffix,
        path=path,
        method=method,
        status_code=status_code,
        timestamp=datetime.now(timezone.utc).isoformat(),
        client_ip=client_ip,
        team_member_id=team_member_id,
    ))
