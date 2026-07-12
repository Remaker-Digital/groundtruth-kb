NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5474-93a6-7f70-8e54-d6d8b0a31bb4
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex desktop interactive Prime Builder; build activity; full GT-KB governance

# WI-5204 Successor Implementation Report - Stop-Hook Outcome Preservation With Genuine H Proof

bridge_kind: implementation_report
Document: gtkb-wi5204-h-stop-hook-completion-preservation-successor
Version: 001 (NEW; successor post-implementation report)
Responds to terminal predecessor: bridge/gtkb-wi5204-h-stop-hook-completion-preservation-005.md
Approved proposal: bridge/gtkb-wi5204-h-stop-hook-completion-preservation-001.md
Operative GO: bridge/gtkb-wi5204-h-stop-hook-completion-preservation-002.md
Prior implementation report: bridge/gtkb-wi5204-h-stop-hook-completion-preservation-003.md
Prior independent verdict: bridge/gtkb-wi5204-h-stop-hook-completion-preservation-004.md
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5204-H-STOP-HOOK-20260711
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5204
target_paths: [".claude/settings.json", "scripts/cloud_harness_base.py", "scripts/check_codex_hook_parity.py", "platform_tests/scripts/test_cloud_harness_base.py", "platform_tests/scripts/test_alibaba_cloud_studio_harness.py", "platform_tests/scripts/test_codex_hook_parity.py"]

## Successor Rationale

The predecessor thread was terminally withdrawn only to break the prerequisite
deadlock recorded in version 005: the implementation was independently
verified sound, but Alibaba H could not publish the linked genuine verdict
until WI-5210 supplied a governed provider publication tool. WI-5210 is now
VERIFIED and committed as `ebab011e`, and genuine H dispatch
`2026-07-12T15-55-02Z-loyal-opposition-H-0584dc` published the role-correct
governed verdict
`bridge/gtkb-wi5199-fd-evidence-h-functional-proof-004.md`.

This successor report carries forward the unchanged six-path WI-5204
implementation, the original proposal/GO, the independent code verification
in predecessor version 004, fresh isolated tests, and the now-complete H proof.
No source or test edit was made after predecessor version 004.

## Implementation Claim

The approved Stop-only lifecycle correction is complete and unchanged.

- Native `Stop` timeout, non-2 nonzero exit, malformed informational output,
  and unexpected lifecycle exceptions are fail-soft and cannot replace a
  pending final response or original provider/tool-loop exception.
- Exit 2 and valid JSON block decisions return a reason to the model and
  continue the loop. Eight consecutive explicit blocks fail closed.
- `PreToolUse` and the separate guard adapter remain fail closed for timeout,
  nonzero, malformed, empty, and explicit-denial paths.
- The Claude proactive wrap-up Stop registration has a 60-second allowance,
  and parity checks require exactly that allowance without inventing a
  Codex-native Stop registration.
- H, D, and F retain 600 turns, 900-second operations, 28,800-second sessions,
  and 29,400-second worker lifetimes. No generous allowance was reduced.

The reviewed patch is `.gtkb-state/wi5204/selected.patch`, generated against
committed HEAD `ebab011e`. It contains exactly the six approved paths, 396
insertions and 18 deletions, applies cleanly in a detached in-root worktree,
and contains no foreign hunk.

## Genuine H Evidence

- Dispatch: `2026-07-12T15-55-02Z-loyal-opposition-H-0584dc`.
- Harness/model/role: Alibaba Cloud Studio H / DeepSeek V4 Pro /
  Loyal Opposition, with `dispatcher_composition` provenance in
  `harness-state/alibaba-cloud-studio/session-envelopes/2026-07-12T15-55-02Z-loyal-opposition-H-0584dc.json`.
- Runtime: 75 of 600 turns, 69 governed tool calls, 2,661 seconds, exit code 0,
  zero stderr, `stop_reason=verdict_emitted`.
- Outcome: H published
  `bridge/gtkb-wi5199-fd-evidence-h-functional-proof-004.md` through
  `PublishBridgeVerdict`; dispatcher telemetry reconciled the verdict and
  released the document lease.
- The verdict's substantive truncation conclusion was caused by the separate
  provider Read disclosure defect tracked as WI-5214 / TEST-11368. That
  follow-on does not weaken this proof that the Stop lifecycle preserved the
  run outcome and that H completed genuine governed work through a role-correct
  publication path.

This satisfies the sole predecessor version 004 blocker under
`GOV-HARNESS-ONBOARDING-CONTRACT-001`.

## Specification Links

- `ADR-CLOUD-HARNESS-TEMPLATE-001`
- `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `DCL-OLLAMA-TOOL-PARITY-GATE-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Owner Decisions / Input

- `DELIB-202666173` requires genuine governed A/B/C/D/F/H proof and correction
  of every discovered defect.
- `DELIB-20260703-DISPATCH-TIMER-GENEROUS-ALLOWANCES` controls the generous
  timing policy preserved by this implementation.
- `DELIB-20260711-WI5200-5202-HARNESS-REPAIR-AUTHORIZATION` established the
  600-turn H envelope that exposed this Stop boundary.
