NEW
::init gtkb lo
::open build

# WI-5156 - Governed Project Dependency and Ordering CLI

bridge_kind: prime_proposal
Document: gtkb-wi5156-governed-project-dependency-ordering-cli
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-17 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; build activity envelope; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5156

target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "scripts/check_project_dependency_ordering.py", "groundtruth-kb/tests/test_project_dependency_ordering.py", "platform_tests/scripts/test_projects_cli.py", ".claude/skills/projects/SKILL.md", ".codex/skills/projects/SKILL.md"]

implementation_scope: source | test | governed CLI | evaluator | canonical skill projection
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implement the complete governed project-dependency and project-ordering surface
required by `DCL-PROJECT-DEPENDENCY-ORDERING-001`. MemBase already has a
primitive `project_dependencies` table and direct `KnowledgeDB` methods, but
the public `gt projects dependencies add|show|list|validate|retire|recover`
commands do not exist. The primitive rows also use ambiguous
`from_project_id` / `to_project_id` names and lack required-state, affected-gate,
provenance, registry, graph-validation, recovery, and readiness semantics.
Consequently the DCL is specified but not executable, and workers cannot use
its sole governed mutation route.

This slice will make dependency lifecycle operations append-only,
self-descriptive, transactionally validated, queryable, and recoverable. It
will also harden `gt projects reorder` so validation and all membership-version
appends occur atomically. A deterministic evaluator will implement the five
outer assertions already stored on the DCL. The live `groundtruth.db` is not a
target of this implementation proposal: all implementation verification uses
temporary databases. After WI-5156 reaches terminal VERIFIED, WI-5462 will use
the new CLI to create separate foundation and downstream black-box child
projects, link WI-5268 and WI-5269 through WI-5276 to those projects, and add a
`requires_project_state` edge from downstream to foundation. That later
governed metadata transaction is the production proving case.

## Specification Links

- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - defines the canonical fields,
  initial dependency kind, CLI-only lifecycle, invalid-edge rejection,
  exact-set reorder, readiness explanation, evaluator contract, and five outer
  assertions implemented by this slice.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - requires the governed route to
  be obvious, self-descriptive, measurable, reversible, and fail-closed without
  impairing existing project and backlog behavior.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - requires
  project dependency and ordering requirements to be enforced mechanically,
  not left as bridge prose or reviewer memory.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - requires the DCL's
  evaluator to reconcile all required outer assertion IDs, report current
  evidence, and never turn missing or partial coverage into PASS.
- `DCL-CANONICAL-CARRIER-NONAUTHORITY-001` - keeps versioned MemBase rows and
  the governed CLI as authority; bridge prose, rendered DAGs, dashboards, and
  cached projections remain evidence or views only.
- `ADR-CROSS-HARNESS-PARITY-001` - the projects skill is a universal governed
  CLI capability; behavioral meaning must remain equivalent wherever an active
  harness loads the canonical or generated skill.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - requires the explicit
  cross-harness disposition below and verifies the canonical `.claude` skill
  and generated `.codex` projection do not drift.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all implementation, temporary
  databases, fixtures, generated skill adapters, and evaluator evidence remain
  inside `E:\GT-KB`; no adopter or out-of-root project dependency is created.
