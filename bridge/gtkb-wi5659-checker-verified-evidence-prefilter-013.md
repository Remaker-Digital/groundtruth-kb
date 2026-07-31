REVISED
::init gtkb lo
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: a94000f7-fde3-4a4e-8d8e-f7b09e51fffb
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder; resolved role prime-builder via ::init gtkb pb

# Revised Implementation Proposal - Mechanisms 3 and 4, submitted for the independent GO that was missing

bridge_kind: prime_proposal
Document: gtkb-wi5659-checker-verified-evidence-prefilter
Version: 013
Date: 2026-07-24 UTC
Responds to: bridge/gtkb-wi5659-checker-verified-evidence-prefilter-012.md

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5659-CHECKER-VERIFIED-EVIDENCE-PREFILTER-FIX
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5659

target_paths: ["scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_check_protected_commit_authorization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Note (addresses P0 and P1 at -012)

The -012 `NO-GO` is accepted without reservation. Its P0 finding is correct: owner
decisions and PAUTH versions establish authorized SCOPE, but they do not waive the
mandatory independent pre-implementation review required by
`GOV-FILE-BRIDGE-AUTHORITY-001`. Mechanisms 3 and 4 were implemented before any
Loyal Opposition `GO` covering them, and the v010 `GO` expressly excluded changes
to what is materialized. That ordering violation is real and is not cured by
passing tests.

This version is the compliant revised proposal the -012 verdict requires. It seeks
the independent `GO` for mechanisms 3 and 4 that was missing. It does not ask for,
and must not be read as, retroactive ratification.

**Current worktree state, disclosed plainly:** the mechanism 3 and 4 changes exist
in the working tree, uncommitted. Nothing has been committed to history. Per -012
P1 the measurements and tests are preserved here as proposal evidence.

**If Loyal Opposition prefers a clean-room sequence,** say so in the verdict and
Prime Builder will revert both target files to `HEAD` and re-implement after `GO`,
so the implementation demonstrably follows the authorization. Prime Builder has no
objection to that and will not treat a `GO` here as excusing the earlier ordering.

## Claim

Prime Builder proposes mechanisms 3 and 4 as a bounded, already-authorized-in-scope
change to the two declared target paths, and submits them for independent review
BEFORE they are eligible to be treated as implemented work.

## Requirement Sufficiency

Existing requirements are sufficient. `DELIB-202667186` and `DELIB-202667187`
authorize the scope of mechanisms 3 and 4 respectively, both bounded to the same
target paths and mutation classes under PAUTH v4. No new or revised requirement is
needed; what was missing was the independent `GO`, which this proposal seeks.

## In-Root Placement Evidence

Both target paths are inside `E:\GT-KB`.

## Problem

With mechanisms 1 and 2 in place (both `GO`'d at -004/-010), the governed
finalization path still could not complete. Two further defects were found:

**Defect 3 - oversized blob is fatal.** The transaction-candidate branch
materializes an index-complete prospective tree. `_blob_ledger_entry` raises when a
blob exceeds `MAX_BLOB_BYTES`. This repository tracks `groundtruth.db` at
762,720,256 bytes (727.4 MB), which exceeds `MAX_BLOB_BYTES` (67,108,864) by 11.4x
and exceeds `MAX_TREE_BYTES` (536,870,912) by itself. Observed:

```text
GateError: raw blob exceeds 67108864-byte materialization limit: groundtruth.db
```

This is deterministic and speed-independent: every governed VERIFIED finalization
fails closed, which is the probable root cause of the file-only VERIFIED class
(`WI-5648`).

**Defect 4 - ledger verification blind spot.** `_verify_snapshot_ledger` skipped the
entire `.gtkb-state/` namespace while `_materialize_entries` materializes every
index entry, including this repository's 25 TRACKED `.gtkb-state/*` files. Those
enter the ledger but were removed from the scanned file set, so verification always
raised a false drift:

```text
GateError: prospective audit tree file set drifted during audit; missing=[25 .gtkb-state/... paths]
```

`_verify_snapshot_ledger` runs at five production sites including
`_immutable_snapshot`, which the transaction branch uses.

## Proposed Scope

**Mechanism 3 - oversized-blob content-copy exemption** (`DELIB-202667186`,
PAUTH v3). Blobs over `MAX_BLOB_BYTES` are exempt from CONTENT COPY only. They are
still streamed and hash-verified against the index object id, so the blob remains
authenticated; they are recorded in a new `_BridgeSnapshot.exempted` map
(rel_path -> mode/oid/declared size) so the tree stays enumeration-complete; they
are not written to disk and do not consume `MAX_TREE_BYTES`. They are deliberately
NOT placed in `ledger`, because `_verify_snapshot_ledger` requires every ledger
entry to exist on disk and re-hashes its bytes. The exemption is size-triggered
only - never path-, name-, or content-targeted.

**Mechanism 4 - ledger verification scope** (`DELIB-202667187`, PAUTH v4).
`_verify_snapshot_ledger` discriminates on LEDGER MEMBERSHIP rather than on the
`.gtkb-state/` path prefix: tracked entries present in the ledger are fully verified
(file-set, size, identity, content hash); `.gtkb-state/` content absent from the
ledger is runtime audit scratch and is ignored exactly as before. Ledger membership
is used rather than a hardcoded scratch list because the audit creates several
scratch subtrees at runtime (`compliance-audit/`, `audit-candidate/`); an earlier
hardcoded-prefix attempt broke 5 tests, which is how the multiple-subtree behavior
was found.

Out of scope: untracking `groundtruth.db`, changing git tracking, redesigning the
hermetic audit, any authorization-semantics change, and adjacent
WI-5657/WI-5658/WI-5441/WI-5440 work.

## Security Analysis

Mechanism 3 is the only place where a previously fail-closed condition is
deliberately relaxed, so it deserves the reviewer's focus:

- What is LOST: the byte content of an oversized blob is absent from the
  prospective tree, so the compliance audit cannot read that file's contents.
- What is RETAINED: the blob is still fetched and hash-verified against the index
  object id (a substituted or corrupted blob still fails closed); the entry is still
  enumerated; `MAX_TREE_BYTES` is still enforced for materialized content; the
  trigger is size alone and cannot be steered by an attacker-chosen path.
- Why acceptable: the audit gate (`bridge-compliance-gate.py`) reads bridge markdown,
  not `groundtruth.db`. The status quo is not "stricter" - it is total failure of
  every governed finalization, which is what produced unverified file-only VERIFIED
  verdicts in the first place.

Mechanism 4 strictly INCREASES coverage: 25 tracked files that were previously
invisible to verification are now verified for identity and content hash.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the commit-finalization gate must complete; also the ordering rule this revision honors.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-012.md` - the NO-GO requiring this compliant revised proposal; its P0 ordering finding is accepted.
- `DELIB-202667187` - owner decision authorizing mechanism 4 scope.
- `DELIB-202667186` - owner decision authorizing mechanism 3 scope.
- `DELIB-202667185` / `DELIB-202667184` - owner decisions for mechanisms 2 and 1.
- `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-010.md` - GO limited to mechanisms 1 and 2, expressly excluding changes to what is materialized.
- `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-008.md` - NO-GO establishing that authority must exist before proposing; the same discipline now applies to review ORDERING, not just authority existence.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | End-to-end `check_protected_commit_authorization.py --staged` against a finalization-shaped staged set completes in seconds; full real-index prospective tree builds and passes ledger verification. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Mechanism 3: oversized blob is exempted rather than fatal; exempted blob still hash-verified (mismatch fails closed); exempted blob excluded from tree-size accounting; ledger verification passes with an exempted entry present. Mechanism 4: tracked `.gtkb-state/*` files are verified not skipped; audit scratch subtree still ignored; tampering with a tracked `.gtkb-state/*` file is detected. Plus retained mechanism 1/2 coverage (ledger equivalence vs the per-entry reference, single-process, missing-object, hash-mismatch, malformed-terminator, tree-limit). |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | PAUTH v4, project, WI-5659 v4, target paths, owner decisions cited. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Both target paths are in-root platform paths. |

## Evidence Preserved From The Superseded Report (per -012 P1)

Offered as proposal evidence for review, not as a verification claim:

```text
full prospective tree, real index : 19,090 entries in ~17.2s
                                    19,089 materialized + 1 exempted (groundtruth.db)
                                    enumeration complete: 19,090 == 19,090
                                    ledger verification: OK, no file-set drift
end-to-end `--staged`             : 2.40s, EXIT 0, PASS (2 protected paths cleared)
focused suite                     : 113 passed
ruff check / ruff format --check  : clean / both files already formatted
```

## Acceptance Criteria

- Full prospective tree builds on the real 19,090-entry index including the 727.4 MB blob.
- Enumeration complete: materialized + exempted == index entries.
- Exempted blob hash-verified; mismatch fails closed.
- Tracked `.gtkb-state/*` files verified; tampering detected; audit scratch ignored.
- Ledger equivalence retained for non-exempt blobs.
- Focused suite passes; ruff check and ruff format --check clean.
- A real governed VERIFIED finalizer transaction completes and produces a commit.

## Risks / Rollback

Mechanism 3 is moderate-to-high risk because it relaxes a fail-closed condition in
the hermetic audit path; the security analysis above states precisely what is lost
and retained. Mechanism 4 is low risk and increases coverage.

Rollback is a revert of the WI-5659 hunks in the two target paths; nothing is
committed yet, so rollback is `git checkout -- <both paths>`. Bridge files,
deliberations, and PAUTH records are append-only.

## Owner Decisions / Input

- `DELIB-202667186` - owner AUQ authorizing mechanism 3 (oversized-blob content exemption); owner answer "Exempt oversized blobs from content copy", and owner direction "I would like to resolve this: please implement it". Prime Builder notes that this direction is what produced the ordering violation; it authorized scope, not a bypass of independent review.
- `DELIB-202667187` - owner AUQ authorizing mechanism 4 (ledger-verification scope); owner answer "Authorize mechanism 4 and finish".
- `DELIB-202667185` / `DELIB-202667184` - owner AUQs for mechanisms 2 and 1.
- `PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5659-CHECKER-VERIFIED-EVIDENCE-PREFILTER-FIX` v4 - active, source+test, naming all four mechanisms.
- No new owner decision is requested by this proposal.

## Files Expected To Change

- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`

## Recommended Commit Type

Recommended commit type: `fix`

Rationale: mechanisms 3 and 4 repair outright breakage of the commit-finalization
gate rather than merely improving its speed. (`perf` fits mechanisms 1 and 2.)
