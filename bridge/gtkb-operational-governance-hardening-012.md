# GT-KB Operational Governance Hardening — Post-Implementation Report

**Status:** NEW (post-implementation report for Codex verification)
**Prime Builder:** Claude Opus 4.6
**Session:** S296
**Implements:** Proposal `-009` (GO at `-010`, supersedes prior incomplete `-011`)
**Repository:** `groundtruth-kb` (main branch, uncommitted pending verification)

---

## Summary

Phase 1 of operational governance hardening is fully implemented. All 8 hooks (6 new + 2 ported), 2 governance modules, schema migration, scaffold updates, and 86 new tests are in place. All 391 tests pass (0 regressions). Ruff clean.

## Implementation Conditions Addressed

### C1 — `source_paths` public API explicit

- Added `source_paths: list[str] | None = None` as explicit keyword on `insert_spec()` at `db.py:545`.
- Stored as JSON-encoded TEXT column via `json.dumps(source_paths)`.
- 4 migration tests added to `tests/test_db.py::TestSourcePathsMigration`: fresh DB, idempotent reopen, insert without source_paths, insert with source_paths.
- `test_spec_before_code_match_via_migrated_db` uses real `KnowledgeDB` (not mock) — proves schema works end-to-end.

### C2 — Structured deny and exit-code blocking separate

- All deny hooks use structured path: `emit_deny()` → exit 0.
- No hook emits deny JSON and exits 2.
- `test_destructive_gate_stdin_blocks` and `test_credential_scan_stdin_blocks` both assert exit 0 + `permissionDecision: "deny"`.
- `test_destructive_gate_env_ignored` proves `TOOL_INPUT` env var is no longer read — clean stdin + malicious env var → no block.

### C3 — Test contract covers prior failures

All test groups from `-009` implemented:
- **Governance hook tests** (`tests/test_governance_hooks.py`): 57 tests covering all 8 hooks, self-test validation, stdin payloads, bridge compliance parsing, deliberation search gate, spec-before-code, kb-not-markdown, session governance.
- **Mutation classifier tests** (`tests/test_governance_mutation.py`): 19 tests covering all 16 MUTATION_PATTERNS including Ruby, plus `is_source_path`.
- **Scaffold settings tests** (`tests/test_scaffold_settings.py`): 6 tests for settings.json generation, settings.local.json, .gitignore coverage, nested hook schema.
- **Migration tests** (in `tests/test_db.py`): 4 tests for source_paths column.
- **Spec-before-code via migrated DB** (`test_spec_before_code_match_via_migrated_db`): uses real `KnowledgeDB`, not mocked schema.

### C4 — File-safety boundaries

No Agent Red files were modified. All implementation is in `groundtruth-kb`. The Agent Red `.gitignore` edit mentioned in `-009:498` was deferred — `.groundtruth/` ignore is handled in generated project `.gitignore` via `bootstrap.py:DEFAULT_PROJECT_GITIGNORE`.

## Files Changed

### New files (groundtruth-kb)

| File | Purpose | Lines |
|------|---------|-------|
| `src/groundtruth_kb/governance/__init__.py` | Package init | 2 |
| `src/groundtruth_kb/governance/output.py` | Canonical hook output builder (emit_additional_context, emit_ask, emit_deny, emit_pass, read_hook_payload) | 98 |
| `src/groundtruth_kb/governance/mutation.py` | Bash command mutation classifier (16 patterns, classify_bash_command, is_source_path) | 56 |
| `templates/hooks/delib-search-gate.py` | UserPromptSubmit: deliberation search advisory | 111 |
| `templates/hooks/delib-search-tracker.py` | PostToolUse: records deliberation searches to JSONL log | 88 |
| `templates/hooks/spec-before-code.py` | PreToolUse: spec coverage advisory for source files | 134 |
| `templates/hooks/bridge-compliance-gate.py` | PreToolUse: bridge proposal compliance gate (latest-status parser) | 142 |
| `templates/hooks/kb-not-markdown.py` | PreToolUse: KB-not-markdown advisory | 101 |
| `templates/hooks/session-start-governance.py` | SessionStart: governance status summary | 97 |
| `templates/project/settings.json` | Generated settings with all 8 governance hooks | 45 |
| `tests/test_governance_hooks.py` | 57 hook integration tests | ~600 |
| `tests/test_governance_mutation.py` | 19 mutation classifier tests | 83 |
| `tests/test_scaffold_settings.py` | 6 scaffold settings tests | 70 |

### Modified files (groundtruth-kb)

| File | Change |
|------|--------|
| `src/groundtruth_kb/db.py` | Migration 3: `source_paths` column (PRAGMA-guard); `insert_spec()` gains `source_paths: list[str] \| None` kwarg |
| `src/groundtruth_kb/bootstrap.py` | `DEFAULT_PROJECT_GITIGNORE` adds `.groundtruth/` and `.claude/settings.local.json` |
| `src/groundtruth_kb/project/scaffold.py` | `_copy_dual_agent_templates()` copies `settings.json` (tracked) + `settings.local.json` (untracked); adds `.groundtruth/` to generated `.gitignore` |
| `templates/hooks/destructive-gate.py` | Ported from `TOOL_INPUT` env var to stdin; exit 2 → structured deny (exit 0 + JSON); `--self-test` added |
| `templates/hooks/credential-scan.py` | Same portation as destructive-gate; `--self-test` added |
| `templates/project/settings.local.json` | Stripped hooks (moved to settings.json); now contains only permissions |
| `.gitignore` | Added `.groundtruth/` |
| `tests/test_db.py` | Added `TestSourcePathsMigration` class (4 tests) |

## Test Results

```
391 passed in 25.77s
ruff check: All checks passed!
ruff format: All files already formatted
```

New tests added: 86 (57 hooks + 19 mutation + 6 scaffold + 4 migration).
Prior test count: 305. New total: 391. No regressions.

## Exit Criteria Checklist

| # | Criterion | Status |
|---|-----------|--------|
| 1 | All 8 hook files implemented | PASS — 6 new + 2 ported |
| 2 | `governance.output` and `governance.mutation` modules tested | PASS |
| 3 | All tests pass | PASS — 391/391 |
| 4 | `--self-test` all 8 hooks exit 0 with hookSpecificOutput + hookEventName | PASS |
| 5 | `ask` gate tests assert both permissionDecisionReason and additionalContext | PASS |
| 6 | destructive-gate + credential-scan block on stdin (exit 0 + JSON deny), ignore TOOL_INPUT env | PASS |
| 7 | `gt project init --profile dual-agent` generates `.claude/settings.json` with all 8 hooks | PASS |
| 8 | Generated `.gitignore` includes `.groundtruth/` and `.claude/settings.local.json` | PASS |
| 9 | Each S295 violation produces advisory or ask checkpoint | PASS |
| 10 | All MUTATION_PATTERNS covered by tests (including Ruby) | PASS |
| 11 | source_paths migration passes fresh + idempotent; spec-before-code uses real KnowledgeDB | PASS |

## Not Implemented (deferred per C4)

- Agent Red `.gitignore` modification (requires Mike's explicit file-specific approval).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
