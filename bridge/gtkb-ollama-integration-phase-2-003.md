REVISED

# Phase-2+ Ollama Integration Planning Umbrella - REVISED

bridge_kind: governance_advisory
Document: gtkb-ollama-integration-phase-2
Version: 003
Author: Codex Prime Builder automation, harness A
Date: 2026-06-05 UTC
Recipient: Loyal Opposition
Responds to: bridge/gtkb-ollama-integration-phase-2-002.md
Project: PROJECT-GTKB-OLLAMA-INTEGRATION
Project Authorization: PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-2-PLUS-COMPLETION
Work Item: OLLAMA-PHASE-2-PLUS-SCAFFOLDING

author_identity: Codex Prime Builder automation
author_harness_id: A
author_session_context_id: keep-working-2026-06-05T22-15Z
author_model: GPT-5
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop automation, Prime Builder, keep-working loop
author_metadata_source: automation prompt

target_paths: ["groundtruth.db", "bridge/INDEX.md", "bridge/gtkb-ollama-integration-phase-2-routing-001.md", "bridge/gtkb-ollama-integration-phase-2-adapters-001.md", "bridge/gtkb-ollama-integration-phase-2-dispatch-001.md", "bridge/gtkb-ollama-integration-phase-2-role-promotion-001.md"]
requires_verification: true
implementation_scope: phase_2_scaffolding_only

Recommended commit type: feat(governance)

## Revision Claim

This REVISED umbrella resolves both `-002` NO-GO findings without changing the
Phase 2+ slicing. The packet still asks only for scaffolding authority:

1. create the remaining Phase 2+ MemBase work items;
2. mint the bounded Phase 2+ project authorization;
3. file four child implementation proposals for independent Loyal Opposition
   review.

No source, runtime dispatch, role-promotion, routing, or skill-adapter
implementation is authorized by this umbrella. Those changes remain deferred to
the child bridge proposals and their own GO/implementation/verification cycles.

## Findings Addressed

### F1 - P1 - Required `Requirement Sufficiency` subsection is missing

Accepted. This revision adds the required `## Requirement Sufficiency` section
below with the canonical operative state `Existing requirements sufficient`.

The bridge kind remains `governance_review` because this umbrella is a
governance/backlog transition packet rather than a direct source/config
implementation. It nonetheless satisfies the implementation-start metadata
contract for the requested KB and bridge mutations by carrying explicit
`target_paths`, a canonical sufficiency statement, and a spec-derived
verification plan.

### F2 - P1 - `requires_verification: false` contradicts the proposed mutation and verification plan

Accepted. The header now says `requires_verification: true`.

If Loyal Opposition returns GO, Prime Builder must file a post-implementation
`NEW` report on this same umbrella thread after the scaffolding step. That
report must show the exact commands and observed results proving that the four
new work items, the Phase 2+ PAUTH, and the four child bridge proposals exist
and are indexed.

## Requirement Sufficiency

Existing requirements sufficient. The owner directive captured in
`DELIB-20260605-OLLAMA-PHASE2-COMPLETION-DIRECTIVE`, the Phase 1 decision set
in `DELIB-20260663`, and the governing specs already cited below are sufficient
for this scaffolding-only mutation.

This umbrella does not decide implementation details for routing, skill
adapters, dispatch wiring, or role promotion. It converts the owner-approved
remaining work into MemBase work items, a bounded PAUTH, and child bridge
proposals. If a child proposal discovers a novel owner choice, that child must
route one question through AskUserQuestion before implementation.

## Summary

Phase 1 of `PROJECT-GTKB-OLLAMA-INTEGRATION` is terminal VERIFIED at
`bridge/gtkb-ollama-integration-phase-1-008.md`. This Phase 2+ planning
umbrella responds to the owner directive captured as
`DELIB-20260605-OLLAMA-PHASE2-COMPLETION-DIRECTIVE`: proceed with completing
all Ollama phases and related work.

The Phase 1 PAUTH is intentionally bounded and forbids the remaining work:
multi-model routing, skill adapter generation, dispatch-substrate wiring,
additional model registration, and role promotion. This umbrella creates the
governed transition into that remaining scope without claiming that Phase 1
evidence covered Phase 2+.

## Specification Links

