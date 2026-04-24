GO

# GT-KB Core Specification Intake - Phase 0 Loyal Opposition Review

**Status:** GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-22
**Reviewed proposal:** `bridge/gtkb-core-spec-intake-001.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Verdict

GO for the Phase 0 workstream shape and compatibility constraints only.

This approval does not authorize direct mutation of governed SPEC, ADR, DCL, or
Deliberation Archive records, and it does not approve GT-KB package code
implementation yet. The next implementation proposal should preserve the
conditions below.

## Rationale

The proposal is justified by the current GT-KB behavior gap and has a reasonable
compatibility boundary: make core application specification intake default for
new projects while preserving explicit opt-out behavior, non-interactive safety,
and the existing minimal/full scaffold semantics unless a later governed
decision changes them.

The persisted-evidence state model is feasible because GT-KB already has the
necessary primitives: stable specification handles/tags, `authority` values,
append-only current-state views, deliberation records, and an already verified
confirm-before-mutate intake path.

## Evidence

- `memory/work_list.md:134-155` records `GTKB-CORE-001` as a TOP priority,
  including default active behavior for newly initialized projects, one missing
  question at a time, persisted provenance, cross-session continuation, and a
  stop condition when slots are owner-stated or explicitly not applicable.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/CORE-SPEC-BASELINE-EVALUATION-2026-04-22.md`
  and
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/CORE-SPEC-INTAKE-IMPLEMENTATION-PLAN-2026-04-22.md`
  both state that current GT-KB does not mechanically provide the requested
  default core-spec intake behavior.
- `src/groundtruth_kb/cli.py:753-843` shows `gt project init` accepts scaffold
  setup options but no core application specification intake option or prompt.
- `src/groundtruth_kb/project/scaffold.py:36-60` defines
  `ScaffoldOptions.spec_scaffold` with default `None`; lines `248-260` apply
  generated specs only when `options.spec_scaffold is not None`.
- `src/groundtruth_kb/spec_scaffold.py:36-68` defines the current minimal/full
  scaffold phases as governance, infrastructure, AI components, and compliance;
  lines `106-222` contain those existing template categories, not a core
  application spec state machine.
- `src/groundtruth_kb/db.py:56-73`, `src/groundtruth_kb/db.py:413-416`, and
  `src/groundtruth_kb/db.py:711-845` show append-only specs with `handle`,
  `tags`, current-state view support, and insert-time `authority`; lines
  `1040-1085` show query support by handle, tag, type, authority, and other
  fields.
- `src/groundtruth_kb/intake.py:176-233` captures owner-conversation intake as a
  deferred deliberation, and `src/groundtruth_kb/intake.py:236-316` confirms it
  into a stated spec while recording an owner-decision deliberation.
- `bridge/gtkb-skill-spec-intake-006.md` verifies the `/gtkb-spec-intake` skill
  and confirms the changed-by provenance and confirm-before-mutate path are
  available as enabling primitives.

Command evidence from the target checkout:

```text
python -m pytest tests/test_spec_scaffold.py tests/test_scaffold_project.py -q --tb=short
16 passed, 1 warning in 3.73s

python -m pytest tests/test_intake.py tests/test_spec_intake_helper.py -q --tb=short
48 passed, 1 warning in 16.37s
```

## Conditions For Later Implementation

1. Preserve this GO's scope: Phase 0 authorizes the governed workstream shape,
   not package code changes or formal artifact mutations.
2. Before implementation changes, create or update the proposed SPEC/ADR/DCL
   artifacts only through the normal approval path, or record an explicit owner
   deferral if implementation proceeds before those artifacts exist.
3. Treat non-interactive and machine-readable command paths as no-prompt paths.
   Any default-on behavior must print deterministic status/question output or
   expose an explicit opt-out/config flag without blocking automation.
4. Match core slots by stable package-level handles or tags, not fuzzy title
   matching. Generated or inferred candidates must not suppress prompts until
   owner-stated or explicitly not-applicable evidence exists.
5. Represent `not_applicable` as explicit persisted decision evidence linked to
   the slot, not as absence of a spec and not as a fake fulfilled requirement.
6. Add regression tests for fresh missing state, partial completion, inferred
   candidates, owner-stated completion, not-applicable completion, all-complete
   prompt suppression, existing minimal/full scaffold compatibility, and
   non-interactive no-prompt behavior.

## Non-Blocking Notes

- The proposed slot catalog is broad but still appropriate for a default
  baseline because it covers product identity, delivery surface, tenancy, users,
  data, compliance, security, reliability, integrations, AI, operations, and
  non-goals without turning initialization into a long wizard.
- The implementation plan should keep `gt core-specs status` and
  `gt core-specs next-question` read-only until the owner uses an approved
  answer/confirmation path.

## Required Actions

No revisions are required for Phase 0.

Prime Builder should file the next bridge proposal before making GT-KB package
code changes, with the implementation conditions above carried forward.

