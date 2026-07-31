NO-GO

# Loyal Opposition Verdict — NO-GO — gtkb-wi5049-headless-spawn-guardrails

bridge_kind: lo_verdict
Document: gtkb-wi5049-headless-spawn-guardrails
Version: 006
Responds to implementation report: bridge/gtkb-wi5049-headless-spawn-guardrails-005.md
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
- content_file: `bridge/gtkb-wi5049-headless-spawn-guardrails-005.md`
- operative_file: `bridge/gtkb-wi5049-headless-spawn-guardrails-005.md`
- preflight_passed: `true`
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
- Operative file: `bridge\gtkb-wi5049-headless-spawn-guardrails-005.md`
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

Loyal Opposition confirms the headless-spawn guardrail gaps that WI-5049 targeted:

1. `scripts/codex_mcp_worker_guard.py` launched PowerShell process-list probes and `taskkill.exe` without `CREATE_NO_WINDOW`, which can flash visible console windows.
2. `scripts/windows_no_window_spawn_audit.py` did not classify `scripts/codex_mcp_worker_guard.py` as release-runtime, so a future regression that removed `CREATE_NO_WINDOW` would not fail the release readiness gate.
3. `groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py` did not block direct `.py` helper-script command heads under GT-KB harness helper directories, leaving a Windows file-association bypass route.

## Implementation Assessment

The substantive implementation in the reported path set is correct and the focused tests pass. The seven changed files directly address the approved proposal:

- `scripts/codex_mcp_worker_guard.py` now uses `no_window_subprocess_kwargs()` for its subprocess calls.
- `scripts/windows_no_window_spawn_audit.py` now treats the MCP worker guard as release runtime.
- `groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py` now blocks direct helper-script launches while preserving explicit `python` invocation.
- Tests were added for audit classification, MCP guard kwargs, helper-script denial, explicit-python allowance, and Codex/Claude hook parity.

Verification evidence collected:
- Applicability preflight: passed.
- ADR/DCL clause preflight: passed with zero blocking gaps.
- Focused pytest: 35 passed.
- Ruff lint and format checks: passed.
- Windows no-window spawn audit: 0 violations.
- Direct helper-script smoke tests: direct launch denied, explicit python launch allowed, Start-Process helper target denied.

## Blocker / Why NO-GO

This verdict is **NO-GO** because the bridge workflow cannot atomically finalize the VERIFIED commit. The mandatory atomic finalization helper (`.claude/skills/verify/helpers/write_verdict.py --finalize-verified`) failed closed with:

> VERIFIED finalization requires a committed predecessor bridge chain; bridge/gtkb-wi5049-headless-spawn-guardrails-001.md is not git-tracked and is not included in the VERIFIED transaction.

The predecessor bridge files for this thread exist on disk but are not tracked in the repository history, and raw `git add` / `git commit` of bridge files is blocked by the implementation start gate as a controlled-artifact direct mutation. Without a committed predecessor chain, the helper cannot produce a canonical VERIFIED artifact, and the protocol requires failing closed rather than leaving an unfinalized terminal VERIFIED file in the worktree.

The implementation itself is sound; the blocker is purely the inability to satisfy the atomic finalization invariant in this worktree state.

## Verified Path Set (for reference)

- `scripts/codex_mcp_worker_guard.py`
- `scripts/windows_no_window_spawn_audit.py`
- `groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py`
- `platform_tests/scripts/test_codex_mcp_worker_guard.py`
- `platform_tests/scripts/test_windows_no_window_spawn_audit.py`
- `groundtruth-kb/tests/framework/test_bash_enforcement_parser.py`
- `platform_tests/scripts/test_fab14_directive_hook_coverage.py`

## Prior Deliberations

- `bridge/gtkb-wi5049-headless-spawn-guardrails-001.md` - Approved Prime Builder implementation proposal.
- `bridge/gtkb-wi5049-headless-spawn-guardrails-002.md` - Loyal Opposition GO verdict authorizing implementation.
- `bridge/gtkb-wi5049-headless-spawn-guardrails-003.md` - Prime Builder post-implementation report for WI-5049.
- `bridge/gtkb-wi5049-headless-spawn-guardrails-005.md` - Restated post-implementation report prepared for finalization.

## Verdict

**NO-GO** (procedural / fail-closed). The WI-5049 implementation is substantively correct and all focused tests pass, but the atomic VERIFIED finalization helper cannot commit because the predecessor bridge chain is not git-tracked in this worktree. Reconcile the bridge chain into git history and rerun finalization, or address the controlled-artifact commit path, before marking this thread VERIFIED.
