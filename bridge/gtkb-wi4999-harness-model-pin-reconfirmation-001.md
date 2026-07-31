NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Prime Builder session; default Codex desktop execution

# Implementation Proposal - Surface stale harness model pins (registry pin vs vendor actual default)

bridge_kind: prime_proposal
Document: gtkb-wi4999-harness-model-pin-reconfirmation
Version: 001
Date: 2026-07-06 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI4999-MODEL-PIN-DRIFT-SURFACE-20260706
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4999

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "config/agent-control/harness-model-pin-confirmations.toml", "platform_tests/scripts/test_harness_model_pin_reconfirmation.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

WI-4999 adds an owner-facing stale harness model-pin reconfirmation surface grounded in canonical harness registry reads.

Work item description: Harness model pins in harness-state/harness-registry.json (headless invocation-surface --model token) can silently diverge from a harness vendor actual default. Incident 2026-07-03: harness C (antigravity) was pinned to gemini-2.5-flash while the live Antigravity/Gemini CLI had moved to Gemini 3.5 Flash (High); owner caught it visually and authorized correcting the pin to gemini-3.5-flash (harnesses table v31, projection regenerated). GT-KB has no mechanism to detect or surface this drift; a stale pin misroutes headless dispatch to a wrong or deprecated model, risking dispatch failures or degraded review quality. Consideration: a doctor WARN listing current per-harness model pins for periodic owner reconfirmation, and/or a reconfirm prompt at harness resume/activate. Full vendor-local model introspection is likely infeasible to automate, so an owner-facing reconfirmation surface is the pragmatic path. Evidence: this session set-invocation-surface correction; 0 existing backlog matches on model-pin search.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4999` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. WI-4999 started as a consideration item, but owner decision DELIB-20260706-WI4999-IMPLEMENTATION-APPROVAL and active PAUTH PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI4999-MODEL-PIN-DRIFT-SURFACE-20260706 now define the bounded implementation boundary. This proposal creates no additional membership or PAUTH state.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/project/doctor.py`, `config/agent-control/harness-model-pin-confirmations.toml`, `platform_tests/scripts/test_harness_model_pin_reconfirmation.py`.

## Specification Links

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
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded project implementation authority.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - auto-linked governing or work-item specification.
- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` - auto-linked governing or work-item specification.
- `REQ-HARNESS-REGISTRY-001` - auto-linked governing or work-item specification.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - auto-linked governing or work-item specification.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- DELIB-20260706-WI4999-IMPLEMENTATION-APPROVAL - owner approved WI-4999 for bounded project authorization and normal bridge implementation-proposal filing.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI4999-MODEL-PIN-DRIFT-SURFACE-20260706` - active project authorization covering `WI-4999`.

## Proposed Scope

- Add an owner-facing doctor/status warning that enumerates each active dispatch-capable harness model pin from canonical harness registry projection reads.
- Add optional confirmation metadata recording the owner's last confirmed model pin per harness without treating vendor defaults as automatically discoverable truth.
- Fail closed around direct harness-registry edits: read pins through canonical harness projection readers and leave pin mutation to existing governed gt harness set-invocation-surface flows.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Normal bridge GO, implementation-start packet, implementation report, and LO verification remain required before source/config/test mutation. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Proposal header includes Project Authorization, Project, and Work Item machine-readable lines. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation cites DELIB-20260706-WI4999-IMPLEMENTATION-APPROVAL and PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI4999-MODEL-PIN-DRIFT-SURFACE-20260706. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` | Doctor implementation uses groundtruth_kb.harness_projection readers rather than direct raw SoT reads. |
| `REQ-HARNESS-REGISTRY-001` | Fixture harness records with invocation_surfaces headless argv produce deterministic model-pin extraction without hard-coded harness branches. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | The status/check surface reports dispatcher-relevant model pins without requiring operators to inspect runtime JSON or config files manually. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Warnings derive from fresh canonical reads of harness projection and confirmation metadata with no cached summary substitution. |

## Acceptance Criteria

- gt project doctor surfaces current per-harness model pins and warns when no current owner confirmation exists or confirmation metadata is stale.
- The implementation never reads harness-state/harness-registry.json directly outside canonical harness projection readers.
- Tests cover active/dispatch-capable harness pin extraction, stale/missing confirmation warnings, and non-dispatchable/credential surfaces remaining out of scope.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `config/agent-control/harness-model-pin-confirmations.toml`
- `platform_tests/scripts/test_harness_model_pin_reconfirmation.py`

## Recommended Commit Type

`feat`