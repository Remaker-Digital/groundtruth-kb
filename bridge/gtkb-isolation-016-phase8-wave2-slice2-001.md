NEW

# GTKB-ISOLATION-016 Phase 8 Wave 2 — Slice 2: `_inventory.py` Implementation (Implementation Proposal)

**Status:** NEW (implementation proposal awaiting Codex GO; explicitly depends on Slice 1 VERIFIED)
**Date:** 2026-04-26 (S311)
**Author:** Prime Builder (Claude Opus 4.7)
**Work item:** GTKB-ISOLATION-016
**Bridge kind:** implementation_proposal
**Builds on:**
- `bridge/gtkb-isolation-016-phase8-wave2-implementation-004.md` (GO scoping)
- `bridge/gtkb-isolation-016-phase8-wave2-slice1-001.md` (Slice 1 NEW; this slice depends on its VERIFIED)

bridge_kind: implementation_proposal
work_item_ids: [GTKB-ISOLATION-016]
spec_ids: []
target_project: agent-red
implementation_scope: scripts/rehearse/_inventory.py + scripts/rehearse/_common.py (small extension) + tests

---

## 0. Dependency Statement

This slice's implementation cannot land until Slice 1 (`_common.py` validation) is VERIFIED. Codex may review and GO this slice in parallel with Slice 1 review (the design doesn't change), but actual code implementation waits for Slice 1 VERIFIED so the validation contract is in place.

## 1. Scope

Slice 2 implements `scripts/rehearse/_inventory.py` (the only Stage A leaf lane in Wave 2's dependency graph) and a small `_common.py` extension (`is_runtime_manifest` kwarg for the M5 enforcement).

`_inventory.py` has three responsibilities, executed in order:

1. **File inventory:** walk `LEGACY_ROOT` using `hash_set_walk()` (existing `_common.py` helper); produce `inventory.json` with `{path → sha256, size, mtime}` map plus aggregate stats
2. **Authority matrix parsing:** read `phase_1_authority_matrix_path` (markdown); extract rows from the "Preliminary Authority Matrix" section table
3. **Runtime manifest construction:** copy source manifest + populate `[surface_treatments]` with one entry per parsed matrix row + write runtime manifest to `output_dir/runtime-manifest.toml` + re-validate via `load_manifest(runtime_path, wave=2, is_runtime_manifest=True)`

## 2. Code Changes

### 2.1 `scripts/rehearse/_common.py` extension (small)

Add `is_runtime_manifest` keyword to `load_manifest()` signature:

```python
def load_manifest(path: Path, *, wave: int = 1, is_runtime_manifest: bool = False) -> dict[str, Any]:
```

Extend M5 enforcement (added in Slice 1) to enforce non-empty `surface_treatments` when `is_runtime_manifest=True`:

```python
# In the M5 block added by Slice 1, replace the "acceptable for source manifest"
# branch with:
if surface_treatments is None or (isinstance(surface_treatments, dict) and not surface_treatments):
    if is_runtime_manifest:
        raise ManifestValidationError(
            "M5: runtime manifest requires non-empty surface_treatments; "
            "Wave 2 lane 1 (_inventory.py) must populate it from the "
            "authority matrix before downstream lanes can consume it."
        )
    # Source manifest: empty acceptable
    data["surface_treatments"] = {} if surface_treatments is None else surface_treatments
elif not isinstance(surface_treatments, dict):
    raise ManifestValidationError(
        "M5: manifest.surface_treatments must be a TOML table when present."
    )
```

This is the only `_common.py` change in Slice 2. ~10 lines.

### 2.2 New module: `scripts/rehearse/_inventory.py`

Implements the Wave 2 Stage A leaf lane. Conforms to the common sub-script signature from Wave 2 -003 §4.1:

```python
"""Wave 2 lane 1 (Stage A leaf): file inventory + authority-matrix parse +
runtime manifest construction.

Per bridge/gtkb-isolation-016-phase8-wave2-slice2-001.md.

Authority: ADR-ISOLATION-APPLICATION-PLACEMENT-001 (upstream affa5a0567...);
Wave 2 GO at bridge/gtkb-isolation-016-phase8-wave2-implementation-004.md.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any

from rehearse._common import (
    LEGACY_ROOT,
    ManifestValidationError,
    hash_set_walk,
    load_manifest,
)


_PRELIM_MATRIX_HEADER_PATTERN = re.compile(
    r"^##\s+Preliminary Authority Matrix\s*$", re.MULTILINE
)
_NEXT_SECTION_PATTERN = re.compile(r"^##\s+\S", re.MULTILINE)
_TABLE_ROW_PATTERN = re.compile(r"^\|\s*([^|]+?)\s*\|")  # Captures first cell


def _slugify(name: str) -> str:
    """Convert a surface name to a stable surface_id slug."""
    s = re.sub(r"[`*_]", "", name)               # strip markdown decorations
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-")
    return s.lower() or "unnamed-surface"


