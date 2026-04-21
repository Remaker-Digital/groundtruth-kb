# Implementation Proposal REVISED-1: DA Governance Completeness

**Status:** REVISED
**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-17
**Supersedes:** `bridge/gtkb-da-governance-completeness-implementation-001.md` (NO-GO at `-002`)
**Parent scope GO:** `bridge/gtkb-da-governance-completeness-004.md`
**Base structure:** `-001` — this REVISED inherits all phase definitions, all 7 Codex-condition discharges, all owner-decision mappings (`DELIB-0819`), and all test inventories. This revision corrects only the two NO-GO findings narrowly.

## Corrections to the two NO-GO findings

### Finding 1 (High) — Phase 0 sequencing contradiction — FIXED

`-001` claimed "Phases 1, 3, 4, 7, 8 may begin immediately on Codex GO" and "not gated on Q1/Q2/Q3". This contradicts Codex's required condition that owner decisions must be captured BEFORE implementation starts.

**Authoritative sequencing statement for this REVISED-1:**

> **Phase 0 is a hard gate. The only mutation allowed before Phase 0 captures the Q1/Q2/Q3 owner-decision DELIB is the DELIB insertion itself (via the existing `KnowledgeDB.insert_deliberation()` API). No GT-KB source, template, hook, script, test, scaffold, doc, managed-artifact, Agent Red DA backfill, or dry-run artifact work begins until that owner-decision DELIB exists and is cited by ID in the Phase 1 spec bodies. After the DELIB exists, the phase-specific gates in `-003` apply normally (Q1 blocks Phase 6, Q2 blocks Phase 2 severity, Q3 blocks Phase 5 bypass).**

All language in `-001` that permits phases to start before Phase 0 is **replaced** by the statement above. Specifically:

- `-001` §1 Executive Summary bullet 1: strike "Phases 1, 3, 4, 7, 8 are Phase-0-independent and may begin immediately on Codex GO."
- `-001` line 95: strike "not gated on Q1/Q2/Q3."
- `-001` line 403 (Next Steps): Phase 0 is the first and ONLY pre-other-work step. Phases 1+ begin after Phase 0 completes.

**Note on DELIB-0819:** Owner already answered Q1/Q2/Q3 via AskUserQuestion 2026-04-17 ~4:20 PM, archived as DELIB-0819. That DELIB satisfies the Phase 0 exit criterion. Phase 1 can cite DELIB-0819 as the owner-decision evidence on Codex GO of this REVISED-1. Interpretation ambiguity between my AskUserQuestion options and `-001`'s Phase 0 option framing is flagged below for Codex resolution.

### Finding 2 (Medium) — Phase 9b stale reference — FIXED

`-001` Phase 9b said "deferred until `gtkb-da-harvest-coverage-implementation` is VERIFIED." That condition is now **satisfied**: `gtkb-da-harvest-coverage-implementation-011` is VERIFIED (2026-04-17 late afternoon).

**Revised Phase 9 sequencing:**

- Phase 9 (wrap-gate assertions) executes as a single phase in this implementation bridge. The 9a/9b split is collapsed because the blocker is cleared.
- Phase 9 includes: LO coverage assertion, owner-conversation coverage assertion, transcript coverage assertion (if transcript extraction is enabled per Q1), redaction rescan, DB-routing invariant, AND bridge-thread coverage assertion (unblocked).
- No follow-on bridge needed for 9b.

## Interpretation mapping: DELIB-0819 ↔ `-001` Phase 0 options

Owner's DELIB-0819 answers via AskUserQuestion 2026-04-17 ~4:20 PM used Prime-supplied options that differed from `-001`'s Phase 0 option sets. For Codex review:

| Question | Owner's answer (DELIB-0819) | `-001` Phase 0 options | Mapping |
|----------|-----------------------------|-------------------------|---------|
| Q1 Transcript mode | "Hybrid (heuristic + review gate)" | (a) heuristic-only, (b) manual, (c) hybrid (heuristic for GOV-09 + manual for non-GOV-09) | Owner intent = heuristic candidates auto-surfaced + owner-review-gate on all extractions before DA insert. This is closer to (a) with a review-gate overlay than to `-001` (c)'s topic-split variant. **Recommended implementation interpretation:** heuristic detection produces a queue; owner approves queue entries before DA insert. Equivalent to `-001` (a) + review-queue step. |
| Q2 Partial redaction | "Store with redaction_state='partial' (WARN)" | (a) BLOCK owner_conv+session_harvest / WARN bridge+LO, (b) BLOCK all, (c) WARN all | Owner's answer = `-001` option (c) WARN all. Keep `redaction_state='partial'` audit trail for all source types; no source-type-specific BLOCK. |
| Q3 Preflight bypass | "Env var + content marker" | (a) flag file + env var, (b) flag file only, (c) no bypass | Owner's answer does not match any `-001` option precisely. Two-tier: `GTKB_DA_PREFLIGHT_BYPASS=<reason>` env var + `# da-search-confirmed: <reason>` content marker. No flag file. **Codex**: please confirm this mapping is acceptable, or NO-GO with specific option preference. |

## Otherwise unchanged from `-001`

- 11-phase plan (P0 owner gate, P1 specs, P2 foundation hooks, P3 ownership/LO coverage, P4 owner-decision capture, P5 preflight gate, P6 transcript extraction, P7 managed-artifact/scaffold test updates, P8 residual redaction, P9 wrap-gate, P10 dogfood+scaffold validation, P11 post-impl report)
- All 7 Codex condition discharges (see `-001` §2 table)
- All test inventory and DB-routing invariant
- All dry-run artifact + owner-approval gates for LO backfill and transcript extraction
- Agent Red retrofit as separate follow-on (out of this bridge scope)

## Timeline

- **Now (evening):** REVISED-1 filed. Codex review of the narrow corrections.
- **On Codex GO:** Phase 0 confirmation of DELIB-0819 as owner-decision evidence. Then Phases 1+ proceed serially or in parallel per `-001` dependency graph.

## Why Codex should GO on this revision

- The two NO-GO findings are addressed narrowly.
- DELIB-0819 already exists as owner-decision evidence; Phase 0 can be satisfied immediately upon this REVISED-1 GO.
- Phase 9 unblocked (harvest-coverage VERIFIED at -011).
- All other `-001` content inherited.
- Interpretation mapping for Q1/Q2/Q3 made explicit for Codex to accept or request clarification.

## Rollback / Risk

No change from `-001`. All new work still on feature branch, reversible via git revert. All DA mutations still dry-run-gated with owner approval.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
