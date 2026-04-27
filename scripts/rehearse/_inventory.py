"""Wave 2 lane 1 (Stage A leaf): file inventory + authority-matrix audit-metadata
parse + runtime manifest construction.

Per ``bridge/gtkb-isolation-016-phase8-wave2-slice2-003.md`` (REVISED-1) and
``-004`` (Codex GO).

The runtime manifest's ``[surface_treatments]`` table is **audit metadata
only** — downstream Wave 2 lanes (2-11) read their operational data from
their own authoritative sources (e.g., ``gt project classify-tree`` for
paths, ``bridge/INDEX.md`` parsing for bridge state, etc.) per the F3
reframing in the source proposal.

Performance + non-silent-drop changes per
``bridge/gtkb-rehearsal-inventory-perf-003.md`` (REVISED-1) and ``-004``
(Codex GO with reporting constraints):

- ``_DEFAULT_IGNORED_TOP_LEVEL`` extended with cache/transient directories
  only (logs/ is migration-relevant evidence and is NOT excluded by default).
- ``os.scandir`` top-level prune avoids descent into ignored directories
  (root cause of the prior 120s timeout was rglob descending into
  ``.codex_pydeps`` with ~38k files before the per-path skip check fired).
- ``dryrun-ignored.json`` emission per Phase 8 plan §"the rehearsal cannot
  silently drop data" — every ignored top-level directory is accounted for
  by directory-count and total-bytes summary (NOT a per-file listing; the
  schema field name and docstring make this explicit per Codex `-004`
  reporting constraint 2).
- Three-metric walltime telemetry (walk + hash + ignored_summary)
  surfaces where the timeout dominates if regressions occur.

Authority: ADR-ISOLATION-APPLICATION-PLACEMENT-001 (upstream commit
``affa5a0567a64f79bb4c5aae891889d4af50a72a``); Wave 2 GO at
``bridge/gtkb-isolation-016-phase8-wave2-implementation-004.md``.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
from pathlib import Path
from typing import Any

from rehearse._common import (
    LEGACY_ROOT,
    ManifestValidationError,
    load_manifest,
)

_PRELIM_MATRIX_HEADER_PATTERN = re.compile(r"^##\s+Preliminary Authority Matrix\s*$", re.MULTILINE)
_NEXT_SECTION_PATTERN = re.compile(r"^##\s+\S", re.MULTILINE)

# Cache/transient directories that don't contribute migration-relevant
# evidence. Each is regenerable at the target child root from existing
# tooling — see ``_IGNORED_TOP_LEVEL_REASONS`` below for per-entry rationale.
# Per Codex `-004` constraint: only cache/transient dirs may be added here
# without bridge review. logs/ is intentionally NOT in this set
# (1,239 files including production build evidence + visual-evidence).
_DEFAULT_IGNORED_TOP_LEVEL: frozenset[str] = frozenset(
    {
        ".git",
        "__pycache__",
        "node_modules",
        ".groundtruth-chroma",
        ".tmp.driveupload",
        ".codex_pydeps",
        ".venv",
        "venv",
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
        "htmlcov",
    }
)

# Per-default-ignored-directory reasoning, surfaced in dryrun-ignored.json
# per Codex GO `-004` reporting constraint 1: "must include a reason for
# every default ignored directory".
_IGNORED_TOP_LEVEL_REASONS: dict[str, str] = {
    ".git": "vcs_metadata_regenerable_via_clone_at_target",
    "__pycache__": "python_bytecode_cache_regenerated_on_import",
    "node_modules": "node_dependencies_regenerable_from_package_json",
    ".groundtruth-chroma": "chroma_embedding_store_handled_separately_by_chromadb_regen_lane",
    ".tmp.driveupload": "transient_drive_sync_artifact_per_s311_recovery_lessons",
    ".codex_pydeps": "codex_python_deps_cache_regenerable_from_pyproject_toml",
    ".venv": "python_virtualenv_regenerable_via_python_m_venv",
    "venv": "python_virtualenv_regenerable_via_python_m_venv",
    ".pytest_cache": "pytest_run_cache_regenerated_on_next_test_run",
    ".ruff_cache": "ruff_lint_cache_regenerated_on_next_ruff_invocation",
    ".mypy_cache": "mypy_typecheck_cache_regenerated_on_next_mypy_run",
    "htmlcov": "coverage_html_report_regenerable_from_coverage_html",
}


def _slugify(name: str) -> str:
    """Convert a surface name to a stable surface_id slug."""
    s = re.sub(r"[`*_]", "", name)
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-")
    return s.lower() or "unnamed-surface"


def _count_files_and_bytes(directory: Path) -> tuple[int, int]:
    """Lightweight enumeration of an ignored directory for audit summary.

    Returns ``(file_count, total_bytes)`` without computing SHA256s. Used
    by ``dryrun-ignored.json`` to record what was excluded without paying
    the per-file hashing cost (which is exactly what motivates excluding
    these directories in the first place).
    """
    file_count = 0
    total_bytes = 0
    if not directory.exists() or not directory.is_dir():
        return (0, 0)
    for path in directory.rglob("*"):
        try:
            if path.is_file():
                file_count += 1
                try:
                    total_bytes += path.stat().st_size
                except OSError:
                    pass
        except OSError:
            continue
    return (file_count, total_bytes)


def _walk_inventory_with_metadata(
    root: Path,
    ignored_top_level: frozenset[str],
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]], float, float]:
    """Walk root with top-level prune; return inventory, ignored summary, and timings.

    Per F1 fix from slice2 ``-002`` NO-GO: single pass collects hash + size
    + mtime together. Per inventory-perf ``-004`` GO: top-level prune via
    ``os.scandir`` avoids descent into ignored directories at iteration
    time (root cause of prior timeout).

    Returns ``(inventory, ignored_summary, walk_walltime, hash_walltime)``:
      - inventory: ``{relative_path: {sha256, size, mtime}}`` for non-ignored files
      - ignored_summary: ``{top_level_name: {file_count, total_bytes, reason}}``
      - walk_walltime: scandir + rglob enumeration time (not hashing)
      - hash_walltime: per-file read_bytes + SHA256 computation time

    Files whose bytes cannot be read (permission denied, transient I/O
    error) are silently skipped, matching the existing tolerance.
    """
    inventory: dict[str, dict[str, Any]] = {}
    ignored_summary: dict[str, dict[str, Any]] = {}
    walk_walltime = 0.0
    hash_walltime = 0.0

    if not root.exists() or not root.is_dir():
        return (inventory, ignored_summary, walk_walltime, hash_walltime)

    walk_start = time.perf_counter()

    # Top-level scandir lets us prune ignored directories before descent.
    try:
        top_entries = list(os.scandir(root))
    except OSError:
        return (inventory, ignored_summary, walk_walltime, hash_walltime)

    included_paths: list[Path] = []
    for entry in top_entries:
        entry_path = Path(entry.path)
        if entry.name in ignored_top_level:
            # Audit-summary enumeration only; no hashing.
            file_count, total_bytes = _count_files_and_bytes(entry_path)
            ignored_summary[entry.name] = {
                "file_count": file_count,
                "total_bytes": total_bytes,
                "reason": _IGNORED_TOP_LEVEL_REASONS.get(entry.name, "manifest_or_default_excluded"),
            }
            continue

        try:
            is_file = entry.is_file(follow_symlinks=False)
            is_dir = entry.is_dir(follow_symlinks=False)
        except OSError:
            continue

        if is_file:
            included_paths.append(entry_path)
        elif is_dir:
            try:
                included_paths.extend(p for p in entry_path.rglob("*") if p.is_file())
            except OSError:
                continue

    walk_walltime = time.perf_counter() - walk_start

    # Hashing pass over the pruned set.
    hash_start = time.perf_counter()
    for path in included_paths:
        try:
            rel = path.relative_to(root)
        except ValueError:
            continue
        try:
            stat_result = path.stat()
            data = path.read_bytes()
        except OSError:
            continue
        inventory[str(rel).replace("\\", "/")] = {
            "sha256": hashlib.sha256(data).hexdigest(),
            "size": stat_result.st_size,
            "mtime": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(stat_result.st_mtime)),
        }
    hash_walltime = time.perf_counter() - hash_start

    return (inventory, ignored_summary, walk_walltime, hash_walltime)


def _emit_dryrun_ignored(
    ignored_summary: dict[str, dict[str, Any]],
    manifest_excluded_paths: list[str],
    output_path: Path,
) -> None:
    """Emit ``dryrun-ignored.json`` per Phase 8 plan §"non-silent-drop".

    Per Codex GO ``-004`` reporting constraint 2: schema name and field
    docstring are explicit that this is a directory-summary
    (count + total bytes per ignored top-level directory), NOT a per-file
    ignored manifest. The "summary" suffix in the schema field
    ``ignored_directories_summary`` makes that explicit.
    """
    payload: dict[str, Any] = {
        "schema_version": 1,
        "schema_kind": "directory_summary_not_per_file_listing",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "ignored_directories_summary": [
            {
                "path": name,
                "file_count": data["file_count"],
                "total_bytes": data["total_bytes"],
                "reason": data["reason"],
                "default_or_manifest": ("default" if name in _DEFAULT_IGNORED_TOP_LEVEL else "manifest"),
            }
            for name, data in sorted(ignored_summary.items())
        ],
        "manifest_excluded_paths": sorted(manifest_excluded_paths),
        "summary": {
            "total_ignored_directories": len(ignored_summary),
            "total_ignored_files": sum(d["file_count"] for d in ignored_summary.values()),
            "total_ignored_bytes": sum(d["total_bytes"] for d in ignored_summary.values()),
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _parse_authority_matrix(matrix_path: Path) -> list[dict[str, str]]:
    """Parse the Preliminary Authority Matrix markdown table for audit metadata.

    Per F3 reframing: extracts the 6 narrative columns as audit context.
    Downstream lanes do NOT use this for operational data.
    """
    content = matrix_path.read_text(encoding="utf-8")
    header_match = _PRELIM_MATRIX_HEADER_PATTERN.search(content)
    if not header_match:
        raise ManifestValidationError(f"_inventory: 'Preliminary Authority Matrix' section not found in {matrix_path}.")
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
                    "Wave 2 audit metadata only; lanes consume operational data from their own authoritative sources."
                ),
            }
        )
    if not rows:
        raise ManifestValidationError(
            f"_inventory: no surface rows extracted from 'Preliminary Authority Matrix' in {matrix_path}."
        )
    return rows


def _build_runtime_manifest(
    source_manifest: dict[str, Any],
    surface_rows: list[dict[str, str]],
) -> dict[str, Any]:
    """Build runtime manifest = source + populated surface_treatments + metadata."""
    runtime = dict(source_manifest)
    runtime["surface_treatments"] = {_slugify(row["surface"]): row for row in surface_rows}
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
    lines: list[str] = ["# Runtime manifest produced by Wave 2 lane 1 (_inventory.py).\n"]
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
         "metrics": {file_count, total_bytes, surface_count,
                     walk_walltime_seconds, hash_walltime_seconds,
                     ignored_summary_walltime_seconds},
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
    excluded_top = frozenset(e.rstrip("/").split("/")[0] for e in excluded) | _DEFAULT_IGNORED_TOP_LEVEL

    try:
        files, ignored_summary, walk_walltime, hash_walltime = _walk_inventory_with_metadata(root, excluded_top)
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
    inventory_path.write_text(json.dumps(inventory, indent=2), encoding="utf-8")
    output_files.append(inventory_path)

    # Emit dryrun-ignored.json per Phase 8 plan §"non-silent-drop".
    ignored_summary_start = time.perf_counter()
    dryrun_ignored_path = output_dir / "dryrun-ignored.json"
    _emit_dryrun_ignored(
        ignored_summary,
        sorted(excluded),  # manifest_excluded_paths from manifest
        dryrun_ignored_path,
    )
    output_files.append(dryrun_ignored_path)
    ignored_summary_walltime = time.perf_counter() - ignored_summary_start

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
            "walk_walltime_seconds": round(walk_walltime, 3),
            "hash_walltime_seconds": round(hash_walltime, 3),
            "ignored_summary_walltime_seconds": round(ignored_summary_walltime, 3),
        },
        "warnings": warnings,
    }
