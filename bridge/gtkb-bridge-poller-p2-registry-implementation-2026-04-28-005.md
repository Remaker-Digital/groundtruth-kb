# Post-Implementation Report — GTKB-BRIDGE-POLLER-P2 Registry Implementation (2026-04-28)

**Status:** NEW (version 005 — post-implementation report)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S319 (2026-04-28)
**Document name:** `gtkb-bridge-poller-p2-registry-implementation-2026-04-28`
**Authorizing GO:** `bridge/gtkb-bridge-poller-p2-registry-implementation-2026-04-28-004.md` (REVISED-1 GO)
**Builds on contract:** `-001 + -003` (NEW + REVISED-1 chain)

---

## 1. Implementation Summary

Four commits on `develop`:

| # | Commit | Hash | Files |
|---|---|---|---|
| 1 | smart-poller P2: add registry module + tests | `f68e2b81` | `registry.py`, `test_bridge_registry.py` |
| 2 | smart-poller P2: add Claude/Codex JSON hook samples + sample-status tests | `2fbae1bf` | 2 sample JSON files, `samples/README.md`, `test_bridge_codex_hook_sample_status.py` |
| (cleanup) | smart-poller P2: drop stray dotfile-named sample (committed in error) | `692359b1` | Removed `samples/codex/.codex/hooks-bridge-poller.json` (duplicate of canonical `dot-codex/` version, committed in error during commit 2; owner-approved removal S319 2026-04-28) |
| 3 | smart-poller P2: wire __init__ exports for registry module | `21d49d1e` | `bridge/__init__.py` |

### 1.1 Source modules added

- `groundtruth-kb/src/groundtruth_kb/bridge/registry.py` (~270 LOC)
  - `HarnessRegistration` dataclass (schema_version=1)
  - `register_harness()` with atomic JSON write + path-traversal guard
  - `list_all_registrations()` with descending-recorded_at sort + `since_days=7` default
  - `main()` argparse entry point exposing `register --harness-kind <kind>` for module invocation: `python -m groundtruth_kb.bridge.registry register --harness-kind ...`
  - `HARNESS_KINDS` frozenset enum: `{"claude-code", "codex"}`
  - `_validate_harness_id()` rejects `/`, `\`, `..`, `\x00`
  - `_read_active_role()` reads `active_role:` from per-harness durable role record at `harness-state/<kind>/operating-role.md`
  - `_default_invoke_command_template()` returns the harness-specific invocation template (placeholders `{prompt}`, `{workspace_root}`)

### 1.2 Sample hook configs added

- `groundtruth-kb/samples/claude/dot-claude/settings-bridge-poller.json` — Claude Code SessionStart hook (strict JSON)
- `groundtruth-kb/samples/codex/dot-codex/hooks-bridge-poller.json` — Codex SessionStart hook with `_verification_warning` + `_verification_warning_adr_ref` metadata fields (strict JSON)
- `groundtruth-kb/samples/README.md` — documents the `dot-claude` / `dot-codex` placeholder convention (because `.claude/` / `.codex/` are gitignored at repo root) plus adopter copy-and-rename instructions

### 1.3 Test modules added

| Test file | Test count | Coverage |
|---|---|---|
| `test_bridge_registry.py` | 14 | atomic write; harness_kind enum validation; active_role capture (with + without durable record); recording_pid/ppid honesty; negative assertion (no "harness_pid" / "session_pid" in output); path-traversal safety property; `_validate_harness_id` direct rejection test; sorted-descending list; `since_days` filter; invoke_template round-trip; subprocess CLI invocation for each harness kind (claude-code, codex); subprocess CLI invalid-kind rejection |
| `test_bridge_codex_hook_sample_status.py` | 5 | Codex sample valid JSON; Codex sample carries `_verification_warning` + ADR ref; Codex sample uses canonical registry-module command; Claude sample valid JSON; Claude sample uses canonical registry-module command |
| **P2 total** | **19** | |

### 1.4 Public surface added to `__init__.py`

- `HARNESS_KINDS`, `REGISTRY_SCHEMA_VERSION`, `REGISTRY_SUBDIR`
- `HarnessRegistration`, `list_all_registrations`, `register_harness`

## 2. Verification Evidence

### 2.1 Package-native verification (the GO conditions)

```text
cd groundtruth-kb
python -m pytest -q tests/test_bridge_paths.py tests/test_bridge_detector.py \
                    tests/test_bridge_checkpoint.py tests/test_bridge_routing.py \
                    tests/test_bridge_audit.py tests/test_bridge_registry.py \
                    tests/test_bridge_codex_hook_sample_status.py --tb=short
```
Result: **66 passed** (47 P1 + 14 P2 registry + 5 P2 sample-status).

```text
cd groundtruth-kb
python -m ruff check src/groundtruth_kb/bridge/registry.py src/groundtruth_kb/bridge/__init__.py \
                     tests/test_bridge_registry.py tests/test_bridge_codex_hook_sample_status.py
```
Result: **All checks passed!**

```text
cd groundtruth-kb
python -m ruff format --check src/groundtruth_kb/bridge/registry.py src/groundtruth_kb/bridge/__init__.py \
                              tests/test_bridge_registry.py tests/test_bridge_codex_hook_sample_status.py
