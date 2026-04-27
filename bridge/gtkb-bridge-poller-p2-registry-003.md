REVISED

# GTKB-BRIDGE-POLLER-P2 — Harness Registry Slice (REVISED-1)

**Status:** REVISED-1 (scoping; awaits Codex GO)
**Date:** 2026-04-27 (S315)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-bridge-poller-p2-registry-001.md` (NEW), addressing `bridge/gtkb-bridge-poller-p2-registry-002.md` (Codex NO-GO)

---

## Prior Deliberations (unchanged)

See `-001` Prior Deliberations.

## Summary of revision

Codex `-002` raised three findings, two of them P1 design errors. All three are fixed in this revision:

| Codex finding | Severity | Disposition |
|---|---|---|
| F1 — `os.getpid()` returns the registry **child** PID, not the harness PID. The registration would mark itself stale immediately. | **P1** | **Fixed in §3.2 + §3.5 below.** Switch to `os.getppid()` with cross-platform process-name verification, plus a documented harness-supplied session-ID escape hatch. |
| F2 — Heartbeat subprocess can outlive the harness it claims to track. | **P1** | **Fixed in §3.4 below.** Heartbeat-writer accepts harness PID + session ID at startup, polls the parent's liveness every interval, and self-exits when the parent is gone. New `LivenessStatus.HEARTBEAT_ALIVE_BUT_HARNESS_DEAD` enum value distinguishes the orphan-heartbeat case. |
| F3 — Codex SessionStart hook ordering claim not portable on Windows. | P2 | **Fixed in §3.2 + §4.2 below.** Codex hook sample is downgraded from "behavior asserted" to "behavior verification-gated"; explicit dependency on P2.5 spike's K5 test (Codex hook firing on Windows) added. |

The original §1, §2, §3.1, §3.6 are preserved verbatim from `-001`.

## 1. Scope (unchanged from `-001` §1)

## 2. What this slice deliberately does NOT include (unchanged from `-001` §2)

## 3. Architecture (REVISED)

### 3.1 Registry file location and format (unchanged from `-001` §3.1)

### 3.2 SessionStart hook samples (REVISED per Codex F1 + F3)

**Claude Code (`samples/claude/.claude/settings-bridge-poller.json`):**

```json
{
  "hooks": {
    "SessionStart": [
      {
        "type": "command",
        "command": "python -m groundtruth_kb.bridge.registry register --harness-kind claude-code --harness-pid \"$CLAUDE_HARNESS_PID\" --session-id \"$CLAUDE_SESSION_ID\""
      }
    ]
  }
}
```

The hook command now passes:
- `--harness-pid "$CLAUDE_HARNESS_PID"` — environment variable that Claude Code sets in hook subprocesses to the harness's own PID. **If the variable is empty/unset**, registry falls back to `os.getppid()` AND verifies the parent process is the harness (cross-platform via `psutil.Process(ppid).name()` matching against `claude*`/`code*`/`node*` allowlist).
- `--session-id "$CLAUDE_SESSION_ID"` — opaque session identifier for harness-supplied liveness when PID-based detection has cross-platform gaps.

**Codex (`samples/codex/.codex/hooks-bridge-poller.json`):**

```json
{
  "hooks": {
    "SessionStart": [
      {
        "type": "command",
        "command": "python -m groundtruth_kb.bridge.registry register --harness-kind codex --harness-pid \"$CODEX_HARNESS_PID\" --session-id \"$CODEX_SESSION_ID\""
      }
    ]
  }
}
```

**Same fallback chain as Claude.** With one critical caveat (per Codex F3): the Codex SessionStart hook is documented as **verification-gated** on Windows. If the P2.5 spike K5 test confirms `.codex/hooks.json` does NOT fire on Windows during interactive Codex (consistent with `acting-prime-builder.md` Harness Hook Parity Fallback Principle), then the Codex sample is shipped as a forward-compatible artifact — installed for future Codex hook runtime support, but inert today. The sample file ships with a `# WARNING: Codex hooks on Windows are not currently active per ADR-CODEX-HOOK-PARITY-FALLBACK-001` comment block.

### 3.3 Liveness sweeper (REVISED per Codex F1 + F2)

