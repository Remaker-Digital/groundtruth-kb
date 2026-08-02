NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: reasoning_effort=default; thread_source=automation
author_metadata_source: x-codex-turn-metadata

bridge_kind: prime_proposal
Document: gtkb-wi5553-modernization-workflow-spec-binding
Version: 001
Date: 2026-08-01 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5553
related_work_items: ["WI-5315", "WI-5333", "WI-5395", "WI-5873"]

target_paths: ["groundtruth-kb/src/groundtruth_kb/modernization/workflow.py", "platform_tests/scripts/test_modernization_end_to_end_workflow.py", "config/governance/modernization-release-candidate.json"]
implementation_scope: modernization_workflow_canonical_spec_authority_binding
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
KB mutation: none; this proposal performs no KB mutation.

# WI-5553 Implementation Proposal — Bind the Modernization Workflow to Canonical Specification Authority

## Summary

Pull WI-5553 forward to remove the phantom production authority `SPEC-E2E-001` without inventing a specification. The string is a disposable rehearsal fixture identifier, but the production workflow and its release-candidate acceptance lane currently expose it as though it were canonical specification authority. Canonical lookup finds no such specification. The existing owner-approved `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` is sufficient authority for production candidate assessment, supported by the verified-testing and artifact-evaluability constraints below.

The repair separates local rehearsal identity from production authority, binds the `AT-END-TO-END-WORKFLOW` manifest row to the live GOV ID, and proves the source/manifest/canonical-MemBase relationship mechanically. It does not seed a copy of the canonical GOV into the disposable rehearsal database, create or amend any formal specification, change the existing acceptance timeout, or claim that unrelated current test failures are fixed.

The governed proposal is filed as the next numbered append-only artifact `bridge/gtkb-wi5553-modernization-workflow-spec-binding-001.md`; it does not delete or rewrite any prior bridge version.

## Current Evidence and Preimages

- `groundtruth-kb/src/groundtruth_kb/modernization/workflow.py` is tracked and clean at SHA-256 `EBAFBE854E5D26CF2AFC023AA61A6F7C1EEBA6986784B3E139263DA580E5FF64`. It declares `SPEC_ID = "SPEC-E2E-001"` and uses that value for disposable rehearsal spec/work-item/PAUTH/report construction.
- `platform_tests/scripts/test_modernization_end_to_end_workflow.py` is tracked and clean at SHA-256 `86D18E9F628C644A80BBD969716E6BEF133C4667483ADCA5B1270CC7970088D5`.
- `config/governance/modernization-release-candidate.json` is tracked and clean at SHA-256 `203824F57C4FF8700E59B06864047C2F3CDD8436F70BB3730DCC0FDC788AF87D`. Its `AT-END-TO-END-WORKFLOW` row currently identifies the command, required path, and existing 900-second activity budget but no canonical specification authority.
- Exact canonical lookup for `SPEC-E2E-001` is absent. Exact lookup for `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` resolves the owner-approved live governance record.
- A current strict physical scan found no live GO or active claim overlapping any of the three targets. The related WI-5315 carrier is latest NO-GO with only an expired historical draft claim.

## Proposed Design

### Slice A — Separate rehearsal identity from production authority

In `workflow.py`, replace the ambiguous module-level `SPEC_ID` with two explicit concepts:

1. `REHEARSAL_SPEC_ID = "SPEC-E2E-001"`, used only inside the disposable isolated rehearsal database and its synthetic proposal/report evidence.
2. `WORKFLOW_AUTHORITY_SPEC_IDS = ("GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",)`, used only when assessing the production release-candidate manifest and emitting production authority evidence.

Do not insert, counterfeit, copy, or otherwise seed canonical GOV bytes into the rehearsal database. The local fixture must remain clearly synthetic; production authority must remain a canonical in-root MemBase lookup.

### Slice B — Bind the acceptance manifest

Add an exact `spec_ids` field, or the manifest's canonical equivalent, to `AT-END-TO-END-WORKFLOW` containing only `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`. Preserve the existing command, required path, and timer value byte-for-byte except for unavoidable formatting caused by the approved writer/formatter. No timeout, throttle, retry, fan-out, or concurrency policy change is in scope.

### Slice C — Fail closed and emit the binding

In `_candidate_assessment()`:

- require the acceptance row's normalized authority set to equal `WORKFLOW_AUTHORITY_SPEC_IDS` exactly;
- fail closed on a missing, empty, duplicate, malformed, unknown, or extra production authority ID;
- resolve every production authority through the canonical platform MemBase rather than the disposable rehearsal database; and
- emit the normalized authority IDs and resolution evidence in the candidate assessment so verification can distinguish canonical production authority from the local rehearsal fixture.

### Slice D — Regression coverage

Extend the focused workflow test module to prove:

