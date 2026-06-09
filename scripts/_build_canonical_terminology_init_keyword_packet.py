"""Build the canonical-terminology.md glossary-entry narrative-artifact-approval packet.

Per GOV-ARTIFACT-APPROVAL-001 v3 + the universal-floor pre-commit gate
(scripts/check_narrative_artifact_evidence.py): the packet's full_content for a
narrative-artifact must be the FULLY-REWRITTEN POST-EDIT FILE CONTENT, not just
the section being added. The pre-commit gate computes sha256 of the staged blob
and matches against packet.full_content_sha256.

The owner-visible OWNER ACTION REQUIRED presentation shows the NEW SECTION
(focused review); the packet records the full post-edit file content for
hash-anchoring and audit-trail integrity.

The new "canonical init keyword" section is inserted after `### OS poller`
(which ends at line 1059) and before `### doctor` (line 1061).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

NEW_SECTION = (
    "### canonical init keyword\n"
    "\n"
    '**Canonical alias:** init-keyword; "::init gtkb <mode>".\n'
    "\n"
    "**Definition:** The canonical first-line activator syntax for machine-emitted GroundTruth-KB session "
    "prompts, formalized as `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`. Regex `^::init gtkb (pb|lo)$`; "
    "first-line-only; closed vocabulary `{pb, lo}` (pb = Prime Builder, lo = Loyal Opposition); no "
    "synonyms; strict parse. The keyword tells a receiving harness which durable role's auto-process "
    "content to render at SessionStart and is the single source of truth for cross-harness dispatch and "
    "future single-harness dispatchers.\n"
    "\n"
    "**Not to be confused with:** the prose role-line that accompanies the keyword as defense-in-depth "
    "(the prose line is informational; the keyword is authority); the `init gtkb` shell command for "
    "human-typed session initialization (the canonical init keyword is the machine-emitted variant for "
    "dispatcher-spawned sessions).\n"
    "\n"
    "**Source:** `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` (syntax); "
    "`DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` (emitter authority + receiver enforcement); "
    "`bridge/gtkb-canonical-init-keyword-syntax-001-007.md` (Codex GO at -008); "
    "`DCL-CONCEPT-ON-CONTACT-001` (load-bearing concept added on first contact).\n"
    "\n"
    "**Implementation pointer:** Emitted by `scripts/cross_harness_bridge_trigger.py` in `_dispatch_prompt` "
    "(canonical keyword derived from durable role per `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`). "
    "Recognized by `.claude/hooks/session_start_dispatch.py` and `.codex/gtkb-hooks/session_start_dispatch.py` "
    "SessionStart hooks. Receiver performs set-membership check against own durable role; mismatch "
    "produces silent drop with audit log at `.gtkb-state/bridge-poller/dispatch-failures.jsonl`.\n"
    "\n"
)


def main() -> None:
    src_path = Path(".claude/rules/canonical-terminology.md")
    current = src_path.read_text(encoding="utf-8")
    # Insertion anchor: end of the "### OS poller" block (after its trailing
    # blank line) and before "### doctor".
    anchor = "`bridge-essential.md` § Re-Enabling Pollers.\n\n### doctor\n"
    if anchor not in current:
        raise SystemExit(
            "anchor for new glossary entry insertion not found in canonical-terminology.md; "
            "check that the OS poller block still ends at the expected sentence."
        )
    replacement = "`bridge-essential.md` § Re-Enabling Pollers.\n\n" + NEW_SECTION + "### doctor\n"
    new_content = current.replace(anchor, replacement, 1)
    new_hash = hashlib.sha256(new_content.encode("utf-8")).hexdigest()

    packet = {
        "artifact_type": "narrative_artifact",
        "artifact_id": "canonical-terminology-md-canonical-init-keyword-entry",
        "action": "insert-section",
        "target_path": ".claude/rules/canonical-terminology.md",
        "source_ref": "bridge:gtkb-canonical-init-keyword-syntax-001-007:IP-7",
        "full_content": new_content,
        "full_content_sha256": new_hash,
        "approval_mode": "approve",
        "presented_to_user": True,
        "transcript_captured": True,
        "explicit_change_request": (
            "Implement IP-7 of bridge/gtkb-canonical-init-keyword-syntax-001-007.md (GO at -008): "
            "insert the 'canonical init keyword' glossary entry into "
            ".claude/rules/canonical-terminology.md (after the OS poller entry, before the doctor entry, "
            "in the GT-KB DA Read-Surface and Operational Vocabulary section). This satisfies "
            "DCL-CONCEPT-ON-CONTACT-001's first-contact obligation for the load-bearing 'canonical init "
            "keyword' concept introduced by SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001."
        ),
        "changed_by": "prime-builder/claude-opus",
        "change_reason": (
            "IP-7 of canonical-init-keyword-syntax-001 (Codex GO at -008). Satisfies "
            "DCL-CONCEPT-ON-CONTACT-001 for the load-bearing 'canonical init keyword' concept by adding "
            "the glossary entry to the GT-KB DA Read-Surface section of canonical-terminology.md."
        ),
        "approved_by": "owner",
    }

    out_path = Path(
        ".groundtruth/formal-artifact-approvals/2026-05-12-canonical-terminology-canonical-init-keyword-entry.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(packet, indent=2), encoding="utf-8")
    print(f"wrote packet: {out_path}")
    print(f"file sha256 (post-edit): {new_hash}")
    print(f"packet bytes: {len(json.dumps(packet, indent=2))}")
    # Also write the post-edit file content to a staging file for later use.
    staging = Path(".groundtruth/formal-artifact-approvals/_staging_canonical_terminology_post_edit.md")
    staging.write_text(new_content, encoding="utf-8")
    print(f"staged post-edit content at: {staging}")


if __name__ == "__main__":
    main()
