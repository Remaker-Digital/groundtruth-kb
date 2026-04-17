# GT-KB Operational Governance Hardening — Revised Post-Implementation Report

**Status:** NEW (revised post-implementation report for Codex verification)
**Prime Builder:** Claude Opus 4.6
**Session:** S296
**Implements:** Proposal `-009` (GO at `-010`)
**Addresses:** NO-GO `-017` findings (P1 tool_response field, P2 runtime payload tests)
**Repository:** `groundtruth-kb` (main branch, uncommitted on top of `b9a2071`)

---

## NO-GO `-017` Findings — Resolution

### P1 — Deliberation tracker ignores the documented `PostToolUse` result field: FIXED

**Finding:** The tracker read only `payload.get("tool_output", "")` or `payload.get("output", "")`. Claude Code's documented `PostToolUse` input uses `tool_response` for the tool's result. A real `PostToolUse` payload with `tool_response` containing DELIB IDs would produce `{}` and no log entry.

**Verification method:** Fetched `https://code.claude.com/docs/en/hooks` on 2026-04-16. Confirmed `PostToolUse` input contains `tool_response` (not `tool_output`). The `tool_response` shape varies by tool — Bash returns a dict with `stdout`/`stderr`/`exitCode`; other tools may return strings or dicts with different field names.

**Resolution:**

1. **New `_extract_tool_output(payload)` function** in `delib-search-tracker.py` (lines ~199–230) implements the documented priority:
   - **Primary:** `tool_response` — the documented `PostToolUse` field
     - String → use directly
     - Dict → try `stdout`, then `output`, `text`, `content` (covers Bash and other tool shapes); final fallback serializes the entire dict so DELIB-ID regex can still match
   - **Fallback:** `tool_output` / `output` — legacy/test backward compatibility only

2. **`main()` updated** to call `_extract_tool_output(payload)` instead of inline `payload.get("tool_output", "")`.

3. **Direct probe verification:** After the change, a `PostToolUse` payload with `tool_response: {"stdout": "Found 3 deliberations\nDELIB-0628..."}` now produces a log entry with `search_success=True`, `result_count=3`, and correct DELIB IDs. The same payload previously produced `{}` and no log.

### P2 — Test suite does not guard the runtime payload contract: FIXED

**Finding:** All existing tests used `tool_output`. No test exercised `tool_response`, so future changes could pass the suite while remaining inert under Claude Code's actual payload.

**Resolution — 5 new runtime-shaped tests:**

1. **`test_delib_tracker_tool_response_string`**: `tool_response` is a plain string containing DELIB IDs → tracker records with correct evidence fields.

2. **`test_delib_tracker_tool_response_dict_stdout`**: `tool_response` is `{"stdout": "...", "stderr": "", "exitCode": 0, "success": true}` (Bash runtime shape) → tracker extracts stdout, records with correct result_count and delib_ids.

3. **`test_delib_tracker_tool_response_failure_not_recorded`**: `tool_response` dict with error stdout and `exitCode: 1` → tracker does NOT record (failed search cannot satisfy gate).

4. **`test_delib_tracker_tool_response_overrides_tool_output`**: Both `tool_response` (valid) and `tool_output` (error string) present → tracker uses `tool_response`, ignoring `tool_output`. Proves priority ordering.

5. **`test_delib_tracker_e2e_tool_response_gate_lifecycle`**: Full gate→tracker→gate lifecycle using documented `PostToolUse` payload with `tool_response` dict shape plus `tool_use_id`. Gate warns → tracker records from `tool_response.stdout` → gate passes on topical match.

**Existing `tool_output` tests retained** as backward-compatibility coverage (they remain relevant for any environment or wrapper that passes `tool_output` instead of `tool_response`).

---

## Test Results

```
Focused: 91 passed in 95.00s (test_governance_hooks + test_scaffold_settings + test_intake)
Full suite: 965 passed in 246.57s
ruff check: All checks passed!
ruff format: 96 files already formatted
```

New tests added since `-016`: 5 (string tool_response + dict stdout tool_response + failure not recorded + priority override + full lifecycle).

Total new tests across `-012` through `-018`: 16.

## Exit Criteria Checklist (revised from `-016`)

| # | Criterion | Status |
|---|-----------|--------|
| 1 | All 8 hook files implemented | PASS — 6 new + 2 ported |
| 2 | `governance.output` and `governance.mutation` modules tested | PASS |
| 3 | All tests pass | PASS — 965 passed |
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
| 18 | Same bridge doc, different topic → gate warns (topic discrimination) | PASS |
| 19 | Failed/error searches not recorded; cannot satisfy gate | PASS |
| 20 | Empty tool_output not recorded; cannot satisfy gate | PASS |
| 21 | Log entries include: search_success, result_count, delib_ids, source_event, search_topics | PASS |
| 22 | Gate rejects entries with search_success=False | PASS |
| 23 | **Tracker reads `tool_response` as primary PostToolUse result field** | PASS |
| 24 | **`tool_response` string shape produces correct log entry** | PASS |
| 25 | **`tool_response` dict/stdout shape (Bash runtime) produces correct log entry** | PASS |
| 26 | **Failed `tool_response` not recorded (runtime negative test)** | PASS |
| 27 | **`tool_response` takes priority over `tool_output` when both present** | PASS |
| 28 | **Full gate lifecycle using documented `tool_response` payload shape** | PASS |

## Files Changed (since `-016`)

| File | Change |
|------|--------|
| `templates/hooks/delib-search-tracker.py` | Added `_extract_tool_output()` adapter: reads `tool_response` (string or dict with stdout/output/text/content) as primary, falls back to `tool_output`/`output` for legacy compat. Updated `main()` to call the adapter. |
| `tests/test_governance_hooks.py` | +5 new tests covering `tool_response` string, dict/stdout, failure, priority override, and full gate lifecycle with runtime payload shape |

## Not Implemented (deferred per C4)

- Agent Red `.gitignore` modification (requires Mike's explicit file-specific approval).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
