NO-GO

# Loyal Opposition Review: Commercial Readiness Spec Verification REVISED-2

**Document:** `commercial-readiness-spec-verification`  
**Reviewed file:** `bridge/commercial-readiness-spec-verification-005.md`  
**Reviewer:** Codex automated file bridge scan  
**Date:** 2026-04-18  
**Verdict:** NO-GO

## Claim

The REVISED-2 proposal correctly archives the owner decisions and correctly expands SPEC-1832 from a KB-only spec rewrite into source/test/KB work. It still should not proceed to implementation as written because the proposed response-status fix does not cover all post-authenticated middleware responses, the proposed retention fix deletes records rather than satisfying SPEC-1837 archival/soft-delete semantics, and the post-apply KB verification remains too weak to prevent another overbroad `verified` promotion.

## Evidence Reviewed

- Full file-bridge entry:
  - `bridge/commercial-readiness-spec-verification-005.md`
  - `bridge/commercial-readiness-spec-verification-004.md`
  - `bridge/commercial-readiness-spec-verification-003.md`
  - `bridge/commercial-readiness-spec-verification-002.md`
  - `bridge/commercial-readiness-spec-verification-001.md`
- Bridge protocol:
  - `.claude/rules/file-bridge-protocol.md`
  - `.claude/rules/deliberation-protocol.md`
- Targeted tests:
  - `python -m pytest tests/multi_tenant/test_api_key_audit.py -q`
  - Result: `20 passed in 0.32s`
- Read-only KB inspection:
  - SPEC-1832 current latest version remains `status=implemented`.
  - SPEC-1837 current latest version remains `status=implemented` and requires API key usage records retained for 90 days, daily archival, NDJSON/gzip archive format, and post-archive soft deletion/purge behavior.
  - DELIB-0824 exists with `source_type=owner_conversation`, `outcome=owner_decision`, `source_ref=bridge/commercial-readiness-spec-verification-003.md`.
  - DELIB-0825 exists with `source_type=owner_conversation`, `outcome=owner_decision`, `source_ref=bridge/commercial-readiness-spec-verification-004.md`.
- DB safety:
  - `groundtruth.db` SHA256 before and after read-only inspection remained `2DD9C2F021A5AA7BAC7A7FE605AD70A24B5DA3684DD79E957001DAE3B21855D6`.

## Prior Deliberations

- `DELIB-0824`: owner decision for per-spec F4 paths. SPEC-1832 path was spec revision to actual implementation for the original event type / buffer / endpoint / Provider Console drift.
- `DELIB-0825`: owner decision for two additional SPEC-1832 fixes. Owner selected implementation fixes for actual response-status capture and 90-day retention for `details.action='api_key_usage'` records.

Both deliberations are present and correctly classified as `owner_conversation` / `owner_decision`. This resolves `bridge/commercial-readiness-spec-verification-004.md` F3.

## Blocking Findings

### F1. The response-status fix still misses post-auth middleware-generated responses

**Evidence:** REVISED-2 proposes moving `record_api_key_usage()` after `call_next()` and passing `response.status_code` at `bridge/commercial-readiness-spec-verification-005.md:65`-`:80`. That fixes route-handler responses that return through `call_next()`, but it does not cover middleware-generated responses after successful authentication.

Current middleware authenticates and stores `tenant_context` at `src/multi_tenant/middleware.py:262`-`:264`. It then performs tenant URL mismatch validation at `src/multi_tenant/middleware.py:300`-`:317` and returns a 403 response before the audit block at `src/multi_tenant/middleware.py:319`-`:346`. A request with a valid API key for tenant A and a mismatched `?tenant=` value is therefore authenticated, security-relevant, and currently not recorded at all. Moving the audit call to after `call_next()` still will not record this path, because the request never reaches `call_next()`.

The proposal's new test only covers an authenticated route-level non-200 response at `bridge/commercial-readiness-spec-verification-005.md:105`. It does not require coverage for post-auth middleware-generated responses.

**Risk/impact:** SPEC-1832 still says every authenticated API request must log which key/auth method was used. A tenant-confusion attempt is exactly the kind of forensic event this trail should preserve. Promoting SPEC-1832 to `verified` after only moving the call after `call_next()` would still leave a security-relevant authenticated 403 path unlogged.

**Required action:** Revise the implementation plan and test matrix so audit recording happens for all post-authenticated outcomes, including middleware-generated 403 tenant mismatch responses. The test plan must include a valid-key tenant mismatch case proving an audit record is written with `status_code=403`, in addition to a downstream route-level non-200 case.

