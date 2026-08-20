<!--
THIS FILE IS A PROJECTION, NOT CANONICAL.
Projected from the neutral harness baseline by the GT-KB projection engine.
Do not edit here: change the baseline (.harness-baseline-configuration) and re-project with
`gt harness project claude`. If a needed change cannot be made through
the baseline and re-projection, file a work item against the projector
(GOV-HARNESS-NEUTRAL-BASELINE-001 obligation 6).
-->
# Bridge Is Essential - Top-Priority Mandate

This rule auto-loads via `.claude/rules/` convention and is TRACKED in git
(negated from the `.claude/` blanket ignore). Do not remove it.

## The Mandate

**Bridge integrity is the top-priority task. Always.**

> Bridge state plus status-bearing versioned files under
> `bridge/` are canonical. Aggregate queue artifacts are not live bridge state.

The Prime Builder / Loyal Opposition bridge is how GroundTruth-KB coordinates
implementation proposals, reviews, and verification. GroundTruth-KB is
non-functional when the bridge stops working. Therefore: keeping the
bridge state correct and consistent with the
versioned bridge file chain is the first duty of every Prime Builder session,
ahead of feature work, backlog progress, test runs, deployments, and
documentation updates.

The bridge as a protocol (proposal -> review -> revise -> GO/NO-GO -> implement
-> post-impl -> VERIFIED, all recorded in versioned files under `bridge/`) is
permanently in force. Any proposal, refactor, or cleanup that would weaken the
protocol's audit trail, GO/NO-GO discipline, or bridge-state
authority must be rejected.

## Operational Mode

**The owner dispatches bridge work manually. There is no automated dispatch
substrate.**

Dispatcher Next is the single future dispatcher. It is an active pre-release
objective and is **not yet ready for activation**. Until the owner activates it,
manual owner assignment is the whole of bridge dispatch, and no automated
substrate may be introduced or restored to stand in for it.

Agents may report dependencies, contention, and readiness. Agents must not
direct the owner's target selection or ordering, and must not assume that
filing an artifact causes anything to be scheduled.

Work as though Dispatcher Next already controls scheduling: do not rely on
direct cross-session communication, on continuing ownership of a work item, or
on returning to an in-flight item after filing. Each bridge action stands on its
own.

## No Automated Dispatch Substrate

There is no live automated dispatch substrate. Do not create one, restore one,
or treat any script, scheduled task, hook, or poller as one.

Harness topology affects which harness the owner may assign work to. It does not
authorize an automation substrate.

## How Bridge Work Reaches a Session

Bridge work reaches an interactive session by **prompt-time surfacing**. There
is no automated dispatch axis, and none may be created.

### Prompt-time surfacing (the only automation surface)

`.claude/hooks/bridge-axis-2-surface.py`, registered via
`hooks/manifest.toml`, surfaces newly-actionable bridge work into the next
prompt as additional context when an interactive session is active. It is
pull-based: it informs a session that is already running. **It dispatches
nothing and spawns nothing.**

A harness whose interaction model supports scheduled thread automation may
instead surface the same information by periodically waking its own interactive
session (inventoried under `config/agent-control/system-interface-map.toml`).
Both forms surface; neither dispatches.

Work that cannot be surfaced this way — owner decisions requiring
`AskUserQuestion`, multi-turn review where context accumulates, cross-thread
coordination, implementation interleaved with owner approval — is assigned by
the owner directly.

### Adding new bridge automation

DO NOT create bridge automation that dispatches, spawns, schedules, or assigns
work. That is Dispatcher Next's role and it is not yet activated.

A new *surfacing* mechanism requires:

1. Owner approval via `AskUserQuestion`.
2. An explicit statement that it surfaces only and dispatches nothing.
3. A `[[systems]]` entry in `config/agent-control/system-interface-map.toml`.
4. An update to this section if it overlaps an existing surface.

## Invariants (Bridge Protocol Itself)

These remain in force regardless of how bridge work is surfaced or assigned:

- bridge state plus status-bearing versioned files under `bridge/`
  are the canonical workflow state. Do not recreate aggregate queue artifacts
  to satisfy stale helpers.
- Bridge files are append-only. Never delete a bridge file; it forms the audit
  trail.
- Per-thread versioning is monotonic. Statuses are NEW, REVISED, GO, NO-GO,
  VERIFIED, ADVISORY, DEFERRED, and WITHDRAWN.
- The full `Document:` block must be read before acting on any single version of
  that thread.
- Scoped commits only. Bridge work commits should not bundle unrelated source
  changes.

Do NOT, without explicit owner approval:

- Recreate aggregate queue artifacts as live bridge state or treat them as authoritative
- Delete bridge files (any version)
- Skip the GO/NO-GO discipline for any code change beyond the explicit
  exemptions in `.claude/rules/counterpart-review-gate.md`
- Re-enable the retired OS poller tasks, freshness hook, foreground
  watchdog, or the retired smart-poller scheduled task / VBS daemon /
  runner as the active automation path

## Incident History (Lessons Encoded)

- **S290-S292**: Windows OS poller broke (`$MAX_ITEMS_PER_SPAWN:` parsed as a
  drive-scoped variable). The outage was silent for ~6 hours because nothing
  surfaced freshness in the owner's chat stream. Lesson: if poller-freshness
  ever returns, the visibility indicator must be independent of the poller it
  monitors.
- **S292**: Session-start briefs for 7+ sessions silently omitted the in-session
  `CronCreate` poller instantiation. Failure was invisible because no alarm
  fired when instantiation was skipped. Lesson: procedural mandates documented
  in `memory/*.md` are not enforceable; hooks and `.claude` hook
  registration are.
- **S294**: Discovered `.claude/` was blanket-ignored in `.gitignore`, so the
  bridge visibility infrastructure lived outside git. Worktrees could not see
  it. Fresh clones could not see it. Lesson: if it is essential, it must be
  tracked. The `!`-negation patterns added then remain in force for the rule
  files and PS1 scripts even though the retired hook itself is now removed.
- **S308 (2026-04-25)**: Former OS poller activation produced ~12.5M
  tokens/day of background spawns (a ~10× jump), most spawning a harness that found no
  actionable work, because each fixed-interval tick spawned a harness
  unconditionally regardless of whether the bridge had changed. Owner directive halted the retired pollers and removed the
  freshness hook, restoring manual-trigger operation until smart-poller
  automation is available. The protocol itself was unaffected; bridge state
  is canonical. Lesson: automation is
  wasteful when it spends an expensive resource — principally agent
  investigation tokens — without a commensurate chance of value; the cheap
  fixed-interval check was never the defect, the unconditional expensive spawn
  was. The remedy is to gate the expensive action behind a cheap, deterministic
  check (the daemon actionable-signature check), evaluated as
  relative value vs. cost per action.
- **S339 (2026-05-09)**: Smart-poller retirement (Slice 4). Smart-poller
  scheduled task `GTKB-SmartBridgePoller` halted; runtime artifacts
  archived to `archive/smart-poller-2026-05-09/`; doctor's
  `_check_smart_bridge_poller` removed. Lesson, stated as history and not as
  current direction: dispatch-on-actionable-change was the load-bearing
  semantic that successive substrates tried to preserve while changing the
  mechanism underneath it. Every substrate named in this history — the OS
  pollers, the smart poller, and the daemon that replaced them — has since been
  retired. Dispatch is now manual until Dispatcher Next is activated; see
  § Operational Mode.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
