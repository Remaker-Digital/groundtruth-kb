#!/usr/bin/env python3
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Mechanical verdict-evidence-anchor preflight (WI-4520).

Validate that a Loyal Opposition ``NO-GO`` or ``VERIFIED`` bridge verdict cites
line numbers and quoted strings that actually exist in the *operative file it is
reviewing*. This prevents fabricated/hallucinated verdict findings of the
WI-4520 class: an Antigravity (gemini) ``NO-GO`` that cited a non-existent
"Draft Template Placeholder" at line 86 of a proposal whose line 86 was
``## Implementation Plan``.

Design contract (per bridge/gtkb-antigravity-lo-hallucination-prevention-005.md
plus the implementation-time false-positive hardening documented in the
post-implementation report):

- Gated statuses: ``NO-GO`` and ``VERIFIED`` only.
- **Operative-file scope.** Only citations to the verdict's operative document
  (the ``reviewed_document`` / ``Responds to`` header target) are checked.
  Citations to other files mentioned in passing are NOT checked, because a
  verdict legitimately references retired, moved, or proposed files whose
  current on-disk state says nothing about whether the verdict was fabricated.
  WI-4520's failure mode was always about the reviewed file's own content.
- **Conservative by design.** Ambiguous citations PASS. No operative-document
  header => no check. A quoted span is treated as an exact-text claim only when
  it is multi-word AND its line carries a cue word ("citing", "reads", ...).
  This gate hard-blocks the bridge, so a false positive that blocks a
  legitimate verdict is worse than the failure mode it guards against.
- **Opt-outs.** A finding line carrying ``[inference]``, ``[no exact anchor]``,
  or ``[absent]``, or absence phrasing ("missing", "does not exist", ...) is not
  required to anchor to present content.
- **Self-reference safety.** Anchors are validated against the operative file
  the verdict CITES, never against the verdict file being written.

Reusable surface (imported by both enforcement chokepoints):

- ``validate_verdict_evidence_anchors(content, *, project_root) -> list``
- ``VerdictEvidenceAnchorError`` (raised by ``write_bridge_file`` on violations)
- ``violation_summary(violations) -> str`` (one-line deny/raise message)

This module aligns with the parsing conventions of
``scripts/bridge_citation_freshness_preflight.py`` (DELIB-20261563) rather than
duplicating them: that preflight checks cross-thread *version* freshness; this
one checks intra-file *line/string* anchors against the operative document.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Final

PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parent.parent

# Verdict statuses whose evidence anchors are gated.
GATED_STATUSES: Final[frozenset[str]] = frozenset({"NO-GO", "VERIFIED"})

# Minimum length of a quoted span considered a citable exact-text anchor.
MIN_QUOTE_LEN: Final[int] = 8
# Max character gap between a quoted span and a bare "line N" reference for the
# quote to be treated as that line's claimed content.
QUOTE_ADJACENCY: Final[int] = 60

_STATUS_LINE_RE: Final[re.Pattern[str]] = re.compile(
    r"^[#>*\-\s`]*(NEW|REVISED|GO|NO-GO|VERIFIED|WITHDRAWN|ADVISORY|DEFERRED)\b",
    re.IGNORECASE,
)

# Opt-out markers and absence phrasing. A verdict line carrying any of these is
# exempt from anchoring (the reviewer is explicitly NOT claiming present text).
_OPT_OUT_RE: Final[re.Pattern[str]] = re.compile(
    r"\[\s*(?:inference|no\s+exact\s+anchor|absent)\s*\]",
    re.IGNORECASE,
)
_ABSENCE_RE: Final[re.Pattern[str]] = re.compile(
    r"\b(?:missing|absent|lacks?|does\s+not\s+exist|doesn't\s+exist|do\s+not\s+exist|"
    r"no\s+longer|not\s+present|removed|never\s+exist(?:s|ed)?|returns?\s+no\s+match(?:es)?|"
    r"no\s+match(?:es)?|should\s+(?:add|create)|to\s+be\s+(?:added|created))\b",
    re.IGNORECASE,
)

