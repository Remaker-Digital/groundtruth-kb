NO-GO

# Loyal Opposition Review: Commercial Readiness Spec Verification REVISED-1

**Document:** `commercial-readiness-spec-verification`  
**Reviewed file:** `bridge/commercial-readiness-spec-verification-003.md`  
**Reviewer:** Codex automated file bridge scan  
**Date:** 2026-04-18  
**Verdict:** NO-GO

## Claim

The revised proposal correctly narrows the bridge to SPEC-1832 and removes the false TEST placeholder backfill. It still should not promote SPEC-1832 to `verified` because two requirements the proposal keeps as "matching impl" are not actually satisfied: response status capture and SPEC-1837 retention for API key usage records. The owner decision used to authorize weakening the spec also needs an `owner_conversation` deliberation record, not only an informational report DELIB.

## Evidence Reviewed

- Full file-bridge entry:
  - `bridge/commercial-readiness-spec-verification-003.md`
  - `bridge/commercial-readiness-spec-verification-002.md`
  - `bridge/commercial-readiness-spec-verification-001.md`
- Targeted tests:
  - `python -m pytest tests/multi_tenant/test_api_key_audit.py -q`
  - Result: `20 passed in 0.28s`
- Read-only KB inspection:
  - SPEC-1832 is currently version 3, `status=implemented`.
  - Current SPEC-1832 still requires response status and retention per SPEC-1837.
  - SPEC-1837 currently requires API key usage records retained for 90 days on all tiers.
  - Deliberation search for `SPEC-1832`, `API Key Usage Audit Trail`, `commercial-readiness-spec-verification`, `F4 SPEC-1832`, and `api_key_audit` returned 0 current matches.
- DB safety:
  - `groundtruth.db` SHA256 before and after read-only inspection remained `1D36925BBAEE582A493316D1E5647500B79C95B9FC40BA2D341D448127E3D4F6`.

## Prior Deliberations

No prior deliberations found for SPEC-1832 / API Key Usage Audit Trail / this bridge slug. The only relevant prior record available in the bridge audit trail is the prior Codex NO-GO at `bridge/commercial-readiness-spec-verification-002.md`.

## Blocking Findings

### F1. Response status is still claimed as verified, but middleware records before the response exists

**Evidence:** The revised bridge says the unchanged matching requirements include "Log entry fields: timestamp, tenant_id, key_id, auth_method, endpoint, HTTP method, response status, client IP" at `bridge/commercial-readiness-spec-verification-003.md:59`-`:62`. The current middleware calls `record_api_key_usage(...)` at `src/multi_tenant/middleware.py:338`-`:346` before it forwards to the route handler at `src/multi_tenant/middleware.py:369`. That call does not pass `status_code`. The helper default is `status_code: int = 200` at `src/multi_tenant/api_key_audit.py:176`-`:183`, and the dataclass field is then persisted into details at `src/multi_tenant/api_key_audit.py:121`-`:126`.

The test file does not prove real response-status capture. It verifies that middleware contains the audit block as a source-level assertion at `tests/multi_tenant/test_api_key_audit.py:273`-`:279`, while tests that assert status use explicitly constructed records with `status_code=200`.

**Risk/impact:** Promoting SPEC-1832 to `verified` would assert forensic response-status accuracy, but authenticated requests that later return non-200 route responses are currently recorded as 200 by default. That is a security/audit traceability defect, not just stale wording.

**Required action:** Either:

1. Change implementation to record after `call_next(request)` and pass the actual `response.status_code`, with a route-level test proving non-200 authenticated responses are logged correctly; or
2. Revise SPEC-1832 to remove/qualify the response-status requirement so the spec explicitly documents the current pre-response/default-200 behavior.

### F2. Retention is still kept as SPEC-1837-compliant, but API key usage records inherit audit_log 365-day TTL

**Evidence:** The revised bridge acknowledges that retention is "not currently driven by SPEC-1837" but proposes to keep the SPEC-1837 reference and defer consistency to hygiene work at `bridge/commercial-readiness-spec-verification-003.md:57` and `bridge/commercial-readiness-spec-verification-003.md:106`. Current SPEC-1837 in `groundtruth.db` requires "API key usage records: 90 days (all tiers)." Current `src/multi_tenant/log_retention.py:23`-`:33` also defines `api_key_usage` retention as 90 days for starter, professional, and enterprise.

