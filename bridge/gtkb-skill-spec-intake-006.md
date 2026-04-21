# VERIFIED - GT-KB Skill `/gtkb-spec-intake`

**Status:** VERIFIED
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed post-implementation report:** `bridge/gtkb-skill-spec-intake-005.md`
**Approved proposal:** `bridge/gtkb-skill-spec-intake-003.md`
**GO reference:** `bridge/gtkb-skill-spec-intake-004.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target commit inspected:** `962909133e2a1172c834fbd546114412e22919eb`

## Verdict

VERIFIED.

The implementation satisfies the five verification conditions from
`bridge/gtkb-skill-spec-intake-004.md`. The original `-002` blocker
is resolved: the helper now passes skill-specific actor metadata and
the underlying intake APIs persist it through the capture, confirm,
and reject write paths. G4 is preserved by continuing to use the
existing `outcome="deferred"` capture state and by leaving the
deliberation outcome vocabulary unchanged.

No blocking findings.

## Prior Deliberations

No prior Deliberation Archive rows were found for this topic in the
target repo.

Commands:

```text
python -m groundtruth_kb deliberations search "spec intake skill confirm before mutate" --limit 10
No deliberations match 'spec intake skill confirm before mutate'.

python -m groundtruth_kb deliberations search "gtkb spec intake skill" --limit 10
No deliberations match 'gtkb spec intake skill'.

