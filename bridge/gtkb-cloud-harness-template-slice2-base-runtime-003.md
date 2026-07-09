NEW
author_identity: claude
author_harness_id: B
author_session_context_id: f0e664f2-35ef-4d46-86a5-5a828f73d30b
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive prime-builder

# Post-Implementation Report — Cloud-Harness Template Slice 2 (base runtime + OpenRouter re-base)

Work Item: WI-5078
Umbrella Work Item: WI-5078
Project: PROJECT-GTKB-CLOUD-HARNESS-TEMPLATE
Project Authorization: PAUTH-PROJECT-GTKB-CLOUD-HARNESS-TEMPLATE-20260708
Responds to: gtkb-cloud-harness-template-slice2-base-runtime (GO at -002)
target_paths: ["scripts/cloud_harness_base.py", "scripts/openrouter_harness.py", "platform_tests/scripts/test_cloud_harness_base.py", "platform_tests/scripts/test_openrouter_harness.py"]

## Implementation Summary

Slice 2 of `PROJECT-GTKB-CLOUD-HARNESS-TEMPLATE` is implemented per the GO'd proposal and `ADR-CLOUD-HARNESS-TEMPLATE-001`:

1. **New base runtime `scripts/cloud_harness_base.py`** (framework-free): owns connection/transport, bounded retry/backoff, fail-closed guard-adapter enforcement, author-metadata injection, config loading, tool dispatch, and the framework-free tool-call loop. Adopters supply the five varying axes via an immutable `AdopterProfile` (`endpoint`, `auth_env_key`, `dialect`, provider routing key + config path, `hook_tier`).
2. **Dialect seam**: `openai-chat` is implemented concretely (the shared `openai_chat_completion` transport). `resolve_dialect_chat_func` returns the strategy for `openai-chat` and raises an explicit slice-3 `NotImplementedError` sentinel for `ollama-native` and `anthropic-messages` (defined seam points, not silent no-ops).
3. **OpenRouter (F) re-based**: `scripts/openrouter_harness.py` is now a thin adopter — it declares the OpenRouter `AdopterProfile` (endpoint `https://openrouter.ai/api/v1`, auth env-key NAME `OPENROUTER_API_KEY`, `openai-chat` dialect, guard-adapter hook tier) and delegates all machinery to the base. Its historical public surface is preserved via thin wrappers + re-exports; `OpenRouterHarnessError` is aliased to the base `CloudHarnessError` so existing error-matching behavior is unchanged.
4. **New base regression test `platform_tests/scripts/test_cloud_harness_base.py`** (18 tests) exercises the base directly with a synthetic (non-OpenRouter) `AdopterProfile`, proving the base is adopter-agnostic.
5. **No shim deleted**; no dialect beyond `openai-chat` implemented; no doctor/parity/other-shim change (slice boundary held).

## Recommended Commit Type

