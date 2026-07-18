NEW
::init gtkb lo
::open build

# WI-5482 - Reconcile one stale project-dependency edge

bridge_kind: prime_proposal
Document: gtkb-wi5482-stale-project-dependency-reconciliation
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-17T19:29:38Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; build activity envelope; approval_policy=never

Project Authorization: PAUTH-TREE-STABILIZATION-WI5482-PROJECT-DEPENDENCY-GRAPH-RECONCILIATION-20260717
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5482

target_paths: ["groundtruth.db"]

implementation_scope: governed project metadata reconciliation
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

Retire exactly one stale active project-dependency edge through the governed
`gt projects dependencies retire` route:

`PDEP-PROJECT-GTKB-ROLE-ENHANCEMENT-PROJECT-GTKB-ISOLATION-PHASE-9-PRODUCTIZATION-DEPENDS-ON`.

The edge's prerequisite is retired and satisfies its required state, but its
dependent project later auto-retired while the edge remained active. The
WI-5156 validator correctly reports that active edge as a blocking
`retired-endpoint` error. Because add transactions validate the complete active
graph, that historical defect prevents WI-5462 from registering the eight
foundation-first black-box dependencies. This proposal repairs only the stale
edge. It does not create any black-box dependency, edit source or configuration,
or mutate dispatcher/TAFE/runtime state.

Current evidence:

- `gt projects dependencies validate --json` reports `valid: false`,
  `active_dependency_count: 14`, and exactly one error naming the target edge
  and retired dependent endpoint.
- `gt projects dependencies show <target> --json` reports version 2,
  `status: active`, required prerequisite state `retired`, and readiness
  `satisfied: true`.
- `gt projects show PROJECT-GTKB-ROLE-ENHANCEMENT --json` reports the dependent
  project at version 4 with `status: retired`.
- The canonical snapshot of the other thirteen current dependency records,
  reduced to id/version/status/endpoints and sorted by id, is
  `sha256:57b1d8769c29c1caa5f33a3aa28d155fcb4217e9c7611e097aced58255ec3fe2`.

Implementation is hard-sequenced behind canonical terminal `VERIFIED` and
focused finalization of WI-5156. The currently editable worktree code is not
production mutation authority.

## Specification Links

- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - makes versioned MemBase dependency
  rows the sole authority, requires CLI-only append-only mutation, classifies an
  active edge with an invalid endpoint as blocking P0, and supplies the
  retirement recovery route used here.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` and
  `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - require the bounded active
  PAUTH and preserve all later review/start gates.
- `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001` - limits the PAUTH to
  WI-5482; WI-5462 and other work cannot consume it.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires Prime Builder NEW filing,
  independent LO disposition, and later independent verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - require the explicit
  specification, project, work-item, and PAUTH linkage in this packet.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires the
  specification-derived `TEST-11574` evidence before VERIFIED.
- `GOV-12` and `GOV-13` - govern the linked test and its PHASE-008 assignment
  created with WI-5482.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - require preserving this discovered
  defect, proposal, disposition, implementation evidence, and terminal result
  as governed artifacts.
- `GOV-STANDING-BACKLOG-001` - authorizes preservation of the discovered
  derived defect without treating backlog capture as implementation approval.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps all artifacts, test
  evidence, and temporary material inside `E:\GT-KB`.

## Prior Deliberations

- `DELIB-20260710-GTKB-MODERNIZATION-PROJECT-DEPENDENCY-ORDERING-DCL-APPROVAL`
  approved one MemBase authority, self-descriptive edge semantics, governed CLI
  transactions, complete-graph validation, and deterministic readiness. This
  proposal applies its explicit retirement route to one legacy-invalid edge.
- `DELIB-20260715-DISPATCHER-BLACKBOX-SPEC-FOUNDATION-FIRST` selected the
  foundation-first sequence that WI-5462 will encode after this prerequisite
  repair.
- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes bounded
  PAUTH carriers and proposals for newly discovered defects needed to complete
  the active bridge/TAFE/harness objective while preserving every independent
  review and non-bypass gate.

## Owner Decisions / Input

Mike's active objective is to complete the black-box bridge/TAFE/harness
program and bring every related child and derived work item to a terminal
verified state. That directive, together with
`DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION`, authorizes creation
of WI-5482, its bounded PAUTH, and this proposal. It does not authorize the
metadata mutation before independent GO, claim, implementation-start, and
terminal WI-5156 evidence.

