NEW
::init gtkb pb
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fe1fd-61a9-7742-a7bf-5e44e1ec9de4
author_model: GPT-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined ::init gtkb pb; build envelope
author_metadata_source: session envelope (worker_role_provenance)

bridge_kind: prime_proposal
Document: gtkb-adbr-t0-p6-githooks-taxonomy-classification
Version: 001
Project Authorization: PAUTH-PROJECT-GTKB-AGENT-DIRECTION-BASELINE-REMEDIATION-T0-T6
Project: PROJECT-GTKB-AGENT-DIRECTION-BASELINE-REMEDIATION
Work Item: WI-6040

target_paths: ["config/governance/project-authorization-operation-taxonomy.toml", "groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py", "groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py"]
implementation_scope: Implement owner-approved ADBR T0 prerequisite P6 by making `.githooks/**` a governed `configuration` path class in the canonical project-authorization taxonomy, teaching the canonical evaluator to consume that rule, and adding focused regression coverage.
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

# ADBR T0 P6 — `.githooks/**` Project-Authorization Taxonomy Classification

## Summary

ADBR T0 cannot register its AC-10 projection-drift check in `.githooks/pre-commit` because the canonical operation-time evaluator currently classifies that path as `unclassified`. The owner approved prerequisite P6 in `DELIB-20260809-ADBR-T0-P6-001`: add a `.githooks/**` classification rule so the pre-commit registration can be authorized.

The live implementation has an additional mechanical constraint that the originating T0 proposal did not describe: `config/governance/project-authorization-operation-taxonomy.toml` currently registers only canonical class/operation names and aliases. `classify_target()` in `groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py` hard-codes path routing and does not consume path rules from the TOML. Adding an inert alias or unconsumed TOML field would leave `.githooks/pre-commit` unclassified and would not satisfy P6.

This proposal therefore implements the smallest effective P6 slice across exactly three clean targets: a governed TOML path rule, evaluator support for that rule, and a focused regression test. It does not modify `.githooks/pre-commit`; it only makes that later T0 target classifiable under the already-allowed `configuration` mutation class.

## Current Evidence

- `classify_target('.githooks/pre-commit').mutation_class` currently returns `unclassified`.
- `classify_target('.gitattributes').mutation_class` returns `repository_metadata`; P5 separately added that class to PAUTH version 5.
- The taxonomy's `configuration` class already owns the alias `hook`, so `configuration` is the established semantic family for hook configuration.
- `_load_operation_taxonomy()` currently parses only `mutation_class` and `operation` tables; `OperationTaxonomy` carries no path-rule collection.
- Focused `git status --short` and `git diff` over all three declared targets produced no output before drafting. The wider worktree is dirty with foreign work and will be preserved.

## Requirement Sufficiency

**Existing requirements sufficient.** `DELIB-20260809-ADBR-T0-P6-001` supplies the owner decision, and the linked DCL/GOV records already require a governed versioned taxonomy, exact single-class path resolution, fail-closed unknown classification, exact proposal target scoping, and specification-derived executable tests. No new or revised requirement is needed before implementation.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — project authorization remains additive to bridge GO, exact target paths, a work-intent claim, and a fresh implementation-start packet.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — operation names and mutation classes come from a governed versioned taxonomy; every target must resolve to exactly one allowed class; unknown or ambiguous paths deny.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — the AC-10 blocking hook registration must be mechanically reachable rather than prose-only.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the canonical taxonomy/evaluator are read directly and the implementation must not depend on a cached classification.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — preserve all existing classifications, define measurable before/after behavior, fail closed on invalid rule data, and provide rollback.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — this protected implementation proceeds only through the numbered bridge chain and an independent verdict.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — the proposal carries the project authorization, project, and work-item headers.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — the proposal links the governing constraints and maps them to tests.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — independent verification must use executed evidence derived from the linked specifications.
- `GOV-WORK-TREE-HYGIENE-001` — preserve foreign work and restrict the diff to the three declared clean targets.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — preserve the owner decision, implementation proposal, test evidence, report, and independent verdict as a traceable artifact chain.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — model the P6 decision, rule, evaluator, regression test, and verification evidence as connected durable artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — keep proposal, implementation-report, and verification lifecycle states explicit; this NEW proposal does not claim implementation or closure.

## Owner Decisions / Input

- `DELIB-20260809-ADBR-T0-P6-001` — owner response `Approve P6`; authorizes the bounded `.githooks/**` taxonomy classification needed by AC-10 while preserving the ordinary bridge and implementation-start gates.
- `DELIB-20260809-ADBR-T0-P5-002` — separately approved P5 and produced PAUTH version 5 with `repository_metadata`; cited only to distinguish P5 from this P6 slice.
- `DELIB-20260807011942` — minimal mechanism repair precedes the ADBR line-by-line review; P6 is part of that mechanism-repair prerequisite set.
- `DELIB-20260807011944` — the projected-artifact provenance control is blocking, which is why the pre-commit registration must be executable rather than advisory.
- `DELIB-20260807011951` — ADBR acceptance criteria include AC-10, the blocking negative-test path that needs `.githooks/pre-commit` classification.

