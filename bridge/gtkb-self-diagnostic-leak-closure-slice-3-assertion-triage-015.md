# Implementation Report - Assertion Signal/Noise Triage (Slice 3, REVISED-5 implementation)

bridge_kind: implementation_report
Document: gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage
Version: 015
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350 (post-S349 continuation)
Reports: implementation of `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-013.md` (REVISED-5, GO at `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-014.md`)
target_paths: ["scripts/assertion_categorize.py", "scripts/assertion_retirement_workflow.py", "platform_tests/scripts/test_assertion_categorize.py", "platform_tests/scripts/test_assertion_retirement_workflow.py", ".claude/hooks/assertion-check.py"]

## Claim

REVISED-5 of Slice 3 of GTKB-SELF-DIAGNOSTIC-LEAK-CLOSURE has been implemented per the GO'd plan at `-013`. The four substantive corrections (F1 retire refusal, F2 `--since` removal, F3 `SPEC-1662` citation, F4 Ruff-clean) all landed verbatim. All 25 spec-derived tests pass, both mandatory mechanical preflights report zero blocking gaps, the narrative-artifact evidence check still passes, and the Codex skill-adapter parity check passes.

## Specification Links

Carried forward from `-013` (REVISED-5):

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge protocol observed throughout implementation; this report filed as `-015` NEW; INDEX entry preserved with prior versions intact.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all touched files inside `E:\GT-KB`; no Agent Red commingling.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this section cites every governing specification; no placeholder text.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the spec-to-test mapping below shows each Codex finding mapped to executed test results.
- SPEC-1662 (GOV-18: Assertion Quality Standard - meaningfulness over coverage) - F3 directly satisfied by replacing stale `SPEC-ASSERTION-CATEGORIZATION-001` references in three module docstrings.
- GOV-03 TEST-CLARITY - retirement-workflow `retire` refusal preserves test-fix-gate clarity; review-candidates and ask paths still surface chronic-noise candidates without ambiguity.
- GOV-15 TEST-FIX-GATE - retire path no longer mutates specs without governed-API + formal-artifact-approval evidence (F1 fix landed; raw-SQL `_retire_spec()` and `sqlite3` import both removed).
- GOV-STANDING-BACKLOG-001 - existing `WI-3294` tracks slice lineage; no new WI inserted in this report (carried forward from `-008` implementation per `-013` IP-G).
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - categorization output remains durable artifact under `.gtkb-state/assertion-triage/`.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - IP-6 glossary entries (already landed at `-009`) codify the four assertion-category concepts.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - assertion-state transitions remain surfaced for owner decision; `retire` lifecycle completes in the follow-on bridge.
- DCL-CONCEPT-ON-CONTACT-001 - glossary entries already verified at `-009`; no new concepts introduced.
- GOV-ARTIFACT-APPROVAL-001 - F1 fix preserves the formal-artifact-approval boundary by refusing retire absent governed packet evidence.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - one-at-a-time AUQ retirement design preserved in `apply_decision`'s packet-gated flow.
- DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE - REVISED-5 implementation is governed standing-backlog work; `WI-3294` lineage retained.
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-014.md - Codex GO authorizing this implementation.
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-013.md - REVISED-5 proposal whose IP-A through IP-D scope landed.
- bridge/gtkb-governed-spec-retirement-001.md - NEW follow-on bridge thread for the deferred governed-retirement work; cited durably in the Slice 3 refusal message at `scripts/assertion_retirement_workflow.py:158-163`.

## Prior Deliberations

- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-014.md - Codex GO at the GO'd version.
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-013.md - REVISED-5 proposal.
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-012.md - Codex NO-GO on REVISED-4 (audit-trail defect now closed; follow-on bridge filed).
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-010.md - Codex NO-GO on `-009` implementation report (F1-F4 originally identified).
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-008.md - Codex GO authorizing the slice's original scope.
- bridge/gtkb-governed-spec-retirement-001.md - NEW follow-on bridge for deferred retirement work.
- DELIB-1580 - Loyal Opposition verification of the backlog work-list retirement directive.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - one-at-a-time AUQ retirement design rationale.
- DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE - governed standing-backlog work guidance.
- DELIB-1469 - GT-KB Self-Measurement Advisory.
- INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM (Codex LO advisory, 2026-05-10) - recommendation A.

## Owner Decisions / Input

- S350 session, 2026-05-14 UTC: owner AskUserQuestion "Which Prime-actionable item should I start with first this session?" answered "Slice 3 (assertion-triage correction)". Authorizes this implementation under the existing GO at `-014`.
- 2026-05-14 UTC, S349 continuation: owner AskUserQuestion "How should REVISED-1 of Slice 3 handle the `retire` mutation path (Codex F1)?" Answer: "Defer retire to follow-on bridge (Recommended)". Authorized the F1 refusal path now landed at `scripts/assertion_retirement_workflow.py:158-163`.
- 2026-05-14 UTC, S349 continuation: owner AskUserQuestion "Which actionable bridge entry should I pick up next?" Answer: "Slice 4 REVISED-1 (Recommended)". Sequenced Slice 4 work after this Slice 3 closure.
- 2026-05-13 UTC, S349: owner AUQ "File both, sequenced" and "parallelize this work to the maximum extent possible".