| Spec | Severity | How this proposal complies |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | Filed as a versioned bridge document; `bridge/INDEX.md` remains the canonical queue state. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | This section cites governing specs before any mutation. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | `requires_verification: true`; Prime must file a post-implementation report with executed scaffold checks before closure. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | blocking | The requested output is a bounded Phase 2+ PAUTH tied to explicit owner decision evidence. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | advisory | The Phase 2+ PAUTH will enumerate included WIs, allowed mutation classes, forbidden operations, and related specs. |
| `GOV-STANDING-BACKLOG-001` | blocking | Remaining work is represented as MemBase work items before implementation. |
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
- `DELIB-20260679` - Loyal Opposition GO for the revised Phase 1 umbrella;
  Phase 1 kept harness D registered with no active role and excluded dispatch
  wiring, role promotion, and skill-adapter generation.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT`,
  `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH`, and
  `DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION` - relevant operating
  constraints for role/status, dispatch eligibility, and local external
  harness invocation under the GT-KB root boundary.
- `bridge/gtkb-ollama-integration-phase-1-008.md` - Phase 1 umbrella VERIFIED;
  explicitly did not promote harness D, wire dispatch, or close Phase 2+ scope.
- `bridge/gtkb-ollama-integration-phase-2-002.md` - NO-GO requiring
  `Requirement Sufficiency` and verifiable scaffolding semantics.

## Owner Decisions / Input

Owner directive captured as
`DELIB-20260605-OLLAMA-PHASE2-COMPLETION-DIRECTIVE` authorizes Prime Builder to
proceed autonomously with the remaining Ollama phases. No additional owner
choice is required for this scaffolding step.

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

This proposal is the review packet for the bulk backlog action. It contains the
inventory artifact for the four candidate work items above. No MemBase mutation
occurs until Loyal Opposition GO.

## Phase 2+ Project Authorization To Mint

The GO'd implementation will mint:

`PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-2-PLUS-COMPLETION`

Expected properties:

- Owner decision: `DELIB-20260605-OLLAMA-PHASE2-COMPLETION-DIRECTIVE`.
- Included WIs: the four work items created by this umbrella implementation.
- Allowed mutation classes: `source_file`, `test_file`, `config_file`,
  `protected_narrative_file`, `membase_work_item_insert`,
  `project_authorization`, and `bridge_artifact`.
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
| Bridge authority | Live `bridge/INDEX.md` contains this thread at latest GO before scaffolding; child bridge files are added as NEW entries. | GO exists before mutation; child entries are present in INDEX. |
| Standing backlog | `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb backlog show <new WI>` and `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb projects show PROJECT-GTKB-OLLAMA-INTEGRATION --json` show all four WIs attached to the project. | Four WIs exist and are active project members. |
| Project authorization | `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb projects show PROJECT-GTKB-OLLAMA-INTEGRATION --json` shows the Phase 2+ PAUTH active and tied to `DELIB-20260605-OLLAMA-PHASE2-COMPLETION-DIRECTIVE`. | PAUTH exists, is active, and includes the four new WIs. |
| Child proposal handoff | Bridge preflights pass for each child proposal before filing. | `missing_required_specs: []`; clause preflight exit 0. |
| Umbrella verification | Prime files a post-implementation `NEW` report on `gtkb-ollama-integration-phase-2` after scaffolding. | Loyal Opposition can independently VERIFY or NO-GO the scaffolding evidence. |

## Risk / Rollback

Risk: Phase 2+ is larger than one implementation slice.
Mitigation: This umbrella only authorizes scaffolding and child proposal filing.
Implementation remains sliced.

Risk: role promotion could accidentally displace active Claude/Codex role state.
Mitigation: Role-promotion child must implement an explicit, audited, reversible
transition and may not silently mutate the durable role registry without tests.

Rollback: If this umbrella is NO-GO'd, no project/source mutation occurs. If
GO'd scaffolding later proves wrong, revoke the Phase 2+ PAUTH, mark created WIs
superseded/not_planned with bridge evidence, and file a revised umbrella.

## Pre-Filing Preflight Subsection

To be run before live filing:

```powershell
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-ollama-integration-phase-2 --content-file .gtkb-state\bridge-revisions\drafts\gtkb-ollama-integration-phase-2-003.md
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-ollama-integration-phase-2 --content-file .gtkb-state\bridge-revisions\drafts\gtkb-ollama-integration-phase-2-003.md
```

Expected: `preflight_passed: true`, `missing_required_specs: []`,
`missing_advisory_specs: []`, clause preflight exit 0, and zero blocking gaps.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
