NEW

# GT-KB Bridge Implementation Report - WI-5173 Shim-harness dispatch telemetry

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f387f-0fc7-7200-abaa-03068ca8eee0
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive session; role=prime-builder resolved via worker session document

bridge_kind: implementation_report
Document: gtkb-wi5173-shim-dispatch-telemetry
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5173-shim-dispatch-telemetry-002.md
Approved proposal: bridge/gtkb-wi5173-shim-dispatch-telemetry-001.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5173-SHIM-TELEMETRY-20260710
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5173
Recommended commit type: feat

## Implementation Claim

Implemented `gtkb.shim_dispatch_telemetry.v1`: one atomic, privacy-bounded JSON
envelope per dispatcher-launched shim run at
`.gtkb-state/bridge-poller/dispatch-runs/<dispatch_id>.telemetry.json`.

The shared cloud loop, OpenRouter wrapper, and Ollama loop record only turn
ordinal, canonical tool names, timing, configured/used turn budget, allowlisted
provider usage and cost scalars, normalized stop reason, and model metadata.
Dispatcher exit processing adds only known exit/verdict facts and creates a
partial record if the worker never wrote one. Telemetry failures are nonfatal to
the original loop and dispatch outcome.

`worker.role` is resolved only through the validated worker session document.
Dispatcher metadata carries bridge correlation only and cannot supply or override
a role. The new `gt harness telemetry` command is bounded and read-only; it
reports only successful reconciled-review distributions and makes no dispatch,
budget, selection, or tuning change.

## Specification Links

- `SPEC-SHIM-HARNESS-DISPATCH-TELEMETRY-001` - v1 envelope, privacy, null semantics, reconciliation, query, and tests.
- `GOV-SESSION-ROLE-AUTHORITY-001` and `DCL-SESSION-ROLE-RESOLUTION-001` - document-only worker-role authority.
- `SPEC-TAFE-R6`, `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, and `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` - dispatcher context.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - required specification-derived evidence.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and `GOV-FILE-BRIDGE-AUTHORITY-001` - mandatory bridge and specification linkage gates.

## Owner Decisions / Input

- `DELIB-202666074` approved bounded implementation authorization for WI-5173; PAUTH, GO, claim, and independent verification remain required.
- `DELIB-202665303` requires measuring real harness behavior before changing budgets.
- No production dispatch-selection, turn-budget, or automatic-tuning change is included.

## Prior Deliberations

- `bridge/gtkb-wi5173-shim-dispatch-telemetry-001.md` - approved implementation proposal.
- `bridge/gtkb-wi5173-shim-dispatch-telemetry-002.md` - independent Loyal Opposition GO.
- `DELIB-20265026` - provider-failure evidence informing partial, nonfatal telemetry.

## Specification-Derived Verification Plan

| Requirement | Executed evidence |
| --- | --- |
| Envelope, atomic replacement, correlation, counts | `platform_tests/groundtruth_kb/test_shim_dispatch_telemetry.py` covers v1 shape, one current record, turn/tool aggregation, context counts, and prefix-child exclusion. |
| Null/zero/cost semantics | Dedicated tests cover absent usage/cost as null, partial coverage, and directly observed provider zero values. |
| Role authority and privacy | Dedicated tests use a validated document against conflicting dispatcher intent, missing-document fail-closed behavior, and serialized prohibited-content scans. |
| Stop/failure behavior | Dedicated stop-reason tests, forced write-failure test, shim observer tests, and dispatcher partial reconciliation. |
| Bounded query | Dedicated module and Click CLI tests cover successful-review filtering, dimensions, raw-complexity value filters, and record bounds. |

## Commands Run

- `python -m pytest platform_tests/groundtruth_kb/test_shim_dispatch_telemetry.py platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short`
- `python -m ruff check` on the eleven scoped Python files.
- `python -m ruff format --check` on the same eleven scoped Python files.
- `git -c core.whitespace=cr-at-eol diff --check -- <WI-5173 target paths>`
- `python -m pytest platform_tests/groundtruth_kb -q --tb=short` as a broader package check.

## Observed Results

- Focused regression suite: `331 passed in 26.65s`.
- Ruff check: `All checks passed!`.
- Ruff format: `11 files already formatted`.
- Scoped CRLF-aware diff check: exit 0.
- Broader `platform_tests/groundtruth_kb`: `300 passed, 1 failed`. The failure is outside this scope in `test_dispatch_lane_scoring_projection.py::test_benchmark_quality_snapshot_overrides_lane_quality_without_raw_evidence`: a fixture generated at `2026-07-07T00:00:00Z` with a 24-hour TTL is stale against the current `2026-07-10` clock and produces quality `0.0` rather than its historical expected `100.0`. No WI-5173 file participates in dispatch-lane scoring; this report does not claim the broader suite is fully green.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/shim_dispatch_telemetry.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `scripts/cloud_harness_base.py`
- `scripts/openrouter_harness.py`
- `scripts/ollama_harness.py`
- `scripts/dispatcher_runtime.py`
- `platform_tests/groundtruth_kb/test_shim_dispatch_telemetry.py`
- `platform_tests/scripts/test_cloud_harness_base.py`
- `platform_tests/scripts/test_openrouter_harness.py`
- `platform_tests/scripts/test_ollama_harness.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`

## Recommended Commit Type

- Recommended commit type: `feat`
- Rationale: adds a bounded observability capability with no production tuning behavior.

## Acceptance Criteria Status

- [x] Per-dispatch v1 envelope is atomic and leaves one current record by dispatch ID.
- [x] Document-derived roles cannot be overridden by dispatcher intent; invalid/missing documents fail closed with `role_document_invalid`.
- [x] Unknown usage, cache, and cost serialize as null rather than fabricated zero; direct observed zero is retained.
- [x] Prompts/messages, tool arguments/results, provider bodies, credentials, environment values, and free-form errors are excluded from persisted telemetry.
- [x] Reconciliation creates bounded partial records from known runtime facts only.
- [x] Read-only distributions are bounded and filter/group by harness, provider/model, role, stop reason, and raw complexity.
- [x] No budget, selection, or automatic tuning behavior changed.

## Risk And Rollback

Residual risk is limited to unavailable provider usage/cost fields and the
documented broader scoring-suite fixture failure outside this implementation.
Telemetry uses a fixed allowlist and nonfatal writes, so removing the observer,
reconciler, and query surfaces restores prior shim behavior without changing
bridge verdicts, worker exit results, dispatch selection, or turn budgets.

## Loyal Opposition Asks

1. Verify the eleven scoped paths and their tests against `SPEC-SHIM-HARNESS-DISPATCH-TELEMETRY-001`, especially document-only role provenance and privacy exclusion.
2. Reproduce the focused suite, lint, formatting, and diff checks; assess the disclosed broader-suite failure independently as unrelated residual evidence.
3. Return VERIFIED only if the implementation and report satisfy the approved proposal; otherwise return NO-GO with concrete findings.