- every production authority ID resolves canonically and the exact manifest/source sets match;
- `REHEARSAL_SPEC_ID` is explicitly local and is not accepted as production authority;
- candidate assessment fails closed for missing, unknown, extra, duplicate, or source/manifest-drifted IDs; and
- the successful end-to-end result reports the canonical authority binding while retaining all existing independent-review, recovery, exact-once mutation, isolation, and non-impairment assertions.

## Scope Boundaries and Related Work

- WI-5315 remains the related modernization workflow adoption lane. This proposal repairs its authority prerequisite; it does not claim the predecessor's current 5/8 acceptance run is complete.
- WI-5333 and WI-5873 already own the repository-wide 30-second acceptance-watchdog mismatch. Current direct execution required the manifest's existing activity budget and completed in 148.33 seconds; no duplicate timer WI or timeout implementation is created here.
- WI-5395 owns the existing tamper-diagnostic text mismatch. Two additional current failures arise because the disposable rehearsal lacks `config/governance/spec-applicability.toml`; those are foreign baseline drift and remain outside this three-target authority-binding scope.
- TAFE/dispatcher activation or mutation, Git mutation, formal artifact mutation, `groundtruth.db` mutation, credential work, deployment, release, and external-system mutation are out of scope.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5553; DELIB-20260710-GTKB-MODERNIZATION-NONIMPAIRMENT-GOV-APPROVAL; DELIB-202667714; PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 with DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 and DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001",
  "primary_route": "Independent bridge GO, exact work-intent claim, schema-v3 implementation-start packet, three-target implementation, implementation report, and independent VERIFIED.",
  "before_behavior": "The workflow exposes SPEC-E2E-001 as a generic SPEC_ID even though it exists only as a disposable rehearsal fixture and has no canonical specification record; the production acceptance manifest declares no exact authority binding.",
  "after_behavior": "The rehearsal fixture and production authority have distinct names and stores; production assessment requires the manifest and source to bind exactly to the live modernization non-impairment GOV and emits canonical resolution evidence.",
  "self_descriptive_naming": "REHEARSAL_SPEC_ID names the isolated synthetic record and WORKFLOW_AUTHORITY_SPEC_IDS names the canonical production authority tuple.",
  "obsolete_guidance_disposition": "The ambiguous SPEC_ID name and implicit production-authority inference are removed; historical bridge and test evidence is preserved, and unrelated timeout or tamper remediation remains with its existing work items.",
  "history_preservation": "All existing bridge, MemBase, deliberation, manifest-history, and Git evidence remains preserved; this proposal creates no formal specification and rewrites no numbered bridge artifact.",
  "baseline": {
    "workflow_sha256": "EBAFBE854E5D26CF2AFC023AA61A6F7C1EEBA6986784B3E139263DA580E5FF64",
    "focused_test_sha256": "86D18E9F628C644A80BBD969716E6BEF133C4667483ADCA5B1270CC7970088D5",
    "manifest_sha256": "203824F57C4FF8700E59B06864047C2F3CDD8436F70BB3730DCC0FDC788AF87D",
    "canonical_state": "SPEC-E2E-001 absent; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 live and owner-approved"
  },
  "expected_result": {
    "authority_binding": "Source tuple and AT-END-TO-END-WORKFLOW manifest authority set match exactly and resolve canonically.",
    "fixture_boundary": "SPEC-E2E-001 remains an explicitly local rehearsal identifier and cannot satisfy production authority.",
    "evidence": "Candidate assessment reports exact authority IDs and canonical resolution status while existing non-impairment behavior remains intact."
  },
  "rollback": {
    "instructions": "Revert only the approved source/test hunks and remove only the manifest authority field through the governed lifecycle.",
    "verification": "Rerun focused authority-binding tests, manifest validation, end-to-end workflow evidence, Ruff lint, and Ruff format checks."
  },
  "hard_invariants": [
    "No canonical GOV bytes are inserted into the disposable rehearsal database.",
    "No formal specification, MemBase row, groundtruth.db, TAFE/dispatcher state, Git state, index lock, deployment, release, or external system is mutated.",
    "The existing manifest command, required path, and timer value are not changed by this authority-binding repair.",
    "Independent review, recovery, exact-once mutation, isolation, and production-deployment separation assertions remain load-bearing."
  ],
  "fail_closed_conditions": [
    "Missing, stale, or mismatched GO, claim, PAUTH, schema-v3 start packet, target preimage, or Prime Builder role evidence.",
    "Missing, empty, malformed, duplicate, unknown, extra, or source/manifest-drifted production authority ID.",
    "Any implementation attempts to treat REHEARSAL_SPEC_ID as production authority or seed canonical GOV bytes into the rehearsal database.",
    "Any target falls outside the declared three-path cohort or outside E:/GT-KB."
  ],
  "essential_context_preservation": "The design preserves the owner-approved modernization non-impairment authority, WI-5315 workflow-adoption context, WI-5333/WI-5873 timer ownership, WI-5395 tamper ownership, current clean preimages, and the full independent bridge lifecycle."
}
```

## Specification Links

- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — blocking production authority. The workflow must prove the frozen acceptance contract without weakening existing behavior.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — blocking. Production authority must map to executed, specification-derived tests.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` — blocking. The manifest/source authority relationship must be mechanically evaluable rather than implied by a missing ID.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — blocking. The proposal requires independent GO, exact claim/start, implementation report, and independent VERIFIED.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — blocking. WI-5553 inherits the active list-free Assurance project PAUTH; legacy WI approval metadata is noncontrolling.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — blocking. All three targets must remain allowed at implementation time.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — blocking. The exact project, PAUTH, WI, and target cohort are declared above.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — blocking. This section identifies every governing authority used by the proposal.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — blocking. The production authority binding is enforced in source, manifest, and tests.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — blocking. The proposal, both code/test targets, the manifest, and all live dependencies remain in-root under `E:/GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory traceability and lifecycle evidence.

## Prior Deliberations

- `DELIB-20260710-GTKB-MODERNIZATION-NONIMPAIRMENT-GOV-APPROVAL` — owner approval of the canonical production non-impairment GOV used by this repair.
- `DELIB-202667714` — owner-approved active list-free Assurance project PAUTH v5; source, test, and configuration mutations are allowed while dispatcher/TAFE, release, deployment, push, and external-system operations remain forbidden.
- No owner decision authorizes inventing `SPEC-E2E-001` as a formal specification. The least-regret correction is to make its local-fixture status explicit and bind production assessment to existing sufficient authority.

## Owner Decisions / Input

No new owner decision is required. The active project PAUTH and owner-approved modernization non-impairment GOV provide bounded implementation and requirement authority. This proposal does not create or amend a formal artifact.

## Requirement Sufficiency

**Existing requirements sufficient.** `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` defines the production behavior being protected. The verified-testing and evaluability DCLs require the exact mechanical binding. Creating a new specification would duplicate existing authority and is not authorized.

## Specification-Derived Verification Plan

| Requirement | Test / evidence | Required observed result |
|---|---|---|
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | existing end-to-end workflow success test plus canonical authority assertions | Independent review, recovery, exact-once mutation, isolation, and production-deployment separation remain unchanged; the completed result reports the canonical GOV binding. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `test_workflow_production_authority_ids_resolve_canonically` | Every production authority ID resolves in the canonical platform MemBase; the local rehearsal ID is not treated as production authority. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | manifest/source equality and drift tests | Source tuple and normalized manifest set are equal; missing, unknown, extra, duplicate, and mismatched IDs fail closed. |
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | candidate-assessment evidence assertions | Output includes exact authority IDs and canonical resolution evidence, not an implicit boolean. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | existing isolated-workspace tests | The disposable rehearsal remains self-contained and does not seed canonical GOV bytes into its local database. |

## Acceptance Criteria

1. Only the three declared targets change, and their pre-edit hashes match the evidence above at implementation start.
2. `SPEC-E2E-001` remains only as the explicitly named local rehearsal fixture ID; no production assessment, manifest authority field, or canonical lookup treats it as a live specification.
3. The source production-authority tuple and `AT-END-TO-END-WORKFLOW` manifest authority set are exactly equal and contain only the canonical modernization non-impairment GOV.
4. Candidate assessment fails closed for every missing/malformed/unknown/extra/duplicate/drifted authority case and emits exact canonical resolution evidence on success.
5. Focused authority-binding tests, the existing end-to-end workflow test module, Ruff lint, and Ruff format checks execute and report observed results. Known foreign baseline failures are reported precisely and are not claimed as WI-5553 failures or closure.
6. Existing manifest timer values are unchanged; no new hard-coded timer, retry, throttle, fan-out, or concurrency value is added.
7. No formal specification, MemBase row, `groundtruth.db`, dispatcher/TAFE state, Git state, index lock, deployment, release, or external system is mutated.

## Risk and Rollback

The primary risk is confusing the disposable rehearsal's synthetic spec with production authority in the opposite direction. Explicit names, separate resolution stores, exact-set equality, negative tests, and emitted provenance bound that risk. A second risk is broadening WI-5553 into unrelated acceptance failures; the three-target and related-work boundaries prevent that. Rollback is the exact source/test hunks plus manifest authority-field removal; no data migration is involved.

## DISARM — Implementation

This proposal is review-only. It authorizes no protected edit. Implementation requires a canonical independent GO, exact current claim, fresh schema-v3 start packet, unchanged target preimages or explicit independent review of drift, and final independent verification.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
