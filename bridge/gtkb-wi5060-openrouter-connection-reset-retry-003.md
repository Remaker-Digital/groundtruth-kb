NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f39ff-4e44-7a32-b5d0-6969ec4d55ec
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex interactive Prime Builder

# GT-KB Bridge Implementation Report - gtkb-wi5060-openrouter-connection-reset-retry - 003

bridge_kind: implementation_report
Document: gtkb-wi5060-openrouter-connection-reset-retry
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5060-openrouter-connection-reset-retry-002.md
Approved proposal: bridge/gtkb-wi5060-openrouter-connection-reset-retry-001.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5060-HARNESS-REPAIR-20260707
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5060
Recommended commit type: fix(harness):

## Implementation Claim

The OpenRouter/F harness transport wrapper now handles direct Python socket connection failures inside the existing bounded retry loop.

`scripts/openrouter_harness.py` changed `call_openrouter_chat` so `ConnectionError` exceptions raised directly from `urllib.request.urlopen` follow the same retry/fail-closed path as `urllib.error.URLError`. `ConnectionResetError` is a `ConnectionError` subclass, so the observed `[WinError 10054]` provider-side reset is retried instead of escaping as a raw traceback. The existing `CHAT_MAX_ATTEMPTS`, timeout budget, backoff behavior, endpoint/payload handling, cloud-default OpenRouter model routing, HTTP 401/403 fail-fast behavior, and response parsing behavior are unchanged.

`platform_tests/scripts/test_openrouter_harness.py` adds focused WI-5060 regression coverage for:

- first-attempt `ConnectionResetError` followed by a valid OpenRouter-style response succeeds after retry;
- repeated `ConnectionResetError` exhausts the existing attempt budget and raises `OpenRouterHarnessError` rather than leaking the raw socket exception.

## Implementation-Start Evidence

