NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Defect-Fix Proposal - Flaky: Claude SessionStart dispatcher tests degrade on startup-service freshness-contract validation under timing pressure

bridge_kind: prime_proposal
Document: gtkb-flaky-claude-sessionstart-dispatcher-tests
Version: 001 (DRAFT; non-dispatchable)
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3456

target_paths: ["platform_tests/scripts/test_claude_session_start_dispatcher.py"]

Defect-fix proposal focused on reproducing, correcting, and verifying a fault.

## Claim

`platform_tests/scripts/test_claude_session_start_dispatcher.py::test_envelope_contains_governance_disclosure` and `::test_envelope_contains_token_budget_content` are flaky: they intermittently fail with zero code change. Both tests subprocess-launch the real SessionStart dispatcher (`_run_dispatcher` -> `.claude/hooks/session_start_dispatch.py` -> `scripts/session_start_dispatch_core.py::main`), which in turn subprocess-launches the canonical startup service (`scripts/session_self_initialization.py --emit-startup-service-payload --fast-hook`). Under timing/load pressure the dispatcher's `_valid_session_start_payload()` returns `False` (or the nested subprocess is slow), so `main()` takes the degraded-banner fallback branch (`_fallback_context`, "GroundTruth-KB Startup Service Degraded"). The degraded banner deliberately omits "Programmatic Startup Payload", "Role being assumed:", and "Token measurement status:", so the two content-asserting tests fail. The degradation is timing/load-sensitive, not a correctness defect in the dispatcher or the startup service: the standalone service produces a valid fresh payload, and the dispatcher's fail-soft degraded-banner branch is intended behavior (separately and deterministically covered by `test_dispatcher_fallback_on_broken_startup_service`). The defect is that these two tests couple a content assertion to a heavy, timing-dependent nested-subprocess success path that is legitimately allowed to degrade.

## Defect / Reproduction

Observed flake (origin of WI-3456): across two consecutive runs with no code change, run 1 had both tests fail; run 2 had `test_envelope_contains_governance_disclosure` pass and `test_envelope_contains_token_budget_content` fail. The surfacing context's own SessionStart banner also degraded with the identical reason ("startup service freshness contract validation failed") at the same time, confirming the trigger is timing/load on the nested subprocess, not the code under test. The behavior was surfaced during Slice 1 of PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE (WI-3453) but is NOT caused by that change (Slice 1 edits only the success-branch cache writer; the Codex dispatcher with a byte-identical edit passes its full suite).

