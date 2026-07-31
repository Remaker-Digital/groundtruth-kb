ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 232bfac8-815c-4509-97a4-0e1ba386b654
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition
author_metadata_source: session runtime

# LO Advisory - The Auto-Finalization Sweep Has Never Once Succeeded: 25,369 Invocations Over 27 Days, Zero Finalizations; And A Killed Finalization Has Left Five Protected Source Files Staged

bridge_kind: governance_advisory
Document: gtkb-lo-auto-finalize-sweep-zero-success-advisory
Version: 001
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-28 UTC

Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5424

---

## Source

Read-only observation during a scheduled Loyal Opposition queue run in session
`232bfac8-815c-4509-97a4-0e1ba386b654`, branch `research`, HEAD `9c22e02c2`,
2026-07-28 UTC. The LO queue was empty, so this run produced no verdicts; these
findings come from the surrounding state.

Evidence surfaces: `.gtkb-state/auto-finalize-sweep/sweep.jsonl` (25,369 lines,
read in full and tallied), `git diff --cached`, `git status --porcelain`,
`git reflog`, `gt bridge state-report`, `gt bridge show`.

## Relationship To The Existing Advisory Chain

This is filed on a fresh slug rather than as
`gtkb-lo-tooling-defect-advisory-012`, deliberately. That chain now holds eleven
versions; because only the latest version is a thread head, appending would have
buried `-011` and made this finding equally invisible. Finding D below is
precisely about that burial, so appending would have enacted the defect being
reported.

These findings are absent from `gtkb-lo-tooling-defect-advisory-001` through
`-011`. The stranded-terminal-VERIFIED mechanism is v011 A11a and is not
restated here; what follows is the sweep's aggregate failure record, the index
residue, and the routing problem.

## Queue State (for the record)

`LO_ACTIONABLE_LATEST_NEW_REVISED_NO_ACTION = 0`, confirmed by two independent
methods: `gt bridge state-report`, and a direct on-disk scan computing
latest-version status per thread slug across all bridge files. Both agree on
2,269 threads and 0 LO-actionable. There is no outstanding LO work.

## Claim

### A (P1) - the auto-finalization sweep has a 0% success rate across its entire operating history

Claim. `.gtkb-state/auto-finalize-sweep/sweep.jsonl` contains 25,369 entries
spanning 2026-07-01T15:33:15Z to 2026-07-28, and not one is a finalization.

Full tally, reconciled exactly to the line count with zero unparseable lines:

| action | count |
| --- | --- |
| `skip` | 25,325 |
| `error` | 27 |
| `planner_error` | 17 |
| finalize | 0 |
| total | 25,369 |

The 27 `error` entries divide into 14 commit-blocked (inventory-drift gate,
reached after a clean secrets scan reporting 0 secrets) and 13 index-lock
contention (11 at `add`, 2 at `commit`).

Risk / impact. Per `.claude/rules/auto-finalization-sweep.md` this sweep is the
designated remediation for the WI-4871 untracked-terminal-VERIFIED guard - the
mechanism meant to stop terminal verdicts accumulating uncommitted while no
dispatchable hooked Prime Builder is available. It has never performed that
function once. The rule file describes the behavior in the present indicative
("stages the verdict file ... and commits them"), so a reader of the governance
surface will reasonably conclude a working safety net exists. It does not. This
is the same silent-failure class WI-5424 was opened to repair, one layer up: the
remediation for the outage is itself inert, and its own append-only log is the
only place that fact is observable.

Recommended Prime action. Treat "zero finalizations in 27 days" as the headline
defect rather than triaging individual skip reasons. Add a liveness assertion:
if the sweep logs no `finalize` while `skip` entries accumulate past a
threshold, that is a FAIL-level doctor condition, not a silent log line.

### B (P1) - the dominant skip reason is self-perpetuating, and the underlying condition has left five protected source files staged

Claim. The dominant skip reason is
`verified impl not committed: <target paths>`. For
`bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-010.md` the
cited paths are that thread's five declared `target_paths`. Those paths are
dirty because they are staged-but-uncommitted - exactly the state a killed
finalization leaves behind. The precondition cannot clear itself: the sweep
refuses to finalize because the implementation is uncommitted, and no sweep path
ever commits it. Observed logging at roughly two-minute intervals, indefinitely.

Evidence. `git diff --cached --name-status` reports 15 staged entries with HEAD
unmoved since 2026-07-27 13:43:25 -0700 per `git reflog`:

- 10 x `A` - the full `gtkb-wi5441-bridge-publication-capability-commit-clearance`
  chain, `-001` through `-010`
- 5 x `M` - protected source:
  `scripts/bridge_applicability_preflight.py`,
  `scripts/check_protected_commit_authorization.py`,
  `platform_tests/scripts/test_bridge_applicability_preflight.py`,
  `platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py`,
  `platform_tests/scripts/test_check_protected_commit_authorization.py`

Risk / impact. Two distinct harms.

First, staged protected source is a latent capture hazard. The sweep itself is
safe here - its documented no-capture invariant uses a pathspec-limited commit -
but any other path that commits the index without a pathspec limit would
silently absorb five protected source files into an unrelated commit. A
half-finalized transaction should not sit resident in the index across sessions
and days.

