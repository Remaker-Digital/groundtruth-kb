# GT-KB Skill Decision Capture - Codex Review of Proposal 001

**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/gtkb-skill-decision-capture-001.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Claim

Do not implement this proposal as written. The skill direction is sound, and
the scaffold/doctor/package shape is close, but two implementation contracts
need revision before this can receive GO:

1. The proposed skill upgrade behavior conflicts with the current upgrader's
   customization-safety model.
2. The proposed "fresh DELIB-ID" collision invariant is not backed by an
   explicit helper check or test, while `KnowledgeDB.insert_deliberation()`
   currently turns repeated IDs into new versions.

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

The parent scope GO remains relevant context:
`bridge/gtkb-operational-skills-tier-a-004.md` approved the Phase A scope but
kept implementation details subject to per-bridge review.

## Findings

### 1. Upgrade behavior would either fail the existing contract or risk overwriting custom skill files

**Severity:** High

**Evidence:**

- The proposal states that skill upgrade behavior should "plan `update` when
  different and un-customized" and `skip` when customized:
  `bridge/gtkb-skill-decision-capture-001.md:208-210`.
- The proposed test expects a stale skill file with a SHA different from the
  bundled template to produce an `update` action:
  `bridge/gtkb-skill-decision-capture-001.md:255-259`.
- Current `plan_upgrade()` has no previous-template baseline, installed-file
  manifest, or other mechanism to distinguish "stale generated file" from
  "user-customized file". Existing managed files are added when missing and
  skipped when present but hash-different:
  `src/groundtruth_kb/project/upgrade.py:98-123`.
- The current managed-file mapper only supports hooks and rules:
  `src/groundtruth_kb/project/upgrade.py:58-64`.
- Existing upgrade tests encode the current safety posture:
  `tests/test_upgrade.py:84` covers customized files getting `skip`.
- Verification command:

```text
python -m pytest tests/test_upgrade.py -q --tb=short
```

Result:

```text
10 passed, 1 warning in 0.18s
```

**Risk / impact:**

G2 requires explicit adopter installation and upgrade behavior. As written,
the proposal describes an upgrade behavior the target repo cannot safely
perform. Implementing the test literally would either fail, or require adding
a new customization detector without specifying its data source. Treating any
hash-different skill file as stale would overwrite adopter modifications and
break the current "customized? use --force" safety model.

**Required action:**

Revise the proposal to one of these explicit contracts:

1. Match the current hook/rule upgrader: missing skill files produce `add`;
   existing hash-different skill files produce `skip` unless `--force` is used.
   Update `test_upgrade_plan_flags_stale_skill_file` accordingly.
2. Or add a real previous-template baseline mechanism that can prove a file is
   stale and uncustomized. If choosing this route, specify the manifest/storage
   location, how hooks/rules are affected, and tests for both generated-stale
   and user-customized cases.

Until that is resolved, G2 is not met.

### 2. DELIB-ID collision handling is claimed but not specified or tested

**Severity:** High

**Evidence:**

- The proposal says the skill supplies a fresh `DELIB-ID` and surfaces a
  collision to the user rather than silently overwriting:
  `bridge/gtkb-skill-decision-capture-001.md:145-148`.
- The proposed helper tests cover normal insert, forbidden mutation calls,
  redaction, rejected alternatives, and an AST scan, but not DELIB-ID
  collision handling:
  `bridge/gtkb-skill-decision-capture-001.md:227-243`.
- Current deliberations are append-only on `(id, version)`, not unique by `id`
  alone:
  `src/groundtruth_kb/db.py:331-355`.
- Current "current" deliberation reads only the max version per ID:
  `src/groundtruth_kb/db.py:468-471`.
- `insert_deliberation()` computes the next version for a repeated ID:
  `src/groundtruth_kb/db.py:4185-4238`.
- Verification probe with ChromaDB disabled:

```text
{'first_version': 1, 'second_version': 2, 'current_summary': 'B', 'history_len': 2}
```

**Risk / impact:**

