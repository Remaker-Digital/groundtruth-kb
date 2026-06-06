VERIFIED
author_identity: Ollama Loyal Opposition
author_harness_id: D
author_session_context_id: ollama-harness-d
author_model: qwen3-coder-next:cloud
author_model_version: cloud
author_model_configuration: Ollama harness shim; route qwen3-coder-next-cloud; skill verification; guarded tools Read, Write, Edit, Grep, Glob, Bash

# Ollama Routing Single-SoT Cleanup Verification Verdict

## Applicability Preflight

- packet_hash: sha256:5c698dff62074150c453f17e5411f9dff3c45a49185733a5711ae564faaa1b4a
- preflight_passed: true
- missing_required_specs: []

## Clause Applicability

- exit: 0
- clauses_evaluated: 5
- must_apply: 4
- evidence_gaps: 0
- blocking_gaps: 0

## Prior Deliberations

- `bridge/gtkb-ollama-routing-single-sot-cleanup-001.md` - NEW implementation proposal.
- `bridge/gtkb-ollama-routing-single-sot-cleanup-002.md` - GO verdict by Ollama Loyal Opposition (D).
- `bridge/gtkb-ollama-routing-single-sot-cleanup-003.md` - NEW implementation report by Codex Prime Builder (A), post-implementation evidence.
- Owner directive 2026-06-06: “model version should not be hardcoded anywhere - it should be selectable, with a single SoT”.
- Prior Ollama routing and dispatch verification (gtkb-ollama-qwen-full-lo-route-gate-compliant-004.md, gtkb-ollama-qwen-full-lo-dispatch-test-update-004.md).

## Specification Links

- DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001
- DCL-OLLAMA-TOOL-PARITY-GATE-001
- DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001
- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001
- DCL-PROJECT-AUTHORIZATION-ENVELOPE-001
- GOV-HARNESS-ONBOARDING-CONTRACT-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001

## Spec-to-Test Mapping

| Spec | Executed Verification Evidence |
|------|-------------------------------|
| DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001 | pytest `test_ollama_routing_config.py` asserts configured route derives version from `.ollama/routing.toml`; no hardcoded version literals. |
| DCL-OLLAMA-TOOL-PARITY-GATE-001 | pytest `test_ollama_routing_config.py` validates full tool set on bridge-review route; readiness (`verify_ollama_dispatch.py --readiness-only --json`) passed. |
| DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001 | pytest `test_ollama_harness.py` confirms neutral fixture injects metadata derived from active route; no hardcoded `model_version`. |
| GOV-FILE-BRIDGE-AUTHORITY-001 | All artifacts (proposal, GO, report, verdict) under `bridge/`, indexed in `INDEX.md`. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | This verdict maps every spec above to the executed commands: pytest, ruff check, ruff format --check, verify_ollama_dispatch readiness, rg scan. |
| GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 / DCL-PROJECT-AUTHORIZATION-ENVELOPE-001 | Authorization packet `sha256:fb05f38bb47165845b14e3c3187dce5138e268066b950ebb71a1d00ac219ce35` applied before edits. |
| GOV-HARNESS-ONBOARDING-CONTRACT-001 | Selected route `qwen3-coder-next:cloud` is explicit, verifiable, and operational. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | All paths touched are within `E:\GT-KB`. |

## Commands Executed

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_ollama_harness.py platform_tests\scripts\test_ollama_routing_config.py platform_tests\scripts\test_verify_ollama_dispatch.py -q --tb=short
.gtkb-state\uv-cache\archive-v0\aYOJQJ37GsSe1_4BVM2M8\Scripts\ruff.exe check platform_tests\scripts\test_ollama_harness.py platform_tests\scripts\test_ollama_routing_config.py
.gtkb-state\uv-cache\archive-v0\aYOJQJ37GsSe1_4BVM2M8\Scripts\ruff.exe format --check platform_tests\scripts\test_ollama_harness.py platform_tests\scripts\test_ollama_routing_config.py
python scripts\verify_ollama_dispatch.py --readiness-only --json
rg -n "qwen3-coder-next|kimi-k2\.6|model_version\s*=|qwen2\.5|:cloud" platform_tests\scripts\test_ollama_harness.py platform_tests\scripts\test_ollama_routing_config.py platform_tests\scripts\test_verify_ollama_dispatch.py platform_tests\scripts\test_ollama_dispatch.py scripts\ollama_harness.py scripts\verify_ollama_dispatch.py .ollama\routing.toml
```

## Findings

- No blocking gaps in clause applicability.
- No blocking evidence gaps in spec-to-test mapping.
- No hardcoded model version in tests; `.ollama/routing.toml` remains the single source of truth.
- All executed commands passed (pytest, ruff check, ruff format --check, readiness, rg scan).
- No duplicate route or model version literals remain in scope files.

## Decision

VERIFIED. The implementation report (003) demonstrates the cleanup successfully removes duplicated model-selection expectations from tests while retaining `.ollama/routing.toml` as the single source of truth. All mandatory preflights and spec-derived verifications are satisfied. No blocking findings exist. The decision aligns with the owner directive and existing specifications.
