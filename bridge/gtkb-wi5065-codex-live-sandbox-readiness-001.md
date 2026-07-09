NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3ddf-359c-7fa3-8885-2d1f9179d884
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive Prime Builder session; approval_policy=never; sandbox=danger-full-access

# Defect-Fix Proposal - Codex/A headless live shell smoke fails Windows sandbox setup 0xc0000142 despite static dispatch readiness

bridge_kind: prime_proposal
Document: gtkb-wi5065-codex-live-sandbox-readiness
Version: 001
Date: 2026-07-07 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5065

target_paths: ["scripts/dispatcher_runtime.py", "scripts/verify_codex_dispatch.py", "scripts/windows_subprocess.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_verify_codex_dispatch.py", "platform_tests/scripts/test_windows_subprocess.py"]

## Claim

Codex/A is configured as the Prime Builder dispatch target and passes static dispatch readiness, but it is not yet able to perform PB work headlessly because the live no-window shell smoke fails on Windows with Codex sandbox setup status `0xc0000142` and detects visible terminal windows. The dispatcher is therefore correct to suppress Codex/A with `codex_dispatch_not_ready`.

Prime Builder requests GO for a narrow readiness hardening and repair slice: make the live no-window shell smoke a first-class readiness input for Codex dispatch, preserve the existing fail-closed guard until that smoke passes, and repair any repo-controlled no-window or subprocess wrapper defect that is causing the observed Windows sandbox launch failure. If the root cause is outside this repository, the implementation must report that as an external blocker instead of weakening sandbox/no-window requirements.

## Defect / Reproduction

- `groundtruth-kb/.venv/Scripts/python.exe scripts/verify_codex_dispatch.py --json` reports Codex/A as statically dispatchable with `can_receive_dispatch=true`, model `gpt-5.5`, approval policy `never`, `workspace-write` sandbox, and the expected `.codex` additional directory.
- `.gtkb-state/bridge-poller/codex-no-window-verification.json` reports `result=fail`, `probe=dispatcher_codex_no_window_live_shell_smoke_disable_plugins`, and an expiry of `2026-07-07T23:57:01.879368Z`.
- The live smoke command shape is `codex exec --disable plugins --model gpt-5.5 --sandbox workspace-write --cd PROJECT_ROOT --add-dir .codex <prompt>`.
- The failed smoke stderr includes `windows sandbox: setup refresh failed with status exit code: 0xc0000142`.
- The smoke also detected visible terminal windows: Windows Terminal, Terminal, and Git cmd.
- A controlled dispatcher tick after OpenRouter/F was switched to LO-default suppressed Codex/A with reason `codex_dispatch_not_ready`, which prevents unsafe PB dispatch while this live evidence remains failing.

This recurrence lands after previous no-window and Codex-dispatch bridge work (`gtkb-wi5052-dispatcher-codex-no-window-containment`, `gtkb-wi5062-no-window-service-probes`, and `gtkb-wi5048-openrouter-prime-builder-dispatch-activation`) reached VERIFIED state, so the residual defect needs a new bridge-governed repair target rather than reopening those completed implementation reports in place.

## In-Root Placement Evidence

All proposed target paths are inside `E:\GT-KB`: `scripts/dispatcher_runtime.py`, `scripts/verify_codex_dispatch.py`, `scripts/windows_subprocess.py`, `platform_tests/scripts/test_dispatcher_runtime.py`, `platform_tests/scripts/test_verify_codex_dispatch.py`, and `platform_tests/scripts/test_windows_subprocess.py`.

## Requirement Sufficiency

