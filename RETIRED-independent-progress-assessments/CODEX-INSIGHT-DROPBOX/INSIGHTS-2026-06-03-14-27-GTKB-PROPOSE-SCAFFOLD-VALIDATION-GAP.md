# Loyal Opposition Insight: `/gtkb-propose` Scaffold Validation Gap

Date: 2026-06-03 UTC
Author: Codex Loyal Opposition (harness A)
Severity: P1
Subject: `gtkb-propose` scaffold helper accepts nonexistent WI/Project/PAUTH metadata

## Executive Summary

The bridge thread `gtkb-proposal-standards-propose-scaffold-skill` is latest
`VERIFIED` at `bridge/gtkb-proposal-standards-propose-scaffold-skill-004.md`,
but a late sidecar verification found one material gap in the shipped helper:
the approved design promised read-only MemBase validation of the
WI/Project/PAUTH triple, while the implementation currently accepts arbitrary
nonexistent IDs and interpolates them into the generated scaffold.

This report does not reopen the terminal bridge thread directly. It preserves
the evidence as an additive Loyal Opposition finding for Prime Builder to
convert into a corrective proposal or work item.

## Finding F1 - Missing WI/Project/PAUTH Validation

### Observation

The approved proposal explicitly required read-only validation of the
WI/Project/PAUTH triple against MemBase:

- `bridge/gtkb-proposal-standards-propose-scaffold-skill-001.md:67`:
  `Validates the WI/Project/PAUTH triple read-only against MemBase`.
- `bridge/gtkb-proposal-standards-propose-scaffold-skill-001.md:76`:
  the helper should pre-list specs from `config/governance/spec-applicability.toml`
  based on planned `target_paths`.

The post-implementation report claimed the design was implemented without
deviation:

- `bridge/gtkb-proposal-standards-propose-scaffold-skill-003.md:39`:
  `No deviation from the GO'd design`.
- `bridge/gtkb-proposal-standards-propose-scaffold-skill-003.md:65`:
  project-linkage lines are filled from `validated inputs`.

The installed skill repeats the validation promise:

- `.claude/skills/gtkb-propose/SKILL.md:47-48`: the helper validates the
  work-item/project/authorization triple read-only against MemBase.

The actual helper validates only slug shape/collision before building the
scaffold:

- `scripts/gtkb_propose_scaffold.py:302-306`: slug validation and collision
  check.
- `scripts/gtkb_propose_scaffold.py:312-316`: user-supplied `work_item`,
  `project`, and `pauth` are passed directly to `build_scaffold`.
- `scripts/gtkb_propose_scaffold.py:190-192`: those values are interpolated
  into the emitted metadata.

Live negative smoke test:

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\gtkb_propose_scaffold.py scaffold --slug lo-validation-smoke-nonexistent --work-item WI-DOES-NOT-EXIST --project PROJECT-DOES-NOT-EXIST --pauth PAUTH-DOES-NOT-EXIST --no-write
exit=0
```

Tests currently reinforce the weaker behavior by using dummy identifiers:

- `platform_tests/scripts/test_gtkb_propose_scaffold.py:39-40` uses
  `PROJECT-DEMO` and `PAUTH-DEMO`.
- `platform_tests/scripts/test_gtkb_propose_scaffold.py:81-83` asserts only
  that those inputs appear in the generated body.

### Deficiency Rationale

The shipped helper can emit structurally compliant bridge drafts carrying
nonexistent project authorization metadata. That is exactly the class the
approved Slice 4 design was supposed to prevent before proposal filing.

The risk is not cosmetic: downstream proposal authors may trust the scaffold's
project-linkage fields as validated evidence, then file bridge artifacts that
pass superficial structure checks but fail implementation authorization or
misroute work to invalid governance metadata.

### Proposed Solution / Enhancement

Prime Builder should file a corrective proposal for `gtkb-propose` scaffold
validation with this minimal scope:

1. Add a read-only MemBase validation function in
   `scripts/gtkb_propose_scaffold.py` that confirms:
   - the work item exists in the current work-item view;
   - the project exists and the work item is an active member of that project;
   - the PAUTH exists, is active, belongs to the project, and includes the work
     item or otherwise authorizes the membership under the established PAUTH
     semantics.
2. Fail closed before scaffold emission when any part of the triple is invalid.
3. Add negative tests for nonexistent work item, nonexistent project,
   nonexistent PAUTH, wrong-project membership, and PAUTH/work-item mismatch.
4. Replace dummy positive IDs in existing tests with fixtures or a controlled
   in-memory/read-only MemBase setup that proves real validation, not string
   interpolation.
5. Keep the helper read-only against MemBase and continue writing only under
   `.gtkb-state/propose-drafts/`.

### Option Rationale

The least-risk fix is to repair the helper rather than weaken the Slice 4
proposal record. The proposal's validation requirement is sound and aligns
with the project-linkage governance objective; the implementation simply did
not enforce it. A focused corrective proposal keeps the terminal bridge audit
trail intact while creating a clean review surface for the missing validation.

## Prime Builder Implementation Context

Objective: make `/gtkb-propose` fail closed on invalid governance linkage before
it emits a draft.

Expected touchpoints:

- `scripts/gtkb_propose_scaffold.py`
- `platform_tests/scripts/test_gtkb_propose_scaffold.py`
- `.claude/skills/gtkb-propose/SKILL.md` only if invocation or operator
  guidance changes

Verification steps:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_gtkb_propose_scaffold.py -q --tb=short
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts/gtkb_propose_scaffold.py platform_tests/scripts/test_gtkb_propose_scaffold.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts/gtkb_propose_scaffold.py platform_tests/scripts/test_gtkb_propose_scaffold.py
```

Acceptance criteria:

- The negative smoke command with `WI-DOES-NOT-EXIST`,
  `PROJECT-DOES-NOT-EXIST`, and `PAUTH-DOES-NOT-EXIST` exits nonzero.
- Positive tests prove the helper accepts a real, active, authorized
  WI/Project/PAUTH triple.
- The emitted scaffold remains structurally compliant with the proposal
  standards gates.

Rollback / containment: revert the corrective commit; no bridge or MemBase
write path should be introduced by this remediation.

## Open Decisions Required From Owner

None for report preservation. A corrective implementation still needs the
normal bridge proposal -> Loyal Opposition review -> implementation -> post-
implementation verification cycle.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
