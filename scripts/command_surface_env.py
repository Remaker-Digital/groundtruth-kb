"""Canonical in-root command-surface environment for GT-KB (WI-4395).

WI-4395 (P1, ``command-surface``, origin=defect). Automation and documented
verification command surfaces invoke ``uv``-backed ``gt`` / ``pytest`` / ``ruff``
commands. When ``uv`` falls back to the default user-profile cache (under
``%LOCALAPPDATA%``), that cache is outside the repo and subject to host / ACL /
cloud-sync races -- the original WI-4395 symptom was a ``Failed to initialize
cache ... Cannot create a file when that file already exists`` outage. Agents
then re-derive an ad-hoc workaround per session, which is why the repo root has
accumulated several ad-hoc ``.uv-cache*`` trees (the HYG-054 sprawl).

This module is the ONE canonical command surface that pins the uv cache and temp
directories to in-root, harness-writable locations under ``.gtkb-state/`` so
callers stop re-deriving them. Both pinned subdirectory names contain the
substring ``uv-cache`` -- one of the runtime-evidence GC directory-name tokens in
``config/governance/runtime-evidence-retention.toml`` ``[gtkb_state_gc]`` -- so
the existing 14-day GC already covers them and no new cache convention is
introduced (dedup against HYG-054 / WI-4356).

Responsibilities:

1. :func:`resolve_command_surface_env` -- path-pure (no filesystem touch):
   returns the canonical ``UV_CACHE_DIR`` / ``TMP`` / ``TEMP`` mapping.
2. :func:`ensure_command_surface_env` -- the only function that touches the
   filesystem: idempotently creates the command-surface directories and returns
   a merged environment dict (caller's / process env overlaid with the pinned
   keys). It NEVER mutates the live process environment and NEVER deletes
   anything; callers pass the result to ``subprocess`` invocations.
3. :func:`main` -- a self-documenting CLI that prints the resolved env (manual
   use), mirroring ``scripts/install_gt_path_shim.py``.

Out of scope (kept minimal and reversible): cleaning up the pre-existing
root-level ``.uv-cache*`` sprawl (WI-4356 / a separate hygiene cleanup; deletion
is destructive), wiring every existing automation caller to this helper (a
follow-on with its own blast-radius review), and editing the retention config
(deliberately avoided by reusing the existing ``uv-cache`` token).

Governing specs: GOV-STANDING-BACKLOG-001 (WI-4395 backlog authority),
GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 /
DCL-PROJECT-AUTHORIZATION-ENVELOPE-001 (PAUTH scope),
ADR-ISOLATION-APPLICATION-PLACEMENT-001 (in-root invariant),
DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (each behaviour has a test).

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

__all__ = [
    "GTKB_STATE_DIRNAME",
    "UV_CACHE_SUBDIR",
    "COMMAND_TMP_SUBDIR",
    "GC_RECOGNIZED_TOKENS",
    "resolve_command_surface_env",
    "command_surface_dirs",
    "gc_recognized_token",
    "ensure_command_surface_env",
    "main",
]

# In-root runtime-evidence root (git-ignored).
GTKB_STATE_DIRNAME = ".gtkb-state"
# Canonical uv cache subdir; the name contains the "uv-cache" GC token.
UV_CACHE_SUBDIR = "uv-cache"
# Canonical command-surface temp subdir; the name contains "uv-cache" so it is
# GC-covered too (TMP/TEMP point here).
COMMAND_TMP_SUBDIR = "uv-cache-tmp"

# Mirror of config/governance/runtime-evidence-retention.toml [gtkb_state_gc]
# directory_name_tokens (substring match). Every directory this module pins must
# contain one of these tokens so the existing 14-day GC already covers it; a
# regression test cross-checks this tuple against the live config to prevent
# drift.
GC_RECOGNIZED_TOKENS = ("pytest-tmp", "pytest_tmp", "pytest-cache", "uv-cache")

# Environment keys this surface pins, in stable order.
_PINNED_KEYS = ("UV_CACHE_DIR", "TMP", "TEMP")


def resolve_command_surface_env(project_root: str | os.PathLike[str]) -> dict[str, str]:
    """Return the canonical command-surface environment mapping (path-pure).

    Pins ``UV_CACHE_DIR`` to ``<project_root>/.gtkb-state/uv-cache`` and both
    ``TMP`` and ``TEMP`` to ``<project_root>/.gtkb-state/uv-cache-tmp``. Builds
    paths only; never touches the filesystem and never reads or mutates the live
    environment.
    """
    state = Path(project_root) / GTKB_STATE_DIRNAME
    uv_cache = state / UV_CACHE_SUBDIR
    command_tmp = state / COMMAND_TMP_SUBDIR
    return {
        "UV_CACHE_DIR": str(uv_cache),
        "TMP": str(command_tmp),
        "TEMP": str(command_tmp),
    }


def command_surface_dirs(project_root: str | os.PathLike[str]) -> tuple[Path, ...]:
    """Return the unique directories the command-surface env points at.

    Order-preserving and de-duplicated (``TMP``/``TEMP`` share one directory).
    """
    env = resolve_command_surface_env(project_root)
    unique: dict[str, None] = {}
    for key in _PINNED_KEYS:
        unique.setdefault(env[key], None)
    return tuple(Path(path) for path in unique)


def gc_recognized_token(name: str) -> str | None:
    """Return the GC directory-name token ``name`` contains, or ``None``.

    Substring match, matching ``runtime-evidence-retention.toml`` semantics.
    """
    for token in GC_RECOGNIZED_TOKENS:
        if token in name:
            return token
    return None


def ensure_command_surface_env(
    project_root: str | os.PathLike[str],
    base_env: dict[str, str] | None = None,
) -> dict[str, str]:
    """Create the command-surface directories and return a merged environment.

    Idempotently ``mkdir(parents=True, exist_ok=True)`` each command-surface
    directory (the only filesystem effect), then return a new dict that overlays
    the canonical pinned keys onto ``base_env`` (or :data:`os.environ` when
    ``base_env`` is ``None``). The pinned keys always win, so a denied or broken
    inherited ``UV_CACHE_DIR`` / ``TMP`` / ``TEMP`` is replaced by the in-root,
    harness-writable location. The live process environment is never mutated.
    """
    for directory in command_surface_dirs(project_root):
        directory.mkdir(parents=True, exist_ok=True)
    merged: dict[str, str] = dict(os.environ if base_env is None else base_env)
    merged.update(resolve_command_surface_env(project_root))
    return merged


def _default_project_root() -> Path:
    """The in-root checkout containing this script (``scripts/`` parent)."""
    return Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    """Print the canonical command-surface env (manual-use entrypoint).

    Read-only by default; ``--ensure`` creates the directories. Prints
    ``KEY=VALUE`` lines (default) or JSON (``--format json``). Returns 0.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Print the canonical GT-KB command-surface environment "
            "(UV_CACHE_DIR/TMP/TEMP pinned under .gtkb-state). WI-4395."
        )
    )
    parser.add_argument(
        "--project-root",
        default=str(_default_project_root()),
        help="GT-KB project root (default: the in-root checkout of this script).",
    )
    parser.add_argument(
        "--ensure",
        action="store_true",
        help="Create the command-surface directories before printing.",
    )
    parser.add_argument(
        "--format",
        choices=("env", "json"),
        default="env",
        help="Output format (default: env -> KEY=VALUE lines).",
    )
    args = parser.parse_args(argv)

    if args.ensure:
        env = ensure_command_surface_env(args.project_root, base_env={})
        env = {key: env[key] for key in _PINNED_KEYS}
    else:
        env = resolve_command_surface_env(args.project_root)

    if args.format == "json":
        print(json.dumps(env, indent=2, sort_keys=True))
    else:
        for key in _PINNED_KEYS:
            print(f"{key}={env[key]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
