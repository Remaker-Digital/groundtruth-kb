ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: cc0eaa61-c6a0-41be-9db7-74f8c9f2e20e
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via canonical init keyword
author_metadata_source: session transcript

# LO Advisory - Six Tooling Defects Observed While Processing The LO Bridge Queue

bridge_kind: governance_advisory
Document: gtkb-lo-tooling-defect-advisory
Version: 001
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-26 UTC

Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5424

## Claim

Six defects were observed directly while processing LO-actionable bridge work on
2026-07-26. Each was reproduced or mechanically confirmed by this session; none
is speculative. **A1 is a live P1: it is blocking two independent Loyal
Opposition sessions from filing a fully-verified `VERIFIED` verdict on
`gtkb-wi5424-auto-finalization-import-repair-v2` at the time of writing.**

None of these is in scope for any bridge item currently in the queue, so they are
filed here rather than folded into a verdict.

## Source

Observed by session `cc0eaa61-c6a0-41be-9db7-74f8c9f2e20e` across three LO runs
on 2026-07-26 while reviewing `gtkb-file-move-rename-canonicalization-v4`,
`gtkb-wi5441-global-registry-membership-reconciliation`, and
`gtkb-wi5424-auto-finalization-import-repair-v2`.

### A1 (P1, live) - VERIFIED finalization cannot reliably complete inside one work-intent claim TTL

**Claim.** The `VERIFIED` commit-finalization path requires a serial sequence of
gate round-trips whose total duration routinely exceeds the 10-minute draft claim
TTL. A reviewer who has done everything correctly still loses the claim mid-flight
and cannot file.

**Mechanism.** `candidate_evidence_hash` is computed by the bridge-compliance
gate over the **final normalized candidate bytes**. Any gate failure that requires
a content edit therefore invalidates the hash just obtained, forcing another
round-trip. The gates are individually correct; their composition is serial and
self-invalidating.

**Observed sequence** on `gtkb-wi5424-auto-finalization-import-repair-v2`, all by
this session, each a separate failed publication attempt:

1. `VERIFIED finalization requires a committed predecessor bridge chain` - the
   untracked `-002` and `-003` chain files had to be added to the `--include` set.
2. `VERIFIED verdict body must include at least one executed Spec-to-Test Mapping
   row with Executed=yes` - the mapping table had to be restructured from three
   columns to four, because the validator regex requires
   `| col | col | yes | col |`.
3. `Verdict applicability freshness check rejected a stale or missing
   candidate_evidence_hash` - hash derived and inserted.
4. `VERIFIED bridge reports must carry Specification Links, a spec-to-test
   mapping, and executed test command evidence` - a `## Specification Links`
   section had to be added, **which invalidated the hash from step 3**.
5. `candidate_evidence_hash` re-derived and re-inserted.

By step 5 the 10-minute claim TTL had expired and session
`8f48e812-4b36-4b70-9891-ccd2abe4c143` acquired the thread.

**Correction, recorded because the first diagnosis was wrong.** This advisory
initially attributed that session's failure-to-file to the TTL race. On a later
attempt with a fresh claim and ample time, the same finalization failed for two
different reasons that are the actual blockers (see A1b and A1c). The TTL race is
real and reproducible, but it is the *second* obstacle, not the first. The
sequence above still stands as evidence of the serial self-invalidating gate
behavior.

### A1b (P1, live) - the finalization helper exits 0 when the commit is rejected

**Claim.** `write_verdict.py --finalize-verified` returned **exit code 0** on a
run where no verdict was written, nothing was staged, and `HEAD` did not move.

**Evidence.** Observed directly. Post-run state: `-004.md` absent, thread head
still `-003` `NEW` at `version_count: 3`, `git log -1` unchanged. The captured
output showed the pre-commit evidence gate rejecting the commit with
`Protected staged files require a live GO implementation packet, committed
terminal VERIFIED bridge evidence, or transaction-local VERIFIED manifest
evidence.`

**Risk / impact.** The rollback itself is correct - the helper failed closed
exactly as `.claude/rules/file-bridge-protocol.md` requires, leaving no terminal
`VERIFIED` artifact. The defect is the exit status. A caller, a script, or an
agent that trusts exit 0 will believe the verdict landed. This is the same
silent-failure class as the WI-5424 defect being verified on this very thread,
where fail-soft converted a total outage into an audit-log-only signal that went
unnoticed for two days.

**Recommended Prime action.** Return a non-zero exit status whenever
finalization does not produce a commit, and print the rejection reason on stderr
rather than only in captured stdout.

### A1c (P1, live) - VERIFIED finalization is blocked by an expired Prime Builder implementation-start packet

**Claim.** The pre-commit evidence gate rejected the finalization with
`gtkb-wi5424-auto-finalization-import-repair-v2: implementation-start packet has
expired`, alongside `Verdict applicability freshness check rejected a stale
packet_hash`.

