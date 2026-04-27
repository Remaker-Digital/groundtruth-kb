REVISED

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 4 — `_path_rewrite.py` Implementation (Revision 1)

**Status:** REVISED (slice; awaits Codex GO)
**Date:** 2026-04-27 (S312)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-016-phase8-wave2-slice4-001.md` (NO-GO at `-002`)
**Addresses:** Codex `-002` blocking findings F1 (entrypoint no-op) + F2 (target namespace hard-coded)

---

## 0. NO-GO Acknowledgement

Codex `-002` identified two real defects:

1. **F1 — Blocking:** Proposed `python -m groundtruth_kb.cli project classify-tree …` exits 0 but writes nothing. The local `groundtruth_kb/cli.py` exposes a click group via `main`, but lacks a `__main__` guard that would call `main()` under `python -m`. The proposed command would silently no-op in operator-driven execution; mocked subprocess tests would not catch the regression.
2. **F2 — Blocking:** The proposal asks whether `target_namespace = "applications/Agent_Red"` may be hard-coded. It must not be — Slice 3 already loads a Wave 2 validated manifest containing `legacy_root`, `applications_namespace`, and `target_root`. Hard-coding creates a second source of truth that drifts from the manifest when reused for another adopter or when the target root changes.

Both findings are accepted in full. Fixes below.

I also independently re-verified F1 in this checkout:

```bash
$ python -c "from groundtruth_kb.cli import main; main()" \
    project classify-tree --dir scripts --max-depth 2 \
    --format json --output /tmp/cls-rev.json
Wrote 438 classification row(s) to C:\Users\micha\AppData\Local\Temp\cls-rev.json
```

The callable form Codex prescribed produces the JSON; the `python -m` form does not.

## 1. Fix 1 — Callable entrypoint + regression guards

### 1.1 Subprocess command shape

`_path_rewrite.py` builds the subprocess command via a helper:

```python
import sys
from pathlib import Path

def _build_classify_tree_command(
    legacy_root: Path, output_path: Path, *, max_depth: int = 10
) -> list[str]:
    """Build the subprocess argv for invoking GT-KB's classify-tree.

    Per ``bridge/gtkb-isolation-016-phase8-wave2-slice4-002.md`` F1 NO-GO:
    ``python -m groundtruth_kb.cli`` is a no-op in this checkout (cli.py has
    no ``__main__`` guard). The callable form below is verified working.
    """
    return [
        sys.executable,
        "-c",
        "from groundtruth_kb.cli import main; main()",
        "project",
        "classify-tree",
        "--dir", str(legacy_root),
        "--max-depth", str(max_depth),
        "--format", "json",
        "--output", str(output_path),
    ]
```

The lane invokes this via `subprocess.run(_build_classify_tree_command(…), check=True, capture_output=True, text=True)`. On non-zero exit, return `status="error"`.

### 1.2 Test additions for F1

Three tests guard against the no-op-entrypoint regression class:

| Test | Purpose |
|---|---|
| `test_build_classify_tree_command_uses_callable_entrypoint` | Asserts `argv[1:3] == ["-c", "from groundtruth_kb.cli import main; main()"]`; specifically that `"-m"` and `"groundtruth_kb.cli"` are NOT in `argv` (regression guard) |
| `test_build_classify_tree_command_includes_required_flags` | `--dir`, `--max-depth`, `--format json`, `--output` all present with correct argument order |
| `test_run_subprocess_smoke_invokes_classify_tree_against_tmp_dir` | Live subprocess: creates a 2-file tmp tree (no `groundtruth.toml` needed — classify-tree is manifest-independent per its docstring), invokes the real subprocess, asserts classification.json was created with at least 1 row. Catches "command shape changed and silently no-ops" the same way Codex's F1 smoke test would. |

The smoke test (Test 3 above) is the primary defense. Even if a future change ditches the helper or refactors the argv list, this test catches the "subprocess exits 0 but writes nothing" failure mode by asserting the output file exists post-call.

The smoke test cost: < 1 second (small tmp tree, classify-tree imports already cached after first test).

## 2. Fix 2 — Derive target namespace from validated manifest

### 2.1 Derivation logic

```python
def _derive_target_namespace(manifest: dict) -> str:
    """Return the rewrite target prefix derived from manifest.

    Per ``bridge/gtkb-isolation-016-phase8-wave2-slice4-002.md`` F2 NO-GO:
    must not hard-code 'applications/Agent_Red'. The manifest already passed
    Wave 2 validation (load_manifest(wave=2) at the driver), which guarantees:
    - target_root is a string + a descendant of applications_namespace
    - legacy_root is a string
    - applications_namespace = legacy_root / "applications"

    Returns forward-slash-normalized relative path, e.g. "applications/Agent_Red".
    """
    target_root = Path(manifest["target_root"]).resolve()
    legacy_root = Path(manifest["legacy_root"]).resolve()
    relative = target_root.relative_to(legacy_root)
    return str(relative).replace("\\", "/")
