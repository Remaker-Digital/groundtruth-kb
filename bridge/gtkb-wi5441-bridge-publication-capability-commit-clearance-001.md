NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f863a-acd3-7320-80c0-1831f0936cc0
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=user
author_metadata_source: x-codex-turn-metadata

# GT-KB Bridge Proposal - WI-5441 Bridge-Publication Commit Clearance

bridge_kind: prime_proposal
Document: gtkb-wi5441-bridge-publication-capability-commit-clearance
Version: 001
Date: 2026-07-27 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-NOTATION-FREE-DIRECT-EDIT-20260726
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5441
target_paths: ["scripts/check_protected_commit_authorization.py","platform_tests/scripts/test_check_protected_commit_authorization.py"]
Requirement Sufficiency: Existing requirements sufficient
KB Mutation: This proposal performs no MemBase mutation.

---

## Objective

Restore terminal bridge finalization by making the protected-commit checker
consume the typed bridge-publication evidence that the canonical bridge writer
already records. Keep the repair exact-path, fail-closed, and limited to the
checker plus its focused test module.

This is a prerequisite repair for both
`gtkb-wi5441-owner-liveness-spec-amendments` and
`gtkb-wi5424-auto-finalization-import-repair-v2`. It does not re-review either
thread and does not alter their prepared verdict bodies.

## Requirement Sufficiency

**Existing requirements sufficient.** The current registry mutation,
projection-parity, bridge-authority, and VERIFIED-finalization requirements
already require typed, exact, independently reviewable publication evidence.
The defect is an adapter mismatch between two existing evidence tables, not a
missing owner requirement or policy choice.

No specification, Deliberation Archive record, approval packet, or MemBase row
is created or changed by this repair.

## Proven Failure

The canonical bridge writer records each versioned bridge publication in
`sot_registry_bridge_publication_capabilities`, then appends an aggregate
`sot_artifact_revisions` row with `operation = bridge_publication` and the same
`capability_hash`.

`scripts/check_protected_commit_authorization.py` instead resolves every
registered staged path through the newest aggregate revision and looks up that
hash only in `sot_registry_observation_capabilities`. The lookup is structurally
empty for bridge publications. Their revisions also carry no transaction
`journal_id`, so both registry-clearance routes are unreachable.

Independent LO evidence in
`bridge/gtkb-lo-tooling-defect-advisory-007.md` reproduces this with a twelve
Markdown-file finalization set and no database or approval packet. Two separate
review sessions produced compensated v012 publication rows and no stranded
verdict, proving both the lookup defect and rollback behavior.

## Important Aggregate-Entry Detail

The registry entry `bridge-versioned-files` recursively covers `bridge/`.
Terminal finalization can stage an entire previously-untracked numbered chain,
while the newest aggregate revision and newest capability describe only the
new terminal verdict path.

Therefore this repair MUST NOT merely query the newest aggregate revision's
capability and apply it to every staged bridge path. It must resolve each staged
bridge path to its own consumed publication capability by exact normalized
`target_path`, then verify that capability's linked aggregate revision and
staged bytes.

## Proposed Design

For a registered staged path whose aggregate revision family is
`bridge_publication`:

1. Normalize the staged repository-relative path using the checker's canonical
   path normalizer.
2. Query `sot_registry_bridge_publication_capabilities` for the exact
   `aggregate_entry_id` plus exact `target_path`, preferring the newest row only
   when duplicate historical attempts exist.
3. Accept only a successful consumed publication row:
   `capability_state = consumed`, non-null `consumed_at`, non-null
   `result_digest`, non-null `revision_id`, no compensation revision, and no
   failure reason.
4. Load the linked `sot_artifact_revisions` row by `revision_id` and require its
   entry id, operation, capability hash, and bridge id to match the publication
   row and aggregate registry entry.
5. Require the publication row's `content_digest` to equal the staged Git-index
   blob bytes for that exact path. Worktree-only bytes are not sufficient.
