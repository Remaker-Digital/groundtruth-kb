NEW

# GTKB Session Overlay Baseline Implementation Report

bridge_kind: implementation_report
scope: protocol
work_item_ids: [GTKB-ISOLATION-006]
parent_proposal: bridge/gtkb-session-overlay-baseline-implementation-001.md
parent_go: bridge/gtkb-session-overlay-baseline-implementation-002.md
target_paths: [".gitignore", "scripts/gtkb_overlay.py", "scripts/check_session_overlay_policy.py", "scripts/release_candidate_gate.py", "scripts/session_self_initialization.py", "tests/scripts/test_gtkb_overlay.py", "tests/scripts/test_release_candidate_gate.py", "tests/scripts/test_session_self_initialization.py"]

## Requested Verdict

VERIFIED that this implementation lands the narrow Phase 6 first-slice overlay
baseline exactly as approved in `-002.md`, respects every `Required
Implementation Boundary`, and introduces no promotion/apply/refresh/hook-
enforcement surface, or NO-GO with specific deviations to address.

## Scope Adherence To GO Boundaries

| Required Boundary (from `-002.md`) | Implementation Location | Status |
|---|---|---|
| Overlay builder copy-only in this slice | `scripts/gtkb_overlay.py::build_overlay` uses `shutil.copy2` only; no write-back path exists and no callers mutate sources | ✓ |
| No promotion/apply, no bridge summary / DA / MemBase / raw DB copies, no hook enforcement | `scripts/gtkb_overlay.py` exposes only builder/loader/validator/stale-evaluator; no `promote`, `apply`, `refresh`, `bridge_summary`, or hook-trigger function is defined or referenced | ✓ |
| `.gitignore` coverage for `.groundtruth/session/overlays/` preserved | `.gitignore` flat ignore with documented rationale block; `test_gitignore_covers_overlay_runtime_root` asserts literal presence | ✓ |

## Delivered Surfaces

### 1. Overlay Library (`scripts/gtkb_overlay.py`, new)

Copy-only, non-authoritative overlay mechanics:

- `OVERLAY_ROOT_RELATIVE = .groundtruth/session/overlays/`,
  `OVERLAY_SCHEMA_VERSION = "1"`, `DEFAULT_OVERLAY_TTL = 12h`.
- `ALLOWLIST` — fixed 4-tuple binding exact source path -> exact overlay
  basename. The binding is enforced both ways: `_validate_allowlist_source`
  returns the required basename, and `build_overlay` raises
  `OverlayPolicyError` if the caller attempts any other name. Bypass of the
  allowlist is not reachable from the module's public API.
- `FORBIDDEN_NAME_PATTERNS` defense-in-depth denylist covering `.env*`,
  `groundtruth.db`, `.groundtruth-chroma/`, `bridge/`, and executable
  extensions (`.py|.ps1|.sh|.bat|.cmd|.exe|.dll|.so|.dylib|.vbs`).
- `OverlayManifest`, `OverlayEntry`, `OverlayStalenessReport`,
  `OverlayStalenessEntry` are frozen dataclasses; every instance carries
  `authoritative=False` in its manifest schema and per-entry.
- `build_overlay(...)` creates `<overlay_id>/files/` + `manifest.json`,
  updates `current.json`, and records a sha256 source hash per entry. Missing
  sources are silently skipped (staleness report surfaces them later).
- `validate_manifest(...)` refuses any manifest that claims
  `authoritative=True`, has a mis-shaped `overlay_id`, escapes the
  application root, uses a source outside the allowlist, uses an overlay
  path outside the allowlist, has non-`file` source kind, fails sha256
  shape, is a duplicate, or matches a forbidden denylist pattern.
- `evaluate_staleness(...)` re-hashes live sources and flags both expired
  overlays and entry-level hash drift.
- `current_overlay_status(...)` returns a structured startup snapshot that
  never propagates a raised exception out — wrapped by
  `_safe_overlay_status` in the startup generator.

### 2. Policy Checker (`scripts/check_session_overlay_policy.py`, new)

Read-only release-gate checker. Iterates every overlay directory under
`.groundtruth/session/overlays/`, calls `load_manifest` + `validate_manifest`
+ `evaluate_staleness`, and produces a structured report with per-overlay
`valid`, `errors`, and `staleness` fields. Exits 1 if any error is recorded,
0 otherwise. Supports `--json` for programmatic consumers and a text
`PASS`/`FAIL` line for the release-gate output stream. `--project-root` is
respected so tests can invoke it against a temporary tree.

Pointer validation guards catch an authoritative pointer or a pointer whose
`overlay_dir` escapes the overlay root.

### 3. Startup Visibility (`scripts/session_self_initialization.py`, modified)

Additive only. Existing startup model/report behavior unchanged for all
existing fields.

- Two-path import of the new library (`scripts.gtkb_overlay` with a bare
  `gtkb_overlay` fallback for direct-script execution, mirroring the
  existing `workstream_focus` import pattern).
- New helper `_safe_overlay_status(project_root)` swallows any exception
  from the library and returns a safe absent-overlay shape. This keeps
  startup emission non-fatal on corrupted local overlay state.
- New key `session_overlay` on the startup model (sibling to
  `workstream_focus`). Preserves the existing keys verbatim.
- New helper `_render_session_overlay_status(status)` emits bullet lines
  documenting the overlay root, the non-authoritative contract, current
  overlay id (if any), stale/expired flags, and the library-supplied notes.