**Risk / impact.** Loyal Opposition cannot renew a Prime Builder
implementation-start packet, so a completed, clean verification cannot be
finalized by the reviewer at all. The verification work for this thread is done
and reproduces exactly (14 passed, ruff clean, diff 11+/1- across the two
declared targets), but the terminal verdict cannot land. This is the same
condition already recorded for a sibling thread in
`bridge/gtkb-wi5640-verified-finalization-packet-expiry-advisory-001.md`, so it
is a recurring class rather than a one-off.

**Recommended Prime action.** Renew the implementation-start packet for
`gtkb-wi5424-auto-finalization-import-repair-v2` so an independent reviewer can
finalize. More durably: either let packet lifetime cover the review window, or
allow a reviewer-side renewal path bound to the existing GO, since the reviewer
is the party that needs it live at finalization time.

### A1d (P1, observed) - a registered file edit halts all bridge publication, and an undocumented path silently re-baselines it

**Claim.** Bridge publication was refused platform-wide with
`bridge publication requires a current registry generation`, caused by exactly
one stale record: `wi5640-source-066`, `coverage_mode: exact`,
`storage_path: .claude/rules/project-root-boundary.md`.

**Evidence.** `registry_currentness` returned `current: False`,
`stale: ['wi5640-source-066']` while an ordinary uncommitted edit to that rule
file was present. No bridge file of any status, on any thread, could be
published during that window. This is a live recurrence of finding F1 in
`bridge/gtkb-bridge-aggregate-drift-publication-lockout-001.md`.

**Second, more consequential observation.** Roughly two hours later
`registry_currentness` returned `current: True`, `stale: []` **while the edit was
still present and unchanged** (`git status` still `M`, the deleted content still
absent). Something re-observed the record and accepted the new digest without the
file reverting. That contradicts the lockout advisory's statement that no
in-band recovery exists, and it means a registered active control-surface
artifact was silently re-baselined by an unidentified path.

**Risk / impact.** Either GT-KB has an undocumented recovery mechanism - in which
case the lockout advisory's "no in-band recovery" claim needs correcting and the
mechanism needs documenting - or something re-baselines registered artifacts
outside `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`. The second reading is
a governance hole: exact-coverage registration exists precisely so a registered
artifact cannot change without authorization.

**Recommended Prime action.** Identify what re-observed `wi5640-source-066` and
when. Then either document it as the sanctioned recovery path, or close the hole.
This should be settled before further reliance is placed on exact-coverage
registration as a change-control mechanism.

**Risk / impact.** A fully-verified implementation sits unfiled while two
independent reviewers cycle on the same thread. The failure is silent to the
owner: the queue simply does not drain. It also wastes an entire verification
pass each time, because the review work is complete before the finalization
attempt begins.

**Recommended Prime action.** Any one of these would break the loop; the first is
cheapest:

- Emit the **expected `candidate_evidence_hash` alongside every other gate
  failure**, so a single round-trip can fix the content *and* the hash.
- Validate the full gate set **before** the hash check, so all content defects
  surface in one report rather than serially.
- Provide a `--dry-run` / `--check` mode on the finalization helper that reports
  every gate outcome without publishing.
- Extend the draft claim TTL for `--finalize-verified` specifically, or renew it
  automatically across gate retries.

### A2 (P2) - three separate shell guards produce false positives by classifying on substring presence rather than argv position

**Claim.** Three distinct guards blocked strictly read-only commands in this
session. All three fail the same way: they match a token anywhere in the command
string instead of considering where it sits in argv.

**Evidence** - each reproduced by this session:

| Guard | Command blocked | Message | Why it is a false positive |
| --- | --- | --- | --- |
| `lo-file-safety-gate` | `python -c` payload containing `len(v)` with a greater-than comparison | "shell mutation to '6' is outside the allow-list" | The `>` was inside a quoted Python expression, not a shell redirect |
| directive-enforcement | `test -f <path>.py` and `sha256sum <path>.py` | "Direct GT-KB Python helper script execution is prohibited" | Neither utility executes anything; the `.py` path is an argument |
| `lo-file-safety-gate` | `for v in 019 020; do f=bridge/...; done` | "unresolved or opaque shell mutation target" | A shell variable assignment is not a filesystem mutation |

**Risk / impact.** Each block pushed this session onto a slower tool or a
rewritten command. The underlying directives are sound - Windows file association
really can launch a GUI harness from a bare `.py` invocation - so the fix is
detector precision, not relaxation.

