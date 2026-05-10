# Bridge Is Essential - Top-Priority Mandate

This rule auto-loads via `.claude/rules/` convention and is TRACKED in git
(negated from the `.claude/` blanket ignore). Do not remove it.

## The Mandate

**Bridge integrity is the top-priority task. Always.**

The Prime Builder / Loyal Opposition bridge is how GroundTruth-KB coordinates
implementation proposals, reviews, and verification. GroundTruth-KB is
non-functional when the bridge stops working. Therefore: keeping the bridge
canonical state correct and accurately reflected in `bridge/INDEX.md` is the
first duty of every Prime Builder session, ahead of feature work, backlog
progress, test runs, deployments, and documentation updates.

The bridge as a protocol (proposal -> review -> revise -> GO/NO-GO -> implement
-> post-impl -> VERIFIED, all recorded in versioned files under `bridge/`) is
permanently in force. Any proposal, refactor, or cleanup that would weaken the
protocol's audit trail, GO/NO-GO discipline, or INDEX.md as canonical state must
be rejected.

## Operational Mode (current as of 2026-05-09)

**Both the retired OS bridge pollers (halted 2026-04-25) and the smart
poller (retired 2026-05-09) are disabled. The cross-harness event-driven
trigger is the canonical bridge automation path while it remains healthy.**

The owner directive that halted OS pollers on 2026-04-25 applied to the
former token-heavy implementation: Windows scheduled tasks
`AgentRedFileBridgeIndexScan-Claude`, `AgentRedFileBridgeIndexScan-Codex`,
`AgentRedBridgeLivenessAlert`, and `AgentRedPollerLivenessWatcher`; the
`.claude/hooks/poller-freshness.py` `UserPromptSubmit` hook; and the
foreground `Agent Red Bridge Monitor` watchdog startup shortcut. Those
retired mechanisms must not be restored as the active automation path.

The Slice 4 retirement on 2026-05-09 (per
`bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-*`)
extended that retirement to the smart poller: the Windows scheduled task
`GTKB-SmartBridgePoller`, the VBS daemon `scripts/run_smart_bridge_poller.vbs`,
the PowerShell wrapper `scripts/run_smart_bridge_poller.ps1`, the install /
uninstall scripts, and the runner `groundtruth-kb/scripts/bridge_poller_runner.py`
have all been archived to `archive/smart-poller-2026-05-09/`. The
`_check_smart_bridge_poller` doctor check has been removed; bridge dispatch
liveness is now reported by `_check_bridge_dispatch_liveness` and
`_check_cross_harness_trigger` (per Slice 4 D4).

Bridge dispatch automation is provided by the cross-harness event-driven
trigger at `scripts/cross_harness_bridge_trigger.py`, registered as
PostToolUse and Stop hooks in `.claude/settings.json` and
`.codex/hooks.json`. The trigger fires on tool-use and Stop events rather
than on a fixed interval. When `bridge/INDEX.md` is modified by a tool
call or the agent ends a turn, the trigger inspects the indexed state and
dispatches the appropriate counterpart harness if a recipient's actionable
queue signature has changed (Codex on latest NEW or REVISED; Prime on
latest GO or NO-GO). VERIFIED is terminal and not dispatched. The trigger
is monitoring and dispatch infrastructure only; `bridge/INDEX.md` remains
the canonical workflow state. Per-recipient dispatch state is recorded at
`.gtkb-state/bridge-poller/dispatch-state.json` (path retained for
compatibility with the smart-poller substrate).

Manual fallback remains available when the trigger is unhealthy (per the
doctor predicate above) or intentionally stopped: the owner triggers a
Prime bridge scan with a brief prompt such as `Bridge` or `Bridge scan`,
Prime then reads `bridge/INDEX.md` and acts on actionable entries. Codex
bridge scans are similarly owner-triggered in the Codex harness.

The 2026-04-25 OS-poller halt was made after the former OS Claude poller
(activated ~2026-04-23) drove a ~10x session token-cost regression: 173
Claude capped-spawns/day at peak, plus 92 Codex spawns/day, each costing
~50k tokens. The 2026-05-09 smart-poller retirement was made after a
S321 daemon-dispatch-disabled incident exposed ongoing scoping ambiguity
between interval-driven dispatch and event-driven dispatch (per
`PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001`); the Slice 4 retirement
preserves the dispatch-on-actionable-change semantic while removing the
interval-driven substrate. The lesson applies to both retired
implementations.

## Bridge Dispatch Enablement Contract

The cross-harness event-driven trigger is opt-out, not opt-in, once all of
these are true:

1. The trigger script (`scripts/cross_harness_bridge_trigger.py`) is
   present in the GT-KB platform.
2. The trigger registrations in `.claude/settings.json` (PostToolUse +
   Stop) and `.codex/hooks.json` (PostToolUse + Stop) are present.
3. `gt project doctor` reports the trigger infrastructure healthy
   (`_check_cross_harness_trigger` PASS / WARN; `_check_bridge_dispatch_liveness`
   per recipient).
4. The host supports the required headless AI-harness invocation.

Do not re-enable the retired OS poller implementation OR the retired
smart poller as a substitute for the cross-harness event-driven trigger
unless Mike gives a new explicit directive for that legacy path.

## Two-Axis Bridge Automation Model

Bridge automation has two complementary first-class axes, each with a
distinct role in the bridge protocol's autonomous-vs-interactive dispatch
model:

### Axis 1: Dispatchable work — cross-harness event-driven trigger

The cross-harness event-driven trigger (`scripts/cross_harness_bridge_trigger.py`)
is the canonical mechanism for **dispatchable work** — work that can be
completed by a freshly-spawned counterpart harness session without further
owner input. Registered as PostToolUse and Stop hooks in
`.claude/settings.json` and `.codex/hooks.json`. Fires on tool-use and Stop.
Spawns counterpart harness sessions when actionable INDEX changes are
detected.

Examples of dispatchable work:
- Loyal Opposition reviews of NEW or REVISED proposals.
- Loyal Opposition verifications of post-implementation reports.
- Self-contained test runs.
- Verdict file authoring.

### Axis 2: Non-dispatchable work — thread automation pattern

A thread automation pattern wakes the interactive chat session
periodically. Its role is to scan `bridge/INDEX.md` and surface work that
**cannot be dispatched to a sub-agent** — work requiring interactive owner
input mid-stream, accumulating context across turns, or coordination across
threads.

Examples of non-dispatchable work:
- Owner-AUQ-required decisions (approvals, waivers, priority choices,
  formal artifact approvals).
- Multi-turn review where context accumulates and a fresh harness would
  lose thread.
- Cross-thread coordination (e.g., umbrella proposal referencing sibling
  threads needing owner sequencing).
- Implementation work that interleaves owner approval packets with code
  changes.

Currently the thread automation pattern is implemented Codex-side only
(the inventoried automations under `config/agent-control/system-interface-map.toml`).
A future Claude-native equivalent would land in this axis (currently
asymmetric).

### Both axes required; roles do not overlap

The cross-harness trigger does NOT refresh already-running interactive
sessions, and the thread automation does NOT spawn counterpart harness
sessions. They are complementary, not duplicative.

### Adding new bridge automation

DO NOT create additional bridge automations as substitutes for either axis
without owner approval. Adding a new bridge automation requires:

1. Owner approval via AskUserQuestion (the canonical owner-decision channel
   per the AUQ-only enforcement stack).
2. Classification by axis (dispatchable vs non-dispatchable).
3. A new `[[systems]]` entry in `config/agent-control/system-interface-map.toml`
   with `concept_vs_artifact` reflecting the axis.
4. Update to this section if the new automation's role overlaps with an
   existing surface.

This section articulates the architecture; it does NOT ratify any specific
existing automation as canonical. Owner disposition of currently-inventoried
Codex-app automations (`monitor-gt-kb-bridge-codex-thread`,
`gt-kb-bridge-monitor-codex-thread`) is a separate concern not addressed
in this slice.

## Invariants (Bridge Protocol Itself)

These remain in force regardless of whether bridge scans are manual or handled
by the cross-harness event-driven trigger:

- `bridge/INDEX.md` is the canonical workflow state. Both agents must trust
  INDEX over any other signal.
- Bridge files are append-only. Never delete a bridge file; it forms the audit
  trail.
- Per-thread versioning is monotonic. Statuses are NEW, REVISED, GO, NO-GO,
  VERIFIED.
- The full `Document:` block must be read before acting on any single version of
  that thread.
- Scoped commits only. Bridge work commits should not bundle unrelated source
  changes.

Do NOT, without explicit owner approval:

- Remove or rename `bridge/INDEX.md`
- Delete bridge files (any version)
- Skip the GO/NO-GO discipline for any code change beyond the explicit
  exemptions in `.claude/rules/codex-review-gate.md`
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
  in `memory/*.md` are not enforceable; hooks and `.claude/settings.json`
  registration are.
- **S294**: Discovered `.claude/` was blanket-ignored in `.gitignore`, so the
  bridge visibility infrastructure lived outside git. Worktrees could not see
  it. Fresh clones could not see it. Lesson: if it is essential, it must be
  tracked. The `!`-negation patterns added then remain in force for the rule
  files and PS1 scripts even though the retired hook itself is now removed.
- **S308 (2026-04-25)**: Former OS Claude poller activation drove a ~10x
  token-cost regression (~12.5M tokens/day from background spawns alone). Owner
  directive halted the retired pollers and removed the freshness hook, restoring
  manual-trigger operation until smart-poller automation is available. The
  protocol itself was unaffected; INDEX.md remains canonical. Lesson: token cost
  is a first-class operational metric; automation that scales faster than the
  work it serves becomes a regression even when it works correctly.
- **S339 (2026-05-09)**: Smart-poller retirement (Slice 4). Smart-poller
  scheduled task `GTKB-SmartBridgePoller` halted; runtime artifacts
  archived to `archive/smart-poller-2026-05-09/`; doctor's
  `_check_smart_bridge_poller` removed in favor of
  `_check_cross_harness_trigger` and `_check_bridge_dispatch_liveness`.
  Bridge dispatch is now event-driven (PostToolUse + Stop hooks fire the
  trigger) rather than interval-driven. Lesson: dispatch-on-actionable-
  change is the load-bearing semantic; the substrate (interval-driven
  poller vs. event-driven trigger) is a mechanism choice that should
  follow the host's natural integration boundary. The cross-harness
  trigger reuses the dispatch-state path
  (`.gtkb-state/bridge-poller/dispatch-state.json`) and the actionable-
  signature scheme byte-identically per
  `tests/scripts/test_cross_harness_bridge_trigger.py` to preserve the
  existing audit-trail invariants while changing the substrate.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
