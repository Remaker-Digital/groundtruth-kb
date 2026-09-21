#!/usr/bin/env python3
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Read-only audit for source citation anchors that no longer resolve."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path

from groundtruth_kb.authority_client import (
    AuthorityClient,
    AuthorityClientError,
    configured_authority_client,
    page_records,
)
from groundtruth_kb.config import GTConfigError

ANCHOR_RE = re.compile(r"\b(?P<prefix>SPEC|GOV|DCL|ADR|PB|REQ|DELIB|WI|GTKB)-[A-Z0-9][A-Z0-9_-]*\b")
SOURCE_EXTENSIONS = {".py", ".md"}
DEFAULT_SCAN_DIRS = (
    "src",
    "scripts",
    "groundtruth-kb/src",
    "groundtruth-kb/tests",
    "platform_tests",
    "tests",
    ".harness-baseline-configuration",
    ".agents/skills",
)
EXCLUDED_DIRS = {
    ".git",
    "scratchpad",
    "credentials",
    "bridge",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "node_modules",
}


@dataclass(frozen=True)
class Citation:
    anchor: str
    kind: str
    path: str
    line: int


@dataclass(frozen=True)
class AuditResult:
    root: str
    authority_url: str
    scanned_files: int
    resolved: dict[str, int]
    orphans: list[Citation]

    def to_jsonable(self) -> dict[str, object]:
        payload = asdict(self)
        payload["orphans"] = [asdict(orphan) for orphan in self.orphans]
        return payload


def load_resolvable_ids(client: AuthorityClient) -> dict[str, set[str]]:
    """Resolve IDs from current native domains, including retained formal history.

    A deliberation ID is only an existing historical reference; this audit does
    not make its content authoritative. Bridge files are never read or required.
    """
    return {
        kind: {row["id"] for row in page_records(client, endpoint)}
        for kind, endpoint in (
            ("spec", "/v1/specifications"),
            ("deliberation", "/v1/deliberations"),
            ("work_item", "/v1/work-items"),
        )
    }


def _citation_kind(anchor: str) -> str:
    prefix = anchor.split("-", 1)[0]
    if prefix == "DELIB":
        return "deliberation"
    if prefix in {"WI", "GTKB"}:
        return "work_item"
    return "spec"


def _scan_roots(root: Path, scan_dirs: Iterable[Path] | None) -> list[Path]:
    if scan_dirs:
        return [path if path.is_absolute() else root / path for path in scan_dirs]
    configured = [root / rel for rel in DEFAULT_SCAN_DIRS if (root / rel).exists()]
    return configured


def iter_source_files(root: Path, scan_dirs: Iterable[Path] | None = None) -> Iterable[Path]:
    for scan_root in _scan_roots(root, scan_dirs):
        if scan_root.is_file():
            candidates = [scan_root]
        elif scan_root.is_dir():
            candidates = scan_root.rglob("*")
        else:
            continue
        for path in candidates:
            if not path.is_file() or path.suffix not in SOURCE_EXTENSIONS:
                continue
            try:
                relative = path.resolve().relative_to(root.resolve())
            except ValueError:
                continue
            if any(part in EXCLUDED_DIRS for part in relative.parts):
                continue
            yield path


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _find_citations(path: Path, root: Path) -> Iterable[Citation]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="ignore")
    rel_path = _rel(path, root)
    for line_no, line in enumerate(text.splitlines(), start=1):
        for match in ANCHOR_RE.finditer(line):
            anchor = match.group(0)
            yield Citation(anchor=anchor, kind=_citation_kind(anchor), path=rel_path, line=line_no)


def audit_root(
    root: Path, scan_dirs: Iterable[Path] | None = None, *, client: AuthorityClient | None = None
) -> AuditResult:
    root = root.resolve()
    reader = client if client is not None else configured_authority_client(root)
    resolvable = load_resolvable_ids(reader)
    resolved: Counter[str] = Counter()
    orphans: list[Citation] = []
    scanned_files = 0

    for path in iter_source_files(root, scan_dirs):
        scanned_files += 1
        for citation in _find_citations(path, root):
            is_resolved = citation.anchor in resolvable[citation.kind]
            if is_resolved:
                resolved[citation.kind] += 1
            else:
                orphans.append(citation)

    return AuditResult(
        root=str(root),
        authority_url=reader.url,
        scanned_files=scanned_files,
        resolved={kind: resolved.get(kind, 0) for kind in ("spec", "deliberation", "work_item")},
        orphans=orphans,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Project root to scan.")
    parser.add_argument(
        "--scan-dir",
        type=Path,
        action="append",
        default=None,
        help="Directory or file to scan, relative to --root. May be supplied more than once.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    if not root.exists():
        print(json.dumps({"error": f"root not found: {root}"}), file=sys.stderr)
        return 2
    try:
        result = audit_root(root, args.scan_dir)
    except (AuthorityClientError, GTConfigError, OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(result.to_jsonable(), indent=2, sort_keys=True))
    return 1 if result.orphans else 0


if __name__ == "__main__":
    raise SystemExit(main())
