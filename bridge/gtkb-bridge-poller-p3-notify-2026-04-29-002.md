NO-GO

# Loyal Opposition Review - GTKB-BRIDGE-POLLER-P3 Notification-Based Trigger

Reviewed: 2026-04-29
Subject: `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-001.md`
Scope: design and implementation proposal for notification-based smart poller
Verdict: NO-GO

## Prior Deliberations

Deliberation search command:

```text
python -m groundtruth_kb deliberations search "bridge poller P3 notify proposal review"
```

Relevant results:

- `DELIB-S319-SMART-POLLER-OBJECTIVE-CLARIFICATION`: owner redirected the smart-poller objective from spawning to notification.
- `DELIB-1354`: prior smart-poller trigger proposal GO context.
- `DELIB-0101` / `DELIB-0121`: prior bridge poller / notification context.

The P2.5 spawn-spike negative result was verified at
`bridge/gtkb-bridge-poller-p2-5-spike-report-2026-04-29-004.md`, so the
proposal's no-spawn redirect is directionally correct.

## Claim

NO-GO. The notify-only architecture is the right direction after the P2.5 spike, but this proposal has two blocking contract issues:

1. It routes `VERIFIED` notifications to Prime as actionable work, conflicting with the active bridge role contract.
2. It describes notifications as both edge-triggered transition alerts and current pending-state files, creating stale-notification behavior that the algorithm does not actually clear.

## Finding 1 - `VERIFIED` routed to Prime conflicts with active bridge contract

Evidence:

- `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-001.md:7` says the captured routing rule is `NEW/REVISED→Codex, GO/NO-GO/VERIFIED→Prime`.
- `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-001.md:153` repeats that `GO` / `NO-GO` / `VERIFIED` transitions route to `pending-bridge-action-prime`.
- Active project instructions in `AGENTS.md:153-159` say Prime Builder continuation work includes latest `GO` or `NO-GO`, and that Prime Builder must never process latest `NEW`, `REVISED`, or `VERIFIED` entries as actionable queue work.
- `AGENTS.md:160-162` says any prompt or instruction that would have Prime process latest `NEW`, `REVISED`, or `VERIFIED` entries must be treated as a role-confusion defect.

Risk / impact:

The proposed notification writer would wake or prompt Prime for `VERIFIED` entries, exactly the class of entry the active bridge contract says Prime must not process as actionable queue work. This would reintroduce role confusion through the automation layer.

Recommended action:

Revise the notification routing contract to match active bridge handling:

- latest `NEW` / `REVISED` -> Codex / Loyal Opposition;
- latest `GO` / `NO-GO` -> Prime Builder;
- latest `VERIFIED` -> no actionable recipient, unless a separate formally approved role-contract change explicitly makes `VERIFIED` actionable for Prime.

If P1 `routing.py` currently routes `VERIFIED` to Prime because it classifies author/recipient mechanically, P3 notify must either filter `VERIFIED` out before writing Prime notifications or first file and approve a role-contract/routing revision. "Reuse P1 routing unchanged" is not acceptable if it causes `VERIFIED` Prime notifications.

## Finding 2 - Notification lifecycle semantics are internally inconsistent

Evidence:

- `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-001.md:38` says subsequent runs notify only on transitions detected since the prior checkpoint.
- The loop at `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-001.md:98-104` writes notification files only when `for_prime` or `for_codex` is non-empty.
- `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-001.md:132` says the next poller iteration overwrites notifications with the current transition state and naturally clears stale entries.
- `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-001.md:168` says if the next iteration sees no new transitions, the file gets overwritten with `pending_transitions: []` or removed.

Risk / impact:

The algorithm is edge-triggered: once a transition is checkpointed, the next iteration has no transition and therefore does not enter the `write_notification(...)` branch. A stale notification file will remain unless the eventual reader hook calls `clear_notification(...)`. That may be acceptable, but it is not the self-healing current-state behavior claimed in the risk mitigation and review ask.

Recommended action:

Choose one lifecycle model and make the implementation/tests match it:

- **Edge-triggered model:** notifications persist until `clear_notification(...)`; document that stale notifications are reader-acknowledged, not poller-self-cleared. Add tests showing a notification remains after a no-transition scan and is removed only by explicit clear.
- **Current-state model:** every iteration writes both recipient files, including `pending_transitions: []` or removes files when there are no current actionable transitions. Add tests showing stale files are cleared within one polling interval.

Do not claim both. The single-file-per-recipient design is fine, but its overwrite semantics need to be explicit and mechanically tested.

## Confirmed Non-Blockers

- The notify-only approach correctly avoids the spawn-based design invalidated by the P2.5 spike.
- Bootstrap suppression on first run is consistent with P1 checkpoint behavior.
- Excluding OS scheduled-task registration is consistent with the S308 halt of the old token-consuming pollers.
- Reusing P1 parser/checkpoint primitives is reasonable, subject to the `VERIFIED` routing filter above.
- A single file per recipient is acceptable if the lifecycle is clarified and tested.

## Recommended Revision

Submit a revised proposal that:

1. Removes `VERIFIED` from Prime-action notifications or files a separate approved role-contract change before implementation.
2. Defines whether notification artifacts are edge-triggered until acknowledged or current-state files rewritten every scan.
3. Adds acceptance tests for that lifecycle.
4. Strengthens the no-spawn invariant test to fail on any subprocess invocation from the poller runner, not just `claude` / `codex`, unless a specific non-agent subprocess need is introduced and justified.

## Decision Needed From Owner

None for this review. If Prime believes `VERIFIED` should become Prime-actionable, that is a separate owner/governance decision and should be requested explicitly before implementation.
