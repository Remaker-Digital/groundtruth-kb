NEW

# Defect-Fix Proposal - Make DORA Track 2 reconciliation tests self-contained

bridge_kind: prime_proposal
Document: gtkb-wi5287-dora-track2-self-contained-tests
Version: 001
Author: Prime Builder Codex A
Date: 2026-07-15 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive; role=prime-builder; approval_policy=never; sandbox=danger-full-access

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5287

target_paths: ["platform_tests/scripts/test_dora_001b_track2_ingest.py"]

implementation_scope: test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Repair six DORA Track 2 tests that no longer reach the behavior they claim to
exercise. Production reconciliation correctly requires the application-owned
`GTKB_DASHBOARD_AZURE_CONTAINER_APP_MAP` and
`GTKB_DASHBOARD_AZURE_RESOURCE_GROUP` settings, but tests T8, T9, T10, T11,
T13, and T14 provide neither. Reconciliation therefore exits before the mocked
Azure subprocess path and returns zero counts.

The implementation will add deterministic test-owned environment setup for the
existing staging fixture. It will not relax production validation, read
credentials, contact Azure, or modify runtime source.

## Baseline And Scope

- HEAD at proposal preparation: `4ba39a438b84ec40c646cfc46c2741d6e7c6a60f`.
- Sole target is tracked and byte-clean at Git blob
  `facdb17e6fbf9a8b57e564e12f41b480a4765ab4`.
- Exact failing command:
  `python -m pytest platform_tests/scripts/test_dora_001b_track2_ingest.py -q --tb=short`.
- Current result inside the release batch: six reconciliation failures because
  the production guard reports both application-owned settings are required.
- `scripts/gtkb_dashboard/refresh_dashboard_db.py`, release-gate source,
  credentials, external systems, and concurrent files are read-only inputs.

## Specification Links

- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - The fixture repair must not
  weaken runtime fail-closed configuration or change DORA reconciliation
  semantics.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - The release
  test must mechanically execute the behavior named by each test rather than
  pass or fail before reaching it.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - Test setup and expected
  matched, drift, and unknown counts remain explicit and deterministic.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Protected test mutation requires an
  independent GO, matching claim, and implementation-start authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This proposal
  binds the exact target, invariants, and verification to governing contracts.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project, PAUTH, work
  item, and target path are explicit above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Independent VERIFIED
  must rerun the focused DORA suite and relevant release-gate batch.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Test data stays inside pytest
  fixtures and the application-owned mapping remains an explicit boundary.
- `GOV-STANDING-BACKLOG-001` - WI-5287 durably records this RC regression.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The observed regression is
  preserved as a governed work item, proposal, test change, report, and
  independent verification rather than remaining transient test output.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Proposal, focused test change,
  implementation report, and independent verdict form the durable packet.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - The verified DORA regression is
  reopened as WI-5287 rather than silently normalizing a red release gate.

## Prior Deliberations

- `DELIB-202666274` - The owner authorized all required GT-KB modernization
  repairs while preserving bridge review and mechanical-operation gates.
- `DELIB-20260715-MODERNIZATION-AUDIT-TRAIL-NONBLOCKING` - Audit defects remain
  repair obligations but do not justify weakening substantive behavior.

## Owner Decisions / Input

The owner authorized the full modernization program and directed the Prime
Builder to capture and continue fixing every blocker. No additional product
choice is needed because this proposal preserves the current production
configuration contract and changes only deterministic test setup. It does not
authorize staging, commit, push, deployment, release, credentials, dispatcher,
TAFE, harness, routing, role, or external-system mutation.

## Requirement Sufficiency

Existing requirements sufficient.

The production function already states the application-owned mapping and
resource-group precondition, and the six tests already state their expected
unknown, matched, drift, and confidence outcomes. The defect is solely that the
test fixture does not establish the production precondition before exercising
the mocked subprocess behavior. No new requirement or runtime behavior is
needed.

## Proposed Scope

1. Extend the existing DORA Track 2 test fixture or a narrowly named helper to
   set a deterministic JSON environment-to-container-app mapping for staging
   and a non-secret resource-group fixture value through `monkeypatch`.
2. Ensure each affected reconciliation test reaches its existing mocked
   `subprocess.run` behavior and retains its current assertions.
3. Preserve explicit tests for missing/failed Azure CLI degradation; the test
   configuration values do not make any external call real.
