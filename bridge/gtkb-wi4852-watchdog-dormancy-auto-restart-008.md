NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 3972336c-f3d6-47b7-bc56-051c146e2f7c
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude interactive Prime Builder auto-process

# Post-Implementation Report: WI-4852 watchdog-dormancy auto-restart

Document: gtkb-wi4852-watchdog-dormancy-auto-restart
Version: 008
Author: Prime Builder (Claude, harness B)
Date: 2026-06-26 UTC
Responds to: bridge/gtkb-wi4852-watchdog-dormancy-auto-restart-007.md
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4852
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4852-WATCHDOG-DORMANCY-AUTO-RESTART

target_paths: ["scripts/ops/dispatch_monitor.py", "scripts/gtkb_dispatcher_daemon.py", "scripts/ops/harness_storm_watchdog.ps1", "platform_tests/scripts/test_dispatch_monitor.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py"]

## Summary

Implements WI-4852 per the `-006` REVISED proposal (GO at `-007`): storm-watchdog
dormancy detection plus a daemon-executed auto-restart remediation action. The
pure detector (`watchdog_dormancy`) lives in `scripts/ops/dispatch_monitor.py`;
the daemon reads the existing storm-watchdog heartbeat artifact, computes
dormancy, and on a dormant verdict executes a fail-soft restart of the watchdog
scheduled task. `scripts/ops/harness_storm_watchdog.ps1` is unmodified (it
already writes the heartbeat artifact this work consumes).

This report carries forward the three implementation corrections this session
made over the in-tree starting state (see § Implementation Detail and § Design
Decision for Reviewer); they are flagged explicitly so the reviewer can weigh
them.

## Specification Links

- ADR-DISPATCHER-ARCHITECTURE-001 — governing architecture decision for the
  dispatcher daemon, its active-monitoring health-response loop, and remediation
  actions. WI-4852 adds a remediation action under this ADR.
- GOV-FILE-BRIDGE-AUTHORITY-001 — bridge artifact under `bridge/`; bridge
  authority, GO/NO-GO discipline, and the canonical append-only numbered-file
  chain apply.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — the linked
  specifications are carried forward from the `-006` proposal.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — the spec-to-test mapping
  below maps each behavioral clause to an executed test.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — all touched paths are GT-KB platform
  source/tests in-root under `E:\GT-KB`; no application or out-of-root path is a
  dependency.
- GOV-STANDING-BACKLOG-001 — WI-4852 is the canonical backlog authority record
  for this work. Its CLAUSE-VISIBILITY-BULK-OPS does not apply: this is a single
  WI implementation, not a bulk backlog operation, so it produces no inventory
  artifact or review-packet and needs no bulk-action formal-artifact-approval
  packet.
- GOV-SOURCE-OF-TRUTH-FRESHNESS-001 — the fail-soft contract (a restart failure
  is recorded, never aborts the tick) is spec-derived and tested.
- GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001 — the new behavior is
  enforced by spec-derived tests over the pure decision function plus daemon
  execution tests.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — advisory; durable code + test artifacts.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — advisory; adds code + tests and advances
  WI-4852 toward verified.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — advisory; the work item, owner decision,
  ADR/DCL linkage, and backlog record are preserved as durable artifacts.

## Prior Deliberations

- DELIB-20266192 (owner_conversation / owner_decision) — owner AUQ 2026-06-26
  authorizing the bounded WI-4852 implementation; source of the covering PAUTH.
- DELIB-20266194 (owner_conversation / owner_decision) — owner AUQ 2026-06-26
  authorizing the NEW-implementation-proposal generation loop over the whole
  backlog (PB picks), under which this session is operating.
- bridge/gtkb-wi4852-watchdog-dormancy-auto-restart-007.md — the `-007` GO
  (independent Cursor LO, harness E) approving REVISED `-006` for implementation.
- bridge/gtkb-wi4852-watchdog-dormancy-auto-restart-006.md — the REVISED proposal
  this report implements (Option B; consume existing heartbeat; fail-soft restart).
- bridge/gtkb-wi4852-watchdog-dormancy-auto-restart-002.md — the `-002` GO that
  settled the design (Option B).
- DELIB-20266132 / DELIB-20266137 / DELIB-20266138 — dispatcher-reliability
  program decisions establishing the daemon health-response substrate this work
  extends.

## Requirement Sufficiency

