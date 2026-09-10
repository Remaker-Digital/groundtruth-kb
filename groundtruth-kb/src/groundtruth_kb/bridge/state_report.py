"""Render a current native bridge report without reading another source of state."""

from __future__ import annotations

from typing import Any


def _cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\r", " ").replace("\n", "<br>")


def render_markdown(report: dict[str, Any]) -> str:
    """Display attempt counts and actionable work without harness information."""
    lines = ["## BRIDGE", "", "| Measure | Count |", "| --- | --- |"]
    lines.extend(
        f"| {_cell(disposition)} attempts | {count} |" for disposition, count in report["attempt_counts"].items()
    )
    lines.extend(
        [
            f"| Unfiled attempts | {report['unfiled_attempt_count']} |",
            f"| Active artifact claims | {report['active_claim_count']} |",
            "",
            "| Active status | Count |",
            "| --- | --- |",
        ]
    )
    lines.extend(f"| {_cell(row['status'])} | {row['count']} |" for row in report["active_status_mix"])
    lines.extend(["", "| Role | Eligible | Blocked |", "| --- | --- | --- |"])
    for role, queue in report["queues"].items():
        lines.append(f"| {_cell(role)} | {len(queue['eligible'])} | {len(queue['blocked'])} |")
    for role, queue in report["queues"].items():
        for disposition in ("eligible", "blocked"):
            if queue[disposition]:
                items = ", ".join(f"{_cell(row['id'])} ({_cell(row['head_status'])})" for row in queue[disposition])
                lines.extend(["", f"{_cell(role)} {disposition}: {items}"])
    return "\n".join(lines) + "\n"
