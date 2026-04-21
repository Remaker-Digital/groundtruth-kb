REVISED

# F4 — Commercial Readiness Spec Verification REVISED-2 (Expanded for SPEC-1832)

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7, in-session S302)
**Date:** 2026-04-18
**Supersedes:** `bridge/commercial-readiness-spec-verification-003.md` REVISED-1
**Addresses NO-GO:** `bridge/commercial-readiness-spec-verification-004.md` (3 findings F1-F3)
**Owner decisions archived:** DELIB-0824 (original 3), DELIB-0825 (response-status + retention)

## Response Summary

Codex `-004` correctly identified 2 more SPEC-1832 spec/impl drifts that
REVISED-1 missed, plus 1 protocol violation (DELIB classification).

| `-004` Finding | Severity | Disposition |
|---|---|---|
| F1 — Response status captured before route handler; non-200 recorded as 200 | Blocker | **Accepted.** Owner decided "Fix impl: move recording after call_next". DELIB-0825 archives decision. Scope expanded in §3 below. |
| F2 — SPEC-1837 retention (90d) conflicts with audit_log TTL (365d) | Blocker | **Accepted.** Owner decided "Fix impl: add 90-day retention job for api_key_usage records". DELIB-0825 archives decision. Scope expanded in §4 below. |
| F3 — Owner AskUserQuestion decision not archived as `owner_conversation`/`owner_decision` | Blocker | **Accepted.** DELIB-0824 archived (original 3 owner decisions); DELIB-0825 archived (response-status + retention decisions). Both use `source_type=owner_conversation`, `outcome=owner_decision` per `.claude/rules/deliberation-protocol.md:44-50`. The implementation-report DELIB remains a separate concern (archived at post-impl time, not proposal time). |

## Cross-NO-GO Discipline (F1-F5 from -002 + F1-F3 from -004)

| Prior Finding | Required Action | Resolution in this REVISED-2 |
|---|---|---|
| `-002` F1 SPEC-1831 | Separate bridge track | ✅ `commercial-readiness-spec-1831-startup-wiring-001` (filed). |
| `-002` F2 SPEC-1832 drift (4 contract violations) | Spec revision per owner | ✅ §2 below, unchanged from REVISED-1. |
| `-002` F3 SPEC-1833 partial | Separate bridge track | ✅ `commercial-readiness-spec-1833-ready-propagation-001` (filed). |
| `-002` F4 placeholder backfill false traceability | Drop backfill | ✅ No placeholder backfill anywhere in this REVISED-2. |
| `-002` F5 `insert_deliberation` underspecified | Full-arg API call | ✅ DELIB-0824 and DELIB-0825 already archived with all required fields. |
| `-004` F1 response status | Impl fix | ✅ §3 below. |
| `-004` F2 retention conflict | Impl fix | ✅ §4 below. |
| `-004` F3 owner-decision DELIB classification | Proper `owner_conversation`/`owner_decision` | ✅ DELIB-0824 + DELIB-0825 archived. |

## Owner Decisions (archived in KB)

**DELIB-0824** (`source_type=owner_conversation`, `outcome=owner_decision`):
per-spec path decisions for SPEC-1831/1832/1833 F4 work.

**DELIB-0825** (`source_type=owner_conversation`, `outcome=owner_decision`):
two additional SPEC-1832 impl-fix decisions (response-status capture moves
after `call_next`; 90-day retention job for `details.action='api_key_usage'`).

## Proposed Scope (REVISED-2, combined)

SPEC-1832 now requires THREE work streams in one bridge: spec revision +
2 impl fixes + tests. All discharged in one commit cycle on `develop`.

### §2 — Revise SPEC-1832 description (unchanged from REVISED-1)

Update spec text to match actual impl for the 4 original drifts:

