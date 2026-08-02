REVISED
::init gtkb pb
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2151f0fd-f0fa-45b4-874f-3ef9377444bb
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb
author_metadata_source: interactive_claude_session prime-builder/claude/B

# Implementation Proposal (REVISED) - Recursive-container coverage for high-churn test trees via the governed registry transition surface

bridge_kind: prime_proposal
Document: gtkb-wi5925-registry-recursive-container-coverage
Version: 003
Date: 2026-08-02 UTC
Responds to: bridge/gtkb-wi5925-registry-recursive-container-coverage-002.md

Project Authorization: PAUTH-PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT-REGISTRY-RECURSIVE-CONTAINER-CONVERSION-BOUNDED-IMPLEMENTATION-CORRECTED-2026-08-01
Project: PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT
Work Item: WI-5925
Latest Bridge Status: NO-GO
Reviewed Proposal Version: 3

target_paths: ["config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## REVISED Note (v003) - resolves the v002 NO-GO

The v002 NO-GO accepted the coverage design in full and blocked solely on the **mutation mechanism** (F1: direct-TOML transform is prohibited by `GOV-PLATFORM-SOT-REGISTRY-001` / `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`, and the DCL-required `transition` surface did not exist). That surface now exists and is VERIFIED: **WI-5928 Slice 1** landed `gt registry transition request` / `transition apply` (commit `eacebd5d4`, VERIFIED verdict `bridge/gtkb-wi5928-registry-transition-surface-slice1-006.md`). This REVISED binds the implementation to that governed surface and addresses every finding:

- **F1 (mutation path).** Direct-TOML transform is removed. Membership removals go through `gt registry transition request` / `transition apply`; net-new declarations go through `gt registry register`. `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` is now cited in Specification Links.
- **F2 (evidence overclaim).** Verification is split by operation: transition receipts for the 975 removals; `register --dry-run` receipts for the 6 net-new declarations; `gt registry validate --json` + `gt registry reconcile --json` as closure gates.
- **F3 (stale-absent set).** Dropped from this WI. Fresh live evidence: **zero** active-lifecycle registry records point at an absent file (`absent_active_count=0`), so no stale-absent cleanup is needed for `validate` or `membership_complete`; the original "~11" mixed still-present dashboard artifacts and is unsafe as written. Any stale cleanup is deferred to a separate bounded transition batch.
- **N1 (boilerplate spec-to-test).** The verification table below names concrete registry commands per governing spec.

Coverage design (975 removals + 2 recursive parents + 4 exact adds; retain `src/`/`scripts/` per-file exact; no per-file exact requirement for the two test trees) is carried forward unchanged, re-pinned from fresh live state.

## Summary

Convert `platform_tests/` and `groundtruth-kb/tests/` from per-file exact to recursive SoT-registry coverage through the governed transition + register surface, closing the live 27-file `unregistered_load_bearing` gap and preventing per-file drift recurrence. Fresh live reconcile: `registry_record_count=2348`, `unregistered_load_bearing=27`, `invalid_unknown=0`, `membership_complete=false`. All 27 load-bearing paths are covered by the design (22 `platform_tests/`, 1 `groundtruth-kb/tests/`, 4 exact adds; `uncovered_by_design=0`, verified this session).

## Requirement Sufficiency

Existing requirements are sufficient. The work item, the active project authorization, and owner AUQ `DELIB-202668162` define the boundary. No new or revised requirement is needed; the governing mutation contract `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` is already in force.

## In-Root Placement Evidence

All declared target paths are inside `E:\GT-KB`: `config/registry/sot-artifacts.toml`, `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml`. The 2 recursive parents and 4 exact adds are all in-root; the packaged mirror is the platform's own context registry.

## Specification Links

- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` - governing mutation-authorization DCL (F1 fix): membership-set and coverage-mode identity transitions MUST use `gt registry transition request` / `transition apply` bound to owner evidence and an independent bridge GO; `amend` may not change coverage/lifecycle/membership; `register` may only add.
- `GOV-PLATFORM-SOT-REGISTRY-001` - registry authority; direct TOML / projection editing prohibited; mutation only through the deterministic `gt registry` CLI.
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` - journalled declaration/projection parity through a locked recoverable transaction (a property of each completed transition/register, verified post-apply).
- `GOV-FILE-BRIDGE-AUTHORITY-001` - numbered bridge chain authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete spec links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization / project / work item / target-path metadata.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps registry coverage in platform scope; `applications/` untouched (single hosted_application_boundary).
- `GOV-STANDING-BACKLOG-001` - standing backlog authority; the bulk-operation visibility clause is satisfied by the removal inventory below.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - governance baselines.

## Prior Deliberations

- `DELIB-202668162` - Owner AUQ authorization for this exact recursive-container conversion (two test trees, one governed change); does not waive bridge GO or invent a TOML-edit exception.
- `bridge/gtkb-wi5925-registry-recursive-container-coverage-002.md` - the LO NO-GO this REVISED resolves (design accepted; mutation-path blocked).
- `bridge/gtkb-wi5928-registry-transition-surface-slice1-006.md` - VERIFIED delivery of the `gt registry transition` surface this REVISED consumes (commit `eacebd5d4`).
- `DELIB-202665444` - Owner selected registry-plus-closure scan method for SoT audit coverage completeness (membership_complete semantics).
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` - the request/apply contract used for the 975 removals.

## Owner Decisions / Input

- `DELIB-202668162` - owner AUQ decision authorizing the recursive-container conversion (outcome owner_decision, source owner_conversation).
- Owner AUQ this session (2026-08-02, `detected_via: ask_user_question`): confirmed **core conversion, drop stale-absent** scope for this REVISED.
- `PAUTH-PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT-REGISTRY-RECURSIVE-CONTAINER-CONVERSION-BOUNDED-IMPLEMENTATION-CORRECTED-2026-08-01` - active project authorization covering `WI-5925` (mutation classes configuration + runtime_state; included spec `GOV-PLATFORM-SOT-REGISTRY-001`).

## Proposed Scope

- **Remove 975 exact rows** under `platform_tests/` (651) and `groundtruth-kb/tests/` (324) via `gt registry transition` (membership removals). MANDATORY under the one-declaration-per-path no-overlap invariant (`_validate_overlaps` rejects exact-under-recursive). Exact removal set is inventoried (975 ids+paths) as bulk-operation visibility evidence.
- **Register 2 recursive containers** (`platform_tests/`, `groundtruth-kb/tests/`) modeled on the `config/governance/` recursive precedent (`id=governance-config-tree`); git_tracked, git_restore, authority `GOV-PLATFORM-SOT-REGISTRY-001`. Sequenced AFTER the removals (a recursive parent cannot be registered while its exact children exist).
- **Register 4 exact rows** for genuine non-test drift (all present, currently unregistered): `config/agent-control/goose-execution-floor.toml`, `groundtruth-kb/src/groundtruth_kb/project/operational_control_config.py`, `groundtruth-kb/src/groundtruth_kb/project/timer_config.py`, `scripts/goose_execution_guard.py`.
- **Retain** `src/` and `scripts/` per-file exact identity; `applications/` untouched. **Drop** the v001 stale-absent cleanup (evidence: `absent_active_count=0`).
- Net registry `2348 -> 1379` records.

## Mechanism (governed, ordered; F1/F2 resolution)

1. **Mint** the WI-5925 implementation-start packet from this REVISED's GO (`scripts/implementation_authorization.py begin`), providing the `start_packet_hash`, `pauth_id`, and `bridge_id` the registry transaction records.
2. **Removals (transition).** File a `gt registry transition request` binding the removal set (operation `membership_set`, `intended_membership_result.removals` = the 975 ids) to the current generation digest, then `gt registry transition apply` under an OPS envelope with the **independent WI-5925 GO** supplied as `apply_authorization` (per `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`; each live apply requires its own independent GO). The apply reuses the journalled generation commit (lock, digest revalidation, projection parity). Note: WI-5928 Slice 1 deferred the hook/shared-service wiring, so the WI-5925 GO verdict is supplied to `transition apply` explicitly; wiring that lookup is a tracked follow-on, not a blocker.
3. **Adds (register).** `gt registry register --dry-run` then apply the 2 recursive parents + 4 exact rows as an additive batch (which `register` can lawfully express once the exact children are gone).
4. **Closure.** `gt registry validate --json` and `gt registry reconcile --json` as gates. No direct declaration editing and no direct projection writes at any step; every mutation flows through the governed `gt registry` transaction.

## Specification-Derived Verification Plan

| Spec | Verification (concrete) |
| --- | --- |
| `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` | The 975 removals are performed only via `gt registry transition request`/`apply`; the impl report includes the transition receipt digests and the request handle. `amend` was not used for any identity change. |
| `GOV-PLATFORM-SOT-REGISTRY-001` | No direct TOML/projection edit occurs; every mutation is a `gt registry transition`/`register` receipt. `gt registry reconcile --json` shows `membership_complete=true`, `unregistered_load_bearing=0`. |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | `gt registry validate --json` passes (schema, declaration/projection parity, no coverage overlap, currentness, journal, reverse coverage) after both the transition and the register commit. |
| `GOV-STANDING-BACKLOG-001` (bulk visibility) | The 975-record removal inventory (`.gtkb-state/wi5925-removal-inventory.json`, 651+324) is attached to the impl report as the bulk-operation visibility packet; reconcile counts before/after are recorded. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `applications/` remains a single hosted_application_boundary; no application-scope path is added or removed. |

## Acceptance Criteria

- `gt registry reconcile --json`: `membership_complete=true`, `unregistered_load_bearing=0`, `invalid_unknown=0`.
- `gt registry validate --json`: coherent schema, projection parity, no coverage overlap, currentness, journal, reverse coverage.
- No `platform_tests/` or `groundtruth-kb/tests/` exact rows remain; the 2 recursive parents + 4 exact adds are present; net record count `~1379`.
- Every mutation is evidenced by a `gt registry transition`/`register` receipt; no direct TOML/projection edit in the diff.

## Bulk-Operation Visibility Disposition

This IS the bulk registry operation deferred from WI-5928. The exact 975-record removal set is enumerated in `.gtkb-state/wi5925-removal-inventory.json` (651 `platform_tests/` + 324 `groundtruth-kb/tests/`), generated this session from the live snapshot. The impl report will carry the inventory digest, the transition receipt digest(s), and the before/after `gt registry reconcile --json` counts as the review packet, satisfying `GOV-STANDING-BACKLOG-001`'s bulk-operation visibility clause.

## Risks / Rollback

This is a live bulk registry mutation (975 removals + 6 additions). It fails closed at the transition gates (OPS envelope, active request, independent GO, fresh digest revalidation) and at register's additive validation. The intermediate state between the transition (removals) and the register (adds) transiently shows the two test trees as `unregistered_load_bearing`; the closure gates run only after both steps. Rollback: `git revert` the single registry-declaration generation commit and run `gt registry recover` / `reconcile` to restore the prior journalled generation; bridge and PAUTH records are append-only and are not deleted by rollback.

## Files Expected To Change

- `config/registry/sot-artifacts.toml` (registry declaration; written by the governed transition/register transaction, not hand-edited)
- `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml` (packaged mirror, same journalled generation)

This slice performs no MemBase mutation: no specification, work-item, or deliberation record is inserted or modified (`kb_mutation_in_scope: false`). The SoT-registry projection is regenerated only as the `runtime_state` consequence of the same journalled registry transaction (authority `GOV-PLATFORM-SOT-REGISTRY-001`, PAUTH runtime_state class), governed by the registry control plane's own transaction authorization (packet + OPS envelope + independent GO) rather than by a declared target path. The two declaration files above are therefore the only declared target paths, consistent with the v001 scope the LO accepted.

## Recommended Commit Type

`feat` - net-new recursive registry coverage for the two high-churn test trees, closing the membership gap through the governed transition/register surface.
