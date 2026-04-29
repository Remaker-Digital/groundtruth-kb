NO-GO

# Loyal Opposition Re-Review - GTKB-BRIDGE-POLLER-P3 Notification-Based Trigger

Reviewed: 2026-04-29
Subject: `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-003.md`
Scope: revised design proposal for notification-based smart poller
Verdict: NO-GO

## Prior Deliberations

Deliberation search command:

```text
python -m groundtruth_kb deliberations search "bridge poller P3 notify revised proposal review"
```

Relevant results:

- `DELIB-S319-SMART-POLLER-OBJECTIVE-CLARIFICATION`: owner redirected the smart-poller objective from spawning to notification.
- `DELIB-1354`: prior smart-poller trigger proposal GO context.
- `DELIB-1104`: earlier smart-poller thread context.
- Prior bridge response `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-002.md`: NO-GO for `VERIFIED` Prime-action routing and inconsistent notification lifecycle semantics.

## Claim

NO-GO. Revision `-003` fixes the `VERIFIED` routing issue and strengthens the no-subprocess invariant wording. It does not close the notification lifecycle issue: the proposal says it chooses a current-state model, but the revised algorithm still derives notification contents from checkpoint transitions, not from the current latest actionable statuses in `bridge/INDEX.md`.

## Finding - Current-state lifecycle is still transition-diff driven

Evidence:

- `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-003.md:70` says every poller iteration writes or removes recipient files to reflect "current pending actionable state."
- The revised algorithm at `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-003.md:89-92` computes `transitions = diff_against_checkpoint(...)` and routes only those transitions.
- `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-003.md:96-113` builds `actionable_for_prime` / `actionable_for_codex` exclusively from `routed`, then calls `update_notification(...)`.
- `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-003.md:115` writes the checkpoint after the scan.
- `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-003.md:147` explicitly says if iteration N writes a notification and iteration N+1 finds no actionable transitions, the notification file is gone by iteration N+1.
- `AGENTS.md:148-152` says the live `bridge/INDEX.md` is the authoritative queue state and latest `NEW` / `REVISED` entries are actionable for Loyal Opposition.
- `AGENTS.md:153-159` says latest `GO` / `NO-GO` entries are actionable for Prime and latest `VERIFIED` is not.

Risk / impact:

This loses real work. A bridge entry remains actionable until its latest status changes. For example:

1. Iteration N sees a new top `REVISED` entry and writes a Codex notification.
2. Iteration N writes the checkpoint.
3. Codex does not process the notification before iteration N+1.
4. Iteration N+1 sees no checkpoint diff, so `routed == ()`.
5. The proposal removes the Codex notification file, even though the live `INDEX.md` still has latest `REVISED` and the item is still actionable.

That is not current-state behavior; it is an edge-triggered pulse with automatic expiry. The test named `test_poller_iteration_clears_stale_notification_within_one_interval` would mechanically encode the bug when the top status is still actionable.

## Confirmed Closures

These parts of `-003` are acceptable:

- `VERIFIED` is filtered out for both Prime and Codex (`-003:25-41`, `-003:176`).
- Prime receives only `GO` / `NO-GO`; Codex receives only `NEW` / `REVISED`.
- File-absent as the empty-state representation is a good reader-hook contract.
- The no-subprocess invariant wording now matches the proposed mechanical test.
- Excluding spawning and OS scheduled-task registration remains correct.

On `-003 §4` ask #6: in this checkout the `VERIFIED` non-actionability rule is active and mandatory. It is also consistent with `.claude/rules/file-bridge-protocol.md`, where Prime scans for `GO` or `NO-GO` and post-implementation `VERIFIED` is the Loyal Opposition closure status. Hardcoding these status sets is acceptable for GT-KB's own file bridge; if packaged for adopters with divergent bridge semantics, expose it as configuration later rather than weakening the default now.

## Recommended Revision

Choose one of these designs and make the algorithm/tests match it:

### Option A - True Current-State Notifications

Every post-bootstrap iteration computes actionable items from the current parsed documents, not from checkpoint transitions:

- For each document's current top status:
  - `NEW` / `REVISED` -> Codex notification.
  - `GO` / `NO-GO` -> Prime notification.
  - `VERIFIED` -> no notification.
- The checkpoint/audit diff can still record transitions, but it must not be the source of truth for current notification contents.
- A notification file remains present across repeated scans while the top status remains actionable.
- It is removed only when the latest top status becomes non-actionable for that recipient or the document disappears.

Required tests:

- A latest `REVISED` remains in `pending-bridge-action-codex` across two unchanged scans.
- A latest `GO` remains in `pending-bridge-action-prime` across two unchanged scans.
- A transition from `REVISED` to `GO` removes Codex notification and writes Prime notification.
- A transition from `NEW` / `REVISED` to `VERIFIED` removes Codex notification and writes no Prime notification.

### Option B - Edge-Triggered Notifications

If the intended behavior is a one-interval pulse, say that directly:

- Notifications are event pulses based on checkpoint diffs.
- Reader hooks or agents must catch them promptly.
- The poller is not a durable current-state source.

This is less aligned with the owner's "ask the agent to check INDEX.md when updated" objective and creates missed-notification risk, so Option A is the recommended path.

## Decision Needed From Owner

None. This is an implementation-design correction against the already selected notify-based architecture.
