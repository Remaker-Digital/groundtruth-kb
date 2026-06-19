NEW
author_identity: prime-builder/codex-automation
author_harness_id: A
author_session_context_id: 019ee20d-e968-7b40-a570-f38cd6a7e3ef
author_model: gpt-5-codex
author_model_version: 2026-06-19
author_model_configuration: Codex desktop automation session; approval_policy=never; autonomous Prime Builder

# WI-4593 Protocol Enforcement Visibility - Slice 1

bridge_kind: prime_proposal
Document: agent-disposition-wi4593-protocol-enforcement-visibility-slice1
Version: 001
Status: NEW
Author: Prime Builder (Codex)
Date: 2026-06-19 UTC

Project Authorization: PAUTH-PROJECT-AGENT-DISPOSITION-PROTOCOL-ENFORCEMENT-UMBRELLA
Project: PROJECT-AGENT-DISPOSITION-AND-PROTOCOL-ENFORCEMENT
Work Item: WI-4593

target_paths: ["scripts/protocol_enforcement_health.py", "platform_tests/scripts/test_protocol_enforcement_health.py"]

implementation_scope: source,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
external_mutation_in_scope: false
production_deployment_in_scope: false
credential_lifecycle_change_in_scope: false

---

## Summary

This child proposal requests a narrow first implementation slice for `WI-4593`: add a read-only protocol enforcement health reporter plus focused tests. The reporter will compute structured visibility data for protected mutation blocks, missing implementation-start packets, missing work-intent claims, unresolved `ADVISORY`/`NO-GO` dispositions, missing post-action receipts, and external-mutation authorization gaps.

The slice deliberately avoids editing currently dirty startup/status/dashboard/wrap surfaces. It creates a reusable read-only core that those surfaces can consume in later child slices after Loyal Opposition reviews the data contract. It does not mutate bridge state, MemBase, dashboards, startup files, wrap files, cloud services, deployments, credentials, or external systems.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Read metadata and state only; do not include credential-shaped fixtures. | Bridge helper credential scan and focused review. | |
| CQ-PATHS-001 | Yes | Add one in-root script and one in-root platform test module. | Applicability preflight, target-path review, and no retired index check. | |
| CQ-COMPLEXITY-001 | Yes | Keep health checks modular and data-oriented. | Focused tests for each reported gap type. | |
| CQ-CONSTANTS-001 | Yes | Centralize health keys, severity levels, and next-action codes. | Tests assert stable codes. | |
| CQ-SECURITY-001 | Yes | Reporter is read-only and must not execute mutation/deployment/external commands. | Tests verify no state writes and use fixtures. | |
| CQ-DOCS-001 | Yes | Keep documentation to bridge/report evidence and concise CLI help. | Loyal Opposition review. | |
| CQ-TESTS-001 | Yes | Add tests for visibility output and read-only behavior. | `python -m pytest platform_tests/scripts/test_protocol_enforcement_health.py -q --tb=short`. | |
| CQ-LOGGING-001 | Yes | Emit structured JSON/Markdown on demand; no persistent log sink in this slice. | Tests assert output shape. | |
| CQ-VERIFICATION-001 | Yes | Run focused pytest, Ruff check, Ruff format-check, bridge preflights, and retired index absence check. | Commands listed in the verification plan. | |

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protocol enforcement health must derive from live versioned bridge state and governed bridge authority.
- `GOV-FILE-BRIDGE-PROTOCOL-001` - bridge actionability and disposition gaps must surface with clear next actions.
- `.claude/rules/file-bridge-protocol.md` - startup and bridge handling must not treat stale summaries or retired indexes as authority.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - health output must expose missing bridge GO, implementation packet, or work-intent evidence rather than bypassing them.
- `REQ-HARNESS-REGISTRY-001` - visibility output must include role/harness context where applicable.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner-action and advisory states must be visible as explicit next actions.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - health checks must read live authoritative state, not cached dashboards or copied summaries.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation proposals must cite applicable requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - proposal must link project, work item, authorization, and target paths explicitly.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must derive from cited requirements.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation must stay within the active PAUTH envelope.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - PAUTH mutation classes and forbidden operations define allowed scope.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - enforcement gaps should become durable, visible artifacts rather than hidden chat state.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable health output should guide future work selection and closeout.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - detected gaps can later be promoted into lifecycle-tracked work or owner decisions.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - implementation and tests must stay inside the GT-KB root.
- `GOV-STANDING-BACKLOG-001` - `WI-4593` is an active ranked child work item under the current project backlog.

