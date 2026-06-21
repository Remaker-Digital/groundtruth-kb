NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019eebd5-bc7d-7011-bcb4-6d87b998a341
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex interactive Prime Builder session; owner-declared ::init gtkb pb; default execution mode

# GT-KB Bridge Implementation Report - gtkb-codex-sessionstart-userpromptsubmit-hook-failures - 003

bridge_kind: implementation_report
Document: gtkb-codex-sessionstart-userpromptsubmit-hook-failures
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-codex-sessionstart-userpromptsubmit-hook-failures-002.md
Approved proposal: bridge/gtkb-codex-sessionstart-userpromptsubmit-hook-failures-001.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4462
Recommended commit type: fix:

## Implementation Claim

Implemented the approved Codex hook-timeout defect fix inside the declared target paths only:

- `.codex/hooks.json`: raised the Codex `SessionStart` hook entry for `.codex/gtkb-hooks/session_start_dispatch.py` from `60` seconds to `180` seconds, which is strictly greater than the inner startup-service timeout constant of `150.0` seconds.
- `.codex/hooks.json`: raised the Codex `UserPromptSubmit` hook entry for `.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py` from `15` seconds to `60` seconds.
- `platform_tests/scripts/test_codex_hook_parity.py`: added regression assertions for both timeout-budget invariants, deriving the inner `STARTUP_SERVICE_TIMEOUT_SECONDS` value from `scripts/session_start_dispatch_core.py`.
- `platform_tests/scripts/test_codex_hook_parity.py`: updated two stale assertions in the same targeted parity suite so the suite reflects current TAFE/dispatcher bridge-state wording and the current `_startup_service_timeout_seconds()` dispatch-core contract.

The implementation removes the timeout-budget inversion that let the Codex hook runner kill a still-valid fail-soft SessionStart or wrap-up hook before the hook's own timeout and fallback path could complete.

## Specification Links

- `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-RELIABILITY-FAST-LANE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `SPEC-AUQ-POLICY-ENGINE-001`

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`: active standing authorization for small defect/reliability fixes under `PROJECT-GTKB-RELIABILITY-FIXES`; implementation authorization packet created successfully at 2026-06-21T20:25:15Z with packet hash `sha256:cba3dac126f36a80107284d467b20c7e3c6637929f5c7b6bcf523b63ae5463a5`.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`: reliability fast-lane owner direction carried forward from the proposal.
- `DELIB-20265457`: owner AUQ authorizing NEW proposals for the open `PROJECT-GTKB-RELIABILITY-FIXES` work-item batch, including WI-4462.

No new owner decision was required for this implementation report.

## Prior Deliberations

- `bridge/gtkb-codex-sessionstart-userpromptsubmit-hook-failures-001.md`: approved implementation proposal carried forward.
- `bridge/gtkb-codex-sessionstart-userpromptsubmit-hook-failures-002.md`: Loyal Opposition GO verdict authorizing implementation.
- `DELIB-1642`, `DELIB-1641`, `DELIB-1643`, `DELIB-1079`, and `DELIB-20264231`: carried forward from the proposal as the relevant SessionStart and hook-parity deliberation context.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001` | `python -m pytest platform_tests/scripts/test_codex_hook_parity.py -q --tb=short` passed: 13 tests collected, 13 passed. The suite includes the new `test_codex_sessionstart_hook_timeout_exceeds_inner_startup_service_timeout` and `test_codex_userpromptsubmit_wrapup_hook_has_headroom_timeout` assertions. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | The targeted parity suite passed and `python -c "<timeout invariant probe>"` reported `{"inner_startup_service_timeout": 150.0, "session_start_outer_gt_inner": true, "session_start_timeout": 180, "wrapup_timeout": 60, "wrapup_timeout_gte_60": true}`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Live thread check showed latest status `GO` at `bridge/gtkb-codex-sessionstart-userpromptsubmit-hook-failures-002.md`; `python scripts/bridge_claim_cli.py claim gtkb-codex-sessionstart-userpromptsubmit-hook-failures` acquired a `go_implementation` claim; `python scripts/implementation_authorization.py begin --bridge-id gtkb-codex-sessionstart-userpromptsubmit-hook-failures` returned authorized with target path globs exactly `.codex/hooks.json` and `platform_tests/scripts/test_codex_hook_parity.py`. |
| `GOV-RELIABILITY-FAST-LANE-001` | The diff remains a bounded defect fix in one hook configuration file plus one parity test file, with no public API, CLI, deployment, or application-surface change. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries forward the proposal's linked governing specifications and files the report in the same bridge thread for Loyal Opposition verification. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table maps every linked governing surface to executed verification evidence or a scope-preservation check. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | The report header carries `Project Authorization`, `Project`, and `Work Item` metadata matching the authorized proposal and implementation packet. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | The corrected timeout budget is preserved in `.codex/hooks.json`, and the invariant is preserved as regression coverage in `platform_tests/scripts/test_codex_hook_parity.py`. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | The implementation converts the incident into an artifact-backed invariant rather than an operational note. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | The hook-config edit and the governing parity-test edit were made together and verified together. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | No file under `applications/` was edited; `python -m json.tool .codex/hooks.json > $null` validated the in-root Codex hook JSON artifact. |
| `SPEC-AUQ-POLICY-ENGINE-001` | The targeted parity suite passed after the changes, preserving the existing AUQ-adjacent parity assertions in the edited test module. |

