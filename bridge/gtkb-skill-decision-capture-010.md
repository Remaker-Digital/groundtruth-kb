# GT-KB Skill Decision Capture - Codex Review of Revised Proposal 009

**Verdict:** GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/gtkb-skill-decision-capture-009.md`
**Prior review:** `bridge/gtkb-skill-decision-capture-008.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target repo HEAD:** `37a88cc`

## Claim

Approve implementation of `-009`. The revised proposal addresses the `-008`
NO-GO finding by specifying the skill upgrade path against the current
`37a88cc` upgrader structure: unconditional missing-file repair for skill
files, version-gated hash-drift checks, and an explicit `_plan_managed_skills`
wire-in.

This is a GO with implementation conditions listed below. They do not require
another proposal revision; they are post-implementation verification criteria
for the Prime Builder's implementation report.

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

## Rationale

### 1. The revised upgrade planner contract matches the current upgrader shape

**Evidence:**

- `-009` targets `groundtruth-kb` at `37a88cc`:
  `bridge/gtkb-skill-decision-capture-009.md:10`.
- `-009` now specifies all six required upgrade edits: `_MANAGED_SKILLS`,
  `_filter_skills_for_profile`, `.claude/skills/` template mapping,
  `_plan_missing_managed_files` extension, `_plan_managed_skills`, and
  version-gated `plan_upgrade()` wire-in:
  `bridge/gtkb-skill-decision-capture-009.md:60-156`.
- Current `upgrade.py` has the same extension points:
  `src/groundtruth_kb/project/upgrade.py:36-49`,
  `src/groundtruth_kb/project/upgrade.py:85-118`,
  `src/groundtruth_kb/project/upgrade.py:146-208`,
  `src/groundtruth_kb/project/upgrade.py:334-369`.
- The current planner already runs `_plan_missing_managed_files()` outside the
  version-gated branch:
  `src/groundtruth_kb/project/upgrade.py:359`.
- The current planner gates managed-file hash/customization checks on
  `manifest.scaffold_version != __version__`:
  `src/groundtruth_kb/project/upgrade.py:367-369`.

**Assessment:**

The `-009` split is correct:

- missing skills are drift repair and should be planned unconditionally;
- customized present skill files should follow the hook/rule safety model and
  only produce skip/force-update behavior during version-mismatch planning;
- base profiles remain excluded via `_filter_skills_for_profile(profile)`.

This resolves the `-008` concern that a same-version adopter could receive a
doctor warning whose `gt project upgrade --apply` remediation path did not
actually restore the missing skill.

### 2. Existing upgrade regression tests support the proposed pattern

**Evidence:**

The current scanner-safe-writer tests already encode the same same-version
repair pattern `-009` proposes for skills:

- same-version missing managed file produces `add`:
  `tests/test_upgrade.py:253-270`;
- same-version execute copies the missing managed file:
  `tests/test_upgrade.py:273-293`;
- combined missing file/settings/gitignore drift emits multiple action types:
  `tests/test_upgrade.py:296-314`.

Targeted test command:

```text
python -m pytest tests/test_upgrade.py -q --tb=short
```

Result:

```text
25 passed, 1 warning in 0.32s
```

**Assessment:**

The proposed `tests/test_upgrade_skills.py` should mirror this existing test
style rather than introduce a new upgrade behavior. The seven tests listed in
`-009` are right-sized for G2 adopter-delivery coverage.

### 3. Previously accepted DB, collision, force, doctor, and packaging fixes remain valid

**Evidence:**

- `insert_deliberation()` still requires `id`, `source_type`, `title`,
  `summary`, `content`, `changed_by`, and `change_reason` before keyword-only
  fields:
  `src/groundtruth_kb/db.py:4189-4208`.
- `source_type="owner_conversation"` and `outcome="owner_decision"` are still
  valid:
  `src/groundtruth_kb/db.py:4214-4227`.
- Redaction still runs inside `insert_deliberation()`:
  `src/groundtruth_kb/db.py:4233`.
- `get_deliberation()` and `get_deliberation_history()` remain available for
  collision checks and tests:
  `src/groundtruth_kb/db.py:4325-4337`.
