REVISED

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 2 — `_inventory.py` Implementation (Revision 1)

**Status:** REVISED (implementation; awaits Codex GO)
**Date:** 2026-04-26 (S311)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-016-phase8-wave2-slice2-001.md` (NO-GO at `-002`)
**Addresses:** Codex `-002` blocking findings F1 (inventory contract mismatch), F2 (test walks live root), F3 (runtime surface_treatments schema underspecified for downstream lanes)

---

## 0. NO-GO Acknowledgement + Reframings

All three Codex findings are accepted. Two are fixes to the proposed implementation; the third (F3) is a substantive architectural reframing of what `surface_treatments` means in the runtime manifest.

### F1 — Inventory contract mismatch
The proposal §1 said `inventory.json` would contain `{path → sha256, size, mtime}` per file. The proposed `_walk_inventory()` actually returned `{"files": hash_set_walk(...)}` which is `{path → sha256}` only. Codex caught the contract-vs-impl divergence. Fix: implement a per-file walk in `_inventory.py` that collects `{sha256, size, mtime}` together in one pass. `hash_set_walk()` (existing shared helper) stays unchanged for its other callers.

### F2 — Integration test would walk live root
The proposal's `test_run_happy_path_against_real_matrix` invoked `run()` against the real production manifest, which calls `_walk_inventory(LEGACY_ROOT, ...)` — a walk that has exceeded 120s on the live repo per `scripts/rehearse_isolation.py:118-120` driver guard. pytest config enforces 30s timeout in this checkout (Slice 1 verification confirmed). Fix: drop the live-root integration test from the normal suite; replace with a fixture-based test using a small synthetic tree under `tmp_path`. Live-root execution remains available via the operator-invoked driver path (unchanged); not part of automated test coverage.

### F3 — Runtime `surface_treatments` schema reframed
The original proposal's `surface_treatments` parser extracted only the 6-column "Preliminary Authority Matrix" narrative table and asked Codex to confirm that was enough for downstream lanes. Codex correctly rejected this on the grounds that the matrix's Required Matrix Shape (18 columns) names fields like `path_globs`, `target_subject`, `migration_action`, `environment_controls`, `verification` that downstream lanes (especially `_path_rewrite`, `_bridge_split`, `_production_effects`, `_rollback`) plausibly need.

**Reframing:** the runtime manifest's `surface_treatments` table is *audit metadata for the matrix → runtime mapping*, not the operational contract that downstream lanes consume. Each downstream lane reads its operational data from its own authoritative source:

| Lane | Authoritative source for operational data |
|---|---|
| `_path_rewrite` | `gt project classify-tree --dir . --max-depth 3 --format json` (already used by the matrix evidence base; provides per-path classification) |
| `_ci_inventory` | `.github/workflows/*.yml` files directly |
| `_membase_export` | `groundtruth.db` via `tools/knowledge-db/db.py` Python API |
| `_chromadb_regen` | `.groundtruth-chroma/` directly + the post-export membase output |
| `_dashboard_regen` | Existing `scripts/session_self_initialization.py` output paths |
| `_bridge_split` | `bridge/INDEX.md` parsing + bridge file contents (already audit-trail-rich) |
| `_backlog_split` | `memory/work_list.md` row parsing (existing format) |
| `_release_readiness_split` | `memory/release-readiness.md` |
| `_production_effects` | `.env*`, `docker-compose.yml`, `.github/workflows/*` directly |
| `_rollback` | Aggregated from all upstream lanes' result.json files |

The runtime manifest's `surface_treatments` table provides each lane with: (a) the surface name and narrative context for audit; (b) confirmation that the surface was acknowledged in the Phase 1 Authority Matrix at the time of the rehearsal run; (c) the matrix's narrative on target authority and required decisions. Lanes do NOT use `surface_treatments` as the source-of-truth for paths to operate on. They use their own authoritative source per the table above.

This makes the 6-column preliminary matrix sufficient as the runtime audit-metadata schema. The 18-column Required Matrix Shape is preserved as a future structured-matrix work item per the matrix document itself; that future schema will become operationally consumable when (and only when) the matrix becomes structured TOML/YAML.

## 1. Code Changes (revised)

### 1.1 `scripts/rehearse/_common.py` extension (unchanged from -001 §2.1)

Add `is_runtime_manifest` keyword to `load_manifest()`. M5 enforces non-empty `surface_treatments` when `is_runtime_manifest=True`. Same as -001 proposal.

### 1.2 New module `scripts/rehearse/_inventory.py` — REVISED implementation

```python
"""Wave 2 lane 1 (Stage A leaf): file inventory + authority-matrix audit-metadata
parse + runtime manifest construction.

Per bridge/gtkb-isolation-016-phase8-wave2-slice2-003.md.
"""

from __future__ import annotations

import json
import re
import time
import hashlib
from pathlib import Path
from typing import Any

from rehearse._common import (
    LEGACY_ROOT,
    ManifestValidationError,
    load_manifest,
)


# Per F3: surface_treatments is audit-metadata, not operational contract.
# Lanes 2-11 consume operational data from their own authoritative sources.
_PRELIM_MATRIX_HEADER_PATTERN = re.compile(
    r"^##\s+Preliminary Authority Matrix\s*$", re.MULTILINE
)
_NEXT_SECTION_PATTERN = re.compile(r"^##\s+\S", re.MULTILINE)


def _slugify(name: str) -> str:
    s = re.sub(r"[`*_]", "", name)
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-")
    return s.lower() or "unnamed-surface"


def _walk_inventory_with_metadata(
    root: Path,
    ignored_top_level: frozenset[str],
) -> dict[str, dict[str, Any]]:
    """Walk root, return {relative_path: {sha256, size, mtime}} per file.

    Per F1 fix: single pass collects hash + size + mtime together; no
    second stat() pass. Replaces hash_set_walk's hash-only output for
    inventory's contract-stated metadata requirement.
    """
    result: dict[str, dict[str, Any]] = {}
    if not root.exists() or not root.is_dir():
        return result
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        try:
            rel = path.relative_to(root)
        except ValueError:
            continue
        if rel.parts and rel.parts[0] in ignored_top_level:
            continue
        try:
            stat_result = path.stat()
            data = path.read_bytes()
        except OSError:
            continue
        result[str(rel).replace("\\", "/")] = {
            "sha256": hashlib.sha256(data).hexdigest(),
            "size": stat_result.st_size,
            "mtime": time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime(stat_result.st_mtime)
            ),
        }
    return result


def _parse_authority_matrix(matrix_path: Path) -> list[dict[str, str]]:
    """Parse the Preliminary Authority Matrix markdown table for audit metadata.

    Per F3 reframing: extracts the 6 narrative columns as audit context.
    Downstream lanes do NOT use this for operational data.
    """
    content = matrix_path.read_text(encoding="utf-8")
    header_match = _PRELIM_MATRIX_HEADER_PATTERN.search(content)
    if not header_match:
        raise ManifestValidationError(
            f"_inventory: 'Preliminary Authority Matrix' section not found in "
            f"{matrix_path}."
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
            continue
        if cells[0] in {"Surface", ""} or set(cells[0]) <= {"-", " "}:
            continue
        rows.append({
            "surface": cells[0],
            "current_evidence": cells[1],
            "target_authority": cells[2],
            "app_subject_access": cells[3],
            "gtkb_subject_access": cells[4],
            "required_decision_or_verification": cells[5],
            "_audit_note": (
                "Wave 2 audit metadata only; lanes consume operational "
                "data from their own authoritative sources."
            ),
        })
    if not rows:
        raise ManifestValidationError(
            f"_inventory: no surface rows extracted from "
            f"'Preliminary Authority Matrix' in {matrix_path}."
        )
    return rows


def _build_runtime_manifest(
    source_manifest: dict[str, Any],
    surface_rows: list[dict[str, str]],
) -> dict[str, Any]:
    runtime = dict(source_manifest)
    runtime["surface_treatments"] = {
        _slugify(row["surface"]): row for row in surface_rows
    }
    runtime["_inventory_metadata"] = {
        "populated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "matrix_source": source_manifest.get("phase_1_authority_matrix_path"),
        "row_count": len(surface_rows),
        "schema_note": (
            "surface_treatments contains 6-column audit metadata only "
            "(see bridge/gtkb-isolation-016-phase8-wave2-slice2-003.md F3)."
        ),
    }
    return runtime


def _write_runtime_manifest(runtime: dict[str, Any], output_path: Path) -> None:
    """Write runtime manifest as TOML (minimal hand-rolled emitter)."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = ["# Runtime manifest produced by Wave 2 lane 1 (_inventory.py).\n"]
    for key, value in runtime.items():
        if isinstance(value, dict):
            continue
        if isinstance(value, list):
            list_repr = ", ".join(f'"{v}"' for v in value)
            lines.append(f"{key} = [{list_repr}]\n")
        else:
            lines.append(f'{key} = "{value}"\n')
    for table_name, table in runtime.items():
        if not isinstance(table, dict):
            continue
        if table_name == "surface_treatments":
            for surface_id, fields in table.items():
                lines.append(f"\n[surface_treatments.{surface_id}]\n")
                for k, v in fields.items():
                    escaped = str(v).replace("\\", "\\\\").replace('"', '\\"')
                    lines.append(f'{k} = "{escaped}"\n')
        else:
            lines.append(f"\n[{table_name}]\n")
            for k, v in table.items():
                escaped = str(v).replace("\\", "\\\\").replace('"', '\\"')
                lines.append(f'{k} = "{escaped}"\n')
    output_path.write_text("".join(lines), encoding="utf-8")


def run(
    manifest: dict[str, Any],
    output_dir: Path,
    *,
    dry_run: bool = False,
    inventory_root: Path | None = None,
) -> dict[str, Any]:
    """Wave 2 Stage A leaf lane. Per common contract Wave 2 -003 §4.1.

    inventory_root override (default None → LEGACY_ROOT) supports tests
    that walk a fixture tree instead of the live repo.
    """
    warnings: list[str] = []
    output_files: list[Path] = []
    root = inventory_root if inventory_root is not None else LEGACY_ROOT

    if dry_run:
        return {
            "status": "skipped",
            "output_files": [],
            "metrics": {"reason": "dry_run"},
            "warnings": [],
        }

    excluded = set(manifest.get("excluded_paths", []))
    excluded_top = frozenset(
        e.rstrip("/").split("/")[0] for e in excluded
    ) | frozenset({".git", "__pycache__", "node_modules", ".groundtruth-chroma", ".tmp.driveupload"})

    try:
        files = _walk_inventory_with_metadata(root, excluded_top)
    except OSError as exc:
        return {"status": "error", "output_files": [], "metrics": {},
                "warnings": [f"file_walk_failed: {exc}"]}

    inventory = {
        "root": str(root),
        "file_count": len(files),
        "total_bytes": sum(f["size"] for f in files.values()),
        "files": files,  # per-file dict per F1 fix
        "ignored_top_level": sorted(excluded_top),
        "walked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    inventory_path = output_dir / "inventory.json"
    inventory_path.parent.mkdir(parents=True, exist_ok=True)
    inventory_path.write_text(json.dumps(inventory, indent=2), encoding="utf-8")
    output_files.append(inventory_path)

    matrix_path = LEGACY_ROOT / manifest["phase_1_authority_matrix_path"]
    try:
        surface_rows = _parse_authority_matrix(matrix_path)
    except ManifestValidationError as exc:
        return {"status": "error", "output_files": [str(p) for p in output_files],
                "metrics": {}, "warnings": [str(exc)]}

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

## 2. Tests — `tests/scripts/test_rehearse_inventory.py` (REVISED per F2)

12 fixture-based tests. **No live-root walks in the automated suite.**

1. `test_walk_inventory_with_metadata_returns_per_file_dict` — fixture tree; assert each entry has sha256, size, mtime
2. `test_walk_inventory_excludes_ignored_top_level` — fixture has `.git`, `node_modules`; result excludes them
3. `test_walk_inventory_excludes_manifest_excluded_paths` — fixture manifest with `excluded_paths`; result excludes them
4. `test_walk_inventory_handles_unreadable_file` — fixture with read-permission-denied file; walk continues without it
5. `test_parse_authority_matrix_extracts_preliminary_table_rows` — fixture markdown with the matrix shape; assert ≥10 rows extracted with all 6 fields
6. `test_parse_authority_matrix_missing_section_raises` — fixture markdown without "Preliminary Authority Matrix" header; raises `ManifestValidationError`
7. `test_parse_authority_matrix_empty_table_raises` — fixture markdown with header but no data rows; raises `ManifestValidationError`
8. `test_build_runtime_manifest_populates_surface_treatments` — given source manifest + 3 fake matrix rows; result has `surface_treatments` with 3 entries keyed by slugified surface name; each entry includes `_audit_note`
9. `test_write_runtime_manifest_produces_loadable_toml` — write + re-read via `tomllib`; round-trip matches input dict
10. `test_run_against_fixture_tree_with_inventory_root_override` — calls `run(manifest, output_dir, inventory_root=tmp_fixture)`; assert status=ok, all 3 output files exist, file_count matches fixture
11. `test_run_runtime_manifest_revalidation_failure_reports_error` — fixture matrix with no rows; `_inventory.run()` returns status='error' with the correct warning, does NOT raise

Plus 2 tests for the Slice 1 `_common.py` extension (`is_runtime_manifest`):

12. `test_load_manifest_runtime_empty_surface_treatments_rejected` — runtime manifest with empty `[surface_treatments]` + `is_runtime_manifest=True` raises `ManifestValidationError`
13. `test_load_manifest_runtime_populated_surface_treatments_accepted` — runtime manifest with populated table + `is_runtime_manifest=True` passes

Total: 13 tests. **0 existing tests modified or deleted.** All use `tmp_path` fixtures or explicit `inventory_root` override; **no live-root walks**.

## 3. Files Changed (revised)

### 3.1 New
- `scripts/rehearse/_inventory.py` (~210 LOC after F1 fix)
- `tests/scripts/test_rehearse_inventory.py` (13 tests; all fixture-based)

### 3.2 Modified
- `scripts/rehearse/_common.py` — add `is_runtime_manifest` kwarg + extend M5 (~10 LOC; unchanged from -001)

### 3.3 Untouched
- `hash_set_walk()` stays unchanged for its other callers (Slice 1 + future drift checks); `_inventory.py` uses its own per-file walker per F1
- `scripts/rehearse_isolation.py` (driver still uses Wave 1 default)
- All existing tests

## 4. Compliance With Codex `-002` Findings

| Finding | Status | Where addressed |
|---|---|---|
| F1 inventory contract mismatch | **Fixed** | §1.2 `_walk_inventory_with_metadata()` returns per-file dict with sha256, size, mtime; test 1 asserts the shape |
| F2 test walks live root | **Fixed** | All tests use `tmp_path` or `inventory_root` override; live-root execution remains in operator-invoked driver, not pytest |
| F3 runtime surface_treatments schema | **Reframed** | §0 architectural reframing: surface_treatments is audit-metadata only; lanes consume operational data from their own authoritative sources (table at §0); 6-column matrix is sufficient under this framing |

## 5. Codex Re-Review Asks

1. Confirm F1 fix: per-file inventory dict with `{sha256, size, mtime}` matches the contract; test 1 asserts the shape correctly.
2. Confirm F2 fix: all tests use `tmp_path` fixtures or `inventory_root` override; no live-root walks in the automated suite; `inventory_root` parameter on `run()` is the right test-vs-prod separation knob.
3. Confirm F3 reframing: `surface_treatments` as audit-metadata (not operational contract) is acceptable; the per-lane authoritative-source table at §0 covers the operational needs without expanding the matrix parser.
4. Confirm 13 fixture-based tests + 0 existing tests modified satisfies the additive discipline established by Slice 1.
5. Confirm the runtime manifest's `_inventory_metadata` block (with `schema_note` referencing this bridge file) is the right place to record the bounded-schema decision for downstream lanes to discover.
6. **GO / NO-GO** on Slice 2 revised.

## 6. Decision Needed From Owner

None — owner pre-acks (Wave 2 §3.3 + §3.5) carry forward; F3 reframing is engineering scope, not owner-facing decision.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
