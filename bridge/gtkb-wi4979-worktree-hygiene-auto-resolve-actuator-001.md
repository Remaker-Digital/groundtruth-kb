NEW

# WI-4979 Work-Tree Hygiene Slice E - Auto-Resolve Actuator

bridge_kind: prime_proposal
Document: gtkb-wi4979-worktree-hygiene-auto-resolve-actuator
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-05 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex desktop Prime Builder; interactive build envelope; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI4979-BATCH-A1-20260705
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4979

target_paths: ["scripts/hygiene/stray_detector.py", "groundtruth-kb/src/groundtruth_kb/hygiene/strays.py", "groundtruth-kb/src/groundtruth_kb/hygiene/auto_resolve.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "scripts/auto_finalize_sweep.py", "platform_tests/scripts/test_work_tree_stray_detector.py", "platform_tests/scripts/test_hygiene_strays_cli.py", "platform_tests/scripts/test_work_tree_hygiene_doctor.py", "platform_tests/hooks/test_auto_finalize_verified_verdicts.py"]

implementation_scope: source/test/cli/hook-adjacent automation
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4979 implements the missing Slice E actuator layer for the already-verified work-tree hygiene surfaces. Slices A-C can detect stale tracked edits, untracked files, stashes, and orphaned worktrees, and they can expose those findings through `gt hygiene strays` and doctor visibility. They still reduce no owner burden in practice because every stale finding currently routes to owner review or manual handling.

This proposal adds deterministic auto-resolve planning and guarded execution mechanics without authorizing destructive cleanup of the live worktree. The implementation should classify findings into explicit candidate actions (`safe_commit`, `auto_ignore`, `auto_drop_byte_identical`, `manual_owner_review`, `skip`) with evidence requirements, expose those actions through the existing CLI/doctor surfaces, and wire the already-registered `auto_finalize_sweep.py` cheap gate to invoke the new planning layer in report-only mode. Applying cleanup to live stale files, dropping stashes, pruning worktrees, deleting untracked files, broad status mutation, or committing another session's stale work remains forbidden unless a later batch supplies item-specific apply evidence.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001` - governs stale worktree/stash detection, preservation boundaries, and evidence-first remediation.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - proposal, review, implementation report, and verification must flow through the append-only bridge chain.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Batch A1 PAUTH is bounded and does not bypass bridge GO or implementation-start scope.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - owner/project authorization is not direct implementation permission.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites governing specs and constrains target paths.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - machine-readable PAUTH/project/work-item metadata is present above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must map each work-tree hygiene behavior to executed tests.
- `GOV-STANDING-BACKLOG-001` - WI-4979 is a MemBase backlog item and must reach terminal state through evidence, not drift out of view.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - stale-work classification must derive from fresh git/registry reads, not cached summaries.
- `GOV-AUTOMATION-VALUE-VS-COST-001` - repetitive stale-work triage belongs in deterministic services when it can be made bounded and auditable.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - hook-adjacent integration must preserve Codex/Claude Stop-hook parity where the existing sweep is already registered.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - target paths under `groundtruth-kb/src/groundtruth_kb/project/**` must remain GT-KB platform root-boundary work and must not blur into Agent Red application surfaces.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the action planner should preserve traceability across findings, evidence, candidate actions, tests, reports, and bridge verification.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - action plans, skip reasons, and apply-evidence requirements must be durable artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - stale workspace state is a lifecycle trigger for explicit candidate action rather than invisible accumulation.

## Prior Deliberations

- `DELIB-20260867` - owner authorization for WI-4356 recurring work-tree hygiene and the twelve-hour stale-work threshold.
- `DELIB-20260705-HIGH-PRIORITY-BATCH-A1-APPROVAL` - owner approved Batch A1, including WI-4979, under explicit forbidden operations.
- `bridge/gtkb-work-tree-hygiene-mechanism-scoping-003.md` - scoping capstone that identified Slice E as the missing recurring actuator layer.
- `bridge/gtkb-work-tree-hygiene-slice-a-detector-004.md` - VERIFIED detector slice for stale workspace/stash/worktree classification.
- `bridge/gtkb-work-tree-hygiene-slice-b-strays-cli-004.md` - VERIFIED `gt hygiene strays` read-only CLI surface.
- `bridge/gtkb-work-tree-hygiene-slice-c-doctor-check-004.md` - VERIFIED doctor visibility for stale work-tree findings.
- `bridge/gtkb-wi4889-auto-finalization-sweep-004.md` and `.claude/rules/auto-finalization-sweep.md` - existing cheap-gated Stop-hook finalizer used as the integration precedent.
- `bridge/gtkb-wi5027-worktree-finalization-triage-003.md` - related Batch A1 implementation report for read-only worktree finalization triage, awaiting verification; this WI must not depend on that unverified implementation.

## Owner Decisions / Input

No new owner decision is required for proposal filing.

Carried-forward authorization:

- `DELIB-20260705-HIGH-PRIORITY-BATCH-A1-APPROVAL` / `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI4979-BATCH-A1-20260705` authorize this WI through the normal bridge process.
- The PAUTH explicitly forbids credential lifecycle, deploy, force-push, secret disclosure, destructive bulk cleanup, broad bulk status mutation, stash drop, branch/worktree prune, untracked file deletion, and committing another session's stale work without specific apply evidence. This proposal preserves those limits.

## Requirement Sufficiency

Existing requirements sufficient.

The governing requirement set is `GOV-WORK-TREE-HYGIENE-001`, the verified Slice A-C bridge chain, WI-4979's backlog text, and the Batch A1 PAUTH. No new GOV/ADR/DCL/SPEC mutation is proposed in this slice.

## Spec-Derived Verification Plan

| Governing surface | Required implementation behavior | Verification |
| --- | --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | Findings classify into deterministic candidate actions with evidence requirements and manual-review fallback. | Extend `platform_tests/scripts/test_work_tree_stray_detector.py` for action taxonomy, registered-artifact preservation, active-session skip, stale tracked/untracked/stash/worktree paths, and byte-identical auto-drop planning without deletion. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | CLI planning derives from fresh git status/stash/worktree/registry reads. | Extend `platform_tests/scripts/test_hygiene_strays_cli.py` to assert fresh source commands, report-only default, and stable JSON/human output for action plans. |
| Batch A1 forbidden operations | No destructive cleanup runs by default; apply mode requires explicit item-level evidence and refuses forbidden categories. | Add focused tests for `groundtruth_kb.hygiene.auto_resolve` and CLI refusal paths proving no `unlink`, `stash drop`, `worktree prune`, or broad commit occurs without evidence. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Existing Stop-hook sweep remains cheap-gated and fail-soft while consulting the new planner in report-only mode. | Extend `platform_tests/hooks/test_auto_finalize_verified_verdicts.py` to assert the sweep can call the planner only after its cheap gate and does not stage source/test paths. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report carries command evidence and spec-to-test mapping. | Post-implementation report must include exact pytest, ruff lint, and ruff format results for changed Python files. |

Minimum verification commands after implementation:

```text
python -m pytest platform_tests\scripts\test_work_tree_stray_detector.py platform_tests\scripts\test_hygiene_strays_cli.py platform_tests\scripts\test_work_tree_hygiene_doctor.py platform_tests\hooks\test_auto_finalize_verified_verdicts.py -q --tb=short
python -m ruff check scripts\hygiene\stray_detector.py groundtruth-kb\src\groundtruth_kb\hygiene\strays.py groundtruth-kb\src\groundtruth_kb\hygiene\auto_resolve.py groundtruth-kb\src\groundtruth_kb\cli.py groundtruth-kb\src\groundtruth_kb\project\doctor.py scripts\auto_finalize_sweep.py platform_tests\scripts\test_work_tree_stray_detector.py platform_tests\scripts\test_hygiene_strays_cli.py platform_tests\scripts\test_work_tree_hygiene_doctor.py platform_tests\hooks\test_auto_finalize_verified_verdicts.py
python -m ruff format --check scripts\hygiene\stray_detector.py groundtruth-kb\src\groundtruth_kb\hygiene\strays.py groundtruth-kb\src\groundtruth_kb\hygiene\auto_resolve.py groundtruth-kb\src\groundtruth_kb\cli.py groundtruth-kb\src\groundtruth_kb\project\doctor.py scripts\auto_finalize_sweep.py platform_tests\scripts\test_work_tree_stray_detector.py platform_tests\scripts\test_hygiene_strays_cli.py platform_tests\scripts\test_work_tree_hygiene_doctor.py platform_tests\hooks\test_auto_finalize_verified_verdicts.py
gt hygiene strays --format json
```

## Risk / Rollback

Risk is moderate because this work is adjacent to files, stashes, worktrees, commits, and hooks. The first implementation must therefore be report-only by default and must fail closed on ambiguous action evidence. The apply surface may be implemented only as a guarded refusal/allowlist framework in this slice; actual live destructive cleanup remains out of scope.

Rollback is a single revert of the implementation commit. Since bridge files are append-only, rollback should leave this proposal and any implementation report in place and file a corrective bridge follow-up if LO identifies an unsafe action path.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4979-worktree-hygiene-auto-resolve-actuator`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`feat:` because the change adds a new deterministic work-tree hygiene action-planning capability and CLI/reporting behavior.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
