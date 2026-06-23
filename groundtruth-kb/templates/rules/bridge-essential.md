# Bridge Is Essential - Top-Priority Mandate

This rule auto-loads via `.claude/rules/` convention and is TRACKED in git
(negated from the `.claude/` blanket ignore). Do not remove it.

## The Mandate

**Bridge integrity is the top-priority task. Always.**

> **2026-06-15 cutover note:** After the WI-4510 Phase-3 cutover,
> TAFE-backed dispatcher state plus status-bearing versioned files under
> `bridge/` are canonical. Aggregate queue artifacts are not live bridge state.

The Prime Builder / Loyal Opposition bridge is how GroundTruth-KB coordinates
implementation proposals, reviews, and verification. GroundTruth-KB is
non-functional when the bridge stops working. Therefore: keeping the
TAFE-backed bridge state correct, dispatcher-visible, and consistent with the
versioned bridge file chain is the first duty of every Prime Builder session,
ahead of feature work, backlog progress, test runs, deployments, and
documentation updates.

The bridge as a protocol (proposal -> review -> revise -> GO/NO-GO -> implement
-> post-impl -> VERIFIED, all recorded in versioned files under `bridge/`) is
permanently in force. Any proposal, refactor, or cleanup that would weaken the
protocol's audit trail, GO/NO-GO discipline, or TAFE/dispatcher bridge-state
authority must be rejected.

## Operational Mode (current as of 2026-05-09)

**Both the retired OS bridge pollers (halted 2026-04-25) and the smart
poller (retired 2026-05-09) are disabled. The cross-harness event-driven
trigger is the canonical bridge automation path while it remains healthy.**

The owner directive that halted OS pollers on 2026-04-25 applied to the
former blind-polling implementation: Windows scheduled tasks
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
than on a fixed interval. When TAFE-backed bridge state changes, or the agent
ends a turn, the trigger inspects dispatcher/TAFE state and dispatches the appropriate counterpart
harness if a recipient's actionable queue signature has changed (Codex on
latest NEW or REVISED; Prime on latest GO or NO-GO). ADVISORY entries are surfaced in the Prime actionable
list by `compute_actionable_pending` for interactive sessions, but the
`_derive_dispatchable` invariant in `groundtruth_kb.bridge.notify` returns
False for ADVISORY, so every headless dispatch surface filters them out
before the signature is computed and they never spawn a Prime worker.
VERIFIED is terminal, and DEFERRED and WITHDRAWN are non-actionable for
dispatch. The trigger
is monitoring and dispatch infrastructure only; TAFE-backed bridge state is the
canonical workflow state. Per-recipient dispatch state is recorded at
`.gtkb-state/bridge-poller/dispatch-state.json` (path retained for
compatibility with the smart-poller substrate).

Manual fallback remains available when the trigger is unhealthy (per the
doctor predicate above) or intentionally stopped: the owner triggers a
Prime bridge scan with a brief prompt such as `Bridge` or `Bridge scan`,
Prime then reads TAFE/dispatcher bridge state and acts on actionable entries.
Codex bridge scans are similarly owner-triggered in the Codex harness.

The 2026-04-25 OS-poller halt was made after the former OS Claude poller
(activated ~2026-04-23) was found to fire on a fixed interval regardless
of bridge activity: 173 Claude capped-spawns/day at peak plus 92 Codex
spawns/day, the great majority spawning a harness that found no actionable work
waiting. The defect was not the fixed-interval check itself — that check was
negligibly cheap — but that each tick spent an expensive resource (waking a
harness into a full ~50k-token investigation) unconditionally, with no cheap
deterministic gate in front of the spawn. The 2026-05-09 smart-poller retirement was made after a
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

## Dual-Substrate Coexistence (Slice 2 of single-harness-bridge-dispatcher)

The bridge protocol has TWO live dispatch substrates as of Slice 2 of
``gtkb-single-harness-bridge-dispatcher-slice-2`` (Codex GO at ``-006``):

1. **Cross-harness event-driven trigger** (multi-harness topology) —
   ``scripts/cross_harness_bridge_trigger.py`` registered as PostToolUse
   and Stop hooks in ``.claude/settings.json`` and ``.codex/hooks.json``.
   Fires on tool-use and Stop events. Applicable when the role map records
   two harness IDs with singleton role-sets.
2. **Single-harness bridge dispatcher** (single-harness topology) —
   ``scripts/single_harness_bridge_dispatcher.py`` invoked by a Windows
   scheduled task ``GTKB-SingleHarnessBridgeDispatcher`` on a fixed
   interval (default 5 minutes; per
   ``DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`` § Platform Bindings).
   Applicable when the role map records one harness ID with a multi-element
   role-set ``["prime-builder", "loyal-opposition"]`` per
   ``ADR-SINGLE-HARNESS-OPERATING-MODE-001``.

   Activation is managed by ``scripts/single_harness_bridge_automation.py``,
   which is registered from both ``.claude/settings.json`` and
   ``.codex/hooks.json``. That manager enables or updates the scheduled task
   only when the live role map is single-harness, deactivates it when the
   topology is multi-harness, and may run a one-shot dispatch after Stop once
   the active-session lock has been cleared.

