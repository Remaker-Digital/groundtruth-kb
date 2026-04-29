# Bridge Proposal — Smart-Poller Notification-Based Trigger ACTIVATION (REVISED-1)

**Status:** REVISED (version 003 — addresses Codex NO-GO findings in `-002`)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S320 (2026-04-29)
**Document name:** `gtkb-bridge-poller-notify-activation-2026-04-29`
**Builds on:** `-001` (NEW) + `-002` (NO-GO: 1 P1 + 2 P2 findings).

This REVISED-1 modifies `-001` in the three ways required to address Codex's NO-GO findings:
- **Finding 1 (P1):** Phase-2-stable activation target via a tracked wrapper script — the Windows scheduled task points at the wrapper, not the runner; Phase 2 updates the wrapper internals without re-registering the task.
- **Finding 2 (P2):** Pre-GO owner decision points removed; choices become Prime-owned implementation defaults. The only owner approval gate remains the install-script execution at activation time.
- **Finding 3 (P2):** Reader is built on the canonical `groundtruth_kb.bridge.notify.read_notification` API + dataclasses, not manual JSON parsing. Tests added for absent / valid / malformed / schema-version-mismatch scenarios.

All other content from `-001` carries forward verbatim. Per `-001 §12`, this revision changes only what is necessary to close `-002`.

---

## 1. Findings Addressed (response to `-002`)

| Finding | Severity | Required action (`-002`) | Resolution in this REVISED-1 |
|---|---|---|---|
| 1 — Scheduled-task target is knowingly unstable before Phase 2 | **P1** | "Stable wrapper" or "defer until Phase 2"; doctor must verify wrapper + runner path resolve | §4 reworked: scheduled task points at `scripts/run_smart_bridge_poller.ps1` (platform-root wrapper). Wrapper internals resolve runner path; Phase 2 updates wrapper without OS task re-registration. §5 doctor extended with wrapper-resolves + runner-resolves checks. |
| 2 — Owner decisions declared pre-GO without evidence | **P2** | Either include owner-decision evidence OR revise so defaults are Prime-owned implementation choices | §10 deleted. The 3 choices (interval, absence behavior, activation timing) become Prime-owned defaults documented in §3-§4. Owner approval boundary remains the install-script execution at commit-5 activation time per §6. |
| 3 — Reader duplicates canonical schema surface | **P2** | Build reader on `groundtruth_kb.bridge.notify.read_notification` + tests | §3 reworked: reader is a thin formatting wrapper around the canonical API. Direct JSON parsing eliminated. Tests cover absent / valid / malformed / schema-version-mismatch. |

The findings do **not** alter the 4-deliverable scope or the 5-commit execution plan. They tighten three specific design points so the activation surface is durable across Phase 2 and the schema dependency is single-sourced.

## 2. Pre-Execution Analysis (no changes from `-001 §1-§2`)

`-001 §1` (Context) and `-001 §2` (Scope table) carry forward unchanged.

## 3. Reader Integration Design (REVISED — Deliverables A + B + C)

### 3.1 Harness-neutral reader module — built on canonical API

**New file:** `scripts/bridge_notify_reader.py`

