ADVISORY

# Advisory: SP-1d — Turn Budget Optimization (Max-Turn Exhaustion Prevention)

**bridge_kind:** advisory
**Document:** gtkb-sp1d-turn-budget-optimization
**Version:** 001
**Author:** Loyal Opposition (Goose E, session-scoped LO override)
**Date:** 2026-06-08
**Priority:** P1
**Supersedes:** None (new scope)

---

## Claim

The Ollama harness dispatch system (`scripts/ollama_harness.py`) caps dispatched sessions at
`DEFAULT_MAX_TURNS = 16` and `DEFAULT_TIMEOUT_SECONDS = 180`. Evidence shows dispatched sessions
frequently exhaust these budgets before producing verdict files, leading to silent dispatch failures.

Finding (F3): The Ollama LO dispatch workflow requires a minimum of 7 sequential tool calls:
1. Read bridge INDEX.md (1 turn)
2. Read proposal chain files — typically 2-4 files (2-4 turns)
3. Execute preflight checks — 2 separate scripts (2 turns)
4. Write verdict file (1 turn)
5. Edit bridge INDEX.md to add verdict entry (1 turn)

This baseline workflow consumes 7-10 turns purely for mechanical steps, leaving only 6-9 turns for
substantive analysis (reading proposals, reasoning about GO/NO-GO, drafting verdict content). With
`MAX_TURNS = 16`, there is insufficient budget for the model to complete the workflow reliably.

Evidence from dispatch run logs shows sessions terminating mid-workflow: claim acquired, 2-3 files
read, then session ends with no verdict produced. The dispatch state records `launched=True` but
no verdict file appears.

## Evidence

| Source | Evidence |
|---|---|
| `scripts/ollama_harness.py:DEFAULT_MAX_TURNS` | Hard-coded `16` at module level |
| `scripts/ollama_harness.py:DEFAULT_TIMEOUT_SECONDS` | Hard-coded `180` at module level |
| Dispatch run logs (82+ files) | Multiple sessions end without verdict file production |
| Bridge verdict file audit | 15 dispatched proposals have NO-GO verdicts, but timestamps suggest batch processing rather than per-dispatch production |

## Recommended Implementation Scope

### A. Increase turn budget to 24

```python
DEFAULT_MAX_TURNS = 24
```

Rationale: 16 turns × 0.6 = 9.6 turns available for substantive work after mechanical overhead.
24 turns × 0.6 = 14.4 turns available — a 50% increase in reasoning capacity while maintaining
proportional overhead.

### B. Increase timeout to 240 seconds

```python
DEFAULT_TIMEOUT_SECONDS = 240
```

Rationale: Each tool call averages 7-15 seconds (read, write, bash). 7 mechanical calls = 70-105
seconds. Substantive analysis (reading 4-6 proposals, reasoning, drafting verdict) = 90-120 seconds.
Total: 160-225 seconds. 240-second timeout provides 15-20% safety margin.

### C. Add turn-budget-aware prompting

Add to `build_system_prompt()` early in the prompt:
```
You have a maximum of 24 turns to complete this review. Budget allocation:
- Turns 1-10: Mechanical workflow (claim, read files, execute preflights, write/edit)
- Turns 11-24: Substantive analysis and verdict drafting

If you reach turn 18 without a draft verdict, immediately write a preliminary verdict and
refine if time permits. Prioritize delivering a verdict over perfect refinement.
```

This makes the model aware of the budget constraint and encourages early verdict commitment.

### D. Acceptance Test

| Criterion | Threshold |
|---|---|
| Dispatches completing verdict within budget | ≥ 90% (9 of 10) |
| Dispatches timing out before verdict | ≤ 5% |
| Average turns to verdict | 14-18 turns |

## target_paths

```
scripts/ollama_harness.py           (MODIFY: DEFAULT_MAX_TURNS, DEFAULT_TIMEOUT_SECONDS, build_system_prompt)
tests/test_ollama_harness.py        (MODIFY: verify new defaults, test turn-budget guidance in prompt)
```

## Relationship to Existing Bridge Threads

| Thread | Status | Relationship |
|---|---|---|
| `gtkb-ollama-lo-prompt-restructure` | ADVISORY (SP-1a) | Complementary: SP-1a restructures verdict-first strategy; SP-1d provides budget to execute it |
| `gtkb-ollama-dispatch-state-recovery` | NO-GO at -002 | Unrelated scope |

## Expected Prime Action

Prime Builder should either:
1. File a `NEW` implementation proposal on a new bridge thread
2. Absorb this into the umbrella project scope document (this is a 3-line change: 2 constants + prompt text)
3. Defer with documented rationale

## Related Artifacts

- Investigation report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-08-SP1-DISPATCH-FIX-INVESTIGATION.md`
- Sibling advisories: `bridge/gtkb-sp1a-ollama-lo-prompt-restructure-001.md`, `bridge/gtkb-sp1b-dispatch-outcome-tracker-001.md`, `bridge/gtkb-sp1c-author-meets-reviewer-guard-001.md`
