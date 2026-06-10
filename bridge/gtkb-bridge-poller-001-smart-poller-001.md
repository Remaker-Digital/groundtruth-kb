NEW

# GTKB-BRIDGE-POLLER-001 — Smart Bridge Poller (Scoping Proposal)

**Status:** NEW (scoping; awaits Codex GO)
**Date:** 2026-04-26 (S311)
**Author:** Prime Builder (Claude Opus 4.7)
**Work item:** GTKB-BRIDGE-POLLER-001 (new; will be added to standing backlog row 14 after Codex GO)
**Bridge kind:** scoping_proposal
**Builds on:**
- S308 OS-poller halt incident (~10× token regression)
- `.claude/rules/bridge-essential.md` "Re-Enabling Pollers" gate
- Owner directive 2026-04-26 (S311)
**Target project:** groundtruth-kb upstream (framework capability; Agent Red adopts)

bridge_kind: prime_proposal
work_item_ids: [GTKB-BRIDGE-POLLER-001]
spec_ids: []
target_project: groundtruth-kb
implementation_scope: framework-tooling + cross-harness coordination

---

## 0. Owner Goal

> "Provide real-time triggers to the appropriate harness without incurring any additional token consumption overhead."

The OLD poller (halted S308) triggered harness sub-agents on a fixed schedule regardless of whether there was actual bridge work. Result: ~12.5M tokens/day at peak from background spawns alone.

The NEW poller is *smart*: it scans `bridge/INDEX.md` cheaply (no sub-agent, just a Python script), and only wakes a harness when there is an actual state transition that demands its attention. This proposal scopes the architecture and addresses owner's 5 questions; implementation is staged.

## 1. Cost/Benefit Analysis (per `.claude/rules/bridge-essential.md` gate)

The bridge-essential rule requires this analysis before re-enabling any poller. Here it is.

| Aspect | Old (halted) poller | Smart poller (proposed) |
|---|---|---|
| Trigger condition | Fixed cron interval (every N minutes) | INDEX state-transition only |
| Spawns sub-agent | Always, regardless of need | Only when actionable state exists for that harness |
| Token cost when idle | ~50k tokens/spawn × ~173 spawns/day at peak = 8.6M tokens/day | **Zero** (Python script reads INDEX, no LLM tokens) |
| Token cost when busy | Same as idle (no awareness) | Roughly equal to manual scan (one wake = one scan) |
| Failure mode (S290–S292 etc.) | Silent failure when poller broke; no chat-stream visibility | Heartbeat + watchdog auto-restart; status visible in dashboard |
| Triggered harness work | Sub-agent reads INDEX after spawn | Active session sees notification; same INDEX-scan motion |

**Net token impact estimate:** poller itself = zero LLM cost. Triggered harnesses use exactly the tokens they would use for an owner-triggered manual scan, but timed to the actual event rather than to an arbitrary owner prompt. Could be *negative* on wall-clock latency without being negative on token cost.

Mitigation that this proposal embeds (lessons from S290-S292, S294, S296, S308):

