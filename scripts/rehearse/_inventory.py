"""Wave 2 lane 1 (Stage A leaf): file inventory + authority-matrix audit-metadata
parse + runtime manifest construction.

Per ``bridge/gtkb-isolation-016-phase8-wave2-slice2-003.md`` (REVISED-1) and
``-004`` (Codex GO).

The runtime manifest's ``[surface_treatments]`` table is **audit metadata
only** — downstream Wave 2 lanes (2-11) read their operational data from
their own authoritative sources (e.g., ``gt project classify-tree`` for
paths, ``bridge/INDEX.md`` parsing for bridge state, etc.) per the F3
reframing in the source proposal.

Authority: ADR-ISOLATION-APPLICATION-PLACEMENT-001 (upstream commit
``affa5a0567a64f79bb4c5aae891889d4af50a72a``); Wave 2 GO at
``bridge/gtkb-isolation-016-phase8-wave2-implementation-004.md``.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any

from rehearse._common import (
    LEGACY_ROOT,
    ManifestValidationError,
    load_manifest,
)


_PRELIM_MATRIX_HEADER_PATTERN = re.compile(
    r"^##\s+Preliminary Authority Matrix\s*$", re.MULTILINE
)
_NEXT_SECTION_PATTERN = re.compile(r"^##\s+\S", re.MULTILINE)
_DEFAULT_IGNORED_TOP_LEVEL: frozenset[str] = frozenset(
    {".git", "__pycache__", "node_modules", ".groundtruth-chroma", ".tmp.driveupload"}
)


def _slugify(name: str) -> str:
    """Convert a surface name to a stable surface_id slug."""
    s = re.sub(r"[`*_]", "", name)
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-")
    return s.lower() or "unnamed-surface"


def _walk_inventory_with_metadata(
    root: Path,
    ignored_top_level: frozenset[str],
) -> dict[str, dict[str, Any]]:
    """Walk root, return ``{relative_path: {sha256, size, mtime}}`` per file.

    Per F1 fix from ``-002`` NO-GO: single pass collects hash + size + mtime
    together. Replaces the hash-only output `hash_set_walk()` would produce
    and avoids a second ``stat()`` pass with TOCTOU concerns. Files whose
    bytes cannot be read (permission denied, transient I/O error) are
    silently skipped, matching the existing ``hash_set_walk`` tolerance.
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
        rows.append(
            {
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
            }
        )
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
    """Build runtime manifest = source + populated surface_treatments + metadata."""
    runtime = dict(source_manifest)
    runtime["surface_treatments"] = {
        _slugify(row["surface"]): row for row in surface_rows
    }
    runtime["_inventory_metadata"] = {
        "populated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "matrix_source": source_manifest.get("phase_1_authority_matrix_path", ""),
        "row_count": str(len(surface_rows)),
        "schema_note": (
            "surface_treatments contains 6-column audit metadata only "
            "(see bridge/gtkb-isolation-016-phase8-wave2-slice2-003.md F3); "
            "downstream lanes consume operational data from their own "
            "authoritative sources."
        ),
    }
    return runtime


def _toml_escape(value: Any) -> str:
    """Escape a value for inclusion in a TOML basic string."""
    return str(value).replace("\\", "\\\\").replace('"', '\\"')


def _write_runtime_manifest(runtime: dict[str, Any], output_path: Path) -> None:
    """Write runtime manifest as TOML using a minimal hand-rolled emitter.

    Produces only the structure ``_build_runtime_manifest`` emits: top-level
    string scalars + lists + a few tables. No nested-table-of-tables beyond
    ``[surface_treatments.<surface_id>]``. Avoids adding ``tomli_w`` as a
    dependency for this single use site.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "# Runtime manifest produced by Wave 2 lane 1 (_inventory.py).\n"
    ]
    for key, value in runtime.items():
        if isinstance(value, dict):
            continue
        if isinstance(value, list):
            list_repr = ", ".join(f'"{_toml_escape(v)}"' for v in value)
            lines.append(f"{key} = [{list_repr}]\n")
        else:
            lines.append(f'{key} = "{_toml_escape(value)}"\n')
    for table_name, table in runtime.items():
        if not isinstance(table, dict):
            continue
        if table_name == "surface_treatments":
            for surface_id, fields in table.items():
                lines.append(f"\n[surface_treatments.{surface_id}]\n")
                for k, v in fields.items():
                    lines.append(f'{k} = "{_toml_escape(v)}"\n')
        else:
            lines.append(f"\n[{table_name}]\n")
            for k, v in table.items():
                lines.append(f'{k} = "{_toml_escape(v)}"\n')
    output_path.write_text("".join(lines), encoding="utf-8")


def run(
    manifest: dict[str, Any],
    output_dir: Path,
    *,
    dry_run: bool = False,
    inventory_root: Path | None = None,
) -> dict[str, Any]:
    """Wave 2 Stage A leaf lane. Per common contract Wave 2 -003 §4.1.

    The ``inventory_root`` override (default None → ``LEGACY_ROOT``) is the
    F2 fix from ``-002`` NO-GO: it lets tests walk a fixture tree under
    ``tmp_path`` instead of the live repo. Operator-invoked production
    execution still defaults to ``LEGACY_ROOT`` via the driver.

    Returns the standard sub-script result dict::

        {"status": "ok"|"error"|"skipped",
         "output_files": [Path, ...],
         "metrics": {file_count, total_bytes, surface_count},
         "warnings": [str, ...]}
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
    excluded_top = (
        frozenset(e.rstrip("/").split("/")[0] for e in excluded)
        | _DEFAULT_IGNORED_TOP_LEVEL
    )

    try:
        files = _walk_inventory_with_metadata(root, excluded_top)
    except OSError as exc:
        return {
            "status": "error",
            "output_files": [],
            "metrics": {},
            "warnings": [f"file_walk_failed: {exc}"],
        }

    inventory = {
        "root": str(root),
        "file_count": len(files),
        "total_bytes": sum(f["size"] for f in files.values()),
        "files": files,
        "ignored_top_level": sorted(excluded_top),
        "walked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    inventory_path = output_dir / "inventory.json"
    inventory_path.parent.mkdir(parents=True, exist_ok=True)
    inventory_path.write_text(
        json.dumps(inventory, indent=2), encoding="utf-8"
    )
    output_files.append(inventory_path)

    matrix_path = LEGACY_ROOT / manifest["phase_1_authority_matrix_path"]
    try:
        surface_rows = _parse_authority_matrix(matrix_path)
    except ManifestValidationError as exc:
        return {
            "status": "error",
            "output_files": [str(p) for p in output_files],
            "metrics": {},
            "warnings": [str(exc)],
        }

    runtime = _build_runtime_manifest(manifest, surface_rows)
    runtime_path = output_dir / "runtime-manifest.toml"
    _write_runtime_manifest(runtime, runtime_path)
    output_files.append(runtime_path)

    try:
        load_manifest(runtime_path, wave=2, is_runtime_manifest=True)
    except ManifestValidationError as exc:
        return {
            "status": "error",
            "output_files": [str(p) for p in output_files],
            "metrics": {"surface_count": len(surface_rows)},
            "warnings": [f"runtime_manifest_revalidation_failed: {exc}"],
        }

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
