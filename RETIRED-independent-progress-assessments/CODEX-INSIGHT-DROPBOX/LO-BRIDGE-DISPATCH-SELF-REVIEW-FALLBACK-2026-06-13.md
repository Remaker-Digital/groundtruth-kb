# LO Bridge Dispatch Self-Review Fallback Report

Date: 2026-06-13 UTC
Role: Loyal Opposition
Harness: Codex / A

## Claim

The cross-harness bridge trigger had a narrow ordered-fallback defect: when a
preferred Loyal Opposition candidate was dispatch-ready but would refuse the
selected bridge item under the same-harness author/reviewer separation rule, the
trigger recorded `author_meets_reviewer_refused` after selection instead of
skipping that candidate and falling through to the next eligible LO harness.

## Evidence

- Durable role check confirmed Codex harness `A` is assigned
  `loyal-opposition` via `python -m groundtruth_kb.cli harness roles`.
- Live bridge scan initially exposed a same-harness verification case on
  `bridge/gtkb-tafe-subproject-prefix-reconciliation-003.md`; Codex harness
  `A` correctly skipped direct verification because the implementation report
  was authored by harness `A`.
- Running `python scripts/cross_harness_bridge_trigger.py --project-root E:\GT-KB --max-items 1 --verbose`
  surfaced the dispatch path that selected a candidate before applying the
  same-harness refusal.
- The repaired path in `scripts/cross_harness_bridge_trigger.py` now evaluates
  the candidate-specific selected bridge item during LO ordered fallback. If
  `_should_refuse_self_review(...)` is true, it records
  `author_meets_reviewer_refused` for that candidate and continues to the next
  ready LO target.
- Regression coverage in
  `platform_tests/scripts/test_cross_harness_bridge_trigger.py` adds
  `test_lo_ordered_fallback_skips_same_harness_author_target`, which proves the
  sequence `D not ready -> A same-harness refused -> F selected`.

## Risk / Impact

Without this repair, a same-harness bridge item could stop automated LO
dispatch even when a later eligible reviewer was available. That weakens bridge
throughput and can strand review work behind a correct self-review refusal.

## Verification

- `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short -k "lo_ordered_fallback or author_meets_reviewer"`
- `python -m ruff check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_bridge_trigger.py`
- `python -m ruff format --check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_bridge_trigger.py`

## Recommended Action

Keep the bridge-trigger repair and regression test. Continue to rely on live
`bridge/INDEX.md` and the same-harness separation rule when selecting LO work.

## Decision Needed From Owner

None.
