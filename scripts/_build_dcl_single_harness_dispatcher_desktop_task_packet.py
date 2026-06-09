"""Build the DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 formal-artifact-approval packet.

One-shot script. Auto-approval mode per AUQ S343 2026-05-12 (scope:
gtkb-single-harness-bridge-dispatcher-001-slice-1-all-five-packets).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

DCL_BODY = (
    "DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 - Single-Harness Dispatcher Wake Substrate Constraint\n"
    "\n"
    "Status: specified.\n"
    "\n"
    "Constraint:\n"
    "\n"
    "The single-harness bridge dispatcher's wake mechanism MUST be a host-platform scheduled task surface, "
    "NOT an in-process timer, daemon, or interactive-session-spawned background loop. The constraint binds "
    "the substrate independent of the dispatcher's behavior contract (which is specified by "
    "SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001).\n"
    "\n"
    "Platform Bindings:\n"
    "\n"
    "- Windows (primary): the dispatcher is woken by a Windows Task Scheduler registered task. The task name "
    "is GTKB-SingleHarnessBridgeDispatcher; the trigger is a fixed-interval schedule (default 5 minutes; "
    "configurable per installation). The task runs a non-interactive Python invocation of the dispatcher "
    "script with CREATE_NO_WINDOW so it does not surface a console window. The task's working directory is "
    "the GT-KB project root.\n"
    "- macOS: launchd plist with StartInterval=300 (5 minutes default).\n"
    "- Linux: systemd timer + service unit, OR cron entry with */5 minute schedule.\n"
    "\n"
    "Rationale:\n"
    "\n"
    "1. Token cost: a host-platform scheduled task does not consume interactive-session tokens; it runs "
    "fire-and-forget from the OS. This contrasts with the retired smart-poller (Slice 4 retirement, 2026-05-09) "
    "where the in-session CronCreate path drove a 10x token-cost regression at scale.\n"
    "2. Isolation: a Desktop scheduled task survives interactive-session termination, IDE restart, and "
    "OS user logout-login cycles within the same OS session-state.\n"
    "3. Liveness visibility: the OS scheduled-task surface provides a separately-inspectable liveness "
    "indicator independent of any GT-KB-internal log surface, addressing the failure-mode class "
    "called out in PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001 (where a daemon ran with dispatch "
    "disabled for 8 hours undetected because the only liveness surface was the same daemon's own log).\n"
    "4. Owner control: scheduled tasks can be enabled, disabled, or removed by the owner through OS-native "
    "tools without modifying GT-KB code or restarting any GT-KB component.\n"
    "\n"
    "Excluded Substrates:\n"
    "\n"
    "The following substrates are NOT permitted under this constraint:\n"
    "\n"
    "- In-process timer threads spawned by an interactive harness session. Excluded because the dispatcher "
    "stops when the interactive session exits; this defeats the single-harness operating mode whenever the "
    "owner is between sessions.\n"
    "- Spawned long-lived daemons started by harness lifecycle hooks. Excluded for the same reason as "
    "the retired smart-poller class.\n"
    "- HTTP webhook listeners or message-bus subscribers. Excluded as out-of-scope substrate complexity for "
    "this Slice; future amendment may add network substrates if owner approval is recorded.\n"
    "\n"
    "Installation:\n"
    "\n"
    "The Slice 2 dispatcher implementation (separate bridge thread; not in scope here) registers the "
    "scheduled task as part of 'gt platform doctor --apply' or an equivalent installer command, citing this "
    "constraint as authority. The installer MUST be idempotent (re-registering the task does not create "
    "duplicate triggers) and MUST honor the same .gtkb-state/bridge-poller path conventions used by the "
    "cross-harness event-driven trigger.\n"
    "\n"
    "Configuration:\n"
    "\n"
    "- Wake interval: default 5 minutes; configurable via task definition without code change.\n"
    "- Lock file path: .gtkb-state/bridge-poller/dispatcher.lock (sanity TTL "
    "GTKB_ACTIVE_SESSION_SANITY_TTL_SECONDS, default 120 s).\n"
    "- Dispatch state path: .gtkb-state/bridge-poller/dispatch-state.json (reused with the cross-harness "
    "trigger).\n"
    "- Failures log: .gtkb-state/bridge-poller/dispatch-failures.jsonl (reused with the cross-harness trigger).\n"
    "\n"
    "Doctor Check:\n"
    "\n"
    "_check_single_harness_dispatcher_when_required validates: when the active harness role-set is "
    "multi-element (single-harness mode applicable), the scheduled task is registered on the host platform "
    "and its last-run-time is within the configured interval + sanity TTL. Failure mode WARN if applicable + "
    "missing; PASS if applicable + present (or not applicable + absent).\n"
    "\n"
    "Cited Specs:\n"
    "\n"
    "- ADR-SINGLE-HARNESS-OPERATING-MODE-001 - the operating-mode topology decision that motivates this "
    "substrate constraint.\n"
    "- SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 - the behavior contract this constraint binds to a substrate.\n"
    "- PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001 - the incident class informing the substrate choice "
    "(liveness visibility outside the dispatcher's own log surface).\n"
    "- ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 - mechanism-agnostic dispatch-on-actionable-change semantic; "
    "this DCL specifies the substrate choice for single-harness mode within that envelope.\n"
    "\n"
    "Implementation Source: bridge/gtkb-single-harness-bridge-dispatcher-001-013.md (REVISED-6, Codex GO at -014).\n"
)

PACKET = {
    "artifact_type": "design_constraint",
    "artifact_id": "DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001",
    "action": "insert",
    "source_ref": "bridge:gtkb-single-harness-bridge-dispatcher-001-013:IP-3",
    "full_content": DCL_BODY,
    "full_content_sha256": hashlib.sha256(DCL_BODY.encode("utf-8")).hexdigest(),
    "approval_mode": "auto",
    "auto_approval_scope": "gtkb-single-harness-bridge-dispatcher-001-slice-1-all-five-packets",
    "auto_approval_activated_by": "owner",
    "presented_to_user": True,
    "transcript_captured": True,
    "explicit_change_request": (
        "Implement IP-3 of bridge/gtkb-single-harness-bridge-dispatcher-001-013.md (REVISED-6, Codex GO at -014): "
        "insert DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 into MemBase as type='design_constraint' with "
        "status='specified' to bind the single-harness dispatcher's wake mechanism to a host-platform scheduled "
        "task substrate."
    ),
    "changed_by": "prime-builder/claude-opus",
    "change_reason": (
        "IP-3 of gtkb-single-harness-bridge-dispatcher-001 (Codex GO at -014). Records the substrate constraint "
        "binding the single-harness dispatcher's wake mechanism to host-platform scheduled tasks (Windows Task "
        "Scheduler / launchd / cron). Companion to ADR-SINGLE-HARNESS-OPERATING-MODE-001 and "
        "SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001."
    ),
}


def main() -> None:
    out_path = Path(
        ".groundtruth/formal-artifact-approvals/2026-05-12-dcl-single-harness-dispatcher-desktop-task-001.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(PACKET, indent=2), encoding="utf-8")
    print(f"wrote packet: {out_path}")
    print(f"sha256: {PACKET['full_content_sha256']}")


if __name__ == "__main__":
    main()
