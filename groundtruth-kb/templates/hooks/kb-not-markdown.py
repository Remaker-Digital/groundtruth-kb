#!/usr/bin/env python3
"""
PreToolUse hook: KB-not-markdown advisory.

Emits an advisory when Claude attempts to write a .md file outside approved
paths, reminding it that canonical project knowledge belongs in the KB,
not in markdown files.

Approved paths (configurable via groundtruth.toml [governance] section):
- bridge/          (file bridge proposals and reviews)
- memory/          (session state and operational patterns)
- independent-progress-assessments/  (Loyal Opposition reports)
- .claude/rules/   (local control rules)
- docs/            (published documentation)
- CLAUDE.md, MEMORY.md, AGENTS.md, README.md  (root files)

Hook type: PreToolUse (tools: Write)

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

DEFAULT_APPROVED_PREFIXES = [
    "bridge/",
    "memory/",
    "independent-progress-assessments/",
    ".claude/rules/",
    "docs/",
    "site/",
]

DEFAULT_APPROVED_FILENAMES = {
    "CLAUDE.md",
    "MEMORY.md",
    "AGENTS.md",
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "CODE_OF_CONDUCT.md",
    "LICENSE.md",
}

WRITE_TOOLS = {"Write"}


def _load_extra_approved_prefixes(cwd: str) -> list[str]:
    """Load extra approved prefixes from groundtruth.toml [governance] section."""
    toml_path = Path(cwd) / "groundtruth.toml"
    extra: list[str] = []
    if not toml_path.exists():
        return extra
    try:
        content = toml_path.read_text(encoding="utf-8")
        in_governance = False
        for line in content.splitlines():
            stripped = line.strip()
            if stripped == "[governance]":
                in_governance = True
                continue
            if stripped.startswith("[") and stripped != "[governance]":
                in_governance = False
                continue
            if in_governance and stripped.startswith("approved_markdown_paths"):
                # Parse the value
                _, _, raw = stripped.partition("=")
                raw = raw.strip()
                try:
                    parsed = json.loads(raw)
                    if isinstance(parsed, list):
                        extra.extend(str(p) for p in parsed)
                except json.JSONDecodeError:
                    pass
    except OSError:
        pass
    return extra


def _is_approved(file_path: str, extra_prefixes: list[str]) -> bool:
    normalized = file_path.replace("\\", "/")
    filename = Path(normalized).name

    if filename in DEFAULT_APPROVED_FILENAMES:
        return True

    all_prefixes = DEFAULT_APPROVED_PREFIXES + extra_prefixes
    return any(normalized.startswith(prefix) or normalized.startswith("./" + prefix) for prefix in all_prefixes)


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
            "[Governance] KB-not-markdown hook active. "
            "Canonical project knowledge belongs in the KB, not markdown files.",
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

    file_path = tool_input.get("file_path", "")
    if not file_path or not file_path.endswith(".md"):
        emit_pass()
        sys.exit(0)

    extra_prefixes = _load_extra_approved_prefixes(cwd)

    if _is_approved(file_path, extra_prefixes):
        emit_pass()
        sys.exit(0)

    emit_additional_context(
        "PreToolUse",
        f"[Governance] Writing to {file_path}: canonical project knowledge belongs in the "
        "Knowledge Database (groundtruth.db), not markdown files. "
        "Use the KB API for specs, tests, documents, and work items. "
        "Approved markdown paths: bridge/, memory/, docs/, .claude/rules/, and named root files.",
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
