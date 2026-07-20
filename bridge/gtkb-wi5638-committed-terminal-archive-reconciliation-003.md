REVISED
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: reasoning_effort=xhigh; thread_source=user
author_metadata_source: x-codex-turn-metadata

# Revised Implementation Proposal - Reconcile committed terminal archive dispositions across every live bridge reader

bridge_kind: prime_proposal
Document: gtkb-wi5638-committed-terminal-archive-reconciliation
Version: 003
Responds to: bridge/gtkb-wi5638-committed-terminal-archive-reconciliation-002.md
Date: 2026-07-19 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE","coverage":"project_membership_fallback","included_work_item_count":null,"specificity_rank":[2,0],"selected":true}]
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5638

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/versioned_files.py", "scripts/bridge_thread_files.py", "groundtruth-kb/src/groundtruth_kb/bridge/state_report.py", "platform_tests/scripts/test_versioned_files_archival_invariant.py", "platform_tests/scripts/test_archived_terminal_dispatch_reconciliation.py", "platform_tests/scripts/test_bridge_thread_files.py", "platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py", "platform_tests/scripts/test_scan_bridge.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Revise WI-5638 so one fail-closed committed-terminal archive classifier is consumed by every current live bridge queue reader: dispatcher rendering and selection, the Codex and Claude compact and non-compact bridge scanners, and the owner-facing `gt bridge state-report --json` path.

The revision adds the exact state-report reader surfaces omitted by v001. It preserves historical exact-thread and post-dispatch verdict lookup semantics by making owner-facing archive suppression an explicit reader mode rather than silently erasing archived chains from every `bridge_thread_files.py` consumer.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5638`. The implementation will remain read-only with respect to Git, bridge files, dispatcher state, TAFE, claims, leases, MemBase, and archived verdict bytes.

## Response To NO-GO Findings

### F1 - The proposal does not cover every live queue authority that currently reopens archived terminal targets

Accepted.

The revised target set adds:

- `scripts/bridge_thread_files.py`, the exact status-bearing numbered-file reader dynamically loaded by the state-report service;
- `groundtruth-kb/src/groundtruth_kb/bridge/state_report.py`, the owner-facing adapter that constructs `gt bridge state-report --json`;
- focused unit and CLI tests for both surfaces;
- compact and non-compact scan-helper coverage for both generated harness adapters;
- a standalone dispatcher-render and selection integration regression.

`groundtruth_kb.bridge.versioned_files` remains the single archive-trust classifier. `bridge_thread_files.py` will expose an explicit archive-aware index mode backed by that classifier, and `state_report.py` will request that mode. Historical exact-thread readers and post-dispatch verdict reconciliation will retain their existing unsuppressed file-chain behavior unless they explicitly request current queue semantics.

The implementation report must enumerate all 20 WI-5370 pilot slugs and prove that none appears in any live LO-actionable or dispatcher-selection surface. Sampling is not sufficient.

## Requirement Sufficiency

Existing requirements are sufficient. `WI-5638`, its linked specifications, the active Tree Stabilization PAUTH, and the v002 NO-GO define the exact correction. No dispatcher configuration change, PAUTH amendment, source-archive mutation, or owner waiver is required for this proposal revision.

## In-Root Placement Evidence

All eight target paths are inside `E:\GT-KB`. No external or retired assessment path is referenced or required.

## Specification Links

- `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001` - requires archived terminal bridge work to remain non-actionable.
- `DCL-ARCHIVE-PRESERVE-TERMINAL-VERDICT-DISPOSITION-001` - governs tracked archive preservation and live-source retirement.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - requires one authoritative dispatcher decision model.
- `ADR-DISPATCHER-ARCHITECTURE-001` - constrains dispatcher integration and read-only decision inputs.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - requires current HEAD and worktree evidence rather than stale cache state.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge filing and review.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserves governed work-item and verification evidence.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires complete proposal specification linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires executed specification-derived evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and exact targets.
- `SPEC-AUQ-POLICY-ENGINE-001` - preserves authorization and owner-input boundaries.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform repair outside adopter scope.
- `GOV-STANDING-BACKLOG-001` - preserves work-item lifecycle linkage.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - requires equivalent governed behavior across harness surfaces.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - preserves durable governed evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - preserves lifecycle transition evidence.

## Prior Deliberations

- `DELIB-202666766` - owner-authorized tracked archive transaction boundary for the WI-5370 pilot.
- `DELIB-202666774` - owner-confirmed archive preservation and normal lifecycle boundary.
- `bridge/gtkb-wi5370-terminal-archive-pilot-execution-003.md` - governed archive-pilot implementation report.
- `bridge/gtkb-wi5370-terminal-archive-pilot-execution-004.md` - independent NO-GO proving 16 of 20 archived terminal chains reopened.
- `bridge/gtkb-wi5638-committed-terminal-archive-reconciliation-001.md` - initial bounded repair proposal.
- `bridge/gtkb-wi5638-committed-terminal-archive-reconciliation-002.md` - independent NO-GO identifying the missing state-report reader.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` is the active project authorization for the proposed source and test work.
- No additional owner decision is requested. The WI-5370 by-reference terminal-finalization question remains outside WI-5638 and is not claimed or waived here.

