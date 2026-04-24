NO-GO

# Loyal Opposition Review — GT-KB / Application Boundary Mechanism Audit

**Reviewed proposal:** `bridge/gtkb-app-boundary-mechanism-audit-001.md`
**Date:** 2026-04-24
**Reviewer:** Codex (Loyal Opposition)
**Verdict:** NO-GO

## Rationale

The audit identifies a real application-boundary question, but the current draft overstates the managed-artifact customization gap and includes at least one relocation classification that is not supported by the cited project files. Those defects materially affect the proposal's core conclusion and sequencing rationale, so the audit should be revised before it is used as the basis for follow-on work.

## Findings

### 1. High — The customization-gap verdict misstates current upgrade behavior for drifted managed files

The proposal says a managed hook/rule/skill edit is clobbered on the next `gt project upgrade` because managed file rows use `upgrade_policy = "overwrite"` and `warn` only logs a warning (`bridge/gtkb-app-boundary-mechanism-audit-001.md:120-133`, `:248-250`). The live upgrade planner does not do that by default. It plans a `skip` action when a managed file differs from the template, with reason `File differs from template (customized?) — use --force to overwrite` (`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:181-211`).

Impact: the proposed verdict "cannot customize content of managed artifacts without ... losing upstream updates" is overstated as written. The real gap is narrower: local customization survives by default, but automatic convergence and a first-class extension contract are missing. That distinction matters because Track A sequencing at `:246-250` is justified using the stronger "relocation will clobber adopter edits" framing.

Required action: revise §§3.2, 3.3, and 5.3 to distinguish between "default upgrade skips drifted managed files" and "there is no explicit supported customization/extension mechanism for managed content."

### 2. Medium — The relocation inventory marks `release-candidate-gate` as definitely cross-cutting even though the checked-in skill and script are Agent Red-specific

The audit places `release-candidate-gate` in the "Definitely cross-cutting → RELOCATE" bucket (`bridge/gtkb-app-boundary-mechanism-audit-001.md:157-168`). The live skill metadata says `project: agent-red-customer-experience`, the description is explicitly "Agent Red release-candidate gate," and the commands all call the local `scripts/release_candidate_gate.py` wrapper (`E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\.claude\skills\release-candidate-gate\SKILL.md:2-3`, `:9-12`, `:23-45`). The script itself opens with `Non-deploying release-candidate gate for Agent Red` and checks Agent Red-specific paths such as `scripts/deploy/production-gateway-generated.yaml` (`E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\scripts\release_candidate_gate.py:2-6`, `:53-79`).

Impact: the relocation totals in §4.6 are inflated by at least one item, and the "definitely relocate" bucket is not yet evidence-backed for this skill.

Required action: reclassify `release-candidate-gate` as `KEEP LOCAL or split`, or add evidence showing which subparts are truly GT-KB-generic.

### 3. Medium — The live inventory baseline is not internally consistent and omits already-implemented divergence-policy options

The proposal says `managed-artifacts.toml` has "51 records" while listing a breakdown of 19 hooks + 10 rules + 6 skills + 15 settings-hook-registrations + 4 gitignore-patterns (`bridge/gtkb-app-boundary-mechanism-audit-001.md:53`). A live parse of `templates/managed-artifacts.toml` reports `total 54` with class counts `{'hook': 19, 'rule': 10, 'skill': 6, 'settings-hook-registration': 15, 'gitignore-pattern': 4}`. Separately, Track A3 proposes adding divergence-policy values `block` and `preserve-with-warning` (`bridge/gtkb-app-boundary-mechanism-audit-001.md:230-233`), but the current type system already includes `error` and `force-merge-on-upgrade` in `DivergencePolicyEnum` (`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\managed_registry.py:69-72`, `:98-102`).

Impact: the audit baseline is not yet reliable enough for design follow-through. Before proposing schema growth, the draft should explain why existing implemented divergence-policy values are insufficient.

Required action: fix the row-count narrative in §2 and add an explicit evaluation of `error` / `force-merge-on-upgrade` before proposing new divergence-policy enum values.

### 4. Low — `Files Touched` contradicts the audit-only framing

The proposal says the bridge is audit-only and that the only artifact produced is the bridge itself (`bridge/gtkb-app-boundary-mechanism-audit-001.md:254`), but §6 then lists `memory/work_list.md` as modified (`:258-269`).

Impact: this creates avoidable ambiguity about whether the bridge is descriptive or also proposing a side-effecting backlog mutation.

Required action: either remove the `memory/work_list.md` entry from §6 or state explicitly that it is a recommended follow-up, not a completed change.

## Evidence Commands

Reviewed with filesystem reads in the Agent Red and `groundtruth-kb` worktrees, including:

- `Get-Content -Raw .claude/rules/file-bridge-protocol.md`
- `Get-Content -Raw bridge/INDEX.md`
- `Get-Content -Raw bridge/gtkb-app-boundary-mechanism-audit-001.md`
- `python -c "import tomllib, pathlib, collections; ..."` against `groundtruth-kb/templates/managed-artifacts.toml`
- line-numbered reads of:
  - `groundtruth-kb/src/groundtruth_kb/project/upgrade.py`
  - `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py`
  - `.claude/skills/release-candidate-gate/SKILL.md`
  - `scripts/release_candidate_gate.py`

## Conditions To Reach GO

1. Correct the managed-file customization analysis so it matches the live `skip unless --force` behavior.
2. Rework the relocation inventory where the evidence is still Agent Red-specific, starting with `release-candidate-gate`.
3. Fix the inventory/count baseline and evaluate existing divergence-policy options before proposing new ones.
4. Resolve the `Files Touched` contradiction.
