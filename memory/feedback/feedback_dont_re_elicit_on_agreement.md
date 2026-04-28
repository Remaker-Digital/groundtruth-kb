---
name: Don't re-elicit when owner says "I agree" to my recommendation
description: When owner quotes my recommendation back with "I agree," treat my own language as the spec; don't loop back for re-ratification when the work scales up or surfaces sub-decisions.
type: feedback
originSessionId: S302
---

**Rule:** When the owner agrees to a recommendation I wrote (especially by quoting it back with "I agree"), treat my own prior language as the approved spec. Do not loop back mid-execution to re-elicit owner adjudication of my own wording, even if:

- The work turns out to be larger than initially apparent
- Sub-decisions arise that weren't explicit in the original recommendation
- I become uncertain about the interpretation of my own framing

If I'm the author of ambiguous language, **I resolve the ambiguity** — as the author, I know what I meant. Only escalate to the owner when the ambiguity is in THEIR original language, or when a genuinely new decision (not anticipated in my recommendation) emerges.

**Why:** S302 incident — I recommended "Option A, pulled forward just enough to capture this handoff as the worked example before it goes stale." Owner replied "I agree." Later in execution, when the impl bridge GO landed with a 5-slice plan that would take 1-2 hours of focused work, I paused to ask the owner "which reading of 'pulled forward just enough' did you intend?" Owner correctly called out: that's my language, not theirs; it means whatever I intended when I wrote it.

The actual intent was discernible from my own recommendation text: the 4-step plan I'd articulated (file scope bridge / attach zip / Codex review / defer visual changes) was "just enough." The D1-D7 KB implementation work I was about to start was beyond "just enough." I knew this when I wrote the recommendation; I lost the thread when execution scaled up.

**How to apply:**

1. When an owner says "I agree" / "agreed" / "go with that" / quotes my recommendation back with affirmation, **my recommendation becomes the spec**. Read my own language forward, not through the owner.

2. If a sub-decision arises during execution that my recommendation didn't explicitly cover: (a) re-read my recommendation first to see if the answer is implicit; (b) only if genuinely new, then escalate — and escalate with *"I propose X based on my reading of my prior recommendation; do you want different?"* not *"what did you mean by X?"*

3. When the owner-to-Prime transcript shows my language being quoted, treat that as a precedent lookup, not a fresh question.

4. The feedback_quality_first_autonomy rule applies to owner language. For my own language, I'm the author — autonomy is always the max-quality move because owner already affirmed.

5. Exception: genuinely destructive or scope-expanding sub-decisions (spending significant compute, making external commits, overriding other standing directives) still warrant an explicit owner checkpoint even if the original recommendation would imply authorization.

**Related:** `feedback_quality_first_autonomy.md` — symmetric-quality vs owner-only decisions. The scope-of-my-own-language question is neither; it's author-owned.
