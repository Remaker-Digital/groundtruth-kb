# GT-KB Skill `/gtkb-decision-capture` (REVISED-4)

**Status:** REVISED (addresses NO-GO at `-008`)
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S298
**NO-GO reference:** `bridge/gtkb-skill-decision-capture-008.md`
**Supersedes:** `bridge/gtkb-skill-decision-capture-007.md`
**Parent scope GO:** `bridge/gtkb-operational-skills-tier-a-004.md`
**Target repo:** `groundtruth-kb` at main (`37a88cc` — Tier A #2 with -010 fix)

## Summary of Revision

Single-finding revision against the **current** `upgrade.py` structure
(post-Tier A #2 + post-`-010` fix). Aligns skill upgrade delivery with
the non-disruptive-upgrade priority (owner directive S298) and the
`_plan_missing_managed_files` helper now present in `upgrade.py`.

All `-007` architectural decisions retained except for the skill
upgrade planning section, which is rewritten against the current planner.

**One specific fix** (Codex `-008` Finding 1):

- **High-1 (skill upgrade path vs current planner)**: `-007` said
  "extend `_map_managed_to_template` + add `_MANAGED_SKILLS`". That's
  insufficient now — `plan_upgrade()` delegates to hook/rule-specific
  helpers and the missing-file check is in a new
  `_plan_missing_managed_files` helper (landed as part of scanner-safe-writer
  `-010` fix at commit `37a88cc`). Skills need their own parallel
  helper AND to participate in the unconditional missing-file check.
  See §Fix 1 below.

## Fix 1 — Skill Upgrade Planner Aligned With Current `upgrade.py` (`-008` Finding 1)

### Current `upgrade.py` structure (at `37a88cc`)

- `_MANAGED_HOOKS: list[str]` — 7 hook files
- `_MANAGED_RULES: list[str]` — 5 rule files
- `_filter_hooks_for_profile(profile)` — profile-filter helper
- `_filter_rules_for_profile(profile)` — profile-filter helper
- `_plan_missing_managed_files(target, profile)` — **unconditional**;
  emits `add` for any missing managed file in the profile's hook/rule
  sets (added S298 per bridge `-010` Finding 1 fix)
- `_plan_managed_hooks(target, profile)` — **version-gated**; emits
  `skip` for hash-drift present files (no longer emits `add`)
- `_plan_managed_rules(target, profile)` — same as above
- `_plan_settings_registration(target, profile)` — unconditional
- `_plan_gitignore_patterns(target, profile)` — unconditional
- `plan_upgrade()` calls unconditional helpers always; calls
  managed-hooks/rules only when `scaffold_version != __version__`

### Revised skill delivery design

Skills follow the **same two-layer pattern** as hooks/rules, leveraging
the existing `_plan_missing_managed_files` + version-gated hash-drift
model. This directly advances the owner's non-disruptive-upgrade
priority (see `memory/project_gtkb_non_disruptive_upgrade_priority.md`):
adopters at current scaffold version receive missing-skill repair
without a version bump.

**Five concrete changes to `upgrade.py`:**

1. **Add module-level `_MANAGED_SKILLS` list:**
   ```python
   _MANAGED_SKILLS = [
       ".claude/skills/decision-capture/SKILL.md",
       ".claude/skills/decision-capture/helpers/record_decision.py",
   ]
   ```

2. **Add `_filter_skills_for_profile(profile: ProjectProfile) -> list[str]`:**
   ```python
   def _filter_skills_for_profile(profile: ProjectProfile) -> list[str]:
       """Return managed skills applicable to the profile.

       Skills are dual-agent-only for Phase A; base profile gets no skills.
       Parallel shape to _filter_hooks_for_profile / _filter_rules_for_profile.
       """
       if not profile.includes_bridge:
           return []
       return list(_MANAGED_SKILLS)
   ```

3. **Extend `_map_managed_to_template()` with skill mapping:**
   ```python
   def _map_managed_to_template(managed: str) -> str | None:
       if managed.startswith(".claude/hooks/"):
           return "hooks/" + managed.split("/")[-1]
       if managed.startswith(".claude/rules/"):
           return "rules/" + managed.split("/")[-1]
       if managed.startswith(".claude/skills/"):
           # Preserve subdirectory structure for helpers/ tree:
           # ".claude/skills/decision-capture/SKILL.md" →
           # "skills/decision-capture/SKILL.md"
           return "skills/" + managed.removeprefix(".claude/skills/")
       return None
   ```

4. **Extend `_plan_missing_managed_files()` to include skills:**
   ```python
   def _plan_missing_managed_files(target: Path, profile: ProjectProfile) -> list[UpgradeAction]:
       """Plan 'add' actions for any missing managed hook/rule/skill file.
       Unconditional (not version-gated): non-disruptive repair for
       existing adopters at current scaffold version."""
       actions: list[UpgradeAction] = []
       for mfile in (
           _filter_hooks_for_profile(profile)
           + _filter_rules_for_profile(profile)
           + _filter_skills_for_profile(profile)  # NEW
       ):
           # ... existing logic unchanged ...
   ```

5. **Add `_plan_managed_skills(target: Path, profile: ProjectProfile) -> list[UpgradeAction]`:**
   ```python
   def _plan_managed_skills(target: Path, profile: ProjectProfile) -> list[UpgradeAction]:
       """Plan 'skip' actions for managed skills that differ from template.
       Missing-file case is handled by _plan_missing_managed_files.
       Version-gated: only runs at scaffold_version mismatch, parallel
       to _plan_managed_hooks / _plan_managed_rules.
       """
       actions: list[UpgradeAction] = []
       for mfile in _filter_skills_for_profile(profile):
           project_path = target / mfile
           if not project_path.exists():
               continue  # Missing-file case handled by _plan_missing_managed_files

           template_rel = _map_managed_to_template(mfile)
           if template_rel is None:
               continue

           template_h = _template_hash(template_rel)
           if template_h is None:
               continue

           project_h = _file_hash(project_path)
           if project_h == template_h:
               continue

           actions.append(
               UpgradeAction(
                   file=mfile,
                   action="skip",
                   reason="File differs from template (customized?) — use --force to overwrite",
               )
           )
       return actions
   ```

6. **Wire `_plan_managed_skills` into `plan_upgrade()`:**
   ```python
   # Existing version-gated block
   if manifest.scaffold_version != __version__:
       actions.extend(_plan_managed_hooks(target, profile))
       actions.extend(_plan_managed_rules(target, profile))
       actions.extend(_plan_managed_skills(target, profile))  # NEW
   ```

### Version-gating decision (per `-008` required action #4)

Skills are **both**:
- **Missing-file repair: unconditional** — via extension of
  `_plan_missing_managed_files`. This means a same-version adopter
  who deletes the skill or never received it (e.g., early dual-agent
  scaffolds before skills existed) receives an `add` action from
  `gt project upgrade --apply` without requiring a version bump.
  **This is the non-disruptive path**.
- **Hash-drift repair: version-gated** — via
  `_plan_managed_skills()`. Same semantics as hooks/rules: if the
  adopter customized the file, it stays `skip` unless `--force`.
  Version gate reflects the convention that files at current
  scaffold version are assumed at-template (or intentionally
  customized).

No version bump required by **this** bridge. Skill files land via
missing-file repair at current scaffold version. A future v0.6.0
release can bundle multiple skill additions together if needed, but
this bridge is independent.

### Rationale for unconditional missing-file repair

Matches the pattern Tier A #2 established (settings.json, gitignore,
hook files are all unconditional drift checks). Skills belong in the
same class because:
- Adopters may predate the skill (haven't re-scaffolded)
- `gt project upgrade` is the expected remediation path per doctor
  warning
- Same-version + missing = a real drift state (not a customization)
- The doctor message "run `gt project upgrade --apply`" must be
  accurate at any version

### Tests (updated per this revision)

Replaces `-007` § tests/test_upgrade_skills.py. All tests use the
current API (`plan_upgrade(target)`, `execute_upgrade(target, actions, force=...)`).

**Missing-file tests (unconditional, same-version):**

1. `test_plan_upgrade_adds_missing_skill_at_same_version` — adopter at
   current scaffold version missing `.claude/skills/decision-capture/SKILL.md`
   → `add` action emitted.
2. `test_plan_upgrade_adds_missing_skill_helper_at_same_version` —
   missing `helpers/record_decision.py` → `add` action.
3. `test_execute_creates_missing_skill_files_at_same_version` —
   end-to-end: plan + execute; skill files land at expected paths with
   non-empty content.

**Version-gated hash-drift tests:**

4. `test_plan_upgrade_skips_customized_skill_at_version_mismatch` —
   customize SKILL.md at an older `scaffold_version`; plan_upgrade at
   current `__version__` → `skip` action with "customized" reason.
5. `test_execute_upgrade_applies_customized_skill_with_force` —
   scaffold with older version + customized file; `execute_upgrade(..., force=True)`
   → file overwritten from template.
6. `test_plan_upgrade_silent_on_at_template_skill_at_version_mismatch` —
   scaffold older version, no customization; plan_upgrade → no
   skill-related skip action (file matches template).

**Profile gating:**

7. `test_base_profile_no_skill_actions` — `local-only` profile: skill
   files neither `add` nor `skip` (profile returns empty managed set).

### Doctor check (unchanged from `-007`)

Still uses keyword construction per `-007` Fix (which was correct and
accepted by `-008`):

```python
return ToolCheck(
    name="skill:decision-capture",
    required=False,
    found=False,
    status="warning",
    message=".claude/skills/decision-capture/ missing: SKILL.md. Run `gt project upgrade --apply` to restore.",
)
```

**The doctor remediation message is now accurate** because of this
revision's unconditional missing-file repair: at any scaffold version,
`gt project upgrade --apply` does restore a missing skill.

## Retained from `-007` (Confirmed by `-008` "Accepted Fixes")

- **Doctor `ToolCheck` uses kwargs** for `status`/`message` per
  `-006` fix (the only `-007` change; confirmed OK)
- **`record_decision()` helper**: all 7 positional args per `-004` fix
- **DELIB-ID collision check** via `db.get_deliberation(candidate_id)`
- **Force at `execute_upgrade()` layer** per `-004` fix
- **`_map_managed_to_template()` subdir preservation**: `removeprefix(".claude/skills/")`
- **Dual-agent-only scaffold destination**: `.claude/skills/`
- **No pyproject.toml edit**: templates tree already force-included
- **Module-local `DeliberationIDCollisionError` + `DeliberationInsertFailed`**

## Updated Implementation Scope

**New files:**
- `templates/skills/decision-capture/SKILL.md` (~100 lines)
- `templates/skills/decision-capture/helpers/record_decision.py` (~100 lines)
- `tests/test_decision_capture_helper.py` (~7 tests)
- `tests/test_scaffold_skills.py` (~3 tests)
- `tests/test_upgrade_skills.py` (~7 tests per this revision)
- `tests/test_doctor_skills.py` (~3 tests with kwargs pattern)

**Modified files:**
- `src/groundtruth_kb/project/scaffold.py`:
  `_copy_skill_templates()` + `_MANAGED_SKILLS_INITIAL` at scaffold time
- `src/groundtruth_kb/project/upgrade.py`: **6 concrete edits** (see
  §Fix 1 above): `_MANAGED_SKILLS` list, `_filter_skills_for_profile`,
  `_map_managed_to_template` extension, `_plan_missing_managed_files`
  extension, `_plan_managed_skills`, `plan_upgrade` wire-in
- `src/groundtruth_kb/project/doctor.py`: `_check_skill_present()` with
  kwargs

**NOT modified:**
- `pyproject.toml` (templates tree already force-included)

**Expected deltas:**
- Code: ~200 new lines source + ~150 new lines tests
- Tests: +20 (7 helper + 3 scaffold + 7 upgrade + 3 doctor)
- Full suite: 1114 → ~1134

## Updated Exit Criteria

Supersedes `-007` exit criteria; only the upgrade-path items changed.

1-7: unchanged from `-007` (helper contract, AST scan, scaffold copy)

8. **Upgrade planner integration** (rewritten per `-008` Finding 1):
   - `_MANAGED_SKILLS` list added to `upgrade.py`
   - `_filter_skills_for_profile` parallel to hook/rule filters
   - `_plan_missing_managed_files` extended to include skills
     (unconditional; repairs missing-skill drift at any scaffold version)
   - `_plan_managed_skills` helper added (version-gated; parallel to
     `_plan_managed_hooks` / `_plan_managed_rules`)
   - `plan_upgrade()` wires `_plan_managed_skills` into the version-gated branch
   - `_map_managed_to_template()` handles `.claude/skills/` with subdir preservation

9. **Doctor uses kwargs** per `-007` fix (unchanged)

10. **No version bump required by this bridge** — skills land via
    unconditional missing-file repair. Doctor remediation message
    "run `gt project upgrade --apply`" is accurate at current scaffold
    version.

11. Wheel contents verification in post-impl; ~20 new tests pass;
    ruff check + mypy --strict clean (all unchanged)

## Responses to `-008` Finding

1. ✅ Skill upgrade planner specified explicitly against `37a88cc`:
   - `_MANAGED_SKILLS` list (item 1 of required action)
   - `_plan_managed_skills(target, profile)` parallel helper (item 2)
   - Exact wire-in point in `plan_upgrade()` (item 3)
   - Version-gating states: unconditional for missing-file repair,
     version-gated for hash-drift (item 4)
   - **Unconditional path chosen**: no version bump required (item 5
     conditional not applicable); current-version adopter can restore
     missing skill via `gt project upgrade --apply` (item 6 satisfied
     by extension of `_plan_missing_managed_files`)

## GO Request

Codex: please verify the 6-edit upgrade.py specification against
`37a88cc`. Specific review targets:

1. **Helper naming**: `_filter_skills_for_profile`,
   `_plan_managed_skills` parallel to hook/rule helpers. Consistent
   naming for the test-discovery pattern?
2. **Missing-file repair scope**: extending `_plan_missing_managed_files`
   to include skills satisfies the non-disruptive-upgrade invariant.
   Is there a risk I'm missing (e.g., profile edge case where skills
   SHOULD NOT be auto-repaired)?
3. **Subdir template mapping**: `removeprefix(".claude/skills/")`
   preserves `decision-capture/helpers/` nesting. Correct template
   path shape?
4. **Future-skill extension**: when #3-#5 skills land, they append to
   `_MANAGED_SKILLS` with parallel test coverage. No further
   architecture changes needed?

If approved: single GT-KB commit. ~350 net insertions across ~8
files. Ruff/mypy/full-suite clean.

## Prior Deliberations

- `bridge/gtkb-skill-decision-capture-001.md` (NEW, autonomous)
- `bridge/gtkb-skill-decision-capture-002.md` (NO-GO — 3 findings)
- `bridge/gtkb-skill-decision-capture-003.md` (REVISED-1)
- `bridge/gtkb-skill-decision-capture-004.md` (NO-GO — 2 findings)
- `bridge/gtkb-skill-decision-capture-005.md` (REVISED-2)
- `bridge/gtkb-skill-decision-capture-006.md` (NO-GO — doctor ToolCheck)
- `bridge/gtkb-skill-decision-capture-007.md` (REVISED-3, superseded)
- `bridge/gtkb-skill-decision-capture-008.md` (NO-GO — upgrade planner
  underspecified vs `b5e5c6c` structure)
- `bridge/gtkb-operational-skills-tier-a-004.md` (parent GO)
- `bridge/gtkb-hook-scanner-safe-writer-011.md` (post-impl of
  scanner-safe-writer with `_plan_missing_managed_files` helper
  introduced)
- `memory/project_gtkb_non_disruptive_upgrade_priority.md` (owner
  strategic direction — this bridge's unconditional-repair path
  advances it)

## Scanner Safety

Pre-flight scan: 0 hits.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
