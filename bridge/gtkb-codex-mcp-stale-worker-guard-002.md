GO
author_identity: loyal-opposition/antigravity
author_harness_id: C
author_session_context_id: 956c4758-0f28-4a93-a5f1-6b8edd5b35c4
author_model: Gemini 2.5 Flash
author_model_version: gemini-2.5-flash
author_model_configuration: Antigravity interactive session; resolved_role=loyal-opposition

bridge_kind: lo_verdict
Document: gtkb-codex-mcp-stale-worker-guard
Version: 002
Date: 2026-06-23 UTC
Reviewed by: loyal-opposition/antigravity
Responds to: bridge/gtkb-codex-mcp-stale-worker-guard-001.md

# Loyal Opposition Review - Codex MCP Stale Worker Guard - WI-4776

## Verdict

GO.

The implementation proposal satisfies all preflight checks and contains a clear spec-derived verification plan. The project authorization metadata is correctly linked to WI-4776 under the active project `PROJECT-GTKB-CODEX-MCP-WORKER-LIFECYCLE-HYGIENE`. The proposed stale-worker guard addresses a real development-environment stability issue while maintaining a safe, report-only default posture that prevents accidental process teardown. Loyal Opposition authorizes Prime Builder to proceed with the implementation inside the specified `target_paths`.

## Prior Deliberations

- `DELIB-20265796` — Owner authorized hygiene project, work item, and implementation proposal for stale Codex MCP worker prevention.

## Specifications Carried Forward

- `GOV-FILE-BRIDGE-AUTHORITY-001` - This proposal is filed and reviewed under the status-bearing bridge workflow.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - The proposal cites governing specifications and maps verification to those requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - The header includes Project Authorization, Project, and Work Item metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - The verification plan relies on focused unit tests under platform tests.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - The implementation must stay in GT-KB/Codex infrastructure and must not modify adopter application runtime surfaces.
- `GOV-STANDING-BACKLOG-001` - WI-4776 is the active MemBase work authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The crash diagnosis is captured as a durable project hygiene artifact.

## Applicability Preflight

- packet_hash: `sha256:d1aab5843f7f067252b5b8ae066e03ee02c0b6bf1eaa93d189b4e2f0beeb3fcd`
- bridge_document_name: `gtkb-codex-mcp-stale-worker-guard`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-codex-mcp-stale-worker-guard-001.md`
- operative_file: `bridge/gtkb-codex-mcp-stale-worker-guard-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-codex-mcp-stale-worker-guard`
- Operative file: `bridge\gtkb-codex-mcp-stale-worker-guard-001.md`
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

## Risk Assessment & Residual Risks

- **Over-broad termination risk**: Cleaning up active development processes is a primary risk. Mitigated by: (1) targeting only known Codex-configured command line patterns, (2) checking for parentless/detached worker states, (3) using a default report-only mode, and (4) exposing an explicitly-invoked cleanup flag that requires approval verification.

## Recommended Next Step

Prime Builder can proceed with implementation inside the approved `target_paths`. Run `python scripts/implementation_authorization.py begin --bridge-id gtkb-codex-mcp-stale-worker-guard` to generate the local implementation-start authorization packet before modifying files.

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
