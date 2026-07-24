NEW
::init gtkb lo
::open build

# gtkb-wi5440-git-maintenance-actuator — Post-Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi5440-git-maintenance-actuator
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-07-22 UTC
Responds to: bridge/gtkb-wi5440-git-maintenance-actuator-002.md

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: b934dabd-089b-45eb-aa95-f7ef2f9c4db6
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5440-GIT-MAINTENANCE-ACTUATOR-20260722
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5440

target_paths: ["groundtruth-kb/src/groundtruth_kb/git_lifecycle/maintenance.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py", "platform_tests/scripts/test_git_lifecycle_maintenance.py"]

implementation_scope: source
requires_review: false
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implemented the GO'd (bridge -002) governed git-maintenance actuator as the new `maintenance` verb in
`groundtruth_kb.git_lifecycle`, resolving the structural gap where `implementation_start_gate.py`
redirects blocked direct git maintenance to a package that lacked any maintenance capability.

- `git_lifecycle/maintenance.py` (new) — `MaintenanceActuator` with `plan` (read-only, default),
  `run` (fail-closed behind a held bounded drain lease; journal-before-mutation; sanctioned
  `worktree prune --expire` / `reflog expire` / `gc --prune` plus a bounded `tmp_obj_*` / `tmp_pack_*`
  sweep), and `recover` (cleans partial state from an interrupted run). A `_FORBIDDEN_TOKENS` guard
  makes it structurally impossible to issue history-rewrite, force-push, LFS, or destructive
  working-tree commands.
- `git_lifecycle/__main__.py` — additive `maintenance` subparser + dispatch composing the existing
  `GitLifecycleService` quiescence primitive; all pre-existing verbs unchanged.
- `platform_tests/scripts/test_git_lifecycle_maintenance.py` (new) — 9 spec-derived tests.

The actuator creates the sanctioned capability only; it performs no reclamation on the canonical
repository and does not untrack `groundtruth.db` (both remain with dependent WI-5431).

This implementation was unblocked by the WI-5652 drift fix landed earlier this session: WI-5440's
3-path PAUTH packet write (`maintenance.py`) — previously blocked by the multi-path
`target_classifications` drift false-positive — now writes cleanly, which is direct end-to-end
evidence that the WI-5652 fix works.

## Specification Links (carried forward)

`GOV-WORK-TREE-HYGIENE-001`, `DCL-DISPATCHER-QUIESCENCE-LEASE-001`,
`GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`, `DCL-GIT-BRANCH-BINDING-PROMOTION-001`,
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`,
`DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`,
`GOV-STANDING-BACKLOG-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

## Spec-to-Test Mapping

| Specification | Test | Result |
|---|---|---|
| `DCL-DISPATCHER-QUIESCENCE-LEASE-001` | `test_run_without_drain_lease_fails_closed` | PASS — run raises `maintenance_lease_not_held` with zero git calls and no journal |
| `DCL-DISPATCHER-QUIESCENCE-LEASE-001` | `test_run_composes_existing_drain_lease` | PASS — with a held lease, issues sanctioned commands + writes a `complete` journal |
| `GOV-WORK-TREE-HYGIENE-001` | `test_worktree_prune_removes_only_stale_registrations` | PASS — real git repo: stale registration pruned, live worktree preserved |
| `GOV-WORK-TREE-HYGIENE-001` | `test_orphan_sweep_bounded_to_tmp_artifacts` | PASS — aged `tmp_obj_*`/`tmp_pack_*` removed; valid loose object and recent temp preserved |
| `DCL-GIT-BRANCH-BINDING-PROMOTION-001` | `test_maintenance_preserves_bound_workitem_refs` | PASS — branch tip + reachable object survive `gc --prune=now` |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | `test_existing_lifecycle_verbs_unchanged` | PASS — pre-existing verbs still parse; `maintenance` is additive |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | `test_plan_is_read_only` | PASS — plan issues no mutating verb; `mutating: False` |
| (owner constraint / hard invariants) | `test_no_history_rewrite_or_lfs_paths` | PASS — no forbidden token issued; `_git` guard raises on `push --force` |
| interruption safety | `test_recover_cleans_partial_run` | PASS — partial garbage cleaned; journal marked `recovered` |

