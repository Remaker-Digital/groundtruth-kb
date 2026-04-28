---
name: Production environment safety
description: Claude makes errors targeting wrong environment — production disrupted accidentally. Hardening needed.
type: feedback
---

Production environment must never be modified without explicit confirmation and environment verification.

**Why:** Owner observed that Claude occasionally makes errors regarding which environment (staging vs production) is being configured, leading to accidental production disruptions. The S254 CMK incident involved direct Cosmos operations on production data (purging documents, deleting tenant records, rotating keys) that — while necessary for incident response — highlighted the absence of environment-scoping safeguards.

**How to apply:**
- Always explicitly state which environment (staging/production) before any destructive or write operation
- Never run Cosmos delete/upsert operations against production without owner confirmation
- Prefer staging-first for all changes — deploy and verify on staging before touching production
- When writing scripts that touch Azure resources, include environment guards (check DB name, FQDN, resource group)
- Phase 2 should include environment-isolation checks in deployment scripts and operational procedures
- Treat any az CLI command, Cosmos SDK call, or Key Vault operation as potentially destructive and environment-sensitive
