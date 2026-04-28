# Onboarding — Operational Lessons

> Full reference: KB DOC-ONBOARDING

## Widget key dual-storage
Rotation must update BOTH TenantDocument (hash) AND PreferencesDocument (raw). Original code only updated one.

## PreferencesDocument may not exist at provisioning
Brand-new tenants lack prefs doc until first draft save. Wrap in try/except.

## PreferencesDocument ID format
`{tenant_id}:{version}`, NOT `{tenant_id}:active`. Use `get_active()` first.

## Config cache invalidation
Direct PreferencesDocument patches (bypassing ConfigProcessor) must call `_invalidate_cache(tenant_id)`.
