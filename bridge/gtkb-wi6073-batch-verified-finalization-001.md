NEW
::init gtkb pb
::open build
author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: 4d038364-5d9f-45c8-9924-a2caefb50a6f
author_model: Claude Opus 5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Prime Builder; harness B; resolved role prime-builder via ::init gtkb pb
author_metadata_source: explicit_interactive_session_metadata

# gtkb-wi6073-batch-verified-finalization - governed batch finalization for accumulated terminal VERIFIED verdicts

bridge_kind: prime_proposal
Document: gtkb-wi6073-batch-verified-finalization
Version: 001
Author: Prime Builder (claude, harness B)
Date: 2026-08-08 UTC

Project Authorization: PAUTH-PROJECT-GTKB-SESSION-ENVELOPE-WHOLE-PROJECT-20260808
Project: PROJECT-GTKB-SESSION-ENVELOPE
Work Item: WI-6073

target_paths: ["scripts/batch_finalize_verified.py", "scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_batch_finalize_verified.py"]

## Summary

Sixteen terminal `VERIFIED` verdicts sit uncommitted in this tree. Each is
refused at `scripts/check_protected_commit_authorization.py`, the fifth
`.githooks/pre-commit` gate. This proposes a governed batch-finalization
operation that clears them under one owner-authorized transaction, and the
narrow gate change that operation requires.

This thread performs no MemBase mutation and no groundtruth.db write.

## Problem — measured, not inferred

Gates one through four pass cleanly for a well-formed staged set: `scan_secrets`
(0 findings), `check_dev_environment_inventory_drift` (PASS, clean),
`check_narrative_artifact_evidence` (PASS), `check_ruff_format` (PASS). Only
gate five refuses.

For `gtkb-wi6055-host-session-id-resolver-unification`, with a correct staged set
(`git add` rc=0), gate five reports four distinct evidence faults:

| # | Fault | Class |
|---|---|---|
| 1 | `bridge publication capability is not consumed ('recovery_required')` | capability-state |
| 2 | `same-transaction manifest does not equal the staged path set; extra=['platform_tests/scripts/test_session_envelope_runtime.py']` | manifest/staged-set equality |
| 3 | `Verdict applicability freshness check rejected a stale packet_hash; expected sha256:b7b595e9…` | evidence freshness |
| 4 | `protected-mutation PAUTH validation failed: Project authorization version drifted since packet creation` | authorization drift |

**A correction this proposal depends on.** An earlier diagnosis recorded on
WI-6071 attributed the block to a candidate-count deadlock, quoting
`same-transaction clearance requires exactly one VERIFIED candidate; found 2`.
That reading was wrong and is superseded. It was produced by a probe whose
`git add` failed with `rc=128`, leaving an empty staged set, which caused the
checker to fall back to a whole-worktree scan that trivially found more than one
candidate. With a correct staged set the failure is thread-specific, as above.
The design below therefore targets per-thread evidence repair, not candidate
counting. Building a grouping-only batch path against the superseded reading
would have fixed nothing.

## Why each fault needs the batch operation rather than per-thread repair

- **Fault 4 has no per-thread repair path.** `implementation_authorization.py
  begin` refuses on a terminal thread: *"requires a GO in the bridge chain;
  latest GO or resumable post-GO NO-GO is required; found latest status
  VERIFIED"*. A VERIFIED thread cannot re-mint the packet whose PAUTH version
  drifted, so it must clear through transaction-local manifest evidence.
- **Fault 2 is a set-equality rule meeting an ordinary reality.** A verdict may
  declare a path that legitimately carries no changes (here a test module the
  implementation did not need to touch). Set equality then fails on a correct,
  honest verdict.
- **Faults 1 and 3 are per-thread state** that a batch operation must detect and
  either recover or refuse on, never silently skip.

## Proposed Change