# Explicit "<path>:<line>" or "<path>:<start>-<end>" citation. Requires a path
# with at least one directory separator and a file extension, so timestamps
# ("01:36:31"), hashes ("sha256:..."), and version tokens do not match.
_FILE_LINE_RE: Final[re.Pattern[str]] = re.compile(
    r"(?P<file>(?:[A-Za-z]:)?[\w.\-]+(?:[\\/][\w.\-]+)+\.[A-Za-z0-9]+)"
    r":(?P<start>\d+)(?:\s*[-–]\s*(?P<end>\d+))?"
)
# Bare "line N" / "lines N-M" citation; the file is the verdict's operative doc.
# The leading negative lookbehind keeps compound CLI flags like
# "--preview-lines 500" from being mis-parsed as a "lines 500" citation.
_BARE_LINE_RE: Final[re.Pattern[str]] = re.compile(
    r"(?<![\w-])lines?\s+(?P<start>\d+)(?:\s*[-–]\s*(?P<end>\d+))?",
    re.IGNORECASE,
)

# Any file-path token (separator + extension). Used to detect when a verdict
# line that carries a bare "line N" citation also mentions a NON-operative file
# (a source path, a CLI command path, ...), in which case the bare line refers
# to that file rather than the operative document and is NOT attributed here.
_PATH_TOKEN_RE: Final[re.Pattern[str]] = re.compile(r"(?:[A-Za-z]:)?[\w.\-]+(?:[\\/][\w.\-]+)+\.[A-Za-z0-9]+")

# Operative-document header fields a verdict uses to name the file under review.
_OPERATIVE_HEADER_RE: Final[re.Pattern[str]] = re.compile(
    r"^\s*(?:reviewed_document|responds[ _]to|reviewed[ _]file|operative[ _]file)"
    r"\s*[:=]\s*`?(?P<path>[^`\s]+)`?",
    re.IGNORECASE | re.MULTILINE,
)

# Quoted-span matchers. Backticks are intentionally excluded: in verdict
# markdown they denote code / paths / identifiers (including the file:line
# citation itself), not exact-text claims. The single-quote matcher uses letter
# boundaries so contraction apostrophes ("doesn't") are not mis-parsed.
_QUOTE_RES: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(r'"([^"\n]+)"'),
    re.compile(r"(?<![A-Za-z])'([^'\n]+)'(?![A-Za-z])"),
)

