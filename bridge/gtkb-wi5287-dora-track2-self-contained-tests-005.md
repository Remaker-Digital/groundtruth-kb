REVISED
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6d64-3432-72d3-a8f2-bc19dd3932b0
author_model: GPT-5.5 Codex
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop Prime Builder bridge-revision worker; reasoning=xhigh; approval_policy=never

# Revised Defect-Fix Proposal - Make DORA Track 2 Reconciliation Tests Self-Contained

bridge_kind: prime_proposal
Document: gtkb-wi5287-dora-track2-self-contained-tests
Version: 005
Responds to: bridge/gtkb-wi5287-dora-track2-self-contained-tests-004.md
Supersedes proposal: bridge/gtkb-wi5287-dora-track2-self-contained-tests-001.md
Date: 2026-07-16 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5287

target_paths: ["platform_tests/scripts/test_dora_001b_track2_ingest.py"]
implementation_scope: test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

Version 004 rejected the otherwise sound one-file test-fixture repair because
the then-current project authorization contained unregistered forbidden-operation
tokens. That authorization defect is now corrected in canonical MemBase state.
This revision cites the same PAUTH ID at active version 3 and carries its exact
current envelope below. The implementation scope, target, runtime contract,
acceptance criteria, and rollback remain unchanged from version 001.

No owner authority is inferred from the earlier invalid envelope. The current
authorization remains subject to an independent GO, matching work-intent claim,
successful implementation-start packet, spec-derived verification, independent
VERIFIED verdict, and all separately applicable owner-contract gates.

## Corrected Project Authorization Evidence

Canonical command:

```text
python -m groundtruth_kb.cli projects show-authorization PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE --json
```

Observed current record:

- status: `active`
- version: `3`
- rowid: `733`
- project_id: `PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE`
- owner_decision_deliberation_id: `DELIB-202666274`
- included_work_item_ids: `null` (project-scoped; WI-5287 is not excluded)
- excluded_work_item_ids: `null`
- allowed_mutation_classes: `bridge`, `metadata`, `source`, `test`,
  `configuration`, `documentation`, `runtime_state`, `governance_evidence`
- forbidden_operations: `credential_lifecycle`, `destructive_cleanup`,
  `dispatcher_mutation`, `external_system_mutation`, `git_commit`,
  `git_history_rewrite`, `git_push`, `production_deployment`, `release`
- change_reason: `Reactivate the exact proposal-bound PAUTH with its prior
  specification set unchanged and normalize only forbidden-operation labels to
  the permanent taxonomy after the prior envelope failed closed on unknown
  tokens. Owner-contract restrictions outside the taxonomy remain mandatory
  under DELIB-202666274.`

The nine forbidden operations above are exact canonical names in
`config/governance/project-authorization-operation-taxonomy.toml`. None of the
eight unknown labels listed by version 004 remains. The envelope allows the
`test` mutation class, has no per-work-item inclusion restriction, and has no
WI-5287 exclusion. It therefore covers this proposal's sole test target at the
project-envelope layer. This proposal does not claim that PAUTH coverage alone
authorizes mutation; operation-time evaluation after a fresh GO and matching
claim remains mandatory.

## Current Baseline And Scope

- Current HEAD observed while revising: `42a252ab57b5a203e9406b626c741d897e8fb196`.
- Sole target is tracked and byte-clean at Git blob
  `facdb17e6fbf9a8b57e564e12f41b480a4765ab4`.
- Target SHA-256 is
  `35D2878C4F5AC9DA6DE90B4CEE98C3E39156FA55B5D720CF92804E787D1B1B9B`;
  size is `27329` bytes.
- Production source, release-gate source, credentials, external systems,
  dispatcher/TAFE state, authorization records, and concurrent worktree files
  are read-only inputs to the implementation.

## Specification Links

- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - The tests must
  reach the mocked Azure behavior they claim to exercise.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - The fixture repair must preserve
  production fail-closed configuration and all existing DORA outcomes.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - The active v3 PAUTH is only
  the project envelope; GO, claim, start, verification, and finalization gates
  remain required.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - Implementation
  must stop unless the post-GO implementation-start evaluator allows the exact
  operation and target.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - WI-5287 is covered by the active
  project-scoped authorization with test mutation allowed and no WI exclusion.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` - This revision carries the
  PAUTH's included specifications and the target-specific requirements.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH correction does not
  bypass independent bridge approval.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Protected test mutation requires a fresh
  independent GO, matching claim, and valid implementation-start packet.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH, project, work
  item, and machine-readable target metadata are explicit above.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - The exact scope
  and verification plan are linked to governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Independent verification
  must rerun the focused DORA and release-gate batches before VERIFIED.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - Fixture setup and exact
  matched, drift, confidence, and unknown outcomes remain deterministic.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - The PAUTH-vocabulary prerequisite is
  now satisfied before this revision requests a fresh GO.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Test data remains in-root and no
  live Azure or out-of-root dependency is introduced.
- `GOV-STANDING-BACKLOG-001` - WI-5287 remains the durable unit of work.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Proposal, test delta, report, and
  independent verdict remain the durable lifecycle packet.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - The NO-GO is answered by this
  append-only revision after its authorization prerequisite changed.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The defect and its correction remain
  governed artifacts rather than transient test output.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - The filing helper must insert complete
  current Prime Builder author/session provenance.

## Prior Deliberations

- `DELIB-202666274` - Owner authorization for required GT-KB modernization
  repairs while preserving bridge and mechanical-operation gates; this is the
  owner-decision record bound to PAUTH v3.
- `DELIB-20260715-MODERNIZATION-AUDIT-TRAIL-NONBLOCKING` - Audit defects remain
  repair obligations without weakening substantive behavior.
- `bridge/gtkb-wi5287-dora-track2-self-contained-tests-004.md` - The controlling
  NO-GO requiring taxonomy-clean PAUTH vocabulary before revision.

## Owner Decisions / Input

No new owner decision is asserted or required by this revision. It relies only
on the existing `DELIB-202666274` authority recorded by the active PAUTH. It
does not authorize credential lifecycle, destructive cleanup, dispatcher or
external-system mutation, Git commit/history rewrite/push, production
deployment, or release.

## Requirement Sufficiency

Existing requirements sufficient.

The production function already defines the application-owned mapping and
resource-group preconditions, and the affected tests already define their exact
unknown, matched, drift, confidence, and canonical-schema outcomes. The defect
is limited to deterministic test setup. No new or revised runtime requirement
is needed before implementation.

## Proposed Scope

1. Add deterministic pytest `monkeypatch` setup in the existing target file for
   `GTKB_DASHBOARD_AZURE_CONTAINER_APP_MAP` and
   `GTKB_DASHBOARD_AZURE_RESOURCE_GROUP` using non-secret staging values.
2. Ensure T8, T9, T10, T11, T13, and T14 reach their existing mocked
   `subprocess.run` paths and retain their exact assertions.
3. Preserve the tests proving failed or unavailable Azure CLI degrades to
   unknown; no real Azure call may occur.
4. Preserve all production and non-target files byte-for-byte.
5. Run the focused test file, Ruff on the target, and the combined
   release-candidate/DORA batch.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5287; DELIB-202666274; PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE version 3 rowid 733",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "python -m pytest platform_tests/scripts/test_dora_001b_track2_ingest.py -q --tb=short",
  "before_behavior": "Six tests exit at an unmet production configuration precondition before their mocked Azure behavior.",
  "after_behavior": "A test-owned fixture supplies deterministic non-secret application identifiers so each test reaches the behavior named by the test.",
  "self_descriptive_naming": "Fixture values use the production environment-variable names and a staging-only mapping.",
  "obsolete_guidance_disposition": "No production guidance is changed; only incomplete test setup is corrected.",
  "history_preservation": "The prior proposal, invalid GO, NO-ACTION, NO-GO, and this correction remain in the numbered bridge chain.",
  "baseline": {
    "head": "42a252ab57b5a203e9406b626c741d897e8fb196",
    "target_blob": "facdb17e6fbf9a8b57e564e12f41b480a4765ab4",
    "target_sha256": "35D2878C4F5AC9DA6DE90B4CEE98C3E39156FA55B5D720CF92804E787D1B1B9B",
    "target_size": 27329,
    "focused_failures_from_original_reproduction": 6
  },
  "expected_result": {
    "focused_failures": 0,
    "runtime_source_changes": 0,
    "live_azure_calls": 0,
    "ambient_azure_variables_required": 0
  },
  "essential_context_preservation": "Existing assertions continue to prove unavailable CLI, nonzero CLI, match, drift, confidence upgrade, and canonical-schema behavior.",
  "hard_invariants": [
    "no production validation relaxation",
    "no live Azure call",
    "no credential access or mutation",
    "no ambient-environment dependency",
    "no target outside platform_tests/scripts/test_dora_001b_track2_ingest.py",
    "no Git, release, deployment, dispatcher, TAFE, harness, role, or routing mutation"
  ],
  "fail_closed_conditions": [
    "latest bridge status is not a fresh independent GO",
    "matching work-intent claim or implementation-start packet is absent",
    "operation-time PAUTH evaluation denies the exact target",
    "target baseline is not attributable",
    "fixture mapping is absent or invalid",
    "mocked subprocess is not reached",
    "expected unknown, matched, drift, or confidence outcome changes",
    "focused or release-gate tests regress"
  ],
  "rollback": "Remove only the WI-5287 fixture setup and rerun the focused DORA suite."
}
```

