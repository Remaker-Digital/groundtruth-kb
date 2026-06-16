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
BRIDGE_FILE_STATUS_RE: Final[re.Pattern[str]] = re.compile(
    r"^[#>*\-\s`]*(NEW|REVISED|GO|NO-GO|VERIFIED|WITHDRAWN)\b",
    re.IGNORECASE,
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
    claimed_summary: str | None
    claimed_counts: dict[str, int]


@dataclass(frozen=True)
class ClaimResult:
    claim_block_index: int
    command: str
    claimed_summary: str | None
    observed_summary: str | None
    status: str
    returncode: int | None
    reason: str
    claimed_counts: dict[str, int]
    observed_counts: dict[str, int]


def _status_from_bridge_file(path: Path) -> str | None:
    try:
        lines = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    except OSError:
        return None
    for raw in lines:
        stripped = raw.strip()
        if not stripped:
            continue
        match = BRIDGE_FILE_STATUS_RE.match(stripped)
        return match.group(1).upper() if match else None
    return None


def parse_index_for_document(bridge_dir: Path, bridge_id: str) -> list[BridgeVersion]:
    versions: list[BridgeVersion] = []
    for path in bridge_dir.glob(f"{bridge_id}-*.md"):
        version_match = re.match(rf"^{re.escape(bridge_id)}-(\d+)\.md$", path.name)
        if not version_match:
            continue
        status = _status_from_bridge_file(path)
        if status is None:
            continue
        versions.append(
            BridgeVersion(
                status=status,
                rel_path=f"bridge/{path.name}",
                abs_path=path,
                version_number=int(version_match.group(1)),
            )
        )
    if not versions:
        raise VerifierError(f"Bridge thread {bridge_id!r} has no readable numbered files")
    return sorted(versions, key=lambda version: version.version_number, reverse=True)


def resolve_report_path(project_root: Path, bridge_id: str, report_version: int | None) -> Path:
    if report_version is not None:
        path = project_root / "bridge" / f"{bridge_id}-{report_version:03d}.md"
        if not path.is_file():
            raise VerifierError(f"Report version not found: {path}")
        return path

    versions = parse_index_for_document(project_root / "bridge", bridge_id)
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


_CROSS_BLOCK_LOOKAHEAD: Final[int] = 2


def _first_command_in_block(block: str) -> tuple[str | None, int | None]:
    lines = [line.rstrip() for line in block.splitlines()]
    for index, line in enumerate(lines):
        command = normalize_command_line(line)
        if command is not None:
            return command, index
    return None, None


def extract_claims(markdown: str) -> list[ExtractedClaim]:
    """Extract pytest claims from a report markdown.

    A claim is a (command, observed-summary) pair. The summary may live in the
    SAME fenced block as the command, OR in a nearby following block (up to
    ``_CROSS_BLOCK_LOOKAHEAD`` blocks ahead, stopping if any intervening block
    introduces its own pytest command). This handles the split command/result
    convention used by bridge post-implementation reports such as
    ``bridge/gtkb-proposal-standards-test-claim-rerun-verifier-005.md`` per
    Codex NO-GO ``-006`` FINDING-P1-001.

    When a command block has no associated summary (in-block or in lookahead),
    the claim is preserved with ``claimed_summary=None`` and empty
    ``claimed_counts`` so downstream logic can surface the parser-miss state
    instead of silently dropping the claim per FINDING-P2-002.
    """

    blocks = list(enumerate(extract_code_blocks(markdown), start=1))
    claims: list[ExtractedClaim] = []
    for position, (block_index, block) in enumerate(blocks):
        command_line, command_index = _first_command_in_block(block)
        if command_line is None:
            continue
        # Per Codex NO-GO -009 FINDING-P1-001: pytest-shape validation MUST
        # happen before any claim is added. The verifier's contract is
        # pytest-claim re-run; non-pytest commands whose output happens to
        # contain pytest-like summary text (e.g. a "9 passed" string in the
        # output of `python scripts/bridge_report_test_claim_rerun_verifier.py`)
        # must NOT be paired into ERROR claims. Apply the guard once, here,
        # before in-block and cross-block summary search.
        _, command_error = pytest_args_for_command(command_line)
        if command_error is not None:
            continue
        # In-block summary takes precedence.
        lines = [line.rstrip() for line in block.splitlines()]
        summary_line = find_summary_line(lines, after_index=command_index)
        if summary_line is None:
            # Cross-block lookahead: scan up to N forward blocks for a summary,
            # stopping if any intervening block has its own command (we don't
            # want to pair commandA with summaryB-belonging-to-commandB).
            for next_position in range(position + 1, min(position + 1 + _CROSS_BLOCK_LOOKAHEAD, len(blocks))):
                _, next_block = blocks[next_position]
                next_lines = [line.rstrip() for line in next_block.splitlines()]
                if any(normalize_command_line(line) is not None for line in next_lines):
                    break
                next_summary = find_summary_line(next_lines)
                if next_summary is not None:
                    summary_line = next_summary
                    break
        if summary_line is None:
            claims.append(
                ExtractedClaim(
                    claim_block_index=block_index,
                    command=command_line,
                    claimed_summary=None,
                    claimed_counts={},
                )
            )
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


# uv-run wrapper unwrapping (Codex NO-GO -011 FINDING-P1-001). The
# project-approved cross-shell reproducible invocation surface is
# ``uv run --with pytest [--with pytest-timeout] python -m pytest ...``. The
# verifier never executes the wrapper itself — it extracts the inner pytest
# args and re-runs pytest via ``sys.executable`` (see run_pytest_claim) — so
# unwrapping the wrapper is what lets the verifier parse and safely re-run the
# same commands the bridge-report reproducibility rule now mandates.
_UV_RUN_VALUE_OPTS: Final[frozenset[str]] = frozenset(
    {
        "--with",
        "--with-requirements",
        "--with-editable",
        "--python",
        "-p",
        "--directory",
        "--project",
        "--index",
        "--default-index",
        "--index-url",
        "--extra-index-url",
        "--cache-dir",
        "--color",
    }
)


def _strip_uv_run_prefix(parts: list[str]) -> list[str]:
    """Strip a leading ``uv run [options] [--with PKG]...`` wrapper.

    Returns the inner command tokens (e.g. ``["python", "-m", "pytest", ...]``)
    when ``parts`` begins with ``uv run``; returns ``parts`` unchanged
    otherwise. Only value-consuming options on a known allowlist consume a
    following token; bare flags consume one token; the first non-option token
    is the start of the inner command. The inner command is still subject to
    the python/pytest validation in ``pytest_args_for_command``, so an
    unexpected wrapped executable is rejected downstream rather than executed.
    """
    if len(parts) < 2:
        return parts
    if Path(parts[0]).name.lower() not in {"uv", "uv.exe"} or parts[1] != "run":
        return parts
    index = 2
    total = len(parts)
    while index < total:
        token = parts[index]
        if not token.startswith("-"):
            break  # start of the inner command
        if "=" in token:
            index += 1
            continue
        if token in _UV_RUN_VALUE_OPTS:
            index += 2  # option + its value
            continue
        index += 1  # bare flag (e.g. --refresh, --no-project, --quiet)
    inner = parts[index:]
    return inner if inner else parts


def pytest_args_for_command(command: str) -> tuple[list[str] | None, str | None]:
    if UNSAFE_SHELL_RE.search(command):
        return None, "command contains shell metacharacters or chaining"
    try:
        parts = shlex.split(command)
    except ValueError as exc:
        return None, f"command cannot be parsed safely: {exc}"
    if not parts:
        return None, "empty command"

    parts = _strip_uv_run_prefix(parts)
    if not parts:
        return None, "empty command after uv-run unwrap"

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


def _extract_option_value(arg: str, next_arg: str | None) -> tuple[str | None, bool]:
    """Return (value, value_consumed_next_arg) for an option-shaped arg.

    Handles both ``--opt=value`` (single arg) and ``--opt value`` (two args).
    Returns ``(None, False)`` when no value is available.
    """

    if "=" in arg:
        return arg.split("=", 1)[1], False
    if next_arg is not None and not next_arg.startswith("-"):
        return next_arg, True
    return None, False


def validate_pytest_args(project_root: Path, pytest_args: list[str]) -> str | None:
    skip_next = False
    for index, arg in enumerate(pytest_args):
        if skip_next:
            skip_next = False
            continue
        option_name = arg.split("=", 1)[0]
        if option_name in PATH_OPTIONS:
            # Per Codex NO-GO -009 FINDING-P1-001 recommendation: allow safe
            # in-root path-valued pytest options by validating the resolved
            # path against the project root. The previous categorical
            # rejection blocked legitimate in-root ``--basetemp=<in-root>``
            # forms used by bridge post-implementation reports for test
            # isolation. Out-of-root values remain rejected.
            next_arg = pytest_args[index + 1] if index + 1 < len(pytest_args) else None
            value, consumed_next = _extract_option_value(arg, next_arg)
            if value is None:
                return f"pytest option {option_name} requires a path value"
            if not _path_within_root(project_root, value):
                return f"pytest option {option_name} value escapes project root: {value}"
            if consumed_next:
                skip_next = True
            continue
        if option_name in VALUE_OPTIONS and "=" not in arg:
            skip_next = True
            continue
        if arg.startswith("-"):
            continue
        if PATH_LIKE_RE.search(arg) and not _path_within_root(project_root, arg):
            return f"pytest target escapes project root: {arg}"
    return None


def run_pytest_claim(project_root: Path, claim: ExtractedClaim, timeout_seconds: int) -> ClaimResult:
    if claim.claimed_summary is None:
        # Per Codex NO-GO -006 FINDING-P2-002: a pytest command without an
        # associated observed-result block is an evidence gap, not a clean
        # absence; surface as ERROR so the strict-mode gate does not pass.
        return ClaimResult(
            claim_block_index=claim.claim_block_index,
            command=claim.command,
            claimed_summary=None,
            observed_summary=None,
            status="ERROR",
            returncode=None,
            reason="pytest command present, no associated observed-result block found",
            claimed_counts={},
            observed_counts={},
        )
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
                claimed=str(raw.get("claimed_summary") or "").replace("|", "\\|"),
                observed=str(raw.get("observed_summary") or "").replace("|", "\\|"),
                reason=str(raw["reason"]).replace("|", "\\|"),
            )
        )
    return "\n".join(lines) + "\n"


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bridge-id", required=True, help="Bridge document name / versioned bridge-thread slug.")
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
