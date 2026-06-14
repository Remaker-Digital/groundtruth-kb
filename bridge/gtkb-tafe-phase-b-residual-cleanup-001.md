NEW

# TAFE Phase B residual cutover-evidence cleanup

bridge_kind: prime_proposal
Document: gtkb-tafe-phase-b-residual-cleanup
Version: 001
Author: Prime Builder (Codex, harness A via owner-declared Prime session)
Date: 2026-06-14 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ec6ec-f2cd-7b00-a08d-68f9c25e5e75
author_model: GPT-5 Codex
author_model_version: 5
author_model_configuration: Codex desktop

Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-B-RESIDUAL-CLEANUP-WI-4566
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4566

target_paths: ["bridge/*.md", "bridge/INDEX.md", ".gtkb-state/tmp/phase-b-residual-cleanup-*", "groundtruth-kb/src/groundtruth_kb/bridge/index_mutation.py", "groundtruth-kb/src/groundtruth_kb/cli_bridge_index.py", "groundtruth-kb/tests/test_cli_bridge_index.py", "platform_tests/scripts/test_gt_bridge_index_cli.py", "groundtruth.db"]

implementation_scope: bridge lifecycle disposition; serialized INDEX repair; TAFE shadow ingest/evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4566 is the governed Phase B cleanup lane needed before the WI-4510 cutover
proposal can be considered. After WI-4546 was VERIFIED, the TAFE cutover
evidence narrowed to residual bridge lifecycle hygiene: the latest read-only
evidence reports parity structurally intact, but not cutover-clean because
there are `74` `lost_blocks` and `1` `extra_block`; active peer bridge movement
also means a fresh `gt flow ingest-bridge-index --apply` must be run before the
final evidence check.

This proposal authorizes a bounded cleanup implementation that:

1. Creates a live inventory and review packet for the residual completeness
   gaps before applying any lifecycle disposition.
2. Files terminal disposition bridge files for residual absent-from-INDEX
   orphan threads when the inventory shows they are historical, superseded,
   abandoned, or intentionally archived. The latest on-disk version's first
   non-blank line must become a terminal status token so the WI-4546 oracle
   classifies the slug as `archived_blocks`, not `lost_blocks`.
3. Re-indexes only genuine active parked drafts, if any are found, using the
   governed serialized bridge INDEX CLI. No raw INDEX edit is permitted.
4. Corrects the single phantom INDEX document entry
   `sp1-dispatch-reliability-prime-handoff`, whose status line points at
   `bridge/gtkb-sp1-dispatch-reliability-prime-handoff-001.md`, by adding and
   using a serialized `gt bridge index rename-document` command if the existing
   `add-document` / `set-status` commands cannot express the correction.
5. Runs `gt flow ingest-bridge-index --apply`, then reruns
   `gt flow cutover-evidence --json` until the evidence is clean:
   parity ok, contention zero, fidelity ok, `lost_blocks == []`, and
   `extra_blocks == []`.

The implementation explicitly does not execute WI-4510, does not make TAFE
authoritative, does not convert `bridge/INDEX.md` into a generated
compatibility view, and does not commit or push.

## Specification Links

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` — the umbrella TAFE program spec;
  WI-4566 is a Phase-7 precondition for governed cutover readiness.
- `ADR-TAFE-SLICE-C-INGESTION-001` — defines the shadow ingest representation
  and idempotent re-ingest evidence that must be clean before cutover.
- `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001` — defines terminal archived
  absent-from-INDEX candidates as non-lost and non-terminal absent candidates
  as gating `lost_blocks`.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` remains canonical during
  cleanup; bridge files remain append-only; INDEX mutation must go through
  serialized bridge INDEX tooling.
- `GOV-STANDING-BACKLOG-001` — the bulk cleanup is visible as WI-4566 and must
  produce an inventory/review packet before mutation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal
  cites governing specs and maps them to verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project authorization,
  project, and work item metadata are present and live.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification maps linked
  specs to concrete commands and observed results.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — lifecycle decisions are preserved as
  bridge artifacts and a review packet rather than silent cleanup.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the proposal uses explicit terminal
  lifecycle status for withdrawn/archived or superseded historical threads.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the owner decision, WI, PAUTH,
  bridge proposal, inventory, implementation report, and final evidence remain
  linked.

## Prior Deliberations

