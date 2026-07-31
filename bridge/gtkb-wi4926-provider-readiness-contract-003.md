NEW

# WI-4926 Provider Readiness Credential And Live-Probe Contract - Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi4926-provider-readiness-contract
Version: 003
Author: Prime Builder (Codex)
Date: 2026-07-06T05:48:00Z

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-06T05-28-36Z-prime-builder-A-1f8cb3
author_model: GPT-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex headless bridge auto-dispatch; approval_policy=never; workspace-write sandbox

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-WI4926-PROVIDER-READINESS-20260706
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4926
Responds to: bridge/gtkb-wi4926-provider-readiness-contract-002.md
Implementation authorization packet: sha256:6a0177eabc79f415f7b46dd3a10749c1f5a7a260f92e918493b0eedf91bfe461

## Summary

Implemented the WI-4926 provider-readiness contract as documentation, registry metadata, and focused assertion coverage. No provider credential values were read, copied, logged, or embedded. No live provider calls were introduced. No provider harness topology, credential lifecycle, production deployment, or direct harness-to-harness invocation behavior was changed.

The implementation adds:

- `docs/harness-parity-phase-2.md`: a provider-readiness contract distinguishing default mocked assertions from live dispatch boundaries for Ollama and OpenRouter.
- `docs/harness-parity-phase-2-matrix.md`: a matrix-level provider readiness section that cross-references the active Ollama/OpenRouter Phase 2 event-source and transcript waivers and states that those waivers do not waive readiness.
- `config/agent-control/harness-capability-registry.toml`: provider-readiness metadata fields under `[harnesses.ollama]` and `[harnesses.openrouter]`.
- `platform_tests/scripts/test_openrouter_harness.py`: assertions for missing `OPENROUTER_API_KEY` as configuration failure, `.env.local` loading before dispatch, and invalid credential/provider rejection as a non-retried path.
- `platform_tests/scripts/test_ollama_provider_scoped_routing.py`: a mocked live-inventory outage assertion for the Ollama `/api/tags` boundary.
- `platform_tests/scripts/test_harness_parity_phase2.py`: a repository assertion that the provider-readiness contract is documented and registered.