Reproduction (logical): when `scripts/session_start_dispatch_core.py::main` runs `subprocess.run(... session_self_initialization.py ...)` and either (a) the nested process is slow enough relative to the dispatcher subprocess timeout, or (b) `_valid_session_start_payload(process.stdout, request_started_at)` returns `False` for any freshness-contract reason, `main()` falls through to `print(_dump_payload(_session_start_payload(_fallback_context(reason))))`. The emitted `additionalContext` is then the degraded banner, which lacks the three substrings the two tests assert. Expected: the two flaky tests must assert their content against the deterministic success-branch payload (the dispatcher's documented contract for the validated startup-service path) rather than against a live, timing-dependent nested-subprocess invocation.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `platform_tests/scripts/test_claude_session_start_dispatcher.py`.

## Specification Links

- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` - governs the token-budget content (`Token measurement status:`, token-consumption guidance) that `test_envelope_contains_token_budget_content` asserts; the fix preserves this assertion but pins it to the deterministic success-branch payload so the contract is verified reliably rather than flakily.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this defect fix is filed and verified through the bridge protocol with a `GO` before implementation; the change is scoped, audit-trailed, and bridge-governed.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the fix preserves the durable test artifact's intent (verifying the governance-disclosure and token-budget startup contract) while removing the timing coupling, keeping the artifact a reliable verification record.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all governing specs and protected behaviors relevant to the SessionStart startup contract and the affected tests (mandatory linkage).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan below derives each repaired test from the spec clause it exercises (`PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001`, `DCL-SESSION-STARTUP-TOKEN-BUDGET-001`) plus a flake-elimination regression assertion (mandatory).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries the Project Authorization / Project / Work Item linkage lines (PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING / PROJECT-GTKB-RELIABILITY-FIXES / WI-3456) as required.
- `SPEC-AUQ-POLICY-ENGINE-001` - not directly exercised by this test-only change; cited for completeness because the SessionStart startup payload surfaces owner-facing governance/AUQ context, and the fix must not alter that owner-decision surface. No AUQ behavior is added, removed, or modified.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the change is confined to a GT-KB platform test under `platform_tests/scripts/`; no application/adopter surface is touched and no placement boundary is crossed. The test continues to assert diagnostics land under `E:\GT-KB\.claude\hooks\`.
- `GOV-STANDING-BACKLOG-001` - WI-3456 is a standing-backlog work item under PROJECT-GTKB-RELIABILITY-FIXES.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the SessionStart dispatcher is the harness-neutral core shared by the Claude and Codex wrappers; this Claude-side test fix preserves the existing envelope-parity assertions (`test_envelope_shape_parity_with_codex`) and does not change the shared core, so harness parity is unaffected.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the repaired test remains an artifact-backed verification of the startup contract; reliability is achieved by deterministic stubbing, not by deleting or weakening coverage.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - repairing a flaky test (a quality/maintenance lifecycle trigger) keeps the test artifact aligned with its verification purpose; no new artifact type is created.

## Prior Deliberations

- `DELIB-20264345` - Loyal Opposition Review, GTKB MemBase Effective Use Recovery Slice A Event Surfacer - touches the `_write_session_start_json` side-channel emitted on the startup-service success path the dispatcher consumes; relevant context for the success-branch payload shape this fix pins against.
- `DELIB-2332` / `DELIB-20264929` - Loyal Opposition Verification Verdicts, Startup Enhancements P2 Freshness Contract - established the `startupFreshness` contract and `_valid_session_start_payload` ordering checks whose timing-sensitivity under load is the proximate cause of the degraded-banner branch this defect surfaces; the fix does not change that contract, it removes the test's dependence on the live nested subprocess.
- `DELIB-2292` - Loyal Opposition Review, Startup Disclosure Relay Truncation Fix - established the in-process `main()` + stubbed `subprocess.run` test pattern (already used by `test_normal_startup_relay_cache_uses_startup_disclosure_field`) that this fix reuses to make the two flaky tests deterministic.
- WI-4564 (`bridge/gtkb-wi4564-startup-service-timeout-and-fanout-006.md`, VERIFIED) - the directly-relevant prior reliability fix that raised the dispatcher subprocess timeout to a budget-aligned `STARTUP_SERVICE_TIMEOUT_SECONDS = 150.0` default and reduced startup subprocess fan-out; it reduced but did not eliminate the timing flake for these two content-asserting tests, which is why this test-determinism fix is needed.
- `DELIB-20265457` - owner decision authorizing the PROJECT-GTKB-RELIABILITY-FIXES proposal batch (this WI is in scope).

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (`DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) - WI-3456 is origin=defect (a flaky test), single-concern, test-only, introduces no new public surface and no new/revised spec, and is bounded to ~1 test file (well under the reliability fast-lane size guide), so it is covered by the reliability fast-lane standing authorization through active project membership.
- `DELIB-20265457` - owner AUQ (2026-06-21) directing authoring of NEW proposals for all open PROJECT-GTKB-RELIABILITY-FIXES work items; WI-3456 (P3) is in that batch scope.

## Requirement Sufficiency

Existing requirements sufficient. `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` and `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` already establish the required governance-disclosure and token-budget content of the SessionStart startup payload; the dispatcher's fail-soft degraded-banner branch is the established, separately-tested behavior. This fix only repairs the two tests so they verify those existing requirements deterministically on the success-branch contract. No new or revised requirement/specification is introduced.

## Proposed Scope

Test-only, defect-removal change in `platform_tests/scripts/test_claude_session_start_dispatcher.py`. No production code (dispatcher core, hook wrapper, or startup service) is modified.

1. Convert `test_envelope_contains_governance_disclosure` and `test_envelope_contains_token_budget_content` from live subprocess invocation (`_run_dispatcher()`) to the deterministic in-process pattern already established by `test_normal_startup_relay_cache_uses_startup_disclosure_field` (line ~544): load the dispatcher hook via `_load_claude_hook_isolated(...)`, monkeypatch `module.subprocess.run` to return a `CompletedProcess` whose stdout is a well-formed success-branch startup-service payload (valid `hookSpecificOutput` + `startupFreshness` that passes `_valid_session_start_payload` for the dispatcher's `request_started_at`), then call `module.main()` and assert the three required substrings on the emitted `additionalContext`.
   - The stubbed `additionalContext` carries "Programmatic Startup Payload", "Role being assumed:", "Role mapping source:", "harness-state/harness-registry.json", "Token measurement status:", and token-consumption guidance, so the existing content assertions are preserved verbatim.
   - The stub builds `startupFreshness` with timestamps ordered relative to the dispatcher's `request_started_at` (use the dispatcher's own `_now_iso`/`STARTUP_FRESHNESS_CONTRACT_VERSION` and `report_origin="in_memory_model_render"`, `validation.startup_payload_fresh=True`, `validation.status="fresh"`) so `_valid_session_start_payload` returns `True` deterministically and `main()` takes the success branch every time.
   - Use `monkeypatch.delenv` for `GTKB_BRIDGE_POLLER_RUN_ID` and `GTKB_BRIDGE_DISPATCH_KEYWORD` (and `monkeypatch.setattr(module, "OUT_DIR", tmp_path)`) so the tests are hermetic in bridge auto-dispatched review sessions and do not write into the live `.claude/hooks/` dir, matching the hermeticity contract already enforced by `_run_dispatcher` and the line-544 test.
