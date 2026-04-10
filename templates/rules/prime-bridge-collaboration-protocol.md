# Prime Bridge Collaboration Protocol

This rule defines mandatory collaboration behavior between agents over the
bridge. The model is synchronous dialog -- the sender maintains awareness of
the exchange across its full lifetime.

## Operating Model

- The bridge is the canonical coordination channel.
- **Synchronous dialog:** the sender tracks the state of each exchange until
  resolution. Not fire-and-forget.
- **Non-blocking persistent retry:** send a message, continue working,
  background retries re-queue notifications until the peer responds. Never
  block waiting for a reply.
- Do not wait for owner confirmation for ordinary execution sequencing.
- Treat bridge messages with the same urgency as direct owner requests.

## Message States

Three states only:

| State | Meaning |
|-------|---------|
| `pending` | Message sent, awaiting processing or reply. |
| `completed` | Successfully resolved. |
| `failed` | Validation failure, permanent error, or superseded. |

There are no claimed, accepted, or SLA breach states.

## Message Semantics

Messages carry a `payload` JSON envelope with:

- `expected_response`: what the sender needs back (`advisory_review`,
  `go_no_go`, `status_update`, `task_handoff`, `correction`, `escalation`)
- `artifact_refs`: repo-relative file paths and KB references relevant to
  the exchange (never absolute paths)
- `action_items`: specific numbered deliverables (not open-ended requests)

Message kinds: `substantive`, `status_update`, `system`. Protocol
acknowledgements are not supported -- all replies must be substantive.

## Thread Continuity

- Threads are identified by `thread_id` derived from `correlation_id`.
- Replies MUST carry a `correlation_id` referencing the original message
  or thread.
- Thread state is derived from messages at query time (no cached thread
  table).
- Sender and recipient must both be participants in the referenced thread.

## Message Lifecycle

### On Receiving a Message

1. Inspect thread context before narrating pickup.
2. If structured `artifact_refs` are present, treat them as first-read source.
3. Execute the work.
4. Send a substantive reply with `correlation_id` back to the sender.
5. Resolve the original inbound request as `completed` or `failed`.

### On Completing Work

Send a correlated completion response that includes:

- **Outcome:** complete or blocked.
- **Evidence inspected:** file paths, commit hashes.
- **Artifacts produced:** IDs, paths, report filenames.
- **Gaps remaining:** any open items or owner decisions needed.

### Malformed Messages

- Messages that fail validation are persisted as `failed` with correction
  guidance.
- Use `send_correction_message()` for failed peer messages.
- Do not claim or process failed messages.

## Non-Blocking Persistent Retry

The resident worker automatically retries stale pending outbound messages
every 5 minutes. This is the primary retry mechanism.

- **Autonomous:** scans for outbound messages pending longer than 3 minutes
  and calls `retry_pending_message()`.
- **Bounded:** capped at 3 retries per message to prevent storms.
- **Non-blocking:** the sender continues working while retries happen.
- Retry metadata tracked in `payload._retry` (count, last_at, max).

## Session Start Sweep

At session start, both agents MUST:

1. Query for all pending messages via `list_inbox(agent=..., status="pending")`.
2. Process each one with a substantive reply or resolve it.
3. Report the count: "Bridge sweep: N messages processed."

## Escalation Boundary

Escalate to the owner only when:

- The action exceeds prior approval.
- A destructive action is required.
- There is a true owner-only product or risk decision.
- Retry limit reached and peer appears offline.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
