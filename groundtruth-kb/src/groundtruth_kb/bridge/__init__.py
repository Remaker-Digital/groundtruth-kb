# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""GroundTruth-KB bridge package.

RETIRED: The smart-poller mechanism was retired on 2026-05-09 in favor of the
cross-harness event-driven trigger at ``scripts/cross_harness_bridge_trigger.py``.
The runtime entrypoint (``bridge_poller_runner``) and OS-task install scripts
have been archived to ``archive/smart-poller-2026-05-09/``. The detector,
checkpoint, routing, audit, registry, paths, notify, and handshake modules in
this package are retained for compatibility and historical reference; they are
no longer the active dispatch surface. Bridge dispatch is now governed by
``.claude/settings.json`` and ``.codex/hooks.json`` PostToolUse + Stop hooks.

The legacy SQLite/MCP message bridge is also retained for compatibility with
projects that still depend on the older database-backed Prime Bridge runtime.
New GroundTruth dual-agent projects should use the file bridge pattern
documented in ``docs/method/12-file-bridge-automation.md`` and the
cross-harness event-driven trigger described in
``docs/tutorials/dual-agent-setup.md``.

Historical references in code comments below to "smart-poller P1/P2/P2.5/P3"
work programs describe the now-retired runtime; the modules themselves remain
importable for adopters that still consume them.
"""

from groundtruth_kb.bridge.audit import (
    AUDIT_FILENAME,
    AuditEvent,
    emit_audit_event,
    emit_bootstrap_event,
    emit_transition_event,
    read_audit_log,
)
from groundtruth_kb.bridge.checkpoint import (
    CHECKPOINT_FILENAME,
    CHECKPOINT_SCHEMA_VERSION,
    Checkpoint,
    CheckpointEntry,
    CheckpointLoadResult,
    Transition,
    diff_against_checkpoint,
    load_checkpoint,
    write_checkpoint,
)
from groundtruth_kb.bridge.detector import (
    BridgeDocument,
    BridgeStatus,
    BridgeVersion,
    ParseError,
    ParseResult,
    ParseWarning,
    parse_index,
)
from groundtruth_kb.bridge.handshake import run_handshake
from groundtruth_kb.bridge.notify import (
    ACTIONABLE_STATUSES_FOR_CODEX,
    ACTIONABLE_STATUSES_FOR_PRIME,
    NOTIFY_SCHEMA_VERSION,
    NOTIFY_SUBDIR,
    ActionablePending,
    NotificationArtifact,
    clear_notification,
    compute_actionable_pending,
    read_notification,
    update_notification,
)
from groundtruth_kb.bridge.paths import (
    GROUNDTRUTH_MARKER,
    PROJECT_ROOT_ENV_VAR,
    STATE_DIR_ENV_VAR,
    ProjectRootNotFoundError,
    StateDirOutOfRootError,
    get_state_dir,
    resolve_project_root,
)
from groundtruth_kb.bridge.registry import (
    HARNESS_KINDS,
    REGISTRY_SCHEMA_VERSION,
    REGISTRY_SUBDIR,
    HarnessRegistration,
    list_all_registrations,
    register_harness,
)
from groundtruth_kb.bridge.routing import (
    BridgeAgent,
    RoutedTransition,
    TransitionOutcome,
    route_transitions,
    synthesize_bootstrap_outcomes,
)
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
    # paths (smart-poller P1)
    "GROUNDTRUTH_MARKER",
    "PROJECT_ROOT_ENV_VAR",
    "STATE_DIR_ENV_VAR",
    "ProjectRootNotFoundError",
    "StateDirOutOfRootError",
    "get_state_dir",
    "resolve_project_root",
    # detector (smart-poller P1)
    "BridgeDocument",
    "BridgeStatus",
    "BridgeVersion",
    "ParseError",
    "ParseResult",
    "ParseWarning",
    "parse_index",
    # checkpoint (smart-poller P1)
    "CHECKPOINT_FILENAME",
    "CHECKPOINT_SCHEMA_VERSION",
    "Checkpoint",
    "CheckpointEntry",
    "CheckpointLoadResult",
    "Transition",
    "diff_against_checkpoint",
    "load_checkpoint",
    "write_checkpoint",
    # routing (smart-poller P1)
    "BridgeAgent",
    "RoutedTransition",
    "TransitionOutcome",
    "route_transitions",
    "synthesize_bootstrap_outcomes",
    # audit (smart-poller P1)
    "AUDIT_FILENAME",
    "AuditEvent",
    "emit_audit_event",
    "emit_bootstrap_event",
    "emit_transition_event",
    "read_audit_log",
    # registry (smart-poller P2)
    "HARNESS_KINDS",
    "REGISTRY_SCHEMA_VERSION",
    "REGISTRY_SUBDIR",
    "HarnessRegistration",
    "list_all_registrations",
    "register_harness",
    # notify (smart-poller P3)
    "ACTIONABLE_STATUSES_FOR_CODEX",
    "ACTIONABLE_STATUSES_FOR_PRIME",
    "NOTIFY_SCHEMA_VERSION",
    "NOTIFY_SUBDIR",
    "ActionablePending",
    "NotificationArtifact",
    "clear_notification",
    "compute_actionable_pending",
    "read_notification",
    "update_notification",
    # legacy runtime
    "Agent",
    "PeerAgent",
    "get_bridge_db",
    "list_inbox",
    "resolve_message",
    "retry_pending_message",
    "send_message",
    "wait_for_notifications",
    # legacy worker
    "resident_worker_is_healthy",
    "resident_worker_health_snapshot",
    "resident_worker_should_defer",
    "run_worker",
    # legacy handshake
    "run_handshake",
]