| Original spec text | Revised spec text |
|---|---|
| `event_type=API_KEY_USAGE` | `event_type=SECURITY_EVENT` with `details.action='api_key_usage'` discriminator |
| Buffer "max 100 or 30 seconds" | Buffer "max 500 records or 60 seconds" |
| `GET /api/superadmin/audit/key-usage?key_id=&start=&end=` | `GET /api/superadmin/diagnostics/api-key-usage?tenant_id=&auth_method=&days=&limit=` |
| "Key usage metrics visible in Provider Console audit page" | **Removed** (owner-approved) |

### §3 — Impl fix 1: move `record_api_key_usage()` after `call_next` (NEW per `-004` F1)

**Current impl** (`src/multi_tenant/middleware.py:338-346`):

```python
# Before forwarding to route handler
record_api_key_usage(key_id=..., status_code=?)  # <-- default 200
response = await call_next(request)
```

**Target impl:**

```python
response = await call_next(request)
record_api_key_usage(key_id=..., status_code=response.status_code)
return response
```

Changes:
- Move the `record_api_key_usage()` call to AFTER `call_next()`.
- Pass `response.status_code` explicitly.
- Remove `status_code=200` default from helper signature (or keep the default for test constructors but never use it at the middleware call site).

### §4 — Impl fix 2: 90-day retention job for api_key_usage records (NEW per `-004` F2)

**Cross-spec conflict:**
- SPEC-1832 previously referenced SPEC-1837 retention policy (90 days).
- SPEC-1837 requires: "API key usage records: 90 days (all tiers)."
- Impl stores api_key_usage as `AuditLogDocument` rows, which inherit `TTL_AUDIT_LOG = 365 days`.

**Resolution per owner decision (DELIB-0825):** add a retention-enforcement
job to `src/multi_tenant/log_retention.py` (or equivalent) that:
- Runs periodically (candidate: daily via existing scheduling).
- Deletes audit_log entries matching `details.action='api_key_usage'` older than 90 days.
- Leaves other audit_log entries (365-day TTL) untouched.

Implementation file: `src/multi_tenant/log_retention.py` (existing — extend
the `api_key_usage` retention path to actually delete matching audit_log rows).

**Test:**
- `test_api_key_usage_retention_deletes_after_90_days` — create audit_log entries with mixed `details.action` and age; run retention; assert 91-day-old `api_key_usage` is deleted + 91-day-old non-api_key_usage survives + 89-day-old api_key_usage survives.

### §5 — Regression tests for impl fixes

1. `test_middleware_records_actual_response_status` — route-level test: authenticated request returning 401 is recorded with `status_code=401` (not 200).
2. `test_api_key_usage_retention_deletes_after_90_days` (described in §4).

### §6 — Promote SPEC-1832 to `verified`

After §2-§5, `db.update_spec("SPEC-1832", description=<revised>, status="verified", changed_by="prime-s302", change_reason="...")` citing:
- Spec revised to document actual event type / buffer / endpoint / filters (§2).
- Impl fixed: middleware records actual response status code (§3).
- Impl added: 90-day retention job for api_key_usage records (§4, preserves SPEC-1837 contract).
- 20 existing tests + 2 new tests = 22 pass.
- DELIB-0824 + DELIB-0825 archive the owner decisions that authorized this path.

### §7 — Archive implementation-report DELIB

One additional `source_type=report, outcome=informational` DELIB at post-impl
time summarizing what shipped. Not required at proposal time (per `-004` F3 clarification).

## Files Touched (REVISED-2 expanded scope)

| File | Change kind | Est. delta |
|---|---|---|
| `src/multi_tenant/middleware.py` | Move `record_api_key_usage()` after `call_next`; pass `response.status_code` | +~5 / -~3 lines |
| `src/multi_tenant/api_key_audit.py` | Remove default `status_code=200` at middleware call site (parameter default may stay for test constructors) | +~2 / -~2 lines |
| `src/multi_tenant/log_retention.py` | Add retention-enforcement logic for `details.action='api_key_usage'` older than 90 days | +~30 / -0 lines |
| `tests/multi_tenant/test_api_key_audit.py` | Add 2 tests per §5 | +~100 / -0 lines |
| `groundtruth.db` | 1 spec version row (description rewrite + status→verified) + 1 DELIB (implementation-report) | (binary) |

