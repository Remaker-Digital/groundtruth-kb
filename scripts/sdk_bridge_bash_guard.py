"""Fail-closed Bash bridge-mutation detector for SDK harnesses."""

from __future__ import annotations

import re

try:
    from scripts.controlled_artifact_paths import BRIDGE_STATUS_ARTIFACT_COMMAND_PATTERN
except ImportError:  # pragma: no cover - direct script execution path
    from controlled_artifact_paths import BRIDGE_STATUS_ARTIFACT_COMMAND_PATTERN

_PROTECTED_BRIDGE_PATH_RE = re.compile(BRIDGE_STATUS_ARTIFACT_COMMAND_PATTERN, re.IGNORECASE)
_REDIRECT_TO_BRIDGE_RE = re.compile(
    rf"(?:^|[\s;&|])(?:\d?>{{1,2}}|>{{1,2}})\s*['\"]?{BRIDGE_STATUS_ARTIFACT_COMMAND_PATTERN}",
    re.IGNORECASE,
)
_MUTATING_COMMAND_RE = re.compile(
    r"\b(?:"
    r"set-content|add-content|out-file|new-item|copy-item|move-item|rename-item|remove-item|clear-content|"
    r"tee-object|sc|ac|ni|cp|mv|rm|ri|del|erase|copy|move|touch|tee"
    r")\b"
    r"|\bsed\s+-i\b"
    r"|\bperl\s+-pi\b"
    r"|\bgit\s+(?:checkout|restore|apply)\b"
    r"|\bpatch\b",
    re.IGNORECASE,
)
_SCRIPT_MUTATION_RE = re.compile(
    r"write_text\s*\("
    r"|write_bytes\s*\("
    r"|open\s*\([^)]*['\"][wax][+b]?['\"]"
    r"|shutil\.(?:copy|copy2|move)\s*\("
    r"|os\.(?:remove|rename|replace|unlink)\s*\("
    r"|\.(?:unlink|rename|replace|touch)\s*\(",
    re.IGNORECASE | re.DOTALL,
)
_SDK_HARNESS_SELF_INVOCATION_RE = re.compile(
    r"(?:^|[\s;&|])"
    r"(?:&\s*)?"
    r"['\"]?(?:[^\s'\";&|]+[\\/])?pythonw?(?:\.exe)?['\"]?"
    r"\s+['\"]?(?P<harness>(?:\.?[\\/])?scripts[\\/](?:ollama_harness|openrouter_harness)\.py)"
    r"(?:\b|['\"\s])",
    re.IGNORECASE,
)


def protected_bridge_paths(command: str) -> tuple[str, ...]:
    """Return protected bridge paths mentioned by a shell command."""
    if not command:
        return ()
    seen: dict[str, str] = {}
    for match in _PROTECTED_BRIDGE_PATH_RE.finditer(command):
        path = match.group(0).strip("\"'`")
        key = path.replace("\\", "/").lower()
        seen.setdefault(key, path)
    return tuple(seen.values())


def bridge_bash_mutation_reason(command: str) -> str | None:
    """Return a denial reason when ``command`` mutates bridge artifacts."""
    self_invocation = _SDK_HARNESS_SELF_INVOCATION_RE.search(command or "")
    if self_invocation:
        harness = self_invocation.group("harness").strip("\"'`").replace("\\", "/").lstrip("./")
        return (
            f"Bash SDK harness self-invocation denied for {harness}. "
            "Use Read/Grep/Glob or governed gt/helper commands instead of launching a nested SDK harness."
        )
    paths = protected_bridge_paths(command)
    if not paths:
        return None
    if not (
        _REDIRECT_TO_BRIDGE_RE.search(command)
        or _MUTATING_COMMAND_RE.search(command)
        or _SCRIPT_MUTATION_RE.search(command)
    ):
        return None
    listed = ", ".join(paths)
    return (
        f"Bash bridge artifact mutation denied for {listed}. "
        "Use guarded Write/Edit dispatch or the scripts/gtkb_bridge_writer.py helper path "
        "for numbered bridge files."
    )
