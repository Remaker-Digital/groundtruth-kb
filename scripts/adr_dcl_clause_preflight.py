"""ADR/DCL clause-test preflight (Slice 2, mandatory gate).

Per ``bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-003.md``
(GO at ``-004``): this CLI is the companion preflight surface to the existing
``scripts/bridge_applicability_preflight.py``. Where the existing tool checks
citation presence for required cross-cutting specs, this tool loads the
ADR/DCL clause registry at ``config/governance/adr-dcl-clauses.toml`` and
asks a finer-grained question for each registered clause:

- Does the bridge proposal/report's content + path token surface trigger
  this clause? (must_apply / may_apply / not_applicable)
- For ``must_apply`` clauses, does the bridge text contain evidence that
  satisfies the clause?
- Are any failure-pattern markers present that would refute the evidence?
- Is the clause owner-waived in the bridge content?

CLAUSE-IN-ROOT may opt into disclosure-block handling for failure-pattern
checks. When ``failure_pattern_disclosure_exempt`` is true, paired
``<!-- in-root-disclosure -->`` ... ``<!-- /in-root-disclosure -->`` spans are
removed before applying the failure pattern, then raw ``target_paths`` metadata
lines from the original content are appended back into the scanned text. This
allows honest non-artifact path disclosures while preserving enforcement on the
declared artifact path surface.

**Default invocation is mandatory.** Returns exit ``5`` when any must_apply
clause with both ``severity = "blocking"`` and ``enforcement_mode = "blocking"``
lacks satisfying evidence and is not explicitly owner-waived. Returns exit ``0``
otherwise.

The ``--report-only`` flag is **diagnostic only**: it prepends an unconditional
non-authorization banner to the markdown output but preserves the default
invocation's exit code. ``--report-only`` output CANNOT satisfy GO/VERIFIED.
The only valid bypass for a real blocking gap is an explicit owner-waiver line
in the bridge content (per ``.claude/rules/file-bridge-protocol.md``):

    Owner waiver: <clause_id> — <DELIB-ID> — <one-line reason>

Clauses with ``enforcement_mode = "advisory"`` are reported but never gate
(intended for newly-added Slice-4 ratchet additions still being tuned).

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CLAUSES_CONFIG = PROJECT_ROOT / "config" / "governance" / "adr-dcl-clauses.toml"
DEFAULT_BRIDGE_DIR = PROJECT_ROOT / "bridge"
IN_ROOT_DISCLOSURE_BLOCK_RE = re.compile(
    r"<!--\s*in-root-disclosure\s*-->.*?<!--\s*/in-root-disclosure\s*-->",
    re.IGNORECASE | re.DOTALL,
)
TARGET_PATHS_DECLARATION_RE = re.compile(
    r"^\s*(?:\*\*)?target_paths?(?:\*\*)?\s*[:=]",
    re.IGNORECASE,
)
DOCUMENT_DECLARATION_RE = re.compile(r"(?im)^\s*Document:\s*([A-Za-z0-9_.-]+)\s*$")
MARKDOWN_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*$")
DISCLOSURE_CONTEXT_HEADING_RE = re.compile(
    r"(?i)\b(?:observed results?|command(?:s executed| output)|test output|diagnostics?|stderr|stdout|"
    r"environment|notes?|context|findings)\b"
)
ARTIFACT_DECLARATION_HEADING_RE = re.compile(
    r"(?i)\b(?:files?\s+(?:changed|modified|created|deleted)|changed files?|target paths?|paths changed|"
    r"generated (?:artifacts?|files?)|outputs?|output paths?|artifacts?)\b"
)
DISCLOSURE_CONTEXT_LINE_RE = re.compile(
    r"(?i)\b(?:diagnostic(?:s)?|disclosure|observed|stderr|stdout|log(?:ged)?|traceback|pytest|"
    r"fixture setup|temp(?:orary)? directory|harness[- ]local|local harness|operator context|"
    r"test environment|command output|repo[- ]local)\b"
)
ARTIFACT_DECLARATION_LINE_RE = re.compile(
    r"(?ix)"
    r"\btarget_paths?\b|"
    r"\bfiles?\s+changed\b|"
    r"\boutputs?\s+(?:go(?:es)?|went|land(?:s)?|reside|write|writes|written|generated|created|stored|saved|under|to)\b|"
    r"\b(?:write|writes|written|create|creates|created|generate|generates|generated|store|stores|stored|"
    r"save|saves|saved)\s+(?:to|under|at)\b|"
    r"\b(?:artifact|output|file)s?\s+(?:path|under|outside|escape|escapes|outside)\b|"
    r"^\s*[-*]\s+`?(?:[A-Za-z]:\\|/tmp/|C:\\temp\\)"
)


@dataclass(frozen=True)
class Clause:
    clause_id: str
    spec_id: str
    description: str
    applies_when_path: tuple[str, ...]
    applies_when_doc_name: tuple[str, ...]
    applies_when_content: tuple[str, ...]
    evidence_required: str
    evidence_pattern: str | None
    failure_condition: str
    failure_pattern: str | None
    severity: str
    waiver_policy: str
    enforcement_mode: str
    failure_pattern_disclosure_exempt: bool = False


@dataclass
class ClauseResult:
    clause: Clause
    applicability: str
    applicability_reasons: list[str] = field(default_factory=list)
    evidence_found: bool | None = None
    evidence_reasons: list[str] = field(default_factory=list)
    gap_summary: str | None = None


def load_clauses(path: Path) -> list[Clause]:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    clauses: list[Clause] = []
    for entry in data.get("clauses", []):
        clauses.append(
            Clause(
                clause_id=entry["clause_id"],
                spec_id=entry["spec_id"],
                description=entry["description"],
                applies_when_path=tuple(entry.get("applies_when_path", [])),
                applies_when_doc_name=tuple(entry.get("applies_when_doc_name", [])),
                applies_when_content=tuple(entry.get("applies_when_content", [])),
                evidence_required=entry["evidence_required"],
                evidence_pattern=entry.get("evidence_pattern"),
                failure_condition=entry["failure_condition"],
                failure_pattern=entry.get("failure_pattern"),
                failure_pattern_disclosure_exempt=bool(entry.get("failure_pattern_disclosure_exempt", False)),
                severity=entry.get("severity", "advisory"),
                waiver_policy=entry.get("waiver_policy", "advisory_only"),
                enforcement_mode=entry.get("enforcement_mode", "advisory_only_in_slice_1"),
            )
        )
    return clauses


def find_operative_file(bridge_id: str, bridge_dir: Path) -> Path | None:
    """Locate the operative bridge file (top-of-stack version) for a bridge id.

    Mirrors the resolution logic used by bridge_applicability_preflight.py:
    scan numbered bridge files for the matching slug and choose the latest
    version.
    """
    matches = sorted(bridge_dir.glob(f"{bridge_id}-[0-9][0-9][0-9].md"))
    return matches[-1] if matches else None


def evaluate_applicability(clause: Clause, content: str, doc_name: str, paths: list[str]) -> tuple[str, list[str]]:
    """Determine must_apply / may_apply / not_applicable for a clause.

    Returns (applicability, reasons).
    """
    reasons: list[str] = []
    path_hit = False
    if clause.applies_when_path:
        for pattern in clause.applies_when_path:
            for path in paths:
                from fnmatch import fnmatch

                if fnmatch(path, pattern):
                    path_hit = True
                    reasons.append(f"path glob `{pattern}` matched `{path}`")
                    break
            if path_hit:
                break

    name_hit = False
    if clause.applies_when_doc_name:
        for pattern in clause.applies_when_doc_name:
            if re.search(pattern, doc_name):
                name_hit = True
                reasons.append(f"doc-name pattern `{pattern}` matched `{doc_name}`")
                break

    content_hit = False
    if clause.applies_when_content:
        for pattern in clause.applies_when_content:
            try:
                if re.search(pattern, content, re.MULTILINE):
                    content_hit = True
                    reasons.append(f"content pattern `{pattern}` matched")
                    break
            except re.error as e:
                reasons.append(f"(content pattern `{pattern}` invalid: {e})")

    triggers_total = sum(
        1 for axis in (clause.applies_when_path, clause.applies_when_doc_name, clause.applies_when_content) if axis
    )
    triggers_hit = sum(1 for hit in (path_hit, name_hit, content_hit) if hit)

    if triggers_total == 0:
        return ("not_applicable", ["no applicability axes defined for clause"])
    if triggers_hit == triggers_total:
        return ("must_apply", reasons)
    if triggers_hit > 0:
        return ("may_apply", reasons)
    return ("not_applicable", ["no applicability axis matched"])


def _failure_pattern_scan_content(clause: Clause, content: str) -> str:
    if not clause.failure_pattern_disclosure_exempt:
        return content

    stripped = IN_ROOT_DISCLOSURE_BLOCK_RE.sub("", content)
    stripped = _strip_report_safe_disclosure_lines(clause, stripped)
    target_path_lines = [line for line in content.splitlines() if TARGET_PATHS_DECLARATION_RE.match(line)]
    if not target_path_lines:
        return stripped
    return "\n".join([stripped, *target_path_lines])


def _strip_report_safe_disclosure_lines(clause: Clause, content: str) -> str:
    """Remove diagnostic-only path disclosures from CLAUSE-IN-ROOT failure scans.

    Raw target-path declarations are appended back by ``_failure_pattern_scan_content``.
    Artifact/output declarations and file-list sections remain in the scanned
    text, so genuine out-of-root implementation claims still refute evidence.
    """
    if not clause.failure_pattern:
        return content

    current_heading = ""
    lines: list[str] = []
    for line in content.splitlines():
        heading_match = MARKDOWN_HEADING_RE.match(line)
        if heading_match:
            current_heading = heading_match.group(1)
            lines.append(line)
            continue

        if _is_report_safe_disclosure_line(clause, line, current_heading):
            continue
        lines.append(line)
    return "\n".join(lines)


def _is_report_safe_disclosure_line(clause: Clause, line: str, current_heading: str) -> bool:
    if not clause.failure_pattern or not re.search(clause.failure_pattern, line):
        return False
    if TARGET_PATHS_DECLARATION_RE.match(line):
        return False
    if ARTIFACT_DECLARATION_HEADING_RE.search(current_heading):
        return False
    if ARTIFACT_DECLARATION_LINE_RE.search(line):
        return False
    return bool(DISCLOSURE_CONTEXT_HEADING_RE.search(current_heading) or DISCLOSURE_CONTEXT_LINE_RE.search(line))


def evaluate_evidence(clause: Clause, content: str) -> tuple[bool, list[str], str | None]:
    """For a must_apply clause, check whether the bridge text shows satisfying evidence.

    Returns (evidence_found, reasons, gap_summary_if_missing).
    """
    reasons: list[str] = []
    if clause.failure_pattern:
        try:
            scan_content = _failure_pattern_scan_content(clause, content)
            if re.search(clause.failure_pattern, scan_content):
                reasons.append(f"failure pattern `{clause.failure_pattern}` matched (refutes evidence)")
                return (
                    False,
                    reasons,
                    f"Failure marker present: {clause.failure_condition}; "
                    f"remove or rephrase text matching failure pattern: {clause.failure_pattern}",
                )
        except re.error as e:
            reasons.append(f"(failure pattern invalid: {e})")
    if not clause.evidence_pattern:
        return (
            False,
            ["no evidence_pattern defined for clause"],
            "Clause has no evidence_pattern; manual review required.",
        )
    try:
        if re.search(clause.evidence_pattern, content):
            reasons.append(f"evidence pattern `{clause.evidence_pattern}` matched")
            return (True, reasons, None)
    except re.error as e:
        reasons.append(f"(evidence pattern invalid: {e})")
        return (False, reasons, "Evidence pattern invalid; manual review required.")
    reasons.append(f"evidence pattern `{clause.evidence_pattern}` did not match")
    return (
        False,
        reasons,
        f"Evidence missing: {clause.evidence_required}; add text matching evidence pattern: {clause.evidence_pattern}",
    )


def evaluate_clauses(clauses: list[Clause], content: str, doc_name: str, paths: list[str]) -> list[ClauseResult]:
    results: list[ClauseResult] = []
    for clause in clauses:
        applicability, app_reasons = evaluate_applicability(clause, content, doc_name, paths)
        result = ClauseResult(clause=clause, applicability=applicability, applicability_reasons=app_reasons)
        if applicability == "must_apply":
            evidence_found, evidence_reasons, gap_summary = evaluate_evidence(clause, content)
            result.evidence_found = evidence_found
            result.evidence_reasons = evidence_reasons
            result.gap_summary = gap_summary
        results.append(result)
    return results


# Owner-waiver line format documented in the "Clause-Test Preflight (Mandatory;
# Slice 2)" section of .claude/rules/file-bridge-protocol.md:
#   Owner waiver: <clause_id> — <DELIB-ID> — <one-line reason>
# Detection is anchored on the clause_id substring and the literal "Owner
# waiver:" prefix to avoid false-positive matches on ordinary prose.
_OWNER_WAIVER_PREFIX_RE = re.compile(r"(?im)^\s*Owner waiver:\s*")


def _is_clause_owner_waived(clause: Clause, content: str) -> bool:
    """Return True if ``content`` contains an explicit owner-waiver line for
    ``clause.clause_id``. The line must start with the literal ``Owner waiver:``
    prefix (case-insensitive) and include the clause_id substring on the same
    line.
    """
    for line in content.splitlines():
        if not _OWNER_WAIVER_PREFIX_RE.match(line):
            continue
        if clause.clause_id in line:
            return True
    return False


_REPORT_ONLY_BANNER = (
    "> ⚠ --report-only mode: this output IS DIAGNOSTIC ONLY and CANNOT satisfy GO/VERIFIED.\n"
    "> ⚠ Mandatory gate runs require the default (no-flag) invocation. Cite an explicit\n"
    "> ⚠ owner-waiver line per blocking gap if a real bypass is required:\n"
    "> ⚠   Owner waiver: <clause_id> — <DELIB-ID> — <one-line reason>\n"
    "\n"
)


def render_markdown(
    bridge_id: str,
    operative_file: Path | None,
    results: list[ClauseResult],
    *,
    content: str = "",
    report_only: bool = False,
) -> str:
    operative_str = (
        str(operative_file.relative_to(PROJECT_ROOT))
        if operative_file and _is_under(operative_file, PROJECT_ROOT)
        else (str(operative_file) if operative_file else "(not found)")
    )
    counts = {"must_apply": 0, "may_apply": 0, "not_applicable": 0}
    gaps: list[ClauseResult] = []
    blocking_gaps: list[ClauseResult] = []
    for r in results:
        counts[r.applicability] = counts.get(r.applicability, 0) + 1
        if r.applicability == "must_apply" and r.evidence_found is False:
            gaps.append(r)
            if (
                r.clause.severity == "blocking"
                and r.clause.enforcement_mode == "blocking"
                and not _is_clause_owner_waived(r.clause, content)
            ):
                blocking_gaps.append(r)

    title = "## Clause Applicability (Slice 2; mandatory gate)"
    mode_line = (
        "- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass."
        if not report_only
        else "- Mode: **--report-only** (diagnostic only; CANNOT satisfy GO/VERIFIED)."
    )
    lines: list[str] = []
    if report_only:
        lines.append(_REPORT_ONLY_BANNER.rstrip("\n"))
    lines += [
        title,
        "",
        f"- Bridge id: `{bridge_id}`",
        f"- Operative file: `{operative_str}`",
        f"- Clauses evaluated: {len(results)}",
        f"- must_apply: {counts['must_apply']}, may_apply: {counts['may_apply']}, not_applicable: {counts['not_applicable']}",
        f"- Evidence gaps in must_apply clauses: {len(gaps)}",
        f"- Blocking gaps (gate-failing): {len(blocking_gaps)}",
        mode_line,
        "",
        "| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |",
        "|---|---|---|---|---|---|",
    ]
    for r in results:
        evidence_cell = "—" if r.evidence_found is None else ("yes" if r.evidence_found else "**no**")
        lines.append(
            f"| `{r.clause.clause_id}` | `{r.clause.spec_id}` | {r.applicability} "
            f"| {evidence_cell} | {r.clause.severity} | {r.clause.enforcement_mode} |"
        )
    if blocking_gaps:
        lines += ["", "### Blocking Gaps (gate-failing must_apply clauses without evidence or owner waiver)", ""]
        for r in blocking_gaps:
            lines.append(f"- **`{r.clause.clause_id}`** ({r.clause.severity}, {r.clause.enforcement_mode})")
            lines.append(f"  - Gap: {r.gap_summary}")
            lines.append(f"  - Evidence required: {r.clause.evidence_required}")
            if r.clause.evidence_pattern:
                lines.append(f"  - Evidence pattern: `{r.clause.evidence_pattern}`")
            if r.clause.failure_pattern:
                lines.append(f"  - Failure pattern: `{r.clause.failure_pattern}`")
            for reason in r.evidence_reasons:
                lines.append(f"  - Detector note: {reason}")
    if gaps and not blocking_gaps:
        lines += ["", "### Evidence Gaps (advisory-mode clauses; not gate-failing)", ""]
        for r in gaps:
            lines.append(f"- **`{r.clause.clause_id}`** ({r.clause.severity}, {r.clause.enforcement_mode})")
            lines.append(f"  - Gap: {r.gap_summary}")
            lines.append(f"  - Evidence required: {r.clause.evidence_required}")
            if r.clause.evidence_pattern:
                lines.append(f"  - Evidence pattern: `{r.clause.evidence_pattern}`")
            if r.clause.failure_pattern:
                lines.append(f"  - Failure pattern: `{r.clause.failure_pattern}`")
    lines += [
        "",
        '_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and',
        "must_apply applicability fail the gate (exit 5) when evidence is absent and",
        "no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.",
        'Clauses with `enforcement_mode = "advisory"` are reported but never gate._',
        "",
    ]
    return "\n".join(lines) + "\n"


def _is_under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _resolve_content_file(raw: Path) -> Path:
    """Normalize a ``--content-file`` argument to an absolute path.

    ``argparse`` keeps a relative argument relative, but ``render_markdown``
    calls ``Path.relative_to(PROJECT_ROOT)``, which is purely lexical and
    raises ``ValueError`` on a relative path. The documented invocation runs
    from the project root with a project-root-relative ``bridge/...`` path,
    so resolve a relative argument against ``PROJECT_ROOT`` first and fall
    back to the current working directory when no project-root candidate
    exists. Absolute arguments are returned unchanged.
    """
    if raw.is_absolute():
        return raw
    root_candidate = PROJECT_ROOT / raw
    if root_candidate.exists():
        return root_candidate.resolve()
    return (Path.cwd() / raw).resolve()


def _derive_bridge_id_from_content_file(content_file: Path) -> str:
    content = content_file.read_text(encoding="utf-8")
    document_match = DOCUMENT_DECLARATION_RE.search(content)
    if document_match:
        return document_match.group(1)
    return re.sub(r"-\d{3}$", "", content_file.stem)


EXIT_BLOCKING_GAP = 5  # matches scripts/bridge_applicability_preflight.py convention
EXIT_CANNOT_EVALUATE = EXIT_BLOCKING_GAP


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--bridge-id",
        help="bridge thread id (without -NNN.md suffix). Optional when --content-file is supplied.",
    )
    parser.add_argument("--clauses-config", type=Path, default=DEFAULT_CLAUSES_CONFIG)
    parser.add_argument("--bridge-dir", type=Path, default=DEFAULT_BRIDGE_DIR)
    parser.add_argument(
        "--index",
        type=Path,
        help="deprecated compatibility argument; dispatcher/TAFE state and numbered files are authoritative",
    )
    parser.add_argument(
        "--content-file",
        type=Path,
        help="Evaluate candidate Markdown content from this file instead of resolving the operative bridge file.",
    )
    parser.add_argument("--out", type=Path, help="optional: write report to this path instead of stdout")
    parser.add_argument(
        "--report-only",
        action="store_true",
        help=(
            "Diagnostic mode: prepend a non-authorization banner to the markdown output. "
            "Exit code is the same as the default invocation. --report-only output CANNOT "
            "satisfy GO/VERIFIED; the only valid bypass for a real blocking gap is an "
            "explicit owner-waiver line in the bridge content."
        ),
    )
    args = parser.parse_args(argv)

    if args.content_file is not None:
        args.content_file = _resolve_content_file(args.content_file)
    if args.bridge_id is None:
        if args.content_file is None:
            parser.error("--bridge-id is required unless --content-file is supplied")
        args.bridge_id = _derive_bridge_id_from_content_file(args.content_file)

    if not args.clauses_config.is_file():
        print(f"ERROR: clauses config not found: {args.clauses_config}", file=sys.stderr)
        return EXIT_CANNOT_EVALUATE

    clauses = load_clauses(args.clauses_config)
    operative_file = (
        args.content_file if args.content_file is not None else find_operative_file(args.bridge_id, args.bridge_dir)
    )
    content = ""
    blocking_gaps_count = 0
    if operative_file is None:
        blocking_gaps_count = 1
        title = (
            "## Clause Applicability (Slice 2; mandatory gate)"
            if not args.report_only
            else "## Clause Applicability (Slice 2; --report-only diagnostic)"
        )
        prefix = _REPORT_ONLY_BANNER if args.report_only else ""
        report = (
            f"{prefix}{title}\n\n"
            f"- Bridge id: `{args.bridge_id}`\n"
            f"- Operative file: (not found - no matching numbered bridge file for `{args.bridge_id}`)\n"
            f"- Mode: cannot evaluate without an operative file; gate fails closed with exit {EXIT_CANNOT_EVALUATE}.\n"
        )
    else:
        content = operative_file.read_text(encoding="utf-8")
        doc_name = args.bridge_id
        paths = [f"bridge/{operative_file.name}"]
        results = evaluate_clauses(clauses, content, doc_name, paths)
        report = render_markdown(args.bridge_id, operative_file, results, content=content, report_only=args.report_only)
        # Compute the gate verdict.
        for r in results:
            if (
                r.applicability == "must_apply"
                and r.evidence_found is False
                and r.clause.severity == "blocking"
                and r.clause.enforcement_mode == "blocking"
                and not _is_clause_owner_waived(r.clause, content)
            ):
                blocking_gaps_count += 1

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8", newline="\n")
    else:
        # Reconfigure stdout to UTF-8 so the markdown's em-dashes and the
        # --report-only banner's warning glyph render correctly on Windows
        # consoles (default cp1252 encoding cannot encode those characters).
        try:
            sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except (AttributeError, OSError):
            # Fallback: drop the non-ASCII glyphs rather than crash.
            report = report.encode("ascii", errors="replace").decode("ascii")
        sys.stdout.write(report)

    # Exit code semantics:
    # - default invocation: exit 5 if any blocking gap, exit 0 otherwise.
    # - --report-only: same exit code as the default invocation. The flag is
    #   diagnostic-output-only (banner) and cannot silently bypass the gate.
    return EXIT_BLOCKING_GAP if blocking_gaps_count > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
