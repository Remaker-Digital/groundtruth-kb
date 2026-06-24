#!/usr/bin/env python3
"""Universal-floor pre-commit gate for narrative-artifact mutations.

Slice C of GTKB-NARRATIVE-ARTIFACT-APPROVAL-EXTENSION-001.
Bridge:    bridge/gtkb-narrative-artifact-approval-extension-001-004.md (GO)
Specs:     GOV-ARTIFACT-APPROVAL-001 (extended), DCL-ARTIFACT-APPROVAL-HOOK-001 (extended)

This script inspects staged paths and, for each path that matches a
protected narrative-artifact pattern (per
config/governance/narrative-artifact-approval.toml), requires either:

  (a) a matching approval packet under .groundtruth/formal-artifact-approvals/
      whose target_path equals the staged path AND whose full_content_sha256
      matches the staged blob's LF-normalized UTF-8 text sha256.
  (b) [Future, depends on Slice B spike] a same-session AUQ audit entry under
      .gtkb-state/auq-audit/<session-id>.jsonl with decision_class=artifact-correction
      and a matching content hash.

Exit codes:
  0 - all narrative-artifact mutations have evidence; staged set is clean.
  1 - one or more narrative-artifact mutations lack evidence; commit rejected.
  2 - configuration or runtime error (e.g., narrative-artifact-approval.toml unreadable).

This gate runs UNDER git commit (.githooks/pre-commit), so it is invoked
regardless of which AI harness produced the staged change. It is the
harness-agnostic universal floor that complements the Claude PreToolUse
hook in Slice A.

CLI:
  python scripts/check_narrative_artifact_evidence.py --staged
  python scripts/check_narrative_artifact_evidence.py --paths PATH1 PATH2 ...

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import tomllib
except ImportError:  # pragma: no cover
    import tomli as tomllib  # type: ignore[import-not-found,no-redef]

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_REL = Path("config/governance/narrative-artifact-approval.toml")
PACKETS_REL = Path(".groundtruth/formal-artifact-approvals")

NARRATIVE_ARTIFACT_TYPE = "narrative_artifact"

REQUIRED_PACKET_FIELDS = {
    "artifact_type",
    "artifact_id",
    "action",
    "target_path",
    "source_ref",
    "full_content",
    "full_content_sha256",
    "approval_mode",
    "presented_to_user",
    "transcript_captured",
    "explicit_change_request",
    "changed_by",
    "change_reason",
}

VALID_APPROVAL_MODES = {"approve", "acknowledge", "edit-and-approve", "auto"}


class GateError(RuntimeError):
    """Raised when the gate cannot evaluate due to configuration or runtime error."""


def _load_config(root: Path) -> dict[str, Any]:
    config_path = root / CONFIG_REL
    if not config_path.exists():
        raise GateError(f"narrative-artifact-approval config not found: {CONFIG_REL.as_posix()}")
    try:
        return tomllib.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise GateError(f"narrative-artifact-approval config unreadable: {exc}") from exc


def _staged_paths(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    return [line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()]


def _normalize_lf(content: str) -> str:
    return content.replace("\r\n", "\n").replace("\r", "\n")


def _staged_blob_text_sha256(root: Path, rel_path: str) -> tuple[str | None, str | None]:
    """Return sha256 of the staged blob's LF-normalized UTF-8 text."""
    try:
        result = subprocess.run(
            ["git", "show", f":{rel_path}"],
            cwd=root,
            capture_output=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        return None, "could not read staged blob (path may be unstaged or deleted)"
    try:
        normalized = _normalize_lf(result.stdout.decode("utf-8"))
    except UnicodeDecodeError:
        return None, "staged blob is not valid UTF-8 text"
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest(), None


def _matches_any(patterns: list[str], rel_path: str) -> bool:
    return any(fnmatch.fnmatch(rel_path, pattern) for pattern in patterns)


def _is_protected(rel_path: str, config: dict[str, Any]) -> bool:
    protected_blocks = config.get("protected_artifacts", []) or []
    exemption_blocks = config.get("exemptions", []) or []
    protected: list[str] = []
    for block in protected_blocks:
        protected.extend(block.get("patterns", []) or [])
    exempted: list[str] = []
    for block in exemption_blocks:
        exempted.extend(block.get("patterns", []) or [])
    if not _matches_any(protected, rel_path):
        return False
    return not (exempted and _matches_any(exempted, rel_path))


def _validate_packet(packet: dict[str, Any], rel_path: str, staged_text_sha256: str) -> str | None:
    missing = sorted(REQUIRED_PACKET_FIELDS - set(packet))
    if missing:
        return f"missing required fields: {', '.join(missing)}"
    if packet.get("artifact_type") != NARRATIVE_ARTIFACT_TYPE:
        return f"artifact_type must be {NARRATIVE_ARTIFACT_TYPE!r}, got {packet.get('artifact_type')!r}"
    if packet.get("approval_mode") not in VALID_APPROVAL_MODES:
        return f"approval_mode invalid: {packet.get('approval_mode')!r}"
    if Path(packet.get("target_path", "")).as_posix() != rel_path:
        return f"target_path {packet.get('target_path')!r} does not match staged path {rel_path!r}"
    full_content = packet.get("full_content")
    if not isinstance(full_content, str) or not full_content:
        return "full_content must be a non-empty string"
    expected = hashlib.sha256(full_content.encode("utf-8")).hexdigest()
    if packet.get("full_content_sha256") != expected:
        return "full_content_sha256 does not match full_content"
    if packet.get("full_content_sha256") != staged_text_sha256:
        return (
            "full_content_sha256 does not match the staged blob's normalized UTF-8 text sha256 "
            "(packet must be regenerated when staged content changes; "
            "CRLF and bare CR are normalized to LF for narrative artifacts)"
        )
    for flag in ("presented_to_user", "transcript_captured"):
        if packet.get(flag) is not True:
            return f"requires {flag}=true"
    if not isinstance(packet.get("explicit_change_request"), str) or not packet.get("explicit_change_request").strip():
        return "explicit_change_request must be non-empty"
    return None


def _find_matching_packet(
    packets_dir: Path, rel_path: str, staged_text_sha256: str
) -> tuple[Path, dict[str, Any]] | tuple[None, None]:
    if not packets_dir.exists():
        return None, None
    for packet_file in sorted(packets_dir.glob("*.json")):
        try:
            data = json.loads(packet_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        if data.get("artifact_type") != NARRATIVE_ARTIFACT_TYPE:
            continue
        if Path(data.get("target_path", "")).as_posix() != rel_path:
            continue
        if data.get("full_content_sha256") != staged_text_sha256:
            continue
        return packet_file, data
    return None, None


def evaluate(
    root: Path,
    *,
    paths: list[str] | None = None,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Pure evaluation entry point used by tests and the CLI."""
    cfg = config if config is not None else _load_config(root)
    if paths is None:
        paths = _staged_paths(root)
    findings: list[dict[str, Any]] = []
    cleared: list[str] = []
    skipped_unprotected: list[str] = []
    for rel_path in paths:
        if not _is_protected(rel_path, cfg):
            skipped_unprotected.append(rel_path)
            continue
        sha256, staged_error = _staged_blob_text_sha256(root, rel_path)
        if sha256 is None:
            findings.append(
                {
                    "path": rel_path,
                    "reason": staged_error or "could not read staged blob (path may be unstaged or deleted)",
                }
            )
            continue
        packets_dir = root / PACKETS_REL
        packet_file, packet = _find_matching_packet(packets_dir, rel_path, sha256)
        if packet is None or packet_file is None:
            findings.append(
                {
                    "path": rel_path,
                    "staged_sha256": sha256,
                    "reason": (
                        f"no matching approval packet found under {PACKETS_REL.as_posix()} "
                        f"with artifact_type={NARRATIVE_ARTIFACT_TYPE!r}, target_path={rel_path!r}, "
                        f"and LF-normalized full_content_sha256={sha256}"
                    ),
                }
            )
            continue
        validation_error = _validate_packet(packet, rel_path, sha256)
        if validation_error:
            findings.append(
                {
                    "path": rel_path,
                    "packet": packet_file.relative_to(root).as_posix(),
                    "reason": f"approval packet failed validation: {validation_error}",
                }
            )
            continue
        cleared.append(rel_path)

    status = "fail" if findings else "pass"
    return {
        "status": status,
        "findings": findings,
        "cleared": cleared,
        "skipped_unprotected": skipped_unprotected,
    }


def _format_human(result: dict[str, Any]) -> str:
    lines: list[str] = []
    if result["status"] == "pass":
        if result["cleared"]:
            lines.append("PASS narrative-artifact evidence ({} cleared)".format(len(result["cleared"])))
        else:
            lines.append("PASS narrative-artifact evidence (no protected paths in staged set)")
        return "\n".join(lines)
    lines.append("FAIL narrative-artifact evidence")
    for finding in result["findings"]:
        lines.append(f"  - {finding['path']}: {finding['reason']}")
    lines.append("")
    lines.append(
        "Generate a packet under .groundtruth/formal-artifact-approvals/ with "
        f"artifact_type={NARRATIVE_ARTIFACT_TYPE!r}, target_path matching the staged path, "
        "and full_content_sha256 matching the staged blob's LF-normalized UTF-8 text sha256."
    )
    lines.append("(Hard-block per GTKB-NARRATIVE-ARTIFACT-APPROVAL-EXTENSION-001 Slice C universal floor.)")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", action="store_true", help="Read staged paths from git diff --cached")
    parser.add_argument("--paths", nargs="*", help="Explicit paths to check (relative to project root)")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    args = parser.parse_args()

    if not args.staged and not args.paths:
        parser.error("must pass --staged or --paths")

    paths = list(args.paths) if args.paths else None

    try:
        result = evaluate(args.project_root, paths=paths)
    except GateError as exc:
        sys.stderr.write(f"narrative-artifact evidence gate error: {exc}\n")
        return 2

    if args.json:
        sys.stdout.write(json.dumps(result, indent=2))
        sys.stdout.write("\n")
    else:
        sys.stdout.write(_format_human(result))
        sys.stdout.write("\n")

    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
