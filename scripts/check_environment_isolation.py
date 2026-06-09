#!/usr/bin/env python3
"""Phase 3 environment-boundary checker for Agent Red.

Static, deterministic, network-free probe of the Agent Red application
environment. Reports repository identity and the default GroundTruth-KB
dependency mode, and runs first-slice GTKB-ISOLATION-003 policy checks
against `.dockerignore`, `Dockerfile`, `docker-compose.yml`, and the default
application requirement files.

Exit code is 0 when no `error`-severity findings are present, non-zero
otherwise. This script is intended to run inside
``scripts/release_candidate_gate.py`` before the pytest lane so environment
boundary regressions surface before broader test execution.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DOCKERIGNORE_REQUIRED_RULES: tuple[str, ...] = (
    ".codex",
    ".groundtruth",
    "bridge",
    "independent-progress-assessments",
    "groundtruth.db",
    ".groundtruth-chroma",
)

DOCKERFILE_FORBIDDEN_COPY_SOURCES: tuple[str, ...] = (
    ".claude",
    ".codex",
    ".groundtruth",
    "bridge",
    "independent-progress-assessments",
    "groundtruth.db",
)

REQUIREMENT_FILES: tuple[str, ...] = (
    "requirements.txt",
    "requirements-test.txt",
    "requirements-local.txt",
)


@dataclass
class Finding:
    code: str
    severity: str
    path: str
    message: str


@dataclass
class EnvironmentReport:
    cwd: str
    repo_root: str | None
    git_remote: str | None
    git_branch: str | None
    default_gtkb_dependency_mode: str
    findings: list[Finding] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "cwd": self.cwd,
            "repo_root": self.repo_root,
            "git_remote": self.git_remote,
            "git_branch": self.git_branch,
            "default_gtkb_dependency_mode": self.default_gtkb_dependency_mode,
            "findings": [asdict(f) for f in self.findings],
        }

    @property
    def has_errors(self) -> bool:
        return any(f.severity == "error" for f in self.findings)


def _git(args: list[str], *, root: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return None
    if result.returncode != 0:
        return None
    stdout = result.stdout.strip()
    return stdout or None


def probe_git(root: Path) -> tuple[str | None, str | None, str | None]:
    """Return (repo_root, remote_url, branch_name) as reported by git."""
    repo_root = _git(["rev-parse", "--show-toplevel"], root=root)
    remote = _git(["config", "--get", "remote.origin.url"], root=root)
    branch = _git(["rev-parse", "--abbrev-ref", "HEAD"], root=root)
    return repo_root, remote, branch


def _read_lines(path: Path) -> list[str] | None:
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None


def _dockerignore_rules(root: Path) -> set[str] | None:
    lines = _read_lines(root / ".dockerignore")
    if lines is None:
        return None
    rules: set[str] = set()
    for raw in lines:
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("!"):
            continue
        rules.add(stripped.rstrip("/"))
    return rules


def check_dockerignore(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    rules = _dockerignore_rules(root)
    if rules is None:
        findings.append(
            Finding(
                code="DOCKERIGNORE_MISSING_FILE",
                severity="error",
                path=".dockerignore",
                message=".dockerignore not found at repository root",
            )
        )
        return findings
    for required in DOCKERIGNORE_REQUIRED_RULES:
        if required not in rules:
            findings.append(
                Finding(
                    code="DOCKERIGNORE_MISSING_RULE",
                    severity="error",
                    path=".dockerignore",
                    message=(f"missing required denylist entry for GT-KB governance/runtime surface: {required}"),
                )
            )
    return findings


_COPY_PATTERN = re.compile(
    r"^\s*COPY\s+(?:--[^\s]+\s+)*(?P<source>\S+)\s+\S+\s*$",
    re.IGNORECASE,
)


def _first_path_segment(source: str) -> str:
    candidate = source
    if candidate.startswith("./"):
        candidate = candidate[2:]
    candidate = candidate.rstrip("/")
    return candidate.split("/", 1)[0]


def check_dockerfile(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    lines = _read_lines(root / "Dockerfile")
    if lines is None:
        return findings
    forbidden = {src.rstrip("/") for src in DOCKERFILE_FORBIDDEN_COPY_SOURCES}
    for lineno, raw in enumerate(lines, start=1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = _COPY_PATTERN.match(raw)
        if not match:
            continue
        source = match.group("source").strip()
        first = _first_path_segment(source)
        if first in forbidden:
            findings.append(
                Finding(
                    code="DOCKERFILE_FORBIDDEN_COPY",
                    severity="error",
                    path=f"Dockerfile:{lineno}",
                    message=(f"COPY source '{source}' imports a GT-KB governance/runtime surface"),
                )
            )
    return findings


# The host group allows either a Windows drive-letter prefix
# (e.g. `C:/foo` or `D:\bar`) or a regular path that has no colon.
# The alternation must appear in this order because the drive-letter
# branch contains a `:` that would otherwise be captured as the
# host/container separator.
_COMPOSE_VOLUME_PATTERN = re.compile(
    r"^\s*-\s+\"?"
    r"(?P<host>(?:[A-Za-z]:[/\\][^:\"]*)|(?:[^\s:\"][^:\"]*))"
    r":(?P<container>[^:\s\"]+)"
    r"(?::(?P<opts>[^\s\"]+))?\"?\s*$"
)

_WINDOWS_DRIVE_LETTER_PATTERN = re.compile(r"^[A-Za-z]:[/\\]")


def _is_host_path(host: str) -> bool:
    return (
        host.startswith(".") or host.startswith("/") or "/" in host or bool(_WINDOWS_DRIVE_LETTER_PATTERN.match(host))
    )


def check_compose(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    lines = _read_lines(root / "docker-compose.yml")
    if lines is None:
        return findings
    for lineno, raw in enumerate(lines, start=1):
        match = _COMPOSE_VOLUME_PATTERN.match(raw)
        if not match:
            continue
        host = match.group("host")
        container = match.group("container")
        opts = match.group("opts") or ""
        if not _is_host_path(host):
            continue
        if (
            host.startswith("/")
            or host.startswith("..")
            or "/../" in host
            or bool(_WINDOWS_DRIVE_LETTER_PATTERN.match(host))
        ):
            findings.append(
                Finding(
                    code="COMPOSE_HOST_BIND_OUT_OF_APP",
                    severity="error",
                    path=f"docker-compose.yml:{lineno}",
                    message=(f"host bind '{host}:{container}' must stay within the app repository (use './<path>')"),
                )
            )
            continue
        # All repo-local binds (those passing _is_host_path and not caught by
        # COMPOSE_HOST_BIND_OUT_OF_APP above) must be read-only by default,
        # per the Phase 3 approved policy.
        opt_tokens = {tok for tok in opts.split(",") if tok}
        if "ro" not in opt_tokens:
            findings.append(
                Finding(
                    code="COMPOSE_SOURCE_BIND_NOT_READONLY",
                    severity="error",
                    path=f"docker-compose.yml:{lineno}",
                    message=(f"repo-local bind '{host}:{container}' must be mounted read-only (':ro')"),
                )
            )
    return findings


_EDITABLE_GTKB_PATTERN = re.compile(r"^\s*-e\s+.*groundtruth[-_]kb", re.IGNORECASE)
_RELEASED_GTKB_PATTERN = re.compile(r"^\s*groundtruth[-_]kb\b", re.IGNORECASE)


def detect_gtkb_mode(root: Path) -> tuple[str, list[Finding]]:
    findings: list[Finding] = []
    mode = "missing"
    editable_seen = False
    released_seen = False

    for filename in REQUIREMENT_FILES:
        lines = _read_lines(root / filename)
        if lines is None:
            continue
        for lineno, raw in enumerate(lines, start=1):
            stripped = raw.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if _EDITABLE_GTKB_PATTERN.match(stripped):
                editable_seen = True
                findings.append(
                    Finding(
                        code="REQUIREMENTS_EDITABLE_GTKB_SIBLING",
                        severity="error",
                        path=f"{filename}:{lineno}",
                        message=(
                            "active editable 'groundtruth-kb' sibling-checkout "
                            "install is not allowed in app-default requirement "
                            "files"
                        ),
                    )
                )
                continue
            if _RELEASED_GTKB_PATTERN.match(stripped):
                released_seen = True

    if editable_seen:
        mode = "editable_local"
    elif released_seen:
        mode = "released_package"
    return mode, findings


def build_report(root: Path) -> EnvironmentReport:
    repo_root, git_remote, git_branch = probe_git(root)
    mode, dep_findings = detect_gtkb_mode(root)
    report = EnvironmentReport(
        cwd=str(Path.cwd().resolve()),
        repo_root=repo_root,
        git_remote=git_remote,
        git_branch=git_branch,
        default_gtkb_dependency_mode=mode,
    )
    report.findings.extend(check_dockerignore(root))
    report.findings.extend(check_dockerfile(root))
    report.findings.extend(check_compose(root))
    report.findings.extend(dep_findings)
    return report


def _render_text(report: EnvironmentReport) -> str:
    lines: list[str] = []
    lines.append("Environment Isolation Report")
    lines.append("-" * 28)
    lines.append(f"  cwd:                          {report.cwd}")
    lines.append(f"  repo_root:                    {report.repo_root or '(not a git repository)'}")
    lines.append(f"  git_remote:                   {report.git_remote or '(none)'}")
    lines.append(f"  git_branch:                   {report.git_branch or '(unknown)'}")
    lines.append(f"  default_gtkb_dependency_mode: {report.default_gtkb_dependency_mode}")
    lines.append("")
    if report.findings:
        lines.append("Findings:")
        for finding in report.findings:
            lines.append(f"  [{finding.severity.upper()}] {finding.code} {finding.path}: {finding.message}")
    else:
        lines.append("No environment-isolation findings.")
    return "\n".join(lines)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Agent Red Phase 3 environment-boundary checker.")
    parser.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="Emit JSON output instead of human-readable text.",
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Override repository root (defaults to the Agent Red repo root).",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)
    root = Path(args.root).resolve() if args.root else PROJECT_ROOT

    report = build_report(root)
    if args.as_json:
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    else:
        print(_render_text(report))
    return 1 if report.has_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
