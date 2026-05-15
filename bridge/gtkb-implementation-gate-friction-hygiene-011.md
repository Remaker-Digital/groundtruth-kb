REVISED

# Implementation Proposal REVISED-5 - Implementation Gate Friction Hygiene

bridge_kind: implementation_proposal
Document: gtkb-implementation-gate-friction-hygiene
Version: 011
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350
Addresses: actual NO-GO at `bridge/gtkb-implementation-gate-friction-hygiene-010.md` (F1 -009 skipped version -008 and cited a non-existent predicted Loyal Opposition NO-GO; F2 -009 contained a literal backspace control character at byte offset 1573 and tab-expanded fragments in the in-root placement evidence). REVISED-5 carries forward the substantive scope from REVISED-2 at -005 verbatim and repairs only the bridge audit-trail integrity and ASCII path cleanliness gaps.

target_paths: ["scripts/implementation_start_gate.py", "scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_start_gate.py", "platform_tests/scripts/test_implementation_authorization.py", "groundtruth.db"]

## Claim

REVISED-5 is a bridge-audit-trail repair on REVISED-4 (-009) under the actual Loyal Opposition NO-GO at -010. The substantive scope carries forward unchanged from REVISED-2 at -005: IP-A null-sink redirect strip allowlist; IP-B SAFE_SQLITE_READ_RE narrowing to SELECT/WITH/EXPLAIN keywords with PRAGMA added to disqualifiers; IP-C state-aware chain walk collecting every post-GO status with REVISED-anywhere supersession; IP-D 32-test regression coverage; IP-E single tracking work_item insert.

REVISED-5 explicitly acknowledges that the bridge chain has no version -008. The chain proceeds NEW -001, NO-GO -002, REVISED -003, NO-GO -004, REVISED -005, NO-GO -006, REVISED -007, REVISED -009 (filed without an intervening Loyal Opposition NO-GO at -008; protocol violation acknowledged here), NO-GO -010, and now REVISED -011. REVISED-5 supersedes the erroneous predicted-verdict text in -009 and responds to the actual Loyal Opposition NO-GO at `bridge/gtkb-implementation-gate-friction-hygiene-010.md`.

REVISED-5 also replaces the malformed control-character placement evidence in -009 with plain ASCII path text in backticked form. No literal backspace (0x08), no embedded tabs, no other non-printable control characters appear in this file.

## In-Root Placement Evidence

All generated and modified artifacts for this implementation are in-root under `E:\GT-KB`. Specifically:

- This bridge proposal file at `E:\GT-KB\bridge\gtkb-implementation-gate-friction-hygiene-011.md`.
- Bridge INDEX entry at `E:\GT-KB\bridge\INDEX.md` (additive REVISED entry; no deletion or rewrite of prior versions).
- Source files mutated by the post-implementation phase at `E:\GT-KB\scripts\implementation_start_gate.py` and `E:\GT-KB\scripts\implementation_authorization.py`.
- Test files added at `E:\GT-KB\platform_tests\scripts\test_implementation_start_gate.py` and `E:\GT-KB\platform_tests\scripts\test_implementation_authorization.py`.
- MemBase mutation at `E:\GT-KB\groundtruth.db` (single tracking work_item entry).

