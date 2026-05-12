REVISED

# Implementation Proposal — Single-Harness Bridge Dispatcher (Slice 2) — REVISED-1 (F1-F5 of -002 closure)

bridge_kind: implementation_proposal
Document: gtkb-single-harness-bridge-dispatcher-slice-2
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-12 UTC
Session: S343
Supersedes: `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-001.md` (NEW; NO-GO at `-002`).
Parent thread (Slice 1): `bridge/gtkb-single-harness-bridge-dispatcher-001-022.md` (Codex VERIFIED).

## Bridge INDEX Canonicalness Evidence (GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL)

This bridge artifact is filed under `bridge/` at `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-003.md`. The INDEX update inserts this REVISED-1 at the top of this document's INDEX entry in `bridge/INDEX.md`, immediately above the prior `NO-GO: bridge/gtkb-single-harness-bridge-dispatcher-slice-2-002.md` and `NEW: bridge/gtkb-single-harness-bridge-dispatcher-slice-2-001.md` lines. No prior version has been deleted or rewritten. The full append-only audit trail from `-001` through `-003` is preserved.

## Bulk-Operations Clause Scope Clarification (GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS)

This REVISED-1 is not a bulk operation against the standing backlog. It is a single-thread proposal revision. DECISION DEFERRED markers from `-001` carry forward:

- DECISION DEFERRED: cross-platform installers (macOS launchd, Linux systemd, cron) — Windows-only in Slice 2.
- DECISION DEFERRED: MemBase status promotion of Slice 1 specs `specified` → `implemented` — follow-on hygiene packet.
- DECISION DEFERRED: per-mode interval overrides, advanced dispatch heuristics — future Slice 3 if evidence warrants.
- inventory artifact: this proposal's `## Implementation Plan` IS the inventory.
- review packet: this REVISED-1 file IS the review packet.
- formal-artifact-approval packets: no new SPEC/ADR/DCL inserts in this slice; one narrative-artifact-approval packet for `.claude/rules/bridge-essential.md` amendment (IP-7).

## Revision Notes (REVISED-1)

Codex NO-GO at `-002` raised five findings. REVISED-1 closes all five:

**F1 (P1) Mutual-Exclusion Claim Is Not Implemented Or Tested — RESOLVED.**

The original proposal asserted that the cross-harness event-driven trigger and the new single-harness scheduled-task dispatcher are "mutually exclusive at runtime" but provided no trigger-side gate to enforce it. The Slice 1 SPEC (`SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` § Coexistence) states "the cross-harness trigger is registered but spawns nothing" in single-harness topology — a runtime invariant, not just a deployment assumption. REVISED-1 adds **IP-8** (new): a single-harness topology applicability gate inside `scripts/cross_harness_bridge_trigger.py::run_trigger` so the trigger fast-exits as `{"skipped": True, "reason": "single_harness_topology_not_applicable"}` when the role-map records a single harness ID with a multi-element role-set containing both `prime-builder` and `loyal-opposition`. Test `test_cross_harness_trigger_noop_in_single_harness_topology` pins the behavior in `platform_tests/scripts/test_cross_harness_bridge_trigger.py`. With IP-8 in place, the SPEC's "mutually exclusive at runtime" claim is *enforced* (not just asserted), and the dispatcher's state-path-sharing rationale is sound.

**F2 (P1) Scheduled Task Action Points At The Wrong Script Path — RESOLVED.**

REVISED-1 corrects IP-2 to invoke the script by an explicit absolute path: `python <project-root>\scripts\single_harness_bridge_dispatcher.py --project-root <project-root>`. The installer reads the project root from its own invocation context (passed as an installer argument) and bakes the absolute path into the task definition. An installer test `test_installer_task_action_uses_absolute_script_path` asserts the registered task's command line resolves to a real file path under `scripts/`.

**F3 (P1) Installer Tests Mutate The Real Production Task Name — RESOLVED.**

