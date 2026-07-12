NEW

# WI-5204 - Preserve H outcomes across native Stop-hook failures - Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi5204-h-stop-hook-completion-preservation
Version: 003 (NEW; post-implementation report)
Author: Prime Builder (Codex, harness A)
Date: 2026-07-12 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f522a-849d-7d43-8c60-0afc829438a6
author_model: gpt-5.5
author_model_version: Codex desktop
author_model_configuration: xhigh reasoning; interactive Prime Builder; bounded worker implementation independently reviewed by parent

Responds to GO: bridge/gtkb-wi5204-h-stop-hook-completion-preservation-002.md
Approved proposal: bridge/gtkb-wi5204-h-stop-hook-completion-preservation-001.md
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5204-H-STOP-HOOK-20260711
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5204
Recommended commit type: fix(harness):

target_paths: [".claude/settings.json", "scripts/cloud_harness_base.py", "scripts/check_codex_hook_parity.py", "platform_tests/scripts/test_cloud_harness_base.py", "platform_tests/scripts/test_alibaba_cloud_studio_harness.py", "platform_tests/scripts/test_codex_hook_parity.py"]

requires_verification: true
kb_mutation_in_scope: false

---

## Implementation Claim

The approved Stop-only lifecycle correction is complete in the six authorized paths.

- Native `Stop` timeout, non-2 nonzero exit, malformed informational output, and unexpected lifecycle exceptions are fail-soft: they no longer replace a pending final response or an original provider/tool-loop exception.
- Exit 2 and valid JSON block decisions return a reason to the model and continue the loop. Eight consecutive explicit blocks fail closed.
- `PreToolUse` and the separate guard adapter remain fail closed for timeout, nonzero, malformed, empty, and explicit-denial paths.
- The Claude proactive wrap-up Stop registration now has a 60-second allowance, and parity checks require exactly that allowance without inventing a Codex-native Stop registration.

H remains dispatcher-ineligible while this report awaits independent code verification. The final onboarding proof is the already-governed WI-5199 H verdict thread; after the reviewer confirms the code gates, H can be temporarily re-enabled through the canonical dispatch control surface, targeted to that thread, and disabled again if the genuine verdict does not complete.

## Implementation Gate Evidence

- Work-intent claim row: `31213`, holder session `019f522a-849d-7d43-8c60-0afc829438a6`.
- Implementation-start packet: `sha256:9e53cd525e843eb246bd056672ea0a759fba493f73290f173b51f3f4c9f70160`.
- Operative GO: `bridge/gtkb-wi5204-h-stop-hook-completion-preservation-002.md`.
- Exact PAUTH: `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5204-H-STOP-HOOK-20260711`.

## Specification Links

- `ADR-CLOUD-HARNESS-TEMPLATE-001`
- `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `DCL-OLLAMA-TOOL-PARITY-GATE-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`

## Owner Decisions / Input

- `DELIB-202666173` requires genuine governed A/B/C/D/F/H proof and correction of every discovered defect.
- `DELIB-20260703-DISPATCH-TIMER-GENEROUS-ALLOWANCES` controls the generous timing policy. No model, operation, session, or worker allowance was reduced.
- No new owner decision is required.

## Prior Deliberations

- `bridge/gtkb-wi5204-h-stop-hook-completion-preservation-001.md`
- `bridge/gtkb-wi5204-h-stop-hook-completion-preservation-002.md`
- `bridge/gtkb-wi5199-fd-evidence-h-functional-proof-003.md`
- `DELIB-202666173`
- `DELIB-20260703-DISPATCH-TIMER-GENEROUS-ALLOWANCES`

## Specification-Derived Verification

| Governing surface | Executed evidence | Result |
| --- | --- | --- |
| `ADR-CLOUD-HARNESS-TEMPLATE-001` | Candidate-result and original-exception tests for Stop timeout, non-2 exit, and malformed output; exit-2/JSON-block continuation; eight-block ceiling | Pass in the 73-test acceptance subset. |
| `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001` | Alibaba native-full candidate-preservation regression plus live settings/parity assertion | Pass; H still uses native-full hooks and the wrap-up allowance is 60 seconds. |
| `DCL-OLLAMA-TOOL-PARITY-GATE-001` | Native `PreToolUse` timeout/nonzero/malformed tests and guard-adapter timeout/nonzero/malformed/empty tests | Pass; mutation controls remain fail closed. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`, `ADR-CROSS-HARNESS-PARITY-001` | Parity source requires Claude's 60-second Stop allowance; Codex retains its non-native disposition | New assertion passes. Five unrelated Codex repository-config tests remain baseline failures at untouched HEAD. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Genuine dispatcher-produced H verdict on WI-5199 | Pending independent code gate and canonical H re-enable; must complete before final acceptance of the owner goal. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest plus separate Ruff check and format gates, with detached pure-HEAD baseline | 73 passed; quality gates clean; foreign five-failure baseline proven. |

