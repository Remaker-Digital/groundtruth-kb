NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f39ff-4e44-7a32-b5d0-6969ec4d55ec
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex interactive Prime Builder

# GT-KB Bridge Implementation Report - gtkb-wi5060-ollama-route-max-turn-budget - 003

bridge_kind: implementation_report
Document: gtkb-wi5060-ollama-route-max-turn-budget
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5060-ollama-route-max-turn-budget-002.md
Approved proposal: bridge/gtkb-wi5060-ollama-route-max-turn-budget-001.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5060-HARNESS-REPAIR-20260707
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5060
Recommended commit type: fix(harness):

## Implementation Claim

Ollama/D route dispatch can now use a route-configured max-turn budget without requiring every dispatcher invocation to pass `--max-turns`.

`scripts/ollama_harness.py` now carries optional `RoutingConfig.max_turns`, parses `[routing.ollama] max_turns` with positive-integer validation, and resolves runtime max turns through `resolve_runtime_max_turns(args, config, argv)`. The resolver mirrors the existing route-aware timeout behavior: if route config supplies `max_turns` and the CLI did not explicitly supply `--max-turns`, the route value is used; if the CLI supplies `--max-turns`, the explicit CLI value remains authoritative.

`.api-harness/routing.toml` now sets `[routing.ollama] max_turns = 200`, increasing the default D bridge-review budget above the exhausted `80` turn default while preserving the existing session timeout and repeated-tool-loop fail-closed guard.

`platform_tests/scripts/test_ollama_harness.py` adds focused coverage for config parsing, non-positive rejection, fractional rejection, route default resolution, and explicit CLI override precedence. `platform_tests/scripts/test_dispatcher_budget_constants_regression.py` was rerun unchanged to preserve the existing parser-default and budget invariant coverage.

## Implementation-Start Evidence

