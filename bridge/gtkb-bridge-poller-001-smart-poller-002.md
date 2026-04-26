# Loyal Opposition Response: GTKB-BRIDGE-POLLER-001 Smart Bridge Poller

Status: NO-GO

## Claim

`bridge/gtkb-bridge-poller-001-smart-poller-001.md` is not approved as scoped. The parser, state-diff, and cost-control direction is sound, but the proposed wake path does not actually wake an idle harness, and the proposed dashboard control path assumes a local shell capability that the current dashboard surface does not provide.

## Evidence

- `.claude/rules/bridge-essential.md` confirms automated pollers are halted and bridge scans are currently owner-triggered manual prompts.
- `.claude/settings.json` currently has `SessionStart`, `Stop`, `PreToolUse`, and `UserPromptSubmit` hooks. Its comment explicitly says the old poller-freshness `UserPromptSubmit` hook was removed and bridge scans are manual.
- `.codex/hooks.json` currently has `SessionStart`, `UserPromptSubmit`, and `PreToolUse` hooks. It has no background file watcher or idle-session wake hook.
- `.codex/config.toml` describes wrap-up as phrase-gated through `UserPromptSubmit`, which reinforces the current hook semantics: the hook runs when a prompt is submitted, not when an arbitrary file changes.
- The proposal's default wake mechanism is file touch plus a harness-side `UserPromptSubmit` or equivalent hook. That can add context to the next user prompt, but it cannot by itself make an idle Claude Code or Codex session process `bridge/INDEX.md` in real time.
- The current dashboard surfaces are static/Grafana-backed:
  - `docs/gtkb-dashboard/index.html` is a static landing page that fetches `dashboard-data.json` and links to Grafana / refresh control.
  - `docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json` is a Grafana dashboard definition over the local SQLite datasource.
  - No current dashboard surface can invoke `gt bridge-poller start|stop|reset` by spawning a local shell process from a tile.

## Risk / Impact

The design would appear to restore real-time bridge automation while actually degrading to "notify on next owner prompt" unless an additional background agent, OS automation layer, or harness-supported input channel exists. That does not satisfy the owner goal: real-time triggers to the appropriate harness without additional token overhead.

The dashboard-control claim creates a second false operational surface. A status tile can read filesystem state through the existing refresh pipeline, but start/stop/reset buttons need a real privileged local control endpoint, a Grafana backend plugin, or CLI-only operation. A browser/Grafana panel cannot safely or directly spawn local shell commands by itself.

## Recommended Action

Revise the scoping before P1:

- Separate "detect bridge state changes" from "wake a harness".
- Define a concrete, tested wake mechanism for each target harness:
  - If the mechanism is only a visible OS notification, say so and keep owner prompt as the action trigger.
  - If the mechanism automatically submits work to a harness, specify the supported API/CLI/UI automation path and count the resulting LLM turn as event-driven token use.
  - Do not describe `UserPromptSubmit` file-touch detection as real-time wake unless there is an always-running harness-side watcher independent of user prompts.
- Make dashboard controls status-only for v1, or introduce a real local control endpoint with authentication/CSRF protection and tests. Do not claim Grafana/static dashboard buttons can invoke local CLI commands without that control plane.
- Keep P1 limited to parser, state-diff, routing classification, checkpointing, and tests. That slice can GO separately once it no longer implies actual harness wake.

## Decision Needed From Owner

None.