- `GOV-STANDING-BACKLOG-001` - preserves `work_items` /
  `current_work_items` as backlog authority while projects and memberships
  organize those canonical work items.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` - the active project
  authorization and this proposal link the approved dependency-ordering DCL.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - the active PAUTH bounds this
  source, test, documentation, and governance-evidence implementation.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - protected
  mutation remains gated on independent GO, exact work intent, and
  implementation-start authorization at operation time.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - project authorization
  does not replace bridge review, implementation start, verification, or
  focused finalization.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal, an independent GO, the
  implementation report, and independent VERIFIED verdict are the lifecycle
  handoff records.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - binds the exact
  implementation targets and tests to the governing specifications.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the PAUTH, project,
  WI-5156, and exact target paths are explicit and machine-readable.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - terminal verification
  must execute the mapping below and reject any missing linked-spec coverage.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - dependencies, validation results,
  readiness explanations, and lifecycle transitions remain durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - dependency state is represented by
  stable records and evidence rather than inferred from narrative.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - add, retire, recover, reorder,
  verification, and later production-edge creation remain separate governed
  transitions.

## Prior Deliberations

- `DELIB-202666274` - Mike authorized all required GT-KB modernization
  implementation work at project scope while preserving bridge, work-intent,
  implementation-start, independent review, and mechanical-operation gates.
- `DELIB-20260710-GTKB-MODERNIZATION-PROJECT-DEPENDENCY-ORDERING-DCL-APPROVAL`
  - approved the exact canonical DCL implemented here.
- `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-FORMAL-LANGUAGE-DRAFT` - contains
  the owner-reviewed formal language and the intended implementation carrier.
- `DELIB-20260715-DISPATCHER-BLACKBOX-SPEC-FOUNDATION-FIRST` - requires the
  dispatcher black-box implementation to begin with WI-5268 and requires
  downstream work to depend on that foundation.
- `bridge/gtkb-first-class-project-artifacts-003.md` - established the
  append-friendly project, membership, dependency, and artifact-link layer
  over canonical work items; this slice completes its dependency lifecycle.
- `bridge/gtkb-dispatcher-black-box-spec-foundation-017.md` and
  `bridge/gtkb-dispatcher-black-box-spec-foundation-018.md` - record the
  approved foundation-first black-box proposal and GO whose dependency is
  currently enforced only through narrative and review.
- `WI-5462` / `TEST-11568` - preserve the production defect and will exercise
  this CLI after WI-5156 is terminal; they do not authorize direct database
  mutation in this slice.

## Owner Decisions / Input

- `DELIB-202666274` authorizes required modernization blocker repairs at the
  project level. It expressly preserves the bridge, independent GO,
  implementation-start, testing, independent VERIFIED, and operation-specific
  safety gates.
- `DELIB-20260710-GTKB-MODERNIZATION-PROJECT-DEPENDENCY-ORDERING-DCL-APPROVAL`
  approves the exact design constraint and names WI-5156 as its implementation
  work item.
- `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE`
  is active, has no per-work-item exclusion, permits the declared mutation
  classes, and includes `DCL-PROJECT-DEPENDENCY-ORDERING-001`.
- The owner-directed black-box goal and
  `DELIB-20260715-DISPATCHER-BLACKBOX-SPEC-FOUNDATION-FIRST` make WI-5462 the
  immediate production consumer. No new owner decision is required to review
  WI-5156. Git commit, live MemBase mutation, dispatcher/TAFE mutation,
  deployment, release, credentials, and destructive cleanup remain outside
  this proposal.

## Requirement Sufficiency

Existing requirements sufficient.
`DCL-PROJECT-DEPENDENCY-ORDERING-001` specifies the complete worker-facing
contract, lifecycle, validator behavior, readiness semantics, projection
boundary, severity, evaluator route, and required assertions.
`GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`,
`DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`, and
`DCL-CANONICAL-CARRIER-NONAUTHORITY-001` supply the cross-cutting
nonimpairment, evidence, and authority constraints. No new or revised formal
requirement is needed before implementation.

## Current-State Evidence

- `gt projects dependencies --help` exits with
  `Error: No such command 'dependencies'`.
- `KnowledgeDB.add_project_dependency()` commits primitive rows directly,
  accepts ambiguous source/target names, and performs no self-edge, cycle,
  retired-endpoint, duplicate-active-edge, kind, state, or lifecycle checks.
- `KnowledgeDB.list_project_dependencies()` exposes the ambiguous physical
  fields directly.
- `ProjectLifecycleService.show_project()` reads primitive dependency rows but
  provides no dependency lifecycle or readiness API.
- `ProjectLifecycleService.reorder_project_items()` validates the requested set
  before writing but commits each membership version separately; a mid-write
  failure can leave a partial reorder.
- `scripts/check_project_dependency_ordering.py` does not exist, so
  `DCL-PROJECT-DEPENDENCY-ORDERING-001` remains `specified` and its five outer
  assertions lack executable evidence.
- The black-box hardening project has no project dependency rows. Because
  WI-5268 and WI-5269 through WI-5276 are members of the same parent project,
  adding a parent-project self-edge would be invalid. The production model must
  use separate child projects and a directional child-project edge.

## Proposed Implementation

1. Extend the project-dependency schema and migration path with canonical
   worker-facing fields:
   `dependent_project_id`, `prerequisite_project_id`, `dependency_kind`,
   `required_prerequisite_state`, `affected_gate`, and `provenance`.
   Preserve existing `from_project_id`, `to_project_id`, and
   `dependency_type` only inside an explicit compatibility migration/adapter.
   New reads and CLI output use canonical names.
2. Define a versioned in-code dependency-kind registry with the initial
   `requires_project_state` kind, supported project states, deterministic gate
   effects, and recovery metadata. Reject unknown kinds and states.
3. Add transaction-aware database write primitives so dependency add, retire,
   recover, and full project reorder append all required versions atomically.
   Any validation or write failure rolls back the complete transaction and
   appends no project, dependency, membership, or work-item version.
4. Add lifecycle-service operations for:
   - self-edge, endpoint existence, endpoint lifecycle, duplicate semantic
     edge, and full active-graph cycle checks;
   - add, show, list, validate, retire, and recover;
   - complete-graph revalidation before recovery;
   - deterministic readiness explanations containing dependency ID, endpoint
     IDs, current and required states, satisfaction, affected gate,
     provenance, and recovery route;
   - exact active-membership reorder with unique contiguous positions and one
     atomic commit.
5. Add the nested public CLI:
   `gt projects dependencies add|show|list|validate|retire|recover`.
   Mutations require explicit `--change-reason` and author provenance.
   Read commands support JSON. Directional option names use
   `--dependent-project` and `--prerequisite-project`; ambiguous
   `--from` / `--to` options are not introduced.
6. Add `scripts/check_project_dependency_ordering.py` as evaluator
   `project-dependency-ordering`. It will reconcile exactly
   `PROJECT-DEP-A1` through `PROJECT-DEP-A5`, report subject and registry
   versions/hashes plus execution time, fail on missing/partial/stale evidence,
   and exercise the modernization six-wave DAG without making a rendered DAG
   authoritative.
7. Update the canonical `.claude` projects skill with the new command contract
   and regenerate the `.codex` adapter. No hand edit of the generated adapter
   is permitted.
8. Keep live MemBase mutation out of this implementation. After terminal
   WI-5156, WI-5462 will create two child projects under the black-box parent,
   add WI-5268 to the foundation child, add WI-5269 through WI-5276 to the
   downstream child, and register a downstream
   `requires_project_state` foundation-child dependency. That separate
   proposal must name `groundtruth.db` and its exact metadata transaction.

## Cross-Harness Disposition

- **Claude Code B:** `.claude/skills/projects/SKILL.md` remains the canonical
  human- and worker-facing command contract. It gains the complete dependency
  lifecycle, readiness, and recovery commands with the same semantics as the
  executable `gt projects` CLI.
- **Codex A:** `.codex/skills/projects/SKILL.md` is regenerated from the
  canonical Claude skill through
  `scripts/generate_codex_skill_adapters.py`; byte-derived adapter metadata and
  focused adapter tests must pass. It is not hand-edited.
- **Antigravity C and Cursor E:** both consume the same installed `gt` CLI
  semantics. No harness-specific dependency store, alternate command, role
  exception, or direct database route is introduced.
- **Ollama D, OpenRouter F, and Alibaba H:** provider-backed workers receive
  the same project dependency semantics whenever their activity envelope and
  role permit project lifecycle work. Their dispatch, eligibility, model,
  lifetime, and routing behavior is unchanged.
- **Templates and future harnesses:** the canonical skill remains the source
  projected through the managed skill adapter pipeline. Any future adopter must
  expose behaviorally equivalent commands or obtain an owner-approved typed
  waiver.
- No typed waiver is requested. The CLI, field direction, validation,
  readiness, lifecycle, and failure behavior are universal across applicable
  active harnesses.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-202666274; DELIB-20260710-GTKB-MODERNIZATION-PROJECT-DEPENDENCY-ORDERING-DCL-APPROVAL; WI-5156; TEST-11325",
  "canonical_authority": "DCL-PROJECT-DEPENDENCY-ORDERING-001; versioned MemBase project dependency and membership records",
  "primary_route": "gt projects dependencies add|show|list|validate|retire|recover and gt projects reorder",
  "before_behavior": "Dependency rows can be created only through a direct Python API with ambiguous endpoint names and no governed graph or lifecycle validation; narrative prerequisites are not mechanically enforced.",
  "after_behavior": "Workers use one self-descriptive CLI whose append-only transactions validate the complete active graph, explain readiness, preserve history, and fail closed before mutation.",
  "self_descriptive_naming": "dependent_project_id, prerequisite_project_id, dependency_kind, required_prerequisite_state, affected_gate, provenance, and recovery_route expose direction and meaning without inference.",
  "obsolete_guidance_disposition": "Direct KnowledgeDB mutation and bridge-prose dependency claims are not governed worker mutation routes; ambiguous from/to fields remain compatibility internals only.",
  "history_preservation": "Existing project dependency and membership versions remain append-only and are migrated or adapted without deletion; rendered DAGs and bridge records remain non-authoritative evidence.",
  "baseline": {
    "public_dependency_cli": "absent",
    "graph_validation": "absent",
    "readiness_explanation": "absent",
    "dcl_assertion_evaluator": "absent",
    "reorder_transactionality": "per-membership commits"
  },
  "expected_result": {
    "public_dependency_cli": "complete governed lifecycle",
    "invalid_edge_behavior": "atomic rejection with zero appended versions",
    "readiness_explanation": "deterministic per-edge evidence",
    "dcl_assertion_evaluator": "five exact outer assertions with currentness metadata",
    "reorder_transactionality": "one all-or-nothing transaction"
  },
  "rollback": {
    "instructions": "Revert only the eight declared source, test, skill, and evaluator paths through a separately authorized focused Git operation; no production dependency row is created by this slice.",
    "verification": "Run the existing project lifecycle and project artifact suites and confirm legacy project list, show, membership, authorization, completion, and backlog behavior remains unchanged."
  },
  "hard_invariants": [
    "work_items and current_work_items remain canonical backlog work-record authority",
    "versioned MemBase rows remain the sole dependency and ordering authority",
    "all applicable active harnesses observe equivalent dependency lifecycle and readiness behavior through the same gt projects CLI",
    "direct database mutation, rendered DAGs, bridge prose, and cached projections cannot establish dependency state",
    "self-edges, cycles, unknown or retired endpoints, duplicate active semantic edges, unknown kinds or states, and contradictory lifecycle transitions append no versions",
    "an unsatisfied hard dependency blocks only its declared gate and never grants project authorization, bridge GO, work intent, or implementation-start authority",
    "no live groundtruth.db, dispatcher, TAFE, harness, routing, credential, deployment, release, or unrelated worktree state is mutated by implementation or tests",
    "all test databases and evidence remain inside E:\\GT-KB"
  ],
  "fail_closed_conditions": [
    "the complete active graph cannot be loaded or validated",
    "a dependency kind or required state is absent from the governed registry",
    "endpoint lifecycle, current state, provenance, or affected gate is missing or contradictory",
    "recovery would reactivate a duplicate edge, self-edge, cycle, or invalid endpoint",
    "readiness evidence is missing, stale, partial, unsupported, or cannot identify a recovery route",
    "the requested reorder is missing, duplicates, or adds an active project member"
  ],
  "essential_context_preservation": "Each dependency version retains stable ID, endpoint direction, kind, required state, lifecycle, rationale, affected gate, related work item, provenance, author, timestamp, and change reason; evaluator evidence retains subject and registry currentness."
}
```

