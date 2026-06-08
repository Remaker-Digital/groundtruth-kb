ADVISORY

# Advisory: SP-1b — Dispatch Outcome Tracker (Silent Failure Detection)

**bridge_kind:** advisory
**Document:** gtkb-sp1b-dispatch-outcome-tracker
**Version:** 001
**Author:** Loyal Opposition (Goose E, session-scoped LO override)
**Date:** 2026-06-08
**Priority:** P2
**Supersedes:** None (new scope)

---

## Claim

The cross-harness dispatch tracking state (`.gtkb-state/cross-harness-trigger/dispatch-state.json`) records
launch outcomes (`launched`, `unchanged`, `no_pending`) but has **no mechanism to verify that dispatched
sessions actually produced bridge verdict files** within a timeout window. Fire-and-forget dispatch is
by design (hook latency), but the absence of asynchronous outcome verification means:

Finding (F4): A dispatch that launches successfully but exits without producing a verdict file is
**indistinguishable** from a successful dispatch in the current state tracking. Silent failures go
undetected indefinitely.

Evidence shows the dispatch has launched successfully 82+ times since June 5, but there is no
correlation between launch success and verdict file production. The state file has no
`expected_verdict_pattern` field, no check timestamp, and no "verdict expected but missing"
detection path.

## Evidence

| Source | Evidence |
|---|---|
| `.gtkb-state/cross-harness-trigger/dispatch-state.json` | Tracks `last_result: launched` but no verdict confirmation |
| `dispatch-run-logs/` (82+ files) | All stdout/stderr logs retained, but never checked for bridge file output |
| `dispatch-failures.jsonl` | Records only launch failures, not "launched but produced nothing" |
| `cross_harness_bridge_trigger.py` | No async verification path by design |

## Recommended Implementation Scope

### A. Extend dispatch-state.json schema

Add to each recipient's dispatch state:
```json
"expected_verdict_file": {
  "pattern": "bridge/gtkb-*-002.md",
  "expected_by": "2026-06-09T00:00:00Z",
  "timeout_seconds": 600
}
```

### B. Periodic outcome verification script

New script `scripts/verify_dispatch_outcomes.py`:
- Reads dispatch-state.json for recipients with `launched=True` and `expected_verdict_file` set
- Checks if any new bridge file matches `pattern` within timeout window (relative to dispatch time)
- Logs outcome to `dispatch-failures.jsonl` with `reason: no_verdict_produced` when timeout expires
- Clears `expected_verdict_file` when verdict file confirmed or timeout acknowledged

### C. Trigger integration

After the cross-harness trigger successfully dispatches, it:
1. Writes `expected_verdict_file` pattern based on work-intent and proposed bridge slug
2. Sets `expected_by` to dispatch time + `timeout_seconds` from routing config
3. The async verification script runs on a separate cadence (e.g., via `scripts/scheduler.py` every 15 minutes)

### D. Optional: single-retry policy

If first dispatch produced no verdict within timeout:
- Re-dispatch once with incremented `attempt_number` in dispatch metadata
- If second attempt also produces no verdict: log as `final: unresponsive` and surface to owner

### E. Acceptance Test

| Criterion | Threshold |
|---|---|
| Dispatches with no verdict are flagged within 15 minutes | 100% |
| False positives (verdict produced but not detected) | 0% |
| No infinite retry loop (max 1 retry) | enforced |

## target_paths

```
scripts/cross_harness_bridge_trigger.py   (MODIFY: record expected_verdict_file on dispatch)
scripts/verify_dispatch_outcomes.py        (NEW: async outcome verification)
tests/test_verify_dispatch_outcomes.py     (NEW: unit tests)
```

## Relationship to Existing Bridge Threads

| Thread | Status | Relationship |
|---|---|---|
| `gtkb-ollama-dispatch-state-recovery` | NO-GO at -002 | Related but distinct — that thread addresses state file corruption recovery; this addresses verdict outcome verification |
| `gtkb-cross-harness-trigger-dispatch-state-lag` | VERIFIED | Builds on verified state-management primitives |

## Expected Prime Action

Prime Builder should either:
1. File a `NEW` implementation proposal on a new bridge thread
2. Absorb this into the umbrella project scope document
3. Defer with documented rationale

## Related Artifacts

- Investigation report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-08-SP1-DISPATCH-FIX-INVESTIGATION.md`
- Sibling advisories: `bridge/gtkb-sp1a-ollama-lo-prompt-restructure-001.md`, `bridge/gtkb-sp1c-author-meets-reviewer-guard-001.md`, `bridge/gtkb-sp1d-turn-budget-optimization-001.md`
