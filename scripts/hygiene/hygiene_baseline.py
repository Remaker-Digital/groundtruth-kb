"""GT-KB hygiene-investigation baseline registry loader (FAB-20, WI-4432).

Read-only loader for ``config/governance/hygiene-baseline-registry.toml`` — the
frozen HYG-001..068 finding corpus produced by the GT-KB self-investigation. This
module defines the structured findings schema (``HygieneFinding``) shared by the
orchestration skill and the chunked report generator, and the ``load_baseline``
entry point that the skill, the report generator, and the deferred delta-mode
follow-on all consume.

The module is pure: it reads a TOML file and returns dataclass instances. It
performs NO subprocess execution, NO MemBase/``groundtruth.db`` write, NO bridge
mutation, and NO filesystem traversal beyond the single registry read. This is
what makes the baseline loadable and enumerable without a live agent run
(``DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001``).

Bridge: bridge/gtkb-fab-20-hygiene-investigation-skill-004.md (GO).
Project Authorization: PAUTH-FAB20-20260610 (PROJECT-FABLE-INVESTIGATION / WI-4432).
Specs: GOV-08, GOV-STANDING-BACKLOG-001, GOV-ARTIFACT-ORIENTED-GOVERNANCE-001,
       SPEC-DSI-DOCTOR-CHECK-001.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
"""Repo root (``scripts/hygiene/hygiene_baseline.py`` -> two parents up)."""

REGISTRY_RELATIVE_PATH = Path("config") / "governance" / "hygiene-baseline-registry.toml"
"""Canonical baseline registry location, relative to the project root."""

VALID_FINDING_CLASSES: frozenset[str] = frozenset({"defect", "debt", "decision-needed", "drift"})
"""The four finding classes (see the structured findings schema in the skill)."""

VALID_RATINGS: frozenset[str] = frozenset({"High", "Medium", "Low"})
"""Allowed Value-Assessment rating words for impact/effort/confidence."""


class BaselineRegistryError(ValueError):
    """Raised when the baseline registry cannot be loaded or is malformed."""


def _opt_str(value: Any) -> str | None:
    """Normalize a TOML string field: empty/absent -> ``None``, else stripped str."""
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _str_tuple(value: Any) -> tuple[str, ...]:
    """Normalize a TOML array (or scalar) of strings into a tuple, dropping blanks."""
    if value is None:
        return ()
    if isinstance(value, str):
        items = [value]
    elif isinstance(value, (list, tuple)):
        items = list(value)
    else:
        items = [value]
    return tuple(str(item).strip() for item in items if str(item).strip())


@dataclass(frozen=True)
class HygieneFinding:
    """One structured hygiene finding.

    This is the canonical findings schema produced by the 4-round probe method and
    frozen in the baseline registry. ``id``, ``title``, and ``finding_class`` are
    always present; the richer live-probe fields (``locations``, ``verification``,
    ``problem_statement``, ...) are optional and absent in the baseline subset.
    """

    id: str
    title: str
    finding_class: str
    locations: tuple[str, ...] = ()
    problem_statement: str | None = None
    verification: str | None = None
    impact: str | None = None
    effort: str | None = None
    confidence: str | None = None
    current_state: str | None = None
    expected_state: str | None = None
    owner_touchpoint_required: bool = False
    owner_question: str | None = None
    decision_complexity: str | None = None
    proposed_approach: str | None = None
    related_items: tuple[str, ...] = ()
    source: str | None = None
    fab_cluster: str | None = None

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> HygieneFinding:
        """Build a finding from a TOML/JSON mapping, tolerant of missing keys."""
        finding_id = _opt_str(data.get("id"))
        title = _opt_str(data.get("title"))
        finding_class = _opt_str(data.get("finding_class"))
        if not finding_id:
            raise BaselineRegistryError("finding is missing a non-empty 'id'")
        if not title:
            raise BaselineRegistryError(f"{finding_id}: missing non-empty 'title'")
        if not finding_class:
            raise BaselineRegistryError(f"{finding_id}: missing non-empty 'finding_class'")
        return cls(
            id=finding_id,
            title=title,
            finding_class=finding_class,
            locations=_str_tuple(data.get("locations")),
            problem_statement=_opt_str(data.get("problem_statement")),
            verification=_opt_str(data.get("verification")),
            impact=_opt_str(data.get("impact")),
            effort=_opt_str(data.get("effort")),
            confidence=_opt_str(data.get("confidence")),
            current_state=_opt_str(data.get("current_state")),
            expected_state=_opt_str(data.get("expected_state")),
            owner_touchpoint_required=bool(data.get("owner_touchpoint_required", False)),
            owner_question=_opt_str(data.get("owner_question")),
            decision_complexity=_opt_str(data.get("decision_complexity")),
            proposed_approach=_opt_str(data.get("proposed_approach")),
            related_items=_str_tuple(data.get("related_items")),
            source=_opt_str(data.get("source")),
            fab_cluster=_opt_str(data.get("fab_cluster")),
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dict (tuples rendered as lists)."""
        return {
            "id": self.id,
            "title": self.title,
            "finding_class": self.finding_class,
            "locations": list(self.locations),
            "problem_statement": self.problem_statement,
            "verification": self.verification,
            "impact": self.impact,
            "effort": self.effort,
            "confidence": self.confidence,
            "current_state": self.current_state,
            "expected_state": self.expected_state,
            "owner_touchpoint_required": self.owner_touchpoint_required,
            "owner_question": self.owner_question,
            "decision_complexity": self.decision_complexity,
            "proposed_approach": self.proposed_approach,
            "related_items": list(self.related_items),
            "source": self.source,
            "fab_cluster": self.fab_cluster,
        }


