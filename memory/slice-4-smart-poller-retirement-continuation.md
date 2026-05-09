# Slice 4 Smart-Poller Retirement — Continuation Note

**Status:** In-progress, paused at owner direction 2026-05-09.
**Bridge thread:** `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-*`
**Operative proposal:** `-015` (GO'd at `-016` by Codex 2026-05-09).
**Next bridge-thread version:** `-017` (post-implementation report; do not file until ALL D-steps complete).

## Landed in this session

- **D1**: `GTKB-SmartBridgePoller` Windows scheduled task **deleted**
  (`schtasks /Delete /F`). Verified absent. Process PID 18616 already
  stopped at session start (mitigation AUQ from earlier today).
- **D2**: All 7 smart-poller runtime files moved via `git mv` to
  `archive/smart-poller-2026-05-09/`. Archive README written
  (`archive/smart-poller-2026-05-09/README.md`). Files moved:
  - `scripts/run_smart_bridge_poller.vbs`
  - `scripts/run_smart_bridge_poller.ps1`
  - `scripts/install_smart_poller_task.ps1`
  - `scripts/uninstall_smart_poller_task.ps1`
  - `groundtruth-kb/scripts/bridge_poller_runner.py`
  - `groundtruth-kb/tests/test_bridge_poller_runner.py`
  - `scripts/bridge_notify_reader.py`
- **D4**: `groundtruth-kb/src/groundtruth_kb/project/doctor.py` refactored.
  Removed: `_check_smart_bridge_poller`, `_recent_audit_run_ids`,
  `_SMART_POLLER_TASK_NAME`/`_WRAPPER_REL`/`_VBS_REL`/`_RUNNER_REL`/`_STATE_REL`/`_AUDIT_REL`/`_NOTIFY_REL`/`_FRESH_SECS`,
  `_BRIDGE_SCHEDULER_DOC`. Renamed `_check_bridge_poller` →
  `_check_bridge_dispatch_liveness` (check name "Claude/Codex bridge
  dispatch"); added new constant `_BRIDGE_DISPATCH_DOC =
  "docs/tutorials/dual-agent-setup.md"` (per `-014` F1 fix). Added new
  `_check_cross_harness_trigger` function (3 subchecks: trigger script,
  PostToolUse+Stop hook registration, dispatch-state.json freshness).
  Updated `checks.append` block (lines ~2304-2306) to call the renamed
  + new functions instead of the removed ones.
- **D4 test layout**:
  - `groundtruth-kb/tests/test_doctor_smart_poller.py` archived to
    `archive/smart-poller-2026-05-09/groundtruth-kb/tests/test_doctor_smart_poller.py`.
  - `groundtruth-kb/tests/test_doctor_bridge_poller.py` renamed to
    `groundtruth-kb/tests/test_doctor_bridge_dispatch_liveness.py`,
    body rewritten for new check name + added
    `test_dispatch_doc_path_exists` (T-4-doctor-dispatch-doc-path-exists).
  - **NEW** `groundtruth-kb/tests/test_doctor_cross_harness_trigger.py`
    with 6 PASS/WARN/FAIL tests (T-4-doctor-cross-harness-trigger-coverage).
  - **NEW** `groundtruth-kb/tests/test_slice_4_doctor_test_layout.py`
    with 4 file-presence assertions (T-4-doctor-test-rename-archive).
  - `groundtruth-kb/tests/test_doctor.py` updated:
    `_check_bridge_poller` references replaced by
    `_check_bridge_dispatch_liveness` (sed-class rename).
- **D5b**: Three template files updated:
  - `groundtruth-kb/src/groundtruth_kb/project/scaffold.py` lines
    783-804: 6 template-variable values replaced (PATH_TO_ENTRYPOINT,
    HOW_IT_RUNS, AUTOMATION_NAME, SCHEDULE, EXECUTOR, SOURCE,
    FAILURE_SIGNAL).
  - `groundtruth-kb/templates/bridge-os-poller-setup-prompt.md`
    rewritten as DEPRECATED stub.
  - `groundtruth-kb/templates/rules/bridge-poller-canonical.md`
    rewritten as DEPRECATED stub.
- **D7**: `tests/scripts/test_cross_harness_bridge_trigger.py`
  refactored. Removed `importlib.util.spec_from_file_location()` import
  of archived `bridge_poller_runner.py`. Added two frozen-reference
  helpers (`_frozen_pending_signature`,
  `_frozen_selected_items_for_prompt`) at top of file with docstrings
  citing the archive source. 18/18 tests still pass byte-identically.
- **D8 (partial)**:
  - All `pending-bridge-action-*` notification files in
    `.gtkb-state/bridge-poller/notifications/` deleted.
  - `scripts/session_self_initialization.py`
    `_render_smart_poller_section` body replaced with `return []`
    stub + retirement docstring. The `_render_diagnostic_section`
    helper is now unreferenced but left in place to minimize
    diff footprint.

## Test status

- `tests/scripts/test_cross_harness_bridge_trigger.py`: 18/18 pass.
- `groundtruth-kb/tests/test_doctor.py`: 37/37 pass.
- `groundtruth-kb/tests/test_doctor_bridge_dispatch_liveness.py`: 11/11 pass.
- `groundtruth-kb/tests/test_doctor_cross_harness_trigger.py`: 6/6 pass.
- `groundtruth-kb/tests/test_slice_4_doctor_test_layout.py`: 4/4 pass.
- Combined doctor surface: 58/58.
- doctor.py syntax-clean; symbol-level invariants verified
  (smart-poller symbols absent; replacements present).

## What remains for next session (resume order)

In rough dependency order. Mechanical-class items first; approval-packet
items last.

### Mechanical (no owner approval needed)

1. **D5d** — Tutorial DEPRECATED stubs:
   - `groundtruth-kb/docs/tutorials/bridge-smart-poller.md` (DEPRECATED stub).
   - `groundtruth-kb/docs/tutorials/bridge-smart-poller-activation.md` (DEPRECATED stub).
   - `groundtruth-kb/docs/tutorials/bridge-os-scheduler.md` (DEPRECATED stub).
   - `groundtruth-kb/docs/tutorials/dual-agent-setup.md` (REWRITE bridge-automation
     section to event-driven trigger guidance — supports D4's
     `_BRIDGE_DISPATCH_DOC` retarget).

2. **D5e** — Startup instruction text update in `scripts/session_self_initialization.py`
   (per Codex `-006` F2; section title + body referencing smart-poller
   should redirect to cross-harness-trigger).

3. **D5f** — Desktop bootstrap path + live docs sweep
   (per Codex `-008` F1).

4. **D5h** — Golden scaffold fixtures:
   - `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/.claude/rules/bridge-poller-canonical.md`
   - `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/BRIDGE-INVENTORY.md`
   - `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/bridge-os-poller-setup-prompt.md`
   - `groundtruth-kb/tests/fixtures/bridge_index_live_snapshot.md`
   These must regenerate with the new D5b template content; run scaffold
   round-trip and update fixtures.

5. **D5i** — Module docstrings + samples + templates:
   - `groundtruth-kb/src/groundtruth_kb/bootstrap.py`
   - `groundtruth-kb/src/groundtruth_kb/bridge/__init__.py`
   - `groundtruth-kb/src/groundtruth_kb/bridge/handshake.py`
   - `groundtruth-kb/src/groundtruth_kb/bridge/launcher.py`
   - `groundtruth-kb/src/groundtruth_kb/bridge/notify.py`
   - `groundtruth-kb/src/groundtruth_kb/bridge/paths.py`
   - `groundtruth-kb/src/groundtruth_kb/bridge/registry.py`
   - `groundtruth-kb/src/groundtruth_kb/cli.py`
   - `groundtruth-kb/samples/README.md`
   - `groundtruth-kb/templates/README.md`
   - `groundtruth-kb/docs/day-in-the-life.md`

6. **D5j** — Method-doc topology line (per `-010` preempt). Single-line
   replacement in whichever file it lives in (grep
   `topology` + `smart poller` to locate).

7. **D5k** — `groundtruth-kb/templates/rules/prime-bridge-collaboration-protocol.md`:
   - § "Polling and Scheduling" (lines 80-91) → rewrite as
     § "Bridge Dispatch Automation"
   - § "Escalation Boundary" 5th bullet (lines 100-101) → single-line replacement
   - § "Configuration Capture" body (lines 103-113) → bullet substitutions

8. **D8 tests** — `tests/scripts/test_session_self_initialization.py`
   lines 1873-2003 smart-poller-section tests: either remove the test
   block entirely OR replace each test with an assertion that the
   section is now always empty (proposal allows either).

9. **D9** — Operating-state + CLI + system-interface-map:
   - `groundtruth-kb/src/groundtruth_kb/operating_state.py` — remove
     smart-poller fields/lines from operating-state report.
   - `groundtruth-kb/src/groundtruth_kb/cli.py` — remove smart-poller
     CLI surfaces (if any visible commands).
   - `config/agent-control/system-interface-map.toml` — update
     bridge-automation entries.
   - `scripts/resolve_system_interface.py` — sweep for smart-poller refs.

10. **D9b** — SessionStart auto-dispatch marker (per Codex `-006` F1).
    Identify whichever scaffold/marker file declares the auto-dispatch
    surface and update.

11. **D6 step 38** — NEW test
    `groundtruth-kb/tests/test_doctor_cli_no_smart_poller_guidance.py`
    (T-4-doctor-cli-no-smart-poller-guidance). CliRunner-based test
    invoking `gt project doctor` and asserting:
    - No occurrence of "verified smart poller", "smart-poller liveness",
      "Configure the smart poller", or any pattern from D6 step 32's
      forbidden-pattern set.
    - Presence of "cross-harness event-driven trigger" or "bridge dispatch"
      wording in dispatch-related check messages.
    - `_check_cross_harness_trigger` reports a status (any of PASS/WARN/FAIL).

12. **D6 step 32** — `tests/test_no_active_smart_poller_wording.py`:
    update allowlist per REVISED-7 changes (no `doctor.py`,
    `bridge_poller_runner.py`, `test_doctor_smart_poller.py`,
    `test_doctor_bridge_poller.py`).

### Owner-approval-packet workflow (D5 + D5c)

Each item requires preview file → AUQ to owner showing full content →
formal-artifact-approval-packet write → MemBase insert or file write.
Per memory `feedback_present_decisions_one_by_one.md`, ask one at a
time.

13. **D5 - 3 narrative-artifact authority edits:**
    - `.claude/rules/bridge-essential.md` § "Operational Mode" + Incident
      History (smart-poller subsections; reframe as RETIRED with
      historical context preserved).
    - `.claude/rules/canonical-terminology.md` § "smart poller" entry
      marked RETIRED with redirect; new § entry for "cross-harness
      event-driven trigger" or similar canonical name. Sources updated
      to cite `scripts/cross_harness_bridge_trigger.py` + Slice 3 hook
      registrations + the v2 supersessions.
    - `AGENTS.md` lines 102/164/200 (per `-003` D5): "verified smart
      poller when available" → "cross-harness event-driven trigger".

14. **D5c - 5 MemBase supersessions** (each a v2 spec insert via
    `db.insert_spec()` or `gt summary` workflow + approval packet):
    - `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` v2 (mechanism-agnostic).
    - `DCL-SMART-POLLER-AUTO-TRIGGER-001` v2 (auto-trigger contract;
      implementation pointer updated).
    - `DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001` v2.
    - `PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001` v2 (reframed:
      trigger MUST dispatch on actionable signature change; doctor's
      `_check_cross_harness_trigger` is the new detector).
    - `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` (NEW deliberation;
      captures the retirement decision, references prior policy stance).
    - `PB-INCIDENT-S321-PROPOSAL-WITHOUT-SPEC-LINKAGE-001` PRESERVED
      unchanged (mechanism-agnostic).

### Final

15. **D6 verification battery** — Run all tests:
    - The 8 spec-derived test rows from `-015`.
    - Full pytest pass under `groundtruth-kb/`.
    - Manual round-trip: bridge mutation triggers event-driven dispatch.

16. **Post-implementation report** — File at
    `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-017.md`.
    Include:
    - Specification Links (carry forward from `-015`).
    - Spec-to-test mapping with executed-result evidence.
    - Files Changed with actual stats.
    - Pre-Filing Preflight (re-run + paste packet_hash).
    - Recommended Commit Type (proposal says `refactor:`).
    - Owner Decisions / Input section (the mitigation+land AUQ
      authorization, the 8 D5/D5c approval packets).
    - Conventional Commits type discipline justification.
    - Risk/Rollback (what's reversible; what's not).

## WIP commit message scope (this session)

```
WIP(governance): GTKB-BRIDGE-POLLER-EVENT-DRIVEN-REPLACEMENT-SLICE-4 D1+D2+D4+D5b+D7+D8(partial)

Per bridge GO at -016. Mechanical retirement of smart-poller surfaces.
Remaining scope (D5d-D5k, D8-tests, D9/D9b, D5, D5c, D6, post-impl) deferred
to next session per owner direction 2026-05-09.
```

## Key invariants preserved

- Bridge protocol unchanged: `bridge/INDEX.md` is canonical workflow state;
  `-015` REVISED at top, no `-017` filed yet.
- Cross-harness event-driven trigger remains active and verified
  (Slice 3 closure at `-006`).
- Append-only versioning: nothing deleted from bridge thread; smart-poller
  surfaces archived (not deleted) per bridge-essential.md.
- 76/76 affected tests green at session pause point.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
