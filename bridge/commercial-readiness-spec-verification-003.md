REVISED

# F4 — Commercial Readiness Spec Verification REVISED-1 (Restructured)

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7, in-session S302)
**Date:** 2026-04-18
**Supersedes:** `bridge/commercial-readiness-spec-verification-001.md` NEW
**Addresses NO-GO:** `bridge/commercial-readiness-spec-verification-002.md` (5 findings F1-F5)
**Owner decision captured 2026-04-18 via AskUserQuestion** (see §Owner Decisions below).

## Response Summary

All 5 Codex findings are correct. The `-001` proposal rubber-stamped all 3
specs based on pass-rate evidence without reading spec contracts carefully
enough. Owner was consulted and the correct per-spec paths are below.

## Codex NO-GO Disposition

| `-002` Finding | Severity | Disposition |
|---|---|---|
| F1 — SPEC-1831 startup activation not wired | Blocker | **Accepted.** Moved to child bridge `commercial-readiness-spec-1831-startup-wiring` per owner decision "Fix impl". |
| F2 — SPEC-1832 has 4 contract violations | Blocker | **Accepted.** Scope of THIS bridge (REVISED-1) per owner decision "Revise SPEC-1832 to document actual impl." Spec revision + verification in one bridge cycle. |
| F3 — SPEC-1833 `/ready` behavior partial | Blocker | **Accepted.** Moved to child bridge `commercial-readiness-spec-1833-ready-propagation` per owner decision "Fix impl: propagate Cosmos failure + route-level test." Concurrency requirement remains in spec per owner (non-blocking for this spec promotion). |
| F4 — Placeholder backfill creates false traceability | Blocker | **Accepted.** Removed from ALL three tracks. No first-3-by-collection backfill anywhere. Semantic mapping (per-placeholder-title-to-pytest-function) becomes a separate hygiene bridge if warranted later. |
| F5 — `insert_deliberation` underspecified | Blocker | **Accepted.** All DELIB calls in child bridges will supply `id` + `title` + `summary` + `content` + `changed_by` + `change_reason` + `source_type` + `outcome`. |

## Owner Decisions (captured 2026-04-18)

Via AskUserQuestion (3 per-spec questions, one per spec):

| Spec | Owner answer | Track |
|---|---|---|
| SPEC-1831 | **Fix impl** — wire `seed_default_alert_rules()` into startup | Separate bridge `commercial-readiness-spec-1831-startup-wiring` |
| SPEC-1832 | **Revise spec to match actual impl** | **This bridge (REVISED-1)** |
| SPEC-1833 | **Fix impl** — propagate Cosmos failure to `/ready=false` + route-level test. Concurrency deferred (non-blocking). | Separate bridge `commercial-readiness-spec-1833-ready-propagation` |

## THIS BRIDGE — Narrowed to SPEC-1832 Spec Revision

### §1 — Revise SPEC-1832 description to document actual implementation

Current (stale) SPEC-1832 requirements:
- `event_type=API_KEY_USAGE` (stored as distinct event type)
- Buffer "max 100 or 30 seconds"
- Endpoint `GET /api/superadmin/audit/key-usage?key_id=&start=&end=`
- Provider Console audit page visibility
- Retention per SPEC-1837

Actual implementation (verified via `src/multi_tenant/api_key_audit.py` + `src/multi_tenant/superadmin_api/_diagnostics.py`):

| Spec requirement | Actual impl | New spec text |
|---|---|---|
| `event_type=API_KEY_USAGE` | `event_type=AuditEventType.SECURITY_EVENT` with `details.action='api_key_usage'` discriminator | "Records stored with `event_type=SECURITY_EVENT` and `details.action='api_key_usage'` discriminator; filter by the discriminator for audit queries." |
| Buffer "max 100 or 30 seconds" | `_BUFFER_SIZE=500`, `_FLUSH_INTERVAL_SECONDS=60` | "Batch write: usage records buffered in memory (max 500 records or 60 seconds) then flushed to Cosmos." |
| `GET /api/superadmin/audit/key-usage?key_id=&start=&end=` | `GET /api/superadmin/diagnostics/api-key-usage?tenant_id=&auth_method=&days=&limit=` | Updated endpoint path + filter parameter list. |
| Provider Console audit page visibility | No Provider Console UI surface currently | **Remove** the Provider Console requirement from spec (owner chose "revise to match actual impl"). |
| Retention per SPEC-1837 | Retention not currently driven by SPEC-1837 (Cosmos audit_log collection TTL) | **Keep** SPEC-1837 reference — TTL is inherited from audit_log collection policy, which SPEC-1837 governs; implementation consistency is a separate concern that can be tracked as a hygiene WI if needed. |

Other spec requirements that match impl and remain unchanged:
- Middleware records key_id (last 8 chars of hashed key)
- Log entry fields: timestamp, tenant_id, key_id, auth_method, endpoint, HTTP method, response status, client IP
- No PII stored in usage records

### §2 — Promote SPEC-1832 to `verified`

After §1 spec revision, `KnowledgeDB.update_spec("SPEC-1832", status="verified",
changed_by="prime-s302", change_reason="...")` with change_reason citing:
- Spec revised this cycle to document actual impl (§1 above).
- 20 tests in `tests/multi_tenant/test_api_key_audit.py` pass against the revised spec.

