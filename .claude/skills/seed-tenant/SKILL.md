---
name: seed-tenant
description: Seed a new tenant in Cosmos DB using the 9-phase seed_tenant.py script. Creates a complete, production-ready tenant environment.
disable-model-invocation: true
argument-hint: [--execute] [--demo] [--embed]
allowed-tools: Bash, Read
license: "Proprietary - Remaker Digital"
compatibility:
  - claude-code >= 1.0
metadata:
  project: agent-red-customer-experience
  category: provisioning
  owner-only: true
  references:
    - references/phases-and-env.md
---

# Seed Tenant

Run the 9-phase tenant seeding script to create a complete tenant environment in Cosmos DB.

**Arguments:** Pass flags directly -- `$ARGUMENTS` is forwarded to `seed_tenant.py`.

## Quick Reference

| Command | Effect |
|---------|--------|
| `/seed-tenant` | Dry-run preview (no writes) |
| `/seed-tenant --execute` | Write to Cosmos DB (clean seed) |
| `/seed-tenant --execute --demo` | + seed demo conversations |
| `/seed-tenant --execute --demo --embed` | + embed KB articles (requires Azure OpenAI) |

## Execution

```bash
cd "E:/Claude-Playground/CLAUDE-PROJECTS/Agent Red Customer Engagement"
python scripts/seed_tenant.py $ARGUMENTS
```

## Process Overview

9 phases: Clean Partition -> Containers -> Tenant -> Preferences -> Team -> Knowledge Base -> Platform Config -> Demo Data -> Summary. See `references/phases-and-env.md` for the full phase table, environment variables, and post-seed steps.

## Safety

- Without `--execute`, the script is a **dry-run** -- no writes occur.
- Phase 0 **deletes ALL existing data** for the tenant partition (intentional clean slate).
- Always run dry-run first to preview what will happen.

## Post-Seed (MANDATORY after --execute)

After a successful seed, you MUST: update Key Vault, restart container app, verify auth, update `.env.local`, and update MEMORY.md. See `references/phases-and-env.md` for detailed commands.
