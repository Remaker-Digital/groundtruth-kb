#!/usr/bin/env python3
"""Check every harness registration against the invocation contract (c123; batch design WP2 2.1 to 2.3, G1).

A registration names no role and uses only the contract's placeholders (``groundtruth_kb.harness_invocation``). For a
GT-KB launcher the template also renders and parses with that launcher's own argument parser; its ``--model``, or the
launcher's default when it has one, is a routing.toml ``[models.<key>]`` row of the launcher's provider; and the API
launchers (F, D and H), which bind their context themselves, carry ``--init {{INIT_LINE}}``, ``--bridge-document
{{DOCUMENT}}`` and ``--bridge-version {{VERSION}}``. The vendor command lines (codex, claude, antigravity and the
DeepSeek SDK's manual surface) are checked for role and placeholder findings only: their models resolve in the vendor's
own CLI and are checked live. A headless surface that runs the Claude Code CLI (host B) also carries the dispatched
permission posture (c123; batch design WP2 2.4, owner decisions B1 and B5): the rule is
``verify_claude_dispatch.permission_posture_problems``, and a row that lacks it has the ``permission_posture_unmet``
finding. The rule follows the program the argv runs, not ``harness_type``: H registers as ``claude`` but runs a GT-KB
launcher.

It reads every row of every status from the native authority (GET only), or rows from a JSON file (``--rows``: a list
of records, or an object whose ``records`` is one), and prints the findings as JSON. Exit 0 when no row has a finding,
1 when one does, 2 when the rows cannot be read. Nothing is written.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
import tomllib
from collections.abc import Callable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from groundtruth_kb.harness_invocation import InvocationError, render, sample_values, surface_findings  # noqa: E402

ROUTING_RELATIVE_PATH = Path(".harness-baseline-configuration") / "routing.toml"
FINDING_TEMPLATE_PARSE = "template_does_not_parse"
FINDING_MODEL_ROUTE = "model_route_unresolved"
FINDING_BRIDGE_TARGET = "bridge_target_placeholders_missing"
FINDING_INIT_LINE = "init_placeholder_missing"
FINDING_PERMISSION_POSTURE = "permission_posture_unmet"
# c123 (batch design WP2 2.4): the program names of the Claude Code CLI a dispatched headless surface may run.
CLAUDE_CLI_NAMES = frozenset({"claude", "claude.exe", "claude.cmd"})


def _openrouter_parser() -> argparse.ArgumentParser:
    from scripts import openrouter_harness

    return openrouter_harness.build_arg_parser()


def _ollama_parser() -> argparse.ArgumentParser:
    from scripts import ollama_harness

    return ollama_harness.build_arg_parser()


def _alibaba_parser() -> argparse.ArgumentParser:
    from scripts import alibaba_cloud_studio_harness

    return alibaba_cloud_studio_harness.build_arg_parser()


def _goose_parser() -> argparse.ArgumentParser:
    with _scripts_on_path():
        from scripts import goose_harness

    return goose_harness.build_arg_parser()


def _cursor_parser() -> argparse.ArgumentParser:
    from groundtruth_kb import cursor_harness

    return cursor_harness.build_arg_parser()


@contextlib.contextmanager
def _scripts_on_path() -> Iterator[None]:
    """goose_harness imports its sibling modules by their bare names; restore sys.path afterwards."""
    saved = list(sys.path)
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    try:
        yield
    finally:
        sys.path[:] = saved


@dataclass(frozen=True)
class Launcher:
    """A GT-KB launcher: its parser, its routing provider (None when the host picks the model) and its rules."""

    parser: Callable[[], argparse.ArgumentParser]
    provider: str | None
    binds_itself: bool
    model_required: bool


LAUNCHERS: dict[str, Launcher] = {
    "scripts/openrouter_harness.py": Launcher(_openrouter_parser, "openrouter", True, False),
    "scripts/ollama_harness.py": Launcher(_ollama_parser, "ollama", True, False),
    "scripts/alibaba_cloud_studio_harness.py": Launcher(_alibaba_parser, "alibaba-cloud-studio", True, False),
    # G passes no model to Goose without --model, so Goose's own unrecorded default would apply: G names one.
    "scripts/goose_harness.py": Launcher(_goose_parser, "goose", False, True),
    "scripts/cursor_harness.py": Launcher(_cursor_parser, None, False, False),
}


def _surfaces_with_argv(record: Mapping[str, Any]) -> list[tuple[str, list[str]]]:
    surfaces = record.get("invocation_surfaces")
    found: list[tuple[str, list[str]]] = []
    if not isinstance(surfaces, Mapping):
        return found
    for name, surface in surfaces.items():
        argv = surface.get("argv") if isinstance(surface, Mapping) else None
        if isinstance(argv, list) and argv and all(isinstance(part, str) for part in argv):
            found.append((str(name), list(argv)))
    return found


def _launcher_position(argv: Sequence[str]) -> tuple[int, Launcher] | None:
    for index, part in enumerate(argv):
        launcher = LAUNCHERS.get(part.replace("\\", "/"))
        if launcher is not None:
            return index, launcher
    return None


def _follows(argv: Sequence[str], flag: str, value: str) -> bool:
    return any(argv[index] == flag and argv[index + 1] == value for index in range(len(argv) - 1))


def _runs_claude_cli(argv: Sequence[str]) -> bool:
    return bool(argv) and argv[0].replace("\\", "/").rsplit("/", 1)[-1].lower() in CLAUDE_CLI_NAMES


def _posture_problems(argv: Sequence[str]) -> list[str]:
    """The Claude verifier's posture rule, so the operator's two checks never disagree (c123; batch design WP2 2.4)."""
    from scripts.verify_claude_dispatch import permission_posture_problems

    return permission_posture_problems(argv)


def _routing(project_root: Path) -> dict[str, Any]:
    try:
        return tomllib.loads((project_root / ROUTING_RELATIVE_PATH).read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return {}


def _last_value(arguments: Sequence[str], flag: str) -> str | None:
    """The value the last ``flag VALUE`` or ``flag=VALUE`` gives, as argparse would keep it."""
    value: str | None = None
    for index, part in enumerate(arguments):
        if part == flag and index + 1 < len(arguments):
            value = arguments[index + 1]
        elif part.startswith(flag + "="):
            value = part[len(flag) + 1 :]
    return value


def _model_finding(launcher: Launcher, arguments: Sequence[str], routing: Mapping[str, Any]) -> str | None:
    if launcher.provider is None:
        return None
    key = _last_value(arguments, "--model")
    if not key:
        if launcher.model_required:
            return "the template names no --model"
        provider_routing = routing.get("routing", {}).get(launcher.provider, {})
        key = provider_routing.get("default_model") if isinstance(provider_routing, Mapping) else None
        if not key:
            return f"no --model and no [routing.{launcher.provider}] default_model"
    row = routing.get("models", {}).get(key) if isinstance(routing.get("models"), Mapping) else None
    if not isinstance(row, Mapping) or row.get("provider") != launcher.provider:
        return f"{key!r} is not a routing.toml [models] row of provider {launcher.provider!r}"
    return None


def row_findings(record: Mapping[str, Any], project_root: Path, routing: Mapping[str, Any]) -> list[dict[str, str]]:
    """Every finding of one registration row, each with its code, place and detail."""
    findings = [
        {"code": finding.code, "path": finding.path, "detail": finding.value}
        for finding in surface_findings(record.get("invocation_surfaces"))
    ]
    for name, argv in _surfaces_with_argv(record):
        if name == "headless" and _runs_claude_cli(argv):
            problems = _posture_problems(argv)
            if problems:
                findings.append(
                    {"code": FINDING_PERMISSION_POSTURE, "path": f"{name}.argv", "detail": "; ".join(problems)}
                )
        located = _launcher_position(argv)
        if located is None:
            continue
        index, launcher = located
        where = f"{name}.argv"
        if launcher.binds_itself:
            if not _follows(argv, "--init", "{{INIT_LINE}}"):
                findings.append({"code": FINDING_INIT_LINE, "path": where, "detail": "--init {{INIT_LINE}}"})
            if not (
                _follows(argv, "--bridge-document", "{{DOCUMENT}}")
                and _follows(argv, "--bridge-version", "{{VERSION}}")
            ):
                findings.append(
                    {
                        "code": FINDING_BRIDGE_TARGET,
                        "path": where,
                        "detail": "--bridge-document {{DOCUMENT}} --bridge-version {{VERSION}}",
                    }
                )
        try:
            arguments = render(argv[index + 1 :], sample_values(str(project_root)))
        except InvocationError as exc:
            findings.append({"code": FINDING_TEMPLATE_PARSE, "path": where, "detail": str(exc)})
            continue
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                launcher.parser().parse_args(arguments)
        except SystemExit:
            detail = "the launcher's own parser refuses the rendered arguments"
            findings.append({"code": FINDING_TEMPLATE_PARSE, "path": where, "detail": detail})
        problem = _model_finding(launcher, arguments, routing)
        if problem is not None:
            findings.append({"code": FINDING_MODEL_ROUTE, "path": where, "detail": problem})
    return findings


def evaluate(records: Sequence[Mapping[str, Any]], project_root: Path) -> dict[str, Any]:
    """The findings of every row; ``passed`` only when no row has one."""
    routing = _routing(project_root)
    rows = []
    for record in sorted(records, key=lambda row: str(row.get("id"))):
        findings = row_findings(record, project_root, routing)
        rows.append({"id": record.get("id"), "status": record.get("status"), "findings": findings})
    return {"passed": all(not row["findings"] for row in rows), "rows": rows, "authority_writes": 0}


def _authority_records(project_root: Path) -> list[dict[str, Any]]:
    from groundtruth_kb.authority_client import AuthorityClient, page_records
    from groundtruth_kb.config import GTConfig

    config = GTConfig.load(project_root / "groundtruth.toml", discover=False)
    if not config.authority_url:
        raise ValueError("native_authority_not_configured")
    return page_records(AuthorityClient(config.authority_url, timeout=10), "/v1/harnesses")


def _file_records(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    records = payload.get("records") if isinstance(payload, dict) else payload
    if isinstance(records, dict):
        records = list(records.values())
    if not isinstance(records, list) or not all(isinstance(row, dict) for row in records):
        raise ValueError("the rows file holds no list of records")
    return records


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--rows", type=Path, help="Read the rows from this JSON file instead of the native authority.")
    args = parser.parse_args(argv)
    project_root = args.project_root.resolve()
    try:
        records = _file_records(args.rows) if args.rows else _authority_records(project_root)
    except Exception as exc:  # noqa: BLE001 - every read failure is a refusal with exit 2, never a pass
        print(json.dumps({"passed": False, "error": f"{type(exc).__name__}: {exc}"}))
        return 2
    result = evaluate(records, project_root)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
