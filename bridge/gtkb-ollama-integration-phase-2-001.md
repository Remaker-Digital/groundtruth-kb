NEW

# Phase-2+ Ollama Integration Planning Umbrella

bridge_kind: governance_advisory
Document: gtkb-ollama-integration-phase-2
Version: 001
Author: Prime Builder (Codex, harness A session override)
Date: 2026-06-05 UTC
Recipient: Loyal Opposition (Codex, harness A durable role)
Project: PROJECT-GTKB-OLLAMA-INTEGRATION

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019e99ba-0220-7292-a2ac-e2329eae912a
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive Prime Builder session override; workspace E:\GT-KB; approval-policy never

target_paths: ["groundtruth.db", "bridge/INDEX.md", "bridge/gtkb-ollama-integration-phase-2-routing-001.md", "bridge/gtkb-ollama-integration-phase-2-adapters-001.md", "bridge/gtkb-ollama-integration-phase-2-dispatch-001.md", "bridge/gtkb-ollama-integration-phase-2-role-promotion-001.md"]

requires_verification: false
implementation_scope: phase_2_scaffolding_only

## Summary

Phase 1 of PROJECT-GTKB-OLLAMA-INTEGRATION is terminal VERIFIED at
`bridge/gtkb-ollama-integration-phase-1-008.md`. This Phase 2+ planning
umbrella responds to the owner directive captured as
`DELIB-20260605-OLLAMA-PHASE2-COMPLETION-DIRECTIVE`: "Proceed with completing
all Ollama phases and related work."

This proposal asks Loyal Opposition to GO a narrow scaffolding step:

1. Create remaining Ollama Phase 2+ MemBase work items.
2. Mint a new project authorization for those work items.
3. File child implementation bridge proposals for Loyal Opposition review.

This proposal does not directly implement code/config changes. The child
bridges will carry implementation-specific Work Item lines, target paths,
tests, and post-implementation reports.

## Why This Umbrella Exists

The implementation-start gate correctly blocks direct MemBase/project mutation
without a live bridge GO authorization packet. The Phase 1 PAUTH is intentionally
bounded and explicitly forbids the remaining work: multi-model routing, skill
adapter generation, dispatch-substrate wiring, additional model registration,
and role promotion.

This umbrella creates the bridge-reviewed transition from Phase 1 closure into
the remaining work. It prevents a governance bypass while avoiding a false claim
that Phase 1's already VERIFIED evidence covered Phase 2+.

## Specification Links

| Spec | Severity | How this proposal complies |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | Filed as a versioned bridge document; `bridge/INDEX.md` remains the canonical queue state. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | This section cites governing specs before any mutation. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | This umbrella is planning/governance only; child implementation bridges must carry spec-to-test mappings and executed results before VERIFIED. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | blocking | The requested output is a bounded Phase 2+ PAUTH tied to explicit owner decision evidence. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | advisory | The Phase 2+ PAUTH will enumerate included WIs, allowed mutation classes, forbidden operations, and related specs. |
| `GOV-STANDING-BACKLOG-001` | blocking | Remaining work is represented as MemBase work_items before implementation. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | The owner directive is preserved as a deliberation and converted into backlog, PAUTH, and bridge artifacts before code mutation. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | Phase 2+ work moves through explicit candidate, GO, implementation, VERIFIED, and project-closure states. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | The work is routed through owner decision evidence, MemBase work items, project authorization, and bridge review. |
| `ADR-OLLAMA-HARNESS-ADOPTION-001` | blocking | Phase 2+ keeps the approved Python shim/static TOML architecture and extends it rather than introducing a framework. |
| `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001` | blocking | Routing expansion must preserve fail-closed schema validation and compatible `.ollama/routing.toml` parsing. |
| `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001` | blocking | Dispatch and adapter work must preserve model-specific author metadata injection before Write/Edit/Bash mutation. |
| `DCL-OLLAMA-TOOL-PARITY-GATE-001` | blocking | Skill adapters and dispatch wiring must preserve canonical tool subset validation and existing destructive-gate delegation. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | blocking | Phase 2+ continues the harness onboarding lifecycle beyond registered/no-active-role state. |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | blocking | Role promotion mechanics must preserve durable registry authority and avoid hidden vendor/model-specific role rules. |
| `GOV-SESSION-ROLE-AUTHORITY-001` | blocking | Any role change must update the durable registry through canonical writer paths; session overrides are not durable role records. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | blocking | All Phase 2+ artifacts remain under `E:\GT-KB`; no live GT-KB artifacts are read from or written outside the project root. |
| `DCL-CONCEPT-ON-CONTACT-001` | advisory | New load-bearing concepts introduced by children must update canonical terminology or justify why existing entries cover them. |

