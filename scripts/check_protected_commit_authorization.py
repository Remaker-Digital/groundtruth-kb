#!/usr/bin/env python3
"""Pre-commit gate for protected-surface GO or VERIFIED evidence."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.controlled_artifact_paths import (  # noqa: E402
    classify_controlled_artifact,
    is_versioned_bridge_status_file,
)
from scripts.implementation_authorization import (  # noqa: E402
    AuthorizationError,
    bridge_entry,
    extract_target_paths,
    list_named_packets,
    path_authorized,
)

BY_BRIDGE_PACKETS_REL = Path(".gtkb-state/implementation-authorizations/by-bridge")
VERSIONED_BRIDGE_RE = re.compile(r"^bridge/.+-\d{3}\.md$")
STATUS_RE = re.compile(r"^(NEW|REVISED|GO|NO-GO|NO-ACTION|VERIFIED|DEFERRED|WITHDRAWN|ADVISORY)$")

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
    if _is_narrative_artifact(rel):
        return False
    if rel.startswith(EXTRA_PROTECTED_PREFIXES):
        return True
    if is_versioned_bridge_status_file(rel):
        return False
    return classify_controlled_artifact(rel).is_controlled


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


def _staged_or_worktree_text(root: Path, rel_path: str) -> str:
    staged = subprocess.run(
        ["git", "show", f":{rel_path}"],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if staged.returncode == 0:
        return staged.stdout
    try:
        return (root / rel_path).read_text(encoding="utf-8")
    except OSError as exc:
        raise GateError(f"could not read {rel_path}: {exc}") from exc


def _first_nonblank_line(text: str) -> str:
    return next((line.strip() for line in text.splitlines() if line.strip()), "")


def _section_body(text: str, heading: str) -> str:
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$", re.IGNORECASE | re.MULTILINE)
    match = pattern.search(text)
    if match is None:
        return ""
    start = match.end()
    next_heading = re.search(r"^##\s+", text[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end].strip()


def _has_commit_finalization_evidence(text: str) -> bool:
    section = _section_body(text, "Commit Finalization Evidence")
    if not section:
        return False
    return "Same-transaction path set" in section and bool(re.search(r"(?m)^\s*-\s+`[^`]+`\s*$", section))


def _verified_bridge_finalization_finding(root: Path, rel_path: str) -> dict[str, Any] | None:
    if not VERSIONED_BRIDGE_RE.fullmatch(rel_path):
        return None
    if not (root / rel_path).exists():
        return None
    content = _staged_or_worktree_text(root, rel_path)
    status = _first_nonblank_line(content)
    if status and not STATUS_RE.fullmatch(status):
        return {
            "path": rel_path,
            "reason": f"versioned bridge file has invalid status token {status!r}",
        }
    if status != "VERIFIED":
        return None
    if _has_commit_finalization_evidence(content):
        return None
    return {
        "path": rel_path,
        "reason": "terminal VERIFIED bridge file lacks Commit Finalization Evidence with a same-transaction path set",
    }


def _load_live_go_evidence(root: Path) -> tuple[list[dict[str, Any]], list[str], int]:
    errors: list[str] = []
    try:
        packets = list_named_packets(root)
    except Exception as exc:  # noqa: BLE001 - fail closed on authorization subsystem errors.
        return [], [f"could not list implementation authorization packets: {exc}"], 0

    valid_packets: list[dict[str, Any]] = []
    for packet in packets:
        if packet.get("error"):
            errors.append(f"{packet.get('path', '<unknown-packet>')}: {packet['error']}")
            continue
        if packet.get("valid") is True:
            valid_packets.append(packet)
    return valid_packets, errors, len(packets)


def _live_go_authorization(
    packets: list[dict[str, Any]], errors: list[str], rel_path: str
) -> tuple[bool, str | None, list[str]]:
    for packet in packets:
        if path_authorized(packet, rel_path):
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


def _load_verified_evidence(root: Path) -> tuple[list[tuple[str, list[str]]], list[str], int]:
    errors: list[str] = []
    evidence: list[tuple[str, list[str]]] = []
    by_bridge_dir = root / BY_BRIDGE_PACKETS_REL
    if not by_bridge_dir.is_dir():
        return evidence, errors, 0

    packet_paths = sorted(by_bridge_dir.glob("*.json"))
    for packet_path in packet_paths:
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
        evidence.append((bridge_id, target_paths))
    return evidence, errors, len(packet_paths)


def _verified_authorization(
    evidence: list[tuple[str, list[str]]], errors: list[str], rel_path: str
) -> tuple[bool, str | None, list[str]]:
    for bridge_id, target_paths in evidence:
        if path_authorized({"target_path_globs": target_paths}, rel_path):
            return True, bridge_id, errors
    return False, None, errors


def _evaluate_protected_path(
    rel_path: str,
    *,
    live_go_packets: list[dict[str, Any]],
    live_go_errors: list[str],
    verified_evidence: list[tuple[str, list[str]]],
    verified_errors: list[str],
) -> dict[str, Any]:
    go_allowed, go_source, go_errors = _live_go_authorization(live_go_packets, live_go_errors, rel_path)
    if go_allowed:
        return {"path": rel_path, "status": "cleared", "evidence": "live_go_packet", "source": go_source}

    terminal_allowed, verified_source, terminal_errors = _verified_authorization(
        verified_evidence, verified_errors, rel_path
    )
    if terminal_allowed:
        return {
            "path": rel_path,
            "status": "cleared",
            "evidence": "terminal_verified_bridge_thread",
            "source": verified_source,
        }

    errors = go_errors + terminal_errors
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
    bridge_findings = [
        finding for path in selected_paths if (finding := _verified_bridge_finalization_finding(root, path)) is not None
    ]

    if not protected_paths and not bridge_findings:
        return {
            "status": "pass",
            "findings": [],
            "cleared": [],
            "skipped_unprotected": skipped_unprotected,
            "protected_paths": [],
            "evidence_summary": {
                "live_go_packets_scanned": 0,
                "live_go_packets_valid": 0,
                "terminal_verified_packets_scanned": 0,
                "terminal_verified_threads_loaded": 0,
            },
        }

    live_go_packets: list[dict[str, Any]] = []
    live_go_errors: list[str] = []
    live_go_count = 0
    verified_evidence: list[tuple[str, list[str]]] = []
    verified_errors: list[str] = []
    verified_packet_count = 0
    if protected_paths:
        live_go_packets, live_go_errors, live_go_count = _load_live_go_evidence(root)
        verified_evidence, verified_errors, verified_packet_count = _load_verified_evidence(root)

    findings: list[dict[str, Any]] = list(bridge_findings)
    cleared: list[dict[str, Any]] = []
    for rel_path in protected_paths:
        result = _evaluate_protected_path(
            rel_path,
            live_go_packets=live_go_packets,
            live_go_errors=live_go_errors,
            verified_evidence=verified_evidence,
            verified_errors=verified_errors,
        )
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
        "evidence_summary": {
            "live_go_packets_scanned": live_go_count,
            "live_go_packets_valid": len(live_go_packets),
            "terminal_verified_packets_scanned": verified_packet_count,
            "terminal_verified_threads_loaded": len(verified_evidence),
        },
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
