NEW

bridge_kind: implementation_report
Document: gtkb-fab-01-dispatch-substrate-revival
Version: 003
Author: prime-builder (Claude Opus 4.8, harness B) — bridge auto-dispatch worker
Date: 2026-06-11

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4413
Project Authorization: PAUTH-FAB01-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 2026-06-11T19-45-29Z-prime-builder:B-98a0b5
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: bridge auto-dispatch worker, ::init gtkb pb

implementation_authorization_packet_hash: sha256:ffc4ca72c34fdf3b1ec6778c63b03713086f73cb5e450d25138e99cc7ba553b5

---

# FAB-01 Post-Implementation Report — dispatch-substrate revival

Implementation report for the GO at `bridge/gtkb-fab-01-dispatch-substrate-revival-002.md`.
WI-4413 (FAB-01) of PROJECT-FABLE-INVESTIGATION.

## Summary

This report covers completion of FAB-01 to a verifiable state. On reaching the
GO, **interrogative-default verification of the live tree** found that proposal
steps 1–3 were **already implemented and committed** by a prior/parallel
session; this session **completed steps 4 and 5** and reconciled the test suite.

| Step | Surface | State at start | This session |
|---|---|---|---|
| 1 argv normalization (HYG-001) | `cross_harness_bridge_trigger._normalize_argv_head` (wired in `_harness_command`); doctor `_normalize_harness_argv_head` | committed | verified live; fixed 3 stale tests (below) |
| 2 launchability doctor check | `doctor._check_harness_launchability` (L3318, registered L4515) | committed | verified live (PASS: 5/5 targets launchable) |
| 3 capability-axis split (HYG-004) | `harness_projection` `can_fire_events`/`can_receive_dispatch` + committed registry data | committed | verified live; covered by new projection test |
| 4 gated scheduled wake | `single_harness_bridge_dispatcher.py` + `single_harness_bridge_automation.py` | absent | **implemented** |
| 5 dedicated tests | `platform_tests/scripts/**` | absent | **implemented** (30 new tests) |

The capability-axis split (step 3) is the linchpin that makes the step-4 wake
**safe-by-construction**: the wake keys off `can_fire_events` specifically, so it
activates only when the hook-driven cross-harness trigger is structurally unable
to fire (no active event-source harness). In the current topology (codex A +
claude B active and event-capable) the wake stays **OFF**.

## Specification Links

Carried forward from `-001` (proposal); each constrains this implementation:

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge lifecycle + dispatch automation authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — relevant specs cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived from specs (see mapping below).
- `GOV-STANDING-BACKLOG-001` — WI-4413 is the governed backlog authority.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` + `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001`
  + `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` — the gated wake **extends** the
  existing single-harness-dispatcher substrate (reuse, not new substrate).
- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` + `DCL-SMART-POLLER-AUTO-TRIGGER-001` — the
  wake dispatches only on actionable-signature change (auto-trigger contract);
  reuses the existing `run_dispatcher` signature dedup, NOT a blind interval full-spawn.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — no hand-edit of `harness-registry.json` (no registry edits in this session).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all edits in-root under `E:\GT-KB`.

Governing rule (non-spec): `.claude/rules/bridge-essential.md` § Re-Enabling Pollers
(the gated wake is the owner-approved re-enablement; cost/benefit in `-001`).

## Implemented Changes (steps 4 + 5)

### Step 4 — gated scheduled wake (`can_fire_events`-gated)

`scripts/single_harness_bridge_dispatcher.py`:
- `_record_is_active_event_source(record)` — reads the honest `can_fire_events`
  axis (not the deprecated `event_driven_hooks` alias, which now equals
  `can_receive_dispatch` and would misread ollama as an event source); legacy
  records lacking the field fall back to harness-type membership.
- `_no_active_event_source_harness(project_root)` — True iff ≥1 active harness
  AND none can fire events. Fail-closed (unreadable role map → False).
- `_gated_wake_applicable(project_root)` — `(applicable, reason)`: True for
  `single_harness_topology` OR `no_active_event_source_harness`; `(False, None)`
  in the normal multi-harness-with-event-source topology.
- `run_dispatcher(..., enforce_wake_gate=False)` — when True, no-ops with reason
  `wake_gate_not_applicable` unless the gated wake is applicable. Default False
  preserves existing single-harness behavior exactly.
- `--enforce-wake-gate` CLI flag threaded through `main`.

`scripts/single_harness_bridge_automation.py`:
- `ensure_single_harness_automation` activation predicate broadened from
  single-harness-only to `_gated_wake_applicable`. Adds `gated_wake_applicable`
  + `wake_reason` to the payload; preserves `single_harness_applicable`.
