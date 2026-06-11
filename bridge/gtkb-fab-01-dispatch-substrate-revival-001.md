NEW

bridge_kind: prime_proposal
Document: gtkb-fab-01-dispatch-substrate-revival
Version: 001
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-10

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4413
Project Authorization: PAUTH-FAB01-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 07ef97df-2cb3-45a4-9c32-be60d702f29c
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb

target_paths: ["scripts/cross_harness_bridge_trigger.py", "scripts/run_with_status.py", "scripts/single_harness_bridge_dispatcher.py", "scripts/single_harness_bridge_automation.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/harness_projection.py", "harness-state/harness-registry.json", "config/agent-control/harness-capability-registry.toml", "groundtruth.db", "platform_tests/scripts/**"]

KB mutation: the harnesses-table capability-flag split (event_driven_hooks -> can_fire_events + can_receive_dispatch) is a MemBase schema/data change in `groundtruth.db`; the regenerated projection writes `harness-state/harness-registry.json`. `groundtruth.db` is in target_paths to declare it.

---

# FAB-01 — Restore bridge dispatch launchability + honest event-source model

WI-4413 (FAB-01) of PROJECT-FABLE-INVESTIGATION. Findings: HYG-001, HYG-004.
Source advisory: `bridge/gtkb-fable-investigation-advisory-001.md`.

## Summary

Bridge auto-dispatch — the platform's self-declared top-priority infrastructure
(`bridge-essential.md`) — is **fully dead end-to-end**, two coupled causes:

- **HYG-001 (P0):** every active dispatch target fails launch with `WinError 2`.
  Reproduced root causes: ollama (D) + openrouter (F) use the relative *forward-slash*
  path `groundtruth-kb/.venv/Scripts/python.exe` (CreateProcess cannot resolve a
  relative forward-slash path); antigravity (C) uses bare argv head `gemini`, which
  exists only as `gemini.ps1/.cmd` (Python subprocess does no PATHEXT resolution).
  `run_with_status.py` catches the failure and writes exit 127; the only launchable
  harnesses (codex A, claude B) are `suspended`. Net: zero auto-dispatch.
- **HYG-004 (architecture):** commit `00b75262` flipped `event_driven_hooks`
  `false→true` for four hook-less harnesses, masking the deadlock at the *eligibility*
  check — those harnesses became valid dispatch TARGETS but none can fire events.
  The flag now lies (it encodes "dispatch here", not "can fire hooks"), and downstream
  topology logic mis-derives from it.

