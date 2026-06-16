NEW
author_identity: prime-builder/Codex
author_harness_id: A
author_session_context_id: S20260616-CODEX-INTERACTIVE
author_model: GPT-5 Codex
author_model_version: 2026-06-16 runtime
author_model_configuration: Codex desktop interactive coding agent

# Umbrella Proposal - Agent Disposition and Protocol Enforcement

bridge_kind: prime_proposal
Document: agent-disposition-protocol-enforcement-umbrella
Version: 001
Date: 2026-06-16 UTC

Project Authorization: PAUTH-PROJECT-AGENT-DISPOSITION-PROTOCOL-ENFORCEMENT-UMBRELLA
Project: PROJECT-AGENT-DISPOSITION-AND-PROTOCOL-ENFORCEMENT
Work Item: WI-4588

related_work_items: ["WI-4588", "WI-4589", "WI-4590", "WI-4591", "WI-4592", "WI-4593"]
target_paths: ["bridge/agent-disposition-protocol-enforcement-umbrella-NNN.md", ".claude/rules/", ".codex/", "config/agent-control/", "harness-state/", "scripts/", "platform_tests/", "groundtruth-kb/src/groundtruth_kb/", "groundtruth-kb/tests/"]

Umbrella proposal coordinating the ranked Agent Disposition and Protocol Enforcement project backlog.

## Claim

GT-KB now needs a project-level implementation program that makes agent disposition and protocol enforcement deterministic across all harnesses. The current operating contract says protected source/config/test/script/hook mutations require live bridge GO plus implementation-start authorization and work-intent claim, but enforcement remains split across prompts, hooks, helper scripts, harness-specific fallbacks, and human discipline. This umbrella proposes the governed work program, ranked backlog, and verification expectations; individual implementation slices must still proceed through their own GO, implementation-start packet, work-intent claim, post-implementation report, and LO verification.

## Requirement Sufficiency

Existing requirements are sufficient for umbrella planning and initial implementation proposals. The owner decision `DELIB-20263455` authorizes closeout planning, ranked work-item creation, and this umbrella proposal. The active project authorization `PAUTH-PROJECT-AGENT-DISPOSITION-PROTOCOL-ENFORCEMENT-UMBRELLA` covers `WI-4588` through `WI-4593` while preserving normal bridge, implementation-start, work-intent, formal-artifact, credential, and deployment restrictions.

## Umbrella Inventory

| Rank | Work item | Priority | Scope |
| --- | --- | --- | --- |
| 1 | `WI-4588` | P1 | Enforce bridge GO plus implementation authorization before protected mutations across harnesses. |
| 2 | `WI-4589` | P1 | Gate cloud deployment and external-service mutations behind owner-visible bridge authorization. |
| 3 | `WI-4590` | P1 | Create post-action audit receipts for agent mutations and reviews. |
| 4 | `WI-4591` | P2 | Normalize bridge disposition workflow for ADVISORY, NO-GO, NEW, REVISED, GO, and VERIFIED states. |
| 5 | `WI-4592` | P2 | Build cross-harness protocol parity tests for prompts, hooks, tools, and fallback behavior. |
| 6 | `WI-4593` | P2 | Surface protocol enforcement gaps in startup status and closeout reports. |

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
| --- | --- | --- | --- | --- |
| CQ-SECRETS-001 | Yes | Do not introduce secrets or credential-shaped examples in prompts, hooks, receipts, tests, or bridge records. | Bridge helper credential scan and focused changed-file review per slice. | |
| CQ-PATHS-001 | Yes | Keep all implementation inside declared project-root targets and each child bridge target set. | Implementation-start packets, target path preflights, and final diff review. | |
| CQ-COMPLEXITY-001 | Yes | Prefer small deterministic gate/check helpers over broad prompt-only policy. | Per-slice code review and focused unit/integration tests. | |
| CQ-CONSTANTS-001 | Yes | Centralize status, role, mutation-class, and receipt-field constants rather than duplicating strings. | Ruff, targeted tests, and symbol/search review. | |
| CQ-SECURITY-001 | Yes | Preserve fail-closed handling for protected files, credentials, cloud/deployment actions, and external services. | Negative-path tests for missing GO, missing packet, missing claim, and external mutation authorization. | |
| CQ-DOCS-001 | Yes | Update active startup/rule/status guidance only in slices that actually change behavior. | Review of changed narrative surfaces and no-index invariant checks. | |
| CQ-TESTS-001 | Yes | Every implementation slice must include focused tests or an explicit manual verification mapping. | Linked tests `TEST-11155` through `TEST-11160` plus per-slice targeted commands. | |
| CQ-LOGGING-001 | Yes | Blocked actions and post-action receipts must leave durable, owner-visible evidence without leaking secrets. | Receipt/status fixture tests and log/output review. | |
| CQ-VERIFICATION-001 | Yes | Require spec-derived verification in every implementation report before LO verification. | Applicability preflight, clause preflight, targeted tests, and LO review. | |

## In-Root Placement Evidence