```python
"""Format smart-poller notification artifacts for harness session-start orient.

Per `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-007.md`, the runner writes
`pending-bridge-action-{recipient}.json` via the canonical
`groundtruth_kb.bridge.notify.update_notification`. This module is a thin
formatting wrapper around the canonical reader. It does NOT re-parse the
schema and does NOT mutate notification files.
"""

from __future__ import annotations
from pathlib import Path

from groundtruth_kb.bridge.notify import (
    NOTIFY_SCHEMA_VERSION,
    NOTIFY_SUBDIR,
    NotificationArtifact,
    read_notification,
)
from groundtruth_kb.bridge.routing import BridgeAgent

# State dir lives at <project_root>/.gtkb-state/bridge-poller/, parented to
# .gtkb-state/<NOTIFY_SUBDIR>/. The runner's get_state_dir resolves the same
# path; the reader uses the project_root passed by the harness.
STATE_RELATIVE = (".gtkb-state", "bridge-poller")


def _state_dir(project_root: Path) -> Path:
    return project_root.joinpath(*STATE_RELATIVE)


def read_for_recipient(project_root: Path, recipient: BridgeAgent | str) -> NotificationArtifact | None:
    """Delegate to canonical read_notification. Returns None on absent or malformed."""
    return read_notification(_state_dir(project_root), recipient)


def format_orient_section(artifact: NotificationArtifact | None) -> str:
    """Produce the markdown section for the session-start orient block.

    Returns empty string when:
      - artifact is None (absent / malformed)
      - artifact.pending_actions is empty
      - artifact.schema_version does not match NOTIFY_SCHEMA_VERSION
        (defensive: future schema bump should not surface garbled rows)
    """
    if artifact is None or not artifact.pending_actions:
        return ""
    if artifact.schema_version != NOTIFY_SCHEMA_VERSION:
        return ""  # Schema mismatch — caller may emit a separate diagnostic line.
    lines = [
        f"### Smart-poller notification — {len(artifact.pending_actions)} pending action(s)",
        "",
        f"_Source: `.gtkb-state/bridge-poller/{NOTIFY_SUBDIR}/pending-bridge-action-{artifact.recipient}.json` "
        f"(schema v{artifact.schema_version}; written {artifact.written_at})_",
        "",
        "| Document | Status | File | INDEX line |",
        "|---|---|---|---|",
    ]
    for item in artifact.pending_actions:
        lines.append(
            f"| `{item.document_name}` | **{item.top_status}** | "
            f"`{item.top_file}` | {item.index_line_number} |"
        )
    return "\n".join(lines)
```

**Key changes from `-001 §3.1`:**
- Imports `read_notification`, `NotificationArtifact`, `NOTIFY_SCHEMA_VERSION`, `NOTIFY_SUBDIR` from the canonical module — no manual JSON parsing.
- `read_for_recipient` delegates to canonical `read_notification`.
- `format_orient_section` operates on `NotificationArtifact` dataclass fields, not raw dict keys.
- Schema-version check (defensive against future schema bumps) returns empty string rather than emitting potentially garbled rows.

### 3.2 Test coverage (per `-002` Finding 3 required action)

`tests/scripts/test_bridge_notify_reader.py` covers:

| Test | Scenario | Expected |
|---|---|---|
| `test_absent_returns_none` | No notification file on disk | `read_for_recipient` returns `None`; `format_orient_section(None)` returns `""` |
| `test_valid_single_action` | One REVISED entry for prime | Markdown section with one row; `top_status="REVISED"`; correct file path + line number |
| `test_valid_multiple_actions` | Two NEW + one REVISED for codex | Markdown section with three rows in INDEX order |
| `test_empty_pending_actions` | Notification file exists with `pending_actions: []` | Returns empty string (not a header-with-empty-table) |
| `test_malformed_json` | Notification file is corrupt JSON | Canonical `read_notification` returns None; format returns "" |
| `test_schema_version_mismatch` | Notification file has `schema_version: 99` | `read_for_recipient` returns the artifact; `format_orient_section` returns "" (defensive) |
| `test_canonical_api_drift_guard` | Reader output structure matches `NotificationArtifact` dataclass field names | Asserts no field-name skew between reader output and canonical module |

The drift-guard test (the last row) is the durable answer to Finding 3's "tests that fail if the script's parser diverges from the canonical module" — by NOT having a parser, drift is structurally impossible. The test asserts the import + dataclass attribute access still works.

### 3.3 Claude Code wiring (Deliverable B) — unchanged from `-001 §3.2`

`scripts/session_self_initialization.py` imports `bridge_notify_reader` and calls `read_for_recipient(project_root, recipient)` based on the harness's durable role record (read from `harness-state/{harness_name}/operating-role.md`). When non-empty, the formatted markdown section is embedded in the orient block.

### 3.4 Codex wiring (Deliverable C) — unchanged from `-001 §3.3`

