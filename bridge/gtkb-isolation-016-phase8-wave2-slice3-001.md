NEW

# GTKB-ISOLATION-016 Phase 8 Wave 2 — Slice 3: Driver Wire-Up (Implementation Proposal)

**Status:** NEW (implementation proposal awaits Codex GO)
**Date:** 2026-04-26 (S311)
**Author:** Prime Builder (Claude Opus 4.7)
**Work item:** GTKB-ISOLATION-016
**Bridge kind:** implementation_proposal
**Builds on:**
- `bridge/gtkb-isolation-016-phase8-wave2-implementation-004.md` (Wave 2 GO)
- `bridge/gtkb-isolation-016-phase8-wave2-slice1-004.md` (Slice 1 VERIFIED — `_common.py` validation)
- `bridge/gtkb-isolation-016-phase8-wave2-slice2-006.md` (Slice 2 VERIFIED — `_inventory.py` lane)
- `bridge/gtkb-isolation-016-phase8-wave2-slice2-004.md` GO recommendation: "Proceed to the next bridge slice for driver wire-up"

bridge_kind: implementation_proposal
work_item_ids: [GTKB-ISOLATION-016]
target_project: agent-red
implementation_scope: scripts/rehearse_isolation.py + tests

---

## 1. Scope

Wire the driver to actually invoke implemented Wave 2 lanes. With Slice 1 (validation) and Slice 2 (inventory lane) VERIFIED, the driver is the only thing still in Wave 1 stub mode.

Three changes:

1. **Switch manifest load to `wave=2`:** `load_manifest(args.manifest)` becomes `load_manifest(args.manifest, wave=2)` — activates the Slice 1 M1-M5 validation rules.
2. **Construct per-run `output_dir`:** append ISO timestamp to manifest's `output_dir` so each rehearsal run lives in its own sandbox directory (`C:/temp/agent-red-rehearsal-{ISO_TIMESTAMP}/`).
3. **Implement `_dispatch()`:** import the lane module + invoke its `run(manifest, output_dir, *, dry_run, inventory_root=None)` per Wave 2 -003 §4.1 contract. For `inventory`, this invokes the real `rehearse._inventory.run()`. For Stages B-D lanes (10 modules) that haven't been implemented yet, the dispatcher recognizes the `ModuleNotFoundError` / `AttributeError` and emits a structured "not yet implemented" stub result.

Out of scope: any Stage B-D lane body. Each is its own future bridge.

## 2. Code Changes — `scripts/rehearse_isolation.py`

### 2.1 `load_manifest()` call

```python
# Before:
manifest = load_manifest(args.manifest)

# After:
manifest = load_manifest(args.manifest, wave=2)
```

### 2.2 Output dir construction

Add a helper `_resolve_output_dir(manifest: dict, override: Path | None) -> Path`:

```python
import time

def _resolve_output_dir(manifest: dict, override: Path | None = None) -> Path:
    """Resolve the per-run output_dir.

    If --output-dir is passed, use it verbatim (advanced override). Otherwise
    append an ISO timestamp to manifest.output_dir for run isolation.
    """
    if override is not None:
        return override
    base = manifest["output_dir"]  # validated by load_manifest(wave=2)
    timestamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    return Path(f"{base}-{timestamp}")
```

Add `--output-dir` to the argparse parser (optional override; default None → timestamped).

### 2.3 `_dispatch()` function

```python
import importlib
from typing import Any

def _dispatch(
    phase_name: str,
    manifest: dict[str, Any],
    output_dir: Path,
    *,
    dry_run: bool,
) -> dict[str, Any]:
    """Look up the lane in DISPATCH_TABLE and invoke its run().

    Returns the lane's standard result dict per Wave 2 -003 §4.1. If the
    lane module or its run() function does not yet exist (Stages B-D not
    yet implemented), returns a structured 'not yet implemented' result
    with status='skipped' rather than raising.
    """
    for cli_name, module_path, func_name in DISPATCH_TABLE:
        if cli_name == phase_name:
            try:
                mod = importlib.import_module(module_path)
                fn = getattr(mod, func_name)
            except (ModuleNotFoundError, AttributeError):
                return {
                    "status": "skipped",
                    "output_files": [],
                    "metrics": {},
                    "warnings": [
                        f"lane {phase_name!r} not yet implemented "
                        f"({module_path}.{func_name} unavailable); "
                        f"future Wave 2 slice will land it"
                    ],
                }
            return fn(manifest, output_dir, dry_run=dry_run)
    raise ValueError(f"unknown phase: {phase_name}")
```

