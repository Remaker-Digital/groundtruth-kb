NEW

bridge_kind: implementation_report
Document: gtkb-lo-dispatch-pipeline-repair
Version: 003
Author: Prime Builder (Codex, harness A)
Date: 2026-06-19 UTC
created_at: 2026-06-19T20:41:00Z
Responds to: bridge/gtkb-lo-dispatch-pipeline-repair-002.md
Recommended commit type: fix
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 2026-06-19T20-32-33Z-prime-builder-A-b54192
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex API session; Prime Builder role; approval_policy=never; workspace-write; PowerShell shell

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4679

target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py"]
implementation_scope: source
requires_verification: true
kb_mutation_in_scope: false

## Implementation Claim

Implemented the approved WI-4679 repair for the Loyal Opposition dispatch retry/fallback path.

The change stays within the GO-authorized target paths:

- `scripts/cross_harness_bridge_trigger.py`
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py`

No retired poller code, dispatcher routing policy, harness precedence, project authorization behavior, bridge status semantics, credential state, or unrelated dirty-worktree files were changed for this implementation.

## Files Changed

Recommended commit type: `fix`

| Path | Change summary |
|---|---|
| `scripts/cross_harness_bridge_trigger.py` | Added fatal Gemini tier markers classified as `harness_unavailable_tier`; added `NON_RETRYABLE_WORKER_FAILURE_CLASSES`; cleared `last_dispatched_signature`, legacy `signature`, and `last_suppressed_signature` when a launched dispatch failure is processed while preserving `last_launch.signature` for retry/backoff evidence; changed provider backoff selection to use the failed launch signature and retry/circuit timing so same-batch retryable failures are demoted only while the retry window or circuit breaker applies; kept non-retryable tier failures demoted even when dispatch dedupe signatures have already been cleared. |
| `platform_tests/scripts/test_cross_harness_bridge_trigger.py` | Added regression coverage for processed failure dedupe clearing, same-batch retry after the retry window, and Gemini `IneligibleTierError` fallthrough with cleared signatures; updated existing fallback assertions to include `backoff_source` evidence for retry-delay skips. |

## Linked Specifications Carried Forward

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `DCL-DISPATCH-ENVELOPE-RULES-001`
- `SPEC-TAFE-R4`
- `REQ-HARNESS-REGISTRY-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `GOV-RELIABILITY-FAST-LANE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Spec-To-Test Mapping

| Specification | Implementation evidence | Executed verification |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Work began only after live bridge state showed latest `GO` at `bridge/gtkb-lo-dispatch-pipeline-repair-002.md`; implementation claim and authorization packet were acquired for `gtkb-lo-dispatch-pipeline-repair`. | `groundtruth-kb/.venv/Scripts/gt.exe bridge show gtkb-lo-dispatch-pipeline-repair --json`; `groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-lo-dispatch-pipeline-repair`. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Retry/fallback state now distinguishes failed-launch batch signature from completed-dispatch dedupe signature, so dispatch health can recover after retry windows. | `test_failed_launch_exit_processing_clears_dispatch_dedupe_signals`; `test_lo_provider_failure_backoff_retries_preferred_after_retry_window`; full focused pytest file. |
| `DCL-DISPATCH-ENVELOPE-RULES-001` | Fallback skip evidence now records explicit `backoff_source` while preserving target selection order and falling through only when a candidate is actively demoted. | `test_lo_provider_failure_backoff_falls_back_after_max_turn_marker`; `test_lo_ordered_fallback_prefers_lowest_precedence_ready_target`; full focused pytest file. |
| `SPEC-TAFE-R4` | TAFE-backed dispatch state fields are updated so `last_dispatched_signature` and legacy `signature` no longer represent failed launches as completed dispatches. | `test_failed_launch_exit_processing_clears_dispatch_dedupe_signals`; full focused pytest file. |
| `REQ-HARNESS-REGISTRY-001` | A fatal Gemini tier failure for harness `C` is treated as candidate-specific unavailability and does not block dispatch to next eligible LO harness `F`. | `test_lo_gemini_ineligible_tier_demotes_candidate_with_cleared_signature`; full focused pytest file. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Cross-harness fallback behavior remains in the event-driven trigger and does not restore or depend on retired poller substrates. | Full focused pytest file plus scoped diff inspection. |
| `GOV-RELIABILITY-FAST-LANE-001` | The implementation is a bounded reliability fix under WI-4679 and changes only the approved source/test paths. | Scoped `git diff -- scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_bridge_trigger.py`; ruff checks. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries forward every specification linked in the approved proposal and maps each to verification evidence. | This `Spec-To-Test Mapping` section. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Report preserves `Project Authorization`, `Project`, `Work Item`, and exact `target_paths` metadata. | Bridge helper filing validation for this report. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Regression tests directly cover both approved defect classes and the report records observed command results. | Focused pytest, ruff lint, and ruff format commands below. |
| `GOV-STANDING-BACKLOG-001` | Work is tied to `WI-4679` and does not introduce a parallel backlog authority. | Implementation authorization packet returned `work_item_id: WI-4679`. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Bridge audit trail is append-only and the implementation report preserves durable evidence for the repair. | This post-implementation report filed as next version `-003`. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | The implementation crosses the report threshold and is recorded as a status-bearing bridge artifact. | This report and bridge helper filing. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Governance evidence is explicit in the bridge chain rather than transient chat-only state. | This report and command evidence below. |

## Verification Commands

1. Command:

   ```powershell
   $tmp='.gtkb-state\pytest-runs\wi4679-envtmp-20260619T2039'; New-Item -ItemType Directory -Force -Path $tmp | Out-Null; $full=(Resolve-Path $tmp).Path; $env:TMP=$full; $env:TEMP=$full; $env:GTKB_HARNESS_NAME='claude'; groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short
   ```

   Observed result: PASS, `91 passed, 2 warnings in 7.17s`.

   Notes: An earlier run without root-contained `TMP`/`TEMP` failed before test execution with `PermissionError: [WinError 5] Access is denied: 'C:\\Users\\micha\\AppData\\Local\\Temp\\pytest-of-micha'`. The passing rerun keeps pytest temp under the GT-KB root boundary and uses the same pytest target/options.

2. Command:

   ```powershell
   groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_bridge_trigger.py
   ```

   Observed result: PASS, `All checks passed!`.

3. Command:

   ```powershell
   groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_bridge_trigger.py
   ```

   Observed result: PASS, `2 files already formatted`.

## Acceptance Status

| Acceptance criterion from GO | Status | Evidence |
|---|---|---|
| Clear or neutralize both `last_dispatched_signature` and legacy `signature` on launched dispatch failure. | PASS | Failure exit processing now clears both fields; `test_failed_launch_exit_processing_clears_dispatch_dedupe_signals` asserts both are `None` while `last_launch.signature` is preserved. |
| Preserve retry-delay and circuit-breaker semantics; do not dispatch repeatedly on every trigger while a provider is in active backoff. | PASS | Existing retry-delay test still passes; `test_lo_provider_failure_backoff_falls_back_after_max_turn_marker` now asserts explicit `backoff_source: retry_delay_enforced`. |
| Same-signature failed dispatch retries once the retry/circuit window permits it. | PASS | `test_lo_provider_failure_backoff_retries_preferred_after_retry_window` proves preferred target `D` is selected again after the window rather than permanently falling through to `F`. |
| Classify Gemini `IneligibleTierError` / tier deprecation as non-retryable harness-unavailable and fall through. | PASS | `test_lo_gemini_ineligible_tier_demotes_candidate_with_cleared_signature` proves candidate `C` is demoted with `failure_class: harness_unavailable_tier` and candidate `F` is selected. |
| Preserve auditable skip/failure evidence. | PASS | Skip evidence carries `failure_class` and `backoff_source`; failure JSONL evidence is still recorded through `_record_dispatch_failure`. |

## Risk / Rollback

Risk remains confined to dispatch retry/fallback semantics in `scripts/cross_harness_bridge_trigger.py`.

Rollback is a single revert of the two implementation files. The bridge audit chain remains append-only.