- **Visibility** independent of the poller it monitors (dashboard tile shows poller liveness; doesn't depend on poller writing it)
- **Heartbeat + watchdog separation** so a broken poller fails loudly
- **Hard rate cap per harness** (e.g., max 1 wake per 60 seconds) prevents pathological wake storms
- **Tracked under git** (the failure to track `.claude/` infrastructure was the S294 lesson)

## 2. Owner's Question 1 — Is INDEX.md format deterministic enough?

**Yes.** Current format is highly regular:

```
Document: <kebab-case-name>
<STATUS>: bridge/<name>-<NNN>.md
<STATUS>: bridge/<name>-<NNN>.md
...

(blank line separator)

Document: <next-name>
...
```

Where `<STATUS>` ∈ {NEW, REVISED, GO, NO-GO, VERIFIED}. Top-of-list per document = current status.

A Python parser (~80 LOC) can:

1. Skip lines starting with `<!--` (HTML comments) and blank lines
2. On `Document: ` lines: open a new entry, capture name
3. On `<STATUS>: bridge/...md` lines: append to entry's version list
4. Validate: filename references must match the entry name + numeric suffix; file must exist on disk; status must be in the enum

State-transition detection is then a diff between two parses (last poll vs current):

- New `Document:` block appeared → trigger appropriate harness
- Top status changed (e.g., NEW → GO, REVISED → GO, NEW → NO-GO) → trigger appropriate harness
- New status line added without document-name change → triggers based on the new status

**Trigger routing rules:**

| New top status | Triggers | Reason |
|---|---|---|
| NEW (Prime-authored) | LO (Codex) | Codex needs to review |
| REVISED (Prime-authored after NO-GO) | LO (Codex) | Codex needs to re-review |
| GO (LO-authored) | PB (Prime) | Prime can implement |
| NO-GO (LO-authored) | PB (Prime) | Prime needs to revise |
| VERIFIED (LO-authored) | PB (Prime) | Prime should acknowledge / close |
| NEW (Prime-authored, post-impl report) | LO (Codex) | Codex needs to verify |

The poller maintains a checkpoint file (last-parsed INDEX hash + last-known top-status-per-document map) under `~/.gtkb-state/bridge-poller/`. Diff against current = trigger set.

**Edge cases handled:** documents removed from INDEX (compaction), HTML-commented lines mid-entry (S307 reconciliation pattern), files referenced but missing on disk (warn, skip), simultaneous writes by both harnesses (file lock + atomic re-read).

## 3. Owner's Question 2 — Session-start harness registration

**Yes**, via a SessionStart hook (already an established harness mechanism per `.claude/settings.json` and `.codex/hooks.json`).

### 3.1 Registration mechanism

Each harness registers itself at session start by writing/updating a registration file:

```
~/.gtkb-state/bridge-poller/harnesses/{harness-id}.json
```

Where `harness-id` is derived from environment (e.g., `claude-code-{pid}`, `codex-{pid}`, or a session UUID provided by the harness).

Registration content:

```json
{
  "harness_id": "claude-code-12484",
  "harness_kind": "claude-code",
  "role": "prime-builder",
  "session_started_at": "2026-04-26T08:00:00Z",
  "registered_at": "2026-04-26T08:00:01Z",
  "wake_mechanism": "file-touch",
  "wake_target": "~/.gtkb-state/bridge-poller/wake/claude-code-12484.signal",
  "operating_role_source": "~/.claude/agent-red-hooks/operating-role.md",
  "process_alive_indicator": {
    "kind": "pid",
    "value": 12484
  },
  "rate_limit_seconds": 60
}
```

### 3.2 Role contract

Per `.claude/rules/operating-role.md` and `.claude/rules/acting-prime-builder.md`:

- The role (PB or LO) is sourced from each harness's durable role record (`~/.claude/agent-red-hooks/operating-role.md` or `~/.codex/agent-red-hooks/operating-role.md`)
- Each harness has its OWN durable role record (so two harnesses can carry distinct roles simultaneously without overwriting each other)
- The poller MUST refuse to wake a harness that is not registered as the role the trigger needs (e.g., never wake a PB harness for a NEW that needs LO review)

If both harnesses are registered as the same role, the poller logs a warning to the dashboard and refuses to trigger (caller resolves the conflict by changing one harness's durable role record).

### 3.3 Liveness check

Before sending a wake signal, the poller checks the harness's `process_alive_indicator`:

- `kind: "pid"` → check process exists (cross-platform via `psutil.pid_exists()`)
- `kind: "heartbeat-file"` → check file mtime is within last N seconds

If liveness check fails, the poller marks the registration `stale` and removes from active routing. The next session-start of that harness re-registers.

## 4. Owner's Question 3 — GT-KB integration + dashboard exposure

**Yes**, framework capability with explicit dashboard surfaces.

### 4.1 Module location (groundtruth-kb upstream)

- `src/groundtruth_kb/bridge/poller.py` — main poller logic (parse INDEX, diff, route)
- `src/groundtruth_kb/bridge/registry.py` — harness registration read/write + liveness check
- `src/groundtruth_kb/bridge/wake.py` — per-harness wake mechanism abstraction (file-touch by default, extensible)
- `src/groundtruth_kb/bridge/state.py` — state file (last-parsed INDEX hash + per-document top-status map + last-trigger-event log)
- `src/groundtruth_kb/cli.py` — extends with `gt bridge-poller {start|stop|status|reset}` group

### 4.2 Dashboard surfaces (under existing `docs/gtkb-dashboard/` structure)

New tile: **Bridge Poller Status**

| Field | Source |
|---|---|
| Poller process state | `running` (heartbeat fresh) / `stopped` (no heartbeat) / `degraded` (heartbeat stale > N seconds) |
| Last poll timestamp | `~/.gtkb-state/bridge-poller/state.json:last_poll_at` |
| Polls in last hour | rolling counter |
| Wake events in last 24h | rolling counter, broken down by target harness |
| Last wake event | timestamp, target harness, reason (`document=X transitioned NEW→GO`) |

New tile: **Harness Registry**

| Harness | Role | Session start | Last seen | Status |
|---|---|---|---|---|
| claude-code-12484 | prime-builder | 08:00:00Z | 10:53:00Z | active |
| codex-7891 | loyal-opposition | 09:15:00Z | 10:54:00Z | active |

New tile: **Bridge In-Flight**

(This already exists in concept via INDEX, but the dashboard renders it visually.)

| Document | Top status | Pending action | Pending action by |
|---|---|---|---|
| gtkb-dora-001b-track1-implementation | REVISED -003 | re-review | Codex |
| gtkb-isolation-016-phase8-wave2-implementation | REVISED -003 | re-review | Codex |

Dashboard refresh reads from `~/.gtkb-state/bridge-poller/state.json` (poller's own state) and `bridge/INDEX.md` (in-flight summary). No new database table needed.

## 5. Owner's Question 4 — Controls + failure detection + restart

**Yes.**

### 5.1 CLI controls

```
gt bridge-poller start [--foreground] [--interval-seconds 5]
gt bridge-poller stop
gt bridge-poller status [--json]
gt bridge-poller reset            # clears state checkpoint; next run treats INDEX as fully-new
gt bridge-poller wake <harness>   # manual wake (testing/debug)
```

### 5.2 Dashboard controls

Buttons in the Bridge Poller Status tile invoke the CLI commands via a thin local shell:

- ▶ Start (only enabled if status=stopped)
- ⏹ Stop (only enabled if status=running)
- 🔄 Reset checkpoint (with confirmation modal)

Implementation note: dashboard runs locally; calling the CLI is straightforward subprocess invocation. No web API surface needed.

### 5.3 Failure detection + auto-restart

**Heartbeat:** poller writes `~/.gtkb-state/bridge-poller/heartbeat` every poll cycle. File contents = ISO timestamp.

**Watchdog:** separate lightweight Python process (`gt bridge-watchdog`) checks heartbeat freshness every 30 seconds. If heartbeat is older than 90 seconds AND the poller's *target state* is `running` (per `target_state.json` set by start/stop commands), watchdog re-launches the poller. Logs every action to `~/.gtkb-state/bridge-poller/watchdog.log` with size cap.

**Watchdog meta-failure:** if the watchdog itself dies, the dashboard's poller-status tile shows `degraded` (heartbeat stale, but watchdog also not running). Owner sees this and intervenes manually. Avoids infinite watchdog-watching-watchdog regress.

This is the visibility independent of the poller pattern from the bridge-essential.md S290 lesson.

## 6. Owner's Question 5 — Cross-platform strategy

**Yes**, with a thin platform-specific layer for service installation only.

### 6.1 Logic that's platform-agnostic (Python)

- INDEX.md parsing
- State diff + trigger routing
- Harness registration / liveness check (via `psutil`, which works cross-platform)
- Heartbeat + watchdog logic
- CLI surface
- Dashboard data emission

### 6.2 Platform-specific (small adapter layer)

| Concern | Windows | Linux | macOS |
|---|---|---|---|
| Service install | Scheduled Task (or NSSM-wrapped) | systemd user unit | launchd plist |
| Wake mechanism (default) | File touch + harness's hook detects | File touch + harness's hook detects | File touch + harness's hook detects |
| Wake mechanism (advanced) | Toast via `winrt.Windows.UI.Notifications` (optional) | `notify-send` (optional) | `osascript display notification` (optional) |
| State dir | `%LOCALAPPDATA%\gtkb-state\bridge-poller\` | `${XDG_STATE_HOME:-~/.local/state}/gtkb/bridge-poller/` | `~/Library/Application Support/gtkb/bridge-poller/` |

The default wake mechanism is **file touch** because it works identically everywhere and the harness-side hook detection is already an established pattern (UserPromptSubmit, SessionStart). The optional toast/notify is gravy.

Service install is the only meaningful platform delta. We provide:

- `gt bridge-poller install-service [--platform auto]` — generates the right unit/task/plist for the host
- Adopters can also install manually if they prefer (templates committed in `templates/bridge-poller-service/`)

### 6.3 Wake-detection hook (harness-side, already exists in pattern)

When the poller wakes a harness, it touches the registered `wake_target` file. The harness's existing UserPromptSubmit hook (or equivalent) detects the file mtime change and prepends a synthetic system message: `"Bridge poller signal: scan INDEX.md for new actionable entries."` The harness then processes as if owner had typed `bridge`.

This means the harness-side integration is **just one hook file per harness** — and we already have hook infrastructure tracked in git (`.claude/hooks/`, `.codex/hooks.json`).

## 7. Architectural Risks + Mitigations

| Risk | Mitigation |
|---|---|
| Wake storm (many state changes in quick succession) | Per-harness rate limit (default 60s between wakes); excess events coalesced into single wake |
| INDEX corruption / partial write | Atomic read (poller copies to temp, validates, then parses); on parse failure, log and skip cycle |
| Two harnesses both register as PB (or both as LO) | Refuse to route; log to dashboard `harness_registry_conflict`; owner resolves by changing one durable role record |
| Stale registration after harness crash | Liveness check (process exists / heartbeat fresh) before every wake; stale entries auto-removed |
| Poller running on host A; harness running on host B | Out of scope for v1 (single-host assumption); v2 could add SSH/socket but not now |
| Token-cost regression slip-back | Hard rate cap; dashboard shows wakes-per-day; alert threshold (e.g., > 100 wakes/day) flags for owner review |
| Watchdog meta-failure | Dashboard shows degraded state; owner manual intervention is the escape hatch |

## 8. Rollout Sequence

| Phase | Scope | Codex review |
|---|---|---|
| **P1** | INDEX parser + state diff + trigger routing logic + tests; no actual wakes yet | one bridge |
| **P2** | Harness registry (read/write + liveness) + SessionStart hook samples for Claude Code and Codex | one bridge |
| **P3** | Wake mechanism (file touch) + harness-side hook for wake detection + per-harness rate limit | one bridge |
| **P4** | CLI (`start/stop/status/reset/wake/install-service`) + watchdog + heartbeat | one bridge |
| **P5** | Dashboard tiles (Bridge Poller Status, Harness Registry, Bridge In-Flight) | one bridge |
| **P6** | Service install templates per platform + docs | one bridge |
| **P7** | Adopter follow-up (Agent Red SessionStart hook installation + role registration) | one bridge after upstream VERIFIED |

P1-P6 land upstream in `groundtruth-kb`. Each phase is independently testable and shippable. P7 is Agent Red specific.

P1 is the foundation that proves the parser and routing work without any actual wake machinery; if Codex NO-GOs P1, no harm done because no real triggers fire yet.

## 9. Out of Scope (this work item)

- Cross-host pollers (single-host assumption for v1)
- Wake mechanism over network sockets / SSH
- Re-enabling the OLD Windows scheduled-task poller infrastructure (`AgentRedFileBridgeIndexScan-*`, etc.) — those stay disabled; this is a fresh, smart replacement
- Token-cost telemetry beyond a simple counter (proper telemetry is GTKB-DORA-001/002 scope)
- Bridge file lifecycle (compaction, archival) — separate concern

## 10. Codex Review Asks

1. Confirm the cost/benefit analysis in §1 satisfies `.claude/rules/bridge-essential.md` "Re-Enabling Pollers" gate.
2. Confirm INDEX.md parser approach in §2 (skip comments + blanks; top-of-list = current status; trigger routing table) is correct given current INDEX format.
3. Confirm harness registration design in §3 supports the existing per-harness role records and avoids the dual-role overwrite class S294 surfaced.
4. Confirm dashboard surface design in §4.2 (3 new tiles, all sourced from filesystem state, no new DB tables) is the right scope vs adding KB rows.
5. Confirm watchdog + heartbeat pattern in §5.3 avoids the infinite-watchdog regress while still fixing the S290 silent-failure pattern.
6. Confirm cross-platform strategy in §6 (Python core + thin platform adapter; file-touch wake) is the right shape vs more aggressive platform-specific optimization.
7. Confirm phase split in §8 is the right granularity vs fewer/larger bridges.
8. **GO / NO-GO** on the scoping.

## 11. Decisions Needed From Owner

After Codex GO, before P1 implementation:

1. **Default poll interval.** Suggest 5 seconds (low latency, negligible CPU). Owner might prefer slower (15s) if any concern about disk thrash on the INDEX file.
2. **State directory location.** Defaults are platform-appropriate per §6.2; owner can override for visibility (e.g., put under `E:\GT-KB\.gtkb-state\` if they want to git-status it — but that risks Drive sync, so the default is per-user state dirs).
3. **Initial deployment scope.** Ship the framework upstream first (P1-P6), then Agent Red adoption (P7) as a separate bridge? Or skip ahead and pilot in Agent Red while upstream still in flight? Recommend the former (cleaner rollback path).

## 12. Relationship to Other Work

- **`GTKB-DB-BACKUP-001`** (S311 in flight): no overlap; backup daemon and bridge poller are independent capabilities
- **`GTKB-COMMAND-SURFACE`** (in flight): the `::bridge` command anticipated in CS-3 could become "manual override of the smart poller" once both ship
- **`GTKB-ISOLATION-016/017/018/019`** (isolation program): the smart poller registry could later be the placeholder for Phase 8/9 cross-application coordination, but not yet
- **`bridge-essential.md` rule update**: after VERIFIED, this rule should be updated to reference the new poller as the *current* mechanism and explain when to use it vs manual scans

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
