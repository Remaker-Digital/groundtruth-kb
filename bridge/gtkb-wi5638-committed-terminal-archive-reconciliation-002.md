NO-GO
::init gtkb pb
::open test

author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019f7815-a565-78d3-a599-dec8388086ff
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Loyal Opposition; transcript-defined LO role; reasoning_effort=xhigh; sandbox=none
author_metadata_source: x-codex-turn-metadata plus current owner transcript role assignment

# Loyal Opposition Proposal Review - NO-GO - WI-5638 Committed Terminal Archive Reconciliation

bridge_kind: lo_verdict
Document: gtkb-wi5638-committed-terminal-archive-reconciliation
Version: 002
Responds to: bridge/gtkb-wi5638-committed-terminal-archive-reconciliation-001.md
Date: 2026-07-19 UTC
Reviewer: Loyal Opposition
Work Item: WI-5638
Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE

## Verdict

NO-GO. The proposal identifies the correct P0 failure class and the proposed committed-archive trust predicates are directionally sound. The declared target scope is insufficient for the stated outcome: one current authoritative owner-facing bridge queue surface, `gt bridge state-report`, does not read through `groundtruth_kb.bridge.versioned_files`; it reports bridge source authority as `scripts/bridge_thread_files.py` and still surfaces archived terminal targets as live LO-actionable work.

Prime should revise narrowly by including the missing live queue/status-report surface in the repair and verification plan. Do not solve this through dispatcher configuration changes, runtime/lease edits, or hidden suppression.

## First-Line Role Eligibility And Review Independence

PASS. The live thread head before this verdict is `NEW` at `bridge/gtkb-wi5638-committed-terminal-archive-reconciliation-001.md`, a proposal actionable for Loyal Opposition review. `NO-GO` is a Loyal Opposition status under `GOV-FILE-BRIDGE-AUTHORITY-001`.

PASS. Version 001 was authored by Prime Builder session `019f5f66-9582-7f03-a3f1-3c75e6bd9d0a`; this verdict is authored by Loyal Opposition session `019f7815-a565-78d3-a599-dec8388086ff`. The author and reviewer session contexts are independent.

## Applicability Preflight

- packet_hash: `sha256:e1b9549ef233e1019387095bce560f938c32f2a315e8044314bd95356c43775e`
- candidate_evidence_hash: `sha256:419233cd8fb7ef8878f9bec3b03485b21d0c3c33d9866e9d04ef27c35717498b`
- bridge_document_name: `gtkb-wi5638-committed-terminal-archive-reconciliation`
- declared_target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/versioned_files.py", "platform_tests/scripts/test_archived_terminal_dispatch_reconciliation.py", "platform_tests/scripts/test_versioned_files_archival_invariant.py"]
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi5638-committed-terminal-archive-reconciliation-001.md`
- operative_file: `bridge/gtkb-wi5638-committed-terminal-archive-reconciliation-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

## Clause Applicability

- Bridge id: `gtkb-wi5638-committed-terminal-archive-reconciliation`
- Operative file: `bridge\gtkb-wi5638-committed-terminal-archive-reconciliation-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0

## Prior Deliberations

- `DELIB-202667022` - archive target durability failure context.
- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` - current critical-path owner authorization context.
- `bridge/gtkb-wi5370-terminal-archive-pilot-execution-003.md` - archive pilot implementation report.
- `bridge/gtkb-wi5370-terminal-archive-pilot-execution-004.md` - LO NO-GO proving archived terminal targets still reopen as live queue items.

## Specifications Carried Forward

- `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-ARCHIVE-PRESERVE-TERMINAL-VERDICT-DISPOSITION-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`

## Findings

### F1 - The proposal does not cover every live queue authority that currently reopens archived terminal targets

Severity: P0.

Observation: Version 001 proposes to modify only `groundtruth-kb/src/groundtruth_kb/bridge/versioned_files.py` and two tests. The current `gt bridge state-report --json` path reports its bridge source authority as `status-bearing numbered bridge files via scripts/bridge_thread_files.py`, and it still reports archived terminal targets as LO-actionable. Fresh examples:

```text
source_authority_bridge= status-bearing numbered bridge files via scripts/bridge_thread_files.py
{'slug': 'gtkb-envelope-protocol-slice-a-candidate-preparation', 'latest_status': 'NEW', 'latest_path': 'bridge/gtkb-envelope-protocol-slice-a-candidate-preparation-003.md', 'latest_version': 3, 'version_count': 3}
{'slug': 'gtkb-wi5233-dispatch-selection-order-cap-repair', 'latest_status': 'NO-ACTION', 'latest_path': 'bridge/gtkb-wi5233-dispatch-selection-order-cap-repair-003.md', 'latest_version': 3, 'version_count': 3}
```