@dataclass(frozen=True)
class BaselineRegistry:
    """The frozen baseline registry: metadata plus the ordered finding corpus."""

    schema_version: int
    baseline_id: str
    generated_at: str | None
    source_reports: tuple[str, ...]
    findings: tuple[HygieneFinding, ...] = field(default_factory=tuple)

    def __len__(self) -> int:
        return len(self.findings)

    def ids(self) -> list[str]:
        """Return the finding ids in registry order."""
        return [finding.id for finding in self.findings]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "baseline_id": self.baseline_id,
            "generated_at": self.generated_at,
            "source_reports": list(self.source_reports),
            "finding_count": len(self.findings),
            "findings": [finding.to_dict() for finding in self.findings],
        }


def _resolve_registry_path(path: Path | None) -> Path:
    if path is not None:
        return path
    return PROJECT_ROOT / REGISTRY_RELATIVE_PATH


def load_baseline(path: Path | None = None) -> BaselineRegistry:
    """Load and parse the frozen hygiene baseline registry.

    Raises ``BaselineRegistryError`` when the file is missing or malformed.
    """
    registry_path = _resolve_registry_path(path)
    if not registry_path.is_file():
        raise BaselineRegistryError(f"baseline registry not found: {registry_path}")
    try:
        data = tomllib.loads(registry_path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:  # pragma: no cover - defensive
        raise BaselineRegistryError(f"{registry_path}: invalid TOML ({exc})") from exc

    raw_findings = data.get("findings")
    if not isinstance(raw_findings, list) or not raw_findings:
        raise BaselineRegistryError(f"{registry_path}: no [[findings]] entries present")

    findings = tuple(HygieneFinding.from_mapping(entry) for entry in raw_findings)
    return BaselineRegistry(
        schema_version=int(data.get("schema_version", 1)),
        baseline_id=str(data.get("baseline_id", "")),
        generated_at=_opt_str(data.get("generated_at")),
        source_reports=_str_tuple(data.get("source_reports")),
        findings=findings,
    )


def main(argv: list[str] | None = None) -> int:
    """CLI: print the loaded baseline as JSON (count + findings)."""
    args = list(sys.argv[1:] if argv is None else argv)
    path = Path(args[0]) if args else None
    try:
        registry = load_baseline(path)
    except BaselineRegistryError as exc:
        print(f"hygiene baseline: FAIL ({exc})", file=sys.stderr)
        return 1
    print(json.dumps(registry.to_dict(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
