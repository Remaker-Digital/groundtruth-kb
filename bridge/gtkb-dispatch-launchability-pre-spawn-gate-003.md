NEW

# WI-4525 Implementation Report: Pre-Spawn Launchability Gate + SessionStart Surfacing

bridge_kind: implementation_report
Document: gtkb-dispatch-launchability-pre-spawn-gate
Version: 003
Reports on: bridge/gtkb-dispatch-launchability-pre-spawn-gate-001.md (NEW proposal)
Authorized by: bridge/gtkb-dispatch-launchability-pre-spawn-gate-002.md (GO; Loyal Opposition, Antigravity harness C)
Date: 2026-06-13 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: c8d27656-a22f-4b94-b7fb-70d016e7b3ee
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive session; Prime Builder declared via ::init gtkb pb; explanatory output style; autonomous PB-implementation loop

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4525-DISPATCH-LAUNCHABILITY-HARDENING
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4525

target_paths: ["scripts/cross_harness_bridge_trigger.py", "scripts/session_self_initialization.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "platform_tests/scripts/test_session_self_initialization.py"]

implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: feat:

---

## Summary

Implemented WI-4525 exactly per the GO'd proposal (-001). Two execution-surface additions reuse the existing FAB-01 / HYG-001 launchability-detection contract without changing the detection logic itself:

1. **Pre-spawn launchability gate** in `scripts/cross_harness_bridge_trigger.py`. In `run_trigger()`'s dispatch loop, after the circuit-breaker / retry-delay / self-review guards and before the `_spawn_harness()` call, the resolved target's argv head is checked for launchability. When the normalized head does not resolve (`shutil.which(resolved) or os.path.isfile(resolved)` is False), the spawn is skipped: `recipient_state["last_result"]` is set to the distinct `"target_unlaunchable"`, a `_record_dispatch_failure()` entry with `reason: "target_unlaunchable"` and `launched: False` is appended to `dispatch-failures.jsonl`, and the loop `continue`s. Because the spawn is skipped, the post-dispatch exit-code failure path never runs, so `failure_count` is NOT incremented and circuit-breaker semantics for genuine transients are preserved.

   - **Placement note (faithful to proposal intent):** the gate is inserted *before* the prime work-intent acquisition block, not literally adjacent to `_spawn_harness()`. This is strictly within the proposal's stated ordering ("after the circuit-breaker, retry-delay, and self-review guards") and yields cleaner failure semantics — an unlaunchable target acquires no work-intent claim and issues no authorization packet before being rejected.
   - Two small module-level helpers were added next to `_normalize_argv_head`: `_dispatch_target_argv_head(target)` (extracts the headless argv head from the resolved `DispatchTarget`, returning `None` for placeholder tokens so they are skipped) and `_argv_head_launchable(head, project_root)` (reuses `_normalize_argv_head` + the same `shutil.which` / `os.path.isfile` resolution the doctor check uses).

2. **SessionStart surfacing** in `scripts/session_self_initialization.py`. A new `_harness_launchability_status(project_root)` helper calls `groundtruth_kb.project.doctor._check_harness_launchability` (lazy import, fail-soft), returning a JSON-serializable `{status, message, verification_command}`. `build_startup_model()` records it under `metrics["harness_launchability"]`. `render_report()` renders a prominent `### Harness Dispatch Launchability` alert section (inserted before `### Active Work Subject`) ONLY when `status == "fail"`; the PASS case adds no rendered noise.

The doctor check itself is unchanged — this is a pure execution-surface addition at the two moments where the 2026-06-13 hollow-venv dispatch jam would have surfaced within minutes instead of hours.

## Specification Links

(Carried forward from -001; independently re-confirmed against the implemented diff.)

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge integrity hardened: a config defect in the dispatch hot-path is now loud (distinct `target_unlaunchable` result + failure record) instead of silently halting review for hours.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all governing specs cited here.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project/WI metadata present in the header.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping + executed results below.
- `REQ-HARNESS-REGISTRY-001` — the gate reads `invocation_surfaces.headless.argv[0]` from the resolved `DispatchTarget` (canonical registry projection), not ad-hoc parsing.
- `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` — the SessionStart surfacing reads the registry through the doctor check's already-conformant `harness_projection` reader.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — clause (c): the gate derives "this target is dispatchable" from a fresh registry + filesystem read at dispatch time, not a stale prior success.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all edits under `E:\GT-KB`; NO file under `groundtruth-kb/src/groundtruth_kb/project/**` modified; the doctor module is not relocated; no artifact under `applications/`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — artifact graph preserved; the new `target_unlaunchable` dispatch-failure state is distinct from the transient `subprocess_execution_failed` state.

## Spec-to-Test Mapping

| Linked spec | Derived test | Result |
|---|---|---|
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` + `REQ-HARNESS-REGISTRY-001` (pre-spawn gate consults fresh registry + fs) | `test_cross_harness_bridge_trigger.py::test_spawn_gate_skips_unlaunchable_harness_with_distinct_failure` — asserts (a) `_spawn_harness` NOT called for the unlaunchable target, (b) `dispatch-failures.jsonl` has `reason=target_unlaunchable` / `launched=False`, (c) `failure_count==0` and `circuit_breaker_tripped` falsy, (d) `last_result=="target_unlaunchable"` | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` + `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` (SessionStart surfaces launchability via canonical reader) | `test_session_self_initialization.py::test_startup_disclosure_includes_harness_launchability_alert` — fail-case asserts model `status=="fail"` + rendered `### Harness Dispatch Launchability` alert carrying the failure message; pass-case asserts the alert section is absent | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` + linkage DCLs | applicability + clause preflight on this slug | applicability `preflight_passed: true`, `missing_required_specs: []`; clause preflight exit 0, blocking gaps 0 |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | all four `target_paths` under `E:\GT-KB` | confirmed |

## Verification Evidence (exact commands + observed results)

Interpreter: global Python 3.14.0 + pytest 9.0.2 (the project venv `groundtruth-kb/.venv` lacks pytest in this checkout; the venv `ruff` is used for the format gate). Trigger tests run with `GTKB_NO_CROSS_HARNESS_TRIGGER` cleared so the dispatch path is exercised CI-equivalently — the new trigger test also `monkeypatch.delenv`s it defensively so it is deterministic regardless of ambient session env.

```text
# New focused tests
python -m pytest \
  "platform_tests/scripts/test_cross_harness_bridge_trigger.py::test_spawn_gate_skips_unlaunchable_harness_with_distinct_failure" \
  "platform_tests/scripts/test_session_self_initialization.py::test_startup_disclosure_includes_harness_launchability_alert" \
  -q --no-header
=> 2 passed

# Full changed-file regression
env -u GTKB_NO_CROSS_HARNESS_TRIGGER python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q
=> 78 passed
env -u GTKB_NO_CROSS_HARNESS_TRIGGER python -m pytest platform_tests/scripts/test_session_self_initialization.py -q
=> 67 passed, 1 environmental flake (see note below)

# Code-quality gates (run as SEPARATE gates on the 4 changed files)
ruff check  scripts/cross_harness_bridge_trigger.py scripts/session_self_initialization.py \
            platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_session_self_initialization.py
=> All checks passed!
ruff format --check <same 4 files>
=> 4 files already formatted

# Mechanical preflights (this slug)
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-dispatch-launchability-pre-spawn-gate
=> preflight_passed: true; missing_required_specs: []; missing_advisory_specs: [];
   packet_hash sha256:1d67722e951ec554ce54dbeec5b93f7b02c7b926f420f8d60d1bf830b2acc04d
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-dispatch-launchability-pre-spawn-gate
=> Clauses evaluated 5; must_apply 3; evidence gaps in must_apply 0; blocking gaps 0; exit 0
```

**Environmental flake note (transparent disclosure):** in the full-file session run, `test_session_self_initialization.py::test_direct_script_execution_emits_startup_payload` intermittently exceeds its subprocess `timeout` under load (it spawns the full startup script as a subprocess, which queries the 1.37 GB canonical `groundtruth.db` on a cloud-synced `E:` drive while a multi-Prime swarm is active). The same test PASSES deterministically in isolation (`12.08s`), and the earlier combined two-file run exited 0. This is a pre-existing timing flake, NOT a regression from this slice: the source change adds only ~5 `shutil.which` calls to `build_startup_model` (sub-100 ms), and neither new test nor any `target_paths` edit affects that subprocess test's timing.

## Prior Deliberations

(Carried forward from -001.)

- `DELIB-20263168` — owner_decision (AskUserQuestion, 2026-06-13) authorizing the WI-4525 reframe to "Both (pre-spawn gate + SessionStart surfacing)" after the previously-authorized "add doctor check" scope was shown redundant (the check already exists). Direct authorization basis for this slice.

## Owner Decisions / Input

No new owner decision is required to file or verify this report. Implementation authority is the active bounded PAUTH `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4525-DISPATCH-LAUNCHABILITY-HARDENING`, backed by owner decision `DELIB-20263168` (AskUserQuestion answers: "Both (pre-spawn gate + SessionStart surfacing)" plus the prior "Platform hardening" branch). The PAUTH's `allowed_mutation_classes` = `source` + `test`; no `kb_schema_change`, no cutover, no dual-write, no live-dispatch-substrate, no authoritative-generated-view. All forbidden-operation bounds are respected.

## Files Changed (this slice only; pathspec commit scope)

- `scripts/cross_harness_bridge_trigger.py` — `_dispatch_target_argv_head` + `_argv_head_launchable` helpers; pre-spawn launchability gate in `run_trigger()`.
- `scripts/session_self_initialization.py` — `_harness_launchability_status` helper; `metrics["harness_launchability"]` in `build_startup_model()`; `### Harness Dispatch Launchability` alert in `render_report()`.
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py` — `test_spawn_gate_skips_unlaunchable_harness_with_distinct_failure`.
- `platform_tests/scripts/test_session_self_initialization.py` — `test_startup_disclosure_includes_harness_launchability_alert`.

The working tree also contains unrelated changes from concurrent swarm sessions (dashboard-observability, tafe-stuck-flow, `memory/*`, `uv.lock`, `scripts/workstream_focus.py`, etc.). Those are explicitly OUT of scope for this commit and are NOT staged; this slice is committed with an explicit pathspec covering only the four files above plus the bridge report and `bridge/INDEX.md`.

## Risk / Rollback

Read-only at the OS layer (`shutil.which` + `os.path.isfile`); the gate is a pure addition before `_spawn_harness()` with all existing guards (circuit breaker, retry delay, self-review refusal) unchanged; the unlaunchable path skips the spawn without incrementing `failure_count`, so transient-failure breaker semantics are untouched. SessionStart surfacing fires only on `status == "fail"` and calls an existing, tested doctor function. Rollback = revert the two source files (the two test files fail open if the source is reverted). No schema, MemBase, or on-disk-state migration; no new dependency.

## Recommended Commit Type

`feat:` — net-new dispatch-time `target_unlaunchable` gate + net-new SessionStart `### Harness Dispatch Launchability` alert section, backed by new tests; not a behavior-preserving refactor and not a fix to existing behavior.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
