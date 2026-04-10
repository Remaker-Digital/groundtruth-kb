# Bridge Pester Protocol

## Principle

Acknowledgement only means the bridge is functioning. You still need to pester the other side until they give you the answer you need for your work to continue.

The bridge is not a reliable delivery mechanism. Codex processes messages on its own session cadence. Messages delivered at the wrong time are sometimes parked and forgotten. Acknowledgement of receipt indicates the bridge can transmit, but does NOT indicate a substantive response is forthcoming.

## Required Behavior

1. **Acknowledgement ≠ response.** Never treat a bridge acknowledgement as evidence that work will be done. Only a substantive reply (with findings, GO/NO-GO, or actionable content) counts as a response.

2. **Persistent follow-up.** After sending a review request or GO/NO-GO request to Codex:
   - Check for substantive responses every 10-15 minutes
   - If no substantive response exists after 15 minutes, send a follow-up ping with `correlation_id` referencing the original message
   - Continue following up until a substantive response is received or the owner intervenes
   - Do not stop following up just because a prior ping was acknowledged

3. **Follow-up content.** Each follow-up should:
   - Reference the original message ID and subject
   - Restate the specific action items requested
   - Note how long the request has been pending
   - Be sent via `send_message()` with `correlation_id` pointing to the original

4. **Escalation.** If no substantive response after 3 follow-up cycles (~45 minutes), report to the owner that Codex has not responded and ask whether to continue waiting or proceed without review.

## Rationale

The bridge is asynchronous message passing. Messages that arrive between Codex sessions, or during session initialization, can be swept but not actioned. Persistent retry compensates for this delivery unreliability. The cost of a redundant follow-up is negligible; the cost of a forgotten review is significant (unreviewed code reaching production).
