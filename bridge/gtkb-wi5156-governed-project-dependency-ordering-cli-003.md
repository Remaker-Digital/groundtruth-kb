REVISED
::init gtkb lo
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; build activity envelope; approval_policy=never
author_metadata_source: explicit_interactive_session_metadata


# WI-5156 - Governed Project Dependency and Ordering CLI, Projection Scope Correction

bridge_kind: prime_proposal
Document: gtkb-wi5156-governed-project-dependency-ordering-cli
Version: 003
Author: Prime Builder (Codex, harness A)
Date: 2026-07-17 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5156

target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "scripts/check_project_dependency_ordering.py", "groundtruth-kb/tests/test_project_dependency_ordering.py", "platform_tests/scripts/test_projects_cli.py", ".claude/skills/projects/SKILL.md", ".codex/skills/projects/SKILL.md", ".codex/skills/MANIFEST.json", ".agent/skills/projects/SKILL.md", ".agent/skills/MANIFEST.json", ".cursor/skills/projects/SKILL.md", ".api-harness/skills/projects/SKILL.md", ".api-harness/skills/MANIFEST.json", "config/agent-control/harness-capability-registry.toml"]

implementation_scope: source | test | governed CLI | evaluator | canonical skill | generated cross-harness projections
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Revision Reason

Version 001 named only the canonical projects skill and the Codex projection.
After the independent GO at version 002, the approved implementation changed
the canonical skill and generated the declared Codex projection. The mandatory
projection checks then proved that the original target set was not closed:

- The Codex adapter check reports the projects manifest entry and Codex
  registry hash as derived projection state.
- The Antigravity adapter check reports the projects adapter, manifest entry,
  and Antigravity registry hash as derived projection state.
- The API adapter check reports the projects compact adapter and manifest entry
  as derived projection state.
- `platform_tests/scripts/test_projects_skill_adapter.py` requires the
  `.agent`, `.cursor`, and `.api-harness` projects projections to carry the
  current canonical source hash.

Those seven additional files are mechanically derived consequences of the
canonical skill change. They were clean before this revision and have not been
mutated. This REVISED proposal adds them rather than silently exceeding the
version 002 GO. Existing unrelated adapter drift reported for the verify,
gtkb-hygiene-reclaim, and managed-skill-adoption-review capabilities remains
out of scope and must not be absorbed.

## Summary

Implement the complete governed project-dependency and project-ordering
surface required by `DCL-PROJECT-DEPENDENCY-ORDERING-001`. The implementation
adds canonical directional fields, a versioned dependency-kind registry,
append-only add/retire/recover operations, complete-graph validation,
deterministic readiness and gate enforcement, an exact-set atomic reorder, the
six public `gt projects dependencies` commands, and evaluator
`project-dependency-ordering`.

The canonical projects skill will document that worker mutations are CLI-only,
explain the dependency lifecycle and authority boundary, and be projected to
every projects skill surface currently checked by the repository. Manifest and
registry changes are limited to the `skill.projects` source hash/description
entries generated from that canonical source. The live `groundtruth.db`,
dispatcher/TAFE state, credentials, Git history, deployment, and release remain
outside implementation scope.

After WI-5156 reaches terminal VERIFIED, WI-5462 will separately create the
black-box foundation and downstream child projects, link WI-5268 and WI-5269
through WI-5276, and create the production
`requires_project_state` dependency. No production dependency row is created
by WI-5156.

## Specification Links

- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - defines the sole MemBase authority,
  canonical directional fields, CLI lifecycle, atomic validation, exact-set
  reorder, readiness, gate effects, projection boundary, and assertions
  PROJECT-DEP-A1 through PROJECT-DEP-A5.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - requires the new route to be
  obvious, measurable, reversible, fail-closed, and non-impairing.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - requires
  dependency and ordering rules to be executable rather than narrative.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - requires exact assertion
  reconciliation, current evidence, hashes, execution time, and fail-closed
  incomplete evidence.
- `DCL-CANONICAL-CARRIER-NONAUTHORITY-001` - makes live versioned MemBase
  records authoritative and keeps rendered DAGs, manifests, and cached
  projections non-authoritative.
- `ADR-CROSS-HARNESS-PARITY-001` - requires equivalent projects capability
  semantics across active harnesses.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - requires canonical/generated
  provenance and mechanically current projections without an unapproved
  waiver.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps all implementation and
  temporary evidence within `E:\GT-KB`.