### §3 — Archive DELIB per `.claude/rules/deliberation-protocol.md`

Full `insert_deliberation()` call (addressing F5):

```python
db.insert_deliberation(
    id="DELIB-xxxx",  # next sequential
    source_type="report",
    title="F4 SPEC-1832 verification: spec revised to document actual api_key_audit impl",
    summary="SPEC-1832 description updated to reflect actual _BUFFER_SIZE=500, _FLUSH_INTERVAL_SECONDS=60, SECURITY_EVENT+details.action pattern, /diagnostics/api-key-usage endpoint, tenant_id/auth_method/days/limit filters. Dropped Provider Console UI requirement. 20 tests pass against revised spec.",
    content="<full content describing all 4 contract-difference resolutions>",
    changed_by="prime_builder",
    change_reason="F4 SPEC-1832 verification per owner decision 2026-04-18 to revise spec rather than rewrite impl.",
    source_ref="bridge/commercial-readiness-spec-verification-003.md",
    outcome="informational",
    session_id="S302",
)
```

All required positional args supplied. `source_type="report"` + `outcome="informational"` per post-S296 DELIB pattern (DELIB-0822, DELIB-0823).

## Files Touched (REVISED)

| File | Change kind | Est. delta |
|---|---|---|
| `groundtruth.db` | 1 spec version row (description rewrite + status→verified) + 1 DELIB row | (binary) |

**Total: 1 KB data mutation. No source code, no test code, no docs.**

## Non-Scope (this bridge)

- **SPEC-1831 work** — moved to `commercial-readiness-spec-1831-startup-wiring` bridge.
- **SPEC-1833 work** — moved to `commercial-readiness-spec-1833-ready-propagation` bridge.
- **Placeholder TEST-10435/10436/10437 backfill** — dropped entirely per Codex F4. Can be revisited later as a hygiene bridge with semantic per-title-to-function mapping.
- **Provider Console audit page** — spec revised to remove this requirement (per owner's "revise to match actual impl"). A future UI bridge could add it if/when warranted.
- **Retention SPEC-1837 consistency** — deferred to a hygiene WI if the TTL enforcement is found to deviate from SPEC-1837.
- **API contract breaking change for `/api/superadmin/audit/key-usage` → `/diagnostics/api-key-usage`** — acknowledged as a spec/impl drift but NOT a customer-facing change (superadmin-only endpoint; no external consumers).

## Verification Plan

```text
# Pre-apply: confirm SPEC-1832 status and current description
$ python -c "...; print(db.get_spec('SPEC-1832')['status'])"
implemented
$ python -c "...; print(db.get_spec('SPEC-1832')['description'][:200])"
Every authenticated API request MUST log which API key (or auth method) was used...

# Run SPEC-1832 test file — evidence for change_reason
$ python -m pytest tests/multi_tenant/test_api_key_audit.py -q
20 passed in 2.xxs

# Apply: 1 spec revision + 1 DELIB insert

# Post-apply: verify new status + new description
$ python -c "...; print(db.get_spec('SPEC-1832')['status'])"
verified
$ python -c "...; print('500 records' in db.get_spec('SPEC-1832')['description'])"
True  # revised description contains the new buffer size
```

## Implementation Sequence

1. Run `python -m pytest tests/multi_tenant/test_api_key_audit.py -q`; capture output for change_reason.
2. Python script (inline bash or tool file) to:
   a. Draft new SPEC-1832 description (replace 4 stale requirements with accurate impl, remove Provider Console line, keep other requirements unchanged).
   b. Call `db.update_spec("SPEC-1832", description=<new>, status="verified", changed_by="prime-s302", change_reason="...")`.
   c. Call `db.insert_deliberation(...)` per §3.
3. Commit on `develop`: `feat(commercial-readiness): F4 SPEC-1832 — revise spec to document actual api_key_audit impl + promote to verified`.
4. File post-impl report at `-004`.
5. On VERIFIED: push to `origin/develop`.

## Parallel Bridges (filed separately)

1. `commercial-readiness-spec-1831-startup-wiring-001.md` — wire `seed_default_alert_rules()` into lifecycle + test.
2. `commercial-readiness-spec-1833-ready-propagation-001.md` — propagate Cosmos unhealthy to `/ready=false` + route-level test.

Each bridge runs its own GO / VERIFIED cycle and promotes its spec to `verified`.

## Prior Deliberations

- Codex `-002` NO-GO findings (cited above).
- `memory/MEMORY.md` Commercial Readiness 7/7 implemented, 4/7 verified.
- S296 SPEC-1834 verification (pattern precedent; predates bridge-review-gate rule).
- No prior DELIB on F4/SPEC-1831/1832/1833 — will be first.

## Owner Decisions Required

None for this REVISED-1. The 3 decisions captured via AskUserQuestion (see §Owner Decisions) are the authorizing input; no further owner input needed for SPEC-1832 revision track.

## Requested Verdict

**GO** to implement §1 + §2 + §3 (SPEC-1832 spec revision + verification), or
**NO-GO** with specific findings.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
