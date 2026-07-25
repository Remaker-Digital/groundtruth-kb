REVISED
::init gtkb lo
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: fb16e5ad-1c90-4810-ad72-a0b4d5832133
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder; resolved role prime-builder via ::init gtkb pb

# Implementation Proposal - Corrected in-ledger mechanism 3 + mechanism 4, on the clean baseline; its VERIFIED is the single fold commit

bridge_kind: prime_proposal
Document: gtkb-wi5659-checker-verified-evidence-prefilter
Version: 020
Date: 2026-07-24 UTC
Responds to: bridge/gtkb-wi5659-checker-verified-evidence-prefilter-019.md

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5659-CHECKER-VERIFIED-EVIDENCE-PREFILTER-FIX
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5659

target_paths: ["scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_check_protected_commit_authorization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Where This Sits In The Sequence

This is the corrected in-ledger mechanism-3/4 design, now reviewable on a clean
baseline. Preconditions established:

- The superseded separate-map implementation was reverted under the `-018` `GO`;
  the reversion report at `-019` documents the worktree is the clean mechanisms-1/2
  baseline (106 tests, ruff clean, mechanism-3/4 symbols absent).
- `DELIB-202667190` folds the reversion's deferred commit into THIS proposal's
  `VERIFIED`. **This proposal's `VERIFIED` is the single governed commit** and will
  contain mechanisms 1 + 2 + corrected 3 + 4. It succeeds where the reverted
  baseline cannot, because corrected mechanism 3 keeps `groundtruth.db` in the
  ledger as a content-exempt entry so the finalizer no longer fails on it.

This proposal supersedes the corrected-design proposal at `-015`, which was
`NO-GO`'d at `-016` solely because the baseline was not yet clean. The contract
resolved at `-014`/`DELIB-202667188` (in-ledger representation, not a separate map)
is unchanged.

## Claim

Prime Builder proposes mechanism 3 rebuilt on the in-ledger exemption contract of
`DELIB-202667186`/`DELIB-202667188`, plus mechanism 4, implemented on the clean
baseline established by the reversion, with a single governed commit at `VERIFIED`.

## Requirement Sufficiency

Existing requirements are sufficient and internally consistent. `DELIB-202667186`
(as reaffirmed by `DELIB-202667188`) defines the in-ledger accounting contract;
`DELIB-202667187` defines mechanism 4; `DELIB-202667190` defines the single-commit
fold; PAUTH v4 bounds paths and mutation classes. No new owner decision is
requested.

## In-Root Placement Evidence

Both target paths are inside `E:\GT-KB`.

## Problem Being Solved

```text
Defect 3: tracked groundtruth.db is 762,720,256 bytes (727.4 MB), exceeding
          MAX_BLOB_BYTES (67,108,864) by 11.4x and MAX_TREE_BYTES (536,870,912)
          by itself. The transaction-candidate branch materializes an
          index-complete prospective tree; _blob_ledger_entry raises
          "raw blob exceeds ...-byte materialization limit". Deterministic and
          speed-independent: EVERY governed VERIFIED finalization fails closed.
          Probable root cause of the file-only VERIFIED class (WI-5648).

Defect 4: _verify_snapshot_ledger skips all of `.gtkb-state/` while
          materialization includes 25 TRACKED .gtkb-state/* files, so the ledger
          and the scanned file set can never agree; false
          "prospective audit tree file set drifted". Runs at five production sites
          including _immutable_snapshot.
```

## Proposed Scope

**Mechanism 3 (in-ledger) - oversized-blob content-copy exemption.**

- `_LedgerEntry` gains an explicit `content_exempt: bool` marker and carries the
  index object id, so an exempt entry records mode, object id, and declared size
  inside the ledger structure exactly as `DELIB-202667186` requires (no separate
  `exempted` map).
- A blob over `MAX_BLOB_BYTES` is still streamed and hash-verified against the
  index object id (mismatch fails closed), is recorded in `ledger` with
  `content_exempt=True`, is not written to disk, and does not consume
  `MAX_TREE_BYTES`.
- `_verify_snapshot_ledger` becomes exemption-aware:
  - the on-disk file set is compared against the NON-exempt ledger keys;
  - each exempt entry is asserted ABSENT from disk (a content file at an exempt
    path is drift and fails closed);
  - each exempt entry's recorded mode, object id, and declared size are verified;
  - non-exempt entries keep today's checks unchanged - size, device/inode/link
    identity, and content hash.

**Mechanism 4 - ledger verification scope.** `_verify_snapshot_ledger`
discriminates on LEDGER MEMBERSHIP rather than the `.gtkb-state/` path prefix, so
the 25 tracked `.gtkb-state/*` files are fully verified while runtime audit scratch
(`compliance-audit/`, `audit-candidate/`, created at runtime) is ignored as before.
Ledger membership is the discriminator, not a hardcoded scratch list, because a
hardcoded-prefix attempt broke 5 tests when the audit created a second scratch
subtree.

Out of scope: untracking `groundtruth.db`, changing git tracking, redesigning the
hermetic audit, any authorization-semantics change, and adjacent
WI-5657/WI-5658/WI-5441/WI-5440 work.

## Security Analysis

Mechanism 3 is the only place a previously fail-closed condition is relaxed:

- LOST: an oversized blob's byte content is absent from the prospective tree, so
  the compliance audit cannot read that file's contents.
- RETAINED: the blob is fetched and hash-verified against the index object id; the
  entry is enumerated in the ledger with mode/oid/size; `MAX_TREE_BYTES` is enforced
  for materialized content; the trigger is size alone and cannot be steered by an
  attacker-chosen path.
- STRENGTHENED over the retired separate-map approach: the verifier now SEES exempt
  entries in the ledger and enforces that no content file exists at an exempt path.
- Why acceptable: the audit gate reads bridge markdown, not `groundtruth.db`. The
  status quo is total failure of every governed finalization, which produced the
  file-only VERIFIED class.

Mechanism 4 strictly INCREASES coverage: 25 tracked files previously invisible to
verification become verified for identity and content hash.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
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

- `DELIB-202667190` - the fold decision: this proposal's `VERIFIED` is the single commit.
- `DELIB-202667188` - the in-ledger contract this design implements; reaffirms `DELIB-202667186` unamended.
- `DELIB-202667187` / `DELIB-202667186` - mechanism 4 and mechanism 3 scope.
- `DELIB-202667185` / `DELIB-202667184` - mechanisms 2 and 1, preserved.
- `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-019.md` - the reversion report establishing the clean baseline.
- `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-016.md` and `-014.md` - the baseline and contract findings this proposal satisfies.
- `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-010.md` and `-004.md` - the mechanism-1/2 `GO` verdicts.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | The single governed commit at this proposal's `VERIFIED` succeeds: the real `check_protected_commit_authorization.py --staged` finalizer path completes and produces a commit, proving the finalizer no longer fails on `groundtruth.db`. Full real-index prospective tree builds and passes exemption-aware ledger verification. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Mechanism 3 (in-ledger): oversized blob appears IN the ledger with `content_exempt=True` and correct mode/oid/declared size; absent from disk; a content file planted at an exempt path is detected as drift; streaming hash mismatch fails closed; exempt entries do not consume `MAX_TREE_BYTES`; enumeration completeness provable from the ledger alone. Mechanism 4: tracked `.gtkb-state/*` files verified not skipped; audit scratch still ignored; tampering with a tracked `.gtkb-state/*` file detected. Retained mechanism 1/2 coverage. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | PAUTH v4, project, WI-5659, target paths, owner-decision chain cited. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Both target paths are in-root platform paths. |

## Acceptance Criteria

- `_LedgerEntry` carries `content_exempt` and object id; exempt entries appear in the ledger, not a separate map.
- Full prospective tree builds on the real 19,090-entry index including the 727.4 MB blob; enumeration completeness provable from the ledger alone (ledger entries == index entries).
- Exempt entries are absent from disk; a planted file at an exempt path fails closed; streaming hash mismatch fails closed.
- Tracked `.gtkb-state/*` files verified; tampering detected; audit scratch ignored.
- Ledger equivalence retained for non-exempt blobs.
- Focused suite passes; ruff check and ruff format --check clean.
- The single governed VERIFIED commit completes and produces a real commit.

## Risks / Rollback

Mechanism 3 touches the hermetic audit's accounting structure (moderate-to-high
risk); the security analysis states what is lost, retained, and strengthened.
Changing `_LedgerEntry` affects every ledger consumer, so non-exempt verification
must stay byte-for-byte identical - the existing prospective-tree tamper and
index-completeness tests are the guard. Mechanism 4 is low risk and increases
coverage.

Rollback before commit is a revert of the WI-5659 hunks in the two target paths.
The single commit at `VERIFIED` is revertible as one unit. Bridge files,
deliberations, and PAUTH records are append-only.

## Owner Decisions / Input

- `DELIB-202667190` - owner AUQ folding the reversion into this proposal's single commit.
- `DELIB-202667188` - owner AUQ resolving the ledger contract to the in-ledger representation ("Keep them in the ledger"); reaffirms `DELIB-202667186` unamended.
- `DELIB-202667187` - owner AUQ authorizing mechanism 4 scope.
- `DELIB-202667186` - owner AUQ authorizing mechanism 3 scope.
- `DELIB-202667185` / `DELIB-202667184` - owner AUQs for mechanisms 2 and 1.
- `PAUTH-...-WI-5659-CHECKER-VERIFIED-EVIDENCE-PREFILTER-FIX` v4 - active, source+test.
- No new owner decision is requested by this proposal.

## Files Expected To Change

- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`

## Recommended Commit Type

Recommended commit type: `fix`

Rationale: mechanisms 3 and 4 repair outright breakage of the commit-finalization
gate; the single commit also carries the GO'd mechanisms 1 (`perf`) and 2 (`perf`).
`fix` best describes the net effect (restoring governed finalization).