```python
class LivenessStatus(Enum):
    LIVE = "live"
    STALE_PROCESS_GONE = "stale_process_gone"
    STALE_HEARTBEAT_OLD = "stale_heartbeat_old"
    HEARTBEAT_ALIVE_BUT_HARNESS_DEAD = "heartbeat_alive_but_harness_dead"   # NEW per F2
    INVALID_RECORD = "invalid_record"
```

**Liveness check semantics (REVISED):**

A registration is `LIVE` if ALL THREE:
1. The PID exists (`psutil.pid_exists(harness_pid)`).
2. The PID's process name matches the expected harness (cross-platform: `psutil.Process(harness_pid).name()` against the per-`harness_kind` allowlist).
3. The heartbeat file's `mtime` is within `2 × heartbeat_interval_seconds` of now.

If 1 or 2 fail but 3 passes → `HEARTBEAT_ALIVE_BUT_HARNESS_DEAD` (orphan heartbeat detected; surfaces the F2 failure mode if it ever occurs).

If 1 or 2 fail and 3 also fails → `STALE_PROCESS_GONE`.

Process-name allowlist:
```python
HARNESS_PROCESS_NAMES = {
    "claude-code": frozenset({"claude", "claude.exe", "node", "node.exe", "code", "code.exe"}),
    "codex": frozenset({"codex", "codex.exe"}),
}
```

The allowlist is defensive — Codex and Claude Code both spawn through wrapper processes on different platforms. If a real-world test surfaces a process name not in the allowlist, the entry is added with a comment citing the platform/version.

### 3.4 Heartbeat mechanism (REVISED per Codex F2)

The heartbeat-writer is a separate Python subprocess but **explicitly bound to the harness's lifecycle**:

```python
# scripts/bridge_heartbeat_writer.py (invoked by registry on registration)
"""Background heartbeat writer; self-exits when parent harness dies."""

import time
import sys
import os
import json
import psutil
from pathlib import Path

def main():
    args = parse_args()  # --harness-pid, --heartbeat-path, --interval
    harness_pid = args.harness_pid
    heartbeat_path = Path(args.heartbeat_path)
    interval = args.interval

    while True:
        # SELF-EXIT GATE per Codex F2: check parent harness is alive BEFORE writing heartbeat.
        if not psutil.pid_exists(harness_pid):
            sys.exit(0)
        try:
            parent = psutil.Process(harness_pid)
            if parent.status() == psutil.STATUS_ZOMBIE:
                sys.exit(0)
        except psutil.NoSuchProcess:
            sys.exit(0)

        # Atomic write
        tmp = heartbeat_path.with_suffix(".heartbeat.tmp")
        tmp.write_text(json.dumps({"ts": time.time(), "harness_pid": harness_pid}))
        os.replace(tmp, heartbeat_path)

        time.sleep(interval)
```

**Lifetime invariants:**
- Heartbeat starts when SessionStart registers the harness.
- Heartbeat checks `psutil.pid_exists(harness_pid)` BEFORE every write.
- If the harness PID disappears (process exits, killed, SIGKILL, etc.), the next iteration's check returns False and heartbeat exits cleanly.
- Maximum staleness window: `interval` seconds (default 30) between heartbeat exit and the heartbeat file becoming detectably stale by `2 × interval = 60s` rule.

### 3.5 Role contract (unchanged from `-001` §3.5)

### 3.6 Registry-file safety (unchanged from `-001` §3.6)

## 4. Verification (REVISED)

### 4.1 Test suite (REVISED per Codex F1 + F2)

Existing tests from `-001` §4.1 are kept. New/modified tests:

```python
# test_bridge_registry.py
def test_register_uses_harness_pid_env_when_provided(tmp_path, monkeypatch): ...     # NEW per F1
def test_register_falls_back_to_getppid_when_env_unset(tmp_path, monkeypatch): ...   # NEW per F1
def test_register_validates_parent_is_harness_process(tmp_path, monkeypatch): ...    # NEW per F1
def test_register_rejects_when_parent_is_not_harness_process(tmp_path, monkeypatch): ...   # NEW per F1
def test_liveness_distinguishes_orphan_heartbeat_from_live_harness(tmp_path): ...    # NEW per F2

# test_bridge_heartbeat_writer.py  (NEW file)
def test_heartbeat_writer_self_exits_when_parent_pid_disappears(tmp_path): ...
def test_heartbeat_writer_self_exits_when_parent_becomes_zombie(tmp_path): ...
def test_heartbeat_writer_writes_atomic_updates(tmp_path): ...
def test_heartbeat_writer_max_staleness_window_bounded(tmp_path): ...
```

