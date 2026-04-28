# Activation Model — Operational Lessons

> Full architecture: KB DOC-ACTIVATION-MODEL

## Config empty-string override trap (S76)
`_preferences_to_config()` (in `config/field_mapping.py`) filters `None` but NOT `""`. Stored `""` overrides `platform_default` via `{**defaults, **stored}`. Use `None` (not `""`) when resetting fields that have a platform_default.

## Cache invalidation after direct patches (S85)
Any code that patches PreferencesDocument directly (bypassing ConfigProcessor) must call `get_config_processor()._invalidate_cache(tenant_id)` afterward. The 60-second TTL cache serves stale data otherwise. `_invalidate_cache()` is defined at `config/processor.py:1289`.

## D52 upsert trap
When creating DRAFT from PREVIOUS via `restore_previous()`, the system uses `container.upsert_item()`. If a DRAFT already exists, it's silently overwritten — no conflict error. This is intentional (latest restore wins) but can surprise callers expecting idempotency.
