# Phase 2 Plan: Runtime Topology Implementation

**Date:** 2026-03-27
**Author:** Prime Builder (Opus 4.6)
**Session:** S223
**Source:** Codex Recovery Plan (INSIGHTS-2026-03-27-01-00.md), Phase 1 GO (INSIGHTS-2026-03-27-09-37.md)
**Governing decisions:** ADR-001 (dispatch by physical possibility), ADR-002 (per-agent containers)
**Status:** DRAFT — sent to Codex for advisory review

---

## Scope

Phase 2 deploys the 6 mandatory agents (per ADR-002) in dedicated containers and wires the canonical dispatch path (per ADR-001). No new test suites (Phase 3). No performance work (Phase 4).

## Pre-Conditions (Phase 1 Deliverables — All Met)

- ADR-001 implemented: SLIM → NATS → HTTP → 503, all environments
- ADR-002 implemented: 6 agents + widget path defined
- DCL-002 enforced: no in-process dispatch in canonical path
- DCL-003 enforced: no phantom test evidence
- Transport specs reference ADRs
- DOC-MCP-EXCEPTIONS backfilled with strict schema
- IPR-001 links Phase 2 WIs to governing ADRs/DCLs

## Existing Foundation (Already Built)

| Component | Status | Path |
|-----------|--------|------|
| Agent base protocol (AgentRedBaseAgent) | Implemented | src/agents/base.py |
| Container app factory (create_agent_app) | Implemented | src/agents/containers/agent_app.py |
| Generic agent Dockerfile (ARG AGENT_MODULE) | Implemented | src/agents/containers/Dockerfile |
| Intent Classifier agent | Fully implemented | src/agents/intent_classifier.py + containers/intent_classifier_app.py |
| Knowledge Retrieval agent | Fully implemented | src/agents/knowledge_retrieval.py + containers/knowledge_retrieval_app.py |
| Response Generator agent (+ SSE streaming) | Fully implemented | src/agents/response_generator.py + containers/response_generator_app.py |
| Escalation Handler agent | Fully implemented (Azure OpenAI context analysis) | src/agents/escalation_handler.py + containers/escalation_handler_app.py |
| Analytics Collector agent | Fully implemented (structured stage logging) | src/agents/analytics_collector.py + containers/analytics_collector_app.py |
| Critic Supervisor agent | Fully implemented (fail-closed with CriticVerdict) | src/agents/critic_supervisor.py + containers/critic_supervisor_app.py |
| Co-Pilot agent (deferred from Phase 2) | Implemented | src/agents/co_pilot.py + containers/co_pilot_app.py |
| AGNTCY SDK integration (SLIM/NATS/HTTP) | Implemented | src/multi_tenant/agntcy_sdk_integration.py |
| Dispatch mixin (3-tier + 503) | Implemented | src/chat/pipeline/agent_dispatch.py |
| Terraform environment | Exists | infrastructure/terraform/main.tf |

## Phase 2 Deliverables

### 2A: Verify Agent Implementations — ALREADY COMPLETE

All 6 agents are fully implemented (not stubs as initially reported):
- **Escalation Handler:** Azure OpenAI GPT-4o-mini context analysis, urgency/category/reason extraction
- **Analytics Collector:** Structured per-stage logging with tenant/conversation/intent metrics
- **Critic Supervisor:** Fail-closed gate with CriticVerdict/CriticBlockReason enums, immutable system prompt, KB-aware false-positive prevention

No implementation work needed for 2A.

### 2B: Build Pipeline for 7 Images

Update scripts/build.py to build 7 images:
1. `api-gateway` (existing)
2. `agent-intent-classifier`
3. `agent-knowledge-retrieval`
4. `agent-response-generator`
5. `agent-escalation-handler`
6. `agent-analytics-collector`
7. `agent-critic-supervisor`

Each agent image uses src/agents/containers/Dockerfile with `--build-arg AGENT_MODULE=<name>_app`.

GitHub Actions workflow updates: add per-agent build jobs (can run in parallel).

### 2C: Terraform Container App Definitions

Add 6 container app resources to infrastructure/terraform/main.tf:

| Container App | Replicas | CPU/Mem | Ingress | Scaling |
|--------------|----------|---------|---------|---------|
| agent-red-ic | min 2 | 1 CPU / 2 GB | Internal | NATS queue depth |
| agent-red-kr | min 2 | 1 CPU / 2 GB | Internal | NATS queue depth |
| agent-red-rg | min 2 | 2 CPU / 4 GB | Internal | NATS queue depth |
| agent-red-critic | min 2 | 1 CPU / 2 GB | Internal | NATS queue depth |
| agent-red-escalation | min 2 | 0.5 CPU / 1 GB | Internal | HTTP concurrent requests |
| agent-red-analytics | min 1 | 0.5 CPU / 1 GB | Internal | NATS queue depth |

All containers share: NATS_URL, COSMOS_DB_ENDPOINT, AZURE_KEYVAULT_URL, AZURE_OPENAI_ENDPOINT (where applicable).

Internal ingress only — agents are not publicly accessible. Gateway routes to them via SLIM/NATS/HTTP.

### 2D: Agent Directory Registration

Wire SPEC-1789 agent directory:
- Each agent container registers its agent card on startup via create_agent_app() (already stubbed)
- Agent cards declare: agent_type, supported protocols (SLIM, NATS, HTTP), endpoint URLs
- Gateway resolves agent locations from directory at dispatch time
- Fallback: environment variables (AGENT_IC_URL, etc.) for static configuration

### 2E: Gateway Dispatch Wiring

Update src/chat/pipeline/agent_dispatch.py and constants.py:
- Resolve container URLs from agent directory (2D) or env vars
- HTTP fallback URLs point to internal container app DNS names
- Transport tier logging: log attempted tier, selected tier, reason for fallback on every dispatch
- Widget-origin request tracing: pass X-Widget-Origin header through dispatch chain

### 2F: Deploy Pipeline Updates

Update scripts/deploy.py:
- Deploy 7 images (gateway + 6 agents) in dependency order
- Health-check each agent container after deploy
- Rollback capability: if any agent fails health check, revert that container

---

## Implementation Sequence

1. **2A** — Complete stub agents (Escalation, Analytics, Critic)
2. **2B** — Build pipeline for 7 images (build.py + GitHub Actions)
3. **2C** — Terraform container definitions (main.tf)
4. **2D** — Agent directory registration (agent cards)
5. **2E** — Gateway dispatch wiring (resolve from directory/env)
6. **2F** — Deploy pipeline updates (deploy.py)
7. **Staging deploy** — Deploy all 7 containers to staging
8. **Smoke test** — Verify transport connectivity between gateway and each agent

## Verification Criteria

Phase 2 is complete when:

1. All 6 agent containers deployed to staging and healthy (/health returns 200)
2. Gateway /ready returns 200 (transport active)
3. Gateway can dispatch to IC, KR, RG via at least one transport tier (NATS or HTTP)
4. Critic gate functions (RG output reviewed before delivery)
5. Escalation handler receives escalation requests
6. Analytics collector receives conversation events
7. Transport tier logged on every dispatch
8. DCL compliance: 3/3 passing
9. Transport governance: 0 violations

## Files Expected to Change

**Agent implementations:**
- src/agents/escalation_handler.py (complete stub)
- src/agents/analytics_collector.py (complete stub)
- src/agents/critic_supervisor.py (complete stub)

**Build & deploy:**
- scripts/build.py (7 images)
- scripts/deploy.py (7 containers)
- .github/workflows/ (per-agent build jobs)

**Infrastructure:**
- infrastructure/terraform/main.tf (6 new container apps)
- infrastructure/terraform/variables.tf (agent-specific vars)

**Dispatch:**
- src/chat/pipeline/agent_dispatch.py (directory resolution, tier logging)
- src/chat/pipeline/constants.py (container URLs)

**No changes to:** tools/knowledge-db/db.py, .claude/hooks/, knowledge.db (Phase 2 is runtime, not governance)

## What Phase 2 Does NOT Do

- No new test suites (Phase 3)
- No performance benchmarks (Phase 4)
- No production deploy (Phase 5)
- No co-pilot container (deferred per owner decision)
- No SLIM server deployment (requires SLIM relay infrastructure; NATS + HTTP are sufficient for initial topology)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
