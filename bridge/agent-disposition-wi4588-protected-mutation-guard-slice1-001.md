NEW

# WI-4588 Protected Mutation Guard Core - Slice 1

bridge_kind: prime_proposal
Document: agent-disposition-wi4588-protected-mutation-guard-slice1
Version: 001
Author: Prime Builder (Codex)
Date: 2026-06-16 UTC

author_identity: prime-builder/codex-auto-dispatch
author_harness_id: A
author_session_context_id: 2026-06-16T18-25-55Z-prime-builder-A-4c4e9e
author_model: GPT-5 Codex
author_model_version: 2026-06-16
author_model_configuration: Codex headless bridge auto-dispatch; approval_policy=never

Project Authorization: PAUTH-PROJECT-AGENT-DISPOSITION-PROTOCOL-ENFORCEMENT-UMBRELLA
Project: PROJECT-AGENT-DISPOSITION-AND-PROTOCOL-ENFORCEMENT
Work Item: WI-4588

target_paths: ["scripts/protected_mutation_guard.py", "platform_tests/scripts/test_protected_mutation_guard.py"]

implementation_scope: source,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This child proposal consumes only the planning authority granted by `bridge/agent-disposition-protocol-enforcement-umbrella-004.md` and requests a concrete first implementation slice for `WI-4588`.

The slice adds a reusable deterministic protected-mutation guard core plus focused tests. It does not edit hook registrations, harness startup files, bridge protocol rules, governance records, cloud/deployment surfaces, credentials, or retired bridge aggregate artifacts. Hook and harness integration remain follow-on child slices after this core contract is reviewed and verified.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Keep fixtures synthetic and avoid credential-shaped examples. | Bridge helper credential scan and focused review. | |
| CQ-PATHS-001 | Yes | Keep implementation inside declared in-root source and test target paths. | Applicability preflight, target-path review, and no retired index check. | |
| CQ-COMPLEXITY-001 | Yes | Add a small deterministic decision module rather than broad prompt-only policy. | Focused unit tests for allow and deny matrix. | |
| CQ-CONSTANTS-001 | Yes | Centralize reason codes and result statuses in the new module. | Ruff and focused tests asserting stable reason codes. | |
| CQ-SECURITY-001 | Yes | Preserve fail-closed behavior for protected targets without secrets or external calls. | Negative-path tests for missing GO, missing packet, and missing claim. | |
| CQ-DOCS-001 | Yes | Keep documentation limited to bridge proposal and report evidence for this slice. | LO review of proposal and report plus unchanged active docs. | |
| CQ-TESTS-001 | Yes | Add focused tests for protected and unprotected mutation decisions. | `python -m pytest platform_tests/scripts/test_protected_mutation_guard.py -q --tb=short`. | |
| CQ-LOGGING-001 | Yes | Return structured reasons suitable for later hook receipts without writing live logs in this slice. | Result schema assertions in tests. | |
| CQ-VERIFICATION-001 | Yes | Run spec-derived focused pytest, Ruff check, Ruff format-check, and no-index absence check before reporting implementation. | Commands listed in the verification plan. | |

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected mutations require bridge authority and role-correct bridge handling.
- `.claude/rules/file-bridge-protocol.md` - implementation must use the file bridge lifecycle instead of alternate queues.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - project authorization does not bypass bridge review or implementation-start gates.
- `REQ-HARNESS-REGISTRY-001` - harness identity and role resolution must come from the durable registry.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner-action and authorization policy must be deterministic and auditable.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation proposals must cite applicable requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - proposal must link project, work item, authorization, and target paths explicitly.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must derive from cited requirements.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex/native hook gaps require explicit fallback and self-enforcement behavior.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - implementation artifacts should preserve durable evidence and future-work boundaries.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifacts govern work selection and traceability.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - cleanup and follow-on findings should become lifecycle-tracked artifacts when appropriate.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - GT-KB platform work must stay within the GT-KB root and preserve application isolation.
- `GOV-STANDING-BACKLOG-001` - `WI-4588` is the current ranked work item under the active project backlog.

## Prior Deliberations

- `DELIB-20263455` - owner-approved Agent Disposition and Protocol Enforcement closeout planning, ranked work items, and umbrella formulation.
- `DELIB-0862` - bridge-first governance and historical warning against ambiguous scope-only GO artifacts.
- `DELIB-20260872` - project authorization grants bridge-cycle eligibility, not blanket implementation authority.
- `DELIB-2258` - implementation-start and work-intent gating are durable safety controls for protected mutations.
- `DELIB-20261178` - bridge/status authority must come from live versioned artifacts and current dispatcher state, not stale summaries.
- `DELIB-S367-PAUTH-BRIDGE-PROTOCOL-RELIABILITY-AMENDMENT-WORK-INTENT` - prior work-intent registry authorization precedent for bridge-protocol reliability.
- `bridge/agent-disposition-protocol-enforcement-umbrella-004.md` - planning-only GO that permits filing this concrete `WI-4588` child proposal and does not authorize protected implementation by itself.

## Owner Decisions / Input

- `DELIB-20263455` - owner directed closeout planning, ranked work items, and umbrella proposal formulation for the Agent Disposition and Protocol Enforcement project.
- `PAUTH-PROJECT-AGENT-DISPOSITION-PROTOCOL-ENFORCEMENT-UMBRELLA` - active bounded project authorization for `WI-4588` through `WI-4593`.
- `bridge/agent-disposition-protocol-enforcement-umbrella-004.md` - Loyal Opposition approved only the planning shape and authorized Prime Builder to file the concrete `WI-4588` child proposal.

