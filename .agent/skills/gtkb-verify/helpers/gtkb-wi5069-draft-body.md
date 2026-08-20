<!--
THIS FILE IS A PROJECTION, NOT CANONICAL.
Projected from the neutral harness baseline by the GT-KB projection engine.
Do not edit here: change the baseline (.harness-baseline-configuration) and re-project with
`gt harness project claude`. If a needed change cannot be made through
the baseline and re-projection, file a work item against the projector
(GOV-HARNESS-NEUTRAL-BASELINE-001 obligation 6).
-->
GO

# gtkb-wi5069-headless-lane-coverage-role-invariant - Replace durable role partition with lane coverage validation

bridge_kind: loyal_opposition_review
Document: gtkb-wi5069-headless-lane-coverage-role-invariant
Version: 002
Author: OpenRouter Loyal Opposition (F)
Date: 2026-07-08T01:54:00Z

author_identity: OpenRouter Loyal Opposition
author_harness_id: F
author_session_context_id: 2026-07-08T01-54-00Z-loyal-opposition-F-manual-wi5069-role-invariant
author_model: moonshotai/kimi-k2.7-code
author_model_version: kimi-k2.7-code
author_model_configuration: OpenRouter harness shim; route openrouter-cloud-default; skill bridge-review; guarded tools Read, Write, Edit, Grep, Glob, Bash

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5069

reviewed_version: 001
prior_bridge_file: bridge/gtkb-wi5069-headless-lane-coverage-role-invariant-001.md

---

## Verdict

GO with binding implementation conditions.

## Summary of Proposal

Prime Builder proposal gtkb-wi5069-001 seeks to replace the absolute durable active PB/LO partition invariant in `groundtruth_kb.mode_switch.invariants` with lane-coverage validation that permits an LO-only headless dispatch surge when an interactive owner-declared Prime Builder session anchors PB responsibility. Target paths include the mode-switch validator/transaction/derive modules, the role behavior-contract markdown rules, and the corresponding platform tests.

## Preflight Evidence

- `scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5069-headless-lane-coverage-role-invariant`: preflight_passed=true, no missing required specs, advisory gaps only (ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001, DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001, GOV-ARTIFACT-ORIENTED-GOVERNANCE-001).
- `scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5069-headless-lane-coverage-role-invariant`: all must_apply clauses satisfied, zero blocking gaps.

## Review Assessment

1. **Authority and scope** - The proposal carries Project Authorization, Project, Work Item, and owner-decision citation (`DELIB-20260707-HEADLESS-LANE-COVERAGE`). Spec linkage satisfies `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`.

2. **Substantive correctness** - The existing `verify_role_document_partition` enforces at least one active durable `prime-builder` and one active durable `loyal-opposition`. That invariant is over-broad once GT-KB recognizes an interactive PB session whose role persists independently of dispatcher/default registry assignments. Moving to lane-coverage validation, with explicit fail-closed behavior when no PB anchor exists, is the correct direction.

3. **Safety concerns addressed by the proposal** - The proposal explicitly requires preserving bridge self-review protection through author/reviewer session-context checks and prohibits a headless worker from reviewing its own proposal via durable role reassignment. This is the critical LO concern and it is named.

4. **Remaining implementation risk** - The proposal is appropriately high-level for a NEW proposal, but the implementation must resolve three underspecified areas:
   - The exact source of "interactive PB anchor" evidence (session-state artifact, transcript-defined session role, or other canonical record) and how it is distinguished from durable registry fallback.
   - The precise definition of "lane coverage" and the algorithm by which an LO-only durable partition is accepted only when a PB anchor is present.
   - The concrete test matrix proving the self-review guard survives registry role switches.

## Binding Conditions for Implementation / Verification

The following are not advisory; they must be satisfied in the implementation and verified before this work can receive a VERIFIED verdict:

1. **Fail-closed PB anchor** - The new validator must reject any candidate role map that lacks both (a) at least one active durable prime-builder AND (b) a valid interactive/owner-declared PB anchor when durable PB coverage is absent. LO-only headless surge is permitted only when a PB anchor exists outside the headless LO lane.

2. **Session-context self-review guard** - The implementation must not weaken the existing bridge author/reviewer session-context protection. A headless worker dispatched as LO must remain unable to review a proposal it authored, regardless of durable registry role reassignment.

3. **Role rule files are behavior contracts only** - Edits to `.claude/rules/operating-role.md` and `.claude/rules/prime-builder-role.md` must be limited to clarifying the interaction between interactive session role and dispatcher/default role. They must not attempt to store or override role assignments.

4. **Test coverage** - The verification must include focused tests demonstrating:
   - Durable LO-only partition rejected without interactive PB anchor.
   - Durable LO-only partition accepted with valid interactive PB anchor.
   - Self-review still blocked after registry role switch.
   - Existing single-harness and multi-harness topologies remain valid.

## Evidence Reviewed

- `bridge/gtkb-wi5069-headless-lane-coverage-role-invariant-001.md`
- `groundtruth-kb/src/groundtruth_kb/mode_switch/invariants.py`
- `groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py` (partial)
- `groundtruth-kb/src/groundtruth_kb/mode_switch/derive.py`
- `.claude/rules/operating-role.md`
- `.claude/rules/prime-builder-role.md`
- `platform_tests/groundtruth_kb/test_mode_switch_invariants.py`
- `platform_tests/groundtruth_kb/test_mode_switch_transaction.py` (partial)
- `harness-state/harness-registry.json`

## Prior Deliberations

- `DELIB-20260707-HEADLESS-LANE-COVERAGE` - Owner agreed the durable active PB/LO partition validator is over-broad for interactive PB plus LO-default headless routing; direct authority for this proposal.
- `DELIB-20264148` - Prior LO review of harness role portability required a full durable role partition for the earlier FR9 model; this proposal intentionally revises that earlier assumption for the newer interactive/headless split.
- `DELIB-1466` - Role and session lifecycle review recommended keeping PB/LO as authority-bearing operating roles while treating other work as session lanes; relevant to separating operating role authority from session lane/coverage.
- `DELIB-20265152` - Prior verification that spawned headless harness prompts defer to the durable role record; this proposal preserves that for headless workers while adding explicit interactive PB anchor handling for topology validation.
- `DELIB-20264030` - Prior GO on whole-candidate mode-switch validation; this change should keep whole-candidate validation, but update the candidate invariant from durable partition symmetry to lane coverage plus session-context protection.
