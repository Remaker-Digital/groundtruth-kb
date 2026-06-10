NEW

# Implementation Proposal - Role Enhancement: Review-Depth Methodology (GTKB-ROLE-ENHANCEMENT)

bridge_kind: prime_proposal
Document: gtkb-role-enhancement-review-depth-methodology
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-SESSION-LIFECYCLE-UX-SESSION-LIFECYCLE-UX-BATCH
Project: PROJECT-GTKB-SESSION-LIFECYCLE-UX
Work Item: GTKB-ROLE-ENHANCEMENT

target_paths: [".claude/rules/loyal-opposition.md", ".claude/rules/report-depth.md", ".claude/rules/report-depth-prime-builder-context.md", "templates/rules/review-depth-methodology.md"]

This NEW proposal addresses the first of 9 underdefined role-contract gaps identified at `DELIB-S310-ROLE-DEFINITION-ASSESSMENT`: review-depth methodology. Per WI description: "deferred until post-isolation". Isolation closeout is now in flight (batch-4), so this proposal advances the first gap while remaining gaps queue for follow-on slices.

## Claim

Document the review-depth methodology contract explicitly in the LO role rule set: when reviewing a bridge proposal, the LO must perform N read-anchor operations (spec-text check, prior-deliberation search, target-paths inspection, test-fixture inspection) and cite each in the verdict. Codifies what currently lives as implicit Codex practice.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol; LO operates within it.
- `GOV-ARTIFACT-APPROVAL-001` - rule files are protected narrative artifacts.
- `SPEC-AUQ-POLICY-ENGINE-001` - policy engine.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping (manual for rule-doc).
- `GOV-STANDING-BACKLOG-001` - WI tracked.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence.
- `DELIB-S310-ROLE-DEFINITION-ASSESSMENT` - originating 9-gap assessment.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - batch-5 authorization.
- `DELIB-S310-ROLE-DEFINITION-ASSESSMENT` - Codex assessment identifying 9 gaps.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved GTKB-SESSION-LIFECYCLE-UX authorization including this WI.
- 2026-04-26 S310: original owner directive for role-contract enhancement.

## Requirement Sufficiency

Existing requirements sufficient. WI description + DELIB-S310 identify the 9 gaps; this slice addresses gap #1.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI, first-of-9 gaps; member of PROJECT-GTKB-SESSION-LIFECYCLE-UX per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`. Review-packet inventory: IP-1 (methodology rule) + IP-2 (LO rule update) + IP-3 (verification) single thread.

## Bridge INDEX Update Evidence

NEW filed; new top entry prepended.

## Proposed Scope

### IP-1: Review-depth methodology rule

New file `.claude/rules/review-depth-methodology.md` (or merge into `report-depth.md` if owner prefers):

Documents the mandatory review-depth checklist for LO bridge reviews:
1. Read the proposal's full content (not just summary).
2. Read the cited specs (verify each exists + claim alignment).
3. Run `bridge_applicability_preflight` + `adr_dcl_clause_preflight`.
4. Search Deliberation Archive for prior decisions on the topic.
5. Inspect proposal's target_paths against current repo state.
6. Read referenced tests / test fixtures (for spec-derived testing claims).
7. Cite each read anchor in the verdict's "Review Scope" section.

This is a narrative artifact; requires `narrative-artifact-approval` packet at implementation time.

### IP-2: LO rule update

In `.claude/rules/loyal-opposition.md`, add a "Review-Depth Methodology" section that references the new rule + binds it as mandatory for bridge reviews.

### IP-3: Verification

Verification is manual: spot-check 3 recent LO verdicts (any of this session's NO-GOs) against the methodology. Document compliance in post-impl report.

## Specification-Derived Verification Plan

| Behavior | Verification |
|---|---|
| review-depth-methodology.md exists | `Path('.claude/rules/review-depth-methodology.md').exists()` |
| LO rule references methodology | grep `review-depth-methodology` in `loyal-opposition.md` returns >= 1 match |
| Methodology includes 7-step checklist | grep numbered list items 1-7 |
| Codex-side verdicts cite anchors | spot-check 3 recent verdicts; documented in post-impl report |

(No automated test; this is a narrative-rule clarification.)

## Acceptance Criteria

- IP-1 rule file landed (with narrative-artifact-approval packet).
- IP-2 LO rule updated (with packet).
- IP-3 spot-check documented in post-impl report.
- Both preflights PASS.

## Risks / Rollback

- Risk: explicit methodology codification may slow LO reviews initially. Mitigation: methodology codifies practice Codex already follows; should be additive only.
- Risk: 9-gap parent WI may stay open after this WI lands. Mitigation: explicit follow-on tracking in post-impl report.
- Rollback: remove rule file + revert LO rule edit.

## Recommended Commit Type

`feat` - role-contract enhancement. ~80 LOC documentation.
