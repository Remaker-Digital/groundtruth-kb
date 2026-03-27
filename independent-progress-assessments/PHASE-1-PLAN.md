# Phase 1 Plan: Architecture & Governance Reset

**Date:** 2026-03-27
**Author:** Prime Builder (Opus 4.6)
**Session:** S223
**Source:** INSIGHTS-2026-03-27-01-00.md (Codex Recovery Plan), Phase 0 GO (INSIGHTS-2026-03-27-07-52.md)
**Status:** IMPLEMENTED — Codex advisory review received (INSIGHTS-2026-03-27-08-31.md), findings addressed

---

## Scope

Phase 1 codifies the transport/container architecture as formal decision records and design constraints. No runtime code changes. No new tests beyond DCL assertions. Goal: the architecture is fully specified with machine-checkable constraints before Phase 2 implementation begins.

## Pre-Conditions (Phase 0 Deliverables)

All verified in S223 and committed (`766452f6`):

- **DCL-002:** No mainline in-process dispatch (implemented, passing)
- **DCL-003:** No phantom evidence for transport specs (implemented, passing)
- **KB governance gate:** insert_spec/update_spec/insert_test/update_test reject phantom evidence for transport-gated specs
- **In-process removal:** All dispatch chains terminate at `_require_transport_or_fail()` → 503
- **health.py:** Transport enforcement in ALL environments
- **8 regression tests** in TestTransportGovernanceGate (all pass)
- **DOC-180:** Gateway load tests scoped as gateway regression only

## Owner Decisions In Force

Captured from bridge message `dc410a42`:

1. **Local debug harness:** Default NO for canonical pipeline. May exist only if explicitly segregated, opt-in, excluded from CI/compliance, never cited as architecture evidence.
2. **Recovery scope:** 6 pipeline-critical agents + widget first. Co-pilot deferred unless explicitly argued as production-critical. Agents: intent-classifier, knowledge-retrieval, response-generator, critic-supervisor, escalation-handler, analytics-collector.

## Phase 1 Deliverables

### 1A: ADR-001 — Dispatch Selection by Physical Possibility

**Artifact:** `ADR-001` (KB spec, type=architecture_decision)

**Decision:** The canonical dispatch algorithm selects transport tier based on physical possibility, not configuration preference or environment. The algorithm is:

1. Resolve the target agent and its reachable protocols (from agent directory/card).
2. If SLIM/gRPC relay is physically reachable for the target → use SLIM.
3. Else if NATS broker is physically reachable → use NATS.
4. Else if HTTP(S) endpoint is physically reachable → use HTTP(S).
5. Else → fail 503 with explicit tier-diagnostic reason.

**Context:**
- Prior state: 4-tier hierarchy with in-process as Tier 4 fallback (development only).
- Owner directive: transport selection by physical possibility, same rule in all environments.
- Phase 0 removed in-process from canonical path. ADR-001 formalizes the replacement.

**Failed approaches:**
- Configuration-based tier selection (allowed environment-specific behavior, masked failures)
- In-process fallback (violated containerization requirement, created phantom verification)

**Consequences:**
- Local development without running containers will get 503 (by design).
- A separate local debug harness may exist outside canonical path (owner decision 1).
- Every dispatch must log: attempted tier, selected tier, reason higher tiers were unavailable.

**Linked specs:** SPEC-1802 (transport architecture), SPEC-1524 (SLIM), SPEC-1525 (NATS)

### 1B: ADR-002 — Dedicated Per-Agent Containers

**Artifact:** `ADR-002` (KB spec, type=architecture_decision)

**Decision:** Each pipeline agent operates in a dedicated container. No shared-process agent hosting in the canonical architecture.

**Mandatory container set (Phase 1 scope):**

| Agent | Container Name | Role |
|-------|---------------|------|
| Intent Classifier (IC) | `agent-red-ic` | Classifies inbound message intent |
| Knowledge Retrieval (KR) | `agent-red-kr` | Retrieves knowledge articles for RAG |
| Response Generator (RG) | `agent-red-rg` | Generates customer-facing responses |
| Critic Supervisor | `agent-red-critic` | Reviews response quality before delivery |
| Escalation Handler | `agent-red-escalation` | Routes to human agents |
| Analytics Collector | `agent-red-analytics` | Aggregates conversation metrics |

**Deferred:** Co-pilot (not in first recovery tranche per owner decision 2).

**Widget:** Edge client — not a container, but its traffic path must traverse the canonical containerized agent system. Widget-origin requests are traced through the same dispatch path.

**Context:**
- Prior state: All agents co-located in gateway process with in-process dispatch.
- Owner directive: "Each agent must operate in a dedicated container."
- This ADR records the topology, not the implementation (Phase 2).

**Consequences:**
- Each container needs its own Dockerfile, health endpoint, and agent card.
- Inter-agent communication is always over transport (SLIM/NATS/HTTP), never in-process.
- Container failure is isolated — one agent down does not take down the pipeline.
- Resource allocation (CPU/memory) is per-agent, enabling independent scaling.

**Linked specs:** SPEC-1802, SPEC-1535 (agent containers), SPEC-1536 (transport fallback)

