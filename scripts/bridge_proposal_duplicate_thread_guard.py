#!/usr/bin/env python3
"""Pre-filing duplicate-live-thread guard for bridge proposals (WI-4573, B#3).

When a NEW bridge proposal is filed, this advisory guard warns if the declared
``Work Item:`` already has a *non-terminal* bridge thread under a **different
slug**. Concurrent swarm sessions filing duplicate proposals for one work item
under different slugs have twice produced owner-AUQ reconciliation (Slice-C
duplicate ADRs; WI-4510 duplicate cutover proposals); the per-thread slug is the
only collision guard, so a same-work-item duplicate is otherwise invisible at
propose-time.

This guard reads canonical TAFE/dispatcher bridge state via
``groundtruth_kb.bridge.read_commands.threads_for_work_item`` (the API backing
``gt bridge threads --wi``). It MUST NOT scan the retired ``bridge/INDEX.md``
aggregate (the 2026-06-15 cutover removed aggregate-queue authority; WI-4573's
original "scan INDEX.md" description predates that cutover).

It is distinct from ``scripts/bridge_proposal_wi_id_collision_check.py``, which
checks cited-id-vs-declared-WI collisions *inside one proposal*; this guard
detects the *same work item carried by another live thread across the bridge*.

Advisory-first: default exit 0; ``--strict`` returns a non-zero exit when a
duplicate live thread is found. No hard gate is introduced.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]

EXIT_OK = 0
EXIT_STRICT_DUPLICATES = 5

# Non-terminal proposal-lifecycle states: a thread in one of these is a live,
# competing proposal for the same work item. Terminal / non-competing states
# (VERIFIED, WITHDRAWN, DEFERRED) and ADVISORY are intentionally excluded.
LIVE_STATUSES = frozenset({"NEW", "REVISED", "GO", "NO-GO"})

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

# Reuse the Work Item parsing contract from the sibling collision checker so the
# two guards agree on what "declared work item" means (GO condition).
from bridge_proposal_wi_id_collision_check import parse_declared_work_item  # noqa: E402


@dataclass(frozen=True)
class DuplicateThread:
    slug: str
    latest_status: str
    latest_path: str

    def to_dict(self) -> dict[str, str]:
        return {"slug": self.slug, "latest_status": self.latest_status, "latest_path": self.latest_path}


def _ensure_groundtruth_importable(project_root: Path) -> None:
    gt_src = project_root / "groundtruth-kb" / "src"
    if gt_src.is_dir() and str(gt_src) not in sys.path:
        sys.path.insert(0, str(gt_src))


def find_duplicate_live_threads(
    project_root: Path,
    declared_wi: str,
    own_slug: str | None,
) -> list[DuplicateThread]:
    """Return live threads citing ``declared_wi`` under a slug != ``own_slug``."""
    _ensure_groundtruth_importable(project_root)
    from groundtruth_kb.bridge.read_commands import threads_for_work_item

    result = threads_for_work_item(project_root, declared_wi)
    duplicates: list[DuplicateThread] = []
    for thread in result.get("threads", []):
        slug = thread.get("slug")
        status = thread.get("latest_status")
        if status not in LIVE_STATUSES:
            continue
        if own_slug is not None and slug == own_slug:
            continue
        duplicates.append(
            DuplicateThread(
                slug=slug,
                latest_status=status,
                latest_path=thread.get("latest_path", ""),
            )
        )
    duplicates.sort(key=lambda item: item.slug)
    return duplicates


def _resolve_content(project_root: Path, bridge_id: str | None, content_file: str | None) -> tuple[str, str | None]:
    """Return ``(proposal_text, own_slug)`` from --content-file or --bridge-id."""
    if content_file:
        return Path(content_file).read_text(encoding="utf-8"), None
    if not bridge_id:
        raise ValueError("either --bridge-id or --content-file is required")
    # --bridge-id: own_slug is the bridge id; read the initial proposal version.
    bridge_file = project_root / "bridge" / f"{bridge_id}-001.md"
    if not bridge_file.is_file():
        raise FileNotFoundError(f"No initial proposal found for bridge {bridge_id!r}: {bridge_file}")
    return bridge_file.read_text(encoding="utf-8"), bridge_id


def run_guard(
    project_root: Path,
    *,
    bridge_id: str | None = None,
    content_file: str | None = None,
    own_slug: str | None = None,
    strict: bool = False,
) -> tuple[dict[str, Any], int]:
    """Run the advisory duplicate-live-thread guard."""
    result: dict[str, Any] = {
        "bridge_id": bridge_id,
        "content_file": content_file,
        "declared_work_item": None,
        "own_slug": own_slug,
        "duplicate_threads": [],
        "strict": strict,
        "verdict": "clean",
        "message": "",
    }

    try:
        text, resolved_slug = _resolve_content(project_root, bridge_id, content_file)
    except (OSError, ValueError) as exc:
        result["verdict"] = "error"
        result["message"] = str(exc)
        return result, EXIT_STRICT_DUPLICATES if strict else EXIT_OK

    effective_slug = own_slug or resolved_slug
    result["own_slug"] = effective_slug

    declared = parse_declared_work_item(text)
    result["declared_work_item"] = declared
    if not declared:
        result["verdict"] = "no_work_item"
        result["message"] = "no declared Work Item; duplicate-thread check skipped"
        return result, EXIT_OK

    try:
        duplicates = find_duplicate_live_threads(project_root, declared, effective_slug)
    except ValueError as exc:
        # Malformed / multi-WI declared value: threads_for_work_item rejects it.
        result["verdict"] = "unparseable_work_item"
        result["message"] = f"declared Work Item not a single resolvable id: {exc}"
        return result, EXIT_OK

    result["duplicate_threads"] = [item.to_dict() for item in duplicates]
    has_duplicates = bool(duplicates)
    result["verdict"] = "duplicates" if has_duplicates else "clean"
    result["message"] = (
        f"{len(duplicates)} live thread(s) already cite {declared} under a different slug"
        if has_duplicates
        else f"no other live thread cites {declared}"
    )
    if strict and has_duplicates:
        return result, EXIT_STRICT_DUPLICATES
    return result, EXIT_OK


def format_markdown(result: dict[str, Any]) -> str:
    lines = [
        "## Duplicate-Live-Thread Guard",
        "",
        f"- declared_work_item: `{result.get('declared_work_item') or '(none)'}`",
        f"- own_slug: `{result.get('own_slug') or '(unset)'}`",
        f"- verdict: `{result['verdict']}`",
        f"- strict: `{str(result['strict']).lower()}`",
        f"- duplicate_threads: `{json.dumps(result['duplicate_threads'])}`",
        f"- message: `{result['message']}`",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--bridge-id", default=None, help="Bridge document id (slug)")
    source.add_argument("--content-file", default=None, help="Draft proposal markdown file to inspect")
    parser.add_argument("--slug", default=None, help="Proposal's own slug to exclude from duplicate detection")
    parser.add_argument("--project-root", default=None, help="GT-KB project root")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of markdown")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when a duplicate live thread is found")
    args = parser.parse_args(argv)

    project_root = Path(args.project_root).resolve() if args.project_root else PROJECT_ROOT
    result, exit_code = run_guard(
        project_root,
        bridge_id=args.bridge_id,
        content_file=args.content_file,
        own_slug=args.slug,
        strict=args.strict,
    )
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(format_markdown(result))
    return exit_code if args.strict else EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