## Requirement Sufficiency

**Existing requirements sufficient.** `DCL-PROJECT-DEPENDENCY-ORDERING-001`
already states the exact defect classification, sole authority, governed
retirement route, append-only history rule, validation behavior, and recovery
constraints. No new specification or amendment is needed for this one-record
reconciliation.

## Proposed Transaction

After WI-5156 is canonically terminal and this proposal has independent GO:

1. Acquire an exact WI-5482 implementation claim and schema-v3 start packet for
   `groundtruth.db`.
2. Capture the target record, global validation result, and sorted current
   dependency snapshot through the governed CLI.
3. Execute only:

   `gt projects dependencies retire PDEP-PROJECT-GTKB-ROLE-ENHANCEMENT-PROJECT-GTKB-ISOLATION-PHASE-9-PRODUCTIZATION-DEPENDS-ON --changed-by prime-builder/codex/A --change-reason "WI-5482: retire the stale satisfied edge after its dependent project reached terminal state; restore a valid governed graph before WI-5462." --json`

4. Re-read the target and complete graph through the CLI. Do not use direct SQL,
   an alternate graph store, or any source/configuration edit.
5. File the implementation report. Independent LO must verify the exact
   transaction and `TEST-11574` before focused finalization.

## Related Work And Sequencing

- `WI-5156` is a hard predecessor. Its dependency-ordering CLI must be
  independently VERIFIED and focused-finalized before this metadata mutation.
- `WI-5462` is a hard successor. It may file its own proposal now, but it must
  not add black-box edges until WI-5482 is terminal and global validation is
  clean.
- `WI-5268` through `WI-5276` remain outside this transaction. This repair
  grants none of them implementation approval.

## Specification-Derived Verification Plan

| Requirement | Evidence and required result |
| --- | --- |
| Bounded PAUTH and exact project/WI/spec linkage | Applicability preflight passes with no missing required or advisory specs; mandatory clause preflight reports zero blocking gaps; the live PAUTH remains active and includes only WI-5482. |
| Canonical predecessor | Live bridge/finalization evidence proves WI-5156 terminal VERIFIED before the retire command. A nonterminal bridge token or dirty candidate is insufficient. |
| Baseline defect is exact | Before mutation, `gt projects dependencies validate --json` reports exactly the named retired-endpoint error and `active_dependency_count: 14`; target `show` reports active version 2. |
| CLI-only append-only retirement | After mutation, target `show` reports version 3 and `status: retired`; versions 1 and 2 remain historical. No direct database writer is used. |
| Complete graph validity | `gt projects dependencies validate --json` exits zero with `valid: true`, `errors: []`, and `active_dependency_count: 13`. |
| No unrelated metadata mutation | Recompute the sorted id/version/status/endpoints hash excluding the target; it remains `sha256:57b1d8769c29c1caa5f33a3aa28d155fcb4217e9c7611e097aced58255ec3fe2`. |
| Specification-derived regression | `TEST-11574` passes only when the exact edge is retired, validation is clean, unrelated records are unchanged, and WI-5462 can proceed through its own governed proposal. |
| No authority escalation | Readiness output continues to state `grants_implementation_authority: false`; the repair does not create a PAUTH, GO, claim, or start for any downstream black-box item. |
| Exact finalization | Independent VERIFIED names the implementation report, exact `groundtruth.db` transaction evidence, proposal/report/verdict chain, recommended commit type, and same-transaction path set before the canonical finalizer runs. |

## Risk / Rollback

The write risk is low but governance-significant because `groundtruth.db` is
the canonical metadata carrier. Scope is one append-only record version. The
main failure modes are running against the unfinalized WI-5156 implementation,
retiring the wrong edge, or accepting a graph that still contains another
error; every one is a fail-closed pre/postcondition above.

Rollback cannot erase history. Governed recovery is allowed only if both
endpoints later return to a state that permits an active edge and the complete
graph validates. With the dependent project currently retired, immediate
recovery must fail. Any future recovery requires its own governed rationale and
CLI transaction. Source/configuration rollback is inapplicable because those
surfaces are excluded.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5482-stale-project-dependency-reconciliation`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix(projects)`: this corrects one invalid canonical dependency record and its
bridge evidence without adding a feature or changing source behavior.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