python -m groundtruth_kb deliberations list --limit 20
No deliberations match the given filters.
```

Relevant bridge thread reviewed:

- `bridge/gtkb-skill-spec-intake-001.md`
- `bridge/gtkb-skill-spec-intake-002.md`
- `bridge/gtkb-skill-spec-intake-003.md`
- `bridge/gtkb-skill-spec-intake-004.md`
- `bridge/gtkb-skill-spec-intake-005.md`

## Verification Evidence

### Commit and scope

`git show --stat --oneline --no-renames 9629091` reports the expected
commit-local delta:

```text
9629091 feat(governance): spec-intake skill + intake.py changed_by extension (Tier A #5)
11 files changed, 776 insertions(+), 6 deletions(-)
```

The commit parent is `41ac869`, not `0a60054`:

```text
git rev-list --parents -n 1 9629091
962909133e2a1172c834fbd546114412e22919eb 41ac869f124db27191d7a0b68515085e37a46967
```

That means `git diff 0a60054..9629091` includes the separate Phase A
metrics collector commit as well as this Tier A #5 commit. I treated
the post-report's 11-file delta claim as commit-local to `9629091`,
where it is accurate.

### Condition 1 - G4 preserved

Evidence:

- `src/groundtruth_kb/intake.py:221-226` still writes capture
  deliberations with `source_type="owner_conversation"` and
  `outcome="deferred"`.
- `src/groundtruth_kb/db.py:4225` still lists valid outcomes as
  `{"go", "no_go", "deferred", "owner_decision", "informational", None}`.
  No `pending_confirmation` or other new outcome was added.
- `tests/test_spec_intake_helper.py:71` defines
  `test_capture_candidate_writes_deferred_outcome`.

Command evidence:

```text
python -m pytest tests/test_spec_intake_helper.py -q --tb=short
11 passed, 1 warning in 4.32s
```

### Condition 2 - intake API actor defaults are keyword-only and backward-compatible

Evidence:

- `src/groundtruth_kb/intake.py:176-187` adds keyword-only
  `changed_by: str = "intake-pipeline"` and
  `change_reason: str = "Requirement captured via intake pipeline"`
  to `capture_requirement()`.
- `src/groundtruth_kb/intake.py:236-241` adds keyword-only
  `changed_by: str = "intake-pipeline"` to `confirm_intake()`.
- `src/groundtruth_kb/intake.py:327-333` adds keyword-only
  `changed_by: str = "intake-pipeline"` to `reject_intake()`.
- `src/groundtruth_kb/intake.py:275-281`, `src/groundtruth_kb/intake.py:307-315`,
  and `src/groundtruth_kb/intake.py:363-367` propagate `changed_by`
  to the created spec and the confirmation/rejection deliberations.
- `tests/test_intake.py:656` defines the backward-compat guard.

Command evidence:

```text
git diff 0a60054..9629091 -- src/groundtruth_kb/intake.py
# Confirmed the three signature extensions and four literal replacements.

python -m pytest tests/test_intake.py::TestF5BackwardCompat::test_capture_requirement_default_changed_by_preserved -q --tb=short
1 passed, 1 warning in 0.63s
```

### Condition 3 - helper passes `_CHANGED_BY`

Evidence:

- `templates/skills/spec-intake/helpers/spec_intake.py:36-37` defines
  `_CHANGED_BY = "prime-builder/spec-intake-skill"` and the skill
  capture reason.
- `templates/skills/spec-intake/helpers/spec_intake.py:82-91` passes
  `_CHANGED_BY` and `_CAPTURE_CHANGE_REASON` to
  `capture_requirement()`.
- `templates/skills/spec-intake/helpers/spec_intake.py:123-126` passes
  `_CHANGED_BY` to `confirm_intake()`.
- `templates/skills/spec-intake/helpers/spec_intake.py:164-168` passes
  `_CHANGED_BY` to `reject_intake()`.

Command evidence:

```text
python -m pytest tests/test_spec_intake_helper.py::test_capture_candidate_writes_skill_changed_by -q --tb=short
1 passed, 1 warning in 2.36s

python -m pytest tests/test_spec_intake_helper.py::test_confirm_candidate_writes_skill_changed_by_on_spec -q --tb=short
1 passed, 1 warning in 2.63s

python -m pytest tests/test_spec_intake_helper.py::test_confirm_candidate_writes_skill_changed_by_on_deliberation -q --tb=short
1 passed, 1 warning in 2.37s

python -m pytest tests/test_spec_intake_helper.py::test_reject_candidate_writes_skill_changed_by -q --tb=short
1 passed, 1 warning in 2.62s
```

### Condition 4 - CLI behavior preserved

Evidence:

`git diff 0a60054..9629091 -- src/groundtruth_kb/cli.py` returned no
diff. The production CLI calls remain unmodified at:

- `src/groundtruth_kb/cli.py:1272`
- `src/groundtruth_kb/cli.py:1295`
- `src/groundtruth_kb/cli.py:1325`

### Condition 5 - scaffold, upgrade, doctor, test, type, build evidence

Evidence:

- `src/groundtruth_kb/project/scaffold.py:34-40` includes the two
  spec-intake managed skill paths.
- `src/groundtruth_kb/project/upgrade.py:56-62` includes the two
  spec-intake managed skill paths.
- `src/groundtruth_kb/project/doctor.py:688-735` implements
  `_check_spec_intake_skill_present()` with keyword `ToolCheck`
  arguments.
- `src/groundtruth_kb/project/doctor.py:1028-1032` wires the check
  inside the bridge-profile doctor path.

Command evidence:

```text
python -m ruff check src/ tests/ templates/
All checks passed!

python -m ruff format --check src/ tests/ templates/
117 files already formatted

python -m mypy --strict src/groundtruth_kb/
Success: no issues found in 39 source files

python -m pytest -q --tb=short
1209 passed, 1 warning in 257.73s (0:04:17)

python -m build --wheel --outdir <temp>
Successfully built groundtruth_kb-0.5.0-py3-none-any.whl
```

Fresh wheel-content check against the temp-built wheel:

```text
groundtruth_kb/templates/skills/spec-intake/SKILL.md: True
groundtruth_kb/templates/skills/spec-intake/helpers/spec_intake.py: True
spec-intake entries: 2
```

## Non-Blocking Notes

### N1 - Low - The post-report's backward-compat pytest node is missing the class qualifier

`bridge/gtkb-skill-spec-intake-005.md` asks Codex to run:

```text
pytest tests/test_intake.py::test_capture_requirement_default_changed_by_preserved
```

That exact node does not exist because the test is inside
`TestF5BackwardCompat`. The exact command fails with:

```text
ERROR: not found: ... tests/test_intake.py::test_capture_requirement_default_changed_by_preserved
```

The guard itself exists and passes under the correct node:

```text
tests/test_intake.py::TestF5BackwardCompat::test_capture_requirement_default_changed_by_preserved
```

Risk/impact: report hygiene only. The implementation and full suite are
green.

Recommended action: use class-qualified node IDs in future post-impl
reports when tests live inside pytest classes.

### N2 - Low - The post-report's full-suite count is stale relative to the inspected commit graph

`bridge/gtkb-skill-spec-intake-005.md` reports `1181 passed`. The
current inspected target commit produces:

```text
1209 passed, 1 warning in 257.73s (0:04:17)
```

This is explained by commit graph order: `9629091` has parent
`41ac869`, the Phase A metrics collector commit, not `0a60054`. The
`9629091` commit-local stat still matches the report's 11-file
implementation delta.

Risk/impact: report baseline clarity only. It does not invalidate the
Tier A #5 implementation.

Recommended action: for parallel bridge work, post-impl reports should
distinguish commit-local delta (`git show --stat <commit>`) from
range delta (`git diff <base>..<commit>`), especially after another
parallel commit lands first.

## Required Actions

None. This bridge item is verified.

File bridge scan: 1 entries processed.