### 1C: DCL-004 — SDK Mock Contract Twins

**Artifact:** `DCL-004` (KB spec, type=design_constraint)

**Constraint:** Every mocked external SDK call in the test suite must have a corresponding contract test that validates the mock against the real installed SDK.

**Rationale:** Codex Finding 3 (INSIGHTS-2026-03-27-01-00) identified that AGNTCY SDK tests validate mocks and structural source strings, not the installed SDK contract. Mocks can drift from reality silently.

**Assertions:** Cleared to `[]` per Codex advisory finding 3 (INSIGHTS-2026-03-27-08-31.md). Original assertions used unsupported field names and directory paths. Assertions will be defined in Phase 3 when contract tests are written.

**Enforcement:** Advisory in Phase 1 (no blocking gate). Becomes blocking in Phase 3 when contract tests are written.

**Linked specs:** SPEC-1524, SPEC-1525

### 1D: DCL-005 — MCP Exception Register

**Artifact:** `DCL-005` (KB spec, type=design_constraint)

**Constraint:** Every non-MCP integration or internal agent link must record an explicit exception with: target system, blocking reason, chosen fallback protocol, and review date.

**Rationale:** Owner directive: "MCP is mandatory except where it is not possible." Without a formal exception register, "not possible" becomes an uncontrolled escape hatch (Codex Finding 5).

**Assertions:** Cleared to `[]` per Codex advisory finding 3 (INSIGHTS-2026-03-27-08-31.md). Original assertion grepped a binary SQLite file. Register existence validated by KB document query instead. Assertions will be defined when DCL-005 is promoted to implemented in Phase 2.

**Enforcement:** Advisory in Phase 1. Becomes blocking in Phase 2 when containers are deployed.

### 1E: Transport Spec Normalization

**Action:** Update existing transport/container specs to reference the new ADRs and reflect the canonical architecture. No status changes — specs remain at `implemented` until Phase 3 provides executable evidence.

**Specs to update:**
- **SPEC-1802:** Add references to ADR-001, ADR-002. Update description to match canonical dispatch algorithm (remove any remaining in-process language).
- **SPEC-1524 (SLIM):** Reference ADR-001 tier 1 selection rule. Clarify: SLIM is used when physically possible, not when configured.
- **SPEC-1525 (NATS):** Reference ADR-001 tier 2 selection rule. Same clarification.
- **SPEC-1535 (Agent containers):** Reference ADR-002 container topology table.
- **SPEC-1536 (Transport fallback):** Reference ADR-001 fallback chain. Remove any "FAIL" terminal — HTTP is now tier 3 before 503.
- **SPEC-1537 (Transport architecture):** Reference both ADRs as governing decisions.

### 1F: MCP Exception Register (Initial)

**Artifact:** `DOC-MCP-EXCEPTIONS` (KB document, category=architecture)

**Content:** Initial exception register. Survey all current agent links and integrations, document which use MCP and which don't, with reasons.

**Expected entries:**
- Widget ↔ Gateway: HTTP/WebSocket (MCP not applicable — browser client, no MCP runtime)
- Gateway ↔ IC/KR/RG/Critic/Escalation/Analytics: SLIM/NATS/HTTP via AGNTCY (MCP used for tool exposure; transport is A2A protocol, not MCP transport)
- External integrations (Stripe, Shopify, etc.): MCP adapters where available, HTTP REST where MCP server doesn't exist

### 1G: Assertion Runner Defect Fix — DONE

**Action:** Fixed. assertions.py line 212 now handles plain-text assertions (strings instead of dicts) gracefully. SPEC-1848 had string assertions causing the crash. Committed in `7c439cc9`.

---

## Verification Criteria

Phase 1 is complete when:

1. ADR-001 and ADR-002 exist in KB at status `implemented`
2. DCL-004 and DCL-005 exist in KB at status `specified` (advisory)
3. All 3 active DCLs pass (`validate_dcl_constraints()` returns 3/3; DCL-004/005 remain specified/advisory, excluded from validator)
4. Transport specs (SPEC-1524/1525/1535/1536/1537/1802) reference ADRs
5. DOC-MCP-EXCEPTIONS exists in KB
6. assertion-check.py runs cleanly (no type errors)
7. IPR-001 document created linking Phase 2 WIs to ADR-001/ADR-002/DCL-002..005

## Files Expected to Change

- `tools/knowledge-db/knowledge.db` (KB records: ADR-001, ADR-002, DCL-004, DCL-005, DOC-MCP-EXCEPTIONS, spec updates)
- `.claude/hooks/assertion-check.py` (defect fix)
- No runtime code changes in Phase 1

## Estimated Scope

- 7 KB artifacts (2 ADRs, 2 DCLs, 1 document, 1 IPR, 6 spec updates)
- 1 bug fix (assertion-check.py)
- No builds, no deploys

## What Phase 1 Does NOT Do

- No runtime code changes (that's Phase 2)
- No new tests beyond DCL assertions (that's Phase 3)
- No performance work (that's Phase 4)
- No production deploy gate (that's Phase 5)
- DCL-004 and DCL-005 are advisory only — they don't block until their respective implementation phases

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
