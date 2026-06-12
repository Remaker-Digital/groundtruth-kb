# Phase 2 Plan: Runtime Topology Implementation (Revised)

**Date:** 2026-03-27
**Author:** Prime Builder (Opus 4.6)
**Session:** S223
**Source:** Codex Recovery Plan (INSIGHTS-2026-03-27-01-00.md), Phase 1 GO (INSIGHTS-2026-03-27-09-37.md)
**Governing decisions:** ADR-001 (dispatch by physical possibility), ADR-002 (per-agent containers)
**Status:** REVISED v2 per Codex re-review (INSIGHTS-2026-03-27-11-16.md) — 503 semantics corrected for critic/escalation

---

## Scope

Phase 2 achieves a fully canonical runtime topology: all 6 mandatory agents in dedicated containers, all in-process fallbacks removed from the canonical pipeline, SLIM and NATS deployed or verified as transport dependencies, and dispatch by physical possibility proven end-to-end. No new test suites (Phase 3). No performance work (Phase 4).

## Pre-Conditions (Phase 1 Deliverables — All Met)

- ADR-001 implemented: SLIM -> NATS -> HTTP -> 503, all environments
- ADR-002 implemented: 6 agents + widget path defined
- DCL-002 enforced: no in-process dispatch in canonical path (IC/KR/RG done in Phase 0; analytics/critic/escalation still need Phase 2 work)
- DCL-003 enforced: no phantom test evidence
- Transport specs reference ADRs
- DOC-MCP-EXCEPTIONS backfilled with strict schema
- IPR-001 links Phase 2 WIs to governing ADRs/DCLs

## Codex Advisory Findings Addressed

| # | Finding | Resolution |
|---|---------|------------|
| P1.1 | Analytics/Critic/Escalation still have in-process fallbacks | Added 2A: remove all in-process canonical fallbacks |
| P1.2 | Plan contradicts itself about stub agents | Rewritten 2B as verification/integration, not stub completion |
| P1.3 | SLIM deferral violates ADR-001 | Added 2C: SLIM+NATS as explicit dependencies |
| P2.1 | Directory not rich enough for protocol-aware routing | Narrowed 2E claims to topic discovery + env-based HTTP |
| P2.2 | Verification criteria too narrow | Expanded to 12 criteria covering all 6 agents + tier selection |

## Existing Foundation

