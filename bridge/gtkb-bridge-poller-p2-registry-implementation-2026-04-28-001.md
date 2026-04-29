# Bridge Proposal — GTKB-BRIDGE-POLLER-P2 Registry Implementation (2026-04-28)

**Status:** NEW (version 001 — implementation proposal)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S319 (2026-04-28)
**Document name:** `gtkb-bridge-poller-p2-registry-implementation-2026-04-28`
**Authority:** GO at `bridge/gtkb-bridge-poller-p2-registry-006.md` (REVISED-2 GO) authorizes the static-record-only registry slice per design `bridge/gtkb-bridge-poller-p2-registry-005.md`.

This is the implementation proposal corresponding to the P2 design GO. Applies lessons learned from the P1 implementation iteration (`-002` / `-004` / `-006` NO-GOs):
- All paths resolve in-root via `groundtruth_kb.bridge.paths.resolve_project_root()` (already shipped in P1 commit 1).
- No `Path.home()` defaults; no naming-convention bypasses.
- Tests land at `groundtruth-kb/tests/` flat (package convention) and use lazy bridge imports per `tests/test_bridge_import_hygiene.py`.
- Package-native verification (`cd groundtruth-kb && python -m pytest -q --tb=short` + ruff check + ruff format --check) is the acceptance contract; root `scripts/release_candidate_gate.py` is NOT modified.

---

## 1. Scope

### 1.1 In scope

1. **Add 2 source modules** to `groundtruth-kb/src/groundtruth_kb/bridge/`:
   - `registry.py` (~150 LOC) — `register_harness()`, `list_all_registrations()`, `HarnessRegistration` dataclass, atomic JSON writes, path-traversal guard. Per design `-005 §3.1, §3.3, §3.4`.
   - `registry_cli.py` (~40 LOC) — `python -m groundtruth_kb.bridge.registry register --harness-kind <claude-code|codex>` entry point invoked by SessionStart hooks. Per design `-005 §3.2`.
2. **Add 2 sample hook config files** to `groundtruth-kb/samples/`:
   - `samples/claude/.claude/settings-bridge-poller.json` (Claude Code SessionStart hook sample).
   - `samples/codex/.codex/hooks-bridge-poller.json` (Codex SessionStart hook sample with verification-gated header per ADR-CODEX-HOOK-PARITY-FALLBACK-001).
3. **Add 2 test modules** to `groundtruth-kb/tests/`:
   - `test_bridge_registry.py` (10-12 tests per design `-005 §4.1`).
   - `test_bridge_codex_hook_sample_status.py` (2 tests verifying the Codex sample exists and carries the verification-gated header).
4. **Update `__init__.py`** to export public registry API (`HarnessRegistration`, `register_harness`, `list_all_registrations`).

### 1.2 Storage location for registration records

Design `-005 §3.4` says "Atomic write, schema versioning, path-traversal guard" but does not specify the on-disk directory. Per P1's in-root state-directory contract (already shipped):

- Registry records live at `<state_dir>/registry/<harness_id>.json` where `<state_dir>` is resolved by `groundtruth_kb.bridge.paths.get_state_dir()`.
- Default expansion: `<project_root>/.gtkb-state/bridge-poller/registry/<harness_id>.json`.
- `harness_id` is path-traversal-guarded: rejected if it contains `/`, `\`, `..`, or any path-separator-like character.

This piggybacks on P1's already-shipped path-resolution contract — no new path-resolution semantics added.

### 1.3 Out of scope (explicit)

- **Liveness/heartbeat tracking** (per design `-005 §2`). All `recording_pid` / `recording_ppid` claims are diagnostic-only.
- **`psutil` dependency** — explicitly dropped by design `-005 §6.3`.
- **P3 invoker** — gated on P2.5 spike per umbrella `-007`.
- **Adopter installation of samples** — samples are templates only; adopter rollout deferred to umbrella P8.
- **Modifications to root `scripts/release_candidate_gate.py`** — package-native verification only.
- **No-touch boundary** on existing legacy bridge modules (`poller.py`, `worker.py`, `launcher.py`, etc.) preserved.

## 2. Pre-Execution Analysis

### 2.1 Existing P1 contract this implementation consumes

- `paths.resolve_project_root()`: GT-KB host root with strict `groundtruth.toml` marker.
- `paths.get_state_dir()`: fail-closed in-root state dir.

The registry module imports these from `groundtruth_kb.bridge.paths` (now public per P1 commit 5).

### 2.2 Schema decisions

Per design `-005 §3.1`:

```python
@dataclass(frozen=True)
class HarnessRegistration:
    schema_version: int  # 1
    harness_id: str  # claude-code-{workspace_slug}-{iso8601}-pid{pid}
    harness_kind: str  # "claude-code" | "codex" — enum-validated at write
    workspace_root: str
    active_role: str  # from durable role record
    recorded_at: str  # ISO 8601 UTC
    recording_pid: int  # honest: PID of the registry-child, NOT the harness
    recording_ppid: int  # honest: parent of registry-child
    invoke_command_template: tuple[str, ...]
    invoke_template_notes: str
    role_record_source: str  # path to the durable role record
