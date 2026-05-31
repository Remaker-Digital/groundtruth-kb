#!/usr/bin/env python3
"""Warn on staged protected narrative artifacts from multiple approval scopes.

Slice 1 for gtkb-commit-scope-bundling-detection-slice-1.

The check is intentionally WARN-only: pass and warn findings both return exit
0 so the predicate can gather signal before any future block-mode escalation.
Configuration errors still return exit 2.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib
except ImportError:  # pragma: no cover
    import tomli as tomllib  # type: ignore[import-not-found,no-redef]

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_REL = Path("config/governance/narrative-artifact-approval.toml")
PACKETS_REL = Path(".groundtruth/formal-artifact-approvals")

DELIB_RE = re.compile(r"\bDELIB-[A-Z0-9_-]+\b")
SPEC_RE = re.compile(r"\b(?:SPEC|GOV|ADR|DCL|PB|REQ)-[A-Z0-9][A-Z0-9_-]*\b")
BRIDGE_SLUG_RE = re.compile(r"\bgtkb-[a-z0-9-]+(?:-\d{3})?\b")
BRIDGE_VERSION_SUFFIX_RE = re.compile(r"-\d{3}$")


class ScopeBundlingError(RuntimeError):
    """Raised when the predicate cannot evaluate safely."""


@dataclass(frozen=True, order=True)
class ScopeIdentity:
    source_ref: str | None
    deliberation_id: str | None
    spec_id: str | None
    bridge_slug: str | None

    @property
    def key(self) -> str:
        return "|".join(
            [
                f"source_ref={self.source_ref or ''}",
                f"deliberation_id={self.deliberation_id or ''}",
                f"spec_id={self.spec_id or ''}",
                f"bridge_slug={self.bridge_slug or ''}",
            ]
        )

    def as_dict(self) -> dict[str, str | None]:
        return {
            "source_ref": self.source_ref,
            "deliberation_id": self.deliberation_id,
            "spec_id": self.spec_id,
            "bridge_slug": self.bridge_slug,
        }


def _load_config(root: Path) -> dict[str, Any]:
    config_path = root / CONFIG_REL
    if not config_path.exists():
        raise ScopeBundlingError(f"narrative-artifact-approval config not found: {CONFIG_REL.as_posix()}")
    try:
        return tomllib.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ScopeBundlingError(f"narrative-artifact-approval config unreadable: {exc}") from exc


def _staged_paths(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    return sorted({line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()})


def _normalise_rel_path(path: str | Path) -> str:
    return Path(path).as_posix().replace("\\", "/")


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


def _load_packets(packets_dir: Path) -> list[dict[str, Any]]:
    if not packets_dir.exists():
        return []
    packets: list[dict[str, Any]] = []
    for packet_file in sorted(packets_dir.glob("*.json")):
        try:
            data = json.loads(packet_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict):
            packets.append(data)
    return packets


def _first_match(pattern: re.Pattern[str], text: str) -> str | None:
    match = pattern.search(text)
    return match.group(0) if match else None


def _packet_scope_identity(packet: dict[str, Any]) -> ScopeIdentity:
    source_ref = packet.get("source_ref")
    if not isinstance(source_ref, str) or not source_ref.strip():
        source_ref = None
    else:
        source_ref = source_ref.strip()

    text = "\n".join(
        str(packet.get(key, ""))
        for key in ("source_ref", "change_reason", "artifact_id")
        if packet.get(key) is not None
    )
    deliberation_id = _first_match(DELIB_RE, text)
    spec_id = _first_match(SPEC_RE, text)
    bridge_slug = _first_match(BRIDGE_SLUG_RE, text)
    if bridge_slug is not None:
        bridge_slug = BRIDGE_VERSION_SUFFIX_RE.sub("", bridge_slug)
    return ScopeIdentity(
        source_ref=source_ref,
        deliberation_id=deliberation_id,
        spec_id=spec_id,
        bridge_slug=bridge_slug,
    )


def _match_packets_to_path(rel_path: str, packets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for packet in packets:
        target_path = packet.get("target_path")
        if not isinstance(target_path, str):
            continue
        if _normalise_rel_path(target_path) == rel_path:
            matches.append(packet)
    if not matches:
        return []
    return [matches[-1]]


def evaluate(root: Path, *, paths: list[str] | None = None) -> dict[str, Any]:
    """Pure evaluation entry point used by tests and the CLI."""

    cfg = _load_config(root)
    candidate_paths = _staged_paths(root) if paths is None else paths
    rel_paths = sorted({_normalise_rel_path(path) for path in candidate_paths if str(path).strip()})
    packets = _load_packets(root / PACKETS_REL)

    scopes: dict[str, dict[str, Any]] = {}
    unscoped_protected: list[str] = []
    skipped_unprotected: list[str] = []
    for rel_path in rel_paths:
        if not _is_protected(rel_path, cfg):
            skipped_unprotected.append(rel_path)
            continue

        matching_packets = _match_packets_to_path(rel_path, packets)
        if not matching_packets:
            unscoped_protected.append(rel_path)
            continue

        for packet in matching_packets:
            identity = _packet_scope_identity(packet)
            scope = scopes.setdefault(identity.key, {**identity.as_dict(), "paths": []})
            if rel_path not in scope["paths"]:
                scope["paths"].append(rel_path)

    for scope in scopes.values():
        scope["paths"].sort()

    findings: list[dict[str, Any]] = []
    if len(scopes) > 1:
        findings.append(
            {
                "kind": "multi_scope_bundle",
                "scope_count": len(scopes),
                "scope_keys": sorted(scopes),
            }
        )
    if unscoped_protected:
        findings.append(
            {
                "kind": "unscoped_protected_paths",
                "paths": sorted(unscoped_protected),
            }
        )

    return {
        "status": "warn" if findings else "pass",
        "scopes": {key: scopes[key] for key in sorted(scopes)},
        "unscoped_protected": sorted(unscoped_protected),
        "skipped_unprotected": sorted(skipped_unprotected),
        "findings": findings,
    }


def _format_human(result: dict[str, Any]) -> str:
    if result["status"] == "pass":
        scope_count = len(result["scopes"])
        skipped_count = len(result["skipped_unprotected"])
        return f"PASS commit-scope bundling check ({scope_count} scope(s), {skipped_count} unprotected path(s) skipped)"

    lines = ["WARN commit-scope bundling detected"]
    if result["scopes"]:
        lines.append(f"  Staged set spans {len(result['scopes'])} approval scope(s):")
        for index, (_key, scope) in enumerate(result["scopes"].items(), start=1):
            lines.append(
                "    scope[{}]: source_ref={}, deliberation={}, spec={}, bridge_slug={}".format(
                    index,
                    scope["source_ref"],
                    scope["deliberation_id"],
                    scope["spec_id"],
                    scope["bridge_slug"],
                )
            )
            lines.append("      paths:")
            for path in scope["paths"]:
                lines.append(f"        - {path}")
    if result["unscoped_protected"]:
        lines.append("  Protected paths with no matching approval packet:")
        for path in result["unscoped_protected"]:
            lines.append(f"    - {path}")
    lines.append("  Slice 1 is WARN-only; commit proceeds. Slice 2 may promote to BLOCK after empirical tuning.")
    return "\n".join(lines)


def _repository_root(start: Path) -> Path:
    resolved = start.resolve()
    for candidate in (resolved, *resolved.parents):
        if (candidate / ".git").exists():
            return candidate
    return resolved


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _resolve_project_root(raw_root: Path, repository_root: Path) -> Path:
    root = raw_root.resolve()
    repo = repository_root.resolve()
    if not _is_relative_to(root, repo):
        raise ScopeBundlingError(
            f"--project-root {root} is outside repository root {repo}; refusing out-of-root evaluation"
        )
    return root


def main(argv: list[str] | None = None, *, repository_root: Path | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", action="store_true", help="Read staged paths from git diff --cached")
    parser.add_argument("--paths", nargs="*", help="Explicit paths to check, relative to project root")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    args = parser.parse_args(argv)

    if not args.staged and not args.paths:
        parser.error("must pass --staged or --paths")

    repo_root = _repository_root(repository_root or PROJECT_ROOT)
    try:
        project_root = _resolve_project_root(args.project_root, repo_root)
        result = evaluate(project_root, paths=list(args.paths) if args.paths else None)
    except (ScopeBundlingError, subprocess.CalledProcessError) as exc:
        sys.stderr.write(f"commit-scope bundling check error: {exc}\n")
        return 2

    if args.json:
        sys.stdout.write(json.dumps(result, indent=2, sort_keys=True))
        sys.stdout.write("\n")
    else:
        output = _format_human(result)
        stream = sys.stderr if result["status"] == "warn" else sys.stdout
        stream.write(output)
        stream.write("\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