- New section `### Session Overlay Status (Non-Authoritative)` inserted in
  `render_report(...)` between `### Active Workstream Focus` and
  `### Fresh-Session Input Semantics`. Ordering is verified by the startup
  test (`< "### Fresh-Session Input Semantics"`).

### 4. Release Gate Wiring (`scripts/release_candidate_gate.py`, modified)

- `_run([sys.executable, "scripts/check_session_overlay_policy.py"])`
  scheduled after `check_environment_isolation.py` and strictly before the
  pytest invocation, with a 60s timeout matching the adjacent policy
  checkers.
- `tests/scripts/test_gtkb_overlay.py` added to the pytest target list in
  `_python_gates`, so the overlay library tests run in the same invocation
  that already covers `test_session_self_initialization.py` and
  `test_release_candidate_gate.py`.

### 5. `.gitignore` Coverage (`.gitignore`, modified)

Added a dedicated section with rationale comment and the flat ignore
`.groundtruth/session/overlays/`. Placed before the
`"Ephemeral session/evaluation artifacts"` block.

### 6. Tests

- `tests/scripts/test_gtkb_overlay.py` (new, 13 tests):
  - copy-only, non-authoritative manifest/entry shape, basename binding,
  - current pointer shape,
  - non-allowlisted source rejected (`scripts/release_candidate_gate.py`
    used as the counter-example),
  - forbidden-denylist rejection even when the caller fabricates an
    allowlist-second-element match,
  - missing sources silently skipped,
  - stale detection on source hash drift,
  - expiry-only staleness independent of source drift,
  - `validate_manifest` rejects authoritative + application_root escape,
  - `current_overlay_status` absent/present shapes,
  - `.gitignore` covers overlay runtime root,
  - checker exits 0 on clean tree with JSON payload correct,
  - checker exits 1 with `FAIL` stderr when a manifest is flipped to
    authoritative.
- `tests/scripts/test_release_candidate_gate.py::test_python_gate_runs_session_overlay_policy_before_pytest`
  — asserts the ordering `env_index < overlay_index < pytest_index` and
  that `tests/scripts/test_gtkb_overlay.py` is in the pytest command.
- `tests/scripts/test_session_self_initialization.py::test_startup_report_surfaces_session_overlay_status_as_non_authoritative`
  — asserts `session_overlay` is present in the model, is
  non-authoritative, has the expected notes/shape, the report section
  header exists, the "non-authoritative by construction" string appears,
  and the section precedes "Fresh-Session Input Semantics".

## Verification Evidence

Commands executed from repo root at verification time (`2026-04-23`):

```powershell
python scripts/check_session_overlay_policy.py --json
# -> exit 0; {"pass": true, "overlay_count": 0, "pointer_present": false, ...}

python -m pytest tests/scripts/test_gtkb_overlay.py \
  tests/scripts/test_release_candidate_gate.py \
  tests/scripts/test_session_self_initialization.py -q --tb=short
# -> 42 passed, 1 failed, 1 warning
# -> the 1 failure is pre-existing and unrelated (see Pre-existing Drift note)

python -m pytest tests/scripts/test_gtkb_overlay.py \
  tests/scripts/test_release_candidate_gate.py::test_python_gate_runs_session_overlay_policy_before_pytest \
  tests/scripts/test_session_self_initialization.py::test_startup_report_surfaces_session_overlay_status_as_non_authoritative \
  -q --tb=short
# -> 15 passed, 1 warning in 6.59s
```

The 15-test isolated run covers every test that exercises code this
implementation added or modified.

## Pre-existing Drift (Not Introduced By This Slice)

`tests/scripts/test_session_self_initialization.py::test_startup_model_contains_role_governance_and_kpi_inventory`
fails locally because it asserts `"workstream-focus.py" in
model["directives"]["hook_files"]`, but that hook file is absent from
`.claude/hooks/` on the current `main` tip (it was removed during the S304
bridge-restoration commit `c6882c9d` documented in `memory/MEMORY.md`). The
failure reproduces on a clean working copy (verified via
`git stash && pytest && git stash pop`) and is unaffected by any of the
files this implementation touched. Remediation belongs to the existing
S304-restoration follow-up, not this bridge.

## Commit Plan

All file changes are staged on the working tree. Recommended single commit
message after VERIFIED is posted:

```
feat(gtkb): Phase 6 session-overlay baseline (non-authoritative, copy-only)

- Adds scripts/gtkb_overlay.py (manifest/builder/stale/validate).
- Adds scripts/check_session_overlay_policy.py release-gate checker.
- Wires overlay status into session_self_initialization startup report.
- Extends release_candidate_gate to run the checker and the new tests.
- Adds .gitignore coverage for .groundtruth/session/overlays/.
- Adds 13 overlay library tests + release-gate ordering test +
  startup-report visibility test.

GTKB-ISOLATION-006. Bridge:
  bridge/gtkb-session-overlay-baseline-implementation-{001,002,003}.md
```

## Non-Scope Confirmation

This slice does NOT implement, register, expose, or depend on any of the
following — all remain later-slice work:

- overlay promotion or apply,
- control-plane overlay refresh endpoints,
- projection preview storage,
- bridge summary copies,
- Deliberation Archive or MemBase copies,
- raw `groundtruth.db` or `.groundtruth-chroma/` copies,
- overlay-dependent hook or startup enforcement paths,
- retention cleanup beyond manifest validation.

No startup, wrap-up, or release-gate code path now treats overlay data as
canonical.

## Owner Decision Needed

None. Requesting VERIFIED.
