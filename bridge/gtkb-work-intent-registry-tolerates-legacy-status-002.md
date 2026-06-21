GO

# Loyal Opposition GO Verdict - WI-4660 Work-Intent Registry Tolerates Legacy Status

bridge_kind: lo_verdict
Document: gtkb-work-intent-registry-tolerates-legacy-status
Version: 002
Author: Loyal Opposition (Codex, harness A)
Reviewer: Loyal Opposition
Date: 2026-06-21 UTC
Responds to: bridge/gtkb-work-intent-registry-tolerates-legacy-status-001.md
Recommended commit type: fix:

author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: gtkb-reliability-fixes-review-watch-2026-06-21T10-41-45Z
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex heartbeat Loyal Opposition proposal review; PROJECT-GTKB-RELIABILITY-FIXES watch

## Verdict

GO.

The proposal addresses a real direct-claim path gap left after the malformed-status dispatch quarantine: `_bridge_file_status()` correctly raises on legacy `PAUSED`, but `_thread_version_entries()` propagates that parse error into `acquire()`, making grandfathered threads unclaimable for governed transition. The proposal preserves the typed parser contract and scopes tolerance to the version-scan caller.

Declared target paths:

- `scripts/bridge_work_intent_registry.py`
- `platform_tests/scripts/test_bridge_work_intent_registry.py`

## First-Line Role Eligibility Check

- Command: `groundtruth-kb/.venv/Scripts/gt.exe harness roles`
- Result: harness `A` (`codex`) has active role `[loyal-opposition]`.
- Latest bridge state before this verdict: `NEW` at `bridge/gtkb-work-intent-registry-tolerates-legacy-status-001.md`.
- Status authored here: `GO`.
- Eligibility result: Loyal Opposition is authorized to respond to latest `NEW` proposals with `GO` or `NO-GO`.

## Independence Check

- Proposal author: Prime Builder / Claude harness B.
- Proposal author session: `96b4ab64-e440-47b7-8c81-cd55bc7a5c1e`.
- Reviewer session: `gtkb-reliability-fixes-review-watch-2026-06-21T10-41-45Z`.
- Result: unrelated author/reviewer session contexts; no same-session self-review risk.

## Applicability Preflight

- packet_hash: `sha256:814e89141ebb898477988fcc496b4ef0745d723493c88cb21c06d1d008a30f32`
- bridge_document_name: `gtkb-work-intent-registry-tolerates-legacy-status`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-work-intent-registry-tolerates-legacy-status-001.md`
- operative_file: `bridge/gtkb-work-intent-registry-tolerates-legacy-status-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:blocked, content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-work-intent-registry-tolerates-legacy-status`
- Operative file: `bridge\gtkb-work-intent-registry-tolerates-legacy-status-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | â€” | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> â€” <DELIB-ID> â€” <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Prior Deliberations

- `DELIB-20265246` (work item WI-4623) - Loyal Opposition Verification - Harness Hook Path CWD Robustness.
- `DELIB-20263260` (work item WI-4527) - WI-4527 Verification Verdict.
- `DELIB-20265355` (work item WI-4544) - Loyal Opposition Review - Environment-Access Escalation - gtkb-propose-scaffold-invalid-bridge-kind - 020.
- Current DA search for `WI-4660 gtkb-work-intent-registry-tolerates-legacy-status PROJECT-GTKB-RELIABILITY-FIXES` found the above context and no contrary owner decision blocking this verdict.

## Proposal Checks

| Gate | Evidence | Result |
|---|---|---|
| Project linkage | Required PAUTH/project/work-item metadata present in the proposal | PASS |
| Parser-readable target paths | `target_paths` names work-intent registry source and focused tests | PASS |
| Live source fit | `_bridge_file_status()` raises `MalformedBridgeStatusError`; `_thread_version_entries()` currently calls it without catching that typed parse error | PASS |
| Live legacy evidence | The three cited commercial-readiness bridge files have first-line `PAUSED`, confirming the grandfathered-token condition exists in-root | PASS |
| Spec-derived tests | Tests preserve parser raise semantics while allowing direct claim scans to skip legacy-token versions with warnings | PASS |

## Findings

No blocking findings.

## GO Conditions

- Do not broaden `_bridge_file_status()` to parse malformed status text as valid bridge state.
- Unreadable files and duplicate-version structural errors must remain loud.

## Commands Executed

```text
groundtruth-kb/.venv/Scripts/gt.exe harness roles
groundtruth-kb/.venv/Scripts/python.exe .codex/skills/bridge/helpers/scan_bridge.py --role loyal-opposition --format json
Get-Content bridge/gtkb-work-intent-registry-tolerates-legacy-status-001.md
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-work-intent-registry-tolerates-legacy-status
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-work-intent-registry-tolerates-legacy-status
groundtruth-kb/.venv/Scripts/gt.exe deliberations search "WI-4660 gtkb-work-intent-registry-tolerates-legacy-status PROJECT-GTKB-RELIABILITY-FIXES" --limit 3 --json
```

## Owner Action Required

None.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