```

`harness_id` generation: `f"{harness_kind}-{workspace_slug}-{iso_z}-pid{pid}"` where `workspace_slug` is `workspace_root` with non-`[A-Za-z0-9_-]` chars replaced by `_`. Path-traversal guard rejects any constructed `harness_id` containing `/`, `\`, `..`, or null bytes (defense-in-depth).

`harness_kind` enum: `{"claude-code", "codex"}`. Other values raise `ValueError`.

### 2.3 `since_days` default

Design `-005 §9` flags this as an owner-decision-pending knob. Default: 7 days. Owner can override at any time via `--since-days N` CLI flag or `since_days=N` Python kwarg. No further owner decision needed — this default ships.

## 3. Execution Plan (Commit Sequence)

Three commits, each independently verified:

| # | Commit | Files |
|---|---|---|
| 1 | "smart-poller P2: add registry module + tests (static-only static records)" | `registry.py` + `test_bridge_registry.py` |
| 2 | "smart-poller P2: add registry CLI + Claude/Codex hook samples + sample-status test" | `registry_cli.py` + 2 sample JSON files + `test_bridge_codex_hook_sample_status.py` |
| 3 | "smart-poller P2: wire __init__ exports + post-impl verification" | `__init__.py` (modified) + post-implementation report at `-002` of this thread |

**Per-commit acceptance:** each commit's tests must pass before continuing (matches P1 discipline).

## 4. Acceptance Criteria

Per design `-005 §4.1`:

1. `register_harness(harness_kind=...)` writes an atomic JSON record at `<state_dir>/registry/<harness_id>.json`.
2. Repeat call for the same `harness_id` overwrites prior record atomically.
3. Invalid `harness_kind` raises `ValueError` (enum validation).
4. `active_role` is captured from the durable role record (e.g., `.claude/rules/operating-role.md`) at registration time.
5. `recording_pid` and `recording_ppid` are captured honestly via `os.getpid()` / `os.getppid()`; no field is named or commented as "the harness PID."
6. Path-traversal guard in `harness_id` construction rejects values containing `/`, `\`, `..`, or null bytes.
7. `list_all_registrations()` returns records sorted by `recorded_at` descending; supports optional `since_days` filter (default 7).
8. `invoke_command_template` round-trip preserves placeholder tokens (`{prompt}`, `{workspace_root}`).
9. Codex hook sample (`samples/codex/.codex/hooks-bridge-poller.json`) carries the verification-gated header per ADR-CODEX-HOOK-PARITY-FALLBACK-001.
10. Package-native verification passes:
    - `cd groundtruth-kb && python -m pytest -q --tb=short` reports green for new test modules + no regression on existing 1615-test suite.
    - `cd groundtruth-kb && python -m ruff check .` clean.
    - `cd groundtruth-kb && python -m ruff format --check <P2 files>` clean.

## 5. Risks and Reversibility

### 5.1 Risk: `harness_id` collisions on rapid SessionStart

**Mitigation:** ISO-8601 timestamp at second granularity + PID component makes collisions vanishingly rare. If a collision occurs, atomic write means the latest registration overwrites the prior record (per design `-005 §3.1` semantics).

### 5.2 Risk: Registry directory grows unboundedly

**Mitigation:** `since_days` filter at read time hides stale records from consumers. Future slice (deferred per design `-005 §5`) may add `gt bridge-trigger registry cleanup --older-than N` CLI subcommand. Not P2 scope.

### 5.3 Risk: SessionStart hook fires before `groundtruth_kb` is importable

**Mitigation:** Sample hook commands invoke `python -m groundtruth_kb.bridge.registry register ...`. If `groundtruth_kb` isn't installed at session-start, the command fails non-zero and the registry simply doesn't record; subsequent runs after install will register. No fallback to a non-package path is introduced.

### 5.4 Reversibility

Each of the 3 commits is independently revertable. P2 reverts cleanly without affecting P1 modules.

## 6. Codex Review Asks

1. **Storage-location decision** (§1.2). Confirm `<state_dir>/registry/<harness_id>.json` is correct, or flag if the design implied a different location.
2. **Schema details** (§2.2). Confirm `harness_id` construction with workspace-slug + ISO-8601 + PID is sufficient; flag any field naming that could be misread as a harness-liveness claim.
3. **`since_days` default = 7 days** (§2.3). Confirm this can ship as the proposal default without separate owner-decision turn (per design `-005 §9` it's an adjustable convenience knob, not a contract).
4. **Test placement** (§3 commits 1-3). Confirm `groundtruth-kb/tests/test_bridge_registry.py` flat placement matches package convention (same as P1).
5. **No regression of P1 contract.** Confirm P2 only consumes the public `paths` API and does not modify any P1-shipped module.

A NO-GO with specific findings remains more valuable than a fast GO.

## 7. Reversibility (No Mutation by This Proposal)

This proposal does not mutate any artifact. The 3 commits in §3 occur only after Codex GO.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
