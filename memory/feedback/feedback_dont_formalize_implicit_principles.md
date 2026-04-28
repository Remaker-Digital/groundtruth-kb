---
name: Don't formalize implicit principles
description: When owner makes a principle-shaped statement (especially elaborations of existing direction), ASK before formalizing as a DELIB/GOV/ADR. Implicit affirmation isn't enough; formal capture deserves an explicit "yes, record this."
type: feedback
originSessionId: 27cde065-5387-4762-a3e6-c0681eba4332
---
When the owner says something that sounds principle-shaped, do NOT auto-escalate to formal artifact capture (DELIB, GOV, ADR, DCL). Ask first.

**Why:** S312 incident. Owner said the CLI should be designed with AI as primary consumer. I escalated to a proposed `DELIB-S312-CLI-AI-FIRST-DESIGN` with full content for approval. Owner pulled back: "I was not aware that I was stating a new design principle. Perhaps I misunderstood an earlier exchange." It turned out the owner was reinforcing framing I had already used in the conversation — not introducing a new commitment. Substance was already in `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`. Same false-positive pattern as the prose-detector class in `pending-owner-decisions.md`: heuristic-on-vague-input produces over-eager artifact creation.

**How to apply:** Before proposing a new DELIB/GOV/ADR/DCL based on a conversational statement, check:

1. **Is the substance already captured?** Search existing DELIBs / rules / specs for the framing. Strategic reminders of existing direction don't need new records.
2. **Did the owner explicitly direct capture?** Phrases like "save this", "record this", "make this a deliberation", or explicit approval of a prior proposal count. "You made an important point earlier" / "this is what we want" / "design with this in mind" do NOT count — they're directional, not commitment-making.
3. **Is this a yes/no decision worth preserving across sessions?** A principle-statement that elaborates existing direction is not a decision; it's a clarification. Clarifications belong in design rationale of the work item that implements them, not in standalone DELIB records.
4. **What's the cheapest faithful capture?** Often: a one-line note in `memory/work_list.md` row for the affected work item. Sometimes: a sentence added to a related existing DELIB at next-formal-revision time. Rarely: a new DELIB.

Default: NO formal capture absent explicit direction. The deterministic-services principle's "do not silently absorb friction" is about *surfacing* repetitive AI work, NOT about *formalizing every conversational statement*. Over-recording is its own friction.

When in doubt, propose an evaluation (like the owner asked me to do here) rather than a formal artifact. "Should I capture this?" is a cheap question; an unwanted DELIB is expensive to retract.
