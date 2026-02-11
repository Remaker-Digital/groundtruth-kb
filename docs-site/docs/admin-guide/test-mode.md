---
sidebar_position: 15
title: Test mode
description: Safely test AI configuration changes by routing a percentage of customer sessions to an experimental variant before committing to production.
---

# Test mode

Test mode lets you try AI configuration changes on a controlled percentage of real customer sessions before rolling them out to everyone. Instead of changing production directly and hoping for the best, you create a test variant, observe its performance, and then decide whether to adopt or discard the changes.

## Why use test mode

Changing your AI's behavior affects every customer conversation. Test mode reduces the risk of AI configuration changes by letting you:

- **Compare before committing** — Run two configurations side by side and compare metrics in the analytics dashboard.
- **Limit exposure** — Route as few as 1% of sessions to the test variant, keeping the majority of customers on the proven production configuration.
- **Iterate safely** — Adjust the test variant without touching production. If something goes wrong, abandon the test instantly.

## How session assignment works

When a customer starts a new conversation, Agent Red assigns it to either the **production** or **test** configuration. The assignment uses a deterministic hash of the session identifier, which means:

- The same session always gets the same assignment — a customer won't flip between configurations mid-conversation.
- The split is statistically even at the configured percentage. For example, at 10%, roughly 1 in 10 new sessions uses the test variant.
- Assignment is invisible to the customer. Both variants use the same widget, the same knowledge base, and the same escalation routing. Only the AI behavior differs.

Conversations created during test mode are tagged internally so you can filter analytics by **test** or **production** sessions later.

## What you can change in test mode

Test mode is designed for AI behavior experimentation. When test mode is active, only the following 13 fields can be modified — all other configuration fields are locked to prevent unintended changes to your production setup.

| Field | What it controls |
|-------|-----------------|
| Brand voice | The AI's personality and communication style |
| Response length | Target response length (concise, balanced, detailed) |
| Formality level | How formal or casual the AI sounds |
| Escalation threshold | Confidence level below which conversations escalate to a human |
| Escalation keywords | Words or phrases that trigger immediate escalation |
| Custom instructions | Direct instructions injected into the AI's system prompt |
| Memory enabled | Whether the AI uses persistent customer memory |
| Retrieval top-k | Number of knowledge base articles retrieved per query |
| Retrieval vector weight | Weight given to semantic (vector) search results |
| Retrieval BM25 weight | Weight given to keyword (BM25) search results |
| Retrieval minimum score | Minimum relevance score for a knowledge article to be included |
| Intent-source mapping | Which knowledge entry types are used for each detected intent |
| Cite sources in response | Whether the AI includes source article titles in its answers |

Fields outside this list — such as widget appearance, integrations, business policies, and customer memory tier settings — remain locked. This ensures that the only difference between production and test sessions is the AI's response behavior.

## Setting up test mode

### Step 1 — Open the onboarding wizard

Navigate to the onboarding wizard in your admin console. If you have already completed initial setup and have a production configuration, the wizard shows a **Mode selection** step as the first screen.

### Step 2 — Choose test mode

On the mode selection screen, select **Test Mode**. This tells the wizard that you want to create a test variant rather than modifying production directly.

If you select **Production** instead, the wizard works normally — changes go directly to your live configuration.

### Step 3 — Configure AI behavior

Walk through the wizard steps. Fields that are locked by test mode appear greyed out with a lock indicator and the message: "This field is locked while Test Mode is active. Only AI behaviour fields can be modified."

Focus on the fields you want to experiment with. For example, you might:

- Change **brand voice** from "professional" to "friendly and casual"
- Increase **retrieval top-k** from 3 to 5 to see if more context improves answers
- Lower **escalation threshold** to see if the AI can handle more edge cases
- Add **custom instructions** for a specific product launch

### Step 4 — Review and set test percentage

The final wizard step, **Review & Launch**, shows a summary of your configuration and a **Test Population** slider. Set the percentage of sessions that should use your test variant (1–50%).

:::tip Start small
Begin with 5–10% to validate your changes with minimal risk. You can always increase the percentage later by revisiting the wizard.
:::

### Step 5 — Activate

Click **Activate AI Agent Test** to go live. The system immediately begins routing the configured percentage of new sessions to your test variant.

A banner appears at the top of the admin console confirming that test mode is active, along with the current test percentage.

## Monitoring test mode

### Analytics filtering

The **Analytics** page includes a segmented control with three options:

| Filter | What it shows |
|--------|--------------|
| **All** | Metrics from every conversation, regardless of assignment |
| **Production** | Only conversations using the production configuration |
| **Test** | Only conversations using the test configuration |

Switch between filters to compare key metrics side by side:

- **Total conversations** — Is the test variant handling a proportional share?
- **Escalation rate** — Is the test variant escalating more or fewer conversations?
- **Critic pass rate** — Is the AI's response quality being maintained?
- **Intent distribution** — Are customers asking different questions, or are the same intents being routed differently?
- **Knowledge gaps** — Are there more or fewer unresolved conversations in the test group?

A contextual banner appears below the filter when you select **Production** or **Test**, confirming which data set you are viewing.

### Global indicator

While test mode is active, a persistent banner appears at the top of the admin console. This prevents you (or team members) from forgetting that a test is running.

## Ending test mode

When you are ready to conclude the test, open the **Review & Launch** step in the wizard. With test mode active, you see two options:

### Roll out to production

Click **Roll Out to Production** to merge your test configuration into the production configuration. All future sessions — 100% — will use the test variant's settings. The test mode deactivates, and the test overrides become the new production values.

Use this when the test variant performed as well as or better than production.

### Abandon test

Click **Abandon Test** to discard the test overrides entirely. Production continues unchanged. All future sessions use the original production configuration.

Use this when the test variant underperformed, caused more escalations, or didn't produce the improvement you expected.

In both cases, historical conversations retain their original assignment. Analytics filtering continues to work for past test and production sessions even after test mode is deactivated.

## Best practices

- **Change one thing at a time.** If you change five fields simultaneously and performance improves, you won't know which change made the difference. Test one or two related changes per experiment.

- **Run tests for at least 48 hours.** Short tests are influenced by time-of-day traffic patterns. Two days of data gives you a more reliable comparison.

- **Watch escalation rate closely.** A rising escalation rate is the earliest signal that a configuration change is degrading the customer experience.

- **Use the conflict scanner before testing.** Knowledge base conflicts cause inconsistent answers regardless of configuration. Run a scan first so your test results aren't polluted by content issues. See [Conflict scanner](./conflict-scanner.md).

- **Document your hypothesis.** Before activating a test, write down what you expect to change and why. This makes it easier to evaluate results objectively.

- **Don't exceed 50%.** The maximum test percentage is 50% by design. Testing on more than half of your traffic defeats the purpose of having a production baseline to compare against.

## Limitations

- **New sessions only.** Test mode assignment applies to new conversations. Ongoing conversations that started before test mode was activated continue using the production configuration.

- **Session-level, not customer-level.** A returning customer may be assigned to different groups across separate sessions. The assignment is per-session, not per-customer.

- **13 fields only.** Infrastructure settings (widget appearance, integrations, memory tier, business policies) cannot differ between test and production. Test mode is specifically for AI response behavior.

- **One test at a time.** You cannot run multiple simultaneous test variants. Deactivate (roll out or abandon) the current test before starting a new one.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
