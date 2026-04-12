# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Legacy SQLite/MCP inter-agent message bridge.

This package is retained for compatibility with projects that still depend on
the older database-backed Prime Bridge runtime. New GroundTruth dual-agent
projects should use the file bridge pattern documented in
docs/method/12-file-bridge-automation.md and should not use this package as
their active coordination channel.
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