### 2.4 `main()` integration

Replace the stub print block at `scripts/rehearse_isolation.py:135-141`:

```python
output_dir = _resolve_output_dir(manifest, getattr(args, "output_dir", None))

selected = (
    DISPATCH_TABLE
    if args.phase == "all"
    else tuple(entry for entry in DISPATCH_TABLE if entry[0] == args.phase)
)

print(f"rehearse_isolation: Wave 2 dispatch — {len(selected)} phase(s)")
print(f"  output_dir: {output_dir}")
print(f"  manifest:   {args.manifest}")

results: dict[str, dict[str, Any]] = {}
any_error = False
for cli_name, _, _ in selected:
    print(f"  -> {cli_name} ...", end="", flush=True)
    result = _dispatch(cli_name, manifest, output_dir, dry_run=args.dry_run)
    results[cli_name] = result
    print(f" {result['status']}")
    if result["status"] == "error":
        any_error = True
        for w in result["warnings"]:
            print(f"     WARNING: {w}", file=sys.stderr)

# Write a run-level summary to output_dir
if any(r["status"] == "ok" for r in results.values()):
    summary_path = output_dir / "run-summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(
        json.dumps({
            "run_started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "manifest_path": str(args.manifest),
            "phase_requested": args.phase,
            "results": results,
        }, indent=2),
        encoding="utf-8",
    )
    print(f"  summary: {summary_path}")

return EXIT_OK if not any_error else EXIT_REFUSE
```

Adds `import json` + `import time` at the top (currently missing).

## 3. Tests — additions to `tests/scripts/test_rehearse_isolation.py`

All new tests use `tmp_path` + `monkeypatch`; no live-root walks. Per Codex Wave 2 -004 GO and Slice 2 -004 GO, this discipline is now load-bearing.