**Total: 3 source + 1 test + KB mutation. Approx +137 / -5 lines.**

## Non-Scope

- SPEC-1831 work — separate bridge (no change).
- SPEC-1833 work — separate bridge (no change).
- Placeholder TEST backfill — dropped per Codex `-002` F4 (no change).
- Provider Console audit page UI — removed from spec per owner decision; UI is separate future work if warranted.
- Full SPEC-1837 review for OTHER log classes (this bridge only addresses api_key_usage).
- Retention-job integration with tenant tier (spec says "all tiers"; current `log_retention.py` has tier-keyed structure but implementation handles unified retention — out of scope unless blocking).

## Verification Plan

```text
# Pre-apply: confirm SPEC-1832 status
$ python -c "...; print(db.get_spec('SPEC-1832')['status'])"
implemented

# Run scoped tests (impl fix evidence)
$ python -m pytest tests/multi_tenant/test_api_key_audit.py -q
# Expect: 22 passed (20 existing + 2 new tests for §3/§4 impl fixes)

# Run full suite to catch regressions
$ python -m pytest -q
# Expect: no regressions

# Apply: impl changes + spec revision + implementation-report DELIB

# Post-apply checks (F4 required by -004)
$ python -c "...; spec = db.get_spec('SPEC-1832'); print(spec['status']); assert 'response_status' not in spec['description'].lower() or '401' in spec['description']"
verified

# Check owner-decision DELIBs exist and are classified correctly
$ python -c "...; for d in [0824, 0825]: r = db.get_deliberation(f'DELIB-{d:04d}'); assert r['source_type']=='owner_conversation'; assert r['outcome']=='owner_decision'"

# Check implementation-report DELIB exists
$ python -c "...; ...; query for source_type='report', outcome='informational', source_ref='bridge/commercial-readiness-spec-verification-*.md'"
```

## Implementation Sequence

1. Read `src/multi_tenant/middleware.py` + `src/multi_tenant/api_key_audit.py` + `src/multi_tenant/log_retention.py` to scope impl changes precisely.
2. Apply §3 middleware refactor.
3. Apply §4 retention job.
4. Add 2 new tests per §5.
5. Run scoped + full test suite; confirm green.
6. Draft revised SPEC-1832 description.
7. Promote SPEC-1832 (§6) + insert implementation-report DELIB (§7).
8. Commit on `develop`: `feat(commercial-readiness): F4 SPEC-1832 — revise spec + fix status capture + add 90d retention job + verify`.
9. File post-impl report at `-006`.
10. On VERIFIED: push to `origin/develop`.

## Parallel Sibling Bridges (unchanged from REVISED-1)

- `commercial-readiness-spec-1831-startup-wiring-001.md` — awaiting Codex review.
- `commercial-readiness-spec-1833-ready-propagation-001.md` — awaiting Codex review.

## Prior Deliberations

- DELIB-0824 (NEW, owner_conversation): original 3 per-spec decisions.
- DELIB-0825 (NEW, owner_conversation): 2 additional SPEC-1832 impl-fix decisions.
- DELIB-0822/0823 (prior, report): F2 Phase 1+2 reports (unrelated to F4 but establish the owner-decision DELIB pattern precedent from F3 of `-004`).
- Codex `-002` and `-004` NO-GO findings (all cited above).

## Owner Decisions Required

None. 5 decisions captured and archived (DELIB-0824 + DELIB-0825).

## Requested Verdict

**GO** to implement §2 + §3 + §4 + §5 + §6 + §7, or **NO-GO** with specific findings.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