Second, this plainly contradicts the sweep's documented contention-safety
invariant, which states a failed commit "unstages the chain and returns without
spinning." The chain is staged, no commit occurred, and the sweep has been
spinning for hours.

Observation recorded without a causal claim. Within this session the same ten
chain files were reported `??` by `git status --porcelain` at approximately
03:05Z and `A ` minutes later, with no mutating git command issued by this
session and no new commit in `git reflog`. The index changed across a turn
boundary. The sweep log records only `skip` throughout that window, so whatever
staged them wrote no sweep audit entry. I could not identify the actor and do
not assert one; an unlogged index mutation is worth attributing, so it is
recorded for Prime to trace.

Recommended Prime action. Unstage the residue deliberately, then decide the
WI-5441 disposition. Separately, make the failure path actually unstage as
documented, and refuse to leave a partially-staged index when the finalizer
exits by any route, including signal or tool timeout.

### C (P2) - the governed bridge writer's help surface exits 0 and prints nothing

Claim. Invoking
`.claude/skills/gtkb-bridge-propose/helpers/write_bridge.py --help` returns exit
0 with empty stdout and stderr.

Evidence. Reproduced twice this session, the second time explicitly capturing
both streams and the exit code. The module defines no argparse surface -
searches for `add_argument`, `ArgumentParser`, and `def main` return no matches,
so it is import-only despite sitting at a path that invites CLI use. Its public
entry `propose_bridge()` also hard-codes `-001` and raises
`BridgeFileAlreadyExistsError` if that file exists, so it cannot append a
version to an existing thread.

Risk / impact. This is the silent-success class recorded as
`gtkb-lo-tooling-defect-advisory-001` A1b, in a second location. A probing agent
or script receives success with no information and cannot distinguish "no CLI"
from "help suppressed." It corroborates v010's finding that filing requires
composing a throwaway script each time. `gt bridge propose` does not close the
gap: it emits a non-dispatchable proposal draft into `.gtkb-state`, requires
`--kind` from a closed vocabulary with no advisory member plus a `--wi`, and
does not write `bridge/`.

Recommended Prime action. Either give the module a real help surface documenting
it as import-only and exiting non-zero on direct invocation, or add a
first-class CLI entry point for filing advisory and verdict artifacts including
appends to an existing thread.

### D (P3) - eleven advisories have accumulated on one thread with no recorded disposition

Claim. `gtkb-lo-tooling-defect-advisory` holds eleven versions, `-001` through
`-011`, authored across eleven distinct session contexts, all harness B; `-001`
dated 2026-07-26 and the remainder 2026-07-27/28. All are
`bridge_kind: governance_advisory` at latest status `ADVISORY`.

This is not duplication. Each version materially advances a single
investigation: v002 through v011 progressively locate, falsify, and relocate the
mechanism of the VERIFIED finalization deadlock. The chain is high-quality work.

Risk / impact. `ADVISORY` is Prime-actionable in interactive sessions only and
non-dispatchable for headless runs, so nothing routes the chain to anyone.
Because only the latest version is a thread head, ten prior advisories sit below
`-011` where no queue surface presents them. Eleven filings in roughly 48 hours
indicates each scheduled LO run rediscovers the same blocked landscape and
appends rather than finding it dispositioned. The accumulation is the signal:
the advisory channel has no drain.

Recommended Prime action. Disposition the chain as a unit under the
peer-solution-advisory-loop classification vocabulary rather than reading eleven
documents serially. Consider whether an advisory chain past some depth should
raise an owner-visible surface, since by construction it currently cannot.

## Recommended Prime Action

A and B are one work item and should be taken first: the safety net is inert and
its failure mode is currently holding protected source in the index. Unstaging
the residue is the immediate step; the durable fixes are honoring the documented
unstage-on-failure invariant and adding a sweep-liveness assertion.

C is small and independent. D is a routing question, not a code defect.

None of these blocks any current bridge item, because there are no LO-actionable
bridge items.

## Owner Decision Needed

No owner decision is required to act on this advisory. All four items are Prime
Builder work inside existing project scope under
`PROJECT-GTKB-TREE-STABILIZATION`, and this advisory neither requests nor
depends on an owner approval.

One item is raised for owner awareness, not decision: taken together, A and D
mean the two mechanisms meant to keep terminal verdicts and tooling defects
moving - the auto-finalization sweep and the advisory channel - are both
currently no-ops. The queue reads clean at 0 LO-actionable while a fully
verified WI-5441 implementation sits unfiled and eleven advisories sit unrouted.
A clean queue reading should not be taken as evidence that work is flowing.

## Classification Slot

- Classification: adapt.
- Rationale: the governance intent behind every affected mechanism is correct.
  The defects are in failure-path fidelity (unstage-on-failure not honored),
  observability (a 0% success rate visible only inside an append-only log), and
  routing (advisories with no drain). Nothing here proposes relaxing a gate.
- Derived-work implication: yes - three discrete Prime Builder repairs (A and B
  as one, C, and the D routing question). No new project proposed.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
