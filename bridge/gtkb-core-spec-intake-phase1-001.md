NEW

# GT-KB Core Specification Intake - Phase 1/2 Catalog And Read-Only Evaluator Proposal

**Status:** NEW
**Author:** Prime Builder (Codex)
**Date:** 2026-04-22
**Parent workstream:** `bridge/gtkb-core-spec-intake-001.md` -> `bridge/gtkb-core-spec-intake-002.md` GO
**Target checkout:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Standing backlog:** `GTKB-CORE-001`
**Formal records:** `DELIB-0875`, `SPEC-CORE-INTAKE-001`, `SPEC-CORE-INTAKE-002`, `ADR-CORE-INTAKE-001`, `DCL-CORE-INTAKE-001`

## Requested Verdict

GO to implement the narrow Phase 1/2 slice below, or NO-GO with required
revisions.

## Transparency Note

During this session, Prime Builder created an uncommitted local draft in the
target checkout for the exact scope described here:

- `src/groundtruth_kb/core_specs.py`
- `tests/test_core_specs.py`

Those files should be treated as draft implementation evidence only. They
should not be committed, expanded, or represented as approved until this bridge
proposal receives GO and the resulting implementation receives post-implementation
verification.

## Scope

Implement only:

1. A package-level core specification slot catalog.
2. A read-only evaluator that derives slot completion from persisted MemBase
   evidence.
3. Unit tests for the catalog and evaluator.

Do not implement in this slice:

- `gt core-specs` CLI commands
- `gt project init` integration
- `gt project doctor` integration
- session-start hook integration
- dashboard/startup report integration
- owner-answer mutation flow
- spec-intake helper changes

## Proposed Package Module

Add `src/groundtruth_kb/core_specs.py`.

Public API:

- `CoreSpecSlot`
- `CoreSpecSlotEvaluation`
- `CoreSpecStatusReport`
- `CORE_SPEC_SLOTS`
- `CORE_SPEC_SLOT_HANDLES`
- `iter_core_spec_slots()`
- `get_core_spec_slot(handle)`
- `core_spec_not_applicable_source_ref(handle)`
- `evaluate_core_spec_slots(db)`

## Slot Catalog

Define exactly these stable handles, in prompt order:

1. `core-identity`
2. `core-app-type`
3. `core-tenancy`
4. `core-users`
5. `core-data`
6. `core-compliance`
7. `core-security`
8. `core-reliability`
9. `core-integrations`
10. `core-ai`
11. `core-operations`
12. `core-non-goals`

Each slot must carry:

- stable handle
- title
- deterministic question text
- why-it-matters text
- expected reply shape
- required fields
- artifact intent
- not-applicable guidance
- deterministic order

## Read-Only Evaluator

Add `evaluate_core_spec_slots(db)` with no writes.

State model:

- `missing`: no current spec and no not-applicable decision exists
- `inferred`: only inferred, provisional, unknown, or null-authority spec
  evidence exists
- `needs_clarity`: owner-stated spec exists but required title/description
  evidence is incomplete
- `stated`: owner-stated spec evidence exists
- `not_applicable`: owner-decision deliberation explicitly marks the slot not
  applicable

Completion rule:

- complete states: `stated`, `not_applicable`
- incomplete states: `missing`, `inferred`, `needs_clarity`

Matching rules:

- spec evidence may match by stable `handle`
- spec evidence may also match by tag equal to the slot handle
- not-applicable evidence uses source_ref:
  `core-spec:{handle}:not-applicable`
- not-applicable evidence must be an `owner_conversation` deliberation with
  `outcome="owner_decision"`

## Tests

Add `tests/test_core_specs.py`.

Required coverage:

- stable slot handles and order
- all slots include prompt metadata and not-applicable guidance
- lookup by handle succeeds
- unknown handle raises
- fresh DB reports `core-identity` as `missing`
- inferred candidate does not suppress prompting
- owner-stated spec completes the slot
- owner-stated spec without description returns `needs_clarity`
- explicit not-applicable decision completes the slot
- all-complete state suppresses next question

Compatibility tests to run unchanged:

```powershell
python -m pytest tests/test_spec_scaffold.py tests/test_scaffold_project.py -q --tb=short
```

## Verification Commands

Expected local verification:

```powershell
python -m pytest tests/test_core_specs.py tests/test_spec_scaffold.py tests/test_scaffold_project.py -q --tb=short
python -m ruff check src/groundtruth_kb/core_specs.py tests/test_core_specs.py
python -m ruff format --check src/groundtruth_kb/core_specs.py tests/test_core_specs.py
python -m mypy --strict src/groundtruth_kb/core_specs.py tests/test_core_specs.py
```

## Current Draft Verification Evidence

The current uncommitted draft in the target checkout produced:

```text
python -m pytest tests/test_core_specs.py tests/test_spec_scaffold.py tests/test_scaffold_project.py -q --tb=short
27 passed, 1 warning

python -m ruff check src/groundtruth_kb/core_specs.py tests/test_core_specs.py
All checks passed!

python -m ruff format --check src/groundtruth_kb/core_specs.py tests/test_core_specs.py
2 files already formatted

python -m mypy --strict src/groundtruth_kb/core_specs.py tests/test_core_specs.py
Success: no issues found in 2 source files
```

## Review Questions

1. Is the proposed read-only evaluator sufficient for Phase 2, or should it
   remain catalog-only until a separate evaluator bridge?
2. Is `core-spec:{handle}:not-applicable` an acceptable source_ref contract for
   explicit slot-level not-applicable decisions?
3. Is matching by handle/tag sufficient for the first implementation, with more
   advanced linked-record matching deferred to the answer/CLI slice?
4. Is `needs_clarity` based on missing title/description acceptable as the first
   structural clarity check?

## Non-Scope

No CLI, project-init, doctor, startup, dashboard, or answer mutation behavior.
No change to existing `minimal`/`full` spec scaffold output.
No commit or package release until a post-implementation verification passes.
