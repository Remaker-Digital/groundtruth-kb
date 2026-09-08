"""Deterministic session wrap service."""

from __future__ import annotations

from pathlib import Path

from groundtruth_kb.session.envelope import close_session
from groundtruth_kb.session.topic_router import first_non_blank_line

_CLOSING_INSTRUCTION = "When you are finished working, close your session envelope by invoking ::wrap."


def is_canonical_wrap_trigger(prompt: str) -> bool:
    return first_non_blank_line(prompt) == "::wrap"


def run_wrap(
    project_root: Path,
    *,
    harness_name: str = "codex",
    harness_id: str | None = None,
    wrap_outcome: str = "manual_wrap",
    session_id: str | None = None,
) -> dict[str, object]:
    envelope, archive_path = close_session(
        project_root,
        harness_name=harness_name,
        harness_id=harness_id,
        wrap_outcome=wrap_outcome,
        session_id=session_id,
    )
    return {
        "session_id": envelope.get("session_id"),
        "archive_path": archive_path,
        "envelope": envelope,
        "summary": render_wrap_summary(envelope, archive_path),
    }


def render_wrap_summary(envelope: dict[str, object], archive_path: Path) -> str:
    steps = envelope.get("wrap_step_results")
    step_count = len(steps) if isinstance(steps, list) else 0
    return "\n".join(
        [
            "# GroundTruth-KB Session Wrap Complete",
            "",
            f"- session_id: `{envelope.get('session_id')}`",
            f"- wrap_outcome: `{envelope.get('wrap_outcome')}`",
            f"- archive: `{archive_path}`",
            f"- wrap_step_results: {step_count}",
            "",
            _CLOSING_INSTRUCTION,
        ]
    )