## Commands Run And Observed Results

1. Focused WI acceptance subset: `73 passed, 1 warning in 1.07s`.
2. Full proposal suite: `81 passed, 5 failed, 1 warning in 1.60s`. The five failures are all pre-existing Codex hook/config assertions.
3. Detached untouched HEAD `45d1c7f2`, `platform_tests/scripts/test_codex_hook_parity.py`: `8 passed, 5 failed`. The exact same five test names and missing Codex registrations fail without the WI-5204 patch.
4. Ruff check on the five changed Python files: `All checks passed!`.
5. Ruff format check: `5 files already formatted`.
6. `git diff --check` on all six target paths: clean.
7. The detached in-root baseline worktree was removed and confirmed absent after verification.

The warning is the repository's pre-existing unknown pytest option `asyncio_mode` and is unrelated to this slice.

## Files Changed

- `.claude/settings.json`
- `scripts/cloud_harness_base.py`
- `scripts/check_codex_hook_parity.py`
- `platform_tests/scripts/test_cloud_harness_base.py`
- `platform_tests/scripts/test_alibaba_cloud_studio_harness.py`
- `platform_tests/scripts/test_codex_hook_parity.py`

No other dirty worktree path is claimed by this implementation.

## Acceptance Criteria Status

- [x] Stop timeout, non-2 nonzero, and malformed informational output preserve a candidate result.
- [x] The same lifecycle failures preserve an original exception.
- [x] Exit-2 and valid JSON blocks continue with their reason.
- [x] Eight consecutive explicit Stop blocks fail closed.
- [x] `PreToolUse` and guard-adapter failures remain fail closed.
- [x] Claude wrap-up Stop timeout is 60 seconds and parity-enforced.
- [x] Focused tests, Ruff check, Ruff format check, and diff check pass.
- [x] Five broad-suite failures are reproduced on untouched HEAD and disclosed, not absorbed.
- [ ] Independent Loyal Opposition code verification.
- [ ] Genuine dispatcher-produced H verdict on the WI-5199 thread after canonical re-enable.
- [ ] Loyal Opposition VERIFIED and focused finalization.

## Risk And Rollback

The principal risk is accidentally broadening fail-soft behavior to mutation guards. Event discrimination is explicit and the mandatory guard regressions remain green. Rolling back only the 60-second registration is mechanically possible but would restore contention risk; rolling back event-specific Stop handling would restore outcome masking and therefore requires H to remain ineligible. Bridge and telemetry evidence remain append-only.

## Loyal Opposition Asks

1. Independently run the mapped Stop/PreToolUse/guard tests and quality gates, including the detached baseline if needed.
2. After the code gate is independently sound, use the canonical dispatcher control surface to re-enable H and targeted-reoffer WI-5199 for one genuine role-correct verdict; do not reduce the approved 600-turn, 900-second operation, 28,800-second session, or 29,400-second worker allowances.
3. Return VERIFIED only if both the code gates and genuine H proof satisfy the linked specifications; otherwise return NO-GO with concrete findings and leave H disabled.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
