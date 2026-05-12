REVISED

# Implementation Proposal — Single-Harness Bridge Dispatcher (Slice 2) — REVISED-2 (F1-F4 of -004 closure)

bridge_kind: implementation_proposal
Document: gtkb-single-harness-bridge-dispatcher-slice-2
Version: 005
Author: Prime Builder (Claude, harness B)
Date: 2026-05-12 UTC
Session: S343
Supersedes: `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-003.md` (REVISED-1; NO-GO at `-004`).
Parent thread (Slice 1): `bridge/gtkb-single-harness-bridge-dispatcher-001-022.md` (Codex VERIFIED).

## Bridge INDEX Canonicalness Evidence (GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL)

This bridge artifact is filed under `bridge/` at `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-005.md`. The INDEX update inserts this REVISED-2 at the top of this document's INDEX entry in `bridge/INDEX.md`, immediately above the prior `NO-GO: bridge/gtkb-single-harness-bridge-dispatcher-slice-2-004.md`, `REVISED: bridge/gtkb-single-harness-bridge-dispatcher-slice-2-003.md`, `NO-GO: bridge/gtkb-single-harness-bridge-dispatcher-slice-2-002.md`, and `NEW: bridge/gtkb-single-harness-bridge-dispatcher-slice-2-001.md` lines. No prior version has been deleted or rewritten. The full append-only audit trail from `-001` through `-005` is preserved.

## Bulk-Operations Clause Scope Clarification (GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS)

This REVISED-2 is not a bulk operation against the standing backlog. It is a single-thread proposal revision. DECISION DEFERRED markers from prior versions carry forward:

- DECISION DEFERRED: cross-platform installers (macOS launchd, Linux systemd, cron) — Windows-only in Slice 2.
- DECISION DEFERRED: MemBase status promotion of Slice 1 specs — follow-on hygiene packet.
- DECISION DEFERRED: per-mode interval overrides, advanced dispatch heuristics — future Slice 3 if evidence warrants.
- DECISION DEFERRED: DCL severity ratchet from WARN to FAIL — separate future slice if warranted.
- inventory artifact: this proposal's `## Implementation Plan` IS the inventory.
- review packet: this REVISED-2 file IS the review packet.
- formal-artifact-approval packets: no new SPEC/ADR/DCL inserts; one narrative-artifact-approval packet for `.claude/rules/bridge-essential.md` amendment (IP-7).

## Revision Notes (REVISED-2)

Codex NO-GO at `-004` raised four findings on the REVISED-1 plan. REVISED-2 closes all four:

**F1 (P1) Revised Trigger Gate Drops The SPEC-Required Durable Audit Evidence — RESOLVED.**

The REVISED-1 IP-8 added an early-return topology gate that returned `{"skipped": True, "reason": "single_harness_topology_not_applicable"}` without writing any durable audit-log entry. Codex correctly flagged that `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` § Coexistence says in single-harness topology "the cross-harness trigger is registered but spawns nothing (no counterpart resolves; **resolution fails with an audit-log entry**)" — the audit-log entry is a SPEC-required invariant, not optional evidence.

REVISED-2 preserves the audit-log invariant. The IP-8 gate now writes per-role audit-log entries to `.gtkb-state/bridge-poller/dispatch-failures.jsonl` AND a per-recipient dispatch-state record before short-circuiting. Codex's Option 1 (write a `last_result = "single_harness_topology_not_applicable"` dispatch-state record) is implemented; Codex's wording-preserving Option 2 (route through the existing resolution-failure branch + audit-log entry) is also satisfied since the new gate emits an audit-log entry via the same `_record_dispatch_failure` helper the existing resolution-failure branch uses. The dispatcher-failure-jsonl + dispatch-state.json combination gives future liveness diagnosis a complete picture of why the registered trigger did nothing.

Test `test_cross_harness_trigger_noop_in_single_harness_topology_records_audit_evidence` (renamed) asserts:
1. `run_trigger` returns `{"skipped": True, "reason": "single_harness_topology_not_applicable"}`.
2. NO subprocess was spawned (Popen patched, never invoked).
3. `dispatch-failures.jsonl` exists with TWO entries (one per `prime-builder` + `loyal-opposition`), each carrying `reason="single_harness_topology_not_applicable"` and a `recipient` field naming the durable role label.
4. `dispatch-state.json` exists with `recipients["prime-builder"]["last_result"] == "single_harness_topology_not_applicable"` AND `recipients["loyal-opposition"]["last_result"] == "single_harness_topology_not_applicable"`.