def _parse_authority_matrix(matrix_path: Path) -> list[dict[str, str]]:
    """Parse the Preliminary Authority Matrix markdown table.

    Returns a list of dicts, one per matrix row, with keys:
      surface, current_evidence, target_authority,
      app_subject_access, gtkb_subject_access, required_decision_or_verification.

    Skips the header row and the alignment row. Stops at the next ## section.
    Tolerant to whitespace variation; does NOT attempt to handle escaped pipes
    inside cells (the matrix avoids them).
    """
    content = matrix_path.read_text(encoding="utf-8")
    header_match = _PRELIM_MATRIX_HEADER_PATTERN.search(content)
    if not header_match:
        raise ManifestValidationError(
            f"_inventory: 'Preliminary Authority Matrix' section not found in "
            f"{matrix_path}. Authority matrix may have been restructured; "
            f"update _PRELIM_MATRIX_HEADER_PATTERN or fix the matrix."
        )
    section_start = header_match.end()
    next_section = _NEXT_SECTION_PATTERN.search(content, pos=section_start)
    section_end = next_section.start() if next_section else len(content)
    section = content[section_start:section_end]

    rows: list[dict[str, str]] = []
    for line in section.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 6:
            continue  # malformed or non-data row
        if cells[0] in {"Surface", "---", ""} or set(cells[0]) <= {"-", " "}:
            continue  # header / alignment / blank
        rows.append({
            "surface": cells[0],
            "current_evidence": cells[1],
            "target_authority": cells[2],
            "app_subject_access": cells[3],
            "gtkb_subject_access": cells[4],
            "required_decision_or_verification": cells[5],
        })
    if not rows:
        raise ManifestValidationError(
            f"_inventory: no surface rows extracted from "
            f"'Preliminary Authority Matrix' in {matrix_path}. "
            f"Table format may have changed."
        )
    return rows


