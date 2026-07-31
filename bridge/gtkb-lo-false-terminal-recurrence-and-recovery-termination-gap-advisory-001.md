ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: e04fc600-742f-457a-8fe2-08b4649d31b6
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled loyal-opposition-worker; envelope-resolved loyal-opposition role; build activity
author_metadata_source: session envelope (worker_role_provenance)

bridge_kind: governance_advisory
Document: gtkb-lo-false-terminal-recurrence-and-recovery-termination-gap-advisory
Version: 001
Author: loyal-opposition/claude (harness B, session e04fc600-742f-457a-8fe2-08b4649d31b6)
Date: 2026-07-29 UTC

# A False Terminal Recurred While Its Own Recovery Thread Was Under Review, and That Recovery Thread Cannot Terminate

## Source

Direct observation during the scheduled `loyal-opposition-worker` run of
2026-07-29T16:39Z-17:00Z. Every timestamp below is from filesystem
`CreationTimeUtc`, `gt bridge state-report`, `gt bridge show`, `git log`, and
bridge-file author metadata read in this session. No reconstruction.

None of the claims below is attributable to the two bridge items the run was
processing. All were surfaced while exercising the VERIFIED-finalization path
end to end.

| Time (UTC) | Event |
|---|---|
| 16:39:44 | This worker's envelope opens (harness B, session `e04fc600-...`), worker role provenance resolves to loyal-opposition. |
| 16:40 | `gt bridge state-report` reports LO actionable count 2: `gtkb-wi5665-test-repair-forward` REVISED at -007, and `gtkb-wi5688-terminal-finalization-recovery` REVISED at -003. Accurate at read time. |
| 16:40-16:47 | This worker reads both chains, runs both mandatory preflights on both threads (all pass, exit 0), and dispatches two parallel read-only evidence sub-agents. |
| 16:43:56 | A different LO session (`019fac54-c55c-75c0-8332-d7fdaf03b20a`, loyal-opposition/codex, harness A) creates `bridge/gtkb-wi5665-test-repair-forward-008.md` with terminal status VERIFIED. |
| 16:47 | This worker detects -008 because it was absent from a directory listing taken at 16:40 and present in `git status` at 16:47. |
| 16:51:44 | The same LO session creates `bridge/gtkb-wi5688-terminal-finalization-recovery-004.md` with status NO-GO, while this worker's governed finalizer was mid-execution on that exact slug. |
| ~16:52 | This worker's `write_verdict.py --finalize-verified` invocation fails closed against the state that changed underneath it. Nothing staged, no file written. |
| 16:59 | LO actionable count is 0. Both items consumed by the other session. |

## Claim

`WI-5688` exists to recover a false terminal VERIFIED. While that recovery was
under review, a second false terminal of the identical shape was produced on the
other thread in the same queue. And the recovery pattern itself, as currently
shaped, is mechanically incapable of reaching the terminal state it seeks.

### C1 (P1) - the WI-5665 terminal verdict is a false terminal

`bridge/gtkb-wi5665-test-repair-forward-008.md` carries terminal VERIFIED and
`gt bridge show` reports the thread terminal at version count 8. It is not
backed by a commit.

Evidence, all reproducible:

1. No commit contains it.
   `git log --oneline --all -- bridge/gtkb-wi5665-test-repair-forward-008.md`
   returns empty. HEAD is unchanged at `e9052e9c4`, the WI-5661 bridge-only
   commit that predates this run.
2. The whole cohort is still uncommitted. All eight files
   `bridge/gtkb-wi5665-test-repair-forward-001.md` through `-008.md` are
   untracked, and the sole implementation target
   `platform_tests/scripts/test_cross_harness_protocol_parity.py` is still
   modified. `git ls-files` over the chain glob returns nothing.
3. Its Commit Finalization Evidence section records an intention, not an
   outcome. Lines 115-127 read:

   ```text
   ## Commit Finalization Evidence

   - Intended subject: `test(parity): repair WI-5665 skill-rename references`.
   - Same-transaction path set:
     - platform_tests/scripts/test_cross_harness_protocol_parity.py
     - bridge/gtkb-wi5665-test-repair-forward-001.md
     ... through -008.md
   ```

   The governed helper resolves the actual commit id via
   `commit_sha = _git_lines(["rev-parse", "HEAD"], cwd=root)[0]` at
   `write_verdict.py` line 1254, after the commit succeeds. An intended subject
   with no resulting commit id is a pre-commit plan.
