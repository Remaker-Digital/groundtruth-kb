NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: S375-interactive-session-role-override-slice-10-new
author_model: Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI default reasoning, explanatory output style

Project Authorization: PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001
Project: PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE
Work Item: WI-3480
target_paths: ["platform_tests/scripts/test_session_role_resolution_table.py", "platform_tests/scripts/test_session_role_marker_invalidation_both_harnesses.py", "platform_tests/scripts/test_codex_hook_parity_resolution_table_drift.py", "platform_tests/scripts/test_cross_harness_trigger_durable_keyed_regression.py", "platform_tests/scripts/test_strict_drop_misdirected_headless_dispatch.py"]

# GT-KB Interactive Session Role Override - Slice 10 Implementation Proposal: Cross-Harness Regression and Integration Tests

bridge_kind: implementation_proposal

Document: gtkb-interactive-session-role-override-slice-10-regression-tests
Version: 001
Date: 2026-05-30 UTC

## Claim

Slice 10 of PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE adds the cross-harness regression and integration test suite that proves the entire interactive-session-role-override architecture works as specified. Five new test modules under `platform_tests/scripts/` cover the 8 machine-checkable assertions in `DCL-SESSION-ROLE-RESOLUTION-001` plus the spec-derived verification scenarios enumerated in `bridge/gtkb-interactive-session-role-override-scoping-003.md` § "Spec-Derived Verification Plan". The tests are additive (no existing test changes), test files live under in-root platform_tests paths, and no protected narrative-authority paths are touched — so no formal-artifact-approval packets are required.

## Live Bridge State

```text
Document: gtkb-interactive-session-role-override-scoping
GO: bridge/gtkb-interactive-session-role-override-scoping-004.md  ← architecture authority

Document: gtkb-interactive-session-role-override-slice-7-doctor-marker-checks
VERIFIED: bridge/...-006.md

Document: gtkb-interactive-session-role-override-slice-6-attribution-role-awareness
VERIFIED: bridge/...-004.md

Document: gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table
NO-GO: bridge/...-015.md  ← v5 NO-GO; this slice has an implementation-sequencing dependency on Slice 8 VERIFIED + Slice 9 VERIFIED

Document: gtkb-interactive-session-role-override-slice-10-regression-tests
NEW: bridge/...-001.md  ← this proposal
```

## Specification Links