- `GOV-STANDING-BACKLOG-001` - preserves `work_items` as backlog authority and
  project-membership order as the project-scoped sequence.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` - requires the active
  project authorization to cite approved specifications.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - bounds source, test,
  documentation, configuration, and governance-evidence mutations.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - requires a
  current GO, exact claim, and implementation-start packet at each mutation.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - preserves independent
  bridge review and verification despite project authorization.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - governs this REVISED handoff, subsequent
  GO, implementation report, and independent VERIFIED verdict.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - binds every
  target and verification action to governing requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires explicit
  PAUTH, project, work item, and target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires the completed
  report and verdict to execute the mapping below.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - treats dependency versions,
  readiness, evaluator output, and lifecycle evidence as durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - requires stable records and
  explicit lifecycle transitions.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - keeps implementation, projection,
  production-edge creation, verification, and finalization distinct.

## Prior Deliberations

- `DELIB-202666274` - authorizes required modernization implementation while
  preserving bridge, claim, implementation-start, testing, verification, and
  finalization gates.
- `DELIB-20260710-GTKB-MODERNIZATION-PROJECT-DEPENDENCY-ORDERING-DCL-APPROVAL`
  - approves the exact DCL implemented by WI-5156.
- `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-FORMAL-LANGUAGE-DRAFT` - records
  the owner-reviewed formal language and implementation carrier.
- `DELIB-20260715-DISPATCHER-BLACKBOX-SPEC-FOUNDATION-FIRST` - requires WI-5268
  to precede the black-box downstream implementation.
- `bridge/gtkb-first-class-project-artifacts-003.md` - established the
  append-friendly project, membership, dependency, and artifact-link layer.
- `bridge/gtkb-dispatcher-black-box-spec-foundation-017.md` and
  `bridge/gtkb-dispatcher-black-box-spec-foundation-018.md` - establish the
  foundation-first black-box proposal and GO.
- `WI-5462` / `TEST-11568` - preserve the later production dependency
  transaction and do not authorize it in this slice.

## Owner Decisions / Input

- `DELIB-202666274` and
  `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE`
  authorize the bounded implementation classes needed by all fifteen targets.
- `DELIB-20260710-GTKB-MODERNIZATION-PROJECT-DEPENDENCY-ORDERING-DCL-APPROVAL`
  approves WI-5156 as the implementation carrier.
- Mike's active black-box goal and
  `DELIB-20260715-DISPATCHER-BLACKBOX-SPEC-FOUNDATION-FIRST` make WI-5462 the
  immediate production consumer after terminal WI-5156.
- No new owner decision is required. This revision corrects mechanical target
  closure only. Git commit, production MemBase mutation, dispatcher/TAFE
  mutation, credentials, deployment, release, and destructive cleanup remain
  excluded.

## Requirement Sufficiency

Existing requirements sufficient. The DCL already specifies fields, lifecycle,
validation, ordering, readiness, gate effects, projection authority, severity,
and evaluator behavior. This revision changes no requirement semantics; it
only declares every generated projection and metadata carrier required to
verify the already-approved canonical skill change.

## Current Candidate Evidence

The candidate implementation under the version 002 GO currently demonstrates:

- `groundtruth-kb/tests/test_project_dependency_ordering.py`: 11 passed.
- `platform_tests/scripts/test_projects_cli.py`: 16 passed.
- `scripts/check_project_dependency_ordering.py --json`: PASS for exactly
  PROJECT-DEP-A1 through PROJECT-DEP-A5.
- Ruff check and Ruff format check: pass on all six Python targets.
- The evaluator exercises self-edge, two-node cycle, multi-node cycle,
  unknown endpoint, retired endpoint, duplicate edge, unknown kind/state,
  invalid transition, append-only recovery, exact-set reorder, current and
  required state explanations, and six-wave DAG fallback.
- `platform_tests/scripts/test_projects_skill_adapter.py` has three passing
  checks and one expected failure caused only by the undeclared stale
  `.agent`, `.cursor`, and `.api-harness` projections.
- `platform_tests/scripts/test_check_harness_parity.py` has 35 passing checks
  and one pre-existing repository-wide Goose-registry failure unrelated to
  WI-5156.
- The broad project nonimpairment run had 76 passing tests and one
  order-sensitive `test_cli_remove_item_invokes_service` failure that passes
  in isolation. Final verification will rerun the required files in isolated
  processes so cross-file environment leakage cannot be mistaken for a
  WI-5156 regression.

Candidate evidence does not replace the required post-revision GO,
implementation-start packet, completed test run, implementation report, or
independent VERIFIED verdict.

## Revised Implementation Plan

1. Preserve the approved compatibility columns only inside the DB adapter;
   expose canonical `dependent_project_id` and `prerequisite_project_id` to
   worker-facing service and CLI output.
2. Keep the versioned `requires_project_state` registry and atomically validate
   self-edge, cycle, endpoint, semantic duplicate, kind/state/gate, and
   lifecycle constraints before mutation.
3. Enforce declared authorization and closure gates while making readiness
   output explicit that dependency satisfaction grants no bridge, claim,
   PAUTH, or implementation-start authority.
4. Keep add, retire, recover, and exact-set reorder append-only and
   transactionally atomic, including transaction-time membership revalidation.
5. Preserve all six public commands:
   `gt projects dependencies add|show|list|validate|retire|recover`.
6. Keep evaluator `project-dependency-ordering` exact over
   PROJECT-DEP-A1 through PROJECT-DEP-A5 and isolated to a temporary in-root
   MemBase.
7. Update `.claude/skills/projects/SKILL.md`, then mechanically render only the
   projects projections for Codex, Antigravity, Cursor, and API harnesses.
8. Update only the `skill.projects` entries in the three generated manifests
   and the Codex/Antigravity projects source hashes in the capability registry.
   Do not absorb unrelated adapter drift.
9. Keep the production database and all black-box project/dependency rows
   untouched until separately governed WI-5462.

## Cross-Harness Disposition

- **Claude Code B:** canonical `.claude/skills/projects/SKILL.md` contains the
  complete command and authority contract.
- **Codex A:** `.codex/skills/projects/SKILL.md` and its manifest/registry hash
  are generated from the canonical skill.
- **Antigravity C:** `.agent/skills/projects/SKILL.md` and its manifest/registry
  hash are generated from the same canonical skill.
- **Cursor E:** the repository's fallback full-body projection at
  `.cursor/skills/projects/SKILL.md` is deterministically rendered from the
  same canonical source and carries the same source hash.
- **API harnesses:** `.api-harness/skills/projects/SKILL.md` remains the compact
  canonical-source pointer and its manifest entry carries the current source
  hash and description.
- **Ordinary, ops, and build envelopes:** all applicable workers receive the
  same dependency semantics. Activity-envelope mutation authority remains
  independently enforced and is not broadened by this skill.
- No typed parity waiver or alternate dependency store is introduced.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-202666274; DELIB-20260710-GTKB-MODERNIZATION-PROJECT-DEPENDENCY-ORDERING-DCL-APPROVAL; WI-5156; TEST-11325",
  "canonical_authority": "DCL-PROJECT-DEPENDENCY-ORDERING-001; versioned MemBase project dependency and membership records",
  "primary_route": "gt projects dependencies add|show|list|validate|retire|recover and gt projects reorder",
  "before_behavior": "Workers have no governed dependency CLI, primitive fields are directionally ambiguous, and project prerequisites remain narrative.",
  "after_behavior": "Workers use one self-descriptive CLI whose append-only transactions validate the complete graph, enforce declared gates, explain readiness, and fail closed before mutation.",
  "self_descriptive_naming": "dependent_project_id, prerequisite_project_id, dependency_kind, required_prerequisite_state, affected_gate, provenance, and recovery_route expose direction and meaning.",
  "obsolete_guidance_disposition": "Direct KnowledgeDB mutation and bridge-prose dependency claims are not worker mutation routes; physical from/to columns remain compatibility internals only.",
  "history_preservation": "Existing dependency and membership versions remain append-only; generated skill projections and rendered DAGs remain non-authoritative views.",
  "baseline": {
    "public_dependency_cli": "absent",
    "graph_validation": "absent",
    "readiness_gate_enforcement": "absent",
    "dcl_evaluator": "absent",
    "reorder_transactionality": "per-membership commits"
  },
  "expected_result": {
    "public_dependency_cli": "complete governed lifecycle",
    "invalid_operation_behavior": "atomic rejection with zero affected versions",
    "readiness_gate_enforcement": "deterministic declared-gate blocking",
    "dcl_evaluator": "five exact current outer assertions",
    "reorder_transactionality": "one all-or-nothing transaction with transaction-time revalidation"
  },
  "rollback": {
    "instructions": "Through separately authorized focused Git work, revert only the fifteen declared targets to their pre-start hashes.",
    "verification": "Run the focused dependency, project lifecycle, adapter parity, and static-quality suites; no production dependency row requires reversal."
  },
  "hard_invariants": [
    "work_items and current_work_items remain canonical backlog work-record authority",
    "versioned MemBase rows remain the sole dependency and ordering authority",
    "all applicable active harnesses observe equivalent dependency semantics",
    "direct database mutation, rendered DAGs, bridge prose, and cached projections cannot establish dependency state",
    "invalid dependency and reorder requests append no affected version",
    "dependency satisfaction never grants project authorization, bridge GO, work intent, or implementation-start authority",
    "no live groundtruth.db, dispatcher, TAFE, credential, deployment, release, or unrelated worktree state is mutated",
    "all test databases and evidence remain inside E:\\GT-KB"
  ],
  "fail_closed_conditions": [
    "the complete active graph cannot be loaded or validated",
    "a dependency kind, required state, endpoint, provenance, or affected gate is missing or contradictory",
    "recovery would reactivate an invalid graph",
    "readiness evidence is missing, stale, partial, unsupported, or lacks a recovery route",
    "the requested reorder is not the exact current active membership set",
    "a generated projects projection, manifest entry, or registry hash does not match the canonical source"
  ],
  "essential_context_preservation": "Each dependency version retains stable identity, direction, kind, required state, lifecycle, rationale, gate, related work item, provenance, author, timestamp, and change reason; each generated projection retains canonical source provenance."
}
```

