"""Build the SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 formal-artifact-approval packet.

One-shot script. Auto-approval mode per AUQ S343 2026-05-12 (scope:
gtkb-single-harness-bridge-dispatcher-001-slice-1-all-five-packets).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

SPEC_BODY = (
    "SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 - Single-Harness Bridge Dispatcher Behavior Contract\n"
    "\n"
    "Status: specified.\n"
    "\n"
    "Purpose:\n"
    "\n"
    "Specify the runtime behavior of the single-harness bridge dispatcher: the dispatch substrate that "
    "absorbs the cross-harness event-driven trigger's responsibilities when the active GT-KB installation has "
    "a single harness with a multi-element role set. The dispatcher is the canonical bridge dispatch substrate "
    "in single-harness mode per ADR-SINGLE-HARNESS-OPERATING-MODE-001.\n"
    "\n"
    "Applicability:\n"
    "\n"
    "The single-harness bridge dispatcher is active iff harness-state/harness-registry.json records a single "
    "active harness whose role-set has cardinality >= 2 (i.e., the single harness holds both prime-builder and "
    "loyal-opposition durable roles). In all other topologies the dispatcher is registered but inert; the "
    "cross-harness event-driven trigger remains the dispatch substrate for multi-harness installations.\n"
    "\n"
    "Wake Mechanism:\n"
    "\n"
    "The dispatcher is invoked by a Desktop scheduled task (per DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 "
    "for the platform-binding constraint). The scheduled task wakes the dispatcher routine on a fixed "
    "interval (default 5 minutes; configurable via task definition). Each wake invocation:\n"
    "\n"
    "1. Acquires a single-instance lock at .gtkb-state/bridge-poller/dispatcher.lock (file-existence-with-mtime "
    "freshness; sanity TTL governed by GTKB_ACTIVE_SESSION_SANITY_TTL_SECONDS, default 120 s). On stale-lock "
    "detection the lock is reclaimed.\n"
    "2. Reads live bridge/INDEX.md and computes the per-role actionable signature using the existing "
    "kind-aware routing path defined by scripts/cross_harness_bridge_trigger.py::_compute_actionable + "
    "_signature. The signature scheme is byte-identical to the cross-harness trigger's per Slice 4 D7.\n"
    "3. For each role in the active harness's role-set (typically prime-builder AND loyal-opposition in "
    "single-harness mode), compares the computed signature to .gtkb-state/bridge-poller/dispatch-state.json "
    "(per-recipient durable record). If the signature has changed and no active-session-suppression lock is "
    "held by the active harness's foreground session, the dispatcher spawns a worker.\n"
    "4. The worker is a subprocess invocation of the same harness (e.g., 'claude -p <prompt>' or "
    "'codex exec <prompt>' depending on command_handle) with the canonical init keyword '::init gtkb <mode>' "
    "as the prompt's first line and GTKB_BRIDGE_POLLER_RUN_ID + GTKB_BRIDGE_DISPATCH_KEYWORD env vars set, "
    "matching the cross-harness trigger's spawn semantics.\n"
    "5. Worker SessionStart hook reads the env vars, applies the StartupDecision enum logic from IP-4 of "
    "canonical-init-keyword-syntax-001 (set-membership check against own role-set), and either authorizes the "
    "dispatch or silently drops with audit-log per PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001.\n"
    "\n"
    "Kind-Aware Dispatchability:\n"
    "\n"
    "The dispatcher honors the existing kind-aware-routing contract from bridge "
    "gtkb-cross-harness-trigger-codex-exec-hook-firing-001:\n"
    "\n"
    "- Terminal GO entries (final GO with no follow-on expected) are NOT dispatched.\n"
    "- Terminal VERIFIED entries are NOT dispatched.\n"
    "- Non-terminal GO/NO-GO entries actionable for the prime-builder role ARE dispatched as prime-mode work.\n"
    "- Non-terminal NEW/REVISED entries actionable for the loyal-opposition role ARE dispatched as lo-mode work.\n"
    "- ADVISORY entries are NOT dispatched (non-dispatchable per file-bridge-protocol.md § Advisory Reports).\n"
    "\n"
    "Idle Suppression:\n"
    "\n"
    "When the active harness is in a foreground interactive session (active-session-suppression lock fresh per "
    "scripts/active_session_heartbeat.py), the dispatcher SHOULD NOT spawn a competing background worker for "
    "the same actionable work. Suppression is signature-aware: the suppressed signature is recorded so the "
    "dispatcher retries after the foreground session exits. The dispatcher MUST honor the existing "
    "active-session-suppression contract from bridge/gtkb-cross-harness-trigger-active-session-suppression-001-008.md.\n"
    "\n"
    "Audit Log:\n"
    "\n"
    "Dispatch failures and silent drops are appended to .gtkb-state/bridge-poller/dispatch-failures.jsonl in "
    "the same format as the cross-harness trigger's failure log per PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001.\n"
    "\n"
    "Coexistence:\n"
    "\n"
    "When both the cross-harness event-driven trigger and the single-harness dispatcher are registered:\n"
    "\n"
    "- Multi-harness topology (singleton role-sets per harness): the cross-harness trigger fires on tool-use "
    "and Stop events; the single-harness dispatcher is registered but its scheduled task is inert (its applicability "
    "check returns false because the multi-element role-set precondition is not met).\n"
    "- Single-harness topology (multi-element role-set on the active harness): the cross-harness trigger is "
    "registered but spawns nothing (no counterpart resolves; resolution fails with an audit-log entry); the "
    "single-harness dispatcher's scheduled task fires and performs in-process dispatch.\n"
    "\n"
    "The two substrates are mutually exclusive at runtime. The active substrate is determined by the role-set "
    "topology of the active harness's durable role record.\n"
    "\n"
    "Implementation Substrates:\n"
    "\n"
    "- Slice 1 (this proposal): governance scaffolding (this SPEC + ADR-SINGLE-HARNESS-OPERATING-MODE-001 + "
    "DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001) + role-set schema runtime migration (helpers + 9 reader/writer "
    "call sites + tests).\n"
    "- Slice 2 (separate thread): dispatcher script, Desktop scheduled task setup, system-interface-map entry, "
    "Slice 2 integration tests. Slice 2 is OUT OF SCOPE for this proposal.\n"
    "\n"
    "Cited Specs:\n"
    "\n"
    "- ADR-SINGLE-HARNESS-OPERATING-MODE-001 - operating-mode topology decision that motivates this dispatcher.\n"
    "- DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 - substrate (Desktop scheduled task) constraint.\n"
    "- SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 - keyword syntax the dispatcher emits.\n"
    "- DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 - emitter/receiver consistency contract.\n"
    "- PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001 - audit-log discipline on dispatch failures.\n"
    "- ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 - mechanism-agnostic dispatch-on-actionable-change semantic.\n"
    "- DCL-SMART-POLLER-AUTO-TRIGGER-001 - actionable-only spawn invariant.\n"
    "\n"
    "Implementation Source: bridge/gtkb-single-harness-bridge-dispatcher-001-013.md (REVISED-6, Codex GO at -014).\n"
)

PACKET = {
    "artifact_type": "requirement",
    "artifact_id": "SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001",
    "action": "insert",
    "source_ref": "bridge:gtkb-single-harness-bridge-dispatcher-001-013:IP-2",
    "full_content": SPEC_BODY,
    "full_content_sha256": hashlib.sha256(SPEC_BODY.encode("utf-8")).hexdigest(),
    "approval_mode": "auto",
    "auto_approval_scope": "gtkb-single-harness-bridge-dispatcher-001-slice-1-all-five-packets",
    "auto_approval_activated_by": "owner",
    "presented_to_user": True,
    "transcript_captured": True,
    "explicit_change_request": (
        "Implement IP-2 of bridge/gtkb-single-harness-bridge-dispatcher-001-013.md (REVISED-6, Codex GO at -014): "
        "insert SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 into MemBase as type='requirement' with "
        "status='specified' to specify the behavior contract of the single-harness bridge dispatcher."
    ),
    "changed_by": "prime-builder/claude-opus",
    "change_reason": (
        "IP-2 of gtkb-single-harness-bridge-dispatcher-001 (Codex GO at -014). Records the behavior contract "
        "for the dispatcher's wake, signature, kind-aware-routing, spawn, suppression, audit-log, and "
        "multi-substrate-coexistence semantics. Companion to ADR-SINGLE-HARNESS-OPERATING-MODE-001."
    ),
}


def main() -> None:
    out_path = Path(".groundtruth/formal-artifact-approvals/2026-05-12-spec-single-harness-bridge-dispatcher-001.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(PACKET, indent=2), encoding="utf-8")
    print(f"wrote packet: {out_path}")
    print(f"sha256: {PACKET['full_content_sha256']}")


if __name__ == "__main__":
    main()
