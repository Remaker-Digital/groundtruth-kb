# Testing Patterns

## Mock Patching Rules

### Lazy import patching
`from x.y import z` in function body → must patch at **source**: `patch("x.y.z")`, NOT `patch("consumer.z")`.
- Example: `cosine_similarity` imported inside `kb_conflict_scanner.py` → patch `"src.multi_tenant.semantic_cache.cosine_similarity"`
- Example: `get_secret_service` lazy-imported inside `admin_integration_api.disconnect_integration()` → patch `"src.multi_tenant.tenant_secret_service.get_secret_service"`
- If the middleware has `try/except: pass` (like SLA monitor in security_middleware), do NOT patch — it handles missing gracefully

### R1 split patch targets (session 31)
After `main.py` split into `src/app/*.py`, patch at the SOURCE module:
- `patch("src.app.standalone_auth._send_admin_reset_email")`, NOT `patch("src.main._send_admin_reset_email")`
- `conftest.py` patches: `_main_mod` → `_lifecycle_mod` and `_health_mod`
- Lazy imports inside handler function bodies cannot be patched via `patch.object()` — they re-import on each call

### Other mock pitfalls
- **Class/static methods**: `patch("module.ClassName.method_name")`, NOT `patch.object(type(mock_instance), ...)`
- **MagicMock in numeric comparisons**: `if value >= 0.85` raises TypeError. Use `side_effect` returning actual floats.
- **FastAPI Query defaults in direct calls**: `Query(0)` is `FieldInfo`, NOT int. Pass explicit values when calling endpoints directly.
- **FakeAsyncIterator for Cosmos DB**: Tests simulating `query_items()` need `__aiter__`/`__anext__` helper.
- **Min-score filtering**: Results must include `"score"` key (not just `"rrf_score"`)
- **TierGate enum**: Values are `PROFESSIONAL_PLUS` (not `PROFESSIONAL`)

## Activation Service Mock Patterns

- **validate_config() argument order**: `(tenant_id, config)`, NOT `(config, tenant_id)`
- **ConfigValidationResult**: Pydantic model — use `.valid`, NOT `.get("valid")`
- **Mock repos**: Must include `get_quick_actions_active` and `get_page_assignments_active` (activation-aware methods)
- **`get_activation_service` replaces `get_config_processor`** as FastAPI dependency in activation endpoints
- **Migration compat mocks**: Return `ConfigValidationResult(valid=True, errors=[], warnings=[])`, NOT plain dict

## Thermal-Safe Test Execution

**Problem:** ~4,500 tests on single core → sustained CPU boost → BSODs on Windows 11.

**Script:** `scripts/run-tests-thermal-safe.ps1` — 5-batch orchestrator with cooling pauses.
- **Defaults:** `-Workers 4 -CoolDown 30`
- **Dependencies:** `pytest-xdist>=3.5.0`, `pytest-timeout>=2.3.0`

### Batch Layout
| # | Name | Tests | Mode |
|---|------|-------|------|
| 1 | core-a | tests/multi_tenant/ (~2,777) | -n 4 |
| 2 | core-b | tests/unit/ + root + migrations (~938) | -n 4 |
| 3 | agents-chat | tests/agents/ + chat + memory + eval (~411) | -n 4 |
| 4 | integrations | tests/integrations/ + security/mocked (~322) | -n 4 |
| 5 | sequential | tests/integration/ + regression + performance + live security | NO xdist, --timeout=60 |

### Run Commands
```
.\scripts\run-tests-thermal-safe.ps1 -SkipLive          # Full thermal-safe
.\scripts\run-tests-thermal-safe.ps1 -Batch agents-chat  # Single batch
.\scripts\run-tests-thermal-safe.ps1 -Fast               # CI mode (no cooling)
.\scripts\run-tests-thermal-safe.ps1 -Coverage -SkipLive  # With coverage
```

### Parallel-Unsafe Directories
`tests/integration/` (TestClient race), `tests/regression/` (session-scoped fixtures), `tests/performance/` (Locust), `tests/security/test_*_live.py` — ALL in batch 5 (sequential).

## Operational Lessons

### ConfigFieldDefinition.step_order must be float
`step_order` in `schema/models.py:187` is `float`, not `int`. `fields.yaml` uses fractional values (e.g., 1.5, 2.5) for insertion ordering.

