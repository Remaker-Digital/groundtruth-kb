GO

# Loyal Opposition Response: GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 3 Revision 1

Status: GO

## Claim

`bridge/gtkb-isolation-016-phase8-wave2-slice3-003.md` resolves the Slice 3
NO-GO findings sufficiently to proceed with implementation.

The revised driver plan preserves safe default dry-run behavior, adds an
explicit Wave 2 `--execute` opt-in, applies M2 output-dir safety to CLI
overrides, and narrows not-yet-implemented lane handling so real lane defects
are not hidden as skips.

## Evidence

- F1 is addressed by introducing `--execute` as the only real-run opt-in while
  preserving `--no-dry-run` refusal
  (`bridge/gtkb-isolation-016-phase8-wave2-slice3-003.md:17` through `:52`).
- F2 is addressed by extracting `validate_sandbox_output_dir()` and calling it
  for `--output-dir` overrides before any writes
  (`bridge/gtkb-isolation-016-phase8-wave2-slice3-003.md:61` through `:93`).
- F3 is addressed by separating missing-lane modules from broken lane imports
  and missing `run()` functions
  (`bridge/gtkb-isolation-016-phase8-wave2-slice3-003.md:111` through `:166`).
- The test plan covers real-run opt-in, default dry-run skip behavior,
  output-dir override safety, and the three dispatch states: missing lane,
  broken dependency, and missing run function
  (`bridge/gtkb-isolation-016-phase8-wave2-slice3-003.md:178` through `:220`).

## Risk / Impact

No blocking proposal-level risk remains.

Two implementation details should be checked in post-implementation review:

- Make the interaction between explicit `--dry-run` and `--execute` visible and
  deterministic. Rejecting both together or documenting `--execute` precedence
  is acceptable; silently ambiguous behavior is not.
- Keep run-summary coverage in the test set. The proposal still includes
  run-summary emission, but the revised test-plan count is inconsistent
  (`13 net additions` after an 11-test table plus one sibling test). The
  implemented tests should assert the summary is written when a lane returns
  `ok` and is not written before output-dir validation succeeds.

## Recommended Action

Proceed with Slice 3 under these implementation conditions:

- Keep the change scoped to `scripts/rehearse_isolation.py`,
  `scripts/rehearse/_common.py`, and additive tests.
- Preserve `--no-dry-run` refusal.
- Use `--execute` for real lane invocation and keep the default safe dry-run.
- Validate output-dir overrides with the same M2 sandbox contract as manifest
  `output_dir`.
- Treat broken implemented lanes as `error`, not `skipped`.

## Decision Needed From Owner

None.
