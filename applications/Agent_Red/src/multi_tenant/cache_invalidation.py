# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Cross-replica cache invalidation via Redis pub/sub (SPEC-1757).

When multiple Container App replicas each maintain local tenant metadata
caches, a config or tier change on one replica leaves stale data on others.
This module provides Redis pub/sub-based invalidation:

- publish_cache_invalidation(tenant_id) — fires on tier/config/status changes
- A background subscriber thread listens and evicts local cache entries

Without Redis the module is a no-op — TTL-based expiry handles invalidation
with eventual consistency within the configured cache TTL window.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import threading
from typing import Any

logger = logging.getLogger(__name__)

# Redis pub/sub channel name
INVALIDATION_CHANNEL = "agentred:cache:invalidate"

# Module-level state
_redis_client: Any | None = None
_subscriber_thread: threading.Thread | None = None
_shutdown_event = threading.Event()


def configure_cache_invalidation(redis_client: Any) -> None:
    """Set the Redis client for cache invalidation pub/sub.

    Called from lifecycle startup after Redis connection is established.
    Starts the background subscriber thread.
    """
    global _redis_client, _subscriber_thread

    _redis_client = redis_client
    _shutdown_event.clear()

    _subscriber_thread = threading.Thread(
        target=_subscriber_loop,
        name="cache-invalidation-subscriber",
        daemon=True,
    )
    _subscriber_thread.start()
    logger.info("Cache invalidation subscriber started on channel: %s", INVALIDATION_CHANNEL)


def shutdown_cache_invalidation() -> None:
    """Stop the background subscriber thread."""
    global _redis_client, _subscriber_thread

    _shutdown_event.set()
    if _subscriber_thread is not None:
        _subscriber_thread.join(timeout=5.0)
        _subscriber_thread = None
    _redis_client = None
    logger.info("Cache invalidation subscriber stopped")


def publish_cache_invalidation(tenant_id: str | None = None) -> bool:
    """Publish a cache invalidation event to all replicas.

    Args:
        tenant_id: The tenant whose cache entries should be invalidated.
            If None, signals a full cache flush.

    Returns:
        True if published successfully, False if Redis is unavailable.
    """
    if _redis_client is None:
        return False

    message = tenant_id or "__all__"
    try:
        _redis_client.publish(INVALIDATION_CHANNEL, message)
        logger.debug("Published cache invalidation: %s", message)
        return True
    except Exception:
        logger.warning(
            "Failed to publish cache invalidation for %s — "
            "other replicas will rely on TTL expiry",
            message,
            exc_info=True,
        )
        return False


def _subscriber_loop() -> None:
    """Background thread that subscribes to invalidation events.

    Reconnects automatically on Redis failures with exponential backoff.
    """
    backoff = 1.0
    max_backoff = 30.0

    while not _shutdown_event.is_set():
        try:
            if _redis_client is None:
                _shutdown_event.wait(timeout=backoff)
                continue

            pubsub = _redis_client.pubsub()
            pubsub.subscribe(INVALIDATION_CHANNEL)
            logger.debug("Subscribed to %s", INVALIDATION_CHANNEL)
            backoff = 1.0  # Reset on successful subscribe

            for message in pubsub.listen():
                if _shutdown_event.is_set():
                    break

                if message["type"] != "message":
                    continue

                data = message.get("data", "")
                # Redis with decode_responses=True returns str, otherwise bytes
                if isinstance(data, bytes):
                    data = data.decode("utf-8", errors="replace")

                tenant_id = None if data == "__all__" else data

                # Invalidate local caches — import here to avoid circular imports.
                # _publish=False prevents re-publishing back to Redis (infinite loop).
                from src.multi_tenant.middleware import invalidate_tenant_meta_cache

                invalidate_tenant_meta_cache(tenant_id, _publish=False)
                logger.debug(
                    "Received cache invalidation: %s",
                    tenant_id or "(full flush)",
                )

            pubsub.unsubscribe()
            pubsub.close()

        except Exception:
            logger.warning(
                "Cache invalidation subscriber error — reconnecting in %.1fs",
                backoff,
                exc_info=True,
            )
            _shutdown_event.wait(timeout=backoff)
            backoff = min(backoff * 2, max_backoff)


def is_configured() -> bool:
    """Return True if Redis pub/sub invalidation is active."""
    return _redis_client is not None and _subscriber_thread is not None
