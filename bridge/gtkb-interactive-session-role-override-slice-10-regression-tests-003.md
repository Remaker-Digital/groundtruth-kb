REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: S375-interactive-session-role-override-slice-10-revised-1
author_model: Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI default reasoning, explanatory output style

Project Authorization: PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001
Project: PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE
Work Item: WI-3480
target_paths: ["platform_tests/scripts/test_session_role_resolution_table.py", "platform_tests/scripts/test_session_role_marker_invalidation_both_harnesses.py", "platform_tests/scripts/test_codex_hook_parity_resolution_table_drift.py", "platform_tests/scripts/test_cross_harness_trigger_durable_keyed_regression.py", "platform_tests/scripts/test_strict_drop_misdirected_headless_dispatch.py"]

# GT-KB Interactive Session Role Override - Slice 10 Implementation Proposal: Cross-Harness Regression and Integration Tests - REVISED-1

bridge_kind: prime_proposal

Document: gtkb-interactive-session-role-override-slice-10-regression-tests
Version: 003 (REVISED-1; addresses Codex NO-GO at -002 F1)
Date: 2026-05-30 UTC

## Response to NO-GO -002 (F1 Resolution)

Codex F1 (P2) correctly identified three bare `pytest` invocations in the -001 proposal (lines 179, 231, 237) that trip `bridge_proposal_pattern_lint.py`'s `[bare-pytest]` rule. On Windows the bare command can resolve to an unexpected interpreter or miss the project module path; the repo standardizes on `python -m pytest` with an explicit interpreter.

This REVISED-1 replaces every bare `pytest` command in the implementation order and acceptance criteria with the explicit form `groundtruth-kb\.venv\Scripts\python.exe -m pytest`. No scope change; verification commands now use the deterministic repository interpreter.

Pre-revision lint output for -001 confirmed Codex's finding:

```text
Bridge proposal pattern lint: bridge/gtkb-interactive-session-role-override-slice-10-regression-tests-001.md
Findings: 3
[bare-pytest] line 179 ...
[bare-pytest] line 231 ...
[bare-pytest] line 237 ...
```

Post-revision lint expectation: `Findings: 0`.

## Claim

Slice 10 of PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE adds the cross-harness regression and integration test suite that proves the entire interactive-session-role-override architecture works as specified. Five new test modules under `platform_tests/scripts/` cover the 8 machine-checkable assertions in `DCL-SESSION-ROLE-RESOLUTION-001` plus the spec-derived verification scenarios enumerated in `bridge/gtkb-interactive-session-role-override-scoping-003.md` § "Spec-Derived Verification Plan". Tests are additive (no existing test changes), test files live under in-root platform_tests paths, and no protected narrative-authority paths are touched, so no formal-artifact-approval packets are required.

## Live Bridge State

```text
Document: gtkb-interactive-session-role-override-scoping
GO: bridge/gtkb-interactive-session-role-override-scoping-004.md  <- architecture authority

Document: gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table
NO-GO: bridge/...-015.md  <- v5 NO-GO; precondition for Slice 10 implementation

Document: gtkb-interactive-session-role-override-slice-9-rule-claude-agents-updates
NO-GO: bridge/...-002.md  <- sibling precondition; this REVISED-1 series in parallel

Document: gtkb-interactive-session-role-override-slice-10-regression-tests
NO-GO: bridge/...-002.md  <- addressed by this REVISED-1
NEW: bridge/...-001.md
```

## Specification Links

