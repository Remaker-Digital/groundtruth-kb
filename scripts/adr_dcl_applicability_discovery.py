#!/usr/bin/env python3
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Advisory ADR/DCL applicability discovery for bridge documents.

This Slice 5.1 helper complements, but never replaces,
``scripts/adr_dcl_clause_preflight.py``. Registered ADR/DCL clauses remain the
authoritative blocking gate. This helper scans the current ADR/DCL MemBase
corpus and emits deterministic advisory candidates that may also apply to a
bridge proposal or implementation report.

The command is intentionally advisory-only and always exits 0. A high-scoring
candidate is review context, not a GO/NO-GO/VERIFIED gate result.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
import tomllib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Final

try:
    from scripts.implementation_authorization import PATH_TOKEN_RE
except ImportError:  # pragma: no cover - direct script execution path
    from implementation_authorization import PATH_TOKEN_RE

PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parent.parent
DEFAULT_BRIDGE_DIR: Final[Path] = PROJECT_ROOT / "bridge"
DEFAULT_DB_PATH: Final[Path] = PROJECT_ROOT / "groundtruth.db"
DEFAULT_CLAUSES_CONFIG: Final[Path] = PROJECT_ROOT / "config" / "governance" / "adr-dcl-clauses.toml"
DEFAULT_THRESHOLD: Final[int] = 30

TARGET_PATH_RE: Final[re.Pattern[str]] = re.compile(r"^\s*target_paths?\s*[:=]\s*(.+)", re.IGNORECASE)
SPEC_ID_RE: Final[re.Pattern[str]] = re.compile(r"\b(?:SPEC|GOV|ADR|DCL|PB|REQ)-[A-Z0-9][A-Z0-9_.-]*\b")
TOKEN_RE: Final[re.Pattern[str]] = re.compile(r"[a-z0-9][a-z0-9_/-]*")
STOP_WORDS: Final[set[str]] = {
    "000",
    "001",
    "002",
    "003",
    "004",
    "005",
    "a",
    "active",
    "actual",
    "adapter",
    "adapters",
    "advisory",
    "affected",
    "after",
    "agent",
    "an",
    "and",
    "applicability",
    "applicable",
    "apply",
    "are",
    "artifact",
    "as",
    "at",
    "author",
    "authorization",
    "before",
    "be",
    "blocking",
    "bridge",
    "builder",
    "by",
    "candidate",
    "canonical",
    "change",
    "changes",
    "check",
    "checks",
    "clause",
    "claude",
    "codex",
    "config",
    "context",
    "dcl",
    "decision",
    "declared",
    "delib",
    "design",
    "document",
    "does",
    "during",
    "enforcement",
    "evidence",
    "existing",
    "file",
    "files",
    "for",
    "from",
    "gate",
    "generate",
    "generated",
    "governance",
    "groundtruth",
    "gtkb",
    "in",
    "implementation",
    "is",
    "it",
    "json",
    "kind",
    "list",
    "may",
    "membase",
    "must",
    "no",
    "non",
    "not",
    "of",
    "on",
    "only",
    "or",
    "owner",
    "path",
    "paths",
    "preflight",
    "project",
    "proposal",
    "python",
    "read",
    "record",
    "registry",
    "report",
    "review",
    "run",
    "schema",
    "script",
    "scripts",
    "section",
    "skill",
    "skills",
    "slice",
    "source",
    "spec",
    "specified",
    "status",
    "test",
    "tests",
    "the",
    "this",
    "to",
    "toml",
    "update",
    "use",
    "verified",
    "version",
    "when",
    "with",
}


@dataclass(frozen=True)
class BridgeContent:
    bridge_id: str
    content: str
    source_path: str
    target_paths: tuple[str, ...]
    cited_specs: tuple[str, ...]