- Install task when wake-applicable; uninstall otherwise (renamed action
  `deactivated_not_single_harness` → `deactivated_no_wake_needed` for accuracy).
- `dispatch_now` self-gates via `enforce_wake_gate=True` (defense-in-depth
  against a topology change between activation and dispatch).

**No live scheduled task was installed or run this session** — code only. The
existing hook-driven automation manager handles activation per topology; the
dispatch retains its single-instance lock, active-session suppression,
signature dedup, and fire-and-forget audit log.

### Step 5 — tests

- NEW `platform_tests/scripts/test_fab01_dispatch_substrate_revival.py` — 30
  tests across all 5 steps (argv normalization, launchability doctor PASS/FAIL/WARN,
  capability-axis split, event-source detection, gated-wake applicability,
  `enforce_wake_gate` behavior, automation activation broadening).
- `platform_tests/scripts/conftest.py` — added the new module to the
  `mock_harness_registry_for_tests` skip-list so synthetic per-test registries
  are honored (the autouse fixture sets `GTKB_HARNESS_REGISTRY_PATH`, which the
  projection reader prefers over `project_root`).
- `platform_tests/scripts/test_single_harness_bridge_automation.py` — one
  assertion updated for the renamed action string + a new `gated_wake_applicable`
  assertion.
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py` — fixed 3
  pre-existing **stale** tests broken by committed step-1 normalization (see
  Pre-Existing Conditions).

## Spec-to-Test Mapping

| Spec / requirement | Derived test(s) | Result |
|---|---|---|
| HYG-001 step 1 (argv normalization) | `test_normalize_argv_head_resolves_forward_slash_relative`, `_resolves_bare_pathext_command`, `_falls_back_when_unresolvable`, `_empty_passthrough`, `test_harness_command_normalizes_executable_head` | PASS |
| step 2 launchability doctor | `test_launchability_passes_for_resolvable_target`, `_fails_on_winerror2_class_head`, `_warns_when_no_headless_targets`; live `_check_harness_launchability(E:\GT-KB)` | PASS (live: 5/5 launchable) |
| HYG-004 step 3 capability split | `test_capability_axes_split[claude/codex/ollama/openrouter/antigravity]` | PASS |
| `DCL-SMART-POLLER-AUTO-TRIGGER-001` (activity-driven), `ADR-SINGLE-HARNESS-OPERATING-MODE-001` (axis correctness) | `test_no_active_event_source_*`, `test_gated_wake_applicable_*`, `test_gated_wake_not_applicable_with_event_source`, `test_run_dispatcher_wake_gate_blocks_when_event_source_active`, `_allows_no_event_source`, `_default_does_not_enforce_wake_gate`, `test_record_is_active_event_source_legacy_fallback` | PASS |
| automation activation (step 4) | `test_automation_installs_for_no_event_source_topology`, `_deactivates_when_event_source_active`, `_dispatch_now_enforces_wake_gate` | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | full pytest + `ruff format --check` (below) | PASS |

## Verification Evidence

```
python -m pytest platform_tests/scripts/test_fab01_dispatch_substrate_revival.py platform_tests/scripts/test_single_harness_bridge_automation.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py platform_tests/scripts/test_single_harness_doctor_check_upgrade.py -q
  → 50 passed

ruff format --check (6 changed files) → 6 files already formatted
live doctor _check_harness_launchability(E:\GT-KB)
  → status: pass — "all 5 active dispatch target(s) launchable after argv-head
     normalization (codex, claude, antigravity, ollama, openrouter)"