No edits were required in `scripts/ollama_harness.py`, `scripts/openrouter_harness.py`, `scripts/check_harness_parity.py`, `platform_tests/scripts/test_check_harness_parity.py`, or `platform_tests/scripts/test_ollama_harness.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `GOV-ENV-LOCAL-AUTHORITY-001`
- `ADR-OLLAMA-HARNESS-ADOPTION-001`
- `DCL-OLLAMA-TOOL-PARITY-GATE-001`
- `SPEC-INTAKE-21c5b3`
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `SPEC-CODE-QUALITY-CHECKLIST-001`

## Worktree Scope Note

This dispatch ran in a dirty worktree. The implementation report covers the WI-4926 changes listed above. The following dirty target-file changes were already present before the WI-4926 edits and are not claimed as this implementation:

- `config/agent-control/harness-capability-registry.toml`: existing `skill.skill-governance-lifecycle` registry entry.
- `platform_tests/scripts/test_harness_parity_phase2.py`: existing `dispatcher_runtime.py` no-window fixture expectation change.

The implementation helper reported `files_changed_count: 165` because the wider checkout already contains many unrelated dirty and untracked files. WI-4926 edits were kept to the approved target paths.

## Specifications Carried Forward

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `GOV-ENV-LOCAL-AUTHORITY-001`
- `ADR-OLLAMA-HARNESS-ADOPTION-001`
- `DCL-OLLAMA-TOOL-PARITY-GATE-001`
- `SPEC-INTAKE-21c5b3`
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `SPEC-CODE-QUALITY-CHECKLIST-001`

## Spec-To-Test Mapping

| Requirement | Evidence |
|---|---|
| Readiness contract is documented | `docs/harness-parity-phase-2.md`; `docs/harness-parity-phase-2-matrix.md`; `platform_tests/scripts/test_harness_parity_phase2.py::test_wi4926_provider_readiness_contract_is_documented_and_registered` |
| Credential values stay out of governed docs and tests | Docs cite variable names and failure classes only; tests use fake keys (`env-file-fixture-key`, `bad-key`) and mocked responses. `git diff --check` passed for scoped files. |
| Phase 2 waiver registry cross-reference exists | Matrix doc cites `WAIVER-P2-OLLAMA-EVENT-SOURCE`, `WAIVER-P2-OPENROUTER-EVENT-SOURCE`, `WAIVER-P2-OLLAMA-FULL-TRANSCRIPT-ARCHIVE`, and `WAIVER-P2-OPENROUTER-FULL-TRANSCRIPT-ARCHIVE`, explicitly stating those waivers do not waive readiness. |
| Missing credential, invalid credential, provider outage, and mocked path semantics are asserted | `platform_tests/scripts/test_openrouter_harness.py::test_main_classifies_missing_openrouter_key_as_configuration_failure`; `::test_main_loads_env_local_key_before_live_dispatch`; `::test_invalid_openrouter_credential_is_not_retried`; `platform_tests/scripts/test_ollama_provider_scoped_routing.py::test_ollama_live_inventory_provider_outage_is_mockable` |
| Live probes do not direct-invoke peer harnesses | Documentation states live probes are provider/control-plane boundaries only; tests mock provider responses and do not launch peer harnesses. The earlier direct-harness guard blocked an over-broad read-only search command, and implementation avoided direct harness invocation thereafter. |
| Minimal classifier fixes stay bounded | No classifier or provider shim source changes were required. |
| Bridge/project authorization lifecycle | Work-intent claim acquired for `gtkb-wi4926-provider-readiness-contract`; implementation authorization created from latest `GO` with packet hash `sha256:6a0177eabc79f415f7b46dd3a10749c1f5a7a260f92e918493b0eedf91bfe461`. |

## Commands Executed

```text
groundtruth-kb\.venv\Scripts\gt.exe harness roles
groundtruth-kb\.venv\Scripts\gt.exe bridge dispatch status --json
groundtruth-kb\.venv\Scripts\gt.exe bridge show gtkb-wi4926-provider-readiness-contract --json --compact
groundtruth-kb\.venv\Scripts\python.exe .codex\skills\bridge\helpers\scan_bridge.py --role prime-builder --compact --format json
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_claim_cli.py claim gtkb-wi4926-provider-readiness-contract
groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-wi4926-provider-readiness-contract
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_openrouter_harness.py platform_tests\scripts\test_ollama_provider_scoped_routing.py platform_tests\scripts\test_harness_parity_phase2.py -q --tb=short --basetemp .gtkb-state\pytest-wi4926
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_openrouter_harness.py platform_tests\scripts\test_ollama_harness.py platform_tests\scripts\test_ollama_provider_scoped_routing.py platform_tests\scripts\test_check_harness_parity.py platform_tests\scripts\test_harness_parity_phase2.py -q --tb=short --basetemp .gtkb-state\pytest-wi4926-full
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_harness_parity_phase2.py::test_wi4926_provider_readiness_contract_is_documented_and_registered -q --tb=short --basetemp .gtkb-state\pytest-wi4926-spot
groundtruth-kb\.venv\Scripts\python.exe -m ruff check platform_tests\scripts\test_openrouter_harness.py platform_tests\scripts\test_ollama_provider_scoped_routing.py platform_tests\scripts\test_harness_parity_phase2.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check platform_tests\scripts\test_openrouter_harness.py platform_tests\scripts\test_ollama_provider_scoped_routing.py platform_tests\scripts\test_harness_parity_phase2.py
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi4926-provider-readiness-contract --json
groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi4926-provider-readiness-contract
git diff --check -- docs\harness-parity-phase-2.md docs\harness-parity-phase-2-matrix.md config\agent-control\harness-capability-registry.toml platform_tests\scripts\test_openrouter_harness.py platform_tests\scripts\test_ollama_provider_scoped_routing.py platform_tests\scripts\test_harness_parity_phase2.py
```

Observed results:

- Focused WI-4926 suite: `47 passed`, with warnings for unknown `asyncio_mode` and pytest cache write contention.
- Full proposal-specified suite: `117 passed`, `1 failed`. The failure was `platform_tests/scripts/test_check_harness_parity.py::test_repository_registry_has_no_unclassified_missing_rows`, caused by the unrelated existing `skill.skill-governance-lifecycle` registry state (`.codex/skills/skill-governance-lifecycle/SKILL.md` absent; Ollama/OpenRouter surface rows absent).
- Spot check after LF normalization: `1 passed`.
- `ruff check`: all checks passed.
- `ruff format --check`: 3 files already formatted.
- Bridge applicability preflight: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.
- ADR/DCL clause preflight: exit 0; blocking gaps 0.
- Scoped `git diff --check`: exit 0.

The initial focused pytest run without `--basetemp` hit `PermissionError: [WinError 5] Access is denied: 'C:\Users\micha\AppData\Local\Temp\pytest-of-micha'`. The tests were rerun with in-repo basetemp directories under `.gtkb-state/` to avoid the locked user temp path.

## Acceptance Status

Accepted for WI-4926 scope. Provider-readiness behavior is now documented, represented in harness registry metadata, and covered by focused mocked assertions. The only failing verification command is an unrelated pre-existing parity registry assertion for `skill.skill-governance-lifecycle`.

## Risk / Rollback

Risk is low because the implementation is docs, registry metadata, and tests only. Rollback is limited to the WI-4926 additions in the listed docs, registry metadata fields, and tests. No credential values, provider activation state, topology, or live provider behavior require rollback.

## Recommended Commit Type

Recommended commit type: `docs:`

`docs:` - primary change is the provider-readiness contract documentation and registry declaration, with focused tests added as assertion coverage.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
