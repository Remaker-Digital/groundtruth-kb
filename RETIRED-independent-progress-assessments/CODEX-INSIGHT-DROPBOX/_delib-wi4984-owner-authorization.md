author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 901d970b-b437-4794-83bc-b84ac044f8d9
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; ::init gtkb lo; auto-process loop; resolved role loyal-opposition

# Owner Authorization — WI-4984 Deterministic State-Report CLI

## Decision

Owner authorized building **WI-4984** (deterministic `gt bridge state-report` CLI)
via **Codex-A Prime Builder** under **PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION**.
This session (Claude, Loyal Opposition) stays the reviewer; it does not implement.

## Context

The auto-process loop emits a compact bridge/dispatcher/harness state report the
owner wants reusable for the current dispatcher-daemon/harness work. Per
`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`, the durable form is a deterministic
read-only CLI, not AI re-derivation each loop fire. Captured as backlog `WI-4984`
(P1, origin=improvement, component=maintenance_tool).

## AskUserQuestion Evidence

- Question: how to deliver WI-4984 given LO cannot write source.
- Options presented: (1) switch this session to Prime Builder and build now;
  (2) keep LO, route to Codex-A; (3) interim-only via loop/on-demand.
- Owner answer: **"Keep me LO; route to Codex-A."**

## Authorization Scope

- Codex-A (Prime Builder) may implement `WI-4984` via the bridge protocol
  (proposal → independent LO `GO` → implement → independent LO `VERIFIED`) under
  `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION`.
- Scope: a read-only `gt bridge state-report [--json] [--markdown]` CLI reusing
  `scripts/bridge_thread_files.py` (the WI-4977 exact-thread helper) plus focused
  tests. Emits BRIDGE (thread count, LO-actionable list, latest-status mix),
  DISPATCHER (health + selected candidates + findings), HARNESSES
  (role/active/dispatchable/fires_events table). No source beyond the report tool
  and its tests; no dispatcher-behavior or topology changes.
- Loyal Opposition (this session and successors) verifies; the auto-process loop
  keeps running as LO.
