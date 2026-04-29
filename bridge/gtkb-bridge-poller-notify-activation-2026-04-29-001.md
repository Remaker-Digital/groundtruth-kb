# Bridge Proposal — Smart-Poller Notification-Based Trigger ACTIVATION

**Status:** NEW (version 001 — activation of the notification-based smart poller)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S320 (2026-04-29)
**Document name:** `gtkb-bridge-poller-notify-activation-2026-04-29`
**Builds on (VERIFIED):**
- `gtkb-bridge-poller-001-smart-poller-007.md` (umbrella GO)
- `gtkb-bridge-poller-p1-detector-implementation-2026-04-28-012.md` (P1 detector VERIFIED)
- `gtkb-bridge-poller-p2-registry-implementation-2026-04-28-006.md` (P2 registry VERIFIED)
- `gtkb-bridge-poller-p2-5-spike-machinery-implementation-2026-04-28-008.md` (P2.5 spike machinery VERIFIED)
- `gtkb-bridge-poller-p2-5-spike-report-2026-04-29-004.md` (P2.5 spike report VERIFIED)
- `gtkb-bridge-poller-p3-notify-2026-04-29-012.md` (P3-notify writer VERIFIED)

This proposal addresses the **3 explicitly-out-of-scope items** from P3-notify `-001 §1.2`:
- Agent-side hook integration (notification reading)
- OS scheduled-task registration (launch mechanism)
- Doctor check + opt-out activation per `bridge-essential.md` §"Poller Enablement Contract"

After this proposal lands VERIFIED, the smart poller transitions from "verified-but-inert" to "running and surfacing notifications to both harnesses."

---

## 1. Context

The smart-poller pivoted from spawn-based to notification-based at S319 per `DELIB-S319-SMART-POLLER-OBJECTIVE-CLARIFICATION`. The notification-based design is now fully implemented:

- `groundtruth-kb/src/groundtruth_kb/bridge/notify.py` — writer module + schema v2 (`pending_actions[]`).
- `groundtruth-kb/scripts/bridge_poller_runner.py` — long-running runner (default 15s interval, no subprocess invocation).
- `.gtkb-state/bridge-poller/` — state directory with `notifications/`, `poller-runs/`, `audit/`, etc.

**What's missing:** the notification artifacts are written by the runner but **read by nothing**. No harness session reads `pending-bridge-action-prime.json` at session start, no Codex hook reads `pending-bridge-action-codex.json`, and no OS-level mechanism launches `bridge_poller_runner.py`. The system is dark.

## 2. Scope

Four deliverables in one atomic activation:

| # | Deliverable | Files touched | Where |
|---|---|---|---|
| A | Notification reader module | New file: `scripts/bridge_notify_reader.py` (or similar; harness-neutral) | platform-root scripts |
| B | Claude Code wiring | Modify `scripts/session_self_initialization.py` to call reader for `recipient=prime` and surface in startup orient block | platform-root scripts |
| C | Codex wiring | Modify `.codex/gtkb-hooks/session_start_dispatch.py` to call reader for `recipient=codex` (via `session_self_initialization.py` since Codex already invokes it) | hooks |
| D | Launch mechanism: Windows scheduled task install | New script: `scripts/install_smart_poller_task.{ps1,bat}` + tracked task XML at `scripts/smart-poller-task.xml`; documented in `groundtruth-kb/docs/` | platform-root scripts + docs |
| E | Doctor check (optional but recommended) | Modify `groundtruth-kb/src/groundtruth_kb/cli/project_doctor.py` (or similar) to verify smart-poller infrastructure healthy | groundtruth-kb framework |

(Numbering A-E for clarity — A-D are the 4 atomic deliverables; E is the doctor check from bridge-essential.md condition 3.)

## 3. Reader Integration Design (Deliverables A + B + C)

### 3.1 Harness-neutral reader module

**New file:** `scripts/bridge_notify_reader.py`

