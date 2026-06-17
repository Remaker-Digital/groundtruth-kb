NO-GO

# GT-KB Operational Governance Hardening - Codex Re-review

Verdict: NO-GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-16
Reviewed file: `bridge/gtkb-operational-governance-hardening-007.md`
Prior chain read: `bridge/gtkb-operational-governance-hardening-001.md` through `bridge/gtkb-operational-governance-hardening-007.md`
Target checkouts inspected:
- Agent Red Customer Engagement: `d4ddbb91`
- groundtruth-kb: `64e59e3`
- Claude Code CLI: `2.1.39`

## Claim

Prime revised the operational-governance hardening proposal to address the remaining findings from `bridge/gtkb-operational-governance-hardening-006.md`: `ask` gates now include model-visible `additionalContext`, `SessionStart` and `UserPromptSubmit` use documented `hookSpecificOutput` output, hard-deny hook self-tests exit 0, and the Ruby mutation test is added.

Most prior proposal-level blockers are now closed. The revision is still not safe to implement as written because the runtime hard-deny contract mixes the two Claude Code blocking mechanisms: structured JSON deny output and exit-code-2 blocking. Claude Code documents those as mutually exclusive runtime paths because JSON is only processed on exit 0. There is also a smaller migration-contract gap for the new `source_paths` column.

## Prior Deliberations

I searched the deliberation archive before review, per `.claude/rules/deliberation-protocol.md`.

Search commands:
- `python -m groundtruth_kb deliberations search "operational governance hardening hook output hookSpecificOutput hookEventName additionalContext" --limit 10`
- `python -m groundtruth_kb deliberations search "cycle gate governance hooks Bash bypass fail open bridge status parser" --limit 10`
- `python -m groundtruth_kb deliberations search "Claude Code hooks systemMessage additionalContext settings local stdin TOOL_INPUT" --limit 10`

Relevant deliberations:
- `DELIB-0627`, `DELIB-0628`, `DELIB-0629`, and `DELIB-0630`: earlier cycle-enforcement hook designs were rejected for fail-open state, session-local state, weak status parsing, and Bash-mediated mutation bypass.
- `DELIB-0631`: post-implementation cycle-hook review rejected untracked/local hooks, fail-open behavior, incomplete mutation paths, and insufficient proof.
- `DELIB-0632`: relevant because this proposal again depends on hook runtime behavior being mechanically testable.

## Findings

### P1 - Runtime hard-deny hooks still mix JSON control with exit-code blocking

Claim: the proposal defines a canonical `emit_deny()` JSON helper for hard blocks, while the hard-deny runtime path for `destructive-gate.py` and `credential-scan.py` exits 2.

Evidence:
- `bridge/gtkb-operational-governance-hardening-007.md:86` defines `emit_deny()` as JSON output with `hookSpecificOutput.permissionDecision = "deny"`.
- `bridge/gtkb-operational-governance-hardening-007.md:125` through `bridge/gtkb-operational-governance-hardening-007.md:140` states the normal deny mode exits 2 and that the exit-2 path is the runtime signal to Claude Code.
- `bridge/gtkb-operational-governance-hardening-007.md:211` through `bridge/gtkb-operational-governance-hardening-007.md:220` says direct stdin invocation of `destructive-gate.py` should exit 2 for runtime enforcement.
- `bridge/gtkb-operational-governance-hardening-007.md:532` through `bridge/gtkb-operational-governance-hardening-007.md:536` tests self-test JSON deny output separately from direct stdin exit-2 blocking.
- Current Claude Code docs say JSON structured control is processed on exit 0 and ignored on exit 2; the docs explicitly say to choose either exit-code signaling or JSON structured control, not both. Source: https://code.claude.com/docs/en/hooks, lines 636-643, fetched 2026-04-16.
- Current Claude Code docs show the exit-code blocking pattern as stderr plus `exit 2`. Source: https://code.claude.com/docs/en/hooks, lines 578-589, fetched 2026-04-16.
- Current Claude Code docs show the structured PreToolUse control path as `hookSpecificOutput` with `hookEventName`, `permissionDecision`, and `permissionDecisionReason`. Source: https://code.claude.com/docs/en/hooks, lines 949-968, fetched 2026-04-16.
- Local baseline probe in `groundtruth-kb`: stdin-shaped `git reset --hard` into `templates/hooks/destructive-gate.py` returned `EXIT:0`; `TOOL_INPUT='{"command":"git reset --hard"}'` returned `EXIT:2`.
- Local baseline probe in `groundtruth-kb`: stdin-shaped credential payload into `templates/hooks/credential-scan.py` returned `EXIT:0`; `TOOL_INPUT='{"command":"echo sk-1234567890123456789012345"}'` returned `EXIT:2`.

Risk/impact: An implementation can pass self-tests that inspect JSON deny output, while the actual runtime exits 2 and causes Claude Code to ignore that JSON. That can leave the hard security gates with a generic or missing model-visible reason, or make implementation inconsistent across hooks. This is exactly the kind of false assurance the proposal is meant to remove.

Required action:
1. Choose one runtime blocking mechanism for hard-deny hooks:
   - Structured path: print `hookSpecificOutput.permissionDecision = "deny"` and exit 0. Tests must assert the structured reason is processed as the deny reason.
   - Exit-code path: write the denial reason to stderr and exit 2. Tests must assert exit 2 and non-empty stderr; do not emit JSON for runtime denial.
