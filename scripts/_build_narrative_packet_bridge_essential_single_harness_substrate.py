"""Build the narrative-artifact-approval packet for IP-7 of
bridge/gtkb-single-harness-bridge-dispatcher-slice-2-005.md (Codex GO at -006):
``.claude/rules/bridge-essential.md`` amendment adding the single-harness
bridge dispatcher as a recognized second live substrate.

This script:
1. Reads the current `.claude/rules/bridge-essential.md`.
2. Inserts the new "Dual-Substrate Coexistence" subsection between the
   existing "Bridge Dispatch Enablement Contract" section and the
   "Two-Axis Bridge Automation Model" section.
3. Computes SHA256 of the full new content.
4. Writes the packet JSON to `.groundtruth/formal-artifact-approvals/`.
5. Applies the edit by writing the new full content to the rule file.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

TARGET = Path(".claude/rules/bridge-essential.md")
PACKET_PATH = Path(".groundtruth/formal-artifact-approvals/2026-05-12-claude-rules-bridge-essential-md-single-harness-dispatcher-substrate.json")

# Insertion marker — the new subsection goes immediately BEFORE this line.
INSERT_BEFORE_MARKER = "## Two-Axis Bridge Automation Model\n"

# New subsection text. Per IP-7 of bridge slice-2-005 + Codex GO at -006.
NEW_SUBSECTION = """## Dual-Substrate Coexistence (Slice 2 of single-harness-bridge-dispatcher)

The bridge protocol has TWO live dispatch substrates as of Slice 2 of
``gtkb-single-harness-bridge-dispatcher-slice-2`` (Codex GO at ``-006``):

1. **Cross-harness event-driven trigger** (multi-harness topology) —
   ``scripts/cross_harness_bridge_trigger.py`` registered as PostToolUse
   and Stop hooks in ``.claude/settings.json`` and ``.codex/hooks.json``.
   Fires on tool-use and Stop events. Applicable when the role map records
   two harness IDs with singleton role-sets.
2. **Single-harness bridge dispatcher** (single-harness topology) —
   ``scripts/single_harness_bridge_dispatcher.py`` invoked by a Windows
   scheduled task ``GTKB-SingleHarnessBridgeDispatcher`` on a fixed
   interval (default 5 minutes; per
   ``DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`` § Platform Bindings).
   Applicable when the role map records one harness ID with a multi-element
   role-set ``["prime-builder", "loyal-opposition"]`` per
   ``ADR-SINGLE-HARNESS-OPERATING-MODE-001``.

Both substrates honor the same actionable-signature scheme (byte-identical
``_signature`` computation), the same active-session-suppression contract
(per ``bridge/gtkb-cross-harness-trigger-active-session-suppression-001-008.md``
VERIFIED), and the same fire-and-forget audit-log discipline
(``.gtkb-state/bridge-poller/dispatch-failures.jsonl``).

They are **mutually exclusive at runtime**:

- In multi-harness topology: the cross-harness trigger is the active
  substrate; the single-harness dispatcher's applicability check returns
  False and the scheduled task no-ops.
- In single-harness topology: the cross-harness trigger's topology gate
  (per IP-8 of the slice-2 thread) inerts it with SPEC-required durable
  audit evidence (per-role entries in ``dispatch-failures.jsonl`` plus
  per-recipient ``last_result = "single_harness_topology_not_applicable"``
  records in ``dispatch-state.json``); the single-harness dispatcher
  performs in-process dispatch.

Substrate applicability is determined by the role-set topology in
``harness-state/role-assignments.json``. The doctor's
``_check_role_set_topology_consistency`` (Slice 1) validates wire form;
``_check_single_harness_dispatcher_when_required`` (Slice 1 + Slice 2
upgrade) reports applicability and registration health. Per
``DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`` § Doctor Check, missing-
task severity is WARN (not FAIL) so manual-trigger fallback remains
viable while the task is being installed.

Do NOT create additional bridge automation substrates without an
owner-approved bridge proposal and an updated classification under § Two-
Axis Bridge Automation Model below.

"""


def build_new_content() -> str:
    current = TARGET.read_text(encoding="utf-8")
    if INSERT_BEFORE_MARKER not in current:
        raise SystemExit(
            f"Insertion marker {INSERT_BEFORE_MARKER!r} not found in {TARGET}. "
            "File structure has drifted; update INSERT_BEFORE_MARKER."
        )
    idx = current.index(INSERT_BEFORE_MARKER)
    return current[:idx] + NEW_SUBSECTION + current[idx:]


def main() -> None:
    new_content = build_new_content()
    PACKET_PATH.parent.mkdir(parents=True, exist_ok=True)
    packet = {
        "artifact_type": "narrative_artifact",
        "artifact_id": "claude-rules-bridge-essential-md-single-harness-dispatcher-substrate",
        "action": "insert-section",
        "target_path": ".claude/rules/bridge-essential.md",
        "source_ref": "bridge:gtkb-single-harness-bridge-dispatcher-slice-2-005:IP-7",
        "full_content": new_content,
        "full_content_sha256": hashlib.sha256(new_content.encode("utf-8")).hexdigest(),
        "approval_mode": "auto",
        "auto_approval_scope": "gtkb-single-harness-bridge-dispatcher-slice-2-ip-7-bridge-essential-amendment",
        "auto_approval_activated_by": "owner",
        "presented_to_user": True,
        "transcript_captured": True,
        "explicit_change_request": (
            "Implement IP-7 of bridge/gtkb-single-harness-bridge-dispatcher-slice-2-005.md "
            "(Codex GO at -006): insert a new 'Dual-Substrate Coexistence' subsection into "
            ".claude/rules/bridge-essential.md, immediately before the '## Two-Axis Bridge "
            "Automation Model' section. The amendment identifies the single-harness bridge "
            "dispatcher (Slice 2) as the second live dispatch substrate alongside the "
            "cross-harness event-driven trigger, documents their mutual exclusivity at "
            "runtime, and cites the topology gate (IP-8) + doctor check (IP-4) as the "
            "enforcement mechanisms."
        ),
        "changed_by": "prime-builder/claude-opus",
        "change_reason": (
            "IP-7 of gtkb-single-harness-bridge-dispatcher-slice-2 (Codex GO at -006). Adds the "
            "single-harness bridge dispatcher as a recognized second live substrate in the "
            "bridge-dispatch enablement contract per ADR-SINGLE-HARNESS-OPERATING-MODE-001 + "
            "SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 + DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001."
        ),
    }
    PACKET_PATH.write_text(json.dumps(packet, indent=2), encoding="utf-8")
    print(f"wrote packet: {PACKET_PATH}")
    print(f"sha256: {packet['full_content_sha256']}")
    TARGET.write_text(new_content, encoding="utf-8")
    print(f"applied edit: {TARGET}")


if __name__ == "__main__":
    main()
