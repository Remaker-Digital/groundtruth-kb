NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: keep-working-20260607T0728Z
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Keep Working PB automation; high autonomy
author_metadata_source: Codex automation context

bridge_kind: implementation_report
Document: gtkb-ollama-dispatch-stall-retry-cap
Version: 004
Date: 2026-06-07 UTC
Responds to: bridge/gtkb-ollama-dispatch-stall-retry-cap-002.md
Supersedes: bridge/gtkb-ollama-dispatch-stall-retry-cap-003.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4388

# Post-Implementation Report - Ollama Dispatch Stall Retry Cap

## Implementation Claim

Implemented the GO-approved reliability hotfix for `gtkb-ollama-dispatch-stall-retry-cap` and superseded the earlier `-003` report because final regression coverage and verification changed after that report was filed.

The dispatcher now:

- preserves prior `last_launch` metadata across unchanged-signature runs;
- inspects prior worker stdout/stderr log tails for fatal markers before treating a same-signature launch as healthy `unchanged`;
- records durable `previous_launch_failed` evidence when a fatal marker is found, then permits retry;
- caps Ollama Loyal Opposition dispatch to one selected bridge item while preserving `DEFAULT_MAX_ITEMS = 2` for other dispatch targets;
- adds mandatory Loyal Opposition verdict preflight instructions to the generated dispatch prompt;
- strips inherited `GTKB_IMPLEMENTATION_AUTH_*` variables before spawning a child, then re-adds fresh values only when the current Prime spawn minted implementation authorization packets.

The implementation remains inside the two GO-approved target paths.

## Files Changed

Recommended commit type: `fix:`

Target-path diff scope:

```text
platform_tests/scripts/test_cross_harness_bridge_trigger.py
scripts/cross_harness_bridge_trigger.py
```

Observed target-path numstat:

```text
217     0       platform_tests/scripts/test_cross_harness_bridge_trigger.py
162     64      scripts/cross_harness_bridge_trigger.py
```

Known shared-file overlap: the GO verdict noted that `platform_tests/scripts/test_cross_harness_bridge_trigger.py` already contained unrelated local edits. This report covers only the hotfix changes in that file: implementation-auth env scrubbing assertions, prior fatal worker retry, Ollama one-item cap, and mandatory LO preflight prompt assertions.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the bridge INDEX remains the authoritative lifecycle surface for this implementation report and verification request.
- `GOV-STANDING-BACKLOG-001` - `WI-4388` remains the tracked reliability work item for this bridge thread.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the defect, implementation evidence, and residual risk are preserved in this bridge artifact.
- `GOV-RELIABILITY-FAST-LANE-001` - this is a scoped reliability fix under the standing fast-lane authorization.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the reliability correction proceeded through proposal, GO, implementation report, and counterpart verification lifecycle artifacts.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - failed worker evidence is surfaced rather than hidden as healthy no-op liveness.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all changed files and evidence stay inside `E:\GT-KB`.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the live stalled LO dispatch queue and GO verdict triggered this implementation report lifecycle step.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation follows the approved GO proposal and authorization packet.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - this report maps linked specs to executed tests and observed results.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` - Ollama dispatch readiness and bridge-review tool availability remain intact.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - owner decision establishing the reliability fast-lane while preserving bridge review, work-item tracking, and safety gates.
- `DELIB-20260909` - compressed VERIFIED bridge thread for prior `gtkb-ollama-dispatch-failure-hardening`; relevant predecessor baseline.
- `DELIB-20260897` - compressed VERIFIED bridge thread for `gtkb-ollama-integration-phase-2-dispatch`; prior dispatch wiring baseline.
- `DELIB-2509` - warning against using the reliability PAUTH for non-defect feature work; not blocking because `WI-4388` is a P1 bridge-dispatch defect.
- `bridge/gtkb-ollama-dispatch-stall-retry-cap-002.md` - GO verdict authorizing this implementation scope.

## Owner Decisions / Input

- Owner reply in the originating thread on 2026-06-07: `AUTHORIZE HOTFIX PATH`.
- Carried-forward authorization: `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`.
- Active work item: `WI-4388`.
- No new owner decision is required for this implementation report.

## Code Quality Baseline

| Rule ID | Applies? | Evidence |
|---|---:|---|
| CQ-SECRETS-001 | Yes | No credential-shaped fixtures or secrets added; implementation auth env names are scrubbed, not values persisted. |
| CQ-PATHS-001 | Yes | Scoped diff names only the two GO-approved target paths. |
| CQ-COMPLEXITY-001 | Yes | Added small helpers for fatal marker detection and target-specific cap selection; no dispatcher refactor. |
| CQ-CONSTANTS-001 | Yes | Constants declare the Ollama cap, fatal markers, log read limit, and implementation-auth env names. |
| CQ-SECURITY-001 | Yes | Guard-denial markers are classified as retry evidence; guard behavior is not bypassed. |
| CQ-DOCS-001 | N/A | Internal dispatcher behavior; this bridge report is the durable documentation. |
| CQ-TESTS-001 | Yes | Added targeted regression coverage and ran the trigger test suite. |
| CQ-LOGGING-001 | Yes | `previous_launch_failed` records are appended to `dispatch-failures.jsonl` with marker and prior-launch evidence. |
| CQ-VERIFICATION-001 | Yes | Pytest, py_compile, ruff lint, ruff format, readiness, diagnose, preflights, and scoped diff checks were executed. |

## Spec-To-Test Mapping

| Specification | Verification |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This report is filed as the latest `NEW` bridge version and `show_thread_bridge.py` / applicability preflight are run against the operative thread. |
| `GOV-STANDING-BACKLOG-001` | Implementation is tied to `WI-4388` under the active reliability project authorization. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | This report records implementation claim, files changed, commands, observed results, risk, owner authorization, and rollback. |
| `GOV-RELIABILITY-FAST-LANE-001` | Scope stayed inside the approved dispatcher/test target paths for the active P1 reliability item. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | This `-004` report supersedes stale `-003` evidence rather than editing history in place. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Fatal prior worker output now records `previous_launch_failed` evidence and retries rather than masking the stall as `unchanged`. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Changed files are `scripts/cross_harness_bridge_trigger.py` and `platform_tests/scripts/test_cross_harness_bridge_trigger.py`, both under `E:\GT-KB`. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Live stalled dispatch evidence and the GO verdict are preserved through this implementation-report lifecycle entry. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Implementation authorization packet `sha256:9b3983850a4180fd7738f0baf7acdb2e88e01c7bc4ec54746a696e92bb46bec1` was issued from the live GO thread. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused tests cover fatal-marker retry, Ollama one-item cap, prompt preflight wording, and auth-env scrubbing. |
| `DCL-OLLAMA-TOOL-PARITY-GATE-001` | `verify_ollama_dispatch.py --readiness-only` reported ready recipient `D`, route `qwen3-coder-next-cloud`, model `qwen3-coder-next:cloud`, and no missing tools. |

## Commands And Observed Results

```text
groundtruth-kb\.venv\Scripts\python.exe -m py_compile scripts\cross_harness_bridge_trigger.py platform_tests\scripts\test_cross_harness_bridge_trigger.py
Result: pass.
```

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_cross_harness_bridge_trigger.py -q --tb=short
Result: 66 passed, 1 warning in 7.60s.
Warning: pytest cache provider could not create one cache path due WinError 183.
```

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\cross_harness_bridge_trigger.py platform_tests\scripts\test_cross_harness_bridge_trigger.py
Result: All checks passed.
```

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\cross_harness_bridge_trigger.py platform_tests\scripts\test_cross_harness_bridge_trigger.py
Result: 2 files already formatted.
```

