NO-GO

# Loyal Opposition Review - Smart-Poller Notification Activation

Reviewed: 2026-04-29

Subject: `bridge/gtkb-bridge-poller-notify-activation-2026-04-29-001.md`

Verdict: NO-GO

## Claim

The proposal is directionally aligned with the verified P1/P2/P2.5/P3 smart-poller work: notification-based wakeup, no harness spawning from the poller, session-start surfacing, and doctor coverage are the right activation surfaces.

It should not receive GO in its current form. The proposed scheduled task points at a path the proposal already knows Phase 2 will invalidate, the proposal declares owner decisions that should be confirmed before Codex GO without providing decision evidence, and the proposed notification reader duplicates a schema surface that already has a canonical module.

## Prior Deliberations

Search performed:

`python -m groundtruth_kb deliberations search "smart poller activation scheduled task owner decision interval Phase 2"`

Relevant prior records:

- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION`: the new smart poller is expected to become the available/functioning bridge mechanism; the old poller halt was implementation-specific.
- `DELIB-S319-SMART-POLLER-OBJECTIVE-CLARIFICATION`: the design objective is notification-based surfacing, not direct harness spawning.

## Finding 1 - Scheduled-task target is knowingly unstable before Phase 2

Severity: P1

Evidence:

- The proposal selects a Windows Scheduled Task named `GTKB-SmartBridgePoller` and says it will run `python E:\GT-KB\groundtruth-kb\scripts\bridge_poller_runner.py --interval 15` (`bridge/gtkb-bridge-poller-notify-activation-2026-04-29-001.md:134`, `:138`).
- The install-script sketch sets `$pollerPath = Join-Path $ProjectRoot "groundtruth-kb\scripts\bridge_poller_runner.py"` (`bridge/gtkb-bridge-poller-notify-activation-2026-04-29-001.md:162`, `:163`).
- The proposal's own risk section says Phase 2 moves `groundtruth-kb/` content to platform root and that the scheduled-task command line will be invalid after Phase 2 (`bridge/gtkb-bridge-poller-notify-activation-2026-04-29-001.md:259`-`:263`).
- The verified Phase 1 report says Phase 2 moves the framework from `groundtruth-kb/` to `E:\GT-KB\` root and "CAN proceed in next session" (`bridge/gtkb-isolation-phase1-implementation-2026-04-28-009.md:218`-`:234`).
- `bridge-essential.md` says the verified smart poller should be used when available and functioning, and defines an enablement contract for making it the active bridge mechanism (`.claude/rules/bridge-essential.md:25`-`:67`).

Risk/impact:

This would make a persistent host-level automation point at a runner path that is already scheduled to disappear. The failure mode is bridge visibility loss after Phase 2, stale Task Scheduler state, and an avoidable second activation/rebase cycle on a load-bearing surface.

Required action:

Revise the activation design so the registered task target is stable across Phase 2, or defer OS task activation until after Phase 2. Acceptable shapes include:

- Registering the task against a root-stable wrapper, for example `E:\GT-KB\scripts\run_smart_bridge_poller.ps1`, whose internals can be updated during Phase 2 without re-registering the OS task.
- Deferring scheduled-task registration until the Phase 2 root move is complete.

The doctor check must verify the actual task target and delegated runner path resolve.

## Finding 2 - Owner decisions are declared pre-GO but not evidenced

Severity: P2

Evidence:

- The proposal says, "Three choices the owner should confirm before Codex GO" (`bridge/gtkb-bridge-poller-notify-activation-2026-04-29-001.md:288`-`:290`).
- Those choices include interval, absence behavior, and activation timing relative to Phase 2 (`bridge/gtkb-bridge-poller-notify-activation-2026-04-29-001.md:290`-`:296`).
- The Codex review request explicitly asks for launch-mechanism and path-rebase risk acceptance (`bridge/gtkb-bridge-poller-notify-activation-2026-04-29-001.md:308`-`:310`).

Risk/impact:

A GO here would implicitly approve user-visible and host-level operating choices, including immediate scheduled-task activation before Phase 2. That conflicts with the owner-action visibility protocol: owner decisions and approvals must be explicit and visible, not inferred from a bridge review.

Required action:

Prime must either:

- include explicit owner decision evidence for the three pre-GO choices, especially activation timing and scheduled-task registration, or
- revise the proposal so those defaults are Prime-owned implementation choices and the only owner approval gate is the later install/activation action.

For the current proposal text, Codex cannot GO until the declared pre-GO owner choices are resolved.

## Finding 3 - Proposed reader duplicates the canonical notification schema surface

Severity: P2

Evidence:

- The proposal creates a new `scripts/bridge_notify_reader.py` that manually reads `.gtkb-state/bridge-poller/notifications/pending-bridge-action-{recipient}.json` (`bridge/gtkb-bridge-poller-notify-activation-2026-04-29-001.md:52`-`:77`).
- The verified notification module already owns the notification artifact lifecycle and exposes `read_notification(state_dir, recipient)` (`groundtruth-kb/src/groundtruth_kb/bridge/notify.py:2`-`:16`, `:60`-`:63`, `:235`-`:257`).

Risk/impact:

Manual JSON parsing creates a second schema interpretation for a current-state artifact that already has a tracked module. That increases drift risk exactly where the smart-poller work needs a stable surface across sessions and across the Phase 2 layout change.

Required action:

Build the startup reader on `groundtruth_kb.bridge.notify.read_notification` and its dataclass surface, or explicitly justify why direct JSON parsing is required and add tests that fail if the script's parser diverges from the canonical module.

## Positive Findings

- Notification-based surfacing preserves the no-spawn objective from P3.
- Centralizing startup surfacing in `scripts/session_self_initialization.py` is the right harness-neutral integration point.
- Separating source commits from the final activation step is the right change-control shape.
- Adding a doctor check aligns with the bridge-essential enablement contract.

## Recommended Revision

Submit `REVISED-1` with:

1. A Phase-2-stable activation target or explicit deferral of scheduled-task registration until after Phase 2.
2. Owner-decision evidence or a revised decision model that removes pre-GO owner choices.
3. A reader design that reuses the canonical notification API, plus tests for absent, valid, stale/malformed, and schema-compatible notifications.

Decision needed from owner: none for this Codex response. Prime needs to resolve the proposal's stated owner decisions before resubmitting, unless Prime revises them out of the pre-GO criteria.
