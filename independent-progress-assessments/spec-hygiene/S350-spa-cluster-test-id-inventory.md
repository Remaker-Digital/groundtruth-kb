# S350 SPA Cluster Test-ID Inventory

Source work item: WI-3183
Bridge thread: gtkb-spa-cluster-test-id-investigation-closure-slice-1
Session: S350
Inventory file: independent-progress-assessments/spec-hygiene/S350-spa-cluster-test-id-inventory.md
Generated at: 2026-09-05T16:35:23+00:00
Commit SHA: 29144a06fe03e6f3afdc658ca6d3bbd60bc29ba9
Database: E:\GT-KB\groundtruth.db

## Closure Summary

- SPA specs enumerated: 10
- Current latest-version tests linked to SPA specs: 0
- Historical recycled test IDs recorded: 23
- Recommended downstream action: use this inventory as WI-3183 closure evidence and let WI-3184 handle any separate status-remediation decision.

## Classification Counts

- placeholder_test_id_unresolved: 10

## Source Queries

Latest spec row:

```sql
SELECT id, version, title, status
FROM specifications
WHERE id = ?
ORDER BY version DESC
LIMIT 1
```

Current latest-version tests per spec:

```sql
WITH latest AS (
    SELECT id, MAX(version) AS mv
    FROM tests
    GROUP BY id
)
SELECT t.id, t.version, t.spec_id, t.title, t.test_file, t.test_function, t.last_result
FROM tests t
JOIN latest l ON l.id = t.id AND l.mv = t.version
WHERE t.spec_id = ?
ORDER BY t.id
```

Historical versions for recycled test IDs:

```sql
SELECT id, version, spec_id, title, test_file, test_function, last_result
FROM tests
WHERE id = ?
ORDER BY version
```

## Recycled Test IDs

| Test ID | Historical spec | Latest spec | Latest result | Latest file | Latest function |
|---|---|---|---|---|---|
| TEST-10481 | SPEC-1816 | SPEC-1837 | historical_agent_red | tests/multi_tenant/test_log_retention.py | test_starter_audit_logs |
| TEST-10482 | SPEC-1816 | SPEC-1837 | historical_agent_red | tests/multi_tenant/test_log_retention.py | test_enterprise_audit_unlimited |
| TEST-10483 | SPEC-1816 | SPEC-1837 | historical_agent_red | tests/multi_tenant/test_log_retention.py | test_custom_override_takes_precedence |
| TEST-10484 | SPEC-1818 | SPEC-1837 | historical_agent_red | tests/multi_tenant/test_log_retention.py | test_custom_override_only_affects_specified_collection |
| TEST-10485 | SPEC-1818 | SPEC-1837 | historical_agent_red | tests/multi_tenant/test_log_retention.py | test_unknown_collection_falls_back |
| TEST-10486 | SPEC-1819 | SPEC-1837 | historical_agent_red | tests/multi_tenant/test_log_retention.py | test_365_days_cutoff |
| TEST-10487 | SPEC-1819 | SPEC-1837 | historical_agent_red | tests/multi_tenant/test_log_retention.py | test_none_retention_returns_none |
| TEST-10488 | SPEC-1820 | SPEC-1837 | historical_agent_red | tests/multi_tenant/test_log_retention.py | test_zero_retention_returns_now |
| TEST-10489 | SPEC-1820 | SPEC-1837 | historical_agent_red | tests/multi_tenant/test_log_retention.py | test_defaults_to_utc_now |
| TEST-10490 | SPEC-1820 | SPEC-1837 | historical_agent_red | tests/multi_tenant/test_log_retention.py | test_path_format |
| TEST-10491 | SPEC-1821 | SPEC-1837 | historical_agent_red | tests/multi_tenant/test_log_retention.py | test_path_with_different_month |
| TEST-10492 | SPEC-1821 | SPEC-1837 | historical_agent_red | tests/multi_tenant/test_log_retention.py | test_defaults_to_now |
| TEST-10493 | SPEC-1822 | SPEC-1837 | historical_agent_red | tests/multi_tenant/test_log_retention.py | test_expired_before_cutoff |
| TEST-10494 | SPEC-1822 | SPEC-1837 | historical_agent_red | tests/multi_tenant/test_log_retention.py | test_none_timestamp_retained |
| TEST-10495 | SPEC-1823 | SPEC-1837 | historical_agent_red | tests/multi_tenant/test_log_retention.py | test_invalid_timestamp_retained |
| TEST-10496 | SPEC-1823 | SPEC-1837 | historical_agent_red | tests/multi_tenant/test_log_retention.py | test_custom_timestamp_field |
| TEST-10497 | SPEC-1824 | SPEC-1837 | historical_agent_red | tests/multi_tenant/test_log_retention.py | test_naive_timestamp_treated_as_utc |
| TEST-10498 | SPEC-1824 | SPEC-1837 | historical_agent_red | tests/multi_tenant/test_log_retention.py | test_empty_records |
| TEST-10499 | SPEC-1824 | SPEC-1837 | historical_agent_red | tests/multi_tenant/test_log_retention.py | test_single_record |
| TEST-10503 | SPEC-1826 | SPEC-1837 | historical_agent_red | tests/multi_tenant/test_log_retention.py | test_starter_summary_structure |
| TEST-10504 | SPEC-1826 | SPEC-1837 | historical_agent_red | tests/multi_tenant/test_log_retention.py | test_starter_has_cutoff_dates |
| TEST-10505 | SPEC-1827 | SPEC-1837 | historical_agent_red | tests/multi_tenant/test_log_retention.py | test_enterprise_audit_unlimited |
| TEST-10506 | SPEC-1827 | SPEC-1837 | historical_agent_red | tests/multi_tenant/test_log_retention.py | test_enterprise_api_key_still_90 |

