ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 931ea858-10a4-4933-ab18-678db95e9c6e
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via session envelope worker_role_provenance
author_metadata_source: session envelope (worker_role_provenance)

bridge_kind: governance_advisory
Document: gtkb-lo-wi5441-stranded-terminal-verified-advisory
Version: 001
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-28 UTC

# LO Advisory - A Terminal VERIFIED Was Stranded On WI-5441 While This Run Was Reviewing It; The Substance Is Independently Corroborated, So The Remedy Is To Commit It, Not To Re-Review It

---

## Source

Scheduled Loyal Opposition worker run in session
`931ea858-10a4-4933-ab18-678db95e9c6e`, branch `research`, HEAD `1c82158e8`,
2026-07-28 UTC.

Every observation below was produced by executing read-only tooling in this
repository during that run. Nothing is inferred from prior sessions. This run
mutated no source, staged nothing, and created no commit.

This advisory is filed under a **new slug** deliberately. The advisory-router
slug-dedup starvation recorded at
`bridge/gtkb-lo-advisory-router-slug-dedup-starvation-advisory-001.md` means a
`-012` appended to the existing `gtkb-lo-tooling-defect-advisory` slug would not
reach the owner. This is the same defect class as
`bridge/gtkb-lo-tooling-defect-advisory-011.md` A11a, but it is a **new
occurrence on a different thread**, caught live rather than reconstructed.

Related prior records, all independently authored:

- `bridge/gtkb-lo-tooling-defect-advisory-011.md` - A11a/A11b/A11c/A11d; the
  mechanism this advisory reproduces on a second thread.
- `bridge/gtkb-lo-auto-finalize-sweep-zero-success-advisory-001.md` - the sweep's
  zero-success record, for which A3 below supplies the structural mechanism.
- `bridge/gtkb-lo-verdict-filing-path-advisory-001.md` - extended by A5 below.
- `bridge/gtkb-lo-ruff-format-gate-crlf-worktree-defect-advisory-001.md` - the
  CRLF gate defect that inflated the `-010` blocker count; now moot for this
  thread because the worktree is format-clean, but still standing.
- `bridge/gtkb-lo-verified-finalization-packet-freshness-advisory-001.md` -
  sibling packet-anchor defect on the same helper.
- `DELIB-20260726-WI5441-REGISTRY-OBSERVATION-BOOTSTRAP-APPROVAL`.
- `DELIB-20260727-WI5441-PLATFORM-WIDE-CONTENT-EDIT-LIVENESS` and
  `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` are the
  governing owner decisions, carried forward and not reopened here.

---

## Claim

### A1 (P0) - a terminal VERIFIED was published for WI-5441 with no commit, and the thread silently left the review queue mid-run

`bridge/gtkb-wi5441-global-registry-membership-reconciliation-012.md` exists on
disk with first token `VERIFIED` and is **untracked**. No commit contains it.

**Evidence, executed by this reviewer.** At run start (~07:05 UTC),
`gt bridge state-report` reported `VERIFIED 1718`, `REVISED 1`, and
`LO_ACTIONABLE_LATEST_NEW_REVISED_NO_ACTION | 1:
gtkb-wi5441-global-registry-membership-reconciliation (REVISED at ...-011.md)`.

At 07:16:33 UTC, mid-review, the same surface reported `VERIFIED 1719` and
`LO_ACTIONABLE_LATEST_NEW_REVISED_NO_ACTION | 0: (none)`.

```
gt bridge show gtkb-wi5441-global-registry-membership-reconciliation --json --compact
  "latest_path":   "bridge/gtkb-wi5441-global-registry-membership-reconciliation-012.md",
  "latest_status": "VERIFIED",
  "version_count": 12
```

Commit state at the same moment:

```
git status --porcelain -- bridge/...-012.md
  ?? bridge/gtkb-wi5441-global-registry-membership-reconciliation-012.md

git ls-files --error-unmatch bridge/...-012.md
  error: pathspec ... did not match any file(s) known to git

git log --oneline -1
  1c82158e8 fix(bridge): reproducible verdict freshness and exact-row publication routing (WI-5441)
```

