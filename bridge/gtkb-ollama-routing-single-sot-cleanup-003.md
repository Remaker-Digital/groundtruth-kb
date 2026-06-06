NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019e99ba-0220-7292-a2ac-e2329eae912a
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive Prime Builder; workspace E:\GT-KB; approval-policy never
author_metadata_source: explicit Prime Builder correction before Loyal Opposition verification; stale bridge-author-metadata cache ignored

# Ollama Routing Single-SoT Cleanup Implementation Report

bridge_kind: implementation_report
Document: gtkb-ollama-routing-single-sot-cleanup
Version: 003
Responds to: bridge/gtkb-ollama-routing-single-sot-cleanup-002.md
Project Authorization: PAUTH-PROJECT-GTKB-OLLAMA-LO-OPERATIONS-QWEN-FULL-LO
Project: PROJECT-GTKB-OLLAMA-LO-OPERATIONS
Work Item: WI-4385
Date: 2026-06-06 UTC
Recommended commit type: test

## Implementation Claim

Implemented the owner clarification that selected Ollama model/version data must not be duplicated outside the routing source of truth. Runtime selection remains in `.ollama/routing.toml`; focused repository tests now derive the active bridge-review/verification route from that config instead of hardcoding the selected Qwen/Kimi route or model IDs as independent expectations.

## Requirement Sufficiency

Existing requirements sufficient. This report implements the GO'd cleanup scope only; no new formal requirement or owner choice was needed after the proposal.

## Specification Links

- `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001`
- `DCL-OLLAMA-TOOL-PARITY-GATE-001`
- `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Owner Decisions / Input

Mike's current-session 2026-06-06 directive is carried forward: the model version should not be hardcoded anywhere as a second selection authority; model selection should be selectable from a single SoT. No additional owner decision was required.

## Prior Deliberations

- `DELIB-20260606-OLLAMA-QWEN-FULL-LO-DIRECTIVE` - owner directive to make Ollama Qwen the active full-capability LO target.
- `DELIB-20260605-OLLAMA-PHASE2-COMPLETION-DIRECTIVE` - owner directive to complete Ollama bridge integration.
- `DELIB-20260895` - owner selected Codex Prime Builder and Ollama Loyal Opposition while Claude Code and Antigravity were offline.
- `DELIB-20260898` - owner clarified suspended harnesses may still participate in GT-KB work.
- `DELIB-20260679` - owner clarified Ollama should be the target for LO work dispatched via the bridge.
- `bridge/gtkb-ollama-routing-single-sot-cleanup-001.md` - approved proposal.
- `bridge/gtkb-ollama-routing-single-sot-cleanup-002.md` - Ollama/Qwen GO verdict.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001` | `platform_tests/scripts/test_ollama_routing_config.py` now derives repository route expectations from `.ollama/routing.toml`; focused pytest passed. |
| `DCL-OLLAMA-TOOL-PARITY-GATE-001` | Repository routing test asserts configured bridge-review route exposes the full LO tool set; live readiness passed. |
| `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001` | `platform_tests/scripts/test_ollama_harness.py` continues to assert prompt metadata uses selected route metadata via neutral fixtures; focused pytest passed. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Proposal, GO, report, and INDEX updates are recorded under the bridge thread. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This report maps every implementation claim to executed pytest, ruff, and readiness evidence. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Implementation authorization packet `sha256:fb05f38bb47165845b14e3c3187dce5138e268066b950ebb71a1d00ac219ce35` was acquired before edits. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All touched paths are within `E:\GT-KB`. |

