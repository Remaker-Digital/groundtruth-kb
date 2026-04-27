GO

# Loyal Opposition Response: GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 4 Revision 1

Status: GO

## Claim

The revised Slice 4 proposal resolves the two blocking findings from `gtkb-isolation-016-phase8-wave2-slice4-002.md` and is approved for implementation.

## Evidence

- Prior F1 blocked the original proposal because `python -m groundtruth_kb.cli project classify-tree ...` exits `0` without writing `classification.json` in this checkout (`gtkb-isolation-016-phase8-wave2-slice4-002.md:16`, `:24`, `:26`).
- The revision replaces that no-op module invocation with a callable entrypoint through `sys.executable -c "from groundtruth_kb.cli import main; main()" project classify-tree ...` (`gtkb-isolation-016-phase8-wave2-slice4-003.md:43`, `:53`, `:55`).
- The revision adds command-shape and live temp-dir subprocess coverage that would catch a future silent no-op because it asserts `classification.json` is created from a real `classify-tree` run (`gtkb-isolation-016-phase8-wave2-slice4-003.md:73`, `:75`).
- Prior F2 blocked the original proposal because `target_namespace = "applications/Agent_Red"` was proposed as a hard-coded value instead of being derived from the validated manifest (`gtkb-isolation-016-phase8-wave2-slice4-002.md:55`, `:57`, `:80`).
- The revision derives the namespace from `manifest["target_root"]` relative to `manifest["legacy_root"]` and normalizes path separators (`gtkb-isolation-016-phase8-wave2-slice4-003.md:86`, `:98`, `:99`, `:100`, `:107`).
- The revised test plan includes a `Different_App` fixture proving the rewrite target follows manifest data rather than an `Agent_Red` constant (`gtkb-isolation-016-phase8-wave2-slice4-003.md:123`, `:124`, `:146`).
- Slice 3 already introduced the `rewrite` dispatch slot, so Slice 4's driver integration target is consistent with the current rehearsal driver surface (`scripts/rehearse_isolation.py:48`, `:143`, `:279`).

## Risk / Impact

No blocking risk remains at the proposal level. The highest implementation risk is preserving the executable command contract: a subprocess that exits successfully but does not create `classification.json` must be treated as `status="error"` rather than as an empty or successful rewrite result.

## Recommended Action

Proceed with implementation under these conditions:

1. Keep `_build_classify_tree_command()` on the callable `sys.executable -c "from groundtruth_kb.cli import main; main()"` form; do not reintroduce `python -m groundtruth_kb.cli`.
2. After a zero-exit subprocess return, explicitly verify that `classification.json` exists before parsing it.
3. Keep live subprocess testing constrained to a tiny temp tree; do not run live classify-tree against `LEGACY_ROOT` in unit tests.
4. Derive rewrite targets from the validated manifest's `target_root` and `legacy_root`, including the non-`Agent_Red` fixture guard.
5. Keep `legacy-exception` and `owner_decision_pending` as warning-producing, non-blocking classifications for this lane unless a later governance artifact changes that contract.

## Decision Needed From Owner

None.
