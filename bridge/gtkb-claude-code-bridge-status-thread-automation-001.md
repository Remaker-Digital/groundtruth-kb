NEW

# Implementation Proposal — Claude Code Bridge-Status Thread Automation (Axis 2 Parity)

bridge_kind: implementation_proposal
Document: gtkb-claude-code-bridge-status-thread-automation-001
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-09 UTC

## Claim

Close the harness-parity gap on Axis 2 of the bridge automation model (interactive bridge-status reporting). Currently asymmetric: Codex has `monitor-gt-kb-bridge` (3-min cadence) and `gt-kb-bridge-monitor` (30-min cadence) thread automations that wake the interactive chat to scan `bridge/INDEX.md` and surface non-dispatchable work. Claude Code has no equivalent. Per owner directive 2026-05-09: *"everything we do needs to be paralleled by Claude Code, for both Loyal Opposition and Prime Builder roles as applicable. The cron job report on bridge status is very useful for both roles."*

This proposal investigates Claude Code's available scheduling primitives, proposes a concrete implementation that mirrors Codex's app-thread pattern functionally (not mechanically — Claude Code lacks Codex's app-thread feature), addresses Slice-4-retirement compatibility (axis-1 dispatch automation was retired; this is axis-2 status automation, a different role), and files the system-interface-map.toml entry when the implementation lands.

## Why Now

Owner directive 2026-05-09 — the bridge-status thread automation is "very useful for both roles" and "everything we do needs to be paralleled by Claude Code." Codex's existing automations (inventoried as `monitor-gt-kb-bridge-codex-thread` and `gt-kb-bridge-monitor-codex-thread` in `config/agent-control/system-interface-map.toml`) provide periodic bridge-status visibility to the running Codex session for non-dispatchable work — owner-AUQ-required decisions, multi-turn review, cross-thread coordination. Claude sessions get no equivalent visibility unless the owner manually types `Bridge` to trigger a scan.

The asymmetry creates a real operational gap: a long-running Claude Code session as Loyal Opposition (when the role is assigned to Claude) or as Prime Builder (current configuration) doesn't see bridge state changes until the next manual prompt. The cross-harness event-driven trigger spawns FRESH counterpart sessions but does NOT refresh already-running ones (per the Axis 1 / Axis 2 split codified in `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001-003` REVISED-1).

Closing this parity gap is consistent with `.claude/rules/acting-prime-builder.md` § "General Principle": *"the roles of Prime Builder and Loyal Opposition are not permanently bound to one model name or vendor harness."* Roles attach to harnesses by owner assignment; harnesses should be peer-equivalent in capability.

## Why Not (Slice-4-retirement compatibility analysis)

Slice 4 (`bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001`, VERIFIED at `-020`) retired Windows scheduled tasks for bridge polling. Specifically:
- `AgentRedFileBridgeIndexScan-Claude`, `AgentRedFileBridgeIndexScan-Codex`, `AgentRedBridgeLivenessAlert`, `AgentRedPollerLivenessWatcher` (OS poller class, halted 2026-04-25)
- `GTKB-SmartBridgePoller` (smart poller, halted 2026-05-09)

These were ALL **Axis 1 dispatch automations** — they spawned counterpart harnesses to do bridge work autonomously. They were retired because:
1. The cross-harness event-driven trigger does the same dispatch job event-driven (no fixed interval needed).
2. Token-cost regressions: 173 Claude capped-spawns/day at peak (smart poller); 480 wakes/day (3-min cadence); fixed-interval automation scales faster than the work it serves.

This proposal targets **Axis 2 status automation** — a different role:
- Axis 2 wakes the running interactive session for status visibility; does NOT spawn counterpart harnesses.
- Axis 2 does NOT replace the cross-harness event-driven trigger.
- Token cost is per-wake (Claude session reads INDEX, reports state, exits); no harness-spawn cost beyond the wake itself.

A Windows scheduled task that invokes `claude -p "Bridge"` on a 30-minute cadence is therefore Slice-4-compatible: it's not in the retired axis-1 class. The Slice 4 § "Operational Mode" rules in `.claude/rules/bridge-essential.md` explicitly distinguish: *"Both the retired OS bridge pollers (halted 2026-04-25) and the smart poller (retired 2026-05-09) are disabled. The cross-harness event-driven trigger is the canonical bridge automation path while it remains healthy."* The retirement applies to dispatch automation, not status automation.

This proposal coordinates with `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001-003` REVISED-1 (which articulates the Axis 1 / Axis 2 model in narrative authority) — the two-axis model legitimizes Axis 2 status automation as a first-class architectural surface.

## Investigation: Claude Code Scheduling Primitives

Three options surveyed; trade-offs documented.

### Option A: Windows scheduled task invoking `claude -p "Bridge"` (RECOMMENDED)

**Mechanism:** Windows Task Scheduler runs a periodic task (e.g., every 30 minutes) that invokes `claude -p "Bridge"` against the GT-KB project root. Each invocation:
- Wakes a fresh Claude Code session in `--print` (non-interactive) mode.
- Sends the prompt "Bridge" (which Claude interprets as a bridge scan request per `.claude/rules/bridge-essential.md` § "Operational Mode" manual-bridge-scan fallback).
- Claude reads `bridge/INDEX.md`, reports the actionable queue state, exits.
- The output is logged to a per-task log file under `.gtkb-state/bridge-poller/claude-status-runs/` (mirroring the smart-poller audit-log path naming convention but with a clearly distinct subdirectory).

**Mirror to Codex:** Codex's app-thread automation creates a periodic prompt; this Windows scheduled task creates a periodic prompt invocation. Functionally equivalent; mechanically different (Claude Code lacks an app-thread feature).

**Pros:**
- Available today; no Claude Code product surface required.
- Owner-manageable via standard Windows Task Scheduler UI.
- 30-min cadence matches `gt-kb-bridge-monitor` (Codex 30-min); 10x token-cost reduction vs the retired smart-poller pattern.
- Each invocation is fully ephemeral (session spawns, reports, exits) — no long-lived state.

**Cons:**
- Slice-4-retirement framing on Windows scheduled tasks may cause confusion ("isn't this a poller?"). Mitigation: this proposal explicitly distinguishes axis-2 status from axis-1 dispatch; the Slice 4 retirement was specifically axis-1.
- Output is to a log file (not a chat stream); owner must check the log or the next manual chat invocation will surface stale state. This is a real cons but acceptable: the use case is "owner periodically checks log to see queue state when not actively in a Claude session"; for in-session visibility, the cross-harness trigger handles dispatch.
- Each `claude -p` invocation has a session-start cost (~50k tokens per session start per S308 measurement). At 30-min cadence: 48 wakes/day × 50k = 2.4M tokens/day. This is significant. Mitigation: the cadence can be lower (60-min: 24 wakes/day = 1.2M; daily: 1 wake = 50k). Or Option B (in-session ScheduleWakeup) avoids the per-session-start cost when a Claude session is already running.

### Option B: In-session `ScheduleWakeup` tool (loop mode)

**Mechanism:** When a Claude Code session is running, the agent uses the `ScheduleWakeup` tool to schedule periodic self-wake-ups within the session (e.g., 30-min `delaySeconds = 1800`). Each wake-up the agent re-reads `bridge/INDEX.md` and reports state.

**Pros:**
- No per-wake session-start cost (uses existing session).
- Cache-warm: 30-min wake-ups stay outside the prompt-cache 5-min TTL but only pay one cache-miss per wake.

**Cons:**
- Only works while a Claude session is RUNNING. Doesn't survive `/exit` or session termination.
- Requires the user to be in a Claude Code session AND to invoke the loop deliberately. Doesn't satisfy "always-on bridge-status visibility" use case.
- Conflicts with normal session work — wake-ups interrupt the agent's current task; the loop semantic is "task on a schedule" not "status reporter on a schedule."

**Verdict:** does NOT match Codex's app-thread pattern. Useful as an in-session occasional-check pattern, not as the parity primitive.

### Option C: `mcp__scheduled-tasks__*` MCP tools (if available)

**Mechanism:** Use `mcp__scheduled-tasks__create_scheduled_task` (a deferred MCP tool surfaced in this session's tool list) to create a Claude-native scheduled task that survives session boundaries.

**Pros:**
- Claude-native (no Windows-specific dependency; works on any platform Claude Code runs on).
- Owner-manageable via `mcp__scheduled-tasks__list_scheduled_tasks` and `mcp__scheduled-tasks__update_scheduled_task`.

**Cons:**
- Requires the `scheduled-tasks` MCP server to be installed and configured. Not all Claude Code installations have it.
- The deferred MCP tools are listed but not invoked in this session; their behavior under the bridge-status-report use case is untested.
- Documentation gap: the tool description doesn't specify whether it spawns fresh `claude -p` sessions or invokes a different mechanism. Investigation needed.

**Verdict:** plausible, depends on MCP availability. Investigation deferred to a follow-on if Option A proves insufficient.

### Recommendation

**Option A** (Windows scheduled task + `claude -p "Bridge"` at 60-min cadence): cleanest path, available today, mirrors Codex's owner-managed app-thread pattern functionally. 60-min instead of 30-min reduces token cost (24 wakes/day × 50k = 1.2M tokens/day; comparable to or below Codex's 30-min `gt-kb-bridge-monitor` cost). The smaller frequency is acceptable because:
- Axis 2 is for non-time-critical status visibility; 60-min cadence still gives the owner reasonable freshness.
- The cross-harness event-driven trigger (Axis 1) handles time-critical dispatch on every actionable INDEX change.
- If higher frequency is needed in practice, the cadence is owner-tunable via Task Scheduler.

## Prior Deliberations

- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-020.md` (VERIFIED) — Slice 4 retired Axis-1 dispatch automation. This proposal targets Axis 2 (different role; not retired class).
- `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001-003.md` (REVISED-1, awaiting Codex review) — articulates the Axis 1 / Axis 2 model. This proposal applies the model to close a parity gap.
- `system-interface-map.toml id = "monitor-gt-kb-bridge-codex-thread"` and `id = "gt-kb-bridge-monitor-codex-thread"` — Codex-side equivalents.
- `.claude/rules/acting-prime-builder.md` § "General Principle" — roles are portable across harnesses; harnesses should be peer-equivalent.
- Owner directive 2026-05-09: parity is mandatory for capabilities applicable to both roles; cron-job bridge-status is a specific example.
- `DELIB-S308-OS-POLLER-TOKEN-COST-REGRESSION` (referenced by Slice 4) — token-cost discipline applies; this proposal's cost analysis (1.2M tokens/day at 60-min cadence) addresses the discipline.

## Specification Links

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001` — INDEX-as-canonical-state preserved.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this Specification Links section satisfies the linkage gate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Spec-Derived Test Plan section maps cited specifications to tests.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched files under `E:\GT-KB`. The Windows scheduled task is owner-managed (out-of-repo state; mirrors Codex's app-thread inventory pattern).
- `GOV-ARTIFACT-APPROVAL-001` v3 — formal-artifact-approval packets if any narrative-authority files are touched.

**Cross-cutting (advisory):**

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — new system-interface-map.toml entry is a lifecycle event.

**Specs created by this slice:** zero. The architectural model (two-axis bridge automation) is articulated by the in-flight `gtkb-startup-trigger-awareness-and-skill-reference-001-003` thread; this thread implements one harness-side instance of Axis 2.

## Owner Decisions / Input

- Owner directive 2026-05-09 (recurring parity principle): "everything we do needs to be paralleled by Claude Code, for both Loyal Opposition and Prime Builder roles as applicable."
- AUQ "File NEW parity-work thread + leave -003 Open Follow-On unchanged (Recommended)" 2026-05-09 — owner authorized this thread.
- During implementation: 1 owner AUQ to confirm cadence choice (60-min recommended; 30-min and daily as alternatives).
- During implementation: 1 owner action to create the Windows scheduled task via `schtasks` or Task Scheduler UI (mirrors Codex app-thread setup pattern; out-of-repo state).

## Pre-Filing Preflight

Per `.claude/rules/file-bridge-protocol.md`. Re-run after this NEW entry is added to `bridge/INDEX.md`. Expected `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.

## Implementation Plan

### IP-1 — Add `[[systems]]` entry for Claude-Code-side bridge-status thread

Add new entry in `config/agent-control/system-interface-map.toml`:

```toml
[[systems]]
id = "claude-code-bridge-status-windows-task"
canonical_name = "Claude Code bridge-status thread automation (Windows scheduled task)"
accepted_aliases = ["Claude Code bridge monitor", "claude-bridge-status", "Claude bridge thread"]
discouraged_aliases = ["bridge poller", "smart poller"]
forbidden_aliases = []
concept_vs_artifact = "supplemental_monitoring"
authoritative_source = "Windows Task Scheduler config (external; owner-managed via schtasks or Task Scheduler UI; not in-repo state)"
generated_or_authoritative = "external_runtime"
read_method = "Inspect via Task Scheduler UI or `schtasks /Query /TN <task name>`; runtime trace at `.gtkb-state/bridge-poller/claude-status-runs/` (mirrors Codex audit-log path naming)."
mutation_method = "Owner-managed via Windows Task Scheduler. Not modifiable from within E:/GT-KB."
role_permissions = "Claude Code-side equivalent of Codex `gt-kb-bridge-monitor`. Wakes a fresh Claude Code session every N minutes (default 60-min) to read `bridge/INDEX.md` and report state. Does NOT spawn counterpart harness, update dispatch-state.json, or replace the cross-harness event-driven trigger (axis 1). Mirrors the axis-2 status reporting role of Codex's `monitor-gt-kb-bridge-codex-thread` and `gt-kb-bridge-monitor-codex-thread`."
startup_visibility = "none"
dashboard_visibility = "none"
harness_caveats = "Claude Code-side parity for axis 2 (interactive bridge-status reporting; non-dispatchable work surfacing). Owner-managed Windows scheduled task; mirrors Codex's app-thread automation functionally. Not the same class as the retired Slice 4 Windows scheduled tasks (those were axis-1 dispatch; this is axis-2 status). Token cost: ~50k per wake; at 60-min cadence = 24 wakes/day = 1.2M tokens/day."
verification_method = "Owner observation; runtime audit log under .gtkb-state/bridge-poller/claude-status-runs/."
lifecycle_state = "active"
related_specs = []
related_deliberations = []
```

### IP-2 — Add `claude-code-bridge-status-windows-task` to `scripts/resolve_system_interface.py` REQUIRED_SEED_IDS

One-line addition; mirrors prior pattern from `monitor-gt-kb-bridge-codex-thread` and `gt-kb-bridge-monitor-codex-thread`.

### IP-3 — Setup script `scripts/setup_claude_code_bridge_status_task.ps1`

PowerShell script that:
1. Registers a Windows scheduled task named `GTKB-ClaudeCodeBridgeStatus`.
2. Configures it to invoke `claude -p "Bridge"` against `E:\GT-KB`.
3. Default cadence: 60 minutes (configurable via `-IntervalMinutes` parameter).
4. Logs to `.gtkb-state/bridge-poller/claude-status-runs/<timestamp>.log`.
5. Idempotent: re-running updates the existing task in place.

The script is parallel to `scripts/install_smart_poller_task.ps1` (archived under `archive/smart-poller-2026-05-09/`) but for axis-2 status, not axis-1 dispatch. Per Slice 4 retirement framing, this is a different role and a different class.

### IP-4 — Owner-managed setup pattern

Document the owner-action setup pattern (`.gtkb-state/bridge-poller/claude-status-runs/README.md` or in `groundtruth-kb/docs/tutorials/`):

1. Owner runs the setup script once: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/setup_claude_code_bridge_status_task.ps1 -IntervalMinutes 60`.
2. Verify: `Get-ScheduledTask -TaskName GTKB-ClaudeCodeBridgeStatus | Format-Table TaskName, State, NextRunTime`.
3. Inspect logs: `Get-ChildItem .gtkb-state/bridge-poller/claude-status-runs/ | Sort-Object LastWriteTime -Descending | Select -First 5`.
4. Adjust cadence: re-run setup with `-IntervalMinutes <new>`.
5. Disable: `Disable-ScheduledTask -TaskName GTKB-ClaudeCodeBridgeStatus`.
6. Remove: `scripts/remove_claude_code_bridge_status_task.ps1` (sibling teardown script).

### IP-5 — Tests

- `tests/scripts/test_setup_claude_code_bridge_status_task.py` — verify the PowerShell script exists, parses without syntax error, and produces a valid `schtasks /Create` payload (dry-run mode).
- `tests/scripts/test_system_interface_map.py` — extend REQUIRED_SEED_IDS check to include `claude-code-bridge-status-windows-task` (existing test should pass after IP-2).
- No automated test for the actual scheduled-task registration (out-of-repo state; owner-managed).

## Spec-Derived Test Plan

| Test | Spec/Requirement | Method |
|---|---|---|
| T-CCBS-system-interface-map-entry-present | IP-1 | `system-interface-map.toml` contains `id = "claude-code-bridge-status-windows-task"` entry with `lifecycle_state = "active"`. |
| T-CCBS-required-seed-ids-includes-claude | IP-2 | `scripts/resolve_system_interface.py` REQUIRED_SEED_IDS includes the new id. |
| T-CCBS-setup-script-exists-and-parses | IP-3 | `scripts/setup_claude_code_bridge_status_task.ps1` exists; PowerShell parser accepts it (ParseError empty). |
| T-CCBS-setup-script-dry-run-payload | IP-3 | Dry-run mode (e.g., `-WhatIf` or environment variable) produces a `schtasks /Create` payload referencing `claude -p "Bridge"` and the project root. |
| T-CCBS-axis-2-not-axis-1 | IP-1 + Slice-4-retirement compat | Setup script does NOT register a task with `bridge_poller_runner.py` invocation OR `cross_harness_bridge_trigger.py` dispatch invocation. Task command line invokes `claude -p` only. |

## Acceptance Criteria

- [ ] Codex confirms IP-1 system-interface-map.toml entry correctly classifies the automation as axis-2 supplemental monitoring (not axis-1 dispatch).
- [ ] Codex confirms IP-3 setup script is functionally parallel to Codex's `gt-kb-bridge-monitor` thread (60-min cadence; status-only; no dispatch).
- [ ] Codex confirms the Slice-4-retirement compatibility argument (axis 1 retired; axis 2 different class) holds.
- [ ] Codex confirms token-cost analysis (1.2M tokens/day at 60-min) is acceptable; cadence tunable.
- [ ] Codex confirms IP-4 owner-managed setup pattern mirrors the Codex-side app-thread setup pattern functionally.

## Risk / Rollback

- **Risk:** future readers might confuse this Windows scheduled task with the retired Slice 4 pollers. Mitigation: distinct task name (`GTKB-ClaudeCodeBridgeStatus`); explicit axis-2-not-axis-1 framing in setup script header comment AND in system-interface-map.toml `harness_caveats`; cross-references to the two-axis model in `.claude/rules/bridge-essential.md`.
- **Risk:** token-cost overrun if cadence is set too aggressively. Mitigation: setup script defaults to 60-min; warns if `-IntervalMinutes < 30`; teardown script available.
- **Risk:** `claude -p` session might block on owner-AUQ-required decisions and time out. Mitigation: each session is ephemeral; if it doesn't complete in the task's timeout window, the next wake produces a fresh session. Bridge state visibility is restored on the next successful wake.

**Rollback:**
- Owner runs `scripts/remove_claude_code_bridge_status_task.ps1` to remove the scheduled task.
- Revert IP-1 system-interface-map.toml entry.
- Revert IP-2 REQUIRED_SEED_IDS addition.
- Delete the setup/teardown scripts.

## Files Expected To Change

- `config/agent-control/system-interface-map.toml` — IP-1 new `[[systems]]` entry.
- `scripts/resolve_system_interface.py` — IP-2 REQUIRED_SEED_IDS extension.
- `scripts/setup_claude_code_bridge_status_task.ps1` (NEW) — IP-3 PowerShell setup script.
- `scripts/remove_claude_code_bridge_status_task.ps1` (NEW) — IP-3 teardown script.
- `.gtkb-state/bridge-poller/claude-status-runs/README.md` (NEW) — IP-4 owner-managed setup pattern documentation.
- `tests/scripts/test_setup_claude_code_bridge_status_task.py` (NEW) — IP-5 test surface.
- `tests/scripts/test_system_interface_map.py` — implicit update via REQUIRED_SEED_IDS extension.
- `bridge/gtkb-claude-code-bridge-status-thread-automation-001.md` (this proposal).
- `bridge/INDEX.md` (NEW entry).

## Open Follow-Ons

1. Future: if Claude Code adds a native app-thread-automation feature (similar to Codex's), migrate from Windows-scheduled-task to native automation; supersede the system-interface-map.toml entry's `concept_vs_artifact` value if the new feature changes the architectural classification.
2. Future: if the `mcp__scheduled-tasks__*` MCP tools become widely available in Claude Code installations, evaluate them as a Claude-native alternative to Windows scheduled tasks (cross-platform compatibility).
3. Future: cadence evolution — token-cost data after 30+ days of operation may suggest tuning (60-min could go up to 4-hourly or down to 30-min based on observed value).
4. Future: parity audit — survey all Codex-side capabilities; identify any other asymmetries; file individual parity threads.

## Recommended Commit Type

`feat:` — net-new capability surface (Claude-Code-side bridge-status thread automation; harness-parity work). Per `bridge/gtkb-governance-hygiene-bundle-001.md` Change B discipline.

## Loyal Opposition Asks

1. Confirm the axis-2-not-axis-1 framing addresses Slice-4-retirement compatibility (this is status automation, not dispatch automation; different class than the retired pollers).
2. Confirm the Option A (Windows scheduled task + `claude -p "Bridge"`) recommendation over Options B (`ScheduleWakeup`) and C (`scheduled-tasks` MCP).
3. Confirm 60-min cadence is appropriate (token cost ~1.2M/day; tunable).
4. Confirm the system-interface-map.toml entry classification (`concept_vs_artifact = "supplemental_monitoring"`) — same as the Codex-side entries; mirrors the inventory pattern.
5. Confirm the owner-managed setup pattern (PowerShell script + Task Scheduler UI) mirrors Codex's owner-managed app-thread pattern functionally.
6. Confirm scope reduction is appropriate (zero new specs/DCLs/DELIBs in this slice; the architectural model is in `gtkb-startup-trigger-awareness-and-skill-reference-001-003`).

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
