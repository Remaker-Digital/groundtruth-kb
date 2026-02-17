# Refactoring and Modularity Assessment

Date: 2026-02-17  
Project: Agent Red Customer Engagement  
Scope: Identify refactor/modularity opportunities to:

1. reduce code quantity to test and maintain  
2. reduce context-token load for analysis/manipulation  
3. reduce physical footprint in production deployment

## Executive Summary

The project is feature-rich but has accumulated several large monoliths and repeated scaffolding patterns.  
Most impact comes from:

- decomposing large backend modules (`src/main.py`, config/repository subsystems)
- consolidating duplicated admin UI logic between shells
- extracting repeated script/test bootstrap logic
- trimming production artifacts (especially sourcemaps and static asset packaging approach)

The highest ROI refactor sequence is:

1. backend composition refactor (`src/main.py` + service registration)
2. configuration subsystem split (`tenant_config_schema`, `tenant_config_processor`, `repository`)
3. admin UI convergence (shared page logic + shell adapters)
4. operational script/tooling consolidation
5. production artifact footprint optimization

## Evidence Snapshot (What Was Measured)

### Repository shape

- Files scanned (`src/admin/widget/scripts/infrastructure/tests`): `348`

### Largest backend Python modules (by lines)

- `src/multi_tenant/tenant_config_schema.py`: `2221`
- `src/multi_tenant/repository.py`: `2178`
- `src/main.py`: `2002`
- `src/multi_tenant/fine_tuning_pipeline.py`: `1566`
- `src/multi_tenant/tenant_config_processor.py`: `1390`
- `src/multi_tenant/tenant_config_api.py`: `1302`
- `src/chat/pipeline.py`: `1293`
- `src/multi_tenant/cosmos_schema.py`: `1282`

### Largest admin source files (excluding node_modules/dist)

- `admin/shared/WidgetConfigurator.tsx`: `78262` bytes
- `admin/shared/KnowledgeBaseManager.tsx`: `57230`
- `admin/standalone/layouts/StandaloneLayout.tsx`: `47047`
- `admin/standalone/pages/Widget.tsx`: `44820`
- `admin/shared/TeamManager.tsx`: `43713`
- `admin/shared/hooks/index.ts`: `40498`

### Large tests indicating maintenance coupling

- `tests/multi_tenant/test_activation_service.py`: `1907` lines
- `tests/integrations/test_http_billing.py`: `1034`
- `tests/persistent_memory/test_fine_tuning.py`: `989`
- `tests/multi_tenant/test_config_api_activation.py`: `888`
- `tests/multi_tenant/test_cosmos_repository.py`: `870`

### Duplication signals

- `.env.local` loader patterns across scripts/tests (`_env_local` / `_env_path`): `~54` hits
- Repeated Pydantic alias boilerplate (`model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)`): `62` hits
- Startup hooks in `src/main.py` (`@app.on_event("startup")`): `35` entries

### Deployment footprint signals

- Dist assets copied into API image:
  - `admin/shopify/dist`: `3.16 MB`
  - `admin/standalone/dist`: `5.8 MB`
  - `widget/dist`: `0.07 MB`
- Sourcemaps present in shipped admin dist:
  - Standalone map size: `~4.53 MB`
  - Shopify map size: `~2.12 MB`
- Sourcemaps enabled in build configs:
  - `admin/standalone/vite.config.ts:25`
  - `admin/shopify/vite.config.ts:24`

## Refactor Opportunities

## 1) Decompose `src/main.py` into an application composition layer

### Observed issue

`src/main.py` mixes:
- app instantiation
- middleware
- static SPA serving
- auth/password reset logic
- service wiring
- many startup/shutdown hooks

### Refactor

- Create `src/app/` package:
  - `factory.py` (create_app)
  - `routers.py` (router registration map)
  - `lifecycle.py` (startup/shutdown orchestration)
  - `static_mounts.py` (admin/widget serving)
  - `dependencies.py` (container/service locator)

### Impact

- Maintenance/test: isolate startup wiring and reduce blast radius.
- Context tokens: smaller files for focused edits.
- Footprint: neutral directly, but enables cleaner service boundaries.

### Priority

`P0`

## 2) Split repository monolith by collection domain

### Observed issue

`src/multi_tenant/repository.py` (2178 lines) centralizes many repositories.

### Refactor

- Move to per-domain modules:
  - `repositories/tenant.py`
  - `repositories/preferences.py`
  - `repositories/conversation.py`
  - `repositories/team.py`
  - `repositories/platform_config.py`
  - shared base in `repositories/base.py`

### Impact

- Maintenance/test: fewer giant tests and clearer ownership.
- Context tokens: repository reasoning no longer requires loading 2k+ lines.
- Footprint: neutral.

### Priority

`P0`

## 3) Convert `tenant_config_schema.py` to data-driven schema registry

### Observed issue

`src/multi_tenant/tenant_config_schema.py` (2221 lines) is mostly declarative metadata.

### Refactor