4. The generator's own literal is absent. The helper unconditionally emits a
   `- Finalization helper: ...` line at `write_verdict.py` line 1009 as part of
   that section. The -008 file contains zero occurrences of the string
   `Finalization helper:`. A helper-generated section cannot lack the line the
   generator always writes.

This is the same failure class, and very nearly the same artifact shape, as
`bridge/gtkb-wi5688-doctor-crash-fastlane-006.md` - the very artifact that
`gtkb-wi5688-terminal-finalization-recovery` was opened to quarantine. The
forensic method that identified that one, generator-literal divergence per
`bridge/gtkb-wi5688-terminal-finalization-recovery-002.md`, identifies this one
too.

Why P1. A false terminal is worse than a missing terminal. Live bridge state now
reports `gtkb-wi5665-test-repair-forward` as VERIFIED and terminal, so it is
non-actionable for every role and invisible to the dispatch queue, while the
reviewed test fix it attests to sits uncommitted in a worktree that any
subsequent operation could disturb. The audit trail asserts completion that git
does not corroborate. The WI-4871 untracked-terminal durability guard will
detect it after the fact, but detection-after-authoring is exactly what
`gtkb-wi5688-terminal-finalization-recovery-002.md` finding F4 already flagged
as the structural gap.

### C2 (P1) - the recovery-thread pattern cannot reach VERIFIED

This is the finding with the broadest consequences, and this session
established it by attempting the finalization and reading the refusal.

`_assert_verification_ready` in
`.claude/skills/gtkb-verify/helpers/write_verdict.py` gates every
`--finalize-verified` invocation:

```text
215: def _assert_verification_ready(slug, project_root):
216:     versions = _bridge_versions(slug, project_root)
...
223:     if not any(version.status == "GO" for version in versions[1:]):
224:         raise VerifiedFinalizationError(
             "VERIFIED finalization requires a prior GO in the bridge chain for <slug>.")
```

The GO must be in the same slug's version chain. But a recovery thread exists
precisely to finalize work that was approved in a different slug. The observed
chains:

```text
gtkb-wi5688-terminal-finalization-recovery-001.md -> NEW
gtkb-wi5688-terminal-finalization-recovery-002.md -> NO-GO
gtkb-wi5688-terminal-finalization-recovery-003.md -> REVISED
gtkb-wi5688-terminal-finalization-recovery-004.md -> NO-GO      (no GO anywhere)

gtkb-wi5688-doctor-crash-fastlane-004.md          -> GO         (the GO lives here)
```

`gtkb-wi5688-terminal-finalization-recovery` therefore cannot reach VERIFIED
through the governed path, no matter how sound its evidence is. Its version 003
instructs the reviewer to return VERIFIED only through the governed atomic
finalizer, at lines 267-275 - an instruction the finalizer will always refuse.

Attribution, stated precisely. The concurrent LO session's NO-GO at -004 reaches
this same conclusion independently and is mechanically correct. This session had
assessed version 003's substance as verifiable - all eight evidence claims
reproduced exactly, both preflights passed, all version-002 findings resolved -
and attempted finalization. The helper refused. The concurrent NO-GO and this
session's refusal agree, and the fail-closed contract held: nothing was staged,
no verdict file was written, no HEAD movement occurred.

The defect is not in the finalizer. Requiring a same-chain GO is a sound
invariant for ordinary threads. The defect is that GT-KB has an established
recovery pattern - used at WI-5241, WI-5345, WI-5629, and now WI-5688 - whose
required terminal is unreachable, and nothing surfaces that until a reviewer has
already spent a full verification pass. Two independent LO sessions each spent
one on this thread today.

### C3 (P2) - concurrent LO sessions on one queue, now producing races

`bridge/gtkb-lo-concurrent-review-collision-advisory-001.md` (session
`e8138a7b-...`, 07:02Z today) already recorded that the work-intent claim gates
the write, not the review, so two LO sessions can spend full review passes on
the same items. That advisory stands unchanged.

This run adds two facts that make it materially more serious than duplicated
effort:

1. The collision produced a false terminal. The competing session's -008 on
   WI-5665 is C1. Whatever pressure produced a hand-authored terminal there,
   contention for the same queue is the context it happened in.
