"""Tests for Windows governance preflight evidence packets."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.governance.preflight_evidence import (  # noqa: E402
    CheckOutcome,
    CheckSeverity,
    PreflightCheck,
    PreflightEvidence,
    PreflightStatus,
)

GENERATED_AT = "2026-06-29T00:00:00Z"


def test_passed_evidence_serializes_stable_schema() -> None:
    evidence = PreflightEvidence.from_checks(
        [
            PreflightCheck.passed("bridge-applicability", summary="required specs cited"),
            PreflightCheck.passed(
                "owner-bypass-prompt",
                severity=CheckSeverity.EVIDENCE_ONLY,
                summary="bypass prompt evidence path available",
            ),
        ],
        evidence_path=Path("artifacts/windows/preflight.json"),
        generated_at=GENERATED_AT,
    )

    payload = evidence.to_dict()

    assert payload == {
        "schema_version": 1,
        "status": "passed",
        "generated_at": GENERATED_AT,
        "evidence_path": "artifacts/windows/preflight.json",
        "summary": "All 2 governance preflight checks passed.",
        "summary_counts": {
            "total": 2,
            "passed": 2,
            "failed": 0,
            "inconclusive": 0,
            "hard_failures": 0,
            "hard_inconclusive": 0,
            "advisory_failures": 0,
            "evidence_only_failures": 0,
        },
        "checks": [
            {
                "name": "bridge-applicability",
                "outcome": "passed",
                "severity": "hard",
                "summary": "required specs cited",
                "detail": None,
                "evidence": {},
                "blocks_release": False,
            },
            {
                "name": "owner-bypass-prompt",
                "outcome": "passed",
                "severity": "evidence_only",
                "summary": "bypass prompt evidence path available",
                "detail": None,
                "evidence": {},
                "blocks_release": False,
            },
        ],
    }
    assert json.loads(evidence.to_json()) == payload


def test_hard_failure_blocks_and_sets_failed_status() -> None:
    evidence = PreflightEvidence.from_checks(
        [
            PreflightCheck.failed(
                "bridge-authority",
                summary="missing GO verdict",
                detail="implementation cannot proceed without live GO",
            ),
            PreflightCheck.passed("artifact-summary", severity=CheckSeverity.ADVISORY),
        ],
        generated_at=GENERATED_AT,
    )

    assert evidence.status == PreflightStatus.FAILED
    assert evidence.summary_counts["hard_failures"] == 1
    assert evidence.checks[0].blocks_release is True


def test_advisory_failure_is_partial_not_hard_failed() -> None:
    evidence = PreflightEvidence.from_checks(
        [
            PreflightCheck.passed("bridge-authority"),
            PreflightCheck.failed(
                "optional-history-note",
                severity=CheckSeverity.ADVISORY,
                summary="no advisory history note found",
            ),
        ],
        generated_at=GENERATED_AT,
    )

    assert evidence.status == PreflightStatus.PARTIAL
    assert evidence.summary_counts["hard_failures"] == 0
    assert evidence.summary_counts["advisory_failures"] == 1
    assert evidence.checks[1].blocks_release is False


def test_inconclusive_hard_check_sets_inconclusive_status() -> None:
    evidence = PreflightEvidence.from_checks(
        [
            PreflightCheck.inconclusive(
                "git-status",
                severity=CheckSeverity.HARD,
                summary="git status command timed out",
            )
        ],
        generated_at=GENERATED_AT,
    )

    assert evidence.status == PreflightStatus.INCONCLUSIVE
    assert evidence.summary_counts["hard_inconclusive"] == 1
    assert evidence.checks[0].outcome == CheckOutcome.INCONCLUSIVE


def test_text_and_markdown_summaries_include_evidence_path() -> None:
    evidence = PreflightEvidence.from_checks(
        [PreflightCheck.passed("bridge-authority", summary="authorized")],
        evidence_path="artifacts/windows/preflight.json",
        generated_at=GENERATED_AT,
    )

    text = evidence.to_text_summary()
    markdown = evidence.to_markdown()

    assert "Evidence path: artifacts/windows/preflight.json" in text
    assert "- Evidence path: `artifacts/windows/preflight.json`" in markdown
    assert "| `bridge-authority` | `passed` | `hard` | no | authorized |" in markdown
