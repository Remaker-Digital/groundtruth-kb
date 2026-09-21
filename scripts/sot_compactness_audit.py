#!/usr/bin/env python3
"""Audit routine source-of-truth read surfaces for compactness.

This helper is intentionally read-only. It classifies large GroundTruth-KB
source-of-truth surfaces by their routine read route, records whether that route
is compact/current/actionable, and emits follow-on dispositions for surfaces
that still need a compact default or compact opt-in.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]

READ_MODE_COMPACT_DEFAULT = "compact_default"
READ_MODE_COMPACT_FLAG = "compact_flag"
READ_MODE_ARCHIVAL_EXPLICIT = "archival_full_explicit"
READ_MODE_GAP = "gap"

COMMAND_KIND_COMPACT = "compact_route"
COMMAND_KIND_BOUNDED = "bounded_route"
COMMAND_KIND_ARCHIVAL = "archival_route"
COMMAND_KIND_UNCLASSIFIED = "unclassified"

STATUS_COVERED = "covered"
STATUS_ARCHIVAL_EXPLICIT = "archival_full_explicit"
STATUS_GAP = "gap"
STATUS_INVALID = "invalid"

VALID_READ_MODES = {
    READ_MODE_COMPACT_DEFAULT,
    READ_MODE_COMPACT_FLAG,
    READ_MODE_ARCHIVAL_EXPLICIT,
    READ_MODE_GAP,
}


@dataclass(frozen=True)
class SurfaceRecord:
    surface_id: str
    title: str
    sot_class: str
    routine_command: str
    read_mode: str
    expected_default: str
    follow_on_disposition: str
    coverage_refs: tuple[str, ...]
    governing_specs: tuple[str, ...]
    archival_command: str = ""
    notes: str = ""


@dataclass(frozen=True)
class AuditRow:
    surface: SurfaceRecord
    status: str
    command_kind: str
    issues: tuple[str, ...]

    @property
    def blocked(self) -> bool:
        return self.status in {STATUS_GAP, STATUS_INVALID}

    def as_dict(self) -> dict[str, Any]:
        return {
            "surface_id": self.surface.surface_id,
            "title": self.surface.title,
            "sot_class": self.surface.sot_class,
            "status": self.status,
            "command_kind": self.command_kind,
            "read_mode": self.surface.read_mode,
            "expected_default": self.surface.expected_default,
            "routine_command": self.surface.routine_command,
            "archival_command": self.surface.archival_command,
            "coverage_refs": list(self.surface.coverage_refs),
            "governing_specs": list(self.surface.governing_specs),
            "follow_on_disposition": self.surface.follow_on_disposition,
            "notes": self.surface.notes,
            "issues": list(self.issues),
        }


def now_stamp() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H-%M-%SZ")


def default_registry() -> tuple[SurfaceRecord, ...]:
    return (
        SurfaceRecord(
            surface_id="native-operating-status",
            title="Native operating status",
            sot_class="Native operating status",
            routine_command="gt status --startup",
            read_mode=READ_MODE_COMPACT_FLAG,
            expected_default="Current operating counts and readiness use the startup summary route.",
            coverage_refs=("groundtruth-kb/src/groundtruth_kb/cli_authority.py",),
            governing_specs=("DCL-SESSION-STARTUP-TOKEN-BUDGET-001",),
            follow_on_disposition="Use the existing startup summary.",
        ),
        SurfaceRecord(
            surface_id="native-work-items",
            title="Bounded work-item reads",
            sot_class="Native work items",
            routine_command="gt backlog list --limit 20 --json",
            read_mode=READ_MODE_COMPACT_DEFAULT,
            expected_default="Limit routine queue reads; inspect the selected work item separately.",
            coverage_refs=("groundtruth-kb/src/groundtruth_kb/cli_authority.py",),
            governing_specs=("GOV-STANDING-BACKLOG-001",),
            follow_on_disposition="Use current native records and explicit list limits.",
        ),
        SurfaceRecord(
            surface_id="native-projects",
            title="Bounded project reads",
            sot_class="Native projects",
            routine_command="gt projects list --limit 20 --json",
            read_mode=READ_MODE_COMPACT_DEFAULT,
            expected_default="Limit the project list and read the selected project record for current state.",
            coverage_refs=("groundtruth-kb/src/groundtruth_kb/cli_authority.py",),
            governing_specs=("GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001",),
            follow_on_disposition="Project authorization is a field on the current project record.",
        ),
        SurfaceRecord(
            surface_id="advisory-state-report",
            title="Informational advisory state",
            sot_class="Native bridge coordination",
            routine_command="gt bridge state-report --json",
            read_mode=READ_MODE_COMPACT_DEFAULT,
            expected_default="Current advisory status counts are separate from both eligible role queues.",
            coverage_refs=("groundtruth-kb/src/groundtruth_kb/bridge/native.py",),
            governing_specs=("DCL-ADVISORY-ROUTING-001", "GOV-STANDING-BACKLOG-001"),
            follow_on_disposition="Read current native state; the owner selects any advisory follow-up.",
            notes="No candidate ledger, file-bridge scan, automatic promotion or disposition inference.",
        ),
    )


def classify_command(command: str) -> str:
    lowered = f" {command.lower()} "
    if not command.strip():
        return COMMAND_KIND_UNCLASSIFIED
    if re.search(r"\s--(compact|startup)\b", lowered):
        return COMMAND_KIND_COMPACT
    archival_markers = (" --history", " --full", " full ", " raw ", " dump ", " archive ", "version chain")
    if any(marker in lowered for marker in archival_markers):
        return COMMAND_KIND_ARCHIVAL
    bounded_markers = (
        " status ",
        " list ",
        " search ",
        " --limit ",
        "manifest",
    )
    if any(marker in lowered for marker in bounded_markers):
        return COMMAND_KIND_BOUNDED
    return COMMAND_KIND_UNCLASSIFIED


def validate_registry(registry: tuple[SurfaceRecord, ...]) -> tuple[str, ...]:
    issues: list[str] = []
    seen: set[str] = set()
    for surface in registry:
        if not surface.surface_id:
            issues.append("surface_id is required")
        if surface.surface_id in seen:
            issues.append(f"duplicate surface_id: {surface.surface_id}")
        seen.add(surface.surface_id)
        if surface.read_mode not in VALID_READ_MODES:
            issues.append(f"{surface.surface_id}: invalid read_mode {surface.read_mode}")
        for field_name in ("title", "sot_class", "routine_command", "expected_default"):
            if not getattr(surface, field_name).strip():
                issues.append(f"{surface.surface_id}: {field_name} is required")
        if not surface.governing_specs:
            issues.append(f"{surface.surface_id}: at least one governing spec is required")
        if (
            surface.read_mode == READ_MODE_COMPACT_FLAG
            and classify_command(surface.routine_command) != COMMAND_KIND_COMPACT
        ):
            issues.append(f"{surface.surface_id}: compact_flag requires a compact routine command")
        if surface.read_mode == READ_MODE_ARCHIVAL_EXPLICIT and not surface.archival_command.strip():
            issues.append(f"{surface.surface_id}: archival_full_explicit requires archival_command")
        if surface.read_mode == READ_MODE_GAP and not surface.follow_on_disposition.strip():
            issues.append(f"{surface.surface_id}: gaps require a follow_on_disposition")
        if surface.read_mode != READ_MODE_GAP and "Follow-on:" in surface.follow_on_disposition:
            issues.append(f"{surface.surface_id}: covered surfaces must not carry follow-on implementation text")
    return tuple(issues)


def audit_registry(registry: tuple[SurfaceRecord, ...] | None = None) -> tuple[AuditRow, ...]:
    selected = registry or default_registry()
    rows: list[AuditRow] = []
    duplicate_ids: set[str] = set()
    seen: set[str] = set()
    for surface in selected:
        if surface.surface_id in seen:
            duplicate_ids.add(surface.surface_id)
        seen.add(surface.surface_id)

    for surface in selected:
        issues: list[str] = []
        command_kind = classify_command(surface.routine_command)
        if surface.read_mode not in VALID_READ_MODES:
            issues.append(f"invalid read_mode: {surface.read_mode}")
        if surface.surface_id in duplicate_ids:
            issues.append("duplicate surface_id")
        if surface.read_mode == READ_MODE_COMPACT_FLAG and command_kind != COMMAND_KIND_COMPACT:
            issues.append("compact route expected but routine command is not compact-signaled")
        if surface.read_mode == READ_MODE_GAP and not surface.follow_on_disposition.strip():
            issues.append("gap lacks follow-on disposition")
        if not surface.governing_specs:
            issues.append("missing governing specs")

        if issues:
            status = STATUS_INVALID
        elif surface.read_mode == READ_MODE_GAP:
            status = STATUS_GAP
        elif surface.read_mode == READ_MODE_ARCHIVAL_EXPLICIT:
            status = STATUS_ARCHIVAL_EXPLICIT
        else:
            status = STATUS_COVERED
        rows.append(AuditRow(surface=surface, status=status, command_kind=command_kind, issues=tuple(issues)))
    return tuple(rows)


def rows_as_json(rows: tuple[AuditRow, ...]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row.status] = counts.get(row.status, 0) + 1
    return {
        "summary": counts,
        "rows": [row.as_dict() for row in rows],
    }


def _md_escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def _join(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "-"


def render_markdown_report(rows: tuple[AuditRow, ...], *, generated_at: str) -> str:
    payload = rows_as_json(rows)
    counts = payload["summary"]
    gap_rows = [row for row in rows if row.status == STATUS_GAP]

    lines = [
        "# Native Read-Surface Compactness Report",
        "",
        f"Generated: `{generated_at}`",
        "",
        "This read-only report describes the declared native read routes. "
        "Its command classification is lexical; it does not execute the routes or measure their payloads.",
        "",
        "## Summary",
        "",
        "| Status | Count |",
        "| --- | ---: |",
    ]
    for status in sorted(counts):
        lines.append(f"| `{status}` | {counts[status]} |")

    lines.extend(
        [
            "",
            "## Surface Matrix",
            "",
            "| Surface | SoT class | Status | Routine route | Archival/full route | Coverage refs | Follow-on disposition |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        surface = row.surface
        lines.append(
            "| "
            + " | ".join(
                [
                    _md_escape(surface.title),
                    _md_escape(surface.sot_class),
                    f"`{row.status}`",
                    f"`{_md_escape(surface.routine_command)}`",
                    f"`{_md_escape(surface.archival_command)}`" if surface.archival_command else "-",
                    _md_escape(_join(surface.coverage_refs)),
                    _md_escape(surface.follow_on_disposition),
                ]
            )
            + " |"
        )

    lines.extend(["", "## Gaps", ""])
    if gap_rows:
        for row in gap_rows:
            lines.extend(
                [
                    f"### {row.surface.title}",
                    "",
                    f"- Surface id: `{row.surface.surface_id}`",
                    f"- Routine route: `{row.surface.routine_command}`",
                    f"- Expected default: {row.surface.expected_default}",
                    f"- Follow-on disposition: {row.surface.follow_on_disposition}",
                    f"- Governing specs: {_join(row.surface.governing_specs)}",
                    "",
                ]
            )
    else:
        lines.append("No compactness gaps identified.")

    lines.extend(
        [
            "",
            "## Verification Notes",
            "",
            "- Validation requires unique surface IDs, governing specifications, compact signals for compact-flag routes, "
            "and a proposed correction for every declared gap.",
            "- The report does not mutate canonical records or dispatch work.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--json", dest="json_output", action="store_true", help="emit machine-readable audit rows")
    parser.add_argument("--generated-at", default=None, help="fixed report timestamp for deterministic tests")
    args = parser.parse_args(argv)

    rows = audit_registry()
    registry_issues = validate_registry(default_registry())
    if registry_issues:
        for issue in registry_issues:
            print(f"sot_compactness_audit: {issue}", file=sys.stderr)
        return 2

    generated_at = args.generated_at or now_stamp()
    if args.json_output:
        payload = rows_as_json(rows)
        payload["generated_at"] = generated_at
        print(json.dumps(payload, indent=2, sort_keys=True))

    if not args.json_output:
        print(render_markdown_report(rows, generated_at=generated_at))

    return 0


if __name__ == "__main__":
    sys.exit(main())
