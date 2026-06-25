ADVISORY

# gtkb-run-with-status-worker-lifetime-timeout — Auto-dispatch stale-entry advisory

bridge_kind: governance_advisory
Document: gtkb-run-with-status-worker-lifetime-timeout
Version: 005
Author: Loyal Opposition (harness D / ollama)
Date: 2026-06-25 UTC
Responds to: auto-dispatch selection of bridge/gtkb-run-with-status-worker-lifetime-timeout-003.md

author_identity: Ollama Loyal Opposition
author_harness_id: D
author_session_context_id: 2026-06-25T02-08-03Z-loyal-opposition-D-42bb52
author_model: kimi-k2.7-code:cloud
author_model_version: cloud
author_model_configuration: Ollama harness shim; route kimi-k2-7-code-cloud; skill bridge-review; resolved role loyal-opposition

---

## Source

Auto-dispatch selected `bridge/gtkb-run-with-status-worker-lifetime-timeout-003.md` (NEW post-implementation report, WI-4806) for Loyal Opposition review.

## Claim

This harness (D / ollama) is resolved as `loyal-opposition`. A work-intent claim was acquired before drafting:

```
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py claim gtkb-run-with-status-worker-lifetime-timeout
```

Result:

```json
{
  "acquired_at": "2026-06-25T02:29:36Z",
  "acting_role": "loyal-opposition",
  "claim_kind": "draft",
  "extension_capped": false,
  "extensions_used": 0,
  "project_id": "PROJECT-GTKB-RELIABILITY-FIXES",
  "rowid": 23995,
  "session_id": "2026-06-25T02-08-03Z-loyal-opposition-D-42bb52",
  "thread_slug": "gtkb-run-with-status-worker-lifetime-timeout",
  "ttl_expires_at": "2026-06-25T02:39:36Z"
}
```

## Owner Decision Needed

No owner decision is required for the bridge content itself. The bridge thread is already closed by `bridge/gtkb-run-with-status-worker-lifetime-timeout-004.md` (VERIFIED). The only queue-management decision is whether the auto-dispatch system should remove or skip `-003` from the loyal-opposition work queue now that `-004` exists.

## Recommended Prime Action

None. The selected entry `-003` is stale because it is superseded by `-004 VERIFIED`. No new GO / NO-GO / VERIFIED verdict should be issued, and no implementation work should be performed on this thread by this harness.

## Classification Slot

- Category: stale-entry / queue hygiene
- Severity: low (audit-trail only; no implementation risk)
- Trigger: cross-harness auto-dispatch selected a NEW entry whose successor is already VERIFIED

## Detail: why the selected entry is no longer actionable

Before acting, the full versioned bridge chain was read:

- `bridge/gtkb-run-with-status-worker-lifetime-timeout-001.md` — prime proposal (NEW)
- `bridge/gtkb-run-with-status-worker-lifetime-timeout-002.md` — Loyal Opposition GO verdict (antigravity / harness C)
- `bridge/gtkb-run-with-status-worker-lifetime-timeout-003.md` — Prime Builder post-implementation report (NEW), responding to -002
- `bridge/gtkb-run-with-status-worker-lifetime-timeout-004.md` — Loyal Opposition VERIFIED verdict (antigravity / harness C), responding to -003

Per the GT-KB bridge protocol, "Latest VERIFIED entries are bridge closure for both roles and are not queue work; do not process them as actionable." Therefore `-003` is not actionable for this role.

## Applicability Preflight (advisory context)

Both required preflight scripts were run against the selected bridge id. Their outputs are included as advisory context only.

### bridge_applicability_preflight.py

```
## Applicability Preflight

- packet_hash: `sha256:5fb4fadd906e7089e60816f178b91e10109816fc5b572b27e582c4ca7e0bdc51`
- bridge_document_name: `gtkb-run-with-status-worker-lifetime-timeout`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-run-with-status-worker-lifetime-timeout-003.md`
- operative_file: `bridge/gtkb-run-with-status-worker-lifetime-timeout-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

### adr_dcl_clause_preflight.py

```
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-run-with-status-worker-lifetime-timeout`
- Operative file: `bridge\gtkb-run-with-status-worker-lifetime-timeout-004.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | may_apply | — | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

The clause preflight automatically selected `-004.md` as the operative file and passed with no blocking gaps, confirming the bridge is already closed.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
