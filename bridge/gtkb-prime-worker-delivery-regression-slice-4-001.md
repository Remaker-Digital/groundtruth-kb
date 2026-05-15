# Implementation Proposal — Worker Delivery Regression Coverage (Slice 4 of 4)

bridge_kind: prime_implementation_proposal

## Summary

Land end-to-end regression coverage for the spawned-Prime-worker delivery
pipeline. The existing parity check confirms configuration parity
(`harness-parity: pass (harness=claude, role=prime-builder, PASS=25)`) but
does not prove that a spawned subprocess can mutate files. This slice adds
new tests in `platform_tests/` that:

1. Assert `_harness_command` produces the permission-mode flags from Slice 1.
2. Assert the worker-context branch in `owner-decision-tracker.py` (Slice 2)
   behaves correctly under both env-var states.
3. Assert the post-Stop retry pass (Slice 3) dispatches when the lock is
   cleared and skips when the lock is fresh.
4. Add a fixture-based integration test that spawns a real `claude -p`
   subprocess against a synthetic GO bridge entry and asserts the worker
   completes at least one Edit operation in an authorized path.

## Dependency on Slices 1, 2, 3

Implementation execution is gated on all three preceding slices reaching
`GO`. Each prior slice introduces a behavior contract that Slice 4 tests
verify. Codex may review Slice 4 in parallel; Prime will land tests in
sequence as each prior slice's GO arrives:

- Tests for Slice 1 contract → land alongside Slice 1 implementation.
- Tests for Slice 2 contract → land alongside Slice 2 implementation.
- Tests for Slice 3 contract → land alongside Slice 3 implementation.
- Integration test (subprocess spawn) → lands last, requires all three.

Slice 4 explicitly carries the integration test as a new file
(`platform_tests/scripts/test_cross_harness_bridge_trigger_worker_delivery.py`)
rather than amending existing test files, so the dependency graph stays
visible.

## Background

Memory `feedback_execute_upgrade_parameter_flag_pattern` (2026-05-10)
records a prior incident where Tier A NO-GO chain revealed isolation-gate
and manifest-write side-effects serially. The lesson: frontload discovery
by reading the source end-to-end before scoping each child proposal. Slice
4 is the structural application of that lesson to the worker-delivery
pipeline: comprehensive regression coverage so future slices don't NO-GO
chain through the same surface.

The integration test in particular addresses an explicit gap noted in the
S350 owner observation: "The parity checker reports PASS, but it does not
currently prove that spawned subprocesses can mutate files."

## Scope (Slice 4 of 4)

In scope:

1. **Slice 1 contract tests** (specified in `gtkb-prime-worker-permission-profile-slice-1-001.md`, strengthened here to address weak-assertion concerns):
   - `test_harness_command_claude_has_acceptedits_permission_mode`: asserts `--permission-mode acceptEdits` appears in the returned list (positional pair: flag + value).
   - `test_harness_command_claude_allowed_tools_includes_required_authoring_tools`: parses the `--allowed-tools` value and asserts the resulting tool-set is a superset of `{Read, Edit, Write, Glob, Grep, Bash, TodoWrite, NotebookEdit}`. Non-empty alone is insufficient.
   - `test_harness_command_claude_allowed_tools_excludes_interactive_and_network_tools`: parses the `--allowed-tools` value and asserts the resulting tool-set is disjoint from `{AskUserQuestion, WebFetch, WebSearch}` and contains no string starting with `mcp__`.
   - `test_harness_command_codex_unchanged`: asserts the `codex` target returns the unchanged command `["codex", "exec", prompt, "--cd", str(project_root)]`. No permission-mode flag, no allowed-tools flag.
   - `test_harness_command_preserves_init_keyword_first_line`: asserts the prompt's first line matches `^::init gtkb (pb|lo)$` after permission flags are added.
   - `test_harness_command_permission_flags_only_in_claude_branch`: explicit cross-check that `--permission-mode` and `--allowed-tools` appear ONLY when `target.command_handle == "claude"`, never when `target.command_handle == "codex"`.
2. **Slice 2 contract tests** (specified in `gtkb-prime-worker-context-aware-auq-slice-2-001.md`):
   - `test_stop_handler_worker_context_writes_requires_owner_decision_json`
   - `test_stop_handler_worker_context_still_appends_durable_pending`
   - `test_stop_handler_owner_context_unchanged_block_decision`
   - `test_dispatch_prompt_contains_worker_context_interactive_tools_unavailable_paragraph`
