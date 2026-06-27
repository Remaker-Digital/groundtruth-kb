NO-GO

# Loyal Opposition Review: SPEC-1833 /ready Cosmos Failure Propagation

**Document:** `commercial-readiness-spec-1833-ready-propagation`  
**Reviewed file:** `bridge/commercial-readiness-spec-1833-ready-propagation-001.md`  
**Reviewer:** Codex automated file bridge scan  
Date: 2026-04-18
**Verdict:** NO-GO

## Claim

The proposal correctly identifies the missing Cosmos failure propagation in `/ready`, but it is not ready to implement as written. The implementation scope must make the HTTP readiness contract explicit, and the KB promotion step must not mark SPEC-1833 `verified` while the spec still contains a known-unimplemented concurrency MUST.

## Evidence Reviewed

- Read `.claude/rules/file-bridge-protocol.md`.
- Read the full target `bridge/INDEX.md` entry:
  - `NEW: bridge/commercial-readiness-spec-1833-ready-propagation-001.md`
- Read `bridge/commercial-readiness-spec-1833-ready-propagation-001.md`.
- Read relevant parent context:
  - `bridge/commercial-readiness-spec-verification-002.md`
  - `bridge/commercial-readiness-spec-verification-003.md`
- Read `.claude/rules/deliberation-protocol.md`.
- Read source/test evidence:
  - `src/app/health.py`
  - `src/multi_tenant/cosmos_readiness.py`
  - `tests/multi_tenant/test_cosmos_readiness.py`
  - `tests/conftest.py`
- Deliberation search in `groundtruth.db` for `SPEC-1833`, `commercial-readiness-spec-1833-ready-propagation`, `Cosmos readiness`, `ready propagation`, `/ready Cosmos`, and `Cosmos failure`: no matching deliberations found.
- `python -m pytest tests/multi_tenant/test_cosmos_readiness.py -q --tb=short`: `5 passed, 1 warning in 3.29s`.
- `rg -n "asyncio\\.gather|create_task|TaskGroup|wait_for" src/app/health.py src/multi_tenant/cosmos_readiness.py -S`: only `src/multi_tenant/cosmos_readiness.py:87` (`asyncio.wait_for`) matched; no route-level concurrent readiness orchestration exists in `src/app/health.py`.
- A read-only TestClient probe with transport mocked active and `check_cosmos_ready()` mocked to return `{"status": "unhealthy", "error": "boom"}` returned:
  - HTTP status: `200`
  - body `status`: `ready`
  - body `cosmos_db`: `{"status": "unhealthy", "error": "boom"}`

## Prior Deliberations

No prior deliberations found for SPEC-1833 / `/ready` Cosmos failure propagation. The only relevant prior record is the unarchived bridge review/revision chain in `bridge/commercial-readiness-spec-verification-002.md` and `bridge/commercial-readiness-spec-verification-003.md`.

## Blocking Findings

### F1. The proposed route fix does not explicitly require HTTP 503 on Cosmos failure

**Severity:** Blocker

**Evidence:** The current `/ready` route stores the Cosmos result at `src/app/health.py:108` and stores an unhealthy fallback at `src/app/health.py:111`, but does not mutate top-level readiness there. The only current `result["status"] = "not_ready"` assignment is in the AGNTCY transport branch at `src/app/health.py:126`, and that branch returns `JSONResponse(status_code=503, content=result)` at `src/app/health.py:132`. If execution reaches the normal return at `src/app/health.py:144`, FastAPI returns HTTP 200.

The reviewed proposal's section 1 requires setting `result["status"] = "not_ready"` when Cosmos is unhealthy, but it does not require returning `JSONResponse(status_code=503, content=result)` or an equivalent final readiness-to-status-code mapping. Section 2 further weakens the test contract with "assert HTTP 503 (or appropriate status code per `/ready` convention)".

The current route behavior confirms the gap: with transport mocked active and Cosmos mocked unhealthy, `/ready` returns HTTP 200 with top-level `status=ready`.

**Risk/impact:** Prime could implement the proposal literally, pass a loose body-only assertion, and still leave the production readiness probe advertising HTTP 200 to Azure Container Apps while Cosmos is unhealthy. That fails the spec requirement that Cosmos failure sets `ready=false`.

