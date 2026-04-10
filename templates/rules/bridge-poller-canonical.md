# Bridge Poller Canonical Instructions

This file is the canonical source of truth for bridge poller behavior.
It applies to any automation, scheduled task, or wake prompt that keeps
the Prime Builder <-> Loyal Opposition bridge operational.

## Core Rule

The bridge is message-driven and notification-driven with synchronous
dialog semantics. The sender tracks each exchange across its full lifetime.

The insight dropbox is a secondary artifact store and fallback signal only.
It is not the primary trigger for bridge work.

The owner is an observer unless the owner explicitly intervenes.

## Required Behavior

### 1. Sweep the Live Bridge First

- Query pending inbox items for the target agent.
- Prefer any canonical bridge snapshot or wake context provided by the runtime.

### 2. Prioritize Live Bridge Obligations

- If there is live bridge work (pending messages), process it before any
  report scanning or exploratory analysis.

### 3. Work Threads Directly with the Peer Agent

- Read the message and any referenced artifacts.
- Send the reply directly to the peer agent over the bridge.
- Resolve or close the message when complete (`completed` or `failed`).

### 4. Do Not Route Through the Owner

- Do not wait for owner relay when a direct bridge reply is possible.
- Only surface a blocker to the owner when a true external decision is
  required (product decisions, destructive actions, scope changes).

### 5. Use Report Scanning as Fallback Only

- If the bridge is clear, the poller may scan report directories for
  new content not reflected in bridge traffic.
- If a new report is found, summarize it and send a bridge note to the
  peer agent.

## Guardrails

- Do not auto-accept substantive work before inspecting context.
- If a message has `failed` status, do not process it. Send a correction
  message instead.
- Process work end-to-end without waiting for the owner unless blocked
  by a real external dependency.
- Use `retry_pending_message()` for messages that need re-delivery, not
  duplicate `send_message()` calls.

## Output Expectations

- If live bridge work was processed: report a concise processing summary.
- If only fallback reports were synced: report that no live bridge work
  existed and that report sync occurred.
- If nothing required action: report that the bridge is clear.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
