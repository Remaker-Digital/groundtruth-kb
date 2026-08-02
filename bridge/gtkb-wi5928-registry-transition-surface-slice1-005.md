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

# Post-Implementation Report - WI-5928 Slice 1 registry identity-transition surface

bridge_kind: prime_proposal
Document: gtkb-wi5928-registry-transition-surface-slice1
Version: 005
Date: 2026-08-02 UTC
Responds to: bridge/gtkb-wi5928-registry-transition-surface-slice1-004.md

Project Authorization: PAUTH-PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT-WI-5928-REGISTRY-TRANSITION-SURFACE-SLICE-1-BOUNDED-IMPLEMENTATION
Project: PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT
Work Item: WI-5928
Latest Bridge Status: GO

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_registry_transition_slice1.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Slice 1 of WI-5928 is implemented. The `gt registry transition request` / `gt registry transition apply` surface is built on the existing `apply_registry_transaction` primitive and journal substrate, delivering the membership-set and in-place coverage-mode identity-transition path per `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`. This unblocks WI-5928's successor WI-5925 (which will consume the surface for the 975 exact->recursive membership removals in a separate cycle) and every future registry membership removal / coverage change platform-wide. No live registry or MemBase mutation occurred; all runtime registry-journal writes are exercised solely against test fixtures.

The implementation matches the v003 design GO'd at v004 and honors all six Binding Start Holds (evidence below).

## Requirement Sufficiency

Existing requirements are sufficient. The work item and the active project authorization define the implementation boundary; no new or revised requirement was needed for this slice.

## In-Root Placement Evidence

All three changed paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`, `groundtruth-kb/src/groundtruth_kb/cli.py`, `platform_tests/scripts/test_registry_transition_slice1.py`.

## Specification Links

- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` - governing mutation-authorization DCL: transition request/apply is the only lawful path for coverage-mode / membership identity transitions. Implemented as `transition_request` / `transition_apply`.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - this report's operative head carries a strict role-qualified `author_identity: prime-builder/claude`.
- `GOV-PLATFORM-SOT-REGISTRY-001` - registry authority; direct TOML prohibited; removal/transition requires digest-bound authorization. The new operation reuses the journalled generation commit.
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` - declaration/projection parity is preserved across a transition apply (verified post-transition).
- `GOV-FILE-BRIDGE-AUTHORITY-001` - report filed on the numbered bridge chain.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete spec links carried forward.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping and executed evidence below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization, project, work item, and target-path metadata present.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the command stays in platform scope (`groundtruth_kb.project`), out of adopter application scope.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` / `GOV-STANDING-BACKLOG-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - governance baselines (carried forward from the GO'd proposal).

## Prior Deliberations

- `DELIB-202668163` - Owner authorization: build the registry identity-transition surface first (WI-5928, predecessor to WI-5925).
- `bridge/gtkb-wi5928-registry-transition-surface-slice1-003.md` - the design proposal (GO'd at -004); design body unchanged in implementation.
- `bridge/gtkb-wi5928-registry-transition-surface-slice1-004.md` - the LO GO carrying the six Binding Start Holds honored here.
- `bridge/gtkb-wi5925-registry-recursive-container-coverage-002.md` - LO NO-GO that surfaced the missing transition surface; WI-5925 stays parked until this surface is VERIFIED.
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` v2 - the request/apply contract implemented here.

## Owner Decisions / Input

- `DELIB-202668163` - owner AUQ decision "Build the transition surface first" authorizing WI-5928 (outcome owner_decision, source owner_conversation).
- `PAUTH-PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT-WI-5928-REGISTRY-TRANSITION-SURFACE-SLICE-1-BOUNDED-IMPLEMENTATION` - active project authorization covering `WI-5928` (source + test mutation classes); implementation-start packet minted from the v004 GO before any protected edit.

## Implemented Changes

### `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`

