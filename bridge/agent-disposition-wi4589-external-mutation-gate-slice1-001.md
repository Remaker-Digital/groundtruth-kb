NEW
author_identity: prime-builder/codex-automation
author_harness_id: A
author_session_context_id: 019ee20d-e968-7b40-a570-f38cd6a7e3ef
author_model: gpt-5-codex
author_model_version: 2026-06-19
author_model_configuration: Codex desktop automation session; approval_policy=never; autonomous Prime Builder

# WI-4589 External Mutation Authorization Gate - Slice 1

bridge_kind: prime_proposal
Document: agent-disposition-wi4589-external-mutation-gate-slice1
Version: 001
Status: NEW
Author: Prime Builder (Codex)
Date: 2026-06-19 UTC

Project Authorization: PAUTH-PROJECT-AGENT-DISPOSITION-PROTOCOL-ENFORCEMENT-UMBRELLA
Project: PROJECT-AGENT-DISPOSITION-AND-PROTOCOL-ENFORCEMENT
Work Item: WI-4589

target_paths: ["scripts/external_mutation_guard.py", "platform_tests/scripts/test_external_mutation_guard.py"]

implementation_scope: source,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
external_mutation_in_scope: false
production_deployment_in_scope: false
credential_lifecycle_change_in_scope: false

---

## Summary

This child proposal requests a narrow first implementation slice for `WI-4589`: add a deterministic external-mutation authorization gate and focused tests. The slice classifies proposed cloud deployment, hosted-application, third-party-service, and credentials-adjacent external actions before execution, then returns a structured allow/deny decision that callers can use before any external side effect occurs.

The slice builds on the already-verified `WI-4588` protected mutation guard and `WI-4590` post-action receipt contract without modifying those verified files. It does not execute deployments, call cloud providers, mutate third-party services, update credentials, push commits, or wire live hook surfaces. Hook, CLI, deployment-script, and harness integration remain follow-on child slices after this additive core is reviewed and verified.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Keep examples synthetic and avoid credential-shaped literals. | Bridge helper credential scan and focused review. | |
| CQ-PATHS-001 | Yes | Restrict implementation to the declared in-root source and test target paths. | Applicability preflight, target-path review, and no retired index check. | |
| CQ-COMPLEXITY-001 | Yes | Add a small policy module with explicit dataclasses/enums rather than broad prose-only checks. | Focused pytest matrix for action classes, authorities, and receipts. | |
| CQ-CONSTANTS-001 | Yes | Centralize action classes, authority fields, reason codes, and verdict statuses. | Tests assert stable values. | |
| CQ-SECURITY-001 | Yes | Fail closed before external side effects unless authority, bridge state when applicable, and receipt plan are present. | Negative tests for missing authority, missing GO, missing receipt plan, and prohibited classes. | |
| CQ-DOCS-001 | Yes | Keep documentation to bridge proposal/report evidence for this slice. | Loyal Opposition review. | |
| CQ-TESTS-001 | Yes | Add focused unit tests for allow/deny behavior without external network calls. | `python -m pytest platform_tests/scripts/test_external_mutation_guard.py -q --tb=short`. | |
| CQ-LOGGING-001 | Yes | Return structured receipt requirements rather than writing live logs in the core slice. | Test result fields and receipt-plan assertions. | |
| CQ-VERIFICATION-001 | Yes | Run spec-derived pytest, Ruff check, Ruff format-check, bridge preflights, and retired index absence check before reporting implementation. | Commands listed in the verification plan. | |

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - deployment, configuration, repository-state, and external mutation work must use the governed bridge process where applicable.
- `.claude/rules/file-bridge-protocol.md` - status-bearing numbered bridge files are the canonical workflow state.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - project authorization does not bypass bridge review or implementation-start gates.
- `REQ-HARNESS-REGISTRY-001` - external-action decisions must carry harness identity and role provenance for later integration.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner-visible approvals and authorization decisions must be deterministic and auditable.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation proposals must cite applicable requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - proposal must link project, work item, authorization, and target paths explicitly.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must derive from cited requirements.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - external actions and receipts must preserve authoring harness/session/model provenance.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation must stay within the active PAUTH envelope.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - PAUTH mutation classes and forbidden classes define the available implementation scope.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner decisions, approvals, and mutation evidence should become durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifacts should govern work selection and traceability.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - external actions that cross governance thresholds must create durable evidence rather than chat-only state.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - implementation and tests must stay inside the GT-KB root and preserve platform/application boundaries.
- `GOV-STANDING-BACKLOG-001` - `WI-4589` is the current ranked child work item under the active project backlog.

