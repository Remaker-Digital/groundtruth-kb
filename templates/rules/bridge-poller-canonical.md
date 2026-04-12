# Bridge Poller Canonical Instructions

This file is the canonical source of truth for file bridge poller behavior.
It applies to any automation, scheduled task, or wake prompt that keeps the
Prime Builder <-> Loyal Opposition bridge operational.

## Core Rule

The active bridge is file-based. The authoritative queue is `bridge/INDEX.md`.
Pollers must inspect the latest status for each bridge document entry and must
not use the archived SQLite/MCP bridge runtime as the active queue.

The owner is an observer unless the owner explicitly intervenes.

## Required Behavior

### 1. Read the File Bridge Index First

- Open `bridge/INDEX.md`.
- Treat document entries as newest-first.
- For each document entry, inspect only the latest status line.
- Historical status lines are evidence, not current work.

### 2. Use Direction-Specific Filters

Loyal Opposition pollers process only latest statuses:

- `NEW`
- `REVISED`

Prime Builder pollers process only latest statuses:

- `GO`
- `NO-GO`

`VERIFIED` is terminal. It must not trigger Prime Builder action.

### 3. Process Work Through Numbered Bridge Files

- Read the referenced bridge document and supporting artifacts.
- Perform the required review or response.
- Write the next numbered bridge document.
- Add the corresponding latest status line at the top of that document entry
  in `bridge/INDEX.md`.

### 4. Do Not Route Through the Owner

- Do not wait for owner relay when the bridge entry is actionable.
- Only surface a blocker to the owner when a true external decision is
  required, such as product direction, destructive action, or scope change.

### 5. Use OS Scheduler State as the Reliability Boundary

- Recurring bridge scans should run from an OS scheduler.
- App-native automations may be supplemental, but they are not authoritative
  unless they produce durable run records across sessions.
- Each scheduled run should log clear scans as well as dispatched work.

## Guardrails

- Do not auto-accept substantive work before inspecting context.
- Do not scan historical statuses as if they are current.
- Do not reprocess `VERIFIED` entries.
- Use a lock file so overlapping scheduled runs cannot create duplicate bridge
  documents.
- Keep prompt text, CLI commands, scheduler names, logs, locks, and required
  plugins/skills documented in `BRIDGE-INVENTORY.md`.

## Output Expectations

- If bridge work was processed: report the document entry, input status,
  output status, and new bridge file.
- If nothing required action: report that the file bridge scan was clear.
- If the scan failed: report the failing path, command, exit code, and log
  location.

---

*Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
