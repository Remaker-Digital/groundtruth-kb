---
sidebar_position: 1
title: Admin guide overview
description: Complete reference for every setting in the Agent Red admin console — what each input does, how changing it affects system behavior, and best practices.
---

# Admin guide

This guide documents every configurable setting in the Agent Red admin console. Each page explains what the setting controls, what the system does when you change it, and how to get the best results.

## Who this is for

This guide is for merchants who have installed Agent Red and want to understand the full range of configuration available to them. If you have not set up Agent Red yet, start with [Initial setup](../getting-started/setup.md).

## How configuration works

Agent Red uses a layered configuration system:

1. **Platform defaults** — Sensible starting values that work for most stores.
2. **Tier defaults** — Adjusted defaults based on your subscription tier (Starter, Professional, Enterprise).
3. **Your overrides** — Any value you change in the admin console.

When you change a setting, your value takes priority over the platform and tier defaults. If you reset a field, it reverts to your tier's default.

Every configuration change is versioned automatically. You can view past versions, compare changes, and roll back to a previous configuration from the Configuration page in the admin console.

:::tip Save and activate
Configuration changes use a two-phase commit model. When you save a setting, it is stored as a **draft** and does not affect your live AI agent. Changes only go live when you explicitly **activate** from the activation banner. This lets you edit multiple settings across different pages, review everything in one place, and go live with confidence. See [Save and activate](./save-and-activate.md) for the full workflow.
:::

## Configuration sections

| Section | What it controls |
|---|---|
| [Brand and tone](./brand-and-tone.md) | Agent name, personality, greetings, farewells |
| [Languages](./languages.md) | Primary and additional response languages, auto-detection |
| [Response style](./response-style.md) | Verbosity, formality, emoji usage, fallback messages |
| [Knowledge base](./knowledge-base.md) | Search behavior, retrieval tuning, source citation, intent routing |
| [Business policies](./business-policies.md) | Return, shipping, warranty, support hours, and custom policies |
| [Escalation rules](./escalation-rules.md) | When and how conversations route to human agents |
| [Integrations](./integrations.md) | Shopify sync, Zendesk, Mailchimp, Google Analytics |
| [Customer memory](./customer-memory.md) | Conversation history, pattern learning, model training, data retention |
| [Widget appearance](./widget-appearance.md) | Colors, position, launcher, dark mode, mobile behavior |
| [Widget behavior](./widget-behavior.md) | Auto-open, offline mode, pre-chat forms, rating, sound |
| [Custom instructions](./custom-instructions.md) | Advanced: direct system prompt injection for specific behaviors |
| [Quick action prompts](./quick-actions.md) | Pre-defined prompt buttons in the widget greeting area |
| [Knowledge base management](./knowledge-base-management.md) | Creating, editing, uploading, and organizing knowledge articles |
| [Conflict scanner](./conflict-scanner.md) | Detect duplicate and conflicting knowledge base articles |
| [Knowledge automation](./knowledge-automation.md) | Storefront ingestion, industry templates, and AI-generated config suggestions |
| [Save and activate](./save-and-activate.md) | Draft, review, and activate configuration changes |
| [Team management](./team-management.md) | Invite team members, assign roles, and control admin console access |
| [Analytics](./analytics.md) | Conversation volume, intent breakdown, resolution rates, first-contact resolution |
| [Data retention](./data-retention.md) | Retention periods, PII scrubbing, consent, automatic deletion |
| [MFA & security](./mfa-security.md) | Two-factor authentication, magic link login, backup codes |
| [Provider console](./provider-console.md) | Platform-level dashboard for multi-tenant monitoring and operations |

## Settings that affect AI prompts

Many configuration values are injected directly into the AI's system prompt — the instructions that guide how it responds. Fields marked with "Affects: response generator" in this guide are inserted into the prompt before every response is generated.

Changing these values changes the AI's behavior immediately for new conversations. The change does not retroactively alter past conversations.

:::caution
The **custom instructions** field gives you direct access to the system prompt. Use it carefully — poorly written instructions can degrade response quality. See [Custom instructions](./custom-instructions.md) for guidance.
:::

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
