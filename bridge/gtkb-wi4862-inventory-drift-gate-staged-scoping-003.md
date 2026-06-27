NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: d5a77c21-caee-404a-8fb3-6629ba276960
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

bridge_kind: implementation_report

# gtkb-wi4862-inventory-drift-gate-staged-scoping — Post-implementation report: staged-mode scoping of the pre-commit inventory-drift gate

Document: gtkb-wi4862-inventory-drift-gate-staged-scoping
Version: 003
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-27 UTC
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4862
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4862-INVENTORY-DRIFT-GATE-STAGED-SCOPING
Responds to: bridge/gtkb-wi4862-inventory-drift-gate-staged-scoping-002.md (GO)
Recommended commit type: fix

target_paths: ["scripts/check_dev_environment_inventory_drift.py", "platform_tests/scripts/test_check_dev_environment_inventory_drift.py"]

implementation_scope: source
requires_review: false
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implemented the GO'd (`-002`) staged-scoping of the pre-commit inventory-drift gate. `evaluate_drift(..., staged=True)` no longer hard-blocks a commit when whole-tree `material_inventory_drift` is present but NO staged path is an inventoried surface; in that case the material-drift finding is downgraded from a blocking error to a warning. The block is retained whenever a staged path IS an inventoried surface (this commit changes the inventory) and whenever `staged=False` (the release-candidate gate). This removes the WI-4862 self-finalization blocker: a headless session committing only its own (non-surface) staged set is no longer blocked by untracked/unstaged inventoried surfaces elsewhere in the working tree.

## Implemented Changes

`scripts/check_dev_environment_inventory_drift.py`:
- Added module constant `INVENTORIED_SURFACE_PATTERNS` — a hand-maintained mirror of the surfaces collected by `scripts/collect_dev_environment_inventory.py` `_repo_surfaces` (`.claude/rules/*.md`, `.claude/skills/*/SKILL.md`, `.claude/hooks/*.py`, `.claude/commands/registry.json`, `.github/workflows/*`) plus the `.claude/settings.json` settings-state surface, with a source-pointer comment.
- Added helper `staged_paths_touch_inventoried_surface(changed_paths)` using the existing `fnmatch.fnmatchcase` convention.
- In `evaluate_drift`, the `material_inventory_drift` block is now conditional: in `staged=True` mode with no staged inventoried surface it appends a warning instead of a blocking entry; otherwise (staged surface touched OR `staged=False`) it blocks exactly as before. The returned `material_inventory_drift` flag is unchanged (still True in the warn case).

`platform_tests/scripts/test_check_dev_environment_inventory_drift.py`:
- Added three spec-derived tests (warn / block-on-surface / unstaged-still-blocks).

No other surfaces changed. `.githooks/pre-commit` already invokes the checker with `--staged --allow-review-evidence`, so no hook change is required. `scripts/release_candidate_gate.py` calls `evaluate_drift` with the default `staged=False` and is intentionally unchanged.

## Specification Links

Carried forward from `-001`:
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; filed as the next append-only numbered bridge file.
- `GOV-17` — Automation script modification approval gate; modifies an automation/governance script; bridge-reviewed and owner-authorized (DELIB-20266208).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — specs cited; tests mapped below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — WI-4862 + PROJECT-GTKB-DISPATCHER-RELIABILITY + active PAUTH metadata present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — staged-scoping behavior maps to derived tests, executed below.
- `GOV-STANDING-BACKLOG-001` — WI-4862 is an authorized standing-backlog item under the active project.

## Spec-to-Test Mapping

| Spec / clause | Test | Result |
|---|---|---|
| WI-4862 acceptance: untracked-surface drift does not block a staged commit | `test_staged_mode_material_drift_warns_when_no_staged_surface` | PASS — `status=pass`, `outcome=clean`, `material_inventory_drift=True`, `blocking=[]`, downgrade warning present |
| Staged inventoried-surface change still blocks | `test_staged_mode_material_drift_blocks_when_staged_surface` | PASS — `status=fail`, blocking reason `normalized_inventory_drift` |
| Release-gate strictness preserved (`staged=False`) | `test_unstaged_mode_material_drift_still_blocks` | PASS — `status=fail` regardless of surface membership |
| Non-regression | existing 14 tests in the suite | PASS |

## Verification Evidence

Repo venv `groundtruth-kb/.venv/Scripts/python.exe`:
- `python -m pytest platform_tests/scripts/test_check_dev_environment_inventory_drift.py -q` → `17 passed in 0.47s`.
- `python -m ruff check` on both changed files → `All checks passed!`.
- `python -m ruff format --check` on both changed files → `2 files already formatted`.
- Live smoke: `python scripts/check_dev_environment_inventory_drift.py --staged --allow-review-evidence` → `PASS (clean)`. Release-gate mode (default) unchanged — still blocks protected-artifact/baseline changes on the live tree. (Live `material_inventory_drift` is currently False, so the new warn branch is exercised deterministically by the unit test above, per the proposal's simulated-drift verification plan.)

## Requirement Sufficiency

Existing requirements sufficient. The governing requirement is that the inventory-drift gate detect baseline/environment drift while not blocking commits whose staged scope changes no inventoried surface (WI-4862 acceptance). DELIB-20266208 sets the staged-mode scoping shape and the release-gate-strictness constraint. No new requirement; this corrects the gate to meet the existing acceptance criteria.

## Owner Decisions / Input

Implementation-authorized under `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4862-INVENTORY-DRIFT-GATE-STAGED-SCOPING` (active; includes WI-4862 + GOV-17; cites `DELIB-20266208`). The owner selected "Fix WI-4862 first" via AskUserQuestion (S20260627, archived as `DELIB-20266208`), authorizing the unblocking behavior change with the explicit constraint that the release-candidate gate retains its current strictness. No additional owner decision is required for this report.

## Prior Deliberations

- `DELIB-20266208` — owner AUQ (S20260627): fix WI-4862 first; pre-commit staged-mode gate must not block when the staged set changes no inventoried surface; release gate stays strict.
- `DELIB-20266203` — autonomous-loop plan; WI-4862 is the self-finalization blocker for PHASE Y.
- `bridge/gtkb-wi4862-inventory-drift-gate-staged-scoping-001.md` (NEW proposal), `-002.md` (Cursor LO GO).

## Risk / Rollback

- Risk: loosening a commit gate could let a real surface change land without a baseline update. Mitigated: the block is retained whenever a staged path IS an inventoried surface; the release-candidate gate (whole-tree, `staged=False`) is unchanged, so release-readiness still catches accumulated baseline drift before a tag.
- Pattern-drift risk: `INVENTORIED_SURFACE_PATTERNS` is a hand-maintained mirror of `collect_inventory`'s surfaces; a new collector surface not added here would not block at pre-commit time (still caught at release-gate). Mitigated by the source-pointer comment.
- Rollback: single-commit revert restores the unconditional material-drift block. No KB mutation (`kb_mutation_in_scope: false`); append-only bridge history untouched.

## Recommended Commit Type

`fix` — repairs the over-broad commit gate (material drift from untracked unstaged surfaces hard-blocking unrelated commits, including headless self-finalization). No new capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
