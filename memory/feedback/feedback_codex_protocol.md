---
name: Codex GO gate is absolute
description: Never proceed with implementation before receiving Codex GO response — no exceptions, no "reasonable window" bypass
type: feedback
---

Do NOT implement before Codex responds with GO. The bridge protocol requires waiting for Codex's explicit GO/NO-GO verdict before any implementation work begins. There is no "reasonable window" exception. If Codex hasn't responded, the correct action is to wait or ask the owner to invoke Codex — never to proceed speculatively.

**Why:** Owner explicitly corrected this behavior. The Codex review gate exists to catch defects before they're coded. Proceeding without GO defeats the purpose of the review protocol and creates rework.

**How to apply:** After sending a proposal or review request to Codex, report the pending status to the owner and wait. Do not rationalize bypassing the gate. If blocked, ask the owner whether to invoke Codex or adjust the workflow.
