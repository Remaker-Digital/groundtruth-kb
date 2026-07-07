REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3ddf-359c-7fa3-8885-2d1f9179d884
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Prime Builder session; Codex desktop execution

# GT-KB Bridge Revision - gtkb-wi5049-headless-spawn-guardrails - 007

bridge_kind: implementation_report
Document: gtkb-wi5049-headless-spawn-guardrails
Version: 007 (REVISED; response to NO-GO)
Responds to NO-GO: bridge/gtkb-wi5049-headless-spawn-guardrails-006.md
Approved proposal: bridge/gtkb-wi5049-headless-spawn-guardrails-001.md
Authorizing GO: bridge/gtkb-wi5049-headless-spawn-guardrails-002.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5049-HEADLESS-SPAWN-20260707
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5049
Recommended commit type: fix:

## Revision Claim

This revision responds to the procedural NO-GO in `bridge/gtkb-wi5049-headless-spawn-guardrails-006.md`.
No source, test, hook, or configuration code was changed after the prior implementation report at
`bridge/gtkb-wi5049-headless-spawn-guardrails-005.md`.

Loyal Opposition already confirmed that the WI-5049 implementation is substantively correct and that the
focused tests, lint, formatting checks, no-window audit, and direct-helper-script smoke checks pass. The remaining
blocker is finalization scope: the predecessor bridge chain is untracked, so the next VERIFIED finalization
transaction must include the predecessor bridge files in the same transaction as the implementation files and
the new VERIFIED verdict.

The finalization helper enforces this condition in `_assert_predecessor_chain_committed`: an untracked predecessor
bridge file is acceptable only when it is included in the VERIFIED transaction path set. This revision therefore
makes the required include set explicit for the next Loyal Opposition verification attempt.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - The append-only bridge file chain remains the canonical coordination and audit surface.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - The approved proposal, reports, and this revision retain specification linkage.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - The PAUTH, project, and work item metadata are preserved.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - The implementation remains covered by spec-derived test and audit evidence.
- `GOV-STANDING-BACKLOG-001` - WI-5049 remains tied to the governed backlog and reliability project.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - The bounded PAUTH remains scoped to `PROJECT-GTKB-RELIABILITY-FIXES` and `WI-5049`.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - The PAUTH does not bypass the GO, claim, or implementation-start gates.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - Background GT-KB dispatcher and helper surfaces must avoid visible console windows.
- `SPEC-INTAKE-21c5b3` - Direct harness-to-harness invocation and bypass launch paths require mechanical enforcement.
- `ADR-CROSS-HARNESS-PARITY-001` - Covered guardrail behavior must remain equivalent across harness-observable surfaces.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - Harness-surface changes must include parity coverage or declare intentional non-equivalence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - This revision preserves traceability across proposal, implementation report, verdict, tests, and finalization evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - The thread lifecycle remains explicit after a procedural NO-GO and REVISED response.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The procedural finalization finding is preserved as durable bridge evidence rather than handled as chat-only state.

## Owner Decisions / Input

No new owner decision is required for this revision. It carries forward owner approval `DELIB-202665869`, which
authorized the WI-5049 durable headless-spawn repair and the bounded PAUTH
`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5049-HEADLESS-SPAWN-20260707`.

## Prior Deliberations

- `DELIB-202665869` - Owner authorized the WI-5049 durable headless-spawn repair after observed Cursor/helper and MCP child-process evidence.
- `DELIB-20260702-AUQ-ADJACENT-CONSOLE-WINDOWS-HEADLESS-REQUIREMENT` - Requires AUQ-adjacent hook and decision-capture launches to be headless on Windows.
- `DELIB-20260707-WI5037-IMPLEMENTATION-APPROVAL` - Adjacent direct-invocation enforcement repair scope.
- `bridge/gtkb-wi5049-headless-spawn-guardrails-001.md` - Approved Prime Builder implementation proposal.
- `bridge/gtkb-wi5049-headless-spawn-guardrails-002.md` - Loyal Opposition GO verdict.
- `bridge/gtkb-wi5049-headless-spawn-guardrails-005.md` - Current implementation report reviewed by the NO-GO verdict.
- `bridge/gtkb-wi5049-headless-spawn-guardrails-006.md` - Procedural NO-GO requiring predecessor-chain finalization reconciliation.

## NO-GO Response

### Procedural finalization blocker

Response: accepted and addressed. The implementation report at version 005 did not make the predecessor-chain
include set explicit, so the verifier attempted finalization with the seven implementation files only. Because
versions 001 through 006 are untracked in this worktree, the finalization helper correctly failed closed.

Correction: the next Loyal Opposition `--finalize-verified` invocation should include every untracked predecessor
bridge file for this thread plus this REVISED file, in addition to the seven verified implementation paths. The
helper will write and stage the new VERIFIED verdict version automatically.

## Finalization Transaction Include Set

Use this path set for the next `VERIFIED` finalization attempt:

```text
bridge/gtkb-wi5049-headless-spawn-guardrails-001.md
bridge/gtkb-wi5049-headless-spawn-guardrails-002.md
bridge/gtkb-wi5049-headless-spawn-guardrails-003.md
bridge/gtkb-wi5049-headless-spawn-guardrails-004.md
bridge/gtkb-wi5049-headless-spawn-guardrails-005.md
bridge/gtkb-wi5049-headless-spawn-guardrails-006.md
bridge/gtkb-wi5049-headless-spawn-guardrails-007.md
scripts/codex_mcp_worker_guard.py
scripts/windows_no_window_spawn_audit.py
groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py
platform_tests/scripts/test_codex_mcp_worker_guard.py
platform_tests/scripts/test_windows_no_window_spawn_audit.py
groundtruth-kb/tests/framework/test_bash_enforcement_parser.py
platform_tests/scripts/test_fab14_directive_hook_coverage.py
```

Representative command shape for Loyal Opposition:

```text
groundtruth-kb/.venv/Scripts/python.exe .claude/skills/verify/helpers/write_verdict.py --slug gtkb-wi5049-headless-spawn-guardrails --body-file <reviewed-verdict-body-file> --finalize-verified --no-prepopulate --commit-message "fix(hooks): verify WI-5049 headless spawn guardrails" --include bridge/gtkb-wi5049-headless-spawn-guardrails-001.md --include bridge/gtkb-wi5049-headless-spawn-guardrails-002.md --include bridge/gtkb-wi5049-headless-spawn-guardrails-003.md --include bridge/gtkb-wi5049-headless-spawn-guardrails-004.md --include bridge/gtkb-wi5049-headless-spawn-guardrails-005.md --include bridge/gtkb-wi5049-headless-spawn-guardrails-006.md --include bridge/gtkb-wi5049-headless-spawn-guardrails-007.md --include scripts/codex_mcp_worker_guard.py --include scripts/windows_no_window_spawn_audit.py --include groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py --include platform_tests/scripts/test_codex_mcp_worker_guard.py --include platform_tests/scripts/test_windows_no_window_spawn_audit.py --include groundtruth-kb/tests/framework/test_bash_enforcement_parser.py --include platform_tests/scripts/test_fab14_directive_hook_coverage.py
```

## Refreshed Verification Evidence

Commands executed after receiving the NO-GO:

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_windows_no_window_spawn_audit.py platform_tests/scripts/test_codex_mcp_worker_guard.py groundtruth-kb/tests/framework/test_bash_enforcement_parser.py platform_tests/scripts/test_fab14_directive_hook_coverage.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts/windows_no_window_spawn_audit.py platform_tests/scripts/test_windows_no_window_spawn_audit.py scripts/codex_mcp_worker_guard.py platform_tests/scripts/test_codex_mcp_worker_guard.py groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py groundtruth-kb/tests/framework/test_bash_enforcement_parser.py platform_tests/scripts/test_fab14_directive_hook_coverage.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts/windows_no_window_spawn_audit.py platform_tests/scripts/test_windows_no_window_spawn_audit.py scripts/codex_mcp_worker_guard.py platform_tests/scripts/test_codex_mcp_worker_guard.py groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py groundtruth-kb/tests/framework/test_bash_enforcement_parser.py platform_tests/scripts/test_fab14_directive_hook_coverage.py`
- `groundtruth-kb\.venv\Scripts\python.exe scripts/windows_no_window_spawn_audit.py --json`

Observed results:

- Focused pytest: 35 passed, 1 warning.
- Ruff check: all checks passed.
- Ruff format check: 7 files already formatted.
- Windows no-window spawn audit: `release_ready: true`, `violation_count: 0`, `compliant_no_window: 71`, `interactive_allowlist: 120`, `non_release_runtime: 480`.

## Pre-Filing Preflight Subsection

Candidate preflights for this exact revision content were run before live filing.

- Applicability preflight command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5049-headless-spawn-guardrails --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5049-headless-spawn-guardrails-007.md --json`
- Applicability preflight result: `preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`.
- Clause preflight command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5049-headless-spawn-guardrails --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5049-headless-spawn-guardrails-007.md`
- Clause preflight result: 5 clauses evaluated; `must_apply: 3`; `may_apply: 2`; `not_applicable: 0`; evidence gaps in must-apply clauses: 0; blocking gaps: 0; exit 0.

## Scope Changes

No implementation scope expansion is requested. No additional source, test, hook, configuration, deployment, or
credential path is modified by this revision. The only change is the finalization transaction path set that Loyal
Opposition should use for atomic VERIFIED commit creation.

## Risk And Rollback

Risk is low and procedural. Including predecessor bridge files in the VERIFIED transaction broadens the commit path
set only to preserve the append-only audit chain that already exists on disk. It does not broaden implementation
scope beyond the seven approved WI-5049 source/test files.

Rollback remains the normal verified-commit revert after Loyal Opposition finalization. Until that finalization
succeeds, the dispatcher no-visible-console guard should remain active.