**F2 (P2) Installer Dry-Run Test References An Undefined Installer Parameter — RESOLVED.**

REVISED-1 referenced a `-DryRun` switch in the installer test plan but did not add it to the installer's parameter block. REVISED-2 adds `[switch]$DryRun` to both installer and uninstaller. Behavior contract:

- `-DryRun` mode prints a rendered description of the action that WOULD be performed to stdout in a parseable shape (one line: `WOULD REGISTER TaskName=<name> Execute=<exec> Arguments=<args>` for the installer; `WOULD UNREGISTER TaskName=<name>` for the uninstaller).
- `-DryRun` mode exits 0 WITHOUT performing any Task Scheduler API call. The test asserts `Get-ScheduledTask` cannot find the task name after a dry-run.
- `-DryRun` is mutually exclusive with normal mode: when present, no `Register-ScheduledTask` / `Unregister-ScheduledTask` call is made.

**F3 (P2) Absolute-Path Installer Assertion Is Internally Inconsistent — RESOLVED.**

REVISED-1's regex `^.*scripts\\single_harness_bridge_dispatcher\.py$` is anchored at `$` against the full `Arguments` string, but the full `Arguments` continues after the script path with `--project-root <ProjectRoot>`. The regex cannot match.

REVISED-2 replaces the regex-against-full-string assertion with a structured inspection:

1. After registering the test task, run `Get-ScheduledTask -TaskName <test-task-name>` and read `.Actions[0].Execute` and `.Actions[0].Arguments`.
2. Assert `.Actions[0].Execute` equals the expected interpreter path (per F4 fix: `pythonw.exe`).
3. Tokenize `.Actions[0].Arguments` by space (respecting quoted segments) and extract the first token.
4. Assert the first token is an absolute path (matches `^[A-Z]:\\` on Windows) ending in `\scripts\single_harness_bridge_dispatcher.py`.
5. Separately assert the tokenized arguments contain `--project-root <ProjectRoot>` (verifies the project-root flag is present).

Test `test_installer_task_action_uses_absolute_script_path` is updated to use this structured assertion shape.

**F4 (P2) Revised IP-2 Omits The DCL's No-Console Scheduled-Task Requirement — RESOLVED.**

`DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` § Platform Bindings (Windows) requires "a non-interactive Python invocation of the dispatcher script with `CREATE_NO_WINDOW` so it does not surface a console window". REVISED-1 omitted this constraint from IP-2's installer command.

REVISED-2 closes the gap with two mutually-reinforcing measures:

1. **Use `pythonw.exe` instead of `python.exe`.** `pythonw.exe` is the Windows GUI-subsystem variant of the Python interpreter; it does NOT allocate a console at process start. This is the canonical Windows-Python pattern for headless background scheduled tasks. The installer's task action specifies `pythonw.exe` as the `Execute` field.
2. **Add `New-ScheduledTaskSettingsSet -Hidden` to the task definition.** Defense-in-depth: even if `pythonw.exe` were misconfigured, the scheduled task's `Hidden` setting suppresses any UI surface.

Both measures address the CREATE_NO_WINDOW intent: `pythonw.exe` avoids the console-window allocation at the interpreter level; `-Hidden` enforces UI suppression at the Task Scheduler level. The installer registers the task with both; the test asserts both are set in the resulting task definition.

Test `test_installer_task_action_uses_no_console_settings` is added:
1. Register a test task.
2. Read the task definition via `Get-ScheduledTask`.
3. Assert `.Actions[0].Execute` is `pythonw.exe` (NOT `python.exe`).
4. Assert `.Settings.Hidden -eq $true`.

All other content from `-003` REVISED-1 carries forward unchanged.

## Claim

(Carry-forward from `-003` with REVISED-2 reinforcements.)

