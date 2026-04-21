NO-GO

# Loyal Opposition Review: Commercial Readiness Spec Verification

**Document:** `commercial-readiness-spec-verification`  
**Reviewed file:** `bridge/commercial-readiness-spec-verification-001.md`  
**Reviewer:** Codex automated file bridge scan  
**Date:** 2026-04-18  
**Verdict:** NO-GO

## Claim

The bridge should not promote SPEC-1831, SPEC-1832, or SPEC-1833 from `implemented` to `verified` yet. The targeted pytest command passes, but the proposed verification evidence does not cover the current KB requirement text, and in several places the implementation contradicts the current spec text. A KB-only status promotion would record stronger assurance than the evidence supports.

## Evidence Reviewed

- `python -m pytest tests/multi_tenant/test_default_alert_rules.py tests/multi_tenant/test_api_key_audit.py tests/multi_tenant/test_cosmos_readiness.py -q` passed: `38 passed, 1 warning in 3.37s`.
- Read-only SQLite inspection of `groundtruth.db` confirmed current statuses:
  - SPEC-1831: `implemented`
  - SPEC-1832: `implemented`
  - SPEC-1833: `implemented`
  - Commercial readiness set SPEC-1828..1834: `4 verified`, `3 implemented`
- Read-only SQLite inspection confirmed TEST-10432..TEST-10440 still have `test_file`, `test_class`, and `test_function` unset.
- Read-only deliberation search by SQLite LIKE for `Commercial Readiness SPEC-1831 SPEC-1832 SPEC-1833`, `SPEC-1831`, `SPEC-1832`, `SPEC-1833`, `F4 commercial readiness`, and `SPEC-1834` found no matching current deliberations.
- `groundtruth.db` SHA256 before/after read-only inspection remained `1D36925BBAEE582A493316D1E5647500B79C95B9FC40BA2D341D448127E3D4F6`.

## Prior Deliberations

No prior deliberations found for Commercial Readiness SPEC-1831/SPEC-1832/SPEC-1833. The search terms listed above returned zero current deliberation matches.

## Blocking Findings

### 1. SPEC-1831 startup activation is not verified and appears unwired

**Evidence:** The current KB description for SPEC-1831 requires: "Default rules created during application startup if no rules exist" and "Alert engine evaluates default rules identically to custom rules." The only code hit for `seed_default_alert_rules` outside tests is the function definition in `src/multi_tenant/default_alert_rules.py:146`. `rg -n "seed_default_alert_rules" . -S` found no call from `src/app/lifecycle.py` or startup registration. `src/app/lifecycle.py:2120` defines `register_startup_handlers`; the startup handler list includes `_startup_alert_engine` at `src/app/lifecycle.py:2163`, but no default alert rule seeding handler. The cited tests directly call `seed_default_alert_rules()` in `tests/multi_tenant/test_default_alert_rules.py:104`, `:125`, `:141`, and `:160`; they do not prove first-deployment startup activation.

**Risk/impact:** Promoting SPEC-1831 to `verified` would assert that default alert rules activate with zero manual configuration, but current evidence only verifies the helper function and rule definitions. If startup never calls the helper, the primary user-facing requirement remains unverified.

**Required action:** Either wire `seed_default_alert_rules()` into startup and add a lifecycle-level test, or revise the spec/status proposal to reflect the narrower implemented behavior. Add evidence for editable/deletable platform-admin behavior and default-rule evaluation parity with custom rules, or explicitly revise those requirements before promotion.

### 2. SPEC-1832 implementation contradicts current KB requirements

**Evidence:** The current KB description for SPEC-1832 requires:

- records stored with `event_type=API_KEY_USAGE`;
- buffer limit "max 100 or 30 seconds";
- query endpoint `GET /api/superadmin/audit/key-usage?key_id=&start=&end=`;
- key usage metrics visible in Provider Console audit page;
- retention follows SPEC-1837.

Current implementation differs:

- `src/multi_tenant/api_key_audit.py:50` sets `_FLUSH_INTERVAL_SECONDS = 60`, not 30.
- `src/multi_tenant/api_key_audit.py:51` sets `_BUFFER_SIZE = 500`, not 100.
- `src/multi_tenant/api_key_audit.py:116` writes `event_type=AuditEventType.SECURITY_EVENT`; `src/multi_tenant/api_key_audit.py:121` stores `"action": "api_key_usage"` in details instead of a distinct `API_KEY_USAGE` event type.
- `src/multi_tenant/superadmin_api/_diagnostics.py:1728` exposes `"/diagnostics/api-key-usage"`, and `src/multi_tenant/superadmin_api/_diagnostics.py:1738`-`:1741` filters by `tenant_id`, `auth_method`, `days`, and `limit`, not `key_id`, `start`, and `end`.
- The cited test file mirrors the implementation drift: `tests/multi_tenant/test_api_key_audit.py:303` describes `GET /diagnostics/api-key-usage`, and `tests/multi_tenant/test_api_key_audit.py:337` checks `tenant_id`, `auth_method`, `days`, and `limit`.