## Commands Executed

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_git_lifecycle_maintenance.py -q --no-header   # 9 passed
groundtruth-kb/.venv/Scripts/python.exe -m ruff check <3 files>   # All checks passed!
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check <3 files>   # 3 files already formatted
```

## Owner Decisions / Input

1. `DELIB-202666764` — git-bloat + housekeeping-hardening program authorization (names the
   git-maintenance actuator track).
2. Owner AUQ 2026-07-22 — WI-5440-scoped PAUTH; non-destructive only (encoded as `forbidden_operations`).
3. Owner directive 2026-07-22 — "Continue until this program is landed. Do not stop for me: I authorize
   your necessary actions."

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5440 under PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5440-GIT-MAINTENANCE-ACTUATOR-20260722; owner decision DELIB-202666764.",
  "canonical_authority": "DCL-DISPATCHER-QUIESCENCE-LEASE-001 and GOV-WORK-TREE-HYGIENE-001.",
  "primary_route": "python -m groundtruth_kb.git_lifecycle maintenance {plan|run|recover}",
  "before_behavior": "implementation_start_gate.py blocked direct git gc/prune/repack/reflog-expire/worktree-prune and redirected to groundtruth_kb.git_lifecycle, which had no maintenance verb; sanctioned object-store maintenance was impossible.",
  "after_behavior": "The redirect resolves to a real verb: read-only plan, quiescence-gated run, and recover. Every pre-existing git_lifecycle verb is behaviorally unchanged (test_existing_lifecycle_verbs_unchanged).",
  "self_descriptive_naming": "Verb 'maintenance' with subverbs plan/run/recover, consistent with the package's existing imperative verbs and the gate's redirect wording.",
  "obsolete_guidance_disposition": "No guidance obsolete; existing 'avoid ad hoc git gc/prune' guidance now points at a sanctioned route.",
  "history_preservation": "No history rewrite, force-push, or LFS; only unreachable garbage above an age threshold is swept; reachable objects and work-item bindings preserved (test_maintenance_preserves_bound_workitem_refs).",
  "baseline": "git count-objects -vH 2026-07-22: 17027 loose / 60.92 GiB, 275 packs / 34.28 GiB, 96 garbage / 9.21 GiB.",
  "expected_result": "9 spec-derived tests pass; ruff check + format clean. This proposal performs no reclamation, so landing it changes no object-store state.",
  "rollback": "Revert the 3 files (one new module, additive CLI wiring, one new test file); no data migration.",
  "hard_invariants": ["never rewrites history", "never force-pushes", "never introduces Git LFS", "never removes reachable objects", "run requires a held bounded drain lease", "plan is read-only and the default subverb"],
  "fail_closed_conditions": ["no held drain lease when run is invoked", "operation journal cannot be written before mutation", "a forbidden git token is requested (guard raises)"],
  "essential_context_preservation": "plan and run emit operation journals under .gtkb-state so an interrupted run is diagnosable and recoverable -- the failure class behind the current 9.21 GiB of tmp_obj_* garbage."
}
```

## Prior Deliberations

- `DELIB-202666764` (program authorization).
- `DELIB-20262499` (prior FAB-04 reclamation NO-GO — handle-lock/stranded-draft failure the journal +
  recover path addresses).
- `bridge/gtkb-wi5440-git-maintenance-actuator-002.md` (the GO carried forward).
- `DELIB-20260722-WI5652-IMPL-START-GATE-MULTIPATH-DRIFT-FIX` (the gate fix that unblocked this
  multi-path implementation).

## Recommended Commit Type

`feat` — adds a new module and a new operator-facing capability (the `maintenance` verb) that did not
exist, unblocking dependent WI-5431. All three target files are clean of foreign work, so the
`VERIFIED` commit stages exactly these three paths.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
