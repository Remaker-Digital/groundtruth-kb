#!/usr/bin/env python3
"""Validate session overlays against first-slice GT-KB overlay policy.

The checker inspects every overlay under ``.groundtruth/session/overlays/`` and
fails loudly if any overlay marks itself authoritative, points outside the
application root, uses a source outside the fixed allowlist, references a
forbidden path (``.env*``, ``groundtruth.db``, ``.groundtruth-chroma/``,
bridge files, or executable content), or contains a malformed manifest.

This script is intentionally read-only: it does not promote, apply, refresh,
or mutate any overlay. It is wired into the release-candidate gate so
overlay drift is caught before a build can be treated as release-worthy.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import gtkb_overlay  # noqa: E402  (sys.path adjusted above)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def check_project(project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    """Return a structured report describing every overlay under ``project_root``."""

    root_resolved = project_root.resolve()
    overlays_root = gtkb_overlay.overlay_root(root_resolved)
    overlays: list[dict[str, Any]] = []
    errors: list[str] = []

    pointer = gtkb_overlay.load_current_pointer(root_resolved)
    pointer_errors: list[str] = []
    if pointer is not None:
        if pointer.get("authoritative") is True:
            pointer_errors.append("current overlay pointer must not claim authoritative=true")
        overlay_dir_rel = pointer.get("overlay_dir")
        if not isinstance(overlay_dir_rel, str) or not overlay_dir_rel:
            pointer_errors.append("current overlay pointer missing overlay_dir")
        else:
            try:
                pointer_target = (root_resolved / overlay_dir_rel).resolve()
                pointer_target.relative_to(overlays_root.resolve())
            except (OSError, ValueError):
                pointer_errors.append(f"current overlay pointer overlay_dir {overlay_dir_rel!r} escapes overlay root")
    errors.extend(pointer_errors)

    for overlay_dir in gtkb_overlay.iter_overlay_dirs(root_resolved):
        overlay_entry: dict[str, Any] = {
            "overlay_id": overlay_dir.name,
            "overlay_dir": str(overlay_dir.relative_to(root_resolved).as_posix()),
            "authoritative": False,
            "valid": True,
            "errors": [],
            "staleness": None,
        }
        try:
            manifest = gtkb_overlay.load_manifest(overlay_dir)
            gtkb_overlay.validate_manifest(manifest, project_root=root_resolved)
            overlay_entry["overlay_id"] = manifest.overlay_id
            overlay_entry["authoritative"] = manifest.authoritative
            staleness = gtkb_overlay.evaluate_staleness(overlay_dir, project_root=root_resolved)
            overlay_entry["staleness"] = {
                "is_stale": staleness.is_stale,
                "expired": staleness.expired,
                "entries_stale": staleness.entries_stale,
                "entries_total": staleness.entries_total,
                "notes": list(staleness.notes),
            }
        except gtkb_overlay.OverlayPolicyError as exc:
            overlay_entry["valid"] = False
            overlay_entry["errors"].append(str(exc))
            errors.append(f"overlay {overlay_dir.relative_to(root_resolved).as_posix()}: {exc}")
        overlays.append(overlay_entry)

    return {
        "project_root": str(root_resolved),
        "overlay_root": str(overlays_root.relative_to(root_resolved).as_posix())
        if overlays_root.exists()
        else str(gtkb_overlay.OVERLAY_ROOT_RELATIVE.as_posix()),
        "overlay_count": len(overlays),
        "pointer_present": pointer is not None,
        "pointer_errors": pointer_errors,
        "overlays": overlays,
        "errors": errors,
        "pass": not errors,
    }


def _print_text(report: dict[str, Any]) -> None:
    if report["pass"]:
        print(f"Session overlay policy: PASS ({report['overlay_count']} overlay(s))")
    else:
        print("Session overlay policy: FAIL", file=sys.stderr)
        for error in report["errors"]:
            print(f"- {error}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        type=Path,
        default=PROJECT_ROOT,
        help="Application root whose .groundtruth/session/overlays/ tree is validated.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the full structured report as JSON on stdout.",
    )
    args = parser.parse_args(argv)

    report = check_project(args.project_root.resolve())
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        _print_text(report)
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