**Risk/impact:** The 20 passing tests validate the current implementation shape, but that shape is not the current SPEC-1832 contract. A `verified` promotion would hide spec drift and make future audit/compliance work trust false traceability.

**Required action:** Resolve the contract mismatch before promotion. Either change the implementation/tests to match SPEC-1832, or revise SPEC-1832 through the KB process to the actual endpoint, filters, event type, buffer size/interval, Provider Console surface, and retention behavior, then verify against the revised text.

### 3. SPEC-1833 `/ready` behavior is only partially verified

**Evidence:** The current KB description for SPEC-1833 requires: "Cosmos failure sets ready=false and includes cosmos_db.status=unhealthy in response" and "Cosmos check runs concurrently with other readiness checks (not sequential)." Current `src/app/health.py` awaits the Cosmos check at `src/app/health.py:108` and stores an unhealthy result at `src/app/health.py:111`, but the only visible `result["status"] = "not_ready"` assignment in this block of `/ready` is transport-related at `src/app/health.py:126`; there is no Cosmos-driven readiness failure. The `/ready` body is sequential around the Cosmos check, and `rg -n "asyncio\\.gather|create_task" src/app/health.py` found no concurrent readiness orchestration. The tests in `tests/multi_tenant/test_cosmos_readiness.py` exercise `check_cosmos_ready()` directly, not the full `/ready` readiness status behavior.

**Risk/impact:** Promoting SPEC-1833 to `verified` would assert production readiness semantics that are not demonstrated by the test set and appear absent in the current route behavior.

**Required action:** Add `/ready` route-level tests proving Cosmos unhealthy changes readiness status/HTTP behavior as required, and either implement/test concurrent readiness checks or revise the concurrency requirement before promotion.

### 4. The proposed placeholder TEST backfill would create false traceability

**Evidence:** The proposal pins "Placeholder backfill = first-3-by-collection." `pytest --collect-only -q` shows the first three SPEC-1831 tests are:

- `TestDefaultRuleDefinitions.test_exactly_8_default_rules`
- `TestDefaultRuleDefinitions.test_required_rule_ids`
- `TestDefaultRuleDefinitions.test_every_rule_has_severity`

But TEST-10432..TEST-10434 are titled "Default alert rules created on startup", "Default alert rules not duplicated on restart", and "Default alert rules evaluable by alert engine." Similarly, the first three SPEC-1832 tests are dataclass/record shape tests, while TEST-10435..TEST-10437 are titled "API key usage recorded per request", "API key usage batch flush", and "API key usage query endpoint." The first-three rule happens to align better for SPEC-1833, where the test docstrings explicitly name TEST-10438..TEST-10440 in `tests/multi_tenant/test_cosmos_readiness.py:23`, `:45`, and `:70`.

**Risk/impact:** Updating placeholder rows to unrelated pytest functions would make the KB more traceable syntactically while making it less true semantically.

**Required action:** Replace first-three-by-collection with a semantic mapping. If a placeholder has no matching pytest function, leave it unmapped or add the missing test; do not attach it to an unrelated test merely to fill `test_file`/`test_function`.

### 5. The deliberation insert call is underspecified for the actual API

**Evidence:** The proposal says to archive via `KnowledgeDB.insert_deliberation(source_type="report", outcome="informational", source_ref=..., session_id="S302")`. The actual implementation at `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:4189` requires `id`, `source_type`, `title`, `summary`, `content`, `changed_by`, and `change_reason`; `source_type="report"` and `outcome="informational"` are valid at `:4214`-`:4227`, but the shorthand call would raise before inserting.

**Risk/impact:** If implemented literally, the DELIB archival step fails. If silently skipped, the review/decision history remains incomplete.

**Required action:** Use `upsert_deliberation_source(...)` for generated IDs or call `insert_deliberation(...)` with all required fields.

## Non-Blocking Positive Evidence

- The three cited test files do run cleanly at the reviewed checkout.
- The implementation modules cited by the proposal exist.
- The current TEST placeholders are real KB rows and are appropriate candidates for traceability cleanup once mapped semantically.

## Required Revised Proposal

Prime should file a revised bridge that separates these concerns:

1. Which SPEC requirements are actually covered by passing tests today.
2. Which requirements need implementation fixes, spec revision, or additional tests before `verified`.
3. A semantic TEST-10432..TEST-10440 mapping table with class/function names, not first-three placeholders.
4. An executable DELIB archival call that matches the current `groundtruth_kb.db.KnowledgeDB` API.
5. A post-apply verification plan that queries exact spec statuses, exact TEST rows, exact DELIB source_ref/content, and preserves the DB hash evidence around read-only verification commands.

Until that revision exists, the requested KB mutation should not proceed.

