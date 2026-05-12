"""Build the SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 formal-artifact-approval packet.

One-shot script. Computes SHA256, writes packet JSON. Idempotent: re-running
overwrites with the same hash if content is unchanged.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

SPEC_BODY = (
    "SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 - Canonical Init-Keyword Syntax for GroundTruth-KB Session Activation\n"
    "\n"
    "Purpose: Establish \"::init gtkb <mode>\" as the canonical first-line activator syntax for machine-emitted "
    "GroundTruth-KB session prompts. The keyword tells a receiving harness which durable role's auto-process "
    "content to render at SessionStart, and is the single source of truth for cross-harness dispatch and "
    "future single-harness dispatchers.\n"
    "\n"
    "Syntax:\n"
    "\n"
    "- Regex: ^::init gtkb (pb|lo)$\n"
    "- First-line-only: the keyword must appear as the first line of an emitted prompt; subsequent lines may "
    "carry task content (e.g., AXIS-2 surface payload, bridge dispatch context).\n"
    "- Closed vocabulary: {pb, lo}.\n"
    "  - pb = Prime Builder\n"
    "  - lo = Loyal Opposition\n"
    "- No synonyms: prime, prime-builder, loyal-opposition, lo-mode, claude-pb, codex-lo, etc. are NOT "
    "accepted as keyword modes.\n"
    "- Strict parse: any deviation from the regex fails parsing; no auto-dispatch payload is constructed by "
    "the receiver.\n"
    "\n"
    "Emission Surface:\n"
    "\n"
    "The keyword is emitted by:\n"
    "\n"
    "- scripts/cross_harness_bridge_trigger.py - cross-harness event-driven trigger; emits on actionable "
    "INDEX change when dispatching a counterpart harness.\n"
    "- Future routines and dispatchers (e.g., the single-harness bridge dispatcher when its thread is "
    "VERIFIED).\n"
    "\n"
    "The keyword MUST be derived from the durable role record per "
    "DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 (two-step lookup: role-assignments.json -> harness ID -> "
    "harness-identities.json -> command handle -> canonical mode), never hardcoded.\n"
    "\n"
    "Reception Surface:\n"
    "\n"
    "The keyword is recognized by:\n"
    "\n"
    "- .claude/hooks/session_start_dispatch.py - Claude Code SessionStart hook.\n"
    "- .codex/gtkb-hooks/session_start_dispatch.py - Codex SessionStart hook.\n"
    "\n"
    "Receivers perform set-membership check against own durable role per "
    "DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001. Mismatch produces silent drop with audit log at "
    ".gtkb-state/bridge-poller/dispatch-failures.jsonl; the prompt is not treated as a task and the session "
    "exits cleanly per the harness's normal no-work path.\n"
    "\n"
    "Status: specified.\n"
    "\n"
    "Related Specs:\n"
    "\n"
    "- DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 - emitter authority + receiver enforcement contract.\n"
    "- GOV-HARNESS-ROLE-PORTABILITY-001 - preserved by deriving keyword from durable role.\n"
    "- GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001 - resolver tracks whatever durable record says.\n"
    "- DCL-CROSS-HARNESS-ENFORCEMENT-001 - strict-ignore is symmetric across harnesses.\n"
    "- DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001 - keyword is the assertion; durable record is "
    "authority.\n"
    "\n"
    "Implementation Source: bridge/gtkb-canonical-init-keyword-syntax-001-007.md (GO at -008).\n"
)

PACKET = {
    "artifact_type": "specification",
    "artifact_id": "SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001",
    "action": "insert",
    "source_ref": "bridge:gtkb-canonical-init-keyword-syntax-001-007:IP-1",
    "full_content": SPEC_BODY,
    "full_content_sha256": hashlib.sha256(SPEC_BODY.encode("utf-8")).hexdigest(),
    "approval_mode": "approve",
    "presented_to_user": True,
    "transcript_captured": True,
    "explicit_change_request": (
        "Implement IP-1 of bridge/gtkb-canonical-init-keyword-syntax-001-007.md (GO at -008): "
        "insert SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 into MemBase as type='specification' with "
        "status='specified' to formalize the canonical init-keyword syntax for machine-emitted GroundTruth-KB "
        "session prompts."
    ),
    "changed_by": "prime-builder/claude-opus",
    "change_reason": (
        "IP-1 of canonical-init-keyword-syntax-001 (Codex GO at -008). Establishes "
        "\"::init gtkb <mode>\" as the canonical first-line activator syntax with closed vocabulary {pb, lo}, "
        "regex-strict parse, no synonyms. Prerequisite for Slice 2 of "
        "gtkb-single-harness-bridge-dispatcher-001."
    ),
    "approved_by": "owner",
}


def main() -> None:
    out_path = Path(".groundtruth/formal-artifact-approvals/2026-05-12-spec-canonical-init-keyword-syntax-001.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(PACKET, indent=2), encoding="utf-8")
    print(f"wrote packet: {out_path}")
    print(f"sha256: {PACKET['full_content_sha256']}")


if __name__ == "__main__":
    main()
