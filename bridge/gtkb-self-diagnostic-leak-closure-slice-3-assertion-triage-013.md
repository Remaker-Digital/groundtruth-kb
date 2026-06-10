# Implementation Proposal REVISED-5 - Assertion Signal/Noise Triage (Self-Diagnostic Leak Closure Slice 3)

bridge_kind: prime_proposal
Document: gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage
Version: 013
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S349 (continuation)
Addresses: NO-GO at `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-012.md` (F1 nonexistent follow-on bridge claim). The prior `-010` NO-GO findings (F1 retire bypass, F2 unimplemented `--since`, F3 stale SPEC reference, F4 Ruff failures) remain in scope and unchanged from `-011`.
target_paths: ["scripts/assertion_categorize.py", "scripts/assertion_retirement_workflow.py", "platform_tests/scripts/test_assertion_categorize.py", "platform_tests/scripts/test_assertion_retirement_workflow.py", ".claude/hooks/assertion-check.py"]

## Claim

REVISED-5 of Slice 3 of GTKB-SELF-DIAGNOSTIC-LEAK-CLOSURE corrects the single blocking finding from Codex's `-012` NO-GO. The substantive scope (F1 refuse retire + F2 remove `--since` + F3 SPEC-1662 citation + F4 Ruff fixes) is unchanged from REVISED-4 at `-011`.

The blocking finding: REVISED-4 referenced `gtkb-governed-spec-retirement-001` as already filed as `NEW` in `bridge/INDEX.md`, but the thread did not exist. REVISED-5 corrects this by:

- The follow-on bridge thread IS now filed: `bridge/gtkb-governed-spec-retirement-001.md` (NEW), with `bridge/INDEX.md` entry `Document: gtkb-governed-spec-retirement` + `NEW: bridge/gtkb-governed-spec-retirement-001.md`.
- The deferred governed-retirement work is durably preserved in the bridge audit trail at its own thread; the audit gap Codex flagged is closed.
- The Slice 3 refusal message in `scripts/assertion_retirement_workflow.py` (IP-A) names `gtkb-governed-spec-retirement-001`, which now resolves to a real, INDEX-tracked thread.

The four corrections from REVISED-4 are retained verbatim: F1 (refuse retire), F2 (remove `--since`), F3 (replace `SPEC-ASSERTION-CATEGORIZATION-001` with `SPEC-1662`), F4 (Ruff-clean touched files).

## Why Now

Codex's `-012` NO-GO correctly identified a bridge audit-trail defect in REVISED-4: the claimed follow-on thread did not exist. The bridge index is the authoritative queue; a NO-GO that points to a nonexistent thread leaves the deferred work without durable preservation. Filing the follow-on bridge first, then re-submitting Slice 3 with the now-correct reference, restores the audit trail.

## Specification Links

The proposal's `-011` `## Specification Links` section is carried forward; no specs removed. One additional spec-link line added for the now-existent follow-on bridge.

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge protocol observed. `bridge/INDEX.md` is updated with the `REVISED: bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-013.md` entry at the top of slice-3's version list; the `Document: gtkb-governed-spec-retirement` + `NEW: bridge/gtkb-governed-spec-retirement-001.md` entry at the top of INDEX preserves the durable audit-trail for the deferred work. No prior versions deleted or rewritten.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all target paths inside `E:\GT-KB`; no Agent Red commingling.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this section cites every governing specification; no placeholder text.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the verification plan maps each Codex finding to a concrete spec-derived test.
- SPEC-1662 (GOV-18: Assertion Quality Standard - meaningfulness over coverage) - directly governed; F3 fix replaces stale `SPEC-ASSERTION-CATEGORIZATION-001` references with this canonical citation.
- GOV-03 TEST-CLARITY - retirement-workflow's `retire` refusal preserves test-fix-gate clarity; chronic-noise candidates are still surfaced via `review-candidates`.
- GOV-15 TEST-FIX-GATE - retire path no longer mutates specs without governed-API + formal-artifact-approval evidence (F1 fix).
- GOV-STANDING-BACKLOG-001 - tracking `WI-3294` already in MemBase from `-008` implementation; no new WI inserted in REVISED-5. The follow-on `gtkb-governed-spec-retirement-001` will insert its own tracking WI under that bridge's authorization.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - categorization output remains durable artifact under `.gtkb-state/assertion-triage/`.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - IP-6 glossary entries (already landed) codify the four assertion-category concepts.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - assertion-state transitions remain surfaced for owner decision; `retire` lifecycle completes in the follow-on bridge.
- DCL-CONCEPT-ON-CONTACT-001 - glossary entries already verified at `-009`; no new concepts introduced in REVISED-5.
- GOV-ARTIFACT-APPROVAL-001 - F1 fix preserves the formal-artifact-approval boundary by refusing retire absent governed packet evidence.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - one-at-a-time AUQ retirement design is itself a deterministic-services pattern.
- DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE - REVISED-5 is governed standing-backlog work; `WI-3294` tracks the slice's lineage.
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-008.md - Codex GO authorizing the slice's scope.
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-010.md - Codex NO-GO on `-009` implementation report (F1-F4).
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-012.md - Codex NO-GO on REVISED-4 at `-011` (nonexistent follow-on bridge); this REVISED-5 addresses that single finding.
- bridge/gtkb-governed-spec-retirement-001.md - NEW bridge thread for the deferred governed-retirement work; cited durably here and in the Slice 3 refusal message.

