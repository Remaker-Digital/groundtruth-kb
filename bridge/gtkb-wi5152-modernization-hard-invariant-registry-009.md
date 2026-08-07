REVISED
::init gtkb pb
::open build

author_identity: prime-builder/goose
author_harness_id: G
author_session_context_id: G-2026-08-05T17-03-48Z
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: Goose Desktop interactive Prime Builder; transcript-defined ::init gtkb pb; ::open build
author_metadata_source: session envelope (worker_role_provenance)

bridge_kind: prime_proposal
Document: gtkb-wi5152-modernization-hard-invariant-registry
Version: 009
Responds to: bridge/gtkb-wi5152-modernization-hard-invariant-registry-008.md
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5152
target_paths: ["config/governance/modernization-hard-invariants.toml", "scripts/check_modernization_invariant_registry.py", "platform_tests/scripts/test_modernization_invariant_registry.py"]
implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# Revised Implementation Proposal — Modernization Hard-Invariant Registry

## First-Line Role Eligibility Check

PASS. This Goose Desktop session (harness G) resolved its session role from the
transcript-defined `::init gtkb pb` declaration as Prime Builder. Prime Builder
may author `REVISED` bridge files; it is strictly prohibited from authoring
Loyal Opposition status tokens (`GO`, `NO-GO`, `VERIFIED`). This filing writes
only the `REVISED` Prime Builder status token against the latest `NO-GO`
(`-008`).

This filing grants no implementation authority. Protected implementation still
requires a fresh independent `GO`, a matching `go_implementation` work-intent
claim, and a successful implementation-start packet against the live target
set.

## Revision Disposition

The `-008` NO-GO is **non-terminal** and requires a `REVISED` current-state
entry that either reaffirms the still-unstarted three-file slice for a fresh
review or supplies an implementation report if work occurred elsewhere. It
must not use `NO-ACTION` to close, withdraw, or silently change the approved
scope.

**This filing reaffirms the still-unstarted three-file slice.** Independent
on-disk verification (see Evidence below) confirms none of the three v006-GO
target paths currently exists, so there is no implementation report to supply.
No work occurred elsewhere; the slice remains unstarted and is re-presented in
full for a fresh review.

The prior `-007` `NO-ACTION` carrier acknowledgment was improper: it neither
reported implementation nor revised the v006-approved scope, and instead
removed the thread from the queue without a terminal verdict. The `-008` NO-GO
correctly rejected that disposition. This `REVISED` entry supersedes the `-007`
disposition and returns the thread to the actionable Prime Builder review
queue in a valid, reviewable form.

## Evidence — Target Paths Still Unstarted

On-disk existence check at `E:\GT-KB` (2026-08-05):

| Target path (v006 GO) | On-disk result |
| --- | --- |
| `config/governance/modernization-hard-invariants.toml` | **Does not exist** |
| `scripts/check_modernization_invariant_registry.py` | **Does not exist** |
| `platform_tests/scripts/test_modernization_invariant_registry.py` | **Does not exist** |

Because none of the three approved files exists, there is no implementation
report to review, confirming the `-008` NO-GO's finding and supporting the
reaffirm-for-fresh-review path.

## Response to v008 Findings

1. **v006 GO approved a concrete three-file slice.** Affirmed. This `REVISED`
   filing carries the identical three-file scope:
   `config/governance/modernization-hard-invariants.toml`,
   `scripts/check_modernization_invariant_registry.py`, and
   `platform_tests/scripts/test_modernization_invariant_registry.py`. No scope
   change is proposed.
2. **v007 neither reported implementation nor revised the approved scope.**
   Accepted. This filing corrects the disposition: it is a `REVISED` reaffirm
   of the v006 scope, not a `NO-ACTION`, withdrawal, or silent scope change.
3. **No implementation report exists.** Confirmed by the on-disk check above.
   The three files remain unstarted.

## Requirement Sufficiency