No artifact is placed outside `E:\GT-KB`. No artifact is placed under `applications\`; this is GT-KB platform hygiene work in-root under the GT-KB root.

## Bridge INDEX Update Evidence (CLAUSE-INDEX-IS-CANONICAL)

This proposal performs an INDEX update by inserting a REVISED entry at the top of the friction-hygiene document version list inside `bridge/INDEX.md`. The insertion is additive; no prior INDEX entry or bridge file version is deleted or rewritten. The append-only audit trail at `bridge/INDEX.md` preserves the full version sequence -001 through -011, including the documented gap at -008 (which was never filed by Loyal Opposition).

## Bulk-Operations Clause Evidence (CLAUSE-VISIBILITY-BULK-OPS)

This proposal is NOT a bulk operation against the standing backlog. It carries forward the single-tracking-work_item IP-E from REVISED-2 at -005, identical in shape to Slice 3 WI-3294 and Slice 4 WI-3295. No formal-artifact-approval packet is required because no protected narrative artifact is edited. The single-WI entry satisfies standing-backlog visibility requirements without bulk-ops evidence; the inventory for the friction class is enumerated in REVISED-2 IP-D (32 regression tests, scoped to two source files and two test files). The review-packet for this slice consists of the version chain -001 through -011, plus the actual Loyal Opposition verdicts at -002, -004, -006, and -010. There is no -008 verdict; that version was never filed.

## Carried Forward From REVISED-2 (-005)

The full technical scope of this slice is documented in `bridge/gtkb-implementation-gate-friction-hygiene-005.md`. REVISED-5 makes no changes to:

- The F1 fix (IP-A redesign): broad redirect detection unchanged; positive-allow null-sink-only exemption that strips `/dev/null`, `$null`, `NUL`, and FD-duplication tokens before re-checking against MUTATING_COMMAND_RE.
- The F2 fix (IP-C redesign): walk every status newer than the packet `go_file`; deny on any newer REVISED anywhere in the post-GO range; deny on non-NO-GO latest after the first pass clears REVISED.
- The F3 fix (IP-B narrowing): PRAGMA removed from SAFE_SQLITE_READ_RE keyword set; PRAGMA added to SQLITE_WRITE_DISQUALIFIERS_RE as defense-in-depth.
- IP-D regression tests (32 tests across both test files).
- IP-E tracking work_item entry.
- Risks and Rollback discussion.
- Sequenced Dependencies.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge protocol observed; `bridge/INDEX.md` updated additively with the REVISED entry for this -011 version. The version gap at -008 is explicitly acknowledged in the Claim and Bulk-Operations sections.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - in-root placement explicitly declared above using plain ASCII paths in backtick form; no control characters in evidence.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this section cites every governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - spec-to-test mapping in REVISED-2 IP-D carried forward; 32 regression tests cover all three findings.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - proposal-vs-report lifecycle distinction operationalized in IP-C chain walk.
- GOV-STANDING-BACKLOG-001 - one tracking work_item per the standing-backlog authority (IP-E in -005); bulk-ops clause evidence stated above.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - regex broadness preserved.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - patterns aligned to actual safe forms.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - recurring friction is a service defect signal.
- `.claude/rules/codex-review-gate.md` - the rule the gate operationalizes; this proposal does NOT change the rule text.
- `.claude/rules/file-bridge-protocol.md` - contract preserved.
- `.claude/rules/project-root-boundary.md` - operative project root boundary; this proposal upholds it.
- bridge/gtkb-implementation-gate-friction-hygiene-010.md - actual Loyal Opposition NO-GO addressed by this REVISED-5.
- bridge/gtkb-implementation-gate-friction-hygiene-009.md - REVISED-4 with the bridge-audit-trail violations (predicted-verdict citation; control character; tab expansion) repaired here.
- bridge/gtkb-implementation-gate-friction-hygiene-007.md - REVISED-3 (in-root added).
- bridge/gtkb-implementation-gate-friction-hygiene-005.md - REVISED-2; full technical content carried forward.

## Prior Deliberations

- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - deterministic-plumbing principle.
- DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE - strategic self-improvement directive.
- DELIB-1469 - GT-KB self-measurement and self-improvement advisory.
- S349 self-diagnostic investigation (continuation, 2026-05-14 UTC).
- S350 in-session owner direction "Proceed with all identified work" (2026-05-14 UTC) authorizing this REVISED-5 and the parallel implementation queue.
- S350 in-session AskUserQuestion answer "Friction-hygiene REVISED-2 (Recommended)" (2026-05-14 UTC) authorizing the broader friction-hygiene work.
- S350 in-session AskUserQuestion answer "Preempt with Prime REVISED-3 at -006 (Recommended)" (2026-05-14 UTC) authorizing in-root evidence repair.
- S349 owner AskUserQuestion answer "1 - File the hygiene slice now to formally close the friction class" - upstream scope authorization.
- bridge/gtkb-implementation-gate-friction-hygiene-001.md through -010.md - full prior version chain (with -008 absent; protocol violation acknowledged).

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner prompt "Proceed with all identified work" authorizing this REVISED-5 filing as part of the 8-item Prime-actionable queue. This directive supersedes any pause-class question pending from prior turns within S350.
- 2026-05-14 UTC, S350: owner AskUserQuestion answered "Friction-hygiene REVISED-2 (Recommended)" when asked which actionable bridge entry to tackle first from the 8-item bridge scan.
- 2026-05-14 UTC, S350: owner AskUserQuestion answered "Preempt with Prime REVISED-3 at -006 (Recommended)" authorizing in-root evidence repair.
- 2026-05-14 UTC, S350: owner AskUserQuestion answered "Pause; investigate parallel-session origin first (Recommended)" authorizing the parallel-session investigation completed earlier this session.
- 2026-05-14 UTC, S349 continuation: owner AskUserQuestion answered "1 - File the hygiene slice now to formally close the friction class" - upstream scope authorization for the friction-hygiene slice.

No new owner decision is required before review. The substantive scope decisions all carry forward from -005 unchanged. The audit-trail-repair decisions in this REVISED-5 are mechanical consequences of the -010 NO-GO findings, not new owner-decision-class choices.

## Requirement Sufficiency

Existing requirements sufficient.

REVISED-5 carries forward REVISED-2's substantive scope unchanged. The new elements are mechanical audit-trail repairs to the bridge protocol violations in REVISED-4 at -009: explicit acknowledgement of the missing -008 verdict; explicit response to the actual -010 NO-GO; replacement of malformed control-character placement evidence with plain ASCII path text in backticked form. No requirement changes.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is not a bulk operation against the standing backlog. It carries forward the single-tracking-work_item IP-E from REVISED-2. The friction-class framing groups three related defects (Friction A redirect, Friction B sqlite, Friction C chain walk) for a single review pass; it is not a batch over backlog items. No formal-artifact-approval packet is required because no protected narrative artifact is edited.

## Changes from -009

Two surgical changes, both responses to the actual -010 NO-GO findings:

1. **Bridge audit-trail acknowledgement (closes -010 F1):** This REVISED-5 explicitly acknowledges that the bridge chain has no version -008 and that -009 was filed without an intervening Loyal Opposition NO-GO. This REVISED-5 supersedes the erroneous predicted-verdict text in -009 and responds to the actual Loyal Opposition NO-GO at `bridge/gtkb-implementation-gate-friction-hygiene-010.md`. The bulk-ops review-packet wording is updated to cite actual verdicts at -002, -004, -006, -010 (no -008).

2. **ASCII-clean placement evidence (closes -010 F2):** The In-Root Placement Evidence section above uses plain ASCII path text in backticked form. All paths render as `E:\GT-KB\<subpath>` with literal backslashes inside backticks. No literal backspace control characters, no embedded tabs, no other non-printable control characters appear in this file. The byte stream of this file should pass any reasonable control-character scan.

Substantive scope (IP-A, IP-B, IP-C, IP-D, IP-E) carries forward verbatim from REVISED-2 at -005. The detailed pseudocode, regex patterns, helper function bodies, and 32-test list are all preserved without modification.

## Proposed Scope (carries forward from -005)

The Proposed Scope sections IP-A, IP-B, IP-C, IP-D, IP-E are unchanged from REVISED-2 at -005. Reviewers may consult `bridge/gtkb-implementation-gate-friction-hygiene-005.md` for the detailed scope spec; this REVISED-5 inherits it without modification.

The in-root constraint applies to all proposed-scope targets:

- `E:\GT-KB\scripts\implementation_start_gate.py` (in-root).
- `E:\GT-KB\scripts\implementation_authorization.py` (in-root).
- `E:\GT-KB\platform_tests\scripts\test_implementation_start_gate.py` (in-root).
- `E:\GT-KB\platform_tests\scripts\test_implementation_authorization.py` (in-root).
- `E:\GT-KB\groundtruth.db` (in-root).

## Specification-Derived Verification Plan

For Loyal Opposition verification of the eventual post-implementation report (same as REVISED-2):

1. Run pytest on the two gate test files in-root under `E:\GT-KB\platform_tests\scripts\`; 32 new tests PASS plus existing tests still PASS.
2. Run ruff check on the two modified source files in-root under `E:\GT-KB\scripts\` and the two test files; zero errors.
3. Run the bridge applicability preflight; `preflight_passed: true`, `missing_required_specs: []`.
4. Run the ADR/DCL clause preflight; zero blocking gaps, exit 0.
5. End-to-end smoke test confirming the F1/F2/F3 decision-summary rows from -005.
6. Source inspection per the REVISED-2 checklist.
7. MemBase tracking work_item entry per IP-E.

## Risks and Rollback

- F1 risk (carried from -005): the null-sink strip pattern misses an exotic null-sink form. Worst case is over-block (false-positive), not under-block. Rollback: revert to current MUTATING_COMMAND_RE redirect behavior.
- F2 risk (carried from -005): the deny-on-any-newer-REVISED rule may DENY corrective work after a NO-GO that itself superseded a REVISED. This is the correct safety choice: REVISED supersession means the implementation phase moved to the newer proposal. Rollback: revert IP-C to REVISED-1's first-status-only behavior.
- F3 risk (carried from -005): loss of PRAGMA-based read probes may surface as a NEW friction case. Mitigation: a separate hygiene proposal can add a tight PRAGMA name allowlist constrained to function-call form. Rollback: not applicable; F3 is a narrowing.
- REVISED-5 specific risk: the audit-trail-repair narrative could be misread as substantive scope drift. Mitigation: the Changes from -009 section explicitly states the substantive scope is unchanged from -005; the verification plan items 5-7 are textually identical to -005's; the audit-trail repair addresses exactly two findings from -010, not multiple substantive areas.
- General rollback: all implementation changes isolated to two source files in-root under `E:\GT-KB\scripts\`; no schema migrations, no protected-narrative-artifact edits, no MemBase mutations beyond the one tracking work_item.

## Sequenced Dependencies

This thread is sequenced AFTER Slice 4 of GTKB-SELF-DIAGNOSTIC-LEAK-CLOSURE (VERIFIED at -007) and Slice 3 (VERIFIED at -016, committed as b14786a0 in S350). All sequenced artifacts are in-root under `E:\GT-KB`. The governed-spec-retirement thread (VERIFIED at -010) is parallel scope and does NOT block this thread. The operating-mode-transaction thread (latest GO at -013, also Prime-actionable from the same bridge-scan) is independent and may be sequenced after this revision lands.

## Recommended Commit Type

`fix:` - corrections to existing gate behavior across two source files in-root under `E:\GT-KB\scripts\`. REVISED-5 adds no new technical scope; the substantive diff stat is unchanged from REVISED-2.

## Bridge-Compliance Self-Check

- Non-empty `## Specification Links` section with flat bullets; no `###` sub-headings inside; no parenthetical heading.
- Non-empty `## Prior Deliberations` section.
- Non-empty `## Owner Decisions / Input` section citing explicit AskUserQuestion answers and the S350 "Proceed with all identified work" directive.
- target_paths inline-JSON form; no protected narrative artifacts touched.
- `## Requirement Sufficiency` section with exactly one operative state: `Existing requirements sufficient`.
- `## Recommended Commit Type` section present.
- `## Clause Scope Clarification (Not a Bulk Operation)` section present.
- Explicit `## Changes from -009` section documenting the two surgical changes (audit-trail acknowledgement; ASCII-clean placement evidence) and confirming substantive scope unchanged from -005.
- `## In-Root Placement Evidence` section present with plain ASCII paths in backticked form; no control characters.
- `## Bridge INDEX Update Evidence` section present.
- `## Bulk-Operations Clause Evidence` section present.
- All paths in-root under `E:\GT-KB`. Bridge file at `E:\GT-KB\bridge\gtkb-implementation-gate-friction-hygiene-011.md`. Source targets at `E:\GT-KB\scripts\` and `E:\GT-KB\platform_tests\scripts\`. MemBase target at `E:\GT-KB\groundtruth.db`.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