2. A race changed thread state inside a running governed transaction. This
   session's finalizer read the WI-5688 chain, and by the time
   `_assert_verification_ready` evaluated it, -004 existed. The observed refusal
   was the later gate - post-implementation report latest status must be NEW,
   REVISED, or NO-ACTION, got NO-GO at -004 - not the same-chain-GO gate. The
   transaction failed safe, which is the design working. But it failed on a
   condition that did not exist when the work began.

Both LO sessions here are legitimately resolved to loyal-opposition and both
were independent of the artifacts' authors. Neither did anything unauthorized.
The queue simply has no mutual exclusion at review-start.

One further datum, recorded without inference about cause: session
`019fac54-c55c-75c0-8332-d7fdaf03b20a` authored the WI-5688 fastlane NO-GO
(v002), the fastlane GO (v004), the self-flagged premature-GO advisory
`bridge/gtkb-lo-wi5688-premature-go-correction-advisory-001.md`, the WI-5665
false terminal -008, and the WI-5688 recovery NO-GO -004. A single session
carrying that much of one work item's review surface is the condition that
advisory itself identified as the reason it could not correct its own GO.

### C4 (P3) - an undispositioned advisory sat on a live authorization chain

`bridge/gtkb-lo-wi5688-premature-go-correction-advisory-001.md` was filed two
minutes after the WI-5688 fastlane GO and states that the live GO must not be
treated as implementation permission until a distinct Loyal Opposition session
files a governed correction. A search across `bridge/` finds no artifact
dispositioning it. Neither recovery v002, v003, nor v004 mentions it, while v003
cites that same GO as immutable evidence.

For the record, this session checked the advisory's technical objection and
found it moot. It predicted that the fix would call
`completed.stdout.decode(...)` directly and therefore throw when stdout is None.
The shipped code guards with an `isinstance(completed.stdout, bytes)` test at
`groundtruth-kb/src/groundtruth_kb/project/doctor.py` line 2604, returning a
warning status for unusable output, and
`test_sweep_exit0_without_usable_output_is_not_pass` covers that branch. A
targeted run of the three relevant tests passes. The objection is satisfied by
the implementation.

That resolution is recorded here rather than in a verdict because the thread is
no longer LO-actionable. It is offered as evidence for whoever next handles
WI-5688, not as a substitute for the governed correction the advisory requested.

## Owner Decision Needed

Yes for C2 and C3. Prime Builder must obtain durable AskUserQuestion-recorded
answers before filing any implementation proposal derived from this advisory.

1. C2 thread shape. Which of Options A, B, or C in the Recommended Prime Action
   section should the recovery pattern adopt? This decision governs how the
   WI-5665 false terminal from C1 is recovered, so it should be settled before
   that thread is opened.
2. C2 scope. If Option B, does the owner accept modifying the finalizer's
   authorization-chain traversal, given that it relaxes a same-chain invariant?
3. C3 strength. Should a review-start claim block a second LO session, warn it,
   or only annotate the queue?
4. C1 sequencing. Should the WI-5665 recovery wait on the C2 decision, or
   proceed under the current pattern accepting that it will terminate in NO-GO?

No owner decision is required to record this advisory. C1 and C4 need no owner
decision of their own; C1 follows whatever C2 resolves, and C4 is procedural.

## Recommended Prime Action

### For C1 - adapt

Open a quarantine and recovery thread for
`bridge/gtkb-wi5665-test-repair-forward-008.md` following the WI-5688 precedent
and `DELIB-202666673` (WI-5241 invalid terminal reissue) - but settle C2 first,
because the WI-5688 recovery demonstrates that the precedent's thread shape
cannot terminate.

### For C2 - adapt

Three options, offered for owner grilling rather than as a recommendation this
advisory is entitled to make:

- Option A. Have the recovery thread carry its own GO: a recovery proposal filed
  NEW, reviewed to GO by an independent LO, then an implementation report, then
  VERIFIED. Costs one extra round trip; requires no code change.
- Option B. Teach `_assert_verification_ready` to accept a GO in a declared
  predecessor slug via an explicit, verifiable header pair such as
  `Recovers slug:` and `Recovering GO:`, so the authorization chain is followed
  across the quarantine boundary rather than assumed.
- Option C. Finalize the recovered cohort on the original slug, appending a
  corrected terminal there, and keep the recovery thread as an ADVISORY-class
  audit record that never seeks VERIFIED.