- Live bridge status before implementation: `groundtruth-kb/.venv/Scripts/gt.exe bridge show gtkb-wi5060-openrouter-connection-reset-retry --json` reported latest status `GO` at `bridge/gtkb-wi5060-openrouter-connection-reset-retry-002.md`.
- Work-intent claim: `python scripts/bridge_claim_cli.py status gtkb-wi5060-openrouter-connection-reset-retry` reported session `019f39ff-4e44-7a32-b5d0-6969ec4d55ec`, acting role `prime-builder`, claim kind `go_implementation`, latest bridge status `GO`, and `expired: false`.
- Approved target paths: `scripts/openrouter_harness.py` and `platform_tests/scripts/test_openrouter_harness.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected source/test changes require a live bridge GO with matching target paths.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation must stay inside active project authorization.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not bypass bridge GO or implementation-start gates.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal must link work item, project, PAUTH, target paths, specs, and verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - implementation proposals require Project Authorization, Project, Work Item, and target_paths metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must map behavior claims to concrete tests/evidence before VERIFIED.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher-owned harnesses must fail predictably and remain process-supervisable during transient provider failures.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher status/health/report commands are the authoritative topology and readiness evidence surface.
- `GOV-ENV-LOCAL-AUTHORITY-001` - no credential lifecycle, disclosure, provider credential mutation, or key rotation is in scope.

## Owner Decisions / Input

No new owner decision is required by this implementation report. Mike already authorized the A/C/D/F harness repair goal and the headless fix; this OpenRouter slice stayed inside the active WI-5060 PAUTH, approved GO scope, and listed target paths.

## Prior Deliberations

- `DELIB-20260707-HARNESS-A-C-D-F-REPAIR-GOAL` - owner-directed goal to test and fix harnesses A, C, D, and F for their currently assigned roles.
- `bridge/gtkb-wi5060-shim-max-turn-exhaustion-authorization-002.md` - GO authorizing the targeted WI-5060 PAUTH path before implementation.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5060-HARNESS-REPAIR-20260707` - bounded WI-5060 source/test/config/governance authorization.
- `bridge/gtkb-wi5060-harness-readiness-repair-004.md` - VERIFIED original shim/readiness repair.
- `bridge/gtkb-wi5060-headless-dispatch-window-hardening-004.md` - VERIFIED headless dispatch window hardening.
- `bridge/gtkb-wi5060-openrouter-connection-reset-retry-001.md` - approved proposal for this slice.
- `bridge/gtkb-wi5060-openrouter-connection-reset-retry-002.md` - Loyal Opposition GO for this slice.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | `groundtruth-kb/.venv/Scripts/gt.exe bridge show gtkb-wi5060-openrouter-connection-reset-retry --json`; `python scripts/bridge_claim_cli.py status gtkb-wi5060-openrouter-connection-reset-retry`. Latest status was `GO`; claim was current and unexpired for this session. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | This report carries the active PAUTH, project, work item, approved proposal, GO response, and target paths from the approved bridge chain. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5060-openrouter-connection-reset-retry` passed with `missing_required_specs: []`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest, ruff check, ruff format check, dispatcher health, and dispatcher status commands are listed below with observed results. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `platform_tests/scripts/test_openrouter_harness.py` now verifies direct connection resets retry and then either succeed or fail closed as `OpenRouterHarnessError`. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | `groundtruth-kb/.venv/Scripts/gt.exe bridge dispatch health --json` reported `health_status: PASS`; `gt bridge dispatch status --json` reported F active/selected for Prime Builder dispatch and C/D active/selected for Loyal Opposition dispatch. |
| `GOV-ENV-LOCAL-AUTHORITY-001` | Diff review confirmed no env file, credential, provider account, key, or model routing mutation. The OpenRouter cloud-default model behavior remains untouched. |

## Commands Run

- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_openrouter_harness.py -q --tb=short --basetemp .test-tmp/pytest-openrouter-connection-reset`
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_verify_ollama_dispatch.py platform_tests/scripts/test_windows_subprocess.py -q --tb=short --basetemp .test-tmp/pytest-verify-ollama-force-windows`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/openrouter_harness.py platform_tests/scripts/test_openrouter_harness.py scripts/windows_subprocess.py scripts/verify_ollama_dispatch.py platform_tests/scripts/test_windows_subprocess.py`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/openrouter_harness.py platform_tests/scripts/test_openrouter_harness.py scripts/windows_subprocess.py scripts/verify_ollama_dispatch.py platform_tests/scripts/test_windows_subprocess.py`
- `groundtruth-kb/.venv/Scripts/gt.exe bridge dispatch health --json`
- `groundtruth-kb/.venv/Scripts/gt.exe bridge dispatch status --json`
- `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5060-openrouter-connection-reset-retry`

## Observed Results

- OpenRouter focused pytest: `39 passed, 1 warning in 0.80s`.
- No-window helper focused pytest, run to keep the adjacent WI-5060 harness slice honest: `25 passed, 1 skipped, 1 warning in 0.53s`.
- Ruff check: exited 0 with `All checks passed!`; it also emitted a cache write warning for `.ruff_cache` access denied, which did not affect lint results.
- Ruff format check: exited 0 with `5 files already formatted`.
- Dispatcher health: `health_status: PASS`; daemon running with fresh heartbeat, supervisor registered/enabled/hidden/using `pythonw.exe`, watchdog registered/enabled/hidden/using `pythonw.exe`.
- Dispatcher status: `health_status: PASS`; OpenRouter/F is active and selected for Prime Builder dispatch; Antigravity/C and Ollama/D are active and selected for Loyal Opposition dispatch. A/C/D/F are therefore functional in their currently assigned roles, with A active as the interactive Prime Builder and C/D/F dispatchable per registry selection.
- Applicability preflight: passed with `missing_required_specs: []`.

## Original Failure Evidence Closed By This Slice

- `.gtkb-state/bridge-poller/dispatch-runs/2026-07-07T07-20-24Z-prime-builder-F-4c4b7e.exit_code` contained `1`.
- `.gtkb-state/bridge-poller/dispatch-runs/2026-07-07T07-20-24Z-prime-builder-F-4c4b7e.stderr.log` showed `ConnectionResetError: [WinError 10054] An existing connection was forcibly closed by the remote host` escaping from `scripts/openrouter_harness.py` at the `urllib.request.urlopen` call inside `call_openrouter_chat`.
- The new tests exercise that exact exception class and prove it no longer escapes the wrapper on retryable attempts.

## Files Changed

OpenRouter slice reported here:

- `scripts/openrouter_harness.py`
- `platform_tests/scripts/test_openrouter_harness.py`

Scoped OpenRouter diff stat:

```text
platform_tests/scripts/test_openrouter_harness.py | 24 +++++++++++++++++++++++
scripts/openrouter_harness.py                     |  2 +-
2 files changed, 25 insertions(+), 1 deletion(-)
```

Adjacent WI-5060 no-window helper files are present in the worktree under their own bridge thread, `gtkb-wi5060-no-window-helper-force-windows-compat`. That thread remains separately GO-authorized but was held by F's failed claim during this report, so those changes are not claimed as completed by this OpenRouter report.

## Acceptance Criteria Status

- [x] A direct `ConnectionResetError` raised by `urllib.request.urlopen` is handled by the existing bounded retry/fail-closed path.
- [x] A first-attempt connection reset followed by a valid OpenRouter response succeeds.
- [x] Repeated direct connection resets exhaust the existing attempt budget and raise `OpenRouterHarnessError`, not a raw traceback.
- [x] Existing HTTP retry, 429 backpressure, non-transient HTTP 401/403 fail-fast, and non-JSON retry tests continue to pass as part of the 39-test OpenRouter focused suite.
- [x] Ruff check and format check pass for `scripts/openrouter_harness.py` and `platform_tests/scripts/test_openrouter_harness.py`.
- [x] Dispatcher health remains `PASS`; no registry or dispatch eligibility mutation is part of this slice.

## Risk And Rollback

Residual risk is low. The behavior change is limited to classifying direct `ConnectionError` transport failures into an already existing bounded retry path. The main behavioral consequence is that direct socket resets can now spend up to the existing retry budget before failing closed as `OpenRouterHarnessError`.

Rollback is a source/test revert for `scripts/openrouter_harness.py` and `platform_tests/scripts/test_openrouter_harness.py`. Bridge files remain append-only governance records.

## Recommended Commit Type

- Recommended commit type: `fix(harness):`
- Justification: this is a narrow harness reliability fix for OpenRouter/F transport failures with focused regression tests.

## Loyal Opposition Asks

1. Verify the OpenRouter implementation against the approved proposal, linked specifications, and command evidence.
2. Return VERIFIED if the implementation satisfies the GO; otherwise return NO-GO with concrete findings.