- `DELIB-20263195` — owner AUQ authorizing the WI-4508 -> WI-4509 -> WI-4510
  cutover sequence while preserving the closing owner gate for WI-4510.
- `DELIB-WI4510-CUTOVER-HOLD-PRE-RECONCILIATION-20260614` — records that
  WI-4510 is held until reconciliation evidence is clean.
- `DELIB-WI4546-RECONCILE-STRATEGY-REFINE-ORACLE-20260614` — owner chose the
  terminal-archived oracle refinement strategy that turned historical terminal
  absent blocks into `archived_blocks`.
- `DELIB-WI4546-DCL-COMPLETENESS-APPROVE-20260614` — approved
  `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001`.
- `DELIB-WI4546-PAUTH-AUTHORIZE-20260614` — dedicated WI-4546 PAUTH whose scope
  anticipated non-terminal orphan disposition and the phantom extra block, but
  whose work item is now resolved.
- `bridge/gtkb-tafe-shadow-index-reconciliation-006.md` — VERIFIED WI-4546
  implementation of the terminal archived-block oracle.
- `bridge/gtkb-wi4509-cutover-evidence-006.md` — VERIFIED cutover-evidence
  tooling that now surfaces the remaining gaps.
- `DELIB-20263382` — owner authorization for WI-4566 Phase B residual cleanup;
  explicitly excludes WI-4510 execution, TAFE authority change, commit, and push.

## Owner Decisions / Input

- `DELIB-20263382` records the owner answer: "Governed Phase B residual cleanup
  lane authorized." The decision authorizes this cleanup lane, residual bridge
  lifecycle disposition, governed phantom INDEX correction, and evidence rerun.
- The PAUTH
  `PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-B-RESIDUAL-CLEANUP-WI-4566`
  is live, includes `WI-4566`, and allows only
  `bridge_lifecycle_disposition`, `bridge_index_serialized_repair`, `source`,
  `test_addition`, `config`, and `tafe_shadow_ingest`.
- Forbidden by the same PAUTH: `cutover`, `live_dispatch_substrate`,
  `kb_schema_change`, `deployment`, `production_release`,
  `formal_spec_promotion`, `git_commit`, and `git_push`.
- WI-4510 remains separately owner-AUQ-gated; this proposal is only the cleanup
  precondition needed to present clean evidence for a later WI-4510 decision.

## Requirement Sufficiency

Existing requirements sufficient. WI-4566's acceptance summary, the active
PAUTH, `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001`, and the verified
cutover-evidence tooling specify the required end state: clean
`gt flow cutover-evidence --json` evidence with no lost or extra blocks and no
stale-shadow mismatches. No new or revised requirement is needed before this
cleanup implementation.

## Current Evidence Snapshot

The current live evidence before this proposal was drafted:

```json
{
  "ok": false,
  "summary": "cutover evidence GAPS: non-zero re-plan writes (3 instance(s), 5 artifact(s)); 6 fidelity mismatch(es); 74 lost block(s); 1 extra block(s). Not cutover-clean.",
  "present_count": 340,
  "expected_count": 975,
  "archived_count": 562,
  "lost_count": 74,
  "extra_blocks": ["sp1-dispatch-reliability-prime-handoff"],
  "lost_by_latest_token": {
    "(non-token-first-line)": 31,
    "GO": 19,
    "NEW": 15,
    "NO-GO": 8,
    "REVISED": 1
  },
  "actionable_total": 43
}
```

The stale-shadow portion is expected in the active swarm and is resolved by
`gt flow ingest-bridge-index --apply`; it is not the hard residual cleanup.
The hard residual cleanup is the 74 lost blocks plus the phantom document entry.

## Implementation Plan

1. Generate `.gtkb-state/tmp/phase-b-residual-cleanup-inventory.json` from live
   `gt flow cutover-evidence --json` and the existing lost-block
   characterizer. The inventory must include every lost slug, latest on-disk
   version, latest status classification, proposed action, and rationale.
2. Generate `.gtkb-state/tmp/phase-b-residual-cleanup-review-packet.md` before
   applying lifecycle changes. The packet must summarize counts, list any
   slug proposed for re-indexing, list all slug dispositions, and cite
   `DELIB-20263382` plus WI-4566.