## Prior Deliberations

- `DELIB-20260809-ADBR-T0-P6-001` — exact current owner approval and bounded scope.
- `DELIB-20260809-ADBR-T0-P5-002` — sibling prerequisite approval; establishes that P5 and P6 are distinct authority changes.
- `DELIB-20260807011942`, `DELIB-20260807011944`, and `DELIB-20260807011951` — T0 sequencing, blocking enforcement, and the AC-01 through AC-16 completion contract.
- `bridge/gtkb-adbr-t0-mechanism-repair-003.md` — current T0 proposal identifying P6 as a prerequisite.
- `bridge/gtkb-adbr-t0-mechanism-repair-004.md` — independent GO confirming P6 must clear before T0 implementation-start.

The bounded semantic search performed before drafting returned no more specific P6 design precedent than these exact owner and bridge records; unrelated high-similarity project-authorization verdicts were not adopted.

## Proposed Implementation

1. Bump `taxonomy_version` to reflect the governed classification-surface change and add one explicit path-rule entry mapping `.githooks/**` to canonical mutation class `configuration`.
2. Extend `OperationTaxonomy` and `_load_operation_taxonomy()` to parse the optional governed path-rule table, reject malformed/unknown-class/conflicting rules, and expose a deterministic immutable rule collection.
3. Extend `classify_target()` to normalize slash forms, evaluate governed path rules before the existing fallback classifier, and fail closed as `unclassified` when more than one governed class matches.
4. Add focused tests proving `.githooks/pre-commit` and its Windows slash form resolve to exactly `configuration`, an envelope allowing `configuration` accepts the path, and existing representative classifications remain unchanged.

No other hard-coded target family is migrated in this slice. That keeps P6 narrow while establishing the governed mechanism its requested TOML rule requires.

## Implementation-Start Sequencing

Changing the taxonomy bytes intentionally invalidates any packet bound to the prior taxonomy SHA. To avoid a self-invalidating partial implementation:

1. Acquire/renew this thread's exact GO implementation claim after an independent GO.
2. Run `implementation_authorization.py begin` under the current taxonomy and confirm the packet covers all three targets.
3. Apply the evaluator and test changes first; apply the TOML taxonomy change last.
4. After the TOML write and before any further protected or repository-state mutation, run `implementation_authorization.py begin` again so the current packet binds the new taxonomy version/SHA.
5. Run the focused verification commands and file the post-implementation report through the same thread.

If the second packet cannot be minted, stop with the three-file diff intact and report the exact denial; do not proceed to staging, commit, or unrelated work.

## Specification-Derived Verification Plan

| Requirement | Verification | Expected result |
| --- | --- | --- |
| P6 / `DELIB-20260809-ADBR-T0-P6-001` | `classify_target('.githooks/pre-commit')` and the focused pytest assertions | Exactly `configuration`, never `unclassified` |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` single-class and allow semantics | Focused pytest exercises slash normalization, exact class, and `evaluate_envelope()` with `configuration` allowed | Deterministic allow; ambiguous/unknown rules retain fail-closed behavior |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Run the complete existing operation-time enforcement test module | Existing source/test/config/repository/bridge classifications remain green |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Load the taxonomy from the canonical root and assert the new rule/version is consumed | No cached or duplicate classifier input |
| Bridge/project scope | Re-run applicability, clause, and pre-verdict executability checks on this exact thread | No missing required specs, blocking gaps, or executability gaps |
| Python quality | Ruff lint, Ruff format-check, and `py_compile` on the two Python targets | Clean |
| Worktree hygiene | Focused `git status`, `git diff --check`, and diff review over exactly three targets | No foreign path absorbed |

Planned commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py
groundtruth-kb/.venv/Scripts/python.exe -m py_compile groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-adbr-t0-p6-githooks-taxonomy-classification
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-adbr-t0-p6-githooks-taxonomy-classification
python scripts/pre_verdict_executability_check.py --bridge-id gtkb-adbr-t0-p6-githooks-taxonomy-classification --json --session-id 019fe1fd-61a9-7742-a7bf-5e44e1ec9de4
git diff --check -- config/governance/project-authorization-operation-taxonomy.toml groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py
```

## Acceptance Criteria

