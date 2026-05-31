#!/usr/bin/env python3
"""Re-run pytest claims from bridge post-implementation reports."""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Final

PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parent.parent
INDEX_DOC_RE: Final[re.Pattern[str]] = re.compile(r"^Document:\s+(\S+)\s*$")
INDEX_STATUS_RE: Final[re.Pattern[str]] = re.compile(
    r"^(NEW|REVISED|GO|NO-GO|VERIFIED|WITHDRAWN):\s+(bridge/\S+\.md)\s*$"
)
SUMMARY_TOKEN_RE: Final[re.Pattern[str]] = re.compile(
    r"\b(?P<count>\d+)\s+(?P<kind>passed|failed|errors?|skipped|xfailed|xpassed)\b",
    re.IGNORECASE,
)
UNSAFE_SHELL_RE: Final[re.Pattern[str]] = re.compile(r"(&&|\|\||[;&|<>`]|[$]\()")
COMMAND_PREFIX_RE: Final[re.Pattern[str]] = re.compile(
    r"^\s*(?:[$>]\s*|PS>\s*|Command:\s*)?(?P<command>.+?)\s*$",
    re.IGNORECASE,
)
COMMAND_START_RE: Final[re.Pattern[str]] = re.compile(
    r"^(?:python(?:3)?(?:\.exe)?|py(?:\.exe)?|pytest(?:\.exe)?|ruff|npm|pnpm|uv|make)\b",
    re.IGNORECASE,
)
PATH_LIKE_RE: Final[re.Pattern[str]] = re.compile(r"(^[.]{1,2}(?:/|\\|$)|/|\\|\.py(?:::\w+)?)")
PATH_OPTIONS: Final[frozenset[str]] = frozenset(
    {
        "--rootdir",
        "--basetemp",
        "--confcutdir",
        "--junitxml",
        "--ignore",
        "--ignore-glob",
    }
)
VALUE_OPTIONS: Final[frozenset[str]] = frozenset(
    {
        "-k",
        "-m",
        "--tb",
        "--maxfail",
        "--timeout",
        "--capture",
        "--rootdir",
        "--basetemp",
        "--confcutdir",
        "--junitxml",
        "--ignore",
        "--ignore-glob",
    }
)


class VerifierError(RuntimeError):
    """Raised when the requested report cannot be evaluated."""


@dataclass(frozen=True)
class BridgeVersion:
    status: str
    rel_path: str
    abs_path: Path
    version_number: int


@dataclass(frozen=True)
class ExtractedClaim:
    claim_block_index: int
    command: str
    claimed_summary: str
    claimed_counts: dict[str, int]


@dataclass(frozen=True)
class ClaimResult:
    claim_block_index: int
    command: str
    claimed_summary: str
    observed_summary: str | None
    status: str
    returncode: int | None
    reason: str
    claimed_counts: dict[str, int]
    observed_counts: dict[str, int]


def parse_index_for_document(index_path: Path, bridge_id: str) -> list[BridgeVersion]:
    if not index_path.is_file():
        raise VerifierError(f"bridge/INDEX.md not found: {index_path}")
    versions: list[BridgeVersion] = []
    in_target = False
    root = index_path.parent.parent
    for raw_line in index_path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        doc_match = INDEX_DOC_RE.match(line)
        if doc_match:
            in_target = doc_match.group(1) == bridge_id
            continue
        if not in_target:
            continue
        status_match = INDEX_STATUS_RE.match(line)
        if status_match:
            rel_path = status_match.group(2)
            version_match = re.search(r"-(\d+)\.md$", rel_path)
            versions.append(
                BridgeVersion(
                    status=status_match.group(1),
                    rel_path=rel_path,
                    abs_path=root / rel_path,
                    version_number=int(version_match.group(1)) if version_match else 1,
                )
            )
        elif line == "":
            break
    if not versions:
        raise VerifierError(f"Document {bridge_id!r} not found in bridge/INDEX.md")
    return versions


def resolve_report_path(project_root: Path, bridge_id: str, report_version: int | None) -> Path:
    if report_version is not None:
        path = project_root / "bridge" / f"{bridge_id}-{report_version:03d}.md"
        if not path.is_file():
            raise VerifierError(f"Report version not found: {path}")
        return path

    versions = parse_index_for_document(project_root / "bridge" / "INDEX.md", bridge_id)
    for version in versions:
        if not version.abs_path.is_file():
            continue
        content = version.abs_path.read_text(encoding="utf-8-sig")
        lowered = content.lower()
        if "bridge_kind: implementation_report" in lowered or "post-implementation report" in lowered:
            return version.abs_path
    raise VerifierError(f"No bridge implementation report found for {bridge_id!r}; pass --report-version")


