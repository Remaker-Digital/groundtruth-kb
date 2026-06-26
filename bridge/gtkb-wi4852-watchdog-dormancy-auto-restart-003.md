REVISED
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: e150e9ce-4657-4130-9e10-af48d3e79a44
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude interactive Prime Builder auto-process

# Implementation Proposal (REVISED): WI-4852 watchdog-dormancy auto-restart as a health_response remediation action

Document: gtkb-wi4852-watchdog-dormancy-auto-restart
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-06-26 UTC
Responds to: bridge/gtkb-wi4852-watchdog-dormancy-auto-restart-002.md
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4852
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4852-WATCHDOG-DORMANCY-AUTO-RESTART

## target_paths

```json
["scripts/ops/dispatch_monitor.py", "scripts/gtkb_dispatcher_daemon.py", "scripts/ops/harness_storm_watchdog.ps1", "platform_tests/scripts/test_dispatch_monitor.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py"]
```

## Revision Note

REVISED after the `-002` GO for a self-detected **format-only** defect: the `-001`
`target_paths` used a plain `target_paths:` line followed by a multi-line fenced
JSON block. `scripts/implementation_authorization.py begin` (`extract_target_paths`)
recognizes only (a) inline single-line `target_paths: [...]` or (b) a
`## target_paths` markdown heading with a fenced JSON list; the `-001` form
matched neither, so `begin` reported "missing concrete target_paths" and blocked
implementation despite the GO. This revision reformats `target_paths` to the
`## target_paths` heading + fenced-JSON form. **Scope is identical to the GO'd
`-001` (same five target paths).**

This revision also folds in the `-002` GO's settled design guidance so the
re-review is trivial:

- **Option B accepted** (heartbeat artifact age vs threshold). Option A
  (schtasks LastRunTime) is rejected.
- The storm watchdog **already writes** `.gtkb-state/ops/storm-watchdog-heartbeat.txt`
  each run (`scripts/ops/harness_storm_watchdog.ps1`). The implementation
  **consumes that existing artifact**; it does NOT add a parallel heartbeat write
  unless a format change is required (documented if so). `harness_storm_watchdog.ps1`
  is retained in `target_paths` for read/verification scope but is expected to be
  unmodified.

## Summary

The dispatch storm class (WI-4670 / WI-4828) is contained by the storm watchdog
(`scripts/ops/harness_storm_watchdog.ps1` + the pure decision module
`scripts/ops/storm_watchdog_reap.py`), which reaps orphaned/over-lifetime worker
process families so a reaped worker's bridge item does not loop as re-dispatched
work. That containment depends on the watchdog actually running. If the watchdog
scheduled task stops firing (disabled, deregistered, host reboot without
re-registration, or silent task-scheduler failure), corpses and over-lifetime
stragglers accumulate undetected and the storm class can recur with no signal.

WI-4790 built the daemon's active-monitoring health-response loop
(`hold -> auto-remediate -> escalate`) in `scripts/ops/dispatch_monitor.py`
(`health_response()` returning per-role `ResponseAction(action, remediation_hint)`
with hints `reap_stale_dispatch_runs` and `drain_and_hold`) and wired it into the
daemon tick (`scripts/gtkb_dispatcher_daemon.py`). WI-4852 extends that loop with
one new remediation capability: detect when the storm watchdog itself is dormant
and emit an auto-restart remediation action that the daemon executes (fail-soft),
so the watchdog's own liveness becomes a monitored, self-healing condition rather
than a silent single point of failure.

This is the WI-4790 / WI-4848 daemon follow-on named in the WI-4852 backlog entry.

## Specification Links

- ADR-DISPATCHER-ARCHITECTURE-001 — governing architecture decision for the
  dispatcher daemon, its active-monitoring health-response loop, and remediation
  actions. WI-4852 adds a remediation action under this ADR. (Linked in the
  WI-4852 PAUTH.)
- GOV-FILE-BRIDGE-AUTHORITY-001 — this proposal is a bridge artifact under
  `bridge/`; bridge authority and GO/NO-GO discipline apply.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this proposal cites
  every relevant governing specification and derives its tests from them.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — the verification plan below
  maps each behavioral clause to an executed test before VERIFIED.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — all touched paths are GT-KB platform
  source/tests in-root under `E:\GT-KB`; no application or out-of-root path is a
  dependency.
- GOV-STANDING-BACKLOG-001 — WI-4852 is the canonical backlog authority record
  for this work; no bulk backlog operation is performed.
- GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001 — the new behavior is
  enforced by spec-derived tests over pure decision functions plus daemon
  execution tests.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — advisory; durable artifact + test
  coverage for the new remediation surface.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — advisory; this work adds code + test
  artifacts and advances WI-4852 toward verified, an artifact lifecycle trigger.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — advisory; the work item, owner decision,
  specification, ADR/DCL linkage, and backlog record are preserved as durable
  artifacts.

## Prior Deliberations

- DELIB-20266192 (owner_conversation / owner_decision) — owner AUQ 2026-06-26
  authorizing this bounded WI-4852 implementation; source of the covering PAUTH.
- bridge/gtkb-wi4852-watchdog-dormancy-auto-restart-002.md — the `-002` GO
  (independent Cursor LO, harness E) accepting Option B and the existing-heartbeat
  approach; this revision folds in its conditions.
- DELIB-20266132 — owner decision re-scoping/closing WI-4670 on storm-containment
  evidence and routing the health-PASS-for-LO-swarm gate to WI-4790; WI-4852 is
  the watchdog-liveness follow-on under that program.
- DELIB-20266137 / DELIB-20266138 — dispatcher-reliability fixes-then-phases and
  minimum-viable-activation owner decisions establishing the daemon
  health-response substrate this work extends.