## Specification-Derived Verification

| Specification | Command or inspection | Expected evidence |
|---|---|---|
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`; `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`; `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | After fresh GO, run `python scripts/bridge_claim_cli.py claim gtkb-wi5287-dora-track2-self-contained-tests --session-id <prime-session>` and `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5287-dora-track2-self-contained-tests --session-id <same-prime-session> --expires-minutes 60`, then validate the sole target. | Claim is held by the same Prime session; a named schema-v3 packet authorizes only the exact target. Any denial or packet defect stops work. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`; `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`; `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | `python -m pytest platform_tests/scripts/test_dora_001b_track2_ingest.py -q --tb=short` | All 18 tests pass without ambient Azure variables; T8-T14 retain exact unknown/matched/drift/confidence assertions and reach mocked subprocess behavior. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`; `GOV-STANDING-BACKLOG-001` | `python -m pytest platform_tests/scripts/test_release_candidate_gate.py platform_tests/scripts/test_dora_001b_track2_ingest.py -q --tb=short` | Combined relevant batch exits zero with exact observed count recorded in the implementation report. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and post-filing applicability and mandatory clause preflights. | `preflight_passed: true`, `missing_required_specs: []`, and zero blocking clause gaps. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001`; `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Inspect the diff and test fixture. | Only the declared in-root test target changes; fixture data is non-secret; runtime source and live services are untouched. |
| All linked specifications | `python -m ruff check platform_tests/scripts/test_dora_001b_track2_ingest.py` | Ruff exits zero on the only implementation target. |

## Acceptance Criteria

1. The current active PAUTH v3 remains taxonomy-clean, covers WI-5287 at the
   project layer, allows `test`, and has no WI-5287 exclusion at implementation
   start.
2. A fresh independent GO, matching claim, and valid named implementation-start
   packet authorize only the sole target before any protected mutation.
3. All target tests pass with both Azure mapping variables initially absent.
4. T8 and T9 still prove failed or unavailable Azure CLI degrades to unknown.
5. T10, T11, T13, and T14 still prove matched, drift, confidence-upgrade, and
   canonical-schema behavior with their existing exact assertions.
6. No runtime source, release-gate source, credential, external system,
   concurrent worktree, Git, release, or deployment mutation occurs.
7. Ruff and the combined release-gate/DORA batch pass, and the implementation
   report records exact commands and observed results for independent review.

## Risk / Rollback

Risk remains confined to fixture leakage or an over-broad environment mutation.
Use pytest `monkeypatch` so values are restored after each test and limit the
mapping to staging. Rollback removes only the attributable WI-5287 fixture
setup and reruns the focused suite. Any PAUTH, claim, packet, target-baseline,
or verification mismatch fails closed without adopting foreign changes.

## Pre-Filing Preflight Subsection

The governed revision helper must run both candidate preflights against this
completed content before publication. After filing, both canonical helpers are
rerun against the operative version 005. Required result: applicability passes
with no missing required specifications and the mandatory clause gate reports
zero blocking gaps.

## Bridge Filing

File this completed revision as the next append-only numbered entry,
`bridge/gtkb-wi5287-dora-track2-self-contained-tests-005.md`. No prior bridge
version is changed or removed. Dispatcher/TAFE state and numbered bridge files
remain canonical.

## Recommended Commit Type

`test` - deterministic fixture repair only. Commit remains separately governed
and is explicitly forbidden by this PAUTH.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