@dataclass(frozen=True)
class AdrDclSpec:
    spec_id: str
    title: str
    description: str
    spec_type: str
    status: str
    scope: str = ""
    section: str = ""
    handle: str = ""
    tags: str = ""
    assertions: str = ""
    source_paths: str = ""

    @property
    def corpus_text(self) -> str:
        return "\n".join(
            [
                self.spec_id,
                self.title,
                self.description,
                self.scope,
                self.section,
                self.handle,
                self.tags,
                self.assertions,
                self.source_paths,
            ]
        )


@dataclass
class DiscoveryResult:
    spec_id: str
    title: str
    spec_type: str
    status: str
    classification: str
    score: int = 0
    reasons: list[str] = field(default_factory=list)


def parse_index_for_document(bridge_id: str, bridge_dir: Path) -> Path | None:
    """Return the latest numbered bridge file for ``bridge_id``."""
    matches = sorted(bridge_dir.glob(f"{bridge_id}-[0-9][0-9][0-9].md"))
    return matches[-1] if matches else None


def _normalize_path_token(value: str) -> str:
    token = value.replace("\\", "/").strip().strip("`'\"")
    token = token.rstrip(".,;:)")
    if "::" in token:
        token = token.split("::", 1)[0]
    return token.strip("/")


def _parse_declared_path_values(raw: str) -> set[str]:
    raw = raw.strip()
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = [p.strip("\"' ") for p in re.split(r"[,\s]+", raw) if p.strip("\"' ")]
    if isinstance(parsed, list):
        return {_normalize_path_token(str(p)) for p in parsed if _normalize_path_token(str(p))}
    parsed_token = _normalize_path_token(str(parsed))
    return {parsed_token} if parsed_token else set()


def extract_target_paths(content: str) -> tuple[str, ...]:
    paths: set[str] = set()
    for line in content.splitlines():
        target_match = TARGET_PATH_RE.match(line)
        if target_match:
            paths.update(_parse_declared_path_values(target_match.group(1)))
    for match in PATH_TOKEN_RE.finditer(content):
        token = _normalize_path_token(match.group("path"))
        if token:
            paths.add(token)
    return tuple(sorted(paths))


def load_bridge_content(
    *,
    bridge_id: str,
    content_file: Path | None = None,
    bridge_dir: Path = DEFAULT_BRIDGE_DIR,
) -> BridgeContent | None:
    operative = content_file or parse_index_for_document(bridge_id, bridge_dir)
    if operative is None or not operative.is_file():
        return None
    content = operative.read_text(encoding="utf-8")
    try:
        source_path = operative.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        source_path = str(operative)
    return BridgeContent(
        bridge_id=bridge_id,
        content=content,
        source_path=source_path,
        target_paths=extract_target_paths(content),
        cited_specs=tuple(sorted(set(SPEC_ID_RE.findall(content)))),
    )


def load_declared_clause_specs(config_path: Path) -> set[str]:
    if not config_path.is_file():
        return set()
    data = tomllib.loads(config_path.read_text(encoding="utf-8"))
    return {str(entry.get("spec_id")) for entry in data.get("clauses", []) if entry.get("spec_id")}


