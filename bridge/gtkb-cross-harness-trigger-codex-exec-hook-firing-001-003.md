REVISED

# Cross-Harness Trigger Codex-Exec Hook Firing Investigation + Fix - REVISED-1

bridge_kind: prime_proposal
Document: gtkb-cross-harness-trigger-codex-exec-hook-firing-001
Version: 003 (REVISED-1 post NO-GO at `-002`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341

## Revision Notes (REVISED-1)

**F1 addressed:** Reframed the diagnostic delta away from interactive-vs-`codex exec` to the actual tested gap: isolated temp-project `codex exec` hook firing versus production GT-KB cross-harness dispatch-session behavior with the live `.codex/hooks.json`, `GTKB_BRIDGE_POLLER_RUN_ID`, cwd/root resolution, and bridge-state side effects. IP-1 diagnostic now exercises the production dispatch path.

**F2 addressed:** IP-1 revised to state explicitly that the diagnostic is a controlled live probe that mutates `.gtkb-state/`, records before/after snapshots, and documents exact side effects in the implementation report. Acceptance criterion reframed: probe succeeds when it determines whether hooks fire in production dispatch (mutation is evidence, not a defect).

**F3 addressed:** Replaced Path C (Prime-startup-only fallback). New Path C adds a post-child reconciliation mechanism tied to the dispatch parent, preserving fire-and-forget latency while keeping dispatch-state current. If child `codex exec` hooks are unavailable, the launcher records child PID/dispatch ID and runs deterministic reconciliation after child exits, meeting the "state stays current after Codex completes" acceptance target.

**F4 addressed:** Added `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v2 to Specification Links and mapped it to concrete tests. Expanded test mapping to include hook-parity regression coverage.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001`
- `DCL-SMART-POLLER-AUTO-TRIGGER-001`
- `DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001`
- `PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`
- `.claude/rules/bridge-essential.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/canonical-terminology.md`

## Prior Deliberations

- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` - empirical foundation: Codex hooks fire on Windows in `codex exec` invocations (confirmed by test invocation). Reframing: tested gap is isolated-project behavior vs production GT-KB dispatch-session behavior with live registration, env-var, and cwd state.
- `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` - `.codex/hooks.json` is live for Codex CLI >= 0.128.0-alpha.1; status depends on supporting production dispatch behavior.
- `bridge/gtkb-cross-harness-trigger-windows-rename-race-001` VERIFIED at -006 (2026-05-10) - closed write-reliability defect class.
- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-001` VERIFIED at -006 - established PostToolUse + Stop hook registrations; runtime firing in production `codex exec` dispatch sessions was not tested.
- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001` VERIFIED at -020 - retired pollers; assumed cross-harness trigger fires reliably.

## Owner Decisions / Input

- **Owner direction 2026-05-10:** "Proceed in order 3, 2 then 1. Please parallelize work whenever possible and continue with new work unsupervised if possible. Close as much of the backlog as you can." Authorizes filing this proposal as Step 3.
- **AUQ S341 (2026-05-11) autonomous-execution directive:** "Proceed with as little input from me as possible and execute on all of the outstanding bridge items and backlog in the order that makes best use of knowledge/context." Authorizes this REVISED-1 filing.

Outstanding owner decisions before VERIFIED: none. Investigation result determines fix path; each path is bridge-protocol-acceptable.

## Scope (Investigation + Branched Fix)

### IP-1: Empirical investigation (deterministic-services principle)

Author `scripts/diagnose_codex_exec_hooks.py` - a controlled live diagnostic that:

1. Reads `.codex/hooks.json` registration state.
2. Records `dispatch-state.json.updated_at` BEFORE invoking `codex exec` with production GT-KB root, live config, and env-var marker.
3. Invokes `codex exec` with the actual dispatch context (mirroring cross-harness trigger invocation).
4. Records `dispatch-state.json.updated_at` AFTER codex exec returns.
5. Records `dispatch-failures.jsonl` line count delta.
6. Emits findings: did the trigger fire (state.updated_at changed)? Did it fail (failure count increased)? Or did it not run (state unchanged + zero failures)?

Diagnostic mutates `.gtkb-state/` (this is the success condition, not a defect). Output is structured markdown with before/after snapshots and operational side effects documented. Run output goes to `.gtkb-state/codex-exec-hook-investigation/<timestamp>-results.md`.

### IP-2: Fix path determined by investigation findings

Three candidate fix paths:

- **Path A: hook-registration repair.** If `.codex/hooks.json` lacks needed registration, add it. Tests verify firing in production dispatch.
- **Path B: trigger-side fallback.** If hooks fire but trigger no-ops (env detection wrong), patch trigger. Tests verify state-update in production dispatch.
- **Path C: documented post-child reconciliation.** If `codex exec` truly does not run hooks, the launcher records child PID/dispatch ID and runs deterministic reconciliation after child exits. Preserves fire-and-forget latency while keeping state current. Fallback documented in `bridge-essential.md`.

### IP-3: Tests for the chosen fix path

Each path has focused tests; detailed in IP-2 of impl-report.

### IP-4: Update `bridge-essential.md`

Add subsection documenting empirical behavior + chosen mechanism + post-child reconciliation fallback (if Path C). Narrative-artifact edit; requires formal-artifact-approval packet.

## Files Expected To Change

- `scripts/diagnose_codex_exec_hooks.py` - NEW (IP-1).
- `scripts/cross_harness_bridge_trigger.py` - POSSIBLY MODIFIED (depends on chosen path).
- `.codex/hooks.json` - POSSIBLY MODIFIED (Path A only).
- `.claude/rules/bridge-essential.md` - MODIFIED (IP-4; with approval packet).
- `platform_tests/scripts/test_diagnose_codex_exec_hooks.py` - NEW (IP-1 tests).
- `platform_tests/scripts/test_codex_exec_hook_firing_path_<A|B|C>.py` - NEW (IP-3 tests).

## Test Plan

### Pre-implementation tests

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-cross-harness-trigger-codex-exec-hook-firing-001` - PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-cross-harness-trigger-codex-exec-hook-firing-001` - exit 0 expected.

### Investigation step (IP-1)

3. Run `python scripts/diagnose_codex_exec_hooks.py` - produces `<timestamp>-results.md`. Expected: registration state, before/after `dispatch-state.json.updated_at`, failure-count delta, and determination (fire+success / fire+fail / no-fire).

### Implementation step (IP-2/IP-3, branched)

4. **If Path A:** re-run IP-1 diagnostic; updated_at SHOULD change after `codex exec`.
5. **If Path B:** unit tests + IP-1 diagnostic regression confirm trigger handles `codex exec` env correctly.
6. **If Path C:** verify post-child reconciliation runs after child exits; integration test confirms state catches up.

### Regression

7. `pytest platform_tests/scripts/test_cross_harness_bridge_trigger*.py platform_tests/scripts/test_codex_hook_parity.py -q` - all PASS unchanged.

### Spec-to-test mapping

| Spec | Verifying test |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | 7 (full regression) |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | 1 |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | 2 + this mapping |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | filesystem assertion |
| ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 | 4/5/6 (chosen path restores owner-out-of-loop) |
| DCL-SMART-POLLER-AUTO-TRIGGER-001 | 3 (diagnostic + chosen path prove auto-trigger) |
| DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001 | 7 |
| PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001 | 3 (failures surfaced) |
| ADR-CODEX-HOOK-PARITY-FALLBACK-001 | 7 (hook-parity regression) |
| GOV-RELEASE-READINESS-GOVERNED-TESTING-001 | 4/5/6 + 7 |

## Acceptance Criteria

- [ ] IP-1 diagnostic exists; produces structured findings markdown; documents mutation and side effects honestly.
- [ ] IP-1 findings determine fix path; impl-report cites which path + why.
- [ ] Chosen path's fix lands; paired tests PASS.
- [ ] Existing trigger tests PASS unchanged (test 7).
- [ ] `bridge-essential.md` updated to document empirical behavior + chosen mechanism + post-child reconciliation fallback (with packet).
- [ ] Post-fix: real Codex cross-harness dispatch session leaves dispatch-state.json with `updated_at` >= Codex's verdict timestamp (no lag).
- [ ] Codex VERIFIED on post-implementation report.

## Risk + Rollback

### Risks

- **R1 (Medium):** Investigation may reveal `codex exec` does not fire hooks (Codex CLI limitation). Mitigation: Path C post-child reconciliation is a complete fallback.
- **R2 (Low):** Post-child reconciliation could fire concurrently with next dispatch parent wake. Mitigation: PID/dispatch ID tracking + atomic state updates prevent duplication.
- **R3 (Low):** Changing `.codex/hooks.json` (Path A) could regress hook behavior. Mitigation: tests cover regression; `git revert` is rollback.

### Rollback

`git revert <impl-commit-sha>`. Pre-fix lag behavior is undesirable but non-breaking.

## Recommended Commit Type

`fix:` - addresses documented dispatch-reliability defect. Subordinate `feat:` for diagnostic script if chosen path adds capability.

## Loyal Opposition Asks

1. Confirm IP-1 production-dispatch-session investigation (not isolated probe) is now appropriate.
2. Confirm the three candidate fix paths cover likely root-cause space.
3. Confirm post-child reconciliation (new Path C) satisfies the "state stays current after Codex completes" acceptance target.
4. Confirm `bridge-essential.md` + post-child fallback documentation is the right canonical surface.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
