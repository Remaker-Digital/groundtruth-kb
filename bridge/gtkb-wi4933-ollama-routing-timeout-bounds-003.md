NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex Desktop; approval_policy=never; sandbox=danger-full-access
author_metadata_source: explicit-current-session

# GT-KB Bridge Implementation Report - gtkb-wi4933-ollama-routing-timeout-bounds - 003

bridge_kind: implementation_report
Document: gtkb-wi4933-ollama-routing-timeout-bounds
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi4933-ollama-routing-timeout-bounds-002.md
Approved proposal: bridge/gtkb-wi4933-ollama-routing-timeout-bounds-001.md
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4933-BACKPRESSURE-HEALTH
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4933
Recommended commit type: fix

target_paths: ["scripts/ollama_harness.py", "platform_tests/scripts/test_ollama_harness.py"]

## Implementation Claim

Implemented the approved Ollama routing-timeout boundedness repair. `scripts/ollama_harness.py` now parses `[routing.ollama].timeout_seconds` from `.api-harness/routing.toml` into `RoutingConfig` and resolves runtime budgets after CLI parsing. When the caller uses default timeout flags, the configured route timeout governs the Ollama inventory request, chat turns, guard calls, and tool subprocess caps. The session timeout is now derived from that route timeout with a fixed 60 second grace window, so unattended Ollama dispatch cannot silently retain the old 540 second session ceiling while config declares a shorter route budget.

Explicit CLI overrides remain preserved. Supplying `--timeout` keeps the requested operation timeout and the existing default session timeout unless `--session-timeout` is also explicitly supplied. Supplying `--session-timeout` always wins for diagnostics and tests.

## Implementation-Start / Work-Intent Evidence

- Work-intent claim: row `25328`, session `019f09c9-2db0-7b00-a337-40f998b07e56`, bridge `gtkb-wi4933-ollama-routing-timeout-bounds`.
- Implementation authorization packet: `sha256:c25125222e782f2d4be27c721352a9769eae70c27f00a068b328fb009dea4b17`.
- Authorized target globs: `scripts/ollama_harness.py`, `platform_tests/scripts/test_ollama_harness.py`.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher-owned harness execution must be bounded and observable.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - runtime failures and bounds must surface through dispatcher-readable diagnostics.
- `ADR-DISPATCHER-ARCHITECTURE-001` - fixes remain inside the dispatcher-owned harness path and do not restore retired trigger fallbacks.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - Windows dispatch remains headless while failures surface through logs/status.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - implementation followed an approved GO verdict and matching work-intent claim.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal and report carry concrete specification links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - report includes spec-derived executed verification evidence.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - report preserves project authorization, project, work item, and target path metadata.

## Owner Decisions / Input

No new owner decision was required. This implementation is within the active WI-4933 project authorization and the GO verdict at `bridge/gtkb-wi4933-ollama-routing-timeout-bounds-002.md`.

## Prior Deliberations

- `bridge/gtkb-wi4933-ollama-routing-timeout-bounds-001.md` - Prime Builder proposal for the routing timeout boundedness repair.
- `bridge/gtkb-wi4933-ollama-routing-timeout-bounds-002.md` - Loyal Opposition GO verdict authorizing implementation.
- Live dispatcher evidence: `2026-06-30T12-27-18Z-loyal-opposition-D-8aeb25` exceeded the intended route bound with empty stdout/stderr until manually terminated.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `python -m pytest platform_tests\scripts\test_ollama_harness.py platform_tests\scripts\test_dispatcher_budget_constants_regression.py -q --tb=short` passed, including new tests that config-derived `timeout_seconds` governs default runtime budgets and session timeout derivation. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | The same focused tests verify invalid route timeout config fails as `OllamaHarnessError`, preserving concise diagnostics for dispatcher reports. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Code diff is limited to `scripts/ollama_harness.py` and its tests; no retired trigger, hook-triggered worker, poller, or alternate runtime path was added. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | No launch code or subprocess window behavior changed; existing `CREATE_NO_WINDOW` and dispatcher `pythonw` wrappers remain untouched. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Work-intent claim and implementation authorization packet were acquired before protected file edits. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Report carries forward the proposal's dispatcher boundedness and control-surface specification links. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Commands and observed pass results are recorded below. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Header metadata includes PAUTH, project, work item, and target paths. |

## Commands Run

- `python -m pytest platform_tests\scripts\test_ollama_harness.py platform_tests\scripts\test_dispatcher_budget_constants_regression.py -q --tb=short`
- `python -m ruff check scripts\ollama_harness.py platform_tests\scripts\test_ollama_harness.py`
- `python -m ruff format --check scripts\ollama_harness.py platform_tests\scripts\test_ollama_harness.py`

## Observed Results

- `pytest`: 52 passed in 1.00s after formatting.
- `ruff check`: All checks passed.
- `ruff format --check`: 2 files already formatted.

## Files Changed

- `scripts/ollama_harness.py`
- `platform_tests/scripts/test_ollama_harness.py`

## Recommended Commit Type

- Recommended commit type: `fix`
- Diff-stat justification: bounded runtime behavior fix with focused regression coverage.

## Acceptance Criteria Status

- PASS: `routing.ollama.timeout_seconds` is parsed and used for default Ollama harness operation budgets.
- PASS: Default session timeout is deterministically derived from route timeout plus a fixed 60 second grace window.
- PASS: Explicit `--timeout` and `--session-timeout` overrides remain supported.
- PASS: Existing dispatcher budget constant regressions remain green.
- PASS: No dispatch launch, windowing, trigger, or topology behavior changed in this slice.

## Risk And Rollback

Risk is low and contained to Ollama harness timeout resolution. The main compatibility risk is that default unattended Ollama dispatch now follows the configured route timeout instead of the historical hard-coded defaults; this is the intended release-health behavior. Rollback is to revert `scripts/ollama_harness.py` and `platform_tests/scripts/test_ollama_harness.py` for this bridge thread.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Return VERIFIED if the report and implementation satisfy the approved proposal, otherwise return NO-GO with findings.
