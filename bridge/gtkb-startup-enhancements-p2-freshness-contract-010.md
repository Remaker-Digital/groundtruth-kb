GO

# Loyal Opposition Review - Startup Enhancements P2 Freshness Contract REVISED

Reviewed proposal: `bridge/gtkb-startup-enhancements-p2-freshness-contract-009.md`
Reviewer: Codex Loyal Opposition, harness A
Date: 2026-05-28 UTC
Verdict: GO

## Verdict

GO. The `-009` revision resolves the prior cache-freshness blocker by changing direction from "repair the startup-service cache" to "remove the service-side payload cache entirely." The proposal cites owner input for that direction reversal, keeps implementation scope within the GT-KB root, maps linked specifications to verification commands, and passes both mandatory bridge preflights.

## Prior Deliberations

Deliberation Archive search was run before review:

`python -m groundtruth_kb deliberations search "GTKB-STARTUP-ENHANCEMENTS startup freshness cache disable session_self_initialization" --limit 5`

Relevant records returned:

- `DELIB-2330` - prior Loyal Opposition GO for this startup-freshness thread.
- `DELIB-2333` - prior Loyal Opposition NO-GO for this startup-freshness thread.
- `DELIB-2167` - related startup dashboard reachability probe bridge thread, latest status VERIFIED.
- `DELIB-1536` - related session-start formalization NO-GO.
- `DELIB-1900` - earlier startup dashboard reachability probe thread, latest status NO-GO.

No prior deliberation found in this review reverses the owner-selected cache-disable direction. The relevant prior NO-GO is addressed by removing the stale-cache vector instead of extending the cache invalidation predicate.

## Review Findings

No blocking findings.

### Confirmation - Prior F1 is addressed by scope, not by implementation claim

Observation: The current checkout still contains `_startup_freshness_from_payload`, `_payload_staleness_reasons`, `_is_payload_fresh`, the cache-read short-circuit, and the cache write in `scripts/session_self_initialization.py`; this is consistent with a pre-implementation proposal. The `-009` proposal authorizes their removal and adds tests for ignoring a pre-populated cache file plus honoring `GTKB_STARTUP_REQUESTED_AT`.

Evidence:

- `scripts/session_self_initialization.py` currently contains `_startup_freshness_from_payload`, `_payload_staleness_reasons`, `_is_payload_fresh`, `startup_payload_cache_path`, and `payload_cache_path=`.
- `bridge/gtkb-startup-enhancements-p2-freshness-contract-009.md` scopes IP-1 through IP-6 to remove the cache path and add request-id regression coverage.
- `platform_tests/scripts/test_session_self_initialization.py` is an in-root authorized test target.

Impact: The implementation phase has a concrete, verifiable remediation path for the stale-request-id defect without requiring a second cache-consistency layer.

Recommended action: Prime Builder may implement the `-009` plan as written. The post-implementation report should explicitly show the cache helpers and cache-write path are absent, and should report the two new regression tests named in IP-5 and IP-6.

## Applicability Preflight

- packet_hash: `sha256:8393afcfd91be45b5476d46bbaffdec290f609fcb5f233d0255d73446e0436f1`
- bridge_document_name: `gtkb-startup-enhancements-p2-freshness-contract`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-startup-enhancements-p2-freshness-contract-009.md`
- operative_file: `bridge/gtkb-startup-enhancements-p2-freshness-contract-009.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:superseded, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-startup-enhancements-p2-freshness-contract`
- Operative file: `bridge\gtkb-startup-enhancements-p2-freshness-contract-009.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

## Verification Performed

- Read live `bridge/INDEX.md` before acting.
- Read the full thread chain for `gtkb-startup-enhancements-p2-freshness-contract`.
- Ran `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-startup-enhancements-p2-freshness-contract`.
- Ran `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-startup-enhancements-p2-freshness-contract`.
- Ran Deliberation Archive search for `GTKB-STARTUP-ENHANCEMENTS startup freshness cache disable session_self_initialization`.
- Inspected current source/test state with `rg` for cache helpers, cache paths, `GTKB_STARTUP_REQUESTED_AT`, and dispatcher request-id validation.

## Prime Builder Implementation Context

Objective: implement the cache-disable remediation in `scripts/session_self_initialization.py` and corresponding regression tests in `platform_tests/scripts/test_session_self_initialization.py`.

Preconditions and constraints: work stays within `target_paths`; bridge latest status is now GO; implementation must create a local implementation authorization packet before protected mutations.

Expected verification: run the exact pytest, ruff, bridge preflight, clause preflight, and dispatcher reproduction commands listed in the `-009` proposal. The post-implementation report should include observed command results and explicit evidence that the service no longer returns `docs/gtkb-dashboard/startup-service-payload.json` as a cache hit.
