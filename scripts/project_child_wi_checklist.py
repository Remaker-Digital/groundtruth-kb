#!/usr/bin/env python3
"""Build a deterministic child-WI checklist from compact project gap records.

The helper is intentionally dry-run only: it emits work-item, test, and bridge
proposal skeleton recommendations, but it never writes MemBase, bridge state, or
other authoritative workflow records.

GO: bridge/gtkb-wi4970-child-wi-generator-checklist-002.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX"
REPORT_NAME_PREFIX = "HARNESS-EQUIVALENCE-PHASE-3-CHILD-WI-CHECKLIST-"

ALLOWED_LIFECYCLE_CLASSIFICATIONS = ("new_work", "supersession", "waiver", "retirement", "no_op")
IMPLEMENTATION_LIFECYCLES = frozenset({"new_work", "supersession", "retirement"})
RAW_PAYLOAD_KEYS = frozenset(
    {
        "raw_payload",
        "full_payload",
        "sot_payload",
        "full_sot_payload",
        "source_of_truth_payload",
        "full_context",
        "transcript",
    }
)

MAX_SUMMARY_CHARS = 360
MAX_EVIDENCE_REF_CHARS = 180
MAX_RAW_PAYLOAD_CHARS = 1_200

SLUG_RE = re.compile(r"[^a-z0-9]+")


@dataclass(frozen=True)
class ValidationIssue:
    severity: str
    field: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"severity": self.severity, "field": self.field, "message": self.message}


@dataclass(frozen=True)
class ChecklistRow:
    gap_id: str
    title: str
    summary: str
    lifecycle_classification: str
    project_id: str
    parent_work_item_id: str
    component: str
    candidate_wi_title: str
    linked_test_prompt: str
    proposal_slug: str
    pauth_need: str
    target_paths: tuple[str, ...]
    spec_links: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    owner_evidence_refs: tuple[str, ...]
    acceptance_criteria: tuple[str, ...]
    issues: tuple[ValidationIssue, ...] = field(default_factory=tuple)

    @property
    def blocked(self) -> bool:
        return any(issue.severity == "error" for issue in self.issues)

    @property
    def status(self) -> str:
        return "blocked" if self.blocked else "ready"

    def as_dict(self) -> dict[str, Any]:
        return {
            "gap_id": self.gap_id,
            "title": self.title,
            "summary": self.summary,
            "lifecycle_classification": self.lifecycle_classification,
            "project_id": self.project_id,
            "parent_work_item_id": self.parent_work_item_id,
            "component": self.component,
            "candidate_wi_title": self.candidate_wi_title,
            "linked_test_prompt": self.linked_test_prompt,
            "proposal_slug": self.proposal_slug,
            "pauth_need": self.pauth_need,
            "target_paths": list(self.target_paths),
            "spec_links": list(self.spec_links),
            "evidence_refs": list(self.evidence_refs),
            "owner_evidence_refs": list(self.owner_evidence_refs),
            "acceptance_criteria": list(self.acceptance_criteria),
            "issues": [issue.as_dict() for issue in self.issues],
            "status": self.status,
        }


def now_stamp() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H-%M-%SZ")


def _clean_string(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _as_string_list(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value.strip(),) if value.strip() else ()
    if isinstance(value, (list, tuple)):
        cleaned: list[str] = []
        for item in value:
            if isinstance(item, dict):
                parts = [
                    _clean_string(item.get("id") or item.get("ref") or item.get("path")),
                    _clean_string(item.get("summary") or item.get("title") or item.get("note")),
                ]
                text = " - ".join(part for part in parts if part)
            else:
                text = _clean_string(item)
            if text:
                cleaned.append(text)
        return tuple(cleaned)
    return (_clean_string(value),) if _clean_string(value) else ()


def _truncate(value: str, limit: int) -> str:
    text = value.strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _slugify(*parts: str) -> str:
    text = "-".join(part for part in parts if part).lower()
    text = SLUG_RE.sub("-", text).strip("-")
    text = re.sub(r"-{2,}", "-", text)
    return text[:96].strip("-") or "unnamed-gap"


def _candidate_wi_title(gap_id: str, title: str, lifecycle: str) -> str:
    prefix_by_lifecycle = {
        "new_work": "Create child WI",
        "supersession": "Supersede existing work",
        "waiver": "Record waiver disposition",
        "retirement": "Retire obsolete work",
        "no_op": "Record no-op disposition",
    }
    prefix = prefix_by_lifecycle.get(lifecycle, "Classify gap")
    return f"{prefix}: {gap_id} - {title}"


def _linked_test_prompt(title: str, summary: str, acceptance_criteria: tuple[str, ...]) -> str:
    if acceptance_criteria:
        criteria = "; ".join(_truncate(item, 120) for item in acceptance_criteria)
        return f"Add or identify a regression test proving: {criteria}"
    basis = _truncate(summary or title, 160)
    return f"Add or identify a regression test covering the child-WI outcome for: {basis}"


def _pauth_need(lifecycle: str) -> str:
    if lifecycle in IMPLEMENTATION_LIFECYCLES:
        return "required before implementation"
    if lifecycle == "waiver":
        return "owner decision required before waiver"
    return "not required for dry-run recommendation"


def _raw_payload_issues(record: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for key in sorted(RAW_PAYLOAD_KEYS.intersection(record)):
        value = record.get(key)
        if value is None:
            continue
        encoded = json.dumps(value, sort_keys=True) if not isinstance(value, str) else value
        if len(encoded) > MAX_RAW_PAYLOAD_CHARS:
            issues.append(
                ValidationIssue(
                    "error",
                    key,
                    "oversized raw payload supplied; use compact evidence_refs instead",
                )
            )
        else:
            issues.append(
                ValidationIssue(
                    "warning",
                    key,
                    "raw payload omitted from checklist; use compact evidence_refs for durable evidence",
                )
            )
    return issues


def _validate_record(
    record: dict[str, Any],
    *,
    gap_id: str,
    title: str,
    lifecycle: str,
    project_id: str,
    parent_work_item_id: str,
    target_paths: tuple[str, ...],
    spec_links: tuple[str, ...],
    evidence_refs: tuple[str, ...],
) -> tuple[ValidationIssue, ...]:
    issues: list[ValidationIssue] = []
    required_scalars = {
        "gap_id": gap_id,
        "title": title,
        "project_id": project_id,
        "parent_work_item_id": parent_work_item_id,
        "lifecycle_classification": lifecycle,
    }
    for field_name, value in required_scalars.items():
        if not value:
            issues.append(ValidationIssue("error", field_name, f"{field_name} is required"))

    if lifecycle and lifecycle not in ALLOWED_LIFECYCLE_CLASSIFICATIONS:
        allowed = ", ".join(ALLOWED_LIFECYCLE_CLASSIFICATIONS)
        issues.append(ValidationIssue("error", "lifecycle_classification", f"must be one of: {allowed}"))

    if not spec_links:
        issues.append(ValidationIssue("error", "spec_links", "at least one governing spec link is required"))
    if not evidence_refs:
        issues.append(ValidationIssue("error", "evidence_refs", "at least one compact evidence reference is required"))

    if lifecycle in IMPLEMENTATION_LIFECYCLES and not target_paths:
        issues.append(
            ValidationIssue(
                "error",
                "target_paths",
                "implementation-affecting lifecycle classifications require target_paths",
            )
        )
    elif not target_paths:
        issues.append(
            ValidationIssue(
                "warning",
                "target_paths",
                "no target_paths supplied; acceptable only for waiver/no-op recommendation",
            )
        )

    for evidence in evidence_refs:
        if len(evidence) > MAX_EVIDENCE_REF_CHARS:
            issues.append(
                ValidationIssue(
                    "warning",
                    "evidence_refs",
                    f"evidence reference was truncated to {MAX_EVIDENCE_REF_CHARS} characters",
                )
            )

    issues.extend(_raw_payload_issues(record))
    return tuple(issues)


def _with_defaults(record: dict[str, Any], defaults: dict[str, Any]) -> dict[str, Any]:
    merged = dict(defaults)
    merged.update({key: value for key, value in record.items() if value is not None})
    return merged


def normalize_input(payload: Any) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Return ``(gap_records, defaults)`` from list or object-shaped JSON."""
    if isinstance(payload, list):
        return payload, {}
    if not isinstance(payload, dict):
        raise ValueError("input must be a JSON object with gaps[] or a JSON array of gap records")
    records = payload.get("gaps", payload.get("records"))
    if not isinstance(records, list):
        raise ValueError("input object must contain a gaps[] or records[] list")
    defaults = {
        key: payload.get(key)
        for key in (
            "project_id",
            "parent_work_item_id",
            "pauth_id",
            "component",
            "owner_evidence_refs",
        )
        if payload.get(key) is not None
    }
    return records, defaults