The `-012` file mtime is 07:14 UTC - roughly nine minutes after this run began
and two minutes before the state read above. The verdict was authored by session
`cc0eaa61-c6a0-41be-9db7-74f8c9f2e20e` (harness B), which also authored `-004`,
`-006`, the `-008` GO, and the `-010` NO-GO.

`-012` carries a commit-finalization-evidence section listing an **intended**
commit subject and a same-transaction path set. The intent is recorded; the
transaction is not. All 32 declared implementation paths remain dirty or
untracked in the worktree.

**Deficiency rationale.** `.claude/rules/file-bridge-protocol.md` Mandatory
VERIFIED Commit-Finalization Gate requires that a terminal `VERIFIED` not exist
in the worktree unless the same local transaction creates the commit containing
the verified paths and the verdict artifact. The published state now asserts
terminal verification of work that is not in git history. Because `VERIFIED` is
terminal and non-dispatchable, the thread simultaneously stopped being
LO-actionable, so no queue surface will resurface it. This is the exact
publish-before-commit mechanism documented as A11a in
`bridge/gtkb-lo-tooling-defect-advisory-011.md`, reproduced on a second thread
within twenty-four hours.

**Aggravating interaction (A11b).** The stranding session authored `-012`, so
review independence bars it from filing the corrective verdict against its own
artifact. The failure mode creates the state that prevents its own correction.

### A2 (P1) - the substance of -012 is independently corroborated, so the remedy is finalization, not re-review

This is the finding with the most forward value, and it is the reason this
advisory exists rather than a bare defect report.

Before `-012` appeared, this run had already completed a full independent
post-implementation verification of `-011` from a session context
(`931ea858-...`) unrelated to both the report author (`019f863a-...`, Codex A)
and the `-012` verdict author (`cc0eaa61-...`). That verification **passes on
every axis**, and it was produced without reading `-012`'s conclusions first.

| Axis | Method | Result |
| --- | --- | --- |
| `-010` F1 blocker (the sole blocker) | `ruff format --check` and `ruff check` over all 29 declared Python paths | PASS - `29 files already formatted`; `All checks passed!`; `git diff --check` exit 0 |
| The two new noqa suppressions | Rule-code identification plus HEAD reproduction via `git show HEAD` piped to `ruff check --stdin-filename` | PASS - `E402` at line 20 is forced by a load-bearing `sys.path` bootstrap; `B023` at line 167 is a closure consumed in the same iteration, so late binding cannot misfire. Both reproduce at HEAD with identical codes and line numbers. No defect masked. |
| Registry postimage | `gt registry inspect --json --no-census` | PASS - 2,346 records; coherent; identity current; declaration and packaged digests both `e72d44ed...b6350`; projection `53dcc53d...b3392`; generation `0cc3fa92...d10849` - all exactly as claimed |
| Transaction chaining | Direct read of `sot_registry_transaction_journal` | PASS - `SOTTXN-002E...AAA8` then `SOTTXN-CEA3...C57F`; second `old_canonical` equals first `new_canonical` (`e69eaa2f...ed89f`); second `new_canonical` equals live declaration digest; both committed; both carry the WI-5441 PAUTH, bridge id, and start packet hash |
| Additive-only | Set difference over journal postimages | PASS - 313 to 2,344 to 2,346; 2,033 additions; zero removals; zero in-place mutation of pre-existing records |
| Member manifest | Parse of the report's TSV against the journal-derived added set | PASS - exactly 2,032 data rows; zero malformed; zero empty observer attributions; zero duplicates; manifest-minus-added is empty and added-minus-manifest is exactly `groundtruth.db`, matching the by-reference waiver |
| Observer policy | Attribution census over the manifest | PASS - `physical_census` attributes zero membership (it is the traversal and pruning observer), consistent with the design |
| Spec-derived tests | All seven declared suites re-executed individually | PASS - 10, 29, 37, 36, 43+1, 12+1, 6 - every claimed count reproduced exactly |
| Both disclosed baselines | Failure-identity and pre-existence analysis | PASS - both are the exact named failures; the parity failure is EOL-only (byte-identical after CRLF normalization, root-caused to a missing `.gitattributes` rule for the active hook path); the harness-parity extra is `gtkb-skill-rollout` on paths untouched by this change |
| Scope accounting | `git status --porcelain` reconciled to declared changed files | PASS - 34 modified minus the 4 named exclusions = 30, plus the 2 new untracked modules = the 32 declared. Zero drift in either direction. |
| Applicability preflight | `bridge_applicability_preflight.py` against `-011` | PASS - `preflight_passed: true`; no missing required or advisory specs; no blocking errors; exit 0 |
| Clause preflight | `adr_dcl_clause_preflight.py` (mandatory mode) | PASS - 5 evaluated, 4 must_apply all with evidence, 0 blocking gaps, exit 0 |
| Deliberation search | `gt deliberations search` | Done - no closely-scoring prior deliberation (best 0.932), consistent with a novel admission design |
| `-010` F2/F3/F4 disclosures | Text inspection plus filesystem check | PASS - taxonomy-hunk provenance disclosed; the named transient index confirmed absent; the four excluded dirty paths named exactly |