## Prior Deliberations

- `DELIB-20263455` - owner-approved Agent Disposition and Protocol Enforcement closeout planning, ranked work items, and umbrella formulation; explicitly includes `WI-4589` after the protected mutation guard slice.
- `DELIB-0862` - bridge-first governance and historical warning against ambiguous broad GO artifacts.
- `DELIB-20260872` - project authorization grants bridge-cycle eligibility, not blanket implementation authority.
- `DELIB-2258` - implementation-start and work-intent gating are durable safety controls for protected mutations.
- `DELIB-20261178` - bridge/status authority must come from live versioned artifacts and current dispatcher state, not stale summaries.
- `bridge/agent-disposition-protocol-enforcement-umbrella-004.md` - planning-only GO that approved the ranked child sequence and requires concrete child proposals.
- `bridge/agent-disposition-wi4588-protected-mutation-guard-slice1-004.md` - VERIFIED protected file/config mutation guard whose structured decision pattern this slice reuses conceptually.
- `bridge/agent-disposition-wi4590-post-action-receipts-slice1-004.md` - VERIFIED post-action receipt contract with `cloud_deployment` and `external_service` mutation classes available for this slice to reference at runtime without modification.

## Owner Decisions / Input

- `DELIB-20263455` - owner directed Agent Disposition and Protocol Enforcement planning, ranked work items, and umbrella formulation.
- `PAUTH-PROJECT-AGENT-DISPOSITION-PROTOCOL-ENFORCEMENT-UMBRELLA` - active bounded project authorization for `WI-4588` through `WI-4593`; allows source, test, config, protected narrative, governance evidence, MemBase work-item update, and project artifact link classes; forbids production deployment, credential lifecycle change, bridge bypass, self-review, retired bridge index recreation, and unapproved formal artifact mutation.
- `bridge/agent-disposition-protocol-enforcement-umbrella-004.md` - Loyal Opposition approved the planning sequence and required each child slice to receive its own concrete review.

No new owner decision is required for this proposal. This bridge asks Loyal Opposition to review a narrow source/test implementation slice before any protected implementation mutation occurs. The proposal does not authorize or request live cloud, deployment, third-party-service, hosted-app, or credential mutation.

## Requirement Sufficiency

Existing requirements are sufficient for this first slice. The work item, PAUTH, project authorization envelope, bridge authority, AUQ policy, provenance, and spec-derived verification rules cover an additive decision module that gates external side-effect attempts before execution.

This proposal is intentionally narrower than full `WI-4589` completion. It supplies the reusable external-action decision contract and tests. Later child proposals must wire the contract into specific harness tools, deployment helpers, connector workflows, and status surfaces before claiming end-to-end enforcement.

## Proposed Implementation

Add `scripts/external_mutation_guard.py` as a deterministic preflight module with structured inputs and outputs.

Core concepts:

- `ExternalActionClass` values for `cloud_deployment`, `external_service`, `hosted_application`, `third_party_api`, and `credentials_adjacent_external_system`.
- `ExternalAuthority` fields for owner-visible authority such as PAUTH id, work item id, bridge thread/version/status when a bridge is required, owner approval or deliberation id when applicable, and harness/session provenance.
- `ReceiptPlan` fields describing the required post-action receipt class, target systems, verification evidence expectation, and whether the action must emit a receipt before the caller may mark work complete.
- `ExternalGuardDecision` with `allowed`, `reason_code`, `details`, and required follow-up evidence fields suitable for later receipt emission.

Decision behavior:

- Deny unknown or unsupported external action classes.
- Deny any external action with no owner-visible initiating authority.
- Deny production deployment and credential lifecycle changes unless an explicit owner approval identifier is present; this first slice may still return deny for those classes because the active PAUTH forbids performing them in implementation.
- Deny cloud deployment, hosted-app mutation, third-party-service mutation, and credentials-adjacent external actions when bridge authority is required but no GO bridge status/version is supplied.
- Deny any action whose receipt plan is missing or whose mutation class is not compatible with the verified post-action receipt vocabulary.
- Allow only non-production, non-credential external actions when the caller supplies authority, applicable GO bridge state, harness/session provenance, and a valid post-action receipt plan.
- Never perform network calls, deployment commands, credential reads/writes, database writes, bridge writes, or MemBase writes.