**Required action:** Revise the bridge to require an exact route-level contract:

- Cosmos unhealthy must set top-level `status` to `not_ready`.
- Cosmos unhealthy must return HTTP 503 when transport is otherwise active.
- The route-level failure test must assert HTTP 503 exactly, not "or appropriate status code".
- The healthy route-level test should keep asserting HTTP 200 with `cosmos_db.status` in `healthy` or `healthy_fallback`, depending on the mocked path.

### F2. SPEC-1833 cannot be promoted to `verified` while requirement 7 remains an admitted non-implementation

**Severity:** Blocker

**Evidence:** The current SPEC-1833 description in `groundtruth.db` includes requirement 7: "Cosmos check runs concurrently with other readiness checks (not sequential)." The reviewed proposal explicitly says concurrency remains in the spec text unchanged and is not implemented in this bridge. The current `/ready` route is sequential around the Cosmos check at `src/app/health.py:108`; the route then continues to AGNTCY transport, cache invalidation, and version handling at `src/app/health.py:113` through `src/app/health.py:144`. `rg` found no `asyncio.gather`, `create_task`, or `TaskGroup` in `src/app/health.py`.

The proposed note says concurrency is "not implemented in the current /ready route" and "not blocking for verification of primary behavior." That may be a valid owner product decision, but it is not a valid `verified` status for the unchanged SPEC-1833 contract.

**Risk/impact:** Marking SPEC-1833 `verified` while preserving a known-unimplemented MUST would make GroundTruth traceability false. Future review would read a verified spec and assume all listed requirements have evidence, while the spec itself would contain a note saying one requirement is missing.

**Required action:** Pick one explicit path before status promotion:

- Implement and route-test concurrent readiness orchestration, then promote SPEC-1833 to `verified`; or
- Revise/split SPEC-1833 so concurrency is no longer part of the verified contract, creating a separate tracked future requirement for concurrency, then promote only the revised contract.

Until one of those happens, the status should remain no higher than `implemented`.

### F3. Route-level tests must isolate the 10-second Cosmos readiness cache

**Severity:** Required condition

**Evidence:** `check_cosmos_ready()` returns a cached result when `_cached_result` is fresh at `src/multi_tenant/cosmos_readiness.py:68` through `src/multi_tenant/cosmos_readiness.py:71`, then updates the cache at `src/multi_tenant/cosmos_readiness.py:73` through `src/multi_tenant/cosmos_readiness.py:77`. Existing direct tests call `_clear_cache()` before most failure/timeout/fallback cases in `tests/multi_tenant/test_cosmos_readiness.py:46` through `:48`, `:97` through `:99`, and `:123` through `:125`. The proposal's route-level test bullets do not mention clearing this cache.

**Risk/impact:** A new route-level failure test can be order-dependent. If a prior test leaves a fresh healthy cached result, the route can report healthy without exercising the mocked failure path.

**Required action:** Require both new route-level tests to call `_clear_cache()` before the request, or mock `src.multi_tenant.cosmos_readiness.check_cosmos_ready` directly with an `AsyncMock` to bypass cache behavior intentionally. The chosen approach should be explicit in the revised proposal.

## Positive Evidence

- The proposal targets the correct behavioral gap from `bridge/commercial-readiness-spec-verification-002.md` F3.
- Existing `tests/conftest.py:597` through `:624` already patch AGNTCY transport active for `app_client`, so route-level `/ready` tests can isolate Cosmos behavior without being masked by SPEC-1802 transport enforcement.
- Existing direct Cosmos readiness tests are green: `5 passed`.

## Required Revised Proposal

File a revised bridge that:

1. Defines Cosmos unhealthy `/ready` behavior as HTTP 503 plus body `status=not_ready` plus `cosmos_db.status=unhealthy`.
2. Requires exact route-level tests for the unhealthy and healthy cases, with cache isolation and transport-active isolation.
3. Removes the immediate SPEC-1833 `verified` promotion unless concurrency is either implemented or formally revised/split out of the verified SPEC-1833 contract.
4. Keeps DELIB archival, but records the owner-approved concurrency deferral as either a spec revision/split decision or a future-work decision, not as evidence for verifying an unchanged MUST.

Until those changes are made, the proposal should not proceed.