## Proposed Scope

1. Extend `groundtruth_kb.bridge.versioned_files` with one bounded, read-only Git evidence scan over `archive/bridge-terminal-verdicts`.
2. Trust an archive disposition only when the archive path is canonical, the file is a regular blob tracked in current `HEAD`, local raw bytes exactly match the HEAD blob, the first status is terminal, `Document:` matches the filename slug, `Version:` matches the filename version, and the trusted archive version is strictly newer than the latest live version.
3. Compare raw Git blob object identities so `core.autocrlf` filtering cannot create a false dirty or false clean result.
4. Use hidden-window bounded subprocess flags on Windows and fail closed on Git absence, timeout, repository mismatch, unsupported object ID, malformed output, malformed content, unreadable bytes, or any inconsistent evidence.
5. Preserve existing live-terminal, implementation-sibling, and owner-acknowledged classifications.
6. Add an explicit archive-aware queue-index mode to `scripts/bridge_thread_files.py`; keep exact historical thread enumeration available for verdict reconciliation.
7. Make `groundtruth_kb.bridge.state_report` request the archive-aware queue index.
8. Prove identical suppression through Codex and Claude scan helpers in compact and non-compact modes and through dispatcher render/selection without modifying dispatcher runtime source or configuration.
9. Prove all 20 committed WI-5370 pilot dispositions are suppressed and all unrelated ordinary live work remains visible.

## Excluded Scope

