NEW
author_identity: claude
author_harness_id: B
author_session_context_id: c6f54cd8-c03e-4eda-bb2f-97d2c392b40f
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb, 1m context

# Defect-Fix Proposal - Provider-Scoped Model Loading in the Ollama Harness (WI-4473)

bridge_kind: prime_proposal
Document: gtkb-ollama-harness-provider-scoped-model-validation
Version: 001
Date: 2026-06-12 UTC

Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4473
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING

target_paths: ["scripts/ollama_harness.py", "platform_tests/scripts/test_ollama_provider_scoped_routing.py"]

## Claim

`scripts/ollama_harness.py::load_routing_config` builds a `ModelRoute` for **every** `[models.<key>]` row in the shared `.api-harness/routing.toml`, regardless of each row's `provider` field. `validate_advertised_models` (`scripts/ollama_harness.py:161-170`) then compares **every** configured `model_id` against the local Ollama `/api/tags` inventory. Since `.api-harness/routing.toml` now also defines `provider = "openrouter"` rows (`google/gemini-2.5-pro`, `qwen/qwen-2.5-coder-32b-instruct`) for the OpenRouter harness, those non-local model ids are never advertised by the local Ollama server, so the harness raises `OllamaHarnessError("configured model_id values are not advertised locally: ...")` and exits 1 **before any work** on every `loyal-opposition:D` dispatch (508 `subprocess_execution_failed` records in `dispatch-failures.jsonl`; the per-recipient circuit breaker trips).

This proposal scopes the Ollama harness's model loading to `provider == "ollama"` rows only, mirroring the already-provider-aware OpenRouter harness (`scripts/openrouter_harness.py:186-188`). After the fix, `validate_advertised_models` only checks Ollama-provider models against the local inventory, so the cross-provider routing.toml no longer aborts the Ollama harness. This is the durable fix that restores the cheapest LO reviewer (Ollama, prefer-local precedence 10) to the dispatch substrate.

## Defect / Reproduction

**Root cause (code).** In `load_routing_config` (`scripts/ollama_harness.py:216-228`), the model-building loop iterates `models_raw.items()` and constructs a `ModelRoute` for each row after only a row-shape check (`:218`). It never reads `row.get("provider")`. The resulting `config.models` therefore contains both Ollama and OpenRouter routes. `validate_advertised_models` (`:167`) computes `configured = {route.model_id for route in config.models.values()}` over **all** providers and raises when any configured model id is absent from the local `/api/tags` set (`:168-170`). `main` (`scripts/ollama_harness.py:861-862`) calls `call_ollama_tags` then `validate_advertised_models`, so the abort happens at startup before any tool loop runs.

**Contrast (already-correct sibling).** `scripts/openrouter_harness.py::load_routing_config` keeps its **own** copy of the loader and at `:186-188` does `provider = row.get("provider"); if provider != "openrouter": continue` — it skips non-OpenRouter rows. The two harnesses hold independent loaders, so the Ollama harness simply never received the symmetric filter (it predates the multi-provider routing.toml). The `[routing.ollama]` table that the Ollama harness reads (`:230`) already scopes routing to Ollama; only the `models` dict and its validation leak cross-provider rows.

**Incident linkage (2026-06-11/12).** `dispatch-failures.jsonl` shows 508 `loyal-opposition:D` `subprocess_execution_failed` records; the harness server is healthy and harness D is correctly registered (LO precedence 10). The failing dispatch added churn to the dispatch substrate and contributed to the 2026-06-11 dispatch-storm investigation noise (WI-4472 is the storm root-cause fix; this WI removes the Ollama-side failure source).

**Why it matters now.** Ollama is the cheapest reviewer (local models are free; `qwen3-coder-next:cloud` proven good). With dispatch currently held OFF by the emergency kill-switch, restoring a clean Ollama launch path is a prerequisite for re-enabling the cheap-harness LO pool.

## In-Root Placement Evidence