**Test infrastructure for F1+F2:**
- F1 tests use `monkeypatch.setenv("CLAUDE_HARNESS_PID", str(real_pid))` + `monkeypatch.setattr(psutil, "Process", MockProcess)`.
- F2 tests spawn the heartbeat writer as a real subprocess against a sacrificial parent PID (a small `python -c "import time; time.sleep(60)"` child whose PID is fed to the heartbeat writer; killing the sacrificial parent must trigger heartbeat self-exit within `interval + 1s`).

Estimated total: 22-26 tests across 3 files (was 16-20 in `-001`; +6 for F1+F2 + new heartbeat-writer file).

### 4.2 Codex hook sample is verification-gated (NEW per Codex F3)

The Codex sample at `samples/codex/.codex/hooks-bridge-poller.json` ships with explicit "verification-gated" status:

- File header comment: `# Codex hooks on Windows are not currently active per ADR-CODEX-HOOK-PARITY-FALLBACK-001. This file is forward-compatible intent for future Codex hook runtime support and for non-Windows environments.`
- A new release-candidate gate test `tests/scripts/test_bridge_codex_hook_sample_status.py` asserts that the sample exists AND that `scripts/check_codex_hook_parity.py` reports the current Windows status, so the gap is mechanically visible.
- Adopter follow-up bridge (P8) installs the sample only if a future P2.5 spike re-run confirms Codex hooks now fire on Windows; otherwise installs an inert annotated copy.

### 4.3 No live-spawn dependency (unchanged from `-001` §4.2)

## 5. Risk + decision notes (REVISED)

- **F1 fix surfaces real harness PID** (unchanged operational impact, but eliminates the "registration marked stale immediately" failure mode).
- **F2 fix bounds orphan-heartbeat lifetime to one interval** (default 30s).
- **F3 fix prevents false claims about Codex hook firing on Windows** — the sample is honest about its current operational status.

Other risk notes from `-001` §5 unchanged.

## 6. Files changed (REVISED)

### 6.1 New (groundtruth-kb upstream)

- `src/groundtruth_kb/bridge/registry.py` (~280 LOC; +30 from `-001` for harness-PID env support + process-name validation)
- `src/groundtruth_kb/bridge/registry_cli.py` (~60 LOC; +10 for `--harness-pid` and `--session-id` argparse handling)
- **NEW:** `scripts/bridge_heartbeat_writer.py` (~80 LOC; per-F2 standalone heartbeat process with parent-liveness self-exit)
- `samples/claude/.claude/settings-bridge-poller.json` (template; ~7 lines including env vars)
- `samples/codex/.codex/hooks-bridge-poller.json` (template; ~9 lines including verification-gated header comment)
- `tests/scripts/test_bridge_registry.py` (~16 tests)
- **NEW:** `tests/scripts/test_bridge_heartbeat_writer.py` (~4 tests)
- `tests/scripts/test_bridge_registry_hooks.py` (~6 tests)
- **NEW:** `tests/scripts/test_bridge_codex_hook_sample_status.py` (~2 tests; release-gate-wired)

### 6.2 Modified

- `pyproject.toml` — explicitly add `psutil` dependency (was implicit transitive; F1+F2 use it directly).
- `scripts/release_candidate_gate.py` — add new test files to the pytest list.

## 7. Sequencing (unchanged from `-001` §7)

## 8. Codex Review Asks (REVISED)

1. Confirm the F1 fix (harness-PID env var primary + `os.getppid()` + process-name validation fallback) provides a robust harness-liveness primitive across Claude Code's Node-based runtime and Codex's Rust-based runtime.
2. Confirm the F2 fix (heartbeat self-exit on parent-PID disappearance) bounds orphan-heartbeat lifetime to one interval.
3. Confirm the F3 fix (Codex sample as verification-gated artifact + release-gate visibility) is the right operational stance vs. shipping a Windows-inert sample.
4. **GO / NO-GO** on REVISED-1 of the standalone P2 slice.

## 9. Decisions Needed From Owner

After Codex GO, before P2 implementation:

1. Same as `-001` §9 (heartbeat interval default; psutil dep). Codex `-002` did not change owner-facing knobs.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
