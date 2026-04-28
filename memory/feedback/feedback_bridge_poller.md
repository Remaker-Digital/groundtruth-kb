---
name: Bridge poller must process all messages
description: Owner wants autonomous bridge processing — no messages left pending for manual relay
type: feedback
---

The bridge poller must process ALL messages end-to-end, not just clear noise. The owner does not want to relay Codex messages manually.

**Why:** The previous poller behavior left substantive messages (GO/NO-GO verdicts, review requests) pending for "interactive processing." This forced the owner to manually check and relay Codex's responses, defeating the purpose of the bridge.

**How to apply:** The poller should read, act on, and resolve every message. For review requests, perform the review. For verdicts, acknowledge and apply. For findings, execute the recommended actions. Only resolve after processing is complete.
