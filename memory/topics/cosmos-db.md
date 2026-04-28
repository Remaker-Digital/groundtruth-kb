# Cosmos DB — Operational Patterns

> Full reference: KB DOC-COSMOS-DB

## Patch Operations
- `patch(tenant_id, document_id, operations)` — NOT `item_id` or `partition_key`
- Operations format: `[{"op": "set", "path": "/field", "value": val}]` (array, not dict)
- All repository constructors take NO arguments — resolve `get_cosmos_manager()` lazily via `_container` property

## PreferencesDocument ID Format
- Format: `{tenant_id}:{version}` (e.g., `remaker-digital-001:1`). `config_state` is a property, NOT part of the ID.
- Always use `get_active()` to fetch, then use its `.id` field for patch operations. Do NOT construct IDs like `{tenant_id}:active`.

## TenantScopedRepository.read()
Requires TWO args (partition_key, document_id). Use `get_active()` for operational access, `read()` only when you have the exact ID.

## create() vs upsert() (D52)
- `create()` → 409 if ID exists. `upsert()` → create-or-replace.
- Use `upsert()` when document may exist from previous state transition. Use `create()` only when certain no document with that ID exists.