## Verification Plan

| Specification / invariant | Executed verification required | Expected result |
| --- | --- | --- |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` PROJECT-DEP-A1/A2 | Focused dependency tests, CLI lifecycle tests, and evaluator | CLI-only worker contract, append-only recoverability, and every invalid case fail atomically |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` PROJECT-DEP-A3; `GOV-STANDING-BACKLOG-001` | Exact-set reorder tests including injected mid-write failure and transaction-time stale membership | Invalid requests append nothing; valid positions are unique/contiguous; global work-item order is unchanged |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` PROJECT-DEP-A4 | State-matrix and declared-gate tests over active/completed/retired/cancelled | Readiness explains every required field and unsatisfied dependencies block only their declared gate |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` PROJECT-DEP-A5; carrier nonauthority | Six-wave temporary-DB evaluator | Five edges are acyclic/queryable; source and registry hashes are reported; rendered DAG is non-authoritative |
| Evaluability and mechanical enforcement | `python scripts/check_project_dependency_ordering.py --json` plus `gt assert --spec DCL-PROJECT-DEPENDENCY-ORDERING-001` in a non-recording mode if available | Exactly five current outer assertions PASS; missing or stale evidence cannot pass |
| Cross-harness parity | Run all three adapter generators in `--check` mode and `pytest platform_tests/scripts/test_projects_skill_adapter.py` | Projects projections/manifests/registry entries are current; any unrelated baseline drift is separately identified and not attributed |
| Nonimpairment | Run `test_project_artifacts.py`, `test_projects_remove_item.py`, `test_project_authorization.py`, and `test_projects_cli.py` in isolated processes | Every required project lifecycle suite passes |
| Static quality | Ruff check, Ruff format check, `py_compile`, and `git diff --check` over exact targets | No errors or whitespace findings |
| Bridge governance | Applicability preflight, clause preflight, exact claim, schema-v3 implementation-start packet, report mapping, independent verification | Every gate passes with the fifteen exact targets |