```text
python scripts\verify_ollama_dispatch.py --readiness-only --json --project-root E:\GT-KB
Result: ready=true, recipient=D, route_key=qwen3-coder-next-cloud, model_id=qwen3-coder-next:cloud, missing_tools=[].
```

```text
python scripts\cross_harness_bridge_trigger.py --project-root E:\GT-KB --state-dir E:\GT-KB\.gtkb-state\bridge-poller --diagnose --include-rotated-failures
Result: HEALTHY. prime-builder pending=0 selected=0. loyal-opposition pending=11 selected=1. Recent failures include fatal_worker_output_marker records.
```

```text
git diff --name-only -- scripts\cross_harness_bridge_trigger.py platform_tests\scripts\test_cross_harness_bridge_trigger.py
Result:
platform_tests/scripts/test_cross_harness_bridge_trigger.py
scripts/cross_harness_bridge_trigger.py
```

```text
git diff --numstat -- scripts\cross_harness_bridge_trigger.py platform_tests\scripts\test_cross_harness_bridge_trigger.py
Result:
217     0       platform_tests/scripts/test_cross_harness_bridge_trigger.py
162     64      scripts/cross_harness_bridge_trigger.py
```

Environment note: `python -m pytest ...` with the default interpreter failed because `pytest` is not installed for `C:\Python314\python.exe`; verification used the repo venv interpreter.

## Acceptance Criteria Status

- Unchanged selected signature with prior fatal worker stderr is no longer treated as healthy `unchanged`: satisfied by fatal-marker retry helper and regression tests.
- Durable failure evidence is recorded for prior fatal worker output: satisfied by `previous_launch_failed` JSONL record and regression tests.
- Ollama Loyal Opposition receives one selected bridge item by default: satisfied by target-specific cap and live diagnose `loyal-opposition selected=1`.
- Dispatch prompt names mandatory applicability and clause preflights before GO/VERIFIED verdict writes: satisfied by prompt text and assertions.
- Existing non-Ollama cap remains unchanged: `DEFAULT_MAX_ITEMS == 2` asserted by tests.
- Guard-denial behavior is preserved: guard-denial text is classified only as failure evidence; no bypass path was added.

## Risk And Rollback

Residual risk is localized to the cross-harness trigger. Retrying after fatal worker markers may create one extra dispatch attempt for the same selected signature, but only when previous worker logs show a known fatal marker. The one-item Ollama cap slows LO queue drain but reduces repeated multi-item worker exhaustion. Rollback is a normal revert of `scripts/cross_harness_bridge_trigger.py` and the related tests; bridge audit files remain append-only.
