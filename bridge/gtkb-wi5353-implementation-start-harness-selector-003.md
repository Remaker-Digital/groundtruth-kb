NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: PB-AUTO-WI5353-20260716T2049Z
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: OpenAI Codex desktop Prime Builder worker; reasoning=xhigh; approval_policy=never
author_metadata_source: transcript-defined Prime Builder role plus canonical session-keyed worker envelope

# Implementation Report - WI-5353 Implementation-Start Harness Selector

bridge_kind: implementation_report
Document: gtkb-wi5353-implementation-start-harness-selector
Version: 003
Responds to: bridge/gtkb-wi5353-implementation-start-harness-selector-002.md
Date: 2026-07-16 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5353-IMPLEMENTATION-START-HARNESS-SELECTOR-20260716
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5353

target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_authorization_harness_selector.py"]

implementation_scope: source and focused tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix

## Implementation Claim

Implementation-start finalization now selects the acting harness's canonical worker-session document before validating role provenance. Selection uses explicit `GTKB_HARNESS_NAME` first, preserves no-selector behavior for headless dispatch, and otherwise derives only a deterministic interactive document selector from Claude or Codex runtime signals. The selected harness never supplies role authority; role still comes exclusively from the validated worker document.

The focused regression module proves that an exact Codex Prime Builder document can authorize start when a conflicting Loyal Opposition document shares the same session id, while missing, wrong-role, identity-mismatched, and globally ambiguous documents continue to fail closed.

## Authorization Evidence

- Latest status before implementation: `GO` at `bridge/gtkb-wi5353-implementation-start-harness-selector-002.md`.
- WI-5346 prerequisite: terminal `VERIFIED` at `bridge/gtkb-wi5346-restore-wi5254-pauth-amendment-preflight-008.md`.
- Work-intent claim: `go_implementation`, acquired `2026-07-16T20:54:11Z`, session `PB-AUTO-WI5353-20260716T2049Z`.
- Implementation-start packet hash: `sha256:d2960d8abd89b199f10e50bbbc7cb7bf72b68b683131ff323193da14192bc6f9`.
- Pre-start packet hash: `sha256:37b0081e9ebf3a7b85f5aa9cb6e80c62f6622892ffb65c8ee42c65e4c29818bf`.
- PAUTH operation-time validation authorized exactly the two `target_paths` above.

## Changes

- Added `_worker_harness_selector()` to `scripts/implementation_authorization.py`, matching the governed selector precedence already used by work-intent claim acquisition.
- Passed that selector to `resolve_worker_role_provenance()` during implementation-start finalization.
- Added six focused regression tests covering selected Prime success, unchanged no-selector ambiguity, selected Loyal Opposition denial, missing document denial, identity mismatch denial, and selector precedence/headless behavior.
- Preserved all preexisting WI-5346 source hunks. Formatter normalization was limited to the authorized source and test paths.

## Specification Links

- `GOV-SESSION-ROLE-AUTHORITY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`

