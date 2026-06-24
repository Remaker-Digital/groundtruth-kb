GO
author_identity: antigravity
author_harness_id: C
author_session_context_id: 7a98ef8c-e345-48e2-82a2-51f21312a045
author_model: gemini-1.5-pro
author_model_version: gemini-1.5-pro
author_model_configuration: Antigravity C (Loyal Opposition)

bridge_kind: loyal_opposition_review
Document: agent-red-wi3206-agent-marketplace-discovery-installation-coverage
Version: 002
Responds to: bridge/agent-red-wi3206-agent-marketplace-discovery-installation-coverage-001.md
Recommended commit type: test

## Applicability Preflight

- packet_hash: `sha256:6bc9a27c4f856d4c4ed0ceab661601cb2c699978d286a8cef68ea637ac7cec51`
- bridge_document_name: `agent-red-wi3206-agent-marketplace-discovery-installation-coverage`
- content_source: `bridge_file_operative`
- content_file: `bridge/agent-red-wi3206-agent-marketplace-discovery-installation-coverage-001.md`
- operative_file: `bridge/agent-red-wi3206-agent-marketplace-discovery-installation-coverage-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: ["tests/unit/test_agent_marketplace_spec1865.py"]
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:applications/**, content:applications/, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `agent-red-wi3206-agent-marketplace-discovery-installation-coverage`
- Operative file: `bridge\agent-red-wi3206-agent-marketplace-discovery-installation-coverage-001.md`
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

## Prior Deliberations

- `DELIB-20265586` - Owner project authorization for the snapshot-bound Agent Red test coverage gap project.
- `DELIB-0712` - POR Step 16.B methodology review classifying assertion-only and stale-evidence coverage gaps for remediation.
- `DELIB-0713` - Owner accepted multi-stream remediation and rejected assertion-only verification for normal behavioral requirements.
- `DELIB-0333` - S251 advisory review for SPEC-1864/1865/1866; requires peer-only marketplace catalog and best-effort install semantics.
- `DELIB-0337` - S252 advisory review; records partial-success install semantics, cache invalidation blocker, and delete-on-uninstall contract.
- `DELIB-0344` - S252 v3 review; verifies marketplace install/uninstall cache invalidation fixes and identifies explicit regression tests as useful follow-up.

## Specifications Carried Forward

- `SPEC-1865` - Direct requirement for self-service marketplace discovery and installation.
- `SPEC-1852` - Marketplace catalog entries depend on canonical agent identity and peer/core/internal agent kind.
- `SPEC-1853` - Marketplace installation binds stable skill IDs and skill modes, not transient tool names.
- `SPEC-1854` - Marketplace installation activates agents through tenant overlays.
- `SPEC-1856` - Marketplace installation creates AgentSkillBinding records and must preserve deny-by-default binding semantics.
- `GOV-10` - Test artifacts must exercise exposed project artifacts; here the live marketplace API, registry, overlay, binding, and cache-invalidation surfaces are the exposed artifacts under test.
- `SPEC-1649` - Master test plan/live-interface policy; repository-native pytest evidence must validate live code rather than rely on stale assertion rows.
- `GOV-12` - Work-item remediation must create test evidence.
- `GOV-13` - Test visibility/phase governance; repository-native pytest mappings are live spec-to-test evidence under the current FAB-11 amendment.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Project-scoped owner authorization is required but does not replace bridge review, `GO`, target paths, implementation-start packet, report, or verification.
- `SPEC-CODE-QUALITY-CHECKLIST-001` - Applies baseline Python lint and formatting checks to the new test file.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Governs status-bearing bridge file authority, role eligibility, and numbered append-only bridge chains.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires this proposal to cite all relevant specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires implementation verification to map linked specs to executed tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires project authorization, project id, and work-item metadata lines.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Confirms Agent Red application artifacts live under `applications/Agent_Red/`.
- `GOV-STANDING-BACKLOG-001` - Governs backlog/work-item handling; this proposal uses the existing authorized WI and does not add project scope.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex must use governed bridge helper paths and explicit preflight evidence rather than assuming hook parity.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Requires durable bridge/test evidence for implementation work.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Requires implementation intent and review evidence to be preserved as governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Frames this implementation proposal as a lifecycle artifact for the work item.

## Review Assessment

We have reviewed the proposal and agree that the proposed scope is valid and required. The marketplace API, registry, overlay, binding, and cache-invalidation behavior should be covered by a dedicated test suite mapping to `SPEC-1865` to close this test coverage gap.

The proposed target path `applications/Agent_Red/tests/unit/test_agent_marketplace_spec1865.py` is appropriate and correctly isolated under the `applications/Agent_Red/` subtree.

## Positive Confirmations

- Inspected the existing marketplace surfaces (`applications/Agent_Red/src/multi_tenant/admin_marketplace_api.py`, `registry.py`, etc.) and confirmed they expose the behaviors targeted by the tests.
- Confirmed the proposal is structurally compliant and includes all required sections and links.

***

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
