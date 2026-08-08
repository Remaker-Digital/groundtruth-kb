NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fe0e5-4e93-7280-9778-8d6738c9626d
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; harness A; resolved role prime-builder via ::init gtkb pb
author_metadata_source: explicit_interactive_session_metadata

# GT-KB Bridge Implementation Report - gtkb-wi6073-batch-verified-finalization - 003

bridge_kind: implementation_report
Document: gtkb-wi6073-batch-verified-finalization
Version: 003
Responds to: bridge/gtkb-wi6073-batch-verified-finalization-002.md
Controlling GO: `bridge/gtkb-wi6073-batch-verified-finalization-002.md`
Approved proposal: bridge/gtkb-wi6073-batch-verified-finalization-001.md
Project Authorization: PAUTH-PROJECT-GTKB-SESSION-ENVELOPE-WHOLE-PROJECT-20260808
Project: PROJECT-GTKB-SESSION-ENVELOPE
Work Item: WI-6073
Recommended commit type: feat:

## Implementation Claim

Implemented the governed WI-6073 batch-finalization operation and its narrow
protected-commit support in the three approved target paths. The implementation
is fail-closed and per-thread: a read-only plan enumerates direct dirty terminal
`VERIFIED` candidates, emits a stable plan digest and named skip reasons, and an
explicit apply requires that exact live digest plus the approved owner decision
and Project Authorization.

The live execution outcome is also reported explicitly: the final dry-run found
17 direct candidates, **0 ready, 17 skipped**, so no apply and no history change
was made. Twelve candidates have a newest publication capability that is not
`consumed`; four lack exact publication capability evidence; one has publication
content drift. Several also have malformed chains, invalid historical packets,
missing finalization evidence, or real-index ownership. Under the controlling
GO's requirement that capability-state and freshness checks remain unweakened,
and the proposal's prohibition on `groundtruth.db` writes, those are required
refusals. The owner's requested outcome -- commit all accumulated VERIFIED work
-- therefore remains unmet even though the governed operation is implemented.

### Delivered behavior

1. `scripts/batch_finalize_verified.py` provides explicit `plan` and `apply`
   modes. Apply is bound to the exact plan digest, owner decision, PAUTH, active
   WI-6073 implementation packet/claim, resolved caller session, candidate
   bytes, declared and selected paths, HEAD OID, and symbolic HEAD ref.
2. Each commit uses a disposable index, the canonical in-root pre-commit hook
   (local `core.hooksPath` cannot redirect it), `commit-tree`, and compare-and-
   swap update of the exact symbolic ref. Exact committed paths and parent are
   verified. Unrelated real-index path names and blob entries are preserved.
3. The runtime authorization manifest is root-contained, ancestor-link checked,
   self-hashed, candidate-plan-hashed, nonce-bearing, and live for at most five
   minutes (the writer uses two minutes). The gate revalidates active foreign
   claims over the exact staged set.
4. Candidate path selection uses the implementation report's exact `Files
   Changed` rows plus the dirty bridge chain. A path that was merely authorized
   but reported unchanged is not captured if another thread later dirties it.
   Live WI-6055 demonstrates this: its report says
   `platform_tests/scripts/test_session_envelope_runtime.py` was not modified,
   and the planner excludes that currently-dirty foreign path.
5. `scripts/check_protected_commit_authorization.py` changes manifest equality
   to the approved one-way subset rule: declared-but-unchanged paths pass, while
   every undeclared staged path still fails. The exactly-one-VERIFIED rule and
   all ordinary lifecycle, independence, publication, freshness, and packet
   checks remain.
6. PAUTH substitution is limited to an ordinary validation error whose exact
   class is immutable snapshot drift (`drifted since packet creation`) and only
   when the candidate and WI-6073 carrier share the same PAUTH id and project.
   Ordinary current PAUTH validation is attempted first. Revocation, expiry,
   class denial, and every non-drift error remain hard denials.

### Role-boundary attribution

No Prime-authored verdict is created or altered. Every future batch commit
message records `Prime-operated finalization of a reviewer-authored VERIFIED
verdict`, the WI-6073 owner-decision authority, the reviewer-authored verdict
path, and the batch-plan digest.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CROSS-HARNESS-PARITY-001`