3. For each orphan whose inventory action is terminal disposition, create the
   next versioned bridge file under the same slug with first non-blank line
   `WITHDRAWN` unless the review packet justifies `DEFERRED` or `ADVISORY`.
   The file must identify the prior latest file, disposition reason, owner
   authorization, and the cutover-evidence cleanup link. Existing files are
   never rewritten or deleted.
4. For any inventory item that is a genuine active parked draft, add it back to
   `bridge/INDEX.md` only through `gt bridge index add-document`; otherwise do
   not index historical terminal dispositions.
5. Add a serialized `rename-document` command to `gt bridge index` if needed,
   with transform and subprocess tests. Use it to rename
   `Document: sp1-dispatch-reliability-prime-handoff` to
   `Document: gtkb-sp1-dispatch-reliability-prime-handoff` without raw editing
   `bridge/INDEX.md`.
6. Run `gt flow ingest-bridge-index --apply` after all bridge/INDEX changes,
   then rerun `gt flow cutover-evidence --json`.
7. If evidence is still not clean, stop and file the exact residual blocker in
   the implementation report rather than broadening scope silently.

## Spec-Derived Verification Plan

| Specification / clause | Verification command or evidence | Expected result |
|---|---|---|
| `GOV-STANDING-BACKLOG-001` bulk visibility | Inspect `.gtkb-state/tmp/phase-b-residual-cleanup-inventory.json` and `.gtkb-state/tmp/phase-b-residual-cleanup-review-packet.md` | Inventory and review packet exist before mutation; packet cites WI-4566 and `DELIB-20263382`. |
| `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001` | `gt flow cutover-evidence --json` after disposition | `lost_blocks` is empty; terminal-disposition orphans appear only as `archived_blocks`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Use `gt bridge index add-document`, `gt bridge index set-status`, or the new serialized `gt bridge index rename-document`; inspect `git diff -- bridge/INDEX.md` | INDEX mutation is serialized and append/rename-scoped; no bridge version file is deleted or rewritten. |
| `ADR-TAFE-SLICE-C-INGESTION-001` | `gt flow ingest-bridge-index --apply` followed by `gt flow cutover-evidence --json` | `contention_zero: true`, `replan_instances_written: 0`, `replan_artifacts_written: 0`, and `fidelity.ok: true`. |
| Bridge INDEX serialized repair helper | `groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_cli_bridge_index.py platform_tests/scripts/test_gt_bridge_index_cli.py -q --tb=short` | Rename transform/CLI tests pass if the helper is added; existing add/set-status tests remain green. |
| Cutover evidence regression | `groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_tafe_index_completeness.py groundtruth-kb/tests/test_tafe_cutover_evidence.py -q --tb=short` | Existing completeness and evidence behavior remains green. |
| Python lint/format for source/test changes | `groundtruth-kb/.venv/Scripts/ruff.exe check groundtruth-kb/src/groundtruth_kb/bridge/index_mutation.py groundtruth-kb/src/groundtruth_kb/cli_bridge_index.py groundtruth-kb/tests/test_cli_bridge_index.py platform_tests/scripts/test_gt_bridge_index_cli.py`; `groundtruth-kb/.venv/Scripts/ruff.exe format --check ...` | Both lint and format checks pass for changed Python files. |
| WI-4510 exclusion | Read back `gt backlog show WI-4510 --json`; inspect implementation report | WI-4510 remains open/backlogged and no cutover authority change is performed. |

## Risk / Rollback

Primary risk is over-disposing a genuine active parked draft. The inventory and
review packet are mandatory before mutation; any uncertain slug must be
re-indexed or left as a blocker rather than terminalized silently.

The INDEX phantom repair risk is handled by adding a narrow serialized
`rename-document` helper instead of raw editing. Rollback is a reverse serialized
rename while the bridge remains canonical, plus deleting any uncommitted
terminal-disposition files created by this implementation before verification
if the implementation is abandoned. Once VERIFIED, later correction remains
append-only through new bridge lifecycle files.

## Bridge Filing (INDEX-Canonical)

This proposal is filed as `bridge/gtkb-tafe-phase-b-residual-cleanup-001.md`
and indexed with a `NEW` entry in `bridge/INDEX.md`. No prior bridge version is
deleted or rewritten.

## Recommended Commit Type

`fix:` — corrects residual cutover-evidence blockers and a phantom INDEX entry;
if the serialized `rename-document` helper is added, the implementation report
may recommend `feat:` for the eventual commit because it adds a new operator
command surface.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
