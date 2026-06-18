#!/usr/bin/env python3
"""Pre-commit gate for protected-surface GO or VERIFIED evidence."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.implementation_authorization import (  # noqa: E402
    AuthorizationError,
    bridge_entry,
    extract_target_paths,
    list_named_packets,
    path_authorized,
)
from scripts.implementation_start_gate import (  # noqa: E402
    ALLOWED_WRITE_PREFIXES,
    DIAGNOSTIC_WRITE_PREFIXES,
    PROTECTED_EXACT,
    PROTECTED_PREFIXES,
)

BY_BRIDGE_PACKETS_REL = Path(".gtkb-state/implementation-authorizations/by-bridge")

EXTRA_PROTECTED_EXACT = frozenset({"groundtruth.db"})
EXTRA_PROTECTED_PREFIXES = (".githooks/",)


class GateError(RuntimeError):
    """Raised when the commit gate cannot evaluate safely."""


def _normalize_rel(path_text: str) -> str:
    rel = path_text.strip().replace("\\", "/")
    while rel.startswith("./"):
        rel = rel[2:]
    return rel


def _is_narrative_artifact(rel_path: str) -> bool:
    name = Path(rel_path).name
    if rel_path == "AGENTS.md":
        return True
    if name.startswith("CLAUDE") and name.endswith(".md"):
        return rel_path == name or rel_path.startswith("applications/")
    return rel_path.startswith(".claude/rules/") and rel_path.endswith(".md")


def is_protected_path(rel_path: str) -> bool:
    rel = _normalize_rel(rel_path)
    if rel.startswith(ALLOWED_WRITE_PREFIXES) or rel.startswith(DIAGNOSTIC_WRITE_PREFIXES):
        return False
    if _is_narrative_artifact(rel):
        return False
    if rel in PROTECTED_EXACT or rel in EXTRA_PROTECTED_EXACT:
        return True
    return rel.startswith(PROTECTED_PREFIXES + EXTRA_PROTECTED_PREFIXES)


def _staged_paths(root: Path) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise GateError(f"could not read staged paths: {exc}") from exc
    return [_normalize_rel(line) for line in result.stdout.splitlines() if line.strip()]


def _live_go_authorization(root: Path, rel_path: str) -> tuple[bool, str | None, list[str]]:
    errors: list[str] = []
    try:
        packets = list_named_packets(root)
    except Exception as exc:  # noqa: BLE001 - fail closed on authorization subsystem errors.
        return False, None, [f"could not list implementation authorization packets: {exc}"]

    for packet in packets:
        if packet.get("error"):
            errors.append(f"{packet.get('path', '<unknown-packet>')}: {packet['error']}")
            continue
        if packet.get("valid") is True and path_authorized(packet, rel_path):
            return True, str(packet.get("bridge_id") or packet.get("path") or "<unknown-packet>"), errors
    return False, None, errors


def _approved_proposal_after_go(versions: list[tuple[str, str]]) -> str | None:
    go_index = next((index for index, (status, _) in enumerate(versions) if status == "GO"), None)
    if go_index is None:
        return None
    for status, path in versions[go_index + 1 :]:
        if status in {"NEW", "REVISED"}:
            return path
    return None


def _verified_authorization(root: Path, rel_path: str) -> tuple[bool, str | None, list[str]]:
    errors: list[str] = []
    by_bridge_dir = root / BY_BRIDGE_PACKETS_REL
    if not by_bridge_dir.is_dir():
        return False, None, errors

    for packet_path in sorted(by_bridge_dir.glob("*.json")):
        try:
            packet = json.loads(packet_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{packet_path.relative_to(root).as_posix()}: corrupt or unreadable: {exc}")
            continue
        bridge_id = packet.get("bridge_id")
        if not isinstance(bridge_id, str) or not bridge_id.strip():
            continue
        try:
            entry = bridge_entry(root, bridge_id)
        except Exception as exc:  # noqa: BLE001 - fail closed when evidence cannot be resolved.
            errors.append(f"{bridge_id}: could not read bridge thread: {exc}")
            continue
        if entry.latest_status != "VERIFIED":
            continue
        proposal_rel = _approved_proposal_after_go(entry.versions)
        if proposal_rel is None:
            errors.append(f"{bridge_id}: terminal VERIFIED thread has no GO-approved proposal")
            continue
        proposal_path = root / proposal_rel
        try:
            target_paths = extract_target_paths(proposal_path.read_text(encoding="utf-8"))
        except (OSError, AuthorizationError) as exc:
            errors.append(f"{bridge_id}: could not resolve approved proposal target_paths: {exc}")
            continue
        if path_authorized({"target_path_globs": target_paths}, rel_path):
            return True, bridge_id, errors
    return False, None, errors


def _evaluate_protected_path(root: Path, rel_path: str) -> dict[str, Any]:
    go_allowed, go_source, go_errors = _live_go_authorization(root, rel_path)
    if go_allowed:
        return {"path": rel_path, "status": "cleared", "evidence": "live_go_packet", "source": go_source}

    verified_allowed, verified_source, verified_errors = _verified_authorization(root, rel_path)
    if verified_allowed:
        return {
            "path": rel_path,
            "status": "cleared",
            "evidence": "terminal_verified_bridge_thread",
            "source": verified_source,
        }

    errors = go_errors + verified_errors
    finding: dict[str, Any] = {
        "path": rel_path,
        "reason": "protected path lacks live GO authorization packet or terminal VERIFIED bridge evidence",
    }
    if errors:
        finding["evidence_errors"] = errors
    return finding


def evaluate(root: Path, *, paths: list[str] | None = None) -> dict[str, Any]:
    root = root.resolve()
    selected_paths = [_normalize_rel(path) for path in (paths if paths is not None else _staged_paths(root))]
    protected_paths = [path for path in selected_paths if is_protected_path(path)]
    skipped_unprotected = [path for path in selected_paths if path not in protected_paths]

    if not protected_paths:
        return {
            "status": "pass",
            "findings": [],
            "cleared": [],
            "skipped_unprotected": skipped_unprotected,
            "protected_paths": [],
        }

    findings: list[dict[str, Any]] = []
    cleared: list[dict[str, Any]] = []
    for rel_path in protected_paths:
        result = _evaluate_protected_path(root, rel_path)
        if result.get("status") == "cleared":
            cleared.append(result)
        else:
            findings.append(result)

    return {
        "status": "fail" if findings else "pass",
        "findings": findings,
        "cleared": cleared,
        "skipped_unprotected": skipped_unprotected,
        "protected_paths": protected_paths,
    }


def _format_human(result: dict[str, Any]) -> str:
    if result["status"] == "pass":
        if result["cleared"]:
            return f"PASS protected-commit authorization ({len(result['cleared'])} protected path(s) cleared)"
        return "PASS protected-commit authorization (no protected paths in staged set)"

    lines = ["FAIL protected-commit authorization"]
    for finding in result["findings"]:
        lines.append(f"  - {finding['path']}: {finding['reason']}")
        for error in finding.get("evidence_errors", []):
            lines.append(f"    evidence error: {error}")
    lines.append("")
    lines.append(
        "Protected staged files require either a live GO implementation packet or terminal VERIFIED bridge evidence."
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", action="store_true", help="Read staged paths from git diff --cached.")
    parser.add_argument("--paths", nargs="*", help="Explicit paths to check.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    args = parser.parse_args(argv)

    if not args.staged and not args.paths:
        parser.error("must pass --staged or --paths")

    try:
        result = evaluate(args.project_root, paths=list(args.paths) if args.paths else None)
    except GateError as exc:
        sys.stderr.write(f"protected-commit authorization gate error: {exc}\n")
        return 2

    if args.json:
        sys.stdout.write(json.dumps(result, indent=2, sort_keys=True))
        sys.stdout.write("\n")
    else:
        sys.stdout.write(_format_human(result))
        sys.stdout.write("\n")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