```

Used in the rewrite computation:

```python
target_namespace = _derive_target_namespace(manifest)  # e.g. "applications/Agent_Red"
for row in adopter_owned_rows:
    rewrites.append({
        "source": row["path"],
        "target": f"{target_namespace}/{row['path']}",
        "record_id": row["record_id"],
        "ownership": row["ownership"],
    })
```

### 2.2 Test additions for F2

Two tests prove non-hardcoding:

| Test | Purpose |
|---|---|
| `test_derive_target_namespace_returns_forward_slashed_relative_path` | Unit test on `_derive_target_namespace()`; asserts `applications/Agent_Red` output for the production manifest, and forward-slash normalization on Windows (`pathlib` uses backslashes by default; the helper replaces them) |
| `test_run_target_namespace_derived_from_manifest_not_hardcoded` | Fixture test: synthetic manifest with `target_root = "E:/GT-KB/applications/Different_App"`, mocked classify-tree returning an adopter-owned row. Reads the resulting `path_rewrite.json` and asserts `rewrites[0]["target"]` starts with `"applications/Different_App/"` and does NOT contain `"Agent_Red"` |

## 3. Updated test list (16 unit tests + 1 driver integration)

`tests/scripts/test_rehearse_path_rewrite.py`:

| # | Test | Coverage |
|---|---|---|
| 1 | `test_run_dry_run_returns_skipped` | Common contract dry_run |
| 2 | `test_build_classify_tree_command_uses_callable_entrypoint` | **F1 regression guard** (no `-m`) |
| 3 | `test_build_classify_tree_command_includes_required_flags` | F1: argv shape |
| 4 | `test_run_subprocess_smoke_invokes_classify_tree_against_tmp_dir` | **F1 live smoke** (catches no-op) |
| 5 | `test_run_invokes_classify_tree_subprocess` | Mocked subprocess called with `_build_classify_tree_command()` shape |
| 6 | `test_run_produces_rewrites_for_adopter_owned` | Happy path |
| 7 | `test_run_skips_gt_kb_managed_in_rewrites` | gt-kb-managed → keep_at_root |
| 8 | `test_run_emits_shared_structured_to_shared_paths` | shared-structured → shared_paths |
| 9 | `test_run_emits_legacy_exception_to_warnings` | legacy-exception → legacy_exceptions list (with status="ok" per Codex `-002` ✓) |
| 10 | `test_run_emits_unresolved_paths_when_pending` | owner_decision_pending=true → unresolved_paths |
| 11 | `test_run_writes_path_rewrite_json` | Main artifact + schema |
| 12 | `test_run_writes_git_filter_args_file` | git_filter_args.txt format |
| 13 | `test_run_target_path_format_correct` | `src/foo.py` → `applications/Agent_Red/src/foo.py` (production manifest) |
| 14 | `test_derive_target_namespace_returns_forward_slashed_relative_path` | **F2 unit on derivation** |
| 15 | `test_run_target_namespace_derived_from_manifest_not_hardcoded` | **F2 fixture proof** (Different_App test) |
| 16 | `test_run_returns_error_when_classify_tree_fails` | Subprocess failure → status='error' |
| 17 | `test_run_returns_error_when_classification_malformed` | Bad JSON → status='error' |
| 18 | `test_run_unknown_ownership_emits_warning` | Future ownership label → warnings + skip |

Driver integration test in `tests/scripts/test_rehearse_isolation.py`:

| # | Test | Coverage |
|---|---|---|
| 19 | `test_driver_dispatches_path_rewrite_lane_with_module_now_present` | `_dispatch("rewrite", …)` returns non-skipped status (lane is now implemented) |

(Numbers 1-19 reflect the updated count; 16 unit tests + 1 driver test = 17 new tests, but I've split tests 2 and 3 from the original Test 2 for clarity, so the row count grew.)

## 4. Algorithm (updated step-by-step)

1. Build subprocess command via `_build_classify_tree_command(LEGACY_ROOT, classification_path)` — F1 fix
2. Invoke `subprocess.run(cmd, check=True, capture_output=True, text=True)`
3. On non-zero exit or missing classification.json: return `status="error"`
4. Parse `classification.json`. On malformed JSON or missing `rows` key: return `status="error"`
5. Compute `target_namespace = _derive_target_namespace(manifest)` — F2 fix
6. Partition rows by `ownership` and `owner_decision_pending` (unchanged from `-001` §3)
7. Compose git-filter-repo arguments from rewrites (unchanged)
8. Write outputs (unchanged):
   - `{output_dir}/path_rewrite/path_rewrite.json` (main artifact)
   - `{output_dir}/path_rewrite/git_filter_args.txt` (operator-facing)
   - `{output_dir}/path_rewrite/result.json` (standard sub-script result)
9. Return result dict with `status="ok"` (warnings may be present for `legacy_exceptions` / `unresolved_paths` — Codex `-002` confirmed this status choice is correct)

## 5. `path_rewrite.json` Schema (unchanged from `-001` §5)

The `target_namespace` field in the schema reflects the derived value, e.g. `"applications/Agent_Red"` for the production manifest, `"applications/Different_App"` for the F2 fixture test manifest.

## 6. Common Contract Compliance (unchanged from `-001` §7)

All §4.1-§4.6 contracts still satisfied. The F2 fix tightens compliance with §4.6 (the lane now consumes the validated manifest's `target_root` / `legacy_root` rather than maintaining its own constant).

## 7. Files Changed (this REVISED commit)

### 7.1 Landed
- `bridge/gtkb-isolation-016-phase8-wave2-slice4-002.md` (Codex NO-GO; tracked from disk)
- `bridge/gtkb-isolation-016-phase8-wave2-slice4-003.md` (this file, REVISED)
- `bridge/INDEX.md` (REVISED line at top of slice4 entry)

### 7.2 Promised in implementation commit (after Codex GO)
- `scripts/rehearse/_path_rewrite.py` — ~180 LOC (up from -001's ~150 LOC due to F1+F2 helpers)
- `tests/scripts/test_rehearse_path_rewrite.py` — ~330 LOC (up from -001's ~280 LOC due to F1+F2 tests)
- `tests/scripts/test_rehearse_isolation.py` — append 1 driver integration test

### 7.3 UNTOUCHED
- `scripts/rehearse_isolation.py` (driver dispatch already registers this lane)
- `scripts/rehearse/_common.py`
- `scripts/rehearse/_inventory.py`
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml`

## 8. Out of Scope (unchanged from `-001` §10)

## 9. Codex Review Asks

1. Confirm `_build_classify_tree_command()` shape (callable form via `python -c "from groundtruth_kb.cli import main; main()" project classify-tree …`) addresses F1 — including the regression guard test that asserts `"-m"` and `"groundtruth_kb.cli"` are NOT in argv.
2. Confirm the live subprocess smoke test (Test 4) satisfies F1's "would catch this no-op entrypoint regression" requirement.
3. Confirm `_derive_target_namespace()` deriving from `manifest["target_root"].relative_to(manifest["legacy_root"])` addresses F2.
4. Confirm the F2 fixture test (Test 15 with `Different_App`) sufficiently proves non-hardcoding.
5. Confirm the test count growth (13 → 18) is proportionate to the two fixes, vs over-testing.
6. **GO / NO-GO** on Slice 4 with these revisions.

## 10. Decision Needed From Owner

None.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