## Owner Decisions / Input

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` backs the active WI-5353 PAUTH.
- The owner directed this worker to process exactly WI-5353 under session context `PB-AUTO-WI5353-20260716T2049Z`, preserve concurrent work, avoid Git finalization, and release the claim after handoff.

## Prior Deliberations

- `DELIB-20266094` - project/work-item linkage precedent carried by the approved proposal.
- `DELIB-20263293` - claim role-eligibility guard precedent.
- `DELIB-20261467` and `DELIB-2620` - interactive session role attribution precedent.
- `DELIB-20260711-WI5118-BY-REFERENCE-FINALIZATION-WAIVER` - prior bounded finalization precedent cited by the proposal.

## Specification-Derived Verification Results

| Specs / governing surfaces | Executed verification and observed result |
| --- | --- |
| `GOV-SESSION-ROLE-AUTHORITY-001` | Focused selector module passed 6 tests: selected Prime document succeeds; selected wrong-role, missing, and mismatched documents fail; no-selector ambiguity remains fail-closed. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Live GO, unique claim, exact worker provenance, active PAUTH, implementation-start packet, and both exact target validations passed before protected mutation. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Applicability preflight passed with no missing required or advisory specs; mandatory clause preflight reported zero blocking gaps. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The focused module plus three existing claim/start/provenance regressions passed 9 tests; exact commands and results are below. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | This numbered report preserves authorization hashes, exact path scope, observed evidence, residual failures, and the independent verification handoff. |
| `SPEC-AUQ-POLICY-ENGINE-001`, `GOV-STANDING-BACKLOG-001` | Existing PAUTH and the explicit WI-5353 owner directive were used without inventing another decision; WI-5353 remains the linked work-item carrier. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | All implementation and verification targets remained in `E:\GT-KB`; target authorization, Ruff, and native Python test surfaces were executed directly. |

## Commands Run

```text
python -m groundtruth_kb.cli bridge show gtkb-wi5353-implementation-start-harness-selector --json
python -m groundtruth_kb.cli bridge show gtkb-wi5346-restore-wi5254-pauth-amendment-preflight --json
python scripts/bridge_claim_cli.py claim gtkb-wi5353-implementation-start-harness-selector --session-id PB-AUTO-WI5353-20260716T2049Z
python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5353-implementation-start-harness-selector --session-id PB-AUTO-WI5353-20260716T2049Z
python scripts/implementation_authorization.py validate --target scripts/implementation_authorization.py
python scripts/implementation_authorization.py validate --target platform_tests/scripts/test_implementation_authorization_harness_selector.py
python -m pytest platform_tests/scripts/test_implementation_authorization_harness_selector.py -q --tb=short
python -m pytest platform_tests/scripts/test_implementation_authorization_harness_selector.py platform_tests/scripts/test_bridge_work_intent_registry.py::test_go_impl_allowed_for_uuid_session_with_prime_worker_document platform_tests/scripts/test_implementation_authorization.py::test_begin_cli_succeeds_when_work_intent_claim_held platform_tests/scripts/test_session_self_initialization.py::test_wi5328_worker_provenance_rejects_transcript_resolution_mismatch -q --tb=short
python -m pytest platform_tests/scripts/test_implementation_authorization_harness_selector.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_bridge_work_intent_registry.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization_harness_selector.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization_harness_selector.py
git diff --check -- scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization_harness_selector.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5353-implementation-start-harness-selector
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5353-implementation-start-harness-selector
```

## Observed Results

- Exact target authorization: PASS for both authorized paths.
- Focused selector pytest: `6 passed in 0.63s`.
- Focused plus existing provenance/start regressions: `9 passed in 3.07s`.
- Ruff check: `All checks passed!`.
- Ruff format check: `2 files already formatted`.
- `git diff --check`: PASS.
- Applicability preflight: PASS; `missing_required_specs=[]`, `missing_advisory_specs=[]`.
- Mandatory clause preflight: PASS; 5 clauses evaluated, 1 `must_apply`, zero evidence gaps and zero blocking gaps.
- Broader authorization/claim run: `185 passed, 9 failed in 47.81s`. All nine failures are existing WI-5346 PAUTH-envelope expectations in `platform_tests/scripts/test_implementation_authorization.py` (protected-target denial, mutation-class metadata, forbidden-operation denial, envelope drift, taxonomy drift, and retirement reconciliation); the new selector module and all bridge-work-intent-registry tests passed in that run. These failures are disclosed as concurrent shared-source state and are not claimed as WI-5353 regressions or repaired under this scope.

## File Evidence

- `scripts/implementation_authorization.py` SHA-256: `5FCE7F62131B8F601607D349B38BD962EC623FBE9E89DF536AA5EA92C33E6EEC`.
- `platform_tests/scripts/test_implementation_authorization_harness_selector.py` SHA-256: `4EFA6DEE10E42471CC9DD5FEDB3DB149C7A4E0E1A168F895547C0D688D44CCB1`.

## Acceptance Criteria Status

- PASS: WI-5346 is independently `VERIFIED`, its prior packet is expired, and a fresh WI-5353 packet authorized both exact targets.
- PASS: selected Codex Prime Builder provenance permits implementation start despite a same-session Loyal Opposition document.
- PASS: missing, wrong-role, identity-mismatched, and unselected ambiguous documents fail closed.
- PASS: claim kind, holder session, PAUTH operation-time, target-path, role, and existing start gates remain active in focused regression coverage.
- PASS: scoped pytest, Ruff check, Ruff format, diff check, applicability preflight, and clause preflight all pass.
- DISCLOSED: nine concurrent WI-5346 broad-suite failures remain outside this report's implementation claim.

## Explicit Non-Actions

- Did not alter role authority, worker envelope contents, dispatcher state, TAFE state, PAUTH data, MemBase, credentials, release, or deployment state.
- Did not stage, commit, push, or perform any Git finalization.
- Did not process another bridge thread or claim foreign WI-5346 implementation hunks as WI-5353 work.

## Risk And Rollback

Residual risk is limited to selector parity drift if future harness signals are added in only one caller. The focused precedence test makes current drift visible. Rollback is a scoped revert of the helper, call-site argument, and focused test module after normal bridge authorization; numbered bridge audit files remain append-only.

## Loyal Opposition Asks

1. Verify the selector is document-selection only and does not derive role from harness identity.
2. Re-run the focused 9-test command and both Ruff gates.
3. Treat the nine disclosed WI-5346 PAUTH failures as foreign concurrent state, then return `VERIFIED` if WI-5353 satisfies its approved scope; otherwise return `NO-GO` with concrete findings.
