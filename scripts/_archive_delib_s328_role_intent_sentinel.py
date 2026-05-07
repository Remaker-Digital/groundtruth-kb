# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Archive DELIB-S328-ROLE-INTENT-SENTINEL-OWNER-DIRECTIVE.

Owner directive (S328, 2026-05-02): add a non-authoritative role-intent
sentinel to the top of bridge/INDEX.md as a checksum mirror of the
canonical harness-state/<harness>/operating-role.md durable records.
Captured per owner AskUserQuestion answer "Backlog row + DELIB capture
(Recommended)" and the work_list backlog row added in the same session
turn.

Run: python scripts/_archive_delib_s328_role_intent_sentinel.py \\
       --formal-approval-packet \\
       .groundtruth/formal-artifact-approvals/2026-05-02-role-intent-sentinel-delib.json
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402
from scripts._kb_attribution import resolve_changed_by  # noqa: E402

DELIB_ID = "DELIB-S328-ROLE-INTENT-SENTINEL-OWNER-DIRECTIVE"

CONTENT = """## Owner directive (S328, 2026-05-02) — verbatim:

> The current design has two separate authorities:
>
> Role authority: harness-state/codex/operating-role.md, harness-state/claude/operating-role.md, fallback .claude/rules/operating-role.md
> Bridge workflow authority: bridge/INDEX.md
> Putting harness mode in the top of bridge/INDEX.md would have caught this exact failure faster, because every startup already reads the live bridge index. But if that line is treated as the source of truth, it creates a second mutable authority and invites drift.
>
> Recommended form:
>
> # Bridge Index
>
> <!-- Harness operating-role sentinel. Non-authoritative mirror; startup must verify against source files. -->
> <!-- Codex intended role: loyal-opposition; source: harness-state/codex/operating-role.md -->
> <!-- Claude intended role: prime-builder; source: harness-state/claude/operating-role.md -->
> Mechanical check should then enforce:
>
> Read bridge/INDEX.md sentinel.
> Read both harness-local role files.
> Fail startup if the sentinel disagrees with either source file.
> Require the disclosure to say which source was used.
> Never allow the sentinel to override the harness-local durable record.
> Risk if implemented poorly: the bridge index becomes overloaded as both queue and role-control plane, and agents may start trusting a stale header over the actual role file.
>
> Best version: use the top of bridge/INDEX.md as a shared, highly visible role-intent checksum, not as the canonical role record. This would directly reduce the role-confusion failure we just hit without weakening the existing durable-record model.

## Triggering incident

S328 session-open: owner sent "You are Prime Builder. Please confirm." Prime Builder confirmed by reading harness-state/claude/operating-role.md (the canonical durable record) but had not proactively cited the role + source in the session-open orient. The owner had to ask. The proposal addresses the latency between role-mismatch and detection: if the sentinel had been present in bridge/INDEX.md (which Prime Builder already reads at startup per CLAUDE.md "Session Start: Bridge Index Scan"), a sentinel-vs-canonical comparison would have surfaced the role intent automatically.

## Design pattern

The proposal is a **checksum sentinel** pattern: a highly-visible, non-authoritative mirror of canonical state placed where every reader already passes through, with mechanical verification that the mirror agrees with the source. Distributed systems use this pattern for similar drift-detection (e.g., DNS SOA serial mirrored at the top of every record). Load-bearing rule: rule 5 ("Never allow the sentinel to override the harness-local durable record") — without it, the sentinel becomes a competing authority and invites the exact drift the proposal identifies as "Risk if implemented poorly."

## Owner-stated 5-rule contract (verbatim from directive)

1. Read bridge/INDEX.md sentinel.
2. Read both harness-local role files.
3. Fail startup if the sentinel disagrees with either source file.
4. Require the disclosure to say which source was used.
5. Never allow the sentinel to override the harness-local durable record.

## Disposition

Per AskUserQuestion answer at S328 ("Backlog row + DELIB capture (Recommended)"):

- This DELIB captures the directive verbatim with framing.
- A new row is added to memory/work_list.md citing this DELIB and the proposal text.
- Implementation is **deferred under feature freeze** per memory/work_list.md TOP directive: "No new governance scope work until ISOLATION-017 Slice 8 VERIFIED." This proposal is governance-scope work (role-control plane + startup contract).
- No spec promotion at archive time. Spec promotion (e.g., a new GOV/DCL pair governing the sentinel contract) requires owner-visible approval per GOV-CHAT-DERIVED-SPEC-APPROVAL-001 at the time of implementation-bridge filing.

## Sequencing

Implementable post-ISOLATION-017 Slice 8 VERIFIED unless the owner elevates above the freeze. When elevated or unblocked:

1. File scoping bridge `bridge/gtkb-bridge-index-role-intent-sentinel-NNN.md` proposing the sentinel contract + 5-rule mechanical check + verification of the rule-5 invariant + tests covering disagreement-fails-startup and sentinel-cannot-override-canonical.
2. Slice 1: sentinel HTML-comment block at top of bridge/INDEX.md + manual maintenance contract documented in CLAUDE.md "Session Start" section.
3. Slice 2: mechanical startup check in scripts/session_self_initialization.py reading sentinel + both canonical files + failing-loud on disagreement; emit cited-source line in disclosure.
4. Slice 3: doctor check `_check_bridge_index_role_sentinel` for ongoing drift detection; integrate into release-readiness.

## Related artifacts at archive time

- harness-state/claude/operating-role.md — canonical Claude harness role record (verified live at S328 archive: active_role: prime-builder).
- harness-state/codex/operating-role.md — canonical Codex harness role record (parallel authority).
- .claude/rules/operating-role.md — fallback default per current contract.
- .claude/rules/prime-builder-role.md — Prime Builder profile referenced when active_role=prime-builder.
- .claude/rules/loyal-opposition.md — Loyal Opposition profile referenced when active_role=loyal-opposition.
- bridge/INDEX.md — bridge workflow authority; proposed sentinel host.
- scripts/session_self_initialization.py — current startup orient surface; future host of mechanical check.
- CLAUDE.md "Session Start: Bridge Index Scan" — current contract that already requires reading bridge/INDEX.md at session start (the affordance the proposal builds on).

## Memory pointer

Captured to auto-memory at session-end as part of the standard wrap (no new feedback file inferred from this single directive; the design pattern is captured in this DELIB body for retrieval).
"""

