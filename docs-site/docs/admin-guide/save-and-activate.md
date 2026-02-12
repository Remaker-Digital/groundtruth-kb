---
sidebar_position: 2
title: Save and activate
description: Understand the two-phase commit model — save configuration changes as a draft, review them, and activate when ready to go live.
---

# Save and activate

Agent Red uses a two-phase commit model for configuration changes. When you edit a setting in the admin console, the change is saved to a **draft** — it does not affect your live AI agent. Your live configuration only changes when you explicitly **activate** the draft.

This means you can freely experiment with settings, walk away, come back later, and activate only when you are confident the changes are correct.

## Why two phases

Changing your AI agent's behavior affects every customer conversation. The two-phase model gives you a safety net:

- **No accidental changes** — Saving a field does not change what your customers experience. You must deliberately activate.
- **Review before going live** — The activation dialog shows exactly which fields changed and whether validation passed, so you know what will happen before it happens.
- **One-click undo** — If an activation does not perform as expected, you can restore the previous configuration immediately.

## How it works

### 1. Save changes (draft)

Edit any configuration page — Brand and tone, Response style, Widget appearance, Quick actions, or any other setting. When you click **Save**, the changes are written to your draft. The draft is private to your admin console and has no effect on the live AI agent or widget.

You can save changes across multiple pages. All saved changes accumulate in the draft until you activate or discard them.

### 2. Review (activation banner)

When you have unsaved draft changes, an **activation banner** appears at the top of the admin console. The banner tells you that changes are pending and offers two actions:

| Action | What it does |
|--------|--------------|
| **Activate** | Opens the activation dialog so you can review and go live |
| **Discard** | Deletes all draft changes — your live configuration stays unchanged |

The banner polls every 30 seconds, so it appears even if changes were saved by another team member or in another browser tab.

### 3. Activate (go live)

Click **Activate** in the banner to open the activation dialog. The dialog shows:

- **Validation status** — Green checks for fields that pass, red indicators for fields that fail, yellow warnings for optional improvements.
- **Change summary** — Every changed field grouped by category (Agent configuration, Widget configuration, Quick actions).
- **Activate now** button — Disabled if any hard-block validation errors exist.

When you click **Activate now**, the draft becomes your live configuration. The previous live configuration is saved as a restore point.

## Draft indicators

While draft changes exist, the admin console shows visual indicators:

- **DRAFT badge** — Individual pages show a badge next to the page title when that page has unsaved draft changes.
- **Activation banner** — The persistent yellow banner at the top of every admin page.

These indicators disappear once you activate or discard the draft.

## Activation validation

Before a draft can be activated, Agent Red validates that the configuration is viable. Two fields are required:

| Field | Requirement | Why |
|-------|-------------|-----|
| **Brand name** | Must be set (not empty) | The AI agent uses your brand name in greetings, responses, and escalation messages. Without it, responses sound generic. |
| **Widget key** | Must exist for the tenant | The widget key connects the chat widget on your storefront to the correct tenant. Without it, the widget cannot load. |

If either validation fails, the **Activate now** button is disabled and the dialog shows the specific error. Fix the issue, save again, and the validation updates automatically.

Additional warnings (non-blocking) may appear for optional fields that improve agent quality, such as an empty brand voice or missing business policies.

## Restoring previous configuration

Every activation preserves a snapshot of the configuration it replaced. If you activate a change and it does not perform well, you can restore the previous version:

1. Open the **Restore previous configuration** option (available in the Configuration page).
2. The restore dialog shows the timestamp and version number of the previous configuration.
3. Click **Restore** to swap the current live configuration with the previous one.

This is a one-level undo. The restored configuration becomes active, and the configuration you just replaced becomes the new restore point. You can toggle back and forth between the two most recent activations.

:::caution
Restoring replaces the live configuration immediately. If you have a draft in progress, the draft is not affected — it remains available for future activation.
:::

## Discarding draft changes

If you decide not to go live with your draft, click **Discard** in the activation banner. This deletes all pending draft changes and returns the admin console to its normal state. Your live configuration is not affected.

Discarding is permanent — the draft content cannot be recovered after discard.

## What activates together

When you click **Activate now**, Agent Red promotes all pending changes as a single unit. The four configuration domains that activate together are:

| Domain | Examples | How it activates |
|--------|----------|-----------------|
| **Agent configuration** | Brand name, brand voice, response length, escalation rules, custom instructions | Saved to draft, activated atomically |
| **Quick actions** | Prompt buttons, page assignments, ordering | Saved to draft, activated atomically |
| **Widget configuration** | Colors, position, launcher style, dark mode, pre-chat form | Saved to draft, activated atomically |
| **Knowledge base** | Articles, categories, conflict scan results | Validated at activation time (not snapshotted) |

The knowledge base is validated during activation to ensure there are no critical conflicts, but its content is managed independently — knowledge base articles go live when you save them. The activation step confirms the knowledge base is in a healthy state but does not snapshot or version it.

## Common scenarios

### I saved changes yesterday but did not activate. Are they lost?

No. Draft changes persist until you activate or discard them. You can close the browser, log out, and return days later — the draft will still be there.

### Two team members saved changes at the same time. What happens?

All draft changes accumulate. If Admin A changes the brand voice and Admin B changes the widget color, both changes appear in the draft. The activation dialog shows all pending changes from all team members.

### I activated and my agent sounds wrong. How do I fix it?

Click **Restore previous configuration** to immediately revert to the configuration that was active before your last activation. This takes effect instantly for new conversations.

### Can I activate only some of my changes?

No. Activation is all-or-nothing across the four domains. If you want to activate only some changes, discard the draft, re-save only the changes you want, and then activate.

### What happens to in-progress conversations when I activate?

In-progress conversations continue using the configuration that was active when they started. New conversations use the newly activated configuration. There is no disruption to ongoing customer interactions.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
