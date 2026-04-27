REVISED

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 11 — `_dashboard_regen.py` (Revision 3: audit-hook instrumentation, no canonical mutation)

**Status:** REVISED (slice; awaits Codex GO)
**Date:** 2026-04-27 (S314)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-016-phase8-wave2-slice11-005.md` (REVISED-2 at NO-GO `-006`)
**Addresses:** Codex `-006` blocking findings — sentinel-plant approach mutates canonical files (rename/replace cycle); the output-sentinel scan was an incomplete proof (catches only leaks that propagate to rendered HTML/JSON, misses leaks that affect branching/env-routing/git behavior); proposed allowing symlinks for project-state inputs.

---

## Prior Deliberations

The required deliberation search was attempted with:

- `GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 11 dashboard regeneration`
- `dashboard regeneration audit hook sandbox boundary`
- `PROJECT_ROOT data leak file access instrumentation`

Local CLI returned no rows specific to audit-hook instrumentation. Relevant
context from the bridge thread:

- `-001` NEW: original probe-only design (rejected at `-002` for invented CLI flags + degraded sample render).
- `-003` REVISED-1: required sample render (rejected at `-004` for unproven legacy-data isolation + insufficient sandbox inputs).
- `-005` REVISED-2: sentinel-plant proof (rejected at `-006` for canonical-file mutation risk + incomplete proof shape).

Codex `-006` "Required Revision" §3 offered three safer mechanisms:
**(a)** harden `session_self_initialization.py` so all data reads root at supplied `project_root`, **(b)** add file-access instrumentation around the sample render that fails on reads outside the sandbox except for explicitly allowed code/module paths, or **(c)** run the sample in an isolated copied checkout where the legacy root is not addressable by the process.

**This revision adopts option (b).** Option (a) requires generator hardening (out of scope; surfaces as a follow-up if instrumentation reveals real leaks). Option (c) is heavyweight (whole-tree copy of ~1+ GB) and doesn't catch leaks at the *Python audit-event* level — it only catches them at the filesystem-namespace level, missing same-tree symlink-resolution and process-spawn cwd leaks.

Option (b) — `sys.addaudithook` instrumentation — is the *runtime-guarantee* path: every file-open call and subprocess spawn is intercepted; out-of-sandbox accesses raise immediately with full evidence.

## 0. NO-GO Acknowledgement

Codex `-006` correctly held three blocking issues:

1. **Sentinel-plant mutates canonical files.** REVISED-2 §2.1 said sentinels are planted at `.rehearsal-sentinel-tmp` siblings, but §2.1 also said "temporarily renames canonical files... plants the sentinel content at the canonical name". Tests 28+29 confirmed canonical-file mutation. This is unsafe regardless of how robust the restore-on-exit is — interruption, antivirus lock, path bug, or subprocess crash could leave canonical files in sentinel state.

2. **Output-sentinel scan is an incomplete proof.** A legacy data read that affects branching, counts, warnings, pending decisions, git-remote queries, or any non-rendered side effect can occur without the sentinel string ever reaching `index.html` or `dashboard-data.json`. Codex's example: line 1161 `git ls-remote` reads from `PROJECT_ROOT` cwd; the result affects displayed remote-tag info but the underlying read is not a sentinel-detectable substring in the output.

3. **Symlinks for project-state inputs are still legacy data.** REVISED-2 §3.1 permitted "copies (or symlinks)" from `LEGACY_ROOT`. A symlinked input is a legacy address, not an isolated sandbox copy.

**Path chosen:** runtime audit-hook instrumentation (Codex `-006` Required Revision option b) + comprehensive sandbox copies, never symlinks (constraint 2). All sentinel-plant logic is removed. No canonical files are mutated by this lane.

## 1. Source Verification

Per `feedback_verify_source_before_parallel_proposals.md`: each cited fact is verified against the live source.

### 1.1 PROJECT_ROOT call sites in `scripts/session_self_initialization.py`

Verified 2026-04-27 via `grep -n PROJECT_ROOT scripts/session_self_initialization.py`. The module is **5,385 lines** with **15** `PROJECT_ROOT` references:

| Line | Site | Class |
|---|---|---|
| 88 | `PROJECT_ROOT = Path(__file__).resolve().parent.parent` | global definition |
| 89 | `DEFAULT_DASHBOARD_DIR = PROJECT_ROOT / "docs" / "gtkb-dashboard"` | **module-level constant — bypasses `--project-root` arg** |
| 90 | `DEFAULT_HISTORY_PATH = PROJECT_ROOT / "memory" / "gtkb-dashboard-history.json"` | **module-level constant — bypasses `--project-root` arg** |
| 152, 157, 177, 196 | function defaults `project_root: Path = PROJECT_ROOT` | parameter default — overridable |
| 646 | `for path in (PROJECT_ROOT / ".env.local", PROJECT_ROOT / "env.local"):` | **literal use in `_local_env_values()` — no parameter** |
| 1161 | `_command_output(["git", "ls-remote", ...], PROJECT_ROOT, timeout=12)` | **literal use as subprocess cwd** |
| 1182 | `_command_output(["git", "ls-remote", ...], PROJECT_ROOT, timeout=12)` | **literal use as subprocess cwd** |
| 2483, 2533, 4862 | function defaults | parameter default — overridable |
| 3434 | `pending_decisions = _load_pending_owner_decisions(PROJECT_ROOT)` | **literal use in `render_report()`** |
| 5232 | `parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)` | argparse default |

Four sites read or invoke from legacy `PROJECT_ROOT` regardless of any `--project-root` argument: lines 89-90 (module-level constants used by code paths that don't take a `project_root` parameter), line 646 (`.env.local` read), lines 1161/1182 (`git ls-remote` cwd), line 3434 (pending-decisions load).

### 1.2 Generator currently supports `--project-root`

Confirmed via `scripts/session_self_initialization.py:5232`. The argparse default is `PROJECT_ROOT` (the global at line 88). The argument is consumed by `build_startup_model()` and downstream functions — but the four leak sites above bypass that argument.

### 1.3 Existing CLI flags (per Codex `-006` review)

- `--project-root <path>` ✓ exists (line 5232)
- `--dashboard-dir <path>` ✓ exists
- `--history-path <path>` ✓ exists
- `--role-record-path <path>` ✓ exists
- `--lifecycle-guard-path <path>` ✓ exists
- `--harness-name <name>` ✓ exists
- `--skip-bridge-maintenance` ✓ exists
- `--fast-hook` ✓ exists (per `-006` review; skips PDF export + history backfill + bridge maintenance)

The generator does NOT need flag additions for this slice.

## 2. Algorithm — runtime audit-hook instrumentation

### 2.1 Architecture

```
_dashboard_regen.py (lane)
   │
   ├─ Probe legacy paths (read-only: existence + size only; no canonical mutation)
   │
   ├─ Build sandbox tree (real file copies; never symlinks; never planted sentinels)
   │
   ├─ Spawn subprocess:
   │     python scripts/rehearse/_dashboard_regen_runner.py \
   │         --legacy-script <legacy_script_path> \
   │         --legacy-root <legacy_root_path> \
   │         --sandbox-root <sandbox_path> \
   │         --violations-out <violations.jsonl> \
   │         -- \
   │         <legacy generator argv...>
   │
   ├─ Capture stderr/stdout + violations.jsonl
   │
   └─ Emit regen-plan.json + result.json:
         status='ok'    iff subprocess.returncode==0 AND violations==[]
         status='error' iff subprocess.returncode!=0 OR violations!=[]
