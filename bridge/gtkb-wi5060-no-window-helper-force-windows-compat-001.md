NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f39ff-4e44-7a32-b5d0-6969ec4d55ec
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex interactive Prime Builder

bridge_kind: prime_proposal
Document: gtkb-wi5060-no-window-helper-force-windows-compat
Version: 001
Author: Prime Builder (Codex)
Date: 2026-07-07 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5060-HARNESS-REPAIR-20260707
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5060

target_paths: ["scripts/windows_subprocess.py", "scripts/verify_ollama_dispatch.py", "platform_tests/scripts/test_windows_subprocess.py"]

implementation_scope: source | tests | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

# WI-5060 Follow-On: no-window helper compatibility for dispatch probes

## Summary

This proposal requests a narrow follow-on GO to reconcile the remaining WI-5060 no-window helper compatibility delta discovered after the verified shim/headless work. The existing WI-5060 bridge chains repaired OpenRouter/F default-model omission, shim max-turn behavior, D/F dispatch readiness, and dispatcher-owned hidden process launch behavior. The current uncommitted delta is smaller: it centralizes `verify_ollama_dispatch.py` service-probe subprocess creation through `scripts/windows_subprocess.py` so the verifier uses the same no-window helper contract and can be tested deterministically.

This is intentionally a fresh bridge thread because the latest WI-5060 chains are already VERIFIED, and `scripts/verify_ollama_dispatch.py` was not in the `gtkb-wi5060-headless-dispatch-window-hardening` target path set. No source commit, implementation report, or closure should rely on that older VERIFIED chain for this additional caller/helper compatibility change.

## Current Evidence

- `gt bridge threads --wi WI-5060 --json --compact` reports two recognized WI-5060 threads, both latest `VERIFIED`: `gtkb-wi5060-harness-readiness-repair` and `gtkb-wi5060-headless-dispatch-window-hardening`.
- `gt backlog show WI-5060 --json` reports `resolution_status=resolved` and `stage=resolved`, with completion evidence from the bridge VERIFIED backlog reconciler.
- `gt projects authorizations PROJECT-GTKB-RELIABILITY-FIXES --json` includes active PAUTH `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5060-HARNESS-REPAIR-20260707`, allowing WI-5060 source, test_addition, configuration, and governance_evidence while forbidding credential lifecycle, deploys, destructive cleanup, broad bulk status mutation, untracked file deletion, and D/F reenablement without smoke evidence.
- `git diff --name-only -- scripts/windows_subprocess.py scripts/verify_ollama_dispatch.py platform_tests/scripts/test_windows_subprocess.py` shows exactly these three modified paths.
- `git diff -- scripts/windows_subprocess.py scripts/verify_ollama_dispatch.py platform_tests/scripts/test_windows_subprocess.py` shows `verify_ollama_dispatch.py` replacing locally assembled `creationflags` with `no_window_subprocess_kwargs(force_windows=command_runner is not None)`, `windows_subprocess.py` adding `force_windows` support and hidden startupinfo to `no_window_subprocess_kwargs`, and `test_windows_subprocess.py` asserting the no-window helper returns hidden startupinfo on Windows.
- Focused verification already run in the current workspace: `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_verify_ollama_dispatch.py platform_tests/scripts/test_windows_subprocess.py -q --tb=short --basetemp .test-tmp/pytest-verify-ollama-force-windows` passed with 25 passed, 1 skipped, 1 warning.
- Focused style checks already run in the current workspace: `ruff check scripts/windows_subprocess.py platform_tests/scripts/test_windows_subprocess.py` passed; `ruff format --check scripts/windows_subprocess.py platform_tests/scripts/test_windows_subprocess.py` reported both files already formatted.
- `gt bridge dispatch health --json` reports `health_status: PASS`; complex lifecycle components daemon, supervisor, and watchdog are healthy and hidden, with supervisor/watchdog using `pythonw.exe`.
- `gt bridge dispatch status --json` reports selected dispatch recipients `loyal-opposition:D`, `loyal-opposition:C`, and `prime-builder:F`; Codex/A remains active but not selected because its dispatch receive flag is currently false.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected source/test changes require a live bridge GO with matching target paths.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation must stay inside active project authorization.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not bypass bridge GO or implementation-start gates.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal must link work item, project, PAUTH, target paths, specs, and verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - implementation proposals require Project Authorization, Project, Work Item, and target_paths metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must map behavior claims to concrete tests/evidence before VERIFIED.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher-facing probes and workers should use governed centralized runtime surfaces rather than ad hoc launch behavior.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher status/health/report commands are the authoritative topology and readiness evidence surface.
- `GOV-ENV-LOCAL-AUTHORITY-001` - no credential lifecycle, disclosure, provider credential mutation, or key rotation is in scope.

## Requirement Sufficiency

Existing requirements are sufficient. WI-5060, the active WI-5060 PAUTH, the verified WI-5060 bridge history, and the dispatcher control/service specs cover a narrow helper/caller/test reconciliation for headless service-probe subprocess behavior. No new requirement, PAUTH, or owner decision is required before Loyal Opposition reviews this proposal.