def load_adr_dcl_specs(db_path: Path) -> list[AdrDclSpec]:
    if not db_path.is_file():
        return []
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=2.0)
    except sqlite3.Error:
        return []
    try:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT id, title, COALESCE(description, '') AS description,
                   COALESCE(type, '') AS type, COALESCE(status, '') AS status,
                   COALESCE(scope, '') AS scope, COALESCE(section, '') AS section,
                   COALESCE(handle, '') AS handle, COALESCE(tags, '') AS tags,
                   COALESCE(assertions, '') AS assertions,
                   COALESCE(source_paths, '') AS source_paths
            FROM current_specifications
            WHERE type IN ('architecture_decision', 'design_constraint')
              AND COALESCE(status, '') NOT IN ('retired', 'withdrawn')
            ORDER BY id
            """
        ).fetchall()
    except sqlite3.Error:
        return []
    finally:
        conn.close()
    return [
        AdrDclSpec(
            spec_id=str(row["id"]),
            title=str(row["title"]),
            description=str(row["description"]),
            spec_type=str(row["type"]),
            status=str(row["status"]),
            scope=str(row["scope"]),
            section=str(row["section"]),
            handle=str(row["handle"]),
            tags=str(row["tags"]),
            assertions=str(row["assertions"]),
            source_paths=str(row["source_paths"]),
        )
        for row in rows
    ]


def tokenize(text: str) -> set[str]:
    tokens: set[str] = set()
    for raw in TOKEN_RE.findall(text.lower().replace("\\", "/")):
        for part in re.split(r"[_/\-.]+", raw):
            if len(part) >= 3 and not part.isdigit() and part not in STOP_WORDS:
                tokens.add(part)
    return tokens


def _path_tokens(paths: tuple[str, ...]) -> set[str]:
    return tokenize("\n".join(paths))


def score_spec(spec: AdrDclSpec, bridge: BridgeContent) -> tuple[int, list[str]]:
    bridge_tokens = tokenize(bridge.content)
    spec_tokens = tokenize(spec.corpus_text)
    target_tokens = _path_tokens(bridge.target_paths)
    source_path_tokens = tokenize(spec.source_paths)
    cited = set(bridge.cited_specs)

    score = 0
    reasons: list[str] = []

    if spec.spec_id in cited:
        score += 80
        reasons.append("direct spec citation in bridge content (+80)")

    id_overlap = tokenize(spec.spec_id) & bridge_tokens
    if id_overlap:
        points = min(20, 5 * len(id_overlap))
        score += points
        reasons.append(f"spec-id token overlap {sorted(id_overlap)} (+{points})")

    title_overlap = tokenize(spec.title) & bridge_tokens
    if title_overlap:
        points = min(25, 5 * len(title_overlap))
        score += points
        reasons.append(f"title token overlap {sorted(title_overlap)} (+{points})")

    body_overlap = (spec_tokens & bridge_tokens) - title_overlap - id_overlap
    if body_overlap and (id_overlap or title_overlap):
        strongest = sorted(body_overlap)[:8]
        points = min(20, len(body_overlap))
        score += points
        reasons.append(f"body token overlap {strongest} (+{points})")

    path_overlap = source_path_tokens & target_tokens
    if path_overlap:
        strongest = sorted(path_overlap)[:8]
        points = min(30, 6 * len(path_overlap))
        score += points
        reasons.append(f"path token overlap {strongest} (+{points})")

    return score, reasons


def discover(
    bridge: BridgeContent | None,
    specs: list[AdrDclSpec],
    declared_specs: set[str],
    *,
    threshold: int = DEFAULT_THRESHOLD,
) -> list[DiscoveryResult]:
    if bridge is None:
        return []
    results: list[DiscoveryResult] = []
    for spec in specs:
        if spec.spec_id in declared_specs:
            results.append(
                DiscoveryResult(
                    spec_id=spec.spec_id,
                    title=spec.title,
                    spec_type=spec.spec_type,
                    status=spec.status,
                    classification="declared",
                    reasons=[
                        "registered in config/governance/adr-dcl-clauses.toml; authoritative clause preflight owns applicability"
                    ],
                )
            )
            continue
        score, reasons = score_spec(spec, bridge)
        classification = "candidate_may_apply" if score >= threshold else "not_applicable"
        results.append(
            DiscoveryResult(
                spec_id=spec.spec_id,
                title=spec.title,
                spec_type=spec.spec_type,
                status=spec.status,
                classification=classification,
                score=score,
                reasons=reasons or ["no deterministic overlap above scoring signals"],
            )
        )
    return sorted(
        results,
        key=lambda r: (
            {"candidate_may_apply": 0, "declared": 1, "not_applicable": 2}.get(r.classification, 9),
            -r.score,
            r.spec_id,
        ),
    )


def render_markdown(
    *,
    bridge_id: str,
    bridge: BridgeContent | None,
    results: list[DiscoveryResult],
    threshold: int,
) -> str:
    candidates = [r for r in results if r.classification == "candidate_may_apply"]
    declared = [r for r in results if r.classification == "declared"]
    not_applicable = [r for r in results if r.classification == "not_applicable"]
    lines: list[str] = [
        "## Candidate Applicable ADR/DCLs (advisory)",
        "",
        f"- Bridge id: `{bridge_id}`",
        f"- Operative file: `{bridge.source_path if bridge else '(not found)'}`",
        f"- Advisory threshold: {threshold}",
        f"- candidate_may_apply: {len(candidates)}",
        f"- declared_authoritative: {len(declared)}",
        f"- not_applicable: {len(not_applicable)}",
        "- Gate effect: none. This helper always exits 0; registered clause preflight remains authoritative.",
        "",
    ]
    if candidates:
        lines += [
            "### Candidate May Apply",
            "",
            "| Spec | Type | Score | Reason |",
            "|---|---|---:|---|",
        ]
        for result in candidates:
            reason = "; ".join(result.reasons[:3])
            lines.append(f"| `{result.spec_id}` | {result.spec_type} | {result.score} | {reason} |")
        lines.append("")
    if declared:
        lines += [
            "### Declared Authoritative Clauses",
            "",
            "| Spec | Type | Note |",
            "|---|---|---|",
        ]
        for result in declared:
            lines.append(
                f"| `{result.spec_id}` | {result.spec_type} | Registered clause; use `scripts/adr_dcl_clause_preflight.py`. |"
            )
        lines.append("")
    if not candidates:
        lines += ["_No heuristic ADR/DCL candidates met the advisory threshold._", ""]
    return "\n".join(lines)


def build_payload(
    *,
    bridge_id: str,
    content_file: Path | None = None,
    bridge_dir: Path = DEFAULT_BRIDGE_DIR,
    db_path: Path = DEFAULT_DB_PATH,
    clauses_config: Path = DEFAULT_CLAUSES_CONFIG,
    threshold: int = DEFAULT_THRESHOLD,
) -> dict[str, Any]:
    bridge = load_bridge_content(
        bridge_id=bridge_id,
        content_file=content_file,
        bridge_dir=bridge_dir,
    )
    specs = load_adr_dcl_specs(db_path)
    declared = load_declared_clause_specs(clauses_config)
    results = discover(bridge, specs, declared, threshold=threshold)
    payload = {
        "bridge_id": bridge_id,
        "operative_file": bridge.source_path if bridge else None,
        "threshold": threshold,
        "target_paths": list(bridge.target_paths) if bridge else [],
        "cited_specs": list(bridge.cited_specs) if bridge else [],
        "results": [asdict(result) for result in results],
        "summary": {
            "candidate_may_apply": sum(1 for result in results if result.classification == "candidate_may_apply"),
            "declared": sum(1 for result in results if result.classification == "declared"),
            "not_applicable": sum(1 for result in results if result.classification == "not_applicable"),
        },
    }
    payload["markdown"] = render_markdown(bridge_id=bridge_id, bridge=bridge, results=results, threshold=threshold)
    return payload


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bridge-id", required=True, help="Bridge document name / versioned bridge-thread slug.")
    parser.add_argument("--content-file", type=Path, help="Evaluate pending markdown content from this file.")
    parser.add_argument("--bridge-dir", type=Path, default=DEFAULT_BRIDGE_DIR)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--clauses-config", type=Path, default=DEFAULT_CLAUSES_CONFIG)
    parser.add_argument("--threshold", type=int, default=DEFAULT_THRESHOLD)
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of markdown.")
    parser.add_argument("--out", type=Path, help="Optional output path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    payload = build_payload(
        bridge_id=args.bridge_id,
        content_file=args.content_file,
        bridge_dir=args.bridge_dir,
        db_path=args.db,
        clauses_config=args.clauses_config,
        threshold=args.threshold,
    )
    output = json.dumps(payload, indent=2, sort_keys=True) + "\n" if args.json else payload["markdown"] + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output, encoding="utf-8", newline="\n")
    else:
        try:
            sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except (AttributeError, OSError):
            output = output.encode("ascii", errors="replace").decode("ascii")
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
