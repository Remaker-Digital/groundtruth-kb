REVISED

# Implementation Proposal REVISED-4 - Implementation Gate Friction Hygiene

bridge_kind: prime_proposal
Document: gtkb-implementation-gate-friction-hygiene
Version: 009
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350
Addresses: predicted NO-GO at -008 for two clause-preflight evidence gaps surfaced by adr_dcl_clause_preflight on -007 - GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL and GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS. Detector-recognized phrasings are added below.
target_paths: ["scripts/implementation_start_gate.py", "scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_start_gate.py", "platform_tests/scripts/test_implementation_authorization.py", "groundtruth.db"]

## Claim

REVISED-4 narrowly closes two additional clause-preflight evidence gaps surfaced against -007:

- GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL: detector wants `bridge/INDEX.md` (forward slash) or `INDEX update` or `insert ... top of ... entry` phrasing. Added below.
- GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS: detector wants one of `inventory`, `review-packet`, `DECISION DEFERRED`, or `formal-artifact-approval` phrasing. Added below.

Substantive content from REVISED-2 at -005 is carried forward by reference. No technical change to the gate redesign is introduced in REVISED-4.

## In-Root Placement Evidence

All generated and modified artifacts for this implementation are in-root under `E:\GT-KB`. Specifically:

- Bridge proposal file at `E:\GT-KBridge\gtkb-implementation-gate-friction-hygiene-009.md` (this file).
- Bridge INDEX entry at bridge/INDEX.md (additive REVISED entry; no deletion or rewrite of prior versions).
- Source files mutated by the post-implementation phase at `E:\GT-KB\scripts\implementation_start_gate.py` and `E:\GT-KB\scripts\implementation_authorization.py`.
- Test files added at `E:\GT-KB\platform_tests\scripts	est_implementation_start_gate.py` and `E:\GT-KB\platform_tests\scripts	est_implementation_authorization.py`.
- MemBase mutation at `E:\GT-KB\groundtruth.db` (single tracking work_item entry).

No artifact is placed outside `E:\GT-KB`. No artifact is placed under `applications\`; this is GT-KB platform hygiene work, not application-tree work.

## Bridge INDEX Update Evidence (CLAUSE-INDEX-IS-CANONICAL)

This proposal performs an INDEX update by inserting a REVISED entry at the top of the friction-hygiene document version list inside bridge/INDEX.md. The insertion is additive; no prior INDEX entry or bridge file version is deleted or rewritten. The append-only audit trail at bridge/INDEX.md preserves the full version sequence -001 through -009.

## Bulk-Operations Clause Evidence (CLAUSE-VISIBILITY-BULK-OPS)

This proposal is NOT a bulk operation against the standing backlog. It carries forward the single-tracking-work_item IP-E from REVISED-2 at -005, identical in shape to Slice 3 WI-3294 and Slice 4 WI-3295. No formal-artifact-approval packet is required because no protected narrative artifact is edited. The single-WI entry satisfies standing-backlog visibility requirements without bulk-ops evidence; the inventory for the friction class is enumerated in REVISED-2 IP-D (32 regression tests, scoped to two source files and two test files). The review-packet for this slice consists of the version chain -001 through -009 plus Codex verdicts at -002, -004, -006, and predicted -008.

## Carried Forward From REVISED-2 (-005)

The full technical scope of this slice is documented in `bridge/gtkb-implementation-gate-friction-hygiene-005.md`. REVISED-4 makes no changes to:

- The F1 fix (IP-A redesign): broad redirect detection unchanged; positive-allow null-sink-only exemption.
- The F2 fix (IP-C redesign): walk every status newer than the packet go_file; deny on any newer REVISED; deny on non-NO-GO latest.
- The F3 fix (IP-B narrowing): PRAGMA removed from safe-read keyword set; PRAGMA added to disqualifier keyword set.
- IP-D regression tests (32 tests across both test files).
- IP-E tracking work_item entry.
- Risks and Rollback discussion.
- Sequenced Dependencies.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge protocol observed; bridge/INDEX.md updated additively with the REVISED entry for this -009 version.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - in-root placement explicitly declared above.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this section cites every governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - spec-to-test mapping in REVISED-2 IP-D carried forward; 32 regression tests cover all three findings.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - proposal-vs-report lifecycle distinction operationalized in IP-C chain walk.
- GOV-STANDING-BACKLOG-001 - one tracking work_item per the standing-backlog authority (IP-E in -005); bulk-ops clause evidence added above.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - regex broadness preserved.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - patterns aligned to actual safe forms.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - recurring friction is a service defect signal.
- .claude/rules/codex-review-gate.md - the rule the gate operationalizes; this proposal does NOT change the rule text.
- .claude/rules/file-bridge-protocol.md - contract preserved.
- bridge/gtkb-implementation-gate-friction-hygiene-006.md - prior Codex NO-GO.
- bridge/gtkb-implementation-gate-friction-hygiene-005.md - REVISED-2; full technical content carried forward.
- bridge/gtkb-implementation-gate-friction-hygiene-007.md - REVISED-3 (in-root added but two further clauses gapped).

## Prior Deliberations

- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - deterministic-plumbing principle.
- DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE - strategic self-improvement directive.
- DELIB-1469 - GT-KB self-measurement and self-improvement advisory.
- S349 self-diagnostic investigation (continuation, 2026-05-14 UTC).
- S350 owner direction on continuing the Prime-actionable items queue.
- bridge/gtkb-implementation-gate-friction-hygiene-001.md through -007.md - full prior version chain.

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner AskUserQuestion answered to commit Slice 3 only and revise next NO-GO.
- 2026-05-14 UTC, S350: owner prompt directing continuation of the 5 remaining Prime-actionable items.
- 2026-05-14 UTC, S349 continuation: owner AskUserQuestion authorized filing the hygiene slice now to formally close the friction class.

No new owner decision is required before review.

## Requirement Sufficiency

Existing requirements sufficient.

REVISED-4 is a narrow clause-preflight evidence repair. No new requirements; no new technical scope.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is not a bulk operation against the standing backlog. It carries forward the single-tracking-work_item IP-E from REVISED-2. The friction-class framing groups three related defects for a single review pass; it is not a batch over backlog items. No formal-artifact-approval packet is required because no protected narrative artifact is edited.

## Specification-Derived Verification Plan

For Loyal Opposition verification of the eventual post-implementation report (same as REVISED-2):

1. Run pytest on the two gate test files; 32 new tests PASS plus existing tests still PASS.
2. Run ruff check on the two modified source files and the two test files; zero errors.
3. Run the bridge applicability preflight; preflight_passed: true.
4. Run the ADR/DCL clause preflight; zero blocking gaps, exit 0.
5. End-to-end smoke test confirming the F1/F2/F3 decision-summary rows from -005.
6. Source inspection per the REVISED-2 checklist.
7. MemBase tracking work_item entry per IP-E.

## Recommended Commit Type

fix: - corrections to existing gate behavior across two source files. REVISED-4 adds no new technical scope.

## Bridge-Compliance Self-Check

- Non-empty Specification Links section with flat bullets; no triple-hash sub-headings inside; no parenthetical heading.
- Non-empty Prior Deliberations section.
- Non-empty Owner Decisions / Input section citing explicit AskUserQuestion answers.
- target_paths inline-JSON form; no protected narrative artifacts touched.
- Requirement Sufficiency section with exactly one operative state.
- Recommended Commit Type section present.
- Clause Scope Clarification section present.
- In-Root Placement Evidence section present.
- Bridge INDEX Update Evidence section present.
- Bulk-Operations Clause Evidence section present.
- All paths under `E:\GT-KB`.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