Both substrates honor the same actionable-signature scheme (byte-identical
``_signature`` computation), the same active-session-suppression contract
(per ``bridge/gtkb-cross-harness-trigger-active-session-suppression-001-008.md``
VERIFIED), and the same fire-and-forget audit-log discipline
(``.gtkb-state/bridge-poller/dispatch-failures.jsonl``).

They are **mutually exclusive at runtime**:

- In multi-harness topology: the cross-harness trigger is the active
  substrate; the single-harness dispatcher's applicability check returns
  False and the scheduled task no-ops.
- In single-harness topology: the cross-harness trigger's topology gate
  (per IP-8 of the slice-2 thread) inerts it with SPEC-required durable
  audit evidence (per-role entries in ``dispatch-failures.jsonl`` plus
  per-recipient ``last_result = "single_harness_topology_not_applicable"``
  records in ``dispatch-state.json``); the single-harness dispatcher
  performs in-process dispatch.

Substrate applicability is determined by the role-set topology in
``harness-state/harness-registry.json`` through
``groundtruth_kb.harness_projection.read_roles`` or the ``roles`` subcommand
under ``gt harness``. The doctor's
``_check_role_set_topology_consistency`` (Slice 1) validates wire form;
``_check_single_harness_dispatcher_when_required`` (Slice 1 + Slice 2
upgrade) reports applicability and registration health. Per
``DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`` § Doctor Check, missing-
task severity is WARN (not FAIL) so manual-trigger fallback remains
viable while the task is being installed.

Do NOT create additional bridge automation substrates without an
owner-approved bridge proposal and an updated classification under § Two-
Axis Bridge Automation Model below.

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
Spawns counterpart harness sessions when actionable dispatcher/TAFE bridge-state
changes are detected.

Examples of dispatchable work:
- Loyal Opposition reviews of NEW or REVISED proposals.
- Loyal Opposition verifications of post-implementation reports.
- Self-contained test runs.
- Verdict file authoring.

### Axis 2: Non-dispatchable work — thread automation pattern

A thread automation pattern wakes the interactive chat session
periodically. Its role is to scan TAFE/dispatcher bridge state and surface work that
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

The two-axis automation surface is implemented:

- AXIS 1 (Claude→Codex and Codex→Claude when no interactive session is
  active): the cross-harness event-driven trigger at
  `scripts/cross_harness_bridge_trigger.py` registered as PostToolUse + Stop
  hooks. Spawns headless counterpart harness on actionable signature change.
- AXIS 2 Codex-side: the inventoried Codex app-thread automation under
  `config/agent-control/system-interface-map.toml`, which wakes the Codex
  interactive session periodically.
- AXIS 2 Claude-native: the `.claude/hooks/bridge-axis-2-surface.py`
  UserPromptSubmit hook (per
  `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-005.md` REVISED-2
  Codex GO at `-006`). Surfaces newly-actionable Prime bridge work into the
  next prompt as additionalContext when an interactive Claude session is
  active. Pull-based by design: Claude's interaction model is prompt-driven,
  so the natural Claude-native AXIS 2 mechanism is prompt-time surfacing, not
  periodic wake. Both AXIS 2 mechanisms are complementary; each fits its
  harness's native interaction model.

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

- TAFE-backed bridge state plus status-bearing versioned files under `bridge/`
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
- **S308 (2026-04-25)**: Former OS Claude poller activation produced ~12.5M
  tokens/day of background spawns (a ~10× jump), most spawning a harness that found no
  actionable work, because each fixed-interval tick spawned a harness
  unconditionally regardless of whether the bridge had changed. Owner directive halted the retired pollers and removed the
  freshness hook, restoring manual-trigger operation until smart-poller
  automation is available. The protocol itself was unaffected; after the
  2026-06-15 cutover, TAFE-backed bridge state is canonical. Lesson: automation is
  wasteful when it spends an expensive resource — principally agent
  investigation tokens — without a commensurate chance of value; the cheap
  fixed-interval check was never the defect, the unconditional expensive spawn
  was. The remedy is to gate the expensive action behind a cheap, deterministic
  check (the cross-harness trigger's actionable-signature check), evaluated as
  relative value vs. cost per action.
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
  `platform_tests/scripts/test_cross_harness_bridge_trigger.py` to preserve the
  existing audit-trail invariants while changing the substrate.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
