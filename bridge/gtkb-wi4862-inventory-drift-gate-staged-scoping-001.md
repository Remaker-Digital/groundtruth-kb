NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: eb4f5b12-588a-43b5-bf6b-5439c7a97cf0
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

bridge_kind: prime_proposal

# gtkb-wi4862-inventory-drift-gate-staged-scoping — Scope the pre-commit inventory-drift gate to the staged set so a headless session can self-finalize commits

Document: gtkb-wi4862-inventory-drift-gate-staged-scoping
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-27 UTC
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4862
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4862-INVENTORY-DRIFT-GATE-STAGED-SCOPING
Recommended commit type: fix

target_paths: ["scripts/check_dev_environment_inventory_drift.py", "platform_tests/scripts/test_check_dev_environment_inventory_drift.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

`scripts/check_dev_environment_inventory_drift.py` computes `material_inventory_drift` by comparing the committed dev-environment-inventory baseline against a freshly-generated current inventory (`collect_inventory`), which scans the entire WORKING TREE — including untracked files. Any single untracked inventoried-surface file (e.g. a new `.claude/rules/*.md`, an untracked `.claude/hooks/*.py`, etc.) sets `material_inventory_drift = True` and hard-blocks EVERY commit, regardless of what the current commit stages. This is the WI-4862 defect and the root cause of the 2026-06-26 dispatcher finalization pile-up; this session it blocked the headless Cursor Loyal Opposition session from committing its own VERIFIED finalization for WI-4855 / WI-4845 (the verdicts had to be committed Prime-side, commit `99aa43550`).

This proposal scopes the material-drift block to the staged set **only in `--staged` (pre-commit) mode**: when `staged=True` and `material_inventory_drift` is detected but NO staged path matches an inventoried surface, the material-drift finding is downgraded from a blocking error to a warning. The pre-commit hook already invokes the checker with `--staged --allow-review-evidence` (`.githooks/pre-commit` L17-19), so no hook change is required. The release-candidate gate (`scripts/release_candidate_gate.py`) calls `evaluate_drift(PROJECT_ROOT)` with the default `staged=False` (whole-tree) and is intentionally NOT changed: release-readiness still hard-blocks on any baseline/environment drift.

### Behavior change (precise)

`evaluate_drift(..., staged=True)`:
- material drift + at least one staged path is an inventoried surface -> **block** (the commit changes a surface; the baseline must be updated — unchanged behavior).
- material drift + NO staged path is an inventoried surface -> **warn, do not block** (the drift is from untracked/unstaged surfaces unrelated to this commit — the fix).
- no material drift -> unchanged.

`evaluate_drift(..., staged=False)` (release gate): unchanged — material drift always blocks.

### Inventoried-surface patterns

A new module constant `INVENTORIED_SURFACE_PATTERNS` enumerates the paths `collect_inventory` derives the public inventory from, sourced from `scripts/collect_dev_environment_inventory.py` `_repo_surfaces`: `.claude/rules/*.md`, `.claude/skills/*/SKILL.md`, `.claude/hooks/*.py`, `.claude/commands/registry.json`, `.claude/settings.json`, `.github/workflows/*`. A staged path matching any of these is "surface-affecting." (Keeping the constant in the drift checker next to the consuming logic, with a comment pointing at the collect source, is the lowest-drift placement; a follow-up may export the patterns from the collector if they diverge.)

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; filed as the next append-only numbered bridge file.
- `GOV-17` (Automation script modification approval gate) — this modifies an automation/governance script; the change is bridge-reviewed and owner-authorized (DELIB-20266208).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — satisfied: cites governing specs; tests mapped below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — satisfied: WI-4862 + PROJECT-GTKB-DISPATCHER-RELIABILITY + active PAUTH metadata present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied: the staged-scoping behavior maps to derived tests.
- `GOV-STANDING-BACKLOG-001` — WI-4862 is an authorized standing-backlog item under the active project.

## Prior Deliberations

- `DELIB-20266208` — Owner AUQ (S20260627): fix WI-4862 first so a headless Loyal Opposition session can self-finalize its VERIFIED commit; pre-commit staged-mode gate must not block when the staged set changes no inventoried surface; release gate stays strict.
- `DELIB-20266203` — autonomous-loop plan; WI-4862 is the discovered self-finalization blocker for PHASE Y.
- `DELIB-20266201` — owner authorization context for the dispatcher-reliability daemon program (the pile-up DELIB-20266201 references).

## Owner Decisions / Input

Implementation-authorized under `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4862-INVENTORY-DRIFT-GATE-STAGED-SCOPING` (active; includes WI-4862 + GOV-17; cites `DELIB-20266208`). The owner selected "Fix WI-4862 first" via AskUserQuestion (S20260627), authorizing the unblocking behavior change with the explicit constraint that the release-candidate gate retains its current strictness. The intended behavior change (staged-mode scoping) is the owner-stated remedy.

## Requirement Sufficiency

Existing requirements sufficient. The governing requirement is that the inventory-drift gate detect baseline/environment drift while not blocking commits whose staged scope does not change an inventoried surface (WI-4862 acceptance summary). DELIB-20266208 sets the staged-mode scoping shape and the release-gate-strictness constraint. No new requirement; this corrects the gate to meet the existing acceptance criteria.

## Spec-Derived Verification Plan

| Spec / clause | Test | Assertion |
|---|---|---|
| WI-4862 acceptance: untracked-surface-file scenario does not block | `test_staged_mode_material_drift_warns_when_no_staged_surface` (new) | with `staged=True`, material drift present, and the staged changed_path set containing only non-surface paths (e.g. a `bridge/*.md` or a source file), `evaluate_drift` returns `status="pass"` with a warning and no `normalized_inventory_drift` blocking entry. |
| Staged surface change still blocks | `test_staged_mode_material_drift_blocks_when_staged_surface` (new) | with `staged=True`, material drift present, and a staged `.claude/rules/*.md` path, `evaluate_drift` returns `status="fail"` (block retained). |
| Release-gate strictness preserved | `test_unstaged_mode_material_drift_still_blocks` (new) | with `staged=False` (release-gate mode), material drift present, `evaluate_drift` returns `status="fail"` regardless of changed-path surface membership. |
| Non-regression | existing `test_check_dev_environment_inventory_drift.py` suite | PASS — protected-change classification, review-evidence acceptance, baseline-update acceptance unchanged. |

Commands (pre-report): targeted `pytest` over `test_check_dev_environment_inventory_drift.py` via the repo venv; `ruff check` AND `ruff format --check` on the changed files. Material drift will be simulated deterministically via `current_inventory=` / `changed_paths=` overrides (no environment mutation).

## Risk / Rollback

- **Risk:** loosening a commit gate could let a real surface change land without a baseline update. Mitigated: the block is retained whenever a staged path IS an inventoried surface (the only case where THIS commit changes the inventory); the release-candidate gate (whole-tree) is unchanged, so release-readiness still catches any accumulated baseline drift before a tag.
- **Pattern-drift risk:** `INVENTORIED_SURFACE_PATTERNS` is a hand-maintained mirror of `collect_inventory`'s surfaces; if the collector adds a surface and this list is not updated, a staged change to the new surface would not block at pre-commit time (still caught at release-gate). Mitigated by the source-pointer comment and a follow-up to export the patterns from the collector.
- **Rollback:** single-commit revert restores the unconditional material-drift block. No KB mutation (`kb_mutation_in_scope: false`); append-only bridge history untouched.

## Recommended Commit Type

`fix` — repairs the over-broad commit gate (material drift from untracked unstaged surfaces hard-blocking unrelated commits, including headless self-finalization). No new capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