- `DCL-SESSION-ROLE-RESOLUTION-001` v1 (specified in MemBase; 8 machine-checkable assertions — primary target of this test suite)
- `GOV-SESSION-ROLE-AUTHORITY-001` v1 (specified in MemBase; authority split that the tests verify)
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` v1 (specified in MemBase; architecture that the tests exercise)
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v1
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` v1
- `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory)
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory)
- `bridge/gtkb-interactive-session-role-override-scoping-003.md` (Slice 10 spec at lines 363-374; spec-derived verification table at lines 452-470)
- `bridge/gtkb-interactive-session-role-override-scoping-004.md` (Codex GO)
- `bridge/gtkb-interactive-session-role-override-slice-1-sessionstart-cache-writer-007.md`
- `bridge/gtkb-interactive-session-role-override-slice-2-session-role-marker-008.md`
- `bridge/gtkb-interactive-session-role-override-slice-3-sessionstart-marker-invalidation-004.md`
- `bridge/gtkb-interactive-session-role-override-slice-4-axis2-role-awareness-004.md`
- `bridge/gtkb-interactive-session-role-override-slice-5-focus-menu-role-awareness-004.md`
- `bridge/gtkb-interactive-session-role-override-slice-6-attribution-role-awareness-004.md`
- `bridge/gtkb-interactive-session-role-override-slice-7-doctor-marker-checks-006.md`

## Prior Deliberations

- `bridge/gtkb-interactive-session-role-override-slice-10-regression-tests-001.md` — original NEW; this REVISED-1 carries forward the substantive scope unchanged.
- `bridge/gtkb-interactive-session-role-override-slice-10-regression-tests-002.md` — Codex NO-GO with F1 (P2) on bare-pytest verification commands; addressed by this REVISED-1.
- `bridge/gtkb-interactive-session-role-override-scoping-003.md` § "Slice 10 - Regression and integration tests" (lines 363-374) — concrete test scope per scoping.
- `bridge/gtkb-interactive-session-role-override-scoping-003.md` § "Spec-Derived Verification Plan" (lines 452-470) — the 8 assertions of DCL-SESSION-ROLE-RESOLUTION-001 mapped to verification scenarios.
- `bridge/gtkb-interactive-session-role-override-scoping-004.md` (Codex GO).
- Slices 1-7 VERIFIED test modules established the testing pattern.
- `DELIB-2507` — S371 owner directive establishing the project.

## Implementation Plan

### Sequencing Dependency

Per scoping-003 Slice 10 dependency note: Slices 1-9 must be VERIFIED before Slice 10 implementation begins. Slices 1, 3, 5, 6, 7 are VERIFIED. Slice 8 is at NO-GO `-015`. Slice 9 is at NO-GO `-002` with a parallel REVISED-1 in progress this session.

As with Slice 9, this dependency is an operator-level manual precondition, NOT a mechanical gate enforced by `scripts/implementation_authorization.py`. Before activating the Slice 10 implementation packet, Prime Builder will execute:

```bash
grep -A1 '^Document: gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table$' bridge/INDEX.md | head -2
grep -A1 '^Document: gtkb-interactive-session-role-override-slice-9-rule-claude-agents-updates$' bridge/INDEX.md | head -2
```

Both expected second lines begin with `VERIFIED:`. If either does not, Prime Builder will abort the Slice 10 activation and wait, OR surface a precondition-override AskUserQuestion to the owner before proceeding. The post-implementation report will include both captured `grep` outputs as evidence.

### New Test Modules

(Unchanged from -001; carried forward verbatim.)

Five new test modules under `platform_tests/scripts/`. Each is independently runnable, follows the existing pytest fixture pattern from Slice 6's `test_kb_attribution_session_role.py`, and uses an in-root basetemp per `.claude/rules/project-root-boundary.md`.

**Module 1: `test_session_role_resolution_table.py`** — end-to-end verification of `DCL-SESSION-ROLE-RESOLUTION-001`'s 7-row resolution table from a session-level perspective. Tests cover headless authorized/misdirected/legacy paths, interactive declaration/continuation/default/resume-after-compaction, marker-with-invalid-role-token, marker-with-stale-session-id. Parameterized via `pytest.mark.parametrize("harness", ["claude", "codex"])` where dispatcher-specific.

**Module 2: `test_session_role_marker_invalidation_both_harnesses.py`** — assertion 5: marker is ephemeral across SessionStart in both dispatchers. Tests invoke each dispatcher via subprocess with pre-written markers (clean, stale-session-id, malformed) and assert post-invocation marker absence.

**Module 3: `test_codex_hook_parity_resolution_table_drift.py`** — assertion 8: parity-check drift detection. Tests mutate one dispatcher in a tmp-staged copy and assert `scripts/check_codex_hook_parity.py` returns non-zero. Drift classes: StartupDecision divergence, cache-writer divergence, marker-invalidation divergence, plus a canonical-pass baseline.

**Module 4: `test_cross_harness_trigger_durable_keyed_regression.py`** — verification that `scripts/cross_harness_bridge_trigger.py` continues to dispatch counterpart bridge work using durable role authority. Tests: trigger ignores session role marker for recipient selection, emits durable-keyed init keyword, actionable signature is marker-independent, dispatch-failure audit log omits marker state.

**Module 5: `test_strict_drop_misdirected_headless_dispatch.py`** — regression that STRICT_DROP fires for misdirected headless dispatch in both dispatchers. Tests cover Claude/Codex STRICT_DROP when dispatched keyword is outside durable set, silent clean exit, audit-log kind correctness, and STRICT_DROP unaffected by session marker presence.

### Implementation Order (CORRECTED per F1)

1. Execute the live-INDEX precondition checks for Slice 8 and Slice 9 (see § Sequencing Dependency above). Record both captured `grep` outputs for the post-implementation report.
2. Activate implementation-start packet for this bridge thread.
3. Write the 5 test modules in the order listed (resolution table → marker invalidation → parity drift → cross-harness trigger regression → STRICT_DROP regression).
4. Run each module focused with the explicit interpreter:

   ```text
   groundtruth-kb\.venv\Scripts\python.exe -m pytest <module> -q --tb=short --basetemp=E:/GT-KB/.pytest-slice10-<timestamp>
   ```

   Then run the full platform lane:

   ```text
   groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/ -q --tb=short --basetemp=E:/GT-KB/.pytest-slice10-lane-<timestamp>
   ```

5. Confirm the existing full test suite still passes (no regressions in Slice 1-9 test modules).
6. Run all mandatory gates (ruff format + check, standalone parity).
7. File post-implementation report.

## Spec-Derived Verification Plan

Per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (mapping unchanged from -001; each DCL-SESSION-ROLE-RESOLUTION-001 assertion maps to test functions in one or more of the modules):

| DCL-SESSION-ROLE-RESOLUTION-001 Assertion | Test Module(s) | Function Count |
|---|---|---|
| 1. resolved=durable when headless and authorized | Module 1, Module 5 | 4+ |
| 2. resolved=keyword when interactive declaration | Module 1 | 1+ |
| 3. resolved=marker when interactive continuation | Module 1 | 1+ |
| 4. resolved=durable when interactive undeclared | Module 1 | 2 (includes compaction-resume case) |
| 5. marker is ephemeral across SessionStart (both dispatchers) | Module 2 | 4 |
| 6. marker carries session id | Module 1 | 1 |
| 7. marker role is role-set-member | Module 1 | 1 |
| 8. parity between harnesses | Module 3 | 5 |

Plus non-DCL spec-derived scenarios:
- Cross-harness trigger remains durable-keyed: Module 4 (4 tests).
- STRICT_DROP regression: Module 5 (5 tests).
- Disclosure shows session role only: covered by Slice 1's existing render-content check.

## Owner Decisions / Input

This slice proceeds on the AskUserQuestion evidence already captured for the parent project. No new owner decisions are required because the test suite implements verification of already-approved architectural intent.

- `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` v3 (active; reactivated per owner AUQ S374). Covers `WI-3480`. Scope: Slices 4-10.
- `DELIB-2507` — S371 owner directive establishing PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE.
- S371 AskUserQuestion decisions 1-6 — the architectural intent that the tests verify.
- Codex GO at `bridge/gtkb-interactive-session-role-override-scoping-004.md` — Slice 10 implementation authority.
- S375 AskUserQuestion (this session): owner directive to proceed with Slices 9 and 10 authorizes this REVISED-1.

## Requirement Sufficiency

**Existing requirements sufficient.** All target behavior is already specified by the three new MemBase artifacts (GOV/DCL/ADR), the revised `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` and `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`, and the scoping-003 § Spec-Derived Verification Plan. The F1 correction is a verification-command fix, not a requirement change.

## Clause Scope Clarification (Not a Bulk Operation)

Per `GOV-STANDING-BACKLOG-001` clause-scope clarification convention: this slice adds 5 new test modules under in-root `platform_tests/scripts/`. It introduces no backlog mutation, no work_items insert/update/retire/supersede, no project create/retire, no authorization change, no MemBase row insert, no canonical artifact insert, no inventory artifact, no review-packet, no formal-artifact-approval packet (test files are not protected narrative-authority paths), and no rule-text change. Evidence-pattern tokens: test additions, regression and integration tests, in-root platform_tests, no protected-path edits, no backlog mutation, no canonical artifact insert.

## In-Root Boundary Affirmation

Per `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `.claude/rules/project-root-boundary.md`: all 5 target paths live under `E:\GT-KB\platform_tests\scripts\`. Test basetemp uses an in-root path per the established convention. No application-layer paths, no `applications/<name>/` paths, no Agent Red references in a live-dependency role.

## Acceptance Criteria

| # | Criterion | Verification |
|---|---|---|
| 1 | All 5 new test modules exist at the target paths | ls + import |
| 2 | All new test functions pass on the canonical (post-Slice-8 + post-Slice-9) codebase | `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_session_role_*.py platform_tests/scripts/test_codex_hook_parity_resolution_table_drift.py platform_tests/scripts/test_cross_harness_trigger_durable_keyed_regression.py platform_tests/scripts/test_strict_drop_misdirected_headless_dispatch.py -q --tb=short` |
| 3 | Module 1 covers DCL-SESSION-ROLE-RESOLUTION-001 assertions 1-7 (assertion 8 covered by Module 3) | per the spec-derived mapping table above |
| 4 | Module 2 verifies marker invalidation in BOTH `.claude/hooks/session_start_dispatch.py` AND `.codex/gtkb-hooks/session_start_dispatch.py` | per Module 2 functions |
| 5 | Module 3 verifies parity-check drift detection for the 4 drift classes plus one canonical-pass baseline | per Module 3 functions |
| 6 | Module 4 verifies cross-harness trigger ignores session marker for recipient selection, init-keyword emission, signature computation, and audit-log content | per Module 4 functions |
| 7 | Module 5 regression-verifies STRICT_DROP behavior in both dispatchers including clean exit and audit-log fidelity, and verifies marker presence does NOT affect STRICT_DROP | per Module 5 functions |
| 8 | No existing test regresses | `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/ -q --tb=short` reports same baseline-PASS count as pre-Slice-10 plus the new tests |
| 9 | `ruff format --check` and `ruff check` clean on all 5 new modules | `groundtruth-kb\.venv\Scripts\ruff.exe format --check platform_tests/scripts/test_session_role_*.py ...` and `groundtruth-kb\.venv\Scripts\ruff.exe check ...` |
| 10 | Bridge applicability + clause preflights pass on the post-implementation report | preflight commands |
| 11 | Sequencing preconditions satisfied via live-INDEX manual checks at Slice 10 activation time. Post-implementation report includes the captured `grep -A1 ...` outputs for both Slice 8 and Slice 9 threads. Both second lines begin with `VERIFIED:` OR an owner-override AskUserQuestion answer is cited. | live INDEX check at activation moment + recorded outputs in post-impl report |
| 12 | **CORRECTED:** No bare `pytest` invocations in this proposal or in the post-implementation report. `bridge_proposal_pattern_lint.py` reports `Findings: 0`. | `groundtruth-kb\.venv\Scripts\python.exe scripts/bridge_proposal_pattern_lint.py --bridge-id ...` |

## Risk and Rollback

- **Risk:** Subprocess invocation of the SessionStart dispatcher in Module 2 introduces test-runtime dependency on the dispatcher's environment expectations. **Mitigation:** reuse the established Slice 7 dispatcher-invocation pattern.
- **Risk:** Mutation tests in Module 3 may shadow real source files. **Mitigation:** mutations operate on a `_stage_relevant_files(tmp_path)` copy per the established pattern.
- **Risk:** Cross-harness trigger Module 4 introduces flakiness due to filesystem race with parallel sessions. **Mitigation:** isolated tmp_path basetemp per test; trigger invocation uses isolated `dispatch-state.json`.
- **Risk:** Slice 8 reaches VERIFIED with v6+ semantics that change parity-check error messages, requiring Module 3 test text updates. **Mitigation:** Slice 10 is sequenced after Slice 8 VERIFIED.
- **Risk:** The new tests slow the platform_tests pytest lane meaningfully. **Mitigation:** ~25-35 added tests against ~2000 baseline; impact small.
- **Risk:** Codex requires additional tests for edge cases not enumerated here. **Mitigation:** REVISED-N is expected if Codex finds gaps; modular file structure makes additions easy.
- **Rollback:** each test module is one new file; removing the file removes the test. No production code change.

## Recommended Commit Type

`test:` — Slice 10 adds tests only. No code, no docs, no behavior change.

## Files Touched

5 files (per target_paths):
- `platform_tests/scripts/test_session_role_resolution_table.py` (new)
- `platform_tests/scripts/test_session_role_marker_invalidation_both_harnesses.py` (new)
- `platform_tests/scripts/test_codex_hook_parity_resolution_table_drift.py` (new)
- `platform_tests/scripts/test_cross_harness_trigger_durable_keyed_regression.py` (new)
- `platform_tests/scripts/test_strict_drop_misdirected_headless_dispatch.py` (new)

No protected narrative-authority paths. No formal-artifact-approval packets required.

## Owner Action Required

At proposal review time: none beyond Codex review.

At implementation start (after Slice 8 + Slice 9 VERIFIED, plus Codex GO on this proposal): none beyond the standard implementation-start packet activation. Precondition-override AskUserQuestion if either Slice 8 or Slice 9 is still not VERIFIED at activation time.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
