NEW

# Implementation Proposal — WI-4482 Explicit-Hint Context-Management Umbrella (governance_review)

bridge_kind: governance_advisory
Document: gtkb-wi4482-explicit-hint-context-management-umbrella
Version: 001
Author: Prime Builder (Cursor, harness E, interactive session via ::init gtkb pb)
Date: 2026-06-30 UTC

author_identity: Cursor Prime Builder
author_harness_id: E
author_session_context_id: cursor-pb-s520-envelope-wi4482-20260630
author_model: Composer
author_model_version: composer-2.5-fast
author_model_configuration: Cursor Agent interactive Prime Builder session

Project Authorization: PAUTH-PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-WI-4482-EXPLICIT-HINT-UMBRELLA
Project: PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT
Work Item: WI-4482
Recommended commit type: docs

target_paths: []

implementation_scope: governance_review_spec_drafting
requires_review: true
requires_verification: false
kb_mutation_in_scope: false

## KB-Mutation Negation (self-demonstration)

This proposal performs no MemBase mutation and writes no protected narrative
files. Glossary edits, ADR, and DCL drafts below land downstream via
formal-artifact-approval-packet and narrative-artifact-approval-packet writes,
each gated by `GOV-ARTIFACT-APPROVAL-001`.

## Claim

Re-anchor WI-4482 after owner withdrawal of
`bridge/gtkb-explicit-hint-layer-specification-003.md` (DELIB-20260621 DEC-5).
The explicit-hint layer is reframed as a **context-management / progressive-
disclosure** mechanism — not a redesign of the envelope program and not the
disposition-profile leg (owned by WI-4684 / `gtkb-activity-disposition-profile-adr-dcl`).

This governance_review proposal drafts four coupled deliverables for LO review:

1. **Glossary term `explicit hint`** in `.claude/rules/canonical-terminology.md`:
   inline `::`-prefixed first-line tokens that steer session stance through harness
   hooks and priority directives. Members include init keywords, wrap keywords, and
   activity open/close keywords. Grammar mirrors `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`
   discipline (first-line-only, closed vocabulary, strict parse).

2. **Canonical rename `topic envelope` → `activity envelope`** with lineage
   (`work envelope` → `topic envelope` → `activity envelope`). Spec IDs
   (`SPEC-TOPIC-*`) persist per append-only versioning; canonical TERM in glossary
   and narrative surfaces changes. Three-axis disambiguation: activity-TYPE
   (`::open <type>`), TARGET/subject (payload on typed open), AREA (`::init` subject
   `{gtkb, application}`).

3. **Init-keyword glossary reconciliation to v3** per `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`
   and DELIB-20260648: `^::init (gtkb|application)( (pb|lo))?$` (subject mandatory,
   role optional). Retire stale v2-only glossary text.

4. **`ADR-EXPLICIT-HINT-CONTEXT-MANAGEMENT-001`** (architecture_decision) +
   **`DCL-ACTIVITY-ENVELOPE-INTERCEPTION-001`** (design_constraint): hook-primary
   interception of `::open <type>` / `::close <type>` injecting the activity's
   context-load bundle (DEC-1/DEC-2), plus a non-blocking soft-reminder gate during
   no-implement activities (DEC-3), with agent-enforced fallback where hook events
   are unavailable (`ADR-CODEX-HOOK-PARITY-FALLBACK-001`). Preserves closed vocabulary
   `{spec, build, test, deliberation, project}`, typed close, and session-envelope
   topics-array durability already specified by WI-4291..WI-4297.

## Why Now

The withdrawn `-001` vehicle used a superseded concurrency and umbrella model.
DELIB-20260621 and DELIB-20265287 reframe explicit hints as targeted context loading
with a single-active activity envelope. Locking glossary + interception DCL before
runtime implementation prevents WI-4301 / disposition runtime from baking in stale
terminology or the topic/subject mis-read.

## Why Not (alternatives considered)

