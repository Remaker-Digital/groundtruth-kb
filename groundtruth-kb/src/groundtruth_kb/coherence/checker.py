"""Read-only deterministic specification-coherence checks.

Layer A intentionally emits candidates, not final governance decisions. The
checker reads ``current_specifications`` and a TOML rule registry, then writes
only caller-requested output artifacts.
"""

from __future__ import annotations

import json
import re
import sqlite3
import tomllib
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from itertools import combinations
from pathlib import Path
from typing import Any

_MAX_EVIDENCE_LEN = 180
_ACTIVE_CHILD_STATUSES = frozenset({"implemented", "verified"})
_DEFAULT_POLARITY_PAIRS = (
    (
        r"\bmust\s+(?!not\b)(?:use|read|load|write|allow|permit|require)\b"
        r"|\brequires?\b|\ballows?\b",
        r"\bmust\s+not\b|\bmust\s+never\b|\bshall\s+not\b|"
        r"\bprohibit(?:s|ed)?\b|\bforbid(?:s|den)?\b|\bdisallow(?:s|ed)?\b",
    ),
)


class CoherenceRuleError(ValueError):
    """Raised when a coherence rule registry is missing or malformed."""


@dataclass(frozen=True)
class PolarityPair:
    """One positive/negative language pair."""

    positive: str
    negative: str
    positive_re: re.Pattern[str]
    negative_re: re.Pattern[str]


@dataclass(frozen=True)
class Rule:
    """One TOML-backed coherence rule."""

    id: str
    rule_class: str
    description: str
    classification: str
    remediation_hint: str
    surface_tags: tuple[str, ...] = ()
    polarity_pairs: tuple[PolarityPair, ...] = ()
    parent_types: tuple[str, ...] = ()
    child_types: tuple[str, ...] = ()


@dataclass(frozen=True)
class Finding:
    """One spec-coherence candidate emitted by a rule."""

    rule_id: str
    spec_a: str
    spec_b: str
    surface: str
    evidence_excerpts: tuple[str, ...]
    classification: str
    remediation_hint: str


@dataclass(frozen=True)
class CoherenceResult:
    """Aggregate output for one spec-coherence run."""

    run_id: str
    generated_at: str
    db_path: str
    rule_set_path: str
    rules_loaded: int
    specs_scanned: int
    findings: tuple[Finding, ...]
    rule_classes: dict[str, str]

    @property
    def finding_count(self) -> int:
        return len(self.findings)


def load_rules(toml_path: Path, name: str | None = None) -> list[Rule]:
    """Load coherence rules from ``toml_path``.

    ``name`` filters to one rule id. The function validates required fields and
    regex syntax up front so CLI failures are deterministic.
    """
    if not toml_path.is_file():
        raise CoherenceRuleError(f"Spec-coherence rule TOML not found: {toml_path}")
    try:
        with toml_path.open("rb") as fh:
            data = tomllib.load(fh)
    except tomllib.TOMLDecodeError as exc:
        raise CoherenceRuleError(f"Malformed TOML in {toml_path}: {exc}") from exc

    raw_rules = data.get("rules") or []
    if not isinstance(raw_rules, list):
        raise CoherenceRuleError(f"'rules' must be an array in {toml_path}")

    rules: list[Rule] = []
    for index, entry in enumerate(raw_rules):
        if not isinstance(entry, dict):
            raise CoherenceRuleError(f"Rule entry #{index} must be a table in {toml_path}")
        rule_id = _required_str(entry, "id", index, toml_path)
        if name is not None and rule_id != name:
            continue
        rule_class = _required_str(entry, "class", index, toml_path)
        rules.append(
            Rule(
                id=rule_id,
                rule_class=rule_class,
                description=str(entry.get("description") or ""),
                classification=str(entry.get("classification") or rule_class),
                remediation_hint=str(entry.get("remediation_hint") or ""),
                surface_tags=_str_tuple(entry.get("surface_tags")),
                polarity_pairs=_polarity_pairs(entry.get("polarity_pairs"), rule_id),
                parent_types=_str_tuple(entry.get("parent_types")),
                child_types=_str_tuple(entry.get("child_types")),
            )
        )
    if name is not None and not rules:
        raise CoherenceRuleError(f"Spec-coherence rule not found: {name}")
    return rules