## Prior Deliberations

- `DELIB-20260605-OLLAMA-PHASE2-COMPLETION-DIRECTIVE` - owner directive
  authorizing completion of all remaining Ollama phases and related work.
- `DELIB-20260663` - Phase 1's 12-AUQ owner-decision set. It selected Option A
  and explicitly marked multi-model routing, skill adapters, dispatch wiring,
  and role promotion as Phase 2+ candidates.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` - lifecycle independence remains
  relevant when moving harness D from registered/no-active-role toward an
  active role.
- `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH` - role and status are
  orthogonal axes; Phase 2+ must preserve that model.
- `DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION` - supports local
  external harness invocation while preserving the `E:\GT-KB` root boundary.
- `bridge/gtkb-ollama-integration-phase-1-008.md` - Phase 1 umbrella VERIFIED;
  explicitly did not promote harness D, wire dispatch, or close Phase 2+ scope.

## Owner Decisions / Input

Owner directive captured as
`DELIB-20260605-OLLAMA-PHASE2-COMPLETION-DIRECTIVE` authorizes Prime Builder to
proceed autonomously with the remaining Ollama phases. No additional owner
choice is required for this scaffolding step: the only action here is converting
the already-named Phase 2+ candidates into governed WIs, PAUTH, and child bridge
handoffs.

If later child implementation discovers a genuinely novel choice, it must route
that one question through AskUserQuestion. Otherwise the child scopes should
proceed under this decision and existing Phase 1 decision evidence.

## Phase 2+ Work Items To Create

The GO'd implementation of this umbrella will create four MemBase work items
and attach them to `PROJECT-GTKB-OLLAMA-INTEGRATION`.

| Planned WI | Scope | Acceptance summary |
|---|---|---|
| Routing expansion | Multi-model `.ollama/routing.toml` support, `[routing.skills.<skill>]` overrides, fail-closed route validation, advertised-model checks. | Multiple model rows and skill overrides parse and resolve deterministically; invalid routes fail closed; tests pass. |
| Skill adapter generation | Generate `.ollama/skills/` adapters from canonical `.claude/skills`; register Ollama surfaces in capability registry; add drift checks. | Adapter generator and check mode detect drift; `.ollama/skills` is populated for required/baseline skills; parity tests pass. |
| Dispatch wiring | Add harness D headless invocation surface; teach dispatch/doctor recipient logic to target Ollama only when role/status policy permits it; fail closed when unavailable. | Command generation and dispatch eligibility tests pass; unavailable daemon does not corrupt bridge state. |
| Role promotion and closure mechanics | Governed role/status transition path and project closure after Phase 2+ child threads are VERIFIED. | Role promotion path is explicit, audited, reversible; project state and MEMORY.md update only after bridge verification. |

## Standing Backlog Bulk-Operation Evidence

This proposal is the review-packet for the bulk backlog action. It contains the
inventory artifact for the four candidate work items in the `Phase 2+ Work
Items To Create` table above. No MemBase mutation occurs until Loyal Opposition
GO.

DECISION DEFERRED: child implementation details that exceed this inventory are
deferred to the child bridge proposals. If a child bridge discovers a genuinely
novel owner choice, that choice must route through AskUserQuestion before the
child implementation proceeds.

## Phase 2+ Project Authorization To Mint

The GO'd implementation will mint:

`PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-2-PLUS-COMPLETION`

Expected properties:

- Owner decision: `DELIB-20260605-OLLAMA-PHASE2-COMPLETION-DIRECTIVE`.
- Included WIs: the four work items created by this umbrella implementation.
- Allowed mutation classes: source_file, test_file, config_file,
  protected_narrative_file, membase_work_item_insert, project_authorization,
  bridge_artifact.
- Forbidden operations: credential lifecycle, production deployment,
  out-of-root artifact creation, bypassing bridge GO/VERIFIED, bypassing
  formal/narrative approval gates.
- Explicitly no longer forbidden: multi-model routing, `.ollama/skills/`
  adapter generation, dispatch-substrate wiring, additional local model
  registration, and governed role-promotion mechanics.

## Child Bridge Plan

After the work items and PAUTH exist, Prime Builder will file child proposals:

1. `gtkb-ollama-integration-phase-2-routing-001`
2. `gtkb-ollama-integration-phase-2-adapters-001`
3. `gtkb-ollama-integration-phase-2-dispatch-001`
4. `gtkb-ollama-integration-phase-2-role-promotion-001`

Each child must cite its concrete Work Item and the Phase 2+ PAUTH, pass both
preflights, define target paths, and provide spec-derived verification.

## Specification-Derived Verification Plan

| Requirement | Verification | PASS criterion |
|---|---|---|
| Bridge authority | Live `bridge/INDEX.md` contains this thread at latest GO before scaffolding; child bridge files are added as NEW/REVISED entries. | GO exists before mutation; child entries are present in INDEX. |
| Standing backlog | `gt backlog show <new WI>` and `gt projects show PROJECT-GTKB-OLLAMA-INTEGRATION --json` show all four WIs attached to the project. | Four WIs exist and are active project members. |
| Project authorization | `gt projects authorizations PROJECT-GTKB-OLLAMA-INTEGRATION --json` shows the Phase 2+ PAUTH active and tied to `DELIB-20260605-OLLAMA-PHASE2-COMPLETION-DIRECTIVE`. | PAUTH exists, is active, and includes the four new WIs. |
| Child proposal handoff | Bridge preflights pass for each child proposal before filing. | `missing_required_specs: []`; clause preflight exit 0. |

## Risk / Rollback

Risk: Phase 2+ is larger than one implementation slice.
Mitigation: This umbrella only authorizes scaffolding and child proposal filing.
Implementation remains sliced.

Risk: role promotion could accidentally displace active Claude/Codex role state.
Mitigation: Role-promotion child must implement an explicit, audited, reversible
transition and may not silently mutate the durable role registry without tests.

Rollback: If this umbrella is NO-GO'd, no project/source mutation occurs. If GO'd
scaffolding later proves wrong, revoke the Phase 2+ PAUTH, mark created WIs
superseded/not_planned with bridge evidence, and file a revised umbrella.

## Applicability Preflight

Command:

```powershell
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-ollama-integration-phase-2 --content-file .gtkb-state\bridge-drafts\gtkb-ollama-integration-phase-2-001.md
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:65e220822f52c27fadf44b8c45f9f01ed5228d673891520be67c1374dac3115f`
- bridge_document_name: `gtkb-ollama-integration-phase-2`
- content_source: `pending_content`
- content_file: `.gtkb-state/bridge-drafts/gtkb-ollama-integration-phase-2-001.md`
- operative_file: `(none)`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []
```

## Clause Applicability

Command:

```powershell
groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-ollama-integration-phase-2 --content-file .gtkb-state\bridge-drafts\gtkb-ollama-integration-phase-2-001.md
```

Observed result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-ollama-integration-phase-2`
- Operative file: `.gtkb-state\bridge-drafts\gtkb-ollama-integration-phase-2-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |
```

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