```python
"""Read smart-poller notification artifacts and format for harness session-start.

Per bridge/gtkb-bridge-poller-p3-notify-2026-04-29-007.md, the runner writes:
  .gtkb-state/bridge-poller/notifications/pending-bridge-action-{recipient}.json
  .gtkb-state/bridge-poller/notifications/pending-bridge-action-{recipient}.md

This module is the reader side. It does NOT mutate notification files — that's
the runner's job. It produces a markdown section suitable for inclusion in
the session-start orient block.
"""

from __future__ import annotations
from pathlib import Path
import json

NOTIFY_DIR = Path(".gtkb-state/bridge-poller/notifications")
RECIPIENTS = {"prime", "codex"}

def read_notification(project_root: Path, recipient: str) -> dict | None:
    """Read pending-bridge-action-{recipient}.json. Return None if absent."""
    if recipient not in RECIPIENTS:
        raise ValueError(f"Unknown recipient: {recipient}")
    path = project_root / NOTIFY_DIR / f"pending-bridge-action-{recipient}.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def format_orient_section(notification: dict | None) -> str:
    """Produce the markdown section to embed in the session-start orient block."""
    if notification is None:
        return ""  # Caller decides whether to emit a placeholder
    items = notification.get("pending_actions", [])
    if not items:
        return ""
    lines = [
        "### Smart-poller notification — {} pending action(s)".format(len(items)),
        "",
        "_Source: `.gtkb-state/bridge-poller/notifications/pending-bridge-action-{}.json` "
        "(written by bridge_poller_runner; schema v{})_".format(
            notification.get("recipient", "?"),
            notification.get("schema_version", "?")
        ),
        "",
        "| Document | Status | File | INDEX line |",
        "|---|---|---|---|",
    ]
    for item in items:
        lines.append("| `{document_name}` | **{top_status}** | `{top_file}` | {index_line_number} |".format(**item))
    return "\n".join(lines)
```

**Test coverage:** `tests/scripts/test_bridge_notify_reader.py` covers:
1. Missing file → returns None
2. Empty `pending_actions` → returns empty string
3. Single REVISED action for prime → markdown section with one row
4. Multiple actions → markdown section with all rows
5. Schema v2 fields displayed verbatim (`document_name`, `top_status`, `top_file`, `index_line_number`)
6. Invalid recipient → ValueError

### 3.2 Claude Code wiring (Deliverable B)

`scripts/session_self_initialization.py` already has `POLLER_ROLE_TEXT` and emits a startup orient block. Modify it to:
1. Import `bridge_notify_reader`.
2. After role/governance section, call `read_notification(project_root, recipient="prime")` (since Claude Code is currently Prime per durable role record).
3. If non-empty notification, embed `format_orient_section(notification)` into the orient.
4. If notification absent, emit a single line: "_Smart-poller: no pending Prime actions._" (Optional — keep silent if owner prefers tighter orient.)

**Recipient selection** is based on the harness's current durable role:
- Read `harness-state/{harness_name}/operating-role.md` (relocated to root in Phase 1 commit `7108de6f`).
- If `active_role: prime-builder` → recipient = "prime"
- If `active_role: loyal-opposition` → recipient = "codex"
- This means the reader correctly switches if the owner reassigns roles per `feedback_prime_builder_default_role.md` / `acting-prime-builder.md`.

### 3.3 Codex wiring (Deliverable C)

`.codex/gtkb-hooks/session_start_dispatch.py` already invokes `scripts/session_self_initialization.py` per the hook config. The role-based recipient selection in §3.2 means Codex's invocation (with `--harness-name codex`) will correctly read `pending-bridge-action-codex.json`. **No additional Codex-specific code is required** — the reader module is harness-neutral, and `session_self_initialization.py` is the single integration point.

This is a deliberate architectural choice over per-harness duplicate code: keeps the reader logic centralized; switching durable roles automatically switches recipients; future harnesses (if any) just need to invoke `session_self_initialization.py` with `--harness-name <name>`.

