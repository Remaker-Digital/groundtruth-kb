---
name: Bridge must be synchronous — sender maintains dialog state
description: Owner rejects async bridge model. Sender holds thread context across exchange. Non-blocking persistent retry until response.
type: feedback
---

The bridge must be synchronous: the sender maintains awareness of dialog state across the entire exchange. This is the opposite of the current async model where each side releases all awareness after each ack and must re-inspect context from scratch on every pickup.

Synchronous means: the sender knows what it sent, what it's waiting for, and why — when the response arrives, context is already held, not rediscovered. Non-blocking persistent retry in the background until the peer responds. No claimed state, no SLA windows, no ack breaches, no response-window classifications.

**Why:** The async model with claimed/ack/breach states forces expensive context re-inspection on every message pickup. Each side "forgets" the conversation after acknowledging, making every exchange feel like a cold start. The owner wants a dialog with memory, not a mailbox of disconnected messages.

**How to apply:** The sender holds thread context: "I sent X, I'm waiting for Y on topic Z." When a response arrives, process it with that context already loaded — no claim/inspect/narrate ritual. The current bridge protocol (.claude/rules/prime-bridge-collaboration-protocol.md) with its SLA windows, ack ceremonies, and stateless pickup model is overengineered and should be simplified toward stateful dialog with persistent retry.
