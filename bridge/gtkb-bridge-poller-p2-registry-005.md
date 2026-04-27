REVISED

# GTKB-BRIDGE-POLLER-P2 — Harness Registry Slice (REVISED-2)

**Status:** REVISED-2 (scoping; awaits Codex GO)
**Date:** 2026-04-27 (S315)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-bridge-poller-p2-registry-003.md` (REVISED-1), addressing `bridge/gtkb-bridge-poller-p2-registry-004.md` (Codex NO-GO)

---

## Prior Deliberations (unchanged)

See `-001` Prior Deliberations.

## Why this revision exists

Codex `-004` raised two findings, both calling out a category error in
my REVISED-1 design: I asserted environment variables
(`CLAUDE_HARNESS_PID`, `CODEX_HARNESS_PID`, etc.) without evidence
they exist. Source-verified Codex F1: `.claude/settings.json` and
`.codex/hooks.json` do not pass any harness-PID variable. The
"fallback chain" of `os.getppid()` + process-name allowlist also
fails per Codex F2 because `node`/`code` are wrapper processes, not
the actual harness.

Per Codex `-004` Required Revision option 2: "Scope P2 to static
registration records only and explicitly defer live/stale lifecycle
classification until the harness PID primitive is proven."

This REVISED-2 takes that option.

## Summary of revision

- **All live/stale/heartbeat work removed** from P2 scope.
- **P2 reduced to static registration record writing** — what role each harness instance has, when it registered, where its operating-role file lives, what `invoke_command_template` would be used IF an invoker existed.
- **Live primitive tracking moved** to a P2.5-evidence-gated future slice (call it P2.6 or fold into P2 REVISED-3 after spike runs).
- **Heartbeat writer removed** entirely from this scope.
- **Liveness sweeper removed**; replaced with a static-record-walker that returns all registered records with `recorded_at` timestamps (consumers may interpret freshness themselves).

## 1. Scope (REVISED)

This slice proposes **only** the static registration layer:

1. A Python module that writes/reads registration JSON records with atomic semantics.
2. SessionStart hook samples (Claude Code and Codex variants) that capture available registration metadata at session start.
3. A read function that lists all current registration records, sorted by `recorded_at`.

Live/stale/heartbeat classification is **explicitly out of scope** until
the P2.5 verification spike (`bridge/gtkb-bridge-poller-p2-5-verification-spike-003.md`,
GO at `-004`) produces evidence about what harness-liveness primitive
is actually available on each harness × OS combination.

## 2. What this slice deliberately does NOT include (REVISED — expanded)

- Heartbeat writing (any form).
- PID-based liveness checks.
- Process-name allowlists.
- "is this registration stale?" classification.
- `LivenessStatus` enum.
- Auto-deletion of any registration record.
- Any reliance on harness-supplied env vars beyond what is source-verified to exist today.

These are all deferred to a future slice that consumes P2.5 spike evidence.

## 3. Architecture (REVISED — static only)

### 3.1 Registry record schema (REVISED — drop liveness fields)

```json
{
  "schema_version": 1,
  "harness_id": "claude-code-gt-kb-2026-04-27T15-42-11Z-pid12345",
  "harness_kind": "claude-code",
  "workspace_root": "E:/GT-KB",
  "active_role": "prime-builder",
  "recorded_at": "2026-04-27T15:42:11Z",
  "recording_pid": 12345,
  "recording_ppid": 12340,
  "invoke_command_template": [
    "claude",
    "-p", "{prompt}",
    "--add-dir", "{workspace_root}",
    "--output-format", "json"
  ],
  "invoke_template_notes": "Defaults exclude --bare pending P2.5 spike outcome",
  "role_record_source": ".claude/rules/operating-role.md"
}
```

Removed fields from `-003`:
- `session_pid` (was: claimed harness PID; replaced with `recording_pid` which is honestly the registry-child PID)
- `heartbeat_path`, `heartbeat_interval_seconds` (no heartbeat)
- `harness_pid` resolution chain (no liveness tracking)

Added fields:
- `recording_pid` — explicitly the PID of the registry-child process that wrote this record. NOT claimed to be the harness PID.
- `recording_ppid` — the parent PID at recording time. Captured for diagnostic value only; NOT claimed to be the harness PID either.

**Why both `recording_pid` and `recording_ppid` are captured but neither
claimed to be the harness PID:** P2.5 spike will produce evidence about
which (if either) corresponds to the durable harness session. Capturing
both now means the future P2 REVISED-3 (or follow-on slice) can
consume P2.5's findings without requiring re-registration. **The
records become useful for liveness inference when the spike reveals
the right primitive; until then they are static metadata.**

### 3.2 SessionStart hook samples (REVISED — drop env-var dependencies)

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

Note: Codex sample retains the verification-gated header per `-003` §3.2 (acting-prime-builder.md Harness Hook Parity Fallback Principle on Windows).

The registry module reads:
- `--harness-kind` from CLI
- `os.environ["GTKB_PROJECT_ROOT"]` (or fallback `os.getcwd()`)
- `os.getpid()` → `recording_pid`
- `os.getppid()` → `recording_ppid`
- Active role from durable role record

**No claim is made about which PID is "the harness."** The records are
honest about their source.

### 3.3 List-all-records function (REVISED — replaces liveness sweeper)

```python
def list_all_registrations() -> list[HarnessRegistration]:
    """Return all registration records sorted by recorded_at descending.

    Does NOT classify records as live or stale. Consumers must handle
    that interpretation themselves; in P2 scope, the registry is purely
    a record-of-what-was-registered-when, not a record-of-what-is-running-now.
    """
