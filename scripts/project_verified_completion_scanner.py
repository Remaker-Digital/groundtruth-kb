#!/usr/bin/env python3
"""Read-only scanner: per-project-authorization VERIFIED-completion readiness.

IP-1 of WI-3316 (bridge thread ``gtkb-project-verified-completion-auq-trigger``).

For every ``status='active'`` project authorization, this scanner determines
whether every work item in ``included_work_item_ids`` is covered by a bridge
thread whose latest ``bridge/INDEX.md`` status is ``VERIFIED``. An authorization
is *completion-ready* iff it lists at least one work item and all of them are
VERIFIED-covered.

The scanner is strictly read-only: it issues no DB writes and no bridge-file
writes. It uses the canonical bridge index parser in ``groundtruth_kb.bridge``
rather than ad-hoc regex for INDEX parsing.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# A bridge proposal/report metadata line: ``Work Item: WI-1234`` (or a
# GTKB-/WORKLIST- descriptive id), optionally backtick-wrapped.
_WORK_ITEM_LINE_RE = re.compile(
    r"^Work Item:\s*`?(WI-\d+|GTKB-[A-Z0-9-]+|WORKLIST-[A-Z0-9-]+)`?\s*$",
    re.MULTILINE,
)


@dataclass(frozen=True)
class AuthorizationReadiness:
    """Completion-readiness verdict for one project authorization."""

    authorization_id: str
    project_id: str
    authorization_name: str
    included_work_item_ids: list[str]
    verified_work_item_ids: list[str]
    unverified_work_item_ids: list[str]
    completion_ready: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "authorization_id": self.authorization_id,
            "project_id": self.project_id,
            "authorization_name": self.authorization_name,
            "included_work_item_ids": self.included_work_item_ids,
            "verified_work_item_ids": self.verified_work_item_ids,
            "unverified_work_item_ids": self.unverified_work_item_ids,
            "completion_ready": self.completion_ready,
        }


def _ensure_groundtruth_importable(project_root: Path) -> None:
    gt_src = project_root / "groundtruth-kb" / "src"
    if gt_src.is_dir() and str(gt_src) not in sys.path:
        sys.path.insert(0, str(gt_src))


def verified_work_items(project_root: Path) -> set[str]:
    """Return the set of work-item ids cited by a bridge thread whose latest
    ``bridge/INDEX.md`` status is ``VERIFIED``.

    Uses the canonical ``groundtruth_kb.bridge.detector.parse_index`` parser to
    find VERIFIED documents, then reads each VERIFIED thread's version files for
    their ``Work Item:`` metadata lines.
    """
    _ensure_groundtruth_importable(project_root)
    from groundtruth_kb.bridge.detector import BridgeStatus, parse_index

    index_path = project_root / "bridge" / "INDEX.md"
    if not index_path.is_file():
        return set()
    result = parse_index(index_path.read_text(encoding="utf-8"), project_root=project_root)

    verified: set[str] = set()
    for document in result.documents:
        top = document.current_top
        if top is None or top.status != BridgeStatus.VERIFIED:
            continue
        for version in document.versions:
            file_path = project_root / version.file_path
            if not file_path.is_file():
                continue
            text = file_path.read_text(encoding="utf-8", errors="replace")
            for match in _WORK_ITEM_LINE_RE.finditer(text):
                verified.add(match.group(1).strip())
    return verified


def _included_work_item_ids(authorization: dict[str, Any]) -> list[str]:
    parsed = authorization.get("included_work_item_ids_parsed")
    if isinstance(parsed, list):
        return [str(value) for value in parsed]
    raw = authorization.get("included_work_item_ids")
    if not raw:
        return []
    try:
        decoded = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return []
    return [str(value) for value in decoded] if isinstance(decoded, list) else []


def scan(project_root: Path = PROJECT_ROOT) -> list[AuthorizationReadiness]:
    """Compute completion readiness for every active project authorization.

    Read-only: opens MemBase for reads only and closes it before returning.
    """
    _ensure_groundtruth_importable(project_root)
    from groundtruth_kb.db import KnowledgeDB

    db = KnowledgeDB(project_root / "groundtruth.db")
    try:
        active = db.list_project_authorizations(status="active")
    finally:
        db.close()

    verified = verified_work_items(project_root)
    results: list[AuthorizationReadiness] = []
    for authorization in active:
        included = _included_work_item_ids(authorization)
        verified_ids = [wi for wi in included if wi in verified]
        unverified_ids = [wi for wi in included if wi not in verified]
        completion_ready = bool(included) and not unverified_ids
        results.append(
            AuthorizationReadiness(
                authorization_id=str(authorization.get("id") or ""),
                project_id=str(authorization.get("project_id") or ""),
                authorization_name=str(authorization.get("authorization_name") or ""),
                included_work_item_ids=included,
                verified_work_item_ids=verified_ids,
                unverified_work_item_ids=unverified_ids,
                completion_ready=completion_ready,
            )
        )
    return results


def completion_ready(project_root: Path = PROJECT_ROOT) -> list[AuthorizationReadiness]:
    """Return only the completion-ready authorizations, project/id-sorted."""
    return sorted(
        (r for r in scan(project_root) if r.completion_ready),
        key=lambda r: (r.project_id, r.authorization_id),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument(
        "--all",
        action="store_true",
        help="report every active authorization, not just completion-ready ones",
    )
    args = parser.parse_args(argv)

    results = scan(PROJECT_ROOT)
    selected = results if args.all else [r for r in results if r.completion_ready]
    selected = sorted(selected, key=lambda r: (r.project_id, r.authorization_id))

    if args.json:
        print(json.dumps([r.as_dict() for r in selected], indent=2))
        return 0

    if not selected:
        print("No completion-ready project authorizations.")
        return 0
    for r in selected:
        flag = "READY" if r.completion_ready else "not-ready"
        print(f"[{flag}] {r.authorization_id} ({r.project_id}) — {r.authorization_name}")
        if r.unverified_work_item_ids:
            print(f"         unverified WIs: {', '.join(r.unverified_work_item_ids)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
