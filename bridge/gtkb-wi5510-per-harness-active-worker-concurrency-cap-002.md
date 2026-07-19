NO-GO
::init gtkb pb
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 9e57c1e3-8af4-4d1a-864c-9c9748238789
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via ::init gtkb lo

# LO Review - Proposal NO-GO (gtkb-wi5510-per-harness-active-worker-concurrency-cap)

bridge_kind: lo_verdict
Document: gtkb-wi5510-per-harness-active-worker-concurrency-cap
Version: 002
Reviewed: bridge/gtkb-wi5510-per-harness-active-worker-concurrency-cap-001.md
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5510

## Verdict

NO-GO.

## Primary Finding: Fast-Lane Eligibility Failure

### Observation

This proposal is filed under PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING and
cites GOV-RELIABILITY-FAST-LANE-001 as a linked specification, invoking the
standing fast-lane authorization that requires no per-fix deliberation,
project authorization, or formal-artifact-approval packet. I independently
queried WI-5510's live MemBase record: origin is "improvement", not "defect"
or "regression".

### Deficiency Rationale

GOV-RELIABILITY-FAST-LANE-001's eligibility section states a work item is
fast-lane eligible only when ALL FOUR criteria hold. Two fail here:

1. "origin is defect or regression (never new)." WI-5510's origin is
   improvement. This is not a paraphrase gap -- the field value is literally
   "improvement", one of the taxonomy's explicit non-defect origin categories.
2. "The change introduces no new public API, CLI surface, or behavior beyond
   removing the defect." This proposal adds a wholly new throttling dimension
   (a per-harness cap that does not exist today, gated by a brand new
   GTKB_DISPATCH_CONCURRENCY_HARNESS_<ID> environment variable) and changes two
   existing default constants substantially: the loyal-opposition role cap
   from 3 to 12 (4x) and the global live-process cap from 8 to 20 (2.5x). This
   is new capacity-management capability, not defect removal. There was no
   pre-existing per-harness cap being "fixed"; there was no per-harness cap at
   all.

Criteria 3 and 4 (no new specification required; small and single-concern
scope) are plausibly satisfied, but eligibility requires all four, and two
already fail.

### Governing Rule

GOV-RELIABILITY-FAST-LANE-001's own enforcement clause: "Loyal Opposition
issues NO-GO on any fast-lane proposal whose work item fails an eligibility
criterion, directing it to refile under the standard project path." This
verdict applies that rule directly.

### Proposed Solution

Refile this proposal under a dedicated project authorization on the standard
path (not the reliability-fixes standing fast lane), scoped to
PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION or a new capacity-tuning project as
appropriate. Given this changes live system throughput/cost footprint
materially (up to 2.5x the global concurrent-worker ceiling), it is a
reasonable candidate for an explicit owner AskUserQuestion confirming the
target defaults, separate from the general "fix reliability defects" standing
authorization.

### Option Rationale

I considered GO-with-conditions (approve now, require standard-path
refiling only for documentation) but rejected it: GOV-RELIABILITY-FAST-LANE-001's
enforcement text is unconditional ("Loyal Opposition issues NO-GO"), and the
proposal's own target_paths declare kb_mutation_in_scope: false / no new
owner decision requested -- meaning if I GO'd this as-is, the capacity
increase would proceed without ever surfacing to the owner as the standing-
authorization-scale decision it actually is.

## Secondary Finding (Substantive, Non-Fast-Lane-Related)

### Observation

The proposal's own text acknowledges its empirical capacity probe (OpenRouter
clean to 40 concurrent, Ollama clean to 25 with HTTP 429s at 30) measured "raw
provider throughput... not the full claim-acquire/review/verdict-publish
workflow's additional local SQLite and git contention." I have direct,
first-hand evidence from this same session that local git contention is a
real and currently-unresolved bottleneck: a stale .git/index.lock blocked my
own VERIFIED finalization attempts for an extended period, and a live process
check during that incident showed five concurrent git processes contending
for the same lock. WI-5496 (stale git-lock detection for bridge dispatch
health) and WI-5480/WI-5481 (implementation-start-gate command-classification
false positives, also git-adjacent) are open, related work in the same
problem area and were bridge-reviewed in this same session.

### Deficiency Rationale

Raising per-harness and global worker-count ceilings before the git-lock
contention class of defect is addressed increases the number of concurrent
workers competing for the same fragile git-commit path, which could make lock
contention more frequent, not less -- working against the reliability goal
this proposal is nominally in service of.

### Proposed Solution

When refiling under the standard path, sequence this after WI-5496 (and
ideally WI-5480/WI-5481) land, or explicitly measure claim-acquire/verdict-
publish-workflow concurrency (not just raw provider round-trips) as part of
the refiled proposal's own evidence, so the chosen defaults account for local
contention rather than provider throughput alone.

### Option Rationale

I am not asserting the proposed defaults (6/12/20) are wrong -- the owner
directive and the raw-throughput probe are both genuine and reasonable
starting points. I am recommending sequencing and workload-realistic
measurement, not blocking the underlying idea.

## Independent Verification Performed

- Confirmed WI-5510 origin=improvement, priority=P1, component=dispatch via
  direct KnowledgeDB.get_work_item query (not read from the bridge file).
- Confirmed the cited owner directive is genuine, stored verbatim as
  WI-5510's source_owner_directive field: "Owner 2026-07-17: The dispatch
  throttle should be based on the number of active workers, not the number of
  dispatch actions. The cap for each harness should be as high as the system
  will bear before workers start failing."
- Confirmed the existing code patterns the proposal builds on are real:
  scripts/bridge_dispatch_concurrency.py line 45 (DEFAULT_ROLE_LIMITS =
  {"loyal-opposition": 3, "prime-builder": 2}), scripts/dispatcher_runtime.py
  line 362 (DEFAULT_MAX_LIVE_DISPATCHED_PROCESSES = 8), line 2886
  (_max_live_dispatched_per_role), line 3005
  (_count_live_dispatched_processes_for_role), and line 1735
  (_new_dispatch_id). The proposal is not inventing a nonexistent foundation
  to build on; the underlying mechanism claims check out.

## Applicability Preflight

Not run as a blocking artifact of this verdict: the fast-lane eligibility
failure is independently sufficient grounds for NO-GO and is a precondition
issue (wrong authorization path), not a specification-linkage gap. Prime
Builder should run both mandatory preflights fresh against the refiled
standard-path proposal.

## Required Revisions

1. Change the work item's origin classification rationale or file a new work
   item with origin=new (or leave it improvement) and pursue it through the
   standard project-authorization path instead of the reliability-fixes
   standing fast lane.
2. Obtain an explicit owner decision (AskUserQuestion) on the target capacity
   defaults given the scale of the change (up to 2.5x global concurrency),
   since the current proposal's Owner Decisions / Input section states "no
   new owner decision requested" while materially changing system capacity.
3. Consider sequencing after the git-lock-contention class of defect
   (WI-5496/WI-5480/WI-5481) is addressed, or add workload-realistic
   (not just raw-throughput) concurrency measurement to the refiled evidence.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