def build_checklist(payload: Any) -> list[ChecklistRow]:
    records, defaults = normalize_input(payload)
    rows: list[ChecklistRow] = []
    for index, source_record in enumerate(records, start=1):
        if not isinstance(source_record, dict):
            source_record = {"gap_id": f"gap-{index}", "title": str(source_record)}
        record = _with_defaults(source_record, defaults)

        gap_id = _clean_string(record.get("gap_id") or record.get("id") or f"gap-{index}")
        title = _clean_string(record.get("title") or record.get("name"))
        summary = _truncate(_clean_string(record.get("summary") or record.get("description")), MAX_SUMMARY_CHARS)
        lifecycle = _clean_string(record.get("lifecycle_classification") or record.get("lifecycle") or "new_work")
        project_id = _clean_string(record.get("project_id") or record.get("project"))
        parent_work_item_id = _clean_string(record.get("parent_work_item_id") or record.get("work_item_id"))
        component = _clean_string(record.get("component") or "platform")
        target_paths = _as_string_list(record.get("target_paths"))
        spec_links = _as_string_list(record.get("spec_links") or record.get("specification_links"))
        evidence_refs = tuple(
            _truncate(item, MAX_EVIDENCE_REF_CHARS) for item in _as_string_list(record.get("evidence_refs"))
        )
        owner_evidence_refs = _as_string_list(record.get("owner_evidence_refs"))
        acceptance_criteria = _as_string_list(record.get("acceptance_criteria"))

        candidate_wi_title = _candidate_wi_title(gap_id, title or "Untitled gap", lifecycle)
        linked_test_prompt = _linked_test_prompt(title, summary, acceptance_criteria)
        proposal_slug = f"gtkb-{_slugify(gap_id, title)}"

        issues = _validate_record(
            record,
            gap_id=gap_id,
            title=title,
            lifecycle=lifecycle,
            project_id=project_id,
            parent_work_item_id=parent_work_item_id,
            target_paths=target_paths,
            spec_links=spec_links,
            evidence_refs=evidence_refs,
        )
        rows.append(
            ChecklistRow(
                gap_id=gap_id,
                title=title,
                summary=summary,
                lifecycle_classification=lifecycle,
                project_id=project_id,
                parent_work_item_id=parent_work_item_id,
                component=component,
                candidate_wi_title=candidate_wi_title,
                linked_test_prompt=linked_test_prompt,
                proposal_slug=proposal_slug,
                pauth_need=_pauth_need(lifecycle),
                target_paths=target_paths,
                spec_links=spec_links,
                evidence_refs=evidence_refs,
                owner_evidence_refs=owner_evidence_refs,
                acceptance_criteria=acceptance_criteria,
                issues=issues,
            )
        )
    return rows


