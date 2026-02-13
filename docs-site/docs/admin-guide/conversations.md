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
- **Status badge** — Active, Escalated, Idle, or Resolved
- **Unread indicator** — Red dot for conversations with unread messages
- **Message count** and last activity timestamp

### Filtering

Use the filter tabs to view conversations by status:

- **All** — Every conversation regardless of status
- **Active** — Currently open conversations with recent customer activity
- **Esc** — Conversations escalated to a human team member
- **Idle** — Conversations with no activity for a configurable period

### Search

The search bar searches across **message content** as well as customer identity. Type any keyword and the list updates in real time (with a short debounce). Search results display matching conversation snippets so you can quickly find the conversation you need.

When a search returns no results, the reader pane is cleared to avoid confusion.

## Conversation Detail

Select a conversation to view the full message thread. The detail panel shows:

- Complete message history with timestamps
- AI-generated responses and customer messages
- Internal notes (visible only to your team, not to customers)

### Actions

- **Escalate** — Hand off to a human team member. When you escalate a conversation, Agent Red sends an email notification to all team members with the `escalation_agent` role. If no escalation agents are configured, the notification falls back to team members with the `admin` role. The conversation status changes to Escalated.
- **Resolve** — Mark the conversation as resolved and close it. The conversation status changes to Resolved.

## Customer Profile

The right panel shows the customer's profile information, including:

- Contact details
- Conversation history summary (message count, start time, last activity)
- Customer context data (when [Customer Memory](/docs/admin-guide/customer-memory) is enabled)

## Billable Conversations

A conversation is billable when the AI produces at least one response. Test, admin, health-check, and system conversations are excluded. See [Billable Conversation Spec](/docs/billing/billable-conversation-spec) for the complete definition.

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