All target paths are relative to the GT-KB project root and remain inside the project: `bridge/agent-disposition-protocol-enforcement-umbrella-NNN.md`, `.claude/rules/`, `.codex/`, `config/agent-control/`, `harness-state/`, `scripts/`, `platform_tests/`, `groundtruth-kb/src/groundtruth_kb/`, and `groundtruth-kb/tests/`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - Protected mutations must be bridge-governed and cannot bypass GO/authorization gates.
- `GOV-FILE-BRIDGE-PROTOCOL-001` - Bridge statuses and role-specific actionability are the review and handoff mechanism.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Owner directives that become durable work must be preserved as projects, work items, proposals, and evidence.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Implementation proposals must cite governing specs before work.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Implementation reports must map specs to verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - This proposal links the project, work item, PAUTH, and target paths.
- `SPEC-AUQ-POLICY-ENGINE-001` - Owner-visible authorization and owner-action routing must be explicit.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Work must remain in the GT-KB root, not external/archive locations.
- `GOV-STANDING-BACKLOG-001` - Ranked work items are the durable cross-session work authority.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex must self-enforce when hook parity is incomplete.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Protocol enforcement must be artifact-backed, not chat-only.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Protocol gaps, owner decisions, and implementation plans trigger artifact lifecycle handling.
- `REQ-HARNESS-REGISTRY-001` - Harness capability/role surfaces must remain consistent with actual harness behavior.

## Prior Deliberations

- `DELIB-20263455` - Owner authorizes Agent Disposition and Protocol Enforcement closeout planning.
- `DELIB-20263383` - Prior owner authorization pattern for bounded harness-state reconciliation work.

## Owner Decisions / Input

- `DELIB-20263455` - Owner directed closeout planning, ranked work items, and umbrella proposal formulation for this project.
- `PAUTH-PROJECT-AGENT-DISPOSITION-PROTOCOL-ENFORCEMENT-UMBRELLA` - Active bounded project authorization for `WI-4588` through `WI-4593`.

## Proposed Scope

This umbrella authorizes review of the overall program shape only. After LO GO, Prime may start the first implementation slice only by creating an implementation-start packet for the specific GO bridge thread and holding a matching work-intent claim. The likely implementation order is:

1. `WI-4588` protected mutation guard core.
2. `WI-4589` external/cloud/deployment mutation classification and authorization gate.
3. `WI-4590` post-action receipt schema and validator.
4. `WI-4591` bridge disposition matrix and wrong-role block reasons.
5. `WI-4592` cross-harness protocol parity test matrix.
6. `WI-4593` startup/status/wrap visibility surfaces.

Out of scope for this umbrella: production deployment, credential lifecycle changes, force-push, bridge protocol bypass, self-review, recreating `bridge/INDEX.md`, or unapproved GOV/SPEC/PB/ADR/DCL mutation.

## Specification-Derived Verification Plan

| Requirement / Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Negative tests prove protected mutations without GO, packet, or claim fail closed; positive tests prove scoped authorized mutations pass. |
| `GOV-FILE-BRIDGE-PROTOCOL-001` | Status/role matrix tests classify NEW, REVISED, GO, NO-GO, VERIFIED, and ADVISORY correctly for Prime and LO. |
| `SPEC-AUQ-POLICY-ENGINE-001` | External/cloud/deployment mutation gates require owner-visible authorization evidence and produce clear owner-action blocks where needed. |
| `REQ-HARNESS-REGISTRY-001` | Cross-harness parity tests compare declared capability/role state to actual prompt/hook/tool behavior. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Each child implementation report includes spec-derived verification and residual-risk disclosure before LO verification. |
| No-index invariant | Every slice confirms `bridge/INDEX.md` remains absent and no new dependency is introduced. |

## Acceptance Criteria

- The six ranked work items remain linked to the project in order 1 through 6.
- LO reviews this umbrella for scope correctness before any implementation slice begins.
- Every child implementation slice has its own bridge GO, implementation-start packet, work-intent claim, focused verification, and implementation report.
- Protected file/config/test/script/hook mutation, external/cloud/deployment mutation, and post-action evidence are all covered by deterministic checks or explicitly documented manual checks.
- No bridge index artifact is recreated or treated as authority.

## Risks / Rollback

Risk: a broad umbrella could hide over-scoped implementation. Mitigation: this umbrella only sets the ranked program; each slice must have its own scoped GO and target paths.

Risk: prompt-only policy may still drift. Mitigation: prioritize deterministic guard/test surfaces before narrative-only guidance updates.

Rollback: withdraw or revise this umbrella without mutating source/config if LO finds scope or authority defects. Child slices are independently reversible according to their own proposals.

## Pre-Filing Preflight

Commands:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id agent-disposition-protocol-enforcement-umbrella --content-file .gtkb-state/bridge-propose-drafts/agent-disposition-protocol-enforcement-umbrella-final.md
python scripts/adr_dcl_clause_preflight.py --bridge-id agent-disposition-protocol-enforcement-umbrella --content-file .gtkb-state/bridge-propose-drafts/agent-disposition-protocol-enforcement-umbrella-final.md
```

Applicability preflight summary:

- bridge_document_name: `agent-disposition-protocol-enforcement-umbrella`
- content_source: `pending_content`
- operative_file: `(none)`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

Clause applicability preflight summary:

- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps: 0
- Mode: mandatory default invocation; exit 0 passed.


## Files Expected To Change

- `bridge/agent-disposition-protocol-enforcement-umbrella-NNN.md`
- `.claude/rules/`
- `.codex/`
- `config/agent-control/`
- `harness-state/`
- `scripts/`
- `platform_tests/`
- `groundtruth-kb/src/groundtruth_kb/`
- `groundtruth-kb/tests/`

## Recommended Commit Type

`feat`