- Latest bridge status before implementation: `GO` at `bridge/gtkb-wi5060-ollama-route-max-turn-budget-002.md`.
- Work-intent claim: `python scripts/bridge_claim_cli.py status gtkb-wi5060-ollama-route-max-turn-budget` reported `claim_kind: go_implementation`, `acting_role: prime-builder`, `latest_bridge_status: GO`, `expired: false`, session `019f39ff-4e44-7a32-b5d0-6969ec4d55ec`, implementation deadline `2026-07-07T08:31:03Z`, and TTL expiration `2026-07-07T08:41:03Z`.
- Implementation-start packet: `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5060-ollama-route-max-turn-budget` reported `packet_hash: sha256:94ae1f4f7f22b47a49c524de13d1c126d84cdeecb62b4df190ecf8a3e64abbdf`, `latest_status: GO`, `proposal_file: bridge/gtkb-wi5060-ollama-route-max-turn-budget-001.md`, `go_file: bridge/gtkb-wi5060-ollama-route-max-turn-budget-002.md`, and expiration `2026-07-07T10:04:54Z`.
- Approved target paths: `.api-harness/routing.toml`, `scripts/ollama_harness.py`, `platform_tests/scripts/test_ollama_harness.py`, and `platform_tests/scripts/test_dispatcher_budget_constants_regression.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected source/test/config changes require a live bridge GO, matching target paths, and append-only bridge evidence.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation must stay inside active project authorization.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not bypass bridge GO, implementation-start gates, post-implementation reporting, or verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal and report must link work item, project, PAUTH, target paths, specs, and verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - implementation proposals require Project Authorization, Project, Work Item, and target_paths metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must map behavior claims to concrete tests/evidence before VERIFIED.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher-selected harnesses must support real bridge-dispatch work in their assigned roles.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher status and health commands are the live topology and reliability evidence surface.
- `GOV-ENV-LOCAL-AUTHORITY-001` - no credential lifecycle, disclosure, provider secret mutation, or key rotation is in scope.
- `GOV-STANDING-BACKLOG-001` - this follow-on uses WI-5060 evidence without mutating unrelated backlog state.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner goal, PAUTH, proposal, implementation report, verification, and runtime evidence remain linked artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the change is handled through a durable artifact chain rather than an untracked patch.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the fresh D runtime failure is preserved as follow-on bridge evidence despite WI-5060's terminal MemBase state.

## Owner Decisions / Input

No new owner decision is required by this implementation report. Mike already directed the A/C/D/F harness repair goal and authorized the headless fix in this session. The current change stayed inside the active WI-5060 PAUTH, the Loyal Opposition GO, and the implementation-start target paths. No credential lifecycle, deployment, destructive cleanup, broad bulk status mutation, secret disclosure, untracked file deletion, or D/F eligibility re-enable operation was performed.

## Prior Deliberations

- `DELIB-20260707-HARNESS-A-C-D-F-REPAIR-GOAL` - owner-directed goal to test and fix harnesses A, C, D, and F for their currently assigned roles.
- `bridge/gtkb-wi5060-shim-max-turn-exhaustion-authorization-002.md` - Loyal Opposition GO authorizing the bounded PAUTH path, while requiring a separate implementation proposal and GO before source/config mutation.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5060-HARNESS-REPAIR-20260707` - active bounded WI-5060 source/test/config/governance authorization.
- `bridge/gtkb-wi5060-harness-readiness-repair-004.md` - VERIFIED prior shim readiness repair, including blank-final-output and repeated identical tool-loop termination.
- `bridge/gtkb-wi5060-openrouter-connection-reset-retry-004.md` - VERIFIED OpenRouter/F retry repair; that verification path exposed D's need for a larger real-review turn budget.
- `bridge/gtkb-wi5060-ollama-route-max-turn-budget-001.md` - approved implementation proposal for this slice.
- `bridge/gtkb-wi5060-ollama-route-max-turn-budget-002.md` - Loyal Opposition GO for this slice.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | `python scripts/bridge_claim_cli.py status gtkb-wi5060-ollama-route-max-turn-budget`; `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5060-ollama-route-max-turn-budget`. Latest status was `GO`; claim was current and unexpired for this session; implementation-start authorized only the listed target paths. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | This report carries the active PAUTH, project, work item, approved proposal, GO response, and target paths from the approved bridge chain. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | LO verdict `bridge/gtkb-wi5060-ollama-route-max-turn-budget-002.md` records a clean applicability preflight with `missing_required_specs: []` and no clause-test blocking gaps. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest, Ruff check, Ruff format check, dispatcher health, bridge-dispatch status, and MemBase backlog status commands are listed below with observed results. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `platform_tests/scripts/test_ollama_harness.py` now proves route-configured max turns are loaded and applied when default dispatch omits `--max-turns`, while explicit CLI overrides still win. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | `gt bridge dispatch health --json` reported `health_status: PASS`; `gt status --component bridge-dispatch --json` reported overall `PASS` for the daemon-only dispatch substrate. |
| `GOV-ENV-LOCAL-AUTHORITY-001` | Diff review confirmed no env file, credential, provider account, key, model route, or credential lifecycle mutation. |

## Commands Run

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_dispatcher_budget_constants_regression.py -q --tb=short --basetemp .test-tmp\pytest-ollama-route-max-turns`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check --no-cache scripts/ollama_harness.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_dispatcher_budget_constants_regression.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check --no-cache scripts/ollama_harness.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_dispatcher_budget_constants_regression.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli bridge dispatch health --json`
- `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli bridge dispatch status --json`
- `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli status --component bridge-dispatch --json`
- `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli backlog show WI-5060`
- `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli backlog status`
- `groundtruth-kb\.venv\Scripts\python.exe .claude\skills\bridge\helpers\impl_report_bridge.py plan gtkb-wi5060-ollama-route-max-turn-budget --compact`

## Observed Results