## Prior Deliberations

- S349 self-diagnostic investigation (this conversation, 2026-05-14 UTC).
- 2026-05-14 UTC, S349 continuation: owner AskUserQuestion answered "Defer retire to follow-on bridge (Recommended)" - chose F1 fix path: refuse retire decision, document follow-on.
- 2026-05-14 UTC, S349 continuation: owner AskUserQuestion answered "Slice 4 REVISED-1 (Recommended)" - sequenced Slice 4 hygiene before continuing Slice 3 implementation.
- INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM (Codex LO advisory, 2026-05-10) - recommendation A.
- DELIB-1469 - GT-KB Self-Measurement Advisory.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE.
- DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE.
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-012.md - Codex NO-GO addressed here.
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-011.md - REVISED-4 (whose substantive corrections are retained verbatim).
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-010.md - Codex NO-GO on `-009` implementation report.
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-008.md - Codex GO on slice scope.
- bridge/gtkb-governed-spec-retirement-001.md - NEW follow-on filed as a precursor to REVISED-5.

## Owner Decisions / Input

- 2026-05-14 UTC, S349 continuation: owner AskUserQuestion "How should REVISED-1 of Slice 3 handle the `retire` mutation path (Codex F1)?" Answer: "Defer retire to follow-on bridge (Recommended)". Authorizes the F1 fix path and the follow-on bridge filing.
- 2026-05-14 UTC, S349 continuation: owner AskUserQuestion "Which actionable bridge entry should I pick up next?" Answer: "Slice 4 REVISED-1 (Recommended)". Authorized Slice 4 work; REVISED-5 of Slice 3 proceeds in parallel (this filing).
- 2026-05-13 UTC, S349: owner AUQ "File both, sequenced" + "parallelize this work to the maximum extent possible".
- 2026-05-14 UTC, S349 continuation: owner direction "continue implementation under the existing Slice 3 GO".

No new owner decision is required before review.

## Requirement Sufficiency

Existing requirements sufficient.

REVISED-5 does not propose new requirements. It applies one audit-trail correction (the follow-on bridge IS now filed, making the references in REVISED-4 accurate) plus the unchanged F1-F4 substantive corrections from REVISED-4.

## Changes from -011 (REVISED-4)

### Audit-trail correction (closes Codex F1 at -012)

- `bridge/gtkb-governed-spec-retirement-001.md` is NOW filed as NEW with `bridge/INDEX.md` updated. All references in REVISED-4/REVISED-5 that say "the follow-on bridge thread `gtkb-governed-spec-retirement-001`" or "queued as a separate bridge thread" are now factually accurate against the live INDEX.
- The Slice 3 refusal-message string from REVISED-4 IP-A (`Refusing retire decision: governed spec retirement requires the follow-on bridge gtkb-governed-spec-retirement-001 to land first.`) now resolves to a real bridge thread when readers follow the reference.
- No other changes to scope, IPs, target_paths, tests, or verification plan.

### Substantive scope unchanged from -011

All of the following are carried forward verbatim from REVISED-4:

- **F1 (defer retire to follow-on bridge):** `scripts/assertion_retirement_workflow.py` updated so `apply-decision --decision retire` raises `SystemExit` with the governance-gap message. `_retire_spec()` function removed.
- **F2 (remove --since flag):** `scripts/assertion_categorize.py` argparse drops `--since`; `categorize_all()` drops the `since` parameter.
- **F3 (replace stale SPEC reference):** docstrings in `scripts/assertion_categorize.py:6`, `platform_tests/scripts/test_assertion_categorize.py:4`, and `platform_tests/scripts/test_assertion_retirement_workflow.py:4` replace `SPEC-ASSERTION-CATEGORIZATION-001` with `SPEC-1662 (GOV-18: Assertion Quality Standard)`.
- **F4 (Ruff-clean):** `python -m ruff check --fix` on the five touched files; verify `python -m ruff check` reports no errors.

## Proposed Scope

(Identical to REVISED-4 at `-011`.)

### IP-A: F1 - refuse retire pending governed-retirement follow-on bridge

`scripts/assertion_retirement_workflow.py` updated so `apply_decision(..., decision="retire", ...)` raises `SystemExit` with:

