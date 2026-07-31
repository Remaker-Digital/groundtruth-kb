NEW

# WI-4926 - Provider Readiness Credential And Live-Probe Contract

bridge_kind: prime_proposal
Document: gtkb-wi4926-provider-readiness-contract
Version: 001
Author: Prime Builder (Codex)
Date: 2026-07-06T02:31:00Z

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Prime Builder session; default Codex desktop execution

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-WI4926-PROVIDER-READINESS-20260706
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4926

target_paths: ["docs/harness-parity-phase-2.md", "docs/harness-parity-phase-2-matrix.md", "config/harness-parity/phase2-waivers.toml", "config/agent-control/harness-capability-registry.toml", "scripts/check_harness_parity.py", "scripts/ollama_harness.py", "scripts/openrouter_harness.py", "platform_tests/scripts/test_check_harness_parity.py", "platform_tests/scripts/test_harness_parity_phase2.py", "platform_tests/scripts/test_ollama_harness.py", "platform_tests/scripts/test_ollama_provider_scoped_routing.py", "platform_tests/scripts/test_openrouter_harness.py"]

implementation_scope: documentation_plus_assertions
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4926 is a low-scope Harness Parity Phase 2 follow-up from the WI-4904 audit. The gap is not that the provider harnesses should be activated or that credentials should be changed; the gap is that GT-KB lacks a governed, test-backed contract explaining which provider-readiness commands require live credentials, how `.env.local` loading is treated, how missing or invalid credentials classify, and which readiness paths must stay mocked.

This proposal scopes a documentation plus assertion-coverage slice for the Ollama and OpenRouter provider-harness surfaces. The implementation should publish the readiness contract in the Harness Parity Phase 2 documentation and matrix, cross-reference the Phase 2 waiver registry, and add tests/assertions that prove the documented skip/configuration-failure/provider-outage distinctions. Source changes are allowed only when a minimal classifier fix is required to make the documented contract true.

