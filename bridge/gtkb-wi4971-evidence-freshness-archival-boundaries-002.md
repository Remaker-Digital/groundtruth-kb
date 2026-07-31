GO

# WI-4971 - Evidence Freshness and Archival Boundaries — Loyal Opposition Review

bridge_kind: lo_verdict
Document: gtkb-wi4971-evidence-freshness-archival-boundaries
Version: 002
Author: Loyal Opposition (Ollama D)
Date: 2026-07-06T01:22:14Z
Reviewing: bridge/gtkb-wi4971-evidence-freshness-archival-boundaries-001.md (Prime Builder Codex A)

author_identity: Ollama Loyal Opposition
author_harness_id: D
author_session_context_id: 2026-07-06T01-22-10Z-loyal-opposition-D-08c96f
author_model: deepseek-v4-pro:cloud
author_model_version: cloud
author_model_configuration: Ollama harness shim; route deepseek-v4-pro-cloud; skill bridge-review; guarded tools Read, Write, Edit, Grep, Glob, Bash

---

## Verdict: GO

The proposal for WI-4971 (Evidence Freshness and Archival Boundaries) is substantively sound, well-linked to governing specifications, and supported by clean preflight results. The Loyal Opposition recommends GO.

## Applicability Preflight

```
## Applicability Preflight

- packet_hash: `sha256:6bc2f38a11ed1198c76b54585271589f651d02830347aa12507418cd6c378a7a`
- bridge_document_name: `gtkb-wi4971-evidence-freshness-archival-boundaries`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi4971-evidence-freshness-archival-boundaries-001.md`
- operative_file: `bridge/gtkb-wi4971-evidence-freshness-archival-boundaries-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## ADR/DCL Clause Preflight

```
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi4971-evidence-freshness-archival-boundaries`
- Operative file: `bridge\gtkb-wi4971-evidence-freshness-archival-boundaries-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |
```

## Review Analysis

### Strengths

1. **Clear scope**: The proposal defines a crisp boundary between compact current-state references (default for routine sessions) and full archived evidence (explicit opt-in for verification/dispute). This directly addresses the Phase 3 gap 09 mandate.

2. **Spec linkage is thorough**: All blocking specs are cited and matched. The proposal links to `SPEC-INTAKE-46594e`, `DCL-SESSION-STARTUP-TOKEN-BUDGET-001`, and `GOV-SESSION-SELF-INITIALIZATION-001` — the exact cross-cutting concerns that freshness/archival boundaries must protect.

3. **Verification plan is spec-derived**: Each requirement maps to concrete test files and verification commands. The plan covers compact-default reads, explicit archive opt-in, stable citation, and startup token budget protection.

4. **Target paths are enumerated**: All 12 target files are listed, covering both source (`cli_session_handoff.py`, `reconciliation.py`, `harness_projection.py`) and test paths.

5. **Risk/rollback is addressed**: The proposal acknowledges the dual risk (stale summaries vs. excessive archive loading) and ties rollback to test regression.

### Observations (Non-Blocking)

1. **B1-B7 blockers are referenced but not enumerated**: The proposal cites "session/activity envelope sharding blockers B1-B7" as evidence the WI must link. The implementation should enumerate these concretely in its post-implementation report so the VERIFIED reviewer can confirm each blocker is addressed. This is a note for the Prime Builder, not a rejection criterion.

2. **Test files may not exist yet**: Several test files in the verification plan (e.g., `test_bridge_citation_freshness_preflight.py`, `test_wrap_capture_transcript.py`) are also in the target_paths list, meaning they are part of the implementation. The post-implementation VERIFIED review will confirm they exist and pass.

3. **Dispatcher health note**: The dispatch health check shows a stale watchdog heartbeat (`complex_lifecycle: WARN`). This is a dispatcher infrastructure note and does not affect the proposal's substantive quality.

### Preflight Summary

| Check | Result |
|---|---|
| Applicability Preflight | PASS — all required specs cited, no missing specs |
| ADR/DCL Clause Preflight (Slice 2) | PASS — all must_apply clauses have evidence, zero blocking gaps |
| Bridge file chain | Canonical — 001 is the sole file for this slug |

## Prior Deliberations

- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` — owner approved Batch C continuation.
- `DELIB-202665197` and `bridge/harness-equivalence-phase-3-umbrella-002.md` — Phase 3 child-gap authority.
- Session/activity envelope sharding blockers B1-B7 — evidence set this WI must link.
- `TEST-11271` — manual test linkage for WI-4971 under `SPEC-INTAKE-46594e`.

## Conclusion

The proposal is well-formed, spec-compliant, and addresses a real Phase 3 gap. Both mandatory preflights pass with zero blocking gaps. The Loyal Opposition issues **GO**.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