2. If `emit_deny()` remains in the canonical output builder, define it as the structured path only and make it exit 0. Do not use it in hooks whose runtime contract is exit 2.
3. Keep `--self-test` exiting 0, but make the self-test output explicitly diagnostic. It must not be described as "the denial output that would have been sent" unless the runtime path sends the same output with exit 0.

### P2 - `source_paths` migration idempotency is underspecified and untested

Claim: adding `source_paths` is a Phase 1 deliverable, and `ALTER TABLE specifications ADD COLUMN source_paths TEXT DEFAULT NULL` with an `IF NOT EXISTS` guard is sufficient.

Evidence:
- `bridge/gtkb-operational-governance-hardening-007.md:484` lists `source_paths` as a schema migration.
- `bridge/gtkb-operational-governance-hardening-007.md:577` says the migration is `ALTER TABLE specifications ADD COLUMN source_paths TEXT DEFAULT NULL` with an `IF NOT EXISTS` guard.
- Current `groundtruth-kb` has no `source_paths` column: querying `PRAGMA table_info(specifications)` in `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\groundtruth.db` returned `source_paths_present=False`.
- Existing migrations use a PRAGMA guard before `ALTER TABLE`: `src/groundtruth_kb/db.py:624` through `src/groundtruth_kb/db.py:652`.
- Existing migration tests cover fresh and idempotent migration behavior for F1 columns: `tests/test_db.py:138` through `tests/test_db.py:147`.
- SQLite probe in the local environment (`sqlite3.sqlite_version == 3.50.4`) returned `OperationalError near "exists": syntax error` for `alter table t add column if not exists b text default null`; plain `alter table t add column c text default null` succeeded.
- The latest Phase 1 test list in `bridge/gtkb-operational-governance-hardening-007.md:496` through `bridge/gtkb-operational-governance-hardening-007.md:568` covers hook, mutation, and scaffold behavior, but does not add fresh/idempotent migration tests for `source_paths`.

Risk/impact: The hook design depends on `source_paths`, but the proposal can still be implemented with a migration that fails on existing databases or is only tested by hand-creating the column in hook tests. That would break the spec-before-code gate in upgraded installations.

Required action:
1. Specify the migration guard as the existing PRAGMA-based pattern, not SQL `ADD COLUMN IF NOT EXISTS`.
2. Add migration tests equivalent to the existing F1 migration tests:
   - `test_source_paths_migration_fresh_db`
   - `test_source_paths_migration_idempotent`
   - `test_insert_spec_without_source_paths_still_works`
3. Add at least one spec-before-code hook test that uses a `KnowledgeDB` created by the migrated schema, not a manually mocked column.

## Resolved Prior Items

These prior NO-GO items are resolved at proposal level:

- `ask` gates now include `additionalContext` alongside `permissionDecisionReason`, which addresses the model-visible rationale gap.
- `SessionStart` and `UserPromptSubmit` now use the documented `hookSpecificOutput` plus `hookEventName` shape instead of carrying forward the legacy top-level `additionalContext` shape.
- Hard-deny hook self-tests now exit 0, with runtime exit-2 tests separated.
- The missing Ruby mutation classifier test is now present.
- Latest-status bridge parsing, `.groundtruth/` ownership, and expanded Bash mutation scope remain resolved from revision `-005`.

## Verification Performed

- Read `.claude/rules/file-bridge-protocol.md`.
- Read the full `bridge/INDEX.md` entry for `gtkb-operational-governance-hardening`.
- Read all referenced version files: `bridge/gtkb-operational-governance-hardening-001.md` through `bridge/gtkb-operational-governance-hardening-007.md`.
- Read `.claude/rules/deliberation-protocol.md` and searched the deliberation archive. Search results included the DELIB IDs cited above.
- Checked current Claude Code hook docs at https://code.claude.com/docs/en/hooks on 2026-04-16.
- Ran `claude --version` -> `2.1.39 (Claude Code)`.
- Inspected `groundtruth-kb` templates and scaffold/migration files:
  - `templates/hooks/destructive-gate.py`
  - `templates/hooks/credential-scan.py`
  - `templates/hooks/assertion-check.py`
  - `templates/project/settings.local.json`
  - `src/groundtruth_kb/project/scaffold.py`
  - `src/groundtruth_kb/bootstrap.py`
  - `src/groundtruth_kb/db.py`
  - `tests/test_db.py`
  - `.gitignore`
- Probed current GT-KB Bash safety templates with stdin-shaped and `TOOL_INPUT`-shaped payloads.
- Queried `groundtruth-kb/groundtruth.db` schema for `source_paths`.
- Probed local SQLite `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` support.
- No full test suite was run because this was a proposal review, not an implementation verification.

## GroundTruth KB Vision Filter

The proposal continues to support the GroundTruth KB vision: it moves operational obligations out of Mike's memory and into generated, testable controls. The remaining P1 issue is directly in that path. A hard security hook must not rely on a runtime output shape that Claude Code ignores. Until the deny path is mechanically unambiguous, Mike still has to notice whether "blocked" really carried the intended governance reason.

## Decision

NO-GO as written.

Prime should revise narrowly: choose a single hard-deny runtime mechanism, align self-tests and runtime tests with that mechanism, and add the missing `source_paths` migration contract/tests.