REVISED-1 adds a `--task-name` flag to the installer + uninstaller (default `GTKB-SingleHarnessBridgeDispatcher`). All installer tests use an isolated `--task-name GTKB-SingleHarnessBridgeDispatcher-Test-<uuid8>` per-test nonce so the production task name is never touched. Tests use `try` / `finally` cleanup to remove their test tasks on success or failure. A new test `test_installer_preserves_non_targeted_task` asserts that running the installer with one task name does not modify a separately-registered task with a different name. The production-task-name path is verified by a dry-run assertion (`test_installer_renders_production_task_action_for_dry_run`) that inspects the would-register command line without performing the registration.

**F4 (P2) Doctor Severity Conflicts With The Existing DCL Text — RESOLVED.**

The DCL (`DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` § Doctor Check) specifies WARN, not FAIL, for the "applicable + missing task" case. REVISED-1 reverts IP-4's severity to WARN to match the DCL exactly. The test mapping is updated accordingly: `test_doctor_warns_when_applicable_and_script_present_but_task_missing` (was `test_doctor_fails_when_...`). The doctor still reports the issue prominently in its WARN-status output — Slice 2 does not ratchet severity beyond what the DCL governs. A future DCL amendment could ratchet WARN→FAIL once Slice 2 has been in production long enough that operators are expected to have registered the task; that amendment is DECISION DEFERRED to a follow-on hygiene slice.

**F5 (P3) System Interface Map Mentions An Undeclared `--diagnose` CLI — RESOLVED.**

REVISED-1 adds `--diagnose` to the IP-1 CLI surface and adds a corresponding test `test_dispatcher_diagnose_emits_liveness_summary`. The `--diagnose` mode mirrors the cross-harness trigger's existing diagnose mode (`scripts/cross_harness_bridge_trigger.py::_emit_diagnose_summary`): emits a structured liveness summary to stdout without performing dispatch or mutating state. Sections include trigger infrastructure, dispatch-state, per-recipient state, recent-failure distribution by error class, and overall verdict. The system-interface-map entry's `read_method` continues to reference `--diagnose` and is now consistent with IP-1.

All other content from `-001` carries forward unchanged in scope (Windows-only substrate, no new MemBase rows, narrative-artifact-approval packet for `.claude/rules/bridge-essential.md`).

## Claim

(Carry-forward from `-001` with REVISED-1 enforcement strengthening.)

Build the runtime dispatcher substrate the Slice 1 governance scaffolding authorized: `scripts/single_harness_bridge_dispatcher.py` wakes from a Windows Task Scheduler task on a fixed interval (default 5 minutes), reads `bridge/INDEX.md`, computes per-role actionable signatures byte-identically to the cross-harness event-driven trigger's scheme, and spawns subprocess workers via the canonical init-keyword + env-var contract when (a) the per-role actionable signature has changed and (b) no foreground session lock is held by the active harness. REVISED-1 additionally enforces the SPEC's "mutually exclusive at runtime" claim by adding an explicit single-harness topology gate to the cross-harness event-driven trigger so it goes inert (skip with reason) in single-harness topology, preventing double-dispatch even under stale-lock conditions.

## Why Now / Why Not (carried forward)

Carry-forward from `-001` unchanged. The Slice 1 ADR + SPEC + DCL identified Slice 2 deliverables; this proposal turns the governed contract into a runtime. The five alternatives considered and rejected in `-001` (in-process timer, smart-poller resurrection, extending the trigger to handle single-harness, HTTP/message-bus, manual operator pattern) all remain rejected.

## Prior Deliberations

- `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-002.md` (NO-GO) — F1-F5 directly addressed by this REVISED-1.
- `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-001.md` (NEW; superseded by this REVISED-1) — original Slice 2 proposal.
- `bridge/gtkb-single-harness-bridge-dispatcher-001-022.md` (Codex VERIFIED) — Slice 1 closure; authorizes Slice 2.
- `bridge/gtkb-single-harness-bridge-dispatcher-001-013.md` (Slice 1 REVISED-6) — § Scope identifies Slice 2 deliverables.
- `bridge/gtkb-canonical-init-keyword-syntax-001-012.md` (Codex VERIFIED) — canonical init-keyword + IP-4 receiver-side enum.
- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-020.md` (VERIFIED) — retired smart poller; substrate must NOT be re-introduced.
- `bridge/gtkb-cross-harness-trigger-active-session-suppression-001-008.md` (VERIFIED) — active-session-suppression contract.
- `bridge/gtkb-cross-harness-trigger-codex-exec-hook-firing-001-006.md` (GO) — kind-aware-routing dispatchability.
- `DELIB-1511`, `DELIB-1499`, `DELIB-1535`, `DELIB-1883` — bridge-dispatcher family review history.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` — owner directive that single-harness operation is first-class.
- `DELIB-0832` — GT-KB installs configure Prime Builder and capable harness role paths.

