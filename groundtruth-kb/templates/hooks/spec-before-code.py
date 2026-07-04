#!/usr/bin/env python3
"""
PreToolUse hook: spec-before-code advisory.

Checks if the file being written/edited has a specification covering it
via the source_paths field or, for platform_tests/ files, explicit bridge
evidence. Emits an advisory if no spec covers the path.

Hook type: PreToolUse (tools: Write, Edit, NotebookEdit)

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SOURCE_EXTENSIONS = {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java", ".cs"}
WRITE_TOOLS = {"Write", "Edit", "NotebookEdit"}
DB_FILENAME = "groundtruth.db"
BRIDGE_STATUS_TOKENS = {"NEW", "REVISED", "GO", "NO-GO", "VERIFIED", "ADVISORY", "DEFERRED", "WITHDRAWN"}
BRIDGE_VERSIONED_FILE_RE = re.compile(r"^.+-\d{3,}\.md$")
PATH_TOKEN_BOUNDARY_RE = r"A-Za-z0-9_./:\\-"


def _find_db(cwd: str) -> Path | None:
    """Walk up from cwd to find groundtruth.db."""
    p = Path(cwd)
    for parent in [p, *p.parents]:
        candidate = parent / DB_FILENAME
        if candidate.exists():
            return candidate
    return None


def _get_target_path(tool_name: str, tool_input: dict) -> str | None:
    if tool_name == "Write":
        return tool_input.get("file_path")
    if tool_name == "Edit":
        return tool_input.get("file_path")
    if tool_name == "NotebookEdit":
        return tool_input.get("notebook_path")
    return None


def _is_source_file(path: str) -> bool:
    return Path(path).suffix in SOURCE_EXTENSIONS


def _normalize_path(path: str) -> str:
    normalized = path.replace("\\", "/").strip()
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def _is_platform_test_path(path: str) -> bool:
    normalized = "/" + _normalize_path(path).lstrip("/")
    return "/platform_tests/" in normalized


def _target_path_candidates(target_path: str) -> set[str]:
    normalized = _normalize_path(target_path)
    candidates = {normalized}
    marker = "/platform_tests/"
    marker_index = normalized.rfind(marker)
    if marker_index >= 0:
        candidates.add(normalized[marker_index + 1 :])
    elif normalized.startswith("platform_tests/"):
        candidates.add(normalized)
    return {candidate for candidate in candidates if candidate}


def _contains_path_token(text: str, path: str) -> bool:
    pattern = rf"(?<![{PATH_TOKEN_BOUNDARY_RE}]){re.escape(path)}(?![{PATH_TOKEN_BOUNDARY_RE}])"
    return re.search(pattern, text) is not None


def _is_status_bearing_bridge_file(path: Path, content: str) -> bool:
    if not BRIDGE_VERSIONED_FILE_RE.match(path.name):
        return False
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        return stripped in BRIDGE_STATUS_TOKENS
    return False


def _find_bridge_dir(cwd: str, db_path: Path) -> Path | None:
    starts = [Path(cwd), db_path.parent]
    seen: set[Path] = set()
    for start in starts:
        try:
            candidates = [start, *start.parents]
        except RuntimeError:
            candidates = [start]
        for parent in candidates:
            if parent in seen:
                continue
            seen.add(parent)
            bridge_dir = parent / "bridge"
            if bridge_dir.is_dir():
                return bridge_dir
    return None


def _bridge_evidence_covers_platform_test(cwd: str, db_path: Path, target_path: str) -> bool:
    if not _is_platform_test_path(target_path):
        return False

    bridge_dir = _find_bridge_dir(cwd, db_path)
    if bridge_dir is None:
        return False

    candidates = _target_path_candidates(target_path)
    for bridge_file in sorted(bridge_dir.glob("*.md")):
        try:
            content = bridge_file.read_text(encoding="utf-8")
        except OSError:
            continue
        normalized_content = content.replace("\\", "/")
        if not _is_status_bearing_bridge_file(bridge_file, normalized_content):
            continue
        if any(_contains_path_token(normalized_content, candidate) for candidate in candidates):
            return True
    return False


def _query_source_paths(db_path: Path, target_path: str) -> tuple[bool, bool]:
    """
    Returns (has_source_paths_specs, any_covers_target).
    has_source_paths_specs: True if any spec has a non-null source_paths
    any_covers_target: True if any spec's source_paths includes target_path
    """
    try:
        import sqlite3

        conn = sqlite3.connect(str(db_path))
        try:
            # Check if source_paths column exists
            cols = {row[1] for row in conn.execute("PRAGMA table_info(specifications)")}
            if "source_paths" not in cols:
                return False, False

            rows = conn.execute("SELECT source_paths FROM specifications WHERE source_paths IS NOT NULL").fetchall()
            if not rows:
                return False, False

            # Normalize target path for comparison
            target_normalized = target_path.replace("\\", "/")

            for (source_paths_json,) in rows:
                try:
                    paths = json.loads(source_paths_json) if isinstance(source_paths_json, str) else []
                    for sp in paths:
                        sp_norm = sp.replace("\\", "/")
                        if target_normalized.endswith(sp_norm) or sp_norm == target_normalized:
                            return True, True
                except (json.JSONDecodeError, TypeError):
                    continue
            return True, False
        finally:
            conn.close()
    except Exception:
        return False, False


def main() -> None:
    try:
        from groundtruth_kb.governance.output import emit_additional_context, emit_pass
    except ImportError:

        def emit_additional_context(event: str, text: str) -> None:  # type: ignore[misc]
            print(json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}))

        def emit_pass() -> None:  # type: ignore[misc]
            print("{}")

    if "--self-test" in sys.argv:
        emit_additional_context(
            "PreToolUse",
            "[Governance] Spec-before-code hook active. "
            "Ensure source files have a specification with matching source_paths.",
        )
        sys.exit(0)

    try:
        payload = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, OSError):
        emit_pass()
        sys.exit(0)

    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {})
    cwd = payload.get("cwd", ".")

    if tool_name not in WRITE_TOOLS:
        emit_pass()
        sys.exit(0)

    target_path = _get_target_path(tool_name, tool_input)
    if not target_path or not _is_source_file(target_path):
        emit_pass()
        sys.exit(0)

    db_path = _find_db(cwd)
    if db_path is None:
        emit_additional_context(
            "PreToolUse",
            f"[Governance] No groundtruth.db found for {target_path}. "
            "Initialize the KB with `gt project init` to enable spec-before-code checks.",
        )
        sys.exit(0)

    has_source_paths, covers_target = _query_source_paths(db_path, target_path)
    bridge_covers_target = _bridge_evidence_covers_platform_test(cwd, db_path, target_path)

    if covers_target or bridge_covers_target:
        # Spec covers this path
        emit_pass()
        sys.exit(0)

    if not has_source_paths:
        emit_additional_context(
            "PreToolUse",
            f"[Governance] No specs with source_paths defined. "
            f"Consider adding source_paths to specs covering {target_path}.",
        )
        sys.exit(0)

    if not covers_target:
        emit_additional_context(
            "PreToolUse",
            f"[Governance] No specification found covering {target_path}. "
            "Create or update a spec with source_paths before writing source code.",
        )
        sys.exit(0)

    emit_pass()
    sys.exit(0)


if __name__ == "__main__":
    main()
