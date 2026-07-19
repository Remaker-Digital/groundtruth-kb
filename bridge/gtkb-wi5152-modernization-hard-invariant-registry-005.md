REVISED
::init gtkb lo
::open build

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-18T23-50-54Z-prime-builder-A-87575d
author_model: GPT-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex headless auto-dispatch; resolved role prime-builder; approval_policy=never; sandbox=workspace-write; selected NO-GO revision dispatch

bridge_kind: prime_proposal
Document: gtkb-wi5152-modernization-hard-invariant-registry
Version: 005
Responds to: bridge/gtkb-wi5152-modernization-hard-invariant-registry-004.md
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

PASS. The dispatched worker resolved durable harness identity `codex` -> `A`
from `harness-state/harness-identities.json`, and
`groundtruth-kb/.venv/Scripts/gt.exe harness roles` reports harness `A` with
role `prime-builder`. Prime Builder may author `REVISED` bridge files. This
session acquired the required draft work-intent claim for
`gtkb-wi5152-modernization-hard-invariant-registry` at
`2026-07-18T23:50:54Z`; latest live thread status was verified as `NO-GO` at
`bridge/gtkb-wi5152-modernization-hard-invariant-registry-004.md`.

This filing grants no implementation authority. Protected implementation still
requires a fresh independent `GO`, a matching implementation claim, and a
successful implementation-start packet.

## Revision Disposition

The `-004` NO-GO accepted the proposal design, the WI-5153 prerequisite, the
three-file target scope, the active project authorization, and both mandatory
preflights. It requested a narrow evidence-accuracy correction:

1. Replace the incorrect prior Gate 1.25 map approval citation with the
   verifiable on-point record.
2. Update the Exact Assertion Map to the live
   `DCL-GIT-BRANCH-BINDING-PROMOTION-001` carrier version and instruct the
   implementation to re-resolve carrier versions from MemBase before TOML
   authoring.

Both corrections are made here without changing the implementation scope,
target paths, WI-5153 dependency treatment, acceptance criteria, or verification
commands.

## Finding Responses

### P1 citation correction

The revised proposal no longer uses the prior numeric Deliberation Archive
record as authority for the 28-assertion map. Fresh MemBase reads show that
record currently resolves to an unrelated WI-5119 memory-label verdict, so it is
not cited in this filing as provenance or owner-decision evidence.

The exact map is instead grounded in:

- `DELIB-202665958`, the independent Loyal Opposition GO on
  `bridge/gtkb-modernization-gate-1-25-execution-design-002.md`, whose Finding
  F3 independently recounts the same 28-entry breakdown: 23 `MUST_APPLY`, 4
  `DEFERRED_TO`, and 1 conditional entry.
- `bridge/gtkb-modernization-gate-1-25-execution-design-001.md`, which contains
  the reviewed Gate 1.25 execution design and exact map.
- `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-ASSURANCE-INVARIANT-PLAN`, which
  establishes the assurance and hard-invariant plan.
- `DELIB-202666274`, which authorizes required GT-KB modernization blocker work
  while preserving bridge, implementation-start, Git, release, and deployment
  gates.

The future registry's `provenance` fields must use the corrected citation set
above and must not copy the rejected prior numeric citation from `-001` or
`-003`.

### P2 carrier-version freshness correction

Fresh MemBase read:

- `groundtruth-kb/.venv/Scripts/gt.exe spec show DCL-GIT-BRANCH-BINDING-PROMOTION-001 --json`
  reports `version: 3`, `status: specified`, and
  `changed_at: 2026-07-10T20:02:26-07:00`.

The Exact Assertion Map below therefore cites
`DCL-GIT-BRANCH-BINDING-PROMOTION-001 v3`, not `v2`. The proposal table remains
review context, not a version source for implementation. Immediately before
authoring `config/governance/modernization-hard-invariants.toml`, Prime Builder
must re-query MemBase for all four carrier versions and write the registry from
those live version values. If any carrier version changes after this filing,
the checker and registry must treat that as a currentness event and fail closed
until the map is re-reviewed or otherwise dispositioned through the bridge.

## Requirement Sufficiency

Existing requirements sufficient. The active Assurance project authorization,
the corrected Gate 1.25 map provenance, the terminal WI-5153 evaluator
baseline, and the linked governing carriers are sufficient for independent
review of this three-file proposal. No formal carrier, database, owner-decision,
dispatcher, TAFE, harness, Git, release, deployment, or credential mutation is
requested by this filing.

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
runtime leases, routing policy, credentials, Git state, or any fourth file.

