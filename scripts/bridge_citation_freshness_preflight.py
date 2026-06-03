#!/usr/bin/env python3
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Advisory preflight for stale cross-thread bridge citations."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Final

PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parent.parent
DEFAULT_BRIDGE_DIR: Final[Path] = PROJECT_ROOT / "bridge"
DEFAULT_INDEX_PATH: Final[Path] = DEFAULT_BRIDGE_DIR / "INDEX.md"

INDEX_DOC_RE: Final[re.Pattern[str]] = re.compile(r"^Document:\s+(\S+)\s*$")
INDEX_STATUS_RE: Final[re.Pattern[str]] = re.compile(
    r"^(NEW|REVISED|GO|NO-GO|VERIFIED|WITHDRAWN|ADVISORY|DEFERRED):\s+(bridge/\S+?-(\d+)\.md)\s*$"
)
BRIDGE_PATH_RE: Final[re.Pattern[str]] = re.compile(r"\bbridge/(?P<slug>[A-Za-z0-9_.-]+)-(?P<version>\d{3})\.md\b")
STATUS_AT_VERSION_RE: Final[re.Pattern[str]] = re.compile(
    r"\b(?:NEW|REVISED|GO|NO-GO|VERIFIED)(?:-\d+)?\s+at\s+-(?P<version>\d+)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class IndexVersion:
    status: str
    rel_path: str
    version: int


@dataclass(frozen=True)
class Citation:
    cited_slug: str
    cited_version: int
    source: str
    text: str


def parse_index(index_path: Path) -> dict[str, list[IndexVersion]]:
    if not index_path.is_file():
        return {}
    documents: dict[str, list[IndexVersion]] = {}
    current_doc: str | None = None
    for raw_line in index_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        doc_match = INDEX_DOC_RE.match(line)
        if doc_match:
            current_doc = doc_match.group(1)
            documents.setdefault(current_doc, [])
            continue
        if current_doc is None:
            continue
        if not line:
            current_doc = None
            continue
        status_match = INDEX_STATUS_RE.match(line)
        if not status_match:
            continue
        documents[current_doc].append(
            IndexVersion(
                status=status_match.group(1),
                rel_path=status_match.group(2),
                version=int(status_match.group(3)),
            )
        )
    return documents


def latest_versions(index_documents: dict[str, list[IndexVersion]]) -> dict[str, IndexVersion]:
    latest: dict[str, IndexVersion] = {}
    for slug, versions in index_documents.items():
        if versions:
            latest[slug] = versions[0]
    return latest


def find_operative_file(bridge_id: str, *, index_path: Path, bridge_dir: Path) -> Path | None:
    versions = parse_index(index_path).get(bridge_id, [])
    if versions:
        return bridge_dir.parent / versions[0].rel_path
    candidates = sorted(bridge_dir.glob(f"{bridge_id}-*.md"))
    return candidates[-1] if candidates else None


def _context_window(text: str, start: int, end: int, *, radius: int = 160) -> str:
    return text[max(0, start - radius) : min(len(text), end + radius)]


def extract_citations(content: str, *, known_slugs: set[str], bridge_id: str) -> list[Citation]:
    citations: list[Citation] = []
    seen: set[tuple[str, int, str]] = set()

    for match in BRIDGE_PATH_RE.finditer(content):
        slug = match.group("slug")
        version = int(match.group("version"))
        if slug == bridge_id:
            continue
        key = (slug, version, "path")
        if key in seen:
            continue
        seen.add(key)
        citations.append(
            Citation(
                cited_slug=slug,
                cited_version=version,
                source="path",
                text=match.group(0),
            )
        )

    for slug in sorted(known_slugs):
        if slug == bridge_id:
            continue
        for slug_match in re.finditer(rf"\b{re.escape(slug)}\b", content):
            window = _context_window(content, slug_match.start(), slug_match.end())
            for status_match in STATUS_AT_VERSION_RE.finditer(window):
                version = int(status_match.group("version"))
                key = (slug, version, "status_at")
                if key in seen:
                    continue
                seen.add(key)
                citations.append(
                    Citation(
                        cited_slug=slug,
                        cited_version=version,
                        source="status_at",
                        text=status_match.group(0),
                    )
                )
    return citations


def _version_path(slug: str, version: int) -> str:
    return f"bridge/{slug}-{version:03d}.md"


def _warning_for(citation: Citation, latest: IndexVersion) -> dict[str, Any]:
    latest_path = latest.rel_path
    cited_path = _version_path(citation.cited_slug, citation.cited_version)
    return {
        "cited_slug": citation.cited_slug,
        "cited_version": citation.cited_version,
        "cited_path": cited_path,
        "latest_version": latest.version,
        "latest_path": latest_path,
        "latest_status": latest.status,
        "severity": "warn",
        "source": citation.source,
        "cleanup_hint": (
            f"Citation of {cited_path} is stale; {latest_path} is the current latest version "
            f"(status {latest.status}). Update the citation or document why the historical version is intentionally cited."
        ),
    }


def _missing_for(citation: Citation) -> dict[str, Any]:
    cited_path = _version_path(citation.cited_slug, citation.cited_version)
    return {
        "cited_slug": citation.cited_slug,
        "cited_version": citation.cited_version,
        "cited_path": cited_path,
        "severity": "warn",
        "source": citation.source,
        "cleanup_hint": (
            f"Citation of {cited_path} references a bridge thread not found in bridge/INDEX.md. "
            "Check the slug or document why the citation cannot be resolved."
        ),
    }


def render_markdown(packet: dict[str, Any]) -> str:
    lines = ["## Citation Freshness", ""]
    warnings = packet["warnings"]
    missing = packet["missing_citations"]
    if not warnings and not missing:
        lines.append("No stale cross-thread citations detected.")
        return "\n".join(lines) + "\n"

    if warnings:
        lines.extend(
            [
                "| Cited Thread | Cited Version | Latest Version | Latest Status | Cleanup Hint |",
                "|---|---:|---:|---|---|",
            ]
        )
        for warning in warnings:
            lines.append(
                "| "
                f"`{warning['cited_slug']}` | "
                f"{warning['cited_version']} | "
                f"{warning['latest_version']} | "
                f"`{warning['latest_status']}` | "
                f"{warning['cleanup_hint']} |"
            )
    if missing:
        if warnings:
            lines.append("")
        lines.extend(
            [
                "| Unresolved Thread | Cited Version | Cleanup Hint |",
                "|---|---:|---|",
            ]
        )
        for item in missing:
            lines.append(f"| `{item['cited_slug']}` | {item['cited_version']} | {item['cleanup_hint']} |")
    return "\n".join(lines) + "\n"


def build_packet(
    *,
    bridge_id: str,
    index_path: Path = DEFAULT_INDEX_PATH,
    bridge_dir: Path = DEFAULT_BRIDGE_DIR,
    content_file: Path | None = None,
) -> dict[str, Any]:
    index_documents = parse_index(index_path)
    latest = latest_versions(index_documents)
    operative = content_file or find_operative_file(bridge_id, index_path=index_path, bridge_dir=bridge_dir)
    content = operative.read_text(encoding="utf-8") if operative and operative.is_file() else ""
    citations = extract_citations(content, known_slugs=set(latest), bridge_id=bridge_id)

    warnings: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    for citation in citations:
        current = latest.get(citation.cited_slug)
        if current is None:
            missing.append(_missing_for(citation))
            continue
        if citation.cited_version != current.version:
            warnings.append(_warning_for(citation, current))

    packet: dict[str, Any] = {
        "bridge_id": bridge_id,
        "content_file": str(operative) if operative else None,
        "index_path": str(index_path),
        "citations": [asdict(citation) for citation in citations],
        "warnings": warnings,
        "missing_citations": missing,
        "warning_count": len(warnings),
        "missing_count": len(missing),
    }
    packet["markdown"] = render_markdown(packet)
    return packet


def _build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bridge-id", required=True, help="Bridge document id / slug to inspect.")
    parser.add_argument("--index-path", type=Path, default=DEFAULT_INDEX_PATH)
    parser.add_argument("--bridge-dir", type=Path, default=DEFAULT_BRIDGE_DIR)
    parser.add_argument("--content-file", type=Path, default=None)
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--json", action="store_true", help="Compatibility alias for --format json.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_argparser().parse_args(argv)
    packet = build_packet(
        bridge_id=args.bridge_id,
        index_path=args.index_path,
        bridge_dir=args.bridge_dir,
        content_file=args.content_file,
    )
    if args.json or args.format == "json":
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print(packet["markdown"], end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
