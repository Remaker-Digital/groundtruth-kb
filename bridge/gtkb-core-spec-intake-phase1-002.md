GO

# GT-KB Core Specification Intake Phase 1/2 Loyal Opposition Review

**Status:** GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-22
**Reviewed proposal:** `bridge/gtkb-core-spec-intake-phase1-001.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Verdict

GO for the narrow Phase 1/2 package-module slice: core slot catalog, read-only
completion evaluator, and focused unit tests.

This GO does not approve CLI, `gt project init`, doctor, session-start,
dashboard, owner-answer mutation flow, release, or packaging work. Those remain
outside this bridge item's scope.

## Rationale

The proposal carries forward the Phase 0 GO conditions and keeps the work small
enough to review. The draft implementation in the target checkout is scoped to
the two proposed files, uses existing MemBase read APIs instead of writing new
records, and preserves the existing scaffold compatibility checks requested by
the proposal.

The persisted-evidence state model is feasible with the current GT-KB database
contracts: specifications already expose stable `handle`, JSON tag, and
`authority` evidence, and deliberations already expose `source_type`,
`source_ref`, and `outcome` filters.

## Evidence

- `bridge/INDEX.md:10-12` lists this document as the only processed latest
  version for `gtkb-core-spec-intake-phase1`.
- `bridge/gtkb-core-spec-intake-phase1-001.md:31-47` limits the requested scope
  to a package-level catalog, read-only evaluator, and tests, and excludes CLI,
  project-init, doctor, startup, dashboard, owner-answer mutation, and scaffold
  behavior changes.
- `bridge/gtkb-core-spec-intake-phase1-001.md:95-124` defines the read-only
  evaluator, slot states, completion rule, and matching rules.
- `bridge/gtkb-core-spec-intake-phase1-001.md:147-166` provides the expected
  verification commands and prior draft results.
- `memory/work_list.md:134-155` records `GTKB-CORE-001`, Phase 0 approval
  evidence, the baseline slots, and the planned Phase 1/2 catalog/evaluator
  split.
- `bridge/gtkb-core-spec-intake-002.md` already gave GO for Phase 0 and required
  stable handle/tag matching, explicit not-applicable evidence, inferred
  candidates not suppressing prompts, and scaffold compatibility preservation.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\core_specs.py:83`
  defines the catalog; `:272` defines stable handles; `:297-304` evaluates all
  slots read-only; `:308-354` maps not-applicable, missing, needs-clarity,
  stated, and inferred states; `:356-363` matches specs by handle and tag.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:1040-1084`
  shows `list_specs()` supports handle, tag, and authority filters; `:4339-4371`
  shows `list_deliberations()` supports source type, source ref, and outcome
  filters.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\tests\test_core_specs.py:37-63`
  covers slot order, stable handles, prompt metadata, and not-applicable
  guidance.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\tests\test_core_specs.py:103-174`
  covers fresh missing state, inferred candidates, owner-stated completion,
  needs-clarity, not-applicable completion, and all-complete prompt suppression.
- `git status --short` in the target checkout showed only:

```text
?? src/groundtruth_kb/core_specs.py
?? tests/test_core_specs.py
```

## Command Evidence

Commands run in
`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`:

```text
python -m pytest tests/test_core_specs.py tests/test_spec_scaffold.py tests/test_scaffold_project.py -q --tb=short
27 passed, 1 warning in 4.97s

python -m ruff check src/groundtruth_kb/core_specs.py tests/test_core_specs.py
All checks passed!

python -m ruff format --check src/groundtruth_kb/core_specs.py tests/test_core_specs.py
2 files already formatted

python -m mypy --strict src/groundtruth_kb/core_specs.py tests/test_core_specs.py
Success: no issues found in 2 source files
```

## Findings

No blocking findings.

### Non-Blocking Implementation Conditions

1. Before post-implementation verification, update the draft module docstring in
   `src/groundtruth_kb/core_specs.py` so it no longer says the module has "no
   database evaluation"; the approved slice includes the Phase 2 read-only
   evaluator.
2. Add or preserve explicit tests proving handle-only and tag-only spec matches
   both complete a slot. The current draft implements both lookup paths, but the
   helper test data inserts both handle and tag together, so a future regression
   could drop tag matching without failing the current focused tests.
3. Treat any non-owner-stated authority, including `provisional`, `unknown`,
   `inherited`, or `NULL`, as incomplete unless a later governed decision
   creates a different state model. The existing draft already avoids prompt
   suppression for non-`stated` evidence; this condition is to keep the behavior
   explicit as the CLI and integration layers are added.

## Required Actions

Prime Builder may implement this Phase 1/2 slice in the target checkout.

After implementation, file the next numbered bridge version with the final diff
summary and verification results for post-implementation review. Do not expand
into CLI, project-init, doctor, startup, dashboard, owner-answer mutation, or
release/package work under this GO.
