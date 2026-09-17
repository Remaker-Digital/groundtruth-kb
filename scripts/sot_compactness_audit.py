#!/usr/bin/env python3
"""Audit routine source-of-truth read surfaces for compactness.

This helper is intentionally read-only. It classifies large GroundTruth-KB
source-of-truth surfaces by their routine read route, records whether that route
is compact/current/actionable, and emits follow-on dispositions for surfaces
that still need a compact default or compact opt-in.

GO: bridge/gtkb-wi4966-cli-compactness-sot-size-controls-002.md
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
BRIDGE_ID = "gtkb-wi4966-cli-compactness-sot-size-controls"
WORK_ITEM_ID = "WI-4966"
PROJECT_ID = "PROJECT-HARNESS-EQUIVALENCE-PHASE-3"
PAUTH_ID = "PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI4966-BATCH-C-20260705"

READ_MODE_COMPACT_DEFAULT = "compact_default"
READ_MODE_COMPACT_FLAG = "compact_flag"
READ_MODE_ARCHIVAL_EXPLICIT = "archival_full_explicit"
READ_MODE_GAP = "gap"

COMMAND_KIND_COMPACT = "compact_route"
COMMAND_KIND_BOUNDED = "bounded_route"
COMMAND_KIND_ARCHIVAL = "archival_route"
COMMAND_KIND_UNCLASSIFIED = "unclassified"

STATUS_COVERED = "covered"
STATUS_COVERED_DUPLICATE = "covered_by_existing_work"
STATUS_ARCHIVAL_EXPLICIT = "archival_full_explicit"
STATUS_GAP = "gap"
STATUS_INVALID = "invalid"

VALID_READ_MODES = {
    READ_MODE_COMPACT_DEFAULT,
    READ_MODE_COMPACT_FLAG,
    READ_MODE_ARCHIVAL_EXPLICIT,
    READ_MODE_GAP,
}
WI4947_REFS = frozenset({"WI-4947", "DELIB-202665119", "bridge/gtkb-envelope-sharding-compact-query-modes-002.md"})


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
            surface_id="membase-backlog-status",
            title="MemBase backlog rollup",
            sot_class="MemBase work_items/projects",
            routine_command="groundtruth-kb/.venv/Scripts/gt.exe backlog status --json",
            read_mode=READ_MODE_COMPACT_DEFAULT,
            expected_default="Routine status reads should emit counts and current status rollups, not raw work-item rows.",
            coverage_refs=("GOV-STANDING-BACKLOG-001",),
            governing_specs=("SPEC-INTAKE-46594e", "DCL-SESSION-STARTUP-TOKEN-BUDGET-001"),
            follow_on_disposition="No new work; keep scanner-backed annotations opt-in.",
            notes="The status command is the compact current-state route; full work-item inspection remains a separate query.",
        ),
        SurfaceRecord(
            surface_id="membase-project-authorization",
            title="Project authorization / PAUTH detail",
            sot_class="MemBase project_authorizations",
            routine_command="groundtruth-kb/.venv/Scripts/gt.exe projects show PROJECT-HARNESS-EQUIVALENCE-PHASE-3 --json",
            read_mode=READ_MODE_GAP,
            expected_default="Routine authorization checks need a compact PAUTH summary by project/work item.",
            coverage_refs=(PAUTH_ID,),
            governing_specs=("GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001", "DCL-SESSION-STARTUP-TOKEN-BUDGET-001"),
            follow_on_disposition=(
                "Follow-on: add a compact project-authorization read route or a project-scoped PAUTH summary so "
                "implementation-start checks do not require the full project payload."
            ),
            notes="Live help exposes only --json for projects show; no compact flag is present.",
        ),
        SurfaceRecord(
            surface_id="deliberation-archive-targeted-search",
            title="Deliberation Archive targeted search",
            sot_class="Deliberation Archive",
            routine_command='groundtruth-kb/.venv/Scripts/gt.exe deliberations search "compact query modes" --limit 5 --json',
            read_mode=READ_MODE_COMPACT_DEFAULT,
            expected_default="Routine DA reads should use targeted search/list filters and low limits.",
            coverage_refs=("DELIB-202665119", "DELIB-202665127"),
            governing_specs=("GOV-ARTIFACT-ORIENTED-GOVERNANCE-001", "DCL-SESSION-STARTUP-TOKEN-BUDGET-001"),
            follow_on_disposition="No new work; keep --limit mandatory in routine DA examples and reports.",
            notes="The invalid proposal citation DELIB-20260701-ENVELOPE-SHARDING-EXECUTE-RETIRE is intentionally omitted.",
        ),
        SurfaceRecord(
            surface_id="bridge-current-thread",
            title="Bridge current thread summary",
            sot_class="Bridge numbered file chain",
            routine_command=f"groundtruth-kb/.venv/Scripts/gt.exe bridge show {BRIDGE_ID} --json --compact",
            read_mode=READ_MODE_COMPACT_FLAG,
            expected_default="Routine bridge reads should expose latest status/path/version count without version payloads.",
            coverage_refs=("WI-4947", "DELIB-202665119", "bridge/gtkb-envelope-sharding-compact-query-modes-002.md"),
            governing_specs=("GOV-FILE-BRIDGE-AUTHORITY-001", "DCL-SESSION-STARTUP-TOKEN-BUDGET-001"),
            archival_command=f"groundtruth-kb/.venv/Scripts/gt.exe bridge show {BRIDGE_ID} --json",
            follow_on_disposition="Already covered by WI-4947 compact query work; no duplicate implementation.",
            notes="Compact mode omits archival version chains by design.",
        ),
        SurfaceRecord(
            surface_id="bridge-role-scan",
            title="Bridge role-actionable scan",
            sot_class="Dispatcher/TAFE bridge state plus numbered files",
            routine_command=(
                "groundtruth-kb/.venv/Scripts/python.exe .codex/skills/bridge/helpers/scan_bridge.py "
                "--role prime-builder --compact --format json"
            ),
            read_mode=READ_MODE_COMPACT_FLAG,
            expected_default="Routine role scans should return current/actionable counts and latest paths only.",
            coverage_refs=("WI-4947", "DELIB-202665119", "bridge/gtkb-envelope-sharding-compact-query-modes-002.md"),
            governing_specs=("GOV-FILE-BRIDGE-AUTHORITY-001", "DCL-SESSION-STARTUP-TOKEN-BUDGET-001"),
            follow_on_disposition="Already covered by WI-4947 compact query work; no duplicate implementation.",
            notes="The full mode remains available for archival investigation.",
        ),
        SurfaceRecord(
            surface_id="dispatcher-status",
            title="Dispatcher health and selection status",
            sot_class="Dispatcher daemon state",
            routine_command="groundtruth-kb/.venv/Scripts/gt.exe bridge dispatch status --json",
            read_mode=READ_MODE_GAP,
            expected_default="Routine dispatcher reads need a compact status route separating health rollup from raw config detail.",
            coverage_refs=("DCL-SESSION-STARTUP-TOKEN-BUDGET-001",),
            governing_specs=("SPEC-INTAKE-46594e", "DCL-SESSION-STARTUP-TOKEN-BUDGET-001"),
            follow_on_disposition=(
                "Follow-on: add --compact or --startup to gt bridge dispatch status, preserving full JSON behind the "
                "existing archival route."
            ),
            notes="Live help exposes only --json; the current JSON payload includes config, health rollup, and selections.",
        ),
        SurfaceRecord(
            surface_id="transcript-inventory-manifest",
            title="Transcript/session inventory",
            sot_class="Harness-local transcript metadata",
            routine_command="groundtruth-kb/.venv/Scripts/gt.exe session envelope show --harness-name codex",
            read_mode=READ_MODE_COMPACT_DEFAULT,
            expected_default="Routine session reads should expose envelope metadata and must not load transcript content.",
            coverage_refs=("WI-4946", "DELIB-202665127", "scripts/wrap_capture_transcript.py"),
            governing_specs=("SPEC-INTAKE-46594e", "DCL-SESSION-STARTUP-TOKEN-BUDGET-001"),
            archival_command="groundtruth-kb/.venv/Scripts/python.exe scripts/wrap_capture_transcript.py --session-id <id>",
            follow_on_disposition="No new work; keep transcript content out of routine startup/session surfaces.",
            notes="wrap_capture_transcript.py is manifest-only; full transcript content is deferred outside routine reads.",
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
        SurfaceRecord(
            surface_id="envelope-sharding-surface",
            title="Session/activity envelope sharding taxonomy",
            sot_class="Harness equivalence envelope config",
            routine_command="groundtruth-kb/.venv/Scripts/gt.exe benchmarks activity-envelope-load --json",
            read_mode=READ_MODE_COMPACT_DEFAULT,
            expected_default="Routine envelope checks should report estimates/classifications, not full startup payload bodies.",
            coverage_refs=("WI-4946", "DELIB-202665127"),
            governing_specs=("SPEC-INTAKE-46594e", "DCL-SESSION-STARTUP-TOKEN-BUDGET-001"),
            follow_on_disposition="No new work; taxonomy baseline already covers payload class separation.",
            notes="This links sharding-baseline coverage rather than duplicating it.",
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
        " envelope show ",
        " activity-envelope-load ",
        " --limit ",
        "manifest",
    )
    if any(marker in lowered for marker in bounded_markers):
        return COMMAND_KIND_BOUNDED
    return COMMAND_KIND_UNCLASSIFIED


def _is_wi4947_duplicate(surface: SurfaceRecord) -> bool:
    return bool(WI4947_REFS.intersection(surface.coverage_refs))


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
        elif _is_wi4947_duplicate(surface):
            status = STATUS_COVERED_DUPLICATE
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
        "bridge_id": BRIDGE_ID,
        "work_item_id": WORK_ITEM_ID,
        "project_id": PROJECT_ID,
        "project_authorization": PAUTH_ID,
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
    duplicate_rows = [row for row in rows if row.status == STATUS_COVERED_DUPLICATE]

    lines = [
        "# Harness Equivalence Phase 3 SoT Compactness Audit",
        "",
        f"Generated: `{generated_at}`",
        f"Bridge: `{BRIDGE_ID}`",
        f"Project: `{PROJECT_ID}`",
        f"Work Item: `{WORK_ITEM_ID}`",
        f"Project Authorization: `{PAUTH_ID}`",
        "",
        "This read-only audit classifies large source-of-truth read surfaces by routine compactness. "
        "It preserves existing compact-query coverage as coverage, not as new work.",
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

    lines.extend(["## Existing Coverage / No Duplicate Work", ""])
    if duplicate_rows:
        for row in duplicate_rows:
            lines.append(
                f"- `{row.surface.surface_id}` is covered by {_join(row.surface.coverage_refs)}; "
                f"disposition: {row.surface.follow_on_disposition}"
            )
    else:
        lines.append("No duplicate-coverage surfaces identified.")

    lines.extend(
        [
            "",
            "## Citation Correction",
            "",
            "`DELIB-20260701-ENVELOPE-SHARDING-EXECUTE-RETIRE` is not used as evidence in this report. "
            "Envelope-sharding compactness context is cited through `DELIB-202665119` and `DELIB-202665127`.",
            "",
            "## Verification Notes",
            "",
            "- Registry validation requires unique surface ids, governing specs, compact signals for compact-flag routes, "
            "and follow-on dispositions for every gap.",
            "- Gap rows are report-backed evidence only; this helper does not mutate MemBase, bridge state, dispatcher state, "
            "or source-of-truth data.",
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