- Bridge threads gtkb-wi4790-slice-2-health-response (VERIFIED) and
  gtkb-wi4790-slice-3-daemon-health-wiring (VERIFIED) — the health-response
  decision core and daemon wiring this proposal extends.
- WI-4828 / scripts/ops/storm_watchdog_reap.py docstring — the liveness-aware reap
  decision whose dormancy is the failure mode this work detects.

## Requirement Sufficiency

Existing requirements sufficient. ADR-DISPATCHER-ARCHITECTURE-001 governs the
daemon health-response and remediation loop; WI-4852 adds a remediation action
within that established surface. No new or revised requirement is needed before
implementation; no formal spec/governance mutation is in scope.

## Design (settled per -002 GO)

Three behavioral pieces, conforming to the five `-002` GO conditions:

1. Dormancy detection (pure, in `dispatch_monitor.py`): a side-effect-free
   function `watchdog_dormancy(last_evidence_epoch, now, threshold_seconds)` (no
   clock/IO inside) returning a structured dormancy verdict (`dormant: bool`,
   `age_seconds`, `reason`). Default `threshold_seconds` = 2x the watchdog
   cadence; a missing/zero `last_evidence_epoch` is treated as dormant.

2. Remediation action (in `dispatch_monitor.py`): a daemon-level (NOT per-role)
   record with `remediation_hint = "restart_storm_watchdog"` emitted when
   dormancy is detected. Per-role `health_response()` is unchanged; the watchdog
   check is a sibling daemon-level surface so the per-role contract is preserved
   (GO condition 2).

3. Execution (in `gtkb_dispatcher_daemon.py`): the daemon reads the existing
   heartbeat artifact `.gtkb-state/ops/storm-watchdog-heartbeat.txt` (GO condition
   1 — consume, do not duplicate), parses its epoch, computes dormancy, and on
   `restart_storm_watchdog` re-runs/re-enables the watchdog scheduled task
   **fail-soft** (a restart failure is recorded in status.json / tick result and
   never aborts the tick — GO condition 3), mirroring the existing fail-soft
   monitoring contract (`test_run_tick_monitoring_failsoft`). The platform restart
   step may remain Windows scheduled-task bound; pure detection tests do not
   require live task registration (GO condition 5).

## Test Plan (spec-to-test mapping)

| Specification clause | Test | File |
|---|---|---|
| ADR-DISPATCHER-ARCHITECTURE-001 (remediation: dormancy detected when evidence age exceeds threshold) | test_watchdog_dormancy_detected_when_stale | platform_tests/scripts/test_dispatch_monitor.py |
| ADR-DISPATCHER-ARCHITECTURE-001 (remediation: fresh watchdog evidence is not dormant) | test_watchdog_dormancy_not_flagged_when_fresh | platform_tests/scripts/test_dispatch_monitor.py |
| ADR-DISPATCHER-ARCHITECTURE-001 (remediation: missing/zero evidence treated as dormant) | test_watchdog_dormancy_missing_evidence_is_dormant | platform_tests/scripts/test_dispatch_monitor.py |
| ADR-DISPATCHER-ARCHITECTURE-001 (daemon emits restart_storm_watchdog action on dormancy) | test_run_tick_emits_restart_watchdog_when_dormant | platform_tests/scripts/test_gtkb_dispatcher_daemon.py |
| GOV-SOURCE-OF-TRUTH-FRESHNESS-001 (fail-soft: restart failure does not abort tick) | test_run_tick_watchdog_restart_failsoft | platform_tests/scripts/test_gtkb_dispatcher_daemon.py |

Commands (run against changed files before the post-implementation report):

```text
python -m pytest platform_tests/scripts/test_dispatch_monitor.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --tb=short
python -m ruff check scripts/ops/dispatch_monitor.py scripts/gtkb_dispatcher_daemon.py
python -m ruff format --check scripts/ops/dispatch_monitor.py scripts/gtkb_dispatcher_daemon.py
```

## Risk / Rollback

- Risk: an over-eager dormancy threshold restarts a healthy-but-slow watchdog.
  Mitigation: conservative default threshold (2x cadence), fail-open below
  threshold, restart is idempotent (re-run of an already-scheduled task).
- Risk: restart execution is platform-specific. Mitigation: fail-soft execution
  (status.json record, tick never aborts); pure detection is fully testable
  independent of the platform restart step.
- Rollback: changes are additive (a new pure function, a new daemon-level action,
  fail-soft execution consuming an existing heartbeat). Reverting the changed
  target files restores prior behavior; no schema, governed-record, or narrative
  change is involved.

## Bridge Filing Discipline

This revision is filed as the next numbered bridge file
(`bridge/gtkb-wi4852-watchdog-dormancy-auto-restart-003.md`) under the canonical
append-only numbered-file chain. Prior versioned bridge files (`-001` NEW, `-002`
GO) are never rewritten or deleted; this REVISED version is added as a new
numbered file so the numbered file chain remains the canonical audit trail per
GOV-FILE-BRIDGE-AUTHORITY-001.

## Owner Decisions / Input

- DELIB-20266192 — owner AUQ (2026-06-26) selected "TIER-1 dispatcher: WI-4852"
  for authorization, which minted the covering PAUTH
  PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4852-WATCHDOG-DORMANCY-AUTO-RESTART
  (allowed mutation classes: source + test_addition; linked spec
  ADR-DISPATCHER-ARCHITECTURE-001). No further owner decision is required to
  re-review this REVISED proposal. The design decision (Option B) was settled by
  the `-002` GO; this revision only reformats `target_paths` for
  `implementation_authorization.py begin` parseability and folds in the GO
  conditions.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