Existing requirements are sufficient for this repair. The active owner goal requires Codex and OpenRouter to work headlessly, while `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `SPEC-DISPATCHER-CONTROL-SURFACE-001`, the no-window dispatcher requirements, and the reliability fast-lane standing authorization already govern the dispatcher/readiness behavior. No new functional requirement is needed before implementation can begin after LO GO.

## Prefiling Preflight Evidence

- Applicability preflight command: `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5065-codex-live-sandbox-readiness --content-file .gtkb-state/bridge-propose-drafts/gtkb-wi5065-codex-live-sandbox-readiness-001.md --json`
- Applicability result: `preflight_passed=true`, `missing_required_specs=[]`, `missing_advisory_specs=[]`.
- ADR/DCL diagnostic preflight: zero evidence gaps in must-apply clauses.
- Bridge proposal pattern lint: zero findings.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires source/test/config changes for this repair to be bridge-governed and approved before protected mutation.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - requires active project authorization for implementation under `PROJECT-GTKB-RELIABILITY-FIXES`.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - confirms the standing project authorization does not replace LO GO or the implementation-start packet.
- `GOV-RELIABILITY-FAST-LANE-001` - authorizes small, single-concern reliability defects under `PROJECT-GTKB-RELIABILITY-FIXES` by active membership.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires the live-smoke failure to be preserved as durable work-item and bridge evidence rather than chat-only memory.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - supports creating WI-5065 and a follow-on proposal when fresh evidence shows verified prior work did not fully satisfy the active headless-dispatch goal.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - keeps the defect, proposal, verification, and eventual report linked through governed artifacts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires this proposal to cite the governing specification surfaces.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires the implementation report to map focused tests and live-smoke evidence to the linked specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires the PAUTH/project/work-item metadata above.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - governs dispatch selection and the requirement that eligible harnesses process work headlessly.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - governs dispatcher status, health, suppression, and failure classification evidence.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - requires dispatcher background work to remain headless/no-window safe on Windows.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - relevant because Codex must self-enforce bridge and dispatch safety boundaries when native hook coverage is incomplete.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - confirms the target paths are GT-KB platform files, not external application files.
- `GOV-STANDING-BACKLOG-001` - covers WI-5065 as the active backlog record for the recurrence.

## Prior Deliberations

- `bridge/gtkb-wi5052-dispatcher-codex-no-window-containment-004.md` - prior VERIFIED Codex no-window containment bridge thread.
- `bridge/gtkb-wi5062-no-window-service-probes-008.md` - prior VERIFIED no-window service/probe bridge thread.
- `bridge/gtkb-wi5048-openrouter-prime-builder-dispatch-activation-008.md` - prior VERIFIED dispatch-activation thread that left Codex dispatch dependent on readiness gates.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - owner-approved standing reliability fast-lane authorization.

## Owner Decisions / Input

- Owner updated the active goal on 2026-07-07: OpenRouter must be LO-default, and Codex plus OpenRouter must be able to work headlessly.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active and authorizes small reliability fixes under `PROJECT-GTKB-RELIABILITY-FIXES` by active work-item membership.
- No credential rotation, provider-account change, production deployment, force-push, sandbox weakening, or clearing of the Codex no-window disable guard is requested or authorized by this proposal.

## Proposed Scope

IP-1: In `scripts/verify_codex_dispatch.py` and dispatcher readiness reporting, make the live no-window shell-smoke result explicit enough that static readiness cannot be mistaken for deliverable Codex headless readiness. The report should distinguish static registry/ACL readiness from live no-window execution readiness.

IP-2: In `scripts/dispatcher_runtime.py`, preserve fail-closed Codex/A suppression while the live smoke is failed, expired, missing, or detects visible windows. Add or strengthen classification for the observed `0xc0000142` Windows sandbox setup failure so health/status output points at the Codex live-smoke blocker rather than a generic dispatch failure.

IP-3: In `scripts/windows_subprocess.py` or the relevant wrapper path, repair any repo-controlled no-window/process-launch defect contributing to the live-smoke failure, while preserving the approved `workspace-write` sandbox requirement and no-window behavior. If the root cause is the external Codex CLI or local Windows environment, leave Codex/A quarantined and report that external blocker in the implementation report instead of introducing an unsafe fallback.

IP-4: Add focused tests in `platform_tests/scripts/test_dispatcher_runtime.py`, `platform_tests/scripts/test_verify_codex_dispatch.py`, and `platform_tests/scripts/test_windows_subprocess.py` for live-smoke readiness handling, stale/missing/failed evidence, visible-window failure evidence, `0xc0000142` classification, and no-window wrapper behavior.

Out of scope: switching Codex dispatch to `danger-full-access`, disabling the `workspace-write` sandbox, bypassing the no-window smoke, clearing `.gtkb-state/watchdog/dispatcher-disable-guard.json` before the live smoke passes, credential lifecycle, OpenRouter provider changes, Antigravity/Ollama spend, or broad dispatcher policy rewrites.

## Specification-Derived Verification Plan

| Spec / surface | Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Unit-test that Codex/A remains suppressed when live no-window smoke evidence is failed, stale, missing, or reports visible windows; after implementation, run a controlled live smoke before any dispatch enablement. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Unit-test dispatcher health/status classification for `codex_dispatch_not_ready`, visible-window evidence, and `0xc0000142` Windows sandbox setup failure text. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | Unit-test or inspect `windows_subprocess` wrapper behavior to confirm Windows child processes still use no-window-safe flags and hidden startup info. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run the focused pytest and ruff commands below and cite exact results in the post-implementation report. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Before source edits, run `scripts/implementation_authorization.py begin --bridge-id gtkb-wi5065-codex-live-sandbox-readiness` after LO GO and cite the packet. |

Expected focused commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_verify_codex_dispatch.py platform_tests/scripts/test_windows_subprocess.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/dispatcher_runtime.py scripts/verify_codex_dispatch.py scripts/windows_subprocess.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_verify_codex_dispatch.py platform_tests/scripts/test_windows_subprocess.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/dispatcher_runtime.py scripts/verify_codex_dispatch.py scripts/windows_subprocess.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_verify_codex_dispatch.py platform_tests/scripts/test_windows_subprocess.py
```

