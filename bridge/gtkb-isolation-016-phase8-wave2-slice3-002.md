NO-GO

# Loyal Opposition Response: GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 3 Proposal

Status: NO-GO

## Claim

`bridge/gtkb-isolation-016-phase8-wave2-slice3-001.md` is not approved as
written. Driver wire-up is the right next slice, but the proposal has three
blocking control-flow and safety defects.

## Findings

### F1 - Blocking: dry-run remains permanently true, so inventory will not run

The proposal says Slice 3 will "actually invoke implemented Wave 2 lanes" and
that `python scripts/rehearse_isolation.py --phase inventory` will produce a
real inventory and runtime manifest
(`bridge/gtkb-isolation-016-phase8-wave2-slice3-001.md:25`,
`:197`, `:230`). But the current parser makes `args.dry_run` true by default
and refuses `--no-dry-run` (`scripts/rehearse_isolation.py:80` through `:103`).
The proposal passes that value directly into `_dispatch()` and the lane call
(`bridge/gtkb-isolation-016-phase8-wave2-slice3-001.md:130`).

Slice 2's verified inventory lane returns `status="skipped"` immediately when
`dry_run=True` (`scripts/rehearse/_inventory.py:226` through `:231`). Therefore
the proposed default driver path still does not produce `inventory.json` or
`runtime-manifest.toml`, contradicting the slice's central claim.

Required revision: explicitly define Wave 2 execution semantics. Either make
normal `--phase inventory` execution pass `dry_run=False` under the existing
sandbox/output-dir safety rules, or revise the slice claim and tests so the
driver remains dry-run-only. If real lane execution is intended, update the
`--dry-run` / `--no-dry-run` CLI behavior and the existing v1 refusal test
accordingly.

### F2 - Blocking: `--output-dir` bypasses M2 output-dir safety

Slice 1 added M2 output-dir validation so the rehearsal output location is a
sandbox path outside `LEGACY_ROOT` and `TARGET_ROOT_DEFAULT`. The Slice 3
proposal validates only the manifest value via `load_manifest(..., wave=2)`.
The new `_resolve_output_dir()` then returns any `--output-dir` override
verbatim (`bridge/gtkb-isolation-016-phase8-wave2-slice3-001.md:54` through
`:67`).

Impact: an operator or test can direct `inventory.json`, `runtime-manifest.toml`,
or `run-summary.json` back into the legacy root, target root, or a synced path,
undoing the safety property that Wave 2 validation was added to enforce.

Required revision: either remove `--output-dir` from this slice or validate the
override with the same effective M2 safety contract as `manifest.output_dir`
before any file writes. Add negative tests for overrides under `LEGACY_ROOT`,
`TARGET_ROOT_DEFAULT`, and a non-allowlisted path, plus a positive override
under an approved sandbox path.

### F3 - Blocking: broad import/attribute handling hides real lane defects

The proposal catches `(ModuleNotFoundError, AttributeError)` around both module
import and `getattr()` and converts either exception into a skipped
"not yet implemented" result
(`bridge/gtkb-isolation-016-phase8-wave2-slice3-001.md:86` through `:105`).

That is too broad. If an implemented lane imports a missing dependency, or if a
module raises `AttributeError` during import, the driver would incorrectly
report "not yet implemented" instead of failing the lane. This would mask real
defects once Stages B-D begin landing.

Required revision: distinguish "lane module does not exist yet" from "lane
module exists but is broken." For example, catch `ModuleNotFoundError` only
when the missing module is exactly the lane module being imported, perform
`getattr()` in a separate block, and return `status="error"` for dependency or
runtime import failures. Add tests for both cases.

## Recommended Action

Revise Slice 3 before implementation:

- Define and test actual execution mode versus dry-run mode.
- Preserve M2 output-dir safety for CLI overrides.
- Narrow unimplemented-lane detection so real implemented-lane defects fail
  visibly.

## Decision Needed From Owner

None.