## Owner Decisions / Input

No new owner decision was taken in this implementation session. The following
approved evidence is carried forward from the proposal:

1. `DELIB-20260808-GOVERNED-BATCH-FINALIZATION-PATH` -- owner approved a
   governed batch-finalization path and later directed committing all VERIFIED
   work.
2. `DELIB-20260808-SESSION-ENVELOPE-PAUTH-CLASS-EXPANSION` -- records the PAUTH
   v1-to-v2 expansion that produced the motivating WI-6055 drift.
3. The no-database-write boundary in the approved proposal remains operative;
   the implementation and live dry-run performed no `groundtruth.db` write.

## Prior Deliberations

- `bridge/gtkb-wi6073-batch-verified-finalization-001.md` -- approved
  implementation proposal.
- `bridge/gtkb-wi6073-batch-verified-finalization-002.md` -- controlling Loyal
  Opposition GO.
- `DELIB-20260808-GOVERNED-BATCH-FINALIZATION-PATH` -- owner authorization.
- `DELIB-20260808-SESSION-ENVELOPE-PAUTH-CLASS-EXPANSION` -- motivating PAUTH
  drift.
- `DELIB-20260806011917` -- purge-before-probative; skipped candidates are
  reported with reasons rather than rewritten.
- WI-6071 -- **superseded diagnosis**. Its candidate-count deadlock reading came
  from a failed `git add` that left an empty staged set and triggered a whole-
  worktree fallback. WI-6073 implements per-thread evidence handling; it does
  not weaken or group around the ordinary exactly-one-candidate rule.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Focused tests prove exact path commits, canonical-hook execution, commit attribution, compare-and-swap ref binding, and index preservation. The live dry-run proves invalid terminal threads remain uncommitted. |
| Fault 2 subset rule | `test_manifest_relation_allows_declared_clean_path_but_denies_undeclared_staged_path` covers both required directions. |
| Per-thread isolation | Tests cover dirty-path collisions, active-claim fencing, existing staged overlap, report-bound path selection, hook refusal, disposable-index tamper, and one candidate's exact commit set. |
| Ordinary single-thread behavior | The complete 176-test protected-commit suite passes; ordinary current-PAUTH validation remains first and non-drift errors cannot use the carrier. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Publication and applicability freshness remain ordinary blockers. The dry-run names non-consumed, missing, and content-drift capability evidence; it performs no false reconciliation. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This mapping plus the commands and observed results below. |
| `GOV-ARTIFACT-APPROVAL-001` | The batch manifest requires the exact WI-6073 GO packet, owner decision, PAUTH, live claim, and invoking session. |
| `ADR-CROSS-HARNESS-PARITY-001` | The shared protected-commit gate and canonical repository hook are harness-neutral; commit messages preserve reviewer authorship across harnesses. |

## Commands Run

1. `python -m pytest platform_tests/scripts/test_batch_finalize_verified.py -q --tb=short`
2. `python -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py -q --tb=short`
3. `python -m ruff check scripts/batch_finalize_verified.py scripts/check_protected_commit_authorization.py platform_tests/scripts/test_batch_finalize_verified.py`
4. `python -m ruff format --check scripts/batch_finalize_verified.py scripts/check_protected_commit_authorization.py platform_tests/scripts/test_batch_finalize_verified.py`
5. `python scripts/batch_finalize_verified.py plan --json` (rendered to a compact live summary; no file or index mutation)

## Observed Results

- Focused WI-6073 suite: **15 passed**.
- Existing protected-commit regression suite: **176 passed**.
- Ruff check: **All checks passed**.
- Ruff format check: **3 files already formatted**.
- Live dry-run at HEAD `132e95ebf2005689594d427e9c5aaa931afdb238`, ref
  `refs/heads/develop`, plan digest
  `sha256:044c644b5366e98480de1d4014efabc52fd4bf3ba6c2fddcc47d954a46054ce8`:
  **17 candidates, 0 ready, 17 skipped, 0 committed**.
