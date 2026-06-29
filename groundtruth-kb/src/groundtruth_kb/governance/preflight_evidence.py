"""Evidence model for Windows-native governance preflight results."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum, StrEnum
from pathlib import Path
from typing import Any, TypeVar

SCHEMA_VERSION = 1


class PreflightStatus(StrEnum):
    """Aggregate governance preflight status."""

    PASSED = "passed"
    FAILED = "failed"
    PARTIAL = "partial"
    INCONCLUSIVE = "inconclusive"


class CheckOutcome(StrEnum):
    """Individual preflight check outcome."""

    PASSED = "passed"
    FAILED = "failed"
    INCONCLUSIVE = "inconclusive"


class CheckSeverity(StrEnum):
    """Preflight check enforcement class."""

    HARD = "hard"
    ADVISORY = "advisory"
    EVIDENCE_ONLY = "evidence_only"
    INCONCLUSIVE = "inconclusive"


EnumType = TypeVar("EnumType", bound=Enum)


def _coerce_enum(enum_type: type[EnumType], value: EnumType | str) -> EnumType:
    if isinstance(value, enum_type):
        return value
    return enum_type(str(value))


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _normalize_path(path: str | Path | None) -> str | None:
    if path is None:
        return None
    return str(path).replace("\\", "/")


@dataclass(frozen=True)
class PreflightCheck:
    """One Windows governance preflight check and its evidence."""

    name: str
    outcome: CheckOutcome | str
    severity: CheckSeverity | str
    summary: str
    detail: str | None = None
    evidence: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "outcome", _coerce_enum(CheckOutcome, self.outcome))
        object.__setattr__(self, "severity", _coerce_enum(CheckSeverity, self.severity))

    @classmethod
    def passed(
        cls,
        name: str,
        *,
        severity: CheckSeverity | str = CheckSeverity.HARD,
        summary: str = "passed",
        detail: str | None = None,
        evidence: Mapping[str, Any] | None = None,
    ) -> PreflightCheck:
        return cls(
            name=name,
            outcome=CheckOutcome.PASSED,
            severity=severity,
            summary=summary,
            detail=detail,
            evidence=evidence or {},
        )

    @classmethod
    def failed(
        cls,
        name: str,
        *,
        severity: CheckSeverity | str = CheckSeverity.HARD,
        summary: str = "failed",
        detail: str | None = None,
        evidence: Mapping[str, Any] | None = None,
    ) -> PreflightCheck:
        return cls(
            name=name,
            outcome=CheckOutcome.FAILED,
            severity=severity,
            summary=summary,
            detail=detail,
            evidence=evidence or {},
        )

    @classmethod
    def inconclusive(
        cls,
        name: str,
        *,
        severity: CheckSeverity | str = CheckSeverity.INCONCLUSIVE,
        summary: str = "inconclusive",
        detail: str | None = None,
        evidence: Mapping[str, Any] | None = None,
    ) -> PreflightCheck:
        return cls(
            name=name,
            outcome=CheckOutcome.INCONCLUSIVE,
            severity=severity,
            summary=summary,
            detail=detail,
            evidence=evidence or {},
        )

    @property
    def blocks_release(self) -> bool:
        return self.severity == CheckSeverity.HARD and self.outcome != CheckOutcome.PASSED

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "outcome": self.outcome.value,
            "severity": self.severity.value,
            "summary": self.summary,
            "detail": self.detail,
            "evidence": dict(self.evidence),
            "blocks_release": self.blocks_release,
        }


@dataclass(frozen=True)
class PreflightEvidence:
    """Serializable Windows governance preflight evidence packet."""

    status: PreflightStatus | str
    checks: tuple[PreflightCheck, ...]
    evidence_path: str | Path | None
    generated_at: str
    summary: str
    summary_counts: Mapping[str, int]
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", _coerce_enum(PreflightStatus, self.status))
        object.__setattr__(self, "checks", tuple(self.checks))
        object.__setattr__(self, "evidence_path", _normalize_path(self.evidence_path))
        object.__setattr__(self, "summary_counts", dict(self.summary_counts))

    @classmethod
    def from_checks(
        cls,
        checks: Sequence[PreflightCheck],
        *,
        evidence_path: str | Path | None = None,
        generated_at: str | None = None,
        summary: str | None = None,
    ) -> PreflightEvidence:
        check_tuple = tuple(checks)
        counts = _summary_counts(check_tuple)
        status = _aggregate_status(check_tuple)
        return cls(
            status=status,
            checks=check_tuple,
            evidence_path=evidence_path,
            generated_at=generated_at or _utc_now_iso(),
            summary=summary or _default_summary(status, counts),
            summary_counts=counts,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "status": self.status.value,
            "generated_at": self.generated_at,
            "evidence_path": self.evidence_path,
            "summary": self.summary,
            "summary_counts": dict(self.summary_counts),
            "checks": [check.to_dict() for check in self.checks],
        }

    def to_json(self, *, indent: int | None = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)

    def to_text_summary(self) -> str:
        lines = [
            f"Status: {self.status.value}",
            f"Summary: {self.summary}",
            f"Generated: {self.generated_at}",
        ]
        if self.evidence_path:
            lines.append(f"Evidence path: {self.evidence_path}")
        for check in self.checks:
            lines.append(f"- {check.name}: {check.outcome.value} ({check.severity.value}) - {check.summary}")
        return "\n".join(lines)

    def to_markdown(self, *, title: str = "Governance Preflight Evidence") -> str:
        lines = [
            f"## {title}",
            "",
            f"- Status: `{self.status.value}`",
            f"- Summary: {self.summary}",
            f"- Generated: `{self.generated_at}`",
        ]
        if self.evidence_path:
            lines.append(f"- Evidence path: `{self.evidence_path}`")
        lines.extend(
            [
                "",
                "| Check | Outcome | Severity | Blocks release | Summary |",
                "|---|---|---|---|---|",
            ]
        )
        for check in self.checks:
            blocks = "yes" if check.blocks_release else "no"
            lines.append(
                f"| `{check.name}` | `{check.outcome.value}` | `{check.severity.value}` | {blocks} | {check.summary} |"
            )
        return "\n".join(lines)


def _summary_counts(checks: Sequence[PreflightCheck]) -> dict[str, int]:
    return {
        "total": len(checks),
        "passed": sum(1 for check in checks if check.outcome == CheckOutcome.PASSED),
        "failed": sum(1 for check in checks if check.outcome == CheckOutcome.FAILED),
        "inconclusive": sum(1 for check in checks if check.outcome == CheckOutcome.INCONCLUSIVE),
        "hard_failures": sum(
            1 for check in checks if check.severity == CheckSeverity.HARD and check.outcome == CheckOutcome.FAILED
        ),
        "hard_inconclusive": sum(
            1 for check in checks if check.severity == CheckSeverity.HARD and check.outcome == CheckOutcome.INCONCLUSIVE
        ),
        "advisory_failures": sum(
            1 for check in checks if check.severity == CheckSeverity.ADVISORY and check.outcome == CheckOutcome.FAILED
        ),
        "evidence_only_failures": sum(
            1
            for check in checks
            if check.severity == CheckSeverity.EVIDENCE_ONLY and check.outcome == CheckOutcome.FAILED
        ),
    }


def _aggregate_status(checks: Sequence[PreflightCheck]) -> PreflightStatus:
    if not checks:
        return PreflightStatus.INCONCLUSIVE
    if any(check.severity == CheckSeverity.HARD and check.outcome == CheckOutcome.FAILED for check in checks):
        return PreflightStatus.FAILED
    if any(check.severity == CheckSeverity.HARD and check.outcome == CheckOutcome.INCONCLUSIVE for check in checks):
        return PreflightStatus.INCONCLUSIVE
    if all(check.outcome == CheckOutcome.INCONCLUSIVE for check in checks):
        return PreflightStatus.INCONCLUSIVE
    if any(check.outcome != CheckOutcome.PASSED or check.severity == CheckSeverity.INCONCLUSIVE for check in checks):
        return PreflightStatus.PARTIAL
    return PreflightStatus.PASSED


def _default_summary(status: PreflightStatus, counts: Mapping[str, int]) -> str:
    if status == PreflightStatus.PASSED:
        return f"All {counts['total']} governance preflight checks passed."
    if status == PreflightStatus.FAILED:
        return f"{counts['hard_failures']} hard governance preflight check(s) failed."
    if status == PreflightStatus.INCONCLUSIVE:
        return "Governance preflight evidence is inconclusive."
    return "Governance preflight checks produced partial evidence without a hard failure."