4. Preserve production behavior and every non-target file byte-for-byte.
5. Run the focused test file, Ruff on the target, and the release-gate pytest
   batch that originally exposed the regression.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5287 and DELIB-202666274",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "python -m pytest platform_tests/scripts/test_dora_001b_track2_ingest.py -q --tb=short",
  "before_behavior": "Six tests exit at an unmet production configuration precondition and never exercise their mocked Azure result.",
  "after_behavior": "The fixture supplies deterministic non-secret application-owned identifiers and each test reaches the behavior named by the test.",
  "self_descriptive_naming": "The fixture names the Azure container-app map and resource group exactly as the production contract does.",
  "obsolete_guidance_disposition": "No production guidance is retired or weakened; stale test setup is replaced with explicit application-owned context.",
  "history_preservation": "The verified DORA implementation and runtime source remain unchanged; WI-5287 records the regression.",
  "baseline": {
    "head": "4ba39a438b84ec40c646cfc46c2741d6e7c6a60f",
    "target_blob": "facdb17e6fbf9a8b57e564e12f41b480a4765ab4",
    "focused_failures": 6,
    "failure_mode": "reconciliation skipped before mocked subprocess behavior"
  },
  "expected_result": {
    "focused_failures": 0,
    "runtime_source_changes": 0,
    "live_azure_calls": 0,
    "ambient_azure_variables_required": 0
  },
  "essential_context_preservation": "Existing exact assertions continue to prove unavailable CLI, nonzero CLI, match, drift, confidence upgrade, and canonical-schema behavior.",
  "hard_invariants": [
    "no production validation relaxation",
    "no live Azure call",
    "no credential access or mutation",
    "no ambient-environment dependency",
    "no target outside the one clean tracked test file",
    "frozen modernization acceptance scope unchanged"
  ],
  "fail_closed_conditions": [
    "fixture mapping is absent or invalid",
    "mocked subprocess is not reached",
    "expected unknown, matched, drift, or confidence outcome changes",
    "focused or release-gate tests regress"
  ],
  "rollback": "Remove only the WI-5287 fixture setup and rerun the focused DORA suite."
}
```

## Spec-Derived Verification Plan

| Specification | Verification and expected result |
|---|---|
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Review the diff to prove runtime source is unchanged; run all DORA Track 2 tests and preserve every existing assertion. |
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | Prove T8, T9, T10, T11, T13, and T14 reach mocked subprocess behavior and report their existing exact counts. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | `python -m pytest platform_tests/scripts/test_dora_001b_track2_ingest.py -q --tb=short` exits zero without ambient Azure variables. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Inspect fixture values as non-secret local test data; no path or dependency crosses the GT-KB root or calls a live service. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability and ADR/DCL clause preflights pass with zero blocking gaps. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Independent LO reruns the focused suite, target Ruff check, and relevant release-gate batch before VERIFIED. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Verify valid GO, matching claim, and implementation-start packet before the target is edited. |

Exact implementation verification commands:

```text
python -m pytest platform_tests/scripts/test_dora_001b_track2_ingest.py -q --tb=short
python -m ruff check platform_tests/scripts/test_dora_001b_track2_ingest.py
python -m pytest platform_tests/scripts/test_release_candidate_gate.py platform_tests/scripts/test_dora_001b_track2_ingest.py -q --tb=short
```

## Acceptance Criteria

1. All tests in `test_dora_001b_track2_ingest.py` pass with both Azure mapping
   variables initially absent from the invoking process.
2. T8 and T9 still prove failed or unavailable Azure CLI degrades to unknown.
3. T10, T11, T13, and T14 still prove matched, drift, confidence-upgrade, and
   canonical-schema behavior with their existing exact assertions.
4. No runtime source, release-gate source, credential, external system, or
   concurrent worktree file changes.
5. The target passes Ruff and the combined release-gate/DORA focused batch.
6. The implementation report carries exact commands and observed counts to an
   independent Loyal Opposition reviewer.

## Risk / Rollback

Risk is confined to accidental fixture leakage between tests or over-broad
environment mutation. Use pytest `monkeypatch` so values are restored after
each test and keep the mapping limited to the staging environment used by this
file. Rollback removes the fixture setup only and reruns the focused suite.

## Bridge Filing

This proposal is filed as the first append-only numbered bridge file,
`bridge/gtkb-wi5287-dora-track2-self-contained-tests-001.md`; no prior version
is deleted or rewritten. Dispatcher/TAFE state plus the numbered bridge files
remain the governed workflow surfaces.

## Recommended Commit Type

`test` - the change repairs deterministic test setup without altering runtime
behavior. Any eventual commit remains separately mechanically authorized.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
