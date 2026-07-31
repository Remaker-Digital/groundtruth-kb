VERIFIED
author_identity: loyal-opposition/antigravity
author_harness_id: C
author_session_context_id: 25ced1cb-a328-452e-b039-cd88c0e659bd
author_model: Gemini 3.5 Flash (Medium)
author_model_version: antigravity-interactive
author_model_configuration: Antigravity headless LO session

bridge_kind: verification_verdict
Document: gtkb-wi4896-codex-hook-parent-leak-containment
Version: 004
Author: Loyal Opposition (Antigravity, harness C)
Date: 2026-06-30 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi4896-codex-hook-parent-leak-containment-003.md
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4896
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4896-CONSOLE-WINDOW-SUPPRESSION
Recommended commit type: fix
Verdict: VERIFIED

## Separation Check

Report -003 author session `019f09c9-2db0-7b00-a337-40f998b07e56` (harness A);
independent Antigravity LO session `25ced1cb-a328-452e-b039-cd88c0e659bd` (harness C).

## Review Summary

**VERIFIED.** The Codex hook parent-shell leak containment follow-up for WI-4896 is fully implemented and verified. The hooks registered in `.codex/hooks.json` are now collapsed into a single `pythonw.exe run_py_no_window --batch <batch_name>` invocation per hook type, which prevents spawning separate shell sessions for each sub-hook command. The batch catalog in `run_py_no_window.py` cleanly maps hook events and handles sequential execution. The default hook child timeout has been raised to 10 seconds to accommodate longer-running operations. Extensionless entry point shims and windows subprocess helpers are cleanly implemented. All focused tests pass successfully.

Regarding the caveat that Codex retains pre-change hook commands in memory in the active session: this is a de facto reload caveat that does not affect on-disk release artifacts or fresh-process containment.

## Applicability Preflight

- packet_hash: `sha256:d2395cc5893b8d67a4bfc58c70082e1e772b7c9f2c847d8719cb1aa36ae64817`
- bridge_document_name: `gtkb-wi4896-codex-hook-parent-leak-containment`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi4896-codex-hook-parent-leak-containment-003.md`
- operative_file: `bridge/gtkb-wi4896-codex-hook-parent-leak-containment-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi4896-codex-hook-parent-leak-containment`
- Operative file: `bridge\gtkb-wi4896-codex-hook-parent-leak-containment-003.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Prior Deliberations

- `DELIB-20266297` - Owner decision authorizing dispatcher console-window suppression.
- `bridge/gtkb-wi4896-codex-hook-parent-leak-containment-001.md` - Approved proposal.
- `bridge/gtkb-wi4896-codex-hook-parent-leak-containment-002.md` - GO verdict.

## Specifications Carried Forward

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
|---|---|---|---|
| Command parity containment | `test_codex_hook_json_commands_containment` | yes | PASS |
| Matcher validation | `test_codex_hook_batch_matching` | yes | PASS |
| Target existence | `test_codex_hook_batch_targets_exist` | yes | PASS |
| Subprocess creation flags | `test_windows_subprocess_creationflags` | yes | PASS |
| Sibling path resolution | `test_windows_subprocess_prefer_pythonw` | yes | PASS |

## Positive Confirmations

- Single-command fanned hooks successfully collapsed to `--batch` runs.
- Durable Codex hook registry verified on Windows.
- Hook batch targets checked and verified.

## Commands Executed

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4896-codex-hook-parent-leak-containment
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4896-codex-hook-parent-leak-containment
python -m pytest platform_tests\scripts\test_codex_hook_runtime_containment.py platform_tests\scripts\test_windows_subprocess.py -q --tb=short
```

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

## Commit Finalization Evidence

- Finalization helper: `.claude/skills/verify/helpers/write_verdict.py --finalize-verified`
- Intended commit subject: `fix: VERIFIED gtkb-wi4896 codex hook parent-shell leak containment`
- Same-transaction path set:
  - `.codex/hooks.json`
  - `.codex/gtkb-hooks/run_py_no_window.py`
  - `.codex/gtkb-hooks/run_py_no_window`
  - `.codex/gtkb-hooks/run_cmd_no_window`
  - `scripts/windows_subprocess.py`
  - `platform_tests/scripts/test_codex_hook_runtime_containment.py`
  - `platform_tests/scripts/test_windows_subprocess.py`
  - `bridge/gtkb-wi4896-codex-hook-parent-leak-containment-001.md`
  - `bridge/gtkb-wi4896-codex-hook-parent-leak-containment-003.md`
  - `bridge/gtkb-wi4896-codex-hook-parent-leak-containment-004.md`
- Final commit SHA is emitted by the helper after commit creation; it is intentionally not self-embedded in this verdict file.
