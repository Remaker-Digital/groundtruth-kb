NEW
author_identity: prime-builder/codex-automation
author_harness_id: A
author_session_context_id: 019ee20d-e968-7b40-a570-f38cd6a7e3ef
author_model: gpt-5-codex
author_model_version: 2026-06-19
author_model_configuration: Codex desktop automation session; approval_policy=never; autonomous Prime Builder

# WI-4592 Cross-Harness Protocol Parity Tests - Slice 1

bridge_kind: prime_proposal
Document: agent-disposition-wi4592-cross-harness-protocol-parity-slice1
Version: 001
Status: NEW
Author: Prime Builder (Codex)
Date: 2026-06-19 UTC

Project Authorization: PAUTH-PROJECT-AGENT-DISPOSITION-PROTOCOL-ENFORCEMENT-UMBRELLA
Project: PROJECT-AGENT-DISPOSITION-AND-PROTOCOL-ENFORCEMENT
Work Item: WI-4592

target_paths: ["platform_tests/scripts/test_cross_harness_protocol_parity.py"]

implementation_scope: test_addition
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
external_mutation_in_scope: false
production_deployment_in_scope: false
credential_lifecycle_change_in_scope: false

---

## Summary

This child proposal requests a test-only first implementation slice for `WI-4592`: add a deterministic cross-harness protocol parity test module that reads existing GT-KB harness, dispatcher, prompt, hook, and fallback surfaces and reports drift without performing live mutations.

The slice is intentionally additive. It does not change harness behavior, hook registrations, dispatcher configuration, prompts, rules, source modules, MemBase records, cloud services, or credentials. It creates a parity test harness so future implementation slices can repair drift with explicit evidence instead of relying on chat memory or stale startup summaries.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Read config/rule files only; use no credential-shaped fixtures. | Bridge helper credential scan and focused review. | |
| CQ-PATHS-001 | Yes | Add one in-root platform test module. | Applicability preflight, target-path review, and no retired index check. | |
| CQ-COMPLEXITY-001 | Yes | Keep assertions table-driven and read-only. | Focused pytest. | |
| CQ-CONSTANTS-001 | Yes | Centralize expected harness names, statuses, and surface paths in the test module. | Tests fail with explicit drift messages. | |
| CQ-SECURITY-001 | Yes | Do not execute hooks, deployment commands, external services, or mutation commands. | Test implementation uses file reads/parsers only. | |
| CQ-DOCS-001 | Yes | Keep documentation in bridge/report evidence; test names explain checks. | Loyal Opposition review. | |
| CQ-TESTS-001 | Yes | This slice is a test addition. | `python -m pytest platform_tests/scripts/test_cross_harness_protocol_parity.py -q --tb=short`. | |
| CQ-LOGGING-001 | No | The test reports via pytest failures, not runtime logging. | N/A | No runtime component is added. |
| CQ-VERIFICATION-001 | Yes | Run focused pytest, Ruff check, Ruff format-check, bridge preflights, and retired index absence check. | Commands listed in the verification plan. | |

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol behavior must be role-correct across harnesses.
- `GOV-FILE-BRIDGE-PROTOCOL-001` - bridge actionability and disposition states must be interpreted consistently.
- `.claude/rules/file-bridge-protocol.md` - Prime Builder and Loyal Opposition have distinct actionability responsibilities.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - tests should verify harness surfaces do not imply PAUTH bypass.
- `REQ-HARNESS-REGISTRY-001` - durable harness identity and role registry must drive harness behavior.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner-action visibility and approval gates must be represented consistently across harnesses.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation proposals must cite applicable requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - proposal must link project, work item, authorization, and target paths explicitly.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must derive from cited requirements.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation must stay within the active PAUTH envelope.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - PAUTH mutation classes and forbidden operations define allowed scope.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - drift findings should be durable and reproducible.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable tests should govern cross-harness parity instead of informal memory.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - detected drift can later become lifecycle-tracked work rather than hidden chat context.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - tests must stay inside the GT-KB root and avoid application lifecycle mutation.
- `GOV-STANDING-BACKLOG-001` - `WI-4592` is an active ranked child work item under the current project backlog.

## Prior Deliberations

- `DELIB-20263455` - owner-approved Agent Disposition and Protocol Enforcement closeout planning, ranked work items, and umbrella formulation; includes `WI-4592` for cross-harness protocol parity tests.
- `DELIB-0862` - bridge-first governance and historical warning against ambiguous queue/workflow state.
- `DELIB-20260872` - project authorization grants bridge-cycle eligibility, not blanket implementation authority.
- `DELIB-2258` - implementation-start and work-intent gating are durable safety controls for protected mutations.
- `DELIB-20261178` - bridge/status authority must come from live versioned artifacts and current dispatcher state, not stale summaries.
- `bridge/agent-disposition-protocol-enforcement-umbrella-004.md` - planning-only GO that approved the ranked child sequence and requires concrete child proposals.
- `bridge/agent-disposition-wi4588-protected-mutation-guard-slice1-004.md` - VERIFIED guard slice that provides protected-write behavior the parity tests should observe.
- `bridge/agent-disposition-wi4589-external-mutation-gate-slice1-001.md` - pending proposal for external mutation gating; parity tests should be able to surface future external-action drift without executing external mutations.
- `bridge/agent-disposition-wi4591-bridge-disposition-workflow-slice1-001.md` - pending proposal for a shared bridge disposition matrix; this test-only slice can start by reading existing surfaces and later adapt to the verified matrix API.

