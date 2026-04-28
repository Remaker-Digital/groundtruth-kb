---
name: Codex Desktop automation dispatch failure
description: Codex heartbeat automations silently fail — scheduler advances next_run_at without creating runs. Use OS cron + codex exec instead.
type: project
---

Codex Desktop automations do not reliably dispatch runs. The `automations` table has active records with advancing `next_run_at`, but `automation_runs` and `inbox_items` are never created. This is a platform-level issue confirmed by independent reports.

**Why:** Schema mismatch between config and runtime layers. The TOML config stores `kind=heartbeat` and `target_thread_id`, but the runtime DB (`codex-dev.db`) has a generic `automations` table that doesn't store `kind` or `target_thread_id`. The scheduler loop advances `next_run_at` mechanically but can't dispatch because it doesn't know the automation type or target thread. `last_run_at` stays NULL, `automation_runs` stays empty. Multiple teams have independently abandoned Desktop automations for external scheduling.

**How to apply:** Do not rely on Codex Desktop automations for the bridge poller or any recurring Codex work. Use Windows Task Scheduler + `codex exec` for reliable Codex-side polling. The bridge protocol's asynchronous design tolerates polling delays — Codex reviewing every 5-10 minutes via OS cron is functionally equivalent to the intended 3-minute automation.

**Discovered:** S281 (2026-04-11). Codex investigated after repeated bridge scan failures.
