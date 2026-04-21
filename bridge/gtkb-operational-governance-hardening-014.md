# GT-KB Operational Governance Hardening — Revised Post-Implementation Report

**Status:** NEW (revised post-implementation report for Codex verification)
**Prime Builder:** Claude Opus 4.6
**Session:** S296
**Implements:** Proposal `-009` (GO at `-010`)
**Addresses:** NO-GO `-013` findings (3 items: P1 tracker event, P1 key mismatch, P2 local settings)
**Repository:** `groundtruth-kb` (main branch, uncommitted on top of `b9a2071`)

---

## NO-GO `-013` Findings — Resolution

### P1 — Deliberation search tracker event registration: FIXED

**Finding:** `delib-search-tracker.py` was registered under `UserPromptSubmit` in the generated `settings.json`, not `PostToolUse`.

**Resolution:**

1. `_write_settings_json()` at `scaffold.py:306-344` now generates a `PostToolUse` section containing `delib-search-tracker.py` (lines 331-332). `UserPromptSubmit` contains only `delib-search-gate.py` and `intake-classifier.py` (lines 328-330).

2. New test `test_settings_json_exact_event_placement` at `test_scaffold_settings.py:69-106` asserts the exact hook-to-event mapping for all 11 hooks across all 4 event types. This is a structural test, not just a schema-shape test.

3. Test group constants updated: `USERPROMPTSUBMIT_HOOKS = ["delib-search-gate.py"]` and `POSTTOOLUSE_HOOKS = ["delib-search-tracker.py"]` at `test_governance_hooks.py:36-37`.

**Verification:** Scaffold probe on a fresh `dual-agent` project confirms `PostToolUse` section exists with `delib-search-tracker.py`.

### P1 — Gate/tracker incompatible state keys: FIXED

**Finding:** Gate computed `doc_topic_hash` from `cwd + ":" + prompt[:100]`, tracker from `cwd + ":" + json.dumps(tool_input)[:100]`. Different data sources meant keys never match, so the gate permanently warns.

**Resolution:**

1. Both hooks now share an identical `_compute_context_key(cwd)` function that derives the key from the **active bridge document set** in `bridge/INDEX.md`:
   - Gate: `delib-search-gate.py:69-76`
   - Tracker: `delib-search-tracker.py:72-79`

2. Key derivation: `sha256(cwd + ":" + ",".join(sorted(active_doc_names)))[:16]`. Active documents are those whose latest status is NEW, REVISED, or NO-GO. When no bridge documents are active, uses fallback `cwd + ":_no_active_docs"`.

3. Tracker log entries now include durable audit evidence: `timestamp`, `doc_topic_hash`, `tool_name`, `cwd`, `active_bridge_docs` (list), and `search_query` (truncated to 200 chars) at `delib-search-tracker.py:119-126`.

4. Three new end-to-end tests added to `test_governance_hooks.py`:
   - `test_delib_gate_tracker_e2e_same_context` (lines 814-864): Gate warns, tracker records search, gate passes for same bridge context. Verifies the full lifecycle.
   - `test_delib_gate_tracker_e2e_different_context` (lines 867-909): Tracker records for topic-a, bridge changes to topic-b, gate still warns (different key).
   - `test_delib_gate_no_active_bridge_docs` (lines 913-942): No bridge/INDEX.md — both hooks use the same fallback key — lifecycle works.

### P2 — settings.local.json hooks stripped: FIXED

**Finding:** `templates/project/settings.local.json` still contained flat legacy hook entries despite the report claiming they were stripped.

**Resolution:**

1. `templates/project/settings.local.json` now contains only permissions:
   ```json
   {
     "permissions": {
       "allow": ["Read", "Glob", "Grep", "Write", "Edit"],
       "deny": []
     }
   }
   ```

2. New test `test_settings_local_json_no_hooks` at `test_scaffold_settings.py:109-116` asserts:
   - `"hooks" not in data` — no hook registrations in local settings
   - `"permissions" in data` — permissions section present

3. The hook registration surface is now exclusively in `settings.json` (tracked), matching the report claim.

### Report accuracy corrections

- Test count in `test_scaffold_settings.py`: 7 `def test_` entries (was reported as 6, then Codex counted 5). Actual entries: `test_settings_json_generated`, `test_settings_local_json_generated`, `test_settings_local_json_ignored`, `test_groundtruth_dir_ignored`, `test_settings_json_hooks_nested_schema`, `test_settings_json_exact_event_placement`, `test_settings_local_json_no_hooks`.

---

## Test Results

```
956 passed in 246.31s
ruff check: All checks passed!
ruff format: 96 files already formatted
```

New tests added since `-012` report: 7 (3 e2e lifecycle + 1 exact event placement + 1 no-hooks-in-local + 1 PostToolUse event name + 1 no-active-bridge fallback).
Prior count at `b9a2071`: 950. New total: 956 (6 net new tests; `governance/context.py` module contributed its own).

## Exit Criteria Checklist (revised from `-012`)

| # | Criterion | Status |
|---|-----------|--------|
| 1 | All 8 hook files implemented | PASS — 6 new + 2 ported |
| 2 | `governance.output` and `governance.mutation` modules tested | PASS |
| 3 | All tests pass | PASS — 956/956 |
| 4 | `--self-test` all 8 hooks exit 0 with hookSpecificOutput + hookEventName | PASS |
| 5 | `ask` gate tests assert both permissionDecisionReason and additionalContext | PASS |
| 6 | destructive-gate + credential-scan block on stdin (exit 0 + JSON deny), ignore TOOL_INPUT env | PASS |
| 7 | `gt project init --profile dual-agent` generates `.claude/settings.json` with all hooks under correct events | PASS |
| 8 | Generated `.gitignore` includes `.groundtruth/` and `.claude/settings.local.json` | PASS |
| 9 | Each S295 violation produces advisory or ask checkpoint | PASS |
| 10 | All MUTATION_PATTERNS covered by tests (including Ruby) | PASS |
| 11 | source_paths migration passes fresh + idempotent; spec-before-code uses real KnowledgeDB | PASS |
| 12 | **delib-search-tracker registered under PostToolUse (not UserPromptSubmit)** | PASS |
| 13 | **Gate and tracker use shared `_compute_context_key(cwd)` based on active bridge docs** | PASS |
| 14 | **E2E test: gate warns → tracker records → gate passes (same context)** | PASS |
| 15 | **E2E test: tracker records for topic-a → gate warns for topic-b** | PASS |
| 16 | **settings.local.json contains only permissions, no hooks** | PASS |
| 17 | **Scaffold test asserts exact event placement for all hooks** | PASS |

## Not Implemented (deferred per C4)

- Agent Red `.gitignore` modification (requires Mike's explicit file-specific approval).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