- Focused pytest: `61 passed, 1 warning in 1.20s`.
- Ruff check: exited 0 with `All checks passed!`.
- Ruff format check: exited 0 with `3 files already formatted`.
- Dispatcher health: `health_status: PASS`; daemon running with fresh heartbeat, supervisor registered/enabled/hidden/using `pythonw.exe`, and watchdog registered/enabled/hidden/using `pythonw.exe`.
- Dispatcher status: `health_status: PASS`; Antigravity/C and Ollama/D are active and selected for Loyal Opposition dispatch, and OpenRouter/F is active and selected for Prime Builder dispatch.
- Bridge-dispatch status: overall `PASS`; dispatcher daemon is the only automated bridge substrate, with retired OS/smart pollers reported as retired.
- MemBase work item check: `WI-5060` is `resolved`, project `PROJECT-GTKB-RELIABILITY-FIXES`, component `harness`, title `Shim harnesses (OpenRouter/F, Ollama/D) hit max-turn exhaustion on real bridge dispatches`.
- Backlog status: `PROJECT-GTKB-RELIABILITY-FIXES` remains active with `wi=27 :: open=8, resolved=19`.
- Implementation-report plan: latest status `GO`, next version `003`, report path `bridge/gtkb-wi5060-ollama-route-max-turn-budget-003.md`.

## Original Failure Evidence Closed By This Slice

- The D/Ollama Loyal Opposition review run `2026-07-07T07-35-47Z-loyal-opposition-D-6f0bf7` exited `1` with stderr exactly `ollama_harness: max-turn exhaustion before final assistant text`.
- A later D/Ollama attempt to review this same max-turn proposal, `2026-07-07T07-52-15Z-loyal-opposition-D-62fdfe`, failed the same way. Antigravity/C then successfully reviewed the proposal and wrote `bridge/gtkb-wi5060-ollama-route-max-turn-budget-002.md`.
- Prior dispatcher health/status now classifies D's `max_turn_exhaustion` evidence as stale because `WI-5060` is terminal in MemBase. This implementation does not claim a completed D real bridge review until a subsequent dispatch or smoke evidence proves it; it fixes the default route budget that caused the exhausted real-review attempts.

## Files Changed

Ollama/D max-turn slice reported here:

- `.api-harness/routing.toml`
- `scripts/ollama_harness.py`
- `platform_tests/scripts/test_ollama_harness.py`
- `platform_tests/scripts/test_dispatcher_budget_constants_regression.py` (rerun unchanged as an approved regression target)

Scoped diff stat:

```text
.api-harness/routing.toml                     |  1 +
platform_tests/scripts/test_ollama_harness.py | 59 +++++++++++++++++++++++++++
scripts/ollama_harness.py                     | 34 ++++++++++++++-
3 files changed, 93 insertions(+), 1 deletion(-)
```

Adjacent WI-5060 work for `gtkb-wi5060-no-window-helper-force-windows-compat` remains a separate GO-authorized thread and is not claimed as completed by this report.

## Acceptance Criteria Status

- [x] `[routing.ollama] max_turns` is optional and loaded into `RoutingConfig`.
- [x] Invalid, fractional, or non-positive route-configured max-turn values fail closed.
- [x] Dispatcher/default invocations that omit `--max-turns` use the route-configured max-turn budget.
- [x] Explicit CLI `--max-turns` continues to override route configuration for focused diagnostics and small smoke tests.
- [x] `.api-harness/routing.toml` sets D's Ollama route max-turn budget to `200`.
- [x] Focused pytest and Ruff checks pass for the changed Python files and targeted regression tests.
- [x] Dispatcher health/status remain `PASS`; no registry, eligibility, credential, or model-route mutation is part of this slice.

## Risk And Rollback

Residual risk is moderate and isolated to D runtime duration. Raising D's default route max-turn budget may allow legitimate bridge reviews to complete, but it can also give a non-identical unproductive loop more turns. The existing repeated identical tool-signature guard, HTTP operation timeout, route session timeout, and fail-closed harness error path remain in place.

Rollback is a source/config/test revert for `.api-harness/routing.toml`, `scripts/ollama_harness.py`, and `platform_tests/scripts/test_ollama_harness.py`. Bridge files remain append-only governance records.

## Recommended Commit Type

- Recommended commit type: `fix(harness):`
- Justification: this is a narrow harness reliability fix for Ollama/D real bridge-review turn-budget exhaustion with focused regression tests.

## Loyal Opposition Asks

1. Verify the Ollama/D route max-turn implementation against the approved proposal, linked specifications, and command evidence.
2. Return VERIFIED if the implementation satisfies the GO; otherwise return NO-GO with concrete findings.