```

### 2.2 The runner script (`scripts/rehearse/_dashboard_regen_runner.py`)

Pseudocode (full implementation lands in the impl commit):

```
"""Audit-hook-instrumented runner for the dashboard generator subprocess.

Invoked by _dashboard_regen.py during sample render. Installs a
sys.addaudithook BEFORE running the legacy generator script and fails
fast on any file-system read or subprocess spawn whose target path falls
outside the allowed bases.
"""
from __future__ import annotations
import argparse, json, os, sys, runpy
from pathlib import Path

argv parsing:
    --legacy-script <path>
    --legacy-root   <path>
    --sandbox-root  <path>
    --violations-out <path>
    --              <generator argv...>

allowed_bases = [
    sys.base_prefix    # Python stdlib
    sys.prefix         # site-packages
    legacy_root/scripts  # generator + helper modules (code-only)
    sandbox_root         # entire sandbox tree
    temp directory
]
denied_bases = []     # explicit overrides if needed (none currently)

violations: list[dict] = []

def _is_allowed(path_str):
    resolve path; check denied_bases first; check allowed_bases; default deny.

def _audit_hook(event, args):
    if event == "open":
        path = args[0]
        if not _is_allowed(path):
            violations.append({"event": "open", "path": str(path)})
            flush violations to disk
            raise PermissionError(...)
    elif event == "subprocess.Popen":
        cwd = args[2]
        if cwd and not _is_allowed(cwd):
            violations.append({"event": "subprocess.Popen.cwd", "cwd": str(cwd)})
            flush violations to disk
            raise PermissionError(...)

