# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""groundtruth_kb.bridge — Reusable inter-agent message bridge.

Synchronous dialog model (v3) for Codex <-> Prime Builder coordination.
"""

from groundtruth_kb.bridge.handshake import run_handshake
from groundtruth_kb.bridge.runtime import (
    Agent,
    PeerAgent,
    get_bridge_db,
    list_inbox,
    resolve_message,
    retry_pending_message,
    send_message,
    wait_for_notifications,
)
from groundtruth_kb.bridge.worker import (
    resident_worker_health_snapshot,
    resident_worker_is_healthy,
    resident_worker_should_defer,
)
from groundtruth_kb.bridge.worker import (
    run as run_worker,
)

__all__ = [
    # runtime
    "Agent",
    "PeerAgent",
    "get_bridge_db",
    "list_inbox",
    "resolve_message",
    "retry_pending_message",
    "send_message",
    "wait_for_notifications",
    # worker
    "resident_worker_is_healthy",
    "resident_worker_health_snapshot",
    "resident_worker_should_defer",
    "run_worker",
    # handshake
    "run_handshake",
]
