NEW

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019e99ba-0220-7292-a2ac-e2329eae912a
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive Prime Builder; workspace E:\GT-KB; approval-policy never

# Ollama Qwen Full LO Route Gate-Compliant Implementation Report

bridge_kind: implementation_report
Document: gtkb-ollama-qwen-full-lo-route-gate-compliant
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-ollama-qwen-full-lo-route-gate-compliant-002.md
Approved proposal: bridge/gtkb-ollama-qwen-full-lo-route-gate-compliant-001.md
Recommended commit type: feat

## Implementation Claim

Implemented the approved Ollama Loyal Opposition route change with `.ollama/routing.toml` as the single operational model-selection SoT. The active `bridge-review`, `verification`, and `implementation` skill routes now resolve through the selected routing key `qwen3-coder-next-cloud`; changing `[routing.skills]` changes the dispatched model without Python code changes.

Removed duplicated live `model_version` fields from `.ollama/routing.toml`. `scripts/ollama_harness.py` derives `ModelRoute.model_version` from the selected `model_id` tag at runtime, so bridge author metadata uses selected route metadata rather than hardcoded model/version literals. `bridge-review` and `verification` runs now receive compact Loyal Opposition bridge context that instructs Ollama to read `bridge/INDEX.md`, read the full version chain, run mandatory preflights, acquire a bridge work-intent claim before verdict writes, write the next bridge verdict file, and update `bridge/INDEX.md`.

`scripts/verify_ollama_dispatch.py` now resolves the configured `bridge-review` skill route and requires the full guarded LO tool set: `Read`, `Write`, `Edit`, `Grep`, `Glob`, and `Bash`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-OLLAMA-HARNESS-ADOPTION-001`
- `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001`
- `DCL-OLLAMA-TOOL-PARITY-GATE-001`
- `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `GOV-HARNESS-ROLE-PORTABILITY-001`
- `GOV-SESSION-ROLE-AUTHORITY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Owner Decisions / Input

No new owner decision is required by this implementation report. The owner clarified during implementation that model version must not be hardcoded and must be selectable from a single SoT; this implementation satisfies that by deriving `author_model_version` from the selected `.ollama/routing.toml` `model_id` tag and keeping model selection in `[routing.skills]`.

## Prior Deliberations

- `DELIB-20260606-OLLAMA-QWEN-FULL-LO-DIRECTIVE` - owner directive to use Qwen as full Ollama LO target.
- `bridge/gtkb-ollama-qwen-full-lo-route-gate-compliant-001.md` - approved gate-compliant implementation proposal.
- `bridge/gtkb-ollama-qwen-full-lo-route-gate-compliant-002.md` - Qwen LO GO verdict.
- `bridge/gtkb-ollama-qwen-full-lo-dispatch-test-update-001.md` and `-002.md` - adjacent test amendment and Qwen LO GO.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001` | `platform_tests/scripts/test_ollama_routing_config.py` verifies selected model route comes from `.ollama/routing.toml`, bridge-review and verification share the configured full-tool route, and model version is derived from selected `model_id`. |
| `DCL-OLLAMA-TOOL-PARITY-GATE-001` | `platform_tests/scripts/test_verify_ollama_dispatch.py`, `platform_tests/scripts/test_ollama_dispatch.py`, and live `python scripts/verify_ollama_dispatch.py --readiness-only --json` verify full LO tool readiness. |
| `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001` | `platform_tests/scripts/test_ollama_harness.py` verifies bridge context and guard env use selected route metadata and derived model version. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Qwen LO filed GO verdicts through `scripts/ollama_harness.py` for both this thread and the test amendment, updating bridge files and `bridge/INDEX.md` through guarded tools. |
| `GOV-HARNESS-ROLE-PORTABILITY-001` / `GOV-SESSION-ROLE-AUTHORITY-001` | Live readiness verifies active Ollama recipient D headless route resolves through the registry and configured skill route. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All modified runtime/test paths are under `E:\GT-KB`; bridge preflights passed with no blocking gaps. |

## Commands Run