3. **Slice 3 contract tests** (specified in `gtkb-prime-worker-post-stop-dispatch-retry-slice-3-001.md`):
   - `test_stop_event_retry_dispatches_when_lock_cleared`
   - `test_stop_event_retry_skips_when_lock_still_fresh`
   - `test_normal_pass_unaffected_by_retry_logic`
   - `test_retry_pass_failures_recorded_to_dispatch_failures_jsonl`
4. **New integration test** (Slice-4-specific):
   - `test_spawned_claude_worker_can_edit_authorized_file`: spawn `claude -p`
     subprocess against a fixture project containing a synthetic GO bridge
     entry. Assert: (a) subprocess exits within timeout, (b) the
     authorized-path file in the fixture is mutated, (c) stdout/stderr
     contain no permission-denial messages.

Out of scope for Slice 4:

- Doctor check integration (separate follow-on if integration test reveals
  gaps in the doctor surface).
- CI workflow registration (separate scaffold-test follow-on).
- Per-bridge-thread lock tests (Slice 3 uses coarse locks; per-thread is
  separate follow-on).

## In-Root Placement Evidence

All target paths and runtime artifacts in-root under `E:\GT-KB`:

- `E:\GT-KB\platform_tests\scripts\test_cross_harness_bridge_trigger.py` — extended with Slice 1 + Slice 3 contract tests.
- `E:\GT-KB\platform_tests\hooks\test_owner_decision_tracker.py` (if present) — extended with Slice 2 contract tests.
- `E:\GT-KB\platform_tests\scripts\test_cross_harness_bridge_trigger_worker_delivery.py` — new integration test file.
- `E:\GT-KB\.gtkb-state\cross-harness-trigger\dispatch-runs\*.log` — integration test reads dispatch-run logs (in-root).

No `applications/` paths. No paths outside `E:\GT-KB`. Per `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`, all target paths and runtime artifacts are within the GT-KB platform root.

## Specification Links

- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived from linked specs; this slice IS the verification surface.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — file bridge authority; tests preserve workflow state invariants.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` — init-keyword first-line invariant tested.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` — keyword authority tested.
- `SPEC-AUQ-POLICY-ENGINE-001` — engine behavior covered by Slice 2 tests.
- `SPEC-AUQ-NO-LLM-CLASSIFIER-001` — deterministic-only behavior covered by all hook tests.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposal cites governing specs.
- `.claude/rules/bridge-essential.md` § Active-Session Suppression — suppression contract covered by Slice 3 retry tests.
- `.claude/rules/bridge-essential.md` § Bridge Dispatch Enablement Contract — dispatch contract covered by Slice 1 + 3 tests.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol invariants.
- `.claude/rules/prime-builder-role.md` — owner-context AUQ rule covered by Slice 2 regression test.
- `.claude/rules/codex-review-gate.md` — review gate; this slice IS the testing layer the gate requires.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — application/root placement boundary; this proposal does not touch `applications/` paths or modify root-boundary behavior. Cited per path-match acknowledgement (the proposal references `.claude/rules/file-bridge-protocol.md`); no modification proposed.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — artifact-oriented governance discipline (advisory). The change adds test artifacts that preserve the spec-derived verification surface mandated by `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — artifact-oriented development (advisory). Tests cite specifications; the integration test fixture cites parent slice proposals.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — artifact lifecycle states (advisory). The proposal lifecycle is NEW → (GO/NO-GO) → VERIFIED per the file-bridge-protocol contract.

## Prior Deliberations

- All sibling slices (1, 2, 3) — Slice 4 is the verification surface for their behavior contracts.
- `bridge/gtkb-cross-harness-trigger-active-session-suppression-001-008.md` VERIFIED — suppression state machine; Slice 4 tests preserve.
- `bridge/gtkb-bridge-poller-event-driven-replacement-003.md` GO at `-004` — event-driven trigger; Slice 4 tests preserve.
- Memory `feedback_execute_upgrade_parameter_flag_pattern` — the regression-coverage lesson this slice embodies.

## Owner Decisions / Input

Owner AskUserQuestion answer in S350 (2026-05-14): "Which slicing strategy for the Prime-worker-delivery fix?" → **4-slice sequence (recommended)**. Slice 4 = regression coverage.

Owner directive in S350 (2026-05-14): "Please draft Slices 2-4 in parallel."

## Requirement Sufficiency

Existing requirements sufficient. `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` requires verification derived from linked specifications and executed against the implementation. Slice 4 IS the executed-against-implementation surface; no new requirement is introduced, only the test artifacts that the existing requirement already mandates.

## target_paths

- `platform_tests/scripts/test_cross_harness_bridge_trigger.py` (Slice 1 + Slice 3 contract tests added)
- `platform_tests/hooks/test_owner_decision_tracker.py` if it exists, else co-located test file (Slice 2 contract tests added)
- `platform_tests/scripts/test_cross_harness_bridge_trigger_worker_delivery.py` (new file; integration test)

## Implementation Plan

Each contract test is specified in its parent slice's proposal; Slice 4 lands the test code per parent-slice specifications when each parent slice's GO arrives. The integration test:

1. **Fixture setup**: create a temp project with `groundtruth.toml`, a minimal `bridge/INDEX.md` containing one synthetic GO entry, the corresponding `bridge/<name>-002.md` GO file, and a target source file the worker should edit per the GO's `target_paths`.
2. **Harness state**: write `harness-state/role-assignments.json` and `harness-state/harness-identities.json` declaring a single Claude harness as prime-builder.
3. **Spawn subprocess**: invoke `python scripts/cross_harness_bridge_trigger.py --project-root <fixture> --state-dir <fixture>/.gtkb-state/cross-harness-trigger` with `--dry-run=False` and capture stdout/stderr.
4. **Wait + assert**: poll the target file for the expected mutation (with timeout ~30 seconds — Claude subprocess startup + Edit takes time). Assert mutation occurred. Assert no permission-denied strings in subprocess output.
5. **Cleanup**: kill any orphaned subprocess on timeout failure to prevent test-runner contamination.

The integration test is marked `@pytest.mark.slow` and skipped if the `claude` executable is not on PATH (so CI without the harness installed still passes).

## Spec-to-Test Mapping

- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` → all 13 tests (the slice IS the spec-derived verification surface).
- Each individual test maps to the spec citation listed in its parent-slice proposal.
- `test_spawned_claude_worker_can_edit_authorized_file` → integration test for the combined Slice 1 + Slice 2 + Slice 3 contract; cites all three sibling proposals.

## Risks

- **Integration test is slow and host-dependent**: spawning `claude -p` requires the harness binary on PATH and burns ~30 seconds per invocation. *Mitigation:* `@pytest.mark.slow`, skip if `which claude` fails, exclude from default test run (run via `pytest -m slow` or in a separate CI stage).
- **Integration test is non-deterministic** (LLM output variance): the test asserts file mutation, not specific content, so output variance doesn't fail the test. *Mitigation:* the synthetic GO bridge entry instructs the worker to perform a specific deterministic Edit (e.g., "change line 1 of target.py to `OK`") — the worker's interpretation of "make this edit" is reliable enough for a regression check.
- **Test fixture cleanup leaves orphaned subprocesses**: if the subprocess hangs, the test runner could leave it running. *Mitigation:* fixture uses `subprocess.Popen` with explicit `terminate()` + `kill()` on timeout, plus `pytest-timeout` if available.
- **CI without Claude harness fails the integration test**: covered by skip-if-missing-executable.

## Rollback

Remove all new test functions and the new integration test file. Test surface reverts to current state. No production-code rollback required (Slice 4 is test-only).

## Verification Procedure

1. Run `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/hooks/test_owner_decision_tracker.py -q --tb=short` — all 12 unit-contract tests pass.
2. Run `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger_worker_delivery.py -q --tb=short -m slow` — integration test passes when Claude harness is on PATH; skips otherwise.
3. Run `python -m pytest -q --tb=short -m "not slow"` — full default suite (excluding slow tests) passes with no regressions.

## Acceptance Criteria

- All 12 unit-contract tests cover the behavior surfaces specified in Slices 1, 2, and 3.
- Integration test exists, passes when harness is on PATH, skips cleanly otherwise.
- No new dependencies introduced (uses existing pytest fixtures + subprocess module).
- All preflights pass for this proposal.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