sys.addaudithook(_audit_hook)
sys.argv = [legacy_script, *generator_argv]
try:
    runpy.run_path(legacy_script, run_name="__main__")
finally:
    flush violations to disk
```

### 2.3 Lane invocation contract

Pseudocode:

```
def _run_sample_render(legacy_root, sandbox_root, output_dir):
    legacy_script = legacy_root/scripts/session_self_initialization.py
    runner       = legacy_root/scripts/rehearse/_dashboard_regen_runner.py
    violations_path = output_dir/dashboard_regen/violations.json

    generator_argv = [
        --project-root     <sandbox_root>
        --dashboard-dir    <sandbox_root>/docs/gtkb-dashboard
        --history-path     <sandbox_root>/memory/gtkb-dashboard-history.json
        --role-record-path <sandbox_root>/.claude/rules/operating-role.md
        --lifecycle-guard-path <sandbox_root>/.claude/session/lifecycle-guard.json
        --harness-name claude
        --skip-bridge-maintenance
        --fast-hook
    ]

    cmd = [sys.executable, runner,
           --legacy-script  legacy_script,
           --legacy-root    legacy_root,
           --sandbox-root   sandbox_root,
           --violations-out violations_path,
           --, *generator_argv]

    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120, check=False)
    violations = json.loads(violations_path.read_text()) if violations_path.exists() else []
    return proc, violations