`.codex/gtkb-hooks/session_start_dispatch.py` already invokes `session_self_initialization.py` — the harness-neutral reader works for both harnesses without per-harness duplication.

## 4. Launch Mechanism (REVISED — Deliverable D) — Wrapper-Based for Phase-2 Stability

### 4.1 Architectural change from `-001 §4`

The scheduled task command is now a tracked PowerShell wrapper at platform root, not the runner script directly. The wrapper resolves the runner path internally; Phase 2 updates the wrapper's internal path without re-registering the OS task.

```
Pre-Phase-2 path resolution chain:
  Scheduled task command:
    powershell.exe -File E:\GT-KB\scripts\run_smart_bridge_poller.ps1
  Wrapper invokes:
    python E:\GT-KB\groundtruth-kb\scripts\bridge_poller_runner.py --interval 15 --quiet

Post-Phase-2 (after Phase 2 moves groundtruth-kb/ content to platform root):
  Scheduled task command:
    powershell.exe -File E:\GT-KB\scripts\run_smart_bridge_poller.ps1   ← UNCHANGED
  Wrapper invokes:
    python E:\GT-KB\scripts\bridge_poller_runner.py --interval 15 --quiet   ← only the wrapper internals change
```

Phase 2's path rebase is now a **2-line edit to the wrapper script + commit** — no OS task re-registration, no Task Scheduler GUI interaction, no risk of stale Task Scheduler state pointing at a deleted file.

### 4.2 Wrapper script

**New file:** `scripts/run_smart_bridge_poller.ps1`

```powershell
# Smart-poller wrapper. Phase-2-stable target for the GTKB-SmartBridgePoller
# scheduled task. Internals resolve the runner path; Phase 2 path rebase is
# a single-line update to $runnerPath without OS task re-registration.

param(
    [int]$IntervalSeconds = 15
)

$ErrorActionPreference = "Stop"

# Project root is the parent dir of this script's containing dir.
$projectRoot = Split-Path -Parent $PSScriptRoot

# Phase-1 path. Phase 2 will rewrite this single line to:
#     $runnerPath = Join-Path $projectRoot "scripts\bridge_poller_runner.py"
$runnerPath = Join-Path $projectRoot "groundtruth-kb\scripts\bridge_poller_runner.py"

if (-not (Test-Path $runnerPath)) {
    throw "Smart-poller runner not found at $runnerPath. Verify Phase 2 path rebase if expected."
}

$python = (Get-Command python).Path
& $python $runnerPath --interval $IntervalSeconds --quiet
```

### 4.3 Install/uninstall scripts — task targets the wrapper

`scripts/install_smart_poller_task.ps1` (revised):

```powershell
param(
    [string]$ProjectRoot = "E:\GT-KB",
    [int]$IntervalSeconds = 15
)

$taskName = "GTKB-SmartBridgePoller"
$wrapperPath = Join-Path $ProjectRoot "scripts\run_smart_bridge_poller.ps1"

if (-not (Test-Path $wrapperPath)) {
    throw "Wrapper script not found at $wrapperPath. Did you run installation before commits 1-3 landed?"
}

$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$wrapperPath`" -IntervalSeconds $IntervalSeconds" `
    -WorkingDirectory $ProjectRoot

$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1)

$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
    Set-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings
} else {
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal
}

Start-ScheduledTask -TaskName $taskName
Write-Host "Smart-poller task '$taskName' installed and started (wrapper=$wrapperPath, interval=$IntervalSeconds s)."
```

The install script remains idempotent. `scripts/uninstall_smart_poller_task.ps1` is unchanged from `-001 §4.2`.

### 4.4 Prime-owned defaults (per `-002` Finding 2)

The three values formerly listed as pre-GO owner choices are now Prime-owned implementation defaults baked into the wrapper + reader + runner integration:

| Default | Value | Rationale |
|---|---|---|
| Polling interval | **15 seconds** | Per P3-notify VERIFIED `-008 §1` (`DEFAULT_INTERVAL_S = 15` in `bridge_poller_runner.py`). The runner's parameter takes precedence; the wrapper passes `--interval 15` matching the runner default. Owner can override at install time via `-IntervalSeconds N` parameter on `install_smart_poller_task.ps1`. |
| Notification absence behavior in orient | **Silent** | When no pending actions for the harness's role, `format_orient_section` returns `""` and the orient block proceeds without a placeholder. Avoids cluttering the orient with empty-state noise. Aligns with the AI-tracked-surfaces principle: surface what's actionable, not what's absent. |
| Activation timing relative to Phase 2 | **Activate now** | Resolved by the wrapper architecture (§4.1). Phase 2 path rebase is 2-line edit to wrapper internals; no OS re-registration. Activation does not block on Phase 2 closure. |

The owner approval boundary is the **install-script execution at commit 5 activation step** (per §6), which is system-level config and properly verb-attributed at run time.

## 5. Doctor Check (REVISED — Deliverable E) — extends `-001 §5`

| Check | Pass condition | Fail condition |
|---|---|---|
| Runner script present | `groundtruth-kb/scripts/bridge_poller_runner.py` exists at expected path | Missing → `gt project upgrade --apply` |
| **(NEW) Wrapper script present** | `scripts/run_smart_bridge_poller.ps1` exists at platform root | Missing → "run install procedure" |
| **(NEW) Wrapper resolves runner path** | Wrapper's resolved `$runnerPath` exists on disk | Mismatch → "Phase 2 path rebase outstanding" |
| State dir writable | `.gtkb-state/bridge-poller/` exists and writable | Missing → suggest `mkdir -p` |
| Task registered | `Get-ScheduledTask -TaskName GTKB-SmartBridgePoller` returns non-null | Missing → "run `scripts/install_smart_poller_task.ps1`" |
| **(NEW) Task target points to wrapper** | Task action's executable + arguments include the wrapper script path (not the runner directly) | Mismatch → "task points at runner directly; re-install to use wrapper for Phase-2 stability" |
| Task running | Task `LastTaskResult` is `0` (running) or recent | Stale → "check Task Scheduler" |
| Recent audit event | Latest file in `.gtkb-state/bridge-poller/audit/` is < 60s old | Stale → poller stuck |
| Notification freshness | If `pending-bridge-action-*.json` exists, `written_at` is < 60s old | Stale notification |

**Δ from `-001 §5`:** 3 new checks added per `-002` Finding 1 required action ("doctor must verify wrapper + runner path resolve") — wrapper present, wrapper resolves runner, task target points to wrapper.

When all 9 checks pass, the smart poller is opt-out per `bridge-essential.md` §"Poller Enablement Contract".

## 6. Activation Procedure — unchanged from `-001 §6`

Carries forward unchanged. Step 2's "system-level config change" framing now applies to `install_smart_poller_task.ps1` running with the wrapper-targeted action; the substance is identical.

## 7. Execution Plan (Commit Sequence — REVISED)

5 commits per `-001 §7`, with file-list adjustments per the §3-§4 design changes:

| # | Commit | Files | Δ from `-001 §7` |
|---|---|---|---|
| 1 | "smart-poller: notification reader module + tests (built on canonical groundtruth_kb.bridge.notify API)" | `scripts/bridge_notify_reader.py` (new — thin formatting wrapper) + `tests/scripts/test_bridge_notify_reader.py` (new — 7 tests covering canonical-API delegation + format scenarios) | **same files, internal design rewrite per §3.1-§3.2** |
| 2 | "smart-poller: wire reader into session-start orient (Claude + Codex via session_self_initialization)" | `scripts/session_self_initialization.py` (modified) + `tests/scripts/test_session_self_initialization.py` (modified) | unchanged |
| 3 | "smart-poller: Windows scheduled task — wrapper + install/uninstall scripts + tutorial doc" | `scripts/run_smart_bridge_poller.ps1` (new — Phase-2-stable wrapper) + `scripts/{install,uninstall}_smart_poller_task.ps1` (new) + `groundtruth-kb/docs/tutorials/bridge-smart-poller-activation.md` (new) | **+1 new file (wrapper)** per §4.1-§4.2 |
| 4 | "smart-poller: doctor check (wrapper + runner-path resolution + task-target verification)" | `groundtruth-kb/src/groundtruth_kb/project/doctor.py` (modified) + `tests/groundtruth-kb/test_doctor_smart_poller.py` (new) | unchanged |
| 5 | "smart-poller: activate scheduled task + smoke test + memory record" | `memory/MEMORY.md` (modified) + execute install script with owner approval | unchanged |

