# Scope Proposal: Agent Red Session-Wrap Automation

**Status:** NEW
**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-17
**Target repo:** Agent Red (`.claude/hooks/` + `.claude/settings.json` ONLY — no GT-KB repo changes in this bridge)
**Priority:** CRITICAL — must land before S299-continuation session boundary so S300 inherits the automation.

## Problem Statement (owner directive verbatim)

Owner 2026-04-17 ~3:25 PM: "I don't want to solve session carry-forward issues with ad hoc, session-specific dialogs — I want to see solutions with hard hooks and automation that will work for future sessions. **If I have to ask this question again at the end of the next session we will have failed.**"

Specifically: the session-wrap problem class exposed this session:
1. Prime forgot to search DA before drafting `gtkb-start-here-adopter-rewrite-001.md` → MemBase governance failure.
2. Plans discussed in conversation (scope revisions, superseded approaches, AskUserQuestion outcomes) stayed in Prime's in-context memory without archive until owner asked "is everything captured?"
3. Manual DELIB-0817/0818 insertion at session boundary is exactly the ad-hoc pattern owner is rejecting.

## Why this is a separate bridge from `gtkb-da-governance-completeness-001`

The umbrella scope bridge I filed ~30 min earlier covers the **product-level** governance fix (GT-KB doctor checks, scaffold propagation, reusable backfill framework, schema rules). That's the right-sized, right-paced work for GT-KB as a product.

This bridge carves off the **three Agent-Red-specific project-local hooks** that address *this session's specific failure class* and must be in place before the next session starts. Scope is narrow: Agent Red's `.claude/hooks/` + `.claude/settings.json`. No GT-KB refactor. No template propagation in this bridge (the umbrella handles propagation later, which is correct sequencing because we need to prove the hook design works in dogfood before scaffolding to all adopters).

Relationship:
- This bridge → land in Agent Red TODAY, dogfood immediately
- Umbrella bridge → formalize into GT-KB product + templates over next several sessions, propagate to all adopters

## Scope (in) — three hooks, all Agent-Red-local

### Hook 1 — `PreToolUse` DA-search preflight (hard block)

**File:** `.claude/hooks/da-preflight-check.py`
**Trigger:** PreToolUse on `Write` tool
**Logic:**
- If `file_path` matches `**/bridge/*-001.md` (new bridge proposal) OR `**/bridge/*-*.md` with "REVISED" or "NEW" content hint:
  - Scan current turn's tool_use history for evidence of DA search:
    - Bash call containing `search_deliberations` or `deliberations search`
    - Python exec containing `db.search_deliberations` or `KnowledgeDB.*deliberations`
    - Or explicit flag `# da-search-confirmed: <reason>` in the bridge content's first 50 lines (escape hatch for edge cases with justification)
  - If no evidence: **BLOCK** with error message: `"Bridge proposal Write blocked by da-preflight-check.py. Run search_deliberations() for the target topic first, or add '# da-search-confirmed: <reason>' marker to the proposal content if search is genuinely not applicable. See .claude/rules/deliberation-protocol.md."`
- Exit 2 (blocks tool call) on failure; exit 0 on pass.

**Rationale:** Would have prevented 2026-04-17 MemBase governance failure mechanically.

### Hook 2 — `Stop` session-wrap coverage gate (LOUD)

**File:** `.claude/hooks/da-wrap-gate.py`
**Trigger:** Stop hook (fires when Claude yields back to user; we use it as a wrap signal)
- OR: SessionEnd hook if/when available; Stop is the reliable current surface.

