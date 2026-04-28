---
name: Canonical Identity Model — Pre-Launch Blocker
description: ADR-004 identity refactor must ship before marketing spend. Internal ID as primary key, contact methods as attributes.
type: project
---

ADR-004: Customer identity primary key must be an internally generated stable ID, not a contact means (email, phone, Shopify ID). Contact methods are mutable attributes of identity.

**Why:** Migrating identity keys after production users exist creates data migration risk and unfixable profile fragmentation. Owner classified this alongside zero-knowledge security as work that must precede user acquisition spend.

**How to apply:** This is a pre-launch blocker. When scoping release milestones, this refactor must be scheduled before any marketing-driven user acquisition. Affects ~15 files across 9 layers (widget, preprocessor, OTP, schema, tokens, escalation, admin, profile, Shopify passthrough). INV-1 (phone) and INV-2 (WhatsApp) depend on this completing first.

**Decision date:** 2026-04-05 (S260)
