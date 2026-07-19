NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; build activity envelope
author_metadata_source: explicit_interactive_session_metadata

# Implementation Proposal - WI-5270 VERIFIED verdict cites three foundation DCL/ADR specs absent from canonical MemBase

bridge_kind: prime_proposal
Document: gtkb-wi5464-wi5270-canonical-spec-reverification
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5464-WI5270-CANONICAL-REVERIFICATION-20260718
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5464

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_worker_context.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_worker_context_cli.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Re-evaluate and exactly finalize WI-5270 using the now-canonical version-2 black-box foundation: adopt the two untracked hash-bound module/test files without semantic edits, verify the already-tracked CLI wiring without touching cli.py, preserve the defective historical v004 append-only, and use a separate independently reviewed repair chain for valid terminal evidence.

Work item description: bridge/gtkb-wi5270-worker-context-full-assigned-content-packet-004.md (VERIFIED, Antigravity/C) lists DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001, DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001, and ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001 in its Specification Links and Specification-Derived Verification table, attributing test coverage to them. As of 2026-07-17, gt spec show returns not found for all three canonically. Same defect class as the F1 finding in bridge/gtkb-wi5269-activity-envelope-authority-validators-003.md and bridge/gtkb-wi5271-mediated-bridge-packet-views-003.md, but landed as a completed VERIFIED rather than a corrected NO-ACTION. Undermines DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (verification must be derived from linked specs that canonically exist).

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5464` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_worker_context.py`, `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_worker_context_cli.py`.

## Specification Links

- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
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
- `GOV-WORK-TREE-HYGIENE-001` - auto-linked governing or work-item specification.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - auto-linked governing or work-item specification.
- `DCL-VERIFIED-BRIDGE-HISTORY-001` - auto-linked governing or work-item specification.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202666122` - Verdict
- `DELIB-20265254` - Defect-Fix Proposal - Ollama Harness UTF-8-Safe Output
- `DELIB-20264419` - Loyal Opposition Verification Verdict - Ollama Phase 2 Dispatch Wiring
- `DELIB-20265334` - Verdict
- `DELIB-202665141` - GO: WI-4943 Revised Proposal v009 -- dependency-envelope correction is clean, justified, and gate-passing

## Owner Decisions / Input

- `PAUTH-DISPATCHER-BLACK-BOX-WI5464-WI5270-CANONICAL-REVERIFICATION-20260718` - active project authorization covering `WI-5464`.

## Proposed Scope

- After independent GO and exact claim/start, adopt without semantic edits the current worker-context module at SHA-256 6146EEA8E2AB5508AD0C4B25D2696CABDD8B884722069DEB886D1A67F2BE5BF4 and focused test at SHA-256 3A25BB9A159C150FF01F7C649B156EBCED8E85F9C316B24F0D17913939F981B2; target hash drift fails closed.
- Re-evaluate the complete worker-context behavior, including the already-tracked CLI wiring introduced in commit 91e2976722c06fc500fcb61f400cd984d2ba2231, against the now-canonical version-2 packet, ordinary-worker boundary, and facade specifications; cli.py is verification-only and must not be edited, staged, or included.
- Preserve the WI-5270 primary 001-004 chain as append-only history, record that v004 used noncanonical reviewer metadata/bridge kind and evaluated three then-absent specs, and use this separate repair thread for current canonical evidence rather than deleting or rewriting history.
- Require an exact implementation report, independent VERIFIED, and atomic focused finalization containing only the two whole-file targets plus the complete WI-5270 and WI-5464 bridge chains; exclude all current unrelated cli.py and worktree changes.
- Do not inspect or mutate dispatcher/TAFE configuration or runtime, harness state/routing/eligibility/roles, credentials, external systems, deployment, release, or Git history.

## Cross-Harness Disposition

- **Codex A**: Prime Builder files and, only after independent GO/start, adopts the two exact current files without semantic edits.
- **Claude Code B**: No runtime behavior, configuration, or target-path change; eligible only for independent role-correct review.
- **Antigravity C**: Historical v004 reviewer provenance is preserved but not reused as current authority; no runtime or target-path change.
- **Cursor E**: No runtime behavior, configuration, or target-path change; eligible only for independent role-correct review.
- **Ollama D**: No source projection or runtime behavior change.
- **OpenRouter F**: No source projection or runtime behavior change.
- **Alibaba H**: No source projection or runtime behavior change.
- **TAFE and dispatcher**: Read-only synthetic fixture behavior only; no configuration, runtime, queue, routing, lease, cap, eligibility, role, or process-lifetime mutation.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5464; PAUTH-DISPATCHER-BLACK-BOX-WI5464-WI5270-CANONICAL-REVERIFICATION-20260718; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "bridge/gtkb-wi5270-worker-context-full-assigned-content-packet-004.md (VERIFIED, Antigravity/C) lists DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001, DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001, and ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001 in its Specification Links and Specification-Derived Verification table, attributing test coverage to them. As of 2026-07-17, gt spec show returns not found for all three canonically. Same defect class as the F1 finding in bridge/gtkb-wi5269-activity-envelope-authority-validators-003.md and bridge/gtkb-wi5271-mediated-bridge-packet-views-003.md, but landed as a completed VERIFIED rather than a corrected NO-ACTION. Undermines DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (verification must be derived from linked specs that canonically exist).",
  "after_behavior": "Re-evaluate and exactly finalize WI-5270 using the now-canonical version-2 black-box foundation: adopt the two untracked hash-bound module/test files without semantic edits, verify the already-tracked CLI wiring without touching cli.py, preserve the defective historical v004 append-only, and use a separate independently reviewed repair chain for valid terminal evidence.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5464",
    "project": "PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING",
    "target_paths": [
      "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_worker_context.py",
      "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_worker_context_cli.py"
    ],
    "linked_specifications": [
      "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001",
      "GOV-FILE-BRIDGE-AUTHORITY-001",
      "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001",
      "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001",
      "DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001",
      "SPEC-AUQ-POLICY-ENGINE-001",
      "ADR-ISOLATION-APPLICATION-PLACEMENT-001",
      "GOV-STANDING-BACKLOG-001",
      "ADR-CODEX-HOOK-PARITY-FALLBACK-001",
      "ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001",
      "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001",
      "DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001",
      "DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001",
      "ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001",
      "GOV-WORK-TREE-HYGIENE-001",
      "GOV-DOCUMENT-AUTHOR-PROVENANCE-001",
      "DCL-VERIFIED-BRIDGE-HISTORY-001",
      "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001"
    ]
  },
  "expected_result": {
    "summary": "Re-evaluate and exactly finalize WI-5270 using the now-canonical version-2 black-box foundation: adopt the two untracked hash-bound module/test files without semantic edits, verify the already-tracked CLI wiring without touching cli.py, preserve the defective historical v004 append-only, and use a separate independently reviewed repair chain for valid terminal evidence.",
    "scope": [
      "After independent GO and exact claim/start, adopt without semantic edits the current worker-context module at SHA-256 6146EEA8E2AB5508AD0C4B25D2696CABDD8B884722069DEB886D1A67F2BE5BF4 and focused test at SHA-256 3A25BB9A159C150FF01F7C649B156EBCED8E85F9C316B24F0D17913939F981B2; target hash drift fails closed.",
      "Re-evaluate the complete worker-context behavior, including the already-tracked CLI wiring introduced in commit 91e2976722c06fc500fcb61f400cd984d2ba2231, against the now-canonical version-2 packet, ordinary-worker boundary, and facade specifications; cli.py is verification-only and must not be edited, staged, or included.",
      "Preserve the WI-5270 primary 001-004 chain as append-only history, record that v004 used noncanonical reviewer metadata/bridge kind and evaluated three then-absent specs, and use this separate repair thread for current canonical evidence rather than deleting or rewriting history.",
      "Require an exact implementation report, independent VERIFIED, and atomic focused finalization containing only the two whole-file targets plus the complete WI-5270 and WI-5464 bridge chains; exclude all current unrelated cli.py and worktree changes.",
      "Do not inspect or mutate dispatcher/TAFE configuration or runtime, harness state/routing/eligibility/roles, credentials, external systems, deployment, release, or Git history."
    ],
    "acceptance_criteria": [
      "Both hash-bound target files remain byte-identical through the implementation report, and the focused worker-context test module passes 2 of 2 under the canonical version-2 specifications.",
      "All three foundation assertion commands pass, Ruff check and format checks pass, py_compile and git diff --check pass, and CLI help exposes the worker-context surface without reading or mutating dispatcher configuration/runtime.",
      "Independent LO verifies packet completeness, protected-internal omission, self/explicit dispatch-id behavior, and read-only state preservation from current canonical specs rather than the defective historical v004 evidence.",
      "Focused finalization tracks the two targets and both complete bridge chains without including cli.py or any foreign path; missing exact finalization evidence or target drift fails closed."
    ]
  },
  "rollback": {
    "instructions": "Revert only the approved source and test implementation targets under separate authority.",
    "verification": "Rerun the proposal's specification-derived tests and bridge preflights."
  },
  "hard_invariants": [
    "Bridge review, implementation-start, and independent verification gates remain mandatory.",
    "Only the declared in-root target paths are attributable to this implementation proposal.",
    "Dispatcher, TAFE, credential, deployment, release, and unrelated work remain outside generated authority."
  ],
  "fail_closed_conditions": [
    "Project membership or active PAUTH coverage is missing.",
    "Target paths escape the project root or candidate/live preflights fail.",
    "Required proposal evidence is empty, malformed, duplicated, or still contains authoring placeholders."
  ],
  "essential_context_preservation": "The generated proposal retains PAUTH, project, work item, targets, specifications, prior deliberations, owner decisions, scope, verification, acceptance, risk, rollback, and expected file changes."
}
```

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run the focused test module, the three canonical foundation assertions, Ruff check/format, py_compile, diff check, and map every result in the implementation report and independent verdict. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Require independent GO, exact claim/start, NEW implementation report, independent VERIFIED, and atomic focused finalization with distinct author/reviewer sessions. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001` | Run gt assert for the spec plus the focused packet-completeness test and verify assigned content, governing specs, targets, actions, blockers, preflight, citations, and provenance are present. |
| `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001` | Run gt assert for the spec plus the focused omission assertions proving raw queue, ranking, dispatcher/TAFE/harness, lock, process, configuration, and other-harness internals are absent. |
| `ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001` | Run gt assert for the ADR plus focused explicit/self dispatch-id CLI cases and a worker-context help smoke check. |
| `GOV-WORK-TREE-HYGIENE-001` | Verify exact hashes/status for the two targets, prove cli.py is not a target or finalization include, and compare the final commit path set to the two targets plus complete bridge chains only. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Validate trusted author metadata on every new status-bearing repair artifact and treat WI-5270 v004 reviewer_* metadata as historical defect evidence only. |
| `DCL-VERIFIED-BRIDGE-HISTORY-001` | Preserve the primary chain unchanged, link this additive repair, include both complete chains in finalization, and record the containing commit as terminal evidence. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Prove semantic target delta is zero, focused behavior remains green, every harness remains available, and no dispatcher/TAFE/runtime/routing/role/process mutation occurs. |

## Acceptance Criteria

- Both hash-bound target files remain byte-identical through the implementation report, and the focused worker-context test module passes 2 of 2 under the canonical version-2 specifications.
- All three foundation assertion commands pass, Ruff check and format checks pass, py_compile and git diff --check pass, and CLI help exposes the worker-context surface without reading or mutating dispatcher configuration/runtime.
- Independent LO verifies packet completeness, protected-internal omission, self/explicit dispatch-id behavior, and read-only state preservation from current canonical specs rather than the defective historical v004 evidence.
- Focused finalization tracks the two targets and both complete bridge chains without including cli.py or any foreign path; missing exact finalization evidence or target drift fails closed.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_worker_context.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_worker_context_cli.py`

## Recommended Commit Type

`feat`