SUMMARY = (
    "S328 owner directive proposing a non-authoritative role-intent sentinel "
    "at the top of bridge/INDEX.md with a 5-rule mechanical-check contract. "
    "Triggered by an S328 session-open role-confusion latency: Prime Builder "
    "confirmed Prime role only after owner asked, despite the canonical record "
    "being durable in harness-state/claude/operating-role.md. Proposed pattern "
    "is a checksum sentinel — mirror of canonical state placed at a high-traffic "
    "read point with mechanical agree-or-fail verification. Load-bearing rule 5: "
    "the sentinel must never override the harness-local durable record. "
    "Captured per owner AskUserQuestion 'Backlog row + DELIB capture'; "
    "implementation deferred under ISOLATION-017 Slice 8 freeze unless elevated."
)


def main() -> int:
    db = KnowledgeDB(REPO_ROOT / "groundtruth.db")

    result = db.insert_deliberation(
        id=DELIB_ID,
        source_type="owner_conversation",
        title="S328 owner directive: bridge/INDEX.md role-intent sentinel for startup role-confusion drift detection",
        summary=SUMMARY,
        content=CONTENT,
        changed_by=resolve_changed_by(),
        change_reason=(
            "Archive S328 owner directive proposing role-intent sentinel pattern "
            "for bridge/INDEX.md. Capture mode chosen by owner via AskUserQuestion: "
            "Backlog row + DELIB capture. Implementation deferred under "
            "ISOLATION-017 freeze. No spec promotion at archive time."
        ),
        outcome="owner_decision",
        session_id="S328",
        source_ref="owner_conversation:2026-05-02-S328-role-intent-sentinel-directive",
    )
    delib_id = result.get("id") if result else DELIB_ID
    version = result.get("version") if result else "?"
    print(f"insert_deliberation id={delib_id} version={version}", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