**Deficiency rationale.** Nothing about this thread requires further review. The
implementation is correct, the evidence reproduces, and two mutually independent
reviewers reached the same conclusion by separate methods. The **only** unmet
requirement is the git commit. Any future session that treats the stranded
`-012` as a reason to re-open substantive review will burn a large token budget
re-deriving a settled result. This section exists so that does not happen.

### A3 (P1) - the auto-finalization sweep structurally cannot rescue this class of strand

`.claude/rules/auto-finalization-sweep.md` requires, as a hard eligibility
condition, that the responded-to report's target paths all be **clean** in
`git status` ("implementation already committed"). For WI-5441 all 32 declared
paths are dirty or untracked, precisely because the finalization commit is the
thing that would have committed them.

The sweep is therefore permanently ineligible for exactly the strands that
matter most: those where the implementation and the verdict were meant to land
in one transaction. It can only rescue verdicts whose implementation was already
committed separately - the easy case. This is consistent with, and supplies the
mechanism for, the zero-success record reported at
`bridge/gtkb-lo-auto-finalize-sweep-zero-success-advisory-001.md`.

### A4 (P2) - the rescue window is bounded by an implementation-start packet that expires before an independent reviewer can act

The packet at
`.gtkb-state/implementation-authorizations/by-bridge/gtkb-wi5441-global-registry-membership-reconciliation.json`
records `created_at 2026-07-28T05:33:36Z` and `expires_at 2026-07-28T07:33:36Z`.

The strand occurred at 07:14 UTC. The packet expired at 07:33:36 UTC - a
nineteen-minute rescue window. Advisory v011 A11c measured the protected-commit
gate at roughly thirteen minutes of wall time, and that measurement was taken
*after* the WI-5658 performance fix (`93f776466`) had landed, so it reflects
current cost.

**Deficiency rationale.** A rescue attempt inside that window is a race against
packet expiry, run through a helper that publishes terminal state *before* it
commits. Losing the race does not fail closed - it appends a **second** stranded
terminal verdict, and bars the rescuing session from correcting that one too.
This run therefore declined to attempt it. That is a deliberate decision to
avoid compounding the defect, not an omission.

### A5 (P2) - the documented finalization helper path is stale in the rules and in the verdicts that cite it

`.claude/rules/file-bridge-protocol.md`, `.claude/rules/loyal-opposition.md`,
and `.claude/rules/codex-review-gate.md` all instruct reviewers to run
`python .claude/skills/verify/helpers/write_verdict.py --finalize-verified`.
That path does not exist. The canonical skill rename (`3e7626a41`) moved it to
`.claude/skills/gtkb-verify/helpers/write_verdict.py`. Executing the documented
command yields `can't open file ... [Errno 2] No such file or directory`.

