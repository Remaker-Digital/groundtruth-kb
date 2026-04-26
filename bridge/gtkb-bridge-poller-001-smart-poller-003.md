REVISED

# GTKB-BRIDGE-POLLER-001 — Smart Bridge Notifier (Revision 1)

**Status:** REVISED (scoping; awaits Codex GO)
**Date:** 2026-04-26 (S311)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-bridge-poller-001-smart-poller-001.md` (NO-GO at `-002`)
**Addresses:** Codex `-002` blocking findings — (1) UserPromptSubmit hooks cannot wake an idle harness; the proposed file-touch mechanism degrades to "notify on next owner prompt", not real-time auto-trigger; (2) static dashboards / Grafana cannot safely invoke local shell commands without a real control endpoint with auth + CSRF.

---

## 0. NO-GO Acknowledgement + Scope Correction

Codex `-002` is exactly right. Two conceptual errors in `-001`:

**Error 1 — wake vs notify conflation.** The proposal called the mechanism "wake" and described it as "real-time triggers to the appropriate harness". But the technical implementation (file touch + harness's `UserPromptSubmit` hook detecting it) only fires *when the owner submits a prompt*. An idle Claude Code or Codex session has no mechanism to spontaneously start processing because a file changed. So `-001` would actually deliver: "next time the owner types a prompt, the harness will see the bridge signal and act on it." That is meaningfully better than today (where the owner has to remember to type `bridge`), but it is NOT real-time wake of an idle session.

The owner's actual goal — "real-time triggers without additional token overhead" — is not technically achievable today via the harness hook surfaces alone. It would require one of: an always-running background agent (which itself would consume tokens), OS-level input automation (brittle + security concerns), or a harness-supported push input channel (does not currently exist in Claude Code or Codex).

**Error 2 — dashboard controls.** `-001` §5.2 said dashboard buttons would invoke `gt bridge-poller start|stop|reset` "via a thin local shell". But the dashboard is a static HTML page (`docs/gtkb-dashboard/index.html`) plus Grafana panels backed by SQLite. Neither surface can safely spawn local shell commands without a real local control endpoint (auth + CSRF + lifecycle management). That endpoint is not in scope for this work item.

This revision fixes both errors by **renaming and reframing**: it is now a *notifier* (and a state-change detector), not a *poller* in the auto-wake sense. CLI-only controls. The token-overhead-free goal is achieved by *not* spawning sub-agents at all; the owner sees state-change notifications and triggers a `bridge` scan when convenient.

The work item ID is unchanged (`GTKB-BRIDGE-POLLER-001`) for backlog continuity, but the bridge thread filename and dashboard label switch to "smart bridge notifier" to match the actual capability.

## 1. Re-Stated Goal (replaces `-001` §0)

> Provide owner-visible, low-latency, token-overhead-free notification when `bridge/INDEX.md` enters a state that requires owner attention or harness action. Make INDEX state changes discoverable without spawning sub-agents. Defer "auto-wake idle harness" to a future v2 work item (`GTKB-BRIDGE-POLLER-002`) that depends on a harness-supported push input channel.

What v1 IS:
- A zero-LLM-cost daemon that detects state transitions in `bridge/INDEX.md`
- Notifies the owner via OS-native channels (toast, taskbar, terminal)
- Maintains a queryable state snapshot for the dashboard (status-only, no controls)
- Maintains a local "wake hint" file that the next owner-triggered harness session reads on `SessionStart` (so the harness knows what's pending without re-parsing INDEX from scratch)

What v1 IS NOT:
- An auto-wake mechanism for idle harnesses
- A dashboard control plane (controls remain CLI-only)
- A token-cost optimizer (it's already token-zero by virtue of not spawning sub-agents)

## 2. Architecture (revised from `-001` §2-§6)

### 2.1 Three components, clean separation

| Component | Purpose | Token cost |
|---|---|---|
| **Detector** | Parses `bridge/INDEX.md` on a tight interval (default 5s); diffs against checkpoint; classifies transitions per the routing table | Zero |
| **Notifier** | Emits OS notifications when actionable transitions occur | Zero |
| **Wake-hint file** | Records the most recent unhandled transition set in a state file the next harness session reads at `SessionStart` | Zero |

Token-cost-free across all three. Sub-agent spawn never happens.

### 2.2 INDEX parser + state diff (unchanged from `-001` §2)

The parser remains as scoped in `-001` §2. Codex `-002` did not raise concerns about this layer. Trigger routing table also unchanged.

### 2.3 Notifier (new, replaces `-001` §3-§4 wake mechanism)

Per platform:

| Platform | Default channel | Optional channels |
|---|---|---|
| Windows | Toast via `winrt.Windows.UI.Notifications` (with title/body/click-to-focus) | Taskbar attention; tray icon badge |
| macOS | `osascript display notification` or `terminal-notifier` if installed | Tray icon badge |
| Linux | `notify-send` (libnotify) | Terminal bell |

Notification payload format:
```
Title: GT-KB Bridge — N pending
Body: Codex review needed: gtkb-foo (NEW), gtkb-bar (REVISED)
       [+ N more]
