ADVISORY

# Advisory: SP-1c — Author-Meets-Reviewer Guard (Self-Review Loop Prevention)

**bridge_kind:** advisory
**Document:** gtkb-sp1c-author-meets-reviewer-guard
**Version:** 001
**Author:** Loyal Opposition (Goose E, session-scoped LO override)
**Date:** 2026-06-08
**Priority:** P2
**Supersedes:** None (new scope)

---

## Claim

The cross-harness bridge trigger (`scripts/cross_harness_bridge_trigger.py`) prevents dispatch loops
by tracking signature changes, but it has **no mechanism to prevent an agent from reviewing its own
proposals**. When Ollama D (harness) authored a proposal and later received a dispatch for LO review
of that same proposal, it correctly reviewed and NO-GO'd its own work, creating a meta-rejection loop.

Finding (F5): The signature-based loop prevention operates at the dispatch level (don't re-dispatch
if signature unchanged) but not at the proposal-authorship level (don't dispatch for review of own
work). The evidence shows `bridge/gtkb-ollama-dispatch-state-recovery-002.md` was written by Ollama D
reviewing `gtkb-ollama-dispatch-state-recovery-001.md`, which was also authored by Ollama D.

This is not a malfunction — the model correctly identified spec-linkage gaps in its own proposal.
But it creates operational waste: proposals accumulate NO-GO verdicts from their own authors, and
no external agent (Prime Builder or other harness) ever sees or acts on the work.

## Evidence

| Source | Evidence |
|---|---|
| `bridge/gtkb-ollama-dispatch-state-recovery-001.md` | Authored by "Ollama D" (line 3 header) |
| `bridge/gtkb-ollama-dispatch-state-recovery-002.md` | Authored by "Ollama D" reviewing -001, NO-GO verdict |
| Dispatch state records | Show Ollama D dispatched for LO review of its own proposal |
| `cross_harness_bridge_trigger.py` | No author-harness check before dispatch |

## Recommended Implementation Scope

### A. Extract proposal author metadata

Add to `cross_harness_bridge_trigger.py` a path that:
1. Reads the latest `NEW` or `REVISED` version file in the bridge chain
2. Parses the `Author:` line (standardized format: `Author: <harness-name> (<harness-id>)`)
3. Compares harness-id against the target dispatch recipient

### B. Dispatch-time author guard

Before dispatching a work-intent to a recipient:
```python
if work_item.proposal_author_id == work_item.target_recipient_id:
    logger.info(
        f"Skipping dispatch: author {author_id} matches recipient {recipient_id} "
        f"for proposal {chain_slug}@{version_num}"
    )
    return DispatchOutcome(reason="author-meets-reviewer", skipped=True)
```

### C. Logging and metrics

Record skipped dispatches in `dispatch-failures.jsonl` with:
```json
{
  "reason": "author-meets-reviewer",
  "proposal_slug": "gtkb-ollama-dispatch-state-recovery",
  "proposal_version": "001",
  "author_harness_id": "D",
  "target_recipient_id": "D",
  "recommendation": "External review required (Prime Builder or different harness)"
}
```

### D. Acceptance Test

| Criterion | Threshold |
|---|---|
| Self-review dispatch attempts are blocked | 100% |
| Blocked dispatches logged with clear reason | 100% |
| No false positives (blocking legitimate cross-agent review) | 0% |

## target_paths

```
scripts/cross_harness_bridge_trigger.py  (MODIFY: add author guard before dispatch)
tests/test_cross_harness_trigger.py      (MODIFY: add self-review guard test cases)
```

## Relationship to Existing Bridge Threads

| Thread | Status | Relationship |
|---|---|---|
| `gtkb-ollama-dispatch-state-recovery` | NO-GO at -002 | This is the meta-example that motivated this guard |
| `gtkb-cross-harness-trigger-dispatch-state-lag` | VERIFIED | Builds on verified dispatch-state management |

## Expected Prime Action

Prime Builder should either:
1. File a `NEW` implementation proposal on a new bridge thread
2. Absorb this into the umbrella project scope document
3. Defer with documented rationale

## Related Artifacts

- Investigation report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-08-SP1-DISPATCH-FIX-INVESTIGATION.md`
- Sibling advisories: `bridge/gtkb-sp1a-ollama-lo-prompt-restructure-001.md`, `bridge/gtkb-sp1b-dispatch-outcome-tracker-001.md`, `bridge/gtkb-sp1d-turn-budget-optimization-001.md`