1. `.githooks/pre-commit` and equivalent backslash input classify as exactly `configuration` through a rule declared in the canonical TOML taxonomy.
2. The taxonomy loader rejects malformed, unknown-class, or conflicting governed path rules rather than silently accepting ambiguous authority.
3. An active authorization allowing `configuration` can authorize `.githooks/pre-commit`; an authorization without that class still denies.
4. All existing focused operation-time enforcement tests pass without changing unrelated classifications.
5. The implementation and report contain only the three declared paths plus the append-only bridge report artifact.
6. The implementation-start packet is refreshed after the taxonomy SHA changes and before any later protected/repository effect.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-20260809-ADBR-T0-P6-001 and GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "canonical_authority": "config/governance/project-authorization-operation-taxonomy.toml plus the canonical project_authorization_operation_time evaluator",
  "primary_route": "numbered bridge proposal, independent GO, exact work-intent claim, implementation-start packet, three-path implementation, and independent verification",
  "before_behavior": "The canonical taxonomy cannot declare path classifications and .githooks/pre-commit fails closed as unclassified despite hook already normalizing to configuration.",
  "after_behavior": "The canonical taxonomy declares one root-relative .githooks/** rule, the evaluator consumes it deterministically as configuration, and invalid or ambiguous rule data fails closed.",
  "self_descriptive_naming": "The path_rule table, mutation_class field, and immutable OperationTaxonomy path_rules collection state their governed purpose directly.",
  "obsolete_guidance_disposition": "No historical guidance is activated or deleted; the earlier config-only P6 description is preserved in the T0 bridge chain and corrected here with live evaluator evidence.",
  "history_preservation": "Owner decisions and numbered bridge artifacts remain append-only; source, taxonomy, and test history remain in Git.",
  "baseline": {
    "taxonomy_version": "1",
    "githooks_pre_commit_class": "unclassified",
    "focused_target_diff": "clean before implementation"
  },
  "expected_result": {
    "taxonomy_version": "2",
    "githooks_pre_commit_class": "configuration",
    "focused_test_module": "all tests pass"
  },
  "rollback": {
    "instructions": "Revert only the three declared P6 files after governed review.",
    "verification": "Rerun the focused operation-time test module and confirm .githooks/pre-commit returns to unclassified."
  },
  "hard_invariants": [
    "every requested target resolves to exactly one governed mutation class",
    "unknown malformed or ambiguous path rules deny",
    "existing target classifications remain unchanged outside .githooks/**",
    "bridge GO claim implementation-start and independent verification remain mandatory",
    "foreign worktree changes remain untouched"
  ],
  "fail_closed_conditions": [
    "unknown mutation class in a path rule",
    "conflicting rule matches",
    "missing current GO or exact claim",
    "implementation packet invalidated by taxonomy SHA change",
    "focused regression or quality gate failure"
  ],
  "essential_context_preservation": "The proposal preserves the P5/P6 distinction, the taxonomy-SHA packet-remint sequence, exact three-path scope, owner decision provenance, and the later T0 .githooks/pre-commit boundary."
}
```

## Risk / Rollback

- **Risk: taxonomy drift invalidates the active packet mid-change.** Mitigation: evaluator/test first, TOML last, then mandatory packet remint under the new SHA before any further protected effect.
- **Risk: a broad glob classifies unintended paths.** Mitigation: the sole rule is root-relative `.githooks/**`; tests include slash normalization and do not classify similarly named nested paths.
- **Risk: path rules overlap.** Mitigation: loader/runtime ambiguity checks fail closed; no first-match-wins authority.
- **Risk: foreign dirty work is absorbed.** Mitigation: all three targets are clean at proposal time and every status/diff/test/report command is explicitly scoped.

Rollback is a three-file git revert after verification. Reverting the taxonomy restores the prior SHA/version and `.githooks/**` returns to fail-closed `unclassified`; no runtime state, MemBase row, dispatcher/TAFE state, external system, credential, deployment, or release mutation is in implementation scope.

## Authority Boundary

This proposal authorizes no implementation until an unrelated Loyal Opposition session records GO and this session obtains the exact claim plus a fresh implementation-start packet. It authorizes no `.githooks/pre-commit` edit, no ADBR T0 implementation, no formal artifact mutation, no MemBase mutation, no dispatcher/TAFE action, no git staging/commit/push, no destructive cleanup, no credential action, and no deployment/release.

## Pre-Filing Preflight

Executed against the completed candidate before filing:

- Applicability: `preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`; `blocking_errors: []`.
- Project authorization operation-time evaluation: `allowed` under PAUTH version 5 for `implementation_packet_create` and `implementation_start`; target classes are `configuration`, `source`, and `test`.
- Clause preflight (mandatory mode): 3 `must_apply`, 2 `may_apply`, 0 evidence gaps, 0 blocking gaps; exit 0.
- Author metadata warnings: none. Unclassified declared target paths: none.

The mechanical preflights are rerun once more against these final bytes immediately before the governed write.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