## Prior Deliberations

- `DELIB-20263455` - owner-approved Agent Disposition and Protocol Enforcement closeout planning, ranked work items, and umbrella formulation; includes `WI-4593` for protocol enforcement visibility surfaces.
- `DELIB-0862` - bridge-first governance and historical warning against ambiguous queue/workflow state.
- `DELIB-20260872` - project authorization grants bridge-cycle eligibility, not blanket implementation authority.
- `DELIB-2258` - implementation-start and work-intent gating are durable safety controls for protected mutations.
- `DELIB-20261178` - bridge/status authority must come from live versioned artifacts and current dispatcher state, not stale summaries.
- `bridge/agent-disposition-protocol-enforcement-umbrella-004.md` - planning-only GO that approved the ranked child sequence and requires concrete child proposals.
- `bridge/agent-disposition-wi4588-protected-mutation-guard-slice1-004.md` - VERIFIED protected mutation guard whose block reasons should become visible in later surfaces.
- `bridge/agent-disposition-wi4589-external-mutation-gate-slice1-001.md` - pending external-mutation gate proposal whose future gaps should be reported without external side effects.
- `bridge/agent-disposition-wi4590-post-action-receipts-slice1-004.md` - VERIFIED receipt contract whose missing/available receipt evidence should be summarized.
- `bridge/agent-disposition-wi4591-bridge-disposition-workflow-slice1-001.md` - pending bridge disposition matrix proposal whose final verified outputs can feed later visibility wiring.
- `bridge/agent-disposition-wi4592-cross-harness-protocol-parity-slice1-001.md` - pending parity test proposal that can validate this reporter's cross-harness assumptions in follow-on work.

## Owner Decisions / Input

- `DELIB-20263455` - owner directed the Agent Disposition and Protocol Enforcement project and ranked `WI-4593` as the visibility-surface child item.
- `PAUTH-PROJECT-AGENT-DISPOSITION-PROTOCOL-ENFORCEMENT-UMBRELLA` - active bounded project authorization includes `WI-4593`; allows source/test/config/protected narrative/governance evidence/MemBase update/project artifact link classes and forbids production deployment, credential lifecycle change, bridge bypass, self-review, retired bridge index recreation, and unapproved formal artifact mutation.
- `bridge/agent-disposition-protocol-enforcement-umbrella-004.md` - Loyal Opposition approved the planning sequence and required each child slice to receive its own concrete review.

No new owner decision is required for this proposal. The proposed slice adds a read-only reporter and tests; it does not wire the reporter into startup, status, dashboard, or wrap surfaces yet.

## Requirement Sufficiency

Existing requirements are sufficient for this first visibility-core slice. `WI-4593` names the required visibility categories, and the linked source-of-truth/bridge/protocol/receipt requirements define where the reporter must derive evidence.

This proposal is intentionally narrower than full `WI-4593` completion. It creates the read-only health data contract first. Later child proposals can wire the reporter into startup/status/dashboard/wrap surfaces after the contract is reviewed and verified, avoiding broad edits across currently dirty files.

## Proposed Implementation

Add `scripts/protocol_enforcement_health.py` with a read-only health model and optional CLI.

The module should gather and normalize, without mutation:

- Prime Builder and Loyal Opposition bridge actionability counts from live versioned bridge state;
- blocked protected mutation evidence from guard-compatible reason codes when provided in fixtures or state files;
- missing implementation authorization packets for latest `GO` items that should be activatable;
- missing or stale work-intent claims where an active implementation thread is present;
- unresolved `ADVISORY` and `NO-GO` dispositions with role-correct next actions;
- missing post-action receipt evidence for completed mutation reports when receipt metadata is available;
- external-mutation authorization gaps once the external gate is implemented, with graceful empty-state behavior in this slice.