Owner-approved (`DELIB-FAB01-REMEDIATION-20260610`): spawn-time argv normalization +
a launchability doctor check; split the capability axes; and re-enable a **gated,
activity-driven scheduled wake** as the fallback event source.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge lifecycle + dispatch automation authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived from specs.
- `GOV-STANDING-BACKLOG-001` — WI-4413 is the governed backlog authority.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` + `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001`
  + `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` — the gated wake **extends** the
  existing single-harness-dispatcher Windows-scheduled-task pattern (reuse, not new
  substrate); the capability-axis split touches the same role/capability schema.
- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` + `DCL-SMART-POLLER-AUTO-TRIGGER-001` — the
  wake MUST dispatch only on actionable-signature change (the auto-trigger contract);
  this is what distinguishes it from the retired blind-interval pollers.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — `harness-registry.json` regenerates from the
  MemBase harnesses table; the fix goes through the table, not hand-edits.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — the doctor-check edit lands under
  `groundtruth-kb/src/groundtruth_kb/project/**`; FAB-01 adds no out-of-root
  artifacts and relocates nothing (this bridge file is under `E:\GT-KB\bridge\`).

Governing rule (non-spec): `.claude/rules/bridge-essential.md` § Re-Enabling Pollers
(the gated-wake re-enablement is owner-approved here with cost/benefit; see below).

## Prior Deliberations

- `bridge/gtkb-fable-investigation-advisory-001.md` — chartering advisory (HYG-001/004
  in the FAB-01 row); evidence frozen, do not re-derive.
- `DELIB-FABLE-GRILL-20260610-Q1..Q7` — project chartering decisions.
- `DELIB-FAB01-REMEDIATION-20260610` — this cluster's owner-decision set (AUQ batch +
  the HYG-004 wake-substrate grill).
- _HYG-004's Related Items augment the open dispatch-deadlock critique advisories and
  the scheduled-wake-restore framing work item (ids enumerated in the v1 finding);
  this proposal converts that framing into a gated, activity-driven wake. No prior
  bridge thread implements this revival._

## Owner Decisions / Input

Collected via `AskUserQuestion` + grill on 2026-06-10, persisted to
`DELIB-FAB01-REMEDIATION-20260610`:

1. **HYG-001 = Spawn-time normalization** — trigger normalizes/resolves each argv head
   (`os.path.normpath` + `shutil.which`) at spawn; portable + covers future rows; plus
   a launchability doctor check that Popens each active argv head with `--version`.
   (Rejected: fix-data-only; re-activate codex/claude; substrate=none.)
2. **HYG-004 = Split axes + gated scheduled wake** — split `event_driven_hooks` into
   `can_fire_events` vs `can_receive_dispatch`; gated wake **extends the
   single-harness-dispatcher pattern**, fires the trigger's dispatch check when no
   active event-source harness exists. (Rejected: smart-poller-as-primary;
   revert-flip + reactivate; manual-only.)
3. **Wake cadence = 5-minute tick**, owner-approved re-enablement with cost/benefit
   (below). (Rejected: 15-min; defer-the-wake.)

## Requirement Sufficiency

**Existing requirements sufficient.** Governed by `GOV-FILE-BRIDGE-AUTHORITY-001`,
the single-harness-dispatcher spec set, the smart-poller auto-trigger contract, and
`GOV-SOURCE-OF-TRUTH-FRESHNESS-001`; the specific choices are fixed by
`DELIB-FAB01-REMEDIATION-20260610`. The capability-axis split is a schema refinement
within `ADR-SINGLE-HARNESS-OPERATING-MODE-001`'s role/capability model, not a new
requirement. The launchability doctor check encodes a derived invariant.

## Re-Enablement Cost/Benefit (bridge-essential.md § Re-Enabling Pollers)

- **What is re-enabled:** a gated scheduled wake that fires the cross-harness
  trigger's dispatch check on a 5-minute tick **only when no active event-source
  (hook-bearing) harness exists**.
- **Why it is not the retired defect:** the retired OS poller (halted 2026-04-25) and
  smart poller (retired 2026-05-09) were retired for blind interval-firing of full
  spawns regardless of activity. This wake only TICKS; the trigger's existing
  actionable-signature dedup means a harness spawns **only on a changed actionable
  signature**. Tick cost is negligible; spawns occur only when there is genuinely new
  actionable work.
- **Benefit:** restores the dead Axis-1 automation layer for the hook-less active
  topology without depending on a suspended-harness interactive session.
- **Guardrail:** the retired OS/smart-poller implementations are NOT restored as the
  active path (forbidden by the PAUTH and `bridge-essential.md`); this reuses the
  governed single-harness-dispatcher substrate.

## Proposed Implementation

1. **Spawn-time argv normalization** (`scripts/cross_harness_bridge_trigger.py`
   `_harness_command`): normalize each argv head with `os.path.normpath` and resolve
   via `shutil.which` (PATHEXT-aware) before `subprocess` launch; covers all current
   and future registry rows. `run_with_status.py` inherits the normalized argv.
2. **Launchability doctor check** (`groundtruth-kb/src/groundtruth_kb/project/doctor.py`):
   Popen each active harness's argv head with `--version`; FAIL on `WinError 2`. The
   existing `_check_cross_harness_trigger` never exercised launch.
3. **Capability-axis split** (`groundtruth.db` harnesses-table schema via `db.py`;
   `harness_projection.py`; regenerated `harness-registry.json`;
   `harness-capability-registry.toml`): replace the overloaded `event_driven_hooks`
   with `can_fire_events` and `can_receive_dispatch`; update `_is_event_capable` and
   topology derivation to read the correct axis. Registry regenerates from the table
   (no hand-edits).
4. **Gated scheduled wake** (`scripts/single_harness_bridge_dispatcher.py` +
   `scripts/single_harness_bridge_automation.py`): generalize the existing
   Windows-scheduled-task dispatch substrate to also fire the cross-harness trigger's
   dispatch check on a 5-minute tick **when no active `can_fire_events` harness
   exists**; reuse the actionable-signature dedup so spawns are activity-driven.
5. **Tests** (`platform_tests/scripts/**`): argv-normalization unit tests (forward-slash
   relative / bare-PATHEXT cases); launchability-doctor test; capability-split
   projection test; wake-gate test (fires only when no event-source harness + only on
   signature change).

## Spec-Derived Verification Plan

| Spec / requirement | Derived test |
|---|---|
| HYG-001 launch fix | unit test: `_harness_command` resolves forward-slash-relative + bare-PATHEXT argv to a launchable command; doctor check FAILs on a synthetic `WinError 2` argv |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | projection regen test: split fields round-trip table→registry; no hand-edit path |
| `ADR-SINGLE-HARNESS-OPERATING-MODE-001` (axis correctness) | `_is_event_capable` reads `can_receive_dispatch`; topology derivation reads `can_fire_events`; test asserts a receive-only harness is not treated as an event source |
| `DCL-SMART-POLLER-AUTO-TRIGGER-001` (activity-driven) | wake-gate test: no spawn when signature unchanged; no tick-spawn when an active event-source harness exists |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | full `pytest platform_tests/scripts/...` + `ruff check`/`format --check` on changed `.py` |

## Acceptance Criteria

1. All active dispatch targets launch (doctor launchability check passes; a real
   dispatched subprocess starts for a signature-changed actionable batch).
2. The capability flag is split; `_is_event_capable`/topology read the correct axes;
   registry regenerates from the table.
3. The gated wake fires the dispatch check on a 5-min tick only when no active
   event-source harness exists, and only spawns on actionable-signature change.
4. Tests + ruff clean; `_check_cross_harness_trigger` now exercises launchability.

## Risk and Rollback

- **Risk:** `shutil.which` resolution differences across hosts → tests cover the
  Windows forward-slash + PATHEXT cases; normalization is additive (falls back to the
  original argv if resolution yields nothing).
- **Risk:** re-enabling a wake re-introduces churn → mitigated by the activity-driven
  signature-dedup gate (cost/benefit above); the wake is OFF when an event-source
  harness is active.
- **Rollback:** revert the trigger/dispatcher/doctor edits and the schema split
  (projection regenerates); disable the scheduled task. No data loss; the harnesses
  table is append-only/versioned.

## Bridge Protocol Compliance

This proposal is filed at `bridge/gtkb-fab-01-dispatch-substrate-revival-001.md` with a
matching `NEW` entry inserted at the top of `bridge/INDEX.md`; it is append-only and
deletes or rewrites no prior bridge version. The HYG-004 capability-axis change touches
the MemBase harnesses table and the dispatch trigger's eligibility logic — it does NOT
alter `bridge/INDEX.md` as canonical workflow state or the bridge versioning discipline
(`GOV-FILE-BRIDGE-AUTHORITY-001` § INDEX-is-canonical is preserved). The gated wake
dispatches *into* the existing bridge protocol; it does not change INDEX authority.

## Recommended Implementation Routing

**Mixed.** The argv normalization + doctor check are mechanical (cheap-model-eligible
under supervision), but the capability-axis schema split + the gated-wake substrate +
the scheduled-task wiring are governance-sensitive and touch the harnesses-table SoT
and the retired-poller boundary — **reserve those for Claude/Codex-supervised
execution**. Coordinate with FAB-10 (claim contract/telemetry) so the wake and the
claim handoff align.

## Recommended Commit Type

`feat:` — restores dispatch launchability + adds the split capability axes, the
launchability doctor check, and the gated wake substrate.
