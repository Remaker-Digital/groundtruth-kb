"""Tier-1 Code Quality Baseline proposal checks."""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from typing import Any

CANONICAL_RULE_IDS = (
    "CQ-SECRETS-001",
    "CQ-PATHS-001",
    "CQ-COMPLEXITY-001",
    "CQ-CONSTANTS-001",
    "CQ-SECURITY-001",
    "CQ-DOCS-001",
    "CQ-TESTS-001",
    "CQ-LOGGING-001",
    "CQ-VERIFICATION-001",
)
REQUIRED_HEADERS = ("Rule ID", "Applies?", "Compliance plan", "Verification", "Waiver / N/A reason")
VAGUE_PHRASES = ("TBD", "to be determined", "pending", "???", "will be careful", "best effort", "trivial", "obvious")
RULE_ID_RE = re.compile(r"^CQ-[A-Z]+-\d{3}$")
WAIVER_RE = re.compile(r"^Owner waiver:\s+(CQ-[A-Z]+-\d{3})\s+-\s+(DELIB-[A-Za-z0-9-]+)\s+-\s+.+$")


@dataclass(frozen=True)
class Finding:
    code: str
    message: str


def _rows(markdown: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in markdown.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if all(set(cell) <= {"-", ":"} for cell in cells):
            continue
        rows.append(cells)
    return rows


def validate(markdown: str) -> list[Finding]:
    findings: list[Finding] = []
    if "bridge_kind: implementation_proposal" not in markdown:
        return findings
    if "## Code Quality Baseline" not in markdown:
        findings.append(Finding("missing_heading", "missing ## Code Quality Baseline section"))
        return findings
    table_rows = _rows(markdown)
    if not table_rows:
        return [Finding("missing_table", "missing Code Quality Baseline table")]
    headers = table_rows[0]
    if headers != list(REQUIRED_HEADERS):
        findings.append(Finding("bad_headers", f"expected headers {REQUIRED_HEADERS}, got {headers!r}"))
        return findings

    seen: set[str] = set()
    for row in table_rows[1:]:
        if len(row) != len(REQUIRED_HEADERS):
            findings.append(Finding("bad_row_shape", f"malformed row: {row!r}"))
            continue
        rule_id, applies, plan, verification, reason = row
        if not RULE_ID_RE.match(rule_id):
            findings.append(Finding("bad_rule_id", f"invalid rule id: {rule_id!r}"))
            continue
        if rule_id not in CANONICAL_RULE_IDS:
            findings.append(Finding("unknown_rule_id", f"unknown rule id: {rule_id}"))
        seen.add(rule_id)
        if applies == "Yes" and (not plan or not verification):
            findings.append(Finding("empty_yes_cells", f"{rule_id} Yes row requires plan and verification"))
        elif applies == "N/A" and not reason:
            findings.append(Finding("empty_na_reason", f"{rule_id} N/A row requires reason"))
        elif applies.startswith("Owner waiver:"):
            match = WAIVER_RE.match(applies)
            if not match:
                findings.append(Finding("bad_waiver", f"{rule_id} waiver row lacks Owner waiver line"))
            elif match.group(1) != rule_id:
                findings.append(Finding("bad_waiver_rule", f"{rule_id} waiver references {match.group(1)}"))
        elif applies != "Yes" and applies != "N/A" and not applies.startswith("Owner waiver:"):
            findings.append(Finding("bad_applies", f"{rule_id} has invalid Applies? value: {applies!r}"))
        row_text = " ".join(row)
        for phrase in VAGUE_PHRASES:
            if phrase.lower() in row_text.lower():
                findings.append(Finding("vague_phrase", f"{rule_id} contains vague phrase: {phrase}"))
    missing = sorted(set(CANONICAL_RULE_IDS) - seen)
    if missing:
        findings.append(Finding("missing_rules", "missing canonical rule ids: " + ", ".join(missing)))
    return findings


@dataclass(frozen=True)
class CheckResult:
    passed: bool
    findings: tuple[str, ...] = ()


def check_content(markdown: str) -> CheckResult:
    findings = validate(markdown)
    return CheckResult(
        passed=not findings,
        findings=tuple(finding.message for finding in findings),
    )


def check_file(path: Any) -> CheckResult:
    from pathlib import Path

    return check_content(Path(path).read_text(encoding="utf-8"))


def hook_response(markdown: str) -> dict[str, Any]:
    findings = validate(markdown)
    if not findings:
        return {}
    return {
        "decision": "block",
        "reason": "Code Quality Baseline proposal check failed: "
        + "; ".join(f"{finding.code}: {finding.message}" for finding in findings),
    }


def _event_content(event: dict[str, Any]) -> str | None:
    tool_input = event.get("tool_input") or event.get("params") or {}
    path = str(tool_input.get("file_path") or tool_input.get("path") or "")
    if path and not path.replace("\\", "/").startswith("bridge/"):
        return None
    return tool_input.get("content") or tool_input.get("new_string") or tool_input.get("command")


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        event = {}
    content = _event_content(event)
    if content is None:
        print("{}")
        return 0
    print(json.dumps(hook_response(str(content))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