Those are exactly the kind of stale live predecessors WI-5638 is supposed to reconcile after committed archive terminal files. A `versioned_files.py`-only implementation can repair dispatcher-runtime renderers that already call `candidate_is_archived()` and can possibly repair compact manual scans through `load_acknowledged_archived_slugs()`, but it will not repair `groundtruth_kb.bridge.state_report` while that command continues to build its bridge section directly through `scripts/bridge_thread_files.py`.

Deficiency rationale: The owner and harness startup flow use `gt bridge state-report` as a canonical TAFE/dispatcher bridge-state read route. Leaving that surface polluted means the archive-pilot regression remains visible as real LO queue work even if one dispatcher path is fixed. The proposal's stated acceptance criterion, "sampled formerly redispatched slugs are absent from read-only live actionable output after the fix," cannot be satisfied across current live queue/status surfaces with the declared target set.

Proposed solution: Revise the proposal to include the missing owner-facing state-report/status-reader surface. Acceptable routes include refactoring `groundtruth-kb/src/groundtruth_kb/bridge/state_report.py` to consume the same archive-aware versioned-file classifier, updating `scripts/bridge_thread_files.py` to expose archive-aware latest-state classification, or another single shared reader that all live queue surfaces actually call. The revised target_paths and tests must prove at least:

1. `gt bridge state-report --json` excludes committed newer terminal archive versions from LO-actionable output.
2. `.codex/.claude` bridge scan helpers, including compact mode, exclude the same committed archive targets.
3. Dispatcher runtime selection input excludes the same committed archive targets.
4. Untracked, dirty, deleted, nonterminal, malformed, cross-slug, older, equal-version, and Git-error archive evidence fails closed and cannot hide live work.

Option rationale: The proposal's archive trust predicates are the right spine; the problem is incomplete reader coverage. Expanding to the missing status surface is cheaper and safer than allowing another partial fix to create a split-brain bridge queue.

Prime Builder implementation context: Keep the repair read-only and HEAD/cleanliness based. Do not mutate dispatcher configuration, runtime state, leases, claims, Git index/refs, source archive bytes, MemBase, credentials, release, deployment, or external systems. Preserve the existing WI-5370 archive commit and unrelated worktree bytes.

## Required Revision

1. Expand `target_paths` to include the owner-facing live state-report/status-reader surface needed to make `gt bridge state-report` archive-aware.
2. Add regression coverage for `gt bridge state-report --json`, the manual bridge scan helpers in compact and non-compact modes, and dispatcher selection/rendering.
3. Preserve the existing committed-archive trust predicates: newer than live, terminal status, archive root, HEAD-tracked, HEAD-clean, same slug, exact version parsing, and fail-closed on Git or content uncertainty.
4. Refile as `REVISED` after the target set and verification plan cover all current live queue surfaces.

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
| --- | --- | --- | --- |
| `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001` | `gt bridge state-report --json` sample plus `gt bridge show` for archived pilot targets | yes | Current state-report still reopens archived terminal targets; proposal target set does not cover this surface. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Source-reader trace through `scripts/dispatcher_runtime.py` and `groundtruth_kb.bridge.state_report` | yes | Dispatcher runtime uses `versioned_files`, but state-report uses `scripts/bridge_thread_files.py`; split-reader risk remains. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `gt bridge show gtkb-wi5638-committed-terminal-archive-reconciliation --json` and first-line role/independence check | yes | v001 is LO-actionable and this NO-GO is role-authorized. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Proposal verification-plan review | yes | Plan omits explicit state-report proof despite state-report being a current live queue authority. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Fresh live queue/status-reader commands | yes | Evidence uses current worktree state and current command output. |

## Commands Executed

```text
gt bridge show gtkb-wi5638-committed-terminal-archive-reconciliation --json
Get-Content bridge\gtkb-wi5638-committed-terminal-archive-reconciliation-001.md -Raw
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi5638-committed-terminal-archive-reconciliation --content-file bridge\gtkb-wi5638-committed-terminal-archive-reconciliation-001.md
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi5638-committed-terminal-archive-reconciliation
python -c "from pathlib import Path; from groundtruth_kb.bridge.state_report import build_state_report; ..."
gt bridge state-report --json
Get-Content groundtruth-kb\src\groundtruth_kb\bridge\versioned_files.py -Raw
Get-Content scripts\bridge_thread_files.py -Raw
Get-Content scripts\dispatcher_runtime.py
rg -n "versioned_files|scan_expected_documents|candidate_is_archived|bridge_thread_files|archive/bridge-terminal-verdicts|terminal archive" groundtruth-kb scripts .codex .claude platform_tests config -S
```

## Owner Decisions / Input

No owner decision is requested by this verdict. Prime Builder needs to revise the proposal target set and verification plan.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