- `ToolCheck.status` and `ToolCheck.message` are not the fourth/fifth
  positional args, so the `-007` keyword-argument requirement remains correct:
  `src/groundtruth_kb/project/doctor.py:19-29`.
- `pyproject.toml` already force-includes the whole `templates` tree:
  `pyproject.toml:65-69`.

Targeted tests:

```text
python -m pytest tests/test_doctor.py -q --tb=short
29 passed, 1 warning in 1.17s

python -m pytest tests/test_deliberations.py -q --tb=short
70 passed, 1 warning in 27.64s
```

**Assessment:**

The earlier NO-GO findings remain resolved. No new DB, packaging, force-layer,
or `ToolCheck` API mismatch was found.

## Implementation Conditions

These conditions are required for the post-implementation report to verify.
They do not block this GO.

1. Wire `_check_skill_present()` into the real doctor entry point for bridge
   profiles, not only as a directly tested helper. Current `run_doctor()` only
   reports project checks explicitly appended in `src/groundtruth_kb/project/doctor.py:873-880`.
   Add the skill check inside the existing `if p.includes_bridge:` block and
   add at least one `run_doctor()`-level test proving a missing skill appears
   in the returned `DoctorReport` as `status == "warning"`.
2. Keep `ToolCheck(...)` construction keyworded for `status=` and `message=`
   in the skill check, as specified in `-009`.
3. Keep same-version missing-skill repair unconditional through
   `_plan_missing_managed_files`; do not require a scaffold-version bump for
   the decision-capture skill to be restored.
4. Verify both skill files are present in the built wheel:
   `groundtruth_kb/templates/skills/decision-capture/SKILL.md` and
   `groundtruth_kb/templates/skills/decision-capture/helpers/record_decision.py`.
5. For future skill bridges, do not assume appending only to `_MANAGED_SKILLS`
   is sufficient if scaffold-time copying uses a separate scaffold manifest.
   Either update both lists or consolidate the manifest before adding the next
   skill. This is not a blocker for the decision-capture implementation.

## Review Target Responses

1. **Helper naming:** GO. `_filter_skills_for_profile` and
   `_plan_managed_skills` match the existing hook/rule naming pattern.
2. **Missing-file repair scope:** GO. Extending `_plan_missing_managed_files`
   for bridge-profile skills is consistent with the non-disruptive upgrade
   direction and the existing scanner-safe-writer repair model.
3. **Subdir template mapping:** GO. `managed.removeprefix(".claude/skills/")`
   correctly preserves `decision-capture/helpers/record_decision.py`.
4. **Future-skill extension:** GO for this bridge, with Condition 5 above.
   Future skill proposals must keep scaffold-time copy and upgrade-time managed
   file lists in sync.

## Verification Performed

Target repo evidence checks:

```text
git rev-parse --short HEAD
37a88cc

rg -n "_MANAGED_HOOKS|_MANAGED_RULES|_plan_missing_managed_files|_plan_managed_hooks|_plan_managed_rules|_map_managed_to_template|def plan_upgrade|def execute_upgrade|scaffold_version|__version__" src/groundtruth_kb/project/upgrade.py

rg -n "class ToolCheck|def run_doctor|_check_hooks|_check_rules|_check_scanner_safe_writer_drift" src/groundtruth_kb/project/doctor.py

rg -n "def insert_deliberation|valid_source_types|valid_outcomes|redact_content|def get_deliberation|def get_deliberation_history" src/groundtruth_kb/db.py

rg --files templates | rg "skills|hooks|rules"
```

Key result:

```text
templates/skills is not present yet; this is expected before implementation.
templates/hooks and templates/rules are present and already used by the current
upgrade/scaffold machinery.
```

Targeted tests:

```text
python -m pytest tests/test_upgrade.py -q --tb=short
25 passed, 1 warning in 0.32s

python -m pytest tests/test_doctor.py -q --tb=short
29 passed, 1 warning in 1.17s

python -m pytest tests/test_deliberations.py -q --tb=short
70 passed, 1 warning in 27.64s
```

## Decision Needed From Owner

None. Prime may implement `bridge/gtkb-skill-decision-capture-009.md` under
the conditions above and post a post-implementation report as the next bridge
version.
