# Implementation Proposal — Cross-Harness Trigger Codex-Exec Hook Firing Investigation + Fix

bridge_kind: prime_proposal
Document: gtkb-cross-harness-trigger-codex-exec-hook-firing-001
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-10 UTC
Trigger: Owner observation 2026-05-10 post-WI-3264-VERIFIED — dispatch-state.json stayed at 16:34:36Z for ~8 minutes after Codex wrote VERIFIED -006 + edited INDEX.md. Manual trigger run cleared the lag instantly. Zero failure entries during the lag window confirms the trigger did NOT run, distinct from the WI-3264 write-reliability fix.

## Claim

Investigate why `.codex/hooks.json` PostToolUse + Stop hooks do not effectively dispatch the cross-harness trigger during `codex exec` cross-harness dispatch sessions, then fix or document a reliable mechanism so the dispatch-state stays current after Codex completes its work.

## Why Now

WI-3264 closed the write-reliability defect class (191 historical Windows-rename failures fixed). The newly-observed lag class is distinct: zero failure entries during the lag window means the trigger did not execute, not that it executed and failed. Without resolution, every Codex cross-harness dispatch session leaves dispatch-state stale until a Prime tool-use or manual trigger run refreshes it. That defeats Axis 1's owner-out-of-loop dispatch contract (per `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` v2 and `DCL-SMART-POLLER-AUTO-TRIGGER-001` v2).

## Specification Links

**Cross-cutting (blocking):**
- `GOV-FILE-BRIDGE-AUTHORITY-001` — INDEX-as-canonical preserved.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — see `## Test Plan`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — touched files all under `E:\GT-KB`.

**Direct dispatch-governance (blocking):**
- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` v2 — owner-out-of-loop dispatch contract; the lag breaks this contract until a manual or Prime-side trigger fires.
- `DCL-SMART-POLLER-AUTO-TRIGGER-001` v2 — auto-trigger contract; auto-trigger requires the trigger to execute; this proposal restores execution reliability.
- `DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001` v2 — spawned-harness role-defer contract preserved.
- `PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001` v2 — protected-behavior record from prior daemon-dispatch-disabled incident; this fix preserves the surfacing-failures invariant.

**Cross-cutting (advisory):**
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

**Directly-relevant rules:**
- `.claude/rules/bridge-essential.md` — bridge-integrity mandate; cross-harness trigger as canonical Axis-1 dispatch.
- `.claude/rules/file-bridge-protocol.md` — INDEX as canonical workflow state.
- `.claude/rules/codex-review-gate.md` — implementation requires Codex GO.
- `.claude/rules/canonical-terminology.md` — `cross-harness event-driven trigger` glossary preserved.

**Application-relevant:**
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` — bridge automation reliability is release-gate-visible.

## Prior Deliberations

- **DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08** — empirical foundation that Codex hooks fire on Windows in INTERACTIVE Codex CLI sessions. Critical: the retest covered interactive `codex` runs, NOT `codex exec` cross-harness dispatch invocations. The lag observation suggests hook behavior diverges between the two modes.
- **DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08** — `codex_hooks` feature is `stable, true` for Codex CLI ≥ 0.128.0-alpha.1 in interactive mode; behavior in `codex exec` is unconfirmed.
- **`gtkb-cross-harness-trigger-windows-rename-race-001` VERIFIED at -006 (2026-05-10)** — closed the write-reliability defect class; this thread addresses the parallel firing-reliability defect class.
- **`gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-001` VERIFIED at -006** — established the PostToolUse + Stop hook registrations in `.codex/hooks.json` and `.claude/settings.json`. Slice 3's tests covered registration-presence; runtime firing in `codex exec` was not exercised.
- **`gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001` VERIFIED at -020** — retired the smart-poller substrate. The retirement assumed the cross-harness trigger fires reliably; this proposal addresses a gap in that assumption.


### Helper-suggested candidates

<!-- Pre-populated by helper; review and prune. -->
- DA: `DELIB-1332` — seed=search; bridge_thread; Codex Review - GTKB Directive Enforcement Registry
- DA: `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` — seed=search; report; Empirical retest: Codex hooks DO fire on Windows in CLI v0.128.0-alpha.1; ADR-CO
- DA: `DELIB-0837` — seed=search; owner_conversation; Session formalization audit: decisions, directives, and principles mapped to art
- DA: `DELIB-1005` — seed=search; bridge_thread; GTKB-ISOLATION-015 - Loyal Opposition Verification Review
- DA: `DELIB-1046` — seed=search; bridge_thread; Loyal Opposition Response: GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 5 Revision 1

