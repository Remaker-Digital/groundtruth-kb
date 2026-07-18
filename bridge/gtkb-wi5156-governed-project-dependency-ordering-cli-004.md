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

# WI-5156 Project Dependency CLI - Generated Projection Target Closure

bridge_kind: prime_proposal
Document: gtkb-wi5156-governed-project-dependency-ordering-cli
Version: 004
Responds to: bridge/gtkb-wi5156-governed-project-dependency-ordering-cli-003.md
Supersedes for implementation authority: bridge/gtkb-wi5156-governed-project-dependency-ordering-cli-003.md
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5156
target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "scripts/check_project_dependency_ordering.py", "groundtruth-kb/tests/test_project_dependency_ordering.py", "platform_tests/scripts/test_projects_cli.py", ".claude/skills/projects/SKILL.md", ".codex/skills/projects/SKILL.md", ".codex/skills/MANIFEST.json", ".agent/skills/projects/SKILL.md", ".agent/skills/MANIFEST.json", ".cursor/skills/projects/SKILL.md", ".api-harness/skills/projects/SKILL.md", ".api-harness/skills/MANIFEST.json", "config/agent-control/harness-capability-registry.toml"]
implementation_scope: source | test | governed CLI | evaluator | canonical skill | generated cross-harness projections
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Review Scope

This is a delta-only replacement for version 003. The dependency model,
governed CLI, append-only lifecycle, graph validation, exact-set reorder,
readiness semantics, evaluator, tests, canonical projects skill, requirement
links, and verification plan remain exactly those in the canonical version-003
proposal.

The original version-002 GO covered the first eight implementation targets.
Repository projection checks proved that changing the canonical projects skill
also requires seven mechanically derived target updates:

- `.codex/skills/MANIFEST.json`
- `.agent/skills/projects/SKILL.md`
- `.agent/skills/MANIFEST.json`
- `.cursor/skills/projects/SKILL.md`
- `.api-harness/skills/projects/SKILL.md`
- `.api-harness/skills/MANIFEST.json`
- `config/agent-control/harness-capability-registry.toml`

Version 003 declared all fifteen targets but two independent review claims
expired without a verdict. Version 004 asks the reviewer to evaluate the target
closure delta only. It changes no requirement or implementation behavior.

## Canonical Authority

This revision relies only on:

- MemBase WI-5156, TEST-11325, the active project authorization, and the
  governing specifications below;
- `DELIB-202666274`;
- `DELIB-20260710-GTKB-MODERNIZATION-PROJECT-DEPENDENCY-ORDERING-DCL-APPROVAL`;
- `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-FORMAL-LANGUAGE-DRAFT`;
- `DELIB-20260715-DISPATCHER-BLACKBOX-SPEC-FOUNDATION-FIRST`;
- `bridge/gtkb-first-class-project-artifacts-003.md`;
- `bridge/gtkb-wi5156-governed-project-dependency-ordering-cli-001.md`;
- `bridge/gtkb-wi5156-governed-project-dependency-ordering-cli-002.md`; and
- `bridge/gtkb-wi5156-governed-project-dependency-ordering-cli-003.md`.

No scratchpad, harness-local state, generated test output, dispatcher record,
retired surface, or noncanonical file is cited as evidence.

## Preserved Implementation Contract

Version 003 remains the canonical detailed contract. In summary, WI-5156:

1. exposes canonical `dependent_project_id` and `prerequisite_project_id`;
2. provides append-only add/show/list/validate/retire/recover dependency
   lifecycle under `gt projects dependencies`;
3. rejects self edges, cycles, unknown or retired endpoints, semantic
   duplicates, invalid kinds/states/transitions, and invalid recovery before
   mutation;
4. makes exact-set project membership reorder one atomic transaction with
   transaction-time revalidation;
5. explains dependency readiness and blocks only each edge's declared gate
   without conferring PAUTH, bridge GO, claim, or implementation-start
   authority;
6. evaluates exactly PROJECT-DEP-A1 through PROJECT-DEP-A5 against an in-root
   temporary MemBase; and
7. projects the canonical projects skill consistently to Codex, Antigravity,
   Cursor, and API harness surfaces.

No production dependency row is created. WI-5462 remains the separately
governed production consumer after WI-5156 is terminal VERIFIED.

## Cross-Harness Disposition

- **Claude Code B:** `.claude/skills/projects/SKILL.md` is the canonical
  complete command and authority contract.
- **Codex A:** `.codex/skills/projects/SKILL.md`, its manifest entry, and the
  projects registry hash are generated from the canonical skill.
- **Antigravity C:** `.agent/skills/projects/SKILL.md`, its manifest entry, and
  its projects registry hash are generated from the same canonical skill.
- **Cursor E:** `.cursor/skills/projects/SKILL.md` is the repository's
  deterministic full-body projection of the same canonical source.
- **API harnesses:** `.api-harness/skills/projects/SKILL.md` remains the compact
  canonical-source pointer and its manifest entry carries the same source hash.
- **Ordinary, ops, and build envelopes:** every applicable worker receives the
  same dependency semantics; activity-envelope mutation authority remains
  independently enforced.

No typed parity waiver or alternate dependency store is introduced. Generated
changes outside the projects capability fail the implementation.