- `DCL-SESSION-ROLE-RESOLUTION-001` v1 (specified in MemBase; 8 machine-checkable assertions — primary target of this test suite)
- `GOV-SESSION-ROLE-AUTHORITY-001` v1 (specified in MemBase; authority split that the tests verify)
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` v1 (specified in MemBase; architecture that the tests exercise)
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v1 (init keyword regex; receiver-side behavior verified)
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` v1 (revised receiver-side decision table; STRICT_DROP + DISPATCH_AUTHORIZED + INTERACTIVE_OVERRIDE_AUTHORIZED + LEGACY_FALLBACK + NORMAL_STARTUP verified)
- `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001` (cross-harness parity contract)
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` (parity-check authority)
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
- `bridge/gtkb-interactive-session-role-override-scoping-004.md` (Codex GO — architecture authority for this slice)
- `bridge/gtkb-interactive-session-role-override-slice-1-sessionstart-cache-writer-007.md`
- `bridge/gtkb-interactive-session-role-override-slice-2-session-role-marker-008.md`
- `bridge/gtkb-interactive-session-role-override-slice-3-sessionstart-marker-invalidation-004.md`
- `bridge/gtkb-interactive-session-role-override-slice-4-axis2-role-awareness-004.md`
- `bridge/gtkb-interactive-session-role-override-slice-5-focus-menu-role-awareness-004.md`
- `bridge/gtkb-interactive-session-role-override-slice-6-attribution-role-awareness-004.md`
- `bridge/gtkb-interactive-session-role-override-slice-7-doctor-marker-checks-006.md`

## Prior Deliberations

- `bridge/gtkb-interactive-session-role-override-scoping-003.md` § "Slice 10 - Regression and integration tests" (lines 363-374) — concrete test scope per scoping.
- `bridge/gtkb-interactive-session-role-override-scoping-003.md` § "Spec-Derived Verification Plan" (lines 452-470) — the 8 assertions of DCL-SESSION-ROLE-RESOLUTION-001 mapped to verification scenarios.
- `bridge/gtkb-interactive-session-role-override-scoping-004.md` (Codex GO) — confirmed the 10-slice decomposition includes a dedicated regression/integration test slice.
- Slices 1-7 VERIFIED test modules established the testing pattern; this slice builds on `platform_tests/scripts/test_kb_attribution_session_role.py` (Slice 6) and `platform_tests/scripts/test_doctor_session_role_marker.py` (Slice 7) as primary reference patterns.
- `DELIB-2507` — S371 owner directive establishing the project.
- `groundtruth-kb/.venv/Scripts/gt.exe deliberations search "interactive session role override slice 10 regression tests" --limit 8` returned no Deliberation Archive matches; this is novel test scope under an existing thread family.

## Implementation Plan

### Sequencing Dependency

Per scoping-003 Slice 10 dependency note: "Slices 1-9." Slices 1, 3, 5, 6, 7 are VERIFIED. Slice 8 is at NO-GO `-015` (v5 finding). Slice 9 is at NEW (this session, filed in parallel with this proposal).

Slice 10 implementation will NOT begin until Slices 8 AND 9 reach VERIFIED, because the tests reference both the parity-check assertions (Slice 8) and the documented rule-text behavior (Slice 9). Several test scenarios from `DCL-SESSION-ROLE-RESOLUTION-001` already have partial test coverage from Slices 1-7's per-slice test modules; Slice 10 consolidates the cross-harness end-to-end view.

### New Test Modules

Five new test modules under `platform_tests/scripts/`. Each module is independently runnable, follows the existing pytest fixture pattern from Slice 6's `test_kb_attribution_session_role.py`, and uses an in-root basetemp (per `.claude/rules/project-root-boundary.md`).

#### Module 1: `test_session_role_resolution_table.py`

**Scope:** end-to-end verification of `DCL-SESSION-ROLE-RESOLUTION-001`'s 7-row resolution table from a session-level perspective. Tests the resolved role for each context combination by exercising `_resolve_session_role` (or equivalent shared resolver added by Slices 1-4) with parameterized fixtures.

**Test functions (one per resolution-table row, parameterized over both harnesses where applicable):**

| Test | Scenario | DCL Assertion |
|---|---|---|
| `test_headless_authorized_resolves_to_durable_when_keyword_in_set` | env-var present, keyword matches durable set | 1 |
| `test_headless_misdirected_strict_drops_when_keyword_not_in_set` | env-var present, keyword NOT in durable set | 1 (negative; STRICT_DROP path) |
| `test_headless_legacy_resolves_to_durable_when_no_keyword` | env-var present, no keyword | 1 (LEGACY_FALLBACK) |
| `test_interactive_declaration_resolves_to_keyword_role` | env-var absent, init keyword present | 2 |
| `test_interactive_continuation_resolves_to_marker_role` | env-var absent, marker present, no keyword on this prompt | 3 |
| `test_interactive_default_resolves_to_durable_when_undeclared` | env-var absent, no marker, no keyword | 4 |
| `test_interactive_resume_after_compaction_resolves_to_durable` | env-var absent, no marker (compaction invalidated), no keyword | 4 (resume special case) |
| `test_marker_with_invalid_role_token_treated_as_absent` | env-var absent, marker with `role=invalid`, no keyword | 7 |
| `test_marker_with_stale_session_id_treated_as_absent` | env-var absent, marker with mismatched session-id, no keyword | 6 |

Parameterization via `pytest.mark.parametrize("harness", ["claude", "codex"])` for tests whose behavior is dispatcher-specific.

#### Module 2: `test_session_role_marker_invalidation_both_harnesses.py`

**Scope:** verification of `DCL-SESSION-ROLE-RESOLUTION-001` assertion 5 (marker is ephemeral across SessionStart in both dispatchers).

**Test functions:**

| Test | Scenario |
|---|---|
| `test_claude_session_start_invalidates_preexisting_marker` | write marker, invoke `.claude/hooks/session_start_dispatch.py` via subprocess, assert marker absent post-run |
| `test_codex_session_start_invalidates_preexisting_marker` | write marker, invoke `.codex/gtkb-hooks/session_start_dispatch.py` via subprocess, assert marker absent post-run |
| `test_session_start_invalidates_stale_marker_from_prior_session_id` | pre-write marker with a different session-id, invoke each dispatcher, assert marker absent |
| `test_session_start_invalidates_malformed_marker` | pre-write marker with invalid JSON, invoke each dispatcher, assert marker absent and a doctor WARN is emittable (deferring the WARN-emission test to the existing Slice 7 test module) |

#### Module 3: `test_codex_hook_parity_resolution_table_drift.py`

**Scope:** verification of `DCL-SESSION-ROLE-RESOLUTION-001` assertion 8 (parity check fails when one dispatcher diverges from the new contract).

This module follows the existing pattern from `platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py` (Slice 8's test module). The Slice 8 module already covers the StartupDecision closed-vocabulary assertion; Slice 10's additions cover the higher-level drift scenarios.

**Test functions:**

| Test | Mutation | Expected |
|---|---|---|
| `test_parity_fails_when_only_claude_implements_interactive_override` | mutate Codex dispatcher to revert to `SPOOF_FALLBACK` | parity check returns non-zero with a STARTUP_DECISION_DRIFT-class error |
| `test_parity_fails_when_only_codex_implements_interactive_override` | mutate Claude dispatcher symmetrically | parity check returns non-zero |
| `test_parity_fails_when_cache_writer_diverges` | mutate one dispatcher's `_write_role_scoped_startup_relay_caches` to skip the alternate-role cache | parity check returns non-zero with a CACHE_WRITER_DRIFT-class error |
| `test_parity_fails_when_marker_invalidation_diverges` | mutate one dispatcher to skip the marker invalidation step | parity check returns non-zero with a MARKER_INVALIDATION_DRIFT-class error |
| `test_parity_passes_on_canonical_implementation` | unchanged source | parity check returns zero |

#### Module 4: `test_cross_harness_trigger_durable_keyed_regression.py`

**Scope:** verification that `scripts/cross_harness_bridge_trigger.py` continues to dispatch counterpart bridge work using durable role authority — the interactive marker MUST NOT affect dispatch routing.

**Test functions:**

| Test | Scenario | Expected |
|---|---|---|
| `test_trigger_ignores_session_role_marker_for_recipient_selection` | write an LO marker, invoke trigger with an actionable NEW; recipient selection should ignore marker | recipient resolved from durable role, not marker |
| `test_trigger_emits_durable_keyed_init_keyword` | trigger dispatching to a durable-PB recipient should emit `::init gtkb pb`, not `::init gtkb lo`, regardless of any present marker | keyword matches durable role |
| `test_trigger_actionable_signature_is_marker_independent` | actionable-signature computation should be byte-identical with and without a marker present | signatures equal |
| `test_trigger_dispatch_failure_audit_log_omits_marker_state` | trigger failure audit-log entries do not include marker contents (marker is interactive-session state, not headless-dispatch context) | audit-log entries free of marker fields |

#### Module 5: `test_strict_drop_misdirected_headless_dispatch.py`

**Scope:** regression that `STRICT_DROP` continues to fire for misdirected headless dispatch in BOTH dispatchers. The new INTERACTIVE_OVERRIDE_AUTHORIZED path must NOT weaken this gate.

**Test functions:**

| Test | Scenario | Expected |
|---|---|---|
| `test_claude_strict_drop_when_dispatched_keyword_outside_durable_set` | env-var present, keyword `::init gtkb lo`, Claude durable PB-only | STRICT_DROP decision; audit-log entry written |
| `test_codex_strict_drop_when_dispatched_keyword_outside_durable_set` | parallel for Codex | STRICT_DROP decision; audit-log entry written |
| `test_strict_drop_silent_clean_exit` | dispatcher exits cleanly (returns zero) after STRICT_DROP; no error surfaced to UserPromptSubmit | clean exit code |
| `test_strict_drop_audit_log_kind` | audit-log entry's `kind` field equals `misdirected_dispatch_strict_drop` per `_AUDIT_LOG_KIND_LITERAL` | matches the literal |
| `test_strict_drop_unaffected_by_session_marker_presence` | write an LO marker, then exercise STRICT_DROP scenario; STRICT_DROP behavior is unchanged because env-var is present (headless path) | STRICT_DROP fires regardless of marker |

### Implementation Order

1. Wait for Slice 8 VERIFIED and Slice 9 VERIFIED.
2. Activate implementation-start packet for this bridge thread.
3. Write the 5 test modules in the order above (resolution table → marker invalidation → parity drift → cross-harness trigger regression → STRICT_DROP regression).
4. Run each module focused (`pytest <module>`), then run them together (`pytest platform_tests/scripts/`).
5. Confirm the existing full test suite still passes (no regressions in Slice 1-9 test modules).
6. Run all mandatory gates (ruff format + check, standalone parity).
7. File post-implementation report.

## Spec-Derived Verification Plan

Per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, this slice's spec-to-test mapping is the test-module table itself — every assertion of `DCL-SESSION-ROLE-RESOLUTION-001` maps to at least one test function in the modules above. Summary:

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

Plus the non-DCL spec-derived scenarios from scoping-003:
- Cross-harness trigger remains durable-keyed: Module 4 (4 tests).
- STRICT_DROP regression: Module 5 (5 tests).
- Disclosure shows session role only: covered by the Slice 1 test module's existing render-content check (no Slice 10 addition needed; the verification is referenced for completeness).

## Owner Decisions / Input

This slice proceeds on the AskUserQuestion evidence already captured for the parent project. No new owner decisions are required because the test suite implements verification of already-approved architectural intent.

- `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` v3 (active; reactivated per owner AUQ S374). Covers `WI-3480`. Scope: Slices 4-10 of the interactive-session-role-override architecture.
- `DELIB-2507` — the S371 owner directive establishing PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE.
- S371 AskUserQuestion decisions 1-6 — the architectural intent that the tests verify.
- Codex GO at `bridge/gtkb-interactive-session-role-override-scoping-004.md` — Slice 10 implementation authority.
- S375 AskUserQuestion (this session): owner directive to proceed with Slices 9 and 10 authorizes the filing of this proposal in parallel with the sibling Slice 9 proposal.

## Requirement Sufficiency

**Existing requirements sufficient.** All target behavior is already specified by the three new MemBase artifacts (GOV/DCL/ADR), the revised `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` and `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`, and the scoping-003 § Spec-Derived Verification Plan that enumerates every verification scenario. No requirement revision is needed.

## Clause Scope Clarification (Not a Bulk Operation)

Per `GOV-STANDING-BACKLOG-001` clause-scope clarification convention: this slice adds 5 new test modules under in-root `platform_tests/scripts/`. It introduces no backlog mutation, no work_items insert/update/retire/supersede, no project create/retire, no authorization change, no MemBase row insert, no canonical artifact insert, no inventory artifact, no review-packet, no formal-artifact-approval packet (test files are not protected narrative-authority paths), and no rule-text change. Evidence-pattern tokens: test additions, regression and integration tests, in-root platform_tests, no protected-path edits, no backlog mutation, no canonical artifact insert.

## In-Root Boundary Affirmation

Per `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `.claude/rules/project-root-boundary.md`: all 5 target paths live under `E:\GT-KB\platform_tests\scripts\`. Test basetemp will use an in-root path per the established convention (e.g., `E:/GT-KB/.pytest-slice10-<timestamp>`). No application-layer paths, no `applications/<name>/` paths, no Agent Red references in a live-dependency role.

## Acceptance Criteria

| # | Criterion | Verification |
|---|---|---|
| 1 | All 5 new test modules exist at the target paths | ls + import |
| 2 | All new test functions pass on the canonical (post-Slice-8 + post-Slice-9) codebase | `pytest platform_tests/scripts/test_session_role_*.py platform_tests/scripts/test_codex_hook_parity_resolution_table_drift.py platform_tests/scripts/test_cross_harness_trigger_durable_keyed_regression.py platform_tests/scripts/test_strict_drop_misdirected_headless_dispatch.py` |
| 3 | Module 1 covers DCL-SESSION-ROLE-RESOLUTION-001 assertions 1-7 (assertion 8 covered by Module 3) | per the spec-derived mapping table above |
| 4 | Module 2 verifies marker invalidation in BOTH `.claude/hooks/session_start_dispatch.py` AND `.codex/gtkb-hooks/session_start_dispatch.py` | per Module 2 functions |
| 5 | Module 3 verifies parity-check drift detection for the 4 drift classes (StartupDecision, cache writer, marker invalidation, plus one canonical-pass baseline) | per Module 3 functions |
| 6 | Module 4 verifies cross-harness trigger ignores the session marker for recipient selection, init-keyword emission, signature computation, and audit-log content | per Module 4 functions |
| 7 | Module 5 regression-verifies STRICT_DROP behavior in both dispatchers, including clean exit and audit-log fidelity, and verifies marker presence does NOT affect STRICT_DROP | per Module 5 functions |
| 8 | No existing test regresses | `pytest platform_tests/scripts/` reports same baseline-PASS count as pre-Slice-10 plus the new tests |
| 9 | `ruff format --check` and `ruff check` clean on all 5 new modules | `ruff format --check platform_tests/scripts/test_session_role_*.py ...` |
| 10 | Bridge applicability + clause preflights pass on the post-implementation report | preflight commands |
| 11 | Slice 8 and Slice 9 are VERIFIED before Slice 10 implementation begins | check `bridge/INDEX.md` |

## Risk and Rollback

- **Risk:** Subprocess invocation of the SessionStart dispatcher in Module 2 introduces test-runtime dependency on the dispatcher's environment expectations. **Mitigation:** use the established Slice 7 dispatcher-invocation pattern (`platform_tests/scripts/test_doctor_session_role_marker.py` already invokes the dispatcher pathway); reuse the fixture rather than reinventing.
- **Risk:** Mutation tests in Module 3 may shadow real source files. **Mitigation:** mutations operate on a `_stage_relevant_files(tmp_path)` copy per the established pattern in `test_check_codex_hook_parity_resolution_table.py`; the live source is never mutated.
- **Risk:** Cross-harness trigger Module 4 introduces flakiness due to filesystem race with parallel sessions. **Mitigation:** use isolated tmp_path basetemp per test; trigger invocation uses an isolated `dispatch-state.json` under the tmp_path.
- **Risk:** Slice 8 reaches VERIFIED with v6+ semantics that change the parity-check error messages, requiring Module 3 test text updates. **Mitigation:** Slice 10 is sequenced after Slice 8 VERIFIED, so the parity-check error format is stable at Module 3 authoring time.
- **Risk:** The new tests slow the platform_tests pytest lane meaningfully. **Mitigation:** the 5 modules together add roughly 25-35 tests; baseline is ~2000 tests in the platform lane; impact is small.
- **Risk:** Codex requires additional tests for edge cases not enumerated here. **Mitigation:** treat REVISED-1 as expected if Codex finds gaps; the modular file structure makes it easy to add a test without restructuring.
- **Rollback:** each test module is one new file; removing the file removes the test. No production code change; no rollback risk to runtime behavior.

## Recommended Commit Type

`test:` — Slice 10 adds tests only. No code, no docs, no behavior change. The Conventional Commits `test:` type is correct per `.claude/rules/file-bridge-protocol.md` § Conventional Commits Type Discipline ("for test-only additions").

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

At implementation start (after Slice 8 + Slice 9 VERIFIED, plus Codex GO on this proposal): none beyond the standard implementation-start packet activation.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
