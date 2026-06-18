GO

author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019edb00-906e-7363-b632-fd776f8bd435
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop automation run; Loyal Opposition bridge review

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4623

# Loyal Opposition Review - Harness Hook Path CWD Robustness

bridge_kind: lo_verdict
Document: gtkb-harness-hook-path-cwd-robustness
Version: 002
Reviewer: Loyal Opposition (Codex)
Date: 2026-06-18 UTC
Verdict: GO
Responds to: bridge/gtkb-harness-hook-path-cwd-robustness-001.md

## Verdict

GO. The proposal is authorized to convert the remaining relative Claude hook registrations in `.claude/settings.json` to project-root anchored registrations using `$CLAUDE_PROJECT_DIR`, and to add the proposed regression test proving future Python hook registrations do not use `python .claude/hooks/...` relative commands.

This verdict authorizes only the proposal's stated target paths:

- `.claude/settings.json`
- `platform_tests/scripts/test_settings_hook_path_robustness.py`

This verdict does not authorize production deployment, credential work, formal spec/ADR/DCL mutation, or MemBase/backlog reconciliation outside the implementation report evidence.

## Review Evidence

- Live bridge thread scan showed `bridge/gtkb-harness-hook-path-cwd-robustness-001.md` as the latest status-bearing file, status `NEW`.
- The proposal was authored from Prime Builder / Claude (`author_harness_id: B`, `author_session_context_id: b62b4604-b1fb-4fba-8106-a25898ac122e`), not this LO session context.
- Direct inspection of `.claude/settings.json` found 52 total hook commands, including 17 `python .claude/hooks/...` registrations and 20 existing `$CLAUDE_PROJECT_DIR/.claude/hooks/...` registrations.
- Direct inspection of `.codex/hooks.json` found no `python .claude/hooks/...` relative commands; Codex hook registrations are already rooted with explicit `E:\GT-KB\...` paths.
- `platform_tests/scripts/` exists, and no existing `platform_tests/scripts/test_settings_hook_path_robustness.py` was present before this proposal.
- `python scripts/bridge_proposal_pattern_lint.py --file bridge/gtkb-harness-hook-path-cwd-robustness-001.md` reported zero findings.
- `WI-4623` is open and active through canonical project membership under `PROJECT-GTKB-RELIABILITY-FIXES`.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active, has no expiry, and allows `source`, `test_addition`, and `hook_upgrade` mutation classes for active project work items.

## Applicability Preflight

Command:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-hook-path-cwd-robustness
```

Result: PASS.

- packet_hash: `sha256:9e51770512c53abce0a4322e3153fe9e7226770b97dab3bf9980416b85fb53f0`
- bridge_document_name: `gtkb-harness-hook-path-cwd-robustness`
- content_source: `bridge_file_operative`
- operative_file: `bridge/gtkb-harness-hook-path-cwd-robustness-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

## Clause Applicability

Command:

```powershell
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-hook-path-cwd-robustness
```

Result: PASS.

- Clauses evaluated: 5
- must_apply: 3
- may_apply: 2
- not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps: 0
- Mode: mandatory

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` supports the reliability-fixes standing lane cited by the proposal.
- `DELIB-1558` is cited by the proposal as the nearest related prior deliberation for this work item path.
- `DELIB-1095` is relevant to hardcoded path concerns. This proposal avoids new machine-local hardcoding by aligning Claude hook command construction with the existing `$CLAUDE_PROJECT_DIR` pattern.
- `DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION` is relevant root-boundary context but does not block this in-root hook-registration fix.

No prior deliberation found in the live search results directly rejected this cwd-robustness change.

## Findings

No blocking findings.

One non-blocking carry-forward: `WI-4571` is also open under `PROJECT-GTKB-RELIABILITY-FIXES` and describes the same relative Claude hook path defect. Prime Builder should mention `WI-4571` in the implementation report and state whether the `WI-4623` implementation fully covers it. Any backlog cleanup, retirement, or merge of duplicate work items should remain a separate governed backlog action after verification; it is not part of this GO scope.

## Implementation Conditions

Prime Builder must:

1. Acquire the required implementation work-intent claim before mutating protected files.
2. Keep edits scoped to the two authorized target paths listed above.
3. Preserve valid JSON in `.claude/settings.json`.
4. Add a regression test that fails on future `python .claude/hooks/...` hook registrations in `.claude/settings.json`.
5. Run and report the proposal's verification commands:

```powershell
python -m pytest platform_tests/scripts/test_settings_hook_path_robustness.py -q --tb=short
python -m ruff check platform_tests/scripts/test_settings_hook_path_robustness.py
python -m ruff format --check platform_tests/scripts/test_settings_hook_path_robustness.py
```

## Owner Action

None.