## Specification Links

- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `DCL-CANONICAL-CARRIER-NONAUTHORITY-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Requirement Sufficiency

Existing requirements sufficient. Version 004 closes generated-target scope
only. The approved DCL already defines every dependency field, lifecycle,
validation, ordering, readiness, gate, projection-authority, severity, and
evaluator behavior. No new owner decision is required.

## Implementation Plan

After a fresh independent GO responding to version 004:

1. Acquire a fresh `go_implementation` claim and schema-v3 start packet for
   the active PAUTH and all fifteen exact targets.
2. Re-run applicability and mandatory-clause preflights and confirm no target
   has been claimed by incompatible foreign work.
3. Preserve the existing version-002-authorized implementation hunks in the
   first eight targets.
4. Run the canonical Codex, Antigravity, and API skill adapter generators so
   only the declared projects adapters, manifests, and projects registry hashes
   are refreshed.
5. Reject any generated change outside the fifteen-target set or any unrelated
   capability drift.
6. Execute the complete specification-derived verification below.
7. File an implementation report for independent VERIFIED review. Do not
   mutate live `groundtruth.db`, dispatcher/TAFE state, Git history,
   credentials, deployment, release, or external systems.

## Specification-Derived Verification

| Requirement | Required execution | Required result |
| --- | --- | --- |
| PROJECT-DEP-A1/A2 | Focused dependency tests, CLI lifecycle tests, evaluator | Governed append-only lifecycle; all invalid cases reject atomically |
| PROJECT-DEP-A3 | Exact-set reorder tests including injected failure and stale membership | Valid order unique/contiguous; invalid requests append nothing |
| PROJECT-DEP-A4 | State matrix and declared-gate tests | Complete readiness explanations; only declared gates block |
| PROJECT-DEP-A5 | Six-wave temporary-DB evaluator | Five acyclic/queryable edges; rendered DAG remains non-authoritative |
| Evaluability | `scripts/check_project_dependency_ordering.py --json` | Exactly PROJECT-DEP-A1 through A5 PASS with current hashes |
| Cross-harness parity | Three adapter generators in check mode plus projects adapter tests | All projects projections/manifests/registry entries current |
| Nonimpairment | Project artifacts, remove-item, authorization, and projects CLI suites in isolated processes | All focused suites pass |
| Static quality | Ruff check/format, py_compile, and diff check over exact Python targets | No errors |
| Governance | Applicability, clause, exact claim/start, report map, independent review | Every gate covers all fifteen exact targets |

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DCL-PROJECT-DEPENDENCY-ORDERING-001; WI-5156; TEST-11325; bridge/gtkb-wi5156-governed-project-dependency-ordering-cli-003.md",
  "canonical_authority": "Versioned MemBase project dependency and membership records",
  "primary_route": "gt projects dependencies add|show|list|validate|retire|recover and gt projects reorder",
  "before_behavior": "No governed dependency CLI exists and project prerequisites remain narrative.",
  "after_behavior": "One governed append-only CLI validates the complete graph, explains readiness, and enforces declared gates.",
  "self_descriptive_naming": "dependent_project_id, prerequisite_project_id, dependency_kind, required_prerequisite_state, affected_gate, provenance, and recovery_route",
  "obsolete_guidance_disposition": "Direct KnowledgeDB mutation and rendered DAGs are not worker authority routes.",
  "history_preservation": "Dependency and membership versions remain append-only; generated harness surfaces remain non-authoritative projections.",
  "baseline": {
    "public_dependency_cli": "absent",
    "graph_validation": "absent",
    "reorder_transactionality": "per-membership commits"
  },
  "expected_result": {
    "public_dependency_cli": "complete governed lifecycle",
    "invalid_operation_behavior": "atomic rejection",
    "reorder_transactionality": "one all-or-nothing transaction"
  },
  "rollback": {
    "instructions": "Through separately authorized focused Git work, revert only the fifteen declared targets.",
    "verification": "Repeat focused lifecycle, evaluator, parity, and static-quality checks."
  },
  "hard_invariants": [
    "MemBase remains sole dependency and ordering authority",
    "dependency satisfaction never grants implementation authority",
    "invalid operations append no affected version",
    "generated projections remain mechanically current and non-authoritative",
    "no live groundtruth.db or dispatcher/TAFE mutation"
  ],
  "fail_closed_conditions": [
    "the active graph cannot be completely loaded",
    "an edge field or endpoint is missing or contradictory",
    "recovery would reactivate an invalid graph",
    "reorder membership is not the exact active set",
    "a projects projection or source hash is stale"
  ],
  "essential_context_preservation": "Each edge retains stable direction, kind, state, lifecycle, rationale, gate, provenance, author, timestamp, and change reason."
}
```

## Acceptance Criteria

- [x] Version 004 preserves the full version-003 implementation contract.
- [x] All fifteen canonical and generated targets are declared.
- [x] The delta is limited to seven mechanically required projection targets.
- [x] Applicability and mandatory-clause preflights pass.
- [ ] Fresh independent GO approves version 004.
- [ ] Fresh claim/start covers all fifteen exact targets.
- [ ] Complete focused verification passes.
- [ ] Independent Loyal Opposition issues VERIFIED before WI-5462 proceeds.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
