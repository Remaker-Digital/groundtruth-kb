NO-GO

# Loyal Opposition Review - Governance-Adoption Doctor Check

**Status:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-05-15 UTC
**Reviewed proposal:** `bridge/gtkb-governance-adoption-doctor-check-001.md`
**Document:** `gtkb-governance-adoption-doctor-check`

## Verdict

NO-GO.

The proposal cannot receive GO as written because it is coupled to the same unresolved Tier A registry design that is currently `NO-GO` in the bridge. The current codebase already has an established managed-artifact registry API used by doctor, so the proposal needs to rebase on that surface or wait for a revised registry proposal to be approved.

## Prior Deliberations

Deliberation Archive search was run before review:

```text
$env:PYTHONPATH='groundtruth-kb\src'; python -m groundtruth_kb --config E:/GT-KB/groundtruth.toml deliberations search 'governance adoption doctor check GTKB-GOV-003 adopter drift Tier A registry' --limit 8
```

Relevant results:

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence for the batch-5 project authorizations cited by the proposal.
- `DELIB-1242` / `DELIB-1243` / `DELIB-1244` - prior Tier A adoption bridge thread hits surfaced by the search.
- `DELIB-1074` - prior Agent Red GroundTruth-KB governance adoption drift and release-readiness context.
- `DELIB-0758` / `DELIB-1207` - mass adoption readiness context.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:b40a088b738785089ac7458f233a7a151e70f3230c1032827fb8cf40006e57e2`
- bridge_document_name: `gtkb-governance-adoption-doctor-check`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-governance-adoption-doctor-check-001.md`
- operative_file: `bridge/gtkb-governance-adoption-doctor-check-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-governance-adoption-doctor-check`
- Operative file: `bridge\gtkb-governance-adoption-doctor-check-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and must_apply applicability fail the gate (exit 5) when evidence is absent and no owner waiver line is cited. Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Findings

### F1 - Proposal depends on an unresolved Tier A registry surface

**Severity:** P1 governance / architecture drift

**Observation:** The proposal says `check_adoption_drift` will load the Tier A registry per `GTKB-GOV-001`, and its pseudocode calls `load_tier_a_registry()`. The live bridge state for `gtkb-tier-a-managed-skill-adoption-apply` is currently `NO-GO`, and that NO-GO specifically rejected the new Tier A registry/CLI design until it reconciles with the existing managed-artifact registry.

**Evidence:** `bridge/gtkb-governance-adoption-doctor-check-001.md:22`, `bridge/gtkb-governance-adoption-doctor-check-001.md:48-50`, `bridge/gtkb-governance-adoption-doctor-check-001.md:67-80`, `bridge/INDEX.md:95-97`, `bridge/gtkb-tier-a-managed-skill-adoption-apply-002.md:87-96`.

**Impact:** A GO would authorize doctor work against a dependency that is not approved and may be replaced by the revised `GTKB-GOV-001` design. That risks building a check with the wrong data model and then immediately revising it.

**Recommended action:** Revise the proposal after `GTKB-GOV-001` reaches GO, or explicitly rebase this proposal on the current approved registry surface: `groundtruth_kb.project.managed_registry` and `groundtruth-kb/templates/managed-artifacts.toml`.

### F2 - Current doctor already consumes the managed-registry API

**Severity:** P1 implementation design mismatch

**Observation:** The current doctor imports `FileArtifact`, `GitignorePattern`, `SettingsHookRegistration`, `artifacts_for_doctor`, and `find_artifact_by_id` from `groundtruth_kb.project.managed_registry`. The proposed function introduces a different `load_tier_a_registry()` API and different status taxonomy without reconciling with the current doctor architecture.

**Evidence:** `groundtruth-kb/src/groundtruth_kb/project/doctor.py:18-24`; `groundtruth-kb/src/groundtruth_kb/project/doctor.py:2662-2668`; `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py:2-9`; `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py:783-795`.

**Impact:** The proposal is likely to introduce parallel registry semantics in the doctor layer or require hidden changes outside the declared target paths. Either path undermines the single-source managed-artifact model.

**Recommended action:** Revise IP-1 to define the doctor drift check in terms of the existing `ManagedArtifact` API, including how `managed_profiles`, `doctor_required_profiles`, artifact classes, and settings-hook-registration rows map to the reported statuses.

### F3 - Silent skip on missing registry weakens the default doctor signal

**Severity:** P2 behavioral ambiguity

**Observation:** The risk section says the check depends on `GTKB-GOV-001` and will fall back to a silent skip when the registry is unavailable, while acceptance criteria require the output to be included in default `gt project doctor` mode.

**Evidence:** `bridge/gtkb-governance-adoption-doctor-check-001.md:102-111`.

**Impact:** A silent skip can make adoption drift invisible exactly when the registry/check integration is absent or broken. That contradicts the stated purpose of providing a first-class adopter health signal beyond test passing.

**Recommended action:** Revise the behavior to produce an explicit `warning`/`skipped` ToolCheck with a clear message when the registry is unavailable, or make registry availability a hard precondition and defer this proposal until the dependency is approved.

### F4 - Verification plan omits existing managed-registry and doctor parity tests

**Severity:** P2 verification gap

**Observation:** The proposal runs only `groundtruth-kb/tests/test_doctor_adoption_drift.py`, but the change touches the same behavioral surface as existing managed-registry and doctor parity tests.

**Evidence:** `bridge/gtkb-governance-adoption-doctor-check-001.md:89-100`; `groundtruth-kb/tests/test_managed_registry.py:2-12`; `groundtruth-kb/tests/test_managed_registry.py:341-360`; `groundtruth-kb/tests/test_managed_registry.py:556-572`; `groundtruth-kb/tests/test_no_parallel_manifests.py:1-13`, `groundtruth-kb/tests/test_no_parallel_manifests.py:78-83`.

**Impact:** New adoption-drift tests could pass while breaking existing doctor-required profile behavior, scanner-safe-writer drift behavior, or no-parallel-manifest safeguards.

**Recommended action:** Add targeted existing tests to the verification plan, at minimum `groundtruth-kb/tests/test_managed_registry.py`, `groundtruth-kb/tests/test_no_parallel_manifests.py`, and the new adoption-drift test file.

### F5 - Applicability preflight found uncited advisory specs

**Severity:** P3 specification-linkage hygiene

**Observation:** The applicability preflight passed required specs but reported missing advisory specs `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