2. Add one regression test, `test_envelope_content_not_subject_to_degraded_banner_flake`, that drives `main()` with the SAME deterministic success-branch stub and asserts the emitted `additionalContext` does NOT contain "GroundTruth-KB Startup Service Degraded" — pinning that, given a valid startup-service payload, the content path is taken (the flake-elimination invariant).

Out of scope (explicitly): relaxing the `startupFreshness` ordering tolerance, raising the dispatcher subprocess timeout further (WI-4564 already set 150 s), or adding production retry logic to the degraded-banner branch. Those are behavior/contract changes that would require a new requirement and are not part of this fast-lane test-determinism defect fix. The end-to-end live-subprocess smoke path remains covered by `test_dispatcher_emits_session_start_envelope` and `test_envelope_shape_parity_with_codex`, which assert only structural (not flaky content) properties.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` (role/governance/role-mapping disclosure present) | `test_envelope_contains_governance_disclosure` (repaired) | Driving `main()` with a deterministic success-branch startup-service payload yields `additionalContext` containing "Programmatic Startup Payload", "Role being assumed:", "Role mapping source:", and "harness-state/harness-registry.json" — on every run. |
| `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` (token-budget content present) | `test_envelope_contains_token_budget_content` (repaired) | Driving `main()` with the same deterministic payload yields `additionalContext` containing "Token measurement status:" and token-consumption guidance — on every run. |
| `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` / `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` (success path is taken for a valid payload; flake elimination) | `test_envelope_content_not_subject_to_degraded_banner_flake` (new) | Given a valid success-branch startup-service payload, the emitted `additionalContext` does NOT contain "GroundTruth-KB Startup Service Degraded"; `main()` returns 0. |

Execution commands:
- `python -m pytest platform_tests/scripts/test_claude_session_start_dispatcher.py -q --tb=short`
- `python -m ruff check platform_tests/scripts/test_claude_session_start_dispatcher.py`
- `python -m ruff format --check platform_tests/scripts/test_claude_session_start_dispatcher.py`

(Optional flake-soak evidence for the report: run the two repaired tests repeatedly, e.g. `python -m pytest platform_tests/scripts/test_claude_session_start_dispatcher.py -q -k "governance_disclosure or token_budget" --count 20` if `pytest-repeat` is available, to show zero failures across N runs.)

## Acceptance Criteria

1. `test_envelope_contains_governance_disclosure` and `test_envelope_contains_token_budget_content` no longer depend on a live nested startup-service subprocess; they drive the dispatcher `main()` in-process against a deterministic success-branch payload and pass on every run.
2. The three required content substrings remain asserted (no coverage weakening); the new regression test pins that a valid payload never yields the degraded banner.
3. No production file is modified; the existing live-subprocess structural tests and the degraded-banner fallback test (`test_dispatcher_fallback_on_broken_startup_service`) remain unchanged and pass.
4. `python -m pytest platform_tests/scripts/test_claude_session_start_dispatcher.py -q --tb=short` is green; `ruff check` and `ruff format --check` are clean on the changed file.

## Risks / Rollback

- Risk: stubbing `subprocess.run` could mask a real regression in the live startup-service success path. Mitigation: the live end-to-end path is still exercised structurally by `test_dispatcher_emits_session_start_envelope`, `test_envelope_shape_parity_with_codex`, and `test_diagnostic_files_land_in_claude_hooks_dir`; the harness-parity import path remains covered by `test_harness_parity_import_repaired`. Only the two flaky CONTENT assertions move to the deterministic path.
- Risk: the stubbed `startupFreshness` could drift from the real contract and silently pass. Mitigation: the stub is built from the dispatcher module's own `STARTUP_FRESHNESS_CONTRACT_VERSION` and timestamp helpers and is validated by the dispatcher's own `_valid_session_start_payload`, so a contract change that breaks production validation also breaks the stub.
- Rollback: revert the test file to its prior revision; the change is confined to two repaired tests plus one added test, with no migration and no production impact.

## Files Expected To Change

- `platform_tests/scripts/test_claude_session_start_dispatcher.py`

## Recommended Commit Type

`fix`