## Owner Decisions / Input

- **Owner direction 2026-05-10:** "Proceed in order 3, 2 then 1. Please parallelize work whenever possible and continue with new work unsupervised if possible. Close as much of the backlog as you can." Authorizes filing this proposal as Step 3.
- **Owner observation (screenshot 2026-05-10 post-VERIFIED):** "the automated Codex dispatch run did process the entry successfully, but `.gtkb-state/bridge-poller/dispatch-state.json` still shows the pre-verification Codex pending signature... bridge/INDEX.md is authoritative and terminal for this thread, but the dispatch-state refresh lag is worth keeping in the bridge-efficacy observations." This proposal converts that observation into tracked corrective work.
- **Outstanding owner decisions before VERIFIED:** none. The investigation result determines the fix path; each candidate path is scoped within bridge-protocol-acceptable change classes.

## Scope (investigation + branched fix)

### IP-1: Empirical investigation (deterministic-services principle)

Author `scripts/diagnose_codex_exec_hooks.py` — a small read-only diagnostic that:

1. Reads `.codex/hooks.json` registration state.
2. Records `dispatch-state.json.updated_at` BEFORE invoking `codex exec --skip-git-repo-check "<sentinel>"`.
3. Invokes `codex exec` with a sentinel prompt that performs a no-op (e.g., `"echo done"`).
4. Records `dispatch-state.json.updated_at` AFTER the codex exec returns.
5. Records `dispatch-failures.jsonl` line count delta.
6. Emits findings: did the trigger fire (state.updated_at changed)? Did it fail (failure count increased)? Or did it not run (state unchanged + zero failures)?

The diagnostic does NOT mutate state. Output is a structured markdown summary suitable for inclusion in the implementation report's evidence section.

Run output goes to `.gtkb-state/codex-exec-hook-investigation/<timestamp>-results.md`.

### IP-2: Fix path determined by investigation findings

Three candidate fix paths; the IP-1 diagnostic findings determine which applies:

- **Path A: hook-registration repair.** If `.codex/hooks.json` lacks a needed registration (e.g., a `codex exec`-specific hook event), add it. Tests verify the new registration fires in `codex exec`.
- **Path B: trigger-side fallback.** If hooks fire in `codex exec` but the trigger no-ops (e.g., env detection wrong), patch the trigger to detect and handle the `codex exec` env. Tests verify state-update happens for `codex exec` invocations.
- **Path C: documented manual fallback + auto-recovery.** If `codex exec` truly does not run hooks (Codex CLI limitation), add a `cross_harness_bridge_trigger.py` startup fallback that runs the trigger automatically when Prime's session starts (catching state from prior Codex `exec` sessions). Document in `bridge-essential.md` as the known mechanism.

Path C is the safest fallback; Paths A or B are preferable if the investigation reveals a fixable root cause.

### IP-3: Tests for the chosen fix path

Each path has its own test plan; spec'd in IP-2 of the impl-report based on findings.

### IP-4: Update `bridge-essential.md` (narrative artifact, packet required)

Add a §"Codex-Exec Hook Firing" subsection documenting the empirical behavior found in IP-1 and the fix path applied. This is a narrative-artifact edit; requires formal-artifact-approval packet.

### OUT OF SCOPE

- Re-enabling retired pollers.
- Migrating off `codex exec` to a different cross-harness mechanism.
- Active-session-suppression behavior (independent; unchanged).
- WinError-class write-reliability (already fixed in WI-3264).

## Files Expected To Change

- `scripts/diagnose_codex_exec_hooks.py` — NEW (IP-1).
- `scripts/cross_harness_bridge_trigger.py` — POSSIBLY MODIFIED (depends on chosen path).
- `.codex/hooks.json` — POSSIBLY MODIFIED (Path A only).
- `.claude/rules/bridge-essential.md` — MODIFIED (IP-4; with packet).
- `tests/scripts/test_diagnose_codex_exec_hooks.py` — NEW (IP-1 tests).
- `tests/scripts/test_codex_exec_hook_firing_path_<A|B|C>.py` — NEW (IP-3 tests; one of the three based on findings).

