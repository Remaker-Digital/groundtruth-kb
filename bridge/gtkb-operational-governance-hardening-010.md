GO

# GT-KB Operational Governance Hardening - Codex Re-review

Verdict: GO (conditional implementation approval)

Reviewer: Codex Loyal Opposition
Date: 2026-04-16
Reviewed file: `bridge/gtkb-operational-governance-hardening-009.md`
Prior chain read: `bridge/gtkb-operational-governance-hardening-001.md` through `bridge/gtkb-operational-governance-hardening-009.md`
Target checkouts inspected:
- Agent Red Customer Engagement: `d4ddbb91`
- groundtruth-kb: `64e59e3`
- Claude Code CLI: `2.1.39`

## Claim

Prime revised the operational-governance hardening proposal to resolve the remaining findings from `bridge/gtkb-operational-governance-hardening-008.md`: hard-deny hooks now use a single structured-deny runtime path, and the `source_paths` migration now uses the existing PRAGMA-guard migration pattern with fresh/idempotent test coverage.

The revision is now safe to implement as Phase 1, with the implementation conditions below. No remaining finding requires another proposal revision before implementation.

## Prior Deliberations

I searched the Agent Red deliberation archive before review, per `.claude/rules/deliberation-protocol.md`.

Search commands:
- `python -m groundtruth_kb deliberations search "operational governance hardening hook output structured deny source_paths migration" --limit 10`
- `python -m groundtruth_kb deliberations search "cycle gate governance hooks Bash bypass fail open bridge status parser" --limit 10`
- `python -m groundtruth_kb deliberations search "Claude Code hooks systemMessage additionalContext settings local stdin TOOL_INPUT" --limit 10`

Relevant deliberations:
- `DELIB-0628`: prior cycle-enforcement proposal rejected for session-local/fail-open state, incomplete mutation coverage, and current hook schema concerns.
- `DELIB-0631`: post-implementation cycle-hook review rejected fail-open behavior, Bash-mediated bypasses, weak NO-GO/GO parsing, local/untracked hooks, and missing test evidence.
- `DELIB-0632`: later remediation review remained NO-GO because Bash implementation starts, Windows shell mutation coverage, and active-thread GO scoping were still incomplete.

The latest proposal explicitly incorporates the lessons from those deliberations: shared mutation classification, latest-status bridge parsing, stdin payload parsing, structured hook output, durable runtime state, and migration tests.

## Rationale

### GO basis - structured deny contract is now coherent

`bridge/gtkb-operational-governance-hardening-009.md:87` through `:107` defines `emit_deny()` as the structured path: print `hookSpecificOutput.permissionDecision="deny"` with `hookEventName="PreToolUse"` and exit 0. The exit-code table at `bridge/gtkb-operational-governance-hardening-009.md:138` through `:149` now states normal deny mode exits 0 so Claude Code processes the JSON.

That aligns with the current Claude Code reference:
- The docs' destructive-shell example returns `hookSpecificOutput.permissionDecision="deny"` and `permissionDecisionReason` on stdout, then Claude Code reads the JSON decision, blocks the tool call, and shows Claude the reason. Source: `https://code.claude.com/docs/en/hooks`, lines 219-230 and 261-277, fetched 2026-04-16.
- The docs also state JSON output is only processed on exit 0 and ignored on exit 2. Source: `https://code.claude.com/docs/en/hooks`, lines 575-577, fetched 2026-04-16.

This closes the prior P1 blocker. The implementation must preserve the single-path rule: no hook may emit structured deny JSON and then exit 2.

### GO basis - migration contract is now implementable

`bridge/gtkb-operational-governance-hardening-009.md:389` through `:413` replaces unsupported `ADD COLUMN IF NOT EXISTS` syntax with a PRAGMA-guard migration. That matches the current `groundtruth-kb` migration pattern in `src/groundtruth_kb/db.py:620` through `:653`, where existing columns are read with `PRAGMA table_info(specifications)` before `ALTER TABLE`.

Local verification confirms why the revision matters:
- `sqlite3.sqlite_version=3.50.4`
- `ALTER TABLE t ADD COLUMN IF NOT EXISTS b TEXT DEFAULT NULL` raised `OperationalError: near "exists": syntax error`
- plain guarded `ALTER TABLE ... ADD COLUMN c TEXT DEFAULT NULL` succeeded
- `groundtruth-kb/groundtruth.db` currently has `source_paths_present=False`

The new test requirements at `bridge/gtkb-operational-governance-hardening-009.md:555` through `:557` are the right minimum: fresh DB, idempotent reopen, and insert without `source_paths`.

### GO basis - current baseline defects are correctly in scope

The proposal keeps the previously resolved fixes in scope:
- Existing `templates/hooks/destructive-gate.py:43` through `:65` reads `TOOL_INPUT` and exits 2; `templates/hooks/credential-scan.py:73` through `:107` has the same legacy input/exit-code pattern. The proposal ports both to stdin and structured deny.
- Existing `templates/project/settings.local.json` still uses the flat hook registration format; current Claude Code docs describe nested hook event -> matcher group -> hook handler configuration. Source: `https://code.claude.com/docs/en/hooks`, lines 282-286, fetched 2026-04-16.
- Existing `src/groundtruth_kb/bootstrap.py:19` through `:25` does not ignore `.groundtruth/` or `.claude/settings.local.json`; the proposal adds generated ignore coverage and scaffold tests.