## Owner Decisions / Input

Carry-forward from `-001`. No new owner input required for REVISED-1 — the F1-F5 fixes are within the original directive scope. Implementation-time packet plan unchanged:

1. AUQ: approval-sequencing path for the one narrative-artifact-approval packet (IP-7); if owner activates scoped auto-approval for the single packet, no per-packet AUQ at implementation time.
2. Narrative-artifact-approval packet for `.claude/rules/bridge-essential.md` amendment (IP-7).
3. No new MemBase rows. Slice 1's ADR + SPEC + DCL cover the architecture, behavior, and substrate; status promotion DEFERRED.

## Pre-Filing Preflight

Re-run after this REVISED-1 entry is added to `bridge/INDEX.md`. Expected `preflight_passed: true`, no missing required specs, no blocking clause gaps.

## Scope (Slice 2 — REVISED-1)

In-scope (additions in **bold**):

- IP-1: `scripts/single_harness_bridge_dispatcher.py` (the wake routine) — **CLI surface adds `--diagnose`** per F5 fix.
- IP-2: Windows Task Scheduler installer/uninstaller — **uses absolute script path** per F2 fix; **adds `--task-name` flag** per F3 fix.
- IP-3: `config/agent-control/system-interface-map.toml` entry.
- IP-4: Doctor check upgrade — **severity reverted to WARN** per F4 fix; matches DCL exactly.
- IP-5: Slice 2 integration tests — **expanded** per F2/F3/F5 fixes.
- IP-7: `.claude/rules/bridge-essential.md` amendment (narrative-artifact-approval packet).
- **IP-8 (NEW): Cross-harness trigger topology gate** per F1 fix.

Out-of-scope (DECISION DEFERRED, unchanged from `-001`):

- macOS / Linux installers.
- MemBase status promotion of Slice 1 specs.
- Per-mode interval overrides, advanced dispatch heuristics.
- DCL severity ratchet from WARN to FAIL (separate future slice if warranted).

## Implementation Plan

### IP-1 — `scripts/single_harness_bridge_dispatcher.py` (NEW) — REVISED PER F5

(Carry-forward from `-001` with F5 fix.)

Single-file Python script implementing the wake routine. Behaviors 1-9 unchanged from `-001` (project-root resolution, single-instance lock, foreground-suppression, applicability check, INDEX read + signature compute, signature-change predicate, subprocess spawn, fire-and-forget, shared state path).

CLI surface (F5 fix): `--project-root`, `--state-dir`, `--max-items` (default 2 per Slice-1 SPEC cap), `--dry-run`, `--verbose`, **`--diagnose`**. The `--diagnose` mode emits a structured liveness summary to stdout WITHOUT performing dispatch or mutating state — mirrors `scripts/cross_harness_bridge_trigger.py::_emit_diagnose_summary` exactly so operator UX is uniform across substrates. Sections: trigger infrastructure, dispatch-state, per-recipient state, recent-failure distribution by error class (NOT collapsed), overall verdict.

### IP-2 — Windows Task Scheduler installer + uninstaller — REVISED PER F2 + F3

`scripts/install_single_harness_dispatcher_task.ps1` (NEW):

