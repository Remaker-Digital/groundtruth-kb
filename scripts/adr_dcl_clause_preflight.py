"""ADR/DCL clause-test preflight (Slice 1, advisory mode).

Per ``bridge/gtkb-adr-dcl-clause-test-enforcement-001.md`` (GO at -002):
this CLI is the companion preflight surface to the existing
``scripts/bridge_applicability_preflight.py``. Where the existing tool
checks citation presence for required cross-cutting specs, this tool
loads the ADR/DCL clause registry at ``config/governance/adr-dcl-clauses.toml``
and asks a finer-grained question for each registered clause:

- Does the bridge proposal/report's content + path token surface trigger
  this clause? (must_apply / may_apply / not_applicable)
- For ``must_apply`` clauses, does the bridge text contain evidence that
  satisfies the clause?
- Are any failure-pattern markers present that would refute the evidence?

Slice 1 is advisory only: the CLI always exits 0, even when blocking
clauses lack evidence. The output is informational. Slice 2 will promote
selected clauses to a hard GO/VERIFIED gate after Slice-1 feedback.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CLAUSES_CONFIG = PROJECT_ROOT / "config" / "governance" / "adr-dcl-clauses.toml"
DEFAULT_BRIDGE_DIR = PROJECT_ROOT / "bridge"
DEFAULT_INDEX_PATH = DEFAULT_BRIDGE_DIR / "INDEX.md"


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
                severity=entry.get("severity", "advisory"),
                waiver_policy=entry.get("waiver_policy", "advisory_only"),
                enforcement_mode=entry.get("enforcement_mode", "advisory_only_in_slice_1"),
            )
        )
    return clauses


def find_operative_file(bridge_id: str, index_path: Path, bridge_dir: Path) -> Path | None:
    """Locate the operative bridge file (top-of-stack version) for a bridge id.

    Mirrors the resolution logic used by bridge_applicability_preflight.py:
    parse INDEX.md for the matching `Document:` block and pick the first
    versioned line. Falls back to glob if INDEX has no entry yet.
    """
    if index_path.is_file():
        text = index_path.read_text(encoding="utf-8")
        in_block = False
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("Document:"):
                doc_name = stripped[len("Document:") :].strip()
                in_block = doc_name == bridge_id
                continue
            if in_block and stripped:
                m = re.match(r"^[A-Z\-]+:\s*(?P<path>bridge/.+\.md)\s*$", stripped)
                if m:
                    candidate = PROJECT_ROOT / m.group("path")
                    if candidate.is_file():
                        return candidate
            if in_block and not stripped:
                in_block = False
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
    if triggers_hit == triggers_total or (content_hit and triggers_hit >= 1):
        return ("must_apply", reasons)
    if triggers_hit > 0:
        return ("may_apply", reasons)
    return ("not_applicable", ["no applicability axis matched"])


def evaluate_evidence(clause: Clause, content: str) -> tuple[bool, list[str], str | None]:
    """For a must_apply clause, check whether the bridge text shows satisfying evidence.

    Returns (evidence_found, reasons, gap_summary_if_missing).
    """
    reasons: list[str] = []
    if clause.failure_pattern:
        try:
            if re.search(clause.failure_pattern, content):
                reasons.append(f"failure pattern `{clause.failure_pattern}` matched (refutes evidence)")
                return (False, reasons, f"Failure marker present: {clause.failure_condition}")
        except re.error as e:
            reasons.append(f"(failure pattern invalid: {e})")
    if not clause.evidence_pattern:
        return (False, ["no evidence_pattern defined for clause"], "Clause has no evidence_pattern; manual review required.")
    try:
        if re.search(clause.evidence_pattern, content):
            reasons.append(f"evidence pattern `{clause.evidence_pattern}` matched")
            return (True, reasons, None)
    except re.error as e:
        reasons.append(f"(evidence pattern invalid: {e})")
        return (False, reasons, f"Evidence pattern invalid; manual review required.")
    reasons.append(f"evidence pattern `{clause.evidence_pattern}` did not match")
    return (False, reasons, f"Evidence missing: {clause.evidence_required}")


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


def render_markdown(bridge_id: str, operative_file: Path | None, results: list[ClauseResult]) -> str:
    operative_str = (
        str(operative_file.relative_to(PROJECT_ROOT)) if operative_file and _is_under(operative_file, PROJECT_ROOT)
        else (str(operative_file) if operative_file else "(not found)")
    )
    counts = {"must_apply": 0, "may_apply": 0, "not_applicable": 0}
    gaps: list[ClauseResult] = []
    for r in results:
        counts[r.applicability] = counts.get(r.applicability, 0) + 1
        if r.applicability == "must_apply" and r.evidence_found is False:
            gaps.append(r)
    lines: list[str] = [
        "## Clause Applicability (Slice 1; advisory mode)",
        "",
        f"- Bridge id: `{bridge_id}`",
        f"- Operative file: `{operative_str}`",
        f"- Clauses evaluated: {len(results)}",
        f"- must_apply: {counts['must_apply']}, may_apply: {counts['may_apply']}, not_applicable: {counts['not_applicable']}",
        f"- Evidence gaps in must_apply clauses: {len(gaps)}",
        "- Slice 1 mode: advisory; this report does NOT block GO/VERIFIED.",
        "",
        "| Clause | Spec | Applicability | Evidence found | Severity |",
        "|---|---|---|---|---|",
    ]
    for r in results:
        evidence_cell = "—" if r.evidence_found is None else ("yes" if r.evidence_found else "**no**")
        lines.append(
            f"| `{r.clause.clause_id}` | `{r.clause.spec_id}` | {r.applicability} | {evidence_cell} | {r.clause.severity} |"
        )
    if gaps:
        lines += ["", "### Evidence Gaps (must_apply clauses without satisfying evidence)", ""]
        for r in gaps:
            lines.append(f"- **`{r.clause.clause_id}`** ({r.clause.severity})")
            lines.append(f"  - Gap: {r.gap_summary}")
            for reason in r.evidence_reasons:
                lines.append(f"  - Detector note: {reason}")
    lines += [
        "",
        "_Slice 1 enforcement_mode: `advisory_only_in_slice_1`. Slice 2 will",
        "promote selected blocking clauses to a hard GO/VERIFIED gate after",
        "Slice-1 feedback. Slice 3 wires the matrix into LO verdict templates.",
        "",
    ]
    return "\n".join(lines) + "\n"


def _is_under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bridge-id", required=True, help="bridge thread id (without -NNN.md suffix)")
    parser.add_argument("--clauses-config", type=Path, default=DEFAULT_CLAUSES_CONFIG)
    parser.add_argument("--bridge-dir", type=Path, default=DEFAULT_BRIDGE_DIR)
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX_PATH)
    parser.add_argument("--out", type=Path, help="optional: write report to this path instead of stdout")
    args = parser.parse_args(argv)

    if not args.clauses_config.is_file():
        print(f"ERROR: clauses config not found: {args.clauses_config}", file=sys.stderr)
        return 0  # advisory mode: still exit 0 per Slice-1 contract

    clauses = load_clauses(args.clauses_config)
    operative_file = find_operative_file(args.bridge_id, args.index, args.bridge_dir)
    if operative_file is None:
        report = (
            f"## Clause Applicability (Slice 1; advisory mode)\n\n"
            f"- Bridge id: `{args.bridge_id}`\n"
            f"- Operative file: (not found — no INDEX entry and no matching `bridge/{args.bridge_id}-NNN.md`)\n"
            f"- Slice 1 mode: advisory; this report does NOT block GO/VERIFIED.\n"
        )
    else:
        content = operative_file.read_text(encoding="utf-8")
        doc_name = args.bridge_id
        paths = [f"bridge/{operative_file.name}"]
        results = evaluate_clauses(clauses, content, doc_name, paths)
        report = render_markdown(args.bridge_id, operative_file, results)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8", newline="\n")
    else:
        sys.stdout.write(report)
    return 0  # advisory mode always exits 0


if __name__ == "__main__":
    raise SystemExit(main())
