NEW

# Implementation Proposal - Adopter Packaging + Clean-Adopter Validation (GTKB-ISOLATION-017)

bridge_kind: implementation_proposal
Document: gtkb-isolation-017-adopter-packaging
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-ISOLATION-CLOSEOUT-ISOLATION-CLOSEOUT-BATCH
Project: PROJECT-GTKB-ISOLATION-CLOSEOUT
Work Item: GTKB-ISOLATION-017

target_paths: ["scripts/clean_adopter_validation.py", "groundtruth-kb/src/groundtruth_kb/scaffold/adopter_package.py", "tests/scripts/test_clean_adopter_validation.py"]

This NEW proposal implements downstream adopter packaging and clean-adopter validation. Per `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT`, adopter projects (e.g., the active demos) must be able to consume GT-KB without depending on internal-only paths.

## Claim

Two parts: (1) a packaging-validation script that simulates a clean adopter checkout (no GT-KB platform files, only consumed surfaces) and verifies the adopter can run `gt project init`, `gt doctor`, and basic backlog/spec operations; (2) scaffold update to emit the minimum set of adopter-side files (no internal-platform leakage).

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - isolation contract.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` - lifecycle independence motivation.
- `GOV-GTKB-ADOPTION-ENFORCEMENT-001` - adoption governance.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - release-readiness contract.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `SPEC-AUQ-POLICY-ENGINE-001` - policy engine.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001` - WI tracked.
- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - batch-4 authorization.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` - foundational lifecycle independence.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved GTKB-ISOLATION-CLOSEOUT including this WI.

## Requirement Sufficiency

Existing requirements sufficient.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI; member of PROJECT-GTKB-ISOLATION-CLOSEOUT per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch4-four-project-authorizations.json`. Review-packet inventory: IP-1 (validation script) + IP-2 (scaffold update) + IP-3 (tests) single thread.

## Bridge INDEX Update Evidence

NEW filed; new top entry prepended.

## Proposed Scope

### IP-1: clean_adopter_validation.py

CLI: `python scripts/clean_adopter_validation.py [--adopter-name <name>] [--temp-dir <path>]`.

Steps:
1. Create temp directory; copy only GT-KB-installed-package files + scaffold templates (no internal `.gtkb-state`, no `bridge/`, no `independent-progress-assessments/`).
2. Run `gt project init --name <adopter-name>` in temp dir.
3. Run `gt project doctor` — must pass.
4. Run smoke ops: `gt backlog add ...`, `gt summary`, etc.
5. Report PASS/FAIL with per-step output.

### IP-2: Scaffold leakage check

In `groundtruth-kb/src/groundtruth_kb/scaffold/adopter_package.py`:
- Define the minimum set of files an adopter should receive (CLAUDE.md template, MEMORY.md template, .claude/rules/*, AGENTS.md template, etc.).
- Function to check that scaffold output contains only that set + no internal-platform paths.

### IP-3: Tests

Tests verify: validation script returns 0 on clean adopter, returns non-zero on adopter missing required pieces, scaffold leakage check correctly identifies leaked paths.

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| Clean-adopter validation passes on healthy scaffold | `test_clean_adopter_validation_passes` |
| Missing scaffold piece fails validation | `test_clean_adopter_missing_piece_fails` |
| `gt doctor` runs cleanly in temp adopter | `test_doctor_runs_in_temp_adopter` |
| Scaffold leakage check identifies internal paths | `test_scaffold_leakage_check_detects_internal` |
| Scaffold leakage check clean on minimum set | `test_scaffold_leakage_clean_minimum_set` |
| Backlog smoke ops work | `test_smoke_backlog_ops_in_temp_adopter` |

Run: `python -m pytest tests/scripts/test_clean_adopter_validation.py -v`.

## Acceptance Criteria

- IP-1, IP-2 landed; 6 tests PASS.
- Both preflights PASS.

## Risks / Rollback

- Risk: temp-dir cleanup may fail under Windows file locks. Mitigation: pytest tmp_path fixture + `Path.rmtree` with error handler.
- Risk: scaffold drift between this validation and actual `gt project init` paths. Mitigation: import the actual scaffold function rather than re-implementing.
- Rollback: remove the scripts.

## Recommended Commit Type

`feat` - new validation tool + scaffold check. ~150 LOC.