Existing requirements sufficient. ADR-DISPATCHER-ARCHITECTURE-001 governs the
daemon health-response and remediation loop; WI-4852 adds a remediation action
within that established surface. No new or revised requirement was needed; no
formal spec/governance mutation is in scope.

## Recommended Commit Type

`feat` — net-new daemon remediation capability (storm-watchdog dormancy detection
+ auto-restart) plus its tests. Matches the `-007` GO recommended commit type.
Diff stat: 4 files changed, 375 insertions(+), 14 deletions(-).

## Implementation Detail

1. `scripts/ops/dispatch_monitor.py` (+29): the pure, side-effect-free
   `watchdog_dormancy(last_evidence_epoch, now, threshold_seconds)` returning a
   `WatchdogDormancyVerdict(dormant, age_seconds, reason)`; a missing/zero epoch
   is treated as dormant; default threshold `DEFAULT_WATCHDOG_DORMANCY_THRESHOLD_SECONDS`
   = 600 (2x the assumed 5-minute watchdog cadence). `WATCHDOG_HEARTBEAT_RELPATH`
   names the consumed artifact.

2. `scripts/gtkb_dispatcher_daemon.py` (+137/-14): `_read_watchdog_heartbeat_epoch`
   reads the existing heartbeat artifact and parses its leading ISO-8601 token;
   `_restart_storm_watchdog` fail-soft re-runs the watchdog scheduled task via
   `schtasks /Run`; `run_tick` computes the dormancy verdict each tick, records it
   (and a `restart_storm_watchdog` remediation hint when dormant) in both the tick
   result and `status.json`, and executes the restart fail-soft.

3. `scripts/ops/harness_storm_watchdog.ps1`: unchanged (read/verification scope
   only; it already writes the heartbeat this work consumes).

4. Tests (`platform_tests/scripts/test_dispatch_monitor.py` +30,
   `platform_tests/scripts/test_gtkb_dispatcher_daemon.py` +193): the pure-detector
   unit tests, the real-format heartbeat fixtures, and the daemon-tick tests.

### Corrections this session made over the in-tree starting state

The WI-4852 changes were partially present in the working tree at session start
(uncommitted, no report filed). This session verified them against live behavior
and corrected three defects before reporting:

- **Heartbeat parse (functional defect).** `_read_watchdog_heartbeat_epoch` fed
  the WHOLE heartbeat line to `datetime.fromisoformat`. The live watchdog writes
  the ISO timestamp FOLLOWED BY space-separated population fields on one line
  (confirmed against the live artifact and `harness_storm_watchdog.ps1`), so
  `fromisoformat` raised `ValueError` on the trailing text and the function
  returned `0.0` for every real heartbeat — making `watchdog_dormancy` report
  dormant on EVERY tick and restart a healthy watchdog continuously. Fixed by
  parsing only the leading whitespace-delimited token (`text.split()[0]`), with
  `IndexError` added to the fail-soft except set for an empty file.
- **Test-coverage gap.** The daemon dormancy fixture wrote a BARE timestamp,
  masking the parse defect. Hardened the fixture to the REAL line format
  (timestamp + trailing population fields) and added a fresh-real-format
  regression test that fails if the parse ever regresses.
- **Shadow/live mode-gating (invariant violation).** The restart executed
  unconditionally, which spawned a `schtasks` subprocess during shadow-mode
  ticks and broke the committed `test_daemon_shadow_mode_never_spawns` /
  `test_daemon_default_substrate_stays_shadow` invariants (a tick without a
  heartbeat reads as dormant). See § Design Decision for Reviewer.

## Design Decision for Reviewer

**Restart execution is gated to LIVE mode; the dormancy verdict is recorded in
both modes.** The committed WI-4848 invariant is that SHADOW mode performs no
subprocess spawns (`test_daemon_shadow_mode_never_spawns` runs three ticks and
asserts `subprocess.Popen` is never called). The watchdog restart is a subprocess
spawn, so executing it unconditionally violated that invariant. The resolution
mirrors the existing `monitoring`/`health` block (computed and recorded in both
modes, side-effect-free): the dormancy verdict + `restart_storm_watchdog`
remediation hint are recorded in both shadow and live ticks for observability,
but the restart subprocess executes only when the daemon is the LIVE dispatch
substrate (it owns executing remediation only when live). This refines the `-006`
design, which did not address the shadow/live boundary. If the reviewer prefers
the restart to fire in shadow mode as well, that is a NO-GO with the committed
shadow-never-spawns tests requiring a corresponding update.