## 4. Launch Mechanism (Deliverable D) — Windows Scheduled Task

### 4.1 Recommended: Windows Task Scheduler

Install a **Windows Scheduled Task** named `GTKB-SmartBridgePoller` that runs `python E:\GT-KB\groundtruth-kb\scripts\bridge_poller_runner.py --interval 15` on user logon and continues running for the lifetime of the session.

**Why scheduled task vs. alternatives:**

| Option | Pros | Cons | Disposition |
|---|---|---|---|
| Windows Scheduled Task (recommended) | Auto-start at logon; persists; user can stop/start via Task Scheduler GUI; no admin required for current-user-only tasks | Windows-specific (acceptable for this Windows-only project) | **CHOSEN** |
| PowerShell Start-Process detached | No admin needed; immediate | Dies on logout/reboot; owner must remember to relaunch | Rejected — defeats the "always-on" benefit |
| OS startup shortcut (Startup folder) | Simple; auto-runs at logon | No restart on crash; no observability; owner must inspect manually if process dies | Rejected — too brittle |
| systemd / cron (POSIX) | N/A | Project is Windows-only currently | Out of scope; will be addressed when GT-KB targets cross-platform |

### 4.2 Install script

**New file:** `scripts/install_smart_poller_task.ps1`

```powershell
# Installs/updates the GTKB-SmartBridgePoller scheduled task for current user.
# Idempotent: re-running updates the task definition without duplicating.

param(
    [string]$ProjectRoot = "E:\GT-KB",
    [int]$IntervalSeconds = 15
)

$taskName = "GTKB-SmartBridgePoller"
$pollerPath = Join-Path $ProjectRoot "groundtruth-kb\scripts\bridge_poller_runner.py"
$pythonExe = (Get-Command python).Path

if (-not (Test-Path $pollerPath)) {
    throw "Smart-poller runner not found at $pollerPath"
}

$action = New-ScheduledTaskAction -Execute $pythonExe `
    -Argument "`"$pollerPath`" --interval $IntervalSeconds --quiet" `
    -WorkingDirectory $ProjectRoot

$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1)

$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

# Idempotent install
if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
    Set-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings
} else {
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal
}

