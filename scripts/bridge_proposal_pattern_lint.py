#!/usr/bin/env python3
"""Lint bridge proposal text for recurring Codex review feedback patterns.

The tool is intentionally diagnostic by default. It prints findings and exits
zero unless ``--strict`` is supplied, which lets Prime run it during drafting
without accidentally turning advisory feedback into a filing blocker.
"""

from __future__ import annotations

import argparse
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BRIDGE_INDEX = PROJECT_ROOT / "bridge" / "INDEX.md"

PROPOSAL_STATUSES = {"NEW", "REVISED"}
STATUS_LINE_RE = re.compile(r"^(NEW|REVISED|GO|NO-GO|VERIFIED|WITHDRAWN|ADVISORY|DEFERRED):\s*(bridge/.+\.md)\s*$")
CODEX_VERIFIED_PENDING_RE = re.compile(r"\bCodex\s+VERIFIED\s*\(\s*pending\s*\)", re.IGNORECASE)
PYTEST_COMMAND_RE = re.compile(r"(?i)(?:^|[`$>]|(?:run|cmd|command):\s*)\s*pytest(?:\s|$)")
RULE_DOCUMENTATION_RE = re.compile(
    r"(?i)(?:recorded .*pattern|pattern \([a-d]\)|literal substring|flag with|flagged|detects|detector targets|"
    r"negative case|positive case|lint inventory)"
)
OWNER_INPUT_RE = re.compile(
    r"(?i)\b(?:pending decision|owner approval needed|awaiting owner|owner input required|decision needed from owner)\b"
)
APPROVAL_PACKET_RE = re.compile(r"(?i)(?:formal-artifact-approval|narrative-artifact|approval packet)")
OWNER_HEADING_TEXT = "OWNER ACTION REQUIRED"
OWNER_REQUIRED_LABELS = (
    "Status:",
    "Decision / Question:",
    "Needed from Mike:",
    "Why it matters:",
    "Options:",
    "Reply requested:",
)


@dataclass(frozen=True)
class Finding:
    pattern_id: str
    title: str
    message: str
    hint: str
    line: int | None = None

    def render(self) -> str:
        location = f" line {self.line}" if self.line is not None else ""
        return f"[{self.pattern_id}]{location} {self.title}: {self.message}\n  Hint: {self.hint}"


def _strip_markdown_leader(line: str) -> str:
    stripped = line.strip()
    stripped = re.sub(r"^[-*+]\s+", "", stripped)
    stripped = re.sub(r"^\d+[.)]\s+", "", stripped)
    return stripped.strip()


def _line_has_python_m_pytest(line: str) -> bool:
    return re.search(r"(?i)\bpython\s+-m\s+pytest\b", line) is not None


def _line_has_bare_pytest_command(line: str) -> bool:
    candidate = _strip_markdown_leader(line)
    if RULE_DOCUMENTATION_RE.search(candidate):
        return False
    if _line_has_python_m_pytest(candidate):
        return False
    return PYTEST_COMMAND_RE.search(candidate) is not None


def _line_documents_lint_rule(line: str) -> bool:
    return RULE_DOCUMENTATION_RE.search(line) is not None


def _owner_heading_line(line: str) -> bool:
    stripped = line.strip()
    markdown_heading = re.sub(r"^#+\s*", "", stripped).strip()
    return stripped == OWNER_HEADING_TEXT or markdown_heading == OWNER_HEADING_TEXT


def _owner_block_body(lines: list[str], heading_index: int) -> str:
    body: list[str] = []
    for line in lines[heading_index + 1 :]:
        if line.startswith("## "):
            break
        body.append(line)
    return "\n".join(body)


def _owner_action_required_needed(text: str) -> bool:
    return OWNER_INPUT_RE.search(text) is not None and APPROVAL_PACKET_RE.search(text) is not None


