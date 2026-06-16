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

BRIDGE_FILE_STATUS_RE: Final[re.Pattern[str]] = re.compile(
    r"^[#>*\-\s`]*(NEW|REVISED|GO|NO-GO|VERIFIED|WITHDRAWN|ADVISORY|DEFERRED)\b",
    re.IGNORECASE,
)
BRIDGE_PATH_RE: Final[re.Pattern[str]] = re.compile(r"\bbridge/(?P<slug>[A-Za-z0-9_.-]+)-(?P<version>\d{3})\.md\b")
STATUS_AT_VERSION_RE: Final[re.Pattern[str]] = re.compile(
    r"\b(?:NEW|REVISED|GO|NO-GO|VERIFIED)(?:-\d+)?\s+at\s+-(?P<version>\d+)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class BridgeFileVersion:
    status: str
    rel_path: str
    version: int


@dataclass(frozen=True)
class Citation:
    cited_slug: str
    cited_version: int
    source: str
    text: str


def _status_from_bridge_file(path: Path) -> str | None:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None
    for raw in lines:
        stripped = raw.strip()
        if not stripped:
            continue
        match = BRIDGE_FILE_STATUS_RE.match(stripped)
        return match.group(1).upper() if match else None
    return None


def parse_bridge_files(bridge_dir: Path) -> dict[str, list[BridgeFileVersion]]:
    documents: dict[str, list[BridgeFileVersion]] = {}
    for path in bridge_dir.glob("*.md"):
        match = re.match(r"^(?P<slug>.+)-(?P<version>\d{3})\.md$", path.name)
        if match is None:
            continue
        status = _status_from_bridge_file(path)
        if status is None:
            continue
        documents.setdefault(match.group("slug"), []).append(
            BridgeFileVersion(
                status=status,
                rel_path=f"bridge/{path.name}",
                version=int(match.group("version")),
            )
        )
    return {
        slug: sorted(versions, key=lambda version: version.version, reverse=True)
        for slug, versions in documents.items()
    }


def latest_versions(index_documents: dict[str, list[BridgeFileVersion]]) -> dict[str, BridgeFileVersion]:
    latest: dict[str, BridgeFileVersion] = {}
    for slug, versions in index_documents.items():
        if versions:
            latest[slug] = versions[0]
    return latest


def find_operative_file(bridge_id: str, *, bridge_dir: Path) -> Path | None:
    versions = parse_bridge_files(bridge_dir).get(bridge_id, [])
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


def _warning_for(citation: Citation, latest: BridgeFileVersion) -> dict[str, Any]:
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
            f"Citation of {cited_path} references a bridge thread not found in numbered bridge files. "
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
    bridge_dir: Path = DEFAULT_BRIDGE_DIR,
    content_file: Path | None = None,
) -> dict[str, Any]:
    index_documents = parse_bridge_files(bridge_dir)
    latest = latest_versions(index_documents)
    operative = content_file or find_operative_file(bridge_id, bridge_dir=bridge_dir)
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
        "bridge_state": str(bridge_dir),
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
    parser.add_argument("--bridge-dir", type=Path, default=DEFAULT_BRIDGE_DIR)
    parser.add_argument("--content-file", type=Path, default=None)
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--json", action="store_true", help="Compatibility alias for --format json.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_argparser().parse_args(argv)
    packet = build_packet(
        bridge_id=args.bridge_id,
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
