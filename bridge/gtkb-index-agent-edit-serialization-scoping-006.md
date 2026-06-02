REVISED

bridge_kind: governance_review
Document: gtkb-index-agent-edit-serialization-scoping
Version: 006
Author: Prime Builder (Codex, harness A)
Date: 2026-06-01 UTC
Session: 019e8466-acc1-7923-b828-0ef7ab4a7758
Recommended commit type: docs
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Items Affected: WI-3513
Responds to: bridge/gtkb-index-agent-edit-serialization-scoping-005.md
target_paths: ["bridge/gtkb-index-agent-edit-serialization-scoping-006.md", "bridge/INDEX.md"]
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019e8466-acc1-7923-b828-0ef7ab4a7758
author_model: GPT-5 Codex
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop app; Prime Builder role; local workspace E:\GT-KB

# Bridge INDEX Agent-Edit Serialization Scoping REVISED-3

## Revision Claim

This revision addresses the `-005` NO-GO by removing the false claim that a
commit-time hook or prompt rule deterministically protects no-hook harnesses
from live `bridge/INDEX.md` damage. The revised plan makes the serialized
live-write path (`gt bridge index` / `atomic_index_update`) the first mandatory
cross-harness mitigation. Harness hooks and git pre-commit checks become
backstops, not the primary closure mechanism.

## Findings Addressed

### P1 - Antigravity remains uncovered for the live INDEX lost-update failure mode

Response: accepted. Version `-004` overclaimed closure for no-hook Antigravity
by treating prompt/rule guidance plus git `pre-commit` as equivalent to a live
write barrier. That is wrong because bridge scanners and dispatchers consume
the working-tree `bridge/INDEX.md` before any commit exists.

This revision changes the design:

- Slice 1 is now the serialized live-write CLI/API, not hook interception.
- All compliant bridge writers, including no-hook harnesses, use the same
  `atomic_index_update` critical section before the working-tree INDEX changes.
- Antigravity raw hand-edits are explicitly not claimed as mechanically
  intercepted. They remain prohibited operator behavior until Antigravity gains
  a live hook surface or an equivalent deterministic tool boundary.
- The first implementation slice must prove that two no-hook subprocesses using
  the CLI serialize without losing live `Document:` entries before any bridge
  scanner reads the file.

## Owner Decisions / Input

- 2026-06-01 UTC, S381 AUQ ("Corrected path"): the owner selected "Scope a NEW
  thread for INDEX write-serialization" after Prime identified that dispatch
  leases and INDEX write serialization were separate problems.
- 2026-06-01 current session: the owner directed the first wave of work to
  concentrate on bridge protocol and harness-assignment limitations that cause
  contention/conflict, optimizing GT-KB for highly parallel work across multiple
  agent harnesses with flexible role assignment.

No new owner decision is required for this scoping revision. Implementation
slices still need their own bridge proposal, GO, and implementation-start
authorization.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - `bridge/INDEX.md` is canonical workflow
  state and must be protected from lost updates.
- `GOV-STANDING-BACKLOG-001` - WI-3513 is the standing backlog anchor for this
  contention-control work.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - the fix routes INDEX mutation through a
  fresh-read live writer instead of stale read-modify-write edits.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all proposed files and tests are
  within `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - advisory traceability for the bridge
  coordination artifact.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - advisory traceability for preserving
  the owner decision and bridge work item as durable artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - advisory traceability for lifecycle
  status transitions represented in `bridge/INDEX.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the revised per-slice test
  plan below maps each proposed behavior to an executable verification surface.
- `.claude/rules/file-bridge-protocol.md` - the protocol root contract whose
  current raw edit instructions are the surface to be routed through the
  serialized writer in a later documentation slice.

## Prior Deliberations

- `DELIB-1841` and `DELIB-1795` - prior NO-GO reviews in the bridge helper
  INDEX parity family; they covered helper/caller migration, not raw
  agent-tool edits.
- `DELIB-1967` and `DELIB-2173` - VERIFIED histories for the bridge-propose
  helper INDEX parity threads.
- `DELIB-S300-001` - prior owner decision touching INDEX drift repair.
- `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH` - owner model for
  role/status orthogonality, relevant because no-hook PB work can still create
  bridge INDEX contention even when the harness is not event-dispatch-active.

No searched or cited deliberation waives live protection for the canonical
bridge source of truth.

## Clause Scope Clarification (Not a Bulk Operation)

`GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` fires on this revision's
project/work-item vocabulary, but this is a single-thread scoping revision for
WI-3513. It does not create, update, retire, reorder, or batch-disposition
standing backlog items.

- No bulk inventory artifact is required because no bulk backlog mutation is
  proposed or performed.
- No review-packet or `DECISION DEFERRED` batch marker applies because there is
  no multi-item backlog batch to defer or approve.
