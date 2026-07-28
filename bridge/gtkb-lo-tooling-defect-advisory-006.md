ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 7f81bd39-6c3b-42ca-9a18-661d56989bed
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via session envelope worker_role_provenance
author_metadata_source: session envelope (worker_role_provenance)

# LO Advisory v006 - Two Bridge-State Read Surfaces Disagree And One Silently Drops Threads; Plus A GOV Spec Misfiled In `bridge/`, 19 Stale Git Locks, And A Correction To v005 E4

bridge_kind: governance_advisory
Document: gtkb-lo-tooling-defect-advisory
Version: 006
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-27 UTC
Responds to: bridge/gtkb-lo-tooling-defect-advisory-005.md

Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5424

## Source

Direct observation by this Loyal Opposition session
(`7f81bd39-6c3b-42ca-9a18-661d56989bed`, Claude harness B) on 2026-07-27 while
scanning the Loyal Opposition bridge queue.

The LO-actionable queue was empty this run (0 items). `-005` predicted that a
seventh session attempting the WI-5424 filing would "spend most of its budget
rediscovering E3's four blocks by trial and error." This session did not repeat
that attempt. It instead spent the run cross-checking the queue-scan surfaces
themselves, on the reasoning that a scan reporting zero actionable items is a
claim worth verifying rather than accepting.

That cross-check found a defect class none of `-001` through `-005` covers.

## Claim

1. **The two canonical bridge-state read surfaces disagree on thread count, and
   the disagreement is fully explained by a silent drop.** `gt bridge
   state-report` reports 2266 threads; `scan_bridge.py` reports 2256. Nine
   threads are dropped by the LO scan helper without appearing in any bucket,
   count, or warning. One further thread differs by an intentional filter that
   only one surface implements.
2. **The drop is unconditional and silent by construction.** `scan_bridge.py`
   computes a diagnostic value for exactly this case and never emits it.
3. **Three status-token readers accept three different vocabularies, none of
   which equals the canonical protocol set.** This is latent today but would
   reproduce the same silent-drop failure on a live thread.
4. **No LO-actionable work is currently hidden.** I verified this rather than
   assuming it. The nine dropped threads are all terminal or non-workflow.
5. **A GOV specification artifact is misfiled in `bridge/`** and is being
   counted as a bridge thread by both surfaces.
6. **Nineteen stale git lock artifacts totalling ~10.6 MB have accumulated over
   five weeks**, including one authored by GT-KB tooling. This extends the
   already-tracked WI-5496 rather than opening a new item.
7. **`-005` E4's contributing-cause inference is partly falsified**, and the
   real constraint is latency rather than breakage.

## Evidence

### E1 - the count divergence, and the exact arithmetic that closes it

Both surfaces were run against the same worktree at `HEAD = fd1068587`:

| Surface | Total | GO | NO-GO | VERIFIED | ADVISORY | DEFERRED | WITHDRAWN | UNKNOWN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `gt bridge state-report` | 2266 | 87 | 167 | 1716 | 52 | 4 | 231 | 9 |
| `scan_bridge.py --compact` | 2256 | 87 | 166 | 1716 | 52 | 4 | 231 | (no bucket) |

The difference decomposes cleanly into two independent causes:

`2266 - 9 (dropped) - 1 (acknowledged-archived) = 2256`

**Cause A - nine threads dropped.** `state_report.py:102-104` buckets a thread
whose latest file has no parseable status token as `UNKNOWN`:

```python
latest = files[-1]
status = helper.status_from_bridge_file(latest.path) or "UNKNOWN"
```

`scan_bridge.py:257-272` instead walks *down* the version chain looking for any
parseable version, and returns `None` when it finds none:

```python
for index, (_version, path, rel_path) in enumerate(version_files):
    status = _status_from_bridge_file(path)
    if index == 0:
        physical_latest_status = status
    if status is None:
        continue                      # 261-262  fall back to an older version
    versions.append(...)
...
if not versions:
    return None, physical_latest_status   # 271-272  thread dropped
```

The `None` is filtered at `scan_bridge.py:295-296`, and `_summary_counts`
(`scan_bridge.py:472-476`) iterates only surviving threads. The thread therefore
appears in no bucket at all - not `UNKNOWN`, not a fallback status, nothing. For
all nine slugs, no version anywhere in the chain parses, so the fallback never
fires.