No new owner decision is required before VERIFIED review.

## Requirement Sufficiency

Existing requirements sufficient.

This report implements the GO'd plan verbatim. No new requirements identified.

## Files Changed

| Path | Change |
|------|--------|
| `scripts/assertion_retirement_workflow.py` | F1: `apply_decision` raises `SystemExit` on `decision == "retire"` (lines 158-163) with refusal message naming `gtkb-governed-spec-retirement-001`; `_retire_spec()` function removed entirely; unused `import sqlite3` removed; `spec_update_result` simplified to literal `None` in the record and return tuple. |
| `scripts/assertion_categorize.py` | F2: `--since` argparse flag, the `since=args.since` call argument, and the `since: str \| None = None` parameter all removed from `categorize_all` (the flag was documented "advisory; not yet implemented"); F3: module docstring line 6 replaces `SPEC-ASSERTION-CATEGORIZATION-001` with `SPEC-1662 (GOV-18: Assertion Quality Standard)`. |
| `platform_tests/scripts/test_assertion_categorize.py` | F3: module docstring line 4 replaces stale SPEC citation with `SPEC-1662 (GOV-18: Assertion Quality Standard)`; F4 sweep: 9 pre-existing F841 `db_path = _build_fixture_db(...)` unused-variable assignments converted to side-effect-only calls. |
| `platform_tests/scripts/test_assertion_retirement_workflow.py` | F3: module docstring line 4 replaces stale SPEC citation; docstring bullet "spec retirement under decision='retire'" rewritten to "retire refusal pending governed follow-on bridge"; `test_apply_decision_retire_promotes_spec_to_retired` replaced with `test_apply_decision_retire_refuses_pending_governed_path` asserting `SystemExit` names `gtkb-governed-spec-retirement-001`, the refusal text contains "refusing retire", no specifications row is inserted, and no decision file is written. |
| `.claude/hooks/assertion-check.py` | F4: included in target_paths for the Ruff-clean verification; no content changes required (file is already Ruff-clean). |

**Pre-existing F841 sweep note:** The 9 F841 unused-variable fixes in `test_assertion_categorize.py` are slightly outside the explicit F1-F4 scope of REVISED-5 IP-A through IP-D, but they were required to satisfy the verification plan's step 2 (`python -m ruff check ... - expect zero errors`). Each fix replaced `db_path = _build_fixture_db(tmp_path, {"SPEC-xxx": runs})` with `_build_fixture_db(tmp_path, {"SPEC-xxx": runs})` (side-effect-only, since the helper writes the DB to `tmp_path/groundtruth.db` and the tests pass `tmp_path` directly to `categorize_all`). No test behavior changes; deterministic outputs unchanged.

## Spec-to-Test Mapping

| Spec / Finding | Test or Verification | Result |
|---|---|---|
| F1 (refuse retire pending follow-on) | `test_apply_decision_retire_refuses_pending_governed_path` | PASS — `SystemExit` raised; message contains `gtkb-governed-spec-retirement-001` and `refusing retire`; no specifications row inserted; no decision file written. |
| F1 (retire-path code removed) | Source inspection: grep for `_retire_spec` and `sqlite3` in `scripts/assertion_retirement_workflow.py` | PASS — zero hits. |
| F1 (accept/keep paths unchanged) | `test_apply_decision_accept_does_not_touch_spec`, `test_apply_decision_keep_does_not_touch_spec` | PASS (2/2). |
| F1 (input gating unchanged) | `test_apply_decision_rejects_packet_assertion_id_mismatch`, `test_apply_decision_rejects_packet_decision_mismatch` | PASS (2/2). |
| F2 (`--since` removed) | Source inspection: grep for `--since`, `args\.since`, `since:\s*str`, `since=` in `scripts/assertion_categorize.py` | PASS — zero hits. |
| F2 (categorization still deterministic) | `test_categorization_deterministic` plus all other categorize tests (10/10) | PASS. |
| F3 (`SPEC-1662` cited; stale SPEC absent) | Source inspection: grep for `SPEC-ASSERTION-CATEGORIZATION-001` in `scripts/` and `platform_tests/` | PASS — zero hits. |
| F4 (Ruff-clean across 5 touched files) | `python -m ruff check ...` | PASS — `All checks passed!`, exit 0. |
| Bridge audit-trail (follow-on bridge filed; closes Codex F1 of `-012`) | Live `bridge/INDEX.md` line 28: `NEW: bridge/gtkb-governed-spec-retirement-001.md` | PASS. |
| Applicability preflight | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage` | PASS — `preflight_passed: true`, `missing_required_specs: []`. |
| Clause preflight | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage` | PASS — `Blocking gaps: 0`, exit 0. |
| Narrative-artifact evidence | `python scripts/check_narrative_artifact_evidence.py --paths .claude/rules/canonical-terminology.md` | PASS — `narrative-artifact evidence (1 cleared)`. |
| Codex skill-adapter parity | `python scripts/generate_codex_skill_adapters.py --check` | PASS — `28 adapters current`. |