- Revive the withdrawn `-001` thread body unchanged — rejected (owner: obsolete).
- Fold disposition-profile ADR/DCL into WI-4482 — rejected; WI-4684 owns that leg.
- Free-form activity vocabulary — rejected (DELIB-20260612, DELIB-2500).
- Supersede WI-4291..WI-4297 envelope specs — rejected (DEC-5 / DELIB-20265287 D8).

## Prior Deliberations

- `DELIB-20260621-EXPLICIT-HINT-CONTEXT-LOAD-REFRAME` (2026-06-21, owner_decision) —
  DEC-1..5 reframing; withdraws obsolete `-001` vehicle.
- `DELIB-20265287` (2026-06-19) — single-active envelope; disposition profile enriches
  intent_hint leg (sibling to this WI, not in scope here).
- `DELIB-20260612-EXPLICIT-HINT-LAYER-DECISION-SET` — umbrella + closed vocabulary.
- `DELIB-20260648` — init-keyword v3 optionality basis.
- `DELIB-20260637` #4 — topic-envelope rename lineage this refines to activity envelope.
- `DELIB-2238` / `DELIB-2500` — envelope-convention foundation.

## Specification Links

Cross-cutting (blocking):

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001`

Domain (blocking):

- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`
- `ADR-ENVELOPE-META-MODEL-001`
- `DCL-ENVELOPE-META-MODEL-001`
- `DCL-TOPIC-ENVELOPE-ROUTING-001`
- `DCL-SESSION-ENVELOPE-DURABILITY-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`

Cross-cutting (advisory):

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`

New formal artifacts created downstream (via formal-artifact-approval-packet):

- `ADR-EXPLICIT-HINT-CONTEXT-MANAGEMENT-001` (architecture_decision)
- `DCL-ACTIVITY-ENVELOPE-INTERCEPTION-001` (design_constraint)

## Owner Decisions / Input

Authorized by:

- `DELIB-20266593` — PAUTH-PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-WI-4482-EXPLICIT-HINT-UMBRELLA
  (S515 project AUQ).
- `DELIB-20260621-EXPLICIT-HINT-CONTEXT-LOAD-REFRAME` — reframe + withdraw obsolete `-001`.
- `PAUTH-PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT-BOUNDED-IMPLEMENTATION-2026-06-23`
  — snapshot-bound WI-4482 membership.

No additional owner AUQ is required for this governance_review drafting thread.

## Requirement Sufficiency

Existing requirements sufficient. WI-4482 description (v2) and the deliberations
above define the durable deliverables; this proposal drafts the governance surface
for LO review before formal-artifact-approval-packet inserts.

## Specification-Derived Verification Plan

Governance-review terminal pattern (`target_paths: []`, `requires_verification: false`):

| Check | Command | Expected |
|-------|---------|----------|
| Applicability preflight | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4482-explicit-hint-context-management-umbrella` | `preflight_passed: true` |
| ADR/DCL clause preflight | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4482-explicit-hint-context-management-umbrella` | exit 0, blocking gaps 0 |
| Phantom-spec sweep | manual review of Specification Links | every cited id exists in MemBase |
| No runtime pytest required pre-GO | `groundtruth-kb/.venv/Scripts/python.exe -m pytest -q --collect-only platform_tests/scripts/test_session_init_keyword_matching.py` | collect-only sanity (no code mutation in this thread) |
| Downstream glossary/ADR/DCL inserts | formal-artifact-approval packets post-GO | separate governed writes |

## Risk / Rollback

Risk: terminology drift if glossary rename lands without coordinated interception DCL.
Rollback: single revert of formal-artifact-approval inserts; bridge chain preserved
append-only; withdrawn `-001` thread remains historical.

## Bridge Filing

Filed as `bridge/gtkb-wi4482-explicit-hint-context-management-umbrella-001.md`.
Supersedes the withdrawn `gtkb-explicit-hint-layer-specification` vehicle for new
LO review; does not mutate prior versions.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