def lint_text(text: str) -> list[Finding]:
    findings: list[Finding] = []
    lines = text.splitlines()

    for index, line in enumerate(lines, start=1):
        if _line_documents_lint_rule(line):
            continue

        if _line_has_bare_pytest_command(line):
            findings.append(
                Finding(
                    pattern_id="bare-pytest",
                    title="Bare pytest command",
                    message="Use `python -m pytest` so the repository interpreter and module path are explicit.",
                    hint="Replace `pytest ...` with `python -m pytest ...`.",
                    line=index,
                )
            )

        if CODEX_VERIFIED_PENDING_RE.search(line):
            findings.append(
                Finding(
                    pattern_id="codex-verified-pending",
                    title="Pre-authored Codex verdict",
                    message="A pre-implementation proposal cannot claim `Codex VERIFIED (pending)`.",
                    hint="Use `Codex GO` for approved implementation scope, then file a post-implementation report.",
                    line=index,
                )
            )

        if 'python -c "' in line and r"\"" in line:
            findings.append(
                Finding(
                    pattern_id="powershell-inline-python-escaping",
                    title="PowerShell-fragile inline Python escaping",
                    message='Inline `python -c "..."` contains backslash-escaped double quotes.',
                    hint="Use a here-string/heredoc, a temporary script, or single-quoted Python literals.",
                    line=index,
                )
            )

    if _owner_action_required_needed(text):
        heading_index = next((index for index, line in enumerate(lines) if _owner_heading_line(line)), None)
        if heading_index is None:
            findings.append(
                Finding(
                    pattern_id="owner-action-required",
                    title="Missing OWNER ACTION REQUIRED block",
                    message="Owner input is requested while approval-packet evidence is in scope, but the block is absent.",
                    hint="Add a standalone `OWNER ACTION REQUIRED` block with all required field labels.",
                )
            )
        else:
            body = _owner_block_body(lines, heading_index)
            missing = [label for label in OWNER_REQUIRED_LABELS if label not in body]
            if missing:
                findings.append(
                    Finding(
                        pattern_id="owner-action-required",
                        title="Incomplete OWNER ACTION REQUIRED block",
                        message="The block is missing required field label(s): " + ", ".join(missing),
                        hint="Include Status, Decision / Question, Needed from Mike, Why it matters, Options, and Reply requested.",
                        line=heading_index + 1,
                    )
                )

    return findings


def _parse_index_versions(index_text: str, bridge_id: str) -> list[tuple[str, str]]:
    versions: list[tuple[str, str]] = []
    in_doc = False
    for raw_line in index_text.splitlines():
        line = raw_line.strip()
        if line.startswith("Document:"):
            if in_doc:
                break
            in_doc = line.removeprefix("Document:").strip() == bridge_id
            continue
        if not in_doc:
            continue
        if not line:
            break
        match = STATUS_LINE_RE.match(line)
        if match:
            versions.append((match.group(1), match.group(2)))
    return versions


def resolve_bridge_proposal_path(bridge_id: str, *, project_root: Path = PROJECT_ROOT) -> Path:
    index_path = project_root / "bridge" / "INDEX.md"
    index_text = index_path.read_text(encoding="utf-8")
    versions = _parse_index_versions(index_text, bridge_id)
    for status, rel_path in versions:
        if status in PROPOSAL_STATUSES:
            return project_root / rel_path
    fallback = project_root / "bridge" / f"{bridge_id}.md"
    if fallback.is_file():
        return fallback
    raise FileNotFoundError(f"No NEW/REVISED bridge proposal found for {bridge_id!r}")


def lint_path(path: Path) -> list[Finding]:
    return lint_text(path.read_text(encoding="utf-8"))


def render_report(findings: Iterable[Finding], *, source: Path) -> str:
    findings = list(findings)
    lines = [f"Bridge proposal pattern lint: {source}", f"Findings: {len(findings)}"]
    if findings:
        lines.extend(finding.render() for finding in findings)
    else:
        lines.append("No recurring Codex feedback patterns detected.")
    return "\n".join(lines)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--bridge-id", help="Bridge document id from bridge/INDEX.md.")
    source.add_argument("--file", type=Path, help="Draft or bridge proposal file to lint.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when any finding is detected.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    source_path = args.file if args.file is not None else resolve_bridge_proposal_path(args.bridge_id)
    findings = lint_path(source_path)
    print(render_report(findings, source=source_path))
    return 1 if args.strict and findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