Both target paths are inside `E:\GT-KB`: `scripts/ollama_harness.py` and `platform_tests/scripts/test_ollama_provider_scoped_routing.py`. The edited config surface `.api-harness/routing.toml` is read-only for this WI (no routing.toml mutation in scope; the OpenRouter slug change is the separately-sequenced WI-4476).

## Requirement Sufficiency

Existing requirements sufficient. The governing requirement set — `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001` (the routing.toml schema, including the per-model `provider` field semantics) plus `ADR-OLLAMA-HARNESS-ADOPTION-001` (the framework-free Python shim that loads `.api-harness/routing.toml`) — already constrains the corrected behavior: the Ollama harness must consume only its own provider's routes. No new or revised requirement is required before implementation. This proposal makes the implementation conform to the existing multi-provider routing schema.

## Standing Fast-Lane Eligibility

This work item (WI-4473) qualifies for the standing reliability fast-lane (`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`) governed by `GOV-RELIABILITY-FAST-LANE-001` because:

- **Defect/Reliability focus:** It is a P1 defect fix that removes a startup-abort failure class (508 failed LO dispatches) from the cross-harness dispatch substrate.
- **Authorized mutation classes:** The implementation consumes only `source` (edit `scripts/ollama_harness.py`) and `test_addition` (new `platform_tests/scripts/test_ollama_provider_scoped_routing.py`) — both within the standing PAUTH's `allowed_mutation_classes`.
- **No forbidden mutations:** No production deployment, force-push, or specification deletion (the PAUTH's `forbidden_operations`) is in scope; no formal spec mutation and no unrelated cleanup.
- **Membership coverage:** WI-4473 is an active member of `PROJECT-GTKB-RELIABILITY-FIXES`; the standing PAUTH covers work items by active project membership (`included_work_item_ids` is null; `scope_summary` = "covers work items by active project membership (no per-fix authorization)").

## Specification Links

- `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001` — **Primary domain spec.** Defines the `.api-harness/routing.toml` schema including the per-model `provider` field. This fix makes the Ollama harness loader honor `provider` per the schema.
- `ADR-OLLAMA-HARNESS-ADOPTION-001` — the Ollama harness adoption decision (framework-free Python shim, static routing.toml). The fix preserves the adopted shim's contract while scoping it to its provider.
- `GOV-RELIABILITY-FAST-LANE-001` — **Standing Reliability Fast-Lane Governance.** Governs eligibility and verification for `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`; eligibility evidence is in `## Standing Fast-Lane Eligibility` above.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` remains the canonical workflow state; this proposal follows the file-bridge protocol.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all changed paths are in-root platform paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites all relevant cross-cutting specs here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan maps the corrected behavior to executable tests derived from the linked specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project / Work Item / Project Authorization metadata present above.
- `GOV-STANDING-BACKLOG-001` — WI-4473 is the standing-backlog work item, an active member of PROJECT-GTKB-RELIABILITY-FIXES.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the 2026-06-12 diagnosis is captured as WI-4473; this proposal is the artifact-lifecycle progression from captured defect to scoped fix.

## Prior Deliberations

- WI-4473 (this work item) — records the 2026-06-12 root-cause diagnosis (provider-blind validation against local `/api/tags`) and the prescribed fix (provider-scoped loading).
- `bridge/gtkb-cross-harness-dispatch-concurrency-cap-003.md` (REVISED, awaiting LO review) — the sibling cheap-harness/reliability fix (WI-4472, the storm concurrency cap). Same project, same standing PAUTH; this proposal adopts that thread's fast-lane-linkage structure (its `-002` NO-GO required citing `GOV-RELIABILITY-FAST-LANE-001` + an eligibility section, which this proposal includes from the outset).
- `scripts/openrouter_harness.py:165-212` — the already-provider-aware sibling loader; the reference implementation this fix mirrors (`provider != "<provider>": continue`).
- `ADR-OLLAMA-HARNESS-ADOPTION-001` / operating-model.md §3 — the Phase-1 Ollama harness adoption (identity D, empty role-set at adoption; framework-free shim; static routing.toml).
- Deliberation Archive search (2026-06-12) for "ollama harness routing config provider model validation advertised local" and "cheap harness ollama provider scoped model validation openrouter deepseek routing" returned no prior decision specific to provider-scoped model loading; this is the first treatment.

## Owner Decisions / Input

- **Owner directive (2026-06-12, this session, resume from session 39746c1a):** the owner directed the cheap-harness fix program — "drive the cheap-harness fix program to VERIFIED autonomously; AUQ only for owner decisions" — and named WI-4472/WI-4473/WI-4476 as the program scope, with WI-4473 (Ollama provider-scoped model validation) explicitly to be filed as a bridge proposal. This is the owner direction to propose WI-4473.
- **Project authorization:** `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (active, project-wide; `source` + `test_addition` + `hook_upgrade`; owner authorization `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`), covering WI-4473 via active project membership.
- No NEW owner decision is required for implementation beyond the standing authorization + the per-item bridge GO. (Note: cross-harness auto-dispatch is currently held OFF by the emergency kill-switch `GTKB_NO_CROSS_HARNESS_TRIGGER=1`; this proposal therefore awaits a MANUAL Loyal Opposition review.)

## Proposed Scope

**IP-1 — Provider-scoped model loading (`scripts/ollama_harness.py`).**

In the model-building loop of `load_routing_config` (currently `:217-228`), immediately after the row-shape check (`:218-219`) and before reading `model_id`, add a provider filter mirroring `scripts/openrouter_harness.py:186-188`:

```python
provider = row.get("provider", "ollama")
if provider != "ollama":
    continue
```

- **Backward-compatibility default.** Unlike the OpenRouter loader (which uses `row.get("provider")` with no default, requiring explicit `provider = "openrouter"`), the Ollama loader defaults an absent `provider` to `"ollama"`. Rationale: Ollama is the original/default provider; a routing.toml row predating the multi-provider schema (no `provider` key) must continue to be treated as Ollama so existing single-provider configs keep loading. OpenRouter is a strictly opt-in provider, so requiring explicit opt-in there is correct and the asymmetry is intentional and documented.
- **Effect.** `config.models` then contains only Ollama-provider routes. `[routing.ollama].default_model` and `[routing.ollama].skills` reference Ollama keys, so the existing `default_model in models` check (`:234`) and `_parse_skill_routes` validation (`:240`) still pass. `validate_advertised_models` (unchanged) now compares only Ollama model ids against `/api/tags`, so the OpenRouter rows no longer cause the false "not advertised locally" abort.
- **No change** to `ModelRoute` (the OpenRouter loader likewise does not capture `provider` in its `ModelRoute`), to `validate_advertised_models`, or to `main`. The fix is a single load-time filter — minimal and idiom-consistent with the sibling harness.

**IP-2 — Tests (`platform_tests/scripts/test_ollama_provider_scoped_routing.py`; new file = clean test_addition).**

- `test_load_routing_config_loads_only_ollama_models`: a mixed-provider routing.toml fixture (Ollama + OpenRouter rows) yields a `config.models` containing only the Ollama keys; OpenRouter keys are absent.
- `test_absent_provider_row_defaults_to_ollama`: a model row with no `provider` key is loaded (backward compatibility) and is resolvable.
- `test_validate_advertised_models_passes_after_provider_filter`: the regression case — with a mixed-provider routing.toml and an advertised set containing only the Ollama model ids, `load_routing_config(project_root, advertised_model_ids=<ollama-only>)` does NOT raise (pre-fix it raised `OllamaHarnessError("configured model_id values are not advertised locally")`).
- `test_openrouter_model_ids_not_in_validated_set`: explicitly assert the OpenRouter model ids are absent from `{route.model_id for route in config.models.values()}` after loading.
- `test_default_and_skill_routes_still_resolve`: `[routing.ollama].default_model` and skill routes still resolve to Ollama `ModelRoute`s after filtering.

## Specification-Derived Verification Plan

| Spec / requirement | Derived test | Command |
|---|---|---|
| `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001` (per-model `provider` honored) | `test_load_routing_config_loads_only_ollama_models`, `test_openrouter_model_ids_not_in_validated_set` | `python -m pytest platform_tests/scripts/test_ollama_provider_scoped_routing.py -q` |
| WI-4473 (no false "not advertised locally" abort) | `test_validate_advertised_models_passes_after_provider_filter` | same |
| `ADR-OLLAMA-HARNESS-ADOPTION-001` (shim contract preserved) | `test_absent_provider_row_defaults_to_ollama`, `test_default_and_skill_routes_still_resolve` | same |
| `GOV-RELIABILITY-FAST-LANE-001` (fast-lane scope compliance) | scope inspection: changed files = exactly the two target paths; mutation classes `source` + `test_addition` only | `git diff --stat` (changed set == target_paths) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | lint + format gates on changed Python | `ruff check <files>`; `ruff format --check <files>` |

## Acceptance Criteria

1. After the fix, `load_routing_config` returns a `RoutingConfig` whose `models` dict contains only `provider == "ollama"` (or provider-absent) rows; OpenRouter rows are excluded.
2. `validate_advertised_models` no longer raises for the live `.api-harness/routing.toml` against an Ollama `/api/tags` set that advertises only the Ollama model ids.
3. A routing.toml row with no `provider` key is treated as Ollama (backward compatibility preserved).
4. `[routing.ollama].default_model` and skill routes still resolve after filtering (no regression in routing resolution).
5. New tests pass; `ruff check` and `ruff format --check` pass on every changed Python file. The change set is exactly the two target paths (fast-lane scope compliance).
6. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-ollama-harness-provider-scoped-model-validation` reports `missing_required_specs: []`; the ADR/DCL clause preflight reports no blocking gaps.

## Risks / Rollback

- **Risk — over-filtering hides a legitimately Ollama-served model.** Mitigation: the filter keys only on the explicit `provider` field; absent → Ollama (inclusive default), so no Ollama row is dropped. Only rows explicitly tagged for another provider are excluded.
- **Risk — a future `[routing.ollama]` default_model points at a filtered (non-Ollama) key.** Mitigation: the existing `default_model in models` check (`:234`) already fails closed in that case with a clear error; this is a config-authoring error, not a regression introduced here, and is covered by `test_default_and_skill_routes_still_resolve`.
- **Risk — editing the harness launch path.** Mitigation: the change is a single additive early-`continue` in the load loop, mirroring the proven OpenRouter sibling; `main`/validation/`ModelRoute` are untouched. Rollback: revert the one-block edit in `scripts/ollama_harness.py` and delete the new test file; no state migration.

## Files Expected To Change

- `scripts/ollama_harness.py` (edit `load_routing_config` model-building loop)
- `platform_tests/scripts/test_ollama_provider_scoped_routing.py` (new)

## Recommended Commit Type

`fix` — repairs a P1 defect (startup-abort of the Ollama harness on a cross-provider routing.toml) with no new user-facing capability surface; the provider filter scopes existing behavior to its provider.

## Bridge Protocol Compliance

Filed at `bridge/gtkb-ollama-harness-provider-scoped-model-validation-001.md` with a matching `NEW` status line inserted at the top of this Document's version list in `bridge/INDEX.md`; append-only. `GOV-FILE-BRIDGE-AUTHORITY-001` honored; `bridge/INDEX.md` remains the canonical workflow queue. The implementation-start packet will be minted from the GO against the project-wide standing PAUTH under `source` + `test_addition`. Cross-harness auto-dispatch is currently OFF (emergency kill-switch); this thread awaits a manual Loyal Opposition review.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