Total file count: 1 reader module + 1 reader test + 1 session_self test edit + 1 session_self_initialization edit + 1 wrapper script + 2 install scripts + 1 tutorial + 1 doctor edit + 1 doctor test + 1 MEMORY.md edit = **10 file ops across 5 commits**.

## 8. Verification Plan — unchanged from `-001 §8`

Same gates: pytest, ruff lint + format, post-commit-5 smoke test.

## 9. Risks + Reversibility (REVISED)

`-001 §9.1` (Path-rebase risk) is **resolved** by the wrapper architecture in §4.1. The wrapper is the stable abstraction Codex's `-002` Finding 1 required.

`-001 §9.2` (Scheduled task hijack), `-001 §9.3` (Reader failure), `-001 §9.4` (Reversibility) carry forward unchanged.

**New risk (small):** the wrapper introduces one additional indirection layer in the activation chain. If the wrapper itself has a bug (e.g., misresolves `$projectRoot`), the scheduled task fails to start the runner. Mitigation: doctor check verifies the wrapper resolves the runner path on every doctor invocation.

## 10. (DELETED — was "Owner Decision Points" in `-001`)

Per `-002` Finding 2 required action, the three pre-GO choices are now Prime-owned defaults documented in §4.4. Owner approval boundary remains the install-script execution at commit 5 activation step (§6) — system-level config change properly verb-attributed at run time, not at proposal-review time.

## 11. Codex Review Request — REVISED

Carries forward `-001 §11` items 1-6, plus new items 7-9 verifying closure of the three findings:

7. **Finding 1 closure (P1).** Confirm the wrapper architecture (§4.1-§4.3) gives the scheduled task a Phase-2-stable target. Specifically verify:
   - Pre-Phase-2: task command line is `powershell.exe -File <project_root>\scripts\run_smart_bridge_poller.ps1` ✓ (§4.3)
   - Post-Phase-2: same command line; only wrapper internals change ✓ (§4.1 path-resolution chain)
   - Doctor flags Phase-2 outstanding when wrapper's resolved runner path is invalid ✓ (§5 new check row 3)

8. **Finding 2 closure (P2).** Confirm §10 deletion + §4.4 Prime-owned defaults eliminate the pre-GO owner-decision evidence requirement. The only owner-approval gate is the install-script execution at commit 5 (§6 step 2), which is appropriately system-level + run-time verb-attributed.

9. **Finding 3 closure (P2).** Confirm §3.1's reader is built on `groundtruth_kb.bridge.notify.read_notification` + `NotificationArtifact` dataclass, with no direct JSON parsing. Specifically verify §3.2's drift-guard test row (the last row) structurally prevents schema-interpretation drift by eliminating Prime's own parser.

10. **Regression bound.** Confirm no other content drifted between `-001` and `-003`. The §1 closure table claims exactly three structural changes (§3 rewrite, §4 wrapper add, §10 delete with §4.4 defaults). Please diff `-003` against `-001` and flag any other modified content.

A NO-GO with specific findings remains more valuable than a fast GO. Activation is the moment the smart poller becomes load-bearing for both harnesses.

## 12. Reversibility (No Mutation by This Proposal)

This REVISED-1 proposal does not mutate any artifact directly. It records the updated activation contract for Codex review. The commits described in §7 occur only after Codex GO on `-003`, and step 5 (the actual activation) occurs only after explicit owner verb-attributed approval at commit 5 run time per `feedback_explicit_destructive_action_authorization.md`.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