## Commands Run

- `python .codex/skills/bridge/helpers/show_thread_bridge.py gtkb-codex-sessionstart-userpromptsubmit-hook-failures --format json` - confirmed latest thread status `GO` at `bridge/gtkb-codex-sessionstart-userpromptsubmit-hook-failures-002.md`.
- `python .codex/skills/bridge/helpers/scan_bridge.py --role prime-builder --format json` - confirmed the thread appears in Prime Builder actionable state with latest status `GO`.
- `python scripts/bridge_claim_cli.py claim gtkb-codex-sessionstart-userpromptsubmit-hook-failures` - acquired `go_implementation` claim for session `019eebd5-bc7d-7011-bcb4-6d87b998a341`.
- `python scripts/implementation_authorization.py begin --bridge-id gtkb-codex-sessionstart-userpromptsubmit-hook-failures` - authorized implementation; packet hash `sha256:cba3dac126f36a80107284d467b20c7e3c6637929f5c7b6bcf523b63ae5463a5`.
- `python -m pytest platform_tests/scripts/test_codex_hook_parity.py -q --tb=short` - passed, 13 tests collected, 13 passed.
- `python -m ruff check platform_tests/scripts/test_codex_hook_parity.py` - passed, `All checks passed!`.
- `python -m ruff format --check platform_tests/scripts/test_codex_hook_parity.py` - passed, `1 file already formatted`.
- `python -m json.tool .codex/hooks.json > $null` - passed with exit code 0.
- `python -c "<timeout invariant probe>"` - passed; printed `session_start_timeout=180`, `inner_startup_service_timeout=150.0`, `session_start_outer_gt_inner=true`, `wrapup_timeout=60`, `wrapup_timeout_gte_60=true`.

## Observed Non-Gate Command Behavior

The proposal listed ruff commands that included `.codex/hooks.json`. Running those exact commands showed that this ruff version treats an explicitly passed JSON file as Python rather than no-oping it:

- `python -m ruff check .codex/hooks.json platform_tests/scripts/test_codex_hook_parity.py` failed with `B018 Found useless expression` at `.codex/hooks.json:1:1`.
- `python -m ruff format --check .codex/hooks.json platform_tests/scripts/test_codex_hook_parity.py` failed with `Would reformat: .codex\hooks.json`.

The verification substitution was therefore: `python -m json.tool .codex/hooks.json > $null` for the JSON artifact, and ruff lint/format gates on the changed Python test file. The proposal's acceptance criteria specifically require ruff to be clean on the changed Python test file; those gates passed.

## Files Changed

- `.codex/hooks.json`
- `platform_tests/scripts/test_codex_hook_parity.py`
- `bridge/gtkb-codex-sessionstart-userpromptsubmit-hook-failures-003.md` (this implementation report)

Not part of this implementation claim: `platform_tests/scripts/test_claude_session_start_dispatcher.py` was already dirty in the worktree and is outside the approved `target_paths`; it was not edited for this bridge thread. The untracked `bridge/gtkb-wi4723-verified-finalize-index-lock-retry-001.md` was also pre-existing and is unrelated.

## Recommended Commit Type

- Recommended commit type: `fix:`
- Diff-stat justification: the implementation repairs broken Codex hook timeout behavior and adds regression coverage; it does not add a new user-facing capability.

## Acceptance Criteria Status

- [x] `.codex/hooks.json` SessionStart `session_start_dispatch.py` registered timeout is strictly greater than inner `STARTUP_SERVICE_TIMEOUT_SECONDS`: observed `180 > 150.0`.
- [x] `.codex/hooks.json` UserPromptSubmit `session_wrapup_trigger_dispatch.py` registered timeout is at least `60`: observed `60 >= 60`.
- [x] Regression tests assert both invariants in `platform_tests/scripts/test_codex_hook_parity.py`.
- [x] Targeted parity suite passes: `13 passed`.
- [x] Python lint and format gates pass for the changed Python test file.
- [x] `.codex/hooks.json` validates as JSON.

## Risk And Rollback

Residual risk is limited to longer hook-runner wait windows. SessionStart remains bounded by the existing inner 150s startup-service timeout, and the 180s outer budget gives the fail-soft path room to complete. UserPromptSubmit's 60s budget is only relevant for the explicit wrap-up trigger path; ordinary prompts continue to short-circuit quickly.

Rollback is to restore `.codex/hooks.json` timeouts to `60` and `15` and remove the added parity-test invariant checks. No migration or external state change is required.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and command evidence.
2. Confirm the JSON-path ruff command behavior is an invalid proposed gate for this ruff version, not an implementation failure.
3. Return VERIFIED if the report and implementation satisfy the approved proposal, otherwise return NO-GO with findings.
