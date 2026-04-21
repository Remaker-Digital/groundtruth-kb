NEW

# F4 Sub-Track: SPEC-1833 /ready Cosmos-Failure Propagation + Route-Level Test

**Status:** NEW
**Author:** Prime Builder (Opus 4.7, in-session S302)
**Date:** 2026-04-18
**Parent bridge:** `bridge/commercial-readiness-spec-verification-003.md` REVISED-1
**Backlog Slot:** F4 sub-track 3 of 3
**Owner decision (2026-04-18):** "Fix impl: propagate Cosmos failure to `/ready=false` + route-level test. Concurrency requirement deferred (non-blocking)."

## Context

Codex `-002` F3 (on parent F4 bridge) found:
1. `/ready` awaits Cosmos check at `src/app/health.py:108` and stores unhealthy result at `:111`, but the only `result["status"] = "not_ready"` assignment is transport-related at `:126`. **No Cosmos-driven readiness failure propagation.**
2. `/ready` body is sequential, no `asyncio.gather` / `create_task`.
3. Existing tests in `tests/multi_tenant/test_cosmos_readiness.py` exercise `check_cosmos_ready()` directly, not the full `/ready` route behavior.

Owner decided (2026-04-18): fix the propagation issue + add route-level test. Concurrency deferred as non-blocking (spec requirement remains in text; implementation is a future enhancement).

## Proposed Scope

### §1 — Propagate Cosmos unhealthy to `ready=false` in `/ready` route

Modify `src/app/health.py` so that when the Cosmos check at line 108-111
returns unhealthy, the route:
1. Sets `result["status"] = "not_ready"` (same pattern as transport at :126).
2. Ensures `result["cosmos_db"]["status"] == "unhealthy"` is already in the
   response payload (likely already true; verify during impl).

### §2 — Route-level integration test

Add to `tests/multi_tenant/test_cosmos_readiness.py` (existing 5 tests) or
new file `tests/multi_tenant/test_ready_route_cosmos_failure.py`:

- `test_ready_returns_not_ready_when_cosmos_unhealthy` — mock Cosmos to fail; call `/ready`; assert HTTP 503 (or appropriate status code per `/ready` convention) AND body shows `status=not_ready` AND `cosmos_db.status=unhealthy`.
- `test_ready_returns_ok_when_cosmos_healthy` — mock Cosmos to succeed; call `/ready`; assert HTTP 200 AND body shows `cosmos_db.status=healthy`.

### §3 — Concurrency deferral documentation

Per owner decision, the spec requirement "Cosmos check runs concurrently with other readiness checks (not sequential)" remains in the spec text unchanged. This bridge does NOT implement concurrent execution. Add a NOTE in the spec description after verification:

```
NOTE (2026-04-18): Concurrency of readiness checks remains a tracked
requirement but is not implemented in the current /ready route. Future
enhancement may refactor to asyncio.gather(). Not blocking for
verification of primary behavior (Cosmos failure propagation).
```

Reviewed with owner — the partial verification is acceptable because the
primary user-facing behavior (failure propagation) is verified; concurrency
is a performance optimization, not a correctness gap.

### §4 — Promote SPEC-1833 to `verified`

After §1 + §2 + §3, `db.update_spec("SPEC-1833", status="verified",
changed_by="prime-s302", change_reason="...")` citing:
- Cosmos failure now propagates to `/ready=false` (§1 landed).
- Route-level tests added (§2, 2 new tests = 7 total).
- Concurrency requirement noted as deferred (§3, owner-approved).

### §5 — Archive DELIB per protocol

Full `insert_deliberation()` call with all required fields.

## Files Touched

| File | Change kind | Est. delta |
|---|---|---|
| `src/app/health.py` | Propagation fix for Cosmos unhealthy → `not_ready` | +~5 / -~2 lines |
| `tests/multi_tenant/test_cosmos_readiness.py` | 2 new route-level tests | +~80 / -0 lines |
| `groundtruth.db` | 1 spec version row (description NOTE + status→verified) + 1 DELIB row | (binary) |

**Total: 2 source/test files + KB mutation.**

## Non-Scope

- **Concurrent readiness check refactor** — owner-deferred as non-blocking performance work.
- **Sentinel document seeding** — spec §5-6 already implemented per existing `check_cosmos_ready()` logic; not touched here.
- **Cache behavior tests** — spec §4 (10-second cache) already covered in existing 5 tests; not re-tested.

## Verification Plan

```text
$ python -m pytest tests/multi_tenant/test_cosmos_readiness.py -q
# Expect: 7 passed (5 existing + 2 new route-level tests)

$ python -m pytest tests/app/ tests/multi_tenant/ -q --tb=short
# Expect: no regressions in health/lifecycle tests

# Post-apply spec status
$ python -c "...; print(db.get_spec('SPEC-1833')['status'])"
verified
```

## Implementation Sequence

1. Read `src/app/health.py:100-130` to understand current `/ready` structure.
2. Modify the Cosmos-check block to set `status=not_ready` on unhealthy.
3. Add 2 route-level tests (consider using existing FastAPI TestClient pattern).
4. Run scoped tests; confirm green.
5. Draft spec description addendum (concurrency NOTE).
6. Promote SPEC-1833 + archive DELIB.
7. Commit on `develop`: `feat(health): SPEC-1833 — propagate Cosmos unhealthy to /ready + route-level test`.
8. File post-impl report.
9. On VERIFIED: push to `origin/develop`.

## Prior Deliberations

- Codex `-002` F3 on parent F4 bridge.
- Owner AskUserQuestion decision 2026-04-18.

## Owner Decisions Required

None (captured in parent bridge REVISED-1).

## Requested Verdict

**GO** to implement §1 + §2 + §3 + §4 + §5, or **NO-GO** with specific findings.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
