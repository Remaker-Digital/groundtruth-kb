# applications/Agent_Red/CLAUDE.md — Agent Red Customer Experience

> **Scope:** This file is **application-scope guidance** for the Agent Red Customer Experience application. It is consulted only when the active GT-KB work subject is `application` AND the named application is Agent Red. It is NOT platform authority and does NOT modify GT-KB platform rules.
>
> Agent Red itself is a **separate project** at `https://github.com/mike-remakerdigital/agent-red`. This file documents the Agent-Red-specific guidance that lives within the GT-KB application-management surface (`applications/Agent_Red/`) per `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001`.
>
> For platform-scope guidance (Roles, Governance Index, Bridge Protocol, Artifact discipline, Knowledge Database Access, AskUserQuestion enforcement), see [`E:\GT-KB\CLAUDE.md`](../../CLAUDE.md). Platform rules govern this application; application rules do not govern the platform.

---

## Application Identity

| Attribute | Value |
|-----------|-------|
| **Application Name** | Agent Red Customer Experience |
| **Type** | Commercial SaaS Product (Shopify + Standalone) |
| **Status** | See `memory/MEMORY.md` for versions, test counts, and release progress. |
| **Owner** | Remaker Digital (DBA of VanDusen & Palmeter, LLC) |
| **Application Project Root** | `E:\GT-KB\applications\Agent_Red\` |
| **Application Source Repository** | `https://github.com/mike-remakerdigital/agent-red` (separate from GT-KB platform) |

### Copyright Notice

All new work in this application directory must include:

```
© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
```

This copyright applies to Agent Red application code. GT-KB platform code carries its own platform-scope copyright; application copyright must not be mistakenly applied to platform code outside `applications/Agent_Red/`.

---

## Adding Commercial Features

When the work subject is Agent Red:

1. Create features in `applications/Agent_Red/src/` exclusively
2. Add the Agent Red copyright notice to all new files
3. Test integration patterns independently
4. Never commit AGNTCY source code into this repo
5. Read AGNTCY from the public repo: https://github.com/Remaker-Digital/AGNTCY-muti-agent-deployment-customer-service

---

## Branching Strategy

This branching strategy applies to **Agent Red application deployment**. GT-KB platform releases follow a separate cycle (PyPI `groundtruth-kb` package; see platform release-readiness governance under `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`).

| Branch | Purpose | Updated when |
|--------|---------|-------------|
| `main` | Production mirror. Always matches the most recent Agent Red production deployment. | Merge from `develop` at deployment time. |
| `develop` | Continuous development. All new Agent Red features, fixes, and experiments land here. | Every session. |
| `hotfix/*` | Emergency production patches. Branched from `main`, merged back to both `main` and `develop`. | Critical production issues only. |

**Workflow:** `develop` → build/test → deploy to staging → staging verified → merge to `main` → deploy to production.

**Rules:**
1. Never commit directly to `main`. All work happens on `develop`.
2. Merge to `main` only as part of an Agent Red production deployment operation.
3. `main` must always be deployable — it represents what is running in Agent Red production.
4. Version tags (v1.98.x) are created on `develop` at build time and propagated to `main` via merge.
5. Hotfixes follow the hotfix workflow below.

**Before deploying any Agent Red build, ask this question: Is Agent Red ready for a full production deployment?** (Per GOV-16 deploy gate; owner approval required.)

### Hotfix Workflow

1. Branch from `main` at the current production tag: `hotfix/v{version}-{issue}` (e.g., `hotfix/v1.98.92-critic-timeout`).
2. Implement the minimal fix. CI (lint, tests, security scan) runs automatically on `hotfix/**` branches.
3. Deploy the hotfix branch to staging for verification.
4. After staging verification, merge to `main` and deploy to production (GOV-16 approval required).
5. Immediately backport: merge `main` to `develop` to prevent divergence.
6. Delete the hotfix branch after both merges are confirmed.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved. Created: 2026-05-29 (Slice 3 of `gtkb-claude-md-scope-clarification`).*