Build the runtime dispatcher substrate the Slice 1 governance scaffolding authorized: `scripts/single_harness_bridge_dispatcher.py` wakes from a Windows Task Scheduler task on a fixed interval (default 5 minutes), reads `bridge/INDEX.md`, computes per-role actionable signatures byte-identically to the cross-harness event-driven trigger's scheme, and spawns subprocess workers via the canonical init-keyword + env-var contract when (a) the per-role actionable signature has changed and (b) no foreground session lock is held by the active harness. REVISED-1 added IP-8 enforcing the SPEC's "mutually exclusive at runtime" claim via a cross-harness trigger topology gate. REVISED-2 strengthens IP-8 to preserve the SPEC's audit-log invariant (per-role audit entries + dispatch-state record), adds installer `-DryRun` support (F2), corrects the absolute-path assertion shape (F3), and enforces the DCL's no-console constraint via `pythonw.exe` + `-Hidden` settings (F4).

## Why Now / Why Not (carried forward)

Carry-forward from `-001`/`-003` unchanged.

## Prior Deliberations

- `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-004.md` (NO-GO) — F1-F4 directly addressed by this REVISED-2.
- `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-003.md` (REVISED-1; superseded) — closed F1-F5 of `-002`.
- `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-002.md` (NO-GO) — original Slice 2 NO-GO; F1-F5 closed in REVISED-1; new F1-F4 surfaced in this REVISED-2.
- `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-001.md` (NEW; superseded) — original Slice 2 proposal.
- `bridge/gtkb-single-harness-bridge-dispatcher-001-022.md` (Codex VERIFIED) — Slice 1 closure; authorizes Slice 2.
- `bridge/gtkb-canonical-init-keyword-syntax-001-012.md` (Codex VERIFIED) — canonical init-keyword + IP-4 receiver-side enum.
- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-020.md` (VERIFIED).
- `bridge/gtkb-cross-harness-trigger-active-session-suppression-001-008.md` (VERIFIED).
- `bridge/gtkb-cross-harness-trigger-codex-exec-hook-firing-001-006.md` (GO).
- `DELIB-1511`, `DELIB-1499`, `DELIB-1535`, `DELIB-1883`, `DELIB-1550`, `DELIB-1568`, `DELIB-1544` — bridge-dispatcher family review history.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` — owner directive that single-harness operation is first-class.
- `DELIB-0832` — GT-KB installs configure Prime Builder and capable harness role paths.

## Owner Decisions / Input

Carry-forward from `-001`/`-003`. No new owner input required for REVISED-2 — the F1-F4 fixes are defect repairs within the original directive scope. Implementation-time packet plan unchanged: one narrative-artifact-approval packet for IP-7's `.claude/rules/bridge-essential.md` amendment; no new MemBase rows.

## Pre-Filing Preflight

Re-run after this REVISED-2 entry is added to `bridge/INDEX.md`. Expected `preflight_passed: true`, no missing required specs, no blocking clause gaps.

## Scope (Slice 2 — REVISED-2)

In-scope (REVISED-2 changes in **bold**):

- IP-1: `scripts/single_harness_bridge_dispatcher.py` — unchanged from REVISED-1 (CLI surface includes `--diagnose`).
- IP-2: Windows Task Scheduler installer/uninstaller — **uses `pythonw.exe` + `-Hidden` settings (F4)**, **adds `[switch]$DryRun` (F2)**, **F3 assertion shape clarified in IP-5**.
- IP-3: `config/agent-control/system-interface-map.toml` entry — unchanged.
- IP-4: Doctor check upgrade (WARN severity) — unchanged from REVISED-1.
- IP-5: Slice 2 integration tests — **expanded** per F1/F2/F3/F4 fixes.
- IP-7: `.claude/rules/bridge-essential.md` amendment — unchanged.
- IP-8: Cross-harness trigger topology gate — **strengthened with audit-log + dispatch-state evidence (F1)**.

Out-of-scope (DECISION DEFERRED, unchanged): macOS/Linux installers, MemBase status promotion of Slice 1 specs, per-mode interval overrides, DCL severity ratchet.

## Implementation Plan

### IP-1 — `scripts/single_harness_bridge_dispatcher.py` (NEW)

Unchanged from REVISED-1. Single-file Python script with all 9 behaviors (project-root resolution, single-instance lock, foreground-suppression, applicability check, INDEX read + signature compute, signature-change predicate, subprocess spawn, fire-and-forget, shared state path) plus CLI surface including `--diagnose`.

### IP-2 — Windows Task Scheduler installer + uninstaller — REVISED PER F2 + F4

`scripts/install_single_harness_dispatcher_task.ps1` (NEW):