## Exact Assertion Map

Implementation must re-resolve the four live carrier versions from MemBase at
TOML-authoring time. The reviewed map at this filing time is:

| Carrier | `MUST_APPLY` to WI-5158 | `DEFERRED_TO` | Conditional |
| --- | --- | --- | --- |
| `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001` v1 | `GIT-ADR-A1`, `A2`, `A3`, `A4`, `A6`, `A7` | `GIT-ADR-A5` -> `WI-5159` | none |
| `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` v1 | `GIT-REQ-A1`, `A2`, `A3`, `A4`, `A6`, `A8` | `GIT-REQ-A5` -> `WI-5159`; `GIT-REQ-A7` -> `WI-5160` | none |
| `DCL-GIT-BRANCH-BINDING-PROMOTION-001` v3 | `BRANCH-BIND-A1`, `A2`, `A3`, `A4`, `A5`, `A7`, `A8`, `A9` | `BRANCH-BIND-A6` -> `WI-5159` | none |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` v1 | `A1` proposal; `A2` activation; `A3` verification/closure | none | `A4` is `NOT_APPLICABLE` only after deterministic proof that no active worker-loading route changes; otherwise `MUST_APPLY` or `UNASSESSED`. |

Totals remain exactly 28 outer assertions: 23 `MUST_APPLY`, 4 `DEFERRED_TO`,
and 1 conditional entry. The DCL v3 live assertion payload preserves the same
outer assertion IDs and applicability split reviewed in the Gate 1.25 design.

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
  "provenance": "DELIB-202665958; bridge/gtkb-modernization-gate-1-25-execution-design-001.md; bridge/gtkb-modernization-gate-1-25-execution-design-002.md; DELIB-20260710-GTKB-MODERNIZATION-GATE-1-ASSURANCE-INVARIANT-PLAN; DELIB-202666274; WI-5152; terminal WI-5153 prerequisite at bridge/gtkb-wi5153-fail-closed-artifact-evaluability-006.md and commit 7ce8fc3d",
  "canonical_authority": "GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001; DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "groundtruth-kb/.venv/Scripts/python.exe scripts/check_modernization_invariant_registry.py --work-item WI-5158 --gate verification --json",
  "before_behavior": "Gate 1.25 has a reviewed 28-assertion map but no executable outer-assertion-to-work-item registry or deterministic result projection.",
  "after_behavior": "Each of 28 assertions has explicit applicability, evaluator, current evidence, and fail-closed successor semantics in a source-linked projection while formal carriers remain authoritative.",
  "self_descriptive_naming": "Carrier IDs, outer assertion IDs, applicability states, successor work items, gates, evaluator routes, and evidence identities are literal registry fields.",
  "obsolete_guidance_disposition": "Existing heuristic applicability and clause registries remain discovery aids and are explicitly not promoted to formal assertion authority. Rejected stale deliberation citations are not copied into registry provenance.",
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
    "wi5153_commit": "7ce8fc3d",
    "dcl_branch_binding_live_version_at_filing": 3
  },
  "expected_result": {
    "registry_exists": true,
    "checker_exists": true,
    "focused_test_exists": true,
    "entry_count": 28,
    "must_apply": 23,
    "deferred_to": 4,
    "conditional": 1,
    "carrier_versions_resolved_from_membase_at_authoring": true,
    "deterministic_runs": true
  },
  "rollback": {
    "instructions": "Remove only the three WI-5152 files through a separately governed rollback transaction.",
    "verification": "Confirm formal carriers, WI-5153, project and backlog state, dispatcher and TAFE state, harness state, and concurrent work remain unchanged."
  },
  "hard_invariants": [
    "exactly 28 entries and no duplicate carrier/assertion key",
    "no missing or stale carrier version",
    "no stale deliberation citation copied into registry provenance",
    "no missing evaluator or evidence identity",
    "no incomplete deferred successor hidden as carrier PASS",
    "no conditional NOT_APPLICABLE without deterministic worker-route proof",
    "no database, formal-carrier, dispatcher, TAFE, harness, Git, or unrelated mutation"
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
  "essential_context_preservation": "Preserve the exact reviewed 28-entry map, all four carrier sources, deferred ownership, conditional route rule, committed WI-5153 evaluator baseline, and broader WI-5152 backlog scope."
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
  establishes the assurance registry and fail-closed hard-invariant plan.
- `DELIB-202665958` independently GO-reviewed the Gate 1.25 execution design
  and re-derived the exact 28-assertion map in Finding F3.
- `bridge/gtkb-modernization-gate-1-25-execution-design-001.md` is the reviewed
  design thread containing the exact WI-5158 assertion map.
- `bridge/gtkb-modernization-gate-1-25-execution-design-002.md` is the
  independent GO for that design thread.
- `DELIB-202666274` authorizes the modernization program while retaining exact
  bridge, claim, implementation-start, verification, Git, release, and
  deployment gates.
- `bridge/gtkb-wi5152-modernization-hard-invariant-registry-001.md` is the
  original complete three-file proposal.
- `bridge/gtkb-wi5152-modernization-hard-invariant-registry-002.md` is the
  resolved prerequisite/preflight NO-GO.
- `bridge/gtkb-wi5152-modernization-hard-invariant-registry-004.md` is the
  current narrow evidence-accuracy NO-GO this filing addresses.
- `bridge/gtkb-wi5153-fail-closed-artifact-evaluability-006.md` is the
  independent terminal prerequisite verdict.

## Owner Decisions / Input

No new owner decision is required. The active project-scoped Assurance PAUTH
has no per-work-item inclusion restriction and includes the governing
mechanical-enforcement, evaluability, project-ordering, bridge, and
artifact-lifecycle specifications. This proposal does not authorize database
mutation, dispatcher/TAFE/harness mutation, credentials, Git staging/commit,
push, release, deployment, destructive cleanup, external-system action, or
formal-carrier mutation.

The apparent Deliberation Archive numeric-ID reassignment discovered by the
`-004` review remains a platform data-integrity concern outside this proposal's
implementation scope. This filing corrects WI-5152's provenance so the registry
does not launch with stale citation evidence; it does not mutate the
Deliberation Archive or create new backlog records.

## Specification-Derived Verification

| Requirement | Verification | Expected result |
| --- | --- | --- |
| Exact map and schema | `groundtruth-kb\\.venv\\Scripts\\python.exe -m pytest platform_tests/scripts/test_modernization_invariant_registry.py -q --tb=short` | Exactly 28 entries: 23 `MUST_APPLY`, 4 `DEFERRED_TO`, 1 conditional; exact required fields and live carrier versions. |
| Carrier-version freshness | The checker and focused tests re-query MemBase carrier versions before validating registry content | No registry entry can pass when carrier version evidence is stale or copied from an obsolete proposal table. |
| Provenance correctness | Focused test asserts registry provenance cites `DELIB-202665958` or the Gate 1.25 design bridge thread and rejects the stale prior citation | Registry provenance is on-point and verifiable. |
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

1. The registry contains exactly the reviewed 28 entries and required metadata.
2. Every entry resolves to a current exact carrier assertion and evaluator.
3. Carrier versions are resolved from MemBase at registry-authoring and
   checking time, not copied blindly from this proposal table.
4. Registry provenance uses the corrected Gate 1.25 map citation set and does
   not copy stale deliberation evidence.
5. Missing, stale, unsupported, contradictory, or unassessed evidence blocks.
6. Deferred assertions keep full carriers partial until successor evidence
   completes.
7. Conditional A4 cannot become not-applicable without deterministic proof.
8. Unchanged repeated runs are deterministic.
9. Existing applicability/clause discovery behavior remains green.
10. Only the three new files are implementation scope; WI-5152 stays open for
    broader coverage.

## Pre-Filing Preflight Evidence

This completed candidate is filed only through
`.codex/skills/bridge/helpers/revise_bridge.py file`, which runs:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5152-modernization-hard-invariant-registry --content-file <candidate> --json
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5152-modernization-hard-invariant-registry --content-file <candidate>
```

Filing is valid only if both candidate preflights exit zero and the
applicability preflight reports `preflight_passed: true`,
`missing_required_specs: []`, `missing_advisory_specs: []`, and no blocking
errors. The helper then publishes the live `REVISED` file through the governed
bridge writer path.

## Implementation Boundary

No protected mutation may begin from this `REVISED` filing. Prime Builder must
first receive a fresh independent `GO`, acquire the exact implementation claim,
and obtain a successful implementation-start packet against the live target
set. Independent post-implementation `VERIFIED` and focused finalization remain
mandatory.

Rollback, if later authorized, removes only the three WI-5152 files through a
separately governed transaction and preserves formal carriers, WI-5153,
project/backlog state, dispatcher/TAFE state, harness state, Git state, and all
concurrent work.

## Recommended Commit Type

`feat` - this proposal would add a new deterministic governance registry and
checker surface if it later receives `GO` and is implemented.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
