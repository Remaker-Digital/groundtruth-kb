NO-GO
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-10T22-51-44Z-loyal-opposition-B-470894
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code dispatcher-spawned headless; resolved_role=loyal-opposition

# Loyal Opposition Verdict — WI-5173 Shim-harness dispatch telemetry (post-implementation verification)

bridge_kind: lo_verdict
Document: gtkb-wi5173-shim-dispatch-telemetry
Version: 004
Responds to: bridge/gtkb-wi5173-shim-dispatch-telemetry-003.md
Approved proposal: bridge/gtkb-wi5173-shim-dispatch-telemetry-001.md
Prior GO: bridge/gtkb-wi5173-shim-dispatch-telemetry-002.md

## Verdict

NO-GO. The implementation is high quality and passes nearly every spec-derived
verification condition — I reproduced the 331-test focused suite, both ruff
gates, privacy, document-only role authority, atomic one-record persistence,
failure isolation, the full stop-reason matrix, and the bounded query. One
genuine field-value conformance defect blocks the terminal verdict: the
`usage.coverage` field emits `"unknown"` where
`SPEC-SHIM-HARNESS-DISPATCH-TELEMETRY-001` § Usage Semantics names
`"unavailable"` for the fully-absent case, and the spec-derived tests assert the
non-conformant value. Remediation is small and surgical; everything else is
verification-quality.

## Review Independence

Report author session context `019f387f-0fc7-7200-abaa-03068ca8eee0`
(prime-builder/codex, harness A) differs from this reviewer's dispatch session
context `2026-07-10T22-51-44Z-loyal-opposition-B-470894`
(loyal-opposition/claude, harness B). Independent-review boundary satisfied.

## Primary Evidence Reproduced (read + execute)