`-012`'s own commit-finalization-evidence section reproduces the stale path
verbatim, which shows the error propagating from the rules into the verdict
corpus. The same stale-path pattern appears in the governed-writer driver
precedent at `.claude/skills/gtkb-bridge-propose/helpers/file_proposal_wi5540.py`,
which still resolves the pre-rename `bridge-propose` directory. This corroborates
and extends `bridge/gtkb-lo-verdict-filing-path-advisory-001.md`.

### A6 (P3) - nine leaked temp index directories, about 21 MB, invisible to git status

Nine directories matching `.gtkb-index-*` sit in the project root, each about
2.3 MB, created between 2026-07-23 and 2026-07-25:
`cwv3hf3w`, `2ybwnnsa`, `hef4mjw4`, `t7nsgbor`, `h_1cwotz`, `3wupbb0i`,
`fhgo52kh`, `jzitjv59`, `ilk3djzq`.

Creator: `scripts/check_protected_commit_authorization.py:900` -
`tempfile.TemporaryDirectory(prefix=".gtkb-index-", dir=root)`. That context
manager cleans up only on normal interpreter exit, so every run killed by a tool
timeout - the documented common case for this very gate (A11c) - leaks a copy.

All nine predate this thread's `-001` proposal (2026-07-26), so they are **out
of scope for the WI-5441 verdict** and are recorded here rather than as a
finding against it. `-010` F3 flagged one instance (`b8nhvvny`, since removed);
the systemic leak remains.

Neither `git status --porcelain` nor `git status --porcelain --untracked-files=all`
lists them, and `.git/info/exclude` contains no matching rule, so ordinary
worktree-hygiene inspection does not surface them.

### A7 - why this run filed no numbered verdict

This run scanned the queue, found one LO-actionable item, and completed its full
independent verification. It filed no numbered verdict on
`gtkb-wi5441-global-registry-membership-reconciliation`, for these reasons:

1. **The thread is already terminal.** By the time verification completed, live
   bridge state read `VERIFIED` at `-012`. A `-013` `VERIFIED` would duplicate a
   correct verdict; a `-013` `NO-GO` would be substantively false, because this
   run's own evidence says the implementation is sound.
2. **Attempting finalization would probably have made it worse.** Per A4, the
   remaining packet window was shorter than the measured gate runtime, and per
   A11a the helper publishes before it commits. The likely outcome was a second
   stranded terminal verdict.
3. **Failing closed is the mandated posture.** `.claude/rules/loyal-opposition.md`
   requires fail-closed behavior when the commit cannot be created. Declining to
   publish is the fail-closed action; publishing and hoping is not.

The correct next action is a **finalization**, performed by a session that holds
a fresh implementation-start packet and can run the protected-commit gate to
completion without a tool timeout. It is not another review.

---

## Owner Decision Needed

**Status:** WI-5441 is blocked at terminal state. The registry work itself is
complete and verified; only the git commit is missing. WI-5640 Stage B remains
paused because it requires this thread genuinely terminal.

**Decision / Question:** WI-5441 rests at a published terminal `VERIFIED`
(`-012`) that no commit supports, and the thread has left the Loyal Opposition
queue, so no automated surface will raise it again. How should it be cleared -
by directing a finalization commit of the existing `-012` verdict plus its 32
declared paths, or by directing correction of the published bridge state first?

**Needed from Mike:** a direction on which of those two paths to take, and
whether recommendation 4 below (invert publish/commit ordering) should be
promoted to implementation-approved work now rather than queued.

**Why it matters:** this is the second stranded terminal `VERIFIED` in
twenty-four hours and at least the fourth session to hit the deadlock. Each
occurrence removes a thread from the queue while asserting verification that git
history does not support, which degrades the audit trail the bridge protocol
exists to produce.

**Options:**

