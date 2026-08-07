REVISED
::init gtkb pb
::open build
author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: c3245ca7-dd29-4c17-92f0-230d816c318c
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb; build activity envelope
author_metadata_source: session runtime, harness-provided; the per-session envelope model fields are unpopulated for this session and are not the source, per WI-6000

bridge_kind: prime_proposal
Document: gtkb-wi5825-publication-capability-recovery-receipt-backfill
Version: 017
Date: 2026-08-07 UTC
Responds to: bridge/gtkb-wi5825-publication-capability-recovery-receipt-backfill-016.md

Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HARNESS-TEST-CORRECTIONS
Work Item: WI-5825

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "scripts/gtkb_bridge_writer.py", "groundtruth-kb/tests/test_registry_control_plane.py", "platform_tests/scripts/test_gtkb_bridge_writer.py", "platform_tests/scripts/test_check_protected_commit_authorization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

Recommended commit type: `feat`

# Implementation Proposal (REVISED) — Consolidated Bridge Publication Finalization Lane, Slice 1: Governed Receipt Back-Fill

## Revision Claim

This revision responds to the version-016 `NO-GO` and, under owner decision
`DELIB-20260807011936`, converts this thread into the **consolidated lane** for
the bridge publication finalization deadlock.

Two changes from version 015:

1. **Finding 1 (P1) addressed.** The version-016 `NO-GO` did not fault the
   product. It recorded that atomic finalization failed on a stale
   `packet_hash` computed against the wrong operative head, and that the
   compensating rollback then raised `BRIDGE_PUBLICATION_REPAIR_REQUIRED`. This
   revision re-establishes a live applicability packet against the current
   operative file, and narrows the implementable slice so finalization is
   attempted against a smaller, self-curable change set.
2. **Scope consolidated.** This lane now holds exclusive ownership of the
   contested surfaces and absorbs WI-5869. Its thread was withdrawn at version
   009 with evidence preserved.

## Specification Links

Blocking cross-cutting specifications:

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every governing
  specification constraining this implementation is cited in this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan
  below maps each linked specification to a concrete executed test.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — this revision is an append-only numbered
  version filed through the governed writer under a live work-intent claim; no
  prior version is edited or deleted.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all five declared target paths are
  in-root under `E:\GT-KB` (`groundtruth-kb/src/...`, `scripts/...`,
  `groundtruth-kb/tests/...`, `platform_tests/...`). This slice is platform
  infrastructure only: it creates no application file, relocates nothing into or
  out of `applications/`, and introduces no dependency on any out-of-root path.

Advisory cross-cutting specifications:

- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the WI-5869 subsumption is carried as
  a withdrawal lifecycle transition, not an ad hoc edit.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the consolidation decision and its
  evidence are preserved as durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — traceability preserved across
  decision, plan, withdrawal, and this proposal.

Specifications governing the implemented behavior:

- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — back-fill must bind the exact current
  bytes of the target file at back-fill time, never a cached or assumed digest.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` — a back-filled receipt must record the
  authority that authorized the back-fill, and must not fabricate or infer the
  original author session.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — back-fill is an explicitly
  authorized operation and must not become a route around publication authority.
- `GOV-RELIABILITY-FAST-LANE-001` — the change is additive and target-bounded.

## Prior Deliberations

- `DELIB-20260807011936` — owner decision, given directly in chat 2026-08-07,
  approving this four-part consolidation. It is the authority for this
  revision's scope change.
- `DELIB-202668164` — owner standing concurrency directive: concurrency and
  parallelism failures receive one durable platform-wide fix rather than another
  competing parallel thread, and deadlock is broken by serializing into a single
  lane holding exclusive ownership of the contested surfaces.
- `DELIB-202667525` — precedent for the same operation shape: the owner named a
  controlling continuation and withdrew the overlapping threads.
- Version 016 of this thread — the `NO-GO` this revision answers, which recorded
  substance green at 298 passed and faulted only finalization.

## Owner Decisions / Input

- `DELIB-20260807011936` (`source_type: owner_conversation`,
  `outcome: owner_decision`) records the owner's chat-given approval. Verbatim:
  "I approve the four decisions in the plan: WI-5825 as lane owner; subsuming
  and withdrawing WI-5869 with evidence preserved; WI-5881 staying independent;
  and the lane's scope including a back-fill operation rather than only retrying
  finalization."
- That decision also records the capture channel explicitly: an earlier
  `AskUserQuestion` result reporting approval was contradicted by a system
  notification stating no human input had been received. Nothing was executed on
  the contradicted result; the owner was asked to confirm in chat and did.
- No further owner decision is required for this slice. Implementation authority
  is the list-free whole-project grant
  `PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730` under
  `DELIB-202667731`.

## Requirement Sufficiency

**Existing requirements sufficient.** The governing requirement surface is
already specified by this work item's description (the three linked gaps),
`GOV-FILE-BRIDGE-AUTHORITY-001`, and `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`. No new
or revised requirement is needed before implementation; this slice adds a
capability that those requirements already imply must exist for recovery to be
possible.

## Problem

A bridge file written outside the governed writer acquires no publication
capability row. It remains untracked. `check_protected_commit_authorization`
then denies staging it, so atomic `VERIFIED` cannot complete for any thread
whose chain contains such a file.

The remedy is structurally unavailable today. Two independent create-only gates,
confirmed by direct source inspection:

- `scripts/gtkb_bridge_writer.py` `write_bridge_file` raises
  `BridgeConflictError` when the target exists, and again when the path exists
  in git history.
- `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`
  `mint_bridge_publication_capability` raises `RegistryAuthorizationError`
  ("bridge publication target already exists") when
  `target.exists() or target.is_symlink()`. Its docstring states it mints
  "before one bridge file is created".

Deleting and recreating the file to satisfy the create-only precondition is
barred by the append-only rule that bridge files are never deleted. No API
therefore exists to cure an already-existing unreceipted file.

Measured instance: chain
`gtkb-wi5869-registry-control-plane-lock-acquisition` holds consumed capability
rows for versions 002, 004, 006 and 008 — every Loyal Opposition verdict — and
none for versions 001, 003, 005 and 007 — every Prime Builder authored version —
with all eight untracked in git. The odd/even split isolates the bypass to the
Prime-side authoring path.

Corroborating observation for the LO to weigh: at the time of writing there is
no CLI path that files a Prime-side `WITHDRAWN`, and `write_verdict.py` without
`--finalize-verified` only emits a prepopulated body. Filing this lane's own
WI-5869 withdrawal required calling the governed writer library directly. That
missing-CLI surface is a plausible mechanism for the odd/even split, but it is
offered as a hypothesis for review, not as an established cause.

## Proposed Change — Slice 1

Add a **distinct, narrowly-scoped, explicitly-authorized back-fill operation**
that can mint and consume a publication capability for an already-existing
bridge file, leaving the ordinary publication path unchanged.

Design constraints, all mandatory:

1. **The create-only invariant on the ordinary path is preserved.**
   `mint_bridge_publication_capability` keeps its `target.exists()` refusal
   unchanged. Back-fill is a separate entry point with its own name, its own
   authority check, and its own audit record. Relaxing the existing gate is
   explicitly rejected: `target.exists()` refusal is what makes a receipt mean
   that this exact file was published under this exact authority, and weakening
   it globally would weaken every receipt in the system.
2. **Exact-byte binding.** The back-filled receipt binds the SHA-256 of the
   file's current bytes, read under the same registry lock that guards minting.
   A file whose bytes change between read and record fails closed.
3. **Honest provenance.** The receipt records the back-fill authority and the
   back-filling session, and marks the row as back-filled rather than
   originally published. It must not fabricate or infer the original author
   session. A back-filled receipt is distinguishable from a natively minted one
   in the durable record.
4. **No file mutation.** Back-fill never creates, deletes, rewrites, moves, or
   overwrites any bridge file. It only records a receipt for bytes already on
   disk.
5. **Explicit authorization required.** Back-fill requires a live work-intent
   claim for the document and a cited authorizing decision. It is not reachable
   as an implicit fallback from the ordinary publication path.
6. **Idempotent and fail-closed.** Back-filling a version that already has a
   capability row is refused, not silently overwritten.

Out of scope for this slice, sequenced for later slices of this lane:

- Gap (a): clearing `recovery_required` rows left by
  `BRIDGE_PUBLICATION_REPAIR_REQUIRED` failures.
- Gap (c): durable pending-publication context that survives process exit.
- The WI-5869 substantive change: registry control-plane lock acquisition
  sizing and externalization for real parallel width.

Slicing rationale: gap (b) is the smallest change that unblocks the largest
number of stalled threads, and it is the one that can potentially cure this
lane's own chain, which is the self-repair ordering constraint recorded in the
consolidation plan.

## Specification-Derived Verification Plan

| Specification | Test | Expected result |
|---|---|---|
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | new: back-fill binds the exact current file bytes; a byte change between read and record fails closed | fail-closed on drift |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | new: back-filled row records back-fill authority and session, and is distinguishable from a natively minted row | provenance recorded, not inferred |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | new: back-fill without a live work-intent claim is refused | `RegistryAuthorizationError` |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | new: back-fill creates, deletes, rewrites and overwrites no bridge file; on-disk bytes and mtime unchanged | file untouched |
| create-only invariant (this proposal) | existing + new: `mint_bridge_publication_capability` still refuses an existing target after the change | unchanged refusal |
| idempotence (this proposal) | new: back-filling a version that already holds a capability row is refused | refused, no overwrite |
| regression | `pytest groundtruth-kb/tests/test_registry_control_plane.py platform_tests/scripts/test_gtkb_bridge_writer.py platform_tests/scripts/test_check_protected_commit_authorization.py` | no regressions |
| static | `ruff check` and `ruff format --check` on all changed files | clean |

## Acceptance Criteria

1. An existing, unreceipted, on-disk bridge file can be given a consumed
   publication capability through the new operation, under a live claim and a
   cited authority.
2. `mint_bridge_publication_capability` behavior on the ordinary path is
   byte-for-byte unchanged; its existing tests pass without modification.
3. Back-fill refuses: a missing file, a version that already holds a row, a
   missing claim, and a byte change detected between read and record.
4. A back-filled row is distinguishable from a natively minted row in the
   durable record.
5. No bridge file is created, deleted, rewritten, or overwritten by back-fill.
6. Ruff check and format pass on all changed files; the three named test modules
   pass with no regressions.

## Risk And Rollback

- **Primary risk — authority laundering.** A back-fill operation is, by
  construction, a way to make an unauthorized file look authorized. Mitigations:
  a separate named entry point, mandatory live claim, mandatory cited authority,
  a durable back-filled marker distinguishing it from native minting, and
  refusal to overwrite an existing row. The LO is specifically asked to attack
  this surface during review.
- **Secondary risk — self-repair ordering.** This lane must eventually finalize
  through the machinery it repairs. Mitigation: this slice is deliberately the
  back-fill capability itself, so once landed the lane can cure its own chain if
  needed. This thread's chain is currently 14 of 16 receipted; the two gaps,
  versions 003 and 004, are already committed to git and therefore do not
  require staging at finalization.
- **Rollback.** The change is additive: a new entry point plus tests. Reverting
  the five target paths to their pre-change bytes fully removes the capability;
  no schema migration is proposed in this slice, and no existing row is mutated.

## Scope Disclosure

No dispatcher, daemon, or guard is activated, re-enabled, or reconfigured by
this proposal. All remain intentionally disabled per the owner standing
directive of 2026-08-07. No deployment, release, credential, or external-system
mutation is in scope. No formal GOV/ADR/DCL/SPEC record is mutated.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