## Commands Run

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_ollama_harness.py platform_tests\scripts\test_ollama_routing_config.py platform_tests\scripts\test_verify_ollama_dispatch.py platform_tests\scripts\test_ollama_dispatch.py -q --tb=short
.gtkb-state\uv-cache\archive-v0\aYOJQJ37GsSe1_4BVM2M8\Scripts\ruff.exe check platform_tests\scripts\test_ollama_harness.py platform_tests\scripts\test_ollama_routing_config.py
.gtkb-state\uv-cache\archive-v0\aYOJQJ37GsSe1_4BVM2M8\Scripts\ruff.exe format --check platform_tests\scripts\test_ollama_harness.py platform_tests\scripts\test_ollama_routing_config.py
.gtkb-state\uv-cache\archive-v0\aYOJQJ37GsSe1_4BVM2M8\Scripts\ruff.exe check scripts\ollama_harness.py scripts\verify_ollama_dispatch.py platform_tests\scripts\test_ollama_harness.py platform_tests\scripts\test_ollama_routing_config.py platform_tests\scripts\test_verify_ollama_dispatch.py platform_tests\scripts\test_ollama_dispatch.py
.gtkb-state\uv-cache\archive-v0\aYOJQJ37GsSe1_4BVM2M8\Scripts\ruff.exe format --check scripts\ollama_harness.py scripts\verify_ollama_dispatch.py platform_tests\scripts\test_ollama_harness.py platform_tests\scripts\test_ollama_routing_config.py platform_tests\scripts\test_verify_ollama_dispatch.py platform_tests\scripts\test_ollama_dispatch.py
python scripts\verify_ollama_dispatch.py --readiness-only --json
rg -n "qwen3-coder-next|kimi-k2\.6|model_version\s*=|qwen2\.5|:cloud" platform_tests\scripts\test_ollama_harness.py platform_tests\scripts\test_ollama_routing_config.py platform_tests\scripts\test_verify_ollama_dispatch.py platform_tests\scripts\test_ollama_dispatch.py scripts\ollama_harness.py scripts\verify_ollama_dispatch.py .ollama\routing.toml
```

## Observed Results

- Focused pytest: `59 passed in 1.02s`.
- Narrow ruff lint: `All checks passed!` with a non-blocking `.ruff_cache` access warning.
- Narrow ruff format: `2 files already formatted`.
- Broader Ollama ruff lint: `All checks passed!`.
- Broader Ollama ruff format: `6 files already formatted`.
- Live readiness JSON: `ready: true`, `route_key: qwen3-coder-next-cloud`, `model_id: qwen3-coder-next:cloud`, `missing_tools: []`, required tools `Read`, `Write`, `Edit`, `Grep`, `Glob`, `Bash`.
- Focused `rg` scan: selected Qwen/Kimi cloud literals remain only in `.ollama/routing.toml`, the intended live routing SoT. Remaining `model_version` occurrences in focused Python files are derived assignments or inert fixture metadata, not active route selection.

## Files Changed

- `platform_tests/scripts/test_ollama_harness.py` - CLI parser test now uses `selected-route` instead of the active Qwen route key.
- `platform_tests/scripts/test_ollama_routing_config.py` - repository routing test now derives active route expectations from `.ollama/routing.toml`; removed Qwen/Kimi selected-model constants.
- `bridge/gtkb-ollama-routing-single-sot-cleanup-001.md`, `-002.md`, `-003.md`, and `bridge/INDEX.md` - record this follow-up bridge lifecycle.

## Acceptance Criteria Status

| Acceptance criterion | Status | Evidence |
| --- | --- | --- |
| No focused test duplicates active selected Ollama model ID/tag as a second selection authority. | Met | `rg` scan shows active cloud literals only in `.ollama/routing.toml`. |
| `.ollama/routing.toml` remains the only live place to switch the active Ollama LO model route. | Met | Repository routing test loads config and validates selected route dynamically. |
| Focused pytest passes. | Met | `59 passed in 1.02s`. |
| Ruff lint and format checks pass for changed Python tests. | Met | Narrow and broader ruff commands passed. |
| Bridge thread receives Loyal Opposition verification before commit. | Pending LO | This `NEW` report is filed for Qwen/Ollama verification. |

## Risk And Rollback

Residual risk is low. The cleanup intentionally keeps behavioral assertions while removing duplicated selected-model constants. If rollback is needed, restore the previous test constants in the two touched test files; runtime routing is unaffected because `.ollama/routing.toml` remains unchanged by this follow-up.

## Loyal Opposition Asks

1. Verify the cleanup against the owner clarification and linked specs.
2. Confirm that the tests now treat `.ollama/routing.toml` as the single live route-selection source.
3. Return `VERIFIED` if the report and implementation satisfy the approved proposal; otherwise return `NO-GO` with concrete findings.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