**Recommended Prime action.** Fix all three as one class: consider argv position
and quoting context. A `.py` path passed to `test`, `sha256sum`, `ls`, `stat`,
`wc`, `cat`, `grep`, `head`, or `tail` is not execution; a `>` inside a quoted
`-c` payload is not a redirect; `VAR=value` is not a mutation target. Add
regression tests covering both the false-positive cases (must pass) and the
genuine cases (must still block).

### A3 (P2) - the resource-selection hook misfires on prompts that do not name the resource

**Claim.** A `UserPromptSubmit` hook emitted: "The current owner prompt explicitly
selects `backlog`. Read `backlog` via `gt backlog list`."

**Evidence.** The owner prompt in force was the recurring Loyal Opposition bridge
task. It contains no occurrence of the term `backlog`. Its subject is
LO-actionable bridge items.

**Risk / impact.** The hook's own text asserts that "current explicit owner terms
outrank activity defaults, startup ordering, prior context". A false positive
therefore instructs the agent to switch work resources on the strength of a term
the owner never used. This session disregarded it, but the guidance is
authoritative in tone and an agent following it would abandon the queue.

**Recommended Prime action.** Require an actual literal-term match against the
prompt text before emitting the selection directive, and log the matched term so
a false positive is diagnosable.

### A4 (P2) - the canonical finalizer generates the retired helper path into finalization evidence

**Claim.** `.claude/skills/gtkb-verify/helpers/write_verdict.py` emits the retired
`.claude/skills/verify/helpers` path into generated Commit Finalization Evidence
text at approximately line 1009. Several tests then assert on that generated
text, which makes the retired string self-reinforcing.

**Risk / impact.** WI-5424 repaired the one place where the retired path was a
resolved import root. This occurrence is different in kind: the canonical
finalizer *produces* the stale path as evidence, so it propagates into new
verdict artifacts and is defended by tests. It is the highest-value remaining
node in the residual surface.

**Recommended Prime action.** Inventory the full residual
`.claude/skills/verify/helpers` surface and repair it, prioritizing this line.
Related, already-tracked work exists under WI-5664 for the rule-file citations;
this occurrence is outside that scope.

### A5 (P3) - a superseded WI-5424 chain is left Prime-actionable at latest-status GO

**Claim.** `gtkb-wi5424-auto-finalization-validation-timeout` has
`latest_status: GO`, `version_count: 2`. Confirmed live via `gt bridge show`.

**Risk / impact.** A `GO`-latest thread is Prime-actionable and will keep
surfacing as available work. Its GO authorizes a superseded three-path scope
including a file now owned by WI-5664. The v2 proposal explains why the chain is
non-authorizing but never dispositions it, so two live WI-5424 threads exist.

**Recommended Prime action.** File a `WITHDRAWN` or `DEFERRED` entry on the v1
chain recording the supersession and citing the v2 thread.

### A6 (P3) - pre-existing byte-parity failures in the hooks test directory

**Claim.** A full run of `platform_tests/hooks/` shows failures unrelated to any
current bridge item. A sampled failure asserts Codex-template byte-equivalence to
the Claude hook.

**Risk / impact.** Several failures are byte-parity assertions between Claude
hooks and their Codex or template mirrors, which suggests live cross-harness
drift rather than test rot. Independently, this failure set can block any
finalization commit whose pre-commit gate exercises that suite - a second,
unrelated path to the A1 symptom.

**Recommended Prime action.** Triage the failing set and determine whether the
drift is in the hooks, the mirrors, or the generator that projects one to the
other.

## Recommended Prime Action

Take A1 first and separately - it is live and is currently costing completed
verification work on a thread whose implementation is already confirmed correct.
The cheapest fix (emit the expected `candidate_evidence_hash` with every gate
failure) is a small change to the compliance-gate error path.

A2 and A3 are agent-productivity defects with the same character: correct
policies, imprecise detectors. They can be batched.

A4 and A5 are bridge-hygiene items that can be folded into existing residual-path
and chain-disposition work. A6 warrants its own triage.

None of these blocks any current bridge item, and no verdict in the queue depends
on them.

## Owner Decision Needed

None to act on this advisory. All six items are Prime Builder work within
existing project scope.

One item is offered for owner awareness rather than decision: **three independent
Loyal Opposition sessions were observed working the same queue concurrently**
(`c24ef7c7`, `4eeaedbf`, `8f48e812`, plus `735da741` earlier). The work-intent
claim system prevented every collision correctly, so this is an efficiency
question rather than a correctness one - but combined with A1 it produces a
livelock, where sessions take turns failing to file the same verdict.

## Classification Slot

- Classification: **adapt**.
- Rationale: every underlying policy is correct. The defects are in detector
  precision, gate sequencing, and chain disposition - not in the governance
  intent. Nothing here proposes relaxing a gate.
- Derived-work implication: yes - six discrete Prime Builder repairs. No new
  project is proposed; A1 is the only item warranting its own bridge thread.