def load_specs_from_db(db_path: Path) -> list[dict[str, Any]]:
    """Read ``current_specifications`` from ``db_path`` using SQLite read-only mode."""
    if not db_path.is_file():
        raise CoherenceRuleError(f"GroundTruth DB not found: {db_path}")
    uri = f"file:{db_path.resolve().as_posix()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute("SELECT * FROM current_specifications").fetchall()
    except sqlite3.OperationalError as exc:
        raise CoherenceRuleError("GroundTruth DB is missing current_specifications") from exc
    finally:
        conn.close()
    return [dict(row) for row in rows]


def check_surface_overlap(specs: list[dict[str, Any]], rules: list[Rule]) -> list[Finding]:
    """Find same-surface spec pairs with opposite-polarity evidence."""
    findings: list[Finding] = []
    for rule in rules:
        if rule.rule_class != "surface_overlap":
            continue
        for spec_a, spec_b in combinations(specs, 2):
            surface = _shared_surface(spec_a, spec_b, rule)
            if surface is None:
                continue
            evidence = _opposing_polarity_evidence(spec_a, spec_b, _pairs_or_default(rule))
            if evidence is None:
                continue
            findings.append(_finding(rule, spec_a, spec_b, surface, evidence))
    return findings


def check_authority_hierarchy(specs: list[dict[str, Any]], rules: list[Rule]) -> list[Finding]:
    """Find child specs that contradict their declared parent authority."""
    by_id = {_spec_id(spec): spec for spec in specs if _spec_id(spec)}
    findings: list[Finding] = []
    for rule in rules:
        if rule.rule_class != "hierarchy_violation":
            continue
        parent_types = {_norm_type(t) for t in rule.parent_types}
        child_types = {_norm_type(t) for t in rule.child_types}
        for child in specs:
            parent_id = _parent_id(child)
            if not parent_id or parent_id not in by_id:
                continue
            parent = by_id[parent_id]
            if parent_types and _norm_type(parent.get("type")) not in parent_types:
                continue
            if child_types and _norm_type(child.get("type")) not in child_types:
                continue
            evidence = _opposing_polarity_evidence(parent, child, _pairs_or_default(rule))
            if evidence is None:
                continue
            findings.append(_finding(rule, parent, child, f"parent:{parent_id}", evidence))
    return findings


def check_status_drift(specs: list[dict[str, Any]], rules: list[Rule]) -> list[Finding]:
    """Find child specs verified before their parent authority changed."""
    by_id = {_spec_id(spec): spec for spec in specs if _spec_id(spec)}
    findings: list[Finding] = []
    for rule in rules:
        if rule.rule_class != "status_drift":
            continue
        for child in specs:
            parent_id = _parent_id(child)
            if not parent_id or parent_id not in by_id:
                continue
            if str(child.get("status") or "").lower() not in _ACTIVE_CHILD_STATUSES:
                continue
            parent = by_id[parent_id]
            parent_changed = _parse_dt(parent.get("changed_at"))
            child_verified = _parse_dt(child.get("implementation_verified_at"))
            if parent_changed is None or child_verified is None or parent_changed <= child_verified:
                continue
            evidence = (
                f"{_spec_id(parent)} changed_at={parent.get('changed_at')}",
                f"{_spec_id(child)} implementation_verified_at={child.get('implementation_verified_at')}",
            )
            findings.append(_finding(rule, parent, child, f"parent:{parent_id}", evidence))
    return findings


def run_all(specs: list[dict[str, Any]], rules: list[Rule]) -> list[Finding]:
    """Run all configured Layer A checks and return candidate findings."""
    return [
        *check_surface_overlap(specs, rules),
        *check_authority_hierarchy(specs, rules),
        *check_status_drift(specs, rules),
    ]


def make_result(
    *,
    db_path: Path,
    rule_set_path: Path,
    specs: list[dict[str, Any]],
    rules: list[Rule],
    findings: list[Finding],
) -> CoherenceResult:
    """Create a timestamped result envelope for CLI emission."""
    now = datetime.now(UTC)
    return CoherenceResult(
        run_id=now.strftime("%Y%m%dT%H%M%SZ"),
        generated_at=now.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        db_path=str(db_path),
        rule_set_path=str(rule_set_path),
        rules_loaded=len(rules),
        specs_scanned=len(specs),
        findings=tuple(findings),
        rule_classes={rule.id: rule.rule_class for rule in rules},
    )