| # | Test | Coverage |
|---|---|---|
| 52 | `test_main_loads_manifest_at_wave2` | Mock `load_manifest`; assert called with `wave=2` |
| 53 | `test_main_constructs_timestamped_output_dir` | Verify output_dir has manifest_output_dir + ISO timestamp suffix |
| 54 | `test_output_dir_override_via_cli_arg` | `--output-dir <path>` bypasses timestamp construction |
| 55 | `test_dispatch_inventory_invokes_real_lane` | Patch `_inventory.run` → mock; `--phase inventory` invokes mock with correct args |
| 56 | `test_dispatch_unimplemented_lane_returns_skipped_status` | `--phase rewrite` (lane module doesn't exist) returns status='skipped' with warning |
| 57 | `test_dispatch_unknown_phase_raises_valueerror` | `_dispatch("nonexistent", ...)` raises ValueError |
| 58 | `test_phase_all_iterates_full_dispatch_table` | `--phase all` calls _dispatch 11 times in table order |
| 59 | `test_run_summary_json_written_when_any_lane_ok` | Patch `_inventory.run` to return ok; summary.json appears in output_dir |
| 60 | `test_main_returns_exit_refuse_on_lane_error` | Patch `_inventory.run` to return error; main() returns EXIT_REFUSE |
| 61 | `test_main_returns_exit_ok_when_all_lanes_skipped` | All lanes skipped (none implemented yet → don't fail just because the rest aren't built); EXIT_OK |

10 new tests. **0 existing tests modified or deleted.**

Note on test 61: Wave 2 sequencing means lanes 2-11 don't yet exist; running `--phase all` today would invoke inventory (real) + 10 stubs. That should NOT fail the run, otherwise the driver would be unusable until every lane is implemented. The "skipped" status distinguishes "not yet implemented" from "tried and failed" — only the latter makes main() return EXIT_REFUSE.

## 4. Files Changed

### 4.1 Modified
- `scripts/rehearse_isolation.py` — switch load_manifest to wave=2; add `_resolve_output_dir()` + `_dispatch()` + `--output-dir` arg; replace stub print block with real dispatch loop + run-summary.json emission

### 4.2 Modified (additive)
- `tests/scripts/test_rehearse_isolation.py` — append 10 new tests for wave=2 load, output_dir construction, dispatch routing, and exit semantics

### 4.3 Untouched
- `scripts/rehearse/_common.py` (no changes; Slice 1 + Slice 2 contract suffices)
- `scripts/rehearse/_inventory.py` (Slice 2 implementation suffices; driver just invokes its existing `run()`)
- All existing 51 driver tests (preserved)

## 5. Backward Compatibility

| Concern | Disposition |
|---|---|
| Existing 51 `test_rehearse_isolation.py` tests | Most are about `validate_target_root()` and `hash_set_walk()` (Wave 1 helpers, untouched). Driver-specific tests that verify the stub print output (`test_dispatch_table_*`) check the dispatch table contents, not the dispatch behavior — those still pass since the table itself is unchanged. |
| Wave 1 driver invocation | Still works: `python scripts/rehearse_isolation.py --phase inventory` now actually runs the inventory lane against the live root (or whatever the manifest specifies). Operator-driven workflow unchanged. |
| `--phase` choices | Same enum; behavior of `verify` and `all` updated; behavior of single-phase invocations matches the lane's `run()` semantics. |
| Manifest validation | Now activates Wave 2 rules; the production manifest at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml` was committed to pass `wave=2` (Slice 1 -003 commit `1e063533`), so this works without manifest changes. |

## 6. Implementation Order

1. Add imports (`importlib`, `json`, `time`)
2. Add `_resolve_output_dir()` helper
3. Add `--output-dir` argparse argument (optional, default None)
4. Add `_dispatch()` function
5. Switch `load_manifest()` call to `wave=2`
6. Replace stub print block in `main()` with dispatch loop + run-summary.json emission
7. Add 10 new tests
8. Run full pytest on `tests/scripts/test_rehearse_*.py`
9. Run release-candidate gate

## 7. Codex Review Asks

1. Confirm the `_dispatch()` design (try-import + AttributeError → status='skipped') is the right pattern for Stage B-D lanes that don't yet exist (vs hard-failing the run).
2. Confirm per-run timestamped `output_dir` (`{manifest_output_dir}-{ISO_TS}`) is the right shape vs requiring the operator to specify each run's directory.
3. Confirm the run-summary.json shape (timestamp + manifest_path + phase + per-lane results dict) is sufficient for Wave 3 verification matrix to consume later.
4. Confirm `EXIT_REFUSE` on lane error vs `EXIT_OK` when all are skipped is the right distinction (i.e., "not yet implemented" should NOT block runs that successfully execute the lanes that do exist).
5. Confirm the 10 new tests cover wave=2 manifest load, output_dir construction, dispatch routing, and exit semantics.
6. Confirm 0 existing tests modified/deleted; the 51 existing tests remain green.
7. **GO / NO-GO** on Slice 3.

## 8. Decision Needed From Owner

None — Wave 2 GO + Slice 1 + Slice 2 cover this slice's authority.

## 9. Sequencing After This Slice

After Slice 3 VERIFIED:
- The driver is fully Wave-2-functional. Operators can run `python scripts/rehearse_isolation.py --phase inventory` and get a real inventory + runtime manifest in a per-run sandbox.
- **Stages B-D (lanes 2-11)** become independently implementable in any order. Each lane is its own bridge proposal + post-impl + VERIFIED. Approximately 10 sub-bridges to close Wave 2.
- After all Wave 2 lanes ship, **Wave 3 verification matrix** (`--phase verify`) becomes the next concern (separate scoping).
- After Wave 2 + Wave 3 close, **ISOLATION-017 Phase 9 productization** begins.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