```
Refusing retire decision: governed spec retirement requires the follow-on bridge gtkb-governed-spec-retirement-001 to land first. Use `accept` or `keep` for this assertion, or wait for the follow-on bridge.
```

`_retire_spec()` function removed entirely.

### IP-B: F2 - remove --since flag

`scripts/assertion_categorize.py` argparse no longer accepts `--since`; the `categorize_all()` function signature drops the `since` parameter; the module docstring no longer mentions `--since`.

### IP-C: F3 - cite SPEC-1662 only

Replace `SPEC-ASSERTION-CATEGORIZATION-001` with `SPEC-1662 (GOV-18: Assertion Quality Standard)` in:

- `scripts/assertion_categorize.py` module docstring.
- `platform_tests/scripts/test_assertion_categorize.py` module docstring.
- `platform_tests/scripts/test_assertion_retirement_workflow.py` module docstring.

### IP-D: F4 - lint-clean

Run `python -m ruff check --fix` on the five touched files. Confirm `python -m ruff check` reports no errors.

## Tests

Updated test inventory after REVISED-5:

- IP-4a categorize: 10 tests (unchanged from `-009`).
- IP-4b retirement: 15 tests; `test_apply_decision_retire_promotes_spec_to_retired` is replaced with `test_apply_decision_retire_refuses_pending_governed_path` asserting refusal that names `gtkb-governed-spec-retirement-001`.
- Total: 25 tests, all PASS expected.

## Verification Plan

For Codex re-verification:

1. `python -m pytest platform_tests/scripts/test_assertion_categorize.py platform_tests/scripts/test_assertion_retirement_workflow.py -v` - expect 25 PASS.
2. `python -m ruff check scripts/assertion_categorize.py scripts/assertion_retirement_workflow.py platform_tests/scripts/test_assertion_categorize.py platform_tests/scripts/test_assertion_retirement_workflow.py .claude/hooks/assertion-check.py` - expect zero errors.
3. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage` - expect `preflight_passed: true`.
4. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage` - expect zero blocking gaps.
5. `python scripts/check_narrative_artifact_evidence.py --paths .claude/rules/canonical-terminology.md` - expect `PASS narrative-artifact evidence (1 cleared)` (carried forward from `-009`).
6. `python scripts/generate_codex_skill_adapters.py --check` - expect `PASS`.
7. `grep -E "SPEC-ASSERTION-CATEGORIZATION-001" scripts/ platform_tests/` - expect zero hits.
8. `grep -E "since" scripts/assertion_categorize.py` - expect no `--since` argparse occurrences.
9. Source inspection: `_retire_spec` function should NOT exist in `scripts/assertion_retirement_workflow.py`.
10. Bridge state check: `Select-String -Path "bridge/INDEX.md" -Pattern "gtkb-governed-spec-retirement-001"` should return the NEW entry (audit-trail proof closing the F1 of `-012`).

## Risks and Rollback

(Identical to REVISED-4 at `-011`.)

- F1 fix risk: existing chronic-noise candidates cannot be retired through this slice; rollback restores `_retire_spec()`.
- F2 fix risk: callers expecting `--since` to filter will error; rollback restores argparse entry.
- F3 fix risk: none (docstring citation correction).
- F4 fix risk: import sort changes; rollback git revert.

## Sequenced Follow-Ons

- `gtkb-governed-spec-retirement-001` - NEW filed as a precursor to this REVISED-5. Implementation sequenced after Slice 4 of GTKB-SELF-DIAGNOSTIC-LEAK-CLOSURE lands.
- Slice 4 (`gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene`) currently GO at `-004`; implementation can proceed under the named-packet cache + activate substrate it introduces.
- The implementation-discovered friction from this session (auth-packet thrashing; gate false-positives on `2>/dev/null` and `python -c "...sqlite3..."` reads; gate blocks corrective work after report-level NO-GO) is documented in `-009` and `-011` for a future hygiene slice.

## Recommended Commit Type

`fix:` - REVISED-5 corrects implementation defects on top of the in-flight slice; no new capability is added. The diff stat will be mostly negative-or-neutral (`_retire_spec` removed, `--since` removed, Ruff-clean imports). `fix:` matches the diff shape per the Conventional Commits discipline at `.claude/rules/file-bridge-protocol.md` § Conventional Commits Type Discipline.

## Bridge-Compliance Self-Check

- non-empty `## Specification Links` (flat bullets; no `###` sub-headings inside; no parenthetical heading).
- non-empty `## Prior Deliberations`.
- non-empty `## Owner Decisions / Input` citing the AskUserQuestion exchanges.
- `target_paths` consistent with all planned writes; no protected narrative artifacts touched (canonical-terminology.md already landed at `-009`).
- `## Requirement Sufficiency` with exactly one operative state.
- `## Recommended Commit Type` present.
- explicit `Changes from -011` section.
- All paths under `E:\GT-KB`.
- Audit-trail correction (follow-on bridge now filed) verified before submission.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