def extract_code_blocks(markdown: str) -> list[str]:
    blocks: list[str] = []
    in_fence = False
    fence_lines: list[str] = []
    indented_lines: list[str] = []

    def flush_indented() -> None:
        nonlocal indented_lines
        if indented_lines:
            blocks.append("\n".join(indented_lines).strip("\n"))
            indented_lines = []

    for line in markdown.splitlines():
        if line.strip().startswith(("```", "~~~")):
            if in_fence:
                blocks.append("\n".join(fence_lines).strip("\n"))
                fence_lines = []
                in_fence = False
            else:
                flush_indented()
                in_fence = True
            continue
        if in_fence:
            fence_lines.append(line)
            continue
        if line.startswith("    ") or line.startswith("\t"):
            indented_lines.append(line[4:] if line.startswith("    ") else line[1:])
        else:
            flush_indented()
    flush_indented()
    return [block for block in blocks if block.strip()]


def parse_summary(text: str) -> dict[str, int]:
    counts = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0, "xfailed": 0, "xpassed": 0}
    for match in SUMMARY_TOKEN_RE.finditer(text):
        kind = match.group("kind").lower()
        if kind == "error":
            kind = "errors"
        counts[kind] = int(match.group("count"))
    return counts if any(counts.values()) else {}


def find_summary_line(lines: list[str], *, after_index: int | None = None) -> str | None:
    candidates = lines[after_index + 1 :] if after_index is not None else lines
    for line in reversed(candidates):
        if parse_summary(line):
            return line.strip()
    return None


def normalize_command_line(line: str) -> str | None:
    match = COMMAND_PREFIX_RE.match(line.strip())
    if not match:
        return None
    command = match.group("command").strip()
    if not COMMAND_START_RE.match(command):
        return None
    return command


def extract_claims(markdown: str) -> list[ExtractedClaim]:
    claims: list[ExtractedClaim] = []
    for block_index, block in enumerate(extract_code_blocks(markdown), start=1):
        lines = [line.rstrip() for line in block.splitlines()]
        command_line: str | None = None
        command_index: int | None = None
        for index, line in enumerate(lines):
            command = normalize_command_line(line)
            if command is not None:
                command_line = command
                command_index = index
                break
        if command_line is None:
            continue
        summary_line = find_summary_line(lines, after_index=command_index)
        if summary_line is None:
            continue
        claims.append(
            ExtractedClaim(
                claim_block_index=block_index,
                command=command_line,
                claimed_summary=summary_line,
                claimed_counts=parse_summary(summary_line),
            )
        )
    return claims


def pytest_args_for_command(command: str) -> tuple[list[str] | None, str | None]:
    if UNSAFE_SHELL_RE.search(command):
        return None, "command contains shell metacharacters or chaining"
    try:
        parts = shlex.split(command)
    except ValueError as exc:
        return None, f"command cannot be parsed safely: {exc}"
    if not parts:
        return None, "empty command"

    executable = Path(parts[0]).name.lower()
    if executable in {"python", "python3", "python.exe", "py", "py.exe"}:
        if len(parts) < 3 or parts[1:3] != ["-m", "pytest"]:
            return None, "command is not a python -m pytest invocation"
        return parts[3:], None
    if executable in {"pytest", "pytest.exe"}:
        return parts[1:], None
    return None, "command is not a pytest invocation"


def _path_within_root(project_root: Path, value: str) -> bool:
    target_text = value.split("::", 1)[0]
    if not target_text:
        return True
    candidate = Path(target_text)
    resolved = (
        candidate.resolve(strict=False) if candidate.is_absolute() else (project_root / candidate).resolve(strict=False)
    )
    try:
        resolved.relative_to(project_root.resolve())
    except ValueError:
        return False
    return True


def validate_pytest_args(project_root: Path, pytest_args: list[str]) -> str | None:
    skip_next = False
    for arg in pytest_args:
        if skip_next:
            skip_next = False
            continue
        option_name = arg.split("=", 1)[0]
        if option_name in PATH_OPTIONS:
            return f"pytest option {option_name} is not safely re-runnable"
        if option_name in VALUE_OPTIONS and "=" not in arg:
            skip_next = True
            continue
        if arg.startswith("-"):
            continue
        if PATH_LIKE_RE.search(arg) and not _path_within_root(project_root, arg):
            return f"pytest target escapes project root: {arg}"
    return None