- Move field definitions to structured data (`yaml/json`) under `config/schema/`.
- Keep a thin typed loader + validator adapter in Python.
- Generate API-facing metadata from the registry.

### Impact

- Maintenance/test: fewer manual edits and easier schema review.
- Context tokens: large token-heavy constant blocks removed from core code.
- Footprint: slight reduction in Python code complexity.

### Priority

`P0`

## 4) Split `tenant_config_processor` into read/write/version/audit components

### Observed issue

`src/multi_tenant/tenant_config_processor.py` (1390 lines) handles validation, merge, caching, versioning, rollback, and auditing.

### Refactor

- `config/read_service.py`
- `config/write_service.py`
- `config/versioning.py`
- `config/cache.py`
- `config/audit.py`

### Impact

- Maintenance/test: targeted unit tests with less fixture overhead.
- Context tokens: narrow task-specific analysis.
- Footprint: neutral.

### Priority

`P1`

## 5) Consolidate admin shells into “shared page + shell adapter” model

### Observed issue

Shopify pages are thin wrappers around shared components, while standalone has large custom pages (example mismatch: `admin/shopify/pages/Configuration.tsx` vs `admin/standalone/pages/Configuration.tsx`).

### Refactor

- Introduce `admin/shared/pages/*` as canonical page logic.
- Keep shell-specific wrappers only for frame/chrome concerns:
  - Shopify layout/app bridge concerns
  - Standalone auth/session concerns

### Impact

- Maintenance/test: one page implementation instead of drifted twins.
- Context tokens: fewer code paths to load.
- Footprint: reduced bundle duplication over time.

### Priority

`P1`

## 6) Break large shared UI components into feature slices

### Observed issue

Very large UI modules (`WidgetConfigurator`, `KnowledgeBaseManager`, `TeamManager`) and giant `admin/shared/hooks/index.ts`.

### Refactor

- Feature folders per domain:
  - `admin/shared/features/widget/*`
  - `admin/shared/features/knowledge/*`
  - `admin/shared/features/team/*`
- Move API client logic to domain services.
- Keep components presentational where possible.

### Impact

- Maintenance/test: smaller components and hook scopes.
- Context tokens: improves partial-file reasoning.
- Footprint: modest by enabling better code splitting.

### Priority

`P1`

## 7) Remove repeated `.env.local` loading code via shared utility

### Observed issue

Many scripts/tests duplicate env bootstrap logic (`_env_local`, `_env_path`, manual `partition("=")` parsing).

### Refactor

- Add `scripts/_env.py` (or `src/devtools/env_loader.py`) and reuse.
- Provide strict mode (`required vars`) and fail-fast diagnostics.

### Impact

- Maintenance/test: less copy/paste drift.
- Context tokens: cleaner script files.
- Footprint: minor code reduction.

### Priority

`P1`

## 8) Introduce base API model config to eliminate repeated Pydantic boilerplate

### Observed issue

`model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)` repeats broadly.

### Refactor

- Create shared base model (for API DTOs) with default `model_config`.
- Override only when needed.

### Impact

- Maintenance/test: less repetitive model setup.
- Context tokens: reduce noise.
- Footprint: minor code reduction.

### Priority

`P2`

## 9) Production artifact footprint optimization

### Observed issue

- Admin sourcemaps are enabled and appear in dist copied into runtime image.
- API container serves backend plus both admin SPAs plus widget static assets.

### Refactor

1. Disable sourcemaps for production admin builds.
2. Use env-conditional sourcemaps (`true` only in non-prod).
3. Consider serving admin static assets from CDN/Blob + separate frontend deployment boundary.
4. Keep API image focused on backend and widget endpoint only (or at least no `.map` files).

### Impact

- Maintenance/test: cleaner release artifacts.
- Context tokens: neutral.
- Footprint: direct reduction in image and transfer size.

### Priority

`P0` for sourcemap cleanup, `P2` for full static hosting split.

## 10) Separate high-complexity pipelines into plugins/modules

### Observed issue

Large algorithmic/service modules (`chat/pipeline.py`, `fine_tuning_pipeline.py`, `gdpr_services.py`, `alert_delivery.py`) combine policy, orchestration, and I/O.

### Refactor

- Split by stage/provider/policy:
  - pipeline stages as pluggable contracts
  - provider adapters (email/alerts/storage)
  - policy engines isolated from I/O

### Impact

- Maintenance/test: easier mocking and contract testing.
- Context tokens: lower per-change context requirements.
- Footprint: neutral.

### Priority

`P2`

## Suggested Implementation Order

1. `P0`: `main.py` composition split, repository split, config schema externalization plan, production sourcemap removal.
2. `P1`: config processor decomposition, admin shell convergence, env-loader consolidation.
3. `P2`: Pydantic base model cleanup, deeper pipeline/plugin modularization, static hosting boundary.

## Expected Outcome (Qualitative)

If executed, this refactor program should:

- materially reduce test surface per change set (smaller bounded modules)
- reduce prompt/context load for AI-assisted development
- reduce deployable artifact size and improve runtime package hygiene

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