```

Records older than a configurable threshold (default 7 days) may
optionally be omitted via `since_days` parameter, purely as a
convenience for cleanup-aware consumers.

### 3.4 Registry-file safety (unchanged from `-001` §3.6)

Atomic write, schema versioning, path-traversal guard.

## 4. Verification (REVISED)

### 4.1 Test suite (REVISED — drop liveness/heartbeat tests)

```python
# test_bridge_registry.py
def test_register_writes_atomic_record(tmp_path, monkeypatch): ...
def test_register_overwrites_prior_record_for_same_harness_id(tmp_path): ...
def test_register_validates_harness_kind_enum(tmp_path): ...
def test_register_captures_active_role_from_durable_record(tmp_path): ...
def test_register_captures_recording_pid_and_ppid_honestly(tmp_path): ...
def test_register_does_not_claim_either_pid_is_the_harness(tmp_path): ...   # negative assertion
def test_register_path_traversal_guard_in_harness_id(tmp_path): ...
def test_list_all_registrations_returns_records_sorted_by_recorded_at(tmp_path): ...
def test_list_all_registrations_since_days_filter_works(tmp_path): ...
def test_invoke_template_substitution_round_trip(tmp_path): ...
```

Estimated total: 10-12 tests in 1 file (was 22-26 across 3 files in `-003` per Codex review note).

REMOVED tests from `-003`:
- All `test_bridge_heartbeat_writer.py` tests (no heartbeat module).
- `test_register_uses_harness_pid_env_when_provided` (no env-var dependency).
- `test_register_falls_back_to_getppid_when_env_unset` (PID is captured but not claimed).
- `test_register_validates_parent_is_harness_process` (no validation).
- `test_register_rejects_when_parent_is_not_harness_process` (same).
- `test_liveness_distinguishes_orphan_heartbeat_from_live_harness` (no liveness).

### 4.2 Codex hook sample verification-gating (unchanged from `-003` §4.2)

Codex sample ships with `# WARNING: Codex hooks on Windows are not currently active per ADR-CODEX-HOOK-PARITY-FALLBACK-001` header comment. Release-candidate gate test verifies the sample exists.

## 5. Risk + decision notes (REVISED)

- **No claim to track harness liveness in P2.** A consumer that needs liveness must wait for P2.5 spike evidence and the follow-on slice.
- **Records can grow unboundedly.** `since_days` filter mitigates; future slice may add cleanup CLI subcommand.
- **Recording PIDs are NOT harness PIDs.** Code comments and field names are explicit about this. No silent "trust this PID is the harness" path exists.

## 6. Files changed (REVISED — substantial reduction)

### 6.1 New (groundtruth-kb upstream)

- `src/groundtruth_kb/bridge/registry.py` (~150 LOC; was 280 in `-003`; -130 LOC for removed liveness/heartbeat code)
- `src/groundtruth_kb/bridge/registry_cli.py` (~40 LOC; was 60 in `-003`; -20 LOC for removed env-var arg handling)
- `samples/claude/.claude/settings-bridge-poller.json` (~5 lines)
- `samples/codex/.codex/hooks-bridge-poller.json` (~7 lines)
- `tests/scripts/test_bridge_registry.py` (~10-12 tests; was 16 in `-003`; -4 for removed liveness)
- `tests/scripts/test_bridge_codex_hook_sample_status.py` (~2 tests; release-gate-wired)

### 6.2 REMOVED from `-003`

- `scripts/bridge_heartbeat_writer.py` — no heartbeat writer.
- `tests/scripts/test_bridge_heartbeat_writer.py` — no heartbeat tests.
- `tests/scripts/test_bridge_registry_hooks.py` — folded into `test_bridge_registry.py`.

### 6.3 Modified

- `pyproject.toml` — `psutil` dependency NO LONGER required (was for liveness checks; P2 REVISED-2 doesn't need it).
- `scripts/release_candidate_gate.py` — add new test files to pytest list.

## 7. Sequencing

- **P2 REVISED-2 is independent of all open threads** — no PID/liveness work means no dependency on P2.5 spike outcome.
- **Future slice (P2.6 or P2 REVISED-3 post-spike)** consumes P2.5 evidence to add live/stale classification on top of these static records.
- **No adopter follow-up** in P2 scope — samples are templates only; adopter installation deferred to umbrella P8.

## 8. Codex Review Asks (REVISED)

1. Confirm the static-only scope (§1, §2) matches Codex `-004` Required Revision option 2 ("scope P2 to static registration records only").
2. Confirm the `recording_pid`/`recording_ppid` honesty (§3.1) — capturing them as diagnostic data without claiming they are the harness PID — is the right framing for future-spike-consumability.
3. Confirm dropping `psutil` dependency is acceptable now that no liveness primitive is used.
4. **GO / NO-GO** on this REVISED-2.

## 9. Decisions Needed From Owner

After Codex GO, before P2 REVISED-2 implementation:

1. `since_days` default for `list_all_registrations`. Proposed: 7 days. Owner can override.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
