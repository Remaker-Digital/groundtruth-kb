NEW
::init gtkb pb
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2151f0fd-f0fa-45b4-874f-3ef9377444bb
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb
author_metadata_source: interactive_claude_session prime-builder/claude/B

# Post-Implementation Report - WI-5925 recursive-container conversion (live) via the governed transition surface

bridge_kind: prime_proposal
Document: gtkb-wi5925-registry-recursive-container-coverage
Version: 005
Date: 2026-08-02 UTC
Responds to: bridge/gtkb-wi5925-registry-recursive-container-coverage-004.md

Project Authorization: PAUTH-PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT-REGISTRY-RECURSIVE-CONTAINER-CONVERSION-BOUNDED-IMPLEMENTATION-CORRECTED-2026-08-01
Project: PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT
Work Item: WI-5925
Latest Bridge Status: GO

target_paths: ["config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

The live recursive-container conversion is complete and self-verified. Through the governed `gt registry transition` + `gt registry register` surface (WI-5928 Slice 1), `platform_tests/` and `groundtruth-kb/tests/` were converted from per-file exact to recursive coverage: 975 exact test-tree rows were removed via a single membership-set transition, then 2 recursive parents + 4 exact non-test rows were registered. The registry moved 2348 -> 1379 records, the 27-file `unregistered_load_bearing` gap is fully closed (0), and the registry validates. No `sot-artifacts.toml` hand-edit occurred; every mutation is a journalled registry-transaction receipt.

This slice performs no MemBase mutation: no specification, work-item, or deliberation record was inserted or modified (`kb_mutation_in_scope: false`). The SoT-registry declaration/projection is the only state changed, through the registry control plane's own transaction authorization.

## Requirement Sufficiency

Existing requirements are sufficient. Owner AUQ `DELIB-202668162` + the active PAUTH + the session AUQ dropping stale-absent define the boundary; the governing mutation contract `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` is in force.

## In-Root Placement Evidence

Both changed declaration paths are inside `E:\GT-KB`. `applications/` is untouched. The 6 registered records are all in-root.

## Specification Links

- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` - the request/apply contract used for the 975 removals; `amend` was not used for any identity change.
- `GOV-PLATFORM-SOT-REGISTRY-001` - no direct TOML/projection edit; every mutation is a governed `gt registry` transaction receipt.
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` - post-conversion `validate` passes (declaration/projection parity); canonical and packaged mirror are byte-identical.
- `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `ADR-ISOLATION-APPLICATION-PLACEMENT-001`; `GOV-STANDING-BACKLOG-001` (bulk-operation visibility); `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`.

## Prior Deliberations

- `DELIB-202668162` - owner AUQ for the recursive-container conversion.
- `bridge/gtkb-wi5925-registry-recursive-container-coverage-004.md` - the GO whose verdict was supplied as the independent apply authorization (Hold 6).
- `bridge/gtkb-wi5928-registry-transition-surface-slice1-006.md` - VERIFIED transition surface consumed here.
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` - request/apply contract.

## Owner Decisions / Input

- `DELIB-202668162` - owner AUQ authorizing the conversion (outcome owner_decision).
- Owner AUQ this session (`detected_via: ask_user_question`): core conversion, drop stale-absent.
- `PAUTH-...-REGISTRY-RECURSIVE-CONTAINER-CONVERSION-...-CORRECTED-2026-08-01` - active project authorization; impl-start packet `sha256:95638816...` minted from the -004 GO.

## Implemented Result (governed receipts)

### Transition - 975 membership removals

- Request: `REGTXNREQ-2CDF7055DFF5464689D1F87ACB576140`; bound generation digest `sha256:1648ec38...`.
- Apply journal: `SOTTXN-B732FD529AC7495F87CCC264AF30A257`; operation `transition`; receipt `sha256:93ce1b54...`; declaration `sha256:3fbc7f4d...`.
- Result: 2348 -> 1373 records; test-tree exact rows remaining = 0.
- Apply authorization (Hold 6): the -004 GO supplied as `apply_authorization` (`status=GO`, `bridge_id=gtkb-wi5925-registry-recursive-container-coverage`, `author_session_context_id=33ad40f0-...` != this session `2151f0fd-...`).

### Register - 2 recursive parents + 4 exact adds

- Dry-run receipt (Hold 1): `sha256:62a54c90...`; desired record count 1379.
- Apply journal: `SOTTXN-76ACB26E920A4415AA0BAA918A1A8ECC`; operation `register`; receipt `sha256:97576d70...`.
- Added: recursive `platform_tests/`, recursive `groundtruth-kb/tests/`, exact `config/agent-control/goose-execution-floor.toml`, `groundtruth-kb/src/groundtruth_kb/project/operational_control_config.py`, `groundtruth-kb/src/groundtruth_kb/project/timer_config.py`, `scripts/goose_execution_guard.py`.
- Result: 1373 -> 1379 records.

### Mechanism note (Hold 1 fidelity)

The 975 removals were executed through the same `transition_request` / `transition_apply` functions that `gt registry transition request|apply` wrap, invoked directly because 975 `--removal` CLI flags exceed the Windows command-line length limit. The governance path is byte-identical (same OPS-envelope / active-request / independent-GO / fresh-digest gates, same journalled generation commit); the journal records `operation=transition`. The removal transition's `entry_id` is a representative removed record (a pure membership-set removal has no coverage-changed parent); the authoritative change is `intended_membership_result.removals` (the 975 ids).

## Specification-Derived Verification (closure gates, Hold 4)

| Check | Before | After |
| --- | --- | --- |
| `gt registry reconcile` record count | 2348 | 1379 |
| `unregistered_load_bearing` | 27 | **0** |
| `invalid_unknown` | 0 | 0 |
| `membership_complete` | false | **true** |
| `registered` members | 18215 | 19967 |
| `validate_registry` (full, reverse-closure) | - | **valid=True, errors=[]** |
| test-tree exact rows | 975 | **0** |
| canonical vs packaged mirror | - | byte-identical (`sha256:4C8FC228...`) |

Registered members rose (18215 -> 19967) because recursive coverage counts every descendant of the two test trees as a member; 975 per-file rows collapse into 2 recursive parents while coverage expands. Bulk-operation visibility: the removal inventory is `.gtkb-state/wi5925-removal-inventory.json` (`removal_count=975`; 651 `platform_tests/` + 324 `groundtruth-kb/tests/`).

## Acceptance Criteria Check

- [x] `reconcile`: `membership_complete=true`, `unregistered_load_bearing=0`, `invalid_unknown=0`.
- [x] `validate`: coherent schema, projection parity, no coverage overlap, currentness, journal, reverse coverage (valid=True).
- [x] No `platform_tests/` or `groundtruth-kb/tests/` exact rows remain; 2 recursive parents + 4 exact adds present; net 1379 records.
- [x] Every mutation is a governed transition/register receipt; no direct TOML/projection edit in the diff.

## Binding Start Holds - Compliance

1. **Mechanism** - transition (removals) then register (adds); no hand-edit. ✓
2. **Independent apply GO** - -004 GO supplied as `apply_authorization` from an independent session. ✓
3. **Ordering** - removals committed first (1373), parents registered only after children were gone. ✓
4. **Closure gates** - receipts + before/after reconcile + validate above; net 1379. ✓
5. **Declared targets only** - only the 2 declaration TOMLs changed (byte-identical); `applications/` untouched; no MemBase mutation. ✓
6. **Shared-path recheck** - both declaration paths were git-clean at implementation-start (recorded). ✓
7. **Rollback** - a pre-mutation DB snapshot was taken; rollback path is `git revert` of the declaration generation + `gt registry recover` / `reconcile`. ✓

## Recommended Commit Type

`feat` - registry coverage-model refinement: recursive coverage for the two high-churn test trees closes the membership gap and prevents per-file drift recurrence. (Declaration/config change via the governed transaction; no source code added.)

## Files Changed

- `config/registry/sot-artifacts.toml` (governed transition + register; not hand-edited)
- `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml` (packaged mirror; byte-identical to canonical)

The SoT-registry projection is regenerated as the `runtime_state` consequence of the same journalled transactions. This slice performs no MemBase mutation (no specification/work-item/deliberation insert); the two declaration files are the only declared target paths.
