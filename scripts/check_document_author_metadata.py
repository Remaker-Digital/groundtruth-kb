#!/usr/bin/env python3
"""Audit governed Markdown files for document-author provenance metadata."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tomllib
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.document_author_metadata import (  # noqa: E402
    DEFAULT_EXCLUSIONS,
    DEFAULT_GOVERNED_SURFACES,
    DocumentAuthorConfig,
    is_governed_document_path,
    relative_path,
    validate_author_metadata,
)

CONFIG_REL = Path("config/governance/document-author-provenance.toml")


@dataclass(frozen=True)
class Finding:
    path: str
    missing_fields: tuple[str, ...]
    invalid_fields: tuple[str, ...]

    @property
    def gaps(self) -> tuple[str, ...]:
        return (*self.missing_fields, *self.invalid_fields)


def load_config(project_root: Path, config_path: Path | None = None) -> DocumentAuthorConfig:
    selected = config_path or project_root / CONFIG_REL
    if not selected.exists():
        return DocumentAuthorConfig()
    data = tomllib.loads(selected.read_text(encoding="utf-8"))
    surfaces = data.get("governed_surfaces", DEFAULT_GOVERNED_SURFACES)
    exclusions = data.get("exclusions", DEFAULT_EXCLUSIONS)
    if not isinstance(surfaces, list) or not all(isinstance(item, str) for item in surfaces):
        raise ValueError("governed_surfaces must be a TOML list of strings")
    if not isinstance(exclusions, list) or not all(isinstance(item, str) for item in exclusions):
        raise ValueError("exclusions must be a TOML list of strings")
    return DocumentAuthorConfig(tuple(surfaces), tuple(exclusions))


def _git_changed_paths(project_root: Path) -> list[str]:
    commands = (
        ["git", "diff", "--name-only", "--diff-filter=A", "HEAD", "--"],
        ["git", "diff", "--cached", "--name-only", "--diff-filter=A", "--"],
    )
    paths: set[str] = set()
    for command in commands:
        result = subprocess.run(command, cwd=project_root, text=True, capture_output=True, check=False)
        if result.returncode == 0:
            paths.update(line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip())
    status = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=project_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if status.returncode == 0:
        for line in status.stdout.splitlines():
            if line.startswith("?? "):
                paths.add(line[3:].strip().replace("\\", "/"))
    return sorted(paths)


def candidate_paths(
    project_root: Path,
    config: DocumentAuthorConfig,
    *,
    changed_only: bool,
    explicit_surfaces: Iterable[str] | None = None,
) -> list[Path]:
    if changed_only:
        return [
            project_root / rel
            for rel in _git_changed_paths(project_root)
            if is_governed_document_path(rel, config) and (project_root / rel).is_file()
        ]
    patterns = tuple(explicit_surfaces or config.governed_surfaces)
    paths: set[Path] = set()
    for pattern in patterns:
        for path in project_root.glob(pattern):
            rel = relative_path(project_root, path)
            if path.is_file() and is_governed_document_path(rel, config):
                paths.add(path)
    return sorted(paths)


def audit_paths(project_root: Path, paths: Iterable[Path], config: DocumentAuthorConfig) -> list[Finding]:
    findings: list[Finding] = []
    for path in paths:
        rel = relative_path(project_root, path)
        if not is_governed_document_path(rel, config):
            continue
        result = validate_author_metadata(path.read_text(encoding="utf-8"))
        if not result.is_valid:
            findings.append(Finding(rel, result.missing_fields, result.invalid_fields))
    return findings


def _json_payload(project_root: Path, findings: list[Finding], *, changed_only: bool) -> dict[str, object]:
    return {
        "project_root": str(project_root),
        "changed_only": changed_only,
        "finding_count": len(findings),
        "findings": [asdict(finding) for finding in findings],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=".", help="Project root to scan.")
    parser.add_argument("--config", help="Optional config TOML path.")
    parser.add_argument("--changed-only", action="store_true", help="Scan changed governed files only.")
    parser.add_argument("--surfaces", nargs="*", help="Override governed surface glob patterns for this run.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    args = parser.parse_args(argv)

    project_root = Path(args.project_root).resolve()
    config_path = Path(args.config).resolve() if args.config else None
    config = load_config(project_root, config_path)
    paths = candidate_paths(project_root, config, changed_only=args.changed_only, explicit_surfaces=args.surfaces)
    findings = audit_paths(project_root, paths, config)
    payload = _json_payload(project_root, findings, changed_only=args.changed_only)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"Document author provenance findings: {len(findings)}")
        for finding in findings:
            print(f"- {finding.path}: {', '.join(finding.gaps)}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