# A quoted span is treated as an exact-text claim only when the verdict line
# also carries a cue word linking the quote to the citation. Without a cue, a
# quoted span is an incidental concept reference and is skipped.
_CITATION_CUE_RE: Final[re.Pattern[str]] = re.compile(
    r"\b(?:cit(?:e|es|ed|ing)|contain(?:s|ed|ing)?|reads?|says?|quot(?:e|es|ed|ing)|"
    r"placeholder|claim(?:s|ed|ing)?|label(?:s|ed|led|ling)?|states?)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class AnchorViolation:
    """A confidently-invalid evidence anchor found in a gated verdict."""

    kind: str  # "missing_file" | "line_out_of_range" | "string_not_found"
    cited_file: str
    detail: str
    evidence_line: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def first_nonblank_line(content: str) -> str:
    for raw in content.splitlines():
        stripped = raw.strip()
        if stripped:
            return stripped.lstrip("﻿")
    return ""


def verdict_status(content: str) -> str | None:
    """Return the canonical gated status token, or None when not gated."""
    match = _STATUS_LINE_RE.match(first_nonblank_line(content))
    if not match:
        return None
    token = match.group(1).upper()
    return token if token in GATED_STATUSES else None


def _norm_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _norm_path(raw: str) -> str:
    """Normalize a path token for operative-file comparison."""
    cleaned = raw.replace("\\", "/").strip().strip("`")
    cleaned = re.sub(r"^\./+", "", cleaned).lstrip("/")
    return cleaned.lower()


def _resolve_path(project_root: Path, raw: str) -> Path:
    normalized = raw.replace("\\", "/").lstrip("/")
    return project_root / normalized


def _read_lines(path: Path) -> list[str] | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None


def _operative_files(content: str) -> list[str]:
    """Return the operative-document path(s) a verdict declares it is reviewing."""
    paths: list[str] = []
    for match in _OPERATIVE_HEADER_RE.finditer(content):
        candidate = match.group("path").strip().strip("`")
        if candidate and candidate not in paths:
            paths.append(candidate)
    return paths


def _line_is_exempt(line: str) -> bool:
    return bool(_OPT_OUT_RE.search(line) or _ABSENCE_RE.search(line))


def _quote_spans(line: str) -> list[tuple[int, int, str]]:
    """Return (start, end, text) for citable exact-text quotes on a line.

    A quote is citable only if it is multi-word and at least ``MIN_QUOTE_LEN``
    characters: single-token concept words and truncated ("...") quotes are
    excluded to avoid false exact-text claims.
    """
    spans: list[tuple[int, int, str]] = []
    for quote_re in _QUOTE_RES:
        for match in quote_re.finditer(line):
            text = match.group(1).strip()
            if len(text) < MIN_QUOTE_LEN or " " not in text:
                continue
            if "..." in text or "…" in text:
                continue
            spans.append((match.start(1), match.end(1), text))
    return spans


def _span_gap(a: tuple[int, int], b: tuple[int, int]) -> int:
    return max(0, max(a[0], b[0]) - min(a[1], b[1]))


def _near_a_bare_line(quote_span: tuple[int, int], bare_spans: list[tuple[int, int]]) -> bool:
    return any(_span_gap(quote_span, bare) <= QUOTE_ADJACENCY for bare in bare_spans)


def validate_verdict_evidence_anchors(
    content: str,
    *,
    project_root: Path | None = None,
) -> list[AnchorViolation]:
    """Return confidently-invalid evidence-anchor violations in a gated verdict.

    Only citations to the verdict's operative document (the ``reviewed_document``
    / ``Responds to`` header target) are checked. An empty list means PASS
    (not a gated verdict, no operative-document header, or no violations).
    """
    if verdict_status(content) is None:
        return []
    root = project_root or PROJECT_ROOT
    operative_paths = _operative_files(content)
    if not operative_paths:
        return []
    op_by_norm = {_norm_path(path): path for path in operative_paths}
    single_op = operative_paths[0] if len(operative_paths) == 1 else None

    lines_cache: dict[str, list[str] | None] = {}

    def _operative_lines(raw_path: str) -> list[str] | None:
        if raw_path not in lines_cache:
            lines_cache[raw_path] = _read_lines(_resolve_path(root, raw_path))
        return lines_cache[raw_path]

    violations: list[AnchorViolation] = []
    seen: set[tuple[str, str, str]] = set()

    def _record(violation: AnchorViolation) -> None:
        key = (violation.kind, violation.cited_file, violation.detail)
        if key not in seen:
            seen.add(key)
            violations.append(violation)

    for raw_line in content.splitlines():
        if _line_is_exempt(raw_line):
            continue

        evidence = _norm_ws(raw_line)[:200]

        # Explicit "<operative-file>:<line>" citations get a line-range check.
        explicit_ops: list[tuple[str, int, int]] = []
        for match in _FILE_LINE_RE.finditer(raw_line):
            raw_path = op_by_norm.get(_norm_path(match.group("file")))
            if raw_path is None:
                continue  # citation to a non-operative file -> not checked
            start = int(match.group("start"))
            end = int(match.group("end")) if match.group("end") else start
            explicit_ops.append((raw_path, start, end))

        for raw_path, start, end in explicit_ops:
            lines = _operative_lines(raw_path)
            if lines is None:
                _record(
                    AnchorViolation(
                        kind="missing_file",
                        cited_file=raw_path,
                        detail=f"operative file not found (line(s) {start}-{end} cited)",
                        evidence_line=evidence,
                    )
                )
                continue
            total = len(lines)
            if start < 1 or end < start or end > total:
                _record(
                    AnchorViolation(
                        kind="line_out_of_range",
                        cited_file=raw_path,
                        detail=f"cited line(s) {start}-{end} outside operative file bounds 1-{total}",
                        evidence_line=evidence,
                    )
                )

        # String check: a quoted exact-text claim is verified only when it sits
        # adjacent to a bare "line N" reference that resolves to the single
        # operative document, with no non-operative path on the line. This is
        # the WI-4520 form ("at line 86 ('<fabricated text>')") and it excludes
        # quotes attributed to specs, docs, prior verdicts, or other proposals.
        # The quote is searched across the WHOLE operative document (not a
        # window): a fabricated quote is text nowhere in the file, while a real
        # quote cited at a slightly wrong line still passes.
        if single_op is None or not _CITATION_CUE_RE.search(raw_line):
            continue
        if "://" in raw_line:  # external URL reference -> not an operative-document claim
            continue
        if any(_norm_path(token) not in op_by_norm for token in _PATH_TOKEN_RE.findall(raw_line)):
            continue
        quote_spans = _quote_spans(raw_line)
        if not quote_spans:
            continue
        # A bare-line reference inside a quoted span is part of the quoted text,
        # not a citation OF it, so it cannot anchor that quote.
        bare_spans = [
            span
            for span in (match.span() for match in _BARE_LINE_RE.finditer(raw_line))
            if not any(qs <= span[0] and span[1] <= qe for qs, qe, _ in quote_spans)
        ]
        if not bare_spans:
            continue
        op_lines = _operative_lines(single_op)
        if op_lines is None:
            continue
        file_text = _norm_ws(" ".join(op_lines))
        for q_start, q_end, quote in quote_spans:
            if not _near_a_bare_line((q_start, q_end), bare_spans):
                continue
            if _norm_ws(quote) not in file_text:
                _record(
                    AnchorViolation(
                        kind="string_not_found",
                        cited_file=single_op,
                        detail=f"quoted text {quote!r} not present in operative document",
                        evidence_line=evidence,
                    )
                )

    return violations


def violation_summary(violations: list[AnchorViolation]) -> str:
    """Return a single-line, deny/raise-ready summary of anchor violations."""
    if not violations:
        return "no evidence-anchor violations"
    parts = [f"{v.kind} [{v.cited_file}]: {v.detail}" for v in violations]
    return "; ".join(parts)


class VerdictEvidenceAnchorError(RuntimeError):
    """Raised by a verdict writer when a gated verdict has invalid anchors."""

    def __init__(self, violations: list[AnchorViolation]):
        self.violations = violations
        super().__init__(
            "verdict cites evidence anchors that do not exist in the operative "
            "document: " + violation_summary(violations) + ". Fix the citation, or "
            "mark the finding [inference] / [no exact anchor] / [absent] if it is "
            "intentionally not an exact-text claim."
        )


def render_markdown(packet: dict[str, Any]) -> str:
    lines = ["## Verdict Evidence Anchors", ""]
    violations = packet["violations"]
    if not packet["gated"]:
        lines.append("Status is not a gated NO-GO/VERIFIED verdict; no anchor check performed.")
        return "\n".join(lines) + "\n"
    if not violations:
        lines.append("No invalid evidence anchors detected.")
        return "\n".join(lines) + "\n"
    lines.extend(["| Kind | Cited File | Detail | Evidence Line |", "|---|---|---|---|"])
    for violation in violations:
        lines.append(
            f"| `{violation['kind']}` | `{violation['cited_file']}` | "
            f"{violation['detail']} | {violation['evidence_line']} |"
        )
    return "\n".join(lines) + "\n"


def build_packet(*, content: str, project_root: Path | None = None) -> dict[str, Any]:
    root = project_root or PROJECT_ROOT
    status = verdict_status(content)
    violations = validate_verdict_evidence_anchors(content, project_root=root)
    packet: dict[str, Any] = {
        "status": status,
        "gated": status is not None,
        "violations": [violation.to_dict() for violation in violations],
        "violation_count": len(violations),
        "summary": violation_summary(violations),
    }
    packet["markdown"] = render_markdown(packet)
    return packet


def _build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--content-file", type=Path, required=True, help="Verdict file to check.")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--json", action="store_true", help="Compatibility alias for --format json.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_argparser().parse_args(argv)
    content = args.content_file.read_text(encoding="utf-8")
    packet = build_packet(content=content, project_root=args.project_root)
    if args.json or args.format == "json":
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print(packet["markdown"], end="")
    # Exit 5 signals a blocking violation (mirrors the clause-preflight convention).
    return 5 if packet["violation_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
