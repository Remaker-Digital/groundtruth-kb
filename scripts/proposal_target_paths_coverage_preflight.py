#!/usr/bin/env python3
"""Advisory proposal target_paths coverage preflight.

This read-only check compares paths implied by a proposal's verification and
generator commands against the proposal's declared ``target_paths`` allowlist.
It catches under-scoped proposals before implementation-start authorization
turns the omission into avoidable bridge churn.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from implementation_authorization import (  # noqa: E402
    AuthorizationError,
    BridgeEntry,
    bridge_entry,
    extract_target_paths,
    normalize_relative_path,
    path_authorized,
    project_root_from_arg,
)

EXIT_OK = 0
EXIT_STRICT_GAPS = 5

GENERATOR_OUTPUT_MAP: dict[str, list[str]] = {
    "scripts/generate_codex_skill_adapters.py": [
        ".codex/skills/**",
        ".codex/skills/MANIFEST.json",
        "config/agent-control/harness-capability-registry.toml",
    ],
}

_PRIME_PROPOSAL_STATUSES = frozenset({"NEW", "REVISED"})
_PY_PATH_RE = re.compile(
    r"(?P<path>(?:(?:\.\.?[/\\][^\s'\"`;]+?\.py)|"
    r"(?:(?:scripts|platform_tests|tests|groundtruth-kb[/\\]tests)[/\\][^\s'\"`;]+?\.py)))"
)
_COMMAND_START_RE = re.compile(
    r"^(?:\.venv[/\\]Scripts[/\\]python(?:\.exe)?|python(?:\.exe)?|py(?:\.exe)?|pytest|uv|poetry)\b"
)


@dataclass(frozen=True)
class PathIssue:
    path: str
    error: str

    def to_dict(self) -> dict[str, str]:
        return {"path": self.path, "error": self.error}


def _strip_prompt(line: str) -> str:
    stripped = line.strip()
    for prefix in (">", "$", "PS>"):
        if stripped.startswith(prefix):
            stripped = stripped[len(prefix) :].strip()
    return stripped


def _command_lines(markdown: str) -> list[str]:
    """Return command-like lines from fenced/indented blocks and command starts."""
    lines: list[str] = []
    in_fence = False
    for raw_line in markdown.splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        candidate = _strip_prompt(raw_line)
        if not candidate:
            continue
        if in_fence or _COMMAND_START_RE.search(candidate):
            lines.append(candidate)
    return lines


def _clean_path_token(value: str) -> str:
    return value.strip().strip("`").rstrip(".,;:)]}").replace("\\", "/")


def _is_pytest_command(command: str) -> bool:
    normalized = command.replace("\\", "/")
    return bool(re.search(r"(^|\s)pytest(\s|$)", normalized) or re.search(r"(^|\s)-m\s+pytest(\s|$)", normalized))


def extract_verification_paths(markdown: str) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    for command in _command_lines(markdown):
        if not _is_pytest_command(command):
            continue
        for match in _PY_PATH_RE.finditer(command):
            path = _clean_path_token(match.group("path"))
            if path and path not in seen:
                seen.add(path)
                found.append(path)
    return found


def extract_generator_paths(markdown: str) -> list[str]:
    command_text = "\n".join(_command_lines(markdown)).replace("\\", "/")
    found: list[str] = []
    seen: set[str] = set()
    for generator, outputs in GENERATOR_OUTPUT_MAP.items():
        generator_name = Path(generator).name
        if generator not in command_text and generator_name not in command_text:
            continue
        for output in outputs:
            if output not in seen:
                seen.add(output)
                found.append(output)
    return found


def _normalize_implied_paths(project_root: Path, paths: list[str]) -> tuple[list[str], list[PathIssue]]:
    normalized: list[str] = []
    issues: list[PathIssue] = []
    seen: set[str] = set()
    for path in paths:
        try:
            normalized_path = normalize_relative_path(project_root, path)
        except (AuthorizationError, ValueError, OSError) as exc:
            issues.append(PathIssue(path=path.replace("\\", "/"), error=str(exc)))
            continue
        if normalized_path not in seen:
            seen.add(normalized_path)
            normalized.append(normalized_path)
    return normalized, issues


def _uncovered(paths: list[str], target_paths: list[str]) -> list[str]:
    packet = {"target_path_globs": target_paths}
    return [path for path in paths if not path_authorized(packet, path)]


def _candidate_proposal_versions(entry: BridgeEntry) -> list[tuple[str, str]]:
    """Return versions that can contain the approved implementation proposal.

    Bridge post-implementation reports are Prime-authored NEW/REVISED files too.
    Once a GO exists, every newer NEW/REVISED belongs to the verification cycle,
    so proposal resolution must inspect the versions older than the latest GO.
    """
    latest_go_index = next((index for index, (status, _) in enumerate(entry.versions) if status == "GO"), None)
    if latest_go_index is None:
        return entry.versions
    return entry.versions[latest_go_index + 1 :]


def _resolve_content_file(project_root: Path, bridge_id: str | None, content_file: str | None) -> str:
    if content_file:
        return normalize_relative_path(project_root, content_file)
    if not bridge_id:
        raise AuthorizationError("either --bridge-id or --content-file is required")
    entry = bridge_entry(project_root, bridge_id)
    for status, rel_path in _candidate_proposal_versions(entry):
        if status in _PRIME_PROPOSAL_STATUSES:
            return rel_path
    raise AuthorizationError(f"No NEW/REVISED proposal file found for bridge {bridge_id}")


def run_preflight(
    project_root: Path,
    *,
    bridge_id: str | None = None,
    content_file: str | None = None,
    strict: bool = False,
) -> tuple[dict[str, Any], int]:
    """Run the advisory coverage check."""
    result: dict[str, Any] = {
        "bridge_id": bridge_id,
        "content_file": None,
        "target_paths": [],
        "implied_verification_paths": [],
        "implied_generator_paths": [],
        "uncovered_verification_paths": [],
        "uncovered_generator_paths": [],
        "out_of_root": [],
        "strict": strict,
        "verdict": "clean",
        "message": "",
    }

    try:
        rel_content_file = _resolve_content_file(project_root, bridge_id, content_file)
        result["content_file"] = rel_content_file
        markdown = (project_root / rel_content_file).read_text(encoding="utf-8")
        target_paths = extract_target_paths(markdown)
    except (AuthorizationError, OSError) as exc:
        result["verdict"] = "error"
        result["message"] = str(exc)
        return result, EXIT_STRICT_GAPS if strict else EXIT_OK

    verification_raw = extract_verification_paths(markdown)
    generator_raw = extract_generator_paths(markdown)
    verification_paths, verification_issues = _normalize_implied_paths(project_root, verification_raw)
    generator_paths, generator_issues = _normalize_implied_paths(project_root, generator_raw)

    out_of_root = [issue.to_dict() for issue in [*verification_issues, *generator_issues]]
    uncovered_verification = _uncovered(verification_paths, target_paths)
    uncovered_generator = _uncovered(generator_paths, target_paths)

    has_gaps = bool(uncovered_verification or uncovered_generator or out_of_root)
    result.update(
        {
            "target_paths": target_paths,
            "implied_verification_paths": verification_paths,
            "implied_generator_paths": generator_paths,
            "uncovered_verification_paths": uncovered_verification,
            "uncovered_generator_paths": uncovered_generator,
            "out_of_root": out_of_root,
            "verdict": "gaps" if has_gaps else "clean",
            "message": "target_paths coverage gaps found" if has_gaps else "all implied paths covered",
        }
    )
    if strict and has_gaps:
        return result, EXIT_STRICT_GAPS
    return result, EXIT_OK


def format_markdown(result: dict[str, Any]) -> str:
    lines = [
        "## Target-Paths Coverage",
        "",
        f"- bridge_id: `{result.get('bridge_id') or '(content-file)'}`",
        f"- content_file: `{result.get('content_file') or '(unresolved)'}`",
        f"- verdict: `{result['verdict']}`",
        f"- strict: `{str(result['strict']).lower()}`",
        f"- target_paths: `{json.dumps(result['target_paths'])}`",
        f"- implied_verification_paths: `{json.dumps(result['implied_verification_paths'])}`",
        f"- implied_generator_paths: `{json.dumps(result['implied_generator_paths'])}`",
        f"- uncovered_verification_paths: `{json.dumps(result['uncovered_verification_paths'])}`",
        f"- uncovered_generator_paths: `{json.dumps(result['uncovered_generator_paths'])}`",
        f"- out_of_root: `{json.dumps(result['out_of_root'])}`",
        f"- message: `{result['message']}`",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--bridge-id", default=None, help="Bridge document id (slug)")
    source.add_argument("--content-file", default=None, help="Proposal markdown file to inspect")
    parser.add_argument("--project-root", default=None, help="GT-KB project root")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of markdown")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when coverage gaps are found")
    args = parser.parse_args(argv)

    project_root = project_root_from_arg(args.project_root)
    result, exit_code = run_preflight(
        project_root,
        bridge_id=args.bridge_id,
        content_file=args.content_file,
        strict=args.strict,
    )
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(format_markdown(result))
    return exit_code if args.strict else EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