1. **New capability table `sot_registry_transition_requests`** (in `ensure_control_plane_schema`) - dedicated active/consumed/expiry lifecycle store mirroring the observation- and publication-capability tables. Binds request_id, request_digest, entry_id, source_locator, current_revision_digest, operation, destination, owner_evidence, intended_membership_result, expiry, and audit columns. **Honors Hold 1**: a pending request never touches `sot_registry_transaction_journal`, so it cannot trip `apply_registry_transaction`'s incomplete-journal gate.
2. **`transition_request(...)`** - validates Slice-1 operation scope (rejects move/rename/delete as deferred), binds the current generation digest and the intended membership result, and records an `active` request under the registry file lock.
3. **`transition_apply(...)`** - enforces the four DCL apply gates (OPS envelope; matching active request; matching independent bridge GO with self-review rejection; fresh operation-time digest revalidation), computes the desired record set (removals + coverage changes), and commits it via `apply_registry_transaction(operation="transition", expected_prior_generation_digest=<bound digest>)`. **Honors Hold 2** (amend-style digest revalidation) and **Hold 6** (each live apply requires its own independent GO).
4. **Three surgical relaxations to the shared commit path, each strictly gated on `operation == "transition"`** so `register` / `amend` / `legacy_bootstrap` are byte-for-byte unchanged:
   - `apply_registry_transaction` removal guard (was: reject any `old_ids - desired_ids`) now permits removals only for `transition`.
   - `transition` now takes the same amend-style early digest revalidation and raises `RegistryGenerationConflict` (not the generic authorization error) on a stale generation.
   - `_append_projection_versions` gains an `allow_removal` parameter; `_commit_prepared_generation` passes `allow_removal=(operation == "transition")`.

### Design decision requiring LO scrutiny - projection membership removal

`current_sot_artifacts` is `MAX(version) per id` with no lifecycle/tombstone filter, so a removed member leaves the projection only if its `sot_artifacts` rows physically leave the table. For `operation == "transition"`, `_append_projection_versions` therefore **physically deletes** the removed ids' `sot_artifacts` rows so the post-commit projection digest equals `_projection_digest(desired)` and parity holds.

- **Append-only tension, deliberately resolved.** The removal stays fully audited: the transaction journal records old/new declaration/packaged/projection digests plus the complete desired payload, and the canonical `config/registry/sot-artifacts.toml` is git-tracked (full declaration history). Only the *derived current-state projection mirror* rows are dropped; the canonical declaration and the journal remain the audit trail.
- **Alternative considered and deferred.** A tombstone version filtered out of `current_sot_artifacts` would preserve projection rows but requires changing the shared view DDL and every consumer of `current_sot_artifacts` - out of scope for a Slice-1, fixture-only surface. If LO prefers the tombstone model, that is a bounded follow-on.
- **Scope note.** This is the projection realization of the "membership removal" the GO'd design routes through `apply_registry_transaction`; it is not a new transaction engine (lock, journal, digest revalidation, projection-parity, and RegistryResolver overlap validation are all reused unchanged).

### `groundtruth-kb/src/groundtruth_kb/cli.py`

Added the `gt registry transition` subgroup with `request` and `apply` subcommands, reusing the existing `_registry_authority_options` decorator and `_registry_control_kwargs`.

### `platform_tests/scripts/test_registry_transition_slice1.py` (new)

11 spec-derived tests covering every apply gate, the fixture-only conversion, the Slice-1 scope boundary, journal hygiene, single-use consumption, amend-unweakened, and CLI wiring.

## Specification-Derived Verification (spec-to-test mapping)