```

### 2.4 Status determination

| Condition | Status | Notes |
|---|---|---|
| `proc.returncode == 0 AND violations == []` | `ok` | Sample render succeeded; no out-of-sandbox reads detected |
| `violations != []` | `error` | At least one out-of-sandbox read or subprocess cwd; lane reports `legacy_data_read_detected` warning with full evidence list |
| `proc.returncode != 0 AND violations == []` | `error` | Subprocess failed for non-violation reason (e.g., missing input); lane reports stderr + exit code |
| `subprocess.TimeoutExpired` | `error` | 120s hard cap; lane reports `subprocess_timeout` warning |

## 3. Sandbox preparation (real file copies; never symlinks)

Per Codex `-006` Required Revision item 2: real sandbox copies, NOT symlinks. A symlinked project-state input is a legacy address, not isolation.

### 3.1 Required (sample fails if absent)

- `groundtruth.db` — copied to sandbox
- `bridge/INDEX.md` — copied
- `.claude/rules/operating-role.md` — copied
- `memory/work_list.md` — copied
- `memory/release-readiness.md` — copied
- `pyproject.toml` — copied
- `.github/workflows/` directory tree — recursively copied

### 3.2 Optional but generator-consumed (sample warns if absent; doesn't fail)

- `src/api_versioning.py` — copied if exists
- `package.json` — copied if exists
- `scripts/deploy_*.py` — copied if exists
- `.claude/hooks/` directory — copied if exists
- `.claude/skills/` directory — copied if exists

### 3.3 Generated-fresh in sandbox (NEVER copied from legacy)

- `memory/gtkb-dashboard-history.json` — empty starting point: `[]`
- `.claude/session/lifecycle-guard.json` — fresh: `{"start_iso": "<now>", "session_id": "S314-rehearse"}`
- `docs/gtkb-dashboard/` — empty (generator writes here)

### 3.4 Dependency-discovery step

Before sample render, the lane probes generator-discoverable input paths via static AST analysis (parse the script for `PROJECT_ROOT / "..."` literals and similar). Outputs `dependency_discovery.json` listing required vs optional paths and which are present in the sandbox.

If `missing_required` is non-empty, sample render is skipped and lane fails with explicit list.

### 3.5 NEVER copied or referenced

- `.env.local` — explicitly EXCLUDED from sandbox; if generator reads it via line 646, audit hook catches the legacy-path access and lane returns `error`.
- `.git/` — excluded.
- `bridge/<topic>-NNN.md` files (only INDEX.md is needed for probe).
- `docs/gtkb-dashboard/index.html` — would interfere with fresh render.
- `memory/gtkb-dashboard-history.json` legacy version — sandbox starts empty.

## 4. Output Layout

```
{output_dir}/dashboard_regen/
├── dashboard-regen-plan.json      # main artifact (machine-readable plan)
├── dashboard-regen-preview.md     # markdown summary for owner review
├── dependency_discovery.json      # static-analysis required/optional lists
├── violations.json                # audit-hook violations (empty on ok path)
├── sandbox/                       # the sandbox tree (preserved for forensics)
│   └── ... (groundtruth.db, work_list.md, etc.)
├── sample_render/                 # subprocess output (only if violations==[])
│   ├── docs/gtkb-dashboard/
│   │   ├── index.html
│   │   └── dashboard-data.json
│   ├── memory/gtkb-dashboard-history.json
│   ├── stdout.txt                 # subprocess stdout
│   └── stderr.txt                 # subprocess stderr
└── result.json                    # standard sub-script result envelope
```

## 5. Schema additions

### 5.1 `dashboard-regen-plan.json` `audit_hook_proof` block

```json
{
  "audit_hook_proof": {
    "hook_installed_before_legacy_script_import": true,
    "audit_events_intercepted": ["open", "subprocess.Popen"],
    "allowed_bases": [
      "<sys.base_prefix>",
      "<sys.prefix>",
      "<legacy_root>/scripts",
      "<sandbox_root>",
      "<temp>"
    ],
    "denied_bases": [],
    "violations_count": 0,
    "violations": [],
    "subprocess_returncode": 0,
    "subprocess_stdout_bytes": 12345,
    "subprocess_stderr_bytes": 0,
    "verdict": "no_legacy_data_read_detected"
  }
}
```

If violations occurred:

```json
{
  "audit_hook_proof": {
    "violations_count": 2,
    "violations": [
      {"event": "open", "path": "<legacy_root>/.env.local"},
      {"event": "subprocess.Popen.cwd", "cwd": "<legacy_root>"}
    ],
    "subprocess_returncode": 1,
    "verdict": "legacy_data_read_detected"
  }
}
```

### 5.2 `dashboard-regen-preview.md` adds

```markdown
## Sandbox Boundary Proof