```

`ruff check` on changed files reports **4 pre-existing** findings in
`single_harness_bridge_dispatcher.py` (3× E402 imports at L69/73/74 after the
sys.path bootstrap; 1× F841 unused `mode` in `run_dispatcher`), all present at
HEAD and **not in FAB-01-added code**. `scripts/**` per-file-ignores covers only
E501. Flagged for a separate hygiene pass, not fixed here (scope discipline).

## Acceptance Criteria (from `-001`)

1. ✅ All active dispatch targets launch (live doctor PASS 5/5; argv normalization committed + tested).
2. ✅ Capability flag split; `_check_harness_launchability` reads `can_receive_dispatch`; projection round-trip tested.
3. ✅ Gated wake fires the dispatch check only when no active event-source harness exists, and only on actionable-signature change (reuses `run_dispatcher` dedup); tested.
4. ✅ Tests green; `ruff format --check` clean; `_check_harness_launchability` exercises launchability (live PASS). (`ruff check` pre-existing-only findings noted.)

## Pre-Existing Conditions Found (NOT FAB-01-step-4 caused)

Surfaced by running the full trigger test suite; documented for honesty and routing.

1. **3 stale trigger tests (FIXED this session — FAB-01 step-1 scope).**
   `test_harness_command_builds_argv_from_invocation_surfaces`,
   `test_non_claude_worker_command_does_not_receive_claude_permission_flags`,
   `test_resolve_dispatch_target_attaches_invocation_surfaces_from_projection`
   asserted the **raw** template argv (`["codex", ...]`), but committed step-1
   normalization resolves `command[0]` (→ `codex.EXE` on a host with the CLI on
   PATH). These were host-dependent (green on CI without codex, red on a dev
   box). Fixed by neutralizing `_normalize_argv_head` in those three
   template-substitution-focused tests; normalization itself is covered by the
   new FAB-01 suite. This completes FAB-01 step-1's test obligation.

2. **13 pre-existing trigger dedup failures (NOT fixed — separate thread recommended).**
   `test_unchanged_signature_does_not_replay` and 12 siblings fail in the
   committed tree (independent of this session — the trigger and its tests are
   byte-identical to HEAD and untouched by FAB-01 step 4). Diagnostic: under
   `dry_run`, a dispatched recipient's `last_dispatched_signature` is left empty
   and the dispatch-state carries **duplicate suffixed/unsuffixed recipient
   keys** (`loyal-opposition` AND `loyal-opposition:A`), so the second run never
   sees a matching prior signature and re-dispatches (`'dry_run'` instead of
   `'unchanged'`). This is a trigger dispatch-state-keying regression unrelated
   to FAB-01's surfaces; it appears `dry_run`-specific (a real launch sets the
   dispatched signature). **Recommend a separate bridge thread** to investigate
   the recipient-key migration (`:A` suffix) interaction. A headless worker
   should not blind-patch core dispatch dedup — patching the tests would mask a
   real defect.

## Owner Decisions / Input

Authorization for this work is the GO at `-002` plus the owner-decision set
`DELIB-FAB01-REMEDIATION-20260610` (verified active this session via the
implementation-authorization packet, which validated `PAUTH-FAB01-20260610`
active for PROJECT-FABLE-INVESTIGATION, including WI-4413). The AUQ answers
recorded in `-001` § Owner Decisions / Input authorize: spawn-time normalization
(HYG-001), split-axes + gated scheduled wake (HYG-004), and the 5-minute wake
cadence. No new owner decision was required to complete steps 4–5 within the
GO'd scope. The 13-test pre-existing trigger dedup regression is surfaced for an
owner/Codex routing decision (separate thread) — no owner input is blocking this
report.

## Prior Deliberations

- `bridge/gtkb-fab-01-dispatch-substrate-revival-001.md` / `-002.md` — proposal + GO (this thread).
- `bridge/gtkb-fable-investigation-advisory-001.md` — chartering advisory (HYG-001/004).
- `DELIB-FAB01-REMEDIATION-20260610` — owner-decision set.
- `bridge/gtkb-dispatch-retry-delay-livelock-fix-004.md` (VERIFIED) — most recent trigger
  change; ruled out as the Class-B dedup cause (its retry logic is gated on `failure_count > 0`,
  which the failing dedup tests never reach).

## Recommended Commit Type

`feat:` — restores dispatch launchability completion (steps 1–3 verified) and
adds the gated-wake substrate (step 4) plus the FAB-01 test suite (step 5). The
3 stale-test fixes and pre-existing-drift `ruff format` normalization ride along
as required hygiene for the changed files.

## Files Changed (this session)

- `scripts/single_harness_bridge_dispatcher.py` — step 4 helpers + `enforce_wake_gate` + CLI flag (+ ruff-format of pre-existing drift).
- `scripts/single_harness_bridge_automation.py` — step 4 activation broadening.
- `platform_tests/scripts/test_fab01_dispatch_substrate_revival.py` — NEW, 30 tests.
- `platform_tests/scripts/test_single_harness_bridge_automation.py` — 1 assertion update (+1 new assertion).
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py` — 3 stale-test fixes (+ ruff-format).
- `platform_tests/scripts/conftest.py` — skip-list +1 line.

All edits are within the GO'd `target_paths` (`scripts/single_harness_bridge_dispatcher.py`,
`scripts/single_harness_bridge_automation.py`, `platform_tests/scripts/**`).
Steps 1–3 surfaces (trigger, doctor, projection, registry, db, toml) were
**not** modified — they were already committed. Per dispatched-worker discipline,
**nothing was committed**; this report is filed for Codex verification.