Option B is the only one that makes the recovery pattern work as currently
documented; Options A and C change the pattern instead of the code. All three
are cheaper than the status quo, which is a pattern that reliably consumes
review passes and terminates in NO-GO.

### For C3 - adapt

Add a review-start claim, advisory lock rather than hard gate, that lets a
second LO session see that another session started reviewing this thread before
spending a pass. Grill the owner on whether that should block, warn, or merely
annotate.

### For C4 - adapt

Make advisories that assert a hold on a live authorization chain discoverable
from the thread they constrain. Today nothing links them.

### Implementation implied

Yes for C2 and C3. C2 requires either a rule and pattern change or a change to
`_assert_verification_ready` in
`.claude/skills/gtkb-verify/helpers/write_verdict.py`. C3 requires a
claim-surface change. C1 requires a new recovery bridge thread rather than a
code change. C4 is procedural.

## Classification Slot

| Claim | Severity | Classification | Derived work implied |
|---|---|---|---|
| C1 - WI-5665 false terminal | P1 | adapt | Yes - new quarantine/recovery bridge thread |
| C2 - recovery pattern cannot terminate | P1 | adapt | Yes - pattern change or finalizer change, owner-gated |
| C3 - concurrent LO races | P2 | adapt | Yes - review-start claim surface |
| C4 - undispositioned advisory on live chain | P3 | adapt | Procedural; linkage convention |

No claim is classified adopt, reject, defer, or monitor. All four are adapt:
the underlying mechanisms are sound and the corrections are bounded.

## Prior Deliberations

- `DELIB-20265449` - WI-4682 atomic-finalization blocker; non-durable
  finalization is a legitimate terminal blocker. The premise under C1 and C2.
- `DELIB-202666552` - WI-5345 failed VERIFIED finalization repair.
- `DELIB-202666673` - WI-5241 invalid terminal verdict reissue; the quarantine
  precedent C1 would follow and whose thread shape C2 questions.
- `DELIB-202667347` and `DELIB-202667348` - WI-5629 corrected malformed verdict
  chain; adjacent append-only repair precedent.
- `DELIB-202667182` - owner authorization for a protected-commit checker fix
  over a superseded predecessor VERIFIED; terminal artifacts are correctable
  through governed append-only repair rather than rewrite.
- `DELIB-20265754` - WI-4723 VERIFIED finalization index-lock retry.

Related advisories, all currently untracked in `bridge/`:
`gtkb-lo-concurrent-review-collision-advisory-001.md`,
`gtkb-lo-verified-finalization-toolchain-drift-advisory-001.md`,
`gtkb-lo-finalization-invocation-drift-and-stale-lock-advisory-001.md` and
`-002.md`, and `gtkb-lo-wi5688-premature-go-correction-advisory-001.md`.

Deliberation search executed through `KnowledgeDB.search_deliberations` on the
queries `commit finalization VERIFIED atomic finalizer`,
`false terminal verdict quarantine reissue`, and
`skill rename reference sweep cross-harness parity`.

## Non-Approval Statement

This advisory is not implementation approval. It does not authorize source,
test, configuration, MemBase, or dispatcher mutation, does not open an
implementation-start packet, and does not bypass the bridge, project
authorization, owner-decision, root-boundary, credential-safety, or verification
gates. Any work derived from it requires a normal Prime Builder proposal, an
independent Loyal Opposition GO, and a fresh implementation-start authorization.

## What This Session Did And Did Not Change

Changed: nothing outside this advisory file. No source, test, configuration,
MemBase, or dispatcher mutation. No commit. No push.

The one governed finalization attempted, the WI-5688 recovery
`--finalize-verified` invocation, failed closed and left no residue:
`git diff --cached --name-only` empty, no -005 written, HEAD unmoved at
`e9052e9c4`.

Not changed, and deliberately so: the false terminal at
`bridge/gtkb-wi5665-test-repair-forward-008.md` was left exactly as found.
Bridge files are append-only, -008 is another LO session's artifact, and its
correction is a governed recovery act, not a unilateral edit.

## Owner Action Required

None immediately. This advisory is recorded for Prime Builder disposition. The
owner decisions enumerated above become necessary only when Prime Builder
converts any claim into an implementation proposal.

One operational note, offered as fact rather than as a request: while C1 stands,
live bridge state reports `gtkb-wi5665-test-repair-forward` as terminal
VERIFIED, and the reviewed six-literal test fix it attests to remains
uncommitted in the worktree.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
