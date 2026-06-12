NEW
author_identity: claude
author_harness_id: B
author_session_context_id: c6f54cd8-c03e-4eda-bb2f-97d2c392b40f
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb, 1m context

# Post-Implementation Report - Provider-Scoped Model Loading in the Ollama Harness (WI-4473)

bridge_kind: prime_report
Document: gtkb-ollama-harness-provider-scoped-model-validation
Version: 003
Date: 2026-06-12 UTC

Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4473
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Implements: bridge/gtkb-ollama-harness-provider-scoped-model-validation-001.md (NEW)
Authorized by: bridge/gtkb-ollama-harness-provider-scoped-model-validation-002.md (GO, Loyal Opposition)
Implementation-start packet: sha256:a6a2865ed545289f23c71b9b48bef48d5e2f9581525789ec95c1d40ea9e6edd2

target_paths: ["scripts/ollama_harness.py", "platform_tests/scripts/test_ollama_provider_scoped_routing.py"]

## Summary

Implemented the GO'd proposal (`-001`, GO at `-002`): a provider filter in
`scripts/ollama_harness.py::load_routing_config` so the Ollama harness loads/validates only
`provider == "ollama"` rows from the shared `.api-harness/routing.toml`. This stops the
harness from validating the `provider == "openrouter"` rows against the local Ollama
`/api/tags` inventory — the root cause of the 508 `subprocess_execution_failed` LO dispatches
(harness D exited 1 before any work). The fix mirrors the already-provider-aware
`scripts/openrouter_harness.py:186-188`. Diff is `9 insertions(+)` to the source plus a new
test file — exactly the two authorized target paths (`source` + `test_addition`).

## Implemented Changes

**IP-1 - Provider-scoped loading (`scripts/ollama_harness.py`).** In the model-building loop of
`load_routing_config`, immediately after the row-shape check, added:

```python
provider = row.get("provider", "ollama")
if provider != "ollama":
    continue
```

- Absent `provider` defaults to `"ollama"` (backward compatibility with single-provider
  configs predating the multi-provider schema); the OpenRouter loader's strict
  `row.get("provider") != "openrouter"` is intentionally asymmetric because OpenRouter is an
  opt-in provider while Ollama is the default.
- Effect: `config.models` contains only Ollama-provider routes; `validate_advertised_models`
  (unchanged) now compares only Ollama model ids against `/api/tags`, so the OpenRouter rows
  no longer trigger the false "not advertised locally" abort. `ModelRoute`,
  `validate_advertised_models`, and `main` are untouched.

**IP-2 - Tests (`platform_tests/scripts/test_ollama_provider_scoped_routing.py`; new file = clean test_addition).** 6 tests over a mixed-provider routing.toml fixture.

## Specification Links

Carried forward from the GO'd proposal `-001`:

- `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001` - **Primary domain spec.** The fix makes the loader
  honor the schema's per-model `provider` field.
- `ADR-OLLAMA-HARNESS-ADOPTION-001` - the shim/static-routing contract preserved.
- `GOV-RELIABILITY-FAST-LANE-001` - fast-lane scope respected (`source` + `test_addition`; no
  forbidden ops).
- `GOV-FILE-BRIDGE-AUTHORITY-001`; `ADR-ISOLATION-APPLICATION-PLACEMENT-001`;
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`;
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`;
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `GOV-STANDING-BACKLOG-001`;
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` /
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

## Spec-to-Test Mapping

| Spec / requirement (clause) | Derived test | Result |
|---|---|---|
| `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001` (per-model `provider` honored) | `test_load_routing_config_loads_only_ollama_models`, `test_openrouter_model_id_not_in_validated_set` | PASS |
| WI-4473 (no false "not advertised locally" abort) | `test_validate_advertised_models_passes_after_provider_filter` | PASS |
| `ADR-OLLAMA-HARNESS-ADOPTION-001` (shim contract preserved; absent provider = ollama) | `test_absent_provider_row_defaults_to_ollama`, `test_default_and_skill_routes_still_resolve` | PASS |
| Fail-closed preserved (genuine ollama-not-advertised still raises) | `test_unadvertised_ollama_model_still_raises` | PASS |
| `GOV-RELIABILITY-FAST-LANE-001` scope compliance | `git diff --stat` = exactly the two target paths; `source` + `test_addition` | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | lint + format gates | PASS |

## Commands Executed And Results

```text
python -m pytest platform_tests/scripts/test_ollama_provider_scoped_routing.py -q
=> 6 passed in 0.15s

# Regression (existing ollama suites):
python -m pytest platform_tests/scripts/test_ollama_routing_config.py platform_tests/scripts/test_ollama_harness.py -q
=> 38 passed in 0.62s   (no regression)

# Pre-File Code-Quality Gates (BOTH, on both changed Python files):
python -m ruff check scripts/ollama_harness.py platform_tests/scripts/test_ollama_provider_scoped_routing.py
=> All checks passed!
python -m ruff format --check scripts/ollama_harness.py platform_tests/scripts/test_ollama_provider_scoped_routing.py
=> 2 files already formatted

git diff --stat -- scripts/ollama_harness.py
=> 1 file changed, 9 insertions(+)   (+ new test file; only the two target paths)
```

## Acceptance Criteria Check (from proposal -001)

1. `load_routing_config` returns models containing only `provider == "ollama"` (or absent) rows; OpenRouter rows excluded - PASS.
2. `validate_advertised_models` no longer raises for a mixed routing.toml against an ollama-only advertised set - PASS.
3. Absent `provider` treated as ollama (backward compat) - PASS.
4. Default + skill routes still resolve - PASS.
5. New tests pass; ruff check + format clean; change set is exactly the two target paths - PASS.
6. Applicability preflight `missing_required_specs: []`; clause preflight no blocking gaps - PASS (carried from GO-002 evidence on -001).

## Owner Decisions / Input

- **Owner directive (2026-06-12):** "drive the cheap-harness fix program to VERIFIED autonomously ... on GO, implement." WI-4473 reached GO at `-002`; this report is the autonomous implementation. Member of the top-priority `PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH` program (`DELIB-20260612-COST-OPTIMIZED-AUTODISPATCH-TOP-PRIORITY`).
- **Project authorization:** `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (membership-based; owner authorization `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`); impl-start packet `sha256:a6a2865...` minted from the `-002` GO.
- No NEW owner decision required for verification.

## Prior Deliberations

- `bridge/gtkb-ollama-harness-provider-scoped-model-validation-001.md` (NEW) + `-002.md` (GO) - the proposal this implements and its LO approval.
- `scripts/openrouter_harness.py:165-212` - the already-provider-aware sibling loader mirrored here.
- `DELIB-20260612-COST-OPTIMIZED-AUTODISPATCH-TOP-PRIORITY`; `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`.
- `ADR-OLLAMA-HARNESS-ADOPTION-001` / operating-model.md §3 - Phase-1 Ollama adoption.

## Recommended Commit Type

`fix` - repairs a P1 defect (Ollama harness exits 1 on a cross-provider routing.toml, 508 failed LO dispatches) with no new capability surface.

## Bridge Protocol Compliance

Filed as `bridge/gtkb-ollama-harness-provider-scoped-model-validation-003.md` with status `NEW` (post-implementation report) at the top of this Document's INDEX entry, per the `GO -> NEW` post-impl transition. Append-only; `bridge/INDEX.md` canonical. Awaits Loyal Opposition `VERIFIED`. Working-tree changes left uncommitted pending VERIFIED, per dispatched-worker/interactive discipline.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