1. **New operation `scripts/batch_finalize_verified.py`.** Enumerates terminal
   `VERIFIED` verdicts whose chains are evidence-valid, and finalizes them under
   one authorized transaction. For each candidate it: parses the verdict's
   declared `Same-transaction path set`; intersects it with paths that actually
   carry changes; verifies applicability-packet freshness; checks
   publication-capability state; and commits per thread with a pathspec limited
   to that thread's set, so no thread's commit can capture another's paths.
2. **Refusal is per-thread and explicit.** A candidate failing any check is
   skipped with a named reason and left untouched. A batch run never partially
   finalizes a thread, and one bad chain never blocks the others — which is the
   behavior the current all-or-nothing path lacks.
3. **Narrow gate change in `check_protected_commit_authorization.py`.** Accept a
   batch-transaction manifest as clearance evidence, and relax fault 2 from set
   equality to *staged set is a subset of the declared manifest*, so a declared
   path with no changes is not a failure while an undeclared staged path still
   is. No other clearance rule is weakened.
4. **Explicit non-goals.** The single-candidate rule for ordinary single-thread
   commits is unchanged; no pre-commit gate is bypassed; verdicts whose chains
   fail evidence validation are not committed.

## Role-Boundary Disclosure

Finalization is normally the reviewing role's transaction, created atomically
with the verdict by
`.claude/skills/gtkb-verify/helpers/write_verdict.py --finalize-verified`. This
operation is run by Prime Builder because the reviewing harness cannot commit in
this tree. Each batch commit message therefore records that it is a
Prime-operated finalization of a reviewer-authored verdict, so history does not
misattribute authorship of the verdict itself.

## Pre-existing Malformed Chains

The same checker reports roughly twenty-two evidence errors on unrelated threads
(missing `Document` metadata, missing `Version` metadata, implementation report
not linked to its approving GO, `Responds to` mismatches, unsupported packet
schemas). Representative: `gtkb-wi4961-session-kickoff-prompt-sequencing`,
`gtkb-wi4978-helper-compliance-audit-chokepoint`,
`gtkb-wi5002-codex-dotdir-sandbox-acl-correction`,
`gtkb-wi5765-lo-atomicity-suites-and-carrier-gate`.

These are **excluded, not repaired**, by this proposal: the batch operation skips
them with a named reason. Repair is a separate tranche, because rewriting
historical bridge chains is append-only-sensitive and needs its own review.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge audit-trail authority; VERIFIED work
  outside git history is the durability failure this repairs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the spec-to-test mapping
  below is carried forward to the implementation report.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every governing
  specification this proposal is constrained by is cited here.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — bridge state currently reports terminal
  VERIFIED for threads absent from history; the two must agree.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project-linkage headers.
- `GOV-ARTIFACT-APPROVAL-001` — the gate being modified is protected; owner
  approval is cited under Owner Decisions.
- `GOV-STANDING-BACKLOG-001` — WI-6073 is the tracked carrier.
- `ADR-CROSS-HARNESS-PARITY-001` — the gate is tree-wide; every harness hits it
  identically, which is why the reviewing harness also cannot commit.

## Prior Deliberations

- `DELIB-20260808-GOVERNED-BATCH-FINALIZATION-PATH` — owner approval of this
  path over narrowing the clearance rule.
- `DELIB-20260808-SESSION-ENVELOPE-PAUTH-CLASS-EXPANSION` — the v1→v2 expansion
  that caused fault 4, recorded so the causal chain is legible.
- `DELIB-20260806011917` — purge before probative; skipped candidates are named
  with reasons rather than annotated in place.


### Helper-suggested candidates

