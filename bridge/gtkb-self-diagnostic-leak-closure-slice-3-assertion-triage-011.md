# Implementation Proposal REVISED-4 - Assertion Signal/Noise Triage (Self-Diagnostic Leak Closure Slice 3)

bridge_kind: prime_proposal
Document: gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage
Version: 011
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S349 (continuation)
Addresses: NO-GO at `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-010.md` (F1 governance bypass, F2 unimplemented `--since`, F3 stale SPEC reference, F4 Ruff failures)
target_paths: ["scripts/assertion_categorize.py", "scripts/assertion_retirement_workflow.py", "platform_tests/scripts/test_assertion_categorize.py", "platform_tests/scripts/test_assertion_retirement_workflow.py", ".claude/hooks/assertion-check.py"]

## Claim

REVISED-4 of Slice 3 of GTKB-SELF-DIAGNOSTIC-LEAK-CLOSURE addresses the four Codex verification findings at `-010` without changing the core slice scope (assertion signal/noise categorization + retirement candidate review + canonical glossary entries). Four targeted corrections:

- **F1 fix:** `apply-decision --decision retire` now refuses with an explicit governance-gap error, deferring governed retirement to a follow-on bridge thread. The read-only, accept, and keep paths remain. Owner-approved deferral via AskUserQuestion in S349 (2026-05-14 UTC) chose this scope contraction over implementing governed retirement in this slice (Codex's option 2).
- **F2 fix:** the `--since` CLI argument is removed from `scripts/assertion_categorize.py` argparse. The `categorize_all()` function's `since` parameter is also removed. Time-bounded categorization becomes a separate follow-on if needed.
- **F3 fix:** `SPEC-ASSERTION-CATEGORIZATION-001` references in `scripts/assertion_categorize.py:6`, `platform_tests/scripts/test_assertion_categorize.py:4`, and `platform_tests/scripts/test_assertion_retirement_workflow.py:4` are replaced with `SPEC-1662 (GOV-18: Assertion Quality Standard)` plus the approved bridge reference.
- **F4 fix:** the 15 Ruff errors (unsorted imports, unused `sys` import, unused `db_path` assignments) are corrected; targeted `python -m ruff check` passes on all touched files.

The slice's IP-1 through IP-7 deliverables already landed under the `-008` GO are retained: tracking `WI-3294` remains in MemBase, the four canonical glossary entries remain in `.claude/rules/canonical-terminology.md` (no edit to the protected narrative artifact in this revision; the F3 fix touches `.py` files only), the assertion-triage skill remains registered, and the SessionStart advisory display remains wired into the hook.

## Why Now

Codex's NO-GO at `-010` identifies real safety and quality gaps in the `-009` implementation report. F1 in particular is a substantive governance boundary violation that must not ship as-VERIFIED. F2/F3/F4 are smaller but observable correctness gaps. Owner directive (AskUserQuestion, 2026-05-14 UTC) chose to defer the substantive governed-retirement work to a follow-on bridge rather than expand this slice; the chosen path closes F1 with a scope contraction.

The follow-on for governed retirement is queued as a separate bridge thread (`gtkb-governed-spec-retirement-001`, NEW in INDEX).

## Specification Links

The proposal's `-007` `## Specification Links` section is carried forward; no specs removed. One spec link added below to reflect the deferred-retirement contraction.

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge protocol observed. `bridge/INDEX.md` is updated with the REVISED-4 entry at the top of the slice-3 version list; no prior versions deleted or rewritten.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all target paths inside `E:\GT-KB`; no Agent Red commingling.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this section cites every governing specification; no placeholder text.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the verification plan maps each Codex finding to a concrete spec-derived test.
- SPEC-1662 (GOV-18: Assertion Quality Standard - meaningfulness over coverage) - directly governed; F3 fix replaces stale `SPEC-ASSERTION-CATEGORIZATION-001` references with this canonical citation.
- GOV-03 TEST-CLARITY - retirement-workflow's `retire` refusal preserves test-fix-gate clarity; chronic-noise candidates are still surfaced via `review-candidates` for owner review.
- GOV-15 TEST-FIX-GATE - retire path no longer mutates specs without governed-API + formal-artifact-approval evidence (F1 fix).
- GOV-STANDING-BACKLOG-001 - tracking `WI-3294` already in MemBase from `-008` implementation; no new WI inserted in REVISED-4. The follow-on governed-retirement bridge will insert its own tracking WI under that bridge's authorization.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - categorization output remains durable artifact under `.gtkb-state/assertion-triage/`.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - IP-6 glossary entries (already landed) codify the four assertion-category concepts.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - assertion-state transitions remain surfaced for owner decision; `retire` now requires the governed-retirement follow-on bridge to complete its lifecycle.
- DCL-CONCEPT-ON-CONTACT-001 - glossary entries already verified at `-009`; no new concepts introduced in REVISED-4.
- GOV-ARTIFACT-APPROVAL-001 - F1 fix preserves the formal-artifact-approval boundary by refusing retire absent governed packet evidence.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - one-at-a-time AUQ retirement design is itself a deterministic-services pattern; the F1 contraction defers its full materialization to a follow-on bridge.
- DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE - REVISED-4 itself is governed standing-backlog work; `WI-3294` continues to track this slice's implementation lineage.
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-008.md - Codex GO authorizing the slice's scope.
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-010.md - Codex NO-GO on `-009` implementation report; this REVISED-4 addresses F1, F2, F3, F4.

## Prior Deliberations

- S349 self-diagnostic investigation (this conversation, 2026-05-14 UTC).
- 2026-05-14 UTC, S349 continuation: owner AskUserQuestion answered "Defer retire to follow-on bridge (Recommended)" - chose F1 fix path: refuse retire decision, document follow-on.
- INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM (Codex LO advisory, 2026-05-10) - recommendation A.
- DELIB-1469 - GT-KB Self-Measurement Advisory.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE.
- DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE.
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-010.md - Codex NO-GO addressed here.
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-008.md - Codex GO on slice scope.
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-007.md - the proposal under that GO.

## Owner Decisions / Input

- 2026-05-14 UTC, S349 continuation: owner AskUserQuestion exchange selecting F1 fix path. Question: "How should REVISED-1 of Slice 3 handle the `retire` mutation path (Codex F1)?" Answer: "Defer retire to follow-on bridge (Recommended)". This authorizes the scope contraction in REVISED-4 and the follow-on bridge thread `gtkb-governed-spec-retirement-001`.
- 2026-05-13 UTC, S349: owner AUQ "File both, sequenced" + "parallelize this work to the maximum extent possible" (carried forward from `-007`).
- 2026-05-14 UTC, S349 continuation: owner direction "continue implementation under the existing Slice 3 GO" (carried forward).

## Requirement Sufficiency

Existing requirements sufficient.

REVISED-4 does not propose new requirements. It applies four targeted corrections to the implementation under the existing slice scope. The F1 contraction (defer retire) is enabled by `GOV-15 TEST-FIX-GATE` and `GOV-ARTIFACT-APPROVAL-001` - both already cited - which require formal-approval evidence for spec mutations. The governed-retirement work proceeds under a separate follow-on bridge with its own scope.

## Changes from -007

### F1 (defer retire to follow-on bridge)

- `scripts/assertion_retirement_workflow.py`:
  - `apply_decision()` validates the packet AS BEFORE (no change to packet validation), then for `decision == "retire"`, raises `SystemExit` with a clear governance-gap message citing the follow-on bridge.
  - Remove `_retire_spec()` function entirely (no spec mutation in this slice).
  - `accept` and `keep` paths unchanged; both write only the decision record to `.gtkb-state/assertion-triage/decisions/<assertion_id>.json` with no MemBase mutation.
- `platform_tests/scripts/test_assertion_retirement_workflow.py`:
  - Replace `test_apply_decision_retire_promotes_spec_to_retired` with `test_apply_decision_retire_refuses_pending_governed_path` that asserts `SystemExit` is raised with a message containing the governance-gap citation.
  - All other 14 tests unchanged.

### F2 (remove --since flag)

- `scripts/assertion_categorize.py`:
  - Remove `--since` from argparse (line 486-492 of the current file).
  - Remove `since` parameter from `categorize_all()` signature and remove it from the kwargs threading (line 292 and line 501).
  - Update docstring to remove the `--since` reference.

### F3 (replace stale SPEC reference)

Three file edits, each replacing `SPEC-ASSERTION-CATEGORIZATION-001` with `SPEC-1662 (GOV-18: Assertion Quality Standard)` plus the approved bridge reference:

- `scripts/assertion_categorize.py:6`.
- `platform_tests/scripts/test_assertion_categorize.py:4`.
- `platform_tests/scripts/test_assertion_retirement_workflow.py:4`.

### F4 (fix Ruff errors)

Run `python -m ruff check --fix` on the five touched files; manual review of the resulting changes; commit only the lint corrections (no behavior changes).

Expected fixes per Codex's enumeration:

- Unsorted import blocks in `.claude/hooks/assertion-check.py`, both new test files, both new scripts.
- Unused `sys` import in `platform_tests/scripts/test_assertion_categorize.py:16` (remove).
- Unused `db_path` assignments in `platform_tests/scripts/test_assertion_categorize.py:127, 147, 166, 185, 202, 220, 248, 266, 294` (remove the assignment; the function side-effect remains intentional).

## Proposed Scope

### IP-A: F1 - refuse retire pending governed-retirement follow-on bridge

`scripts/assertion_retirement_workflow.py` updated so `apply_decision(..., decision="retire", ...)` raises `SystemExit` with:

```
Refusing retire decision: governed spec retirement requires the follow-on bridge gtkb-governed-spec-retirement-001 to land first. Use `accept` or `keep` for this assertion, or wait for the follow-on bridge.
```

`_retire_spec()` function removed entirely (no raw SQL spec insert in this slice).

### IP-B: F2 - remove --since flag

`scripts/assertion_categorize.py` argparse no longer accepts `--since`; the `categorize_all()` function signature drops the `since` parameter; the module docstring no longer mentions `--since`.

### IP-C: F3 - cite SPEC-1662 only

Replace `SPEC-ASSERTION-CATEGORIZATION-001` with `SPEC-1662 (GOV-18: Assertion Quality Standard)` in:

- `scripts/assertion_categorize.py` module docstring.
- `platform_tests/scripts/test_assertion_categorize.py` module docstring.
- `platform_tests/scripts/test_assertion_retirement_workflow.py` module docstring.

### IP-D: F4 - lint-clean

Run `python -m ruff check --fix` on the five touched files. Confirm `python -m ruff check` reports no errors on those files.

## Tests

Updated test inventory after REVISED-4:

- IP-4a categorize: 10 tests (unchanged from `-009`).
- IP-4b retirement: 15 tests, one of which (`test_apply_decision_retire_promotes_spec_to_retired`) is replaced with `test_apply_decision_retire_refuses_pending_governed_path` asserting refusal.
- Total: 25 tests, all PASS expected.

## Verification Plan

For Codex re-verification:

1. `python -m pytest platform_tests/scripts/test_assertion_categorize.py platform_tests/scripts/test_assertion_retirement_workflow.py -v` - expect 25 PASS including the new `test_apply_decision_retire_refuses_pending_governed_path`.
2. `python -m ruff check scripts/assertion_categorize.py scripts/assertion_retirement_workflow.py platform_tests/scripts/test_assertion_categorize.py platform_tests/scripts/test_assertion_retirement_workflow.py .claude/hooks/assertion-check.py` - expect zero errors.
3. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage` - expect `preflight_passed: true`, no missing specs.
4. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage` - expect zero blocking gaps.
5. `python scripts/check_narrative_artifact_evidence.py --paths .claude/rules/canonical-terminology.md` - expect `PASS narrative-artifact evidence (1 cleared)` (carried forward from `-009`; glossary entries unchanged in REVISED-4).
6. `python scripts/generate_codex_skill_adapters.py --check` - expect `PASS` (skill registration unchanged).
7. `grep -E "SPEC-ASSERTION-CATEGORIZATION-001" scripts/ platform_tests/` - expect zero hits (F3 verification).
8. `grep -E "since" scripts/assertion_categorize.py` - expect no `--since` argparse occurrences (F2 verification; the word may appear in unrelated context).
9. Source inspection: `_retire_spec` function should NOT exist in `scripts/assertion_retirement_workflow.py` (F1 verification).
10. `python -m groundtruth_kb deliberations search "S349 assertion triage retire deferral"` - the AskUserQuestion deferral decision should be DA-harvestable next wrap.

## Risks and Rollback

- F1 fix risk: existing chronic-noise candidates cannot be retired through this slice; the workflow refuses them at execution time. Mitigation: `accept` and `keep` still let owners record decisions; the follow-on bridge implements governed retirement. Rollback: restore `_retire_spec()` and revert the refusal logic (low impact since no callers depend on retirement landing yet).
- F2 fix risk: callers expecting `--since` to filter will now error on unknown argument. Mitigation: no documented callers exist; the flag was advisory-only since IP-1. Rollback: restore argparse entry without the filter logic.
- F3 fix risk: none; docstring citation correction.
- F4 fix risk: import sort changes may interact with circular-import edge cases. Mitigation: targeted pytest run after Ruff fixes confirms behavior. Rollback: git revert the Ruff-fix commit.

## Sequenced Follow-Ons

- `gtkb-governed-spec-retirement-001` - new bridge thread (filed alongside this REVISED-4) for governed spec retirement: formal-artifact-approval-packet validation + `db.update_specification()` path + tests for missing/malformed/mismatched/non-approved packets. Out of scope for REVISED-4 per owner AUQ.
- Slice 4 (`gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene`) currently NO-GO at `-002`; REVISED-1 of Slice 4 must address Codex's three findings about multi-active-packet semantics. Separate thread.
- The implementation-discovered friction from this session (auth-packet thrashing under cross-harness trigger spawning; gate false-positives on `2>/dev/null` and `python -c "...sqlite3..."` reads) is documented in `-009` and should be folded into Slice 4 REVISED-1 scope.

## Recommended Commit Type

`fix:` - REVISED-4 corrects implementation defects on top of the in-flight slice; no new capability is added. The diff stat will be mostly negative-or-neutral (`_retire_spec` removed, `--since` removed, Ruff-clean imports). `fix:` matches the diff shape per the Conventional Commits discipline at `.claude/rules/file-bridge-protocol.md` § Conventional Commits Type Discipline.

## Bridge-Compliance Self-Check

- non-empty `## Specification Links` (flat bullets; no `###` sub-headings inside; no parenthetical heading).
- non-empty `## Prior Deliberations`.
- non-empty `## Owner Decisions / Input` citing the AskUserQuestion exchange.
- `target_paths` consistent with all planned writes; no protected narrative artifacts touched (canonical-terminology.md already landed at `-009`).
- `## Requirement Sufficiency` with exactly one operative state.
- `## Recommended Commit Type` present.
- explicit `Changes from -007` section.
- All paths under `E:\GT-KB`.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
