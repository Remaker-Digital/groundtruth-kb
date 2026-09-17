"""Native CLI bridge boundaries shared by independent provider runtimes."""

from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

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
    r"\s+['\"]?(?P<harness>(?:\.?[\\/])?scripts[\\/][a-zA-Z0-9_]+_harness\.py)"
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
        "Author the complete message in session scratch and use gt bridge deliver "
        "with the exact next-artifact claim."
    )


class BridgeDeliveryIncomplete(RuntimeError):
    code = "bridge_delivery_incomplete"


def bridge_completion_target(skill, document, version):
    """Require an exact successor for an explicitly selected bridge workload.

    Initialization binds a context; it does not assign bridge work. Prompt prose
    and init markers are never a substitute for the launcher's target arguments.
    Bridge-only skills require those arguments, and partial targets fail before
    model execution. Every explicit target still requires canonical delivery.
    """
    required = document is not None or version is not None or skill in {"bridge-review", "verification"}
    if not required:
        return None
    if not isinstance(document, str) or not document.strip() or type(version) is not int or version < 1:
        raise BridgeDeliveryIncomplete(
            "bridge_delivery_incomplete: Supply the assigned --bridge-document and --bridge-version before launch"
        )
    return document, version


def verify_bridge_completion(target, native_context_id, project_root: Path, timeout, runner=None):
    """Verify through the native CLI only; author and publish nothing."""
    if target is None:
        return
    document, version = target
    argv = [
        sys.executable,
        "-m",
        "groundtruth_kb",
        "bridge",
        "check-delivery",
        document,
        "--version",
        str(version),
        "--native-context-id",
        native_context_id,
        "--json",
    ]
    env = {key: value for key, value in os.environ.items() if not key.startswith(("PG", "GT_POSTGRES_"))}
    env.pop("GTKB_AUTHOR_SESSION_CONTEXT_ID", None)
    env.update(GT_PROJECT_ROOT=str(project_root), GTKB_NATIVE_CONTEXT_ID=native_context_id, PYTHONIOENCODING="utf-8")
    try:
        if timeout <= 0:
            raise BridgeDeliveryIncomplete(
                "bridge_delivery_incomplete: No time remains for canonical delivery readback"
            )
        if runner is None:
            completed = subprocess.run(
                argv,
                cwd=project_root,
                env=env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=min(timeout, 10),
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        else:
            command = subprocess.list2cmdline(argv) if os.name == "nt" else shlex.join(argv)
            completed = runner(command, project_root, env, min(timeout, 10))
        if completed.returncode:
            raise BridgeDeliveryIncomplete(
                f"bridge_delivery_incomplete: Native CLI could not confirm {document} v{version} (exit {completed.returncode})"
            )
        result = json.loads(completed.stdout)
        if (
            not isinstance(result, dict)
            or result.get("status") != "delivered"
            or result.get("document") != document
            or type(result.get("version")) is not int
            or result["version"] != version
            or result.get("native_context_id") != native_context_id
            or not isinstance(result.get("author_session_context_id"), str)
            or not result["author_session_context_id"].strip()
            or not isinstance(result.get("bridge_status"), str)
            or not result["bridge_status"].strip()
        ):
            raise BridgeDeliveryIncomplete("bridge_delivery_incomplete: Native CLI returned no matching delivery")
    except (OSError, subprocess.TimeoutExpired, ValueError) as exc:
        raise BridgeDeliveryIncomplete(
            "bridge_delivery_incomplete: Canonical delivery readback was unavailable or invalid"
        ) from exc