## Per-Spec Inventory

### SPEC-1816 - Superadmin Entitlement Management API

- Latest version: 4
- Status: active
- Classification: placeholder_test_id_unresolved
- No current linkage: true
- Current latest-version tests: 0
- Historical recycled test IDs: TEST-10481, TEST-10482, TEST-10483

| Recycled test ID | Historical title | Latest title | Latest spec |
|---|---|---|---|
| TEST-10481 | GET /api/superadmin/entitlements returns entitlement list | SPEC-1837: get_retention_days starter audit=365 | SPEC-1837 |
| TEST-10482 | PUT /api/superadmin/entitlements/{tenant_id} updates entitlements | SPEC-1837: get_retention_days enterprise=None | SPEC-1837 |
| TEST-10483 | GET /api/superadmin/entitlements/diff returns change diff | SPEC-1837: Custom override beats default | SPEC-1837 |

### SPEC-1818 - SPA Console: Full Service Management

- Latest version: 5
- Status: active
- Classification: placeholder_test_id_unresolved
- No current linkage: true
- Current latest-version tests: 0
- Historical recycled test IDs: TEST-10484, TEST-10485

| Recycled test ID | Historical title | Latest title | Latest spec |
|---|---|---|---|
| TEST-10484 | Provider Console renders 29 pages in 5 nav groups | SPEC-1837: Override scoped to collection | SPEC-1837 |
| TEST-10485 | Control Plane nav group visible with 9 pages | SPEC-1837: Unknown collection fallback | SPEC-1837 |

### SPEC-1819 - SPA Console: Code-Free Runtime Configuration

- Latest version: 4
- Status: active
- Classification: placeholder_test_id_unresolved
- No current linkage: true
- Current latest-version tests: 0
- Historical recycled test IDs: TEST-10486, TEST-10487

| Recycled test ID | Historical title | Latest title | Latest spec |
|---|---|---|---|
| TEST-10486 | EntitlementConfig page renders editable fields | SPEC-1837: 365-day cutoff computed correctly | SPEC-1837 |
| TEST-10487 | Config changes saved via PUT endpoint | SPEC-1837: None retention returns None cutoff | SPEC-1837 |

### SPEC-1820 - Allow/Block List Management

- Latest version: 4
- Status: active
- Classification: placeholder_test_id_unresolved
- No current linkage: true
- Current latest-version tests: 0
- Historical recycled test IDs: TEST-10488, TEST-10489, TEST-10490

| Recycled test ID | Historical title | Latest title | Latest spec |
|---|---|---|---|
| TEST-10488 | GET /api/superadmin/blocklists returns lists | SPEC-1837: Zero retention cutoff = now | SPEC-1837 |
| TEST-10489 | PUT /api/superadmin/blocklists/{id} updates list | SPEC-1837: Defaults to UTC now | SPEC-1837 |
| TEST-10490 | POST /api/superadmin/blocklists/check validates entry | SPEC-1837: Archive path format correct | SPEC-1837 |

