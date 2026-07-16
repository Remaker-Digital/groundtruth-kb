NEW

# Implementation Proposal - Add the modernization hard-invariant registry

bridge_kind: prime_proposal
Document: gtkb-wi5152-modernization-hard-invariant-registry
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-16 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive; role=prime-builder; approval_policy=never; sandbox=danger-full-access

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5152

target_paths: ["config/governance/modernization-hard-invariants.toml", "scripts/check_modernization_invariant_registry.py", "platform_tests/scripts/test_modernization_invariant_registry.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Add a canonical, source-linked projection for the 28 outer assertions governing
the WI-5158 Gate 1.25 slice. The registry records applicability and evaluator
ownership explicitly; a read-only checker joins it to current carrier versions,
project/work-item state, and WI-5153 evaluator results, then fails closed on
missing, stale, contradictory, or incomplete evidence.

This is a clean three-new-file implementation. It does not edit the existing
heuristic applicability/clause registries, `groundtruth.db`, formal carriers,
dispatcher/TAFE/harness state, or any dirty shared source. WI-5153 must provide
the fail-closed evaluator before this checker can qualify as VERIFIED.

## Specification Links

- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - Every named Gate 1.25 obligation requires an executable, source-linked registry entry.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - Registry evaluation fails closed on unsupported, incomplete, stale, contradictory, or unassessed evidence.
- `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001` - Supplies seven registered Git architecture assertions for WI-5158.
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` - Supplies eight registered operational Git requirements for WI-5158.
- `DCL-GIT-BRANCH-BINDING-PROMOTION-001` - Supplies nine registered branch-binding and promotion constraints.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - Supplies four proposal/activation/verification/worker-route assertions and governs non-impairment.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - Release readiness cannot pass without complete current hard-invariant evidence.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Protected implementation requires independent GO, matching claim/start authority, reporting, and independent VERIFIED.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Exact registry/checker/test paths are linked to the governing carriers.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project, PAUTH, WI, and target paths are explicit.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Independent verification executes every registry failure mode and deterministic output check.
- `GOV-STANDING-BACKLOG-001` - WI-5152 remains the durable owner of broader hard-invariant coverage beyond this first slice.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - All implementation and runtime output remain under `E:\GT-KB`.

## Prior Deliberations

- `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-ASSURANCE-INVARIANT-PLAN` - Establishes the assurance registry and fail-closed evaluation sequence.
- `DELIB-202666080` - Approves the exact Gate 1.25 applicability map and child outcomes.
- `DELIB-202666274` - Authorizes the modernization program while retaining bridge and exact Git gates.

## Owner Decisions / Input

No new owner decision is required. The active Assurance PAUTH and approved
Gate 1.25 design cover this proposal. This proposal does not authorize database
mutation, Git staging/commit, cleanup, dispatcher/TAFE/harness mutation,
release, deployment, or WI-5158 Git operations.

## Requirement Sufficiency

Existing requirements sufficient. The four governing carriers define the 28
outer assertions, and the cross-cutting/evaluability carriers define registry
and fail-closed behavior. No carrier amendment is required.

## Exact Assertion Map

| Carrier | MUST_APPLY to WI-5158 | DEFERRED_TO | Conditional |
|---|---|---|---|
| `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001` v1 | `GIT-ADR-A1`, `A2`, `A3`, `A4`, `A6`, `A7` | `GIT-ADR-A5` -> `WI-5159` | none |
| `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` v1 | `GIT-REQ-A1`, `A2`, `A3`, `A4`, `A6`, `A8` | `GIT-REQ-A5` -> `WI-5159`; `GIT-REQ-A7` -> `WI-5160` | none |
| `DCL-GIT-BRANCH-BINDING-PROMOTION-001` v2 | `BRANCH-BIND-A1`, `A2`, `A3`, `A4`, `A5`, `A7`, `A8`, `A9` | `BRANCH-BIND-A6` -> `WI-5159` | none |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` v1 | `A1` proposal; `A2` activation; `A3` verification/closure | none | `A4` is `NOT_APPLICABLE` only after deterministic proof that no active worker-loading route changes; otherwise `MUST_APPLY` or `UNASSESSED`. |

Totals: 28 outer assertions; 23 `MUST_APPLY`; 4 `DEFERRED_TO`; one conditional entry.

## Proposed Scope

1. Add `modernization-hard-invariants.toml` with schema version, slice identity, exact work item/gate, and exactly 28 entries.
2. Require every entry to carry carrier ID/version, outer assertion ID, applicability, owning WI, gate, evaluator route, current-evidence identity, severity, and provenance.
3. Limit applicability to `MUST_APPLY`, `DEFERRED_TO`, and governed conditional `NOT_APPLICABLE`; unknown/unclassified values fail.
4. Resolve each carrier and exact version from MemBase at runtime without mutating it.
5. Resolve every deferred successor, active project membership, gate, and owner-approved charter provenance; missing/stale successors fail.
6. Invoke or consume WI-5153's evaluator for current evidence. Missing evaluator, changed carrier version, stale evidence, unsupported assertions, contradictory applicability, or unassessed results block.
7. Keep the full carrier `PARTIAL` while any `DEFERRED_TO` assertion remains incomplete; never convert a scoped pass to a full-carrier pass.
8. Permit non-impairment `A4` as `NOT_APPLICABLE` only from a deterministic target-path and dependency proof showing no active worker-loading route change.
9. Emit stable JSON with normalized ordering and a nonzero exit for every aggregate state other than complete slice PASS.
10. Prove repeated unchanged runs are byte-identical apart from no timestamps; the report contains no volatile field.
11. Keep `config/governance/spec-applicability.toml` and `config/governance/adr-dcl-clauses.toml` as bridge discovery/review aids, not this registry's authority.
12. Keep WI-5152 open after the 28-entry slice for the broader all-carrier/all-modernization Assurance charter.
13. Exclude database/formal-carrier mutation, result receipts, bridge/dispatcher/harness controls, WI-5158 Git activity, and any fourth file.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-202666080",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "python scripts/check_modernization_invariant_registry.py --work-item WI-5158 --gate verification --json",
  "before_behavior": "Gate 1.25 has an approved prose map but no executable outer-assertion-to-WI registry or deterministic result projection.",
  "after_behavior": "Each of 28 assertions has explicit applicability, evaluator, current evidence, and fail-closed successor semantics in one source-linked projection.",
  "self_descriptive_naming": "Carrier IDs, outer assertion IDs, applicability states, successor WIs, and gates are literal registry fields.",
  "obsolete_guidance_disposition": "Existing heuristic applicability and clause registries remain discovery aids and are explicitly not promoted to formal assertion authority.",
  "history_preservation": "Formal carrier versions, assertion history, deliberations, deferred successor records, and evaluator evidence remain unchanged and queryable.",
  "baseline": {
    "registry_exists": false,
    "entry_count": 0,
    "approved_entry_count": 28,
    "must_apply": 23,
    "deferred_to": 4,
    "conditional": 1
  },
  "expected_result": {
    "registry_exists": true,
    "entry_count": 28,
    "must_apply": 23,
    "deferred_to": 4,
    "conditional": 1,
    "deterministic_runs": true
  },
  "rollback": "Remove only the three WI-5152 files through a separately governed rollback; preserve carriers, WI-5153, project/backlog state, and all concurrent work.",
  "hard_invariants": [
    "exactly 28 entries and no duplicate carrier/assertion key",
    "no missing or stale carrier version",
    "no missing evaluator or evidence identity",
    "no incomplete deferred successor hidden as carrier PASS",
    "no conditional NOT_APPLICABLE without deterministic worker-route proof",
    "no database or formal-carrier mutation"
  ],
  "fail_closed_conditions": [
    "WI-5153 unavailable or unverified",
    "carrier or assertion missing",
    "carrier version changes",
    "unknown applicability",
    "missing or stale successor membership",
    "missing current evidence",
    "nondeterministic normalized report"
  ],
  "essential_context_preservation": "The exact approved 28-entry map, all four carrier sources, deferred ownership, conditional route rule, and broader WI-5152 backlog scope remain visible."
}
```

## Spec-Derived Verification Plan

| Requirement | Verification | Expected result |
|---|---|---|
| Exact map/schema | `python -m pytest platform_tests/scripts/test_modernization_invariant_registry.py -q --tb=short` | Exactly 28 entries, 23 MUST_APPLY, 4 DEFERRED_TO, 1 conditional; all required fields and versions match. |
| Fail-closed evaluability | Focused fixtures for missing evaluator, unsupported assertion, stale version/evidence, contradiction, and unassessed result | Every fixture exits nonzero with stable reason codes. |
| Deferred ownership | Fixtures for missing WI-5159/WI-5160, inactive membership, wrong gate/charter, and incomplete deferred evidence | Slice and full carrier cannot pass. |
| Conditional A4 | Fixtures with and without active worker-loading route changes | `NOT_APPLICABLE` only with deterministic no-route-change proof; otherwise MUST_APPLY/UNASSESSED. |
| Determinism | Run `python scripts/check_modernization_invariant_registry.py --work-item WI-5158 --gate verification --json` twice and compare bytes | Identical normalized reports and exit codes. |
| Existing discovery tools | `python -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/scripts/test_adr_dcl_clause_preflight.py -q --tb=short` | Existing heuristic proposal/review discovery remains green and non-authoritative. |
| Scope isolation | Hash/check only the three target paths | No database, formal carrier, existing registry, bridge, dispatcher, harness, or Git mutation occurs. |

## Acceptance Criteria

1. The registry contains exactly the approved 28 entries and required metadata.
2. Every entry resolves to a current exact carrier assertion and evaluator.
3. Missing/stale/unsupported/contradictory/unassessed evidence blocks.
4. Deferred assertions keep full carriers partial until successor evidence completes.
5. Conditional A4 cannot become not-applicable without deterministic proof.
6. Unchanged repeated runs are deterministic.
7. Existing applicability/clause discovery behavior remains green.
8. Only the three new files are implementation scope; WI-5152 stays open for broader coverage.

## Risk / Rollback

The registry will expose unresolved Gate 1.25 evidence instead of making WI-5158
ready immediately; that is the intended fail-closed result. The main design risk
is creating a second authority, controlled by resolving every entry back to the
formal carrier and treating the TOML/report as a generated source-linked
projection only.

Rollback removes the three new files through a separately governed transaction.
No carrier, database, project, work item, bridge history, or concurrent path is
rewritten.

## Bridge Filing

This proposal is filed as the next append-only numbered file for
`gtkb-wi5152-modernization-hard-invariant-registry`. Dispatcher/TAFE state plus
the numbered file chain remain workflow authority; this session performs no
manual routing or direct harness contact.

## Recommended Commit Type

`feat` - adds a new deterministic governance registry and checker surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
