#!/usr/bin/env python3
"""Report-only per-thread finalization repair planner for WI-5116."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GT_SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if str(GT_SRC) not in sys.path:
    sys.path.insert(0, str(GT_SRC))
if str(PROJECT_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import worktree_finalization_triage as triage  # noqa: E402
from implementation_authorization import AuthorizationError, extract_target_paths  # noqa: E402

BRIDGE_VERSION_RE = re.compile(r"^bridge/(?P<slug>.+)-(?P<version>\d{3})\.md$")
RESPONDS_TO_RE = re.compile(r"^Responds to:\s*(?:GO\s+)?(?P<path>bridge/[^\s]+-\d{3}\.md)", re.MULTILINE)
WORK_ITEM_RE = re.compile(r"\bWI-?\d+\b", re.IGNORECASE)
STATUS_TOKENS = {
    "ACCEPTED",
    "ADVISORY",
    "BLOCKED",
    "DEFERRED",
    "GO",
    "NEW",
    "NO-ACTION",
    "NO-GO",
    "REVISED",
    "VERIFIED",
    "WITHDRAWN",
}
IN_FLIGHT_STATUSES = {"ADVISORY", "DEFERRED", "GO", "NEW", "NO-ACTION", "NO-GO", "REVISED"}
DOCUMENTATION_TERMINAL_STATUSES = {"ACCEPTED", "BLOCKED", "WITHDRAWN"}
TRACKED_TERMINAL_VERDICT_CHANGE_KINDS = {"deleted", "modified"}


@dataclass(frozen=True)
class BridgeVersion:
    slug: str
    version: int
    rel_path: str
    status: str
    text: str


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run_git(root: Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout


def _normalize_path(path: str) -> str:
    return path.replace("\\", "/").strip()


def _first_nonblank_status(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            token = stripped.split(maxsplit=1)[0].upper()
            return token if token in STATUS_TOKENS else "UNKNOWN"
    return "UNKNOWN"


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _bridge_slug(path: str) -> str | None:
    match = BRIDGE_VERSION_RE.match(_normalize_path(path))
    return match.group("slug") if match else None


def _chain(root: Path, slug: str) -> list[BridgeVersion]:
    versions: list[BridgeVersion] = []
    bridge_dir = root / "bridge"
    if not bridge_dir.is_dir():
        return versions
    pattern = re.compile(rf"^{re.escape(slug)}-(?P<version>\d{{3}})\.md$")
    for path in bridge_dir.glob(f"{slug}-*.md"):
        match = pattern.match(path.name)
        if not match:
            continue
        text = _read_text(path)
        versions.append(
            BridgeVersion(
                slug=slug,
                version=int(match.group("version")),
                rel_path=f"bridge/{path.name}",
                status=_first_nonblank_status(text),
                text=text,
            )
        )
    return sorted(versions, key=lambda item: item.version)


def _work_items(slug: str, versions: list[BridgeVersion]) -> list[str]:
    found: set[str] = set()
    for raw in WORK_ITEM_RE.findall(slug):
        found.add(_normalize_wi(raw))
    for version in versions:
        for raw in WORK_ITEM_RE.findall(version.text):
            found.add(_normalize_wi(raw))
    return sorted(found)


def _normalize_wi(value: str) -> str:
    text = value.strip().upper()
    if text.startswith("WI-"):
        return text
    if text.startswith("WI"):
        return "WI-" + text[2:].lstrip("-")
    return text


def _is_excluded(slug: str, work_items: list[str], excluded: set[str]) -> bool:
    slug_text = slug.upper().replace("-", "")
    for wi in excluded:
        if wi in work_items:
            return True
        if wi.replace("-", "") in slug_text:
            return True
    return False


def _git_status_lines(root: Path, rel_path: str) -> list[str]:
    output = _run_git(root, ["status", "--porcelain=v1", "--untracked-files=all", "--", rel_path])
    return [line for line in output.splitlines() if line.strip()]


def _extract_targets(report_text: str) -> tuple[list[str] | None, str | None]:
    try:
        targets = [_normalize_path(path) for path in extract_target_paths(report_text)]
    except AuthorizationError as exc:
        return None, str(exc)
    except Exception as exc:  # noqa: BLE001 - report-only diagnostic
        return None, f"target path extraction failed: {exc}"
    if not targets:
        return None, "no target paths found"
    return sorted(dict.fromkeys(targets)), None


def _responded_report(root: Path, latest: BridgeVersion) -> tuple[str | None, str]:
    match = RESPONDS_TO_RE.search(latest.text)
    if not match:
        return None, "latest VERIFIED verdict has no Responds to report reference"
    rel_path = _normalize_path(match.group("path"))
    if not (root / rel_path).is_file():
        return None, f"responded-to report is missing: {rel_path}"
    return rel_path, ""


def _dirty_items_by_slug(plan: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in plan.get("items", []):
        path = str(item.get("path") or "")
        slug = _bridge_slug(path)
        if slug is None:
            continue
        grouped.setdefault(slug, []).append(item)
    return grouped


def _non_bridge_dirty_paths(plan: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    for item in plan.get("items", []):
        path = str(item.get("path") or "")
        if not _bridge_slug(path):
            paths.append(path)
    return sorted(paths)


def _tracked_terminal_verified_verdict_dirt(dirty_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    hazards: list[dict[str, Any]] = []
    for item in dirty_items:
        if not item.get("tracked"):
            continue
        if str(item.get("bridge_status") or "").upper() != "VERIFIED":
            continue
        change_kind = str(item.get("change_kind") or "").lower()
        if change_kind not in TRACKED_TERMINAL_VERDICT_CHANGE_KINDS:
            continue
        hazards.append(
            {
                "path": item.get("path"),
                "change_kind": change_kind,
                "git_status": item.get("git_status"),
                "reason": item.get("reason"),
            }
        )
    return hazards


def _thread_base(slug: str, versions: list[BridgeVersion], dirty_items: list[dict[str, Any]]) -> dict[str, Any]:
    latest = versions[-1] if versions else None
    return {
        "thread_slug": slug,
        "latest_status": latest.status if latest else "UNKNOWN",
        "latest_path": latest.rel_path if latest else None,
        "version_count": len(versions),
        "dirty_bridge_paths": [
            item.get("path") for item in sorted(dirty_items, key=lambda value: str(value.get("path")))
        ],
        "work_items": _work_items(slug, versions),
    }


def _terminal_verified_plan(
    root: Path,
    base: dict[str, Any],
    versions: list[BridgeVersion],
    target_claims: dict[str, list[str]],
) -> dict[str, Any]:
    latest = versions[-1]
    report_rel, report_error = _responded_report(root, latest)
    if report_rel is None:
        base.update(
            {
                "classification": "terminal_verified_blocked_missing_scope",
                "stop": True,
                "reason": report_error,
            }
        )
        return base

    targets, target_error = _extract_targets(_read_text(root / report_rel))
    if targets is None:
        base.update(
            {
                "classification": "terminal_verified_blocked_missing_scope",
                "stop": True,
                "responds_to": report_rel,
                "reason": target_error,
            }
        )
        return base

    conflicts = {
        path: sorted(set(target_claims.get(path, []))) for path in targets if len(set(target_claims.get(path, []))) > 1
    }
    if conflicts:
        base.update(
            {
                "classification": "mixed_provenance_stop",
                "stop": True,
                "responds_to": report_rel,
                "target_paths": targets,
                "conflicting_target_owners": conflicts,
                "reason": "one or more target paths are claimed by multiple dirty terminal VERIFIED threads",
            }
        )
        return base

    dirty_targets = {path: _git_status_lines(root, path) for path in targets if _git_status_lines(root, path)}
    base.update({"responds_to": report_rel, "target_paths": targets})
    if dirty_targets:
        base.update(
            {
                "classification": "terminal_verified_blocked_dirty_targets",
                "stop": True,
                "dirty_targets": dirty_targets,
                "reason": "implementation/report target paths are still dirty or untracked",
            }
        )
        return base

    base.update(
        {
            "classification": "terminal_verified_repair_candidate",
            "stop": False,
            "reason": "terminal VERIFIED verdict has parseable target paths and those target paths are clean",
            "suggested_next_steps": [
                "Re-run this planner immediately before acting.",
                "Confirm the terminal verdict is independent and still latest.",
                "Use the standard finalization path or approved verdict-chain-only equivalent; do not add unrelated paths.",
            ],
        }
    )
    return base


def _classify_thread(
    root: Path,
    slug: str,
    dirty_items: list[dict[str, Any]],
    excluded: set[str],
    target_claims: dict[str, list[str]],
) -> dict[str, Any]:
    versions = _chain(root, slug)
    base = _thread_base(slug, versions, dirty_items)
    latest_status = base["latest_status"]

    if _is_excluded(slug, base["work_items"], excluded):
        base.update(
            {
                "classification": "excluded_active_program",
                "stop": True,
                "reason": "thread matches an explicitly excluded active handoff scope",
            }
        )
        return base

    terminal_verdict_dirt = _tracked_terminal_verified_verdict_dirt(dirty_items)
    if terminal_verdict_dirt:
        base.update(
            {
                "classification": "mixed_provenance_stop",
                "stop": True,
                "dirty_terminal_verdicts": terminal_verdict_dirt,
                "reason": "tracked modified or deleted terminal VERIFIED verdict requires exact byte ownership before finalization",
            }
        )
        return base

    if latest_status == "VERIFIED":
        return _terminal_verified_plan(root, base, versions, target_claims)

    if latest_status in DOCUMENTATION_TERMINAL_STATUSES:
        base.update(
            {
                "classification": "terminal_withdrawn_or_nonverified_documentation",
                "stop": True,
                "reason": "terminal non-VERIFIED bridge documentation requires protocol review before any commit",
            }
        )
        return base

    if latest_status in IN_FLIGHT_STATUSES:
        base.update(
            {
                "classification": "in_flight_bridge_chain",
                "stop": True,
                "reason": "latest bridge status is not terminal VERIFIED; do not finalize as implementation work",
            }
        )
        return base

    base.update(
        {
            "classification": "mixed_provenance_stop",
            "stop": True,
            "reason": "thread status is unknown or unsupported for automated finalization repair",
        }
    )
    return base


def _target_claims(root: Path, slugs: list[str]) -> dict[str, list[str]]:
    claims: dict[str, list[str]] = {}
    for slug in slugs:
        versions = _chain(root, slug)
        if not versions or versions[-1].status != "VERIFIED":
            continue
        report_rel, _ = _responded_report(root, versions[-1])
        if report_rel is None:
            continue
        targets, _ = _extract_targets(_read_text(root / report_rel))
        if targets is None:
            continue
        for target in targets:
            claims.setdefault(target, []).append(slug)
    return claims


def build_repair_plan(root: Path, *, exclude_wis: list[str] | None = None) -> dict[str, Any]:
    root = root.resolve()
    excluded = {_normalize_wi(wi) for wi in (exclude_wis or [])}
    source_plan = triage.build_plan(root)
    grouped = _dirty_items_by_slug(source_plan)
    slugs = sorted(grouped)
    target_claims = _target_claims(root, slugs)

    threads = [_classify_thread(root, slug, grouped[slug], excluded, target_claims) for slug in slugs]
    singly_claimed_targets = {path for path, owners in target_claims.items() if len(set(owners)) == 1}
    unattributed = [path for path in _non_bridge_dirty_paths(source_plan) if path not in singly_claimed_targets]
    if unattributed:
        threads.append(
            {
                "thread_slug": None,
                "latest_status": None,
                "classification": "mixed_provenance_stop",
                "stop": True,
                "reason": "dirty non-bridge paths need separate thread attribution before mutation",
                "path_count": len(unattributed),
                "paths": unattributed,
            }
        )

    class_counts: dict[str, int] = {}
    for thread in threads:
        classification = str(thread["classification"])
        class_counts[classification] = class_counts.get(classification, 0) + 1

    return {
        "schema_version": 1,
        "generated_at": _now(),
        "root": str(root),
        "read_only": True,
        "mutation_capabilities": [],
        "excluded_work_items": sorted(excluded),
        "counts": {
            "threads": len([thread for thread in threads if thread.get("thread_slug")]),
            "classification": dict(sorted(class_counts.items())),
            "source_dirty_paths": source_plan.get("counts", {}).get("dirty_paths"),
            "source_actuator_actions": source_plan.get("counts", {}).get("actuator_actions", {}),
        },
        "threads": sorted(threads, key=lambda item: str(item.get("thread_slug") or "~mixed")),
    }


def format_markdown(plan: dict[str, Any]) -> str:
    lines = [
        "# Per-Thread Finalization Repair Plan",
        "",
        f"- Generated: `{plan['generated_at']}`",
        f"- Root: `{plan['root']}`",
        f"- Read only: `{str(plan['read_only']).lower()}`",
        f"- Excluded work items: `{', '.join(plan['excluded_work_items']) or 'none'}`",
        "",
        "## Counts",
        "",
    ]
    for key, value in plan["counts"]["classification"].items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Threads", ""])
    for thread in plan["threads"]:
        slug = thread.get("thread_slug") or "(unattributed dirty paths)"
        lines.append(f"### {slug}")
        lines.append(f"- classification: `{thread['classification']}`")
        lines.append(f"- stop: `{str(thread.get('stop', True)).lower()}`")
        lines.append(f"- reason: {thread.get('reason')}")
        if thread.get("latest_status"):
            lines.append(f"- latest_status: `{thread['latest_status']}`")
        if thread.get("target_paths"):
            lines.append(f"- target_paths: {', '.join(f'`{path}`' for path in thread['target_paths'])}")
        if thread.get("dirty_targets"):
            lines.append(f"- dirty_targets: {', '.join(f'`{path}`' for path in thread['dirty_targets'])}")
        if thread.get("path_count") is not None:
            lines.append(f"- path_count: {thread['path_count']}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Report-only per-thread finalization repair planner.")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    parser.add_argument(
        "--exclude-wi",
        action="append",
        default=[],
        help="Work item to classify as excluded active program. Repeat as needed.",
    )
    args = parser.parse_args(argv)

    plan = build_repair_plan(args.project_root, exclude_wis=args.exclude_wi)
    if args.format == "json":
        print(json.dumps(plan, indent=2, sort_keys=True))
    else:
        print(format_markdown(plan), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
