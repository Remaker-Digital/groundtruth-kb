"""Wave 2 lane 2 (Stage B): path-rewrite mapping for adopter-owned content.

Per ``bridge/gtkb-isolation-016-phase8-wave2-slice4-003.md`` (REVISED-1) and
``-004`` (Codex GO with 5 implementation conditions).

Computes the path-rewrite mapping that resolves the manifest's
``git_filter_command_template`` placeholder
``<agent-red-paths-from-_path_rewrite>`` for the eventual Phase 9 cutover.
The lane only generates arguments; running ``git filter-repo`` is
explicitly out of scope for the Phase 8 rehearsal.

Authoritative source: ``gt project classify-tree`` invoked as a subprocess
through the callable click entrypoint (per F1 NO-GO ``-002``: the
``python -m groundtruth_kb.cli`` form is a no-op in this checkout because
``cli.py`` lacks a ``__main__`` guard).

Authority: ADR-ISOLATION-APPLICATION-PLACEMENT-001 (upstream commit
``affa5a0567a64f79bb4c5aae891889d4af50a72a``); Wave 2 GO at
``bridge/gtkb-isolation-016-phase8-wave2-implementation-004.md``.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from rehearse._common import LEGACY_ROOT


_CLASSIFY_TREE_DEFAULT_MAX_DEPTH = 10
"""Matches ``gt project classify-tree --max-depth`` default."""

_SCHEMA_VERSION = 1
"""``path_rewrite.json`` schema version."""


def _build_classify_tree_command(
    legacy_root: Path,
    output_path: Path,
    *,
    max_depth: int = _CLASSIFY_TREE_DEFAULT_MAX_DEPTH,
) -> list[str]:
    """Build the subprocess argv for invoking GT-KB's ``classify-tree``.

    Per ``bridge/gtkb-isolation-016-phase8-wave2-slice4-002.md`` F1 NO-GO:
    ``python -m groundtruth_kb.cli`` is a no-op in this checkout (``cli.py``
    has no ``__main__`` guard, so ``runpy`` exits cleanly without invoking
    the click group). The callable form below is verified working.

    The returned argv is a list of strings suitable for ``subprocess.run``.
    """
    return [
        sys.executable,
        "-c",
        "from groundtruth_kb.cli import main; main()",
        "project",
        "classify-tree",
        "--dir",
        str(legacy_root),
        "--max-depth",
        str(max_depth),
        "--format",
        "json",
        "--output",
        str(output_path),
    ]


def _derive_target_namespace(manifest: dict[str, Any]) -> str:
    """Return the rewrite target prefix derived from manifest.

    Per ``bridge/gtkb-isolation-016-phase8-wave2-slice4-002.md`` F2 NO-GO:
    the target prefix must not be hard-coded as ``applications/Agent_Red``.
    The validated manifest already carries ``target_root``,
    ``legacy_root``, and ``applications_namespace``; deriving from those
    keeps the lane reusable for any GT-KB adopter and prevents drift from
    the manifest if the target root changes.

    Returns a forward-slash-normalized relative path string, e.g.
    ``"applications/Agent_Red"``. Pre-condition (already enforced by
    ``load_manifest(wave=2)`` at the driver): ``target_root`` is a
    descendant of ``applications_namespace`` which equals
    ``legacy_root / "applications"``.
    """
    target_root = Path(manifest["target_root"]).resolve()
    legacy_root = Path(manifest["legacy_root"]).resolve()
    relative = target_root.relative_to(legacy_root)
    return str(relative).replace("\\", "/")


def _partition_rows(
    rows: list[dict[str, Any]],
    target_namespace: str,
) -> dict[str, list[dict[str, Any]]]:
    """Partition classify-tree rows into the five Slice 4 buckets.

    Per ``-003`` §3 / ``-004`` recommendation 5: ``legacy-exception`` and
    ``owner_decision_pending`` rows produce warnings without escalating
    status to ``error``. The lane surfaces classifications; resolution is
    a Wave 3 verification matrix concern.
    """
    rewrites: list[dict[str, Any]] = []
    keep_at_root: list[dict[str, Any]] = []
    shared_paths: list[dict[str, Any]] = []
    legacy_exceptions: list[dict[str, Any]] = []
    unresolved_paths: list[dict[str, Any]] = []
    unknown_ownership: list[dict[str, Any]] = []

    for row in rows:
        path = row.get("path", "")
        ownership = row.get("ownership", "")
        record_id = row.get("record_id", "")
        notes = row.get("notes", "")

        if row.get("owner_decision_pending"):
            unresolved_paths.append(
                {
                    "path": path,
                    "ownership": ownership,
                    "record_id": record_id,
                    "notes": notes,
                    "owner_decision_pending": True,
                }
            )
            continue

        if ownership == "adopter-owned":
            rewrites.append(
                {
                    "source": path,
                    "target": f"{target_namespace}/{path}",
                    "record_id": record_id,
                    "ownership": ownership,
                }
            )
        elif ownership in ("gt-kb-managed", "gt-kb-scaffolded"):
            keep_at_root.append(
                {"path": path, "ownership": ownership, "record_id": record_id}
            )
        elif ownership == "shared-structured":
            shared_paths.append(
                {"path": path, "ownership": ownership, "record_id": record_id}
            )
        elif ownership == "legacy-exception":
            legacy_exceptions.append(
                {
                    "path": path,
                    "ownership": ownership,
                    "record_id": record_id,
                    "notes": notes,
                }
            )
        else:
            unknown_ownership.append(
                {"path": path, "ownership": ownership, "record_id": record_id}
            )

    return {
        "rewrites": rewrites,
        "keep_at_root": keep_at_root,
        "shared_paths": shared_paths,
        "legacy_exceptions": legacy_exceptions,
        "unresolved_paths": unresolved_paths,
        "unknown_ownership": unknown_ownership,
    }


def _compose_git_filter_args(
    rewrites: list[dict[str, Any]],
) -> str:
    """Compose the git-filter-repo --path / --path-rename argument lines."""
    return "".join(
        f"--path {r['source']} --path-rename {r['source']}:{r['target']}\n"
        for r in rewrites
    )


def run(
    manifest: dict[str, Any],
    output_dir: Path,
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Wave 2 Stage B leaf lane. Per common contract Wave 2 -003 §4.1.

    Returns the standard sub-script result dict::

        {"status": "ok"|"error"|"skipped",
         "output_files": [str, ...],
         "metrics": {...},
         "warnings": [str, ...]}
    """
    if dry_run:
        return {
            "status": "skipped",
            "output_files": [],
            "metrics": {"reason": "dry_run"},
            "warnings": [],
        }

    lane_dir = output_dir / "path_rewrite"
    lane_dir.mkdir(parents=True, exist_ok=True)
    classification_path = lane_dir / "classification.json"

    cmd = _build_classify_tree_command(LEGACY_ROOT, classification_path)

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=False
        )
    except OSError as exc:
        return {
            "status": "error",
            "output_files": [],
            "metrics": {},
            "warnings": [f"classify_tree_subprocess_failed_to_spawn: {exc}"],
        }

    if result.returncode != 0:
        return {
            "status": "error",
            "output_files": [],
            "metrics": {},
            "warnings": [
                f"classify_tree_nonzero_exit: code={result.returncode}; "
                f"stderr={result.stderr.strip()[:500]}"
            ],
        }

    # Per Codex GO -004 condition 2: explicit file-existence check after
    # zero-exit return. Catches the historical "python -m no-op" failure
    # mode in production even if the entrypoint regresses.
    if not classification_path.exists():
        return {
            "status": "error",
            "output_files": [],
            "metrics": {},
            "warnings": [
                "classify_tree_zero_exit_but_no_classification_file: "
                f"expected {classification_path}; classify-tree subprocess "
                "exited 0 but did not write the JSON output. Likely indicates "
                "an entrypoint regression (see slice4-002 F1)."
            ],
        }

    try:
        classification = json.loads(classification_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "status": "error",
            "output_files": [str(classification_path)],
            "metrics": {},
            "warnings": [f"classification_json_unreadable: {exc}"],
        }

    rows = classification.get("rows")
    if not isinstance(rows, list):
        return {
            "status": "error",
            "output_files": [str(classification_path)],
            "metrics": {},
            "warnings": [
                f"classification_rows_missing_or_malformed: "
                f"expected list, got {type(rows).__name__}"
            ],
        }

    target_namespace = _derive_target_namespace(manifest)
    buckets = _partition_rows(rows, target_namespace)

    warnings: list[str] = []
    if buckets["legacy_exceptions"]:
        warnings.append(
            f"legacy_exceptions_present: "
            f"{len(buckets['legacy_exceptions'])} path(s) "
            f"flagged as legacy-exception (explicit unresolved adoption "
            f"debt; surface for owner decision at Wave 3)"
        )
    if buckets["unresolved_paths"]:
        warnings.append(
            f"unresolved_paths_present: "
            f"{len(buckets['unresolved_paths'])} path(s) with "
            f"owner_decision_pending=true (not auto-rewritten; surface for "
            f"owner decision at Wave 3)"
        )
    if buckets["unknown_ownership"]:
        warnings.append(
            f"unknown_ownership_labels: "
            f"{len(buckets['unknown_ownership'])} row(s) had ownership "
            f"values outside the 5 known categories — skipped from rewrites; "
            f"check classify-tree version for new ownership labels"
        )

    path_rewrite_doc = {
        "schema_version": _SCHEMA_VERSION,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source_root": str(LEGACY_ROOT).replace("\\", "/"),
        "target_namespace": target_namespace,
        "classification_source": str(classification_path).replace("\\", "/"),
        "classification_metadata": {
            "gt_kb_version": classification.get("gt_kb_version", ""),
            "gt_kb_head": classification.get("gt_kb_head", ""),
            "target_head": classification.get("target_head", ""),
            "total_paths_classified": classification.get(
                "total_paths_classified", len(rows)
            ),
        },
        "summary": {
            "rewrites_count": len(buckets["rewrites"]),
            "keep_at_root_count": len(buckets["keep_at_root"]),
            "shared_paths_count": len(buckets["shared_paths"]),
            "legacy_exceptions_count": len(buckets["legacy_exceptions"]),
            "unresolved_count": len(buckets["unresolved_paths"]),
            "unknown_ownership_count": len(buckets["unknown_ownership"]),
            "total_classified": len(rows),
        },
        "rewrites": buckets["rewrites"],
        "keep_at_root": buckets["keep_at_root"],
        "shared_paths": buckets["shared_paths"],
        "legacy_exceptions": buckets["legacy_exceptions"],
        "unresolved_paths": buckets["unresolved_paths"],
    }

    path_rewrite_path = lane_dir / "path_rewrite.json"
    path_rewrite_path.write_text(
        json.dumps(path_rewrite_doc, indent=2), encoding="utf-8"
    )

    git_filter_path = lane_dir / "git_filter_args.txt"
    git_filter_path.write_text(
        _compose_git_filter_args(buckets["rewrites"]), encoding="utf-8"
    )

    return {
        "status": "ok",
        "output_files": [
            str(classification_path),
            str(path_rewrite_path),
            str(git_filter_path),
        ],
        "metrics": {
            "rewrites_count": len(buckets["rewrites"]),
            "total_classified": len(rows),
            "target_namespace": target_namespace,
        },
        "warnings": warnings,
    }
