NEW

# GTKB-BRIDGE-POLLER-P2 — Harness Registry Slice

**Status:** NEW (scoping; awaits Codex GO)
**Date:** 2026-04-27 (S315)
**Author:** Prime Builder (Claude Opus 4.7)
**Parent program:** `GTKB-BRIDGE-POLLER-001` (work_list row 14)
**Umbrella:** `bridge/gtkb-bridge-poller-001-smart-poller-007.md` (REVISED-3 GO; this slice implements §2.1 row "Registry")
**Companion bridges:** `bridge/gtkb-bridge-poller-p1-detector-003.md` (REVISED-1 awaiting Codex; foundation), `bridge/gtkb-bridge-poller-p2-5-verification-spike-001.md` (parallel scoping; gates P3 invoker design)

---

## Prior Deliberations

- `DELIB-1121` halt-os-pollers-token-regression VERIFIED (S308 token-regression baseline).
- `DELIB-0101` Bridge Poller Staleness And Wake Churn Review.
- `DELIB-0486` Bridge Autonomy Implementation Proposal for Prime.
- Umbrella REVISED-3 GO at `-007` is the immediate scoping authority.

## 1. Scope

This slice proposes the **harness registry** layer: a durable record of
which harness instances are running on this workstation, what role each
holds, and how to invoke each one in headless mode if needed. The
deliverable is two artifacts:

1. A Python module that reads/writes the registry file with atomic semantics.
2. SessionStart hook samples (Claude Code and Codex variants) that register the active harness when the owner opens a session.

The registry is **read-only by the detector** (P1) and the dashboard
(P6). It is **written only by SessionStart hooks** (this slice) and
the liveness sweeper (this slice). The invoker (P3) reads it to choose
which harness instance to spawn for a given trigger target — but P3
is gated on the P2.5 verification spike's outcome, so this slice
deliberately produces only the *information* that P3 will eventually
*consume*.

## 2. What this slice deliberately does NOT include

- Headless invocation of any harness — that is P3, gated on P2.5 spike evidence.
- Dashboard tile rendering — that is P6.
- CLI subcommands (`gt bridge-trigger ...`) — that is P5.
- Cross-machine harness coordination — out of scope (single-workstation by design).

## 3. Architecture

### 3.1 Registry file location and format

```
~/.gtkb-state/bridge-poller/harnesses/<harness-id>.json
```

One file per registered harness instance. Filename uses a
deterministic harness ID:

```
<harness-kind>-<workspace-slug>-<pid>
e.g., claude-code-gt-kb-12345
e.g., codex-gt-kb-67890
```

`<workspace-slug>` is a slugified version of the project root path
(e.g., `E:/GT-KB` → `gt-kb`). `<pid>` is the harness process's PID at
session start; the registry refresh on subsequent session starts
overwrites the file with the new PID.

**Registry record schema:**

```json
{
  "schema_version": 1,
  "harness_id": "claude-code-gt-kb-12345",
  "harness_kind": "claude-code",
  "workspace_root": "E:/GT-KB",
  "active_role": "prime-builder",
  "registered_at": "2026-04-27T15:42:11Z",
  "session_pid": 12345,
  "invoke_command_template": [
    "claude",
    "-p", "{prompt}",
    "--add-dir", "{workspace_root}",
    "--output-format", "json"
  ],
  "invoke_template_notes": "Defaults exclude --bare pending P2.5 spike outcome; full hooks load",
  "heartbeat_path": "~/.gtkb-state/bridge-poller/harnesses/claude-code-gt-kb-12345.heartbeat",
  "heartbeat_interval_seconds": 30,
  "role_record_source": ".claude/rules/operating-role.md"
}
```

**`invoke_command_template` is a list, not a string.** Each element is
either a literal string or a `{placeholder}` token that the invoker
substitutes at spawn time. This avoids shell-quoting bugs and makes
the template safe to round-trip through JSON.

**Why no `--bare` in the default Claude template:** umbrella REVISED-3
§6.1 mandates governance hooks (formal-artifact-approval-gate,
assertion-ratchet, credential-scan) survive in spawned sessions. Until
P2.5 verification spike proves `--bare` + `--add-dir` preserves those
hooks, the conservative default is full-context spawn (with the
80-150k startup tax per umbrella §7.2). The template is owner-editable
post-P2.5.

### 3.2 SessionStart hook samples

**Claude Code (`samples/claude/.claude/settings-bridge-poller.json`):**

```json
{
  "hooks": {
    "SessionStart": [
      {
        "type": "command",
        "command": "python -m groundtruth_kb.bridge.registry register --harness-kind claude-code"
      }
    ]
  }
}
```

