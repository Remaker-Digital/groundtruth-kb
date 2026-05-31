# Security Policy — GroundTruth-KB Platform

This is the platform-level security policy entry point for GroundTruth-KB.

## Reporting a Vulnerability

To report a vulnerability in the GroundTruth-KB platform itself (governance contract, role enforcement, approval-packet evidence layer, secrets scanning, doctor checks, CLI surfaces), email **security@remakerdigital.com**.

To report a vulnerability in a specific application managed by GT-KB, see the per-application security policy:

- **Agent Red Customer Experience:** [`applications/Agent_Red/SECURITY.md`](applications/Agent_Red/SECURITY.md)

## Platform Security Practices

The GroundTruth-KB platform enforces:
- Pre-commit secrets scanning via `gt secrets scan --staged --fail-on verified-provider`.
- Narrative-artifact approval-packet evidence layer via `scripts/check_narrative_artifact_evidence.py` (universal `.githooks/pre-commit` floor).
- Append-only versioning of canonical artifacts in MemBase.
- Role-based authority via `harness-state/role-assignments.json` durable role map.
- Bridge-protocol GO/NO-GO/VERIFIED audit trail for governance-sensitive changes.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