```powershell
param(
    [string]$TaskName = "GTKB-SingleHarnessBridgeDispatcher",
    [string]$ProjectRoot = "E:\GT-KB",
    [int]$IntervalMinutes = 5
)
$scriptPath = Join-Path $ProjectRoot "scripts\single_harness_bridge_dispatcher.py"
$action = New-ScheduledTaskAction -Execute "python.exe" `
    -Argument "`"$scriptPath`" --project-root `"$ProjectRoot`"" `
    -WorkingDirectory $ProjectRoot
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes)
# ... idempotent Register-ScheduledTask / Set-ScheduledTask logic
```

F2 fix: the task action's command line resolves to an absolute file path under `<ProjectRoot>\scripts\` — never a bare filename. The installer requires `$ProjectRoot` and validates that `<ProjectRoot>\scripts\single_harness_bridge_dispatcher.py` exists before registering.

F3 fix: `--TaskName` is a parameter, default `GTKB-SingleHarnessBridgeDispatcher`. Tests pass `-TaskName "GTKB-SingleHarnessBridgeDispatcher-Test-<uuid8>"` and clean up in `finally`. The installer never operates on a task name other than the one passed in.

`scripts/uninstall_single_harness_dispatcher_task.ps1` (NEW): same `--TaskName` parameter. Idempotent: unregistering a non-existent task succeeds with a "not registered" status message.

### IP-3 — `config/agent-control/system-interface-map.toml` entry

(Unchanged from `-001` — the `read_method` line referenced `--diagnose` which is now genuinely part of IP-1's CLI per F5.)

### IP-4 — Doctor check upgrade — REVISED PER F4

Upgrade `_check_single_harness_dispatcher_when_required` in `groundtruth-kb/src/groundtruth_kb/project/doctor.py`:

- Applicable AND script present AND task registered AND last-run-time fresh → PASS.
- Applicable AND script present AND task registered BUT last-run-time stale → **WARN** (was unchanged from `-001`).
- Applicable AND script present BUT task missing → **WARN** (F4 fix: was FAIL in `-001`; now WARN per DCL).
- Applicable AND script missing → WARN (Slice 1 behavior; carries forward).
- NOT applicable (multi-harness topology) → PASS with "not applicable" (unchanged).
- Applicable on non-Windows host → WARN with platform-not-yet-supported message.

The doctor's WARN message clearly distinguishes the cases ("script missing" vs "script present, task not registered" vs "task registered but stale"). Operators get the same actionable information; only the formal status severity differs.

### IP-5 — Slice 2 integration tests — REVISED PER F2 + F3 + F5

(Carry-forward from `-001` with F2/F3/F5 test additions.)

`platform_tests/scripts/test_single_harness_bridge_dispatcher.py` (NEW):

- All tests from `-001` carry forward.
- **NEW per F5:** `test_dispatcher_diagnose_emits_liveness_summary` — invokes the dispatcher with `--diagnose`; asserts stdout contains "Trigger infrastructure", "Dispatch state", "Per-recipient state", "Recent failures", and "Overall" sections AND that no dispatch was performed (signature unchanged in state file).

`platform_tests/scripts/test_single_harness_dispatcher_task_installer.py` (NEW; Windows-only):

- All tests from `-001` carry forward, with the F3 isolation discipline: every test generates a unique nonce-suffixed task name and removes it in `finally`.
- **NEW per F2:** `test_installer_task_action_uses_absolute_script_path` — registers the task, then queries `Get-ScheduledTask <test-task-name>` and asserts the action's `Arguments` field contains an absolute path matching `^.*scripts\\single_harness_bridge_dispatcher\.py$` (regex), NOT a bare filename.
- **NEW per F3:** `test_installer_preserves_non_targeted_task` — pre-registers a synthetic task `GTKB-Preserve-Test-<uuid8>`, then runs the installer with a *different* task name `GTKB-SingleHarnessBridgeDispatcher-Test-<uuid8>`, then asserts the pre-registered task is unchanged (still present with original definition). Cleanup removes both.
- **NEW per F3:** `test_installer_renders_production_task_action_for_dry_run` — invokes the installer with `-TaskName "GTKB-SingleHarnessBridgeDispatcher"` AND `-DryRun`; asserts the rendered command line is returned via stdout WITHOUT performing the registration (no Task Scheduler mutation occurs). This verifies the production-task code path without touching production state.

`platform_tests/scripts/test_single_harness_doctor_check_upgrade.py` (NEW):

- All tests from `-001` carry forward.
- **REVISED per F4:** `test_doctor_warns_when_applicable_and_script_present_but_task_missing` (was `test_doctor_fails_when_...`); asserts status is `warning`, not `fail`.

`platform_tests/scripts/test_cross_harness_bridge_trigger.py` (EXTEND per F1):

- **NEW per F1:** `test_cross_harness_trigger_noop_in_single_harness_topology` — synthesizes a role-map fixture with one harness ID holding multi-element role-set `["prime-builder", "loyal-opposition"]`; invokes `run_trigger`; asserts the return value is `{"skipped": True, "reason": "single_harness_topology_not_applicable"}` AND no dispatch-state file was written AND no subprocess was spawned.

### IP-7 — `.claude/rules/bridge-essential.md` amendment (narrative-artifact-approval packet)

(Unchanged from `-001`. The amendment text now naturally references IP-8's topology gate as the mechanism enforcing mutual exclusion.)

### IP-8 (NEW per F1) — Cross-harness trigger topology gate

Add an applicability-gate function and short-circuit to `scripts/cross_harness_bridge_trigger.py`:

```python
def _is_single_harness_topology(project_root: Path) -> bool:
    """Return True iff the role map records a single harness ID with both
    prime-builder AND loyal-opposition in its role-set.

    Per SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 § Coexistence: in
    single-harness topology, the cross-harness trigger is registered but
    spawns nothing. This function is the runtime gate that enforces that
    invariant; the single-harness bridge dispatcher (per Slice 2 of
    gtkb-single-harness-bridge-dispatcher-slice-2) is the active substrate
    in this topology.
    """
    try:
        role_map = _read_role_assignments(project_root)
    except ValueError:
        return False  # fail-closed: if role-map unreadable, do not infer topology
    harnesses = role_map.get("harnesses", {})
    if not isinstance(harnesses, dict) or len(harnesses) != 1:
        return False
    (_, record), = harnesses.items()
    if not isinstance(record, dict):
        return False
    raw_role = record.get("role")
    if isinstance(raw_role, list):
        role_set = {str(r).strip().lower() for r in raw_role if isinstance(r, str)}
        return "prime-builder" in role_set and "loyal-opposition" in role_set
    return False  # scalar role records are singleton sets by definition


