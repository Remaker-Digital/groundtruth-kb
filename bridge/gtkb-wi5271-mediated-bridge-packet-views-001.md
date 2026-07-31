NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role via ::init gtkb pb; approval_policy=never; sandbox=danger-full-access

# Implementation Proposal - Mediated bridge packet views and raw bridge protection

bridge_kind: prime_proposal
Document: gtkb-wi5271-mediated-bridge-packet-views
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5271-MEDIATED-BRIDGE-VIEWS-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5271

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/read_commands.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_bridge_read_commands.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

WI-5271 proposes a read-only mediated bridge packet view so ordinary workers can receive assigned bridge content through a worker-safe facade while raw bridge files and bridge-state internals remain protected surfaces; hard enforcement gates remain later phased work.

Work item description: Implement mediated bridge packet views for ordinary workers so assigned proposal, verdict, implementation-report, and verification content is available through worker-safe packet commands rather than direct raw bridge-file dependency. Protect raw bridge and bridge-state internals from ordinary workers, while allowing governed ops/build/case-authorized paths to perform black-box configuration or internal mutations according to the activity-envelope authority model.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5271` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/bridge/read_commands.py`, `groundtruth-kb/src/groundtruth_kb/cli.py`, `platform_tests/scripts/test_bridge_read_commands.py`.

## Specification Links

- `ADR-DISPATCHER-ARCHITECTURE-001` - auto-linked governing or work-item specification.
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
- `DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001` - auto-linked governing or work-item specification.
- `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001` - auto-linked governing or work-item specification.
- `ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20266267` - Bounded implementation authorization: governance/bridge reliability hardening (WI-4457, WI-4458, WI-4871)
- `DELIB-20263164` - Owner decision: deepen TAFE Phase-2 (authorize WI-4504/4505/4506/4507/4511; exclude cutover 4508-4510)
- `DELIB-20263237` - Loyal Opposition Verdict: gtkb-wi3439-requirement-sufficiency-presence-check-001
- `DELIB-20266137` - Owner authorization: drive 7 dispatcher-reliability WIs (Fixes-then-Phases); yield WI-4818 to concurrent session
- `DELIB-2026-06-13-WI-4516-OWNER-AUTHORIZATION` - Owner authorization to implement WI-4516 bridge Bash hardening

## Owner Decisions / Input

- `DELIB-20260715-BRIDGE-FILES-PROTECTED-WORKER-SURFACE` - owner-decision evidence supplied to this command.
- `PAUTH-DISPATCHER-BLACK-BOX-WI5271-MEDIATED-BRIDGE-VIEWS-20260717` - active project authorization covering `WI-5271`.

## Proposed Scope

- Add a governed, read-only mediated bridge packet view for an assigned bridge thread/work item, returning proposal, verdict, implementation-report, and verification content needed by the worker without instructing the worker to read raw bridge files or bridge index/state internals.
- Keep direct raw bridge-file/index protection as a worker-surface contract in this WI and leave hard read/write denial gates to the later enforcement slice; this WI provides the safe replacement path required before hardening.
- Sequence implementation after WI-5270 worker-context packet GO/implementation or integrate with that surface without racing the same CLI contract; dispatcher/TAFE runtime/config mutation, worker ranking, harness registry internals, and unrelated queue state are out of scope.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Run targeted bridge read-command tests proving the mediated view is read-only and does not mutate dispatcher/TAFE/bridge state. |
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
| `DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001` | Exercise the mediated packet output for assigned proposal, verdict, implementation-report, and verification content and assert the safe fields are present. |
| `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001` | Regression-test that ordinary packet output does not expose raw bridge/index/state/config paths, ranking data, harness registry internals, or unrelated queue state. |
| `ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001` | Verify the new mediated view can be composed with the WI-5270 worker-context facade or remains explicitly sequenced behind it without duplicating competing CLI behavior. |

## Acceptance Criteria

- A worker-safe CLI/API view can retrieve assigned bridge packet content by work item or slug and includes enough provenance for the assignment while omitting raw bridge/index/runtime/config paths and unrelated queue/selection state.
- The existing gt bridge show/threads read surface remains available for authorized operators, while ordinary-worker documentation and output point to mediated packet content rather than raw bridge files as live dependencies.
- Tests cover full mediated content, compact/provenance behavior, no bridge/INDEX.md dependency exposure, no arbitrary raw path traversal, and compatibility with existing bridge show/threads commands.
- The proposal/report explicitly states that ops-envelope configuration mutation and build-envelope direct-internal mutation remain outside this WI except through later case-authorized work.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/bridge/read_commands.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `platform_tests/scripts/test_bridge_read_commands.py`

## Recommended Commit Type

`feat`
