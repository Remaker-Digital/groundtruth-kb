"""Build the ADR-SINGLE-HARNESS-OPERATING-MODE-001 formal-artifact-approval packet.

One-shot script. Auto-approval mode per AUQ S343 2026-05-12 (scope:
gtkb-single-harness-bridge-dispatcher-001-slice-1-all-five-packets).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ADR_BODY = (
    "ADR-SINGLE-HARNESS-OPERATING-MODE-001 - GT-KB Operating Mode Topology: Single-Harness And Multi-Harness Both First-Class\n"
    "\n"
    "Status: specified.\n"
    "\n"
    "Context:\n"
    "\n"
    "Prior GT-KB implementation assumed a multi-harness deployment: a Prime Builder harness (Claude Code) and "
    "a Loyal Opposition harness (Codex) installed side-by-side, coordinating through the file-bridge. Bridge "
    "dispatch was provided by the cross-harness event-driven trigger (scripts/cross_harness_bridge_trigger.py) "
    "registered as PostToolUse and Stop hooks on both harnesses. The runtime role-record schema treated each "
    "harness ID's role as a scalar value drawn from {prime-builder, loyal-opposition}.\n"
    "\n"
    "Owner directive (S341) established that single-harness operation must be supported as a first-class GT-KB "
    "deployment topology, in both directions (Claude-only and Codex-only). In single-harness mode the bridge "
    "dispatch path that depends on a counterpart harness is non-applicable, and the active harness must absorb "
    "both Prime Builder and Loyal Opposition responsibilities through an in-process dispatcher.\n"
    "\n"
    "Decision:\n"
    "\n"
    "GT-KB supports BOTH single-harness and multi-harness operating-mode topologies as first-class architecture "
    "topologies. Neither is a degradation of the other; both are governed-supported deployment paths with "
    "distinct dispatch substrates:\n"
    "\n"
    "- Multi-harness (current default): harness A and harness B installed with singleton role sets; "
    "cross-harness event-driven trigger active; single-harness dispatcher NOT active.\n"
    "- Single-harness (first-class): single harness installed with multi-element role set "
    "{prime-builder, loyal-opposition}; cross-harness trigger registered but spawns nothing (no counterpart); "
    "single-harness dispatcher active via Desktop scheduled task (per DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001).\n"
    "\n"
    "Role records (harness-state/role-assignments.json) carry role as a JSON list (the wire representation of a "
    "role set) drawn from {prime-builder, loyal-opposition}. Singleton lists represent the multi-harness case; "
    "multi-element lists represent the single-harness case. Readers normalize legacy scalar values into "
    "singleton sets via _normalize_role_field. Writers always emit list form.\n"
    "\n"
    "Failed Approaches:\n"
    "\n"
    "1. Hardcoding 'claude' or 'codex' as recipient throughout the trigger code (pre-DispatchTarget). Tied the "
    "dispatch path to specific vendor names; collapsed under owner role-switch operations.\n"
    "2. Treating single-harness as a degraded fallback (e.g., 'when no counterpart, error out'). Failed because "
    "owner-directed single-harness operation is a primary use case, not an exception.\n"
    "3. Carrying scalar role schema forward while teaching readers to interpret strings as 'multi-role markers' "
    "(e.g., 'prime-builder+loyal-opposition' as a string). Failed validation against the helper-API ergonomics "
    "test and lost set-semantic guarantees.\n"
    "\n"
    "Rejected Alternatives:\n"
    "\n"
    "1. Path 1 (governance-scaffolding-only Slice 1): land operating-role.md amendment and ADR/SPEC/DCL "
    "MemBase rows in Slice 1, defer runtime reader/writer migration to a future Slice 2. REJECTED per "
    "DELIB-1511 and Codex NO-GO at -006: would leave runtime scalar readers honoring a different schema than "
    "the governance text claims, producing rule/runtime divergence and silent drift.\n"
    "2. Path 3 (pure scaffolding without runtime migration ever): leave runtime forever scalar; treat role-set "
    "as future-design only. REJECTED: would defeat the single-harness operating mode at the runtime level.\n"
    "3. Coupling single-harness dispatch to the retired smart-poller substrate. REJECTED: the smart-poller was "
    "retired in Slice 4 (2026-05-09) and the cross-harness event-driven trigger is the live multi-harness "
    "substrate; a separate Desktop-task substrate is the parsimonious choice for single-harness.\n"
    "\n"
    "Consequences:\n"
    "\n"
    "Architecture changes:\n"
    "\n"
    "- Role-set schema is the active runtime schema (Path 2 atomic migration per Codex NO-GO at -006 + "
    "owner answer S341).\n"
    "- harness-state/role-assignments.json wire format is list-of-strings drawn from "
    "{prime-builder, loyal-opposition}.\n"
    "- Runtime helpers: _normalize_role_field, _role_set_to_json, is_prime_builder, is_loyal_opposition in "
    "scripts/harness_roles.py.\n"
    "- Reader call sites in scripts/harness_roles.py, scripts/_kb_attribution.py, scripts/workstream_focus.py, "
    "scripts/session_self_initialization.py, scripts/cross_harness_bridge_trigger.py migrate from scalar "
    "equality to set-membership semantics.\n"
    "- Writer call sites always emit list form.\n"
    "- Legacy scalar values are accepted on READ and upgraded to list form on first WRITE (one-shot migration).\n"
    "- Compatibility/provenance value 'acting-prime-builder' is accepted on READ (legacy compatibility) but "
    "rejected on SET (per ADR-ACTING-PRIME-BUILDER-CLASSIFICATION-001).\n"
    "\n"
    "Dispatch substrates:\n"
    "\n"
    "- Multi-harness: cross-harness event-driven trigger (existing, unchanged).\n"
    "- Single-harness: Desktop scheduled task dispatcher (per DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 + "
    "SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001).\n"
    "\n"
    "Doctor checks:\n"
    "\n"
    "- _check_role_set_topology_consistency: verifies role-record list form, valid role tokens, no "
    "duplicates; surfaces drift.\n"
    "- _check_single_harness_dispatcher_when_required: when only one harness identity is present, verifies "
    "the single-harness dispatcher is registered.\n"
    "\n"
    "Spec Linkage:\n"
    "\n"
    "- GOV-HARNESS-ROLE-PORTABILITY-001 - preserved by both topologies; role attaches to harness ID via the "
    "two-step authority chain regardless of singleton vs multi-element set.\n"
    "- GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001 - preserved; multi-harness install configures both capable "
    "harnesses with singleton sets.\n"
    "- DCL-CROSS-HARNESS-ENFORCEMENT-001 - preserved; multi-harness symmetric enforcement remains.\n"
    "- SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 - both substrates emit ::init gtkb <mode> as first-line "
    "activator; the dispatcher mode is derived from set-membership in the target role.\n"
    "- DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 - receiver-side set-membership check is the same on both "
    "substrates; multi-element sets accept either mode.\n"
    "- ADR-CODEX-HOOK-PARITY-FALLBACK-001 - independent; this ADR does not change the Codex hook parity stance.\n"
    "\n"
    "Implementation Source: bridge/gtkb-single-harness-bridge-dispatcher-001-013.md (REVISED-6, Codex GO at -014).\n"
)

PACKET = {
    "artifact_type": "architecture_decision",
    "artifact_id": "ADR-SINGLE-HARNESS-OPERATING-MODE-001",
    "action": "insert",
    "source_ref": "bridge:gtkb-single-harness-bridge-dispatcher-001-013:IP-1",
    "full_content": ADR_BODY,
    "full_content_sha256": hashlib.sha256(ADR_BODY.encode("utf-8")).hexdigest(),
    "approval_mode": "auto",
    "auto_approval_scope": "gtkb-single-harness-bridge-dispatcher-001-slice-1-all-five-packets",
    "auto_approval_activated_by": "owner",
    "presented_to_user": True,
    "transcript_captured": True,
    "explicit_change_request": (
        "Implement IP-1 of bridge/gtkb-single-harness-bridge-dispatcher-001-013.md (REVISED-6, Codex GO at -014): "
        "insert ADR-SINGLE-HARNESS-OPERATING-MODE-001 into MemBase as type='architecture_decision' with "
        "status='specified' to record the decision that GT-KB supports both single-harness and multi-harness "
        "operating-mode topologies as first-class architecture topologies."
    ),
    "changed_by": "prime-builder/claude-opus",
    "change_reason": (
        "IP-1 of gtkb-single-harness-bridge-dispatcher-001 (Codex GO at -014). Records the operating-mode "
        "topology decision and the Path 2 atomic-migration consequence chain. Companion to "
        "SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 (behavior contract) and "
        "DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 (substrate constraint)."
    ),
}


def main() -> None:
    out_path = Path(".groundtruth/formal-artifact-approvals/2026-05-12-adr-single-harness-operating-mode-001.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(PACKET, indent=2), encoding="utf-8")
    print(f"wrote packet: {out_path}")
    print(f"sha256: {PACKET['full_content_sha256']}")


if __name__ == "__main__":
    main()
