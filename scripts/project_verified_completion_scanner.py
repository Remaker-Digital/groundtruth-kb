#!/usr/bin/env python3
"""Read-only scanner: per-project-authorization VERIFIED-completion readiness.

IP-1 of WI-3316 (bridge thread ``gtkb-project-verified-completion-auq-trigger``).

For every ``status='active'`` project authorization, this scanner determines
whether every work item linked to the authorization's project via an active
project-to-work-item membership link is covered by a bridge thread whose
latest status-bearing numbered bridge file is ``VERIFIED`` (the
``GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`` v2 "explicitly linked"
gating definition). An authorization is *completion-ready* iff its project has
at least one active membership-linked work item and all of them are
VERIFIED-covered.

The scanner is strictly read-only: it issues no DB writes and no bridge-file
writes.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# A bridge proposal/report metadata line: ``Work Item: WI-1234`` (including
# spec-intake ``WI-AUTO-*`` ids, or a GTKB-/WORKLIST- descriptive id),
# optionally backtick-wrapped.
_WORK_ITEM_LINE_RE = re.compile(
    r"^Work Item:\s*`?(WI-AUTO-[A-Z0-9-]+|WI-\d+|GTKB-[A-Z0-9-]+|WORKLIST-[A-Z0-9-]+)`?\s*$",
    re.MULTILINE,
)
_COMPLETION_GUARD_RELATIONSHIP = "plan_incomplete"
_COMPLETION_GUARD_ARTIFACT_TYPES = ("completion_guard", "bridge_thread")


# WI-4737: id-agnostic recognition helpers. A work item whose VERIFIED bridge
# thread carries no regex-parseable ``Work Item:`` line (a non-canonical id, or
# a thread authored before its work item existed) is recognized as
# verified-for-project via its own ``related_bridge_threads`` field instead.
# These two helpers normalize that field and are mirrored byte-for-byte in
# ``groundtruth-kb/src/groundtruth_kb/project/lifecycle.py``.
def _thread_slug_from_ref(ref: object) -> str:
    """Normalize a ``related_bridge_threads`` entry to a bare thread slug.

    Accepts either a bare slug (``gtkb-foo``) or a versioned bridge-file path
    (``bridge/gtkb-foo-003.md``); returns the slug, or ``""`` when empty.
    """
    text = str(ref or "").strip()
    if not text:
        return ""
    base = text.replace("\\", "/").rsplit("/", 1)[-1]
    match = re.match(r"^(?P<slug>.+)-\d{3}\.md$", base)
    if match:
        return match.group("slug")
    if base.endswith(".md"):
        base = base[:-3]
    return base


def _related_thread_slugs(value: object) -> set[str]:
    """Parse a work item's ``related_bridge_threads`` field into a set of slugs.

    The field may be a JSON string, a list, or ``None``; unparseable input
    yields the empty set (defensive — never raises).
    """
    if value is None:
        return set()
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except (ValueError, TypeError):
            return set()
    if not isinstance(value, (list, tuple)):
        return set()
    return {slug for slug in (_thread_slug_from_ref(item) for item in value) if slug}


@dataclass(frozen=True)
class AuthorizationReadiness:
    """Completion-readiness verdict for one project authorization."""

    authorization_id: str
    project_id: str
    authorization_name: str
    included_work_item_ids: list[str]
    verified_work_item_ids: list[str]
    unverified_work_item_ids: list[str]
    completion_guarded: bool
    completion_guard_refs: list[dict[str, Any]]
    completion_ready: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "authorization_id": self.authorization_id,
            "project_id": self.project_id,
            "authorization_name": self.authorization_name,
            "included_work_item_ids": self.included_work_item_ids,
            "verified_work_item_ids": self.verified_work_item_ids,
            "unverified_work_item_ids": self.unverified_work_item_ids,
            "completion_guarded": self.completion_guarded,
            "completion_guard_refs": self.completion_guard_refs,
            "completion_ready": self.completion_ready,
        }


def _ensure_groundtruth_importable(project_root: Path) -> None:
    gt_src = project_root / "groundtruth-kb" / "src"
    if gt_src.is_dir() and str(gt_src) not in sys.path:
        sys.path.insert(0, str(gt_src))


def _implements_links_by_project(project_root: Path) -> dict[str, set[str]]:
    """Return ``{project_id: {bridge_thread_slug}}`` for active implements links.

    v4 PROJECT-SCOPED 'addressing-thread' discriminator per
    ``GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`` v4 clause (a): coverage
    from a bridge thread T accrues ONLY to the project(s) that themselves hold
    an active ``project_artifact_links`` row (``artifact_type = 'bridge_thread'``,
    ``relationship = 'implements'``, ``status = 'active'``) for T's slug. A link
    held by a *different* project does not transfer coverage — this is the fix
    for the cross-project false-positive defect (NO-GO -012 F1): the prior
    global-slug set discarded ``project_id`` and let a PROJECT-A link satisfy a
    PROJECT-B authorization.

    Incidental ``'related'`` / ``'implementation_proposal'`` / ``'source_evidence'``
    links do not contribute. The query reads ``current_project_artifact_links``
    (the latest-version view) so superseded rows do not contribute.
    """
    db_path = project_root / "groundtruth.db"
    if not db_path.is_file():
        return {}
    con = sqlite3.connect(db_path)
    try:
        rows = con.execute(
            "SELECT project_id, artifact_ref FROM current_project_artifact_links "
            "WHERE artifact_type = 'bridge_thread' "
            "AND relationship = 'implements' "
            "AND status = 'active'"
        ).fetchall()
    finally:
        con.close()
    by_project: dict[str, set[str]] = {}
    for project_id, slug in rows:
        if project_id and slug:
            by_project.setdefault(str(project_id), set()).add(str(slug))
    return by_project


def _completion_guards_by_project(project_root: Path) -> dict[str, list[dict[str, Any]]]:
    """Return active ``plan_incomplete`` completion guards keyed by project."""
    db_path = project_root / "groundtruth.db"
    if not db_path.is_file():
        return {}
    con = sqlite3.connect(db_path)
    try:
        rows = con.execute(
            "SELECT project_id, artifact_type, artifact_ref, relationship, notes "
            "FROM current_project_artifact_links "
            "WHERE status = 'active' "
            "AND relationship = ? "
            f"AND artifact_type IN ({', '.join('?' for _ in _COMPLETION_GUARD_ARTIFACT_TYPES)}) "
            "ORDER BY project_id, artifact_type, artifact_ref",
            (_COMPLETION_GUARD_RELATIONSHIP, *_COMPLETION_GUARD_ARTIFACT_TYPES),
        ).fetchall()
    finally:
        con.close()

    guards: dict[str, list[dict[str, Any]]] = {}
    for project_id, artifact_type, artifact_ref, relationship, notes in rows:
        if not project_id:
            continue
        guards.setdefault(str(project_id), []).append(
            {
                "project_id": str(project_id),
                "artifact_type": str(artifact_type or ""),
                "artifact_ref": str(artifact_ref or ""),
                "relationship": str(relationship or ""),
                "notes": notes,
            }
        )
    return guards


def _verified_thread_work_items(project_root: Path) -> dict[str, set[str]]:
    """Return ``{bridge_thread_slug: {work_item_id}}`` for VERIFIED-topped threads.

    Scans ALL versions of each thread whose latest numbered-file status is
    ``VERIFIED`` for ``Work Item:`` metadata lines (D3 corrected scope: per-thread,
    all versions — the top version is the Codex verdict, which carries no
    ``Work Item:`` metadata; the metadata lives in the Prime implementation
    report one or more versions below).
    """
    _ensure_groundtruth_importable(project_root)
    from groundtruth_kb.bridge.versioned_files import status_from_bridge_file

    bridge_dir = project_root / "bridge"
    if not bridge_dir.is_dir():
        return {}
    grouped: dict[str, list[tuple[int, Path]]] = {}
    bridge_file_re = re.compile(r"^(?P<slug>.+)-(?P<version>\d{3})\.md$")
    for path in bridge_dir.glob("*.md"):
        match = bridge_file_re.match(path.name)
        if match is None:
            continue
        grouped.setdefault(match.group("slug"), []).append((int(match.group("version")), path))
    by_thread: dict[str, set[str]] = {}
    for slug, versioned_files in grouped.items():
        latest_path = max(versioned_files, key=lambda item: item[0])[1]
        if status_from_bridge_file(latest_path) != "VERIFIED":
            continue
        wis: set[str] = set()
        for _version, file_path in sorted(versioned_files):
            if not file_path.is_file():
                continue
            text = file_path.read_text(encoding="utf-8", errors="replace")
            for match in _WORK_ITEM_LINE_RE.finditer(text):
                wis.add(match.group(1).strip())
        if wis:
            by_thread[slug] = wis
    return by_thread


def _latest_bridge_thread_statuses(project_root: Path) -> dict[str, str | None]:
    """Return ``{bridge_thread_slug: latest_status}`` from versioned bridge files.

    Mirrors ``ProjectLifecycleService._latest_bridge_thread_statuses``.
    """
    _ensure_groundtruth_importable(project_root)
    from groundtruth_kb.bridge.versioned_files import status_from_bridge_file

    bridge_dir = project_root / "bridge"
    if not bridge_dir.is_dir():
        return {}
    grouped: dict[str, list[tuple[int, Path]]] = {}
    bridge_file_re = re.compile(r"^(?P<slug>.+)-(?P<version>\d{3})\.md$")
    for path in bridge_dir.glob("*.md"):
        match = bridge_file_re.match(path.name)
        if match is None:
            continue
        grouped.setdefault(match.group("slug"), []).append((int(match.group("version")), path))
    return {
        slug: status_from_bridge_file(max(versioned_files, key=lambda item: item[0])[1])
        for slug, versioned_files in grouped.items()
    }


def _augment_verified_with_related_threads(
    verified_by_project: dict[str, set[str]],
    links_by_project: dict[str, set[str]],
    project_root: Path,
) -> None:
    """WI-4737 additive recognition path (mirrors lifecycle.py).

    A work item counts as verified-for-project when it is an active member of
    the project AND its own ``related_bridge_threads`` names a VERIFIED-topped
    thread that the project holds an active ``implements`` link to. Opens a
    read-only DB connection only when at least one VERIFIED implements-linked
    thread exists; closes it before returning.
    """
    statuses_by_thread = _latest_bridge_thread_statuses(project_root)
    verified_slugs_by_project = {
        project_id: {s for s in slugs if statuses_by_thread.get(s) == "VERIFIED"}
        for project_id, slugs in links_by_project.items()
    }
    if not any(verified_slugs_by_project.values()):
        return
    db_path = project_root / "groundtruth.db"
    if not db_path.is_file():
        return
    _ensure_groundtruth_importable(project_root)
    from groundtruth_kb.db import KnowledgeDB

    db = KnowledgeDB(db_path)
    try:
        for project_id, verified_implements_slugs in verified_slugs_by_project.items():
            if not verified_implements_slugs:
                continue
            verified = verified_by_project.setdefault(project_id, set())
            for membership in db.list_project_work_items(project_id):
                if str(membership.get("membership_status") or "").strip().lower() != "active":
                    continue
                work_item_id = str(membership.get("work_item_id") or "")
                if not work_item_id or work_item_id in verified:
                    continue
                work_item = db.get_work_item(work_item_id)
                if work_item is None:
                    continue
                if _related_thread_slugs(work_item.get("related_bridge_threads")) & verified_implements_slugs:
                    verified.add(work_item_id)
    finally:
        db.close()


def verified_work_items_by_project(project_root: Path) -> dict[str, set[str]]:
    """Return ``{project_id: {verified work_item_id}}`` (project-scoped; closes F1).

    A work item WI-X is VERIFIED *for project P* (per
    ``GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`` v4) iff P holds an active
    ``relationship='implements'`` link to a VERIFIED-topped bridge thread that
    either (regex path) cites WI-X in a ``Work Item:`` line, or (WI-4737
    id-agnostic path) is named in WI-X's own ``related_bridge_threads`` while
    WI-X is an active member of P. Coverage is attributed to the linking project
    only: a thread implements-linked to PROJECT-A contributes WI metadata to
    PROJECT-A's verified set and to no other project, even if a different
    project's gating WI is cited in that thread.

    This replaces the prior global ``verified_work_items() -> set[str]`` whose
    project-blind union was the NO-GO -012 F1 cross-project false-positive
    defect. There is intentionally no global-set decision function: the only
    completion-authorizing view is project-scoped.
    """
    links_by_project = _implements_links_by_project(project_root)
    wis_by_thread = _verified_thread_work_items(project_root)
    verified_by_project: dict[str, set[str]] = {}
    for project_id, slugs in links_by_project.items():
        verified: set[str] = set()
        for slug in slugs:
            verified |= wis_by_thread.get(slug, set())
        verified_by_project[project_id] = verified
    # WI-4737 additive id-agnostic recognition path (mirrors lifecycle.py).
    _augment_verified_with_related_threads(verified_by_project, links_by_project, project_root)
    return verified_by_project


def _project_membership_work_item_ids(db: Any, project_id: str) -> list[str]:
    """Return the work-item ids linked to ``project_id`` via an active
    project-to-work-item membership link.

    GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v2 defines the
    completion-gating set as the project's explicitly-linked work items - the
    active project-to-work-item membership links - not the authorization
    envelope's ``included_work_item_ids`` list. ``ProjectLifecycleService``
    sources the gating set the same way so the scanner and the service agree.
    """
    if not project_id:
        return []
    memberships = db.list_project_work_items(project_id)
    return [
        str(membership["work_item_id"])
        for membership in memberships
        if str(membership.get("membership_status") or "").strip().lower() == "active"
    ]


def scan(project_root: Path = PROJECT_ROOT) -> list[AuthorizationReadiness]:
    """Compute completion readiness for every active project authorization.

    Read-only: opens MemBase for reads only and closes it before returning.
    """
    _ensure_groundtruth_importable(project_root)
    from groundtruth_kb.db import KnowledgeDB

    db = KnowledgeDB(project_root / "groundtruth.db")
    try:
        active = db.list_project_authorizations(status="active")
        gating_by_project: dict[str, list[str]] = {}
        for authorization in active:
            project_id = str(authorization.get("project_id") or "")
            if project_id and project_id not in gating_by_project:
                gating_by_project[project_id] = _project_membership_work_item_ids(db, project_id)
    finally:
        db.close()

    verified_by_project = verified_work_items_by_project(project_root)
    guards_by_project = _completion_guards_by_project(project_root)
    results: list[AuthorizationReadiness] = []
    for authorization in active:
        project_id = str(authorization.get("project_id") or "")
        included = gating_by_project.get(project_id, [])
        # Project-scoped (v4 F1 fix): a WI counts as verified for THIS project
        # only via this project's own implements-linked VERIFIED threads.
        project_verified = verified_by_project.get(project_id, set())
        verified_ids = [wi for wi in included if wi in project_verified]
        unverified_ids = [wi for wi in included if wi not in project_verified]
        guard_refs = guards_by_project.get(project_id, [])
        completion_guarded = bool(guard_refs)
        completion_ready = bool(included) and not unverified_ids and not completion_guarded
        results.append(
            AuthorizationReadiness(
                authorization_id=str(authorization.get("id") or ""),
                project_id=project_id,
                authorization_name=str(authorization.get("authorization_name") or ""),
                included_work_item_ids=included,
                verified_work_item_ids=verified_ids,
                unverified_work_item_ids=unverified_ids,
                completion_guarded=completion_guarded,
                completion_guard_refs=guard_refs,
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
        if r.completion_guarded:
            refs = ", ".join(
                f"{ref['artifact_type']}:{ref['artifact_ref']} ({ref['relationship']})"
                for ref in r.completion_guard_refs
            )
            print(f"         completion guard: {refs}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