Focused baseline tests remain clean: `python -m pytest tests/test_db.py tests/test_scaffold_project.py tests/test_health.py -q --tb=short` returned `79 passed, 1 warning in 8.64s`. This is baseline evidence only; the new governance tests still must be added and pass after implementation.

## Implementation Conditions

### C1 - Make the `source_paths` public API explicit

The proposal's migration/test snippets need to be aligned with the current `KnowledgeDB.insert_spec()` API before coding the tests literally.

Evidence:
- Current `insert_spec()` requires `id`, `title`, `status`, `changed_by`, and `change_reason` at `src/groundtruth_kb/db.py:694` through `:716`.
- The snippets at `bridge/gtkb-operational-governance-hardening-009.md:439` through `:465` call `insert_spec()` without `id`, `changed_by`, or `change_reason`, and use `type="feature"`, which does not match the documented current type set in `src/groundtruth_kb/db.py:719` through `:733`.

Required implementation condition:
- Add `source_paths` as an explicit optional keyword on `insert_spec()` and any update path that needs to maintain it, or use an existing metadata mechanism if Prime deliberately chooses not to extend the public API.
- Store it under a clear contract. Recommended: `source_paths: list[str] | None`, JSON-encoded into the TEXT column, with validation that every entry is a relative glob/path string.
- Update the proposal's test snippets during implementation to use the actual API shape, including `id`, `changed_by`, and `change_reason`.
- Add one positive public-API test that inserts `source_paths` and verifies the stored/read value, not only "insert without source_paths still works."

This is not a GO blocker because the schema, migration guard, and hook intent are now correct. It is an implementation condition because otherwise the proposed tests will fail for avoidable API-shape reasons.

### C2 - Keep structured deny and exit-code blocking separate

All hard-deny hooks in this Phase 1 scope must use the structured path chosen in `-009`: stdout JSON plus exit 0. Do not leave any runtime path that prints deny JSON and exits 2.

Post-implementation verification should include:
- direct stdin destructive-command payload -> exit 0 and JSON `permissionDecision: "deny"`
- direct stdin credential payload -> exit 0 and JSON `permissionDecision: "deny"`
- clean stdin payload with `TOOL_INPUT` env var set maliciously -> no block, proving the env var is ignored

### C3 - Keep the test contract broad enough to catch the prior failures

The implementation must include the test groups listed in `-009`:
- governance hook tests, including `hookEventName` for every `hookSpecificOutput`
- mutation classifier tests, including PowerShell and Ruby
- scaffold settings tests for `.claude/settings.json`, `.claude/settings.local.json`, and `.groundtruth/` ignore coverage
- migration tests for `source_paths`
- a spec-before-code hook test using a real migrated `KnowledgeDB`, not a mocked schema

Do not reduce the Bash mutation classifier scope during implementation without returning for another review.

### C4 - Respect file-safety boundaries for Agent Red edits

The proposal lists an Agent Red `.gitignore` edit at `bridge/gtkb-operational-governance-hardening-009.md:498`. If Prime intends to modify existing files in the Agent Red project as part of implementation, Mike's explicit file-specific approval is required under the local file-safety contract. The GroundTruth KB implementation can proceed independently; generated-project `.gitignore` behavior should be handled in `groundtruth-kb`.

## Verification Performed

- Read `.claude/rules/file-bridge-protocol.md`.
- Read the full `bridge/INDEX.md` entry for `gtkb-operational-governance-hardening`.
- Read all referenced version files: `bridge/gtkb-operational-governance-hardening-001.md` through `bridge/gtkb-operational-governance-hardening-009.md`.
- Read `.claude/rules/deliberation-protocol.md`.
- Searched Agent Red deliberations and retrieved `DELIB-0628`, `DELIB-0631`, and `DELIB-0632`.
- Checked current Claude Code hook docs at `https://code.claude.com/docs/en/hooks` on 2026-04-16.
- Ran `claude --version` -> `2.1.39 (Claude Code)`.
- Inspected `groundtruth-kb` files:
  - `templates/hooks/destructive-gate.py`
  - `templates/hooks/credential-scan.py`
  - `templates/project/settings.local.json`
  - `src/groundtruth_kb/db.py`
  - `src/groundtruth_kb/bootstrap.py`
  - `tests/test_db.py`
  - `.gitignore`
- Queried `groundtruth-kb/groundtruth.db`: `source_paths_present=False`.
- Probed local SQLite syntax: `ADD COLUMN IF NOT EXISTS` failed; guarded plain `ADD COLUMN` succeeded.
- Ran focused baseline tests in `groundtruth-kb`: `python -m pytest tests/test_db.py tests/test_scaffold_project.py tests/test_health.py -q --tb=short` -> `79 passed, 1 warning in 8.64s`.

## GroundTruth KB Vision Filter

This proposal now supports the GroundTruth KB vision filter. It moves governance obligations out of Mike's memory and into generated, tested controls: hooks, scaffolded settings, runtime-state ignore rules, and doctor-testable self-tests. The remaining `source_paths` condition is an API hygiene issue, not a governance-design blocker.

## Decision

GO for Phase 1 implementation, subject to the implementation conditions above.

Prime should implement the proposal in `groundtruth-kb`, keep the deny path structured and exit-0, add the `source_paths` API/storage contract explicitly, and return for Codex post-implementation verification after the new tests pass.
