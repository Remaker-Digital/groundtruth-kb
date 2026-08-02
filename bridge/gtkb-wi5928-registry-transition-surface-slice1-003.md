REVISED
::init gtkb pb
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 0f38ea76-2b25-4e4e-8913-45f97c849364
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb
author_metadata_source: interactive_claude_session prime-builder/claude/B


# Implementation Proposal - Build registry identity-transition capability (transition-request/transition-apply) per DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001

bridge_kind: prime_proposal
Document: gtkb-wi5928-registry-transition-surface-slice1
Version: 003
Date: 2026-08-02 UTC
Responds to: bridge/gtkb-wi5928-registry-transition-surface-slice1-002.md

Project Authorization: PAUTH-PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT-WI-5928-REGISTRY-TRANSITION-SURFACE-SLICE-1-BOUNDED-IMPLEMENTATION
Project: PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT
Work Item: WI-5928
Latest Bridge Status: NO-GO
Reviewed Proposal Version: 3

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_registry_transition_slice1.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## REVISED Note (v003)

This REVISED addresses the sole blocking finding of the v002 NO-GO (F1, P0):
the operative v001 carried `author_identity: claude`, which is not
role-parseable, so `bridge_lifecycle_resolver` classified the operative
`legacy` and a dependent LO GO failed `OPERATIVE_VERSION_MISSING_PROVENANCE`.
This v003 operative carries a strict role-qualified `author_identity:
prime-builder/claude` with complete author metadata (including
`author_metadata_source`) so the operative is publication-eligible under
`GOV-DOCUMENT-AUTHOR-PROVENANCE-001` and a dependent LO GO can publish.

The Slice-1 design body below is UNCHANGED from v001 and was pre-accepted per
the v002 Design Note (request/apply wrapping `apply_registry_transaction`,
membership-set + coverage-mode only, fixture-only registry writes, deferral of
move/rename/delete-quarantine to later slices). Provenance-only correction; no
design, scope, target_paths, or acceptance change from v001. Root cause of the
bare identity: a concurrent same-tree Cursor LO run contaminated this PB
session's role surfaces and the author-metadata env-merge dropped the role
prefix (tracked as WI-5929).

## Summary

Slice 1 of WI-5928: build the gt registry transition-request/transition-apply authorized wrapper plus CLI on the existing generic apply_registry_transaction primitive and journal substrate, delivering the membership-set and coverage-mode identity-transition path per DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001. Unblocks WI-5925 and every future registry membership removal / coverage change platform-wide. Predecessor verified from LO NO-GO bridge/gtkb-wi5925-registry-recursive-container-coverage-002.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`, `groundtruth-kb/src/groundtruth_kb/cli.py`, `platform_tests/scripts/test_registry_transition_slice1.py`.

## Specification Links

- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` - governing mutation-authorization DCL: transition request/apply is the only lawful path for coverage-mode / membership identity transitions.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - forward-only strict operative author provenance (the v002 blocker).
- `GOV-PLATFORM-SOT-REGISTRY-001` - registry authority; direct TOML prohibited; removal/transition requires digest-bound authorization.
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` - journalled declaration/projection parity for identity mutations.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance baseline.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - lifecycle-trigger discipline.
- `GOV-STANDING-BACKLOG-001` - standing backlog authority.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - artifact-oriented development baseline.

## Prior Deliberations

- `DELIB-202668163` - Owner authorization: build registry identity-transition surface first (WI-5928, predecessor to WI-5925).
- `bridge/gtkb-wi5925-registry-recursive-container-coverage-002.md` - LO NO-GO that surfaced the missing transition surface.
- `bridge/gtkb-wi5928-registry-transition-surface-slice1-002.md` - LO NO-GO on v001 (design accepted; provenance-only blocker addressed here).


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

- `DELIB-202668163` - owner AUQ decision "Build the transition surface first" authorizing WI-5928 (outcome owner_decision, source owner_conversation).
- `PAUTH-PROJECT-GT-KB-REGISTRY-COVERAGE-MODEL-REFINEMENT-WI-5928-REGISTRY-TRANSITION-SURFACE-SLICE-1-BOUNDED-IMPLEMENTATION` - active project authorization covering `WI-5928` (source + test mutation classes).

## Proposed Scope

- transition-request records a digest-bound request in sot_registry_transaction_journal (operation=transition_request) binding entry id, source locator, current revision digest, operation, destination, owner evidence, intended membership result, and expiry; returns a request handle
- transition-apply requires an OPS envelope, a matching active request, a matching independent bridge GO, and fresh operation-time revalidation (current revision digest unchanged); computes the desired record set (membership removals plus coverage-mode changes) and commits it through the existing apply_registry_transaction(desired, operation=transition)
- Add gt registry transition request and gt registry transition apply subcommands to the registry command group; reuse the existing lock, journal, digest, projection-parity, and RegistryResolver overlap validation with NO new transaction machinery
- Slice 1 scope is membership-set and coverage-mode identity transitions only (in-place declaration changes, no filesystem move/rename/delete); delete-to-quarantine, move/rename, and 30-day retention are explicitly deferred to Slice 2+
- RegistryResolver validates the desired set for exact-under-recursive overlap before commit, so an exact-to-recursive coverage conversion with the mandated exact-child removals is enforced coherent; amend continues to reject coverage-mode/lifecycle/membership changes and direct TOML editing remains prohibited
- This implementation performs no MemBase mutation and executes no groundtruth.db writes against the canonical KB: it adds source and test code only; the transition surface runtime registry-journal writes are exercised solely against test fixtures, not the live groundtruth.db

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` | new tests assert transition request/apply gating (OPS envelope, matching active request, independent bridge GO, fresh revalidation) and that membership removal plus coverage-mode change succeed only through this path |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | operative proposal head carries a strict role-qualified author_identity; bridge_lifecycle_resolver classification is non-legacy and author_role resolves to prime-builder |
| `GOV-PLATFORM-SOT-REGISTRY-001` | test asserts a coverage-mode transition plus membership removal commits through gt registry transition and gt registry validate passes with no coverage overlap |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | test asserts declaration/projection parity and journal recoverability after a transition apply |

## Acceptance Criteria

- transition request creates a digest-bound journal request carrying the DCL-required fields; transition apply is rejected when there is no matching active request, no matching independent bridge GO, or the source revision digest is stale
- an exact-to-recursive coverage conversion with the mandated exact-child membership removals succeeds via transition apply, and gt registry validate and gt registry reconcile pass afterward
- amend still rejects coverage-mode / lifecycle / membership changes (unchanged); no direct-TOML mutation path is introduced
- operative REVISED proposal carries a strict role-qualified author_identity so bridge_lifecycle_resolver classifies it non-legacy and a dependent LO GO verdict publishes without OPERATIVE_VERSION_MISSING_PROVENANCE

## Bulk-Operation Visibility Disposition

This proposal builds the transition capability and performs no bulk backlog or registry operation itself; it adds source and test code only (three target files). No inventory artifact or review packet is required here because no bulk backlog/registry mutation occurs under this WI-5928 build slice. The actual bulk registry operation (the WI-5925 downstream membership removals plus coverage-mode conversions) is a separate work item that will produce its own inventory artifact and review packet when it consumes `gt registry transition`. DECISION DEFERRED: bulk-operation visibility evidence for the conversion itself is deferred to the WI-5925 REVISED that uses this surface, per GOV-STANDING-BACKLOG-001.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures. Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `platform_tests/scripts/test_registry_transition_slice1.py`

## Recommended Commit Type

`feat`