6. Clear that one staged bridge path only. A capability for one version must
   never authorize another version or another aggregate entry.

For non-bridge registered artifacts, preserve the existing
`sot_registry_observation_capabilities` and transaction-journal behavior
unchanged. Do not add a blanket `bridge/**` exemption and do not treat mere
registry membership, a status token, or an unlinked capability row as
authorization.

## Implementation Plan

1. Extract a small helper in
   `scripts/check_protected_commit_authorization.py` that evaluates exact
   bridge-publication evidence for one staged path and returns a boolean plus a
   precise failure reason.
2. Route aggregate bridge-publication revisions through that helper before the
   ordinary observation-capability predicate.
3. Use the existing index snapshot to hash or read the staged blob. Do not read
   the working-tree file as commit authority.
4. Preserve the existing observation and journal predicates for every other
   registered artifact.
5. Improve the emitted finding enough to distinguish missing publication
   capability, non-consumed/compensated capability, linkage mismatch, and staged
   digest mismatch. This is diagnostic precision within the same source file,
   not a new policy surface.
6. Add focused fixtures and one real temporary-repository commit-path regression
   in the existing test module.

## Test Matrix

The focused tests MUST cover:

- one exact consumed bridge-publication capability clears its matching staged
  bridge file;
- twelve separately published paths under one aggregate entry all clear in one
  terminal include set when each has exact consumed evidence;
- the newest aggregate revision cannot authorize a different predecessor path;
- missing, minted, expired, compensated, or failed capability rows fail closed;
- wrong `target_path`, wrong `aggregate_entry_id`, wrong `capability_hash`, wrong
  `revision_id`, wrong bridge id, and staged-content digest mismatch fail closed;
- a worktree file differing from the index does not change the staged-digest
  decision;
- ordinary observation-capability and journal-backed registered-artifact tests
  remain unchanged and pass;
- a temporary Git repository can stage a synthetic numbered bridge chain and
  pass the protected-commit checker through the same path used by a VERIFIED
  finalizer.

## Acceptance Criteria

1. A canonical terminal bridge transaction with exact consumed publication
   evidence can commit registered `bridge/*.md` files without `--no-verify`.
2. Every staged bridge path is bound to its own publication capability and
   staged content digest; no aggregate-wide or newest-revision authorization
   shortcut exists.
3. Compensated attempts such as the two failed WI-5441 v012 rows cannot clear a
   future commit.
4. Existing observation-capability and transaction-journal clearance behavior
   is byte-for-byte or behaviorally unchanged for non-bridge registered
   artifacts.
5. The focused test module passes, including the multi-predecessor and real Git
   commit-path regression.
6. `python -m py_compile scripts/check_protected_commit_authorization.py` passes.
7. `ruff check` and `ruff format --check` pass for both target files.
8. No database schema, registry declaration, specification, packet, hook,
   dispatcher, bridge writer, finalizer, migration, WI-5640 Stage B, source
   retention, release, or deployment path changes.
9. The implementation report lists only the two declared target paths. Terminal
   finalization may additionally include this thread's numbered bridge chain and
   independently authored verdict through the governed writer.

## Specification Links

