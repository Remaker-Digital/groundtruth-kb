#!/usr/bin/env python3
"""Read-only dispatcher black-box boundary scanner and closure gate.

The scanner classifies ordinary-worker evidence for direct black-box reads,
direct black-box mutations, missing worker-safe packet usage, ops/build
authority confusion, case-authorization bypass, and unsupported-surface waiver
gaps. It never mutates dispatcher, TAFE, harness, bridge, Git, or MemBase state.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROTECTED_SURFACE_RE = re.compile(
    r"(?i)(?:"
    r"\.gtkb-state[/\\](?:dispatcher-daemon|work-intent|implementation-authorizations|bridge-|leases)|"
    r"harness-state[/\\](?:harness-registry|harness-identities|[^\\/\s]+[/\\]session-envelopes)|"
    r"bridge[/\\](?:INDEX\.md|[^\\/\s]+-\d{3}\.md)|"
    r"scripts[/\\](?:gtkb_dispatcher_daemon|dispatcher_runtime|implementation_authorization|implementation_start_gate)\.py|"
    r"config[/\\]agent-control[/\\]activity-disposition-profiles\.toml"
    r")"
)
READ_VERB_RE = re.compile(r"(?i)\b(?:read|cat|type|get-content|select-string|rg|grep|open)\b")
MUTATION_VERB_RE = re.compile(
    r"(?i)\b(?:write|edit|patch|apply_patch|set-content|add-content|remove-item|move-item|delete|mutate|update)\b"
)
RAW_PACKET_RE = re.compile(
    r"(?i)(?:assigned\s+(?:proposal|verdict|report)|raw\s+bridge|bridge[/\\][^\\/\s]+-\d{3}\.md|bridge\s+show)"
)
SAFE_PACKET_RE = re.compile(
    r"(?i)(?:worker-context|worker_safe|worker-safe|assigned-content packet|mediated packet|build_worker_context_packet)"
)
OPS_BUILD_CONFUSION_RE = re.compile(
    r"(?i)(?:ops\b.{0,80}\b(?:internal|source|implementation|direct mutation)|"
    r"build\b.{0,80}\b(?:configuration|hook|prompt|skill)\b.{0,80}\bwithout\b.{0,40}\bops|"
    r"ordinary\b.{0,80}\b(?:harness-state|dispatcher-daemon|TAFE|runtime state))"
)
BUILD_INTERNAL_RE = re.compile(
    r"(?i)\bbuild\b.{0,100}\b(?:black-box internals?|dispatcher_runtime|gtkb_dispatcher_daemon|TAFE|runtime state)"
)
CASE_AUTH_RE = re.compile(
    r"(?i)(?:case[- ]authorization|implementation-start|implementation_authorization\.py begin|PAUTH-)"
)
UNSUPPORTED_WAIVER_RE = re.compile(r"(?i)(?:unsupported surface|waiver)")
WAIVER_EVIDENCE_RE = re.compile(r"(?i)(?:DELIB-[A-Z0-9_-]+|AUQ-[A-Z0-9_-]+|owner decision)")


@dataclass(frozen=True)
class BoundaryFinding:
    finding_class: str
    source: str
    line_number: int
    evidence: str
    severity: str = "blocking"

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _line_window(lines: list[str], index: int, radius: int = 2) -> str:
    start = max(0, index - radius)
    end = min(len(lines), index + radius + 1)
    return "\n".join(lines[start:end])


def scan_text(text: str, *, source: str = "<memory>") -> list[BoundaryFinding]:
    """Classify black-box boundary findings in one evidence payload."""
    lines = text.splitlines()
    whole_text_has_safe_packet = SAFE_PACKET_RE.search(text) is not None
    findings: list[BoundaryFinding] = []
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        line_number = index + 1
        window = _line_window(lines, index)
        protected = PROTECTED_SURFACE_RE.search(stripped)
        if protected and READ_VERB_RE.search(stripped):
            findings.append(BoundaryFinding("direct_protected_read", source, line_number, stripped))
        if protected and MUTATION_VERB_RE.search(stripped):
            findings.append(BoundaryFinding("direct_protected_mutation", source, line_number, stripped))
        if RAW_PACKET_RE.search(stripped) and not (whole_text_has_safe_packet or SAFE_PACKET_RE.search(window)):
            findings.append(BoundaryFinding("missing_worker_safe_packet_usage", source, line_number, stripped))
        if OPS_BUILD_CONFUSION_RE.search(stripped):
            findings.append(BoundaryFinding("ops_build_authority_confusion", source, line_number, stripped))
        if BUILD_INTERNAL_RE.search(stripped) and CASE_AUTH_RE.search(window) is None:
            findings.append(BoundaryFinding("case_authorization_bypass", source, line_number, stripped))
        if UNSUPPORTED_WAIVER_RE.search(stripped) and WAIVER_EVIDENCE_RE.search(window) is None:
            findings.append(BoundaryFinding("unsupported_surface_waiver_gap", source, line_number, stripped))
    return findings


def scan_paths(paths: Iterable[Path]) -> list[BoundaryFinding]:
    findings: list[BoundaryFinding] = []
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="utf-8", errors="replace")
        findings.extend(scan_text(text, source=_display_path(path)))
    return findings


def _load_project_completion_scanner() -> Any:
    completion_scanner_path = (PROJECT_ROOT / "scripts" / "project_verified_completion_scanner.py").resolve()
    try:
        completion_scanner_path.relative_to(PROJECT_ROOT.resolve())
    except ValueError as exc:
        raise RuntimeError(
            f"Project completion scanner must resolve inside the project root: {completion_scanner_path}"
        ) from exc
    if not completion_scanner_path.is_file():
        raise RuntimeError(f"Project completion scanner not found: {completion_scanner_path}")

    spec = importlib.util.spec_from_file_location(
        "_gtkb_project_verified_completion_scanner",
        completion_scanner_path,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load project completion scanner: {completion_scanner_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if not callable(getattr(module, "member_completion_scan", None)):
        raise RuntimeError(f"Project completion scanner lacks member_completion_scan: {completion_scanner_path}")
    if not callable(getattr(module, "_ensure_groundtruth_importable", None)):
        raise RuntimeError(f"Project completion scanner lacks import bootstrap: {completion_scanner_path}")
    readiness_type = getattr(module, "MemberCompletionReadiness", None)
    if not callable(getattr(readiness_type, "from_service_status", None)):
        raise RuntimeError(f"Project completion scanner lacks readiness adapter: {completion_scanner_path}")
    return module


def _member_completion_status(project_root: Path, project_id: str) -> dict[str, Any]:
    completion_scanner = _load_project_completion_scanner()
    completion_scanner._ensure_groundtruth_importable(project_root)
    from groundtruth_kb.db import KnowledgeDB  # noqa: PLC0415
    from groundtruth_kb.project.lifecycle import ProjectLifecycleService  # noqa: PLC0415

    db = KnowledgeDB(project_root / "groundtruth.db")
    try:
        if db.get_project(project_id) is None:
            return {
                "project_id": project_id,
                "completion_ready": False,
                "nonterminal_work_item_ids": [],
                "exclusion_reasons": ["project_not_found"],
            }
        status = ProjectLifecycleService(db).member_completion_status(project_id, project_root=project_root)
        return completion_scanner.MemberCompletionReadiness.from_service_status(status).as_dict()
    finally:
        db.close()


def closure_status(
    *,
    project_root: Path = PROJECT_ROOT,
    project_id: str,
    evidence_paths: Iterable[Path] = (),
) -> dict[str, Any]:
    """Combine project terminal-state readiness with boundary-scan evidence."""
    member_status = _member_completion_status(project_root, project_id)
    findings = scan_paths(evidence_paths)
    blocking_findings = [finding for finding in findings if finding.severity == "blocking"]
    ready = bool(member_status.get("completion_ready")) and not blocking_findings
    return {
        "project_id": project_id,
        "ready": ready,
        "member_completion_ready": bool(member_status.get("completion_ready")),
        "member_completion": member_status,
        "boundary_finding_count": len(findings),
        "blocking_boundary_finding_count": len(blocking_findings),
        "findings": [finding.as_dict() for finding in findings],
    }


def format_text(report: dict[str, Any]) -> str:
    flag = "READY" if report["ready"] else "NOT READY"
    lines = [
        f"[{flag}] {report['project_id']}",
        f"member_completion_ready: {str(report['member_completion_ready']).lower()}",
        f"boundary_findings: {report['boundary_finding_count']}",
        f"blocking_boundary_findings: {report['blocking_boundary_finding_count']}",
    ]
    nonterminal = report.get("member_completion", {}).get("nonterminal_work_item_ids") or []
    if nonterminal:
        lines.append("nonterminal_work_items: " + ", ".join(nonterminal))
    for finding in report["findings"]:
        lines.append(
            "- {finding_class} {source}:{line_number}: {evidence}".format(
                finding_class=finding["finding_class"],
                source=finding["source"],
                line_number=finding["line_number"],
                evidence=finding["evidence"],
            )
        )
    return "\n".join(lines) + "\n"


def _display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return str(path)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-id", required=True, help="Project id to evaluate for closure readiness.")
    parser.add_argument("--evidence", action="append", type=Path, default=[], help="Evidence file to scan; repeatable.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    report = closure_status(project_id=args.project_id, evidence_paths=args.evidence)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(format_text(report), end="")
    return 0 if report["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
