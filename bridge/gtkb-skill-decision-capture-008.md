# GT-KB Skill Decision Capture - Codex Review of Revised Proposal 007

**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/gtkb-skill-decision-capture-007.md`
**Prior review:** `bridge/gtkb-skill-decision-capture-006.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target repo HEAD:** `b5e5c6c`

## Claim

Do not implement `-007` as written. The revision fixes the only `-006`
finding: the proposed doctor check now requires keyword construction for
`ToolCheck.status` and `ToolCheck.message`, which matches the target repo.

However, because the target repo is now `b5e5c6c` after Tier A #2 landed, the
retained upgrade contract is no longer explicit enough for implementation.
`plan_upgrade()` now delegates managed-file planning to hook/rule-specific
helpers and gates those managed-file checks on scaffold-version mismatch. A
skill bridge that only says "add `_MANAGED_SKILLS` + extend
`_map_managed_to_template()`" can miss existing adopters and can also produce
tests that fail against the current planner.

## Prior Deliberations

No prior deliberations found for `skill decision capture owner decision
deliberation capture`.

Verification command:

```text
python -m groundtruth_kb deliberations search "skill decision capture owner decision deliberation capture"
```

Result:

```text
No deliberations match 'skill decision capture owner decision deliberation capture'.
```

## Findings

### 1. Skill upgrade planning is underspecified against the current `b5e5c6c` upgrader

**Severity:** High

**Evidence:**

- `-007` explicitly targets `groundtruth-kb` at `b5e5c6c`:
  `bridge/gtkb-skill-decision-capture-007.md:10`.
- `-007` retains the earlier upgrade contract as "plan_upgrade(target) for
  skip plan; execute_upgrade(target, actions, force=True) for overwrite":
  `bridge/gtkb-skill-decision-capture-007.md:162-163`.
- `-007` says exit criteria 1-7 are unchanged, including
  `_MANAGED_SKILLS`, upgrade semantics, and force-at-execute behavior:
  `bridge/gtkb-skill-decision-capture-007.md:170-175`.
- Current `upgrade.py` maps only hooks and rules:
  `src/groundtruth_kb/project/upgrade.py:85-90`.
- Current `plan_upgrade()` does not build one flat managed-file list. It
  delegates to `_plan_managed_hooks()` and `_plan_managed_rules()`:
  `src/groundtruth_kb/project/upgrade.py:94`,
  `src/groundtruth_kb/project/upgrade.py:148`,
  `src/groundtruth_kb/project/upgrade.py:329-331`.
- Those managed-file checks are gated on
  `manifest.scaffold_version != __version__`:
  `src/groundtruth_kb/project/upgrade.py:329`.
- Existing regression coverage now encodes the version gate:
  `tests/test_upgrade.py:468-478`.
- `-007`'s proposed doctor message tells users to restore the missing skill
  with `gt project upgrade --apply`:
  `bridge/gtkb-skill-decision-capture-007.md:93-101`.

**Risk / impact:**

G2 requires explicit adopter installation. On the current checkout, adding a
skill manifest constant and a template mapping is not sufficient by itself:
`plan_upgrade()` must also call a skill planner. The proposal does not say
where that call belongs in the now-refactored planner.

There is also a version-gating ambiguity. If the implementation adds skills
as ordinary managed files inside the existing
`manifest.scaffold_version != __version__` block, then existing projects only
receive `add` actions when their manifest version is older than the installed
package. If this bridge does not also bump the scaffold/package version, a
current-version adopter can get a doctor warning whose recommended
`gt project upgrade --apply` path does not restore the missing skill.

This makes the retained upgrade test sketches unsafe if implemented literally,
especially the "scaffold, delete skill, plan_upgrade -> add" shape from the
earlier proposal chain. A fresh scaffold writes the current scaffold version,
and the current planner intentionally skips managed-file add/skip checks at
the current version.

**Required action:**

Revise the proposal to specify the skill upgrade path against `b5e5c6c`
explicitly. Minimum acceptable contract:

1. Add `_MANAGED_SKILLS` in `upgrade.py`.
2. Add `_plan_managed_skills(target, profile)` rather than relying on the
   hook/rule helpers.
3. Add `actions.extend(_plan_managed_skills(target, profile))` in the intended
   location in `plan_upgrade()`.
4. State whether skill managed-file checks are version-gated like hooks/rules
   or unconditional like settings/gitignore drift.
5. If version-gated, require a version/scaffold-version bump in this bridge's
   implementation, and write the skill upgrade tests with an older
   `scaffold_version` fixture.
6. If unconditional, explain why skills are drift-repair checks rather than
   managed scaffold-file checks, and add a current-version test proving
   `gt project upgrade --apply` restores a missing skill exactly as the doctor
   message promises.

Until this is explicit, G2 is not met for existing adopter delivery.

## Accepted Fixes From `-007`

The `-006` finding is addressed and should be retained:

- The proposed doctor implementation constructs `ToolCheck(...)` with
  `status=` and `message=` keyword arguments:
  `bridge/gtkb-skill-decision-capture-007.md:79-110`.
- The proposal explicitly calls out the field-order trap and bans positional
  construction for `status` and `message`:
  `bridge/gtkb-skill-decision-capture-007.md:113-116`,
  `bridge/gtkb-skill-decision-capture-007.md:177-181`.
- Current `ToolCheck` field order confirms why this is necessary:
  `src/groundtruth_kb/project/doctor.py:19-28`.

The previously accepted items remain acceptable:

- `record_decision()` call shape with the seven required
  `insert_deliberation()` arguments is aligned with the current DB API:
  `src/groundtruth_kb/db.py:4189-4208`.
- `source_type="owner_conversation"` and `outcome="owner_decision"` remain
  valid:
  `src/groundtruth_kb/db.py:4214-4227`.
- `db.get_deliberation(delib_id)` remains available for the pre-insert
  collision check:
  `src/groundtruth_kb/db.py:4325`.
- Force still belongs to `execute_upgrade(..., force=True)`, not
  `plan_upgrade()`:
  `src/groundtruth_kb/project/upgrade.py:300`,
  `src/groundtruth_kb/project/upgrade.py:336-340`.

## Verification Performed

Target repo evidence checks:

```text
git rev-parse --short HEAD
b5e5c6c

python -c "from inspect import signature; from groundtruth_kb.project.doctor import ToolCheck; from groundtruth_kb.db import KnowledgeDB; from groundtruth_kb.project.upgrade import plan_upgrade, execute_upgrade; print(signature(ToolCheck)); print(ToolCheck('skill:decision-capture', False, False, 'warning', 'missing')); print(signature(KnowledgeDB.insert_deliberation)); print(signature(plan_upgrade)); print(signature(execute_upgrade))"
```

Key signature result:

```text
ToolCheck(name='skill:decision-capture', required=False, found=False, version='warning', min_version='missing', status='pass', message='', auto_installable=False)
```

Targeted tests:

```text
python -m pytest tests/test_upgrade.py -q --tb=short
22 passed, 1 warning in 0.30s

python -m pytest tests/test_doctor.py -q --tb=short
29 passed, 1 warning in 1.24s

python -m pytest tests/test_deliberations.py -q --tb=short
70 passed, 1 warning in 28.06s
```

## Decision Needed From Owner

None. Prime should post `gtkb-skill-decision-capture-009.md` as `REVISED`
with the skill upgrade planner and version-gating contract corrected for the
current `b5e5c6c` target repo.
