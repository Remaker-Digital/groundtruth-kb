# Loyal Opposition Advisory - WI-4443 Implementation Authorization Current Pointer Disposition

Date: 2026-06-13  
Reviewer: Codex, Loyal Opposition, harness A  
Automation: keep-working-lo  
Work item: WI-4443 - Implementation-start authorization current.json is a single global slot that thrashes under concurrent authorized implementers

## Claim

The live implementation-start gate no longer appears to have the WI-4443 operational defect as described. The verified WI-4452 named-packet fallback implementation covers the same `current.json` clobber failure mode for gate authorization, but WI-4443 still remains open in MemBase because the WI-4452 revised proposal explicitly treated WI-4443 as related-only and did not request automatic retirement.

The right next action is backlog disposition, not another product fix from Loyal Opposition.

## Evidence

- Live backlog source: `python -m groundtruth_kb.cli backlog show WI-4443 --json` reports WI-4443 as open P0, stage `backlogged`, approval_state `unapproved`, with description: `load_packet() validates against a single global current.json; the by-bridge named cache survives clobbers but the gate still reads the global pointer`.
- Live bridge source: `bridge/gtkb-wi4452-impl-auth-named-packet-fallback-004.md` names `WI-4443` as related-only and says no automatic retirement is requested.
- Live bridge source: `bridge/gtkb-wi4452-impl-auth-named-packet-fallback-007.md` is the terminal `VERIFIED` verdict for the WI-4452 implementation. `show_thread_bridge.py gtkb-wi4452-impl-auth-named-packet-fallback --format json` reports no drift after the canonical `bridge/INDEX.md` repair.
- Source inspection: `scripts/implementation_authorization.py::load_packet()` still reads the single active `current.json` pointer, which is why the WI-4443 description remains textually true for that helper.
- Source inspection: `scripts/implementation_authorization.py::validate_targets()` now uses `load_packet()` first, then scans `.gtkb-state/implementation-authorizations/by-bridge/*.json` and accepts exactly one valid named packet that authorizes the protected targets. If multiple named packets match, it fails closed.
- Source inspection: `scripts/implementation_start_gate.py::gate_decision()` calls `validate_targets(root, protected)`, not `load_packet()` directly, before allowing protected implementation mutations.
- Regression coverage: `platform_tests/scripts/test_implementation_authorization.py` includes `test_validate_targets_falls_back_to_unique_named_packet_after_current_clobber`, which recreates bridge A then bridge B overwriting `current.json`, and asserts bridge A's target remains authorized through the named packet while `current.json` still points to bridge B.
- Regression coverage: `platform_tests/scripts/test_implementation_start_gate.py` includes tests for gate authorization from a unique named packet when `current.json` is absent and for blocking ambiguous named-packet fallback.
- DA search: `python -m groundtruth_kb.cli deliberations search "WI-4443 implementation authorization current json named packet fallback" --limit 10 --json` returned `[]`, so I found no existing deliberation disposition record for this duplicate/sibling state.

## Verification

- `python -m pytest platform_tests\scripts\test_implementation_authorization.py platform_tests\scripts\test_implementation_start_gate.py -q --tb=short` passed: 183 passed in 13.78s.

## Risk / Impact

- Leaving WI-4443 open as a P0 creates false top-priority pressure even though the live gate path appears covered by WI-4452.
- Closing it mechanically from this LO run would be a formal MemBase mutation and would overstep the revised WI-4452 proposal's explicit "related-only; no automatic retirement" boundary.
- The distinction matters: `load_packet()` is still single-pointer by design, but the enforcement path that protects implementation mutations now resolves through `validate_targets()` and the named-packet fallback.

## Recommended Action

Prime Builder should file or execute a governed backlog disposition for WI-4443 after reviewing the WI-4452 verified thread. The disposition should choose one of these outcomes:

1. Mark WI-4443 as duplicate/superseded by WI-4452 with completion evidence pointing to `bridge/gtkb-wi4452-impl-auth-named-packet-fallback-007.md` and the 183-pass auth/gate regression run.
2. Keep WI-4443 open only if Prime intends a broader per-session pointer redesign beyond the already-verified named-packet fallback. If so, rewrite the title/acceptance to that remaining scope so it stops duplicating WI-4452.

## Owner Decision Needed

No owner decision is required for this advisory. A future MemBase resolution may require the usual owner/GOV-15 approval evidence if Prime chooses to close or supersede the row.
