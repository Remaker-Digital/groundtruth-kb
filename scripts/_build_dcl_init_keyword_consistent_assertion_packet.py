"""Build the DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 formal-artifact-approval packet.

One-shot script. Computes SHA256, writes packet JSON.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

DCL_BODY = (
    "DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 - Init-Keyword Emitter Must Derive From Durable Records; "
    "Receiver Must Check Set-Membership Against Durable Role\n"
    "\n"
    "Purpose: Constrain how the canonical init-keyword (\"::init gtkb <mode>\" per "
    "SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001) is emitted by dispatchers and validated by receivers. The "
    "constraint preserves harness role portability (GOV-HARNESS-ROLE-PORTABILITY-001) and ensures the "
    "durable role record is the single authority, not any hardcoded identity assumption or denormalized "
    "metadata field.\n"
    "\n"
    "Emitter-Side Constraint:\n"
    "\n"
    "When emitting \"::init gtkb <mode>\", the emitter MUST resolve the keyword via a two-step lookup:\n"
    "\n"
    "1. harness-state/role-assignments.json - find the harness ID with the needed durable role.\n"
    "2. harness-state/harness-identities.json (inverted) - resolve harness ID -> harness command handle "
    "(\"claude\" or \"codex\").\n"
    "\n"
    "The role record's harness_type field is OPTIONAL drift-detection metadata, NOT authority. The emitter "
    "MUST treat any disagreement between the role record's harness_type and the identity-derived handle as "
    "a fail-closed configuration drift error.\n"
    "\n"
    "Harness-local files (harness-state/<harness>/operating-role.md) MUST NOT be used as authority sources; "
    "they are legacy pointers per .claude/rules/operating-role.md.\n"
    "\n"
    "The canonical mode emission is derived from the needed role label:\n"
    "\n"
    "- needed_role_label \"prime-builder\" -> canonical mode \"pb\"\n"
    "- needed_role_label \"loyal-opposition\" -> canonical mode \"lo\"\n"
    "\n"
    "Receiver-Side Constraint:\n"
    "\n"
    "The recipient harness's SessionStart hook MUST read its durable role from "
    "harness-state/role-assignments.json (resolving its own harness ID via "
    "harness-state/harness-identities.json). The check uses set-membership against the receiver's role set.\n"
    "\n"
    "For the current scalar-role schema, the role is treated as a singleton set ({pb} or {lo}); future "
    "role-set schemas (per gtkb-single-harness-bridge-dispatcher-001) generalize naturally to multi-element "
    "sets such as {pb, lo} for single-harness configurations.\n"
    "\n"
    "Mismatch Behavior (Strict-Ignore-on-Mismatch):\n"
    "\n"
    "If the parsed keyword mode is NOT a member of the receiver's role set, the SessionStart hook MUST "
    "silently drop the dispatch:\n"
    "\n"
    "- The SessionStart context returned to the harness DOES NOT contain the bridge auto-dispatch payload.\n"
    "- The session is NOT to treat the prompt as a task; it exits cleanly per the harness's normal "
    "\"no work to process\" path.\n"
    "- An audit-log entry is written to .gtkb-state/bridge-poller/dispatch-failures.jsonl with structured "
    "fields: run_id, expected_role_set, observed_keyword_mode, own_harness_id, timestamp.\n"
    "\n"
    "Machine-Checkable Assertions:\n"
    "\n"
    "1. grep scripts/cross_harness_bridge_trigger.py for _invert_identities and _resolve_dispatch_target - "
    "emitter-side authority chain present.\n"
    "2. grep .claude/hooks/session_start_dispatch.py and .codex/gtkb-hooks/session_start_dispatch.py for "
    "the set-membership check pattern - receiver-side enforcement present in both harnesses.\n"
    "3. grep scripts/cross_harness_bridge_trigger.py and both SessionStart hooks for "
    ".gtkb-state/bridge-poller/dispatch-failures.jsonl - audit-log path written on mismatch.\n"
    "4. grep absence of harness-state/<name>/operating-role.md reads in emitter and receiver code paths - "
    "legacy authority source NOT used.\n"
    "5. grep absence of direct role_record[\"harness_type\"] reads as command-handle authority in emitter "
    "code paths - drift-detection only, not authority.\n"
    "\n"
    "Status: specified.\n"
    "\n"
    "Related Specs:\n"
    "\n"
    "- SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 - syntax this DCL constrains.\n"
    "- GOV-HARNESS-ROLE-PORTABILITY-001 - portability preserved by durable-record authority.\n"
    "- DCL-CROSS-HARNESS-ENFORCEMENT-001 - strict-ignore is symmetric across harnesses.\n"
    "- DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001 - durable record is authority over keyword "
    "assertion.\n"
    "- PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001 - audit-log on misdirect makes silent-drop "
    "investigable.\n"
    "\n"
    "Implementation Source: bridge/gtkb-canonical-init-keyword-syntax-001-007.md (GO at -008).\n"
)

PACKET = {
    "artifact_type": "design_constraint",
    "artifact_id": "DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001",
    "action": "insert",
    "source_ref": "bridge:gtkb-canonical-init-keyword-syntax-001-007:IP-2",
    "full_content": DCL_BODY,
    "full_content_sha256": hashlib.sha256(DCL_BODY.encode("utf-8")).hexdigest(),
    "approval_mode": "approve",
    "presented_to_user": True,
    "transcript_captured": True,
    "explicit_change_request": (
        "Implement IP-2 of bridge/gtkb-canonical-init-keyword-syntax-001-007.md (GO at -008): "
        "insert DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 into MemBase as type='design_constraint' with "
        "status='specified' to formalize the emitter and receiver constraints for the canonical "
        "init-keyword."
    ),
    "changed_by": "prime-builder/claude-opus",
    "change_reason": (
        "IP-2 of canonical-init-keyword-syntax-001 (Codex GO at -008). Constrains keyword emission via "
        "two-step durable-record lookup with drift detection, and receiver-side set-membership check with "
        "strict-ignore-on-mismatch. Pairs with SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 to define the full "
        "canonical-init-keyword contract."
    ),
    "approved_by": "owner",
}


def main() -> None:
    out_path = Path(".groundtruth/formal-artifact-approvals/2026-05-12-dcl-init-keyword-consistent-assertion-001.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(PACKET, indent=2), encoding="utf-8")
    print(f"wrote packet: {out_path}")
    print(f"sha256: {PACKET['full_content_sha256']}")


if __name__ == "__main__":
    main()