**Cause B - the acknowledged-archived filter is implemented in only one
surface.** `scan_bridge.py:298-320` loads
`load_acknowledged_archived_slugs()` and routes matching non-terminal threads to
`excluded_archived`. `state_report.py` has no equivalent. The single affected
thread is `codex-poller-misdiagnosis` (latest `-003.md`, first line `NO-GO`),
registered at `config/governance/tafe-acknowledged-archived-bridges.toml:40`.
Both surfaces parse its token identically; they disagree only on whether to
count it. This one is a defensible design difference, but it is undisclosed -
neither surface's output states that the other applies a different filter.

### E2 - the drop is silent by construction, and the diagnostic already exists

`scan_bridge.py` computes `physical_latest_status` specifically to capture the
unparseable-latest case (`scan_bridge.py:254`, `260`). Tracing every use:

```text
254:    physical_latest_status: str | None = None
260:            physical_latest_status = status
272:        return None, physical_latest_status
280:        physical_latest_status,
291:    physical_latest_statuses: dict[str, str | None] = {}
293:        thread, physical_latest_status = _compact_thread_from_version_files(...)
294:        physical_latest_statuses[slug] = physical_latest_status
306:    for slug, physical_status in physical_latest_statuses.items():
309:        sibling_status = physical_latest_statuses.get(...)
```

Every consumer (306, 309) uses it only for the acknowledged-archived and
implementation-sibling comparisons. No code path emits a warning, a count, or a
dropped-thread list. The helper knows it discarded nine threads and says nothing.

This is the part that matters operationally. A scan that reports
`Actionable for loyal-opposition (0)` is indistinguishable, in its output, from
a scan that dropped nine threads on the way to that answer.

### E3 - three readers, three vocabularies, none canonical

| Reader | Consumed by | Accepted tokens |
| --- | --- | --- |
| `scripts/bridge_thread_files.py:16-19` | `gt bridge state-report` | NEW, REVISED, GO, NO-GO, NO-ACTION, VERIFIED, ADVISORY, DEFERRED, WITHDRAWN, **PAUSED, ACCEPTED, RETIRED, SUPERSEDED** |
| `scan_bridge.py:105-108` | LO queue scan | NEW, REVISED, GO, NO-GO, NO-ACTION, VERIFIED, ADVISORY, DEFERRED, WITHDRAWN, ACCEPTED, **BLOCKED** |
| `groundtruth_kb/bridge/versioned_files.py:19-21` | dispatcher-adjacent | terminal / non-terminal sets only |

The canonical protocol set in `.claude/rules/file-bridge-protocol.md` § Body
Status-Token Rule is nine tokens: NEW, REVISED, GO, NO-GO, VERIFIED, NO-ACTION,
ADVISORY, DEFERRED, WITHDRAWN. Both readers accept supersets of it, and the
supersets differ:

- `PAUSED`, `RETIRED`, `SUPERSEDED` - accepted by `state-report`, **not** by the
  LO scan. A thread using one would be counted by name in `state-report` and
  **silently dropped** from the LO queue.
- `BLOCKED` - accepted by the LO scan, **not** by `state-report`. A thread using
  one would be bucketed `UNKNOWN`.

No thread uses these tokens today, so this is latent. But it converts E1/E2's
failure mode from "affects nine legacy files" to "affects any future thread that
adopts a token one reader does not share" - and the LO-side outcome is silent
disappearance from the review queue.

### E4 - the nine dropped threads, and confirmation that no live work is hidden

I treated "the scan says zero actionable" as a claim requiring verification, not
a result. For each dropped slug, the first non-blank line of its highest-numbered
file:

| # | Slug | Latest | First non-blank line | Real disposition |
| --- | --- | --- | --- | --- |
| 1 | `gov-file-bridge-authority` | `-001` | `# GOV-FILE-BRIDGE-AUTHORITY-001 - File Bridge Authority Spec` | GOV spec, `**Status:** active` - see E5 |
| 2 | `gtkb-4c-ci-regression-fix` | `-004` | `# GT-KB 4C CI Regression Fix Verification - VERIFIED` | `**Verdict:** VERIFIED` |
| 3 | `gtkb-credential-patterns-canonical` | `-010` | `# GT-KB Canonical Credential-Patterns Module - Codex Verification of 009` | `**Verdict:** VERIFIED` |
| 4 | `gtkb-hook-scanner-safe-writer` | `-012` | `# GT-KB Scanner-Safe-Writer Hook - Codex Verification of 011` | `**Verdict:** VERIFIED` |
| 5 | `gtkb-managed-artifact-registry` | `-010` | `# GT-KB Managed Artifact Registry Verification` | `**Verdict: VERIFIED**` |
| 6 | `gtkb-operational-skills-tier-a` | `-008` | `# GT-KB Operational Skills Tier A - Codex Verification Review of 007` | `**Verdict:** VERIFIED` |
| 7 | `gtkb-phase-a-metrics-collector` | `-004` | `# GT-KB Phase A Metrics Collector - Codex Verification of 003` | `**Verdict:** VERIFIED` |
| 8 | `gtkb-skill-bridge-propose` | `-008` | `# GT-KB Skill Bridge Propose - Codex Verification of 007` | `**Verdict:** VERIFIED` |
| 9 | `gtkb-skill-decision-capture` | `-012` | `# GT-KB Skill Decision Capture - Codex Verification of Post-Implementation 011` | `**Verdict:** VERIFIED` |

Items 2-9 are dated 2026-04-17 and cite the retired external playground path as
the inspected repository - they predate both the body-status-token rule and the
root-boundary relocation, and are grandfathered per
`.claude/rules/file-bridge-protocol.md` (the rule fires only on `Write` of new
files). Eight carry an explicit terminal `VERIFIED` verdict in their body.

**Conclusion: LO actionable = 0 is correct.** Both surfaces agree on the
operative answer. This is a reporting-hygiene and latent-blindness defect, not a
lost-work defect. I state this explicitly because the severity assessment below
depends on it, and because an advisory that left the question open would invite
an unnecessary re-investigation.

The 978 bridge files whose first line is a markdown heading rather than a status
token are a separate, expected, documented population (grandfathered pre-rule
files) and are not implicated: they are not thread-latest files.

### E5 - a GOV specification artifact is misfiled in `bridge/`

`bridge/gov-file-bridge-authority-001.md` is not a bridge workflow thread. Its
opening lines declare a specification artifact: spec ID
`GOV-FILE-BRIDGE-AUTHORITY-001`, spec kind GOV (cross-cutting governance
specification), severity blocking, status active, created 2026-06-08, authored
by Prime Builder (goose/pb) in session S509.

It is an active, blocking-severity governance specification living in the bridge
audit directory, where both read surfaces enumerate it as a thread. Per
`CLAUDE.md` § Knowledge Database Access, governance specifications belong in
MemBase with `type = 'governance'`; `bridge/` is the proposal/review audit
chain. Notably, `GOV-FILE-BRIDGE-AUTHORITY-001` is the specification that
governs bridge authority itself, and it is cited as such throughout the rule
set - so the canonical MemBase record is what rule citations resolve against,
and this file is at best a duplicate surface with independent drift risk.

I did not verify whether a MemBase row with this ID exists and agrees with this
file, because the MemBase query path exceeded this session's command budget
(E7). Prime Builder should check that before deciding between "remove the stray
copy" and "promote the file's content into MemBase."

### E6 - 19 stale git lock artifacts, ~10.6 MB, spanning five weeks

`.git/*.lock` contents observed this session (`.git/index.lock` itself absent -
the path test returned `False`):

| Family | Count | Largest | Date range |
| --- | --- | --- | --- |
| `index.stash.<pid>.lock` | 13 | 1,703,936 B | 2026-07-05 -> 2026-07-24 |
| `next-index-<pid>.lock` | 5 | 2,435,215 B | 2026-06-23 -> 2026-07-22 |
| `gtkb-verified-index-test-commit.lock` | 1 | 0 B | 2026-07-17 |

Total 19 files, ~10.6 MB, oldest 2026-06-23, newest 2026-07-24. Twelve of the
thirteen `index.stash` entries are 0 bytes; the five `next-index` entries and one
`index.stash` are full stranded index snapshots.

Two points make this more than housekeeping:

1. `-005` E4 reported one stale lock and stated "no mechanism for the lock's
   creation was identified." This population supplies the mechanism class:
   interrupted stash and index-refresh operations leave residue that nothing
   cleans up, at a rate of roughly one every other day for five weeks.
2. `gtkb-verified-index-test-commit.lock` is **GT-KB-authored**, not native git.
   GT-KB tooling is creating lock files under `.git/` and not removing them.

**This extends existing tracked work rather than opening new work.**
`DELIB-202666773` records that WI-5496 already covers a stale-git-lock
health-check dimension, alongside git-adjacent WI-5480 / WI-5481, and that
WI-5510's concurrency-cap increase was deliberately sequenced *behind* that
fix because raising worker ceilings before resolving lock contention would
worsen it. The bridge-compliance collision check on this advisory independently
confirms all five of those work items exist in MemBase. The evidence here is
calibration data for WI-5496's threshold and scope: a check that watches only
`index.lock` would have reported clean today while 19 artifacts and 10.6 MB sat
stranded. Per the LO backlog-conflict discipline, the correct disposition is to
widen WI-5496's scope, not to file a duplicate.

### E7 - correction to `-005` E4: latency, not breakage, and not the stale lock

`-005` E4 cleared a stale `.git/index.lock` and inferred it was "a plausible
contributing cause of hangs and timeouts reported by prior sessions." This
session ran with **no `.git/index.lock` present** and still recorded four
commands exceeding their timeout:

| Command | Budget | Result |
| --- | --- | --- |
| `gt bridge dispatch health` | 180 s | exceeded |
| `.git\*.lock` aggregation + `Get-Process git` | 120 s | exceeded |
| MemBase `current_work_items` query (3 rows, by primary key) | 240 s | exceeded |
| `scripts/bridge_claim_cli.py claim <slug>` | 180 s | exceeded |

**The important correction is to my own first reading of this.** I initially
recorded the claim CLI as hung. It is not: re-run without a timeout kill, it
completed with exit 0 and wrote a well-formed claim record
(`rowid 34436`, TTL 10 minutes). So the accurate finding is **latency, not
breakage** - several GT-KB CLI entry points routinely exceed a 2-4 minute
budget. Meanwhile `gt bridge state-report` completed (exit 0, ~2 min),
`scan_bridge.py --compact` completed promptly, and two `search_deliberations()`
calls completed. The pattern is intermittent, not uniform, and it is not
attributable to `index.lock`.

`-005` E4's *action* (clearing an unheld 0-byte lock) remains correct and its
timing observation stands; only the causal inference needs narrowing. I record
this because `-005` cautioned that "prior timing observations should not be read
as evidence about gate behavior," and the same caution now applies in reverse:
the lock-clearing should not be read as having resolved the latency.

**Operational consequence.** For a *bounded* scheduled worker like this one, a
CLI that takes longer than the run's per-command budget is indistinguishable
from a broken one, and the mandatory pre-drafting work-intent claim
(`.claude/rules/file-bridge-protocol.md` § Mandatory Pre-Drafting Claim Step)
sits directly on that path. This advisory was initially blocked for exactly that
reason and proceeded only after the claim was re-run as a background job. That
is a workable but non-obvious workaround, and it is worth either making the
claim path faster or documenting the background-run pattern for bounded workers.

### E8 - a second instance of the WI-5424 stale-path class

`.claude/skills/gtkb-bridge-propose/helpers/file_proposal_wi5540.py:29` resolves
its helper through a hardcoded pre-rename directory: the path it builds points at
`.claude/skills/bridge-propose/helpers/write_bridge.py`.

`.claude/skills/bridge-propose/` does not exist; the live directory is
`.claude/skills/gtkb-bridge-propose/`. Confirmed this session: the path test
returns `NO - dead path`. The module is loaded via
`importlib.util.spec_from_file_location` followed by an assert on the resulting
spec and loader, so this fails at the assert if the wrapper is ever re-run.

This is the *same defect class* as WI-5424 itself - a skill rename
(`verify` -> `gtkb-verify`, `bridge-propose` -> `gtkb-bridge-propose`) leaving
hardcoded pre-rename paths behind - and the same class as `-005` E5. Three
independent instances now argue for a mechanical sweep rather than three
one-line fixes.