- `GOV-PLATFORM-SOT-REGISTRY-001` v3 - the canonical registry and its governed
  evidence are authoritative for registered artifacts.
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` v2 - registered identity
  operations remain governed; content-only liveness is not converted into a
  blanket commit exemption.
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` v4 - aggregate coverage and exact-path
  evidence must retain distinct semantics.
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` v3 - no projection or schema change is
  introduced by this adapter repair.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - numbered bridge publication and independent
  terminal verdict authority remain intact.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation remains bound
  to this GO, claim, authorization packet, and exact two-file target set.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the test matrix derives
  directly from the typed capability and exact-path requirements above.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal names
  the concrete specifications governing every declared implementation surface.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the defect, proposal, implementation,
  review, and terminal evidence remain explicit governed lifecycle artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the repair preserves durable bridge,
  test, and advisory evidence rather than relying on session-only conclusions.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the LO advisory is converted into this
  implementation proposal before any protected source mutation.

## Specification-Derived Verification Plan

| Requirement | Executable evidence | Expected result |
| --- | --- | --- |
| Exact publication table | Focused fixture with an observation-table decoy and a valid bridge-publication row | Valid publication row clears; decoy is ignored |
| Per-path aggregate binding | Twelve-path synthetic chain under `bridge-versioned-files` | Each path binds to its own capability; all clear together |
| Staged-byte authority | Index/worktree divergence fixture | Index digest controls the result |
| Compensation rejection | Consumed row paired with compensation/failure metadata | Fail closed with precise reason |
| Non-bridge non-regression | Existing observation and journal fixture families | Same pass/fail outcomes as baseline |
| Real commit path | Temporary Git repository invoking the protected-commit checker | Commit succeeds without hook bypass |

## Cross-Thread Coordination

1. `gtkb-wi5441-owner-liveness-spec-amendments-011.md` is independently verified
   in full. Its ready terminal body remains at
   `.gtkb-state/propose-drafts/wi5441-012-verdict-body.md`. Do not re-run or edit
   the six specifications.
2. After this repair is implemented and its focused tests pass, re-attempt that
   child v012 terminal finalization through the canonical writer. Do not use a
   commit-hook bypass.
3. Only after the child reaches terminal VERIFIED may
   `gtkb-wi5441-global-registry-membership-reconciliation` v007 replace its
   terminal-evidence placeholder and be filed for review.
4. WI-5640 Stage A remains terminal VERIFIED at v4-020. Stage B stays paused
   until the parent WI-5441 reconciliation is GO, implemented, and independently
   verified.
5. All 90 obsolete migration sources remain present. This repair authorizes no
   move, rename, deletion, or reference rewrite.
6. The dispatcher remains disabled and MUST NOT be activated.

## Risks And Rollback

The primary risk is over-broad aggregate authorization. The exact target,
aggregate, linked-revision, capability-state, and staged-digest checks prevent
one publication from authorizing sibling versions.

The secondary risk is changing ordinary registered-artifact behavior. Keeping
the existing observation and journal predicates untouched and running their
current fixtures bounds that risk.

Rollback is the ordinary Git rollback of these two files before terminal
verification. No schema or live MemBase migration is involved. Failed bridge
publication attempts continue to use the existing compensation path.

## Prior Deliberations

- `bridge/gtkb-lo-tooling-defect-advisory-007.md` - controlling causal evidence,
  two-table mismatch, successful rollback proof, and recommended Prime action.
- `bridge/gtkb-lo-tooling-defect-advisory-001.md` through
  `bridge/gtkb-lo-tooling-defect-advisory-006.md` - prior finalization hypotheses
  and corrections; retained as historical evidence, not reused as the causal
  basis for this repair.
- `bridge/gtkb-wi5441-owner-liveness-spec-amendments-011.md` - correct,
  independently verified report awaiting terminal publication.
- `bridge/gtkb-wi5441-global-registry-membership-reconciliation-006.md` - parent
  NO-GO whose two-file target scope already includes this checker and test.
- `DELIB-20260727-WI5441-PLATFORM-WIDE-CONTENT-EDIT-LIVENESS` - owner liveness
  requirement; not cited as commit-finalization or waiver authority.

## Owner Decisions / Input

None required. This proposal selects the existing typed capability route and
repairs its adapter. It does not introduce a new governance choice or request a
waiver.

## Requested Loyal Opposition Action

Verify the two-table diagnosis and the aggregate predecessor-chain consequence.
File GO only if the exact-path consumed-capability design can clear a canonical
multi-file terminal transaction without exempting `bridge/**`, trusting
worktree-only bytes, or changing non-bridge registry behavior.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