## Verification Commands and Observed Output

(All commands run from `E:\GT-KB`.)

1. `python -m pytest platform_tests/scripts/test_assertion_categorize.py platform_tests/scripts/test_assertion_retirement_workflow.py -v` → `25 passed in 0.84s`.
2. `python -m ruff check scripts/assertion_categorize.py scripts/assertion_retirement_workflow.py platform_tests/scripts/test_assertion_categorize.py platform_tests/scripts/test_assertion_retirement_workflow.py .claude/hooks/assertion-check.py` → `All checks passed!`, exit 0.
3. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage` → `preflight_passed: true`, exit 0.
4. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage` → `Blocking gaps: 0`, exit 0.
5. `python scripts/check_narrative_artifact_evidence.py --paths .claude/rules/canonical-terminology.md` → `PASS narrative-artifact evidence (1 cleared)`, exit 0.
6. `python scripts/generate_codex_skill_adapters.py --check` → `Codex skill adapters: PASS (28 adapters current)`, exit 0.
7. Grep `SPEC-ASSERTION-CATEGORIZATION-001` in `scripts/` and `platform_tests/` → zero hits.
8. Grep `--since|args\.since|since:\s*str|since=` in `scripts/assertion_categorize.py` → zero hits.
9. Source inspection: `_retire_spec` and `sqlite3` absent from `scripts/assertion_retirement_workflow.py`.
10. `bridge/INDEX.md` contains `NEW: bridge/gtkb-governed-spec-retirement-001.md` at line 28 (audit-trail proof closing Codex F1 of `-012`).

## Implementation-Discovered Friction (carried forward from `-009`/`-011` to Slice 4)

This implementation session reproduced the auth-packet thrashing already documented in `-009` and `-011`:

- The implementation-authorization `current.json` was overwritten multiple times by a concurrent `begin --bridge-id gtkb-self-diagnostic-leak-closure-slice-1-advisory-router` invocation. Evidence: `.gtkb-state/implementation-authorizations/by-bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router.json` mtime 02:46:02Z; `current.json` mtime 02:51:34Z; the by-bridge Slice 1 packet hardlinked with `current.json` (Links: 2).
- The originating process could not be conclusively identified in-session. The single-harness scheduled task is not registered (`single_harness_applicable: false` per `.gtkb-state/bridge-poller/single-harness-automation-state.json`); the cross-harness trigger reported `counterpart_active_session_present` and suppressed dispatch; yet `current.json` was rewritten with Slice 1 content at least twice during the implementation window (once before any `activate` call, then again after an `activate` succeeded).
- Workaround used: `python scripts/implementation_authorization.py activate --bridge-id gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage` was rerun immediately before each blocked edit batch. Slice 4's named-cache plus explicit `activate` recovery path performed exactly as designed — every recovery succeeded.
- This is the exact use case the Slice 4 hygiene proposal at `-003` (GO at `-004`) addresses; no new bridge thread is needed.

## Risks and Rollback

| Risk | Mitigation | Rollback |
|------|------------|----------|
| Existing chronic-noise candidates cannot be retired through this slice (intentional). | Refusal message names the follow-on bridge; `accept` and `keep` paths remain functional and tested. | `git revert` restores `_retire_spec()`, the `import sqlite3`, and the retire branch in `apply_decision`. |
| Callers expecting `--since` to filter assertions will receive an argparse error. | The flag was documented "advisory; not yet implemented" — no production caller depended on it. | `git revert` restores the argparse entry, parameter, and call argument. |
| F3 docstring citation change. | Pure documentation; no behavioral change. | `git revert`. |
| F4 9-line `db_path =` removals in `test_assertion_categorize.py`. | Pure cleanup; the assignments were never read; all 10 categorize tests still pass. | `git revert` restores prior assignments (would still be Ruff-warned, but harmless). |

## Recommended Commit Type

`fix:` — REVISED-5 corrects implementation defects on top of the in-flight slice. The diff shape is mostly negative-or-neutral: `_retire_spec()` removed, `--since` argparse/parameter/call argument removed, `sqlite3` import removed, 9 unused `db_path =` assignments cleaned; the only meaningful addition is the refusal `raise SystemExit(...)` block and one test method body. `fix:` matches the diff shape per `.claude/rules/file-bridge-protocol.md` § Conventional Commits Type Discipline.

## Bridge-Compliance Self-Check

- non-empty `## Specification Links` (flat bullets; no `###` sub-headings inside; no parenthetical heading).
- non-empty `## Prior Deliberations`.
- non-empty `## Owner Decisions / Input` citing the AskUserQuestion exchanges that authorized this work.
- `target_paths` consistent with all source/test/hook writes; no protected narrative artifacts touched in this implementation (canonical-terminology.md already landed at `-009`; narrative-artifact evidence check still PASSes).
- `## Requirement Sufficiency` with exactly one operative state.
- `## Recommended Commit Type` present.
- All paths under `E:\GT-KB`.
- 25/25 spec-derived tests PASS; both mandatory preflights pass; pre-existing 9-line F841 sweep called out explicitly above.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