## Owner Decisions / Input

- `DELIB-20263455` - owner directed the Agent Disposition and Protocol Enforcement project and ranked `WI-4592` as the cross-harness parity-test child item.
- `PAUTH-PROJECT-AGENT-DISPOSITION-PROTOCOL-ENFORCEMENT-UMBRELLA` - active bounded project authorization includes `WI-4592`; allows test addition/modification and forbids production deployment, credential lifecycle change, bridge bypass, self-review, retired bridge index recreation, and unapproved formal artifact mutation.
- `bridge/agent-disposition-protocol-enforcement-umbrella-004.md` - Loyal Opposition approved the planning sequence and required each child slice to receive its own concrete review.

No new owner decision is required for this proposal. The proposed slice adds read-only tests and does not change live harness behavior.

## Requirement Sufficiency

Existing requirements are sufficient for a test-only first slice. The work item names the harness set and the expected parity categories: startup role resolution, bridge dispatch actionability, protected-write preflights, owner-action visibility, tool/plugin assumptions, and hook fallback behavior.

This proposal is intentionally narrower than full `WI-4592` completion. It creates the first parity test module. Later child proposals may add source or config fixes for any drift the tests expose.

## Proposed Implementation

Add `platform_tests/scripts/test_cross_harness_protocol_parity.py` with read-only, table-driven tests that inspect existing files and structured configuration.

Initial checks:

- Harness identity/role surfaces include the expected durable harnesses and do not hardcode role behavior by vendor name alone.
- Dispatcher rule/config surfaces include Codex, Claude Code, Antigravity, Ollama, and OpenRouter routing entries or documented non-applicability.
- Bridge actionability surfaces preserve Prime Builder versus Loyal Opposition responsibility boundaries.
- Protected-write guard surfaces expose bridge GO, implementation authorization packet, and work-intent claim requirements for protected mutation attempts.
- Owner-action visibility guidance is present for blocking decisions and is not replaced by buried prose-only chat requirements.
- Hook/fallback surfaces distinguish hook-bearing harnesses from no-hook or partial-hook environments and point at deterministic fallback behavior.
- Tool/plugin capability assumptions are represented through the capability registry or existing parity scripts rather than invisible prompt-only expectations.

The tests must use file reads, TOML/JSON parsing when applicable, and deterministic assertions. They must not invoke hooks, spawn harnesses, run deployment commands, call external services, mutate MemBase, write bridge files, or edit runtime state.

## Explicit Non-Scope

- No source/config/rule/prompt/hook mutation in this slice.
- No live harness process spawning.
- No cloud, hosted-app, third-party API, production deployment, or credential mutation.
- No formal GOV/SPEC/PB/ADR/DCL mutation.
- No MemBase mutation.
- No `bridge/INDEX.md` recreation.
- No claim that `WI-4592` is complete after this slice; this is the first parity-test tranche.

## Spec-Derived Verification Plan

- `REQ-HARNESS-REGISTRY-001`: focused tests must inspect durable harness identity/role surfaces and fail on missing expected harness entries.
- `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-FILE-BRIDGE-PROTOCOL-001`, and `.claude/rules/file-bridge-protocol.md`: focused tests must verify bridge actionability expectations are represented in inspected surfaces.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`: focused tests must verify protected-write surfaces mention or expose bridge GO plus implementation authorization plus work-intent requirements.
- `SPEC-AUQ-POLICY-ENGINE-001`: focused tests must verify owner-action visibility requirements are represented for blocking owner decisions.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: proposal and implementation report must carry project metadata, linked specs, spec-to-test mapping, command evidence, and observed results.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`: tests must stay inside the active PAUTH's test-addition scope and avoid forbidden operations.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`: tests must use in-root paths only; `Test-Path bridge/INDEX.md` must remain `False`.

Implementation-report commands:

```text
python -m pytest platform_tests/scripts/test_cross_harness_protocol_parity.py -q --tb=short
python -m ruff check platform_tests/scripts/test_cross_harness_protocol_parity.py
python -m ruff format --check platform_tests/scripts/test_cross_harness_protocol_parity.py
python scripts/bridge_applicability_preflight.py --bridge-id agent-disposition-wi4592-cross-harness-protocol-parity-slice1
python scripts/adr_dcl_clause_preflight.py --bridge-id agent-disposition-wi4592-cross-harness-protocol-parity-slice1
Test-Path bridge/INDEX.md
```

## Acceptance Criteria

- A read-only cross-harness protocol parity test module exists and can run independently.
- Tests inspect Codex, Claude Code, Antigravity, Ollama, and OpenRouter-related surfaces where represented in the repo.
- Tests cover startup role resolution, bridge actionability, protected-write preflight requirements, owner-action visibility, tool/plugin capability assumptions, and hook fallback behavior at least at first-slice breadth.
- The implementation produces reproducible drift failures without mutating live project state or requiring external services.

## Risk / Rollback

The main risk is brittle tests over narrative text. The implementation should prefer structured TOML/JSON/config files and stable helper/source constants where available, using narrative text checks only for hard operating-contract phrases that already govern harness behavior.

Rollback is path-local deletion of `platform_tests/scripts/test_cross_harness_protocol_parity.py` before follow-on slices depend on it.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered bridge file for `agent-disposition-wi4592-cross-harness-protocol-parity-slice1`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`test:` - the approved implementation would add read-only cross-harness protocol parity tests.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
