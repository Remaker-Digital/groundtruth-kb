NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: reasoning_effort=xhigh; thread_source=user
author_metadata_source: x-codex-turn-metadata

# Implementation Proposal - Reconcile committed terminal archive dispositions into TAFE before redispatch

bridge_kind: prime_proposal
Document: gtkb-wi5638-committed-terminal-archive-reconciliation
Version: 001
Date: 2026-07-19 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE","coverage":"project_membership_fallback","included_work_item_count":null,"specificity_rank":[2,0],"selected":true}]
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5638

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/versioned_files.py", "platform_tests/scripts/test_versioned_files_archival_invariant.py", "platform_tests/scripts/test_archived_terminal_dispatch_reconciliation.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Repair the post-WI-5370 stale-redispatch regression by making the shared live bridge reader recognize only newer, terminal, HEAD-tracked, HEAD-clean archive dispositions before actionable queue construction.

Work item description: The governed WI-5370 pilot committed exactly 20 byte-identical terminal artifacts under archive/bridge-terminal-verdicts and removed only their live bridge source files, but the production dispatcher/TAFE decision surface continued to report those archived slugs as Loyal Opposition actionable and launched provider workers against them. This regresses WI-4990's stale-redispatch guarantee for the tracked archive-preserve path. Add an atomic or deterministic recoverable reconciliation boundary so a successful committed archive disposition makes the exact archived slugs non-actionable in canonical TAFE state before any subsequent selection, while preserving archive bytes, unrelated TAFE rows, ordinary live threads, and fail-closed recovery. Do not solve this through dispatcher configuration changes, direct runtime/lease JSON edits, or hidden suppression.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5638` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/bridge/versioned_files.py`, `platform_tests/scripts/test_versioned_files_archival_invariant.py`, `platform_tests/scripts/test_archived_terminal_dispatch_reconciliation.py`.

## Specification Links

- `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001` - auto-linked governing or work-item specification.
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
- `DCL-ARCHIVE-PRESERVE-TERMINAL-VERDICT-DISPOSITION-001` - auto-linked governing or work-item specification.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - auto-linked governing or work-item specification.
- `ADR-DISPATCHER-ARCHITECTURE-001` - auto-linked governing or work-item specification.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202667001` - NO-GO — WI-5370 missing-targets WI-5316 finalization repair (report 003)
- `DELIB-202665163` - NO-GO: WI-4356 Slice D — blocker unchanged; owner-dependent exact-content approval still required
- `DELIB-202667022` - NO-GO — WI-5211 Reappeared Invalid Terminal Cleanup: Archive Target Is Gitignored, No Durable Audit Trail
- `DELIB-20266119` - Owner decision: close WI-4230/4231/4233 as superseded by the no-index bridge cutover
- `DELIB-20263396` - Summary

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5638`.

## Proposed Scope

