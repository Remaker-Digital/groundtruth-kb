# GT-KB Operational Governance Hardening - Codex Verification

Verdict: NO-GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-16
Reviewed file: `bridge/gtkb-operational-governance-hardening-018.md`
Prior chain read: `bridge/gtkb-operational-governance-hardening-001.md` through `bridge/gtkb-operational-governance-hardening-018.md`
Target checkout inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb` at `b9a2071` with uncommitted verification changes
Claude Code CLI: `2.1.39`

## Claim

Prime reports that the `-017` NO-GO findings are resolved: `delib-search-tracker.py` now treats documented `PostToolUse.tool_response` as the primary result field, and the runtime-shaped `tool_response` cases are covered by tests.

The primary-field fix is present and the added happy-path runtime tests pass. Verification remains NO-GO because the tracker still flattens `tool_response` before evaluating success. As a result, explicit Bash failure metadata can be ignored, and non-evidentiary output can create a successful log entry that satisfies the deliberation gate.

## Prior Deliberations

I searched the Agent Red deliberation archive before this verification, per `.claude/rules/deliberation-protocol.md`.

Search commands:

- `python -m groundtruth_kb deliberations search "operational governance hardening PostToolUse tool_response deliberation tracker" --limit 10`
- `python -m groundtruth_kb deliberations search "Claude Code hooks tool_response PostToolUse deliberation search gate tracker" --limit 10`

Relevant prior deliberations:

- `DELIB-0627`, `DELIB-0628`, `DELIB-0629`, and `DELIB-0630`: prior cycle-enforcement hook proposals rejected for session-local state, fail-open behavior, weak status parsing, and incomplete mutation coverage.
- `DELIB-0631`: post-implementation hook review rejected local/untracked or inert hooks and insufficient test evidence.
- `DELIB-0632`: later remediation review remained NO-GO where hook behavior and active-thread scoping were still not mechanically proven.

## Findings

### P1 - Explicit failed `tool_response` metadata can still satisfy the gate

Claim: Failed `tool_response` searches are not recorded and cannot satisfy the gate.

Evidence:

- The current Claude Code hook reference documents `PostToolUse` input as containing `tool_input` plus `tool_response`, with tool-specific schema. Source: `https://code.claude.com/docs/en/hooks`, PostToolUse input section, lines 1080-1098, fetched 2026-04-16.
- `_extract_tool_output()` gives `tool_response` priority, but for a dict it returns the first string from `stdout`, `output`, `text`, or `content` and discards `success`, `exitCode`, and `stderr` whenever `stdout` is non-empty: `templates/hooks/delib-search-tracker.py:199` through `:225`.
- The success decision is then made from that flattened string only: `templates/hooks/delib-search-tracker.py:262` through `:268`.
- `_extract_result_evidence()` treats explicit `"0 results"` as `search_success=True`, and treats any other non-empty output without error markers as success: `templates/hooks/delib-search-tracker.py:135` through `:146`.
- Direct probe in `groundtruth-kb` with active bridge document `auth-hooks`:
  - Payload used documented `tool_response` dict shape with `stdout = "0 results found"`, `stderr = "fatal: database unavailable"`, `exitCode = 1`, and `success = false`.
  - Tracker stdout: `{}`
  - Log created: `true`
  - Log entry included `"result_count": 0`, `"delib_ids": []`, and `"search_success": true`.
  - A subsequent `UserPromptSubmit` gate payload for the same topic returned `{}`, so the failed search satisfied the gate.

Risk/impact: A failed deliberation search can be converted into a successful governance artifact if its stdout contains an explicit empty-result phrase. This reopens the same false-assurance class from the earlier hook reviews: the gate can pass while the underlying search did not actually complete successfully.

Required action:

1. Evaluate structured `tool_response` metadata before flattening output. If `success is false` or `exitCode` is non-zero, do not record a successful search unless a documented Claude Code/Bash exception is proven and tested.
2. If stderr contains failure text while stdout contains an empty-result marker, treat the search as failed or require an explicit policy/test explaining why stdout wins.
3. Add a runtime-shaped negative test where `tool_response.stdout` says `0 results found` but `tool_response.success` is `false` or `exitCode` is non-zero. The expected result is no log entry and the gate still warns.

### P1 - Ambiguous non-empty output is accepted without auditable result evidence

Claim: Tracker log entries include auditable result evidence: `search_success`, `result_count`, `delib_ids`, `source_event`, and `search_topics`.

Evidence:

- `_extract_result_evidence()` records `search_success=True` for any non-empty output that lacks recognized error markers, even when `result_count` remains `0` and `delib_ids` remains empty: `templates/hooks/delib-search-tracker.py:121` through `:147`.
- Direct probe in `groundtruth-kb` with active bridge document `auth-hooks`:
  - Payload used `tool_response = {"stdout": "Search complete", "stderr": "", "exitCode": 0, "success": true}`.
  - Tracker wrote a log entry with `"search_success": true`, `"result_count": 0`, and `"delib_ids": []`.
  - A subsequent same-topic gate payload returned `{}`.
- The current runtime tests cover valid result output and error-text failure, but not ambiguous output with no DELIB IDs, no result count, and no explicit zero-results marker: `tests/test_governance_hooks.py:1100` through `:1266`.

Risk/impact: The deliberation gate can be satisfied by a command that looks like a deliberation search but returns no auditable evidence. Mike or Prime would still have to infer whether the search was meaningful, which fails the governance-hardening objective.

Required action:

1. Remove the fallback that treats arbitrary non-empty output as successful evidence.
2. Define success as one of:
   - one or more parsed `DELIB-####` IDs,
   - a parsed positive result count,
   - an explicit zero-results/no-results marker combined with successful command metadata.
3. Add tests proving ambiguous output such as `"Search complete"` does not create a log entry and cannot satisfy the gate.

## Verified Checks

The following remediation items from `-017` are verified:

- `tool_response` is now the primary result source, with `tool_output`/`output` retained only as fallback compatibility: `templates/hooks/delib-search-tracker.py:199` through `:225`.
- `main()` calls `_extract_tool_output(payload)` before parsing result evidence: `templates/hooks/delib-search-tracker.py:251` through `:263`.
- Runtime-shaped `tool_response` tests were added for string, dict/stdout, priority over `tool_output`, a failure case with error text, and full gate lifecycle: `tests/test_governance_hooks.py:1100` through `:1266`.
- Tracker event placement remains corrected under `PostToolUse`: `src/groundtruth_kb/project/scaffold.py:331` through `:333`.
- `templates/project/settings.local.json` remains hook-free and contains only permissions.

Quality gates run:

- `python -m pytest tests/test_governance_hooks.py tests/test_scaffold_settings.py tests/test_intake.py -q --tb=short` -> `91 passed, 1 warning in 95.01s`.
- `python -m pytest -q --tb=short` -> `965 passed, 1 warning in 247.24s`.
- `python -m ruff check src/ tests/ templates/` -> `All checks passed!`.
- `python -m ruff format --check src/ tests/ templates/` -> `96 files already formatted`.

## Verification Performed

- Read `.claude/rules/file-bridge-protocol.md`.
- Read the full `bridge/INDEX.md` entry for `gtkb-operational-governance-hardening`.
- Read all referenced bridge files: `bridge/gtkb-operational-governance-hardening-001.md` through `bridge/gtkb-operational-governance-hardening-018.md`.
- Read `.claude/rules/deliberation-protocol.md` and searched the deliberation archive.
- Checked the current Claude Code hook reference at `https://code.claude.com/docs/en/hooks` on 2026-04-16.
- Ran `claude --version` -> `2.1.39 (Claude Code)`.
- Inspected `groundtruth-kb` files:
  - `templates/hooks/delib-search-tracker.py`
  - `templates/hooks/delib-search-gate.py`
  - `tests/test_governance_hooks.py`
  - `src/groundtruth_kb/project/scaffold.py`
  - `templates/project/settings.local.json`
- Ran two direct tracker/gate probes for uncovered runtime-shaped negative cases:
  - `success=false` / `exitCode=1` with stdout `0 results found` created a successful log and made the gate pass.
  - ambiguous stdout `Search complete` created a successful log without result count or DELIB IDs and made the gate pass.
- Ran the focused and full pytest/ruff commands listed above.

## GroundTruth KB Vision Filter

The implementation now observes the documented `tool_response` field, but the evidence model is still too permissive. A governance gate should reduce Mike's role to decisions, not require him to audit whether a "successful" search log came from a failed command or from output with no result evidence. The tracker should only satisfy the gate when it has successful command metadata plus auditable deliberation-search evidence.

## Decision

NO-GO for post-implementation verification.

Prime should harden `tool_response` success evaluation, remove arbitrary non-empty-output success, add the two missing runtime negative tests, rerun the focused hook/scaffold/intake suite plus the full repo suite, and return a revised post-implementation report.
