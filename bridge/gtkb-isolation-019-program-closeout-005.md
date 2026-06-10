REVISED
author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 2026-05-29-prime-builder-isolation-019-revised-2
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: explanatory output style; interactive Prime Builder session

# Implementation Proposal - Isolation Backstop Prerequisite (GTKB-ISOLATION-019) - REVISED-2

bridge_kind: prime_proposal
Document: gtkb-isolation-019-program-closeout
Version: 005 (REVISED)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-29 UTC
Responds-To: `bridge/gtkb-isolation-019-program-closeout-004.md` (NO-GO)

Project Authorization: PAUTH-PROJECT-GTKB-ISOLATION-CLOSEOUT-ISOLATION-CLOSEOUT-BATCH
Project: PROJECT-GTKB-ISOLATION-CLOSEOUT
Work Item: GTKB-ISOLATION-019

target_paths: ["scripts/isolation_program_backstop.py", "scripts/release_candidate_gate.py", "platform_tests/scripts/test_isolation_program_backstop.py"]

Recommended commit type: feat

## Revision Claim

This REVISED-2 carries forward the `-003` scope (backstop + release-gate integration; closeout report deferred) unchanged and resolves the single NO-GO finding from `-004`:

- **FINDING-P1-001 (NO-GO -004)**: Test target path inconsistent with live platform test layout. Resolved by retargeting all references from `tests/scripts/test_isolation_program_backstop.py` to `platform_tests/scripts/test_isolation_program_backstop.py` in `target_paths`, IP-3 scope, Specification-Derived Verification Plan commands, Acceptance Criteria, and Risk And Rollback section. The `platform_tests/scripts/` directory is the live convention per `scripts/release_candidate_gate.py:343-364` and existing platform-test files like `platform_tests/scripts/test_release_candidate_gate.py`.

Also added: a `## Requirement Sufficiency` subsection (required by `scripts/implementation_authorization.py` since the `-003` carry-forward; same proposal-shape concern Codex identified on sibling threads).

No scope, behavior contract, acceptance criterion, or risk/rollback semantic change relative to `-003`'s approved intent.

## Specification Links

- ADR-ISOLATION-APPLICATION-PLACEMENT-001
- DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT
- GOV-RELEASE-READINESS-GOVERNED-TESTING-001
- GOV-FILE-BRIDGE-AUTHORITY-001
- SPEC-AUQ-POLICY-ENGINE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-STANDING-BACKLOG-001
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001
- DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS

## Prior Deliberations

- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - owner-approved `PROJECT-GTKB-ISOLATION-CLOSEOUT`, including `GTKB-ISOLATION-019`.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` - lifecycle independence and single-active-application contract.
- `DELIB-1965` - compressed VERIFIED bridge thread for `gtkb-isolation-017-slice3-init-defaults-2026-05-02`.
- `DELIB-1969` - compressed VERIFIED bridge thread for `gtkb-isolation-017-slice2-registry-isolation`.
- `bridge/gtkb-isolation-019-program-closeout-002.md` (NO-GO) and `-003.md` (REVISED) - prior closeout-bundle split; carried forward in this revision.
- `bridge/gtkb-isolation-019-program-closeout-004.md` (NO-GO) - the operative NO-GO this REVISED-2 corrects (test-path lane mismatch).

## Owner Decisions / Input

No new owner decision required. The S350 project authorization remains in force. This revision corrects a mechanical test-layout error identified in NO-GO `-004`; it does not change scope, target behavior, or acceptance semantics relative to the prior `-003` revision.

## Findings Addressed

### FINDING-P1-001 (from -004) - Test target path is inconsistent with the live platform test layout

Response: Retargeted from `tests/scripts/test_isolation_program_backstop.py` (nonexistent directory) to `platform_tests/scripts/test_isolation_program_backstop.py` (the live convention) in:

- `target_paths` (line above).
- IP-3 (Proposed Scope -> Tests).
- Specification-Derived Verification Plan (pytest and ruff commands).
- Acceptance Criteria (AC3).
- Risk And Rollback (focused-tests deletion path).

The `platform_tests/scripts/` lane is established by:

- `scripts/release_candidate_gate.py` lists platform script tests under that path (lines 343-364 of that script).
- The existing release-gate test surface `platform_tests/scripts/test_release_candidate_gate.py` lives there.
- `Test-Path tests\scripts` returned False; `Test-Path platform_tests\scripts` returned True per the -004 verdict's evidence.

No new `tests/scripts` lane is created.

## Proposed Scope

### IP-1: Backstop script

Create `scripts/isolation_program_backstop.py`.

Required behavior:

1. Scan canonical GT-KB platform files for unauthorized `applications/<name>/` path references.
2. Allow explicitly authorized cross-scope references required by GT-KB operating-model documentation, bridge history, and test fixtures.
3. Emit JSON with `violations`, `allowed_references`, and `scanned_files`.
4. Exit non-zero if unauthorized references exist.
5. Stay read-only.

### IP-2: Release-candidate gate integration

Update `scripts/release_candidate_gate.py` to run the backstop as a non-deploying release-readiness check.

Required behavior:

1. Backstop failure fails the gate.
2. Missing backstop script fails the gate with a clear diagnostic.
3. Backstop command output is included in the release-gate result payload.

### IP-3: Tests

Add `platform_tests/scripts/test_isolation_program_backstop.py` (the active platform script-test lane, not `tests/scripts/`).

The tests must cover unauthorized reference detection, allowlist behavior, clean-tree exit code, JSON output shape, and release-gate invocation.

## Explicitly Deferred

- `docs/gtkb-isolation-program-closeout-report.md`.
- Any final claim that the isolation program is complete.
- Any retrospective phase/slice closeout table.

Future closeout-report proposal precondition: the bridge entries for the required sibling isolation work must be latest `VERIFIED`, and the new report must cite concrete live bridge versions.

## Requirement Sufficiency

Existing requirements sufficient. `GTKB-ISOLATION-019` is authorized under the active `PAUTH-PROJECT-GTKB-ISOLATION-CLOSEOUT-ISOLATION-CLOSEOUT-BATCH` (owner evidence `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS`). The backstop's behavior, allowlist semantics, JSON shape, and release-gate failure semantics fully specify the work; no new or revised requirement is required before implementation. This REVISED-2 strictly corrects the test-lane retargeting flagged in NO-GO -004 and does not change scope.

## Specification-Derived Verification Plan

| Behavior / spec obligation | Verification |
|---|---|
| Backstop detects unauthorized `applications/<name>/` references | `python -m pytest platform_tests/scripts/test_isolation_program_backstop.py -q --tb=short` |
| Backstop allows documented cross-scope references | `python -m pytest platform_tests/scripts/test_isolation_program_backstop.py -q --tb=short` |
| Backstop emits stable JSON and read-only exit codes | `python -m pytest platform_tests/scripts/test_isolation_program_backstop.py -q --tb=short` |
| Release-gate invokes the backstop and fails closed | `python -m pytest platform_tests/scripts/test_isolation_program_backstop.py -q --tb=short` |
| Changed scripts lint and format cleanly | `python -m ruff check scripts/isolation_program_backstop.py scripts/release_candidate_gate.py platform_tests/scripts/test_isolation_program_backstop.py` and `python -m ruff format --check ...` |

## Acceptance Criteria

1. `scripts/isolation_program_backstop.py` exists and is read-only.
2. `scripts/release_candidate_gate.py` runs the backstop and fails closed on violations or missing script.
3. `platform_tests/scripts/test_isolation_program_backstop.py` covers detection, allowlist, JSON shape, clean exit, and release-gate invocation.
4. No closeout report is created in this slice.
5. Applicability and clause preflights pass before and after filing.
6. (Pending Codex) Re-GO on this REVISED-2 at `-006`.

## Risk And Rollback

Risk: allowlist tuning may be too broad or too narrow. Mitigation: require explicit allowlist tests and JSON reporting of allowed references.

Risk: release-gate integration could add noise before the allowlist is tuned. Mitigation: gate output must include exact violating paths so failures are actionable.

Rollback: remove the release-gate call, delete `scripts/isolation_program_backstop.py`, and delete `platform_tests/scripts/test_isolation_program_backstop.py`. No documentation closeout artifact is affected.

## Pre-Filing Preflight Subsection

To be executed before submission for review:

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-019-program-closeout`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-isolation-019-program-closeout`

Expected: `preflight_passed: true`; `missing_required_specs: []`; clause preflight exit 0.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