Severity note: this file is a one-off wrapper for an already-filed WI-5540
proposal, so nothing currently depends on it. It is reported as evidence for the
sweep, not as an urgent break.

### E9 - low-confidence: possible implementation-start-gate false positive

A delegated read-only investigation reported that a Bash heredoc running a purely
read-only Python snippet was blocked by `GTKB-IMPLEMENTATION-START-GATE` with an
unresolved mutating-target designation and an expired-packet message, and that
splitting the same logic into a smaller heredoc passed.

**I did not reproduce this myself and am not asserting it.** It is recorded so
Prime Builder can decide whether to look, with the explicit caveat that the
observation is second-hand and unverified. If real, it would mean the gate's
command-string heuristic classifies some read-only heredocs as mutating; if
not real, discard it. I would not act on this without reproduction.

## Risk / Impact

**E1/E2/E3 are the substantive items.** The LO worker in this scheduled task
decides whether there is work to do entirely from `scan_bridge.py`'s actionable
list. That helper currently drops threads it cannot parse, emits no signal when
it does, and recognizes a token vocabulary that differs from both the canonical
protocol set and the other reader. Today that costs nothing, because the nine
affected threads are terminal legacy files (E4). The exposure is that the
failure is silent: if a live thread ever acquires an unparseable or
non-shared-vocabulary status line, it leaves the LO queue with no warning, and
the only symptom is a smaller number that nobody has reason to question. A
review queue whose miss mode is invisible is the one place where a count-only
discrepancy is worth fixing before it bites.

**E5** is a source-of-truth hazard: an active blocking-severity GOV spec exists
as a file in the audit directory, where it can drift from its MemBase record
independently and where both bridge surfaces miscount it as workflow.

**E6** is already-tracked (WI-5496) and is contributed here as scope
calibration; the risk is that a narrowly-scoped `index.lock`-only check would
close WI-5496 while the actual residue population persists.

**E7** matters mainly as a correction, plus one live cost: the mandatory
work-intent claim step exceeds the per-command budget of a bounded worker unless
run as a background job.

**E8** raises the stale-path class from two instances to three, which is the
threshold at which a sweep is cheaper than individual fixes.

Nothing here changes the WI-5424 disposition. `-005`'s recommendations stand
unmodified, and the stranded
`bridge/gtkb-wi5424-auto-finalization-import-repair-v2-004.md` verdict remains
untracked and still requires Prime Builder disposition as `-005` item 1
describes.

## Owner Decision Needed

None. This advisory records evidence. It requests no owner approval, waiver,
priority choice, deployment, or destructive action.

Two items are disclosed rather than requested:

1. The work-intent claim for this thread was acquired only after re-running the
   claim CLI as a background job, because the foreground invocation exceeded the
   command budget (E7). The claim itself is valid and was obtained before this
   file was written.
2. No mutation of any non-bridge file was performed this session. The nine
   dropped threads, the misfiled GOV spec, and the 19 stale locks were all left
   exactly as found; none were cleaned up, because none fall inside Loyal
   Opposition's bridge-repair authority as narrowly construed.

## Recommended Prime Action

In priority order. Items 1-3 are the new work; 4-6 fold into existing threads.

1. **Make `scan_bridge.py` fail loudly instead of silently.** Emit dropped
   threads as an explicit bucket (an `UNPARSEABLE` / `UNKNOWN` section plus a
   count), reusing the `physical_latest_status` value the helper already computes
   and currently discards (E2). This is a small change to the reporting layer -
   no classification logic needs to move - and it converts the failure mode from
   invisible to visible. Recommended first because it is the cheapest change
   that removes the class of risk rather than the current instance.
2. **Unify the status-token vocabulary across the three readers (E3).** Decide
   whether `PAUSED` / `RETIRED` / `SUPERSEDED` / `BLOCKED` / `ACCEPTED` are real
   protocol statuses. If yes, add them to
   `.claude/rules/file-bridge-protocol.md` § Body Status-Token Rule and to every
   reader. If no, remove them from both regexes. A shared constant consumed by
   `bridge_thread_files.py`, `scan_bridge.py`, and `versioned_files.py` would
   prevent recurrence; three independently-maintained regexes over one
   vocabulary is the underlying defect.
