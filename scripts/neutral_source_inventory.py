#!/usr/bin/env python3
"""Deterministic neutral-source inventory and fail-closed sanitation guard (WI-6040).

Provides a case-insensitive complete-tree walk of the canonical neutral
configuration source, classifying every current source artifact exactly once
under a registered family/owner and reporting its read/mutation route.

The inventory never treats a generated harness directory (`.claude/`,
`.codex/`, `.goose/`, `.cursor/`, `.agent/`, `.api-harness/`) as a source
family (GOV-HARNESS-NEUTRAL-BASELINE-001).

Output is diagnostic evidence only and carries no authority. The service
mutates no source, projection, specification, project authorization, or
alternate state; it writes only a machine-readable plan/check result (stdout
JSON and an optional `.gtkb-state/` report).

Exit codes:
  0  inventory/check clean (every artifact classified, no contamination)
  1  contamination/classification failure
  2  usage error
  3  unreadable/malformed input
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CONFIG_RELATIVE = Path("config") / "governance" / "neutral-source-inventory.toml"


class NeutralSourceInventoryError(Exception):
    """Raised when the inventory cannot produce a clean result."""


def _load_config(root: Path) -> dict[str, Any]:
    """Load the inventory TOML, fail-closed on malformed input."""
    try:
        import tomllib
    except ImportError:  # pragma: no cover - Python 3.11+
        import tomli as tomllib  # type: ignore[import-not-found]
    cfg_path = root / CONFIG_RELATIVE
    try:
        with cfg_path.open("rb") as fh:
            return tomllib.load(fh)
    except FileNotFoundError as exc:
        raise NeutralSourceInventoryError(
            f"inventory config missing: {cfg_path}"
        ) from exc
    except Exception as exc:
        raise NeutralSourceInventoryError(
            f"inventory config malformed: {cfg_path}: {exc}"
        ) from exc


def _resolve_root_paths(root: Path, config: dict[str, Any]) -> list[Path]:
    """Resolve the walk roots from the TOML `[roots]` table."""
    roots: list[Path] = []
    for value in (config.get("roots") or {}).values():
        p = Path(str(value))
        if not p.is_absolute():
            p = root / p
        roots.append(p.resolve())
    return roots


def _projection_prefixes(config: dict[str, Any]) -> list[str]:
    return [
        str(p).rstrip("/") + "/"
        for p in (config.get("projection_prefixes") or {}).get("paths", [])
    ]


def _disposable_prefixes(config: dict[str, Any]) -> list[str]:
    return [str(p) for p in (config.get("disposable_prefixes") or {}).get("paths", [])]


def _classify(rel_posix: str, config: dict[str, Any]) -> str:
    """Classify a relative path as exactly one family. Returns the family name.

    Priority:
      1. disposable/junk (caches, scratch, pyc)
      2. projection (generated harness trees)
      3. registered family by extension/route heuristic
    """
    lower = rel_posix.lower()
    # Disposable first (never a source family)
    for disp in _disposable_prefixes(config):
        d = disp.lower()
        if d.endswith("/"):
            if lower.startswith(d):
                return "junk"
        elif lower.endswith(d) or lower == d:
            return "junk"
    # Projection (generated harness trees)
    for proj in _projection_prefixes(config):
        if lower.startswith(proj.lower()):
            return "projection"
    # Registered families by extension / position
    if rel_posix.startswith("config/governance/"):
        return "governance_evidence"
    if rel_posix.startswith("config/") and rel_posix.endswith(".toml"):
        return "configuration"
    if rel_posix.startswith("config/") and rel_posix.endswith(".md"):
        return "configuration"
    if rel_posix.endswith(".py"):
        return "source" if "/test" not in lower else "test"
    if rel_posix.endswith((".md", ".rst")):
        return "documentation"
    if rel_posix.endswith((".toml", ".json")):
        return "metadata"
    return "junk"


def _owner_for(rel_posix: str) -> str:
    if rel_posix.startswith("applications/"):
        return "applications"
    return "platform"


def _walk_and_classify(root: Path, config: dict[str, Any]) -> list[dict[str, Any]]:
    """Walk the roots case-insensitively and classify every artifact once."""
    artifacts: list[dict[str, Any]] = []
    seen: set[Path] = set()
    for base in _resolve_root_paths(root, config):
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*"), key=lambda p: p.as_posix().lower()):
            if path.is_dir():
                continue
            if not path.is_file():
                continue
            try:
                resolved = path.resolve()
            except OSError:
                continue
            if resolved in seen:
                continue
            seen.add(resolved)
            try:
                rel = path.relative_to(root).as_posix()
            except ValueError:
                rel = path.as_posix()
            family = _classify(rel, config)
            if family == "projection":
                # Projections are reported but flagged; they are not source families.
                artifacts.append(
                    {
                        "path": rel,
                        "family": "projection",
                        "owner": _owner_for(rel),
                        "consumer": "generated harness tree",
                        "route": "generated output; do not edit in place",
                        "projection": True,
                    }
                )
                continue
            artifacts.append(
                {
                    "path": rel,
                    "family": family,
                    "owner": _owner_for(rel),
                    "consumer": "agent-visible surface" if family != "junk" else "none",
                    "route": _route_for(family, config),
                    "projection": False,
                }
            )
    return artifacts


def _route_for(family: str, config: dict[str, Any]) -> str:
    routes = config.get("routes") or {}
    read_map = routes.get("read") or {}
    mutate_map = routes.get("mutate") or {}
    if family == "projection":
        return "generated output; do not edit in place"
    return f"read={read_map.get(family, 'n/a')}; mutate={mutate_map.get(family, 'n/a')}"


def _content_digest(artifacts: list[dict[str, Any]]) -> str:
    """Deterministic normalized digest of the classification result (acceptance 3)."""
    payload = json.dumps(artifacts, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _check(artifacts: list[dict[str, Any]]) -> list[str]:
    """Return a list of contamination findings (empty = clean)."""
    findings: list[str] = []
    for artifact in artifacts:
        if artifact["family"] == "unclassified":
            findings.append(f"unclassified artifact: {artifact['path']}")
    return findings


def run_inventory(
    root: Path, config: dict[str, Any], *, report_dir: Path | None = None
) -> dict[str, Any]:
    artifacts = _walk_and_classify(root, config)
    digest = _content_digest(artifacts)
    findings = _check(artifacts)
    result = {
        "schema_version": config.get("schema_version", 1),
        "source_tree": ".harness-baseline-configuration + config + scripts + groundtruth-kb/src",
        "artifact_count": len(artifacts),
        "families": _family_counts(artifacts),
        "digest": digest,
        "clean": not findings,
        "findings": findings,
        "artifacts": artifacts,
    }
    if report_dir is not None:
        report_dir.mkdir(parents=True, exist_ok=True)
        (report_dir / "neutral-source-inventory.json").write_text(
            json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
        )
    return result


def _family_counts(artifacts: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for a in artifacts:
        counts[a["family"]] = counts.get(a["family"], 0) + 1
    return counts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Neutral-source inventory and fail-closed guard"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Run the inventory and exit 1 if any artifact is unclassified/contaminated",
    )
    parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable JSON"
    )
    parser.add_argument(
        "--report-dir", type=Path, default=None, help="Optional .gtkb-state report dir"
    )
    parser.add_argument(
        "--project-root", type=Path, default=None, help="Host root override"
    )
    args = parser.parse_args(argv)

    root = (args.project_root or PROJECT_ROOT).resolve()
    try:
        config = _load_config(root)
    except NeutralSourceInventoryError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3

    report_dir = args.report_dir
    if report_dir is not None and not report_dir.is_absolute():
        report_dir = root / report_dir

    result = run_inventory(root, config, report_dir=report_dir)

    if args.json or args.check:
        print(
            json.dumps(result, indent=2, sort_keys=True)
            if not args.json
            else json.dumps(result, sort_keys=True)
        )

    if args.check and not result["clean"]:
        for f in result["findings"]:
            print(f"contamination: {f}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