def emit_json(result: CoherenceResult, out_path: Path) -> None:
    """Write structured JSON output."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "run_id": result.run_id,
        "generated_at": result.generated_at,
        "db_path": result.db_path,
        "rule_set_path": result.rule_set_path,
        "rules_loaded": result.rules_loaded,
        "specs_scanned": result.specs_scanned,
        "finding_count": result.finding_count,
        "findings": [asdict(finding) for finding in result.findings],
    }
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def emit_markdown(result: CoherenceResult, out_path: Path) -> None:
    """Write a human-readable markdown rollup grouped by rule class."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Spec Coherence Summary",
        "",
        f"- Generated: {result.generated_at}",
        f"- Run id: {result.run_id}",
        f"- DB: {result.db_path}",
        f"- Rule set: {result.rule_set_path}",
        f"- Rules loaded: {result.rules_loaded}",
        f"- Specs scanned: {result.specs_scanned}",
        f"- Findings: {result.finding_count}",
        "",
    ]
    if not result.findings:
        lines.append("No findings.")
    else:
        grouped: dict[str, list[Finding]] = {}
        for finding in result.findings:
            grouped.setdefault(result.rule_classes.get(finding.rule_id, "unknown"), []).append(finding)
        for rule_class in sorted(grouped):
            findings = grouped[rule_class]
            lines.append(f"## {rule_class} ({len(findings)})")
            lines.append("")
            for finding in findings:
                lines.append(
                    f"- `{finding.rule_id}` `{finding.spec_a}` <-> `{finding.spec_b}` "
                    f"on `{finding.surface}` ({finding.classification})"
                )
                for excerpt in finding.evidence_excerpts:
                    lines.append(f"  - Evidence: {excerpt}")
                if finding.remediation_hint:
                    lines.append(f"  - Remediation: {finding.remediation_hint}")
            lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def _required_str(entry: dict[str, Any], key: str, index: int, toml_path: Path) -> str:
    value = entry.get(key)
    if not isinstance(value, str) or not value.strip():
        raise CoherenceRuleError(f"Rule entry #{index} missing '{key}' (string) in {toml_path}")
    return value.strip()


def _str_tuple(value: object) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        return ()
    return tuple(str(item).strip() for item in value if str(item).strip())


def _polarity_pairs(value: object, rule_id: str) -> tuple[PolarityPair, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise CoherenceRuleError(f"Rule '{rule_id}' polarity_pairs must be an array")
    pairs: list[PolarityPair] = []
    for index, entry in enumerate(value):
        if not isinstance(entry, dict):
            raise CoherenceRuleError(f"Rule '{rule_id}' polarity pair #{index} must be a table")
        positive = entry.get("positive")
        negative = entry.get("negative")
        if not isinstance(positive, str) or not isinstance(negative, str):
            raise CoherenceRuleError(f"Rule '{rule_id}' polarity pair #{index} needs positive and negative regex")
        try:
            pairs.append(
                PolarityPair(
                    positive=positive,
                    negative=negative,
                    positive_re=re.compile(positive, re.IGNORECASE | re.DOTALL),
                    negative_re=re.compile(negative, re.IGNORECASE | re.DOTALL),
                )
            )
        except re.error as exc:
            raise CoherenceRuleError(f"Rule '{rule_id}' polarity pair #{index} has invalid regex: {exc}") from exc
    return tuple(pairs)


def _pairs_or_default(rule: Rule) -> tuple[PolarityPair, ...]:
    if rule.polarity_pairs:
        return rule.polarity_pairs
    return tuple(
        PolarityPair(
            positive=positive,
            negative=negative,
            positive_re=re.compile(positive, re.IGNORECASE | re.DOTALL),
            negative_re=re.compile(negative, re.IGNORECASE | re.DOTALL),
        )
        for positive, negative in _DEFAULT_POLARITY_PAIRS
    )


def _spec_id(spec: dict[str, Any]) -> str:
    return str(spec.get("id") or "")


def _spec_text(spec: dict[str, Any]) -> str:
    fields = (
        spec.get("title"),
        spec.get("description"),
        spec.get("constraints"),
        spec.get("authority"),
        spec.get("tags"),
    )
    return "\n".join(str(field) for field in fields if field)


def _norm_surface(value: object) -> str:
    text = str(value or "").lower().replace("_", " ").replace("-", " ")
    return " ".join(text.split())


def _norm_type(value: object) -> str:
    return str(value or "").lower().replace("-", "_")


def _tags(spec: dict[str, Any]) -> set[str]:
    raw = spec.get("tags")
    if raw is None:
        return set()
    if isinstance(raw, list):
        return {_norm_surface(item) for item in raw}
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, list):
            return {_norm_surface(item) for item in parsed}
        return {_norm_surface(part) for part in re.split(r"[,;]", raw) if part.strip()}
    return {_norm_surface(raw)}