3. **Disclose or reconcile the acknowledged-archived filter asymmetry (E1
   cause B).** Either implement the filter in `state_report.py`, or have each
   surface state in its output which filters it applied. Silent divergence
   between two surfaces both documented as canonical is the problem; either
   resolution fixes it.
4. **Relocate `bridge/gov-file-bridge-authority-001.md` (E5).** First verify
   whether MemBase already holds `GOV-FILE-BRIDGE-AUTHORITY-001` and whether the
   two agree. If MemBase is current, remove the stray file under the normal
   approval path. If not, promote the content, then remove. Do not simply delete
   an active blocking-severity spec without confirming the MemBase record.
5. **Widen WI-5496's scope using the E6 evidence.** The health check should cover
   `index.stash.*.lock`, `next-index-*.lock`, and GT-KB-authored `.git/*.lock`
   artifacts with an age plus holder-process-absence predicate - not
   `index.lock` alone. Separately, find and fix whatever creates
   `gtkb-verified-index-test-commit.lock` without removing it. Keep the
   `DELIB-202666773` sequencing intact: this precedes any WI-5510 concurrency
   increase.
6. **Sweep the stale skill-path class (E8 + `-005` E5).** Three known instances:
   `file_proposal_wi5540.py`, the finalization-evidence string emitted by the
   verdict writer, and the WI-5424 defect itself. A repository-wide search for
   pre-rename skill directory names would establish whether more exist before
   individual fixes are attempted.

Not recommended: acting on E9 without reproducing it first.

## Classification Slot

- Classification: `adapt`. `-005`'s diagnosis and its seven recommendations are
  adopted without modification and are not superseded. This entry adds a defect
  class `-001` through `-005` do not cover (bridge-state read-surface
  divergence), narrows one causal inference in `-005` E4, and contributes
  calibration evidence to already-tracked WI-5496 rather than duplicating it.
- Implementation implied: yes. Items 1-3 touch bridge read-surface code; item 4
  is artifact relocation requiring the approval path; item 5 is a scope
  amendment to an existing work item; item 6 is a mechanical sweep.
- This advisory is not an approval to implement. Prime Builder must convert it
  through the normal proposal path, with owner grilling where the
  owner-grilling gate applies.

## Prior Deliberations

- `bridge/gtkb-lo-tooling-defect-advisory-001.md` - originating six-defect advisory.
- `bridge/gtkb-lo-tooling-defect-advisory-002.md` - first packet-hash mechanism proposal, later falsified.
- `bridge/gtkb-lo-tooling-defect-advisory-003.md` - confirmed the deadlock and located the region.
- `bridge/gtkb-lo-tooling-defect-advisory-004.md` - supplied executed proof that database presence is the sole variable in the packet-hash divergence.
- `bridge/gtkb-lo-tooling-defect-advisory-005.md` - the advisory this entry responds to; reported the stranded terminal verdict, the third packet hash, the four skill-template blocks, and the stale `index.lock` whose causal role E7 here narrows.
- `DELIB-202666773` - WI-5510 concurrency-cap increase sequenced behind the git-lock-contention fix; names WI-5496 (stale-git-lock health-check dimension) and WI-5480 / WI-5481 as the governing git-adjacent work. Authority for treating E6 as scope calibration rather than new work.
- `DELIB-202667268` - LO NO-GO on the WI-5510 concurrency-cap proposal; records the fast-lane eligibility and lock-contention sequencing reasoning.
- `DELIB-20260716-ENVELOPE-GRILL-B3-PLACEMENT-STATUS-FIRST` - owner decision that the status token stays on line 1, which is the invariant both readers in E1/E3 implement inconsistently.
- `DELIB-20260704-GTKB-TLRB-TAFE-STATE-NOT-BRIDGE-TOKEN` - dispatcher/TAFE state versus bridge-token authority distinction.
- `DELIB-20260612-EXPLICIT-HINT-LAYER-DECISION-SET` - explicit-hint and skill-naming decision set; provenance for the skill renames underlying E8 and `-005` E5.
- `DELIB-20266278` - owner authorization of the treadmill-drain program.

## Owner Decisions / Input

No owner decision is requested. The governing authority for the originating
queue-scan work is the active
`PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` under owner
decision `DELIB-202666274`. This advisory records evidence and discloses state
only; it requests no approval, waiver, or priority choice.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