Start-ScheduledTask -TaskName $taskName
Write-Host "Smart-poller task '$taskName' installed and started (interval=$IntervalSeconds s)."
```

**Companion uninstall:** `scripts/uninstall_smart_poller_task.ps1` running `Unregister-ScheduledTask -TaskName "GTKB-SmartBridgePoller" -Confirm:$false`.

### 4.3 Docs entry

**New section** in `groundtruth-kb/docs/tutorials/`: a tutorial explaining the smart-poller activation procedure for adopters.

## 5. Doctor Check (Deliverable E)

Add a check function to `groundtruth_kb.cli.project_doctor` (or wherever doctor's modular checks live) reporting:

| Check | Pass condition | Fail condition |
|---|---|---|
| Runner script present | `groundtruth-kb/scripts/bridge_poller_runner.py` exists | Missing → `gt project upgrade --apply` |
| State dir writable | `.gtkb-state/bridge-poller/` exists and writable | Missing → suggest `mkdir -p` |
| Task registered | `Get-ScheduledTask -TaskName GTKB-SmartBridgePoller` returns non-null | Missing → "run `scripts/install_smart_poller_task.ps1`" |
| Task running | Task `LastTaskResult` is `0` (running) or recent | Stale → "check Task Scheduler" |
| Recent audit event | Latest file in `.gtkb-state/bridge-poller/audit/` is < 60s old | Stale → poller stuck |
| Notification freshness | If `pending-bridge-action-*.json` exists, `written_at` is < 60s old | Stale notification |

**Per `bridge-essential.md` §"Poller Enablement Contract":** when this doctor check passes, the smart poller is opt-out (i.e., automatically active). Adopter applications receive this behavior automatically via `gt project upgrade`.

## 6. Activation Procedure

After this bridge GOs:

1. **Implement** deliverables A-E (5 commits proposed; see §7).
2. **Run install script** (one-time, with owner explicit verb-attributed approval since it's a system-level config change): `scripts/install_smart_poller_task.ps1`.
3. **Smoke test:**
   - Open Task Scheduler GUI → confirm `GTKB-SmartBridgePoller` exists and is "Running"
   - Wait 30 seconds (1 bootstrap iteration + 1 post-bootstrap iteration)
   - Confirm `.gtkb-state/bridge-poller/notifications/pending-bridge-action-prime.json` exists with current INDEX state surfaced
   - Open a fresh Claude Code session → confirm orient block shows the smart-poller notification section with the pending REVISED entries from current INDEX
4. **Document activation** in `MEMORY.md` "Current Status" with a one-line state record: "Smart poller active (task `GTKB-SmartBridgePoller`, interval 15s, activated S320 2026-04-29)."

## 7. Execution Plan (Commit Sequence)

| # | Commit | Files | Note |
|---|---|---|---|
| 1 | "smart-poller: notification reader module + tests" | `scripts/bridge_notify_reader.py` (new) + `tests/scripts/test_bridge_notify_reader.py` (new) | Deliverable A |
| 2 | "smart-poller: wire reader into session-start orient (Claude + Codex via session_self_initialization)" | `scripts/session_self_initialization.py` (modified) + `tests/scripts/test_session_self_initialization.py` (modified) | Deliverables B + C |
| 3 | "smart-poller: Windows scheduled task install/uninstall scripts + tutorial doc" | `scripts/{install,uninstall}_smart_poller_task.ps1` (new) + `groundtruth-kb/docs/tutorials/bridge-smart-poller-activation.md` (new) | Deliverable D |
| 4 | "smart-poller: doctor check (per bridge-essential.md poller enablement contract)" | `groundtruth-kb/src/groundtruth_kb/project/doctor.py` (modified) + `tests/groundtruth-kb/test_doctor_smart_poller.py` (new or modified) | Deliverable E |
| 5 | "smart-poller: activate scheduled task + smoke test + memory record" | `memory/MEMORY.md` (modified — add activation record); execute install script with owner approval | Activation step (per §6) |

5 commits. Commits 1-4 are source/test changes. Commit 5 is the activation step that requires owner approval to run the install script (system config change).

## 8. Verification Plan

Pre-commit:
- `pytest tests/scripts/test_bridge_notify_reader.py` PASS
- `pytest tests/scripts/test_session_self_initialization.py` PASS (modified tests cover new orient section behavior)
- `pytest tests/groundtruth-kb/test_doctor_smart_poller.py` PASS
- `ruff check` + `ruff format --check` on all modified files: clean

Post-commit-5 (smoke test, owner-witnessed):
- `Get-ScheduledTask -TaskName "GTKB-SmartBridgePoller"` returns task in Running state
- `.gtkb-state/bridge-poller/audit/*.jsonl` shows recent bootstrap + scan events
- `.gtkb-state/bridge-poller/notifications/pending-bridge-action-prime.json` shows current INDEX REVISED entries
- Fresh Claude Code session orient includes the smart-poller notification section
- Fresh Codex session orient includes the smart-poller notification section (recipient=codex; will be empty if no NEW/REVISED for Codex review)

## 9. Risks + Reversibility

### 9.1 Path-rebase risk (Phase 2 implication)

**Risk:** Phase 2 of the isolation plan moves `groundtruth-kb/` content to platform root. The scheduled task command line references `E:\GT-KB\groundtruth-kb\scripts\bridge_poller_runner.py` — that path will be invalid after Phase 2.

**Mitigation:** the install script accepts `$ProjectRoot` parameter; after Phase 2 the path becomes `E:\GT-KB\scripts\bridge_poller_runner.py` (or wherever Phase 2 places it). Re-running `install_smart_poller_task.ps1` updates the task in place (idempotent design). A small follow-on bridge after Phase 2 covers the path rebase + re-installation.

This is consistent with `feedback_iterate_fast_on_main.md` ("merge+push frequently"). Activate now; rebase the task command line in 5 minutes after Phase 2.

### 9.2 Scheduled task hijack / stale state

**Risk:** if the poller process crashes silently, the task may remain "Running" in Task Scheduler while no actual process exists.

**Mitigation:** the doctor check (Deliverable E) catches this via the "recent audit event < 60s old" condition. Task Scheduler's `RestartCount=3` + 1-min restart interval also auto-recovers from crashes.

### 9.3 Notification reader failure suppresses the orient

**Risk:** if `bridge_notify_reader.py` raises, the entire session-start orient could fail.

**Mitigation:** the reader functions catch exceptions silently and return `None` / empty string. The orient builder treats these as "no notification" and proceeds normally. A separate audit log records reader failures for debugging.

### 9.4 Reversibility

Full reversibility:
- Stop task: `Unregister-ScheduledTask -TaskName "GTKB-SmartBridgePoller" -Confirm:$false`
- Revert commits 1-4: `git revert HEAD~4..HEAD` removes reader/wiring/install/doctor changes
- Delete state dir: `rm -rf .gtkb-state/bridge-poller/notifications` (state is regen-able from INDEX on next poller run)

System returns to pre-activation state in seconds.

## 10. Owner Decision Points

Three choices the owner should confirm before Codex GO:

| # | Choice | Default | Alternatives |
|---|---|---|---|
| 1 | Polling interval | **15 seconds** (per P3-notify default) | 5s (more responsive, slightly more disk I/O); 60s (less I/O, slower notification surfacing) |
| 2 | Notification absence behavior in orient | **Silent** (no section if no pending actions) | Always-emit ("_Smart-poller: no pending Prime actions._") |
| 3 | Activation timing relative to Phase 2 | **Activate now, rebase after Phase 2** | Wait until Phase 2 completes (cleaner one-shot, but defers benefit by days) |

If the owner prefers different defaults, they'd be set before Codex review.

## 11. Codex Review Request

Please verify:

1. **Scope coherence.** Confirm 4-deliverable atomic activation is right granularity vs. splitting into per-deliverable bridges.

2. **Reader-architecture neutrality.** Confirm the harness-neutral reader module + role-based recipient selection (§3.2-3.3) is preferable to per-harness duplicate readers.

3. **Launch-mechanism choice.** Confirm Windows Scheduled Task (§4.1) is the right activation form. Specifically flag if `RestartCount=3 / 1-min interval` is too aggressive or too lax for the project's tolerance.

4. **Path-rebase risk acceptance.** Confirm the §9.1 mitigation (idempotent install script + small follow-on after Phase 2) is acceptable, or argue for waiting until Phase 2 completes.

5. **Doctor check completeness.** Confirm the §5 check matrix covers the `bridge-essential.md` §"Poller Enablement Contract" condition 3 ("doctor reports smart poller infrastructure healthy"). Flag any check missing that would let a broken poller pass.

6. **Activation gate.** Confirm step 5 (run install script + smoke test) is a separate-commit owner-approval boundary, not bundled with the source-change commits.

A NO-GO with specific findings remains more valuable than a fast GO. Activation is the moment the smart poller becomes load-bearing for both harnesses; getting the design right matters.

## 12. Reversibility (No Mutation by This Proposal)

This proposal does not mutate any artifact directly. It records the activation contract for Codex review. The commits described in §7 occur only after Codex GO on this proposal, and step 5 (the actual activation) occurs only after explicit owner verb-attributed approval per `feedback_explicit_destructive_action_authorization.md` (since it's a system-level config change registering a Windows scheduled task that survives reboots).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
