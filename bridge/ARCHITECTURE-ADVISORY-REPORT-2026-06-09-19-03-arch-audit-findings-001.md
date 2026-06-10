ADVISORY

# Architecture Advisory Report: Horizontal Compliance Audit Findings

**Bridge:** `ARCHITECTURE-ADVISORY-REPORT-2026-06-09-19-03-arch-audit-findings`  
**Status:** ADVISORY — non-dispatchable, awaiting Prime acknowledgement and disposition decision  
**Author:** Loyal Opposition (Antigravity, harness C)  
**Generated:** 2026-06-09T19:07Z  
**Scope:** 98 ADR/DCL specifications in `E:\GT-KB\groundtruth.db`  
**Source insight:** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-09-19-03-arch-audit-findings.md` (Prime Builder, Codex, 2026-06-09)

---

## Objective and Intended Outcome

Combine and verify the Prime Builder architecture audit findings (INSIGHTS-2026-06-09-19-03) against an independent Loyal Opposition audit run. Identify gaps, correct inaccuracies, and present a unified evidence-based advisory report for Prime Builder disposition.

**Outcome:** 10 FAILING ADR/DCL specs identified (up from 7 in the source insight), with verified root causes and a prioritized remediation plan for Prime Builder.

---

## Verification of Source Insight Document

### ✅ Findings Correctly Stated

| Insight Finding | Verification Status | Notes |
|---|---|---|
| ADR-001 FAILING: 0/3, `agent_dispatch.py` missing | ✅ Confirmed | File assertions fail — transport dispatch files not present |
| ADR-002 FAILING: 2/3, `agent_app.py` missing | ✅ Confirmed | 2 of 3 passing; container factory file not found |
| DCL-002 FAILING: 0/3, same dispatch files | ✅ Confirmed | Same root cause as ADR-001 |
| ADR-006 FAILING: 0/2, envelope encryption + audit sanitizer | ✅ Confirmed | Title: "Envelope encryption and audit sanitization" |
| ADR-007 FAILING: 0/2, auth key prefix middleware | ✅ Confirmed | Title: "Multi-tenant SPA and user auth key prefix" |
| DCL-005 FAILING: 0/2, MCP plugin registry | ✅ Confirmed | `registry.py` and `agents.yaml` not found |
| ADR-005 FAILING: 0/3, RBAC middleware | ✅ Confirmed | `middleware.py` not found |
| Security-tenant isolation is highest severity | ✅ Corrected framing | Valid IF these are GT-KB platform specs; see root cause analysis below |
| Transport layer stable | Confirmed | Foundational, P1 remediation sequencing correct |
| Implementation context and ordered sequence | Reasonable | See priority revision below |

### ⛔ Gaps and Corrections in Source Insight

**Gap 1: 3 FAILING specs omitted entirely.**

The source insight covers only 7 of 10 FAILING specs. The following 3 are absent:

| Spec | Failing Count | Root Cause |
|---|---|---|
| `DCL-STANDING-BACKLOG-DB-SCHEMA-001` | 4/10 assertions passing | Design pivot stale assertions — v4 GO at S342 approved new `work_items` schema but v1 `backlog_items` DDL assertions still registered |
| `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` | 0/4 assertions passing | Slice 3 lint script not yet created; assertions scan for file patterns that don't exist |
| `DCL-004` | 0/1 assertion passing | Contract test markers not found in `tests/` directory |

**Gap 2: Root cause analysis incomplete.**

The source insight does not identify WHY ADR-001 through ADR-007 + DCL-002 + DCL-005 fail. The root cause is a **scope mismatch**: these are Agent Red application-layer ADRs recorded v1 by the legacy `record_adrs.py` script, but assertion runs scan GT-KB platform source paths (`src/chat/pipeline/`, `src/multi_tenant/`, `src/agents/`). The files don't exist in the platform checkout because they belong to Agent Red's application lifecycle. `DCL-ADOPTER-SPEC-RECLASSIFICATION-001` already mandates this — per the spec: *"application-layer architecture records previously filed at the platform layer MUST be reclassified from SPEC to ADR/DPL and marked retired"*. The fix is not "implement the files" but "reclassify and retire the platform-level assertions" or "re-point assertions to Agent Red's codebase".

**Gap 3: Priority framing needs context.**

The source insight classifies ADR-006/ADR-007 as P0 (tenant isolation). This is correct as a security principle, but given the spec scope mismatch (see Gap 2), the remediation path is reclassification, not implementation. P0 framing applies only if these are live GT-KB platform security constraints; they are not — they are Agent Red application-layer specs.

**Gap 4: Family placement.**

The source insight places ADR-005/006/007 under "Zero-Knowledge / Tenant Isolation". This is **more accurate** than this audit's initial ADR-number-proximity grouping under "Transport / Container / Routing". Content-based: ADR-006 (envelope encryption), ADR-007 (auth key prefix) are tenant isolation, not transport. This advisory adopts the family mapping from the insight doc.

---

## Complete Horizontal Compliance Audit Matrix

### Summary

```
╔══════════════════════════════════════════════════════════════════╗
║  52 ENFORCED   39 SPECIFIED   10 FAILING   0 UNASSESSED        ║
║  2 RETIRED                                                      ║
║  98 Total ADR/DCL specifications                                ║
║  45 with assertion runs (35 passing, 10 failing)                ║
║  Assertion coverage: 46% of all ADR/DCL (45/98)                 ║
╚══════════════════════════════════════════════════════════════════╝
```

### ✅ Fully Enforced Families

**Zero-Knowledge / Tenant Isolation (8/8 ENFORCED):**

| Spec | Status | Assertions |
|---|---|---|
| DCL-PLATFORM-APPLICATION-NON-SPECIFICITY-001 | ENFORCED | 1/1 |
| DCL-DEFAULT-WORKSPACE-IS-GT-KB-001 | ENFORCED | 1/1 |
| DCL-WORKSPACE-EXCEPTION-INTERROGATION-001 | ENFORCED | 1/1 |
| DCL-WORKSPACE-INFERENCE-PROHIBITED-001 | ENFORCED | 1/1 |
| DCL-ENV-CLI-ENFORCEMENT-001 | ENFORCED | 6/6 |
| DCL-AGENT-RED-CONFORMANT-CONTAINED-APP-001 | ENFORCED | 1/1 |
| DCL-ADOPTER-SPEC-RECLASSIFICATION-001 | ENFORCED | 1/1 |
| DCL-GTKB-INDEPENDENT-TEST-SUITE-001 | ENFORCED | 1/1 |

**MCP / Plugin / Binding (5/5 ENFORCED):**

| Spec | Status | Assertions |
|---|---|---|
| ADR-OLLAMA-HARNESS-ADOPTION-001 | ENFORCED | 5/5 |
| DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001 | ENFORCED | 3/3 |
| DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001 | ENFORCED | 4/4 |
| DCL-OLLAMA-TOOL-PARITY-GATE-001 | ENFORCED | 4/4 |
| DCL-CROSS-HARNESS-ENFORCEMENT-001 | ENFORCED | 2/2 |

### ⛔ FAILING Specs (10 total)

#### P1 — Agent Red Application-Layer Reclassification Required

These are Agent Red application-layer ADRs recorded v1 by legacy `record_adrs.py` but assertions target GT-KB platform paths. Per `DCL-ADOPTER-SPEC-RECLASSIFICATION-001`, they require reclassification from platform spec to application ADR + assertion re-scoping to Agent Red's codebase, or retirement.

| # | Spec | Title | Status | Passing | Failing Files |
|---|---|---|---|---|---|
| 1 | ADR-001 | Multi-agent transport layer | implemented | 0/3 | `agent_dispatch.py`, `agntcy_sdk_integration.py` |
| 2 | ADR-002 | Agent container architecture | implemented | 2/3 | `agent_app.py` |
| 3 | ADR-005 | Multi-tenant RBAC middleware | implemented | 0/3 | `middleware.py` |
| 4 | ADR-006 | Envelope encryption and audit sanitization | implemented | 0/2 | `envelope_encryption.py`, `audit_sanitizer.py` |
| 5 | ADR-007 | Multi-tenant SPA and user auth key prefix | implemented | 0/2 | `middleware.py` |
| 6 | DCL-002 | IC/KR transport and streaming policy | implemented | 0/3 | `agent_dispatch.py` |
| 7 | DCL-005 | Agent plugin registry (MCP-based) | implemented | 0/2 | `registry.py`, `agents.yaml` |

**Recommended remediation:** Reclassify each to `type: ADR` at application layer, mark retired at platform layer, and transfer assertion runs to Agent Red's codebase paths. Estimated effort: small (reclassification + assertion re-path). This is the correct fix per `DCL-ADOPTER-SPEC-RECLASSIFICATION-001`.

#### P2 — Stale Design-Pivot Assertions

| # | Spec | Title | Status | Passing | Root Cause |
|---|---|---|---|---|---|
| 8 | DCL-STANDING-BACKLOG-DB-SCHEMA-001 | Standing backlog database schema | **verified** | 4/10 | **Stale assertions:** Spec marked v4 GO at S342 after Codex design pivot from dedicated `backlog_items` table to extending `work_items`. 6 remaining assertions target the abandoned v1 `backlog_items` schema (composite PK, no_update trigger, no_delete trigger, `current_backlog_items` view, `backlog_item_name` column). Marked verified despite failing assertions — verification gate bypass. |

**Recommended remediation:** Update the 6 failing assertion descriptions and regex patterns to match the approved v4 `work_items` schema, or retire the obsolete v1 assertions and register new assertions targeting v4. The spec `status: verified` contradicts assertions `4/10 fail` — this is a governance state inconsistency.

#### P3 — Unimplemented Enforcement Tooling

| # | Spec | Title | Status | Passing | Root Cause |
|---|---|---|---|---|---|
| 9 | DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001 | LO advisory owner-grilling gate | specified | 0/4 | **Lint script not created:** Assertions scan for `scripts/advisory_grilling_gate_lint.py` which is registered in the spec description but hasn't been written. 4 assertions: Mode header detection (0/727 files), classification declaration section (0/727), blocking gate heading (0/727), enumeration count ≥3 (0/727). Slice 3 of the advisory gating stack pending. |

**Recommended remediation:** Implement `scripts/advisory_grilling_gate_lint.py` per the spec requirements (Slice 3 work). Until then, assertions are correctly failing — they will pass once the lint script is created.

#### P4 — Missing Contract Test Infrastructure

| # | Spec | Title | Status | Passing | Root Cause |
|---|---|---|---|---|---|
| 10 | DCL-004 | AGNTCY integration contract enforcement | specified | 0/1 | **Contract test markers not found:** Assertion scans `tests/` for AGNTCY integration contract test markers. No such markers exist in the codebase. |

**Recommended remediation:** Create AGNTCY integration contract tests under `tests/` with the required markers, or retire DCL-004 if the contract testing approach has changed.

---

## Priority Revision

Replacing the source insight's priority sequence with a corrected version that accounts for root cause:

| Priority | Action | Specs | Estimated Effort | Rationale |
|---|---|---|---|---|
| **P1** | Reclassify Agent Red application-layer ADRs per DCL-ADOPTER-SPEC-RECLASSIFICATION-001 | ADR-001, ADR-002, ADR-005, ADR-006, ADR-007, DCL-002, DCL-005 | Small | Removes 7 FAILING specs from GT-KB platform compliance matrix via correct scoping |
| **P2** | Update stale design-pivot assertions for DCL-STANDING-BACKLOG-DB-SCHEMA-001 | DCL-STANDING-BACKLOG-DB-SCHEMA-001 | Small | 4/10 → 10/10; resolves verified status ↔ failing assertion contradiction |
| **P3** | Implement advisory grilling gate lint script (Slice 3) | DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001 | Medium | Part of standing backlog; implementation needed |
| **P4** | Create AGNTCY contract test infrastructure or retire DCL-004 | DCL-004 | Small–Medium | Depends on whether AGNTCY integration remains a priority |

---

## Assertion Coverage Gap

46% of all ADR/DCL (45/98) have assertion runs. 53 SPECIFIED specs have no assertions — this is consistent with `DCL-SPEC-TEST-IMPL-TRIAD-COMPLETENESS-001` enforcement: all `verified` specs require assertions, but `specified` specs don't yet need them until they reach `verified` status. No action required unless specs are blocked at `specified` when they should be `verified`.

---

## Evidence

- **Database:** `E:\GT-KB\groundtruth.db` — `specifications` table, assertion runs via `scripts/record_adrs.py` and related tooling
- **Audit script:** `.tmp_compliance_audit.py` (ran during session, cleaned up)
- **Source insight:** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-09-19-03-arch-audit-findings.md`
- **Spec reclassification requirement:** `DCL-ADOPTER-SPEC-RECLASSIFICATION-001` (ENFORCED, 1/1 assertions passing)

---

## Open Decision Required from Owner

Should Prime Builder prioritize the P1 reclassification work (7 Agent Red application-layer specs) to clear the platform audit, or is any of the Agent Red application-layer ADR/DCL still in active use as governance artifacts for the GT-KB platform itself?

If the latter, reclassification is not the correct fix — those specs would need assertion re-scoping to Agent Red's codebase instead.

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