<!-- Pre-populated by helper; review and prune. -->
- DA: `DELIB-202665674` — seed=search; bridge_thread; Loyal Opposition Verdict -- GO (no-source-change direct-thread reconciliation ac
- DA: `DELIB-202667534` — seed=search; owner_conversation; Advisory corpus disposition table: all 94 live ADVISORY threads triaged and disp
- DA: `DELIB-202667587` — seed=search; bridge_thread; LO Review — WI-5458 PAUTH precedence v2 implementation report revision
- DA: `DELIB-202666402` — seed=search; bridge_thread; Loyal Opposition Corrected Verdict (review_no_action) - NO-GO - WI-5211 F Govern
- DA: `DELIB-202666490` — seed=search; bridge_thread; Loyal Opposition Verdict - NO-GO (finalization-scoped) - gtkb-wi5313-runtime-rec

## Owner Decisions / Input

Collected in session `4d038364-5d9f-45c8-9924-a2caefb50a6f` on 2026-08-08.

1. **Batch path approved.** Owner: *"I approve a governed batch-finalization path
   that clears accumulated verdicts in one authorized transaction."* Recorded as
   `DELIB-20260808-GOVERNED-BATCH-FINALIZATION-PATH`. This is the operative
   authorization for the gate change proposed here.
2. **Proceed directive.** Owner directed proceeding with the implementation and
   terminating the errant git process holding the index lock. Both actions were
   taken; the lock is clear and HEAD is unchanged.
3. **Commit all VERIFIED work.** Owner: *"Please commit all work that is
   VERIFIED"*, reaffirmed after an initial failure report. That is the outcome
   this operation delivers.

## Requirement Sufficiency

**Existing requirements sufficient.** `GOV-FILE-BRIDGE-AUTHORITY-001` already
requires the bridge audit trail to be durable, and the VERIFIED
commit-finalization gate already requires verdict and verified paths to enter
history together. This repairs an implementation that cannot satisfy those
existing requirements at the current scale; it introduces no new requirement.

## Specification-Derived Verification

| Linked specification | Derived verification (spec-to-test) |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | After a batch run, assert every finalized thread's verdict and verified paths are present in git history. |
| Fault 2 rule change | Assert a declared-but-unchanged path no longer fails clearance, and assert an **undeclared** staged path still fails. Both directions required. |
| Per-thread isolation | Assert a thread failing a check is skipped with a named reason, left untouched, and does not prevent other threads from finalizing. |
| Non-goal: single-thread rule | Assert ordinary single-thread commits are unaffected by the gate change. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Assert bridge state and git history agree on finalized threads after a run. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This mapping plus executed command evidence in the implementation report. |

Commands to be executed and reported:

- `python -m pytest platform_tests/scripts/test_batch_finalize_verified.py -q`
- `python -m ruff check` and `python -m ruff format --check` on the declared
  Python target paths, as separate gates
- A dry-run batch enumeration reporting candidates and skip reasons
- Post-run verification that each finalized verdict resolves in `git log`

## Acceptance Criteria

1. A batch run finalizes every evidence-valid terminal VERIFIED thread.
2. Each commit is pathspec-limited to its own thread's declared set.
3. Ineligible threads are skipped with named reasons and left untouched.
4. A declared-but-unchanged path does not fail clearance; an undeclared staged
   path still does.
5. Ordinary single-thread commit behavior is unchanged.
6. No pre-commit gate is bypassed and no evidence-invalid verdict is committed.

## Risk and Rollback

**Risk.** This modifies a protected authorization gate, so a defect could admit
commits that should be refused. Mitigation: the only relaxation is set-equality
to subset on the manifest check, tested in both directions; every other
clearance rule is untouched, and the negative test for undeclared staged paths
is a blocking acceptance criterion.

A second risk is scale: a batch run touching sixteen threads makes a large
history change. Mitigation: per-thread pathspec commits keep each change
independently revertable, and a dry-run mode reports the full plan before any
commit.

**Rollback.** Revert of the declared files restores the current gate behavior.
Commits produced by a batch run are ordinary per-thread commits and revert
individually. No MemBase mutation, no bridge-state change, no verdict file is
altered.

## Recommended Commit Type

`feat:` — adds a new governed operation plus the narrow gate support it requires.

---

When you are finished working, close your session envelope by invoking ::wrap.