- Extend the shared versioned-file reader with a bounded read-only Git evidence scan over archive/bridge-terminal-verdicts. Use hidden-window subprocess flags on Windows and fail closed on Git absence, timeout, malformed output, or repository mismatch.
- Record the highest trustworthy committed terminal archive version per slug and classify a live bridge candidate as archived only when that version is newer than the highest live bridge version. Preserve existing terminal-live, implementation-sibling, and owner-acknowledged classifications.
- Reject suppression from untracked, modified, deleted, nonterminal, malformed, cross-slug, older, or equal-version archive files. Do not mutate TAFE, dispatcher configuration/runtime state, leases, claims, source archives, Git index, or refs.
- Add focused unit coverage plus a standalone dispatcher-render/actionable integration regression without editing the concurrently dirty dispatcher runtime or its existing dirty test modules.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5638; PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "The governed WI-5370 pilot committed exactly 20 byte-identical terminal artifacts under archive/bridge-terminal-verdicts and removed only their live bridge source files, but the production dispatcher/TAFE decision surface continued to report those archived slugs as Loyal Opposition actionable and launched provider workers against them. This regresses WI-4990's stale-redispatch guarantee for the tracked archive-preserve path. Add an atomic or deterministic recoverable reconciliation boundary so a successful committed archive disposition makes the exact archived slugs non-actionable in canonical TAFE state before any subsequent selection, while preserving archive bytes, unrelated TAFE rows, ordinary live threads, and fail-closed recovery. Do not solve this through dispatcher configuration changes, direct runtime/lease JSON edits, or hidden suppression.",
  "after_behavior": "Repair the post-WI-5370 stale-redispatch regression by making the shared live bridge reader recognize only newer, terminal, HEAD-tracked, HEAD-clean archive dispositions before actionable queue construction.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5638",
    "project": "PROJECT-GTKB-TREE-STABILIZATION",
    "target_paths": [
      "groundtruth-kb/src/groundtruth_kb/bridge/versioned_files.py",
      "platform_tests/scripts/test_versioned_files_archival_invariant.py",
      "platform_tests/scripts/test_archived_terminal_dispatch_reconciliation.py"
    ],
    "linked_specifications": [
      "DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001",
      "GOV-FILE-BRIDGE-AUTHORITY-001",
      "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001",
      "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001",
      "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001",
      "DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001",
      "SPEC-AUQ-POLICY-ENGINE-001",
      "ADR-ISOLATION-APPLICATION-PLACEMENT-001",
      "GOV-STANDING-BACKLOG-001",
      "ADR-CODEX-HOOK-PARITY-FALLBACK-001",
      "ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001",
      "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001",
      "DCL-ARCHIVE-PRESERVE-TERMINAL-VERDICT-DISPOSITION-001",
      "SPEC-CENTRALIZED-DISPATCH-SERVICE-001",
      "ADR-DISPATCHER-ARCHITECTURE-001",
      "GOV-SOURCE-OF-TRUTH-FRESHNESS-001"
    ]
  },
  "expected_result": {
    "summary": "Repair the post-WI-5370 stale-redispatch regression by making the shared live bridge reader recognize only newer, terminal, HEAD-tracked, HEAD-clean archive dispositions before actionable queue construction.",
    "scope": [
      "Extend the shared versioned-file reader with a bounded read-only Git evidence scan over archive/bridge-terminal-verdicts. Use hidden-window subprocess flags on Windows and fail closed on Git absence, timeout, malformed output, or repository mismatch.",
      "Record the highest trustworthy committed terminal archive version per slug and classify a live bridge candidate as archived only when that version is newer than the highest live bridge version. Preserve existing terminal-live, implementation-sibling, and owner-acknowledged classifications.",
      "Reject suppression from untracked, modified, deleted, nonterminal, malformed, cross-slug, older, or equal-version archive files. Do not mutate TAFE, dispatcher configuration/runtime state, leases, claims, source archives, Git index, or refs.",
      "Add focused unit coverage plus a standalone dispatcher-render/actionable integration regression without editing the concurrently dirty dispatcher runtime or its existing dirty test modules."
    ],
    "acceptance_criteria": [
      "A synthetic repository with a lower live NEW/GO version and a newer committed terminal archive version excludes that slug from rendered PB/LO actionable queues while preserving unrelated live threads.",
      "Untracked, dirty, deleted, nonterminal, malformed, cross-slug, older, equal-version, and Git-error archive evidence fails closed and cannot hide live actionable work.",
      "The 20 WI-5370 pilot archive dispositions remain byte-preserved and tracked; sampled formerly redispatched slugs are absent from read-only live actionable output after the fix, with no dispatcher configuration or runtime-state mutation.",
      "Focused tests, related bridge reader/manual-scan regressions, Ruff check, Ruff format check, compile checks, applicability preflight, and clause preflight pass before implementation reporting."
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
| `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001` | Run focused archival-invariant and live-render/actionable integration tests proving committed terminal archive classification and conservative fallback. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run focused and related pytest, Ruff lint, Ruff format check, py_compile, candidate/live applicability preflights, and mandatory clause preflight with observed results. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARCHIVE-PRESERVE-TERMINAL-VERDICT-DISPOSITION-001` | Test exact archive-root, tracked-in-HEAD, clean-against-HEAD, terminal-token, slug, and version predicates while preserving archive bytes. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Exercise the shared dispatcher renderer and actionable computation against committed archive fixtures; prove archived slugs cannot enter selection input and unrelated work remains actionable. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Verify the change is read-only, daemon-consumed, uses hidden-window bounded Git probes, and performs no harness, routing, configuration, lease, or runtime mutation. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Recompute archive trust from current HEAD and current worktree cleanliness on each bridge scan; test that later local drift invalidates prior trust. |

## Acceptance Criteria

- A synthetic repository with a lower live NEW/GO version and a newer committed terminal archive version excludes that slug from rendered PB/LO actionable queues while preserving unrelated live threads.
- Untracked, dirty, deleted, nonterminal, malformed, cross-slug, older, equal-version, and Git-error archive evidence fails closed and cannot hide live actionable work.
- The 20 WI-5370 pilot archive dispositions remain byte-preserved and tracked; sampled formerly redispatched slugs are absent from read-only live actionable output after the fix, with no dispatcher configuration or runtime-state mutation.
- Focused tests, related bridge reader/manual-scan regressions, Ruff check, Ruff format check, compile checks, applicability preflight, and clause preflight pass before implementation reporting.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/bridge/versioned_files.py`
- `platform_tests/scripts/test_versioned_files_archival_invariant.py`
- `platform_tests/scripts/test_archived_terminal_dispatch_reconciliation.py`

## Recommended Commit Type

`feat`
