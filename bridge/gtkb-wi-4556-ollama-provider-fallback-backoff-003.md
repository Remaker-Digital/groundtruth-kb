NEW

# GT-KB Bridge Implementation Report - WI-4556 Ollama Provider Fallback Backoff

bridge_kind: implementation_report
Document: gtkb-wi-4556-ollama-provider-fallback-backoff
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi-4556-ollama-provider-fallback-backoff-002.md
Approved proposal: bridge/gtkb-wi-4556-ollama-provider-fallback-backoff-001.md
Author: Prime Builder (Codex, harness A)
Date: 2026-06-16 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-06-16T14-41-46Z-prime-builder-A-889075
author_model: gpt-5-codex
author_model_version: 5
author_model_configuration: Codex desktop automation; Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4556
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4556

target_paths: ["scripts/cross_harness_bridge_trigger.py", "scripts/ollama_harness.py", "scripts/openrouter_harness.py", "scripts/verify_ollama_dispatch.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "platform_tests/scripts/test_ollama_harness.py", "platform_tests/scripts/test_openrouter_harness.py", "platform_tests/scripts/test_bridge_dispatch_config.py", "bridge/gtkb-wi-4556-ollama-provider-fallback-backoff-*.md"]

Recommended commit type: fix:

---

## Implementation Claim

Implemented the bounded WI-4556 dispatcher hardening approved in the GO
verdict. The cross-harness trigger now treats provider/output failures and LO
workers that exit successfully without producing a bridge verdict as failed
work delivery rather than clean launches. When the same selected bridge batch
would otherwise be relaunched against the same failed provider and another
eligible LO backend is available, the failed provider target is temporarily
skipped with explicit backoff evidence and the dispatcher can select the next
eligible backend.

The implementation preserves single-target retry behavior: provider-failure
backoff causes target fallback only when there is another candidate after the
current target. It does not restore or depend on `bridge/INDEX.md`.

## Specification Links

- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001`
- `DCL-DISPATCH-ENVELOPE-RULES-001`
- `SPEC-TAFE-R4`
- `SPEC-TAFE-R5`
- `SPEC-TAFE-R6`

## Owner Decisions / Input

No new owner decision is required by this implementation report. The
implementation remains within the owner authorization recorded in
`DELIB-20263381` / `AUQ-2026-06-14-COST-AUTODISPATCH-WI-4556`.

## Prior Deliberations

- `bridge/gtkb-wi-4556-ollama-provider-fallback-backoff-001.md` - approved
  implementation proposal carried forward.
- `bridge/gtkb-wi-4556-ollama-provider-fallback-backoff-002.md` - Loyal
  Opposition GO verdict authorizing bounded implementation.
- `DELIB-20263381` / `AUQ-2026-06-14-COST-AUTODISPATCH-WI-4556` - owner
  authorization for WI-4556 cost-optimized autodispatch work.

## Implementation Details

- Added fatal worker-output marker detection for Ollama max-turn exhaustion,
  Ollama chat/model inventory failures, OpenRouter completion/API failures,
  and the OpenRouter missing-key path. Matched markers are written as
  dispatch-failure evidence before any generic exit-code classification.
- Refactored bridge-verdict detection into a one-shot lookup and used it while
  processing completed LO launches. Exit code `0` without a post-launch bridge
  verdict now records `no_verdict_produced` with `missing_bridge_verdict`
  evidence instead of clearing failure state.
- Extended launch metadata with `selected_documents` and `primary_bridge_id`
  so no-verdict checks and diagnostics can tie a worker launch back to the
  selected bridge thread.
- Added same-signature provider-failure backoff and fallback selection. The
  dispatcher records `provider_failure_backoff_active` skip evidence for the
  failed target and seeds target-specific state while continuing to the next
  eligible candidate.
- Updated the Ollama prompt invariant test to assert that the route metadata
  references the full versioned bridge-file chain and does not reference the
  retired `bridge/INDEX.md`.
- Applied ruff-only cleanup in `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
  and `platform_tests/scripts/test_bridge_dispatch_config.py` to satisfy the
  focused lint lane.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | `python scripts/bridge_claim_cli.py status gtkb-wi-4556-ollama-provider-fallback-backoff` showed a live `go_implementation` claim for harness A; `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi-4556-ollama-provider-fallback-backoff` issued packet `sha256:eff81428b7e16ca2f9be87a4f90f770ce0072f479c7a59accd6b67e79df0a956` for the approved target globs before protected edits. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `SPEC-TAFE-R5`, `SPEC-TAFE-R6` | `platform_tests/scripts/test_cross_harness_bridge_trigger.py::test_lo_provider_failure_backoff_falls_back_after_max_turn_marker` verifies fatal Ollama output is failure evidence and no longer remains a clean launch. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `SPEC-TAFE-R5`, `SPEC-TAFE-R6` | `platform_tests/scripts/test_cross_harness_bridge_trigger.py::test_lo_exit_zero_without_verdict_backs_off_and_falls_back` verifies an LO worker exit code `0` without a verdict records `no_verdict_produced` / `missing_bridge_verdict`. |
| `SPEC-DISPATCH-ENVELOPE-ELEMENT-001`, `DCL-DISPATCH-ENVELOPE-RULES-001`, `SPEC-TAFE-R4` | Both new trigger tests configure D and F LO candidates, preserve the selected bridge batch signature, and assert fallback to F only after D is skipped with `provider_failure_backoff_active`. |
| WI-4556 duplicate/stale worker suppression | Both new trigger tests seed the same selected signature in dispatch state and assert the failed D target is skipped rather than relaunched for that same batch. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Full focused pytest, ruff check, and ruff format-check lanes passed with exact commands and observed results below. |
| No-index invariant | `Test-Path bridge\INDEX.md` returned `False` before and after implementation; no code path recreated the retired index. |

## Commands Run

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest -o addopts='' --basetemp .pytest-tmp-wi4556 platform_tests/scripts/test_cross_harness_bridge_trigger.py::test_lo_provider_failure_backoff_falls_back_after_max_turn_marker platform_tests/scripts/test_cross_harness_bridge_trigger.py::test_lo_exit_zero_without_verdict_backs_off_and_falls_back -q --tb=short
```

Observed result:

```text
2 passed, 2 warnings
```

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest -o addopts='' --basetemp .pytest-tmp-wi4556-full platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_bridge_dispatch_config.py -q --tb=short
```

Observed result:

```text
124 passed, 2 warnings in 6.21s
```

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff format scripts/cross_harness_bridge_trigger.py scripts/ollama_harness.py scripts/openrouter_harness.py scripts/verify_ollama_dispatch.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_bridge_dispatch_config.py
```

Observed result:

```text
3 files reformatted, 6 files left unchanged
```

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts/cross_harness_bridge_trigger.py scripts/ollama_harness.py scripts/openrouter_harness.py scripts/verify_ollama_dispatch.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_bridge_dispatch_config.py
```

Observed result:

```text
All checks passed!
```

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts/cross_harness_bridge_trigger.py scripts/ollama_harness.py scripts/openrouter_harness.py scripts/verify_ollama_dispatch.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_bridge_dispatch_config.py
```

Observed result:

```text
9 files already formatted
```

```text
Test-Path bridge\INDEX.md
```

Observed result:

```text
False
```

Notes:

- The first pytest attempt used the repository addopts and failed because this
  local virtual environment does not have `pytest-timeout` for `--timeout=30`.
  The rerun used `-o addopts=''` to exercise the focused tests without that
  unavailable local plugin.
- The focused full pytest lane used `--basetemp .pytest-tmp-wi4556-full`
  because the default Windows temp pytest directory was not writable in this
  sandbox. This does not change the tested behavior.
- Pytest warnings were pre-existing environment warnings:
  `PytestConfigWarning: Unknown config option: asyncio_mode` and a cache write
  warning for an existing `.pytest_cache` path.

## Files Changed

- `scripts/cross_harness_bridge_trigger.py`
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py`
- `platform_tests/scripts/test_ollama_harness.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `platform_tests/scripts/test_bridge_dispatch_config.py`
- `bridge/gtkb-wi-4556-ollama-provider-fallback-backoff-003.md` (this report)

Approved but unchanged implementation-lane files:

- `scripts/ollama_harness.py`
- `scripts/openrouter_harness.py`
- `scripts/verify_ollama_dispatch.py`
- `platform_tests/scripts/test_openrouter_harness.py`

Scoped diff stat:

```text
.../src/groundtruth_kb/bridge_dispatch_config.py   |   6 +-
.../scripts/test_bridge_dispatch_config.py         |   4 +-
.../scripts/test_cross_harness_bridge_trigger.py   | 185 +++++++++++
platform_tests/scripts/test_ollama_harness.py      |   4 +-
scripts/cross_harness_bridge_trigger.py            | 349 +++++++++++++++++----
5 files changed, 483 insertions(+), 65 deletions(-)
```

## Acceptance Criteria Status

- [x] A launched worker that exits without a bridge verdict no longer remains a
  clean `launched` success state for LO dispatch.
- [x] Provider/output failures are recorded as operational dispatch evidence.
- [x] Same selected-batch provider failures suppress or delay duplicate
  relaunch of the failed target while an alternate eligible backend is
  available.
- [x] Fallback to the next eligible backend preserves role, selected batch,
  dispatchability, and configured candidate ordering gates.
- [x] Focused regression tests, lint, and format checks passed.
- [x] `bridge/INDEX.md` remains absent.

## Risk And Rollback

Residual risk is bounded to dispatch target selection and completed-worker
status processing. The main behavioral risk is over-skipping a recovered cheap
provider for one retry window when another backend is available; this is
intentional for WI-4556 because the prior behavior repeatedly selected a
provider that had already failed the same batch without producing a verdict.

Rollback is a single implementation commit revert for the changed dispatcher
and test files, preserving the append-only bridge audit trail. Rollback must
not recreate `bridge/INDEX.md` and must preserve the earlier WI-4484 ordered
fallback behavior unless a follow-up bridge explicitly authorizes otherwise.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed
   command evidence.
2. Return `VERIFIED` if the report and implementation satisfy the approved
   proposal, otherwise return `NO-GO` with findings.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
