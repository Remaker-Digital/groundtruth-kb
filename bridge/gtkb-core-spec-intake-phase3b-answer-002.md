GO

# GT-KB Core Specification Intake Phase 3B Answer Command Review

**Status:** GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-22
**Reviewed proposal:** `bridge/gtkb-core-spec-intake-phase3b-answer-001.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Verdict

GO to implement the narrow Phase 3B mutating `gt core-specs answer` command,
subject to the required conditions below.

This GO does not approve project-init prompting, doctor integration,
session-start integration, dashboard integration, Agent Red application
changes, package release, commit, push, merge, staging, production deployment,
or any automatic mutation from `status` or `next-question`.

## Rationale

The proposal is appropriately scoped as a GT-KB infrastructure command and
keeps the Phase 3A read-only commands non-mutating. The requested owner-stated
answer path and explicit not-applicable path align with the existing evaluator:
current specs with stable handle/tag and `authority="stated"` complete normal
slots, while canonical owner-decision deliberations complete not-applicable
slots.

The implementation can proceed because the stated dependency is satisfied:
`bridge/INDEX.md` lists `gtkb-core-spec-intake-phase3a-cli` with latest status
`VERIFIED: bridge/gtkb-core-spec-intake-phase3a-cli-004.md`.

## Evidence

- `bridge/gtkb-core-spec-intake-phase3b-answer-001.md` limits the request to
  `gt core-specs answer` and excludes project init, doctor, session-start,
  dashboard, release, packaging, Agent Red source changes, and automatic
  mutation from read-only commands.
- `bridge/gtkb-core-spec-intake-phase3a-cli-004.md` VERIFIED the Phase 3A
  read-only CLI slice and preserved the requirement that mutating answer
  behavior needs a separate proposal.
- `bridge/gtkb-core-spec-intake-phase1-004.md` VERIFIED the slot catalog and
  read-only evaluator dependency.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\cli.py`
  currently registers only `core-specs status` and `core-specs next-question`;
  no `answer` command exists yet.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\core_specs.py`
  defines stable slot handles, `get_core_spec_slot(handle)`,
  `core_spec_not_applicable_source_ref(handle)`, and
  `evaluate_core_spec_slots(db)`.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\core_specs.py`
  evaluates owner-stated specs as complete only when title and description are
  present, and evaluates explicit not-applicable deliberations through
  `source_type="owner_conversation"`,
  `source_ref=core-spec:{handle}:not-applicable`, and
  `outcome="owner_decision"`.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py`
  exposes `insert_spec`, `update_spec`, `insert_deliberation`,
  `list_specs`, and `list_deliberations` primitives that can support this
  slice without adding a new storage layer.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\intake.py`
  has confirm-before-mutate requirement-intake primitives, but the proposal is
  correct that the current confirm path does not preserve core slot handle,
  slot tag, description, or not-applicable semantics.

## Command Evidence

Commands run in
`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`:

```text
python -m pytest tests/test_cli_core_specs.py tests/test_core_specs.py tests/test_intake.py -q --tb=short
60 passed, 1 warning in 13.08s
```

```text
python -m ruff check src/groundtruth_kb/cli.py src/groundtruth_kb/core_specs.py src/groundtruth_kb/intake.py tests/test_cli_core_specs.py tests/test_core_specs.py tests/test_intake.py
All checks passed!
```

```text
python -m ruff format --check src/groundtruth_kb/cli.py src/groundtruth_kb/core_specs.py src/groundtruth_kb/intake.py tests/test_cli_core_specs.py tests/test_core_specs.py tests/test_intake.py
6 files already formatted
```

```text
python -m mypy --strict src/groundtruth_kb/core_specs.py tests/test_cli_core_specs.py
Success: no issues found in 2 source files
```

The pytest warning is the known ChromaDB/Python deprecation warning for
`asyncio.iscoroutinefunction`; it is not specific to this proposal.

## Findings

No blocking findings.

### Condition 1 - Not-applicable eligibility must be machine-readable

The slot catalog currently stores not-applicable policy as prose in
`not_applicable_guidance`. The implementation must not infer "always
applicable" or "eligible for not-applicable" by parsing that prose. Add an
explicit catalog field such as `not_applicable_allowed: bool`, or implement the
proposal's `--force-not-applicable` escape with a required audit reason and
focused tests.

### Condition 2 - Answer mutations must use stable, auditable evidence

Owner-stated answers must persist as current spec evidence with a stable slot
handle, slot tag, `authority="stated"`, non-empty title and description, and
`changed_by` / `change_reason` values that identify core-spec intake. The
implementation should use a deterministic spec ID per slot or otherwise prove
that repeated answers update the same current slot evidence instead of
creating duplicate current specs for the same handle.

### Condition 3 - Not-applicable capture must remain deliberation evidence

`--not-applicable` must create or update canonical deliberation evidence using
`core_spec_not_applicable_source_ref(handle)`, `source_type="owner_conversation"`,
and `outcome="owner_decision"`. It must not create a fake requirement spec to
make the evaluator pass.

### Condition 4 - Dry-run and read-only commands must remain non-mutating

`--dry-run` must leave both specifications and deliberations unchanged.
Existing `status` and `next-question` commands must remain read-only, including
when `--json` is used.

## Required Actions

1. Implement only the scoped Phase 3B command and tests described in
   `bridge/gtkb-core-spec-intake-phase3b-answer-001.md`.
2. Carry the four conditions above into implementation and verification
   evidence.
3. Run the proposal's focused verification commands before requesting
   post-implementation verification.

## Decision Needed From Owner

None for this bridge item.
