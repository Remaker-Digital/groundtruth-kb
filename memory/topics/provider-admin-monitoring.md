# Provider Admin — Operational Patterns

> Full architecture: KB DOC-PROVIDER-ADMIN

## Null-Safety Pattern (S54)
Backend returns null for empty aggregates. React code must use `?? {}` before `Object.entries()` / `Object.keys()`. Fixed in 8 Provider Console files. All future Provider Console pages MUST use `?? {}` on any API response field passed to `Object.entries()` or `Object.keys()`.

## Architecture Patterns
- **Cross-partition Cosmos:** `enable_cross_partition_query=True` (no partition key)
- **Module-level repo globals:** Set via `configure_superadmin_services()` at startup
- **Lazy imports with degradation:** Dashboard subsystem imports inside function body, try/except — partial data on failure
- **Pydantic camelCase:** `ConfigDict(alias_generator=to_camel, populate_by_name=True)`
