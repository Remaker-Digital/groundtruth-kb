NEW

# GT-KB Bridge Implementation Report - gtkb-cloud-harness-template-slice4a-native-hook-wiring - 003

bridge_kind: implementation_report
Document: gtkb-cloud-harness-template-slice4a-native-hook-wiring
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-cloud-harness-template-slice4a-native-hook-wiring-002.md
Approved proposal: bridge/gtkb-cloud-harness-template-slice4a-native-hook-wiring-001.md
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f4929-9343-7480-a8a0-055a97ab4b8a
author_model: GPT-5
author_model_version: gpt-5
author_model_configuration: Codex desktop, Prime Builder role
Work Item: WI-5078
Project: PROJECT-GTKB-CLOUD-HARNESS-TEMPLATE
Project Authorization: PAUTH-PROJECT-GTKB-CLOUD-HARNESS-TEMPLATE-20260708
Recommended commit type: feat:

## Implementation Claim

Implemented the Slice 4a `native-full-hooks` lifecycle wiring in the shared cloud harness base while preserving the existing `guard-adapter-floor` behavior.

The completed implementation:

- Adds Claude-style native hook event constants for `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, and `Stop`.
- Loads hook registrations from `.claude/settings.json`, including command hook arrays, optional `matcher` filters, and optional per-hook `timeout` values.
- Adds a framework-free native hook runner using the existing fail-closed subprocess pattern, JSON stdin payloads, JSON stdout interpretation, and Windows `CREATE_NO_WINDOW` behavior.
- Supplies `CLAUDE_PROJECT_DIR` / `GTKB_PROJECT_ROOT` environment values and expands those variables in tracked hook command strings before invocation.
- Wires `run_tool_loop` so `native-full-hooks` fires:
  - `SessionStart` at loop entry.
  - `UserPromptSubmit` before the initial user message is sent to the provider.
  - `PreToolUse` before each tool dispatch.
  - `PostToolUse` after each tool dispatch or blocked tool result.
  - `Stop` at loop termination.
- Implements `PreToolUse` block semantics: a hook output such as `{"decision": "block", "reason": "..."}` refuses the tool and feeds the reason back to the model as a tool result instead of dispatching the tool.
- Keeps the fail-closed guard-adapter floor enforced for mutating tools under both hook tiers.

Implementation authorization:

- Work-intent claim: `gtkb-cloud-harness-template-slice4a-native-hook-wiring`
- Session context: `019f4929-9343-7480-a8a0-055a97ab4b8a`
- Authorization packet hash: `sha256:7e2890b0ebb30f834c1b1a5843fa56cc441da90c62f7ce681e842026d058b3a7`
- Authorized target paths:
  - `scripts/cloud_harness_base.py`
  - `platform_tests/scripts/test_cloud_harness_base.py`

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `ADR-CLOUD-HARNESS-TEMPLATE-001`
- `SPEC-INTAKE-9ec893`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `DCL-CLOUD-HARNESS-TEMPLATE-TOOL-PARITY-GATE-001`
- `ADR-OLLAMA-HARNESS-ADOPTION-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Owner Decisions / Input

No new owner decision is required by this implementation report. This report stays within the approved Slice 4a scope: native-hook lifecycle wiring with stubbed transport proof only.

## Prior Deliberations

