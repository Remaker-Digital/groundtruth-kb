VERIFIED

# Loyal Opposition Verdict — VERIFIED — gtkb-wi5049-headless-spawn-guardrails

bridge_kind: lo_verdict
Document: gtkb-wi5049-headless-spawn-guardrails
Version: 004
Responds to implementation report: bridge/gtkb-wi5049-headless-spawn-guardrails-003.md
Approved proposal: bridge/gtkb-wi5049-headless-spawn-guardrails-001.md
Authorizing GO: bridge/gtkb-wi5049-headless-spawn-guardrails-002.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5049-HEADLESS-SPAWN-20260707
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5049
Recommended commit type: fix:

author_identity: Ollama Loyal Opposition
author_harness_id: D
author_session_context_id: 2026-07-07T18-19-50Z-loyal-opposition-D-5bf7d4
author_model: kimi-k2.7-code:cloud
author_model_version: cloud
author_model_configuration: Ollama harness shim; route kimi-k2-7-code-cloud; skill bridge-review; guarded tools Read, Write, Edit, Grep, Glob, Bash

## Applicability Preflight

- packet_hash: `sha256:6bd11ebdbb4b038a1e730ee506ed4a1f8fdd7aa86a55b740e2bb14e71caa22d1`
- bridge_document_name: `gtkb-wi5049-headless-spawn-guardrails`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5049-headless-spawn-guardrails-003.md`
- operative_file: `bridge/gtkb-wi5049-headless-spawn-guardrails-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5049-headless-spawn-guardrails`
- Operative file: `bridge\gtkb-wi5049-headless-spawn-guardrails-003.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Defect Confirmation

Loyal Opposition confirms the three headless-spawn guardrail gaps that WI-5049 targeted:

1. `scripts/codex_mcp_worker_guard.py` launched PowerShell process-list probes and `taskkill.exe` without `CREATE_NO_WINDOW`, which can flash visible console windows when the guard runs as background/runtime tooling.
2. `scripts/windows_no_window_spawn_audit.py` did not classify `scripts/codex_mcp_worker_guard.py` as release-runtime, so a future regression that removed `CREATE_NO_WINDOW` from the guard would not fail the release readiness gate.
3. `groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py` did not block direct `.py` helper-script command heads under GT-KB harness helper directories, leaving a Windows file-association route that could open a Cursor window instead of routing through the governed interpreter.

## Implementation Assessment

The post-implementation report (bridge/gtkb-wi5049-headless-spawn-guardrails-003.md) addresses all approved target paths:

- `scripts/codex_mcp_worker_guard.py` now passes `no_window_subprocess_kwargs()` to its Windows PowerShell listing, POSIX `ps`, and Windows `taskkill.exe` calls.
- `scripts/windows_no_window_spawn_audit.py` now includes `scripts/codex_mcp_worker_guard.py` in `RELEASE_RUNTIME_FILES`, raising missing-no-window regressions to release violations.
- `groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py` now denies direct `.py` helper-script command heads and `Start-Process` targets under `.claude/hooks/`, `.claude/skills/`, `.codex/gtkb-hooks/`, `.codex/skills/`, and `.cursor/skills/`, while preserving explicit `python helper.py` invocation.
- Tests were added or updated for each changed surface, including Codex Bash and Claude PowerShell hook parity coverage.

## Verified Path Set

- `scripts/codex_mcp_worker_guard.py`
- `scripts/windows_no_window_spawn_audit.py`
- `groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py`
- `platform_tests/scripts/test_codex_mcp_worker_guard.py`
- `platform_tests/scripts/test_windows_no_window_spawn_audit.py`
- `groundtruth-kb/tests/framework/test_bash_enforcement_parser.py`
- `platform_tests/scripts/test_fab14_directive_hook_coverage.py`

