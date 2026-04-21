---
name: arch-audit
description: "Run horizontal architecture compliance audit. Classifies all ADR/DCL as ENFORCED/SPECIFIED/UNASSESSED grouped by family. Optionally records as KB document."
argument-hint: "[--record]"
allowed-tools: Bash, Read
license: "Proprietary - Remaker Digital"
compatibility:
  - claude-code >= 1.0
metadata:
  project: agent-red-customer-experience
  category: governance
  governance: GOV-20
---

# Architecture Compliance Audit

Run all ADR/DCL assertions and produce a family-grouped compliance matrix.

**Arguments:**
- `--record`: Record audit results as a DOC in KB (Prime only)

## Behavior

1. Run `/kb-assert --dry-run` to get assertion results for all ADR/DCL specs
2. Classify each artifact:
   - **ENFORCED**: implemented/verified + assertions passing
   - **SPECIFIED**: specified status + assertions exist
   - **FAILING**: implemented but assertions failing
   - **UNASSESSED**: no assertions or not yet implemented
3. Group by family:
   - Transport / Container / Routing
   - Zero-Knowledge / Tenant Isolation
   - MCP / Plugin / Binding
   - KB / Governance Infrastructure
   - RBAC
   - Test / Contract Enforcement
4. Print compliance matrix
5. If `--record`: create DOC in KB with audit results

## Output Format

```
=== HORIZONTAL COMPLIANCE AUDIT ===

--- Transport / Container / Routing ---
  ADR-001      ENFORCED     (implemented)
  ADR-002      ENFORCED     (implemented)
  ...

Summary: N ENFORCED, N SPECIFIED, N FAILING, N UNASSESSED
```

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
