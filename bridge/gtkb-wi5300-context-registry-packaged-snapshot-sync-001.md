NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive; Prime Builder A; default reasoning configuration

# Implementation Proposal - Synchronize packaged context registry snapshots during canonical registry finalization

bridge_kind: prime_proposal
Document: gtkb-wi5300-context-registry-packaged-snapshot-sync
Version: 001
Date: 2026-07-15 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-CONTEXT-MANIFESTS-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-CONTEXT-MANIFESTS
Work Item: WI-5300

target_paths: ["config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Governed baseline stabilization for the WI-5170 canonical SoT registry candidate and its stale packaged v1 projection, preserving the independently VERIFIED WI-5266 baseline.

Work item description: HEAD 4eef2c30 keeps config/registry/sot-artifacts.toml byte-identical to its packaged v1 context-registry snapshot. The live checkout also contains older independently developed canonical registry additions that predate WI-5266 and are not in the packaged snapshot, causing test_packaged_v1_snapshot_matches_source_checkout_registry_inputs to fail in both the focused context and WI-5266 suites. Finalize the canonical source change and deterministically regenerated packaged snapshot in one bounded integration, preserving the committed WI-5266 baseline and never hand-editing generated output.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5300` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `config/registry/sot-artifacts.toml`, `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml`.

## Specification Links

- `DCL-ACTIVITY-CONTEXT-MANIFEST-001` - auto-linked governing or work-item specification.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202666159` - WI-5204 Stop-Hook Outcome Preservation With Genuine H Proof — Post-Implementation Verification
- `DELIB-202666228` - Loyal Opposition Review - gtkb-wi5224-provider-verdict-completion-contract-002
- `DELIB-202666253` - Loyal Opposition Verification Verdict - WI-5249 Prime NO-ACTION Claim/Filer
- `DELIB-20265869` - Loyal Opposition Review - dispatcher live-state and consistency reconciliation - WI-4768
- `DELIB-202666178` - WI-5213 - Loyal Opposition Post-Implementation Verification: VERIFIED

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-CONTEXT-MANIFESTS-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5300`.

## Proposed Scope

- Treat the current pre-start bytes of config/registry/sot-artifacts.toml as the owned WI-5170 canonical candidate baseline and preserve them byte-for-byte.
- Regenerate only the packaged v1 sot-artifacts.toml snapshot from the canonical registry using the repository's deterministic projection contract; do not hand-edit generated output.
- Finalize the canonical and packaged pair together only after exact byte equality, focused context-manifest tests, release Ruff, and independent VERIFIED evidence.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `DCL-ACTIVITY-CONTEXT-MANIFEST-001` | Run groundtruth-kb/tests/test_context_manifest.py and groundtruth-kb/tests/test_wi5266_resource_routing.py; both packaged-snapshot equality checks and all focused tests must pass. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- The packaged v1 sot-artifacts.toml snapshot is byte-identical to config/registry/sot-artifacts.toml.
- The focused context-manifest and WI-5266 resource-routing tests pass without changing WI-5266 behavior.
- No path outside the exact two-target integration scope is mutated, staged, or finalized by implementation.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `config/registry/sot-artifacts.toml`
- `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml`

## Recommended Commit Type

`feat`