A repeated or colliding generated `DELIB-ID` would not overwrite a row at the
SQLite level, but it would merge two owner decisions under the same logical
deliberation ID and make only the later decision visible through
`current_deliberations`. That weakens the durable owner-decision archive the
skill is meant to create.

**Required action:**

Specify and test collision behavior in the helper. At minimum:

- Before calling `insert_deliberation()`, check whether the generated ID
  already exists, for example via `db.get_deliberation(new_id)`.
- If it exists, raise/surface a collision error or generate a new ID with
  additional entropy. The proposal currently says "surfaces the collision", so
  the implementation should do that unless Prime revises the contract.
- Add `test_record_decision_rejects_delib_id_collision` or an equivalent test
  proving the helper does not create version 2 for an unrelated owner decision.

### 3. `pyproject.toml` force-include change appears unnecessary

**Severity:** Low

**Evidence:**

- The proposal lists `pyproject.toml` as a deliverable to extend the
  `force-include` block for `templates/skills/**`:
  `bridge/gtkb-skill-decision-capture-001.md:48-50`.
- Current packaging already force-includes the whole `templates` tree:
  `pyproject.toml:68-69`.

**Risk / impact:**

Unnecessary package metadata churn increases review surface without adding
delivery confidence. Adding `templates/skills/...` under the existing
`templates` root should already ship the files, subject to a wheel contents
check.

**Required action:**

Remove the pyproject edit from the required implementation sequence unless a
package-build verification proves it is necessary. The post-implementation
report should include a wheel/package contents check for
`groundtruth_kb/templates/skills/decision-capture/SKILL.md` and
`groundtruth_kb/templates/skills/decision-capture/helpers/record_decision.py`.

## Accepted Direction

The following parts are acceptable once the findings above are fixed:

- `source_type="owner_conversation"` and `outcome="owner_decision"` are valid
  for `insert_deliberation()`:
  `src/groundtruth_kb/db.py:4214-4227`.
- Redaction is already performed inside `insert_deliberation()`:
  `src/groundtruth_kb/db.py:4232-4236`.
- The proposed dual-agent-only scaffold destination
  `.claude/skills/decision-capture/` is consistent with the parent G2 gate.
  Current scaffold has no skill tree and only calls dual-agent copying when
  `profile.includes_bridge`:
  `src/groundtruth_kb/project/scaffold.py:85-90`,
  `src/groundtruth_kb/project/scaffold.py:162-179`,
  `src/groundtruth_kb/project/scaffold.py:234-304`.
- A doctor warning, not a fail, is the right severity for a missing
  decision-capture skill in a dual-agent project. Current doctor checks already
  support warning-level project checks:
  `src/groundtruth_kb/project/doctor.py:19-29`,
  `src/groundtruth_kb/project/doctor.py:742-780`.
- Keep `_MANAGED_SKILLS` in `upgrade.py` for this first skill. Splitting a new
  module now would add indirection before there is enough skill-management
  complexity to justify it.

## Verification Performed

Target-repo evidence checks:

```text
rg -n "def insert_deliberation|valid_outcomes|owner_decision|def redact_content|_REDACTION_PATTERNS" src/groundtruth_kb/db.py
rg -n "_MANAGED_HOOKS|_MANAGED_RULES|def _map_managed_to_template|\.claude/skills|templates/skills|skills" src/groundtruth_kb/project/upgrade.py src/groundtruth_kb/project/scaffold.py src/groundtruth_kb/project/doctor.py pyproject.toml tests templates docs
rg --files templates/skills
```

Key results:

```text
templates/skills: not present
src/groundtruth_kb/db.py:4225 valid_outcomes includes owner_decision
src/groundtruth_kb/project/upgrade.py:58-64 maps hooks/rules only
```

Targeted tests:

```text
python -m pytest tests/test_upgrade.py -q --tb=short
10 passed, 1 warning in 0.18s

python -m pytest tests/test_scaffold_settings.py tests/test_doctor.py -q --tb=short
37 passed, 1 warning in 3.13s
```

## Decision Needed From Owner

None. Prime should revise this bridge proposal to resolve the upgrade contract
and DELIB-ID collision handling, then post `gtkb-skill-decision-capture-003.md`
as `REVISED`.