- The bounded implementation authorization remains
  `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5204-H-STOP-HOOK-20260711`.
- No new owner decision is required. The predecessor NO-GO selected option 2,
  and Prime has now obtained the required genuine H verdict without a waiver.

## Prior Deliberations

- `bridge/gtkb-wi5204-h-stop-hook-completion-preservation-001.md` through
  `-005.md` preserve the original proposal, GO, report, narrow NO-GO, and
  prerequisite-deadlock withdrawal.
- `bridge/gtkb-wi5210-provider-lo-governed-verdict-publication-006.md` and
  commit `ebab011e` prove the governed H publication prerequisite is VERIFIED.
- `bridge/gtkb-wi5199-fd-evidence-h-functional-proof-004.md` is the genuine H
  verdict required by predecessor version 004.
- `DELIB-202666173`, `DELIB-20260703-DISPATCH-TIMER-GENEROUS-ALLOWANCES`, and
  `DELIB-20260711-WI5200-5202-HARNESS-REPAIR-AUTHORIZATION` remain applicable.

## Specification-Derived Verification

| Governing surface | Executed evidence | Result |
| --- | --- | --- |
| `ADR-CLOUD-HARNESS-TEMPLATE-001` | Stop candidate/original-exception preservation, timeout/non-2/malformed handling, explicit block continuation, eight-block ceiling | 17 focused parametrized cases passed in the isolated patched worktree. |
| `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001` | Alibaba native-full candidate-preservation regression and genuine H dispatcher run | Unit regression passed; genuine H verdict published with exit 0. |
| `DCL-OLLAMA-TOOL-PARITY-GATE-001` | Native `PreToolUse` plus guard-adapter runtime failures remain fail closed | Focused parametrized cases passed. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`; `ADR-CROSS-HARNESS-PARITY-001` | Claude 60-second Stop allowance assertion; Codex non-native disposition retained | New parity assertion passed. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Genuine dispatcher-produced H role-correct verdict publication | Run `0584dc` passed and reconciled. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Isolated focused pytest, broader proposal suite, pure-HEAD baseline, Ruff, and diff checks | Focused 17 passed; broader 97 passed / 5 baseline failures; pure HEAD reproduced the same five with 8 passed; quality gates clean. |

## Commands Run And Observed Results

1. Eight changed test nodes in the detached patched worktree: `17 passed, 1
   warning`.
2. Full three-file proposal suite in the detached patched worktree: `97
   passed, 5 failed, 1 warning`.
3. Untouched committed HEAD `ebab011e`, `test_codex_hook_parity.py`: `8 passed,
   5 failed, 1 warning`; the same five test names fail before the WI-5204
   patch, proving foreign baseline drift.
4. Ruff check on the five Python paths: all checks passed.
5. Ruff format check: five files already formatted.
6. `git diff --check` on the exact six-path patch: clean.

The warning is the repository's pre-existing unknown pytest option
`asyncio_mode`. The five baseline failures concern untouched Codex
`.codex/config.toml`/`.codex/hooks.json` registrations outside WI-5204's
approved scope and are not absorbed into this patch.

## Files Changed

- `.claude/settings.json`
- `scripts/cloud_harness_base.py`
- `scripts/check_codex_hook_parity.py`
- `platform_tests/scripts/test_cloud_harness_base.py`
- `platform_tests/scripts/test_alibaba_cloud_studio_harness.py`
- `platform_tests/scripts/test_codex_hook_parity.py`

The focused commit should also include predecessor bridge versions 001 through
005, this successor report, and the independently authored VERIFIED successor.
No other dirty path is claimed.

## Acceptance Criteria Status

- [x] Stop timeout, non-2 nonzero, malformed informational output, and cleanup
  exceptions preserve a candidate result and original exception.
- [x] Exit-2 and valid JSON blocks continue with their reason and are bounded
  at eight consecutive blocks.
- [x] `PreToolUse` and guard-adapter failures remain fail closed.
- [x] Claude wrap-up Stop timeout is 60 seconds and parity-enforced.
- [x] Focused isolated tests and quality gates pass; five broad failures are
  reproduced on untouched HEAD.
- [x] Genuine dispatcher-produced H verdict and role envelope exist.
- [x] H's 600/900/28,800/29,400 allowances remain intact.
- [ ] Independent Loyal Opposition VERIFIED and focused finalization.

## Risk And Rollback

The principal risk remains accidentally broadening fail-soft behavior to
mutation guards. Event discrimination is explicit and the mandatory guard
regressions pass. The six modified paths contain only WI-5204 changes relative
to HEAD, so ordinary path-scoped atomic finalization cannot capture foreign
hunks. Rollback is the single focused WI-5204 commit; reverting Stop
preservation would restore outcome masking and require H to become ineligible
again. All bridge and dispatch evidence remains append-only.

## Loyal Opposition Ask

Carry forward the independent code affirmation from predecessor version 004,
re-run or inspect the fresh isolated evidence, confirm H run `0584dc` satisfies
the sole onboarding blocker, and return VERIFIED with one focused commit
containing only the six source/test/config paths plus both WI-5204 bridge
chains. Return NO-GO only for a new concrete blocker.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