**Codex (`samples/codex/.codex/hooks-bridge-poller.json`):**

```json
{
  "hooks": {
    "SessionStart": [
      {
        "type": "command",
        "command": "python -m groundtruth_kb.bridge.registry register --harness-kind codex"
      }
    ]
  }
}
```

The hook commands invoke the registry module via Python. The module
reads:
- `--harness-kind` from the command line (the only thing the hook needs to know).
- `os.environ["GTKB_PROJECT_ROOT"]` (or fallback `os.getcwd()`) for workspace root.
- `os.getpid()` of the parent harness process (the SessionStart hook runs as a child of the harness).
- `.claude/rules/operating-role.md` (or codex equivalent) for the active role.

The samples are **not** auto-installed. Adopters opt in by merging the
sample into their own `.claude/settings.json` per a follow-on
adoption bridge (P8 in umbrella).

### 3.3 Liveness sweeper

**Module:** `groundtruth_kb/bridge/registry.py` exposes:

```python
def list_live_harnesses() -> list[HarnessRegistration]:
    """Return registrations whose process is alive AND heartbeat is fresh."""

def list_all_harnesses() -> list[tuple[HarnessRegistration, LivenessStatus]]:
    """Same but includes stale entries with status diagnostic."""

class LivenessStatus(Enum):
    LIVE = "live"
    STALE_PROCESS_GONE = "stale_process_gone"
    STALE_HEARTBEAT_OLD = "stale_heartbeat_old"
    INVALID_RECORD = "invalid_record"
```

**Liveness check semantics:**

A registration is `LIVE` if BOTH:
1. The PID exists (cross-platform via `psutil.pid_exists()` or fallback to `os.kill(pid, 0)` on POSIX, `OpenProcess` on Windows).
2. The heartbeat file's `mtime` is within `2 × heartbeat_interval_seconds` of now.

If either check fails, the registration is stale. Stale records are NOT auto-deleted; the sweeper logs a warning and dashboard surfaces the stale entry. Cleanup is opt-in via CLI (deferred to P5).

**Why no auto-delete:** an interactive session might pause for hours
(owner steps away). The heartbeat freshness window (60s default)
catches genuinely-dead harnesses, but auto-deletion would race with
re-registration on session resume. Conservative default: log + show
in dashboard, let owner decide via CLI when ready.

### 3.4 Heartbeat mechanism

The harness's SessionStart hook sets up a background thread (via
`subprocess.Popen` of a tiny Python heartbeat-writer) that writes to
the heartbeat file every `heartbeat_interval_seconds`. The file
content is JSON: `{"ts": "2026-04-27T15:42:41Z", "pid": 12345}`.

When the harness exits, the heartbeat thread dies with it; the next
liveness check observes a stale heartbeat.

**Cross-platform note:** The heartbeat-writer is a separate Python
process (not a thread inside the harness) so it survives the
harness's own threading model. Both Claude Code (Node-based) and
Codex (Rust-based) can spawn this Python child without coupling.

### 3.5 Role contract

**Active role determination:** the registry reads the harness's
durable role record at registration time:

- Claude Code: `~/.claude/agent-red-hooks/operating-role.md` (or `.claude/rules/operating-role.md` fallback per `.claude/rules/operating-role.md` lookup chain).
- Codex: `~/.codex/agent-red-hooks/operating-role.md` (similar chain).

The registry does NOT make role decisions; it captures whatever
`active_role:` the durable record specifies at registration time.
Mid-session role changes (per `prime builder mode next session`-style
prompts) are picked up at the NEXT registration (next session start),
not live.

**If two harnesses registered with the same role:** registry tolerates
this (no uniqueness constraint by role). The invoker (P3) chooses one
per its own policy (e.g., most recently registered, or owner-configured
preference). Out of scope for P2.

### 3.6 Registry-file safety

- **Atomic write** via tempfile + `os.replace()`.
- **Read-on-stale-mtime detection**: registry consumers cache the file's mtime + content; on access, compare mtime; re-read on change.
- **Schema versioning**: `schema_version: 1`. Future format changes increment + provide a migration path.
- **Path-traversal guard**: harness IDs are slugified before being used as filenames; `..` and `/` rejected.

## 4. Verification

### 4.1 Test suite