def _surface_for(spec: dict[str, Any], rule: Rule) -> str | None:
    tag_values = _tags(spec)
    text = _norm_surface(_spec_text(spec))
    for raw_surface in rule.surface_tags:
        surface = _norm_surface(raw_surface)
        if not surface:
            continue
        if surface in tag_values or surface in text:
            return raw_surface
    return None


def _shared_surface(spec_a: dict[str, Any], spec_b: dict[str, Any], rule: Rule) -> str | None:
    surface_a = _surface_for(spec_a, rule)
    surface_b = _surface_for(spec_b, rule)
    return surface_a if surface_a is not None and surface_b is not None else None


def _opposing_polarity_evidence(
    spec_a: dict[str, Any],
    spec_b: dict[str, Any],
    pairs: tuple[PolarityPair, ...],
) -> tuple[str, ...] | None:
    text_a = _spec_text(spec_a)
    text_b = _spec_text(spec_b)
    for pair in pairs:
        a_pos = pair.positive_re.search(text_a)
        a_neg = pair.negative_re.search(text_a)
        b_pos = pair.positive_re.search(text_b)
        b_neg = pair.negative_re.search(text_b)
        if a_pos and b_neg:
            return (
                f"{_spec_id(spec_a)} positive: {_excerpt(text_a, a_pos)}",
                f"{_spec_id(spec_b)} negative: {_excerpt(text_b, b_neg)}",
            )
        if a_neg and b_pos:
            return (
                f"{_spec_id(spec_a)} negative: {_excerpt(text_a, a_neg)}",
                f"{_spec_id(spec_b)} positive: {_excerpt(text_b, b_pos)}",
            )
    return None


def _excerpt(text: str, match: re.Match[str]) -> str:
    collapsed = " ".join(text.split())
    matched = " ".join(match.group(0).split())
    start = max(collapsed.lower().find(matched.lower()), 0)
    excerpt = collapsed[start : start + _MAX_EVIDENCE_LEN]
    return excerpt + ("..." if len(collapsed) > start + _MAX_EVIDENCE_LEN else "")


def _finding(
    rule: Rule,
    spec_a: dict[str, Any],
    spec_b: dict[str, Any],
    surface: str,
    evidence: tuple[str, ...],
) -> Finding:
    return Finding(
        rule_id=rule.id,
        spec_a=_spec_id(spec_a),
        spec_b=_spec_id(spec_b),
        surface=surface,
        evidence_excerpts=evidence,
        classification=rule.classification,
        remediation_hint=rule.remediation_hint,
    )


def _parent_id(spec: dict[str, Any]) -> str | None:
    parent = spec.get("parent")
    if isinstance(parent, str) and parent.strip():
        return parent.strip()
    affected_by = spec.get("affected_by")
    if isinstance(affected_by, str):
        try:
            parsed = json.loads(affected_by)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, list):
            for item in parsed:
                if isinstance(item, str) and item.strip():
                    return item.strip()
    return None


def _parse_dt(value: object) -> datetime | None:
    if not value:
        return None
    text = str(value)
    try:
        parsed = datetime.fromisoformat(text[:-1] + "+00:00" if text.endswith("Z") else text)
    except ValueError:
        return None
    return parsed.astimezone(UTC) if parsed.tzinfo is not None else parsed.replace(tzinfo=UTC)