- No formal-artifact-approval packet is used by this revision because it mutates
  only the append-only bridge file plus `bridge/INDEX.md`.

## Revised Design

### Coverage Principle

The platform can deterministically protect only writes that pass through a
deterministic boundary. Therefore the first slice creates and mandates that
boundary. Hook and commit gates are valuable but insufficient as the first
control because they do not cover no-hook live working-tree writes.

### Harness Coverage Table

| Harness / path | Primary live-write control | Backstop | Residual risk statement |
|---|---|---|---|
| Claude Code raw bridge workflow | `gt bridge index` CLI/API, backed by `atomic_index_update` | Claude PreToolUse guard in a later slice | Raw edits are rejected after the guard slice; before then, use the CLI. |
| Codex raw bridge workflow | `gt bridge index` CLI/API, backed by `atomic_index_update` | Codex hook coverage for `apply_patch` / shell edits in a later slice | Raw edits are rejected after the guard slice; before then, use the CLI. |
| Antigravity / no-hook workflow | `gt bridge index` CLI/API, backed by `atomic_index_update` | git pre-commit warning/block in a later slice | Arbitrary raw hand-edits cannot be live-intercepted today; this proposal no longer claims they are closed. |
| Existing helper/script writers | migrate or wrap with the same serialized API | test coverage around each writer | Existing helpers are in scope only when a slice explicitly names them. |

### Revised Slice Plan

| Slice | Scope | Why first |
|---|---|---|
| 1 | Implement `gt bridge index add-document` and `gt bridge index set-status`, both backed by `scripts.bridge_index_writer.atomic_index_update`; add a small Python API for helper callers. | This is the only deterministic live-write control shared by hook and no-hook harnesses. |
| 2 | Migrate bridge helper paths that currently edit INDEX directly (`revise_bridge.py`, `impl_report_bridge.py`, and bridge-propose writer if needed) onto the serialized API. | Removes the highest-frequency scripted bypasses and proves day-to-day protocol operations use the lock. |
| 3 | Add Claude/Codex raw-edit guard hooks and git pre-commit checks that detect dropped `Document:` entries. | Backstop for accidental stale raw edits in hook-capable harnesses and commit-time damage detection. |
| 4 | Update `.claude/rules/file-bridge-protocol.md`, the bridge skill adapters, and any bridge helper instructions to route INDEX mutation through `gt bridge index`. | Makes the serialized path the documented operator path. |

Slice 1 is the recommended next implementation proposal. It is intentionally
limited to new CLI/API behavior and tests; it does not claim full raw-edit
closure for every harness.

## Spec-Derived Verification Plan

| Behavior | Proposed verification |
|---|---|
| `add-document` serializes two concurrent document prepends without lost updates | `python -m pytest platform_tests/scripts/test_gt_bridge_index_cli.py -q -k concurrent_add_document` |
| `set-status` prepends a status line under an existing document without clobbering concurrent changes | `python -m pytest platform_tests/scripts/test_gt_bridge_index_cli.py -q -k concurrent_set_status` |
| no-hook live-write path is protected when using the CLI | subprocess test with no Claude/Codex hook environment: two stale callers use the CLI and a fresh scanner sees both entries before commit |
| malformed status or missing document fails closed | CLI tests for invalid status, missing document, existing file mismatch |
| existing parser preserves legal bottom-suffix archival semantics | unit test over shared parse/drop-detection helpers if introduced in Slice 3 |

For every implementation slice, run separate lint and format gates on changed
Python files:

```text
python -m ruff check <changed files>
python -m ruff format --check <changed files>
```

## Acceptance Criteria

- The next implementation proposal for Slice 1 must not describe hooks or
  pre-commit as the primary live-write mitigation.
- Slice 1 must include a no-hook subprocess concurrency test proving the
  serialized writer protects the live working-tree INDEX before commit.
- Any statement about Antigravity/no-hook coverage must distinguish "covered
  when using the CLI/API" from "raw edits mechanically intercepted." The latter
  is not true today and must not be claimed.
- Later hook/pre-commit slices may reduce accidental bypasses but must remain
  described as backstops.

## Pre-Filing Preflight Subsection

Candidate revision preflights must pass before filing this `REVISED` line:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-index-agent-edit-serialization-scoping --content-file .tmp/gtkb-index-agent-edit-serialization-scoping-006.md --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-index-agent-edit-serialization-scoping --content-file .tmp/gtkb-index-agent-edit-serialization-scoping-006.md
```

## Risk And Rollback

This scoping revision mutates only the bridge file and `bridge/INDEX.md`. If the
revised design is rejected, file the next `REVISED` version addressing the
review findings; do not rewrite prior versions.

The implementation risk is shifted toward a narrow, testable primitive first:
serialized live INDEX writes. Rollback for that future slice is ordinary source
revert plus restoring documented bridge instructions to their prior state.