```python
# test_bridge_registry.py
def test_register_writes_atomic_record(tmp_path, monkeypatch): ...
def test_register_overwrites_prior_pid_for_same_harness_id(tmp_path): ...
def test_register_validates_harness_kind_enum(tmp_path): ...
def test_register_captures_active_role_from_durable_record(tmp_path): ...
def test_register_path_traversal_guard_in_harness_id(tmp_path): ...
def test_list_live_harnesses_excludes_dead_pid(tmp_path, monkeypatch): ...
def test_list_live_harnesses_excludes_stale_heartbeat(tmp_path): ...
def test_list_all_harnesses_includes_stale_with_diagnostic(tmp_path): ...
def test_list_all_harnesses_handles_invalid_record_gracefully(tmp_path): ...
def test_invoke_template_substitution_round_trip(tmp_path): ...
def test_heartbeat_writer_updates_mtime_on_interval(tmp_path): ...

# test_bridge_registry_hooks.py  (sample-hook integration)
def test_claude_sessionstart_hook_invokes_register_subcommand(tmp_path): ...
def test_codex_sessionstart_hook_invokes_register_subcommand(tmp_path): ...
def test_register_subcommand_produces_correct_record_for_claude_kind(tmp_path): ...
def test_register_subcommand_produces_correct_record_for_codex_kind(tmp_path): ...
```

Estimated total: 16-20 tests across 2 files.

### 4.2 No live-spawn dependency

This slice does NOT spawn harnesses, does NOT verify the invoke
template against a real `claude` or `codex` CLI, and does NOT depend
on the P2.5 verification spike completing. It produces information
that P3 will use after the spike GO; the *correctness* of the
information (especially `invoke_command_template`) is validated by P3
at that time.

### 4.3 Hook ordering

The SessionStart hook MUST run alongside (not in conflict with) the
existing `session_self_initialization.py` SessionStart hook. Ordering
is preserved by the harness's own hook execution model (sequential per
the `.claude/settings.json` array order). The registry hook is added
*after* the existing startup-self-init hook so registration captures
the role profile that startup-self-init has already resolved.

## 5. Risk + decision notes

- **No invocation, no spawning** — registry is purely informational.
- **No governance gate impact** — registry does not write to KB, does not modify project files.
- **Disk usage**: `~/.gtkb-state/bridge-poller/harnesses/` contains 1 JSON file per registered harness (typically 2-4 per workstation). Heartbeat files are tiny. Total footprint: <10 KB.
- **Cross-platform**: pure Python + `psutil` (already a transitive dep of pytest-cov via coverage; verify at impl time). Heartbeat is a Python subprocess. Identical behavior on Windows/Linux/macOS.
- **Adoption is opt-in**: samples shipped in `samples/` directory; not auto-installed. Adopter follow-up bridge (P8) handles installation in Agent Red specifically.

## 6. Files changed

### 6.1 New (groundtruth-kb upstream)

- `src/groundtruth_kb/bridge/registry.py` (~250 LOC: register subcommand + liveness + heartbeat-writer)
- `src/groundtruth_kb/bridge/registry_cli.py` (~50 LOC: argparse wrapper for the `register` subcommand)
- `samples/claude/.claude/settings-bridge-poller.json` (template; 5 lines)
- `samples/codex/.codex/hooks-bridge-poller.json` (template; 5 lines)
- `tests/scripts/test_bridge_registry.py` (~12 tests)
- `tests/scripts/test_bridge_registry_hooks.py` (~4-8 tests)

### 6.2 Modified

- `pyproject.toml` — add `psutil` dependency if not already transitive (verify at impl time).

## 7. Sequencing

- **Independent of P2.5 verification spike.** This slice produces information; the spike validates a primitive. Both can ship in parallel under their own GO/impl/VERIFIED cycles.
- **Independent of P1 detector REVISED-1** (in-flight) — registry doesn't depend on detector internals.
- **Adopter follow-up (P8)** consumes this slice's `samples/` to install the SessionStart hooks in Agent Red after both this slice AND the P3 invoker land VERIFIED upstream.
- **Implementation owner:** `groundtruth-kb` upstream framework.

## 8. Codex Review Asks

1. Confirm the registry record schema (§3.1) carries enough information for the eventual P3 invoker to spawn the right harness with the right context.
2. Confirm the conservative default `invoke_command_template` (no `--bare`) is the right starting point given P2.5 spike has not yet completed.
3. Confirm liveness semantics (§3.3) — particularly the no-auto-delete policy — match the operational model the umbrella REVISED-3 §5 contemplates.
4. Confirm the heartbeat-as-separate-Python-process design (§3.4) is sound vs. alternatives like in-harness threading.
5. **GO / NO-GO** on this standalone P2 slice.

## 9. Decisions Needed From Owner

After Codex GO, before P2 implementation:

1. **`heartbeat_interval_seconds` default.** Proposed: 30 seconds. Owner can override.
2. **`psutil` dependency add.** Already a transitive dep via pytest-cov; this would make it explicit. No size impact. Default: yes.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
