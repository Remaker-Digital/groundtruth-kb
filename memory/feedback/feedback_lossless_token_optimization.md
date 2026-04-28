---
name: Lossless token optimization only
description: When optimizing token use, never reduce quality, completeness, parallel throughput, verification rigor, or test/schema depth. Cut redundancy, not substance. S313.
type: feedback
originSessionId: edd21d0c-c044-4405-902e-57685ce1b332
---
When the owner signals token conservation (e.g., sharing usage metrics, mentioning weekly cap), optimize lossly only — never lossy.

**Why:** S313 — owner shared a usage screenshot showing 67% weekly cap with 2 days to reset. I responded by proposing to scale back (smaller proposals, single-thread cycles, less narration, stop after each step). Owner corrected immediately: *"Do not change your posture in any way which will reduce quality and completeness. Our goal is to optimize token use in ways which are not lossy."*

The corrections I proposed were all lossy:
- "Tighter proposals" → fewer sections → less coverage
- "Single-thread work" → less throughput when threads are genuinely independent
- "Less inline narration" → owner loses status visibility
- "Stop after each step" → owner has to drive every transition

**How to apply:**

Lossless wins to pursue:
- Don't re-read files already in context
- Drop "Unchanged from -001" enumeration boilerplate (one line: "all other sections retained" suffices)
- Cut insight blocks that just restate the prose immediately following them
- Don't re-state bridge protocol mechanics in every new proposal
- Tighter commit messages that don't duplicate the full bridge content
- Skip context re-establishment when the reader has it (Codex sees the prior bridge file; INDEX.md is in their scan)
- Avoid explanatory mode prefaces ("As I mentioned earlier…") when the owner can see the prior turn

Lossy cuts to **never** make under a token-conservation pretext:
- Reduce schema completeness in proposals
- Drop test plan items
- Skip codex review asks
- Cut evidence citations (file:line, command outputs)
- Skip parallel filing when threads are safely independent and the parallel-rework risk is bounded
- Reduce verification rigor (live runs, smoke tests, regression guards)
- Drop the per-finding response in NO-GO acknowledgements
- Skip status reports that give the owner clear next-action visibility

The principle is *signal density per token*, not *fewer tokens at the cost of signal*. Per `feedback_no_lossy_compression.md` (S311) — same lesson reinforced: reject compress/filter/summarize between substance and consumer.