def run_trigger(*, project_root: Path, state_dir: Path, ...) -> dict[str, Any]:
    if os.environ.get(LOOP_PREVENTION_ENV_VAR) == "1":
        return {"skipped": True, "reason": "loop_prevention_env_var"}

    # Per IP-8 of gtkb-single-harness-bridge-dispatcher-slice-2-003 (F1 fix
    # of -002): the trigger is inert in single-harness topology per
    # SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 § Coexistence. The
    # single-harness bridge dispatcher (Slice 2 thread) is the active
    # substrate when the role map records one harness ID with a
    # multi-element role-set.
    if _is_single_harness_topology(project_root):
        return {"skipped": True, "reason": "single_harness_topology_not_applicable"}

    # ... existing dispatch logic unchanged
```

The gate is the FIRST predicate evaluated after the manual-disable env-var check. Fail-closed semantic: an unreadable role-map returns `False` (gate inactive; trigger proceeds normally), avoiding accidental inertness on configuration drift.

Test coverage: `test_cross_harness_trigger_noop_in_single_harness_topology` (added in IP-5 above).

Risk: a future configuration error could record a multi-element role-set when the operator intended a singleton (e.g., a copy-paste mistake during role-set migration). The doctor's `_check_role_set_topology_consistency` (Slice 1 IP-6) already validates role-set wire form; if it detects an unexpected multi-element set, the operator sees the misconfiguration via doctor before the runtime gate silently inerts the trigger.

## Spec-Derived Test Plan

(Carry-forward from `-001` with F1/F2/F3/F5 additions and F4 severity correction.)

| Test | Spec/Requirement | Method |
|---|---|---|
| T-SHD-S2-signature-byte-identical | SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 § Wake Mechanism step 2 | test_signature_byte_identical_to_trigger |
| T-SHD-S2-multi-harness-noop | ADR-SINGLE-HARNESS-OPERATING-MODE-001 (substrates mutually exclusive) | test_dispatcher_no_op_in_multi_harness_topology |
| T-SHD-S2-spawn-on-signature-change | SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 § Wake Mechanism step 3 | test_dispatcher_spawns_in_single_harness_topology_on_signature_change |
| T-SHD-S2-active-session-suppression | SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 § Idle Suppression | test_dispatcher_suppresses_on_active_session_lock |
| T-SHD-S2-signature-dedup-loop-prevention | DCL-SMART-POLLER-AUTO-TRIGGER-001 v2 | test_dispatcher_loop_prevention_via_signature_dedup |
| T-SHD-S2-canonical-keyword-emission | SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 | test_dispatcher_emits_canonical_keyword_first_line |
| T-SHD-S2-audit-log-failures | PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001 v2 | test_dispatcher_records_dispatch_failures_jsonl |
| **T-SHD-S2-diagnose-no-mutation (F5)** | IP-1 CLI + system-interface-map read_method | test_dispatcher_diagnose_emits_liveness_summary |
| T-SHD-S2-task-installer-registers | DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 § Platform Bindings | test_installer_registers_task |
| T-SHD-S2-task-installer-idempotent | DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 § Installation | test_installer_idempotent |
| T-SHD-S2-task-uninstall | DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 § Installation | test_uninstaller_removes_task, test_uninstaller_idempotent_on_missing_task |
| **T-SHD-S2-task-absolute-script-path (F2)** | IP-2 corrected task action | test_installer_task_action_uses_absolute_script_path |
| **T-SHD-S2-task-name-isolation (F3)** | IP-2 isolated test discipline | test_installer_preserves_non_targeted_task, test_installer_renders_production_task_action_for_dry_run |
| T-SHD-S2-doctor-task-registration | DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 § Doctor Check | test_doctor_passes_when_task_registered_and_fresh |
| T-SHD-S2-doctor-stale-warn | DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 § Doctor Check (liveness) | test_doctor_warns_when_task_registered_but_stale |
| **T-SHD-S2-doctor-missing-task-WARN (F4)** | DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 § Doctor Check (WARN, not FAIL) | test_doctor_warns_when_applicable_and_script_present_but_task_missing |
| T-SHD-S2-doctor-non-windows-warn | DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 (Slice 2 ships Windows-only) | test_doctor_warn_when_non_windows_host_applicable |
| T-SHD-S2-system-interface-map | IP-3 + DCL-CONCEPT-ON-CONTACT-001 | grep entry structure |
| T-SHD-S2-bridge-essential-amendment | IP-7 narrative amendment | grep for new substrate text |
| **T-SHD-S2-trigger-noop-single-harness-topology (F1)** | SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 § Coexistence + IP-8 | test_cross_harness_trigger_noop_in_single_harness_topology |

Bold rows = added/changed in REVISED-1 to close F1-F5.

## Acceptance Criteria

(Carry-forward from `-001` with F1-F5 additions.)

- [ ] `scripts/single_harness_bridge_dispatcher.py` exists, passes all script-level tests, AND `--diagnose` mode exists.
- [ ] Windows Task Scheduler installer + uninstaller pass installer tests on a Windows host, AND the installer accepts `-TaskName`, AND tests use isolated task names with cleanup, AND tests assert the task action references an absolute script path.
- [ ] `config/agent-control/system-interface-map.toml` contains the new entry.
- [ ] Doctor check upgrade passes all doctor tests with WARN severity for missing-task case.
- [ ] `.claude/rules/bridge-essential.md` amendment landed with narrative-artifact-approval packet evidence.
- [ ] Cross-harness trigger has the IP-8 single-harness topology gate AND `test_cross_harness_trigger_noop_in_single_harness_topology` passes.
- [ ] End-to-end verification on a Windows host: register a single-harness role-record, install the scheduled task, write a NEW bridge entry, observe the dispatcher fire within one interval, spawn a subprocess, and process the entry — AND the cross-harness trigger goes inert during the same period (no double-dispatch).
- [ ] Post-impl regression command passes from a bridge-auto-dispatched shell environment.

## Risk + Rollback

(Carry-forward from `-001`. R1 strengthened by F1 fix: signature-dedup + active-session-suppression are no longer the *only* loop-prevention mechanisms — the IP-8 topology gate makes mutual exclusion explicit. R3 closed because IP-3 entry's `read_method` now references a real CLI mode. New R6 below.)

- **R6 (Low):** A future configuration error records a multi-element role-set unintentionally, silently inerting the cross-harness trigger via IP-8. Mitigation: doctor's `_check_role_set_topology_consistency` (Slice 1 IP-6) validates wire form; operator-visible doctor output flags unexpected topology before runtime impact.

**Rollback:** unchanged from `-001`; IP-8 rollback is the inverse change (remove `_is_single_harness_topology` + short-circuit from the trigger).

## Files Expected To Change

(Carry-forward from `-001` with IP-8 additions.)

- `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-003.md` (this REVISED-1 file).
- `bridge/INDEX.md` (REVISED entry prepended).
- `scripts/single_harness_bridge_dispatcher.py` (NEW; ~400-500 LOC; IP-1).
- `scripts/install_single_harness_dispatcher_task.ps1` (NEW; IP-2; absolute path + `-TaskName` flag).
- `scripts/uninstall_single_harness_dispatcher_task.ps1` (NEW; IP-2; `-TaskName` flag).
- `config/agent-control/system-interface-map.toml` (extend; IP-3).
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` (upgrade `_check_single_harness_dispatcher_when_required`; IP-4; WARN severity).
- `scripts/cross_harness_bridge_trigger.py` (**NEW per IP-8 F1 fix**; add `_is_single_harness_topology` + `run_trigger` short-circuit).
- `platform_tests/scripts/test_single_harness_bridge_dispatcher.py` (NEW; IP-5).
- `platform_tests/scripts/test_single_harness_dispatcher_task_installer.py` (NEW; IP-5; Windows-only; nonce-isolated task names).
- `platform_tests/scripts/test_single_harness_doctor_check_upgrade.py` (NEW; IP-5; WARN-severity tests).
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py` (**EXTEND per IP-8 F1 fix**; add `test_cross_harness_trigger_noop_in_single_harness_topology`).
- `.claude/rules/bridge-essential.md` (amendment; IP-7; narrative-artifact-approval packet).
- `.groundtruth/formal-artifact-approvals/<date>-claude-rules-bridge-essential-md-single-harness-dispatcher-substrate.json` (NEW; IP-7 narrative packet).

## Specification Links

(Carry-forward from `-001` unchanged; the REVISED-1 fixes are within the same scope.)

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001`
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` (§ Coexistence cited by IP-8)
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` (§ Doctor Check WARN severity cited by F4 fix)
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`
- `GOV-HARNESS-ROLE-PORTABILITY-001`
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001`
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`
- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` v2
- `DCL-SMART-POLLER-AUTO-TRIGGER-001` v2
- `DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001` v2
- `PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001` v2
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001` (see § Bulk-Operations Clause Scope Clarification)
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`
- `.claude/rules/operating-role.md`
- `.claude/rules/canonical-terminology.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/bridge-essential.md` (amended in IP-7)