- `DELIB-20260709-CLOUD-HARNESS-TEMPLATE-SLICE4-SCOPE-SPLIT` - owner decision limiting this slice to native-hook wiring plus stubbed proof; Alibaba Cloud Studio live proof remains deferred to Slice 4b.
- `DELIB-20260708-CLOUD-HARNESS-TEMPLATE-SLICE3-NATIVE-HOOK-SCOPE` - owner decision that Slice 3 validated the seam/flag and Slice 4 wires the concrete lifecycle.
- `DELIB-20260708-BUILD-REUSABLE-DIRECT-CLOUD-HARNESS-TEMPLATE` - program authorization.
- `bridge/gtkb-cloud-harness-template-slice3-dialect-abstraction-004.md` - VERIFIED Slice 3 dependency.
- `bridge/gtkb-cloud-harness-template-slice4a-native-hook-wiring-001.md` - approved implementation proposal.
- `bridge/gtkb-cloud-harness-template-slice4a-native-hook-wiring-002.md` - Loyal Opposition GO verdict.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `ADR-CLOUD-HARNESS-TEMPLATE-001`, `SPEC-INTAKE-9ec893`, `ADR-OLLAMA-HARNESS-ADOPTION-001` | Added framework-free native hook lifecycle helpers to `scripts/cloud_harness_base.py`; no new agent framework or external runtime dependency introduced. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001`, `DCL-CLOUD-HARNESS-TEMPLATE-TOOL-PARITY-GATE-001` | Added `test_native_full_hooks_run_tool_loop_still_enforces_guard_floor`, proving mutating `Write` still routes through the fail-closed guard floor under `native-full-hooks`. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001`, `ADR-CROSS-HARNESS-PARITY-001`, `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Added stubbed loop tests proving lifecycle order, PreToolUse block behavior, and OpenRouter regression coverage with no adopter config changes. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Ran targeted and slice regression pytest suites plus ruff check and format-check; results recorded below. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Implementation stayed within the GO-approved two target paths under `E:\GT-KB`; this report names the exact bridge GO and authorization packet. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Behavior is preserved as tracked source plus tracked tests and filed through the governed bridge chain. |

## Commands Run

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_cloud_harness_base.py -q --tb=short --basetemp .harness-tmp\cloud4a-target`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format scripts\cloud_harness_base.py platform_tests\scripts\test_cloud_harness_base.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_cloud_harness_base.py platform_tests\scripts\test_openrouter_harness.py platform_tests\scripts\test_openrouter_routing_deepseek.py -q --tb=short --basetemp .harness-tmp\cloud4a-slice`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\cloud_harness_base.py platform_tests\scripts\test_cloud_harness_base.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\cloud_harness_base.py platform_tests\scripts\test_cloud_harness_base.py`

## Observed Results

- Targeted platform test: `37 passed, 1 warning in 0.72s`.
- Formatter: `1 file reformatted, 1 file left unchanged`.
- Slice regression set: `86 passed, 1 warning in 1.39s`.
- Ruff check: `All checks passed!`.
- Ruff format check: `2 files already formatted`.

The warning is the pre-existing pytest configuration warning: `Unknown config option: asyncio_mode`.

## Files Changed

- `scripts/cloud_harness_base.py`
- `platform_tests/scripts/test_cloud_harness_base.py`

No DB, generated projection, bridge registry, adopter onboarding, live endpoint, `ollama-native`, doctor, or unrelated dirty-tree files are included in this implementation scope.

## Acceptance Criteria Status

- [x] `native-full-hooks` fires `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, and `Stop` in the tool loop.
- [x] Hook registrations are read from `.claude/settings.json` using command hooks, matchers, and timeouts.
- [x] `PreToolUse` block semantics refuse the tool and feed the block reason back to the model.
- [x] Existing `guard-adapter-floor` default behavior is unchanged.
- [x] Mutating tools still enforce the guard-adapter floor under `native-full-hooks`.
- [x] Verification is stubbed/local only; no live adopter endpoint or credentials are required.

## Cross-Harness Disposition

`scripts/cloud_harness_base.py` is a shared harness surface. This implementation is additive for the opt-in `native-full-hooks` tier and preserves the default `guard-adapter-floor` path. The regression set includes OpenRouter harness coverage to prove the existing adopter behavior remains intact. No harness role registry, generated projection, or adopter-specific configuration was changed.

## Recommended Commit Type

- Recommended commit type: `feat:`
- Rationale: adds the concrete native hook lifecycle capability to the reusable direct-cloud harness base.

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