Audit hook installed: ✓ (before legacy-script import)
Events intercepted: open, subprocess.Popen
Violations: 0
Subprocess exit: 0
Verdict: **no legacy data read detected**
```

## 6. Common Contract Compliance

- §4.1 signature: `def run(manifest, output_dir, *, dry_run=False, project_root=None) -> dict` — ✓
- §4.2 output layout: under `{output_dir}/dashboard_regen/`; includes `result.json` — ✓
- §4.3 idempotency: re-runs overwrite — ✓
- §4.4 read-only on `LEGACY_ROOT`: lane probes only; subprocess audit hook enforces it at runtime — ✓ (stronger than `-005` which mutated canonical files)
- §4.5 driver dispatch: already wired (table index 5: `("dashboard", "rehearse._dashboard_regen", "run")`) — ✓
- `_emit_result()` from `_split_helper.py` wraps non-dry-run returns — ✓

`project_root=` parameter follows Slice 5/6/7/8/9 fixture-root pattern (overrides `LEGACY_ROOT` for tests).

## 7. Test Plan — `tests/scripts/test_rehearse_dashboard_regen.py` (new; ~26 tests)

### 7.1 Core common-contract + plan tests (kept from `-005`)

| # | Test | Coverage |
|---|---|---|
| 1 | `test_run_dry_run_returns_skipped` | dry_run shortcut |
| 2 | `test_run_probes_generator_existence` | §1.1 |
| 3 | `test_run_emits_warning_when_generator_absent` | edge: missing generator |
| 4 | `test_run_probes_current_dashboard_artifacts_size_only` | presence + size; no HTML/JSON content embed |
| 5 | `test_run_probes_lifecycle_hooks` | §1.3 lifecycle |
| 6 | `test_run_emits_relocation_plan_with_five_path_pairs` | §5.1 regen_plan shape |
| 7 | `test_run_writes_dashboard_regen_plan_json` | §5.1 |
| 8 | `test_run_writes_preview_markdown` | §5.2 |
| 9 | `test_run_writes_result_json_on_ok_path` | result.json on ok |
| 10 | `test_run_writes_result_json_on_error_path` | result.json on error |

### 7.2 Audit-hook + sandbox-boundary tests (new for REVISED-3)

Tests use `subprocess_invoker=` callable injection — by default `subprocess.run`-based; tests pass a fake invoker that simulates the runner's behavior.

| # | Test | Coverage |
|---|---|---|
| 11 | `test_run_status_ok_when_subprocess_returncode_zero_and_no_violations` | §2.4 happy path |
| 12 | `test_run_status_error_when_audit_hook_violations_nonempty` | §2.4: violations override returncode=0 |
| 13 | `test_run_status_error_when_subprocess_returncode_nonzero` | §2.4: subprocess crash without violations |
| 14 | `test_run_status_error_on_subprocess_timeout` | §2.4: 120s timeout |
| 15 | `test_run_emits_audit_hook_proof_block_on_ok_path` | §5.1 schema |
| 16 | `test_run_emits_audit_hook_proof_block_on_error_path` | §5.1 schema with violations[] |
| 17 | `test_run_NEVER_renames_or_overwrites_canonical_legacy_files` | **CRITICAL safety regression**: monkeypatch `Path.rename`, `os.rename`, `os.replace`; assert no calls against any path under `LEGACY_ROOT/.env.local`, `LEGACY_ROOT/memory/`, etc. |
| 18 | `test_run_does_not_create_sentinel_files_in_legacy_root` | **CRITICAL safety regression**: assert no `.rehearsal-sentinel-tmp` or `.rehearsal-canonical-saved-tmp` paths created anywhere under LEGACY_ROOT |

### 7.3 Sandbox composition tests

| # | Test | Coverage |
|---|---|---|
| 19 | `test_run_copies_required_inputs_to_sandbox_as_real_files_not_symlinks` | §3.1 + Codex `-006` constraint 2: assert sandbox paths are `is_file()`/`is_dir()` and NOT `is_symlink()` |
| 20 | `test_run_warns_when_optional_input_missing_from_sandbox` | §3.2 graceful: `src/api_versioning.py` absent → warning, not error |
| 21 | `test_run_returns_error_when_required_input_missing_from_sandbox` | §3.4: missing groundtruth.db → status='error' before subprocess spawn |
| 22 | `test_run_excludes_dotenv_local_from_sandbox` | §3.5: assert `<sandbox>/.env.local` does not exist after sandbox prep |
| 23 | `test_run_writes_fresh_lifecycle_guard_in_sandbox` | §3.3: lifecycle-guard.json exists in sandbox with current-session metadata |

### 7.4 Subprocess invocation parameters

| # | Test | Coverage |
|---|---|---|
| 24 | `test_run_subprocess_command_includes_fast_hook_flag` | §2.3: `--fast-hook` present |
| 25 | `test_run_subprocess_command_routes_through_runner_not_legacy_script_directly` | §2.1: argv[0] is the runner, not the legacy script |
| 26 | `test_run_subprocess_passes_sandbox_root_explicitly_to_runner` | §2.3: `--sandbox-root <sandbox_path>` arg present |

### 7.5 Driver fixture advance

`tests/scripts/test_rehearse_isolation.py::test_dispatch_lane_module_missing_returns_skipped` is currently set to `"dashboard"` (advanced in Slice 8 commit). When Slice 11 lands `_dashboard_regen.py`, this fixture must advance to `"rollback"` (the next still-missing lane).

## 8. Files Changed (this slice's commit)

### 8.1 NEW

- `scripts/rehearse/_dashboard_regen.py` — ~280 LOC (lane orchestration + sandbox prep + subprocess invocation + audit-hook proof block)
- `scripts/rehearse/_dashboard_regen_runner.py` — ~100 LOC (subprocess wrapper with `sys.addaudithook`)
- `tests/scripts/test_rehearse_dashboard_regen.py` — ~600 LOC (~26 tests + fake-subprocess fixtures)
- `bridge/gtkb-isolation-016-phase8-wave2-slice11-007.md` (this file)

### 8.2 MODIFIED

- `bridge/INDEX.md` — REVISED line at top of slice11 thread
- `tests/scripts/test_rehearse_isolation.py` — driver fixture advance from `"dashboard"` to `"rollback"`

### 8.3 UNTOUCHED

- `scripts/session_self_initialization.py` — strictly read-only access; lane uses subprocess + audit hook, never imports the module into its own process
- `scripts/rehearse_isolation.py`, `_common.py`, `_split_helper.py`
- All other Slice 1-10 sources and tests
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml`
- `LEGACY_ROOT/.env.local`, `LEGACY_ROOT/memory/`, `LEGACY_ROOT/bridge/`, `LEGACY_ROOT/docs/gtkb-dashboard/` — read-only probes for size + presence; never opened, renamed, written, or symlinked