## Acceptance Criteria

- Worker-facing dependency operations exist only through the governed nested
  CLI and use canonical directional names.
- Every mutation is append-only and complete-graph validated; rejected
  dependency/reorder operations append no affected version.
- Readiness and declared authorization/closure gates are deterministic and
  never confer implementation authority.
- `project-dependency-ordering` reconciles exactly PROJECT-DEP-A1 through
  PROJECT-DEP-A5 with current hashes and invalidation state.
- Canonical and generated projects skill surfaces carry the same source hash
  and semantics; manifests and registry agree.
- No unrelated adapter, manifest, or registry hunk is absorbed.
- No live MemBase, dispatcher/TAFE, credential, deployment, release, or Git
  mutation occurs.
- A complete implementation report receives independent VERIFIED before
  WI-5156 is finalized or WI-5462 mutates production project metadata.

## Risk And Rollback

- **Projection breadth:** generated metadata spans multiple harness surfaces.
  Mitigation: limit changes to the projects adapter bodies, their manifest
  entries, and two registry hash lines; inspect each exact diff.
- **Shared registry:** unrelated capability drift exists. Mitigation: hunk-only
  update of `skill.projects`; preserve every foreign byte.
- **Schema compatibility:** physical legacy columns remain internal. Mitigation:
  lazy write-time migration and focused legacy project-artifact regression.
- **Atomicity:** failures could otherwise leave partial versions. Mitigation:
  transaction-time revalidation, rollback tests, and row-count evidence across
  projects, dependencies, memberships, and work items.
- **Rollback:** through separately authorized focused Git work, revert only the
  fifteen declared targets to their pre-start hashes. No production dependency
  row needs reversal because this slice creates none.

## Pre-Filing Preflight

The candidate-content applicability and clause preflights will be run against
this completed revision immediately before helper-mediated filing. Filing is
permitted only when applicability reports no missing required/advisory specs
and clause preflight reports zero blocking gaps.
