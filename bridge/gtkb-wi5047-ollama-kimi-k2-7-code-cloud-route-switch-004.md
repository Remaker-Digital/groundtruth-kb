NO-GO
author_identity: loyal-opposition/antigravity
author_harness_id: C
author_session_context_id: 2026-07-06T17-06-32Z-loyal-opposition-C-df26940c
author_model: Gemini 1.5 Pro
author_model_version: gemini-1.5-pro
author_model_configuration: Antigravity interactive Loyal Opposition; resolved_role=loyal-opposition

# Loyal Opposition Review - WI-5047 Ollama Kimi Route Switch - 004

bridge_kind: lo_verdict
Document: gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch
Version: 004
Responds to: gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch-003 (NEW, post-implementation blocker report)
Reviewer: Loyal Opposition (Antigravity, harness C, interactive)
Date: 2026-07-06 UTC
Verdict: NO-GO

## Verdict Summary

NO-GO. The implementation is returned as a **NO-GO** due to a documented configuration block. The active Ollama route configuration and harness D headless argv correctly point to Kimi. However, the dispatcher configuration at `config/dispatcher/rules.toml` is stale (budget model label still points to `deepseek-v4-pro-cloud` instead of `kimi-k2-7-code-cloud`). Direct mutation of `rules.toml` is prohibited by `DCL-DISPATCHER-CONFIG-CLI-ONLY-001`, and the CLI control surface lacks the transaction necessary to update `budget.harnesses.<id>.model`.

## Findings

### [P1] Stale Dispatcher Configuration Metadata
- **Evidence Source**: `bridge/gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch-003.md` and `gt bridge dispatch config --json`.
- **Impact**: Stale dispatcher metadata label causes a parity defect under `ADR-CROSS-HARNESS-PARITY-001`.
- **Recommended Action**: Confirming the Prime Builder's assessment: the correct follow-up is a separate implementation proposal to introduce a new dispatcher config transaction `set-model` (or similar) on the CLI dispatcher control surface, then utilize it to update harness D's budget model to `kimi-k2-7-code-cloud`.

## Prior Deliberations

- `DELIB-20260706-OLLAMA-KIMI-K2-7-CODE-CLOUD` - Owner decision to switch Ollama/D to `kimi-k2.7-code:cloud`.
- `DELIB-20260702-OLLAMA-DEEPSEEK-V4-PRO-CLOUD` - Prior DeepSeek route decision, now superseded for this forward work.

## Applicability Preflight

- packet_hash: `sha256:c25370b29263afc4d4eff8a0c0ee3f9d32230c8f296fd18dff99d41973a6833f`
- bridge_document_name: `gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch-003.md`
- operative_file: `bridge/gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:blocked, content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch`
- Operative file: `bridge\gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch-003.md`
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

## Methodology Trail

Files inspected:
- `bridge/gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch-003.md`
- `.api-harness/routing.toml`
- `harness-state/harness-registry.json`

Commands run:
- `gt bridge dispatch config --help`
- `gt bridge dispatch config set-eligibility --help`
- `gt bridge dispatch config add-harness --help`
- `gt bridge dispatch config set-caps --help`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch`

## Owner Decisions / Input

None required.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
