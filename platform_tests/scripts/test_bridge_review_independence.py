"""Fail-closed tests for exact bridge report review-independence binding."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
for candidate in (ROOT, SCRIPTS):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

import bridge_review_independence as independence  # noqa: E402


def _write_report(root: Path, relative_path: str, author: str = "REPORT-SESSION") -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"NEW\n\nauthor_session_context_id: {author}\n\nbridge_kind: implementation_report\n",
        encoding="utf-8",
    )


def _verdict(reference: str | None, reviewer: str = "REVIEW-SESSION") -> str:
    lines = ["VERIFIED", "", f"author_session_context_id: {reviewer}"]
    if reference is not None:
        lines.extend(["", f"Responds to: `{reference}`"])
    return "\n".join(lines) + "\n"


def test_exact_latest_same_thread_report_proves_independence(tmp_path: Path) -> None:
    expected = "bridge/subject-003.md"
    _write_report(tmp_path, expected)

    assert (
        independence.reviewed_artifact_path(
            _verdict(expected),
            "subject",
            tmp_path,
            expected_artifact_path=expected,
        )
        == (tmp_path / expected).resolve()
    )
    assert (
        independence.verdict_self_review_reason(
            _verdict(expected),
            "subject",
            tmp_path,
            expected_artifact_path=expected,
        )
        is None
    )


@pytest.mark.parametrize(
    "reference",
    [
        None,
        "bridge/../subject-003.md",
        "../bridge/subject-003.md",
        "outside/subject-003.md",
        "bridge/other-subject-003.md",
        "bridge/subject-001.md",
        "C:\\outside\\subject-003.md",
        "/outside/subject-003.md",
    ],
    ids=[
        "missing",
        "bridge-traversal",
        "root-traversal",
        "out-of-bridge",
        "wrong-subject-thread",
        "wrong-version",
        "absolute-windows",
        "absolute-posix",
    ],
)
def test_exact_report_binding_rejects_invalid_reference(tmp_path: Path, reference: str | None) -> None:
    expected = "bridge/subject-003.md"
    _write_report(tmp_path, expected)
    _write_report(tmp_path, "bridge/subject-001.md", author="OLDER-REPORT")
    _write_report(tmp_path, "bridge/other-subject-003.md", author="OTHER-SUBJECT")

    verdict = _verdict(reference)

    assert (
        independence.reviewed_artifact_path(
            verdict,
            "subject",
            tmp_path,
            expected_artifact_path=expected,
        )
        is None
    )
    assert (
        independence.verdict_self_review_reason(
            verdict,
            "subject",
            tmp_path,
            expected_artifact_path=expected,
        )
        == independence.REVIEWED_ARTIFACT_REFERENCE_INVALID
    )


def test_exact_report_binding_still_refuses_same_session(tmp_path: Path) -> None:
    expected = "bridge/subject-003.md"
    _write_report(tmp_path, expected, author="SAME-SESSION")

    assert (
        independence.verdict_self_review_reason(
            _verdict(expected, reviewer="SAME-SESSION"),
            "subject",
            tmp_path,
            expected_artifact_path=expected,
        )
        == independence.AUTHOR_MEETS_REVIEWER_REFUSED
    )
