REVISED
::init gtkb lo
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: GPT-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined ::init gtkb pb; governed proposal revision

bridge_kind: prime_proposal
Document: gtkb-wi5152-modernization-hard-invariant-registry
Version: 003
Responds to: bridge/gtkb-wi5152-modernization-hard-invariant-registry-002.md
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5152
target_paths: ["config/governance/modernization-hard-invariants.toml", "scripts/check_modernization_invariant_registry.py", "platform_tests/scripts/test_modernization_invariant_registry.py"]
implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# Revised Implementation Proposal - Modernization Hard-Invariant Registry

## First-Line Role Eligibility Check

PASS. Session `019f5f66-9582-7f03-a3f1-3c75e6bd9d0a` is transcript-defined
Prime Builder and holds the exact draft claim for this latest `NO-GO` thread.
`REVISED` is role-correct. This filing grants no implementation authority.

## Revision Disposition

Version 002 rejected the original proposal for two concrete reasons: the
reviewer could not execute the mandatory preflights, and the WI-5153
fail-closed evaluator prerequisite was not yet terminal. Both conditions have
cleared without changing the WI-5152 design or target set:

1. `gtkb-wi5153-fail-closed-artifact-evaluability` is latest `VERIFIED` at
   `bridge/gtkb-wi5153-fail-closed-artifact-evaluability-006.md`.
2. Its independently verified implementation and bridge chain are committed at
   `7ce8fc3d` (`fix(bridge): WI-5153 fail-closed artifact evaluability
   VERIFIED`).
3. The applicability and mandatory ADR/DCL clause preflights execute in the
   current project environment.
4. All three declared WI-5152 targets are absent and clean relative to current
   HEAD. No inherited, foreign, or uncommitted target bytes need adoption.

This revision therefore requests fresh independent Loyal Opposition review of
the unchanged three-new-file implementation plan.

## Requirement Sufficiency

Existing requirements sufficient. The approved Gate 1.25 assertion map, active
Assurance PAUTH, terminal WI-5153 evaluator baseline, cross-cutting
mechanical-enforcement requirements, and artifact-lifecycle requirements
together govern the implementation. No formal-carrier or database amendment is
required.

## Scope

Add one source-linked registry, one read-only deterministic checker, and one
focused test module:

1. `config/governance/modernization-hard-invariants.toml` records exactly 28
   outer assertions for the WI-5158 Gate 1.25 slice.
2. `scripts/check_modernization_invariant_registry.py` resolves the registry
   against current formal-carrier versions, project/work-item state, deferred
   successors, and WI-5153 evaluator results without mutation.
3. `platform_tests/scripts/test_modernization_invariant_registry.py` proves the
   exact map, fail-closed behavior, deferred ownership, conditional A4
   semantics, and deterministic output.

The implementation must not edit `groundtruth.db`, formal carriers, existing
applicability/clause registries, dispatcher or TAFE state, harness state,
runtime leases, routing policy, credentials, or any fourth file.

## Exact Assertion Map

