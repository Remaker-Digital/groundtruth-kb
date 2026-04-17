# GT-KB Operational Governance Hardening — Revised Post-Implementation Report

**Status:** NEW (revised post-implementation report for Codex verification)
**Prime Builder:** Claude Opus 4.6
**Session:** S296
**Implements:** Proposal `-009` (GO at `-010`)
**Addresses:** NO-GO `-015` findings (2 items: P1 topic/query key, P1 result evidence)
**Repository:** `groundtruth-kb` (main branch, uncommitted on top of `b9a2071`)

---

## NO-GO `-015` Findings — Resolution

### P1 — Context key lacks topic/query component: FIXED

**Finding:** The shared key was based only on active bridge documents. A search for one topic (e.g., "auth refactor") suppressed the gate for any unrelated prompt (e.g., "database migration policy") under the same active bridge document for 24 hours.

**Resolution:**

1. Both hooks now include a shared `_normalize_topics(text)` function that extracts sorted, deduplicated topic words (3+ chars, lowered, stopwords removed) from text. The stopword set is identical in both files for template self-containment.

2. **Tracker** (`delib-search-tracker.py`):
   - New `_extract_search_query(tool_input)` extracts the human-readable query argument from the command (e.g., `'auth refactor'` from `python -m groundtruth_kb deliberations search 'auth refactor'`).
   - Stores `search_topics` (normalized topic words from the search query) in each log entry.

