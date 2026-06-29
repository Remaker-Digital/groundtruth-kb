NEW
author_identity: codex
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: gpt-5-codex
author_model_version: 2026-06-29
author_model_configuration: Codex desktop Prime Builder session; approval_policy=never; harness parity phase 2 implementation

# GT-KB Bridge Implementation Report - gtkb-wi4904-provider-harness-dispatch-readiness - 003

bridge_kind: implementation_report
Document: gtkb-wi4904-provider-harness-dispatch-readiness
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi4904-provider-harness-dispatch-readiness-002.md
Approved proposal: bridge/gtkb-wi4904-provider-harness-dispatch-readiness-001.md
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4904
Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Recommended commit type: feat:

## Implementation Claim

WI-4904 is implemented for the provider-harness readiness slice. The Ollama and OpenRouter harness shims now enforce bounded whole-session runtime with a new `--session-timeout` CLI option, cap per-turn chat calls and retry sleeps against the remaining session budget, and cap Bash tool `timeout_seconds` so a provider tool loop cannot exceed the dispatch session envelope. The implementation keeps provider harnesses receive-only and does not change dispatcher topology, production deployment, or credential values.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `GOV-HARNESS-ROLE-PORTABILITY-001`
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

No new owner decision is required. This report carries forward the owner directive to make harness parity a release blocker and the active Phase 2 project authorization.

## Prior Deliberations

- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE`
- `bridge/gtkb-wi4904-provider-harness-dispatch-readiness-001.md` - approved implementation proposal.
- `bridge/gtkb-wi4904-provider-harness-dispatch-readiness-002.md` - Loyal Opposition GO verdict.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | WI-4904 bridge applicability preflight passed; clause preflight passed with 0 blocking gaps. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight found no missing required or advisory specs. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Proposal and GO verdict carry Project, Work Item, PAUTH, and target path metadata; implementation stayed inside provider harness source/test target paths. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Shim-focused tests passed; provider proposal bundle passed; broader parity/provider bundle passed; ruff lint and format checks passed. |
| `GOV-STANDING-BACKLOG-001` / `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | WI-4904 is the tracked Phase 2 work item and implementation-start authorization was acquired before protected edits. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` / `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Ollama and OpenRouter retain the canonical tool envelope and guard path; new tests prove session budgets apply before provider chat turns and Bash tool calls. |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | Provider shims remain role-neutral receive surfaces; no Prime/LO role is hard-coded into timeout behavior. |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | Strict Phase 2 parity matrix returned overall `PASS`, supported=52, waived=8, invalid waivers=0. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Provider runtime bounding is inside the harness shims and does not restore retired pollers or mutate dispatch selection rules. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Evidence is captured in this bridge report and tests, not harness-local scratchpads. |

## Commands Run

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi4904-provider-harness-dispatch-readiness
groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi4904-provider-harness-dispatch-readiness
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_ollama_harness.py platform_tests\scripts\test_openrouter_harness.py platform_tests\scripts\test_verify_antigravity_dispatch.py -q --tb=short
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\ollama_harness.py scripts\openrouter_harness.py scripts\verify_antigravity_dispatch.py platform_tests\scripts\test_ollama_harness.py platform_tests\scripts\test_openrouter_harness.py platform_tests\scripts\test_verify_antigravity_dispatch.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\ollama_harness.py scripts\openrouter_harness.py scripts\verify_antigravity_dispatch.py platform_tests\scripts\test_ollama_harness.py platform_tests\scripts\test_openrouter_harness.py platform_tests\scripts\test_verify_antigravity_dispatch.py
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_verify_ollama_dispatch.py platform_tests\scripts\test_ollama_harness.py platform_tests\scripts\test_openrouter_harness.py platform_tests\scripts\test_openrouter_routing_deepseek.py -q --tb=short
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_dispatch_env_local_auth_loader.py platform_tests\scripts\test_dispatch_parity.py platform_tests\scripts\test_harness_parity_phase2.py platform_tests\scripts\test_generate_antigravity_skill_adapters.py -q --tb=short
groundtruth-kb\.venv\Scripts\python.exe scripts\harness_parity_phase2.py --project-root . --format markdown --strict
groundtruth-kb\.venv\Scripts\python.exe scripts\verify_ollama_dispatch.py --readiness-only --skip-daemon --json
groundtruth-kb\.venv\Scripts\python.exe scripts\verify_ollama_dispatch.py --help
groundtruth-kb\.venv\Scripts\python.exe scripts\ollama_harness.py --help
groundtruth-kb\.venv\Scripts\python.exe scripts\openrouter_harness.py --help
```

## Observed Results

- Applicability preflight: `preflight_passed: true`, no missing required specs, no missing advisory specs.
- Clause preflight: 5 clauses evaluated, 2 `must_apply`, 0 evidence gaps, 0 blocking gaps.
- Shim-focused tests: `76 passed in 2.36s`.
- Ruff: `All checks passed!`; format check: `6 files already formatted`.
- Provider proposal bundle: `88 passed, 1 skipped in 2.03s`.
- Broader parity/provider bundle: `31 passed in 1.77s`.
- Strict Phase 2 parity matrix: overall `PASS`, supported=52, waived=8, active waivers=8, invalid waivers=0.
- Ollama dispatch readiness: `ready: true`; only warning was the known non-blocking absence of a Windows scheduled task or service matching Ollama.
- `ollama_harness.py --help` and `openrouter_harness.py --help` expose `--session-timeout`.

## Files Changed

- `scripts/ollama_harness.py`
- `scripts/openrouter_harness.py`
- `platform_tests/scripts/test_ollama_harness.py`
- `platform_tests/scripts/test_openrouter_harness.py`

## Recommended Commit Type

- Recommended commit type: `feat:`
- Diff-stat justification: provider harness behavior changes add a release-readiness capability and matching tests.

```text
 scripts/ollama_harness.py                         | 56 +++++++++++++-
 scripts/openrouter_harness.py                     | 62 ++++++++++++++-
 platform_tests/scripts/test_ollama_harness.py     | 79 +++++++++++++++++++
 platform_tests/scripts/test_openrouter_harness.py | 95 ++++++++++++++++++++++
```

## Acceptance Criteria Status

- [x] Provider harness dispatch sessions are bounded by a whole-session timeout instead of relying only on per-call timeouts.
- [x] Provider chat retries and Bash tool calls are capped against the remaining session budget.
- [x] Ollama readiness still resolves registry argv, shim presence, routing model, and required tools.
- [x] OpenRouter and Ollama CLI surfaces expose the new timeout control.
- [x] Focused provider tests and strict Phase 2 parity checks pass.
- [x] No credential values, dispatcher topology, production deployment, or retired poller surfaces were changed.

## Risk And Rollback

Residual risk is limited to provider long-running behavior: very slow legitimate provider sessions can now fail closed when the session budget is exhausted. This is intentional for dispatcher release health. Rollback is the four listed files in this report; bridge audit files remain append-only.

## Loyal Opposition Asks

1. Verify that the provider harness timeout enforcement and tests satisfy the approved WI-4904 proposal.
2. Confirm the scoped changed-file list excludes unrelated dirty worktree files.
3. Return VERIFIED if the implementation satisfies the linked specifications, otherwise return NO-GO with concrete findings.