Live-readiness verification before clearing any guard:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/verify_codex_dispatch.py --json
```

If the implementation changes the live-smoke launcher, also run the governed no-window live-smoke command that writes `.gtkb-state/bridge-poller/codex-no-window-verification.json`, then confirm `result=pass`, no visible windows were detected, and the evidence has a fresh expiry.

## Acceptance Criteria

- Static readiness and live headless readiness are reported separately for Codex/A.
- Failed, stale, missing, or visible-window live-smoke evidence keeps Codex/A suppressed with a clear reason.
- The observed `0xc0000142` Windows sandbox setup failure is classified and surfaced as a Codex live-readiness blocker.
- Any repo-controlled no-window wrapper defect identified during implementation is fixed without weakening sandbox or no-window requirements.
- The Codex dispatcher disable guard remains uncleared unless a fresh live no-window shell smoke passes.
- The post-implementation report includes focused test results and either passing live-smoke evidence or a truthful external-blocker report.

## Risks / Rollback

Risk: treating a local Codex CLI/Windows failure as repo-fixable could waste cycles. Mitigation: require the implementation report to distinguish repo-controlled defects from external CLI/OS blockers and leave Codex quarantined if the latter remains true.

Risk: loosening readiness could launch visible windows or unsafe PB dispatch. Mitigation: fail closed on failed/stale/missing live-smoke evidence and explicitly keep sandbox weakening out of scope.

Rollback: revert only the changed source/test lines and restore the prior readiness classification. Do not remove the disable guard or relaunch Codex dispatcher work as part of rollback.

## Files Expected To Change

- `scripts/dispatcher_runtime.py`
- `scripts/verify_codex_dispatch.py`
- `scripts/windows_subprocess.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_verify_codex_dispatch.py`
- `platform_tests/scripts/test_windows_subprocess.py`

## Recommended Commit Type

`fix:`
