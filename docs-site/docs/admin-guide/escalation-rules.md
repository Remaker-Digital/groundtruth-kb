---
sidebar_position: 7
title: Escalation rules
description: Configure when the AI agent routes conversations to human agents — confidence thresholds, trigger keywords, turn limits, and notification settings.
---

# Escalation rules

Escalation is the process of routing a conversation from the AI agent to a human agent. These settings control when and how escalation happens.

## How escalation works

The escalation detection agent evaluates every customer message for signals that a human is needed. It considers:

1. **Confidence threshold** — Is the AI confident enough in its ability to handle this conversation?
2. **Keyword triggers** — Did the customer use a word or phrase that should always trigger escalation?
3. **Turn limit** — Has the conversation exceeded a maximum number of back-and-forth exchanges?
4. **Sentiment signals** — Is the customer expressing frustration, anger, or urgency? (automatic, not configurable)

If any of these conditions trigger, the conversation is escalated.

---

## Escalation threshold

| | |
|---|---|
| **Field** | `escalation_threshold` |
| **Type** | Slider (0.0–1.0) |
| **Default** | Starter: `0.7`, Professional: `0.6`, Enterprise: `0.5` |
| **Affects** | Escalation handler |

The confidence level below which the AI escalates instead of responding. The escalation agent assigns a confidence score (0.0 to 1.0) to each conversation turn. If the score drops below this threshold, the conversation is routed to a human.

| Threshold | Behavior |
|---|---|
| **0.3–0.4** | Very aggressive AI. Escalates rarely. Only use if you have a very comprehensive knowledge base and accept that some customers may get suboptimal AI answers. |
| **0.5–0.6** | Balanced. The AI handles most questions but escalates when it is unsure. Good for stores with solid knowledge bases. |
| **0.7–0.8** | Conservative. The AI escalates more often. Good for stores that are still building their knowledge base or where customer issues tend to be complex. |
| **0.9–1.0** | Very conservative. The AI escalates almost everything. Effectively turns Agent Red into a triage system that classifies intent and routes to humans. |

**Why tiers have different defaults:**
- **Starter (0.7):** New merchants typically have smaller knowledge bases, so a higher threshold avoids low-quality AI responses.
- **Professional (0.6):** Merchants on Professional are expected to have more complete knowledge bases and are comfortable with more AI autonomy.
- **Enterprise (0.5):** Enterprise merchants have typically invested in thorough knowledge base setup and want maximum automation.

**Recommendation:** Start with the default for your tier. After 1–2 weeks, review escalated conversations in the Inbox. If many escalated conversations could have been handled by the AI, lower the threshold by 0.05–0.1. If customers are getting poor AI answers, raise it.

---

## Escalation keywords

| | |
|---|---|
| **Field** | `escalation_keywords` |
| **Type** | Tag list (up to 30 keywords, each up to 50 characters) |
| **Default** | None |
| **Affects** | Escalation handler |

Words or phrases that immediately trigger escalation, regardless of the confidence score. When a customer message contains any of these keywords (case-insensitive), the conversation is escalated.

**Common escalation keywords:**
- `speak to a human` / `talk to a person` / `real person`
- `manager` / `supervisor`
- `lawyer` / `legal` / `sue`
- `cancel my account` / `close my account`
- `report` / `complaint` / `BBB`

**Tips:**
- Keep the list focused on high-intent phrases. Adding too many common words (like "problem" or "help") will cause unnecessary escalation.
- Include variations: if you add `refund`, also consider `get my money back`.
- Test each keyword by imagining a sentence a customer would say containing it. If that sentence should always go to a human, add it. If it sometimes should not, leave it out and let the confidence threshold handle it.

---

## Escalation notification email

| | |
|---|---|
| **Field** | `escalation_notification_email` |
| **Type** | Email address |
| **Default** | None |
| **Affects** | Escalation handler |

An email address that receives a notification when a conversation is escalated. The notification includes the customer's name (if known), the conversation summary, and a link to the conversation in the admin Inbox.

**If not set:** Escalated conversations appear in the admin Inbox but no email notification is sent. Team members must check the Inbox manually or rely on the dashboard alert indicators.

**Tip:** Use a team email alias (e.g., `support@yourstore.com`) rather than a personal email so that the notification reaches whoever is on shift.

---

## Maximum AI turns before escalation

| | |
|---|---|
| **Field** | `max_ai_turns_before_escalation` |
| **Type** | Number (1–50) |
| **Default** | `10` |
| **Affects** | Escalation handler |

Forces escalation after the conversation reaches this many back-and-forth exchanges (turns), even if the confidence score is above the threshold. This is a safety net to prevent customers from getting stuck in a loop with the AI.

**How it works:**
- A "turn" is one customer message followed by one AI response.
- The counter starts at 1 with the first exchange.
- When the counter reaches the limit, the next response includes an escalation notice.

| Value | Use case |
|---|---|
| **3–5** | For stores where AI is primarily a triage tool and humans should handle extended conversations. |
| **8–12** | Standard range. Most product and policy questions resolve within 5–8 turns. |
| **15–50** | For stores with extensive knowledge bases where complex, multi-step conversations are expected (e.g., troubleshooting technical products). |

**Recommendation:** Start with `10`. Review the Inbox after the first week — if most conversations resolve in 3–4 turns, lowering to `6–8` gives customers a faster path to a human when needed.

---

## What happens when a conversation is escalated

1. The AI sends a handoff message to the customer explaining that a human agent will take over.
2. The conversation appears in the admin Inbox with an "Escalated" status badge.
3. If an escalation email is configured, a notification is sent.
4. If Zendesk integration is enabled, a ticket is created in your Zendesk instance (Professional+ only).
5. The AI does not send further responses in the conversation unless a team member explicitly reassigns it back to the AI.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