## Prior Deliberations

- `DELIB-20260707-HARNESS-A-C-D-F-REPAIR-GOAL` - owner-directed goal to test and fix harnesses A, C, D, and F for their currently assigned roles.
- `bridge/gtkb-wi5060-shim-max-turn-exhaustion-authorization-002.md` - GO authorizing the targeted WI-5060 PAUTH path before implementation.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5060-HARNESS-REPAIR-20260707` - active bounded WI-5060 source/test/config/governance authorization.
- `bridge/gtkb-wi5060-harness-readiness-repair-004.md` - VERIFIED original shim/readiness repair.
- `bridge/gtkb-wi5060-headless-dispatch-window-hardening-004.md` - VERIFIED headless dispatch window hardening.
- `bridge/gtkb-wi5062-no-window-service-probes-004.md` - VERIFIED stale service/SoT retry-state closure related to no-window service probes.

## Owner Decisions / Input

No additional owner decision is needed for this bridge filing. Mike already authorized the A/C/D/F harness repair goal and the headless fix in this session. This proposal is the governance follow-through for a small target-path delta that should not be folded into already-VERIFIED WI-5060 chains.

## Proposed Scope

1. Keep `scripts/verify_ollama_dispatch.py` service probes on the centralized no-window subprocess helper instead of assembling raw Windows creation flags locally.
2. Add `force_windows` support to `scripts/windows_subprocess.py` so non-Windows/monkeypatched tests can deterministically exercise Windows no-window kwargs without lying about the actual runtime OS path.
3. Ensure `no_window_subprocess_kwargs()` includes hidden `STARTUPINFO` on Windows in addition to `CREATE_NO_WINDOW`, matching the stronger hidden-launch behavior used elsewhere.
4. Add focused regression coverage in `platform_tests/scripts/test_windows_subprocess.py` for the hidden startupinfo returned by the simple no-window helper.

## Out Of Scope

- No changes to OpenRouter credentials, provider configuration, model names, or cloud default routing.
- No changes to Ollama model routing or service lifecycle.
- No changes to dispatcher eligibility, ranking, role assignment, cost budgets, max-turn budgets, or harness registry state.
- No changes to `groundtruth.db`, backlog status, bridge terminal statuses, or broad worktree cleanup.
- No deployment, push, force-push, credential lifecycle, or untracked file deletion.

## Spec-Derived Verification Plan

| Spec / requirement | Verification command or evidence | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | `gt bridge show gtkb-wi5060-no-window-helper-force-windows-compat --json --compact`; `python scripts/bridge_claim_cli.py claim gtkb-wi5060-no-window-helper-force-windows-compat --session-id 019f39ff-4e44-7a32-b5d0-6969ec4d55ec` after GO | Latest status is `GO` before implementation report/commit; implementation claim is current-session scoped. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Inspect proposal header and active PAUTH record | Proposal cites `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5060-HARNESS-REPAIR-20260707`; target paths fit source/test governance scope. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_verify_ollama_dispatch.py platform_tests/scripts/test_windows_subprocess.py -q --tb=short --basetemp .test-tmp/pytest-verify-ollama-force-windows` | `verify_ollama_dispatch.py` uses the centralized no-window helper and helper behavior is regression-covered. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | `gt bridge dispatch health --json`; `gt bridge dispatch status --json` | Dispatcher health remains `PASS`; no dispatcher registry/eligibility change is included. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report maps each claim above to focused pytest, ruff, and dispatcher health/status evidence | Loyal Opposition can verify the change without relying on stale terminal WI-5060 descriptions. |
| `GOV-ENV-LOCAL-AUTHORITY-001` | Diff review | No credential values, provider secrets, env.local mutation, credential upload, or rotation instructions. |

## Acceptance Criteria

- `verify_ollama_dispatch.py` no longer constructs raw `creationflags` locally for the service-probe subprocess.
- `no_window_subprocess_kwargs(force_windows=True)` exposes deterministic no-window kwargs for test callers while preserving ordinary non-Windows runtime behavior.
- The helper returns hidden startupinfo on Windows so simple no-window subprocess paths receive the same hidden-window disposition as the dispatcher child-launch path.
- Focused pytest passes for `test_verify_ollama_dispatch.py` and `test_windows_subprocess.py`.
- Ruff check and format check pass for the changed scripts/tests.
- Dispatcher health remains `PASS`; no registry or dispatch eligibility mutation is part of this slice.

## Risk / Rollback

Risk is low and isolated to subprocess kwargs returned by a shared Windows helper and one verifier caller. Rollback is a source/test revert for the three listed target paths. Bridge files are append-only governance records and are not deleted by rollback.

## Bridge Filing Note

This proposal intentionally does not use `gt bridge file-implementation-proposal` because its dry-run selected the broad standing PAUTH for WI-5060. The governed bridge-propose writer is used instead so the filed proposal cites the narrower active WI-5060 PAUTH and avoids unrelated auto-linked specs.

## Recommended Commit Type

`fix(harness):`

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
