GO

# agent-red-deploy-pipeline-phase0-path-repair — Loyal Opposition Verdict

bridge_kind: lo_verdict
Document: agent-red-deploy-pipeline-phase0-path-repair
Version: 002
Author: OpenRouter Loyal Opposition (F)
Date: 2026-06-30T19:28:00Z

author_identity: OpenRouter Loyal Opposition
author_harness_id: F
author_session_context_id: openrouter-harness-f-lo-review-2026-06-30-agent-red-deploy-pipeline-phase0-path-repair
author_model: deepseek/deepseek-v4-pro
author_model_version: deepseek-v4-pro
author_model_configuration: OpenRouter harness shim; route deepseek-v4-pro; skill bridge-review; guarded tools Read, Write, Edit, Grep, Glob, Bash

Prior Verdict: bridge/agent-red-deploy-pipeline-phase0-path-repair-001.md (NEW, Prime Builder A)

---

## Verdict: GO

The Prime Builder's path-repair proposal for the Agent Red deploy pipeline is approved for implementation. The proposal correctly identifies a misalignment between the application isolation contract and the actual script placement, and proposes a narrow, well-bounded fix.

## Applicability Preflight

```
warning: bridge preflight missing parent directories: tests/unit/helpers/run_mocked_pipeline.py, tests/unit/test_deploy_pipeline_production.py
## Applicability Preflight

- packet_hash: sha256:b141a8f98d7a5e921affa2f2b2923edf6f491f63b1332fa1bd13857f27485a07
- bridge_document_name: agent-red-deploy-pipeline-phase0-path-repair
- content_source: bridge_file_operative
- content_file: bridge/agent-red-deploy-pipeline-phase0-path-repair-001.md
- operative_file: bridge/agent-red-deploy-pipeline-phase0-path-repair-001.md
- preflight_passed: true
- warnings.missing_parent_dirs: ["tests/unit/helpers/run_mocked_pipeline.py", "tests/unit/test_deploy_pipeline_production.py"]
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 | advisory | no | content:artifact, content:deliberation, content:MemBase |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | blocking | yes | path:applications/**, content:applications/, content:Agent Red |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | advisory | no | content:blocked, content:verified |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | blocking | yes | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | blocking | yes | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | advisory | no | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| GOV-FILE-BRIDGE-AUTHORITY-001 | blocking | yes | doc:*, path:bridge/** |
```

## ADR/DCL Clause Preflight (Slice 2)

```
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: agent-red-deploy-pipeline-phase0-path-repair
- Operative file: bridge\agent-red-deploy-pipeline-phase0-path-repair-001.md
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT | ADR-ISOLATION-APPLICATION-PLACEMENT-001 | may_apply | — | blocking | blocking |
| GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL | GOV-FILE-BRIDGE-AUTHORITY-001 | must_apply | yes | blocking | blocking |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS | DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | must_apply | yes | blocking | blocking |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING | DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | must_apply | yes | blocking | blocking |
| GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS | GOV-STANDING-BACKLOG-001 | may_apply | — | blocking | blocking |

Slice 2 mandatory gate: clauses with enforcement_mode = "blocking" and
must_apply applicability fail the gate (exit 5) when evidence is absent.
```

## Analysis

### Authorization Chain

The proposal cites an active project authorization `PAUTH-PROJECT-AGENT-RED-DEPLOY-PIPELINE-AGENT-RED-DEPLOY-PIPELINE-BOUNDED-IMPLEMENTATION-2026-06-23`, backed by owner decision `DELIB-20265586`. The PAUTH includes `WI-3172`, the sole open work item in `PROJECT-AGENT-RED-DEPLOY-PIPELINE`. No prior bridge threads exist for `WI-3172`, so this is a clean first proposal.

### Evidence Quality

The Prime Builder provides concrete, reproducible evidence: pytest results (30 collected, 27 failed — specifically from missing app-local scripts), ripgrep confirmation that deploy scripts exist at root-level `scripts/` not under `applications/Agent_Red/scripts/`, and `.gtkb-app-isolation.json` showing bucket `A` allocation for app-local scripts. This evidence is internally consistent and verifiable.

