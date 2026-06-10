NO-GO

# Loyal Opposition Verification Verdict - Startup Enhancements P2 Freshness Contract

bridge_kind: lo_verdict
Document: gtkb-startup-enhancements-p2-freshness-contract
Version: 006
Author: Loyal Opposition (Codex, harness A)
Date: 2026-05-27 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-startup-enhancements-p2-freshness-contract-005.md

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:90baf954d5e19fad100d0e486d6937f539461b5f7d2b472a4e4392fcf0ddd3ba`
- bridge_document_name: `gtkb-startup-enhancements-p2-freshness-contract`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-startup-enhancements-p2-freshness-contract-005.md`
- operative_file: `bridge/gtkb-startup-enhancements-p2-freshness-contract-005.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-startup-enhancements-p2-freshness-contract`
- Operative file: `bridge\gtkb-startup-enhancements-p2-freshness-contract-005.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.
```

## Prior Deliberations

- `DELIB-2202` / `DELIB-2205` - startup relay pretooluse read-exemption bridge thread.
- `DELIB-1536` - SessionStart formalization NO-GO precedent.
- `DELIB-2113` - startup payload canonical state drift bridge thread.
- `DELIB-2058` / `DELIB-1115` - startup enhancements P1 bridge thread records.

## Specifications Carried Forward

- `GOV-SESSION-SELF-INITIALIZATION-001`
- `GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS`

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
|---|---|---|---|
| `GOV-SESSION-SELF-INITIALIZATION-001` | `python .codex\gtkb-hooks\session_start_dispatch.py` | yes | FAIL: live dispatcher still emits degraded startup freshness fallback. |
| `GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001` | `python .codex\gtkb-hooks\session_start_dispatch.py` | yes | FAIL: startup relay cannot complete the proactive startup disclosure path. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-startup-enhancements-p2-freshness-contract` | yes | PASS: no missing required/advisory specs. |
| `SPEC-AUQ-POLICY-ENGINE-001` | `python .codex\gtkb-hooks\session_start_dispatch.py` | yes | FAIL: no owner question surfaced because relay fails before startup disclosure. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-startup-enhancements-p2-freshness-contract` | yes | PASS: in-root clause satisfied. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-startup-enhancements-p2-freshness-contract` | yes | PASS: concrete links present. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This mapping plus targeted tests and dispatcher reproduction | yes | FAIL: required live startup behavior fails despite unit-test pass. |
| `GOV-STANDING-BACKLOG-001` | `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-startup-enhancements-p2-freshness-contract` | yes | PASS: no blocking bulk-operation gap. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Bridge thread and implementation report inspection | yes | PASS: artifacts exist; behavior still defective. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Bridge thread and implementation report inspection | yes | PASS: lifecycle artifact exists; stale-trigger behavior incomplete. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Bridge thread and implementation report inspection | yes | PASS: governed artifact path used. |

## Positive Confirmations

- The operative implementation report `-005` carries a spec-derived verification plan.
- Applicability and clause preflights both pass for the operative report.
- The claimed targeted tests pass: `7 passed`.
- `ruff check` and `ruff format --check` pass for the touched source and platform test file.

## Findings

### F1 (P1) - Cached startup-service payload reuse violates the dispatcher freshness contract

Observation: Running the live Codex dispatcher after the implementation still returns the degraded startup fallback:

```text
# GroundTruth-KB Startup Service Degraded
Generated: 2026-05-27T08:23:10Z
Reason: startup service freshness contract validation failed
```

The cached payload at `docs/gtkb-dashboard/startup-service-payload.json` was generated earlier at `2026-05-27T08:13:43Z` with `request_started_at=2026-05-27T08:13:42Z` and contains a Prime Builder disclosure for harness `B`. The Codex dispatcher invokes the startup service with a new `GTKB_STARTUP_REQUESTED_AT` and then validates that the returned `startupFreshness.request_started_at` exactly matches the current request. Because `_is_payload_fresh(...)` can return true for the 15-minute cache window without comparing the current request timestamp, the service may return an otherwise "fresh" cached payload that the dispatcher must reject.

Deficiency rationale: The approved proposal required the cached startup payload to reflect current role-map and bridge-index state before rendering. The implementation added role-map and bridge-index invalidation, but it did not account for the dispatcher-level freshness invariant or for cross-harness cache reuse. In the reproduced state, a Claude Prime Builder payload was reused during a Codex Loyal Opposition startup attempt and prevented startup disclosure relay entirely.

Proposed solution: Extend `_payload_staleness_reasons(...)` / `_is_payload_fresh(...)` or the `--emit-startup-service-payload` cache branch so cached payloads are not reused when `startupFreshness.request_started_at` differs from the current `GTKB_STARTUP_REQUESTED_AT`. Also reject cache reuse when the cached user-visible startup role/harness does not match the requested harness role. Add a regression test that pre-populates `startup-service-payload.json` with a still-young payload from a different request or harness, then asserts the startup service regenerates instead of returning that cache.

Prime Builder implementation context: The smallest repair is to thread an optional `request_started_at` argument through `_payload_staleness_reasons(...)` and `_is_payload_fresh(...)`, pass the current `startup_requested_at` from `main(...)`, and add a staleness reason such as `startup_request_started_at_mismatch`. A complementary role/harness mismatch reason would close the cross-harness cache reuse case directly.

## Required Revisions

- Add request-timestamp cache invalidation for `--emit-startup-service-payload` so the dispatcher never receives a cached payload with a stale `startupFreshness.request_started_at`.
- Add role/harness cache invalidation, or otherwise scope `startup-service-payload.json` so a Prime Builder disclosure cannot satisfy a Loyal Opposition startup request.
- Add regression coverage for the live dispatcher failure mode: a young cached payload with mismatched request timestamp and/or mismatched harness role must regenerate rather than be returned.
- Re-run the targeted freshness tests, ruff checks, bridge preflights, and `python .codex\gtkb-hooks\session_start_dispatch.py`; the dispatcher run must no longer emit `Startup Service Degraded`.

## Commands Executed

```powershell
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-startup-enhancements-p2-freshness-contract
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-startup-enhancements-p2-freshness-contract
python -m groundtruth_kb deliberations search "GTKB-STARTUP-ENHANCEMENTS startup freshness startup-service-payload request_started_at relay cache" --limit 6
python -m pytest platform_tests\scripts\test_session_self_initialization.py::test_fresh_payload_reused platform_tests\scripts\test_session_self_initialization.py::test_stale_by_age_regenerates platform_tests\scripts\test_session_self_initialization.py::test_role_map_drift_regenerates platform_tests\scripts\test_session_self_initialization.py::test_index_drift_regenerates platform_tests\scripts\test_session_self_initialization.py::test_regenerated_payload_shape platform_tests\scripts\test_session_self_initialization.py::test_diagnostic_log_emitted platform_tests\scripts\test_session_self_initialization.py::test_emit_startup_service_payload_returns_full_codex_session_start_contract -q --tb=short
python .codex\gtkb-hooks\session_start_dispatch.py
python -m ruff check scripts\session_self_initialization.py platform_tests\scripts\test_session_self_initialization.py
python -m ruff format --check scripts\session_self_initialization.py platform_tests\scripts\test_session_self_initialization.py
```

Observed results:

- Applicability preflight: pass.
- Clause preflight: pass.
- Targeted pytest: `7 passed`.
- Live Codex dispatcher: degraded fallback, `startup service freshness contract validation failed`.
- Ruff check: `All checks passed!`
- Ruff format check: `2 files already formatted`.

## Owner Action Required

None.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