The proposal explicitly excludes credential lifecycle changes, provider key rotation, topology activation, production deployment, direct harness-to-harness invocation, broad status mutation, and live provider calls outside dispatcher/control-plane or owner/manual operation.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected implementation work requires this proposal, Loyal Opposition review, latest `GO`, implementation-start authorization, implementation report, and verification before WI-4926 can be terminal.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the cited PAUTH bounds the owner-approved WI-4926 implementation path.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - project authorization supplies owner approval evidence only; it does not bypass bridge `GO`, target paths, implementation report, or verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this implementation proposal must cite all governing bridge, harness, credential, and dispatcher requirements before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the header binds this proposal to the active project authorization, project, and work item.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must map the readiness contract and classifier assertions to executed tests.
- `GOV-STANDING-BACKLOG-001` - WI-4926 remains the MemBase backlog authority and must close only through bridge/report/verification evidence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the decision, PAUTH, proposal, tests, report, and terminal state must remain traceable as durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the work should preserve the artifact graph rather than relying on scratchpad or chat-only state.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-4926 moves through explicit lifecycle states from owner-gated backlog item to proposal, implementation, verification, and terminal disposition.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - provider-harness readiness belongs to the harness onboarding capability floor and must distinguish required artifacts, capability declarations, and machine-checkable assertions.
- `GOV-ENV-LOCAL-AUTHORITY-001` - credential and runtime configuration values must come from the authoritative `.env.local` surface; documentation may cite variable names, placeholders, and fake examples only.
- `ADR-OLLAMA-HARNESS-ADOPTION-001` - Ollama harness adoption establishes the shim/routing and governance foundation that this readiness contract must not contradict.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` - any Ollama readiness assertion touching mutating tool capability must preserve fail-closed guard-adapter behavior.
- `SPEC-INTAKE-21c5b3` - direct harness-to-harness invocation is prohibited; live readiness proof must use dispatcher/control-plane surfaces or owner/manual operation.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - bridge and harness safety controls must remain enforceable across Codex, Claude Code, Ollama, OpenRouter, Cursor, and future harness paths.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatch remains a GT-KB-owned daemon/control-plane service; harnesses consume work rather than directly controlling each other.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all GT-KB harness/provider readiness work must stay within the GT-KB root and must not silently resolve to adopter application lifecycle surfaces.
- `SPEC-CODE-QUALITY-CHECKLIST-001` - the implementation report must satisfy the applicable documentation, test, security, and verification evidence expectations, especially for credential-handling surfaces.

## Prior Deliberations

- `DELIB-20260706-WI4926-IMPLEMENTATION-APPROVAL` - owner authorized WI-4926 during the backlog-completion pass and bounded the work to governed PAUTH plus bridge proposal flow.
- `DELIB-20260663` - owner approved Ollama Phase 1 with heavy governance, static routing, full tool parity under guardrails, and a procedural plus machine-checkable harness onboarding GOV.
- `DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN` - owner prohibited one harness directly launching or commanding another as a fallback path; this proposal applies that rule to readiness probing.
- WI-4926 backlog row - records the WI-4904 audit follow-up: residual documentation gap from spurious draft reconciliation; scope is documentation plus assertion coverage, with no credential rotation, topology activation, or harness behavior change unless a minimal classifier fix is required.

The required Deliberation Archive semantic searches for "WI-4926 provider readiness credential live probe", "OpenRouter provider readiness credential live probe harness", and "Ollama harness credential live probe provider outage" returned no additional direct matches during drafting.

## Owner Decisions / Input

Owner approval is recorded by `DELIB-20260706-WI4926-IMPLEMENTATION-APPROVAL` and active authorization `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-WI4926-PROVIDER-READINESS-20260706`.

The approved scope is documentation plus assertion coverage for provider-readiness credential/live-probe contracts. The owner did not approve credential lifecycle work, provider key rotation, topology activation, production deployment, broad status mutation, direct harness-to-harness invocation, or live provider calls outside dispatcher/control-plane or owner/manual operation.

## Requirement Sufficiency

Existing requirements sufficient. WI-4926 defines the concrete gap and scope. `GOV-HARNESS-ONBOARDING-CONTRACT-001`, `GOV-ENV-LOCAL-AUTHORITY-001`, `ADR-OLLAMA-HARNESS-ADOPTION-001`, `DCL-OLLAMA-TOOL-PARITY-GATE-001`, `SPEC-INTAKE-21c5b3`, and `ADR-DISPATCHER-ARCHITECTURE-001` provide enough governance to distinguish documentation/assertion work from forbidden credential or dispatch-control changes.

If implementation discovers that the currently implemented classifier behavior contradicts the intended contract, the allowed repair is a minimal in-root classifier fix plus test coverage inside the listed target paths. Broader harness behavior, topology, or credential changes require a separate proposal.

## Spec-Derived Verification Plan

| Requirement | Verification |
|---|---|
| Readiness contract is documented | Update Harness Parity Phase 2 docs/matrix to state which readiness checks are mocked, which require live credentials, how `.env.local` is loaded, and how missing credentials classify. |
| Credential values stay out of governed docs and tests | Review changed files and run repository credential/bridge scans as applicable; docs may use variable names, placeholders, and fake examples only per `GOV-ENV-LOCAL-AUTHORITY-001`. |
| Phase 2 waiver registry cross-reference exists | Update `config/harness-parity/phase2-waivers.toml` or the docs to cross-reference relevant waiver entries and explain gap-to-waiver disposition. |
| Missing credential, invalid credential, provider outage, and mocked path semantics are asserted | Add or update focused tests for Ollama/OpenRouter readiness classification without real provider calls by default. |
| Live probes do not direct-invoke peer harnesses | Tests or static assertions confirm any live-provider probe path is dispatcher/control-plane-compatible or explicitly owner/manual, not one harness launching another. |
| Minimal classifier fixes stay bounded | If source changes are required, implementation report maps each source change to the documented contract and proves no topology activation or credential lifecycle behavior was added. |
| Bridge/project authorization lifecycle | Implementation runs only after latest `GO` and `implementation_authorization.py begin --bridge-id gtkb-wi4926-provider-readiness-contract`; the report cites target-path authorization evidence. |

Minimum expected verification commands after implementation:

```text
python -m pytest platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_ollama_provider_scoped_routing.py -q --tb=short
python -m pytest platform_tests/scripts/test_check_harness_parity.py platform_tests/scripts/test_harness_parity_phase2.py -q --tb=short
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4926-provider-readiness-contract --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4926-provider-readiness-contract
```

## Pre-Filing Self-Check

Draft preflight evidence before filing:

- `python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-propose-drafts/gtkb-wi4926-provider-readiness-contract-001.md --json` -> `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.
- `python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-propose-drafts/gtkb-wi4926-provider-readiness-contract-001.md` -> exit 0, blocking gaps 0.

## Risk / Rollback

Primary risk is accidentally turning a documentation slice into a provider-topology or credential-lifecycle change. Keep the implementation doc/test first, use mocked readiness paths by default, and require explicit evidence before any minimal classifier fix. If tests or docs regress, revert the WI-4926 changes as one scoped commit; no credential or topology state should need rollback because it is out of scope.

## Bridge Filing

This proposal is filed as `bridge/gtkb-wi4926-provider-readiness-contract-001.md`. Dispatcher/TAFE state plus the numbered bridge file chain are the live workflow state; no aggregate queue artifact is created or updated.

## Recommended Commit Type

docs - the expected implementation is primarily documentation plus assertion coverage, with only minimal classifier fixes if the documented contract exposes a small inconsistency.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