```powershell
param(
    [string]$TaskName = "GTKB-SingleHarnessBridgeDispatcher",
    [string]$ProjectRoot = "E:\GT-KB",
    [int]$IntervalMinutes = 5,
    [switch]$DryRun
)

$scriptPath = Join-Path $ProjectRoot "scripts\single_harness_bridge_dispatcher.py"
$pythonwExe = "pythonw.exe"  # F4: GUI-subsystem variant; no console window allocation

# F4: Use pythonw.exe (no console) + Hidden setting (defense-in-depth UI suppression).
$action = New-ScheduledTaskAction -Execute $pythonwExe `
    -Argument "`"$scriptPath`" --project-root `"$ProjectRoot`"" `
    -WorkingDirectory $ProjectRoot
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes)
# F4: Hidden=$true at the Task Scheduler level (defense-in-depth).
$settings = New-ScheduledTaskSettingsSet -Hidden

if ($DryRun) {
    Write-Output "WOULD REGISTER TaskName=$TaskName Execute=$pythonwExe Arguments=`"$scriptPath`" --project-root `"$ProjectRoot`""
    exit 0
}

# Idempotent registration: Unregister-then-Register pattern (Set-ScheduledTask
# does not allow changing all trigger/settings attributes in place).
if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}
Register-ScheduledTask -TaskName $TaskName -Action $action `
    -Trigger $trigger -Settings $settings -RunLevel Limited
```

F4 fix: `pythonw.exe` is the Windows GUI-subsystem Python interpreter that does NOT allocate a console at process start. `-Hidden` setting on the task suppresses any residual UI surface. Both measures together satisfy `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` § Platform Bindings (Windows) "non-interactive Python invocation ... so it does not surface a console window".

F2 fix: `[switch]$DryRun` is a first-class parameter. When set, the installer prints a single parseable line `WOULD REGISTER TaskName=... Execute=... Arguments=...` to stdout and exits 0 without calling `Register-ScheduledTask`.

`scripts/uninstall_single_harness_dispatcher_task.ps1` (NEW):

```powershell
param(
    [string]$TaskName = "GTKB-SingleHarnessBridgeDispatcher",
    [switch]$DryRun
)
if ($DryRun) {
    Write-Output "WOULD UNREGISTER TaskName=$TaskName"
    exit 0
}
if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Output "Unregistered TaskName=$TaskName"
} else {
    Write-Output "TaskName=$TaskName not registered; nothing to remove"
}
```

### IP-3 — `config/agent-control/system-interface-map.toml` entry

Unchanged from `-001`/`-003`.

### IP-4 — Doctor check upgrade

Unchanged from REVISED-1. WARN severity for all "applicable + present-but-broken" cases (script missing, task missing, task stale). PASS for "applicable + healthy" and "not applicable". WARN for "applicable on non-Windows host".

### IP-5 — Slice 2 integration tests — REVISED PER F1 + F2 + F3 + F4

`platform_tests/scripts/test_single_harness_bridge_dispatcher.py` (NEW):

- All tests from `-003` REVISED-1 carry forward.

`platform_tests/scripts/test_single_harness_dispatcher_task_installer.py` (NEW; Windows-only):

- `test_installer_registers_task` — invokes installer with `-TaskName <nonce>`; asserts `Get-ScheduledTask <nonce>` returns the task.
- `test_installer_idempotent` — runs installer twice with same nonce; asserts single registered task.
- `test_uninstaller_removes_task` — registers + uninstalls; asserts task absent.
- `test_uninstaller_idempotent_on_missing_task` — uninstaller on non-existent task exits 0.
- `test_installer_preserves_non_targeted_task` — pre-registers `GTKB-Preserve-Test-<nonce-A>`; installer runs with `-TaskName GTKB-SingleHarnessBridgeDispatcher-Test-<nonce-B>`; asserts both tasks present with original definitions.
- **NEW per F2:** `test_installer_dry_run_does_not_register` — invokes installer with `-TaskName <nonce> -DryRun`; asserts stdout contains `WOULD REGISTER TaskName=<nonce>` AND `Get-ScheduledTask <nonce>` returns nothing (task NOT registered).
- **NEW per F2:** `test_uninstaller_dry_run_does_not_unregister` — pre-registers task; runs uninstaller with `-DryRun`; asserts task still present; stdout contains `WOULD UNREGISTER TaskName=<nonce>`.
- **NEW per F3 (revised assertion shape):** `test_installer_task_action_uses_absolute_script_path` — registers test task; reads `Get-ScheduledTask <nonce>`; asserts:
  - `.Actions[0].Execute` equals `pythonw.exe` (covers F4 too).
  - Tokenize `.Actions[0].Arguments` by space (handling quoted segments); first token is an absolute path matching `^[A-Z]:\\.*\\scripts\\single_harness_bridge_dispatcher\.py$` (drive-anchored, end-anchored on the first token only).
  - Tokenized arguments separately contain `--project-root` followed by an absolute path matching `^[A-Z]:\\` (the project root).
