# Provisioning — Operational Lessons

> Full reference: KB DOC-PROVISIONING

## Cascading async
When making functions async, grep ALL callers — unawaited coroutines → cryptic 502s.

## FakeTenantRepo
Shared test double in `tests/helpers/fake_tenant_repo.py` prevents duplication across 5+ test files.

## Test drift from new enums
Adding `BillingChannel.MANUAL` requires updating expected value sets in tests — maintenance, not regressions.
