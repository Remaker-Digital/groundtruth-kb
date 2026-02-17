---
sidebar_label: Conversations
title: Conversation Inbox
description: Monitor, filter, and manage customer conversations in real time from the Inbox.
---

# Conversation Inbox

The Inbox provides a real-time view of all customer conversations, with tools to filter, assign, escalate, and resolve them.

## Conversation List

The left panel shows all conversations, sorted by most recent activity. Each entry displays:

- **Customer identity** — Displayed using the best available identification: Shopify customer name (verified), asserted name from conversation (unverified, shown with badge), or session ID as fallback
- **Status badge** — Active, Escalated, or Resolved
- **Unread indicator** — Red dot for conversations with unread messages
- **Message count** and last activity timestamp

### Filtering

Use the filter tabs to view conversations by status:

- **All** — Every conversation regardless of status
- **Active** — Currently open conversations with recent customer activity
- **Esc** — Conversations escalated to a human team member
- **Resolved** — Conversations that have been resolved (by agent action, customer ending the chat, or reaching max conversation turns)
- **Archived** — Conversations that have been archived for long-term storage

### Search

The search bar searches across **message content** as well as customer identity. Type any keyword and the list updates in real time (with a short debounce). Search results display matching conversation snippets so you can quickly find the conversation you need.

When a search returns no results, the reader pane is cleared to avoid confusion.

## Conversation Detail

Select a conversation to view the full message thread. The detail panel shows:

- Complete message history with timestamps
- AI-generated responses and customer messages
- Internal notes (visible only to your team, not to customers)

### Actions

- **Escalate** — Hand off to a human team member. You can optionally select a category (service, support, sales, account, technical assistance, or general inquiry) and a specific team member. When a category is selected without a specific agent, Agent Red automatically assigns the conversation to the escalation agent with the fewest unresolved escalations in that category. Email notification is sent to the assigned agent (or all escalation agents if no specific assignment). The conversation status changes to Escalated.
- **Resolve** — Mark the conversation as resolved and close it. The conversation status changes to Resolved.
- **Archive** — Move a resolved or timed-out conversation to the archive for long-term storage. Archived conversations no longer appear in the default list view but remain accessible via the Archived filter tab.
- **Unarchive** — Restore an archived conversation back to the main list.

### AI-Initiated Escalation

When the AI pipeline detects that a conversation should be escalated (based on confidence thresholds, keyword triggers, or turn limits), it also classifies the conversation into a category. The system then automatically assigns the conversation to the best-fit escalation agent based on category match and current workload. The assigned agent receives a targeted email notification.

### Escalation Details

For escalated conversations, the detail panel shows:

- **Escalation category** — Displayed as a badge (e.g., "support", "sales", "technical assistance")
- **Assigned to** — The team member assigned to handle the escalation, shown by display name

## Customer Profile

The right panel shows the customer's profile information, including:

- Contact details
- Conversation history summary (message count, start time, last activity)
- Customer context data (when [Customer Memory](/docs/admin-guide/customer-memory) is enabled)

## Billable Conversations

A conversation is billable when the AI produces at least one response. Test, admin, health-check, and system conversations are excluded. See [Billable Conversation Spec](/docs/billing/billable-conversation-spec) for the complete definition.

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