- **A.** Direct a Prime Builder session to refresh the packet and create the
  finalization commit for the existing `-012`. Fastest unblock; leaves the
  ordering defect in place for the next thread.
- **B.** Direct correction of the published bridge state back to `REVISED`
  first, then re-finalize cleanly. Slower; produces a cleaner audit trail.
- **C.** Fix the publish/commit ordering (recommendation 4) first, then finalize
  through the corrected path. Slowest unblock; prevents recurrence.

**Reply requested:** one option label, plus a yes/no on promoting recommendation
4 to implementation-approved work.

This advisory requests no implementation authority and grants none. It is filed
under the standing Loyal Opposition advisory-capture authority in
`.claude/rules/codex-standing-priorities.md` on strategic self-improvement,
which permits recording evidence-based future-work candidates without an
approval barrier. Recommendations 4 through 8 are consideration candidates only;
none is implementation-approved by this filing.

---

## Recommended Prime Action

**Immediate (unblocks WI-5441 and WI-5640 Stage B):**

1. Refresh the implementation-start packet for
   `gtkb-wi5441-global-registry-membership-reconciliation` via
   `scripts/implementation_authorization.py begin --bridge-id`.
2. From a session able to run a thirteen-minute gate to completion, create the
   finalization commit containing the 32 declared paths plus the `-012` verdict
   artifact, with the intended subject already recorded in `-012`. Do **not**
   stage `groundtruth.db` - the by-reference waiver forbids it.
3. Do not re-run the reconciliation and do not re-execute either registry
   transaction. The registry is already in the intended state (2,346 records,
   coherent, identity current). Re-running would create needless transactions
   against a registry that is already correct.

**Structural (prevents recurrence):**

4. Invert the finalization order in `finalize_verified_commit` so bridge-state
   publication happens **after** the commit succeeds, making the transaction
   genuinely atomic. This is the single highest-value fix; it converts every
   future failure in this window from a silent strand into a clean retry.
5. Make the implementation-start packet TTL survive an independent verification
   cycle, or exempt reviewer-side finalization commits from packet expiry, so
   the mandated independent reviewer is not locked out by design.
6. Relax the auto-finalization sweep's "implementation already committed"
   precondition, or add a companion path that can finalize source-bearing
   strands, so the sweep covers the case that actually strands.
7. Correct the helper path in `.claude/rules/file-bridge-protocol.md`,
   `.claude/rules/loyal-opposition.md`, and `.claude/rules/codex-review-gate.md`
   to `.claude/skills/gtkb-verify/helpers/write_verdict.py`, and correct the
   stale `bridge-propose` resolution in the governed-writer driver precedent.
8. Wrap the `check_protected_commit_authorization.py` temp index in
   kill-tolerant cleanup (or place it under a swept state directory), and remove
   the nine existing leaked directories.

**Sequencing note.** Items 1 through 3 are the unblock and can proceed
independently. Item 4 should precede the next source-bearing finalization on any
thread; otherwise the next strand is a matter of timing, not chance.

**Verification expectation for the resulting work.** A fix for item 4 should be
provable by a test that simulates a commit-phase failure and asserts that bridge
state remains non-terminal and the thread remains LO-actionable afterward.

---

## Classification Slot

Recommended Prime Builder disposition: **adapt**.

The defect class is confirmed and the immediate unblock (items 1 through 3) is
mechanical and in-scope. The structural items (4 through 8) should be converted
into scoped GT-KB work items rather than adopted verbatim, because items 5 and 6
involve governance trade-offs - packet TTL and sweep preconditions are both
fail-closed controls, and loosening either has a process-safety cost the owner
should weigh explicitly.

Prime Builder disposition to be recorded on intake, one of: adopt, adapt,
reject, defer, monitor. Per `.claude/rules/peer-solution-advisory-loop.md`, an
adopt or adapt disposition requires the owner-grilling gate to run and its
AskUserQuestion evidence to land in the derived proposal's owner-decisions
section before that proposal is filed as `NEW`.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
