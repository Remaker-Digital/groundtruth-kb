GO

# Loyal Opposition Verdict — GO — gtkb-wi5052-dispatcher-codex-no-window-containment

bridge_kind: prime_proposal
Document: gtkb-wi5052-dispatcher-codex-no-window-containment
Version: 002
Date: 2026-07-07T19:30:00Z
author_identity: Antigravity Loyal Opposition
author_harness_id: C
author_session_context_id: 6a6faa20-6fa7-48c7-b692-1aa5f9c0bcec
author_model: Gemini 3.5 Flash (High)
author_model_version: gemini-3.5-flash
author_model_configuration: Antigravity harness session; skill bridge-review

## Applicability Preflight

- packet_hash: `sha256:c5c86a295cea54741828c840951324e65f217083ed3c2971de8b1316e9a568a0`
- bridge_document_name: `gtkb-wi5052-dispatcher-codex-no-window-containment`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5052-dispatcher-codex-no-window-containment-001.md`
- operative_file: `bridge/gtkb-wi5052-dispatcher-codex-no-window-containment-001.md`
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
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5052-dispatcher-codex-no-window-containment`
- Operative file: `bridge\gtkb-wi5052-dispatcher-codex-no-window-containment-001.md`
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

## Defect Confirmation & Findings

Loyal Opposition confirms the dispatcher Codex no-window containment defect context reported on 2026-07-07. The defect consists of:
1. Visible command console windows relentlessly spawning on the user workstation during auto-dispatch.
2. Long-lived child shell processes (`pwsh.exe`) being spawned under Codex CLI command-safety handling without `CREATE_NO_WINDOW` flags.
3. Lack of auto-dispatch quarantine control during unsafe launch paths.

## Proposed Fix Assessment

The proposed work is targeted and minimal, affecting exactly:
1. `scripts/dispatcher_runtime.py` and platform tests: Implements quarantine controls and dispatcher-wide no-window check enforcement.
2. `scripts/windows_no_window_spawn_audit.py` and platform tests: Extends audit coverage to detect non-compliant shell launches.
3. `config/dispatcher/rules.toml` and `harness-state/harness-registry.json`: Configures the required rules and overrides.

All files listed in `target_paths` are within the project root `E:\GT-KB`.

## Requirement Sufficiency

Existing requirements are sufficient. The proposed fix closes gaps in the implementation of `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`, `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, and `SPEC-DISPATCHER-CONTROL-SURFACE-001`.

## Specification Links Assessment

The proposal cites all required blocking specifications, and the preflight tool has confirmed that no required cross-cutting specs are missing.

## Prior Deliberations

- `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS` - Owner directive that no visible console windows may spawn on this workstation.
- `INTAKE-8242840e` - Treating repeated worker launch failure as an operations-owned recovery case.
- `INTAKE-6554ff58` - Quiescing the dispatcher complex.

## Verdict

**GO**. The implementation proposal is compliant, preflights pass with zero blocking gaps, targets are root-contained, and the proposed changes directly address the confirmed dispatcher console window leak.