- **NEW per F4:** `test_installer_task_action_uses_no_console_settings` — registers test task; reads `Get-ScheduledTask <nonce>`; asserts:
  - `.Actions[0].Execute -eq "pythonw.exe"` (NOT `python.exe`).
  - `.Settings.Hidden -eq $true`.

`platform_tests/scripts/test_single_harness_doctor_check_upgrade.py` (NEW):

Unchanged from REVISED-1 (WARN severity for all relevant cases).

`platform_tests/scripts/test_cross_harness_bridge_trigger.py` (EXTEND per F1 strengthening):

- **NEW per F1 (renamed + strengthened):** `test_cross_harness_trigger_noop_in_single_harness_topology_records_audit_evidence`:
  - Synthesize a role-map fixture with one harness ID holding multi-element role-set `["prime-builder", "loyal-opposition"]`.
  - Patch `subprocess.Popen` to assert it's never called.
  - Invoke `run_trigger`.
  - Assert return value is `{"skipped": True, "reason": "single_harness_topology_not_applicable"}`.
  - Assert Popen.call_count == 0.
  - Assert `.gtkb-state/bridge-poller/dispatch-failures.jsonl` exists.
  - Assert it contains EXACTLY 2 JSONL entries, one per role label, each with:
    - `reason == "single_harness_topology_not_applicable"`
    - `recipient` is `"prime-builder"` for one entry and `"loyal-opposition"` for the other.
    - `launched is False`.
    - `error_message` references the SPEC's coexistence clause.
  - Assert `.gtkb-state/bridge-poller/dispatch-state.json` exists with:
    - `recipients["prime-builder"]["last_result"] == "single_harness_topology_not_applicable"`.
    - `recipients["loyal-opposition"]["last_result"] == "single_harness_topology_not_applicable"`.
    - Both records have `updated_at` field.

### IP-7 — `.claude/rules/bridge-essential.md` amendment

Unchanged from `-001`/`-003`.

### IP-8 — Cross-harness trigger topology gate — REVISED PER F1

`scripts/cross_harness_bridge_trigger.py` gains:

```python
def _is_single_harness_topology(project_root: Path) -> bool:
    """Return True iff the role map records a single harness ID with both
    prime-builder AND loyal-opposition in its role-set."""
    try:
        role_map = _read_role_assignments(project_root)
    except ValueError:
        return False  # fail-closed: unreadable role-map -> gate inactive
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
    return False


def _record_single_harness_topology_skip(state_dir: Path) -> None:
    """Write durable audit + dispatch-state evidence for the topology skip.

    Per SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 § Coexistence: in single-
    harness topology, the cross-harness trigger is registered but spawns
    nothing AND resolution fails with an audit-log entry. This function
    preserves the audit-log invariant by recording the skip in both:
      - dispatch-failures.jsonl (one entry per role label)
      - dispatch-state.json (per-recipient last_result)

    Per F1 of bridge/gtkb-single-harness-bridge-dispatcher-slice-2-004.md
    closure in REVISED-2 (`-005`).
    """
    ts = _now_iso()
    for role_label in ("prime-builder", "loyal-opposition"):
        _record_dispatch_failure(
            state_dir,
            {
                "ts": ts,
                "dispatch_id": f"{ts}-{role_label}-topology-skip",
                "recipient": role_label,
                "launched": False,
                "reason": "single_harness_topology_not_applicable",
                "error_message": (
                    "Cross-harness trigger inert in single-harness topology per "
                    "SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 § Coexistence. The "
                    "single-harness bridge dispatcher is the active substrate when "
                    "one harness ID holds a multi-element role-set."
                ),
            },
        )
    # Per-recipient dispatch-state record so --diagnose mode + doctor can
    # surface the topology skip without parsing the failures log.
    state = _load_dispatch_state(state_dir)
    recipients_state = state.get("recipients") if isinstance(state, dict) else {}
    if not isinstance(recipients_state, dict):
        recipients_state = {}
    recipients_state = _migrate_recipients_state_keys(recipients_state)
    for role_label in ("prime-builder", "loyal-opposition"):
        prior = recipients_state.get(role_label) if isinstance(recipients_state.get(role_label), dict) else {}
        if not isinstance(prior, dict):
            prior = {}
        prior["last_result"] = "single_harness_topology_not_applicable"
        prior["updated_at"] = ts
        recipients_state[role_label] = prior
    payload = {
        "schema_version": 1,
        "updated_at": ts,
        "recipients": recipients_state,
    }
    _write_dispatch_state(state_dir, payload)


def run_trigger(
    *,
    project_root: Path,
    state_dir: Path,
    max_items: int = DEFAULT_MAX_ITEMS,
    dry_run: bool = False,
) -> dict[str, Any]:
    if os.environ.get(LOOP_PREVENTION_ENV_VAR) == "1":
        return {"skipped": True, "reason": "loop_prevention_env_var"}

    # Per IP-8 of bridge/gtkb-single-harness-bridge-dispatcher-slice-2-005.md
    # REVISED-2 (F1 closure of -004): trigger is inert in single-harness
    # topology AND records SPEC-required durable audit evidence before
    # short-circuiting.
    if _is_single_harness_topology(project_root):
        _record_single_harness_topology_skip(state_dir)
        return {"skipped": True, "reason": "single_harness_topology_not_applicable"}

    # ... existing dispatch logic unchanged
```

The audit-log + dispatch-state evidence preserves the SPEC's coexistence-clause invariant exactly. Future liveness diagnosis tools (doctor's `_check_bridge_dispatch_liveness`, cross-harness trigger's `--diagnose` mode) see explicit "topology skip" entries instead of inferring inertness from missing data.

## Spec-Derived Test Plan

(Carry-forward from `-003` with REVISED-2 corrections + additions.)

| Test | Spec/Requirement | Method |
|---|---|---|
| T-SHD-S2-signature-byte-identical | SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 § Wake Mechanism step 2 | test_signature_byte_identical_to_trigger |
| T-SHD-S2-multi-harness-noop | ADR-SINGLE-HARNESS-OPERATING-MODE-001 | test_dispatcher_no_op_in_multi_harness_topology |
| T-SHD-S2-spawn-on-signature-change | SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 § Wake Mechanism step 3 | test_dispatcher_spawns_in_single_harness_topology_on_signature_change |
| T-SHD-S2-active-session-suppression | SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 § Idle Suppression | test_dispatcher_suppresses_on_active_session_lock |
| T-SHD-S2-signature-dedup | DCL-SMART-POLLER-AUTO-TRIGGER-001 v2 | test_dispatcher_loop_prevention_via_signature_dedup |
| T-SHD-S2-canonical-keyword | SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 | test_dispatcher_emits_canonical_keyword_first_line |
| T-SHD-S2-audit-log | PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001 v2 | test_dispatcher_records_dispatch_failures_jsonl |
| T-SHD-S2-diagnose-no-mutation | IP-1 CLI + system-interface-map read_method | test_dispatcher_diagnose_emits_liveness_summary |
| T-SHD-S2-installer-registers | DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 § Platform Bindings | test_installer_registers_task |
| T-SHD-S2-installer-idempotent | DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 § Installation | test_installer_idempotent |
| T-SHD-S2-uninstall | DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 § Installation | test_uninstaller_removes_task, test_uninstaller_idempotent_on_missing_task |
| T-SHD-S2-task-name-isolation | F3 of -002 closure | test_installer_preserves_non_targeted_task |
| **T-SHD-S2-installer-dry-run (F2)** | F2 of -004: installer must accept `-DryRun` | test_installer_dry_run_does_not_register |
| **T-SHD-S2-uninstaller-dry-run (F2)** | F2 of -004 (parity) | test_uninstaller_dry_run_does_not_unregister |
| **T-SHD-S2-absolute-script-path (F3, corrected)** | IP-2 absolute path + corrected assertion shape | test_installer_task_action_uses_absolute_script_path |
| **T-SHD-S2-no-console-settings (F4)** | DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 § Platform Bindings (no-console) | test_installer_task_action_uses_no_console_settings |
| T-SHD-S2-doctor-task-fresh | DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 § Doctor Check | test_doctor_passes_when_task_registered_and_fresh |
| T-SHD-S2-doctor-task-stale | DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 § Doctor Check | test_doctor_warns_when_task_registered_but_stale |
| T-SHD-S2-doctor-missing-task-WARN | DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 § Doctor Check (WARN per DCL) | test_doctor_warns_when_applicable_and_script_present_but_task_missing |
| T-SHD-S2-doctor-non-windows-warn | DCL Slice 2 ships Windows-only | test_doctor_warn_when_non_windows_host_applicable |
| T-SHD-S2-system-interface-map | IP-3 + DCL-CONCEPT-ON-CONTACT-001 | grep config/agent-control/system-interface-map.toml |
| T-SHD-S2-bridge-essential | IP-7 narrative amendment | grep .claude/rules/bridge-essential.md |
| **T-SHD-S2-trigger-noop-with-audit-evidence (F1 strengthened)** | SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 § Coexistence (audit-log invariant) | test_cross_harness_trigger_noop_in_single_harness_topology_records_audit_evidence |

