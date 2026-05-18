#!/usr/bin/env python3
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Event-driven bridge/INDEX.md archival entry point (WI-3364).

``maybe_archive_and_prune_index()`` is the deterministic, best-effort step the
four bridge-write helper paths call after their own ``bridge/INDEX.md`` write.
Below the line threshold it is a cheap no-op that does not load the
Deliberation Archive database. Above threshold it invokes the existing
``archive_verified_threads_and_prune_index()`` pipeline with the current
bridge thread excluded, so a verdict write never archives-and-prunes its own
just-written thread.

The call never raises: any failure is captured and swallowed so a bridge
write is never failed by an archival problem. On a detected concurrent
``bridge/INDEX.md`` change the underlying pipeline skips its write, and the
trim simply retries on the next bridge write.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS_DIR = _PROJECT_ROOT / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

# Line threshold aligned with the file-bridge protocol's ~200-line Index
# Maintenance guideline. Tunable here without a specification change.
INDEX_LINE_THRESHOLD = 200


def maybe_archive_and_prune_index(
    project_root: Path | str,
    *,
    current_thread: str,
    threshold: int = INDEX_LINE_THRESHOLD,
) -> dict[str, Any]:
    """Archive + prune ``bridge/INDEX.md`` when it exceeds ``threshold`` lines.

    Best-effort and fail-open: this function never raises. Below ``threshold``
    it returns without loading the Deliberation Archive database. Above
    ``threshold`` it invokes ``archive_verified_threads_and_prune_index`` with
    ``current_thread`` excluded.

    Args:
        project_root: Repository root containing ``bridge/INDEX.md``.
        current_thread: Slug of the bridge thread written by the in-progress
            bridge write; excluded from this archival pass.
        threshold: Line count above which the pipeline is invoked.

    Returns:
        A result dict. ``triggered`` is ``True`` only when the pipeline ran;
        ``reason`` explains a no-op; ``report`` carries the pipeline report
        when triggered.
    """
    try:
        root = Path(project_root)
        index_path = root / "bridge" / "INDEX.md"
        if not index_path.is_file():
            return {"triggered": False, "reason": "no_index"}
        line_count = len(index_path.read_text(encoding="utf-8").splitlines())
        if line_count <= threshold:
            return {
                "triggered": False,
                "reason": "below_threshold",
                "line_count": line_count,
            }
        from retroactive_harvest_bridge_threads import (  # noqa: PLC0415
            archive_verified_threads_and_prune_index,
        )

        report = archive_verified_threads_and_prune_index(
            index_path=index_path,
            bridge_dir=root / "bridge",
            kb_path=str(root / "groundtruth.db"),
            exclude_threads=frozenset({current_thread}),
        )
        return {
            "triggered": True,
            "line_count_before": line_count,
            "report": report,
        }
    except Exception as exc:  # noqa: BLE001 - best-effort; never fail a bridge write
        return {"triggered": False, "reason": "error", "error": repr(exc)}


__all__ = ["INDEX_LINE_THRESHOLD", "maybe_archive_and_prune_index"]
