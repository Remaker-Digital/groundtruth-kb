"""Deterministic in-root ``gt`` PATH-shim content/path generator.

WI-4530 (P3, ``developer-environment``, origin=improvement). A fresh GT-KB
checkout exposes the ``gt`` CLI only as the venv console-script at
``groundtruth-kb/.venv/Scripts/gt.exe`` (Windows) / ``groundtruth-kb/.venv/bin/gt``
(POSIX). That venv has no pip and pipx is not installed, so ``gt`` is not on
PATH and the bare ``gt ...`` invocations assumed throughout the rules / skills /
docs fail on a fresh install. The 2026-06-13 manual workaround placed a
``gt.cmd`` launcher under a user-PATH directory forwarding to the venv exe, but
that out-of-root placement was manual and does not survive a fresh install on
another machine.

WI-4954 repairs the emergency regression where that venv console script is
absent. The durable CLI entrypoint remains ``groundtruth_kb.cli:main``; the PATH
shim now launches that module through the project venv Python with the in-root
``groundtruth-kb/src`` directory on ``PYTHONPATH``.

This module is the deterministic generator for that launcher's TEXT CONTENT and
its launcher target paths. It has two responsibilities, both pure:

1. Resolve the venv Python executable and source-tree path from a
   ``project_root`` (path-pure; no filesystem touch).
2. Emit the launcher script's text content (Windows ``.cmd`` / POSIX shell)
   that forwards all arguments to ``python -m groundtruth_kb.cli``
   (string-pure; no file write).

Crucially this module performs **no I/O**: it does not write any file, does not
mutate PATH or any environment variable, and does not launch a subprocess in any
public function. The ``if __name__ == "__main__"`` entrypoint only prints the
rendered content to stdout for manual use. Placing the rendered launcher on a
user-PATH directory (an out-of-root concern) and wiring this generator into the
install / bootstrap path are explicitly deferred to a follow-on install slice
with its own authorization and project-root-boundary review.

Governing specs: GOV-STANDING-BACKLOG-001 (WI-4530 backlog authority),
GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 (project work ordering),
ADR-ISOLATION-APPLICATION-PLACEMENT-001 (in-root invariant),
DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (each behaviour has a test).

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import shlex
import sys
from pathlib import Path

__all__ = [
    "WINDOWS_PLATFORMS",
    "POSIX_PLATFORMS",
    "resolve_source_tree",
    "resolve_venv_gt_exe",
    "resolve_venv_python_exe",
    "render_windows_cmd_shim",
    "render_posix_shell_shim",
    "render_for_platform",
    "main",
]

# Platform tokens (as produced by ``sys.platform``) the generator supports.
WINDOWS_PLATFORMS = frozenset({"win32"})
POSIX_PLATFORMS = frozenset({"linux", "darwin"})


def resolve_venv_gt_exe(project_root: str | Path, platform: str) -> Path:
    """Return the legacy venv-internal ``gt`` executable path for ``platform``.

    Path-pure and retained for diagnostics/tests that need to identify stale
    WI-4530 launchers. New launcher content must use
    :func:`resolve_venv_python_exe` plus :func:`resolve_source_tree`.

    Raises ``ValueError`` for any unsupported platform string.
    """
    root = Path(project_root)
    venv = root / "groundtruth-kb" / ".venv"
    if platform in WINDOWS_PLATFORMS:
        return venv / "Scripts" / "gt.exe"
    if platform in POSIX_PLATFORMS:
        return venv / "bin" / "gt"
    supported = ", ".join(sorted(WINDOWS_PLATFORMS | POSIX_PLATFORMS))
    raise ValueError(f"Unsupported platform {platform!r}; supported platforms: {supported}.")


def resolve_venv_python_exe(project_root: str | Path, platform: str) -> Path:
    """Return the venv-internal Python executable path for ``platform``.

    Path-pure: builds the path by joining segments under ``project_root`` and
    never touches the filesystem. Windows resolves to
    ``<root>/groundtruth-kb/.venv/Scripts/python.exe``; POSIX resolves to
    ``<root>/groundtruth-kb/.venv/bin/python``.

    Raises ``ValueError`` for any unsupported platform string.
    """
    root = Path(project_root)
    venv = root / "groundtruth-kb" / ".venv"
    if platform in WINDOWS_PLATFORMS:
        return venv / "Scripts" / "python.exe"
    if platform in POSIX_PLATFORMS:
        return venv / "bin" / "python"
    supported = ", ".join(sorted(WINDOWS_PLATFORMS | POSIX_PLATFORMS))
    raise ValueError(f"Unsupported platform {platform!r}; supported platforms: {supported}.")


def resolve_source_tree(project_root: str | Path) -> Path:
    """Return the in-root import path containing the ``groundtruth_kb`` package."""
    return Path(project_root) / "groundtruth-kb" / "src"


def render_windows_cmd_shim(python_exe_path: str | Path, source_tree_path: str | Path) -> str:
    """Return the Windows ``gt.cmd`` launcher content forwarding all args.

    String-pure. The Python executable and source-tree path are double-quoted
    where needed so paths containing spaces are tolerated. ``%*`` forwards all
    caller arguments verbatim.
    """
    python_exe = str(python_exe_path)
    source_tree = str(source_tree_path)
    return (
        "@echo off\n"
        "REM gt CLI launcher shim (WI-4530/WI-4954) -- generated by "
        "scripts/install_gt_path_shim.py\n"
        "REM Launches the in-root GT-KB CLI module through the project venv Python.\n"
        f'set "PYTHONPATH={source_tree};%PYTHONPATH%"\n'
        f'"{python_exe}" -m groundtruth_kb.cli %*\n'
    )


def render_posix_shell_shim(python_exe_path: str | Path, source_tree_path: str | Path) -> str:
    """Return the POSIX ``gt`` shell launcher content forwarding all args.

    String-pure. Begins with a ``#!/usr/bin/env bash`` shebang, shell-quotes the
    Python executable and source-tree path so spaces are tolerated, and uses
    ``exec ... "$@"`` so the launcher replaces itself with the CLI module
    process and forwards all args.
    """
    python_exe = shlex.quote(str(python_exe_path))
    source_tree = shlex.quote(str(source_tree_path))
    return (
        "#!/usr/bin/env bash\n"
        "# gt CLI launcher shim (WI-4530/WI-4954) -- generated by "
        "scripts/install_gt_path_shim.py\n"
        "# Launches the in-root GT-KB CLI module through the project venv Python.\n"
        f"export PYTHONPATH={source_tree}${{PYTHONPATH:+:$PYTHONPATH}}\n"
        f'exec {python_exe} -m groundtruth_kb.cli "$@"\n'
    )


def render_for_platform(project_root: str | Path, platform: str) -> dict[str, str]:
    """Convenience wrapper returning everything a caller needs for one platform.

    Returns ``{"filename": "gt.cmd"|"gt", "content": <str>,
    "python_exe": <str>, "source_tree": <str>, "legacy_venv_gt_exe": <str>}``.
    Combines :func:`resolve_venv_python_exe` and :func:`resolve_source_tree`
    with the platform-appropriate renderer. Raises ``ValueError`` for an
    unsupported platform string.
    """
    python_exe = resolve_venv_python_exe(project_root, platform)
    source_tree = resolve_source_tree(project_root)
    legacy_venv_gt = resolve_venv_gt_exe(project_root, platform)
    if platform in WINDOWS_PLATFORMS:
        return {
            "filename": "gt.cmd",
            "content": render_windows_cmd_shim(python_exe, source_tree),
            "python_exe": str(python_exe),
            "source_tree": str(source_tree),
            "legacy_venv_gt_exe": str(legacy_venv_gt),
        }
    # POSIX (resolve_venv_gt_exe already rejected unsupported platforms above).
    return {
        "filename": "gt",
        "content": render_posix_shell_shim(python_exe, source_tree),
        "python_exe": str(python_exe),
        "source_tree": str(source_tree),
        "legacy_venv_gt_exe": str(legacy_venv_gt),
    }


def main(argv: list[str] | None = None) -> int:
    """Print the rendered launcher content to stdout (manual-use entrypoint).

    No file write, no PATH modification, no out-of-root placement -- those are
    the follow-on install slice's responsibility. Returns 0 on success, 2 for an
    unsupported ``--platform`` value.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Emit the gt CLI launcher-shim content to stdout (WI-4530). Does NOT write any file or modify PATH."
        )
    )
    parser.add_argument(
        "--platform",
        default=sys.platform,
        help="Target platform token (default: current sys.platform).",
    )
    parser.add_argument(
        "--project-root",
        default=str(Path(__file__).resolve().parents[1]),
        help="GT-KB project root (default: the in-root checkout of this script).",
    )
    args = parser.parse_args(argv)

    try:
        rendered = render_for_platform(args.project_root, args.platform)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(rendered["content"], end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