Bold rows = changed/added in REVISED-2 to close F1-F4.

## Acceptance Criteria

(Carry-forward from `-001`/`-003` with REVISED-2 additions.)

- [ ] `scripts/single_harness_bridge_dispatcher.py` exists and passes all script-level tests including `--diagnose`.
- [ ] Windows installer + uninstaller pass installer tests on a Windows host AND accept `-TaskName` + `-DryRun` AND use `pythonw.exe` + `Hidden=$true` settings.
- [ ] `config/agent-control/system-interface-map.toml` contains the new entry.
- [ ] Doctor check upgrade passes all tests with WARN severity for missing/stale-task cases.
- [ ] `.claude/rules/bridge-essential.md` amendment landed with narrative-artifact-approval packet evidence.
- [ ] Cross-harness trigger IP-8 topology gate writes durable audit-log + dispatch-state evidence before short-circuiting; `test_cross_harness_trigger_noop_in_single_harness_topology_records_audit_evidence` passes.
- [ ] Installer test `test_installer_task_action_uses_absolute_script_path` uses structured assertion (Execute + tokenized Arguments) rather than full-string anchored regex.
- [ ] Installer test `test_installer_task_action_uses_no_console_settings` verifies `pythonw.exe` + `Hidden=$true`.
- [ ] Installer tests `test_installer_dry_run_does_not_register` and `test_uninstaller_dry_run_does_not_unregister` exercise the dry-run path without mutating Task Scheduler state.
- [ ] End-to-end verification on a Windows host.
- [ ] Post-impl regression command passes from a bridge-auto-dispatched shell.

## Risk + Rollback

(Carry-forward from `-001`/`-003` with REVISED-2 strengthening on R1.)

- R1 (resolved, no longer Medium): the IP-8 topology gate now writes durable audit + dispatch-state evidence. Liveness diagnosis tools have explicit signals; no silent inertness.
- R2 (Low): Windows Task Scheduler API differs across versions. Mitigation: PowerShell `Register-ScheduledTask` covers Windows 8+ uniformly; installer header documents Windows 10+ requirement.
- R3 (closed by `-001`): system-interface-map schema entry uses `concept_vs_artifact = "axis-1-dispatchable"`. If novel, schema-defining comment or accepted alternate.
- R4 (Low): non-Windows doctor path. Mitigation: platform-gated check returns WARN with platform-extension pointer.
- R5 (Medium): shared `.gtkb-state/bridge-poller/` state path. Mitigation: IP-8 topology gate enforces mutual exclusion at runtime; doctor's `_check_role_set_topology_consistency` catches mis-configuration.
- R6 (Low): false-positive single-harness topology detection if role-map is misconfigured. Mitigation: doctor's role-set-topology check catches it; the IP-8 fail-closed semantic (unreadable role-map → gate inactive) avoids accidental inertness.
- **R7 (Low; NEW in REVISED-2):** the IP-8 audit-log records two entries per trigger wake while in single-harness topology — if the trigger fires frequently (every PostToolUse/Stop), the dispatch-failures.jsonl can grow. Mitigation: in single-harness topology the trigger fires only if hooks are still registered AND interactive sessions are active; the audit-log growth rate is bounded by interactive activity, not by the scheduled-task wake cadence. A future log-rotation slice (not Slice 2) can address steady-state log size.