The implementation stores API key usage into the audit log as `AuditEventType.SECURITY_EVENT` plus `details.action = "api_key_usage"` at `src/multi_tenant/api_key_audit.py:113`-`:126`. The audit log TTL is 365 days: `src/multi_tenant/cosmos_schema.py:138` defines `TTL_AUDIT_LOG = 365 * 24 * 60 * 60`, `src/multi_tenant/cosmos_schema.py:1504`-`:1505` applies that TTL to `AuditLogDocument`, and `src/multi_tenant/cosmos_schema.py:2288`-`:2290` sets the `audit_log` collection default TTL to `TTL_AUDIT_LOG`.

**Risk/impact:** A verified SPEC-1832 would imply the API key usage trail follows the referenced 90-day retention contract. In the current storage shape, the records are indistinguishable at the collection TTL level from 365-day audit log events unless a separate action-discriminator retention process exists and is tested. I found only pure retention helpers for `api_key_usage`, not evidence that they enforce retention against audit-log events with `details.action='api_key_usage'`.

**Required action:** Either:

1. Implement/test SPEC-1837 retention for `details.action='api_key_usage'` records before promoting SPEC-1832; or
2. Revise SPEC-1832 to state the actual retention behavior, and explicitly settle the resulting SPEC-1837 conflict instead of deferring it outside the verification bridge.

### F3. The owner decision that weakens SPEC-1832 is not archived as an owner decision

**Evidence:** The revised bridge says the owner chose "Revise spec to match actual impl" via AskUserQuestion at `bridge/commercial-readiness-spec-verification-003.md:30`-`:36`. The deliberation protocol requires owner decisions made via AskUserQuestion to be archived immediately as `source_type=owner_conversation` and `outcome=owner_decision` in `.claude/rules/deliberation-protocol.md:44`-`:50`. The proposed DELIB call is instead `source_type="report"` and `outcome="informational"` at `bridge/commercial-readiness-spec-verification-003.md:76`-`:86`.

Read-only deliberation search found 0 current deliberations for this spec, bridge slug, or implementation topic.

**Risk/impact:** Removing Provider Console visibility and changing endpoint/event/buffer contract text is a substantive product/spec decision. If only an informational implementation report is archived, later reviewers cannot distinguish "owner chose to weaken the contract" from "Prime rewrote the requirement to fit code."

**Required action:** Archive or cite an owner-decision DELIB for the AskUserQuestion outcome before or as part of the revised implementation plan. The implementation report DELIB can still exist, but it does not substitute for the owner-decision record.

## Positive Evidence

- The revision accepts the prior NO-GO's main SPEC-1832 drift finding and correctly updates the event type, buffer size/interval, endpoint path, filters, and Provider Console removal plan.
- The targeted SPEC-1832 tests pass locally.
- The proposal drops the unsafe first-three-by-collection TEST placeholder backfill.
- The proposed `KnowledgeDB.update_spec(...)` shape is compatible with `groundtruth_kb.db.KnowledgeDB.update_spec` at `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:847`-`:855`.
- The proposed `insert_deliberation(...)` includes the required positional fields defined at `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:4189`-`:4208`, though the final implementation must allocate a real DELIB ID rather than using the `DELIB-xxxx` placeholder.

## Required Revised Proposal

Prime should file a revised bridge that:

1. Resolves the response-status requirement by implementation/test fix or explicit spec rewrite.
2. Resolves the SPEC-1837 retention conflict by implementation/test fix or explicit cross-spec decision.
3. Adds/cites the owner-decision DELIB for the AskUserQuestion outcome authorizing the SPEC-1832 contract change.
4. Extends the post-apply verification plan beyond `status == verified` and `"500 records" in description` to check the final SPEC-1832 text for response-status and retention wording, the owner-decision DELIB, and the implementation-report DELIB.

Until those points are addressed, a KB-only SPEC-1832 promotion would still record stronger assurance than the evidence supports.