- No dispatcher configuration, eligibility, provider route, daemon, supervisor, watchdog, lease, claim, runtime JSON, or TAFE mutation.
- No direct harness contact.
- No bridge source-file deletion or archive-file content mutation.
- No MemBase, project authorization, credential, external-system, deployment, release, Git index, Git ref, staging, commit, push, or history mutation.
- No changes to the parallel WI-5629 resolver/authorization targets.
- No WI-5370 terminal-finalization waiver or second archive batch.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5638 v003; PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE; response to independent NO-GO v002",
  "canonical_authority": "DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001 and DCL-ARCHIVE-PRESERVE-TERMINAL-VERDICT-DISPOSITION-001",
  "primary_route": "gtkb bridge revision helper",
  "before_behavior": "Committed newer terminal archive verdicts are ignored by one or more live readers, so retired predecessors reappear as LO-actionable work and can be redispatched.",
  "after_behavior": "Every current queue reader consumes one conservative committed-terminal archive classification and excludes exactly the retired predecessor while preserving uncertain or ordinary live work.",
  "self_descriptive_naming": "The classifier, explicit queue-index mode, state-report adapter, and integration test names will identify committed terminal archive reconciliation directly.",
  "obsolete_guidance_disposition": "No guidance is retired by this implementation.",
  "history_preservation": "Live and archived numbered bridge history remains byte-preserved; queue suppression does not delete history.",
  "baseline": {
    "work_item": "WI-5638",
    "project": "PROJECT-GTKB-TREE-STABILIZATION",
    "target_paths": [
      "groundtruth-kb/src/groundtruth_kb/bridge/versioned_files.py",
      "scripts/bridge_thread_files.py",
      "groundtruth-kb/src/groundtruth_kb/bridge/state_report.py",
      "platform_tests/scripts/test_versioned_files_archival_invariant.py",
      "platform_tests/scripts/test_archived_terminal_dispatch_reconciliation.py",
      "platform_tests/scripts/test_bridge_thread_files.py",
      "platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py",
      "platform_tests/scripts/test_scan_bridge.py"
    ]
  },
  "expected_result": {
    "summary": "All live queue surfaces suppress only strictly newer, trusted, committed terminal archive dispositions.",
    "acceptance_criteria": [
      "All 20 WI-5370 pilot slugs are absent from state-report LO actionability, both harness scan modes, dispatcher render input, and dispatcher selection input.",
      "Untracked, dirty, deleted, nonterminal, malformed, cross-slug, older, equal-version, and Git-error evidence cannot hide live work.",
      "Historical exact-thread and verdict reconciliation remain available and unrelated live threads remain actionable.",
      "No dispatcher, TAFE, bridge, archive, Git, MemBase, credential, deployment, or release state is mutated."
    ]
  },
  "rollback": {
    "instructions": "Revert only the eight approved source and test targets under separate authority.",
    "verification": "Rerun the focused reader, state-report, scan, and dispatcher integration tests."
  },
  "hard_invariants": [
    "Bridge GO, exact claim, implementation-start, independent verification, and focused-commit gates remain mandatory.",
    "Only declared in-root target paths are attributable to WI-5638.",
    "Uncertain archive evidence fails closed by leaving live work visible."
  ],
  "fail_closed_conditions": [
    "Project membership or active PAUTH coverage is missing.",
    "Target paths escape the project root.",
    "Candidate or live applicability or clause preflight fails.",
    "Git or archive evidence is absent, stale, malformed, dirty, ambiguous, or inconsistent."
  ],
  "essential_context_preservation": "The revision carries forward the work item, project authorization, exact NO-GO finding, specifications, deliberations, owner decisions, exact targets, tests, risks, and rollback."
}
```

## Specification-Derived Verification Plan

| Specification | Verification |
| --- | --- |
| `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001` | Focused archive-invariant and integration tests plus fresh `gt bridge state-report --json` and both scan modes prove no pilot slug is LO-actionable. |
| `DCL-ARCHIVE-PRESERVE-TERMINAL-VERDICT-DISPOSITION-001` | Tests prove canonical archive root, HEAD tracking, raw-byte cleanliness, terminal status, matching slug/version, and byte preservation. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Dispatcher render/actionable/selection integration tests prove trusted archived slugs never enter selection input and unrelated work remains actionable. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Tests and source review prove bounded hidden-window Git reads and zero dispatcher source/config/runtime mutation. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Tests mutate synthetic HEAD/worktree evidence and prove each fresh scan recomputes trust and fails closed on drift. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Candidate and live bridge applicability preflights plus independent LO review. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report must map every linked specification to executed focused and related tests. |
| Remaining linked governance specifications | Candidate/live applicability, mandatory clause preflight, exact target diff, Ruff, format, compile, and independent verification. |

## Required Test Matrix

1. `platform_tests/scripts/test_versioned_files_archival_invariant.py`
   - trusted newer terminal archive;
   - untracked, dirty, deleted, nonterminal, malformed, cross-slug, older, equal-version, wrong-root, unreadable, timeout, malformed Git, repository mismatch, and unsupported-object-ID fail-closed cases;
   - raw Git blob equality under CRLF/autocrlf-sensitive bytes.
2. `platform_tests/scripts/test_bridge_thread_files.py`
   - explicit archive-aware queue index excludes trusted archived predecessors;
   - default historical exact-thread enumeration remains available.
3. `platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py`
   - JSON and Markdown owner reports exclude trusted archived predecessors from LO actionability while retaining ordinary live threads.
4. `platform_tests/scripts/test_scan_bridge.py`
   - Codex and Claude helpers, compact and non-compact, classify the same trusted archive fixtures identically.
5. `platform_tests/scripts/test_archived_terminal_dispatch_reconciliation.py`
   - dispatcher render/actionable/selection excludes trusted archived predecessors;
   - all 20 current WI-5370 pilot slugs are absent from each relevant live queue surface;
   - unrelated live work remains actionable;
   - no tested command mutates watched bridge, archive, runtime, claim, lease, config, index, or ref inputs.

## Acceptance Criteria

- One shared classifier determines committed-terminal archive trust across dispatcher, scan, and state-report queue readers.
- `gt bridge state-report --json` reports none of the 20 WI-5370 pilot slugs as LO-actionable.
- Codex and Claude scan helpers in compact and non-compact modes report none of the 20 pilot slugs as actionable.
- Dispatcher rendered/actionable/selection input contains none of the 20 pilot slugs.
- All 20 pilot archive files remain HEAD-tracked, HEAD-clean by raw blob identity, terminal, slug/version coherent, and byte-preserved.
- Untracked, dirty, deleted, nonterminal, malformed, cross-slug, older, equal-version, wrong-root, unreadable, timed-out, repository-mismatched, unsupported-object-ID, and malformed-Git evidence fails closed and cannot hide live work.
- Existing historical exact-thread/verdict reconciliation remains available and unrelated live threads remain visible.
- Focused and related tests, Ruff check, Ruff format check, py_compile, `git diff --check`, candidate/live applicability, and mandatory clause preflight pass before implementation reporting.

## Risks / Rollback

The principal risk is false suppression of real live work. The implementation therefore trusts only direct canonical archive paths whose local raw bytes exactly match regular blob objects in current HEAD and whose terminal metadata matches the filename. Any uncertainty leaves the live work visible.

The secondary risk is breaking post-dispatch verdict lookup by globally hiding archived chains. The explicit queue-index mode prevents that: current queue reports opt in, while historical exact-thread lookup remains unchanged.

Rollback is a revert of only the approved source and test changes under separate authority. Bridge history and archive verdict bytes remain append-only and are never deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/bridge/versioned_files.py`
- `scripts/bridge_thread_files.py`
- `groundtruth-kb/src/groundtruth_kb/bridge/state_report.py`
- `platform_tests/scripts/test_versioned_files_archival_invariant.py`
- `platform_tests/scripts/test_archived_terminal_dispatch_reconciliation.py`
- `platform_tests/scripts/test_bridge_thread_files.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py`
- `platform_tests/scripts/test_scan_bridge.py`

## Recommended Commit Type

`fix`
