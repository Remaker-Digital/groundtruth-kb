NEW

# Dispatcher target resolution separates durable identity from runtime kind

bridge_kind: prime_proposal
Document: gtkb-wi5185-dispatcher-identity-runtime-kind
Version: 001
Author: Prime Builder / Codex
Date: 2026-07-11 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f387f-0fc7-7200-abaa-03068ca8eee0
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive; role=prime-builder resolved from validated session document
author_metadata_source: validated harness-state/codex/session-envelopes session document plus Codex runtime context

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5185-DISPATCHER-IDENTITY-RUNTIME-KIND-20260711
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5185

target_paths: ["scripts/dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime.py"]

implementation_scope: source | test_addition | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Repair the LO review-delivery blocker in `_resolve_dispatch_targets`. The resolver currently compares registry `harness_type` (runtime implementation kind) to the durable installation name derived from `harness_id`, rejecting the valid `alibaba-cloud-studio` installation because its Claude-compatible runtime kind is `claude`.

The repair will validate a present registry `harness_name` against the identity-derived name, retain the existing fail-closed behavior for missing or mismatched identity information, and leave `harness_type` available only to existing runtime-readiness behavior. It changes neither dispatcher configuration nor role/selection/ranking/routing state.

## Specification Links

- `SPEC-DISPATCHER-IDENTITY-RUNTIME-KIND-SEPARATION-001` - defines the identity/runtimetype distinction, strict failure cases, and the acceptance matrix.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` - provides the existing durable identity/projection consistency boundary this correction preserves.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, and `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - require PAUTH, independent GO, a claim, and implementation-start authorization before protected edits.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires executed spec-derived test evidence before independent verification.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - preserve the defect, specification, authorization, bridge, test, and verification lineage.

## Prior Deliberations

- `DELIB-202666084` - owner approval of the bounded WI-5185 PAUTH after the live delivery failure was demonstrated.
- `SPEC-DISPATCHER-IDENTITY-RUNTIME-KIND-SEPARATION-001` approval packet - owner-approved requirement that separates durable installation identity from runtime kind without weakening identity drift checks.
- Live `gt bridge dispatch daemon status --json` evidence on 2026-07-11 - recorded `dispatch_target_resolution_failed` because `harness_type='claude'` was compared with identity `alibaba-cloud-studio` for H.

## Owner Decisions / Input

- `DELIB-202666084` records the owner's `Approve WI-5185 PAUTH` decision.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5185-DISPATCHER-IDENTITY-RUNTIME-KIND-20260711` is active and restricts this proposal to `scripts/dispatcher_runtime.py` and `platform_tests/scripts/test_dispatcher_runtime.py`.
- This proposal is not permission to edit protected files. Implementation remains blocked until independent Loyal Opposition GO, a matching claim, and an implementation-start packet are live.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-DISPATCHER-IDENTITY-RUNTIME-KIND-SEPARATION-001` defines both the narrowly permitted behavior and the fail-closed protections. The PAUTH explicitly excludes dispatcher configuration, roles, identity maps, selection, ranking, routing, provider requests, credentials, deployment, destructive operations, and unrelated paths.

## Spec-Derived Verification Plan

| Requirement | Automated evidence |
| --- | --- |
| Valid separation | A synthetic active H record with `harness_name=alibaba-cloud-studio` and `harness_type=claude` resolves as a LO target with command handle `alibaba-cloud-studio`. |
| Identity fail-closed | A synthetic registry record with a name that disagrees with the durable identity raises a precise identity/projection-drift error. Missing or unknown identity remains rejected. |
| Runtime-kind preservation | A distinct runtime kind remains available to existing readiness logic without becoming the identity comparison key. |
| Delivery regression | A dry-run cycle with the valid distinct runtime kind selects an LO target without recording `dispatch_target_resolution_failed` for that difference alone. |
| Scope guard | Assert the resolver change does not mutate dispatcher configuration, role assignment, identity projections, ranking, or routing inputs. |

Run `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short`, then the affected dispatch CLI/report suite. Run `groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py` and `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py`.

## Risk / Rollback

- Risk: replacing the comparison could accidentally suppress genuine identity drift. Mitigation: compare the identity-derived name to `harness_name`, fail closed on absent/mismatched values, and add a negative regression test.
- Risk: runtime kind could be discarded or become authority for identity. Mitigation: preserve it for existing readiness logic and test the distinct-kind success case explicitly.
- Risk: fixing resolution could alter selection behavior. Mitigation: keep candidate ranking/configuration untouched and use a dry-run delivery regression.
- Rollback: revert the single `fix` commit; configuration, durable identity, role maps, and dispatch policy are unchanged.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5185-dispatcher-identity-runtime-kind`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` - corrects a dispatcher target-resolution defect that blocks governed independent review delivery.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
