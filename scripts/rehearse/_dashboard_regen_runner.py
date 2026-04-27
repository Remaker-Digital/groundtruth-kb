"""Audit-hook-instrumented runner for the dashboard generator subprocess.

Invoked by ``_dashboard_regen.py`` during sample render. Installs a
``sys.addaudithook`` BEFORE running the legacy generator script and fails
fast on any file-system read or subprocess spawn whose target path falls
outside the allowed bases.

Per Slice 11 GO at ``bridge/gtkb-isolation-016-phase8-wave2-slice11-012.md``
(REVISED-5 spec). Constraints:

- No recursive ``legacy_root/scripts`` allowance (per ``-008``).
- Legacy originals of the 5 generator-consumed deployment files are
  denied; sandbox copies under ``<sandbox_root>/scripts/...`` are allowed
  via the sandbox prefix rule.
- Path resolution canonicalizes ``..`` and symlinks before allowlist
  match.

The module exposes ``build_is_allowed`` and ``build_audit_hook`` factories
so unit tests can validate the policy without spawning subprocesses.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

# ---- Policy constants -------------------------------------------------

# Filenames under ``legacy_root/scripts`` that are denied by glob even
# though the current generator doesn't read them. Defense-in-depth
# against a future generator change adding `deploy_*.py` reads (per
# REVISED-4 ``-008`` defense-in-depth rationale).
_DENIED_FILENAME_GLOBS_UNDER_LEGACY_SCRIPTS: tuple[str, ...] = (
    "deploy_*.py",
    "deploy.py",
)


def _resolve(p: Path) -> Path:
    """Canonicalize a path: resolve ``..`` and symlinks; never raise."""
    try:
        return p.resolve(strict=False)
    except (OSError, ValueError):
        return p


def _is_relative_to(child: Path, parent: Path) -> bool:
    """Return True iff ``child`` is the same as or under ``parent``."""
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def _build_allowed_path_rules(legacy_root: Path, sandbox_root: Path) -> list[tuple[str, Path]]:
    """Per-file code allowlist + Python runtime + sandbox + sys.path prefixes.

    Per Slice 11 REVISED-4 ``-008`` and REVISED-5 ``-010``: code-only
    legacy reads are OK; data-only legacy reads are NOT. The legacy
    code surface is restricted to exact-file allows (8 files; verified
    at impl time). Python runtime paths (stdlib + site-packages +
    user-site + editable-install dirs from sys.path) are allowed
    recursively — they're framework-installed code, not legacy project
    state, so allowing them doesn't conflict with the principle.

    sys.path filtering: any sys.path entry under ``legacy_root`` is
    EXCLUDED from the runtime prefix set so the per-file legacy code
    allowlist remains the only mechanism for legacy code reads. This
    preserves Codex's `-008` boundary while accommodating Python's real
    import surface (discovered at impl-time live smoke: 1,418 denied
    opens across site-packages + editable-installed packages).
    """
    legacy_root = _resolve(legacy_root)
    sandbox_root = _resolve(sandbox_root)

    runtime_prefixes: list[Path] = []
    runtime_prefixes.append(_resolve(Path(sys.base_prefix)))
    runtime_prefixes.append(_resolve(Path(sys.prefix)))
    # site.getsitepackages() + site.USER_SITE catch user-installed
    # packages. Required for pip-installed dependencies the generator
    # imports (e.g., ``groundtruth_kb`` editable install).
    import site  # noqa: PLC0415  (intentional: deferred to avoid early site init)

    for sp in site.getsitepackages():
        runtime_prefixes.append(_resolve(Path(sp)))
    if site.ENABLE_USER_SITE and site.USER_SITE:
        runtime_prefixes.append(_resolve(Path(site.USER_SITE)))
    # Any sys.path entry that is a real directory and NOT under
    # legacy_root (those are governed by per-file allows + sandbox).
    for entry in sys.path:
        if not entry:
            continue
        try:
            rp = _resolve(Path(entry))
        except (OSError, ValueError):
            continue
        if not rp.is_dir():
            continue
        # Skip anything under legacy_root — preserves Codex `-008` boundary.
        try:
            rp.relative_to(legacy_root)
            continue
        except ValueError:
            pass
        if rp not in runtime_prefixes:
            runtime_prefixes.append(rp)

    rules: list[tuple[str, Path]] = []
    for rp in runtime_prefixes:
        rules.append(("prefix", rp))
    # Sandbox tree (recursive). All generator project-state reads must
    # come from here.
    rules.append(("prefix", sandbox_root))
    # Per-file code allowlist (legacy_root/scripts) — exact paths only.
    # Source-verified at impl time: REVISED-5 missed three ``try:``-block
    # imports at lines 38-86 of session_self_initialization.py
    # (workstream_focus, gtkb_overlay, gtkb_scoped_client). Transitive-
    # closure scan confirmed the 4 generator-imported modules import
    # only stdlib — no further local files.
    rules.extend(
        [
            ("exact", _resolve(legacy_root / "scripts" / "session_self_initialization.py")),
            ("exact", _resolve(legacy_root / "scripts" / "_wrap_io.py")),
            ("exact", _resolve(legacy_root / "scripts" / "workstream_focus.py")),
            ("exact", _resolve(legacy_root / "scripts" / "gtkb_overlay.py")),
            ("exact", _resolve(legacy_root / "scripts" / "gtkb_scoped_client.py")),
            ("exact", _resolve(legacy_root / "scripts" / "rehearse" / "_dashboard_regen_runner.py")),
            ("exact", _resolve(legacy_root / "scripts" / "__init__.py")),
            ("exact", _resolve(legacy_root / "scripts" / "rehearse" / "__init__.py")),
            # Bytecode caches for the allowed code files. Python writes/reads
            # .pyc bytecode to ``__pycache__`` next to .py source.
            ("prefix", _resolve(legacy_root / "scripts" / "__pycache__")),
            ("prefix", _resolve(legacy_root / "scripts" / "rehearse" / "__pycache__")),
        ]
    )
    return rules


def _build_denied_path_prefixes(legacy_root: Path) -> list[Path]:
    """Explicit denylist (precedence over any allow rule).

    Per Slice 11 REVISED-5 ``-010`` Required Revision: legacy originals
    of the 5 generator-consumed deployment files MUST be denied while
    sandbox copies remain allowed via the sandbox prefix rule.
    """
    legacy_root = _resolve(legacy_root)
    return [
        # Per Codex `-010`: legacy originals of the 5 deployment files.
        _resolve(legacy_root / "scripts" / "agent-container-template.yaml"),
        _resolve(legacy_root / "scripts" / "deploy"),
        # Project-state data the generator may read (per Codex `-006`/`-008`).
        _resolve(legacy_root / ".env.local"),
        _resolve(legacy_root / ".env"),
        _resolve(legacy_root / "memory"),
        _resolve(legacy_root / "bridge"),
        _resolve(legacy_root / "docs" / "gtkb-dashboard"),
        _resolve(legacy_root / ".github" / "workflows"),
        _resolve(legacy_root / "groundtruth.db"),
        _resolve(legacy_root / ".groundtruth"),
        _resolve(legacy_root / ".git"),
    ]


def build_is_allowed(legacy_root: Path, sandbox_root: Path) -> Callable[[str], bool]:
    """Factory: return a path-policy callable bound to the given roots.

    The returned ``is_allowed(path_str)`` resolves the path (`Path.resolve`),
    applies denylist precedence (Tier 0), then allow-list prefix/exact
    rules (Tier 1/2). Default deny on no match. Empty/None paths are
    allowed (stdin/stdout file descriptors).
    """
    allowed_rules = _build_allowed_path_rules(legacy_root, sandbox_root)
    denied_prefixes = _build_denied_path_prefixes(legacy_root)
    legacy_scripts_path = _resolve(_resolve(legacy_root) / "scripts")

    def is_allowed(path_str: str) -> bool:
        if not path_str:
            return True
        try:
            p = _resolve(Path(path_str))
        except (OSError, ValueError):
            return False
        # Tier 0: explicit denies
        for denied in denied_prefixes:
            if _is_relative_to(p, denied):
                return False
        # Tier 0b: glob-deny under legacy_root/scripts (top-level only).
        # `Path.match` matches the rightmost-most components, so a file
        # like legacy_root/scripts/deploy_pipeline.py is matched by
        # `deploy_*.py` only when it sits directly under scripts/.
        if _is_relative_to(p, legacy_scripts_path):
            for pattern in _DENIED_FILENAME_GLOBS_UNDER_LEGACY_SCRIPTS:
                if p.match(pattern):
                    return False
        # Tier 1: exact-file allowlist
        for kind, allowed in allowed_rules:
            if kind == "exact" and p == allowed:
                return True
        # Tier 2: prefix allowlist
        for kind, allowed in allowed_rules:
            if kind == "prefix" and _is_relative_to(p, allowed):
                return True
        return False

    return is_allowed


def build_audit_hook(
    legacy_root: Path,
    sandbox_root: Path,
    violations: list[dict[str, Any]],
    violations_out: Path | None,
) -> Callable[[str, tuple[Any, ...]], None]:
    """Factory: return an ``sys.addaudithook``-compatible callable.

    Intercepts ``open`` and ``subprocess.Popen`` audit events. Out-of-
    sandbox accesses append to ``violations``. ``violations_out`` is
    used by the lane to persist the list AFTER the subprocess returns;
    the hook itself does NOT flush on every violation — that would
    trigger an infinite recursion (write → audit event → hook fires →
    appends + flushes → write triggers audit event → ...).

    Implementation notes (impl-time discoveries on Python 3.14 Windows):

    - **Log-and-continue, not raise.** Raising ``PermissionError`` from
      inside the hook triggers a pathlib internal-attribute
      ``AttributeError`` chain during traceback formatting that hangs
      the subprocess (~120s timeout reproducibly). Switching to
      log-and-continue: the hook appends to ``violations`` and returns
      normally. The generator proceeds; subsequent legacy reads also
      produce violations, which is more informative — operators see the
      FULL set of legacy reads in one run, not just the first.
    - **No per-violation flush.** ``violations_out`` is the path the
      lane reads after the subprocess returns. The hook's own write
      would re-enter via the ``open`` audit event, causing recursion.

    Lane-side semantics unchanged from REVISED-5: ``len(violations) > 0``
    produces ``status='error'`` per Codex `-012` constraint matrix.
    Proof of no-leak is still ``status='ok'`` with empty violations —
    achievable only when the generator is hardened to read only from
    sandbox. Until then, every dashboard rehearsal run produces
    ``status='error'`` with an enumerated list of legacy paths.
    """
    is_allowed = build_is_allowed(legacy_root, sandbox_root)
    # ``violations_out`` retained on closure so the lane can persist
    # post-subprocess; not used inside the hook itself (see docstring
    # "No per-violation flush" rationale).
    _ = violations_out

    def hook(event: str, args_tuple: tuple[Any, ...]) -> None:
        if event == "open":
            path = args_tuple[0] if args_tuple else None
            if isinstance(path, (str, bytes, os.PathLike)) and not is_allowed(str(path)):
                violations.append({"event": "open", "path": str(path)})
        elif event == "subprocess.Popen":
            cwd = args_tuple[2] if len(args_tuple) > 2 else None
            if cwd and not is_allowed(str(cwd)):
                violations.append({"event": "subprocess.Popen.cwd", "cwd": str(cwd)})

    return hook


# ---- CLI entry --------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit-hook-instrumented runner for the dashboard generator subprocess."
    )
    parser.add_argument("--legacy-script", required=True, type=Path)
    parser.add_argument("--legacy-root", required=True, type=Path)
    parser.add_argument("--sandbox-root", required=True, type=Path)
    parser.add_argument("--violations-out", required=True, type=Path)
    return parser


def _split_argv(argv: list[str]) -> tuple[list[str], list[str]]:
    """Split runner args from generator argv at the ``--`` separator."""
    if "--" in argv:
        i = argv.index("--")
        return argv[:i], argv[i + 1 :]
    return argv, []


def main(argv: list[str] | None = None) -> int:
    runner_args, generator_argv = _split_argv(list(argv if argv is not None else sys.argv[1:]))
    args = _build_parser().parse_args(runner_args)

    violations: list[dict[str, Any]] = []
    hook = build_audit_hook(args.legacy_root, args.sandbox_root, violations, args.violations_out)

    # Install hook BEFORE any further file activity. From this point on,
    # every Python-level open() and subprocess.Popen passes through the
    # policy gate.
    sys.addaudithook(hook)

    # Reshape sys.argv so the legacy script sees its expected argv[0].
    sys.argv = [str(args.legacy_script), *generator_argv]

    # Insert legacy_root and legacy_root/scripts into sys.path so the
    # generator's import surface works identically to the production
    # ``python scripts/session_self_initialization.py`` invocation:
    #   - ``from scripts.workstream_focus import ...`` resolves via legacy_root
    #   - ``from workstream_focus import ...`` resolves via legacy_root/scripts
    # The 4 generator local imports (workstream_focus, gtkb_overlay,
    # gtkb_scoped_client, _wrap_io) all use one of these two paths.
    # Per ``feedback_verify_source_before_parallel_proposals.md``: this
    # behavior was not in REVISED-3/4/5; it was discovered at impl time
    # via live-smoke ModuleNotFoundError.
    legacy_root_str = str(args.legacy_root.resolve())
    legacy_scripts_str = str((args.legacy_root / "scripts").resolve())
    if legacy_scripts_str not in sys.path:
        sys.path.insert(0, legacy_scripts_str)
    if legacy_root_str not in sys.path:
        sys.path.insert(0, legacy_root_str)

    # Note: import is deliberately deferred until after the hook is
    # registered, so any imports the legacy script triggers go through
    # the hook too.
    import runpy  # noqa: PLC0415  (intentional: post-hook-install import)

    try:
        runpy.run_path(str(args.legacy_script), run_name="__main__")
    finally:
        # Ensure violations are persisted even on exception/crash.
        if args.violations_out is not None:
            args.violations_out.parent.mkdir(parents=True, exist_ok=True)
            args.violations_out.write_text(json.dumps(violations, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