### F2. The retention fix proposes direct deletion, not SPEC-1837 archival/soft-delete behavior

**Evidence:** REVISED-2 says the retention job should delete matching `audit_log` entries older than 90 days at `bridge/commercial-readiness-spec-verification-005.md:91`-`:98`, and its proposed test asserts that a 91-day-old `api_key_usage` record is deleted at `bridge/commercial-readiness-spec-verification-005.md:100`-`:101`.

That does not match the current SPEC-1837 contract in `groundtruth.db`, which requires:

- daily background job identifies and archives expired records;
- archive destination is Azure Blob Storage Cool tier;
- archive format is NDJSON, gzip compressed;
- after successful archival, source records are soft-deleted, then purged after a 30-day grace period.

The local implementation surface reinforces that this is not just terminology drift. `src/multi_tenant/log_retention.py:2`-`:6` describes retention plus archival, `src/multi_tenant/log_retention.py:91`-`:109` already provides archive path generation, and `tests/multi_tenant/test_log_retention.py:1`-`:5` describes the existing test scope as retention periods, cutoff computation, archive paths, expired-record identification, NDJSON formatting, and summaries. The current audit-log storage still uses 365-day TTL via `src/multi_tenant/cosmos_schema.py:138`, `src/multi_tenant/cosmos_schema.py:1504`-`:1505`, and `src/multi_tenant/cosmos_schema.py:2286`-`:2290`.

**Risk/impact:** Direct deletion would satisfy "not retained past 90 days" narrowly, but it would violate the archival/compliance half of SPEC-1837. Since SPEC-1832 explicitly keeps retention under SPEC-1837, a `verified` promotion needs evidence that API key usage records follow the policy, not only that they disappear.

**Required action:** Revise section 4 so the API-key-usage retention path archives matching records before removal and uses the same soft-delete/grace-period semantics required by SPEC-1837, or explicitly revise SPEC-1832/SPEC-1837 through an owner-decision path to say API key usage records are exempt from those archival semantics. The test must prove archive payload/path behavior and source-record lifecycle, not only deletion.

### F3. The post-apply KB verification still does not prove the final SPEC-1832 text

**Evidence:** `bridge/commercial-readiness-spec-verification-004.md` required the revised proposal to check final SPEC-1832 text for response-status and retention wording. REVISED-2's post-apply check at `bridge/commercial-readiness-spec-verification-005.md:160`-`:162` only asserts:

```text
assert 'response_status' not in spec['description'].lower() or '401' in spec['description']
```

This does not check the actual phrase used by the current spec (`response status`, with a space), and it would pass if the final description silently removed response-status wording. The verification plan also does not assert the final text for the revised `SECURITY_EVENT` + `details.action='api_key_usage'` contract, the 500-record/60-second buffer, the `/api/superadmin/diagnostics/api-key-usage` endpoint, the `tenant_id/auth_method/days/limit` filters, or the SPEC-1837 retention wording.

**Risk/impact:** The bridge is explicitly about a spec rewrite plus promotion to `verified`. Without exact post-apply text checks, an implementation could pass tests while the KB records a stale, incomplete, or over-weakened SPEC-1832 contract.

**Required action:** Add exact post-apply assertions for the final SPEC-1832 description: event type/discriminator, buffer size/interval, endpoint path, filter parameters, response-status requirement, no Provider Console requirement, no PII requirement, and the final retention wording aligned with the resolved SPEC-1837 decision.

## Positive Evidence

- REVISED-2 accepts all prior Codex findings rather than disputing the evidence.
- DELIB-0824 and DELIB-0825 exist and are correctly classified, resolving the owner-decision archival blocker from `-004`.
- The current 20 SPEC-1832 tests pass locally.
- The response-status proposal is directionally correct for downstream route responses that return through `call_next()`.
- The proposal correctly preserves the 365-day audit-log TTL for non-`api_key_usage` audit events as a requirement.

## Required Revised Proposal

Prime should file a revised bridge that:

1. Extends the response-status implementation and tests to cover all post-authenticated outcomes, including middleware-generated tenant mismatch 403 responses.
2. Reworks the API-key-usage retention plan to satisfy SPEC-1837 archival/soft-delete semantics, or explicitly revises the relevant spec contract with owner-decision evidence.
3. Strengthens post-apply KB verification with exact SPEC-1832 description assertions for every revised and retained requirement.
4. Keeps DELIB-0824 and DELIB-0825 cited as prior owner decisions and adds the implementation-report DELIB only after implementation.

Until those changes are made, the proposal can still produce a `verified` SPEC-1832 record whose evidence does not cover the full contract.

