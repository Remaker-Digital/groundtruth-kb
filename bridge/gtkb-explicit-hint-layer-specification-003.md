WITHDRAWN

# Withdrawal - Explicit-Hint Layer Specification (obsolete)

bridge_kind: owner_directed_withdrawal
Document: gtkb-explicit-hint-layer-specification
Version: 003
Date: 2026-06-21 UTC
Withdraws: bridge/gtkb-explicit-hint-layer-specification-001.md (NEW) + -002.md (GO, terminal)
Work Item: WI-4482

## Status

WITHDRAWN by owner direction. Terminal.

## Owner Decisions / Input

Owner directive (2026-06-21, ::open deliberation session), captured as
DELIB-20260621-EXPLICIT-HINT-CONTEXT-LOAD-REFRAME (owner_conversation /
owner_decision, AUQ-backed): the -001 governance-review proposal is obsolete -
"it was an error; it never made sense." DEC-5 of that DELIB directs WITHDRAWN.

## Rationale

The -001 proposal (filed 2026-06-12, GO-terminal at -002) drafted a governance
surface for the explicit-hint layer under a model the owner has since reframed.
DELIB-20265287 (2026-06-19) and DELIB-20260621 (2026-06-21) supersede its substance:
- The -001 concurrency model ("<=1 per type, up to 5 simultaneous") is superseded
  by DELIB-20265287 D1 (single active activity envelope).
- The layer is reframed as a context-management / progressive-disclosure mechanism
  with a 4-class context-load profile (DELIB-20260621 DEC-1/DEC-2), carried forward
  by the re-scoped WI-4684, not by this thread.

## Blast radius

Nil. The -002 GO was governance-review-terminal (target_paths: [],
requires_verification: false, kb_mutation_in_scope: false). The downstream artifacts
it authorized (ADR-EXPLICIT-HINT-LAYER-001, DCL-ACTIVITY-ENVELOPE-INTERCEPTION-001,
canonical-terminology.md edits) were never created, so withdrawal removes no
canonical state. The audit trail (-001, -002, -003) is preserved append-only.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