| Component | Status | Path |
|-----------|--------|------|
| Agent base protocol | Implemented | src/agents/base.py |
| Container app factory | Implemented | src/agents/containers/agent_app.py |
| Generic agent Dockerfile | Implemented | src/agents/containers/Dockerfile |
| All 6 agents | Fully implemented | src/agents/*.py + containers/*_app.py |
| SLIM server app | Exists | src/agents/containers/slim_server_app.py |
| AGNTCY SDK (SLIM/NATS/HTTP) | Implemented | src/multi_tenant/agntcy_sdk_integration.py |
| Dispatch mixin (IC/KR/RG: 3-tier + 503) | Implemented | src/chat/pipeline/agent_dispatch.py |
| Terraform (all 9 containers incl SLIM+NATS) | Defined | infrastructure/terraform/main.tf |
| GitHub Actions agent build | Created (S223) | .github/workflows/build-agent-containers.yml |

## Phase 2 Deliverables

### 2A: Remove In-Process Canonical Fallbacks (Analytics, Critic, Escalation)

**Problem:** Phase 0 removed in-process fallback from IC/KR/RG dispatch but did NOT touch analytics, critic, or escalation. These three still terminate at in-process agent calls when transport+HTTP fail.

**Files to modify:**
- `src/chat/pipeline/analytics.py` lines 95-98: Remove `await self._an_agent.process(analytics_data, {})` in-process fallback. Replace with silent drop + warning log. Analytics is fire-and-forget — pipeline must never fail because analytics is unavailable.
- `src/chat/pipeline/critic_escalation.py` lines 81-89: Remove `_validate_with_critic_direct()` in-process path. Preserve fail-closed safe-response semantics: when transport+HTTP both fail, return `(False, SAFE_FALLBACK_MESSAGE, CriticResult(block_reason=UNAVAILABLE))`. NOT a raw 503.
- `src/chat/pipeline/critic_escalation.py` lines 309-323: Remove `_call_escalation_handler_direct()` in-process fallback. Preserve exception-to-default behavior in `_handle_escalation()`: when transport+HTTP both fail, proceed with default escalation handling (reason="transport_unavailable", urgency="medium"). NOT a raw 503.

**Three distinct failure behaviors (NOT uniform 503):**

| Agent | In-process removal | Failure behavior when transport+HTTP exhausted |
|-------|-------------------|-----------------------------------------------|
| IC/KR/RG | Already done (Phase 0) | 503 via `_require_transport_or_fail()` — correct, pipeline cannot proceed without these |
| Analytics | Phase 2 | Silent drop + warning log — fire-and-forget, never blocks pipeline |
| Critic | Phase 2 | Fail-closed safe response — blocks the AI response with safe fallback message, does NOT 503 the request |
| Escalation | Phase 2 | Exception-to-default — proceeds with default escalation context, does NOT 503 the request |

### 2B: Verify Agent Implementations + Integration Hardening

All 6 agents are fully implemented (confirmed S223). This step is NOT stub completion — it is:
- Verify each agent's container app starts and responds to /health
- Verify each agent's A2A process() endpoint handles the expected payload
- Verify container app factory wiring (configure_fn, extra_routes_fn)
- No new agent code unless integration testing reveals gaps

### 2C: SLIM + NATS as Explicit Runtime Dependencies

**Per ADR-001 and Codex finding P1.3:** SLIM and NATS must be explicit Phase 2 dependencies, not deferred.

**NATS:** Terraform already defines `nats` container (nats:2.10-alpine, port 4222, min 2 replicas). Phase 2 must verify NATS is deployed in staging or deploy it.

**SLIM:** Terraform already defines `slim-gateway` container. `slim_server_app.py` exists. Phase 2 must:
1. Build SLIM server image (add to build pipeline)
2. Deploy to staging
3. Verify SLIM transport is selected as Tier 1 when reachable
4. If SLIM cannot be deployed (external dependency, relay service), document physical impossibility per DOC-MCP-EXCEPTIONS

**Build pipeline addition:** Add SLIM server to GitHub Actions workflow or separate workflow.

### 2D: Build + Deploy Pipeline for All Containers

**Build (7+ images):**
- api-gateway (existing)
- 6 agent containers (created S223: build-agent-containers.yml)
- SLIM server (new — add to build pipeline)
- NATS uses public image (nats:2.10-alpine, no build needed)

**Deploy (scripts/deploy.py):**
- Deploy gateway + 6 agents + SLIM in dependency order
- Health-check each container after deploy
- NATS deployed via Terraform (not deploy.py)

### 2E: Dispatch Wiring + Agent Resolution

**Per Codex finding P2.1:** Directory is currently good for topic discovery, not full endpoint/protocol routing. Phase 2 uses:
- **Topic resolution:** AGNTCY Directory for A2A topic discovery (existing)
- **HTTP endpoint resolution:** Environment variables (AGENT_*_URL) with Container Apps internal DNS defaults (updated S223 in constants.py)
- **Transport tier selection:** Existing SDK logic — SLIM if configured+reachable, else NATS if configured+reachable, else HTTP

Phase 2 does NOT claim full protocol-aware directory routing. That is deferred.

**Transport tier logging:** Already in place (span attributes, _warn_http_failure_mode). Verify all 6 agent dispatch paths log tier selection.

### 2F: Widget Path Verification

Widget traffic must traverse the canonical containerized agent system:
- Widget HTTP/WebSocket -> Gateway -> IC (container) -> KR (container) -> RG (container) -> Critic (container) -> response
- X-Widget-Origin header propagated through dispatch chain
- Streaming responses (RG) work over the selected transport tier

## Implementation Sequence (Revised per Codex)

| Step | Status | Notes |
|------|--------|-------|
| **2A** — Remove in-process canonical fallbacks | ✅ COMPLETE (S223, f1cb97e4) | Analytics/critic/escalation — 3 distinct failure behaviors |
| **2C** — Verify/deploy SLIM + NATS in staging | ✅ COMPLETE (S224) | NATS: running (nats:2.10-alpine). SLIM: health sidecar added, Dockerfile.slim created, Terraform SLIM env vars added |
| **2D** — Build pipeline: add SLIM image | ✅ COMPLETE (S224) | build-slim-gateway.yml, build.py + deploy.py updated with SLIM + agent deploy loop |
| **2B** — Verify agent container health + A2A | ✅ COMPLETE (S224) | agent_app.py: /health, /ready, A2A process(), gateway short paths. Internal DNS confirmed |
| **2E** — Dispatch wiring verification | ✅ COMPLETE (S224) | transport→HTTP→503 chain confirmed. CONTAINER_APP_ENV_FQDN resolves correctly |
| **2F** — Widget path verification | ✅ COMPLETE (S224) | Widget uses same dispatch pipeline (X-Widget-Key auth → standard dispatch) |
| **Dead code** — S224 cleanup | ✅ COMPLETE (S224) | Removed _validate_with_critic_direct, _call_escalation_handler_direct, _cr_agent, _esc_agent, _an_agent |
| **Staging deploy** — Build + deploy correct images | ⏳ BLOCKED | Agent images not yet in ACR. Trigger build-agent-containers.yml + build-slim-gateway.yml, then deploy |
| **Smoke test** — Transport connectivity | ⏳ BLOCKED on staging deploy | Verify SLIM/NATS/HTTP tier selection end-to-end |

## Verification Criteria (Expanded per Codex)

Phase 2 is complete when:

1. All 6 agent containers deployed to staging and healthy (/health returns 200)
2. Gateway /ready returns 200 (transport active)
3. **No in-process fallback exists in analytics, critic, or escalation canonical paths**
4. Gateway dispatches to IC, KR, RG via transport (SLIM or NATS, not just HTTP)
5. Gateway dispatches to Critic, Escalation, Analytics via transport or HTTP (no in-process)
6. **SLIM selected as Tier 1 when SLIM endpoint is configured and reachable**
7. **NATS selected as Tier 2 when SLIM unavailable but NATS reachable**
8. **HTTP used only as Tier 3 when higher tiers exhausted**
9. Critic gate functions (fail-closed: RG output blocked when critic unavailable)
10. **RG streaming works over the selected transport tier**
11. **Widget-origin traffic traced through containerized agent pipeline**
12. DCL compliance: 3/3 passing, transport governance: 0 violations

## Files Expected to Change

**In-process removal (2A):**
- src/chat/pipeline/analytics.py (remove in-process fallback)
- src/chat/pipeline/critic_escalation.py (remove in-process fallback for critic + escalation)

**Build + deploy (2C-2D):**
- .github/workflows/build-agent-containers.yml (add SLIM if needed)
- scripts/build.py (SLIM image)
- scripts/deploy.py (agent container deployment loop)

**Dispatch (2E):**
- src/chat/pipeline/agent_dispatch.py (verify tier logging for all 6 agents)

## What Phase 2 Does NOT Do

- No new test suites (Phase 3)
- No performance benchmarks (Phase 4)
- No production deploy (Phase 5)
- No co-pilot container (deferred per owner decision)
- No full protocol-aware directory routing (narrowed per Codex P2.1)

---

*Revised per Codex advisory INSIGHTS-2026-03-27-10-52.md. All 5 findings incorporated.*

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