No new owner decision is required for this proposal. This bridge asks Loyal Opposition to review a narrow source and test implementation slice before any protected implementation mutation occurs.

## Requirement Sufficiency

Existing requirements sufficient. The linked bridge authority, project authorization, work item, harness-registry, Codex fallback, and spec-derived verification requirements cover this narrow implementation proposal.

This proposal is intentionally narrower than full `WI-4588` completion. It establishes the reusable decision contract that later Codex, Claude Code, Antigravity, and dispatched-worker hook surfaces can call without each reimplementing bridge, packet, and claim checks.

## Proposed Implementation

Add `scripts/protected_mutation_guard.py` as a deterministic decision module that evaluates a proposed mutation attempt using structured inputs:

- harness identity and role context;
- tool/action class and command metadata;
- proposed target paths resolved under the GT-KB root;
- bridge thread slug, status, and version evidence;
- implementation-start packet status and target-path match;
- current work-intent claim state;
- protected-path classification.

The module returns a structured allow/deny result with machine-readable reason codes such as `not_protected`, `missing_bridge_go`, `missing_implementation_packet`, `stale_implementation_packet`, `target_out_of_scope`, `missing_or_stale_claim`, `target_outside_project_root`, and `forbidden_operation`.

The implementation should reuse existing project helpers where practical instead of creating a competing bridge parser, implementation authorization model, or work-intent registry. Where existing helpers are too command-oriented to call directly from tests, this slice may introduce small adapter functions inside the new module only.

Add `platform_tests/scripts/test_protected_mutation_guard.py` with isolated fixture coverage for:

- unprotected targets are allowed without bridge evidence;
- protected targets deny when bridge GO is missing;
- protected targets deny when the implementation packet is missing, stale, or target paths do not match;
- protected targets deny when no current work-intent claim exists;
- protected targets allow only when GO, packet, claim, and target scope align;
- outside-root target paths deny deterministically;
- reason codes remain stable for later hook integrations.

## Explicit Non-Scope

- No `.claude/hooks/`, `.codex/hooks.json`, `.codex/gtkb-hooks/`, or startup-control mutation in this slice.
- No formal GOV/SPEC/PB/ADR/DCL mutation.
- No cloud, deployment, credential, or external-service mutation.
- No `bridge/INDEX.md` recreation.
- No claim that `WI-4588` is complete after this slice; follow-on child proposals must wire the core into live harness surfaces.

## Spec-Derived Verification Plan

- `GOV-FILE-BRIDGE-AUTHORITY-001`, `.claude/rules/file-bridge-protocol.md`, and `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`: `python -m pytest platform_tests/scripts/test_protected_mutation_guard.py -q --tb=short` must show fail-closed protected mutation behavior without GO, packet, or claim and allow behavior only when all are aligned.
- `REQ-HARNESS-REGISTRY-001` and `ADR-CODEX-HOOK-PARITY-FALLBACK-001`: focused tests must cover harness identity and role inputs plus stable reason codes for later hook integration; implementation report must state that live hook wiring remains follow-on.
- `SPEC-AUQ-POLICY-ENGINE-001`: tests and implementation report must show owner and authorization decisions become structured results rather than prose-only blocks.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: proposal and post-implementation report must carry project metadata, linked specs, spec-to-test mapping, command evidence, and observed results.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`: tests must use in-root fixtures only; `Test-Path bridge/INDEX.md` must remain `False`.

Implementation-report commands:

```text
python -m pytest platform_tests/scripts/test_protected_mutation_guard.py -q --tb=short
python -m ruff check scripts/protected_mutation_guard.py platform_tests/scripts/test_protected_mutation_guard.py
python -m ruff format --check scripts/protected_mutation_guard.py platform_tests/scripts/test_protected_mutation_guard.py
Test-Path bridge/INDEX.md
```

## Pre-Filing Preflight

Prime Builder must run the following against the completed candidate content before filing:

```text
python scripts/bridge_applicability_preflight.py --bridge-id agent-disposition-wi4588-protected-mutation-guard-slice1 --content-file .gtkb-state/propose-drafts/agent-disposition-wi4588-protected-mutation-guard-slice1-001.md
python scripts/adr_dcl_clause_preflight.py --bridge-id agent-disposition-wi4588-protected-mutation-guard-slice1 --content-file .gtkb-state/propose-drafts/agent-disposition-wi4588-protected-mutation-guard-slice1-001.md
```

Expected: applicability preflight passes with `missing_required_specs: []` and `missing_advisory_specs: []`; ADR/DCL clause preflight exits 0 with no blocking gaps. Observed results are recorded in the auto-dispatch final summary and can be re-run by Loyal Opposition from the filed bridge content.

## Acceptance Criteria

- A reusable guard module returns structured allow/deny results for protected mutation attempts.
- The module enforces the bridge GO plus implementation-start packet plus current work-intent claim contract for protected paths.
- Tests demonstrate both denial and success cases without mutating live project state or relying on stale dashboard/index artifacts.
- The implementation report identifies follow-on hook/harness integration work rather than silently claiming full `WI-4588` closure.

## Risk / Rollback

The main risk is duplicating logic already present in `implementation_start_gate.py` and `implementation_authorization.py`. The implementation should mitigate this by reusing existing helpers and keeping the new module focused on decision composition and structured results.

Rollback is path-local deletion of `scripts/protected_mutation_guard.py` and `platform_tests/scripts/test_protected_mutation_guard.py` before any follow-on integration consumes them.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered bridge file for `agent-disposition-wi4588-protected-mutation-guard-slice1`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`feat:` - the approved implementation would add a new reusable guard module plus tests.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