- `python scripts\implementation_authorization.py begin --bridge-id gtkb-ollama-qwen-full-lo-route-gate-compliant` - authorized; packet hash `sha256:6b10e6a61d2e6a5b292f165e9c8e54571a4a5193c74a582cfa56e70a2b659f5d`.
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_ollama_harness.py platform_tests\scripts\test_ollama_routing_config.py platform_tests\scripts\test_verify_ollama_dispatch.py platform_tests\scripts\test_ollama_dispatch.py -q --tb=short`
- `python scripts\verify_ollama_dispatch.py --readiness-only --json`
- `.gtkb-state\uv-cache\archive-v0\aYOJQJ37GsSe1_4BVM2M8\Scripts\ruff.exe check scripts\ollama_harness.py scripts\verify_ollama_dispatch.py platform_tests\scripts\test_ollama_harness.py platform_tests\scripts\test_ollama_routing_config.py platform_tests\scripts\test_verify_ollama_dispatch.py platform_tests\scripts\test_ollama_dispatch.py`
- `.gtkb-state\uv-cache\archive-v0\aYOJQJ37GsSe1_4BVM2M8\Scripts\ruff.exe format --check scripts\ollama_harness.py scripts\verify_ollama_dispatch.py platform_tests\scripts\test_ollama_harness.py platform_tests\scripts\test_ollama_routing_config.py platform_tests\scripts\test_verify_ollama_dispatch.py platform_tests\scripts\test_ollama_dispatch.py`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\ollama_harness.py --skill bridge-review --max-turns 2 --timeout 180 --prompt "Do not use tools. Reply exactly: OK"`

## Observed Results

- Focused pytest: `59 passed in 1.20s`.
- Live readiness JSON: `ready: true`; `route_key: qwen3-coder-next-cloud`; `model_id: qwen3-coder-next:cloud`; required tools `Read`, `Write`, `Edit`, `Grep`, `Glob`, `Bash`; all readiness checks passed.
- Ruff lint: `All checks passed!`.
- Ruff format check: `6 files already formatted`.
- Live Qwen harness smoke: output exactly `OK`.

## Files Changed

Scoped implementation files:

- `.ollama/routing.toml`
- `scripts/ollama_harness.py`
- `scripts/verify_ollama_dispatch.py`
- `platform_tests/scripts/test_ollama_harness.py`
- `platform_tests/scripts/test_ollama_routing_config.py`
- `platform_tests/scripts/test_verify_ollama_dispatch.py`

Related bridge files:

- `bridge/gtkb-ollama-qwen-full-lo-route-gate-compliant-001.md`
- `bridge/gtkb-ollama-qwen-full-lo-route-gate-compliant-002.md`
- `bridge/gtkb-ollama-qwen-full-lo-route-gate-compliant-003.md`
- `bridge/INDEX.md`

Note: the worktree contained many pre-existing unrelated dirty paths before this slice. They are not part of this implementation claim.

## Recommended Commit Type

- Recommended commit type: `feat`
- Justification: the runtime route, harness context, and dispatch readiness behavior now enable Ollama Qwen to operate as the active full-tool Loyal Opposition bridge target.

## Acceptance Criteria Status

- [x] Active Ollama `bridge-review` and `verification` skills resolve to `qwen3-coder-next-cloud` through `.ollama/routing.toml`.
- [x] Active LO route exposes `Read`, `Write`, `Edit`, `Grep`, `Glob`, and `Bash`.
- [x] Ollama bridge-review and verification invocations receive compact Loyal Opposition bridge context before the user prompt.
- [x] Live readiness succeeds for the active Ollama LO route.
- [x] Focused pytest, ruff check, and ruff format check pass for changed files.
- [x] Qwen smoke bridge actions filed GO verdicts through guarded tools for the proposal and amendment threads.
- [x] Implementation authorization succeeded before implementation started.

## Risk And Rollback

Residual risk: Qwen has shown it can file bridge verdicts under bounded prompts, but copied preflight output may preserve mojibake from existing terminal output. That is cosmetic and should be monitored during LO verification quality assessment.

Rollback: restore `.ollama/routing.toml` skill routes to the prior read/search-only route, remove LO system-prompt injection, restore `OLLAMA_DISPATCH_REQUIRED_TOOLS` to the prior read/search-only set, and revert focused tests. Bridge artifacts remain audit history.

## Loyal Opposition Asks

1. Verify live routing and readiness use `.ollama/routing.toml` as the selected-model SoT and do not hardcode model version in Python runtime logic.
2. Verify full guarded LO tools are required for dispatch readiness.
3. Verify Qwen-authored GO verdicts demonstrate practical bridge-file write capability through the guarded harness path.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