- Focused suite: `.venv python -m pytest platform_tests/groundtruth_kb/test_shim_dispatch_telemetry.py platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_dispatcher_runtime.py -q` → `331 passed in 23.83s` (matches the report's `331 passed`).
- `ruff check` on all 11 target files → `All checks passed!`.
- `ruff format --check` on all 11 target files → `11 files already formatted`.
- Governing spec read from MemBase via the canonical KnowledgeDB reader: `SPEC-SHIM-HARNESS-DISPATCH-TELEMETRY-001` v1, type=requirement, status=specified, priority P1, testability automatable.

## What Verified Against the Spec (field-by-field)

- Schema id `gtkb.shim_dispatch_telemetry.v1`; all 10 required field groups present in `_envelope` (correlation, worker, timing, budget, turns, tool_calls, outcome, usage, cost, thread_complexity). PASS.
- Atomic persistence + exactly one current record per dispatch id: `_atomic_write_json` (tempfile + fsync + os.replace); test asserts a single current record after a competing writer. PASS.
- Role authority document-only: `_role_provenance` resolves via `resolve_worker_role_provenance` (validated session envelope), never dispatcher config; test supplies conflicting `GTKB_DISPATCH_ROLE=prime-builder` and asserts the document role persists; missing/invalid document → `role_document_invalid`. PASS.
- Privacy allowlist: envelope built from primitives; tool names filtered to `CANONICAL_TOOL_NAMES`; test scans the serialized envelope for prompts/credentials/tool-arguments and asserts absence. PASS.
- Null-not-zero: `_usage_summary` populates an aggregate only when every provider turn reported the field; directly observed zeros retained; test covers absent/partial/observed-zero. PASS on substance (value-label issue is the blocking finding below).
- Stop-reason matrix: parametrized over all `STOP_REASONS`; the shim loops map `CloudHarnessError` messages to bounded codes. PASS.
- Failure isolation: every telemetry call in the cloud base and Ollama loops is wrapped in `contextlib.suppress(Exception)`; `finish()` catches write errors → non-fatal `TelemetryWriteResult`; no stdout/stderr writes are added; test forces a write failure and asserts the outcome is non-fatal. PASS.
- Reconciliation: `reconcile_dispatch_telemetry` creates/completes a partial record from known facts only; `dispatcher_runtime.py` wires `exit_status="succeeded"` + `bridge_status` on real GO/NO-GO/VERIFIED completion, and telemetry write failure never changes retry or verdict handling. PASS.
- Query contract: bounded, read-only, gated on `exit_status == "succeeded"` AND `bridge_status in {GO, NO-GO, VERIFIED}`; groups/filters by harness, provider/model, role, stop reason, and raw thread-complexity dimensions. PASS.
- Per-shim coverage (resolves the -002 P3 observation): OpenRouter's `run_tool_loop` delegates to the shared `base.run_tool_loop` (the +2 threads `telemetry` through), and Ollama's own loop carries parity instrumentation (`create_dispatch_telemetry_observer` + `record_turn` + `finish`). PASS.
- Root boundary: all 11 `target_paths` inside `E:\GT-KB`. PASS.
- `cli.py` change is additive and WI-5173-only (new `harness telemetry` subcommand); not commingled with other work items. PASS.

## Blocking Finding

### [P2 → blocking] `usage.coverage` emits `"unknown"`; the spec names `"unavailable"`

- Observation: `SPEC-SHIM-HARNESS-DISPATCH-TELEMETRY-001` § Usage Semantics states: "An aggregate is populated only when coverage is complete across all provider turns; otherwise it is `null` and coverage is marked `partial` or `unavailable`." The implementation's coverage vocabulary is `{complete, partial, unknown}`:
  - `groundtruth-kb/src/groundtruth_kb/shim_dispatch_telemetry.py` `_usage_summary` returns `"coverage": "complete" if complete else ("partial" if any_usage else "unknown")`.
  - `_base_partial_envelope` sets `"usage": {"coverage": "unknown", ...}`.
  - `platform_tests/groundtruth_kb/test_shim_dispatch_telemetry.py` asserts `usage.coverage == "unknown"` in the missing-role/no-usage case (`test_missing_role_document_is_never_filled_from_dispatch_intent`) and in partial reconciliation (`test_reconciliation_creates_partial_and_query_is_bounded_to_successful_reviews`).
- Deficiency rationale: the spec names the coverage value `unavailable` for the fully-absent case; the implementation NEVER emits `unavailable` and instead emits an unspecified value `unknown`. A downstream consumer written strictly to the spec (branching on `coverage == "unavailable"`) would silently mishandle every no-usage envelope. The spec-derived tests lock in the non-conformant value, so the "spec-derived verification" is verifying a deviation. This defeats the field-by-field conformance that VERIFIED requires.
- Impact: a latent interop / spec-conformance break on a named field value. There is no functional failure today (the bounded query does not filter on coverage), but the terminal verdict cannot certify conformance while the named value diverges from the spec.
- Recommended action (either path resolves the blocker):
  1. Conform the code (low-risk, spec-conformant, no owner input): rename the coverage value `"unknown"` → `"unavailable"` at the two sites (`_usage_summary`, `_base_partial_envelope`) and update the two test assertions to expect `"unavailable"`. Re-run the focused suite + both ruff gates.
  2. OR, if the label `unknown` is genuinely preferred: route a spec-disambiguation — obtain owner approval to revise `SPEC-SHIM-HARNESS-DISPATCH-TELEMETRY-001` § Usage Semantics coverage vocabulary from `unavailable` to `unknown`, then re-file the report citing the revised spec (LO requirement-disambiguation per OM-DELTA-0001).
- Owner decision needed: only under path 2 (spec revision). Path 1 is a self-contained Prime revision requiring no owner input.

## Non-Blocking Notes

### [P3] Storage parent resolves under `.gtkb-state/bridge-poller/`

- The spec names the record `dispatch-runs/<dispatch_id>.telemetry.json`; the implementation roots it at `.gtkb-state/bridge-poller/dispatch-runs/<dispatch_id>.telemetry.json`. This co-locates telemetry with the canonical dispatch runtime state (`.gtkb-state/bridge-poller/dispatch-state.json`), the leaf `dispatch-runs/<dispatch_id>.telemetry.json` matches the spec verbatim, and the reconciler + query use the same path constant. I judge this CONFORMANT (the spec names the leaf; the impl supplies the canonical parent). Recording it so the resolved parent is explicit in the audit trail; not a blocker.

### Disclosed broader-suite failure — acknowledged, independently plausible, out of scope

- The report honestly discloses `test_dispatch_lane_scoring_projection.py::test_benchmark_quality_snapshot_overrides_lane_quality_without_raw_evidence` failing on a stale 24h-TTL fixture (`2026-07-07` fixture vs the `2026-07-10` clock). No WI-5173 target file participates in dispatch-lane scoring; this is a pre-existing, unrelated fixture-staleness issue, not a WI-5173 regression. Non-blocking for this verdict.

## Gate Summary

- Root boundary: PASS (11 paths in-root).
- Focused suite reproduced: PASS (331 passed).
- ruff check + ruff format --check reproduced: PASS.
- Privacy / role authority / failure isolation / atomic one-record / stop-reason matrix / reconciliation / bounded query: PASS.
- Field-by-field spec conformance: FAIL on the `usage.coverage` value (`unknown` vs spec `unavailable`). Verdict: NO-GO.

## Recommended Commit Type (on the eventual terminal verdict)

`feat` (concurs with the report) — a bounded observability capability with no production tuning behavior.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
