NEW

# gtkb-wi4790-slice-1-dispatch-monitor-detection — Active-monitoring slice 1: read-only dispatch failure-class / saturation / corrupt-output detector

bridge_kind: prime_proposal
Document: gtkb-wi4790-slice-1-dispatch-monitor-detection
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-26 UTC

author_identity: claude
author_harness_id: B
author_session_context_id: 34aad0ba-5c20-4abf-9003-ce498e7adf34
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-MINVIABLE-ACTIVATION-DRIVE-2026-06-26
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4790

target_paths: ["scripts/ops/dispatch_monitor.py", "platform_tests/scripts/test_dispatch_monitor.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4790 (Phase 3, active monitoring + correct health) is the gating capability for activating the GT-KB dispatcher daemon: the daemon cannot safely own live spawning without proactive detection of the failure modes that previously fed the storm. This is the first of three slices and delivers the **detection foundation** — a self-contained, read-only module that classifies recent dispatch outcomes into a structured monitoring snapshot the later slices (liveness probing; hold->auto-remediate->escalate) consume.

It is deliberately pure and read-only: it observes dispatch evidence and emits a snapshot, mutating no dispatch state. It does not change dispatch behavior; it makes the failure modes machine-detectable.

## Design (for LO review)

New module `scripts/ops/dispatch_monitor.py`, mirroring the gather-vs-pure-decision split already used by `scripts/ops/storm_watchdog_reap.py`:

- **Dataclasses.** `DispatchOutcome` (one parsed dispatch-run / dispatch-failures record: `role`, `harness_id`, `exit_code`, `has_verdict`, `stdout_bytes`, `error_message`, `created_epoch`, `pid_alive`); `RoleMonitorSnapshot` (`role`, `error_class_counts`, `total`, `corrupt_output_count`, `saturation_ratio`, `stale_live_count`, `healthy`); `DispatchMonitorSnapshot` (`per_role`, `generated_at`, `window_seconds`).
- **`classify_outcome(outcome) -> str`** — the canonical error-class taxonomy, parity-checked against the trigger's existing `_classify_failure_record` / `_classify_invocation_outcome`: `success`, `worker_timeout` (exit 124 / lifetime kill), `provider_failure`, `corrupt_output`, `cap_reached`, `no_active_target`, `subprocess_failed`, `other`. **corrupt_output** is the killed-mid-output signature observed this session (a worker with a non-zero `exit_code` AND `stdout_bytes == 0` AND `has_verdict == False`).
- **`compute_snapshot(outcomes, caps, now, *, window_seconds) -> DispatchMonitorSnapshot`** — a pure function (no clock / IO / randomness inside), so it is fully unit-testable. Computes per-role error-class distribution over the window, `corrupt_output_count`, `saturation_ratio` (in-flight vs per-role cap), `stale_live_count` (records marked live whose `pid_alive` is False or whose age exceeds the max-lifetime backstop — the "phantom live worker" class diagnosed this session), and a `healthy` boolean per a conservative rule (no saturation, no corrupt-output streak, no stale-live accumulation).
- **`main` glue** — read-only gather from the dispatch-runs dir + `dispatch-failures.jsonl` + `dispatch-state.json`, parse into `DispatchOutcome`s, call `compute_snapshot`, emit JSON to stdout. No state mutation.

Boundary: the canonical classifier lives here (daemon-facing). A later slice may refactor the transitional trigger to consume it, but this slice does NOT touch the trigger (which is retired at cutover) — it is self-contained to keep the slice small and the decision module reusable by the daemon.

## Specification Links

- `ADR-DISPATCHER-ARCHITECTURE-001` — architecture-of-record; the daemon owns liveness/quality/health, and active monitoring (this WI) is the health capability the daemon needs before it can own spawning.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — the centralized dispatch service the monitoring snapshot feeds.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the snapshot derives from fresh canonical reads of the dispatch evidence (runs / failures / state), not cached summaries.
- `GOV-RELIABILITY-FAST-LANE-001` — context; this is authorized project work under PAUTH-MINVIABLE-ACTIVATION-DRIVE-2026-06-26, not a fast-lane defect.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; filed as the next numbered bridge file (`bridge/gtkb-wi4790-slice-1-dispatch-monitor-detection-001.md`) in the append-only versioned bridge chain, with no prior version rewritten.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — satisfied: cites all governing specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — satisfied: Project / Work Item / Project Authorization metadata present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied: spec-to-test mapping below.
- `GOV-STANDING-BACKLOG-001` — WI-4790 is the governing backlog item.

## Prior Deliberations

- `DELIB-20266138` — owner decision: minimum-viable activation driven autonomously (this drive); WI-4790 is the first critical-path slice.
- `DELIB-20266084` — owner authorization of the WI-4787 daemon foundation this monitoring serves.
- `DELIB-20266104` — surgical storm-watchdog liveness-awareness; the corrupt-output / stale-live classes here generalize that reaper's evidence model.
- `DELIB-20266081` — WI-4789 per-role dispatch-health boundary; this slice extends health from passive findings to active error-class detection.

## Owner Decisions / Input

- Owner AUQ (2026-06-26): chose **"Minimum-viable activation, autonomous"** — drive WI-4790 -> WI-4788 -> WI-4848 slice by slice, reporting only blockers/owner-gated decisions until ready to activate. Recorded as `DELIB-20266138`; authorized envelope `PAUTH-MINVIABLE-ACTIVATION-DRIVE-2026-06-26`.
- Owner directive (2026-06-25): topology Claude(B)=Prime Builder, Cursor(E)=Loyal Opposition; Codex(A) and Antigravity(C) unavailable today. Cursor (E) reviews this proposal.
- No further owner decision is required for this read-only detection slice; it changes no runtime dispatch behavior.

## Requirement Sufficiency

Existing requirements sufficient — `ADR-DISPATCHER-ARCHITECTURE-001` + `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` constrain the monitoring capability; the error-class taxonomy is derived from the observed dispatch failure modes. No new or revised requirement is needed before implementation.

## Spec-Derived Verification Plan

| Spec / clause | Test | Assertion |
|---|---|---|
| ADR-DISPATCHER-ARCHITECTURE-001 (active health detection) | `test_classify_outcome_taxonomy` (new) | Each synthetic outcome classifies to the expected error-class; corrupt_output requires nonzero exit + 0-byte stdout + no verdict (the killed-mid-output signature). |
| GOV-SOURCE-OF-TRUTH-FRESHNESS-001 (fresh evidence) | `test_compute_snapshot_per_role_distribution` (new) | `compute_snapshot` returns per-role error-class counts, corrupt_output_count, saturation_ratio, and stale_live_count matching the seeded outcomes; pure (same inputs -> same snapshot). |
| ADR-DISPATCHER-ARCHITECTURE-001 (saturation + stale detection) | `test_snapshot_flags_saturation_and_stale_live` (new) | A role at/over its cap reports saturation_ratio >= 1.0 and healthy=False; live-marked records with dead pids / over-lifetime age increment stale_live_count. |
| No-regression | `ruff check` + `ruff format --check` on the new files; the module imports cleanly and `main` runs read-only against the live state dirs without mutation | green |

Commands (run pre-report): `python -m pytest platform_tests/scripts/test_dispatch_monitor.py -q --tb=short`; `ruff check <new .py>`; `ruff format --check <new .py>`.

## Risk / Rollback

- Risk: low. The module is read-only and additive (a new file + its test); it mutates no dispatch state and changes no dispatch behavior. It is consumed by later slices, not wired into the live path in this slice.
- Rollback: delete the two new files; nothing else references them yet. Append-only KB untouched (`kb_mutation_in_scope: false`).
- Out of scope (later slices): proactive liveness probing (slice 2), the hold->auto-remediate->escalate loop (slice 3), wiring the snapshot into the daemon's health, and any trigger refactor. The quality/consensus subsystem is deferred per the min-viable decision.