### SPEC-1821 - Back-off and Retry Configuration

- Latest version: 4
- Status: active
- Classification: placeholder_test_id_unresolved
- No current linkage: true
- Current latest-version tests: 0
- Historical recycled test IDs: TEST-10491, TEST-10492

| Recycled test ID | Historical title | Latest title | Latest spec |
|---|---|---|---|
| TEST-10491 | RetryConfig page renders retry settings | SPEC-1837: Archive path month padding | SPEC-1837 |
| TEST-10492 | Retry config changes saved and applied | SPEC-1837: Archive path defaults to now | SPEC-1837 |

### SPEC-1822 - Alert Threshold Configuration

- Latest version: 4
- Status: active
- Classification: placeholder_test_id_unresolved
- No current linkage: true
- Current latest-version tests: 0
- Historical recycled test IDs: TEST-10493, TEST-10494

| Recycled test ID | Historical title | Latest title | Latest spec |
|---|---|---|---|
| TEST-10493 | AlertThresholdConfig page renders thresholds | SPEC-1837: Records before cutoff expired | SPEC-1837 |
| TEST-10494 | Alert threshold update persists | SPEC-1837: None timestamp retained | SPEC-1837 |

### SPEC-1823 - Notification Channel Configuration

- Latest version: 4
- Status: active
- Classification: placeholder_test_id_unresolved
- No current linkage: true
- Current latest-version tests: 0
- Historical recycled test IDs: TEST-10495, TEST-10496

| Recycled test ID | Historical title | Latest title | Latest spec |
|---|---|---|---|
| TEST-10495 | NotificationChannelConfig page renders channels | SPEC-1837: Invalid timestamp retained | SPEC-1837 |
| TEST-10496 | Channel enable/disable toggle persists | SPEC-1837: Custom timestamp field supported | SPEC-1837 |

### SPEC-1824 - Feature Flag System

- Latest version: 4
- Status: active
- Classification: placeholder_test_id_unresolved
- No current linkage: true
- Current latest-version tests: 0
- Historical recycled test IDs: TEST-10497, TEST-10498, TEST-10499

| Recycled test ID | Historical title | Latest title | Latest spec |
|---|---|---|---|
| TEST-10497 | GET /api/superadmin/feature-flags returns flags | SPEC-1837: Naive datetime treated as UTC | SPEC-1837 |
| TEST-10498 | PUT /api/superadmin/feature-flags updates flag state | SPEC-1837: Empty records returns empty | SPEC-1837 |
| TEST-10499 | is_feature_enabled() evaluates flag correctly | SPEC-1837: Single record NDJSON | SPEC-1837 |

### SPEC-1826 - SPA Test Execution Trigger

- Latest version: 4
- Status: active
- Classification: placeholder_test_id_unresolved
- No current linkage: true
- Current latest-version tests: 0
- Historical recycled test IDs: TEST-10503, TEST-10504

| Recycled test ID | Historical title | Latest title | Latest spec |
|---|---|---|---|
| TEST-10503 | TestExecution page renders pipeline controls | SPEC-1837: Starter summary structure | SPEC-1837 |
| TEST-10504 | Test pipeline trigger endpoint responds | SPEC-1837: Starter has cutoff dates | SPEC-1837 |

### SPEC-1827 - Diagnostic Data Export for Claude Code

- Latest version: 4
- Status: active
- Classification: placeholder_test_id_unresolved
- No current linkage: true
- Current latest-version tests: 0
- Historical recycled test IDs: TEST-10505, TEST-10506

| Recycled test ID | Historical title | Latest title | Latest spec |
|---|---|---|---|
| TEST-10505 | GET /api/superadmin/diagnostics/{tenant_id} returns snapshot | SPEC-1837: Enterprise audit unlimited in summary | SPEC-1837 |
| TEST-10506 | Diagnostic export includes all subsystems | SPEC-1837: Enterprise API key still 90d | SPEC-1837 |

## Closure Statement

The SPA control-plane cluster currently has zero latest-version MemBase test rows bound to SPEC-1816, SPEC-1818 through SPEC-1824, SPEC-1826, or SPEC-1827. The 23 historical test IDs listed above were recycled to SPEC-1837 in their latest versions, so they are not current evidence for the SPA specs under append-only latest-version semantics.

End of inventory.