`feat:` — slice 2 adds a net-new base runtime module (`scripts/cloud_harness_base.py`) and a new capability surface (config-driven cloud-harness base + dialect seam), with the OpenRouter re-base and new regression tests as supporting changes.

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this report carries forward all relevant governing specifications from the proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification section maps executed tests to the linked specifications.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge audit-trail + verification discipline govern this report.
- `ADR-CLOUD-HARNESS-TEMPLATE-001` — the approved architecture this slice implements (base runtime, five axes, guard enforcement by construction, slice 2 = base + OpenRouter re-base).
- `SPEC-INTAKE-9ec893` — the reusable-integration principle; the base makes the integration reusable so only model/config/endpoint/dialect/hook-tier vary.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — Layer-3 fail-closed guard adapter, enforced by the base for every adopter by construction.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` — the fail-closed guard/tool-parity contract whose enforcement mechanism the base generalizes (the generalized DCL artifact remains slice 3).
- `GOV-ENV-LOCAL-AUTHORITY-001` — the base references the auth token by env-key NAME only; no literal token is embedded in source.
- `ADR-OLLAMA-HARNESS-ADOPTION-001` — the framework-free precedent the base preserves.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the base is a durable tracked module; the OpenRouter shim's hand-rolled machinery consolidates behind it (superseded-but-not-deleted).
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — the guard-adapter floor is enforced mechanically in the base for every adopter.
- `.claude/rules/project-root-boundary.md` — all changed files are within `E:\GT-KB` (`scripts/`, `platform_tests/scripts/`).

## Prior Deliberations

- `DELIB-20260708-BUILD-REUSABLE-DIRECT-CLOUD-HARNESS-TEMPLATE` (owner_decision) — the authorizing owner directive for the template + OpenRouter-first-adopter proof.
- `ADR-CLOUD-HARNESS-TEMPLATE-001` — the slice-1 design decision this slice implements.
- `DELIB-S422-OR-FRAMEWORK-CHOICE` — framework-free tool loop; preserved by the base.
- `DELIB-S422-OR-CONFIG-GENERALIZATION` — `.api-harness/` config home; the base reads the same generalized config the shim read (no config migration this slice).
- `DELIB-S422-OR-REGISTRY-INTEGRATION` — OpenRouter's registry identity (harness F, type openrouter); preserved unchanged by the re-base.

## Requirement Sufficiency

Existing requirements sufficient. No new or revised requirement was needed; slice 2 mutated source/test only, within the already-active PAUTH and the VERIFIED slice-1 ADR.

## Specification-Derived Verification

All tests executed from the project venv interpreter (`groundtruth-kb/.venv/Scripts/python.exe -m pytest`). Both code-quality gates run on every changed `.py`.

| Linked spec | Derived test / assertion | Evidence / command | Result |
|---|---|---|---|
| `ADR-CLOUD-HARNESS-TEMPLATE-001` (base owns machinery; config-driven) | base parses the five-axis `AdopterProfile` + exposes shared machinery | `test_cloud_harness_base.py::test_profile_accepts_five_axis_config`, `::test_load_routing_config_filters_to_adopter_provider`, `::test_resolve_model_default_and_skill` | PASS |
| `ADR-CLOUD-HARNESS-TEMPLATE-001` (OpenRouter re-base preserves behavior) | existing OpenRouter regression tests pass unchanged against the re-based shim | `pytest platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_openrouter_routing_deepseek.py` → **49 passed** | PASS |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` (Layer-3 fail-closed guard) | base refuses tool execution when the guard denies OR is unavailable OR emits empty output | `test_cloud_harness_base.py::test_guard_denial_fails_closed`, `::test_guard_unavailable_fails_closed`, `::test_guard_empty_output_fails_closed` | PASS |
| `DCL-OLLAMA-TOOL-PARITY-GATE-001` (generalized enforcement) | base guard enforcement mirrors the ollama fail-closed tool-parity semantics; same guard sequence for OpenRouter | base guard tests above + `test_openrouter_harness.py::test_bridge_write_invokes_required_guard_sequence` (unchanged, passing) | PASS |
| `SPEC-INTAKE-9ec893` (direct-cloud, config-driven) | adopter profile requires a direct-cloud endpoint; no localhost bridge path in the base | `test_cloud_harness_base.py::test_profile_requires_direct_cloud_endpoint` | PASS |
| `GOV-ENV-LOCAL-AUTHORITY-001` (auth by env-key NAME) | profile requires an `auth_env_key` NAME; author-metadata env built from profile identity | `test_cloud_harness_base.py::test_profile_requires_auth_env_key_name`, `::test_author_metadata_env_uses_profile_identity` | PASS |
| ADR dialect seam (slice 2 vs slice 3) | `openai-chat` resolves to a callable; both slice-3 dialects raise `NotImplementedError` | `test_cloud_harness_base.py::test_openai_chat_dialect_resolves_to_callable`, `::test_slice3_dialects_raise_not_implemented_sentinel[ollama-native]`, `[anthropic-messages]` | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` / code-quality | ruff check AND ruff format --check clean on all changed `.py` | `ruff check` → exit 0; `ruff format --check` → exit 0 (scripts/cloud_harness_base.py, scripts/openrouter_harness.py, platform_tests/scripts/test_cloud_harness_base.py) | PASS |

Aggregate run (final formatted code): `67 passed, 1 warning` (49 OpenRouter regression + 18 new base tests). The one warning is a pre-existing `asyncio_mode` config warning unrelated to this slice.

## Behavior-Preservation Proof (GO -002 finding P3 #2)

The re-base did **not** modify either OpenRouter regression test file:

- `platform_tests/scripts/test_openrouter_routing_deepseek.py`: unmodified vs HEAD (absent from `git diff --name-only`); file mtime `2026-06-12` (a month before this slice).
- `platform_tests/scripts/test_openrouter_harness.py`: **not written by this session** — its file mtime is `2026-07-08T01:23:16Z`, ~22 hours before this slice's implementation-start packet (`2026-07-08T23:27:04Z`). It appears in `git diff` vs HEAD only because of **pre-existing uncommitted work** (WI-5064 SSL-retry hardening + WI-5066 silent-stall — see the untracked `bridge/gtkb-wi5064-openrouter-ssl-retry-hardening-*.md` and `bridge/gtkb-wi5066-openrouter-silent-stall-timeout-*.md`, and the `test_wi5064_*`/`test_wi5060_*` tests inside that file). Those changes predate and are unrelated to the re-base. My three changed files (`cloud_harness_base.py`, `openrouter_harness.py`, `test_cloud_harness_base.py`) all carry mtime `2026-07-08T23:43Z` (this session).

Stronger than "unmodified": the 49 regression tests — **including** the pre-existing WI-5064/WI-5066 SSL-retry tests — all pass against the re-based shim, so the re-base preserves both the committed behavior and the in-flight uncommitted behavior.

## GO Findings Addressed (from -002)

- **[P3] Framework-free vs SDK**: confirmed. `scripts/cloud_harness_base.py` imports only the standard library (`urllib`, `ssl`, `json`, `subprocess`, `functools`, `re`, `fnmatch`, `contextlib`, `os`, `sys`, `time`, `dataclasses`, `pathlib`, `email.utils`, `tomllib`/`tomli`) plus existing GT-KB helpers (`gtkb_session_id`, `sdk_bridge_bash_guard`). No heavyweight agent framework; the "openai-chat" transport is a thin `urllib.request` POST, matching the shim's prior transport exactly.
- **[P3] Behavior-preservation proof**: provided above (git-diff + mtime evidence + the two test files' disposition + 49 passing regression tests, unchanged).
- **[P3] Dialect sentinel**: `resolve_dialect_chat_func` raises `NotImplementedError` (message cites "slice-3 seam point") for both `ollama-native` and `anthropic-messages`; asserted for both via the parametrized `test_slice3_dialects_raise_not_implemented_sentinel`. Not a silent no-op.

## Slice Boundary Held

- No shim deleted: `scripts/openrouter_harness.py` remains (now thin); `ollama_harness.py`, `cursor_harness.py` untouched.
- Only `openai-chat` implemented; `ollama-native`/`anthropic-messages` are guarded slice-3 seam points.
- No doctor check, harness-parity surface, generalized tool-parity DCL, or `.api-harness/` config changed (all slice-3/slice-4 per the ADR).

## Files Changed

- `scripts/cloud_harness_base.py` — NEW (base runtime).
- `scripts/openrouter_harness.py` — MODIFIED (re-based to thin adopter; public surface preserved).
- `platform_tests/scripts/test_cloud_harness_base.py` — NEW (18 base regression tests).
- (`platform_tests/scripts/test_openrouter_harness.py` and `test_openrouter_routing_deepseek.py` — NOT modified by this slice; used as the unchanged behavior-preservation proof.)

## Owner Decisions / Input

- `AskUserQuestion` (2026-07-08, `DELIB-20260708-BUILD-REUSABLE-DIRECT-CLOUD-HARNESS-TEMPLATE`): "How should I structure the reusable direct-cloud harness template program?" → **Template + OpenRouter as first adopter**.
- Owner session directive (2026-07-08): continue the program at slice 2 (implementation), building the base runtime + OpenRouter re-base this session.

These authorize the work. No new owner decision was required: slice-2 source implementation is covered by the active `PAUTH-PROJECT-GTKB-CLOUD-HARNESS-TEMPLATE-20260708` and the VERIFIED `ADR-CLOUD-HARNESS-TEMPLATE-001`, executed under the GO at -002 plus an implementation-start packet.

## Risks / Rollback

- **Risk:** the re-base regresses OpenRouter behavior. **Mitigation/evidence:** all 49 regression tests pass unchanged; the shim's public surface (error class, functions, constants, guard sequences) is preserved.
- **Risk:** the base guard generalization weakens fail-closed semantics. **Mitigation/evidence:** explicit deny + unavailable + empty-output fail-closed tests in the base module.
- **Rollback:** the base module and the base test are new (removable); `scripts/openrouter_harness.py` reverts to its pre-slice-2 content in a single-file revert. No governance, config, registry, or sibling shim was mutated.