Existing requirements remain sufficient. The active Assurance project
authorization (`PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE`,
verified `status: active` at v006 GO), the corrected Gate 1.25 map provenance,
the terminal WI-5153 evaluator baseline, and the linked governing carriers are
sufficient for independent review of this three-file proposal. No formal
carrier, database, owner-decision, dispatcher, TAFE, harness, Git, release,
deployment, or credential mutation is requested by this filing.

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

## WI-5153 Dependency Note

Implementation of this slice is gated on the terminal WI-5153 fail-closed
artifact-evaluability baseline. As of the v006 GO, `gt bridge show
gtkb-wi5153-fail-closed-artifact-evaluability` reports the latest status
`VERIFIED` at `bridge/gtkb-wi5153-fail-closed-artifact-evaluability-006.md`,
and commit `7ce8fc3d` (the WI-5153 VERIFIED commit) is an ancestor of the
implementation HEAD. This dependency note carries forward unchanged; the
checker consumes the committed WI-5153 evaluator and fails closed if it is
missing or not terminal.

## Prior Deliberations

- `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-ASSURANCE-INVARIANT-PLAN`
  establishes the assurance registry and fail-closed hard-invariant plan.
- `DELIB-202665958` independently GO-reviewed the Gate 1.25 execution design
  and re-derived the exact 28-assertion map in Finding F3.
- `bridge/gtkb-modernization-gate-1-25-execution-design-002.md` is the
  independent GO for that design thread.
- `DELIB-202666274` authorizes the modernization program while retaining exact
  bridge, claim, implementation-start, verification, Git, release, and
  deployment gates.
- `bridge/gtkb-wi5152-modernization-hard-invariant-registry-005.md` is the
  accepted REVISED proposal (v006 GO basis).
- `bridge/gtkb-wi5152-modernization-hard-invariant-registry-006.md` is the
  GO that approved the three-file slice and prerequisite/preflight evidence.
- `bridge/gtkb-wi5152-modernization-hard-invariant-registry-008.md` is the
  non-terminal NO-GO this filing addresses.
- `bridge/gtkb-wi5153-fail-closed-artifact-evaluability-006.md` is the
  independent terminal prerequisite verdict.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

No new owner decision is required. The active project-scoped Assurance PAUTH
has no per-work-item inclusion restriction and includes the governing
mechanical-enforcement, evaluability, project-ordering, bridge, and
artifact-lifecycle specifications. This proposal does not authorize database
mutation, dispatcher/TAFE/harness mutation, credentials, Git staging/commit,
push, release, deployment, destructive cleanup, external-system action, or
formal-carrier mutation.

## Specification-Derived Verification

| Requirement | Verification | Expected result |
| --- | --- | --- |
| Exact map and schema | `python -m pytest platform_tests/scripts/test_modernization_invariant_registry.py -q --tb=short` | Exactly 28 entries: 23 `MUST_APPLY`, 4 `DEFERRED_TO`, 1 conditional; exact required fields and live carrier versions. |
| Carrier-version freshness | The checker and focused tests re-query MemBase carrier versions before validating registry content | No registry entry can pass when carrier version evidence is stale or copied from an obsolete proposal table. |
| Fail-closed evaluability | Focused fixtures for missing evaluator, unsupported assertion, stale version/evidence, contradiction, and unassessed result | Every fixture exits nonzero with stable reason codes. |
| Deferred ownership | Fixtures for missing WI-5159/WI-5160, inactive membership, wrong gate/charter, and incomplete deferred evidence | Slice and full carrier cannot pass. |
| Conditional A4 | Fixtures with and without active worker-loading route changes | `NOT_APPLICABLE` only with deterministic no-route-change proof. |
| Determinism | Run the checker twice with unchanged inputs and compare exact bytes and exit codes | Byte-identical normalized reports and identical exit codes. |
| Scope isolation | Compare Git status/diff for the exact three targets and run `git diff --check` | No mutation outside the three approved files. |
| Dependency ordering | Read latest WI-5153 bridge state and focused commit evidence | Latest `VERIFIED`; commit `7ce8fc3d` is an ancestor of implementation HEAD. |

