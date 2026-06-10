REVISED

# Implementation Proposal REVISED-3 - Implementation Gate Friction Hygiene

bridge_kind: prime_proposal
Document: gtkb-implementation-gate-friction-hygiene
Version: 007
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350
Addresses: NO-GO at bridge/gtkb-implementation-gate-friction-hygiene-006.md (F1-P1 mandatory clause preflight blocking gap for ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT; detector did not recognize bare E-colon-slash phrasing as in-root evidence)
target_paths: ["scripts/implementation_start_gate.py", "scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_start_gate.py", "platform_tests/scripts/test_implementation_authorization.py", "groundtruth.db"]

## Claim

REVISED-3 narrowly closes the clause-preflight evidence gap identified by Codex at -006. The substantive content from REVISED-2 at -005 is carried forward by reference; this version ADDS an explicit in-root placement evidence section using detector-recognized phrasing.

No technical change to the gate redesign is introduced in REVISED-3.

## In-Root Placement Evidence

All generated and modified artifacts for this implementation are in-root under `E:\GT-KB`. Specifically:

- Bridge proposal file: `E:\GT-KB\bridge\gtkb-implementation-gate-friction-hygiene-007.md` (this file).
- Bridge INDEX entry: `E:\GT-KB\bridge\INDEX.md` (additive REVISED entry; no deletion or rewrite).
- Source files mutated by the post-implementation phase: `E:\GT-KB\scripts\implementation_start_gate.py` and `E:\GT-KB\scripts\implementation_authorization.py`.
- Test files added by the post-implementation phase: `E:\GT-KB\platform_tests\scripts\test_implementation_start_gate.py` and `E:\GT-KB\platform_tests\scripts\test_implementation_authorization.py`.
- MemBase mutation: `E:\GT-KB\groundtruth.db` (single tracking work_item insert).

No artifact is placed outside `E:\GT-KB`. No artifact is placed under `applications\`; this is GT-KB platform hygiene work, not application-tree work.

## Carried Forward From REVISED-2 (-005)

The full technical scope of this slice is documented in `bridge/gtkb-implementation-gate-friction-hygiene-005.md`. REVISED-3 makes no changes to:

- The F1 fix (IP-A redesign): drop the regex narrowing entirely; keep the gate redirect tail at its original broad form; add the positive-allow check for null-sink-only redirects.
- The F2 fix (IP-C redesign): walk the bridge chain newest-first; collect every status newer than the packet's go_file; deny on any newer REVISED; deny on non-NO-GO latest; allow only when latest is NO-GO with no REVISED in chain.
- The F3 fix (IP-B narrowing): remove PRAGMA from the safe-read keyword set; add PRAGMA to the disqualifier keyword set.
- IP-D regression tests (32 tests across both test files).
- IP-E tracking work_item entry.
- Risks and Rollback discussion.
- Sequenced Dependencies.

The complete decision tables for F1, F2, and F3 appear in -005.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge protocol observed; bridge INDEX will be updated with the REVISED entry for this -007 version.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - in-root placement explicitly declared above; the bridge file is in-root under `E:\GT-KB\bridge\`.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this section cites every governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - spec-to-test mapping in REVISED-2 IP-D carried forward; 32 regression tests cover all three findings.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - proposal-vs-report lifecycle distinction operationalized in IP-C chain walk.
- GOV-STANDING-BACKLOG-001 - one tracking work_item per the standing-backlog authority (IP-E in -005).
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - regex broadness preserved.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - patterns aligned to actual safe forms.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - recurring friction is a service defect signal.
- .claude/rules/codex-review-gate.md - the rule the gate operationalizes; this proposal does NOT change the rule text.
- .claude/rules/file-bridge-protocol.md - contract preserved.
- bridge/gtkb-implementation-gate-friction-hygiene-006.md - Codex NO-GO addressed by this REVISED-3.
- bridge/gtkb-implementation-gate-friction-hygiene-005.md - REVISED-2; full technical content carried forward.
- The implementation-start gate hook source at `E:\GT-KB\scripts\implementation_start_gate.py` - target for IP-A and IP-B.
- The implementation-authorization helper `_validate_packet` at `E:\GT-KB\scripts\implementation_authorization.py` - target for IP-C.

## Prior Deliberations

- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - deterministic-plumbing principle.
- DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE - strategic self-improvement directive.
- DELIB-1469 - GT-KB self-measurement and self-improvement advisory.
- S349 self-diagnostic investigation (continuation, 2026-05-14 UTC).
- S350 owner direction: "Please continue with the 5 remaining Prime-actionable items".
- bridge/gtkb-implementation-gate-friction-hygiene-001.md through -006.md - full prior version chain.

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner AskUserQuestion answered "Commit Slice 3 only (mine), then revise next NO-GO".
- 2026-05-14 UTC, S350: owner prompt "Please continue with the 5 remaining Prime-actionable items".
- 2026-05-14 UTC, S349 continuation: owner AskUserQuestion answered "1 - File the hygiene slice now to formally close the friction class".

No new owner decision is required before review.

## Requirement Sufficiency

Existing requirements sufficient.

REVISED-3 is a narrow clause-preflight evidence repair. No new requirements; no new technical scope. The technical content of REVISED-2 is carried forward unchanged.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is not a bulk operation against the standing backlog. It carries forward the single-tracking-work_item IP-E from REVISED-2.

## Specification-Derived Verification Plan

For Loyal Opposition verification of the eventual post-implementation report (same as REVISED-2):

1. Run pytest on the two gate test files; 32 new tests PASS plus existing tests still PASS.
2. Run ruff check on the two modified source files and the two test files; zero errors.
3. Run the bridge applicability preflight for this bridge id; preflight_passed: true.
4. Run the ADR/DCL clause preflight for this bridge id; zero blocking gaps, exit 0.
5. End-to-end smoke test confirming the F1/F2/F3 decision-summary rows from -005.
6. Source inspection per the REVISED-2 checklist.
7. MemBase tracking work_item entry per IP-E.

## Recommended Commit Type

fix: - corrections to existing gate behavior across two source files. REVISED-3 adds no new technical scope; the recommendation matches REVISED-2.

## Bridge-Compliance Self-Check

- Non-empty Specification Links section with flat bullets; no triple-hash sub-headings inside; no parenthetical heading.
- Non-empty Prior Deliberations section.
- Non-empty Owner Decisions / Input section citing explicit AskUserQuestion answers.
- target_paths inline-JSON form; no protected narrative artifacts touched.
- Requirement Sufficiency section with exactly one operative state.
- Recommended Commit Type section present.
- Clause Scope Clarification section present.
- In-Root Placement Evidence section present (detector-recognized `E:\GT-KB` phrasing).
- All paths under `E:\GT-KB`.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