**Evidence:** Applicability Preflight above.

**Impact:** This is not a mechanical blocking gap by itself, but the proposed doctor check is artifact-lifecycle governance work and should carry the advisory context or explain non-applicability.

**Recommended action:** Cite the advisory specs in the revised proposal or explain why each is not applicable.

## Required Action Items

1. Revise and resubmit as `bridge/gtkb-governance-adoption-doctor-check-003.md` with `REVISED` status.
2. Rebase the check on the approved existing managed-registry surface, or wait for revised `GTKB-GOV-001` to reach GO.
3. Replace silent-skip semantics with an explicit doctor result or make registry availability a hard precondition.
4. Broaden the verification plan to include existing managed-registry, doctor parity, and no-parallel-manifest tests.

## Decision Needed From Owner

None at this review stage.

## Commands Run

```text
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-governance-adoption-doctor-check --format json
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-governance-adoption-doctor-check
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-governance-adoption-doctor-check
$env:PYTHONPATH='groundtruth-kb\src'; python -m groundtruth_kb --config E:/GT-KB/groundtruth.toml deliberations search 'governance adoption doctor check GTKB-GOV-003 adopter drift Tier A registry' --limit 8
Read-only inspection of bridge/INDEX.md, bridge/gtkb-tier-a-managed-skill-adoption-apply-002.md, doctor.py, managed_registry.py, test_managed_registry.py, and test_no_parallel_manifests.py
```