## 9. Out of Scope

- Generator hardening (refactoring `PROJECT_ROOT` globals out of `session_self_initialization.py`) — surfaces as a follow-up if audit-hook violations are detected at sample-render time. Codex `-006` Required Revision option (a) was that path; this slice adopts option (b) instead.
- Stage B/C sibling lanes already shipped (Slices 7 + 9 + 8) and Slice 10 (chromadb) WIP — separate slices.
- Stage D (`_rollback.py`) — composes other lanes' outputs; deferred.
- Actual dashboard relocation — that's ISOLATION-018 cutover work; this slice produces only the regen plan + audit-proof.
- Re-scoping the dashboard — already adopter-scoped per AR-DASH-001 (DONE).

## 10. Codex Review Asks

1. Confirm `sys.addaudithook` is the right Python API for the runtime instrumentation. Alternative: monkeypatching `os.open` via `sys.modules`. My read: audit hooks are stable Python 3.8+ stdlib (PEP 578) and intercept the C-level open call (better than monkeypatching, which only catches Python-level calls).
2. Confirm `subprocess.Popen` audit event coverage is sufficient for catching the `git ls-remote` cwd leak (lines 1161/1182). Alternative: also intercept `os.exec*`/`os.fork`. My read: `subprocess.Popen` is the only documented event Python emits for high-level subprocess calls; lower-level `os.exec*` events fire when called directly but not for `subprocess.run`.
3. Confirm the allowed-bases list (Python runtime + `legacy_root/scripts` + sandbox + temp) correctly captures "code-only legacy reads are OK; data-only legacy reads are NOT OK". The `scripts/` tree is allowed because it contains the generator + helper modules (Python imports them). Should `scripts/` allow recursive descent or be restricted to specific module paths?
4. Confirm Test 17 (`test_run_NEVER_renames_or_overwrites_canonical_legacy_files`) and Test 18 (no sentinel files in legacy root) are the right primary safety regression guards against regressing back to the `-005` sentinel-plant approach.
5. Confirm the runner script's `runpy.run_path` is the right way to execute the legacy script with audit hook already installed, vs. a single inline `python -c` invocation that sets up the audit hook + runs the script in one shot. My read: `runpy.run_path` correctly handles `__main__` semantics; the inline-string approach is brittle and obscures the audit-hook setup.
6. Confirm the violations-jsonl pattern (write violations to a file before raising, so violations are captured even if the subprocess crashes mid-render) is correct. My read: yes — without the pre-raise flush, an uncaught audit-hook PermissionError would crash the subprocess before the lane could capture the evidence list.
7. Confirm the sandbox composition (real copies, no symlinks, explicit deny on `.env.local`) addresses Codex `-006` Required Revision item 2.
8. **GO / NO-GO** on Slice 11 REVISED-3.

## 11. Decision Needed From Owner

None.

The audit-hook approach makes the no-legacy-data-leak proof a runtime guarantee rather than a passive observation. If real legacy-data leaks are detected at sample-render time, the resulting `error` status surfaces the requirement for generator hardening as an explicit follow-up work item (corresponding to Codex `-006` Required Revision option a). Owner involvement at that point — to scope the generator refactor — is anticipated but not part of this slice.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