### Specification Coverage

All blocking specs are cited. `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `ADR-APPLICATION-ISOLATION-CONTRACT-001` are correctly identified as the governing isolation requirements. `GOV-16` is correctly cited as the no-autonomous-deployment boundary. `DCL-APP-ROOT-MINIMIZATION-001` is relevant and correctly cited.

### Scope and Boundaries

The `target_paths` list is narrow and appropriate: three deploy scripts to be created/relocated under `applications/Agent_Red/scripts/`, plus two test files. `external_deployment_in_scope: false` is correctly declared and critical — this proposal does not authorize any real deployment. `kb_mutation_in_scope: false` is also correct.

### Preflight Advisory: Missing Parent Directories

The applicability preflight warns that `tests/unit/helpers/run_mocked_pipeline.py` and `tests/unit/test_deploy_pipeline_production.py` have no existing parent directories in `target_paths`. These are target files under `applications/Agent_Red/tests/unit/`, and the Prime Builder should ensure parent directories exist or are scaffolded during implementation. This is advisory context, not a blocking issue.

### Implementation Concern Noted

The proposal specifies "path repair" but does not detail whether this means: (a) copying root-level scripts to the app root, (b) creating wrappers that import from root-level, or (c) rewriting scripts for app-root placement. The implementation report must make this choice explicit and justify it against `ADR-APPLICATION-ISOLATION-CONTRACT-001`. Additionally, root-level `scripts/deploy_pipeline.py`, `scripts/deploy_config.py`, and `scripts/deploy.py` must not be silently abandoned — their disposition (deprecation, removal, or wrapper) must be documented.

### Clause Preflight

Zero blocking gaps. All three `must_apply` clauses have evidence. The `may_apply` clause `CLAUSE-IN-ROOT` from `ADR-ISOLATION-APPLICATION-PLACEMENT-001` correctly flags as applicable (applications-scoped path repair) but without blocking evidence requirement at proposal stage.

## Conditions of GO

1. Implementation must not perform any real staging or production deployment (`GOV-16`).
2. Root-level deploy scripts (`scripts/deploy_pipeline.py`, `scripts/deploy_config.py`, `scripts/deploy.py`) must have their disposition documented in the implementation report — removal, deprecation wrapper, or explicit justification for keeping them.
3. The implementation must include `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` test evidence: the 27 currently-failing tests must pass after path repair, and any new tests must be linked to `SPEC-1615` requirements.
4. The three advisory-spec gaps should be assessed during implementation and cited if relevant.
5. The missing parent directories flagged by the applicability preflight must be created or their absence justified.

## Prior Deliberations

- `DELIB-20265586` — owner decision backing the active project authorization for `PROJECT-AGENT-RED-DEPLOY-PIPELINE` and `WI-3172`. (Source: proposal-001)
- `DELIB-20265219` — prior deliberation cited in proposal-001 (content truncated in bridge file). (Source: proposal-001)
- `DELIB-20265220` — prior deliberation cited in proposal-001 (content truncated in bridge file). (Source: proposal-001)
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — requires GT-KB adopter applications to live under `applications/<name>/`. (Source: proposal-001 specification links)
- `ADR-APPLICATION-ISOLATION-CONTRACT-001` — requires Agent Red lifecycle surfaces to be scoped to `applications/Agent_Red/` when they govern the Agent Red application. (Source: proposal-001 specification links)
- `SPEC-1615` — owns the scripted build/deploy pipeline behavior, dry-run/mocked execution expectations, diagnostics, and Phase 0 environment validation context. (Source: proposal-001 specification links)
- `GOV-16` — forbids autonomous staging or production deployments and requires explicit owner approval immediately before any real deployment. (Source: proposal-001 specification links)
- `DCL-APP-ROOT-MINIMIZATION-001` — constrains Agent Red app-root artifacts and registry justification for app-local scripts. (Source: proposal-001 specification links)