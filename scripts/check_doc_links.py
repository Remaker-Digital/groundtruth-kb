"""Focused link-integrity checker for the adopter documentation path.

`mkdocs build --strict` exits 0 even when it reports an existing
missing-anchor info message. That is not acceptable for a fail-closed
adopter-path gate. This checker walks the adopter path explicitly and
fails on missing pages AND missing anchors, per Codex condition 3 of
`bridge/gtkb-start-here-adopter-rewrite-implementation-002.md`.

Adopter path (cover set, not full repo):

    README.md -> docs/start-here.md -> {
        docs/evidence.md,
        docs/day-in-the-life.md,
        docs/known-limitations.md,
        docs/groundtruth-kb-executive-overview.md,
    }

Plus all Markdown links within those pages, resolved transitively to
depth 2 so a broken link from the adopter landing to the method docs is
still caught.

Usage:
    python scripts/check_doc_links.py            # full adopter-path sweep
    python scripts/check_doc_links.py --verbose  # print every link checked

Exit codes:
    0 — all adopter-path links resolved (pages + anchors).
    1 — missing pages, missing anchors, or both.
    2 — invocation error (unexpected path, argument problem).
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import unquote, urlparse

REPO_ROOT = Path(__file__).resolve().parent.parent

ADOPTER_ROOTS = [
    REPO_ROOT / "README.md",
    REPO_ROOT / "docs" / "start-here.md",
    REPO_ROOT / "docs" / "evidence.md",
    REPO_ROOT / "docs" / "day-in-the-life.md",
    REPO_ROOT / "docs" / "known-limitations.md",
    REPO_ROOT / "docs" / "groundtruth-kb-executive-overview.md",
]

MAX_TRANSITIVE_DEPTH = 2

# Markdown link regex: [text](url) — tolerant of parentheses in URLs via
# a lazy match up to the first unescaped closing paren.
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
# ATX + setext heading extraction for anchor resolution.
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$", re.MULTILINE)
# HTML anchor (e.g., <a name="foo"> / <a id="foo">).
HTML_ANCHOR_RE = re.compile(r'<a\s+(?:name|id)\s*=\s*"([^"]+)"', re.IGNORECASE)


@dataclass
class Finding:
    source: Path
    link_text: str
    target: str
    reason: str


@dataclass
class Report:
    checked: int = 0
    failures: list[Finding] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.failures


def _slugify(text: str) -> str:
    """Convert a heading to a MkDocs-style anchor slug.

    Matches the mkdocs-material default slugifier closely enough for our
    purposes: lowercase, non-alphanumerics (except hyphens) removed,
    spaces replaced with hyphens, consecutive hyphens collapsed.
    """
    text = text.strip().lower()
    # Strip markdown inline code fences and emphasis markers that appear in headings.
    text = re.sub(r"[`*_~]", "", text)
    # Replace any run of non-alphanum (except hyphen) with a hyphen.
    text = re.sub(r"[^a-z0-9\-]+", "-", text)
    # Collapse runs of hyphens.
    text = re.sub(r"-+", "-", text).strip("-")
    return text


def _extract_anchors(md_path: Path) -> set[str]:
    if not md_path.exists():
        return set()
    content = md_path.read_text(encoding="utf-8", errors="replace")
    anchors: set[str] = set()
    for match in HEADING_RE.finditer(content):
        anchors.add(_slugify(match.group(2)))
    for match in HTML_ANCHOR_RE.finditer(content):
        anchors.add(match.group(1).strip())
    return anchors


def _resolve_target(source: Path, target: str) -> tuple[Path | None, str | None, bool]:
    """Resolve (target_path, anchor, is_external).

    Returns (None, None, True) for external / mailto links.
    """
    parsed = urlparse(target)
    if parsed.scheme in {"http", "https", "mailto", "ftp"}:
        return None, None, True
    # Drop query string; keep anchor.
    path_part = unquote(parsed.path)
    anchor = parsed.fragment or None
    if not path_part:
        # Same-page anchor like #section.
        return source, anchor, False
    # Relative path resolution against the source's parent directory.
    candidate = (source.parent / path_part).resolve()
    return candidate, anchor, False


def _check_file(md_path: Path, report: Report, queue: list[tuple[Path, int]], depth: int, verbose: bool) -> None:
    if not md_path.exists():
        report.failures.append(
            Finding(
                source=md_path,
                link_text="(root file)",
                target=str(md_path),
                reason="Adopter-path root does not exist",
            )
        )
        return
    try:
        content = md_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        report.failures.append(
            Finding(
                source=md_path,
                link_text="(read)",
                target=str(md_path),
                reason=f"Read failed: {exc}",
            )
        )
        return

    for link_text, raw_target in LINK_RE.findall(content):
        report.checked += 1
        target_path, anchor, is_external = _resolve_target(md_path, raw_target)
        if is_external:
            if verbose:
                print(f"  [skip external] {md_path.name}: {raw_target}")
            continue
        if target_path is None:
            continue
        # Point to target file (rewrite to the closest readable file).
        if target_path.is_dir():
            # Some links target a directory expecting index.md.
            candidate_index = target_path / "index.md"
            if candidate_index.exists():
                target_path = candidate_index
            else:
                report.failures.append(
                    Finding(
                        source=md_path,
                        link_text=link_text,
                        target=raw_target,
                        reason=f"Target directory has no index.md: {target_path}",
                    )
                )
                continue
        if not target_path.exists():
            report.failures.append(
                Finding(
                    source=md_path,
                    link_text=link_text,
                    target=raw_target,
                    reason=f"Target file missing: {target_path}",
                )
            )
            continue
        if anchor:
            anchors = _extract_anchors(target_path)
            if _slugify(anchor) not in anchors and anchor not in anchors:
                report.failures.append(
                    Finding(
                        source=md_path,
                        link_text=link_text,
                        target=raw_target,
                        reason=f"Anchor '#{anchor}' not found in {target_path.name}",
                    )
                )
                continue
        if verbose:
            print(f"  [ok] {md_path.name} -> {target_path.name}{('#' + anchor) if anchor else ''}")

        # Queue Markdown targets for transitive scanning.
        if target_path.suffix == ".md" and depth + 1 <= MAX_TRANSITIVE_DEPTH:
            queue.append((target_path, depth + 1))


def check(verbose: bool = False) -> Report:
    report = Report()
    seen: set[Path] = set()
    queue: list[tuple[Path, int]] = [(path, 0) for path in ADOPTER_ROOTS]
    while queue:
        path, depth = queue.pop(0)
        try:
            resolved = path.resolve()
        except OSError:
            resolved = path
        if resolved in seen:
            continue
        seen.add(resolved)
        if verbose:
            print(f"[depth={depth}] {resolved.relative_to(REPO_ROOT) if REPO_ROOT in resolved.parents else resolved}")
        _check_file(path, report, queue, depth, verbose)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", "-v", action="store_true", help="Print every link checked.")
    args = parser.parse_args()

    report = check(verbose=args.verbose)
    print()
    print(f"Links checked: {report.checked}")
    print(f"Failures:      {len(report.failures)}")
    if report.failures:
        print()
        for finding in report.failures:
            try:
                source_rel = finding.source.resolve().relative_to(REPO_ROOT)
            except (OSError, ValueError):
                source_rel = finding.source
            print(f"  FAIL {source_rel}: [{finding.link_text}]({finding.target})")
            print(f"       {finding.reason}")
        return 1
    print("All adopter-path links resolved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
