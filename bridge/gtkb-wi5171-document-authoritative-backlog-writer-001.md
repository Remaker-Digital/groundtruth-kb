NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f387f-0fc7-7200-abaa-03068ca8eee0
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive session; approval_policy=never; role=prime-builder
author_metadata_source: Codex system runtime context plus explicit session document

# Implementation Proposal - Implement explicit dispatched session-role envelopes and isolated worker bootstrap

bridge_kind: prime_proposal
Document: gtkb-wi5171-document-authoritative-backlog-writer
Version: 001
Date: 2026-07-10 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-RUNTIME-INTERFACES-WI5171-WI5086-DOCUMENT-ROLE-001
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-RUNTIME-INTERFACES
Work Item: WI-5171

target_paths: ["scripts/_kb_attribution.py", "scripts/session_self_initialization.py", "scripts/check_dispatched_role_bootstrap.py", "groundtruth-kb/src/groundtruth_kb/session/envelope.py", "groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py", "groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py", "groundtruth-kb/src/groundtruth_kb/cli_backlog_add_work_item.py", "platform_tests/scripts/test_kb_attribution.py", "platform_tests/scripts/test_kb_attribution_session_role.py", "platform_tests/scripts/test_cli_backlog_add.py", "platform_tests/scripts/test_cli_backlog_add_work_item.py", "platform_tests/scripts/test_session_envelope_runtime.py", "platform_tests/scripts/test_dispatched_role_bootstrap.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Implement the first P0 role-authority cutover for WI-5171/WI-5086, grounded in DELIB-20260710-GTKB-INTERACTIVE-KB-ATTRIBUTION-GLOBAL-MARKER-COLLISION: explicit session-document role provenance becomes the sole worker-role source for canonical backlog mutations, while dispatch remains intent confirmation and all missing/conflicting evidence fails before mutation.

Work item description: Implement GOV-SESSION-ROLE-AUTHORITY-001 v5 and DCL-SESSION-ROLE-RESOLUTION-001 v6 across dispatcher composition, explicit session envelopes, worker bootstrap, activity ordering, cross-harness delivery, mismatch audit, recovery, and session-specific marker/attribution isolation. Remove the marker_session_id_unverified shared-marker authorization path and provide the deterministic ten-assertion evaluator. Work remains unapproved: no implementation may begin until bounded PAUTH, bridge GO, matching work intent, exact target paths, and implementation-start evidence exist.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5171` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/_kb_attribution.py`, `scripts/session_self_initialization.py`, `scripts/check_dispatched_role_bootstrap.py`, `groundtruth-kb/src/groundtruth_kb/session/envelope.py`, `groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py`, `groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py`, `groundtruth-kb/src/groundtruth_kb/cli_backlog_add_work_item.py`, `platform_tests/scripts/test_kb_attribution.py`, `platform_tests/scripts/test_kb_attribution_session_role.py`, `platform_tests/scripts/test_cli_backlog_add.py`, `platform_tests/scripts/test_cli_backlog_add_work_item.py`, `platform_tests/scripts/test_session_envelope_runtime.py`, `platform_tests/scripts/test_dispatched_role_bootstrap.py`.

## Specification Links

- `GOV-SESSION-ROLE-AUTHORITY-001` - auto-linked governing or work-item specification.
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
- `DCL-SESSION-ROLE-RESOLUTION-001` - auto-linked governing or work-item specification.
- `ADR-ENVELOPE-META-MODEL-001` - auto-linked governing or work-item specification.
- `DCL-ENVELOPE-META-MODEL-001` - auto-linked governing or work-item specification.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202666073` - Authorize document-authoritative worker role correction
- `DELIB-20260710-GTKB-MODERNIZATION-DISPATCHED-WORKER-ROLE-DCL-V6-APPROVAL` - Owner approval of session-role resolution DCL v6
- `DELIB-20260710-GTKB-MODERNIZATION-DISPATCHED-WORKER-ROLE-AUTHORITY-PAIR-RESULT` - Dispatched worker session-role authority pair result
- `DELIB-20260710-GTKB-MODERNIZATION-RUNTIME-INTERFACES-WORK-PACKET` - Approve GT-KB Modernization Runtime Interfaces work packet
- `DELIB-20260710-GTKB-MODERNIZATION-DISPATCHED-WORKER-ROLE-GOV-V5-FORMALIZATION-RESULT` - Dispatched-worker session-role GOV v5 formalization result

## Owner Decisions / Input

- `DELIB-202666073` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-RUNTIME-INTERFACES-WI5171-WI5086-DOCUMENT-ROLE-001` - active project authorization covering `WI-5171`.

## Proposed Scope

- Compose explicit session-document role, role-resolution source, run, and session provenance before worker activity or backlog mutation.
- Make the canonical backlog add, update, resolve, and add-work-item paths derive changed_by role exclusively from the validated session document.
- Use dispatch-run evidence only to confirm dispatcher intent; never use dispatcher registry, target maps, ranking, shared markers, or poller environment to select or substitute worker role.
- Fail before mutation with an actionable recovery result when role-document evidence is missing, malformed, conflicting, stale, or session-mismatched.
- Replace tests that accept marker_session_id_unverified or durable-role fallback and add the deterministic GOV/DCL evaluator.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-SESSION-ROLE-AUTHORITY-001` | Run the deterministic dispatched-role bootstrap evaluator and focused document-authority regressions; all five outer assertions pass. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run proposal applicability and clause preflights and confirm the live thread is NEW with Prime-authored metadata. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Audit the requirement, formal GOV/DCL, WI, owner decision, PAUTH, bridge, test, and report lineage through canonical read surfaces. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run bridge_applicability_preflight.py and require no missing required or advisory specifications. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Map every linked specification to executed evidence in the implementation report and require all mappings to pass. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run bridge compliance and confirm Project Authorization, Project, Work Item, and JSON target_paths metadata. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Validate the owner-decision packet and active PAUTH; confirm this slice changes no AUQ policy behavior. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Inspect target paths and test that all implementation remains in GT-KB platform scope with no adopter application dependency. |
| `GOV-STANDING-BACKLOG-001` | Use canonical backlog and project reads to confirm WI-5171/WI-5086 lineage and no MEMORY.md authority or duplicate WI. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run cross-runtime attribution fixtures proving equivalent document-role behavior without hook or dispatcher-config dependence. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Audit the owner requirement through approved specifications, work items, PAUTH, bridge, tests, and verification artifacts. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Confirm the owner requirement triggered the existing formal carrier and corrective WI/PAUTH/bridge path without duplicate formal artifacts. |
| `DCL-SESSION-ROLE-RESOLUTION-001` | Run the deterministic evaluator plus writer/session-envelope tests; all ten outer assertions execute and pass. |
| `ADR-ENVELOPE-META-MODEL-001` | Inspect and test invocation, intent_hint, and payload/provenance composition without synthetic dispatcher authority. |
| `DCL-ENVELOPE-META-MODEL-001` | Run session-envelope runtime tests covering qualified envelope anatomy and dispatched-session references. |
| `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` | Run dispatched-session fixtures proving the role document is complete and the dispatch event is confirmation only. |

## Acceptance Criteria

- A conflicting registry role or peer shared marker cannot change the role recorded by any canonical backlog mutation surface.
- Interactive and dispatched fixtures use explicit role documents; dispatch confirmation never supplies or substitutes role.
- Missing, malformed, conflicting, stale, and session-mismatched role documents fail before any work-item, test, or phase write.
- All three backlog writer services share one document-role resolver and have behavioral integration coverage.
- The GOV v5 and DCL v6 executable assertions run without skipped, metadata-only, or partial outer assertions.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/_kb_attribution.py`
- `scripts/session_self_initialization.py`
- `scripts/check_dispatched_role_bootstrap.py`
- `groundtruth-kb/src/groundtruth_kb/session/envelope.py`
- `groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py`
- `groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py`
- `groundtruth-kb/src/groundtruth_kb/cli_backlog_add_work_item.py`
- `platform_tests/scripts/test_kb_attribution.py`
- `platform_tests/scripts/test_kb_attribution_session_role.py`
- `platform_tests/scripts/test_cli_backlog_add.py`
- `platform_tests/scripts/test_cli_backlog_add_work_item.py`
- `platform_tests/scripts/test_session_envelope_runtime.py`
- `platform_tests/scripts/test_dispatched_role_bootstrap.py`

## Recommended Commit Type

`feat`