| Carrier | `MUST_APPLY` to WI-5158 | `DEFERRED_TO` | Conditional |
| --- | --- | --- | --- |
| `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001` v1 | `GIT-ADR-A1`, `A2`, `A3`, `A4`, `A6`, `A7` | `GIT-ADR-A5` -> `WI-5159` | none |
| `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` v1 | `GIT-REQ-A1`, `A2`, `A3`, `A4`, `A6`, `A8` | `GIT-REQ-A5` -> `WI-5159`; `GIT-REQ-A7` -> `WI-5160` | none |
| `DCL-GIT-BRANCH-BINDING-PROMOTION-001` v2 | `BRANCH-BIND-A1`, `A2`, `A3`, `A4`, `A5`, `A7`, `A8`, `A9` | `BRANCH-BIND-A6` -> `WI-5159` | none |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` v1 | `A1` proposal; `A2` activation; `A3` verification/closure | none | `A4` is `NOT_APPLICABLE` only after deterministic proof that no active worker-loading route changes; otherwise `MUST_APPLY` or `UNASSESSED`. |

Totals remain exactly 28 outer assertions: 23 `MUST_APPLY`, 4 `DEFERRED_TO`,
and 1 conditional entry.

## Behavioral Contract

- Every registry entry carries carrier ID/version, outer assertion ID,
  applicability, owning WI, gate, evaluator route, current-evidence identity,
  severity, and provenance.
- Allowed applicability is limited to `MUST_APPLY`, `DEFERRED_TO`, and the
  governed conditional `NOT_APPLICABLE`; unknown values fail closed.
- Every carrier and exact version resolves from MemBase at runtime without
  mutation.
- Every deferred successor, project membership, gate, and approved charter
  provenance resolves or the check fails.
- The checker consumes the committed WI-5153 evaluator. Missing evaluator,
  changed carrier version, stale evidence, unsupported assertion,
  contradictory applicability, or unassessed result blocks.
- A full carrier remains `PARTIAL` while any deferred assertion is incomplete.
- Non-impairment `A4` becomes `NOT_APPLICABLE` only from deterministic proof
  that no active worker-loading route changes.
- Stable normalized JSON contains no volatile timestamps and exits nonzero for
  every aggregate state other than complete slice `PASS`.
- Existing `spec-applicability.toml` and `adr-dcl-clauses.toml` remain
  proposal/review discovery aids, not assertion authority.
- WI-5152 remains open after this first 28-entry slice for broader Assurance
  coverage.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-202666080; DELIB-202666274; WI-5152; terminal WI-5153 prerequisite at bridge/gtkb-wi5153-fail-closed-artifact-evaluability-006.md and commit 7ce8fc3d",
  "canonical_authority": "GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001; DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "python scripts/check_modernization_invariant_registry.py --work-item WI-5158 --gate verification --json",
  "before_behavior": "Gate 1.25 has an approved prose map but no executable outer-assertion-to-work-item registry or deterministic result projection.",
  "after_behavior": "Each of 28 assertions has explicit applicability, evaluator, current evidence, and fail-closed successor semantics in a source-linked projection while formal carriers remain authoritative.",
  "self_descriptive_naming": "Carrier IDs, outer assertion IDs, applicability states, successor work items, gates, evaluator routes, and evidence identities are literal registry fields.",
  "obsolete_guidance_disposition": "Existing heuristic applicability and clause registries remain discovery aids and are explicitly not promoted to formal assertion authority.",
  "history_preservation": "Formal carrier versions, assertion history, deliberations, deferred successor records, terminal WI-5153 evidence, and bridge history remain unchanged and queryable.",
  "baseline": {
    "registry_exists": false,
    "checker_exists": false,
    "focused_test_exists": false,
    "approved_entry_count": 28,
    "must_apply": 23,
    "deferred_to": 4,
    "conditional": 1,
    "wi5153_latest": "VERIFIED",
    "wi5153_commit": "7ce8fc3d"
  },
  "expected_result": {
    "registry_exists": true,
    "checker_exists": true,
    "focused_test_exists": true,
    "entry_count": 28,
    "must_apply": 23,
    "deferred_to": 4,
    "conditional": 1,
    "deterministic_runs": true
  },
  "rollback": {
    "instructions": "Remove only the three WI-5152 files through a separately governed rollback transaction.",
    "verification": "Confirm formal carriers, WI-5153, project and backlog state, dispatcher and TAFE state, harness state, and concurrent work remain unchanged."
  },
  "hard_invariants": [
    "exactly 28 entries and no duplicate carrier/assertion key",
    "no missing or stale carrier version",
    "no missing evaluator or evidence identity",
    "no incomplete deferred successor hidden as carrier PASS",
    "no conditional NOT_APPLICABLE without deterministic worker-route proof",
    "no database, formal-carrier, dispatcher, TAFE, harness, or unrelated mutation"
  ],
  "fail_closed_conditions": [
    "WI-5153 unavailable or not terminal VERIFIED",
    "carrier or assertion missing",
    "carrier version changes",
    "unknown applicability",
    "missing or stale successor membership",
    "missing current evidence",
    "nondeterministic normalized report"
  ],
  "essential_context_preservation": "Preserve the exact approved 28-entry map, all four carrier sources, deferred ownership, conditional route rule, committed WI-5153 evaluator baseline, and broader WI-5152 backlog scope."
}
```

## Specification Links

- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001`
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001`
- `DCL-GIT-BRANCH-BINDING-PROMOTION-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-ASSURANCE-INVARIANT-PLAN`
  establishes the assurance registry and fail-closed evaluation sequence.
- `DELIB-202666080` approves the exact Gate 1.25 applicability map and child
  outcomes.
- `DELIB-202666274` authorizes the modernization program while retaining exact
  bridge, claim, implementation-start, verification, and Git gates.
- `bridge/gtkb-wi5152-modernization-hard-invariant-registry-001.md` is the
  original complete three-file proposal.