The output should be a deterministic structure such as:

- `status`: `healthy`, `warning`, or `blocked`;
- `generated_at`;
- `source_paths` used for evidence;
- `items`: list of gap dictionaries with `category`, `severity`, `evidence`, `next_action`, and `owner_visible`;
- `summary`: counts by category/severity.

Add `platform_tests/scripts/test_protocol_enforcement_health.py` with fixture-based tests for:

- empty state yields `healthy` and no mutation;
- latest `NO-GO` yields Prime Builder next action;
- latest `ADVISORY` yields owner-visible Prime disposition rather than headless implementation dispatch;
- latest `GO` missing packet yields implementation-start next action;
- missing work-intent claim yields a distinct gap;
- missing post-action receipt yields a receipt-evidence gap when fixture data indicates a mutation completed;
- output is JSON-serializable and stable;
- no files outside a fixture temp root are read or written.

## Explicit Non-Scope

- No edits to startup, status, dashboard, wrap, or report-generation surfaces in this slice.
- No MemBase mutation.
- No bridge file mutation outside this proposal/report thread.
- No live external service, cloud, deployment, hosted-app, or credential operation.
- No formal GOV/SPEC/PB/ADR/DCL mutation.
- No `bridge/INDEX.md` recreation.
- No claim that `WI-4593` is complete after this slice; follow-on slices must wire the reporter into owner-visible surfaces.

## Spec-Derived Verification Plan

- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-FILE-BRIDGE-PROTOCOL-001`, and `.claude/rules/file-bridge-protocol.md`: tests must use live-shape versioned bridge fixtures and must not rely on cached dashboard/index summaries.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`: tests must surface missing GO/packet/work-intent evidence as gaps rather than allowing silent continuation.
- `SPEC-AUQ-POLICY-ENGINE-001`: tests must mark `ADVISORY` and owner-action states as owner-visible next actions.
- `REQ-HARNESS-REGISTRY-001`: tests must leave room for role/harness context and avoid vendor-hardcoded decisions.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: proposal and implementation report must carry project metadata, linked specs, spec-to-test mapping, command evidence, and observed results.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`: implementation must stay inside the active PAUTH and avoid forbidden operations.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`: tests must use in-root fixtures only; `Test-Path bridge/INDEX.md` must remain `False`.

Implementation-report commands:

```text
python -m pytest platform_tests/scripts/test_protocol_enforcement_health.py -q --tb=short
python -m ruff check scripts/protocol_enforcement_health.py platform_tests/scripts/test_protocol_enforcement_health.py
python -m ruff format --check scripts/protocol_enforcement_health.py platform_tests/scripts/test_protocol_enforcement_health.py
python scripts/bridge_applicability_preflight.py --bridge-id agent-disposition-wi4593-protocol-enforcement-visibility-slice1
python scripts/adr_dcl_clause_preflight.py --bridge-id agent-disposition-wi4593-protocol-enforcement-visibility-slice1
Test-Path bridge/INDEX.md
```

## Acceptance Criteria

- A read-only protocol enforcement health reporter exists with deterministic structured output.
- Tests cover bridge disposition gaps, implementation packet gaps, work-intent gaps, receipt gaps, advisory owner-visible states, and JSON-serializable output.
- The reporter does not mutate bridge state, MemBase, startup files, dashboard files, wrap files, or external systems.
- The implementation report identifies follow-on wiring into startup/status/dashboard/wrap surfaces rather than claiming full `WI-4593` closure.

## Risk / Rollback

The main risk is creating a visibility core whose categories drift from the final `WI-4591` disposition matrix or `WI-4589` external gate. The implementation should mitigate that by using graceful empty states and stable category names, then allowing follow-on slices to integrate verified APIs after those threads complete.

Rollback is path-local deletion of `scripts/protocol_enforcement_health.py` and `platform_tests/scripts/test_protocol_enforcement_health.py` before downstream surfaces consume them.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered bridge file for `agent-disposition-wi4593-protocol-enforcement-visibility-slice1`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`feat:` - the approved implementation would add a read-only protocol enforcement health reporter plus tests.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
