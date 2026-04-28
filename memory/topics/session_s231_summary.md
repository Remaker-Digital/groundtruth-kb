---
name: S231 Session Summary
description: Cosmos persistence, Phase 4a UI, chat identity fix, UI redesign, competitive analysis
type: project
---

## S231 — 2026-03-29

### Commits (8 functional + 3 version bumps)
- `c607af14` — Cosmos persistence repos (WI-4010..4015): 2 collections, 2 repos, lazy hydration at 4 async boundaries, write-path invalidation
- `2f02c076` — Phase 4a UI + tenant-admin API (SPEC-1863): 11 frontend files, 10 endpoints at /api/admin/agents, RBAC
- `f1e413db` — Codex NO-GO fixes: mock registration, bindable-skills endpoint, URL sync, stale data
- `d6d37562` — Cosmos indexing fix: remove /id/? from custom policy
- `11f2fa7d` — Chat widget identity (SPEC-1862): pass admin auth token for team member identification
- `0fc96dc9` — Phase 4a UI redesign: 6 owner-directed changes (sidebar scroll, rename/reorder, unified skills table, tooltips, merge integrations, provider logos)

### Deployments
- Staging: v1.98.68 deployed and verified. v1.98.69 built (identity fix) but deployment paused per owner.
- Production: v1.98.66 unchanged (GOV-16 pending).
- Cosmos containers (agent_overlays, agent_bindings) created on both staging and production databases.

### Codex Reviews: 7 GO verdicts + 1 architecture memo
- 3 rounds on Cosmos persistence (cache coherency, hydration paths, cold-cache coverage)
- 4 rounds on Phase 4a API/UI (auth boundary, RBAC, mock registration, bindable-skills)
- Architecture memo: RBAC + agent extensibility proposal with 7 architecture tracks

### Key Decisions
- Sync/async contract: synchronous facade, cache-backed, async repo writes + immediate invalidation
- API surface: /api/admin/agents (tenant-admin), not /api/superadmin/ (platform-admin)
- Integrations merged into agents: Zendesk, Slack, Google Docs added to agents.yaml (20 total)
- All agents available at all tiers (foundational entitlement) until entitlements configured
- Phase B should be smaller than Codex proposed: admin + team_member only, defer escalation_member scoping

### Pending for S232
- **Codex response** to competitive analysis + adjusted phasing (msg 6a38df03) — start S232 by reading this
- **Registry data review** — agent/skill descriptions, tier_gate values (dedicated activity)
- **Per-agent tier entitlements** — deferred until infrastructure proven
- **.env.staging URL fix** — corrected locally (admin/standalone/.env.staging, admin/provider/.env.staging)
- **Build v1.98.69** ready in ACR but deployment paused
- **Production deploy** — requires GOV-16 owner approval
- **Chat widget identity** — committed but not deployed to staging yet (in v1.98.69)

### Competitive Analysis (owner-approved)
- Agent Red's pluggable model ahead of SMB competitors (Gorgias, Intercom) but behind Salesforce
- Architecture should SUPPORT enterprise complexity without REQUIRING it in phase one
- Product gaps noted: NL escalation guidance, marketplace model, conversation-level agent activation