def _bullet_list(items: tuple[str, ...], *, empty: str = "_None supplied._") -> str:
    if not items:
        return empty
    return "\n".join(f"- `{item}`" for item in items)


def _issue_block(row: ChecklistRow) -> str:
    if not row.issues:
        return "- No validation issues."
    return "\n".join(f"- {issue.severity.upper()} `{issue.field}`: {issue.message}" for issue in row.issues)


def render_markdown_report(rows: list[ChecklistRow], *, generated_at: str | None = None) -> str:
    generated = generated_at or datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    ready = sum(1 for row in rows if not row.blocked)
    blocked = len(rows) - ready
    warnings = sum(1 for row in rows for issue in row.issues if issue.severity == "warning")

    table = [
        "| Gap | Lifecycle | Candidate WI | Linked Test Prompt | PAUTH | Proposal Slug | Status |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        table.append(
            "| "
            + " | ".join(
                [
                    _escape_table(row.gap_id),
                    _escape_table(row.lifecycle_classification),
                    _escape_table(row.candidate_wi_title),
                    _escape_table(row.linked_test_prompt),
                    _escape_table(row.pauth_need),
                    f"`{row.proposal_slug}`",
                    row.status,
                ]
            )
            + " |"
        )

    sections = [
        "# Harness Equivalence Phase 3 Child-WI Checklist",
        "",
        f"Generated: `{generated}`",
        "",
        "Scope: deterministic dry-run recommendations only. This helper performed no MemBase mutation, no bridge "
        "mutation, and no backlog mutation; governed CLI workflows remain the authority for creating child work.",
        "",
        f"Summary: `{len(rows)}` gaps processed; `{ready}` ready; `{blocked}` blocked; `{warnings}` warnings.",
        "",
        *table,
        "",
    ]

    for row in rows:
        sections.extend(
            [
                f"## {row.gap_id} - {row.title or 'Untitled gap'}",
                "",
                f"Status: `{row.status}`",
                f"Lifecycle classification: `{row.lifecycle_classification}`",
                f"Project: `{row.project_id or 'missing'}`",
                f"Parent work item: `{row.parent_work_item_id or 'missing'}`",
                f"Component: `{row.component}`",
                "",
                "### Candidate Work Item Skeleton",
                "",
                f"- Title: {row.candidate_wi_title}",
                "- Stage: `backlogged`",
                f"- PAUTH need: {row.pauth_need}",
                f"- Summary: {row.summary or '_No summary supplied._'}",
                "",
                "### Linked Test Prompt",
                "",
                row.linked_test_prompt,
                "",
                "### Bridge Proposal Skeleton",
                "",
                f"- Slug: `{row.proposal_slug}`",
                f"- target_paths:\n{_bullet_list(row.target_paths)}",
                f"- spec_links:\n{_bullet_list(row.spec_links)}",
                f"- evidence_refs:\n{_bullet_list(row.evidence_refs)}",
                f"- owner_evidence_refs:\n{_bullet_list(row.owner_evidence_refs)}",
                "",
                "### Validation",
                "",
                _issue_block(row),
                "",
            ]
        )
    return "\n".join(sections).rstrip() + "\n"


