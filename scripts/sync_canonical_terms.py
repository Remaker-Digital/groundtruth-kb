#!/usr/bin/env python3
"""Synchronize MemBase canonical_terms from the markdown glossary.

FAB-15 keeps ``.claude/rules/canonical-terminology.md`` as the glossary source
of truth while making the backing ``canonical_terms`` table deterministically
regenerable and doctor-checkable.
"""

from __future__ import annotations

import argparse
import json
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from groundtruth_kb import canonical_terms
from groundtruth_kb.db import KnowledgeDB

DEFAULT_CONFIG = Path("config/governance/canonical-terms-sync.toml")
DEFAULT_FAILURE_OPS = frozenset({"insert", "update", "retire"})


@dataclass(frozen=True)
class SyncConfig:
    glossary_path: Path
    database_path: Path
    changed_by: str
    freshness_failure_operations: frozenset[str]


def resolve_project_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / "groundtruth.toml").is_file():
            return candidate
    raise RuntimeError("cannot locate GT-KB project root; groundtruth.toml not found")


def _repo_path(project_root: Path, value: str, *, field: str) -> Path:
    path = Path(value)
    resolved = path if path.is_absolute() else project_root / path
    try:
        resolved.resolve().relative_to(project_root.resolve())
    except ValueError as exc:
        raise ValueError(f"{field} must remain inside project root: {value}") from exc
    return resolved


def load_config(project_root: Path, config_path: Path) -> SyncConfig:
    resolved_config = config_path if config_path.is_absolute() else project_root / config_path
    raw = tomllib.loads(resolved_config.read_text(encoding="utf-8"))
    if raw.get("schema_version") != 1:
        raise ValueError("canonical-terms sync config schema_version must be 1")

    glossary_path = _repo_path(project_root, str(raw.get("glossary_path", "")), field="glossary_path")
    database_path = _repo_path(project_root, str(raw.get("database_path", "")), field="database_path")
    changed_by = str(raw.get("changed_by") or "canonical-terms-sync")
    failure_ops = raw.get("freshness_failure_operations", sorted(DEFAULT_FAILURE_OPS))
    if not isinstance(failure_ops, list) or not all(isinstance(op, str) for op in failure_ops):
        raise ValueError("freshness_failure_operations must be a list of operation names")

    return SyncConfig(
        glossary_path=glossary_path,
        database_path=database_path,
        changed_by=changed_by,
        freshness_failure_operations=frozenset(failure_ops),
    )


def build_plan(config: SyncConfig, *, apply: bool, changed_by: str | None = None) -> dict[str, Any]:
    db = KnowledgeDB(str(config.database_path))
    try:
        plan = canonical_terms.seed_from_markdown(
            db,
            config.glossary_path,
            dry_run=not apply,
            changed_by=changed_by or config.changed_by,
        )
        freshness_plan = canonical_terms.seed_from_markdown(db, config.glossary_path, dry_run=True) if apply else plan
    finally:
        db.close()
    payload = plan.to_dict()
    pending_ops = [
        op for op in freshness_plan.to_dict()["operations"] if op["op"] in config.freshness_failure_operations
    ]
    payload["freshness"] = {
        "fresh": not pending_ops,
        "pending_count": len(pending_ops),
        "failure_operations": sorted(config.freshness_failure_operations),
    }
    return payload


def _emit_text(payload: dict[str, Any], *, mode: str) -> None:
    print(f"canonical-terms sync [{mode}]")
    print(f"  source: {payload['source_path']}")
    print(f"  hash:   {payload['source_hash']}")
    summary = payload.get("summary", {})
    print("  summary: " + (", ".join(f"{key}={value}" for key, value in sorted(summary.items())) or "(none)"))
    freshness = payload["freshness"]
    print(f"  fresh:  {freshness['fresh']} (pending={freshness['pending_count']})")
    for op in payload["operations"]:
        print(f"    {op['op']:<10} {op['id']:<40} {op['canonical_term']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=None)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Plan operations without mutating MemBase.")
    mode.add_argument("--apply", action="store_true", help="Apply insert/update/retire operations append-only.")
    mode.add_argument("--check", action="store_true", help="Fail when sync-changing operations are pending.")
    parser.add_argument("--changed-by", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        project_root = (args.project_root or resolve_project_root()).resolve()
        config = load_config(project_root, args.config)
        applying = bool(args.apply)
        payload = build_plan(config, apply=applying, changed_by=args.changed_by)
    except Exception as exc:
        print(f"canonical-terms sync error: {exc}", file=sys.stderr)
        return 2

    mode_name = "APPLY" if args.apply else "CHECK" if args.check else "DRY-RUN"
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        _emit_text(payload, mode=mode_name)

    if args.check and not payload["freshness"]["fresh"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