The module should reuse simple stdlib-only structures and import the existing `scripts.post_action_receipt.MUTATION_CLASSES` vocabulary when practical. It must not create a competing bridge parser, implementation-start packet writer, or post-action receipt writer in this slice.

Add `platform_tests/scripts/test_external_mutation_guard.py` with isolated tests for:

- unknown action classes deny with a stable reason code;
- missing owner-visible authority denies;
- missing bridge GO denies for action classes requiring bridge authority;
- production deployment and credential lifecycle actions fail closed without explicit owner approval and remain non-executable in this PAUTH scope;
- missing receipt plan denies;
- incompatible receipt mutation class denies;
- non-production external-service action allows only when authority, bridge GO, harness provenance, and receipt plan are present;
- the module performs no external network or file-system mutation during decision evaluation;
- reason codes remain stable for later hook and harness integrations.

## Explicit Non-Scope

- No actual cloud, hosted-application, third-party API, production deployment, credential, or external-service mutation.
- No changes to `scripts/protected_mutation_guard.py` or `scripts/post_action_receipt.py` in this slice.
- No hook, connector, deployment script, CLI, cross-harness trigger, startup, or status-surface wiring in this slice.
- No formal GOV/SPEC/PB/ADR/DCL mutation.
- No MemBase mutation except later project/work-item status updates after verified implementation if separately authorized.
- No `bridge/INDEX.md` recreation.
- No claim that `WI-4589` is complete after this slice; follow-on child proposals must wire the gate into live execution paths.

## Spec-Derived Verification Plan

- `GOV-FILE-BRIDGE-AUTHORITY-001`, `.claude/rules/file-bridge-protocol.md`, and `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`: `python -m pytest platform_tests/scripts/test_external_mutation_guard.py -q --tb=short` must show fail-closed behavior without applicable bridge GO evidence and no bridge-bypass path.
- `SPEC-AUQ-POLICY-ENGINE-001`: tests must show owner-visible authority is required as structured data, not merely prose.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` and `REQ-HARNESS-REGISTRY-001`: tests must show decisions include required harness/session provenance fields before allow.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`: tests and implementation report must state that production deployment and credential lifecycle mutation remain forbidden under the active PAUTH and are not executed.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: proposal and implementation report must carry project metadata, linked specs, spec-to-test mapping, command evidence, and observed results.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`: tests must show a valid receipt plan is required before allow.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`: tests must use in-root fixtures only; `Test-Path bridge/INDEX.md` must remain `False`.

Implementation-report commands:

```text
python -m pytest platform_tests/scripts/test_external_mutation_guard.py -q --tb=short
python -m ruff check scripts/external_mutation_guard.py platform_tests/scripts/test_external_mutation_guard.py
python -m ruff format --check scripts/external_mutation_guard.py platform_tests/scripts/test_external_mutation_guard.py
python scripts/bridge_applicability_preflight.py --bridge-id agent-disposition-wi4589-external-mutation-gate-slice1
python scripts/adr_dcl_clause_preflight.py --bridge-id agent-disposition-wi4589-external-mutation-gate-slice1
Test-Path bridge/INDEX.md
```

## Acceptance Criteria

- A reusable external-mutation guard module returns structured allow/deny results before any external side effect.
- The module fails closed for unsupported action classes, missing owner-visible authority, missing bridge GO when required, missing harness/session provenance, missing receipt plans, production deployment without explicit owner approval, and credential lifecycle actions.
- Tests demonstrate allow and deny cases without network access, cloud-provider calls, deployment commands, credential mutation, MemBase mutation, or bridge mutation.
- The implementation report identifies follow-on hook, connector, deployment-helper, and harness integrations instead of silently claiming full `WI-4589` closure.

## Risk / Rollback

The main risk is adding a second governance policy surface that drifts from the protected mutation guard and post-action receipt contract. The implementation should mitigate that by keeping this module focused on external side-effect classification and importing existing receipt vocabulary where practical.

Rollback is path-local deletion of `scripts/external_mutation_guard.py` and `platform_tests/scripts/test_external_mutation_guard.py` before any follow-on integration consumes them.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered bridge file for `agent-disposition-wi4589-external-mutation-gate-slice1`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`feat:` - the approved implementation would add a new external mutation gate module plus tests.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