| Spec / Hold | Test(s) | Evidence |
| --- | --- | --- |
| `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` (four apply gates) | `test_apply_rejects_without_ops_envelope`, `test_apply_rejects_without_active_request`, `test_apply_rejects_without_independent_go`, `test_apply_rejects_on_stale_digest` | each gate rejects fail-closed |
| `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` (happy path) | `test_apply_converts_coverage_and_removes_members` | opaque->recursive conversion + member removals commits; post-state asserted |
| `GOV-PLATFORM-SOT-REGISTRY-001` / `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | `test_apply_converts_coverage_and_removes_members` | `validate_registry(require_reverse_closure=False)["valid"]` is True post-transition |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | this operative head | `author_identity: prime-builder/claude` (strict) |
| Hold 1 (journal hygiene) | `test_request_binds_dcl_fields_and_keeps_journal_clean` | `_nonterminal_journal(db_path) is None` after request |
| Hold 2 (apply digest binding) | `test_apply_rejects_on_stale_digest` | `RegistryGenerationConflict` on superseded generation |
| Hold 3 (no live mutation) | all tests | fixture registry/packaged/db paths only |
| Hold 6 (independent GO per apply) | `test_apply_rejects_without_independent_go` | same-session GO rejected as self-review |
| Slice-1 scope boundary | `test_request_rejects_deferred_move_operation` | move/rename/delete rejected |
| Single-use | `test_apply_is_single_use` | consumed request cannot re-apply |
| amend unweakened | `test_amend_still_rejects_identity_and_coverage_changes` | coverage/locator/lifecycle amends still rejected |
| CLI wiring | `test_cli_transition_subcommands_registered` | `gt registry transition request|apply --help` exit 0 |

## Commands Executed

```text
# implementation-start authorization (minted from the v004 GO)
python scripts/bridge_claim_cli.py claim gtkb-wi5928-registry-transition-surface-slice1   # exit 0
python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5928-registry-transition-surface-slice1   # exit 0

# code-quality gates (separate; both required)
ruff check <3 changed files>            # All checks passed!
ruff format --check <3 changed files>   # 3 files already formatted

# new spec-derived tests
python -m pytest platform_tests/scripts/test_registry_transition_slice1.py -q   # 11 passed

# regression: existing control-plane suite unaffected by the shared-path relaxations
python -m pytest groundtruth-kb/tests/test_registry_control_plane.py -q   # 58 passed
```

## Acceptance Criteria Check

- [x] transition request creates a digest-bound request carrying the DCL-required fields; apply is rejected without a matching active request, without a matching independent bridge GO, and on a stale source revision digest.
- [x] an exact/opaque -> recursive coverage conversion with the mandated member removals succeeds via transition apply, and `validate_registry` passes afterward (fixture reverse-closure census disabled per Hold 3; the live-tree census + `gt registry reconcile` are exercised by the downstream WI-5925 live cycle).
- [x] amend still rejects coverage-mode / locality / lifecycle changes (unchanged); no direct-TOML mutation path introduced.
- [x] operative report head carries a strict role-qualified `author_identity` so the lifecycle resolver classifies it non-legacy.

## Binding Start Holds - Compliance

1. **Request journal hygiene** - dedicated `sot_registry_transition_requests` table; journal untouched by requests (test-proven).
2. **Apply digest binding** - `transition_apply` revalidates the bound generation digest and passes `expected_prior_generation_digest` to `apply_registry_transaction` (amend-style).
3. **No live WI-5925 conversion under this GO** - source/test only; every test uses fixture paths; no `config/registry/sot-artifacts.toml` / packaged-mirror / live `groundtruth.db` mutation.
4. **Shared identity-authorization / hook wiring deferred** - request/apply shipped without hook call sites; the DCL is NOT claimed complete; the shared identity-authorization service remains a follow-on slice.
5. **Shared-target recheck** - `registry_control_plane.py` and `cli.py` were clean in git at start; no competing in-flight PB edits; recorded before implementation.
6. **Independent GO for each live apply** - `transition_apply` requires an independent-session GO for the apply operation and rejects self-review; this surface is not a standing live-mutation grant.

## Recommended Commit Type

`feat` - net-new registry identity-transition capability (control-plane functions + CLI subgroup + spec-derived tests).

## Risks / Rollback

The shared-path relaxations are strictly gated on `operation == "transition"`; the 58-test existing control-plane regression suite passing confirms register/amend/legacy_bootstrap/reconcile behavior is unchanged. The projection physical-delete for removals is the one item warranting explicit LO judgement (disclosed above). Rollback is a revert of the three source/test targets; bridge and PAUTH records are append-only and are not deleted by rollback.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `platform_tests/scripts/test_registry_transition_slice1.py`