### patch.dict env var interference (S84)
`patch.dict("os.environ", {})` without `clear=True` merges with real env. Always explicitly set higher-priority env vars to empty string, or use `clear=True`.

### Count/set assertion maintenance
Tests like `test_registry_loads_79_fields`, `test_billing_channel_values` must be updated when adding new fields/enums.

### Regression test path
At `tests/regression/test_upgrade_regression.py` (NOT `tests/integration/test_production_regression.py`). The conftest loads `.env.local` via `scripts/_env.load_env_local()`.

### T0 failures after re-seed
401 errors after re-seed → stale `.env.local` `PREVIEW_WIDGET_KEY`. Fix: rotate widget key, update `.env.local`, re-run.

### Two-tier consent test pattern (S79)
Must mock `PreferencesRepository` with `consent_collection_enabled: True` to exercise denied-consent path. Default (false) triggers implied GRANTED.

### Global exception handler
`RuntimeError("not initialized")` → 503 (not 500). Tests expecting Cosmos DB down should assert 503.

### PCM vectorization patch target (S79)
`patch("src.multi_tenant.conversation_vectorizer.get_vectorizer", ...)` — NOT `src.app.background.get_vectorizer` (lazy import).

### PII scrubbing AsyncMock compatibility (S27)
Sync method `set_pii_scrubber()` on AsyncMock sessions causes RuntimeWarning. Fix: use explicit `session.set_pii_scrubber = MagicMock()`.

### Cosmos cosine_similarity mock target
`cosine_similarity` in `kb_conflict_scanner.py` is lazy-imported — mock at source: `"src.multi_tenant.semantic_cache.cosine_similarity"`.

### Quality test prerequisites
Chat pipeline must be initialized (201 not 503). Golden dataset expects KB data — seed first. Jailbreak scenarios may return empty responses (critic rejection) — expected.

### Test tenant known issues
- Config save endpoint requires `fields` wrapper body, not flat JSON (422 otherwise)
- Re-running seed regenerates ALL API keys — update credentials + scripts
- Cosmos direct writes (seed_conversations) bypass AI pipeline

## Container Test Infrastructure (S209)

### Test Host Architecture
- **Test host:** `agent-red-test-host` (internal ingress, port 8001, scale 0→1)
- **Suites defined in:** `test_host/suites.py` — `SUITE_CONFIGS` dict
- **Runner:** `test_host/runner.py` — subprocess pytest orchestrator
- **Results:** Progressive upserts to Cosmos `platform_config` container

### Staging vs Development Test Separation
- **Staging (container):** Excludes tests requiring external services (Azure OpenAI, NATS, Stripe/Shopify live, Tenant B keys, CI workflows, docs/ files)
- **Development (local):** Full suite via `scripts/test_pipeline.py` — includes all external service tests when env vars are set
- **Exclusions defined in:** `test_host/suites.py` via `--ignore=` in `pytest_args`

### Skip-as-Fail Policy (S209)
- Skipped/xfailed tests map to `"fail"` status in `test_host/runner.py` (line 274)
- Skip reason captured in failure detail for diagnosis
- Infrastructure-dependent tests are EXCLUDED from suites rather than skipped

### Tests Excluded from Container Suites
**Core:** `test_s153_batch10_spec_verification.py` (reads CLAUDE.md project content)
**Integration:** `test_azure_services.py`, `test_integration_real_services.py`, `test_nats_jetstream.py`
**Security:** `test_ci_tooling.py`, `test_documentation_cleanup.py`, `test_data_integrity_live.py`, `test_resilience_live.py`, `test_tenant_isolation_live.py`

### Container File Availability
Files available in test container (via Dockerfile.test COPY):
- `src/`, `tests/`, `scripts/`, `config/`, `test_host/`
- `pyproject.toml`, `shopify.app.toml`, `CLAUDE.md`
- `widget/dist/`, `widget/src/`, all `admin/*/` dirs
- **NOT available:** `docs/`, `memory/`, `.claude/`, `.github/workflows/`

### Path Existence Test Discovery
`tests/test_host/test_path_discovery.py` scans all `Path("...").exists()` calls in test files and verifies each path is COPY'd in Dockerfile.test. Run this after adding new file-existence tests.

### Build via GitHub Actions (NOT az acr build)
See `memory/deployment.md` § "Test Host Container" for the full procedure.
