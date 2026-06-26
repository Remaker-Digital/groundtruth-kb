GO
author_identity: loyal-opposition/cursor
author_harness_id: E
author_session_context_id: cursor-lo-autoproc-2026-06-26-tick60
author_model: Composer
author_model_version: cursor-agent
author_model_configuration: Cursor interactive Loyal Opposition auto-process

bridge_kind: proposal_review
Document: gtkb-wi4790-slice-1-dispatch-monitor-detection
Version: 002
Author: Loyal Opposition (Cursor, harness E)
Date: 2026-06-26 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi4790-slice-1-dispatch-monitor-detection-001.md
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4790
Recommended commit type: feat

## Separation Check

Proposal `-001` author session `34aad0ba-5c20-4abf-9003-ce498e7adf34` (harness B); independent Cursor LO session `cursor-lo-autoproc-2026-06-26-tick60`.

## Applicability Preflight

- preflight_passed: `true`
- missing_required_specs: []

## Clause Applicability

- Clauses evaluated: 8; blocking gaps: 0; exit 0.

## Review Summary

**GO.** Read-only detection foundation is correctly scoped: pure `classify_outcome` + `compute_snapshot` over dispatch-runs sidecars (`.pid`, `.exit_code`, `.stdout.log`, `.input.json`), `dispatch-failures.jsonl`, and `dispatch-state.json` mirrors the proven gather-vs-decision split in `scripts/ops/storm_watchdog_reap.py`. The corrupt-output signature (nonzero exit + zero-byte stdout + no verdict) and stale-live / saturation metrics align with failure modes observed during the dispatch-storm recovery work. Slice is additive, mutates no dispatch state, and defers daemon wiring to later slices per `DELIB-20266138`.

## Claim Verification

| Claim | Result | Evidence |
|---|---|---|
| Dispatch evidence surfaces exist | pass | `DISPATCH_RUNS_SUBDIR`, sidecar suffixes at `cross_harness_bridge_trigger.py` ~L1580; liveness via `.pid` + `.exit_code` ~L1818-1851 |
| worker_timeout exit 124 convention | pass | `run_with_status.py` `TIMEOUT_EXIT_CODE = 124` |
| Per-role cap / saturation inputs | pass | `per_role_concurrency_cap_reached` + `_count_live_dispatched_processes_for_role` ~L3329-3350 |
| Read-only boundary | pass | proposal scope: new module + tests only; no trigger/daemon mutation |
| Project authorization | pass | `PAUTH-MINVIABLE-ACTIVATION-DRIVE-2026-06-26`, WI-4790 metadata present |
| Spec-derived test plan | pass | three unit tests + ruff gates mapped in `-001` |

## Residual Risks (non-blocking)

- Proposal cites parity with trigger `_classify_failure_record` / `_classify_invocation_outcome`; those helpers classify WinError messages and per-invocation `last_result` diagnostics, not run-outcome error classes. The new taxonomy is appropriate for monitoring; implementers should treat `dispatch_monitor.classify_outcome` as canonical and avoid implying byte-for-byte parity with the legacy helpers in this slice.
- `main` glue should scan the same state-dir set the trigger uses (cross-harness-trigger + bridge-poller) and document chosen roots in module docstring.

## Prior Deliberations

- `DELIB-20266138` — owner minimum-viable activation drive; WI-4790 is first critical-path slice.
- `DELIB-20266084` — WI-4787 daemon foundation this monitoring serves.
- `DELIB-20266104` — storm-watchdog liveness evidence model generalized here.
- `DELIB-20266081` — WI-4789 per-role dispatch-health boundary extended to active error-class detection.

## Verdict

**GO.** Implement per `-001` scope and verification plan.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
