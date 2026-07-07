GO

# Loyal Opposition Verdict — GO — gtkb-wi5049-headless-spawn-guardrails

bridge_kind: prime_proposal
Document: gtkb-wi5049-headless-spawn-guardrails
Version: 002
Date: 2026-07-07T17:31:00Z
author_identity: Antigravity Loyal Opposition
author_harness_id: C
author_session_context_id: b8780ee4-3e1c-4d1e-a4a9-f22410833b6c
author_model: Gemini 3.5 Flash (High)
author_model_version: high
author_model_configuration: Antigravity harness session; skill bridge-review

## Applicability Preflight

- packet_hash: `sha256:ed3cb553e252f9ba5de23c98a231db2a4ed270b5b097d95d77e35d144d23e7f2`
- bridge_document_name: `gtkb-wi5049-headless-spawn-guardrails`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5049-headless-spawn-guardrails-001.md`
- operative_file: `bridge/gtkb-wi5049-headless-spawn-guardrails-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5049-headless-spawn-guardrails`
- Operative file: `bridge\gtkb-wi5049-headless-spawn-guardrails-001.md`
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

## Defect Confirmation & Findings

Loyal Opposition confirms the headless spawn and direct-invocation defect context reported on 2026-07-07. The defect consists of:
1. Direct execution of GT-KB `.py` helper files (e.g. `write_verdict.py` and other hooks/helpers) which can bypass Python executable bindings and execute via Windows shell file association, opening GUI surfaces (such as Cursor) rather than being restricted to the intended command boundary.
2. Hook-invoked support scripts in `.codex/gtkb-hooks` and other platform hook paths being mislabeled or missing from no-visible-console verification.
3. The Codex MCP worker guard launching shell process-manager probes (`cmd.exe` and `pwsh.exe`) without using the shared `CREATE_NO_WINDOW` spawn wrappers, resulting in visible console flashes on the user desktop.

The proposed scope targets these leaks mechanically at the platform enforcement boundary without altering external config surfaces.

## Proposed Fix Assessment

The proposed work is targeted and minimal, affecting exactly:
1. `groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py` and tests: Prevents direct script execution file-association leaks by blocking direct helper execution unless routed through Python or wrappers.
2. `scripts/windows_no_window_spawn_audit.py` and tests: Extends the verification coverage so hook-invoked support scripts are properly audited.
3. `scripts/codex_mcp_worker_guard.py` and tests: Updates process-management calls to consistently use no-window wrappers.

All files listed in `target_paths` are within the project root `E:\GT-KB`. Coordination with `WI-5037` is declared and will be handled during implementation.

## Requirement Sufficiency

Existing requirements are sufficient. The proposed fix closes gaps in the implementation of `SPEC-INTAKE-21c5b3`, `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`, and `DELIB-20260702-AUQ-ADJACENT-CONSOLE-WINDOWS-HEADLESS-REQUIREMENT`.

## Specification Links Assessment

The proposal cites all required blocking specifications, and the preflight tool has confirmed that no required cross-cutting specs are missing. The advisory specification omissions reported by the preflight tool are not blocking and do not impact the correctness of the proposal.

## Prior Deliberations

- `DELIB-202665869` - Owner-authorized backlog entry and cutoff target for the WI-5049 headless-spawn repair.
- `DELIB-20260702-AUQ-ADJACENT-CONSOLE-WINDOWS-HEADLESS-REQUIREMENT` - Requirement for headless AUQ-adjacent script executions on Windows.

## Verdict

**GO**. The implementation proposal is compliant, preflights pass with zero blocking gaps, targets are root-contained, and the proposed changes directly address the confirmed Windows console/window leaks.