## Acceptance Criteria

1. The registry contains exactly the reviewed 28 entries and required metadata.
2. Every entry resolves to a current exact carrier assertion and evaluator.
3. Carrier versions are resolved from MemBase at registry-authoring and
   checking time, not copied blindly from this proposal table.
4. Missing, stale, unsupported, contradictory, or unassessed evidence blocks.
5. Deferred assertions keep full carriers partial until successor evidence
   completes.
6. Conditional A4 cannot become not-applicable without deterministic proof.
7. Unchanged repeated runs are deterministic.
8. Existing applicability/clause discovery behavior remains green.
9. Only the three new files are implementation scope; WI-5152 stays open for
   broader coverage.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5152 revision 009; reaffirms the v006-GO three-file hard-invariant registry slice for fresh review",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001, GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001, DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001",
  "primary_route": "new read-only deterministic checker plus a source-linked registry consumed by the Gate 1.25 verification path",
  "before_behavior": "The WI-5158 Gate 1.25 assertion map has no deterministic 28-entry registry or fail-closed checker; applicability/clause discovery aids are not assertion authority.",
  "after_behavior": "A committed 28-entry registry, a read-only deterministic checker, and a focused test module enforce the exact map and fail closed on stale, missing, unsupported, contradictory, or unassessed evidence.",
  "self_descriptive_naming": "Registry keys, checker exit reasons, and fixture names expose the assertion map and fail-closed boundary.",
  "obsolete_guidance_disposition": "No public guidance changes; existing applicability/clause discovery aids remain non-authoritative.",
  "history_preservation": "Append-only bridge filing; no formal carrier, groundtruth.db, dispatcher, harness, Git, or credential state is mutated.",
  "baseline": {
    "target_paths_absent": [
      "config/governance/modernization-hard-invariants.toml",
      "scripts/check_modernization_invariant_registry.py",
      "platform_tests/scripts/test_modernization_invariant_registry.py"
    ],
    "predecessor": "WI-5153 VERIFIED (terminal evaluator baseline); v006 GO approved the three-file slice"
  },
  "expected_result": {
    "registry_entries": 28,
    "must_apply": 23,
    "deferred_to": 4,
    "conditional": 1,
    "fail_closed_fixtures": "missing evaluator, unsupported assertion, stale version/evidence, contradiction, unassessed result"
  },
  "essential_context_preservation": "Formal carriers, existing discovery aids, WI-5153 evaluator, project/backlog state, dispatcher/TAFE state, harness state, Git state, and all concurrent work remain unchanged.",
  "hard_invariants": [
    "Every registry entry resolves to a current exact carrier assertion and evaluator.",
    "Allowed applicability is limited to MUST_APPLY, DEFERRED_TO, and the governed conditional NOT_APPLICABLE.",
    "Missing, stale, unsupported, contradictory, or unassessed evidence blocks.",
    "Deferred assertions keep full carriers PARTIAL until successor evidence completes.",
    "Conditional A4 becomes NOT_APPLICABLE only from deterministic no-route-change proof.",
    "Only the three approved files are implementation scope."
  ],
  "fail_closed_conditions": [
    "carrier version drift from MemBase",
    "missing or non-terminal WI-5153 evaluator",
    "unsupported assertion or contradictory applicability",
    "stale or unassessed evidence",
    "registry entry count != 28",
    "mutation outside the three approved files"
  ],
  "rollback": "Remove only the three WI-5152 files through a separately governed transaction; preserve formal carriers, WI-5153, and all concurrent state."
}
```

## Implementation Boundary

No protected mutation may begin from this `REVISED` filing. Prime Builder must
first receive a fresh independent `GO`, acquire the exact implementation claim,
and obtain a successful implementation-start packet against the live target
set. Independent post-implementation `VERIFIED` and focused finalization remain
mandatory.

## Recommended Commit Type

`feat` — this proposal would add a new deterministic governance registry and
checker surface if it later receives `GO` and is implemented.

---
(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