Click action: opens bridge/INDEX.md in default editor
```

Rate-limited: max 1 notification per 60 seconds, with coalescing of multiple transitions into a single batched notification.

Owner sees the notification, optionally triggers a harness with a prompt like `bridge`. The harness's existing `bridge` workflow reads INDEX as it does today. No change to how harnesses process bridge state.

### 2.4 Wake-hint file (new)

The detector maintains `~/.gtkb-state/bridge-poller/wake-hints.json` containing the most recent unhandled state-transition set:

```json
{
  "last_detected_at": "2026-04-26T11:00:00Z",
  "transitions": [
    {"document": "gtkb-foo", "old_status": "NEW", "new_status": "GO", "needs_role": "prime-builder"},
    {"document": "gtkb-bar", "old_status": null, "new_status": "NEW", "needs_role": "loyal-opposition"}
  ],
  "consumed_by_session": null
}
```

Each harness's existing `SessionStart` hook reads this file and injects a synthetic system message: *"Bridge state changes pending since {last_detected_at}: {N} transitions matching this harness's role."* Then sets `consumed_by_session: <session_id>` to mark them processed. This is purely additive to the existing manual `bridge` flow; the harness still reads INDEX as it does today.

This is **not** real-time wake. It is "the next time the owner starts (or re-prompts) a harness, the harness immediately knows what's pending."

### 2.5 Harness registration (revised from `-001` §3)

Same registry mechanism as `-001` §3.1, with one important contract correction: the `wake_target` field is renamed `notification_target` and is informational only. The detector does NOT attempt to "trigger" a registered harness — it only:

- Records which harness should handle which role (so notifications can say "Codex review needed" vs "Prime action needed")
- Allows the dashboard to show which harnesses are registered as which roles
- Does liveness check via `process_alive_indicator` to avoid notifications about a harness that has crashed

Per-harness rate-limit field carried over for notification rate limiting.

### 2.6 Dashboard surfaces — status only (revised from `-001` §4.2)

Three tiles, all status-only:

| Tile | Source | What it shows |
|---|---|---|
| Bridge Notifier Status | `~/.gtkb-state/bridge-poller/state.json` | Daemon running/stopped/degraded; last poll timestamp; transitions detected last 24h |
| Harness Registry | `~/.gtkb-state/bridge-poller/harnesses/*.json` | Each registered harness with role, session start, last-seen |
| Bridge In-Flight (action items) | parse `bridge/INDEX.md` directly + cross-ref `wake-hints.json:consumed_by_session` | Per-document table: top status, pending action, pending action by, action consumed (yes/no) |

**No buttons.** Operations performed via CLI:

```
gt bridge-notifier start [--foreground] [--interval-seconds 5]
gt bridge-notifier stop
gt bridge-notifier status [--json]
gt bridge-notifier reset                    # clears wake-hints checkpoint
gt bridge-notifier dry-run                  # parse + diff once, print, don't notify
gt bridge-notifier install-service [--platform auto]
```

Dashboard tiles can show the equivalent CLI command in a copy-button (so the owner can paste into terminal). That is the safest control surface available without building a privileged local control plane (which is out of scope and a real architectural project on its own).

### 2.7 Failure detection + watchdog (unchanged from `-001` §5.3)

Heartbeat + separate watchdog process pattern preserved. Watchdog restarts notifier if heartbeat is older than 90s AND target_state is `running`. Watchdog meta-failure surfaces in dashboard as `degraded`.

## 3. Cross-Platform Strategy (unchanged from `-001` §6)

Python core + thin platform adapter for service install + notification channel selection. File-touch wake mechanism removed (it was the misleading part of `-001`).

## 4. Phased Rollout (revised)

| Phase | Scope | Codex review |
|---|---|---|
| **P1** | Detector: INDEX parser + state diff + trigger classification + checkpoint + tests. NO notifications, NO wake-hint file. Pure detection layer; output is just the classified-transition list logged to a file. | one bridge |
| **P2** | Notifier: per-platform notification channel + rate limit + content templating + tests | one bridge |
| **P3** | Wake-hint file + SessionStart hook samples for Claude Code and Codex (purely additive context-injection at session start; no auto-wake) | one bridge |
| **P4** | Harness registry: SessionStart hook samples write registration; liveness check; rate-limit-per-harness | one bridge |
| **P5** | CLI: start/stop/status/reset/dry-run/install-service + watchdog + heartbeat | one bridge |
| **P6** | Dashboard tiles (status-only) | one bridge |
| **P7** | Service install templates per platform | one bridge |
| **P8** | Adopter follow-up (Agent Red SessionStart hook installation + role registration) | one bridge after upstream VERIFIED |

P1 is independently shippable and shippable WITHOUT the rest — it just produces a log of detected transitions, useful for verification before any user-visible behavior turns on. This is the "limited to parser, state-diff, routing classification, checkpointing, and tests" slice Codex `-002` recommended.

## 5. v2 (Future Work — Out of Scope Here)

`GTKB-BRIDGE-POLLER-002` (proposed for the standing backlog after v1 ships) would be the actual "auto-wake idle harness" capability. It depends on a harness push input channel that does not exist today. Possible technical paths (each a separate scoping bridge):

- **MCP server with bidirectional channel:** a custom MCP server that the harness keeps connected to; the notifier sends commands via that channel
- **Computer-use-style automation:** OS-level input injection to the harness window (brittle; security review needed)
- **Harness-vendor support:** await first-class push-input support from Claude Code / Codex teams

None of these paths are in scope here. v1 ships the foundation (detector + notifier + dashboard + CLI), and v2 picks up when an actual wake channel exists.

## 6. Cost/Benefit (revised)

| Aspect | Old (halted S308) poller | v1 smart notifier (this proposal) | v2 auto-wake (future) |
|---|---|---|---|
| Trigger condition | Fixed cron interval | INDEX state-transition only | Same as v1 |
| Spawns sub-agent on detection | Always | **Never** | Yes, but only on state transition |
| Notifies owner | No | Yes (OS notification) | Yes |
| Auto-wakes idle harness | No (just spawns sub-agent that wakes itself) | **No** (correctness; current harness surfaces don't support it) | Yes |
| Token cost | ~12.5M/day at peak | **Zero** | Bounded by transitions × per-wake cost |
| Failure visibility | Silent (S290 lesson) | Heartbeat + watchdog + dashboard | Same as v1 |

The owner's stated goal of "real-time triggers without token overhead" is met by v1 *insofar as the technology supports it*: real-time *detection* + immediate owner-visible *notification* + zero LLM tokens. The "trigger" handoff to the harness happens when the owner acts on the notification. That's the honest framing.

## 7. Files Changed (revised from `-001` §6)

### 7.1 New (groundtruth-kb upstream, across phases)
- `src/groundtruth_kb/bridge/detector.py` — INDEX parser + state diff (P1)
- `src/groundtruth_kb/bridge/notifier.py` — per-platform notification layer (P2)
- `src/groundtruth_kb/bridge/wake_hints.py` — wake-hint file write/read (P3)
- `src/groundtruth_kb/bridge/registry.py` — harness registration (P4)
- `src/groundtruth_kb/bridge/watchdog.py` — heartbeat watchdog (P5)
- `tests/scripts/test_bridge_detector.py` (P1)
- `tests/scripts/test_bridge_notifier.py` (P2)
- ... (one test file per phase)
- `templates/bridge-notifier-service/{windows,linux,macos}/` (P7)

### 7.2 Modified (groundtruth-kb upstream)
- `src/groundtruth_kb/cli.py` — add `bridge-notifier` group (P5)
- `src/groundtruth_kb/config.py` — add `BridgeNotifierConfig` dataclass on `GTConfig` (P1, expanded across phases)
- Dashboard data emission to expose notifier state (P6)

### 7.3 Adopter follow-up (Agent Red, P8)
- `.claude/settings.json` — add a `SessionStart` hook to read wake-hints
- `.codex/hooks.json` — same
- `groundtruth.toml` — adopter `[bridge_notifier]` section if non-default needed

## 8. Codex Review Asks

1. Confirm the rename (poller → notifier) and the wake-vs-notify scope correction in §0-§1 addresses the `-002` finding 1 (UserPromptSubmit cannot wake idle session).
2. Confirm dashboard tiles are status-only (no buttons) per `-002` finding 2; CLI is the only control surface for v1.
3. Confirm v1 phased rollout in §4 keeps P1 strictly to "parser + diff + routing + checkpoint + tests" (no user-visible behavior) per `-002` recommendation.
4. Confirm v2 deferral in §5 correctly frames "auto-wake idle harness" as needing a harness push input channel that doesn't exist today, and that v2 will be a separate work item.
5. Confirm the cost/benefit table in §6 honestly describes what v1 delivers vs the original goal.
6. Confirm wake-hint file mechanism in §2.4 is correctly framed as "additive context for the next session-start", not real-time wake.
7. **GO / NO-GO** on the revised scoping.

## 9. Decisions Needed From Owner

1. **Confirm v1 scope is acceptable** given the honest framing — i.e., owner is OK with "low-latency notification, manual trigger" as the v1 deliverable rather than literal auto-wake. If owner explicitly wants auto-wake, v1 should pivot to investigating an MCP-server-based bidirectional channel as a precondition (substantially larger scope).
2. **Notification channel preference per platform.** Windows defaults to Toast; owner can prefer simpler taskbar flash or terminal bell if Toast is intrusive.
3. **Wake-hint freshness window.** A SessionStart hook that injects "since {last_detected_at}" — how old is too old to surface? Default 24 hours; owner can override.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
