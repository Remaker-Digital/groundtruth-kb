---
sidebar_label: Data Retention
title: Data Retention & Privacy
description: Configure data retention periods, PII scrubbing, consent management, and GDPR compliance settings.
---

# Data Retention & Privacy

These settings control how long customer conversation data is stored, whether personally identifiable information is automatically redacted, and how GDPR data requests are handled. All settings apply to every customer on your account.

## Data Retention Period

Choose how long conversation data is retained before automatic deletion:

| Period | Use Case |
|--------|----------|
| 30 days | Minimal storage, strict privacy requirements |
| 90 days | Standard retention for most businesses |
| 180 days | Extended retention for trend analysis |
| 1 year | Long-term analytics and compliance |
| 2 years | Maximum retention for regulated industries |

After the retention period expires, conversation data is permanently deleted during the nightly cleanup job (03:00 UTC).

## PII Scrubbing

When enabled, the system automatically detects and redacts personally identifiable information from stored conversation transcripts, including:

- Email addresses
- Phone numbers

Detected PII is replaced with `[REDACTED]` in stored transcripts. Live responses delivered to the customer during the conversation are not affected — PII scrubbing operates at the storage layer only, so the customer experience is unchanged while stored data is cleaned for privacy compliance.

Enable PII scrubbing from the **Memory & Privacy** page in the admin console.

## Consent Required

When enabled, a consent prompt appears at the start of each conversation asking the customer for permission to store their conversation data. If the customer declines, the conversation proceeds normally but is not stored after it ends.

## Automatic Deletion on Request

When enabled, the system automatically processes GDPR "right to erasure" requests. When a customer or their representative submits a deletion request, all stored conversation data, customer profile information, and learned patterns for that customer are permanently removed.

When disabled, deletion requests are queued for manual review by an admin before processing.

## Related Settings

- [Customer Memory](/docs/admin-guide/customer-memory) — Controls what the AI remembers about customers across sessions
- [Billable Conversation Spec](/docs/billing/billable-conversation-spec) — How conversations are counted for billing

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
