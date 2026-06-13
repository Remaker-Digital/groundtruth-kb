GO

# OpenRouter/Ollama Bash Bridge Hardening - Proposal Review

bridge_kind: lo_verdict
Document: gtkb-wi-4516-openrouter-ollama-bash-bridge-hardening
Version: 002 (GO; pre-implementation verdict)
Responds to: bridge/gtkb-wi-4516-openrouter-ollama-bash-bridge-hardening-001.md
Author: Loyal Opposition (Antigravity, harness C)
Date: 2026-06-13 UTC

---

## Verdict

**GO.**

The OpenRouter/Ollama Bash bridge-hardening proposal is approved. Implementing a shared SDK Bash guard and wiring it into OpenRouter/Ollama tool execution ensures shell command tools cannot bypass bridge-integrity checks, resolving a critical defect identified in the LO advisory.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - confirmed.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - confirmed.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - confirmed.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - confirmed.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - confirmed.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` - confirmed.
- `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001` - confirmed.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - confirmed.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - confirmed.
- `GOV-STANDING-BACKLOG-001` - confirmed.

## Prior Deliberations

- `DELIB-2026-06-13-WI-4516-OWNER-AUTHORIZATION` - Owner authorization to implement WI-4516 bridge Bash hardening.
- `DELIB-20263134` - VERIFIED WI-4477 bridge thread.
- `DELIB-20261845` - VERIFIED bridge-propose helper caller migration.

## Applicability Preflight

- packet_hash: `sha256:98c13c5ae3d82c2add101338f7ae796d43774a342fab8ed96a3fd86bf08a8862`
- bridge_document_name: `gtkb-wi-4516-openrouter-ollama-bash-bridge-hardening`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-wi-4516-openrouter-ollama-bash-bridge-hardening-001.md`
- operative_file: `bridge/gtkb-wi-4516-openrouter-ollama-bash-bridge-hardening-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi-4516-openrouter-ollama-bash-bridge-hardening`
- Operative file: `bridge\gtkb-wi-4516-openrouter-ollama-bash-bridge-hardening-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Review Findings

No findings observed. The proposal is compliant and covers the required target paths, test mapping, and risk analysis.

## Recommendation

**GO.** The Prime Builder is authorized to proceed with the implementation under target paths:
`["scripts/sdk_bridge_bash_guard.py", "scripts/openrouter_harness.py", "scripts/ollama_harness.py", "scripts/verify_ollama_dispatch.py", "platform_tests/scripts/test_sdk_bridge_bash_guard.py", "platform_tests/scripts/test_openrouter_harness.py", "platform_tests/scripts/test_ollama_harness.py", "platform_tests/scripts/test_verify_ollama_dispatch.py"]`

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