## Spec-Derived Verification Plan

| Specification / invariant | Verification | Expected result |
| --- | --- | --- |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` PROJECT-DEP-A1 | `groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_project_dependency_ordering.py platform_tests/scripts/test_projects_cli.py -q --tb=short` lifecycle cases for add/show/list/validate/retire/recover, append-only history, and direct-route rejection | All governed commands pass; each lifecycle transition appends one current version and preserves prior versions. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` PROJECT-DEP-A2 | Focused fixtures for self-edge, two- and multi-node cycles, unknown endpoint, retired endpoint, duplicate semantic edge, invalid kind/state, contradictory retirement/recovery, and injected mid-transaction failure | Every case fails deterministically and row/version counts for projects, dependencies, memberships, and work items remain unchanged. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` PROJECT-DEP-A3; `GOV-STANDING-BACKLOG-001` | Existing and new reorder tests cover missing, extra, duplicate, foreign, inactive, and mid-write failure cases plus a valid non-default start position | Invalid requests append nothing; valid output is unique and contiguous in `membership_order`; `work_items.implementation_order` is not mutated. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` PROJECT-DEP-A4 | CLI JSON fixtures evaluate satisfied and unsatisfied `requires_project_state` edges across active, completed, retired, and cancelled prerequisite states | Every edge reports ID, endpoints, current/required state, satisfaction, affected gate, provenance, and recovery route; unsatisfied edges block only the declared gate. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` PROJECT-DEP-A5 | Temporary-DB six-wave DAG fixture plus `groundtruth-kb/.venv/Scripts/python.exe scripts/check_project_dependency_ordering.py --json` | The DAG is acyclic and queryable, projection hashes/versions are reported, and loss of a rendered projection falls back to live CLI-backed records. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Evaluator tests reconcile the exact stored outer IDs and simulate missing, unsupported, stale, partial, contradictory, and complete evidence | Incomplete evidence is FAIL/PARTIAL/UNASSESSED, never PASS; exact current complete evidence passes. |
| `DCL-CANONICAL-CARRIER-NONAUTHORITY-001`; `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | Tests attempt direct service/database bypass classifications and modify non-authoritative rendered/prose fixtures | Only governed CLI transactions establish state; non-authoritative fixtures never satisfy a dependency gate. |
| `ADR-CROSS-HARNESS-PARITY-001`; `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | `groundtruth-kb/.venv/Scripts/python.exe scripts/generate_codex_skill_adapters.py --check --update-registry`, `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_projects_skill_adapter.py platform_tests/scripts/test_check_harness_parity.py -q --tb=short`, and direct canonical/generated skill provenance comparison | Claude canonical and Codex generated skill surfaces remain synchronized; the same `gt projects` behavior applies to every applicable active harness; no waiver or alternate route exists. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Path-boundary fixtures and a test-artifact inventory verify every temporary database, DAG fixture, generated adapter, and evaluator output resolves inside the pytest temporary root under `E:\GT-KB` | No live dependency, test artifact, or generated output resolves outside the mandatory project root or into an adopter repository. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_project_artifacts.py groundtruth-kb/tests/test_projects_remove_item.py platform_tests/scripts/test_project_authorization.py platform_tests/scripts/test_projects_cli.py -q --tb=short` | Existing project, membership, artifact-link, authorization, removal, completion, and reporting behavior remains green. |
| Canonical skill projection | `groundtruth-kb/.venv/Scripts/python.exe scripts/generate_codex_skill_adapters.py --check --update-registry` followed by `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_projects_skill_adapter.py -q --tb=short` | Canonical and generated projects skills are byte-derived and registry checks pass. |
| Formatting and static quality | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/src/groundtruth_kb/project/lifecycle.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_project_dependency_ordering.py platform_tests/scripts/test_projects_cli.py scripts/check_project_dependency_ordering.py` and matching `ruff format --check` | No lint or formatting findings on exact Python targets. |
| Bridge and clause gates | Candidate and live `bridge_applicability_preflight.py`, `adr_dcl_clause_preflight.py`, and `git diff --check --` over exact targets | No missing required/advisory specs, zero blocking clause gaps, and no whitespace errors. |

## Acceptance Criteria

- The exact nested dependency CLI named by the DCL exists with all six verbs.
- Worker-facing dependency records use canonical directional field names.
- The initial dependency-kind registry is versioned and rejects unsupported
  kinds, states, and gate effects.
- All invalid add/recover/reorder requests are atomic no-ops.
- Retirement and recovery preserve complete append-only history.
- Readiness output explains all active satisfied and unsatisfied edges and
  provides a recovery route without granting unrelated authority.
- Exact project membership order remains canonical and contiguous after valid
  reorder; the compatibility work-item order does not compete.
- `project-dependency-ordering` executes and reconciles
  PROJECT-DEP-A1 through PROJECT-DEP-A5.
- The modernization six-wave DAG is representable and queryable without making
  its rendering authoritative.
- Existing project lifecycle, backlog, authorization, and completion behavior
  remains green.
- No live MemBase dependency row or black-box project/subproject mutation
  occurs until the separately governed WI-5462 transaction.

## Risk / Rollback

The primary risks are schema compatibility, accidental partial writes, reversed
edge direction, and false-ready results. Canonical fields and explicit CLI
options remove directional inference; complete-graph prevalidation and one
transaction per mutation prevent partial state; readiness fixtures cover every
supported prerequisite state. Existing primitive fields remain isolated in a
tested compatibility migration rather than being silently reinterpreted.

Rollback is source-only for this slice because production MemBase mutation is
excluded. A separately authorized focused Git operation can revert the eight
declared paths, after which the existing project lifecycle regression suite must
pass. No migration is run against live `groundtruth.db` until WI-5462 has its
own PAUTH, proposal, GO, claim, and implementation-start evidence.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5156-governed-project-dependency-ordering-cli`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`feat(projects):` because this adds the governed dependency lifecycle, CLI,
readiness, and evaluator surface specified by the DCL.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