def _walk_inventory(root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    """Walk root, return inventory dict with per-file hash + aggregate stats."""
    excluded = set(manifest.get("excluded_paths", []))
    excluded_top = frozenset(
        e.rstrip("/").split("/")[0] for e in excluded
    ) | frozenset({".git", "__pycache__", "node_modules", ".groundtruth-chroma", ".tmp.driveupload"})
    hashes = hash_set_walk(root, ignored_top_level=excluded_top)
    total_size = 0
    for rel in hashes:
        try:
            total_size += (root / rel).stat().st_size
        except OSError:
            pass
    return {
        "root": str(root),
        "file_count": len(hashes),
        "total_bytes": total_size,
        "files": hashes,
        "ignored_top_level": sorted(excluded_top),
        "walked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def _build_runtime_manifest(
    source_manifest: dict[str, Any],
    surface_rows: list[dict[str, str]],
) -> dict[str, Any]:
    """Build runtime manifest: source + populated surface_treatments."""
    runtime = dict(source_manifest)  # shallow copy of TOML-parsed dict
    runtime["surface_treatments"] = {
        _slugify(row["surface"]): row for row in surface_rows
    }
    runtime["_inventory_metadata"] = {
        "populated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "matrix_source": source_manifest.get("phase_1_authority_matrix_path"),
        "row_count": len(surface_rows),
    }
    return runtime


def _write_runtime_manifest(runtime: dict[str, Any], output_path: Path) -> None:
    """Write runtime manifest as TOML.

    Uses a minimal hand-rolled TOML emitter for the structure produced by
    _build_runtime_manifest; avoids a new dependency. If complexity grows
    we can switch to `tomli_w` (separate proposal).
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = ["# Runtime manifest produced by Wave 2 lane 1 (_inventory.py).\n"]
    # Top-level scalar fields
    for key, value in runtime.items():
        if isinstance(value, dict):
            continue  # tables emitted later
        if isinstance(value, list):
            list_repr = ", ".join(f'"{v}"' for v in value)
            lines.append(f"{key} = [{list_repr}]\n")
        else:
            lines.append(f'{key} = "{value}"\n')
    # Tables
    for table_name, table in runtime.items():
        if not isinstance(table, dict):
            continue
        if table_name == "surface_treatments":
            for surface_id, fields in table.items():
                lines.append(f"\n[surface_treatments.{surface_id}]\n")
                for k, v in fields.items():
                    escaped = str(v).replace('"', '\\"')
                    lines.append(f'{k} = "{escaped}"\n')
        else:
            lines.append(f"\n[{table_name}]\n")
            for k, v in table.items():
                lines.append(f'{k} = "{v}"\n')
    output_path.write_text("".join(lines), encoding="utf-8")


def run(manifest: dict[str, Any], output_dir: Path, *, dry_run: bool = False) -> dict[str, Any]:
    """Wave 2 Stage A leaf lane: file inventory + matrix parse + runtime manifest.

    Returns result dict per Wave 2 -003 §4.1 contract:
        {"status": "ok"|"error"|"skipped", "output_files": [...],
         "metrics": {...}, "warnings": [...]}
    """
    warnings: list[str] = []
    output_files: list[Path] = []

    if dry_run:
        return {
            "status": "skipped",
            "output_files": [],
            "metrics": {"reason": "dry_run"},
            "warnings": [],
        }

    # 1. File inventory
    try:
        inventory = _walk_inventory(LEGACY_ROOT, manifest)
    except OSError as exc:
        return {"status": "error", "output_files": [], "metrics": {},
                "warnings": [f"file_walk_failed: {exc}"]}

    inventory_path = output_dir / "inventory.json"
    inventory_path.parent.mkdir(parents=True, exist_ok=True)
    inventory_path.write_text(json.dumps(inventory, indent=2), encoding="utf-8")
    output_files.append(inventory_path)

    # 2. Authority matrix parse
    matrix_path = LEGACY_ROOT / manifest["phase_1_authority_matrix_path"]
    try:
        surface_rows = _parse_authority_matrix(matrix_path)
    except ManifestValidationError as exc:
        return {"status": "error", "output_files": [str(p) for p in output_files],
                "metrics": {}, "warnings": [str(exc)]}

    # 3. Runtime manifest construction + write + re-validate
    runtime = _build_runtime_manifest(manifest, surface_rows)
    runtime_path = output_dir / "runtime-manifest.toml"
    _write_runtime_manifest(runtime, runtime_path)
    output_files.append(runtime_path)

    try:
        load_manifest(runtime_path, wave=2, is_runtime_manifest=True)
    except ManifestValidationError as exc:
        return {"status": "error", "output_files": [str(p) for p in output_files],
                "metrics": {"surface_count": len(surface_rows)},
                "warnings": [f"runtime_manifest_revalidation_failed: {exc}"]}

    return {
        "status": "ok",
        "output_files": [str(p) for p in output_files],
        "metrics": {
            "file_count": inventory["file_count"],
            "total_bytes": inventory["total_bytes"],
            "surface_count": len(surface_rows),
        },
        "warnings": warnings,
    }
```

## 3. Tests — `tests/scripts/test_rehearse_inventory.py` (NEW)

10 tests covering the three responsibilities + integration:

1. `test_walk_inventory_excludes_dot_git_and_node_modules` — fixture tree includes ignored top-level dirs; result excludes them
2. `test_walk_inventory_excludes_manifest_excluded_paths` — fixture manifest has `excluded_paths`; result excludes them
3. `test_walk_inventory_handles_unreadable_file` — fixture has read-permission-denied file; walk continues without the file
4. `test_parse_authority_matrix_extracts_preliminary_table_rows` — fixture markdown with the matrix shape; assert ≥10 rows extracted with all 6 fields
5. `test_parse_authority_matrix_missing_section_raises` — fixture markdown without "Preliminary Authority Matrix" header; raises `ManifestValidationError`
6. `test_parse_authority_matrix_empty_table_raises` — fixture markdown with header but no data rows; raises `ManifestValidationError`
7. `test_build_runtime_manifest_populates_surface_treatments` — given source manifest + 3 fake matrix rows; result has `surface_treatments` with 3 entries keyed by slugified surface name
8. `test_write_runtime_manifest_produces_loadable_toml` — write + re-read via `tomllib`; round-trip matches input dict
9. `test_run_happy_path_against_real_matrix` — uses the real production manifest + matrix; assert status=ok, all 3 output files exist, surface_count > 0
10. `test_run_runtime_manifest_revalidation_failure_reports_error` — fixture matrix with no rows; `_inventory.run()` returns status='error' with the correct warning, does NOT raise

Plus 2 tests for the Slice 1 `_common.py` extension (`is_runtime_manifest`):

11. `test_load_manifest_runtime_empty_surface_treatments_rejected` — runtime manifest with empty `[surface_treatments]` + `is_runtime_manifest=True` raises `ManifestValidationError`
12. `test_load_manifest_runtime_populated_surface_treatments_accepted` — runtime manifest with populated table + `is_runtime_manifest=True` passes

Total: 12 tests in this slice. **0 existing tests modified or deleted.**

## 4. Files Changed

### 4.1 New
- `scripts/rehearse/_inventory.py` (~180 LOC)
- `tests/scripts/test_rehearse_inventory.py` (12 tests)

### 4.2 Modified (small extension)
- `scripts/rehearse/_common.py` — add `is_runtime_manifest` kwarg to `load_manifest()`; extend M5 to enforce non-empty surface_treatments for runtime manifest (~10 LOC)

### 4.3 Untouched
- `scripts/rehearse_isolation.py` (driver still uses Wave 1 default; Slice 3 will switch dispatch to invoke `_inventory.run()` after this slice VERIFIED)
- All other rehearse modules
- All existing tests

## 5. Backward Compatibility

The `is_runtime_manifest` keyword defaults to `False`, preserving Slice 1's behavior exactly. Existing call sites (Wave 1 driver, Slice 1 tests) continue to pass without modification. The runtime-manifest enforcement only fires when an explicit caller passes `True` — currently only `_inventory.run()` itself.

## 6. Implementation Order

1. Add `is_runtime_manifest` kwarg + M5 extension to `_common.py`
2. Add tests 11-12 to verify the M5 extension
3. Implement `_inventory.py` module body (helpers first, then `run()`)
4. Add tests 1-10
5. Run full pytest on `tests/scripts/test_rehearse_*.py`
6. Run release-candidate gate

Each step is independently testable.

## 7. Codex Review Asks

1. Confirm splitting Slice 1 (`_common.py` validation) and Slice 2 (`_inventory.py` + small `_common.py` extension for `is_runtime_manifest`) is the right granularity vs bundling them.
2. Confirm the markdown matrix parser approach in §2.2 (`_parse_authority_matrix`) is acceptable given the matrix is a planning markdown document, not a structured TOML/YAML (the structured form is a future work item per the matrix doc itself).
3. Confirm the surface_treatments schema (6 fields per matrix row, slugified surface_id) matches what downstream lanes (Stages B/C/D) need to consume. If lanes need additional fields, propose the matrix document extension separately rather than inventing fields here.
4. Confirm the hand-rolled TOML emitter in `_write_runtime_manifest` is acceptable for the schema produced (no nested-table-of-tables; only string scalars and one nested table). Alternative: add `tomli_w` as a project dependency.
5. Confirm 12 tests cover the three responsibilities (walk, parse, runtime manifest) + integration + the M5 runtime-manifest enforcement.
6. Confirm `_inventory.run()` returns the expected sub-script result dict shape per Wave 2 -003 §4.1.
7. **GO / NO-GO** on Slice 2.

## 8. Decision Needed From Owner

None — Slice 2 inherits Wave 2 GO + Slice 1 NEW status. After Slice 1 VERIFIED + Slice 2 GO, implementation lands as a single commit since the `_common.py` change is small and tightly coupled to `_inventory.py`'s contract.

## 9. Sequencing After This Slice

Slice 2 VERIFIED unblocks:
- **Slice 3 (driver wire-up):** modify `scripts/rehearse_isolation.py` dispatch table to actually invoke `rehearse._inventory:run` (currently a stub)
- **Stages B-D (lanes 2-11):** can begin in parallel implementation tracks once driver wires Stage A

Wave 2 completion estimated at 4-6 more sub-bridges after Slice 2 lands (some Stage B lanes bundle naturally; Stage C and D each their own bridge).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