def run_pytest_claim(project_root: Path, claim: ExtractedClaim, timeout_seconds: int) -> ClaimResult:
    pytest_args, error = pytest_args_for_command(claim.command)
    if error is not None or pytest_args is None:
        return ClaimResult(
            claim_block_index=claim.claim_block_index,
            command=claim.command,
            claimed_summary=claim.claimed_summary,
            observed_summary=None,
            status="ERROR",
            returncode=None,
            reason=error or "command not safely re-runnable",
            claimed_counts=claim.claimed_counts,
            observed_counts={},
        )
    validation_error = validate_pytest_args(project_root, pytest_args)
    if validation_error is not None:
        return ClaimResult(
            claim_block_index=claim.claim_block_index,
            command=claim.command,
            claimed_summary=claim.claimed_summary,
            observed_summary=None,
            status="ERROR",
            returncode=None,
            reason=validation_error,
            claimed_counts=claim.claimed_counts,
            observed_counts={},
        )

    state_dir = project_root / ".gtkb-state" / "test-claim-rerun"
    state_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    with tempfile.TemporaryDirectory(prefix="pytest-", dir=state_dir) as temp_dir:
        env.update({"TMPDIR": temp_dir, "TEMP": temp_dir, "TMP": temp_dir})
        completed = subprocess.run(
            [sys.executable, "-m", "pytest", *pytest_args],
            cwd=project_root,
            env=env,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )

    output_lines = (completed.stdout + "\n" + completed.stderr).splitlines()
    observed_summary = find_summary_line(output_lines)
    if observed_summary is None:
        return ClaimResult(
            claim_block_index=claim.claim_block_index,
            command=claim.command,
            claimed_summary=claim.claimed_summary,
            observed_summary=None,
            status="ERROR",
            returncode=completed.returncode,
            reason="pytest run produced no parseable summary line",
            claimed_counts=claim.claimed_counts,
            observed_counts={},
        )
    observed_counts = parse_summary(observed_summary)
    if observed_counts == claim.claimed_counts:
        return ClaimResult(
            claim_block_index=claim.claim_block_index,
            command=claim.command,
            claimed_summary=claim.claimed_summary,
            observed_summary=observed_summary,
            status="PASS",
            returncode=completed.returncode,
            reason="observed pytest summary matches claimed summary",
            claimed_counts=claim.claimed_counts,
            observed_counts=observed_counts,
        )
    return ClaimResult(
        claim_block_index=claim.claim_block_index,
        command=claim.command,
        claimed_summary=claim.claimed_summary,
        observed_summary=observed_summary,
        status="DIVERGED",
        returncode=completed.returncode,
        reason="observed pytest summary differs from claimed summary",
        claimed_counts=claim.claimed_counts,
        observed_counts=observed_counts,
    )


def build_packet(
    *,
    bridge_id: str,
    project_root: Path = PROJECT_ROOT,
    report_version: int | None = None,
    timeout_seconds: int = 30,
) -> dict[str, object]:
    root = project_root.resolve()
    report_path = resolve_report_path(root, bridge_id, report_version)
    content = report_path.read_text(encoding="utf-8-sig")
    claims = extract_claims(content)
    results = [run_pytest_claim(root, claim, timeout_seconds) for claim in claims]
    failed = [result for result in results if result.status != "PASS"]
    packet: dict[str, object] = {
        "bridge_id": bridge_id,
        "report_file": report_path.relative_to(root).as_posix(),
        "claim_count": len(results),
        "status": "fail" if failed else "pass",
        "claims": [asdict(result) for result in results],
    }
    packet["markdown"] = format_markdown(packet)
    return packet


def format_markdown(packet: dict[str, object]) -> str:
    lines = [
        "## Test-Claim Re-Run",
        "",
        f"- bridge_id: `{packet['bridge_id']}`",
        f"- report_file: `{packet['report_file']}`",
        f"- status: `{packet['status']}`",
        f"- claim_count: `{packet['claim_count']}`",
        "",
    ]
    claims = packet.get("claims", [])
    if not claims:
        lines.append("No pytest command/output claim blocks detected.")
        return "\n".join(lines) + "\n"
    lines.extend(
        [
            "| Block | Status | Command | Claimed | Observed | Reason |",
            "|---|---|---|---|---|---|",
        ]
    )
    for raw in claims:
        assert isinstance(raw, dict)
        lines.append(
            "| {block} | `{status}` | `{command}` | `{claimed}` | `{observed}` | {reason} |".format(
                block=raw["claim_block_index"],
                status=raw["status"],
                command=str(raw["command"]).replace("|", "\\|"),
                claimed=str(raw["claimed_summary"]).replace("|", "\\|"),
                observed=str(raw.get("observed_summary") or "").replace("|", "\\|"),
                reason=str(raw["reason"]).replace("|", "\\|"),
            )
        )
    return "\n".join(lines) + "\n"


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bridge-id", required=True, help="Bridge Document id from bridge/INDEX.md.")
    parser.add_argument("--report-version", type=int, default=None, help="Specific report version number to inspect.")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT, help=argparse.SUPPRESS)
    parser.add_argument("--timeout-seconds", type=int, default=30, help="Per-claim pytest timeout.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when any claim diverges or errors.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    try:
        packet = build_packet(
            bridge_id=args.bridge_id,
            project_root=args.project_root,
            report_version=args.report_version,
            timeout_seconds=args.timeout_seconds,
        )
    except VerifierError as exc:
        payload = {"status": "error", "error": str(exc)}
        if args.json:
            sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        else:
            sys.stdout.write(f"ERROR: {exc}\n")
        return 2
    if args.json:
        sys.stdout.write(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    else:
        sys.stdout.write(str(packet["markdown"]))
    return 1 if args.strict and packet["status"] != "pass" else 0


if __name__ == "__main__":
    raise SystemExit(main())
