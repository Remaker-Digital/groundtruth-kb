#!/usr/bin/env python3
"""Lint bridge proposal text for recurring Codex review feedback patterns.

The tool is intentionally diagnostic by default. It prints findings and exits
zero unless ``--strict`` is supplied, which lets Prime run it during drafting
without accidentally turning advisory feedback into a filing blocker.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

PROPOSAL_STATUSES = {"NEW", "REVISED"}
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

# git-hooks-path-mismatch detector (WI-3482).
# The Git default hook directory; when ``core.hooksPath`` differs, files under
# ``.git/hooks`` are inert because Git never consults them.
_GIT_DEFAULT_HOOKS_PATH = ".git/hooks"
# Inactive-surface tokens a proposal must not target when core.hooksPath differs:
# the default hook directory and the historical staging path (both named in the
# WI-3482 acceptance summary).
INACTIVE_HOOK_TOKENS = (".git/hooks/", "scripts/guardrails/pre-commit")
# Sentinel: resolve the active hook path from live git config. Tests inject an
# explicit string (including "" for the Git default) to stay hermetic.
_RESOLVE_HOOKS_PATH = object()
# A dedicated guard so a proposal *describing* the hooks-path hazard (like the
# WI-3482 proposal itself, or this module's own docs) does not self-trigger,
# while a proposal that genuinely *targets* the inactive surface still fires.
# Kept separate from RULE_DOCUMENTATION_RE so other detectors are unaffected.
HOOKS_HAZARD_DOCUMENTATION_RE = re.compile(
    r"(?i)(?:inactive|inert|never consult|overrides? the default|silently[- ]broken|"
    r"core\.hooksPath|active (?:hook|path)|hook surface|would modify a directory|"
    r"git never consults|git-hooks-path-mismatch|produces? (?:a |no )?finding|reproduces?|"
    r"the detector|token scan|\bfires?\b)"
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


def _normalize_path_separators(value: str) -> str:
    """Fold Windows-style backslashes to forward slashes for path-token matching."""
    return value.replace("\\", "/")


def _resolve_active_hooks_path(project_root: Path = PROJECT_ROOT) -> str:
    """Return the repo's active ``core.hooksPath`` (normalized); ``""`` if default.

    Reads ``git config --get core.hooksPath`` with ``cwd=project_root``, no shell,
    captured output. A missing/empty/failed read degrades to ``""`` (the Git
    default ``.git/hooks``), so a default-configured clone never trips the
    detector. The subprocess is guarded; ``git`` absence is a no-op, not a crash.
    """
    try:
        completed = subprocess.run(
            ["git", "config", "--get", "core.hooksPath"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    if completed.returncode != 0:
        return ""
    return _normalize_path_separators(completed.stdout.strip())


def _line_targets_inactive_hook_surface(line: str) -> bool:
    """True when ``line`` references an inactive hook surface but is not hazard docs.

    Folds backslashes first (so ``.git\\hooks\\pre-commit`` matches), checks for an
    inactive-surface token, and excludes lines that merely *describe* the hazard
    via ``HOOKS_HAZARD_DOCUMENTATION_RE`` so the detector does not self-trigger on
    a proposal that explains the check.
    """
    normalized = _normalize_path_separators(line)
    if not any(token in normalized for token in INACTIVE_HOOK_TOKENS):
        return False
    return HOOKS_HAZARD_DOCUMENTATION_RE.search(line) is None


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


def lint_text(text: str, *, active_hooks_path: object = _RESOLVE_HOOKS_PATH) -> list[Finding]:
    findings: list[Finding] = []
    lines = text.splitlines()

    # Resolve the active hook path once. ``_RESOLVE_HOOKS_PATH`` triggers a live
    # ``git config`` read; tests inject an explicit string (including "" for the
    # Git default) so they never touch real git config.
    if active_hooks_path is _RESOLVE_HOOKS_PATH:
        resolved_hooks_path = _resolve_active_hooks_path()
    else:
        resolved_hooks_path = _normalize_path_separators(str(active_hooks_path or ""))
    hooks_path_is_nondefault = resolved_hooks_path not in ("", _GIT_DEFAULT_HOOKS_PATH)

    for index, line in enumerate(lines, start=1):
        if _line_documents_lint_rule(line):
            continue

        if hooks_path_is_nondefault and _line_targets_inactive_hook_surface(line):
            findings.append(
                Finding(
                    pattern_id="git-hooks-path-mismatch",
                    title="Target surface is an inactive Git hook path",
                    message=(
                        "References an inactive hook surface (.git/hooks or scripts/guardrails/pre-commit) "
                        f"while the active hook path is '{resolved_hooks_path}'. Git does not consult "
                        ".git/hooks when core.hooksPath differs, so edits there are silently inert."
                    ),
                    hint=(
                        f"Target the active hook directory '{resolved_hooks_path}' "
                        f"(e.g. {resolved_hooks_path}/pre-commit) instead of the .git/hooks default."
                    ),
                    line=index,
                )
            )

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


def resolve_bridge_proposal_path(bridge_id: str, *, project_root: Path = PROJECT_ROOT) -> Path:
    gt_src = project_root / "groundtruth-kb" / "src"
    if gt_src.is_dir() and str(gt_src) not in sys.path:
        sys.path.insert(0, str(gt_src))
    from groundtruth_kb.bridge.versioned_files import scan_expected_documents, status_from_bridge_file

    document = scan_expected_documents(project_root).get(bridge_id)
    if document is not None:
        for rel_path in reversed(document.files):
            status = status_from_bridge_file(project_root / rel_path)
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
    source.add_argument("--bridge-id", help="Bridge document slug from numbered bridge files.")
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