- `bridge/gtkb-wi5152-modernization-hard-invariant-registry-002.md` is the
  resolved prerequisite/preflight NO-GO.
- `bridge/gtkb-wi5153-fail-closed-artifact-evaluability-006.md` is the
  independent terminal prerequisite verdict.

## Owner Decisions / Input

No new owner decision is required. The active project-scoped Assurance PAUTH
has no per-work-item inclusion restriction and includes the governing
mechanical-enforcement, evaluability, project-ordering, bridge, and
artifact-lifecycle specifications. This proposal does not authorize database
mutation, dispatcher/TAFE/harness mutation, credentials, Git staging/commit,
push, release, deployment, destructive cleanup, or external-system action.

## Specification-Derived Verification

| Requirement | Verification | Expected result |
| --- | --- | --- |
| Exact map and schema | `python -m pytest platform_tests/scripts/test_modernization_invariant_registry.py -q --tb=short` | Exactly 28 entries: 23 `MUST_APPLY`, 4 `DEFERRED_TO`, 1 conditional; exact required fields and versions. |
| Fail-closed evaluability | Focused fixtures for missing evaluator, unsupported assertion, stale version/evidence, contradiction, and unassessed result | Every fixture exits nonzero with stable reason codes. |
| Deferred ownership | Fixtures for missing WI-5159/WI-5160, inactive membership, wrong gate/charter, and incomplete deferred evidence | Slice and full carrier cannot pass. |
| Conditional A4 | Fixtures with and without active worker-loading route changes | `NOT_APPLICABLE` only with deterministic no-route-change proof. |
| Determinism | Run the checker twice with unchanged inputs and compare exact bytes and exit codes | Byte-identical normalized reports and identical exit codes. |
| Discovery non-authority | Run focused bridge applicability and clause-preflight tests | Existing discovery behavior remains green and is not promoted to assertion authority. |
| Scope isolation | Compare Git status/diff for the exact three targets and run `git diff --check` | No mutation outside the three approved files. |
| Dependency ordering | Read latest WI-5153 bridge state and focused commit evidence | Latest `VERIFIED`; commit `7ce8fc3d` is an ancestor of implementation HEAD. |

Commands required before the implementation report:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_modernization_invariant_registry.py -q --tb=short
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/scripts/test_adr_dcl_clause_preflight.py -q --tb=short
groundtruth-kb\.venv\Scripts\ruff.exe check scripts/check_modernization_invariant_registry.py platform_tests/scripts/test_modernization_invariant_registry.py
groundtruth-kb\.venv\Scripts\ruff.exe format --check scripts/check_modernization_invariant_registry.py platform_tests/scripts/test_modernization_invariant_registry.py
groundtruth-kb\.venv\Scripts\python.exe scripts/check_modernization_invariant_registry.py --work-item WI-5158 --gate verification --json
groundtruth-kb\.venv\Scripts\python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5152-modernization-hard-invariant-registry
groundtruth-kb\.venv\Scripts\python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5152-modernization-hard-invariant-registry
git diff --check -- config/governance/modernization-hard-invariants.toml scripts/check_modernization_invariant_registry.py platform_tests/scripts/test_modernization_invariant_registry.py
```

## Acceptance Criteria

1. The registry contains exactly the approved 28 entries and required metadata.
2. Every entry resolves to a current exact carrier assertion and evaluator.
3. Missing, stale, unsupported, contradictory, or unassessed evidence blocks.
4. Deferred assertions keep full carriers partial until successor evidence
   completes.
5. Conditional A4 cannot become not-applicable without deterministic proof.
6. Unchanged repeated runs are deterministic.
7. Existing applicability/clause discovery behavior remains green.
8. Only the three new files are implementation scope; WI-5152 stays open for
   broader coverage.

## Pre-Filing Preflight Evidence

The mandatory applicability and ADR/DCL clause preflights are executed against
this exact completed candidate immediately before filing. Filing is permitted
only when applicability reports `preflight_passed: true`, no missing required
or advisory specifications, no blocking errors, and the clause preflight exits
zero with no blocking gaps.

## Implementation Boundary

No protected mutation may begin from this `REVISED` filing. Prime Builder must
first receive a fresh independent `GO`, acquire the exact implementation claim,
and obtain a successful implementation-start packet against the live target
set. Independent post-implementation `VERIFIED` and focused finalization remain
mandatory.

Rollback, if later authorized, removes only the three WI-5152 files through a
separately governed transaction and preserves formal carriers, WI-5153,
project/backlog state, and all concurrent work.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
