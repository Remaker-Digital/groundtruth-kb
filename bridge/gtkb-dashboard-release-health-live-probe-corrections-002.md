GO

# Verdict: GO -- Dashboard Release-Health Live-Probe and Card Consistency Corrections

Document: gtkb-dashboard-release-health-live-probe-corrections
Version: 002
Topic Slug: gtkb-dashboard-release-health-live-probe-corrections
Date: 2026-06-30T21:50:00Z
Verifier: Loyal Opposition (OpenRouter/F)
author_identity: loyal-opposition/openrouter
author_harness_id: F
author_session_context_id: openrouter-harness-f
author_model: deepseek/deepseek-v4-pro
author_model_version: deepseek-v4-pro
author_model_configuration: OpenRouter harness shim; route deepseek-v4-pro; skill bridge-review; guarded tools Read, Write, Edit, Grep, Glob, Bash

## Applicability Preflight

- packet_hash: `sha256:cf12923190fe23390184af1530f7ded6b8e37a736c3ffba8648749ecaf3fcdea`
- bridge_document_name: `gtkb-dashboard-release-health-live-probe-corrections`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-dashboard-release-health-live-probe-corrections-001.md`
- operative_file: `bridge/gtkb-dashboard-release-health-live-probe-corrections-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-dashboard-release-health-live-probe-corrections`
- Operative file: `bridge\gtkb-dashboard-release-health-live-probe-corrections-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | n/a | blocking | blocking |

## Prior Deliberations

- `DELIB-20265586` -- owner-approved bounded implementation authorization for `PROJECT-GTKB-DASHBOARD-OBSERVABILITY`, including `GTKB-DASHBOARD-003`.
- `DELIB-0840` and `DELIB-0842` -- source decisions behind `SPEC-PROJECT-DASHBOARD-KPI-LINK-001`.
- `DELIB-0828` -- release readiness requires governed test evidence before release GO.
- `DELIB-20265795` -- dispatcher reporting/configuration should be exposed through governed `gt bridge dispatch` surfaces.
- `DELIB-20260630-DEFERRAL-EXPIRY-001` -- owner decision that deferred work requires explicit expiry.
- `INTAKE-670252e3` -- owner clarification: dashboard deployment surfaces are application-populated and deployment-environment agnostic.
- `bridge/gtkb-dashboard-release-health-schema-provider-neutrality-001.md` through `-004.md` -- prior VERIFIED provider-neutrality slice; this follows up.
- `bridge/gtkb-wi4937-dispatcher-supervisor-governance-006.md` -- dispatcher supervisor is verified and headless.

## Findings

The proposal is a disciplined, narrow bugfix with three well-diagnosed defects, clear remediation scope, and explicit out-of-scope boundaries. All preflights pass.

### F1: Defect Diagnosis Quality -- PASS
- Severity: P2 (positive)
- All three defects are precisely characterized with evidence, not speculation:
  - **Defect 1**: `health_cards` vs `current_metrics.release_blockers` mismatch with specific values (3/red vs 0 blockers/green). Root cause: health cards not reconciled after live probe refresh.
  - **Defect 2**: Startup-model dirty count (8) vs `git status` dirty count (304/305). Root cause: different counting sources used without reconciliation.
  - **Defect 3**: `integration_status.github = live_state_unavailable` despite `gh` working. Root cause: `build_startup_model(...)` mutates `XDG_CONFIG_HOME` to temp, causing `gh` subprocess to miss host auth store.
- Each defect maps to a specific scope item with corresponding regression tests.

### F2: Scope Discipline -- PASS
- Severity: P2 (positive)
- The proposal explicitly defines 8 in-scope items and 4 out-of-scope items.
- Out-of-scope exclusions are important: dispatcher route/runtime failures remain visible as release blockers; no pushing main or changing external GitHub settings; no restoring retired cross-harness trigger automation. These boundary statements protect the narrow fix from scope creep.
- IP-6 (WI-4937 supervisor health row) correctly distinguishes healthy headless state from route/runtime WARNs without trying to fix the WARNs.
- IP-7 preserves existing provider-neutral mock deployment rows per `INTAKE-670252e3`.

### F3: Verification Plan Adequacy -- PASS
- Severity: P2 (positive)
- Eight rows in the spec-derived verification plan table, each mapping a governing surface to concrete verification.
- Focused command set covers the affected paths: pytest, ruff check/format, live-probe dashboard refresh.
- Risk mitigations are appropriate: mock `gh` subprocess for unit tests, capture live evidence separately.

### F4: Provider-Neutrality Boundary -- PASS
- Severity: P2 (positive)
- The XDG_CONFIG_HOME fix for `gh` is host-local environment preservation, not a deployment-provider dependency.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` is explicitly cited and the no-Azure/Agent-Red constraint is reinforced.
- IP-7 keeps provider-neutral mock rows intact with Azure reconciliation opt-in.

### F5: Risk Acknowledgment -- PASS
- Severity: P3 (note)
- The proposal acknowledges that surfacing hidden blockers "could make the dashboard look worse" -- a correctness-over-cosmetics tradeoff aligned with `SPEC-PROJECT-DASHBOARD-KPI-LINK-001`.
- Rollback is a single-commit revert.

### F6: XDG_CONFIG_HOME Fix -- Design Advisory
- Severity: P4 (advisory)
- The `build_startup_model` XDG_CONFIG_HOME mutation is the deepest bug. Prime Builder should document the chosen remediation approach (snapshot/restore, explicit `--config` flag, or reorder pipeline) in the implementation report. This does not block GO.

## Verdict: GO

This is a well-diagnosed, narrow bugfix proposal with clear scope boundaries, concrete verification, and honest risk acknowledgment. All blocking preflights pass. Proceed to implementation under Prime Builder (harness A).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*