def _escape_table(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def rows_as_json(rows: list[ChecklistRow]) -> dict[str, Any]:
    return {
        "dry_run": True,
        "mutations": {"membase": False, "bridge": False, "backlog": False},
        "allowed_lifecycle_classifications": list(ALLOWED_LIFECYCLE_CLASSIFICATIONS),
        "rows": [row.as_dict() for row in rows],
        "summary": {
            "processed": len(rows),
            "ready": sum(1 for row in rows if not row.blocked),
            "blocked": sum(1 for row in rows if row.blocked),
            "warnings": sum(1 for row in rows for issue in row.issues if issue.severity == "warning"),
        },
    }


def default_report_path(project_root: Path = PROJECT_ROOT) -> Path:
    return project_root / REPORT_DIR.relative_to(PROJECT_ROOT) / f"{REPORT_NAME_PREFIX}{now_stamp()}.md"


def validate_report_path(path: Path, *, project_root: Path = PROJECT_ROOT) -> Path:
    resolved = path.resolve()
    root = project_root.resolve()
    report_dir = (project_root / REPORT_DIR.relative_to(PROJECT_ROOT)).resolve()
    if root not in resolved.parents and resolved != root:
        raise ValueError(f"report path must stay under project root: {project_root}")
    if report_dir not in resolved.parents:
        raise ValueError(f"report path must stay under {report_dir}")
    if not resolved.name.startswith(REPORT_NAME_PREFIX) or resolved.suffix.lower() != ".md":
        raise ValueError(f"report filename must match {REPORT_NAME_PREFIX}*.md")
    return resolved


def write_report(markdown: str, report_file: Path, *, project_root: Path = PROJECT_ROOT) -> Path:
    target = validate_report_path(report_file, project_root=project_root)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(markdown, encoding="utf-8", newline="\n")
    return target


def read_json_input(path: str) -> Any:
    if path == "-":
        text = sys.stdin.read()
    else:
        text = Path(path).read_text(encoding="utf-8")
    return json.loads(text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="-", help="JSON input file, or '-' for stdin.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--report-file", help="Optional markdown report path under CODEX-INSIGHT-DROPBOX.")
    parser.add_argument("--fail-on-blocked", action="store_true", help="Return exit 2 when any row is blocked.")
    args = parser.parse_args(argv)

    try:
        rows = build_checklist(read_json_input(args.input))
        if args.format == "json":
            output = json.dumps(rows_as_json(rows), indent=2, sort_keys=True)
        else:
            output = render_markdown_report(rows)

        if args.report_file:
            if args.format != "markdown":
                raise ValueError("--report-file can only be used with --format markdown")
            written = write_report(output, Path(args.report_file))
            print(f"wrote dry-run checklist report: {written}")
        else:
            print(output, end="" if output.endswith("\n") else "\n")

        if args.fail_on_blocked and any(row.blocked for row in rows):
            return 2
        return 0
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