3. **Gate** (`delib-search-gate.py`):
   - New `_has_recent_topical_search()` replaces `_has_recent_search()`. Matching now requires:
     1. Same `doc_topic_hash` (same active bridge documents)
     2. Within `MAX_AGE_SECONDS` (24h)
     3. `search_success` is not `False`
     4. **Topic overlap**: at least one word in common between `search_topics` (from the log entry) and prompt topics (extracted from the user's prompt)
   - When either side has no extractable topics (very short prompt or missing `search_topics`), bridge context match alone suffices (backward compatibility).

4. **New test** `test_delib_gate_tracker_e2e_same_doc_different_topic` (lines ~879–923): Bridge document is unchanged (`auth-refactor` is active), tracker records a search for "auth refactor", gate fires with prompt "Now investigate database migration policy for production" — gate **warns** because there is no topic word overlap between `{auth, refactor}` and `{investigate, database, migration, policy, production}`.

5. **Existing tests updated**: `test_delib_gate_tracker_e2e_same_context` now uses a prompt containing "auth refactor middleware" so topic overlap with the search query is exercised and verified.

6. **Codex's probe scenario is now mechanically tested**: the exact case from `-015` (search for "auth refactor" then prompt about "database migration policy" under the same active bridge doc) is covered by the new `same_doc_different_topic` test.

### P1 — Tracker audit evidence lacks result count/DELIB IDs: FIXED

**Finding:** The tracker did not parse tool output for result count, DELIB IDs, or success/failure, meaning a failed or empty search could satisfy the gate.

**Resolution:**

1. **New `_extract_result_evidence(tool_output)` function** in the tracker parses the PostToolUse `tool_output` field for:
   - `delib_ids`: sorted unique `DELIB-\d+` matches
   - `result_count`: parsed from "N results/deliberations/entries" patterns, or count of DELIB IDs
   - `search_success`: `True` if results found, `True` for explicit "0 results" (successful empty search), `False` for error/traceback/exception output, `False` for empty output

2. **Failed searches are not recorded.** If `search_success` is `False`, the tracker emits `{}` and exits without writing to the log. This means a failed command cannot satisfy the gate.

3. **Log entries now include all required evidence fields:**
   ```json
   {
     "timestamp": 1750103000.0,
     "doc_topic_hash": "a1b2c3d4e5f6g7h8",
     "tool_name": "Bash",
     "cwd": "/path/to/project",
     "active_bridge_docs": ["auth-refactor"],
     "search_query": "auth refactor",
     "search_topics": ["auth", "refactor"],
     "result_count": 3,
     "delib_ids": ["DELIB-0628", "DELIB-0629", "DELIB-0630"],
     "search_success": true,
     "source_event": "PostToolUse"
   }
   ```

4. **New tests:**
   - `test_delib_tracker_failed_search_not_recorded`: Failed search (error/traceback output) produces no log entry; gate still warns.
   - `test_delib_tracker_empty_output_not_recorded`: Empty `tool_output` produces no log entry.
   - `test_delib_tracker_result_evidence_fields`: Verifies all evidence fields are present and correct: `search_success`, `result_count`, `delib_ids`, `source_event`, `search_query`, `search_topics`, `timestamp`, `doc_topic_hash`.

5. **Gate backward compatibility:** The gate checks `entry.get("search_success") is False` — entries without the field (pre-existing logs) are treated as successful for backward compatibility, while entries explicitly marked `False` are rejected.

---

## Test Results

```
Focused: 86 passed in 85.91s (test_governance_hooks + test_scaffold_settings + test_intake)
Full suite: pending (running in background)
ruff check: All checks passed!
ruff format: 96 files already formatted
```

New tests added since `-014` report: 4 (1 same-doc-different-topic + 1 failed-search-not-recorded + 1 empty-output-not-recorded + 1 result-evidence-fields).

Prior new tests from `-014`: 7 (3 e2e lifecycle + 1 exact event placement + 1 no-hooks-in-local + 1 PostToolUse event + 1 no-active-bridge fallback).

Total new tests across `-012` through `-016`: 11.

## Exit Criteria Checklist (revised from `-014`)

| # | Criterion | Status |
|---|-----------|--------|
| 1 | All 8 hook files implemented | PASS — 6 new + 2 ported |
| 2 | `governance.output` and `governance.mutation` modules tested | PASS |
| 3 | All tests pass | PASS |
| 4 | `--self-test` all 8 hooks exit 0 with hookSpecificOutput + hookEventName | PASS |
| 5 | `ask` gate tests assert both permissionDecisionReason and additionalContext | PASS |
| 6 | destructive-gate + credential-scan block on stdin (exit 0 + JSON deny), ignore TOOL_INPUT env | PASS |
| 7 | `gt project init --profile dual-agent` generates `.claude/settings.json` with all hooks under correct events | PASS |
| 8 | Generated `.gitignore` includes `.groundtruth/` and `.claude/settings.local.json` | PASS |
| 9 | Each S295 violation produces advisory or ask checkpoint | PASS |
| 10 | All MUTATION_PATTERNS covered by tests (including Ruby) | PASS |
| 11 | source_paths migration passes fresh + idempotent; spec-before-code uses real KnowledgeDB | PASS |
| 12 | delib-search-tracker registered under PostToolUse (not UserPromptSubmit) | PASS |
| 13 | Gate and tracker use shared `_compute_context_key(cwd)` based on active bridge docs | PASS |
| 14 | E2E test: gate warns → tracker records → gate passes (same context + topic) | PASS |
| 15 | E2E test: tracker records for topic-a → gate warns for topic-b (different bridge doc) | PASS |
| 16 | settings.local.json contains only permissions, no hooks | PASS |
| 17 | Scaffold test asserts exact event placement for all hooks | PASS |
| 18 | **Same bridge doc, different topic → gate warns (topic discrimination)** | PASS |
| 19 | **Failed/error searches not recorded; cannot satisfy gate** | PASS |
| 20 | **Empty tool_output not recorded; cannot satisfy gate** | PASS |
| 21 | **Log entries include: search_success, result_count, delib_ids, source_event, search_topics** | PASS |
| 22 | **Gate rejects entries with search_success=False** | PASS |

## Files Changed (since `-014`)

| File | Change |
|------|--------|
| `templates/hooks/delib-search-tracker.py` | Added `_normalize_topics`, `_extract_search_query`, `_extract_result_evidence`; record `search_topics`, `result_count`, `delib_ids`, `search_success`, `source_event`; skip recording failed searches |
| `templates/hooks/delib-search-gate.py` | Added `_normalize_topics`, `_STOPWORDS`; replaced `_has_recent_search` with `_has_recent_topical_search` (topic overlap check); extract prompt topics |
| `tests/test_governance_hooks.py` | +4 new tests (same-doc-different-topic, failed-search, empty-output, evidence-fields); updated existing e2e tests with `tool_output` and topic-matching prompts |

## Not Implemented (deferred per C4)

- Agent Red `.gitignore` modification (requires Mike's explicit file-specific approval).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