## Specification-to-Test Mapping

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python scripts/bridge_claim_cli.py status gtkb-wi5049-headless-spawn-guardrails` confirms active LO claim and NEW status on the implementation report. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | The implementation report carries concrete specification links and the bridge applicability preflight returned `preflight_passed: true` with `missing_required_specs: []`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest, ruff, format check, no-window audit, and enforcement smoke tests are mapped below under Verification Evidence. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | `platform_tests/scripts/test_windows_no_window_spawn_audit.py` and `platform_tests/scripts/test_codex_mcp_worker_guard.py` verify no-window subprocess handling and release-runtime audit coverage. |
| `SPEC-INTAKE-21c5b3` | `groundtruth-kb/tests/framework/test_bash_enforcement_parser.py` verifies direct helper `.py` launch blocking and explicit Python invocation allowance. |
| `ADR-CROSS-HARNESS-PARITY-001` | `platform_tests/scripts/test_fab14_directive_hook_coverage.py` verifies the direct-helper block through Codex Bash and Claude PowerShell hook paths. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Cross-harness Codex/Claude hook coverage was added for the enforcement path touched by this repair. |

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - Protected source/test edits require live bridge authority and the numbered bridge chain remains canonical.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - The approved proposal and implementation report cite concrete governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - This verdict maps linked specifications to executed tests and runtime evidence.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - Background/scheduled Windows GT-KB surfaces must avoid visible console windows.
- `SPEC-INTAKE-21c5b3` - Direct harness-to-harness invocation and bypass launch paths require mechanical enforcement.
- `ADR-CROSS-HARNESS-PARITY-001` - Equivalent harness-observable guardrail behavior is maintained across Codex and Claude hook surfaces.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - Harness-surface changes include parity coverage rather than silently changing one harness.

## Verification Evidence

1. Applicability preflight for the implementation report passed with `preflight_passed: true` and no missing required specs.
2. ADR/DCL clause preflight passed with zero blocking gaps.
3. Focused `python -m pytest` run over the changed test modules: 35 passed, 0 failed.
4. Ruff check: all checks passed for the seven changed files.
5. Ruff format check: 7 files already formatted.
6. Windows no-window spawn audit: 0 violations, 71 compliant no-window findings, 120 interactive allowlist findings, 480 non-release-runtime findings.
7. Direct helper-script enforcement check:
   - `.claude/skills/verify/helpers/write_verdict.py --slug demo` → denied with the helper-script denial message.
   - `python .claude/skills/verify/helpers/write_verdict.py --slug demo --body-file draft.md` → allowed.
   - `Start-Process -FilePath E:\GT-KB\.cursor\skills\verify\helpers\write_verdict.py` → denied.

## Risk And Rollback

Residual risk is low. The enforcement change is narrowly scoped to known GT-KB harness helper directories and direct `.py` command heads or `Start-Process` targets, with explicit interpreter invocation preserved. Rollback is a revert of the seven verified paths.

## Commit Finalization Evidence

- Finalization helper: `.claude/skills/verify/helpers/write_verdict.py --finalize-verified`
- Commit message: `fix(spawn-guardrails): close headless-spawn gaps in MCP worker guard, no-window audit, and helper-script enforcement`
- Same-transaction path set:
  - `scripts/codex_mcp_worker_guard.py`
  - `scripts/windows_no_window_spawn_audit.py`
  - `groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py`
  - `platform_tests/scripts/test_codex_mcp_worker_guard.py`
  - `platform_tests/scripts/test_windows_no_window_spawn_audit.py`
  - `groundtruth-kb/tests/framework/test_bash_enforcement_parser.py`
  - `platform_tests/scripts/test_fab14_directive_hook_coverage.py`
  - `bridge/gtkb-wi5049-headless-spawn-guardrails-004.md`

## Verdict

**VERIFIED**. WI-5049 is implemented as approved. The changes satisfy the authorized proposal, pass all required preflights and focused tests, and close the identified headless-spawn and direct-helper-script bypass gaps.

## Prior Deliberations

- `bridge/gtkb-wi5049-headless-spawn-guardrails-001.md` - Approved Prime Builder implementation proposal.
- `bridge/gtkb-wi5049-headless-spawn-guardrails-002.md` - Loyal Opposition GO verdict authorizing implementation.
- `bridge/gtkb-wi5049-headless-spawn-guardrails-003.md` - Prime Builder post-implementation report for WI-5049.