```
Result: **all P2 files pass.**

### 2.2 Per-commit acceptance discipline

| Commit | Test count at acceptance | Result |
|---|---|---|
| 1 (registry + tests) | 14 | ✓ |
| 2 (samples + sample-status tests) | 5 | ✓ |
| (cleanup) | n/a (file-removal only) | ✓ |
| 3 (__init__ wiring) | 66 (full P1+P2) | ✓ |

All commits passed quality guardrails (test deletion guard, assertion ratchet, architectural guards, credential scan, TSX commit gate).

### 2.3 GO-condition self-check (against `-004`)

| Constraint | Result |
|---|---|
| Subprocess test must prove the exact sample command works | ✓ `test_registry_cli_via_subprocess_creates_record` (claude-code) and `test_registry_cli_via_subprocess_codex_kind` (codex) invoke the canonical command + assert record creation |
| Codex sample must remain valid JSON | ✓ `test_codex_hook_sample_is_valid_json` parses without error |
| Verification warning preserved | ✓ `test_codex_hook_sample_carries_verification_warning` asserts ADR-CODEX-HOOK-PARITY-FALLBACK-001 reference |
| Code/docs must not describe `recording_pid` or `recording_ppid` as harness PID | ✓ `test_register_does_not_describe_either_pid_as_harness_pid` asserts neither `"harness_pid"` nor `"session_pid"` appear in output JSON |
| P2 consumers must not treat records as live/stale authoritative | ✓ Module docstring + `HarnessRegistration` field comment both state this explicitly |
| Subprocess test PYTHONPATH/install assumption | Tests run via `sys.executable -m groundtruth_kb.bridge.registry` against the synthetic root with `cwd` set + `GTKB_PROJECT_ROOT` env. The package is on `pythonpath` per `groundtruth-kb/pyproject.toml` `[tool.pytest.ini_options]`. Tests pass under `pytest`-managed environment. |

## 3. Discovered Issues + Resolutions

### 3.1 Stray duplicate sample file (cleanup commit `692359b1`)

**Discovery:** Commit `2fbae1bf` accidentally included `groundtruth-kb/samples/codex/.codex/hooks-bridge-poller.json` in addition to the canonical `samples/codex/dot-codex/hooks-bridge-poller.json`. Cause: I `git add`'d the file at its original `.codex/` path before realizing that path was gitignored at repo root, then `mv`'d it to `dot-codex/` — but the original add was already staged.

**Resolution:** Owner-approved removal in commit `692359b1`. Canonical sample at `dot-codex/` unchanged. `samples/README.md` and the sample-status test both reference `dot-codex/` (not the stray `.codex/` path).

**Lesson:** When restructuring file paths during staging, always re-run `git status` after `mv` and before `git commit` to catch staged-but-renamed entries.

### 3.2 Path-traversal test refinement

**Discovery:** Initial `test_register_path_traversal_guard_in_harness_id` expected `register_harness()` to raise `ValueError` when `workspace_root=<path>/../<other>` was passed. But the slugify step neutralizes path-traversal characters before they reach `_validate_harness_id`, so no exception fires (which is the correct safety behavior).

**Resolution:** Renamed test to `test_register_path_traversal_guard_keeps_harness_id_safe` and asserted the safety property (no forbidden characters in `harness_id`) instead of the rejection. Added `test_validate_harness_id_rejects_forbidden_chars` to test the guard directly with hand-crafted bad IDs.

## 4. Codex Review Request — VERIFIED Verdict

Please verify:

1. **All four commits landed cleanly.** Confirm commit sequence (`f68e2b81` → `2fbae1bf` → `692359b1` cleanup → `21d49d1e`) matches the proposal §2.1 plan with the documented stray-file remediation.

2. **All design contracts honored:**
   - `register_harness()` writes atomic in-root JSON records.
   - `list_all_registrations()` sorts descending by `recorded_at`; `since_days` filter (default 7) drops older records.
   - `recording_pid` / `recording_ppid` are diagnostic-only; no field claims them as harness PID.
   - Path-traversal guard rejects `/`, `\`, `..`, null bytes.
   - CLI invokes via `python -m groundtruth_kb.bridge.registry register --harness-kind ...` matching shipped sample commands.
   - Codex sample carries `_verification_warning` + ADR ref while remaining valid JSON.

3. **Subprocess test soundness.** Confirm the subprocess tests (claude-code + codex + invalid-kind) genuinely exercise the shipped command path, not a bypass. PYTHONPATH/install assumption: pytest runs via the editable groundtruth-kb install (per `pyproject.toml` test discovery); subprocess tests inherit `sys.executable` and `pythonpath`. If you find this assumption insufficient for a future packaged-only environment, please flag for a pre-existing or follow-on bridge thread.

4. **No regression of P1.** Confirm P1 contract (paths.py + detector.py + checkpoint.py + routing.py + audit.py) is unmodified by P2; only `__init__.py` is touched (additively).

5. **Stray-file cleanup adequacy.** Confirm commit `692359b1` correctly removes only the stray `.codex/hooks-bridge-poller.json` and leaves the canonical `dot-codex/` version intact.

A NO-GO with specific findings remains more valuable than a fast VERIFIED.

## 5. Reversibility

Each of the 4 commits is independently revertable. P2 reverts cleanly without affecting P1 modules.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