**Logic** (runs in background so it doesn't delay response):
- Query current DA state vs session activity.
- Check coverage:
  - Every `AskUserQuestion` interaction this session → at least one DELIB with `source_type='owner_conversation'` and session_id = current.
  - Every bridge-proposal Write this session → corresponding bridge_thread DELIB exists.
  - Every LO report in `CODEX-INSIGHT-DROPBOX/` dated since session start → DELIB with matching source_ref.
- If gap found: write to `.claude/hooks/da-wrap-gate.last-alarm` with structured JSON describing the gap.
- Emit systemMessage visible to next response: `"⚠️ DA-WRAP-GATE ALARM: N items discussed this session not yet archived. See .claude/hooks/da-wrap-gate.last-alarm for details."`

**First-run behavior (tolerance):** on first few wrap runs, gap may be non-trivial (today's unarchived plans). Hook writes ALARM but does not block. After 3 consecutive ALARM runs, behavior escalates to blocking wrap-skill completion until gap closed.

**Rationale:** Would have proactively surfaced "DELIB-0817/0818 not yet filed" before owner had to ask manually.

### Hook 3 — `UserPromptSubmit` owner-decision auto-capture

**File:** `.claude/hooks/owner-decision-capture.py`
**Trigger:** UserPromptSubmit
**Logic:**
- Parse the user's prompt content.
- Detect patterns:
  - GOV-09 specification language: contains "must", "should", "needs to", "we should", numbered criteria ≥ 3 items
  - AskUserQuestion response acknowledgment: prior assistant turn had `AskUserQuestion` tool call, current prompt is interpreted as its answer
  - Direct decision language: "decision:", "I decide:", "we are going with", "approve", "reject"
- When detected: append to `.claude/hooks/owner-decision-capture.queue` a structured entry with timestamp, prompt excerpt, detected pattern.
- At session-wrap (coordinated with Hook 2), the queue is drained into DA as `source_type='owner_conversation'` DELIBs.

**Rationale:** Removes the manual "remember to insert DELIB" burden. Prime's in-context memory of decisions becomes unnecessary because the hook writes them to the archive queue in real time.

## Scope (out)

- **Transcript extraction** (deferred to umbrella — requires more careful heuristic design).
- **Redaction gates** (deferred to umbrella — schema already supports it; enforcement can follow).
- **Source-ref identity validation** (deferred to umbrella — schema-level change).
- **GT-KB template propagation** (deferred to umbrella — correct sequencing is dogfood-first).
- **Retroactive coverage sweep** (covered by in-flight `gtkb-da-harvest-coverage` bridge).

## Owner Decisions Pre-Pinned

1. Hook 1 preflight enforcement: **HARD BLOCK** (per owner AskUserQuestion 2026-04-17 ~2:40 PM).
2. Hook 3 ownership: Agent Red local; GT-KB template propagation later via umbrella.
3. Hook 2 first-run tolerance: ALARM not BLOCK for first 3 runs, escalate after (avoids immediate session-breakage).

## Prior Deliberations

- `DELIB-0715`, `DELIB-0716`, `DELIB-0717`, `DELIB-0718`, `DELIB-0719`, `DELIB-0817`, `DELIB-0818` — this session's archived plans and owner decisions.
- `bridge/gtkb-da-governance-completeness-001.md` (NEW, pending Codex) — the parallel umbrella scope for the product-level work.
- `.claude/rules/deliberation-protocol.md` — the rule that failed to mechanically enforce.
- `.claude/rules/codex-review-gate.md` — the rule that required bridge review before KB mutations.
- `.claude/rules/bridge-essential.md` — top-priority mandate; this bridge protects the MemBase/DA variant of the same class of failure.

## Implementation Approach

**Phase 1** — Draft hook scripts (three files above) on a feature branch. Unit-testable where practical; integration-testable via simulated tool calls. All three hooks are pure Python + standard library + the existing `groundtruth.db` connection pattern (`sys.path.insert(0, 'tools/knowledge-db'); from db import KnowledgeDB`).

**Phase 2** — Register hooks in `.claude/settings.json`. Hook 1 on PreToolUse(Write). Hook 2 on Stop. Hook 3 on UserPromptSubmit. All three marked required for this project.

**Phase 3** — Dogfood in this session: after landing, simulate each failure class:
- Attempt to Write a new `bridge/*-001.md` without prior DA search → expect Hook 1 BLOCK.
- At end of session, expect Hook 2 to have archived outstanding items OR ALARM on genuinely uncaptured plans.
- Owner prompts tagged as specification language by Hook 3 → check queue file.

**Phase 4** — Post-impl report with dogfood evidence. Codex VERIFIED before merge (these changes affect Agent Red's active hook surface, so governance gate is critical).

## Verification

- Hook 1 tested by: (a) attempt Write to `bridge/fake-test-001.md` without DA search → BLOCK exit 2; (b) add `# da-search-confirmed: test` marker → pass; (c) make a DA search call in same turn → pass.
- Hook 2 tested by: simulate session with one unarchived AskUserQuestion response → ALARM emitted. Simulate clean session → OK.
- Hook 3 tested by: submit prompt with GOV-09 spec language → queue file contains entry. Submit routine question → queue empty.

## Timeline

- **Now (session-end, tonight):** this scope bridge filed NEW. Given CRITICAL priority and narrow scope, request Codex expedited review.
- **On Codex GO:** immediate implementation. Hooks land before session wrap.
- **S300 start:** hooks auto-load via `.claude/settings.json` registration. First session where Prime's DA governance is mechanically enforced.

## Risk / Blast Radius

- Hook 1 BLOCK could frustrate legitimate bridge work. Mitigation: escape hatch `# da-search-confirmed: <reason>` with justification.
- Hook 2 first-run ALARM for today's session is expected (today's late-session plans may be archived by DELIB-0817 but cross-reference may not catch every one). That's acceptable — we want the ALARM to surface what's actually outstanding.
- Hook 3 false positives (GOV-09 pattern matches routine prompts) manageable because queue is drained at wrap with human-readable summary before DELIB insert. Worst case: extra DELIB rows, not missing rows. Safer direction.

## Why Codex should GO quickly

- Scope is narrow (3 hook files + settings.json + tests).
- All changes reversible via git revert of single feature branch.
- Owner has explicitly escalated priority.
- Alternative (waiting for umbrella bridge) leaves S300 boundary exposed to the exact failure class that just fired twice in one session.

## Next Steps After Codex GO

1. Implement 3 hooks.
2. Register in `.claude/settings.json`.
3. Dogfood in current session (prove hook 1 blocks, hook 2 alarms, hook 3 queues).
4. Post-impl report with dogfood transcript.
5. Codex VERIFIED.
6. S300 session inherits automation mechanically.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