**Rollback:** unchanged from `-003`. IP-8 rollback is removing `_is_single_harness_topology` + `_record_single_harness_topology_skip` + the `run_trigger` short-circuit.

## Files Expected To Change

(Carry-forward from `-003` unchanged; IP-8 implementation file remains `scripts/cross_harness_bridge_trigger.py` with an additional `_record_single_harness_topology_skip` helper function.)

- `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-005.md` (this REVISED-2 file).
- `bridge/INDEX.md` (REVISED entry prepended).
- `scripts/single_harness_bridge_dispatcher.py` (NEW; ~400-500 LOC; IP-1).
- `scripts/install_single_harness_dispatcher_task.ps1` (NEW; IP-2; `pythonw.exe`, `-Hidden`, `-DryRun`).
- `scripts/uninstall_single_harness_dispatcher_task.ps1` (NEW; IP-2; `-DryRun`).
- `config/agent-control/system-interface-map.toml` (extend; IP-3).
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` (upgrade `_check_single_harness_dispatcher_when_required`; IP-4; WARN severity).
- `scripts/cross_harness_bridge_trigger.py` (IP-8; add `_is_single_harness_topology` + `_record_single_harness_topology_skip` + `run_trigger` short-circuit).
- `platform_tests/scripts/test_single_harness_bridge_dispatcher.py` (NEW; IP-5).
- `platform_tests/scripts/test_single_harness_dispatcher_task_installer.py` (NEW; IP-5; Windows-only).
- `platform_tests/scripts/test_single_harness_doctor_check_upgrade.py` (NEW; IP-5).
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py` (EXTEND; IP-8 test with audit-evidence assertions).
- `.claude/rules/bridge-essential.md` (amendment; IP-7).
- `.groundtruth/formal-artifact-approvals/<date>-claude-rules-bridge-essential-md-single-harness-dispatcher-substrate.json` (NEW; IP-7 narrative packet).

## Specification Links

(Carry-forward from `-003` unchanged.)

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001`
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` (§ Coexistence; audit-log invariant cited by IP-8 strengthening)
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` (§ Platform Bindings cited by IP-2 F4 fix; § Doctor Check WARN cited by IP-4)
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`
- `GOV-HARNESS-ROLE-PORTABILITY-001`
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001`
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`
- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` v2
- `DCL-SMART-POLLER-AUTO-TRIGGER-001` v2
- `DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001` v2
- `PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001` v2 (audit-log discipline preserved by IP-8 strengthening)
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`
- `.claude/rules/operating-role.md`
- `.claude/rules/canonical-terminology.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/bridge-essential.md`

## Recommended Commit Type

`feat:` — same justification as `-001`/`-003`. REVISED-2 strengthens IP-8 with audit-log evidence, corrects installer test assertions, adds `-DryRun` support, and enforces the no-console DCL constraint — all defect repairs and reinforcements within the original Slice 2 feature scope.

## Loyal Opposition Asks

1. Confirm F1 closed: IP-8 writes per-role audit-log entries to `dispatch-failures.jsonl` AND per-recipient `last_result` records to `dispatch-state.json` before short-circuiting; the SPEC's "resolution fails with an audit-log entry" invariant is preserved.
2. Confirm F2 closed: installer + uninstaller accept `[switch]$DryRun` with defined behavior (rendered command line to stdout, no Task Scheduler mutation, exit 0); test pair `test_installer_dry_run_does_not_register` + `test_uninstaller_dry_run_does_not_unregister` verifies.
3. Confirm F3 closed: installer test uses structured assertion (Execute + tokenized Arguments inspection); no full-string anchored regex; absolute path verification on first token; `--project-root` flag verified separately.
4. Confirm F4 closed: installer uses `pythonw.exe` + `-Hidden` settings; test `test_installer_task_action_uses_no_console_settings` asserts both.
5. Confirm the new R7 risk (audit-log growth in single-harness topology with frequent hook fires) is acceptably bounded by interactive-activity rate-limiting; log rotation is a future-slice concern.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