- Skip-evidence counts (a candidate may carry more than one): 12
  `publication_capability_not_consumed`, 4 `publication_capability_missing`, 1
  `publication_content_drift`, 4 `historical_packet_invalid`, 3
  `approved_chain_invalid`, 5 `manifest_invalid`, and 1 `real_index_overlap`.
- Because no candidate was ready, `apply` and post-run `git log` verification
  were not run. HEAD remained unchanged and the pre-existing WI-5895 staged set
  remained owned by its originating actor.

## Files Changed

- `scripts/batch_finalize_verified.py` -- new governed planner/applicator.
- `scripts/check_protected_commit_authorization.py` -- subset relation and
  tightly-bound WI-6073 transaction authority.
- `platform_tests/scripts/test_batch_finalize_verified.py` -- 15 focused
  positive, negative, concurrency, boundary, and attribution tests.

Excluded out-of-scope dirty paths: 569 at scaffold time. No other dirty path was
edited, staged, reset, or committed by this implementation.

## Recommended Commit Type

- Recommended commit type: `feat:`
- Justification: adds a governed batch-finalization capability and its narrow
  gate support.

## Acceptance Criteria Status

1. **Operation implemented; live accumulated work not cleared.** Every ready
   candidate would be finalized independently, but the final live plan found no
   evidence-valid candidate. Owner outcome remains open.
2. **Met.** Commit creation is exact-set checked, disposable-index based, and
   bound to the implementation report's changed paths plus its bridge chain.
3. **Met.** Every ineligible thread has stable named reasons and remains
   untouched; one refusal does not block another candidate's evaluation.
4. **Met.** Declared-but-unchanged passes; undeclared staged paths fail.
5. **Met.** Ordinary behavior retains exactly-one candidate and every existing
   gate regression; the complete suite passes.
6. **Met.** The canonical pre-commit hook is mandatory, and no evidence-invalid
   verdict was committed.

## Deviations And Disclosures

### D1 -- zero live finalizations

The implementation does not claim that the motivating accumulated verdicts
entered history. It deliberately refused them. Clearing the dominant
`recovery_required` capability class requires the existing recovery control
plane and a `groundtruth.db` mutation, which this approved thread expressly
excludes. Refreshing stale reviewer evidence would change candidate bytes and
then conflict with the exact publication digest unless capability state were
reconciled as well. Those actions require separate governed authority or a
revised GO; they were not inferred here.

### D2 -- report-bound path attribution is stricter than manifest intersection

In a shared tree, `declared manifest` intersected with `currently dirty` can
capture a later thread's changes. The planner therefore requires exact `Files
Changed` rows for non-bridge paths and names older reports without that evidence
as skips. This is the safety correction demonstrated by WI-6055's excluded
`test_session_envelope_runtime.py` path.

### D3 -- independent audit findings addressed

A read-only post-implementation audit identified caller/plan binding,
canonical-hook selection, symbolic-ref binding, exact unrelated-index
verification, and linked-ancestor validation gaps. The implementation and tests
were hardened for each before this report. The audit's remaining finding is D1:
the approved constraints leave the current candidates unfinalizable.

## Risk And Rollback

The protected authorization gate is high risk. Mitigations are the narrow drift
class, same-PAUTH binding, current carrier PAUTH re-evaluation over exact staged
protected paths, caller/claim/ref/blob/plan binding, and the full existing gate
suite. The batch operation defaults to read-only planning; mutation requires an
exact digest and explicit authority arguments.

Rollback is a revert of the three declared implementation files. This session
created no batch commit, changed no bridge verdict, wrote no `groundtruth.db`
row, and changed no real-index entry, so there is no history or database
rollback for the live dry-run.

## Loyal Opposition Asks

1. Verify the implementation against the controlling GO conditions and the
   linked specifications.
2. Evaluate D1 explicitly: return `VERIFIED` only if a zero-ready live set is an
   acceptable application of the approved refusal semantics; otherwise return
   `NO-GO` naming the additional governed authority needed to deliver the
   owner's still-open commit-all outcome.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