## Spec-to-Test Mapping

| Specification clause | Test | File | Result |
|---|---|---|---|
| ADR-DISPATCHER-ARCHITECTURE-001 (dormancy detected when evidence age exceeds threshold) | test_watchdog_dormancy_detected_when_stale | platform_tests/scripts/test_dispatch_monitor.py | PASS |
| ADR-DISPATCHER-ARCHITECTURE-001 (fresh watchdog evidence is not dormant) | test_watchdog_dormancy_not_flagged_when_fresh | platform_tests/scripts/test_dispatch_monitor.py | PASS |
| ADR-DISPATCHER-ARCHITECTURE-001 (missing/zero evidence treated as dormant) | test_watchdog_dormancy_missing_evidence_is_dormant | platform_tests/scripts/test_dispatch_monitor.py | PASS |
| ADR-DISPATCHER-ARCHITECTURE-001 (live daemon emits restart action and executes restart on dormancy) | test_run_tick_emits_restart_watchdog_when_dormant | platform_tests/scripts/test_gtkb_dispatcher_daemon.py | PASS |
| GOV-SOURCE-OF-TRUTH-FRESHNESS-001 (fail-soft: restart failure does not abort tick) | test_run_tick_watchdog_restart_failsoft | platform_tests/scripts/test_gtkb_dispatcher_daemon.py | PASS |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (regression guard: fresh REAL-format heartbeat parsed as not dormant, no restart) | test_run_tick_fresh_real_format_heartbeat_not_dormant | platform_tests/scripts/test_gtkb_dispatcher_daemon.py | PASS |
| ADR-DISPATCHER-ARCHITECTURE-001 (mode-gating: shadow records verdict + hint but executes no restart) | test_run_tick_shadow_mode_records_dormancy_without_restart | platform_tests/scripts/test_gtkb_dispatcher_daemon.py | PASS |

## Verification Evidence

Commands run against the changed files (project venv interpreter):

```text
python -m pytest platform_tests/scripts/test_dispatch_monitor.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --tb=short
  => 25 passed in 2.32s
python -m ruff check scripts/ops/dispatch_monitor.py scripts/gtkb_dispatcher_daemon.py platform_tests/scripts/test_dispatch_monitor.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py
  => All checks passed!
python -m ruff format --check scripts/ops/dispatch_monitor.py scripts/gtkb_dispatcher_daemon.py platform_tests/scripts/test_dispatch_monitor.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py
  => 4 files already formatted
```

## Risk / Rollback

- Risk: an over-eager dormancy threshold restarts a healthy-but-slow watchdog.
  Mitigation: conservative default threshold (2x cadence); fail-open below
  threshold; the restart is idempotent (re-run of an already-scheduled task).
- Risk: restart execution is platform-specific (`schtasks`). Mitigation:
  fail-soft execution (recorded in result/status, the tick never aborts); pure
  detection is fully testable independent of the platform restart step.
- Risk: the parse fix or mode-gating changes behavior. Mitigation: the
  fresh-real-format regression test and the shadow-mode no-restart test pin both.
- Rollback: changes are additive (a pure function, a daemon-level action,
  fail-soft execution consuming an existing heartbeat). Reverting the changed
  files restores prior behavior; no schema, governed-record, or narrative change
  is involved.

## Bridge Filing Discipline

This report is filed as the next numbered bridge file
(`bridge/gtkb-wi4852-watchdog-dormancy-auto-restart-008.md`) under the canonical
append-only numbered-file chain. Prior versioned bridge files (`-001` … `-007`)
are never rewritten or deleted; this report is added as a new numbered file so
the chain remains the canonical audit trail per GOV-FILE-BRIDGE-AUTHORITY-001.

## Owner Decisions / Input

- DELIB-20266192 — owner AUQ (2026-06-26) authorized the bounded WI-4852
  implementation and minted the covering PAUTH
  PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4852-WATCHDOG-DORMANCY-AUTO-RESTART
  (allowed mutation classes: source + test_addition; linked spec
  ADR-DISPATCHER-ARCHITECTURE-001).
- DELIB-20266194 — owner AUQ (2026-06-26) authorized the whole-backlog
  NEW-implementation-proposal generation loop (PB picks) under which this work
  was selected. No further owner decision is required to verify this report; the
  shadow/live mode-gating refinement (§ Design Decision for Reviewer) is the one
  item the reviewer should weigh.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