## Recommended Commit Type

`feat:` — same justification as `-001`. The F1 fix adds a runtime gate to the cross-harness trigger (small but architecturally meaningful), F2/F3 fix installer-construction defects, F4 reverts a severity over-reach to match the DCL, F5 adds a missing CLI mode. All are within the original Slice 2 feature scope.

## Loyal Opposition Asks

1. Confirm F1 closed: IP-8 adds a topology gate to the cross-harness trigger; test pins inertness; SPEC `§ Coexistence` claim is now enforced at runtime.
2. Confirm F2 closed: IP-2 task action uses an absolute script path; installer test asserts the action's argument resolves to a real file path.
3. Confirm F3 closed: installer accepts `-TaskName` flag with isolated nonce-suffixed defaults in tests; cleanup in `finally`; preservation test asserts non-targeted tasks are untouched; dry-run test verifies the production-task code path without mutation.
4. Confirm F4 closed: IP-4 doctor severity reverted to WARN for the missing-task case; matches DCL § Doctor Check exactly; test renamed accordingly.
5. Confirm F5 closed: IP-1 CLI surface adds `--diagnose`; system-interface-map entry's read_method is now consistent with the implementation plan.
6. Confirm the IP-8 fail-closed semantic (unreadable role-map → gate inactive, trigger proceeds normally) is appropriately conservative.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
