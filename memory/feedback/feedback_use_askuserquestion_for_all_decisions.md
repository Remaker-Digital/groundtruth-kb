---
name: Use AskUserQuestion for ALL owner decisions, not inline chat prose
description: Owner may not see decisions embedded in chat flow and inline requests are often unclear. Use the AskUserQuestion tool for every owner-only decision, with explicit labeled options and descriptions.
type: feedback
originSessionId: S302
---

**Rule:** When an owner decision is needed — Accept/Retire/Hold, priority choice, Option A vs B, token mapping strategy, ANY owner-only decision class per `feedback_quality_first_autonomy` — use the **AskUserQuestion tool** with explicit labeled options and per-option descriptions.

**Do NOT:**
- Surface decisions inline in prose paragraphs (owner may not see them)
- Bury decision requests at the end of long poller responses
- Use markdown tables or bulleted lists as a substitute for the decision-dialog tool
- Repeat the same inline ask across multiple turns (the churn wastes tokens and still doesn't guarantee visibility)

**Do:**
- Invoke `AskUserQuestion` as a dedicated tool call for every owner decision that fits its shape (2–4 mutually exclusive options, or multi-select if genuinely parallel choices)
- Phrase the `question` field with enough context that the owner can decide without reading the preceding chat history
- Write each `option.description` to be self-contained — describe the choice, its consequences, and its reversibility
- Keep `header` under 12 chars and specific (e.g., "Disposition", "Priority", "Token map")

**Why:** S302 incident. I asked owner Accept/Retire/Hold on the D1-D7 over-implementation via inline prose at the end of a poller response. Owner explicitly told me: *"DO NOT ask decisions in the chat flow and wait for me to respond - I do not always see those decisions and they are not always sufficiently clear. Please use explicit decision dialogs for ALL decisions, if possible."*

The owner is not reading every line of every poller response. Chat-flow decision asks are unreliably delivered. `AskUserQuestion` produces a dedicated UI affordance the owner will not miss.

**How to apply:**

1. Whenever I find myself typing "**Which path?**" / "**Your decision needed**" / "**Tell me X or Y**" / tables-labelled-with-options → **stop**, fire `AskUserQuestion` instead.
2. Even "routine" decisions (priority ordering, Option A vs B, default override, y/n on minor ratification) should use the dialog if possible. Err on the side of over-using the tool rather than under-using.
3. The 2–4-options constraint may require grouping. If the real decision is >4 options, split into sequential dialogs.
4. `AskUserQuestion` can fire multiple questions in a single call (1–4 questions). Use this for bundled related decisions (e.g., "Which disposition?" + "Should the deferral-marker hook become a bridge?").
5. Exception: genuinely conversational turns (acknowledgments, clarifications of my own wording, reports of state) don't need the tool. The rule applies to **decisions with durable consequences**.

**Related memories:**
- `feedback_quality_first_autonomy.md` — defines the owner-only decision class.
- `feedback_dont_re_elicit_on_agreement.md` — don't re-ask something owner already answered.
- Together: if it IS an owner-only decision AND owner hasn't already answered, use the dialog.
