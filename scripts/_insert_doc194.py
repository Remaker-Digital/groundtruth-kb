#!/usr/bin/env python3
"""One-shot script to insert DOC-194 into the Knowledge Database.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root))
sys.path.insert(0, str(_root / "tools" / "knowledge-db"))
from db import KnowledgeDB

BODY = r"""## Purpose

Verified baseline for the widget/chat improvement roadmap (S253 Phase 0). Establishes factual current state for every area, replacing the stale assumptions that caused the S252 NO-GO. This document is the scope anchor for Phases 1-4.

Owner decisions locked in S253: (1) re-baseline approved, (2) stream-then-validate confirmed, (3) fail-closed confirmed, (4) WCAG 2.1 AA target.

---

## A. Widget Transport Layer

### Active transports
- **SSE** (widget/src/transport/sse.ts, 347 lines): Manual reconnect with exponential backoff (1s-30s, 10 max). streamComplete flag prevents duplicate pipeline runs. ACTIVE.
- **HTTP** (widget/src/transport/http.ts, 429 lines): All API calls. Widget key as X-Widget-Key header. Retry on 429/5xx (opt-in). No message idempotency key. ACTIVE.

### Dormant transport
- **WebSocket** (widget/src/transport/ws.ts, 251 lines): Implemented but never instantiated. Backend WS endpoint exists (endpoints.py:1216-1267). Owner decision S253: DEFERRED.

### P0-2 Fix Applied (S253)
SSE replay contract mismatch fixed: backend reads last_event_id from both Last-Event-ID header and last_event_id query parameter. endpoints.py:644-655. Two tests added.

---

## B. Widget Testing

~62 files, ~2,170 tests across 5 layers: source inspection (771), E2E mocked (533), E2E live (686), live API (32), unit SSE/chat (148).

Critical gap: NO local JS/TS test runner. No vitest/jest. Zero component-level runtime tests.

Existing: axe-core WCAG AA scanning, widget readiness live tests, transport live tests.

---

## C. Quality Stack

### Two separate systems
1. **Project quality** (src/quality_metrics/, SPEC-1838): KB-based metrics. OPERATIONAL.
2. **Conversation quality** (src/chat/quality_scorer.py): Per-turn scoring. DEFINED BUT NEVER CALLED.

### Conversation quality gap
- EXISTS: scorer module, regression/escalation/feedback modules, quality_config (Cosmos), 3 superadmin read endpoints, Langfuse Lane 1+2
- MISSING: Runtime invocation of scorer. Cosmos quality_aggregate write path. Orchestrator integration.

### P0-4 Wiring Assessment
Minimal path: orchestrator post-pipeline calls score_turn(), persists to conversation document quality_aggregate, existing read endpoints return real data. Scorer has zero external dependencies. LOW complexity. The five dormant quality modules (regression, config, escalation, feedback) can activate independently in Phase 3.

---

## D. Critic Topology

- Current: single URL (lifecycle.py:641), global circuit breaker (critic_policy.py:323), fail-closed (correct).
- Design intent: min 2 replicas (critic_policy.py:307). Not implemented.

### P0-5 Assessment
Per-tenant breaker: process-local dict keyed by tenant_id. No Redis needed. ~4 KB memory for 20 tenants. Independent breaker state per gateway replica is acceptable.
Multi-replica: comma-separated AGENT_CRITIC_SUPERVISOR_URL. CriticPolicy already supports multiple URLs (round-robin + failover). LOW complexity for both changes.

---

## E. Security / Auth / CORS

- Widget key: query param (SSE), header (HTTP). Origin restriction: middleware.py:794-849.
- CORS: hardened on staging+production (APP_CORS_ORIGINS). Widget.js: CORS * (intentional).
- CSP: admin paths only. No widget-embed CSP. HSTS: 1 year.

---

## F. Accessibility

- EXISTS: 11 aria-labels, aria-expanded on launcher, OTP focus management, axe-core scanning.
- MISSING: aria-live regions, role=status/alert/log, prefers-reduced-motion, focus-trap, brand color contrast gap (~4.0:1 vs 4.5:1 AA).

---

## G. Release Gates

- release_pipeline.py: Class C gate (CANONICAL). Widget canary: code-complete, TF pending.
- deploy.py: --skip-widget-check (helper path, not canonical). Pre-flight: D.9 + D.10, failure = rollback.

---

## P0-6: Widget Test Runner Assessment

Recommend adding vitest in Phase 2 (not Phase 0). Vite-native, 3 devDeps. Priority targets: transport reconnection, store mutations, core components. Existing ~2,170 Python tests cover Phase 1 adequately.

---

## P0-7: Phase 1-4 Revised Scope

### Phase 1 Acceptance Criteria (MANDATORY)
1. Release-path widget proof (release_pipeline.py Class C + canary TF + browser/live)
2. Idempotent retry / duplicate suppression (idempotency key + pipeline dedup + failed-message UI)
3. SSE replay (P0-2 deployed + buffer cleanup verified)
4. Per-tenant Critic isolation (process-local breaker + multi-replica config)
5. Transport auth hardening (SSE query param exposure evaluation)

### Scope Tags (exists/partial/missing per item)
Phase 1: SSE replay EXISTS, canary PARTIAL, idempotency MISSING, Critic isolation MISSING.
Phase 2: Test runner MISSING, bundle optimization PARTIAL, accessibility AA PARTIAL.
Phase 3: Quality scorer activation PARTIAL, write path MISSING, dashboards EXISTS (empty).
Phase 4: Canary TF PARTIAL, abuse detection MISSING, docs MISSING.

Original S252: 35 specs, 97 WIs, 16 weeks. Corrected: estimate per-phase only after prior phase completes.
"""

kb = KnowledgeDB()
doc = kb.insert_document(
    id="DOC-194",
    title="S253 Phase 0: Widget/Chat Verified Baseline & Assessments",
    category="technical_assessment",
    status="current",
    changed_by="prime-builder",
    change_reason="S253 Phase 0: verified baseline for widget/chat roadmap",
    content=BODY.strip(),
    tags=["phase0", "baseline", "widget", "quality", "critic", "accessibility", "transport", "s253"],
)
print(f"Created: {doc['id']} v{doc['version']}")