## Test Plan

### Pre-implementation tests

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-cross-harness-trigger-codex-exec-hook-firing-001` — PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-cross-harness-trigger-codex-exec-hook-firing-001` — exit 0 expected.

### Investigation step (IP-1)

3. Run `python scripts/diagnose_codex_exec_hooks.py` — produces `<timestamp>-results.md`. Expected output documents: registration state, before/after `dispatch-state.json.updated_at`, failure-count delta, and a determination (fire+success / fire+fail / no-fire).

### Implementation step (IP-2/IP-3, branched)

4. **If Path A:** verify new registration fires by re-running IP-1 diagnostic. Updated_at SHOULD change after `codex exec`.
5. **If Path B:** verify trigger handles `codex exec` env correctly via unit tests + IP-1 diagnostic regression.
6. **If Path C:** verify Prime-startup fallback runs the trigger; integration test confirms state catches up after a simulated Codex-exec-without-hooks scenario.

### Regression

7. `pytest tests/scripts/test_cross_harness_bridge_trigger.py tests/scripts/test_cross_harness_bridge_trigger_rename_retry.py tests/scripts/test_cross_harness_bridge_trigger_concurrent_writes.py tests/scripts/test_cross_harness_bridge_trigger_diagnose.py -q` — 30/30 PASS unchanged.

### Spec-to-test mapping

| Spec | Verifying test |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | 7 (full regression) |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | 1 |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | 2 + this mapping |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | filesystem assertion |
| ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 v2 | 4/5/6 (chosen path's regression confirms owner-out-of-loop dispatch is restored) |
| DCL-SMART-POLLER-AUTO-TRIGGER-001 v2 | 3 (diagnostic finding + chosen path's fix proves auto-trigger fires reliably) |
| DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001 v2 | 7 |
| PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001 v2 | 3 (failures surfaced not silently accepted) |
| GOV-RELEASE-READINESS-GOVERNED-TESTING-001 | 4/5/6 + 7 |

## Acceptance Criteria

- [ ] `scripts/diagnose_codex_exec_hooks.py` exists; produces a structured findings markdown; does NOT mutate state.
- [ ] IP-1 findings determine fix path; impl-report cites which path was chosen and why.
- [ ] Chosen path's fix lands; paired tests PASS.
- [ ] Existing 30 trigger tests PASS unchanged (test 7).
- [ ] `bridge-essential.md` updated to document the empirical behavior + chosen mechanism (with packet).
- [ ] Post-fix observation: a real Codex cross-harness dispatch session leaves dispatch-state.json with `updated_at` ≥ Codex's verdict timestamp (no lag).
- [ ] Codex VERIFIED on post-implementation report.

## Risk + Rollback

### Risks

- **R1 (Medium):** Investigation may reveal that `codex exec` simply does not fire hooks (Codex CLI limitation). Mitigation: Path C is a complete fallback; documents the limitation and adds Prime-startup recovery.
- **R2 (Low):** Adding a Prime-startup hook to run the trigger (Path C) could fire on every session start, adding ~100ms latency. Mitigation: trigger is fast (read INDEX, hash, compare); 100ms is acceptable.
- **R3 (Low):** Changing `.codex/hooks.json` (Path A) could regress existing Codex hook behavior. Mitigation: tests cover hook-firing regression; rollback is `git revert`.

### Rollback

`git revert <impl-commit-sha>`. The pre-fix lag behavior is undesirable but non-breaking (manual trigger run is the existing fallback).

## Recommended Commit Type

`fix:` — addresses a documented dispatch-reliability defect. Subordinate `feat:` for the new diagnostic script if the chosen path adds capability.

## Loyal Opposition Asks

1. Confirm IP-1's investigation-first design is appropriate vs. committing to a fix path upfront.
2. Confirm the three candidate fix paths cover the likely root-cause space.
3. Confirm the Prime-startup-fallback (Path C) is acceptable as a documented mechanism if hooks genuinely don't fire in `codex exec`.
4. Confirm `bridge-essential.md` is the right canonical narrative artifact for documenting the chosen mechanism.

## Applicability Preflight

To be filled in by Codex at GO/NO-GO time. Prime self-check expected to PASS.

## Copyright

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
