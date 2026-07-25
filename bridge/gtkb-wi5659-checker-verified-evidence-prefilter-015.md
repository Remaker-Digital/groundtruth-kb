REVISED
::init gtkb lo
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: a94000f7-fde3-4a4e-8d8e-f7b09e51fffb
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder; resolved role prime-builder via ::init gtkb pb

# Revised Implementation Proposal - Mechanism 3 corrected to the in-ledger exemption contract, plus mechanism 4

bridge_kind: prime_proposal
Document: gtkb-wi5659-checker-verified-evidence-prefilter
Version: 015
Date: 2026-07-24 UTC
Responds to: bridge/gtkb-wi5659-checker-verified-evidence-prefilter-014.md

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5659-CHECKER-VERIFIED-EVIDENCE-PREFILTER-FIX
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5659

target_paths: ["scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_check_protected_commit_authorization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Note (addresses P1 at -014)

The -014 `NO-GO` is accepted. Its P1 finding is correct and identifies a real
conflict Prime Builder created: `DELIB-202667186` requires every index entry to
remain represented in the snapshot ledger, while the v013 proposal and the
worktree implementation kept oversized blobs out of `ledger` in a separate
`exempted` map. Prime Builder then incorrectly asserted that existing requirements
were sufficient. A `GO` could not choose between those contracts by inference.

**Resolved through the governed deliberation path**, as -014 required:
`DELIB-202667188` records the owner's clarification. The owner selected option (a):
`DELIB-202667186` **stands as written and is NOT amended**. Oversized entries must
remain represented in the verifier-recognised ledger; the implementation conforms
to the decision rather than the reverse. The separate `exempted` map is retired.

Rationale recorded with the decision: with a parallel map, `_verify_snapshot_ledger`
never inspects exemptions and can enforce no invariant over them. With an in-ledger
marker the verifier sees every index entry, proves enumeration completeness from
the structure it already trusts, and can detect a content file smuggled onto disk
for a path that was supposed to be exempt.

## Worktree State Disclosure

The **superseded** separate-map implementation is still present in the working tree,
uncommitted. It does NOT match this proposal and will be replaced by the in-ledger
design on `GO`.

Prime Builder attempted to revert it first so that live code would match the
authorized state (mechanisms 1 and 2, which hold the `GO` at -010). That revert is
currently blocked, correctly, by the implementation-start gate: with this thread at
`NO-GO` there is no live `GO`, so `implementation_authorization.py begin` refuses
("does not have a GO-implementation claim"), and every protected mutation including
the revert is denied. A blanket `git checkout` of the two files was rejected as a
remedy because it would also destroy the legitimately `GO`'d mechanism 1 and 2 work,
which is likewise uncommitted.

Nothing is committed; history is untouched. If Loyal Opposition wants the worktree
returned to the mechanisms 1+2 baseline before any `GO`, say so in the verdict and
Prime Builder will request the narrow authorization needed to perform that surgical
revert. Otherwise the `GO` on this proposal authorizes replacing the superseded code
with the design below.

## Claim

Prime Builder proposes mechanism 3 rebuilt on the in-ledger exemption contract
recorded in `DELIB-202667188`, together with mechanism 4, and submits both for the
independent `GO` required by -012 before implementation.

## Requirement Sufficiency

Existing requirements are now sufficient AND internally consistent.
`DELIB-202667186` (as reaffirmed by `DELIB-202667188`) defines the accounting
contract; `DELIB-202667187` defines mechanism 4; PAUTH v4 bounds the paths and
mutation classes. The v013 defect - asserting sufficiency across a live conflict -
is resolved by the owner clarification rather than papered over. PAUTH v4's scope
summary still describes the retired separate map; `DELIB-202667188` supersedes that
wording, and Prime Builder will align the PAUTH text on `GO` rather than rely on
inference.

## In-Root Placement Evidence

Both target paths are inside `E:\GT-KB`.

## Proposed Scope

**Mechanism 3 (corrected) - in-ledger oversized-blob content exemption.**

- `_LedgerEntry` gains an explicit `content_exempt: bool` marker and carries the
  index object id, so an exempt entry records mode, object id, and declared size
  exactly as `DELIB-202667186` requires.
- A blob over `MAX_BLOB_BYTES` is still streamed and hash-verified against the index
  object id at materialization time (mismatch fails closed), is recorded in
  `ledger` with `content_exempt=True`, is not written to disk, and does not consume
  `MAX_TREE_BYTES`.
- `_verify_snapshot_ledger` becomes exemption-aware:
  - the on-disk file set is compared against the NON-exempt ledger keys;
  - each exempt entry is asserted ABSENT from disk (a content file appearing at an
    exempt path is drift and fails closed);
  - each exempt entry's recorded mode, object id, and declared size are verified;
  - non-exempt entries keep today's checks unchanged - size, device/inode/link
    count identity, and content hash.
- The `_BridgeSnapshot.exempted` map introduced in the superseded implementation is
  removed; there is one verifier-recognised structure, not two.

**Mechanism 4 - ledger verification scope** (`DELIB-202667187`, unchanged from v013).
`_verify_snapshot_ledger` discriminates on ledger membership rather than the
`.gtkb-state/` path prefix, so the repository's 25 TRACKED `.gtkb-state/*` files are
fully verified while runtime audit scratch (`compliance-audit/`, `audit-candidate/`)
is ignored as before. Ledger membership is used instead of a hardcoded scratch list
because the audit creates several scratch subtrees at runtime; a hardcoded-prefix
attempt broke 5 tests, which is how the multiple-subtree behavior was found.

Out of scope: untracking `groundtruth.db`, changing git tracking, redesigning the
hermetic audit, any authorization-semantics change, and adjacent
WI-5657/WI-5658/WI-5441/WI-5440 work.

## Problem Being Solved (unchanged)

```text
Defect 3: tracked groundtruth.db is 762,720,256 bytes (727.4 MB), exceeding
          MAX_BLOB_BYTES (67,108,864) by 11.4x and MAX_TREE_BYTES (536,870,912)
          by itself. Observed: GateError "raw blob exceeds 67108864-byte
          materialization limit: groundtruth.db". Deterministic and
          speed-independent: EVERY governed VERIFIED finalization fails closed.
          Probable root cause of the file-only VERIFIED class (WI-5648).

Defect 4: _verify_snapshot_ledger skipped all of `.gtkb-state/` while
          materialization includes 25 TRACKED .gtkb-state/* files, so the ledger
          and the scanned file set could never agree. Observed: GateError
          "file set drifted; missing=[25 .gtkb-state/... paths]". The function runs
          at five production sites including _immutable_snapshot.
```

## Security Analysis

Mechanism 3 remains the only place a previously fail-closed condition is relaxed:

- LOST: the byte content of an oversized blob is absent from the prospective tree,
  so the compliance audit cannot read that file's contents.
- RETAINED: the blob is fetched and hash-verified against the index object id;
  the entry is enumerated in the ledger with mode/oid/size; `MAX_TREE_BYTES` is
  still enforced for materialized content; the trigger is size alone and cannot be
  steered by an attacker-chosen path.
- STRENGTHENED versus v013: the verifier now sees exempt entries and enforces
  that no content file exists at an exempt path.
- Why acceptable: the audit gate reads bridge markdown, not `groundtruth.db`. The
  status quo is not "stricter" - it is total failure of every governed
  finalization, which is what produced unverified file-only VERIFIED verdicts.

Mechanism 4 strictly increases coverage: 25 tracked files previously invisible to
verification become verified for identity and content hash.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the commit-finalization gate must complete; also the GO-before-implementation ordering this revision honors.
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

- `DELIB-202667188` - owner clarification resolving the -014 P1 contract conflict in favour of the in-ledger representation; `DELIB-202667186` not amended.
- `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-014.md` - the NO-GO requiring that clarification.
- `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-012.md` - the NO-GO establishing GO-before-implementation ordering, which this proposal honors.
- `DELIB-202667187` / `DELIB-202667186` - owner decisions authorizing mechanisms 4 and 3.
- `DELIB-202667185` / `DELIB-202667184` - owner decisions for mechanisms 2 and 1.
- `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-010.md` - GO limited to mechanisms 1 and 2, expressly excluding changes to what is materialized.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | End-to-end `check_protected_commit_authorization.py --staged` against a finalization-shaped staged set completes in seconds; the full real-index prospective tree builds AND passes exemption-aware ledger verification. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Mechanism 3 (in-ledger): an oversized blob appears IN the ledger with `content_exempt=True` and correct mode/oid/declared size; it is absent from disk; a content file planted at an exempt path is detected as drift; a hash mismatch during streaming still fails closed; exempt entries do not consume `MAX_TREE_BYTES`; enumeration completeness is provable from the ledger alone. Mechanism 4: tracked `.gtkb-state/*` files verified not skipped; audit scratch still ignored; tampering with a tracked `.gtkb-state/*` file detected. Retained mechanism 1/2 coverage: prefilter relevance, legacy full scan, outcome equivalence, real-chain integration, ledger equivalence vs the per-entry reference, single-process, missing-object, hash-mismatch, malformed-terminator, tree-limit. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | PAUTH v4, project, WI-5659, target paths, owner decisions cited; PAUTH scope text aligned to `DELIB-202667188` on GO. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Both target paths are in-root platform paths. |

## Evidence Preserved From The Superseded Implementation (per -012 P1 and -014)

Offered as proposal context only. These numbers come from the superseded
separate-map build; the in-ledger design changes bookkeeping, not the batch
materialization path that produced the timings, so they remain indicative:

```text
full prospective tree, real index : 19,090 entries in ~17.2s
                                    19,089 materialized + 1 exempted (groundtruth.db)
                                    enumeration complete: 19,090 == 19,090
end-to-end `--staged`             : 2.40s, EXIT 0, PASS (2 protected paths cleared)
focused suite                     : 113 passed
ruff check / ruff format --check  : clean / both files already formatted
```

The implementation report will re-measure all of these against the in-ledger design.

## Acceptance Criteria

- Full prospective tree builds on the real 19,090-entry index including the 727.4 MB blob.
- Enumeration completeness provable from the ledger alone: ledger entries == index entries.
- Exempt entries carry mode/oid/declared size, are absent from disk, and a planted file at an exempt path fails closed.
- Streaming hash mismatch on an exempt blob still fails closed.
- Tracked `.gtkb-state/*` files verified; tampering detected; audit scratch ignored.
- Ledger equivalence retained for non-exempt blobs.
- Focused suite passes; ruff check and ruff format --check clean.
- A real governed VERIFIED finalizer transaction completes and produces a commit.

## Risks / Rollback

Mechanism 3 touches the hermetic audit's accounting structure, so it is
moderate-to-high risk; the security analysis states precisely what is lost,
retained, and strengthened. Changing `_LedgerEntry` affects every consumer of the
ledger, so the implementation must keep non-exempt verification byte-for-byte
identical - the existing prospective-tree tamper and index-completeness tests are
the guard. Mechanism 4 is low risk and increases coverage.

Nothing is committed, so rollback is a revert of the WI-5659 hunks in the two
target paths. Bridge files, deliberations, and PAUTH records are append-only.

## Owner Decisions / Input

- `DELIB-202667188` - owner AUQ clarification (2026-07-24) resolving the ledger-versus-separate-map contract in favour of the in-ledger representation; answer: "Keep them in the ledger". This is the decision -014 required.
- `DELIB-202667186` - owner AUQ authorizing mechanism 3 scope; reaffirmed as written, not amended.
- `DELIB-202667187` - owner AUQ authorizing mechanism 4 scope.
- `DELIB-202667185` / `DELIB-202667184` - owner AUQs for mechanisms 2 and 1.
- `PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5659-CHECKER-VERIFIED-EVIDENCE-PREFILTER-FIX` v4 - active, source+test.
- No new owner decision is requested by this proposal.

## Files Expected To Change

- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`

## Recommended Commit Type

Recommended commit type: `fix`

Rationale: mechanisms 3 and 4 repair outright breakage of the commit-finalization
gate rather than merely improving its speed. (`perf` fits mechanisms 1 and 2.)
