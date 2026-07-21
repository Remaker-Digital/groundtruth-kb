#!/usr/bin/env python3
"""Protected narrative-artifact writer for the bridge skill.

This helper is a Layer-C universal-floor evidence path. It validates a
narrative-artifact approval packet, writes the protected file with LF
normalization, stages the target path, then runs
``scripts/check_narrative_artifact_evidence.py`` against the staged blob. It
does not trigger or emulate any harness PreToolUse interception.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[4]
CHECKER_PATH = PROJECT_ROOT / "scripts" / "check_narrative_artifact_evidence.py"


class ProtectedWriteError(RuntimeError):
    """Raised when the helper cannot complete a governed protected write."""


class EvidenceCheckerError(ProtectedWriteError):
    """Raised when the universal-floor checker rejects the staged write."""


def _load_checker_module() -> Any:
    spec = importlib.util.spec_from_file_location("check_narrative_artifact_evidence_for_protected_write", CHECKER_PATH)
    if spec is None or spec.loader is None:
        raise ProtectedWriteError(f"Could not load evidence checker at {CHECKER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _normalize_lf(content: str) -> str:
    return content.replace("\r\n", "\n").replace("\r", "\n")


def _read_content(*, content_file: Path | None, content_stdin: bool) -> str:
    if content_file is not None:
        try:
            return _normalize_lf(content_file.read_bytes().decode("utf-8"))
        except OSError as exc:
            raise ProtectedWriteError(f"content file could not be read: {exc}") from exc
        except UnicodeDecodeError as exc:
            raise ProtectedWriteError(f"content file must be UTF-8 text: {exc}") from exc
    if content_stdin:
        return _normalize_lf(sys.stdin.read())
    raise ProtectedWriteError("must provide --content-file or --content-stdin")


def _normalize_target(target: str, project_root: Path) -> tuple[str, Path]:
    root = project_root.resolve()
    candidate = Path(target)
    resolved = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
    try:
        rel_path = resolved.relative_to(root).as_posix()
    except ValueError as exc:
        raise ProtectedWriteError(f"target path is outside project root: {target}") from exc
    if not rel_path or rel_path == ".":
        raise ProtectedWriteError("target path must name a file under the project root")
    return rel_path, resolved


def _load_packet(packet_path: Path, project_root: Path) -> dict[str, Any]:
    path = packet_path if packet_path.is_absolute() else project_root / packet_path
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ProtectedWriteError(f"approval packet could not be read: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ProtectedWriteError(f"approval packet is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ProtectedWriteError("approval packet root must be a JSON object")
    return data


def _validate_target_is_protected(checker: Any, rel_path: str, project_root: Path) -> None:
    config = checker._load_config(project_root)
    if not checker._is_protected(rel_path, config):
        raise ProtectedWriteError(
            f"target path {rel_path!r} is not a protected narrative artifact per "
            "config/governance/narrative-artifact-approval.toml"
        )


def _validate_packet(checker: Any, packet: dict[str, Any], rel_path: str, content: str) -> str:
    proposed_sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
    validation_error = checker._validate_packet(packet, rel_path, proposed_sha256)
    if validation_error:
        raise ProtectedWriteError(
            "approval packet failed validation per GOV-ARTIFACT-APPROVAL-001 / "
            f"DCL-ARTIFACT-APPROVAL-HOOK-001: {validation_error}"
        )
    return proposed_sha256


def _write_lf(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
    except OSError as exc:
        raise ProtectedWriteError(f"target file could not be written: {exc}") from exc


def _stage_target(project_root: Path, rel_path: str) -> None:
    result = subprocess.run(
        ["git", "add", "--", rel_path],
        cwd=project_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise ProtectedWriteError(f"could not stage target path {rel_path!r}: {detail}")


def _checker_human_output(checker: Any, result: dict[str, Any]) -> str:
    formatter = getattr(checker, "_format_human", None)
    if callable(formatter):
        return str(formatter(result))
    return json.dumps(result, indent=2, sort_keys=True)


def _run_evidence_checker(checker: Any, project_root: Path, rel_path: str) -> dict[str, Any]:
    result = checker.evaluate(project_root, paths=[rel_path])
    if result.get("status") != "pass":
        raise EvidenceCheckerError(_checker_human_output(checker, result))
    return result


def write_protected_file(
    *,
    target: str,
    content: str,
    packet_path: Path,
    project_root: Path = PROJECT_ROOT,
) -> dict[str, Any]:
    """Write a protected narrative artifact and return the checker result."""
    root = project_root.resolve()
    checker = _load_checker_module()
    rel_path, target_path = _normalize_target(target, root)
    _validate_target_is_protected(checker, rel_path, root)
    packet = _load_packet(packet_path, root)
    _validate_packet(checker, packet, rel_path, content)
    _write_lf(target_path, content)
    _stage_target(root, rel_path)
    return _run_evidence_checker(checker, root, rel_path)


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, help="Protected target path relative to the project root.")
    content_group = parser.add_mutually_exclusive_group(required=True)
    content_group.add_argument("--content-file", type=Path, help="UTF-8 file containing the proposed full content.")
    content_group.add_argument("--content-stdin", action="store_true", help="Read proposed full content from stdin.")
    parser.add_argument("--packet", required=True, type=Path, help="Narrative-artifact approval packet JSON.")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--json", action="store_true", help="Emit the evidence-checker result as JSON on success.")
    args = parser.parse_args(argv)

    try:
        content = _read_content(content_file=args.content_file, content_stdin=args.content_stdin)
        result = write_protected_file(
            target=args.target,
            content=content,
            packet_path=args.packet,
            project_root=args.project_root,
        )
    except ProtectedWriteError as exc:
        sys.stderr.write(f"{exc}\n")
        return 1

    if args.json:
        sys.stdout.write(json.dumps(result, indent=2, sort_keys=True))
        sys.stdout.write("\n")
    else:
        checker = _load_checker_module()
        sys.stdout.write(_checker_human_output(checker, result))
        sys.stdout.write("\n")
    return 0


__all__ = [
    "EvidenceCheckerError",
    "ProtectedWriteError",
    "write_protected_file",
]


if __name__ == "__main__":
    raise SystemExit(_main())
