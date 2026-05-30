#!/usr/bin/env python3
"""Phase-2 deterministic backfill of project->bridge-thread ``implements`` links.

WI-3462 (PROJECT-GTKB-RELIABILITY-FIXES). Bridge thread
``gtkb-implements-link-backfill-phase2-implementation`` (GO at -002); scoping GO
``gtkb-implements-link-backfill-phase2-scoping-002``; owner authorization
``DELIB-2510`` -> ``PAUTH-WI-3462-PHASE2-IMPLEMENTS-BACKFILL-001`` (allowed
mutation class ``project-artifact-link-insert``).

Background. ``GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`` v4 (VERIFIED on
``gtkb-project-completion-scanner-addressing-thread-fix-017``) made project
auto-completion fire only when a project P holds an active
``project_artifact_links`` row (``artifact_type='bridge_thread'``,
``relationship='implements'``, ``status='active'``) to a VERIFIED-topped bridge
thread that cites each of P's gating work items. At v4 landing zero such links
existed platform-wide, so auto-completion is fail-safe-paused everywhere. This
tool arms v4 by backfilling those links for projects whose addressing thread is
deterministically unambiguous.

Design (per the scoping GO). For each active-authorization project, discover the
gating work items (active membership links) and the candidate "addressing
threads" (bridge threads whose version files declare ``Work Item: <WI>``, ANY
status). Classify:

- CLEAN: every gating WI resolves (after the D3 rule) to exactly one addressing
  thread. ``--apply`` inserts one ``implements`` link per distinct resolved
  thread, skipping links that already exist (idempotent).
- AMBIGUOUS: at least one gating WI still has >1 candidate after the D3 rule.
  Left UNLINKED and surfaced for owner AUQ (fail-closed).
- UNADDRESSED: at least one gating WI has no candidate addressing thread. Left
  untouched (there is no thread to link).

D3 ambiguity rule (GO'd): for a gating WI mapping to >1 candidate thread,
(1) drop ``*-scoping`` threads when a non-scoping sibling cites the same WI; and
(2) drop a superseded thread when its superseder also cites the same WI. If
exactly one candidate survives, link it; otherwise fail closed to AUQ.

Safety. ``--report`` (and the default no-arg mode) is strictly read-only.
``--apply`` refreshes discovery immediately before mutating, mutates only via the
deterministic ``KnowledgeDB.add_project_artifact_link`` API (no hand-written SQL
edits), is idempotent, and never marks a project complete: v4 still requires all
gating WIs VERIFIED before completion. ``project_artifact_links`` is
append-only/versioned, so a wrong link is corrected by a status-change
supersession, never a destructive delete.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CHANGED_BY = "prime-builder/claude/B"
CHANGE_REASON = (
    "Phase-2 implements-link backfill (WI-3462; "
    "PAUTH-WI-3462-PHASE2-IMPLEMENTS-BACKFILL-001; DELIB-2510); "
    "bridge/gtkb-implements-link-backfill-phase2-implementation"
)

# A ``Work Item: WI-1234`` metadata declaration line (same id grammar the v4
# scanner uses). Only metadata-declaration lines count as an addressing-thread
# signal; prose mentions in other sections are not ``^Work Item:`` lines.
_WORK_ITEM_LINE_RE = re.compile(
    r"^Work Item:\s*`?(WI-AUTO-[A-Z0-9-]+|WI-\d+|GTKB-[A-Z0-9-]+|WORKLIST-[A-Z0-9-]+)`?\s*$",
    re.MULTILINE,
)

# A bridge-thread document slug referenced inside a "Supersedes" line, e.g.
# ``Supersedes implementation thread: bridge/gtkb-foo-001.md`` ->  ``gtkb-foo``.
_SUPERSEDE_LINE_RE = re.compile(r"^.*supersede.*$", re.IGNORECASE | re.MULTILINE)
_BRIDGE_SLUG_REF_RE = re.compile(r"bridge/([a-z0-9][a-z0-9-]*?)(?:-\d+)?\.md")
# A bare slug after ``thread:`` (no bridge/ prefix, no -NNN.md), e.g.
# ``Supersedes implementation thread: gtkb-foo (latest GO -019)``.
_SUPERSEDE_BARE_SLUG_RE = re.compile(
    r"supersedes[^:\n]*thread:\s*`?([a-z0-9][a-z0-9-]+?)`?(?:\s|\(|$)",
    re.IGNORECASE,
)

_SCOPING_SUFFIX = "-scoping"


def _ensure_groundtruth_importable(project_root: Path) -> None:
    gt_src = project_root / "groundtruth-kb" / "src"
    if gt_src.is_dir() and str(gt_src) not in sys.path:
        sys.path.insert(0, str(gt_src))


@dataclass
class ThreadInfo:
    """All-status bridge-thread facts the backfill needs."""

    slug: str
    top_status: str
    work_items: set[str] = field(default_factory=set)
    supersedes: set[str] = field(default_factory=set)


def scan_all_threads(project_root: Path) -> dict[str, ThreadInfo]:
    """Return ``{slug: ThreadInfo}`` for every document in ``bridge/INDEX.md``.

    Unlike the v4 scanner (which only reads VERIFIED-topped threads), the
    backfill needs candidates of ANY status: an addressing thread may still be
    GO/in-flight when its project is backfilled, and the v4 completion gate will
    simply stay paused for that project until the thread reaches VERIFIED.
    """
    _ensure_groundtruth_importable(project_root)
    from groundtruth_kb.bridge.detector import parse_index

    index_path = project_root / "bridge" / "INDEX.md"
    if not index_path.is_file():
        return {}
    result = parse_index(index_path.read_text(encoding="utf-8"), project_root=project_root)

    threads: dict[str, ThreadInfo] = {}
    for document in result.documents:
        top = document.current_top
        info = ThreadInfo(
            slug=document.name,
            top_status=(
                top.status.value if top is not None and hasattr(top.status, "value") else str(top.status) if top else ""
            ),
        )
        for version in document.versions:
            file_path = project_root / version.file_path
            if not file_path.is_file():
                continue
            text = file_path.read_text(encoding="utf-8", errors="replace")
            for match in _WORK_ITEM_LINE_RE.finditer(text):
                info.work_items.add(match.group(1).strip())
            for line in _SUPERSEDE_LINE_RE.findall(text):
                for ref in _BRIDGE_SLUG_REF_RE.findall(line):
                    if ref != document.name:
                        info.supersedes.add(ref)
                bare = _SUPERSEDE_BARE_SLUG_RE.search(line)
                if bare and bare.group(1) != document.name:
                    info.supersedes.add(bare.group(1))
        threads[document.name] = info
    return threads


def _candidates_for_wi(wi: str, threads: dict[str, ThreadInfo]) -> set[str]:
    """All thread slugs (any status) that declare ``Work Item: <wi>``."""
    return {slug for slug, info in threads.items() if wi in info.work_items}


def resolve_addressing_thread(wi: str, threads: dict[str, ThreadInfo]) -> tuple[set[str], str]:
    """Apply the GO'd D3 rule to a gating WI's candidate set.

    Returns ``(surviving_slugs, reason)``. ``reason`` is one of:
      - ``"unaddressed"``    -> 0 candidates;
      - ``"clean"``          -> exactly 1 surviving candidate;
      - ``"ambiguous"``      -> >1 surviving candidate after the rule.
    """
    candidates = _candidates_for_wi(wi, threads)
    if not candidates:
        return set(), "unaddressed"
    if len(candidates) == 1:
        return candidates, "clean"

    survivors = set(candidates)

    # D3 filter 1: drop *-scoping threads when a non-scoping sibling cites the WI.
    non_scoping = {s for s in survivors if not s.endswith(_SCOPING_SUFFIX)}
    if non_scoping and non_scoping != survivors:
        survivors = non_scoping

    # D3 filter 2: drop a superseded thread when a surviving superseder also
    # cites the WI. A thread S is dropped if some surviving S' lists S in its
    # ``supersedes`` set.
    superseded: set[str] = set()
    for superseder in survivors:
        for victim in threads[superseder].supersedes:
            if victim in survivors:
                superseded.add(victim)
    survivors -= superseded

    if len(survivors) == 1:
        return survivors, "clean"
    if not survivors:
        # Pathological: the rule eliminated everything (mutual supersession).
        # Fail closed rather than guess.
        return candidates, "ambiguous"
    return survivors, "ambiguous"


@dataclass
class ProjectClassification:
    project_id: str
    authorization_id: str
    gating_work_items: list[str]
    classification: str  # "clean" | "ambiguous" | "unaddressed"
    # wi -> resolved single addressing thread (clean WIs only)
    resolved_links: dict[str, str] = field(default_factory=dict)
    unaddressed_work_items: list[str] = field(default_factory=list)
    ambiguous_work_items: dict[str, list[str]] = field(default_factory=dict)
    already_linked: set[str] = field(default_factory=set)

    def as_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "authorization_id": self.authorization_id,
            "gating_work_items": self.gating_work_items,
            "classification": self.classification,
            "resolved_links": self.resolved_links,
            "unaddressed_work_items": self.unaddressed_work_items,
            "ambiguous_work_items": self.ambiguous_work_items,
            "already_linked": sorted(self.already_linked),
        }


def discover(project_root: Path = PROJECT_ROOT) -> list[ProjectClassification]:
    """Classify every active-authorization project. Strictly read-only."""
    _ensure_groundtruth_importable(project_root)
    from groundtruth_kb.db import KnowledgeDB

    # Reuse the v4 scanner primitives so classification stays parity-identical.
    from project_verified_completion_scanner import (
        _implements_links_by_project,
        _project_membership_work_item_ids,
    )

    threads = scan_all_threads(project_root)
    existing_links = _implements_links_by_project(project_root)

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

    results: list[ProjectClassification] = []
    seen_projects: set[str] = set()
    for authorization in active:
        project_id = str(authorization.get("project_id") or "")
        if not project_id or project_id in seen_projects:
            continue
        seen_projects.add(project_id)
        gating = gating_by_project.get(project_id, [])
        already = existing_links.get(project_id, set())

        resolved_links: dict[str, str] = {}
        unaddressed: list[str] = []
        ambiguous: dict[str, list[str]] = {}
        for wi in gating:
            survivors, reason = resolve_addressing_thread(wi, threads)
            if reason == "clean":
                resolved_links[wi] = next(iter(survivors))
            elif reason == "unaddressed":
                unaddressed.append(wi)
            else:
                ambiguous[wi] = sorted(survivors)

        if not gating:
            classification = "unaddressed"  # nothing to arm
        elif ambiguous:
            classification = "ambiguous"
        elif unaddressed:
            classification = "unaddressed"
        else:
            classification = "clean"

        results.append(
            ProjectClassification(
                project_id=project_id,
                authorization_id=str(authorization.get("id") or ""),
                gating_work_items=gating,
                classification=classification,
                resolved_links=resolved_links,
                unaddressed_work_items=unaddressed,
                ambiguous_work_items=ambiguous,
                already_linked=already,
            )
        )
    return sorted(results, key=lambda r: (r.project_id, r.authorization_id))


def apply_backfill(
    project_root: Path = PROJECT_ROOT,
    *,
    changed_by: str = CHANGED_BY,
    change_reason: str = CHANGE_REASON,
) -> dict[str, Any]:
    """Insert implements-links for CLEAN projects. Idempotent.

    Refreshes discovery immediately before mutating (the live classification is
    recomputed inside this call, not read from a stale ``--report``). For each
    CLEAN project, inserts one ``implements`` link per distinct resolved
    addressing thread that is not already implements-linked to the project.
    Returns the inserted link records + skipped (already-linked) records +
    the AMBIGUOUS projects surfaced for owner AUQ.
    """
    _ensure_groundtruth_importable(project_root)
    from groundtruth_kb.db import KnowledgeDB

    classifications = discover(project_root)  # refresh-before-mutation

    inserted: list[dict[str, str]] = []
    skipped: list[dict[str, str]] = []
    needs_owner_auq: list[dict[str, Any]] = []

    db = KnowledgeDB(project_root / "groundtruth.db")
    try:
        for pc in classifications:
            if pc.classification == "ambiguous":
                needs_owner_auq.append(pc.as_dict())
                continue
            if pc.classification != "clean":
                continue  # unaddressed: untouched
            wanted_slugs = sorted(set(pc.resolved_links.values()))
            for slug in wanted_slugs:
                if slug in pc.already_linked:
                    skipped.append({"project_id": pc.project_id, "thread": slug, "reason": "already_linked"})
                    continue
                row = db.add_project_artifact_link(
                    pc.project_id,
                    "bridge_thread",
                    slug,
                    changed_by,
                    change_reason,
                    relationship="implements",
                )
                inserted.append(
                    {
                        "project_id": pc.project_id,
                        "thread": slug,
                        "link_id": str(row.get("id")) if row else "",
                        "version": str(row.get("version")) if row else "",
                    }
                )
    finally:
        db.close()

    return {
        "inserted": inserted,
        "skipped": skipped,
        "needs_owner_auq": needs_owner_auq,
        "clean_projects": [pc.project_id for pc in classifications if pc.classification == "clean"],
        "ambiguous_projects": [pc.project_id for pc in classifications if pc.classification == "ambiguous"],
        "unaddressed_projects": [pc.project_id for pc in classifications if pc.classification == "unaddressed"],
    }


def _format_report(classifications: list[ProjectClassification]) -> str:
    buckets = {"clean": [], "ambiguous": [], "unaddressed": []}
    for pc in classifications:
        buckets[pc.classification].append(pc)
    lines: list[str] = ["Phase-2 implements-link backfill - discovery report", ""]
    lines.append(
        f"CLEAN={len(buckets['clean'])}  AMBIGUOUS={len(buckets['ambiguous'])}  "
        f"UNADDRESSED={len(buckets['unaddressed'])}  (total {len(classifications)})"
    )
    for bucket in ("clean", "ambiguous", "unaddressed"):
        if not buckets[bucket]:
            continue
        lines.append("")
        lines.append(f"== {bucket.upper()} ==")
        for pc in buckets[bucket]:
            lines.append(f"  {pc.project_id} ({pc.authorization_id})")
            if pc.resolved_links:
                for wi, slug in sorted(pc.resolved_links.items()):
                    flag = " [already-linked]" if slug in pc.already_linked else ""
                    lines.append(f"      {wi} -> {slug}{flag}")
            for wi in pc.unaddressed_work_items:
                lines.append(f"      {wi} -> (no addressing thread)")
            for wi, slugs in sorted(pc.ambiguous_work_items.items()):
                lines.append(f"      {wi} -> AMBIGUOUS: {', '.join(slugs)}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--report", action="store_true", help="read-only discovery report (default)")
    mode.add_argument("--apply", action="store_true", help="insert implements-links for CLEAN projects (idempotent)")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args(argv)

    if args.apply:
        result = apply_backfill(PROJECT_ROOT)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(
                f"applied: inserted={len(result['inserted'])} "
                f"skipped={len(result['skipped'])} "
                f"needs_owner_auq={len(result['needs_owner_auq'])}"
            )
            for ins in result["inserted"]:
                print(f"  + {ins['project_id']} -> {ins['thread']} ({ins['link_id']} v{ins['version']})")
            for sk in result["skipped"]:
                print(f"  = {sk['project_id']} -> {sk['thread']} (already linked)")
            if result["needs_owner_auq"]:
                print("  ! AMBIGUOUS projects need owner AUQ (left unlinked):")
                for pc in result["needs_owner_auq"]:
                    print(f"    - {pc['project_id']}: {pc['ambiguous_work_items']}")
        return 0

    # default + --report: read-only
    classifications = discover(PROJECT_ROOT)
    if args.json:
        print(json.dumps([pc.as_dict() for pc in classifications], indent=2))
    else:
        print(_format_report(classifications))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
