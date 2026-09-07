#!/usr/bin/env python3
"""Project the .claude skill tree from the harness baseline.

Owner directive 2026-08-13: the harness baseline is authoritative and every
individual harness configuration directory is a projection of it. The baseline
tree is ``.harness-baseline-configuration``; the earlier ``.agents`` tree it
replaced was retired by WI-6228 after the transition landed inverted (the old
tree was emptied before the repoint), leaving this generator the last consumer
still bound to it.

``.claude`` is the case that makes the directive real. Before this generator it
was simultaneously the baseline *and* Claude Code's live configuration - one
directory serving two roles - so repointing the capability registry at the
baseline without also generating ``.claude`` would leave ``.claude``
hand-edited and unenforced. The baseline would fork on the first edit, exactly
the way ``.cursor`` drifted 73 files behind canonical while nothing reported it.

Unlike the codex, cursor, antigravity and api generators this performs an
**identity projection**: ``.claude`` receives the baseline bytes unchanged, with
no generated-marker block and no path rewriting. Those generators translate
canonical content for a foreign harness surface; ``.claude`` consumes the
canonical form directly, and the registry records its capabilities as ``native``
rather than ``adapter``. A marker here would change what Claude Code loads for no
benefit.

Scope is ``skills/`` only - the surface the harness capability registry governs
and the one every other generator projects. ``rules/``, ``hooks/`` and
``commands/`` exist under both trees, but ``.claude`` mixes runtime-generated
artifacts into those directories (startup-disclosure caches, session state), so
mirroring them wholesale would fight the runtime. That is a separate slice with
its own exclusion contract.

Side-effect-free with respect to harness state: never registers a harness,
changes a role, or writes database state.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
# WI-6228 Change A — the harness baseline is the curated
# `.harness-baseline-configuration` tree, not the retired `.agents` tree.
#
# This is the last remaining source-root binding to the retired baseline. The
# other four generators resolve their sources through
# `config/agent-control/gtkb-harness-capability-registry.toml`, whose
# `canonical_source` / `adapter_source` entries were already migrated; only this
# generator directory-scans a hardcoded path, which is why it was the only one
# left reading an emptied tree.
#
# The empty-baseline guard below (see `generate`) is deliberately RETAINED. It is
# what prevented the inverted transition — tree emptied before the repoint landed
# — from erasing `.claude/skills`, since this generator prunes anything absent
# from the baseline via `unlink(missing_ok=True)`.
BASELINE_SKILLS = Path(".harness-baseline-configuration") / "skills"
CLAUDE_SKILLS = Path(".claude") / "skills"

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
from _wrap_io import _atomic_write_bytes  # noqa: E402

EXCLUDED_PARTS = {"__pycache__"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}
EXCLUDED_PREFIXES = ("_temp_", "tmp_", "draft-", "draft_")


class ClaudeProjectionError(RuntimeError):
    """Raised when the .claude projection cannot be produced deterministically."""


def _projectable(path: Path) -> bool:
    if not path.is_file():
        return False
    if EXCLUDED_PARTS & set(path.parts):
        return False
    if path.suffix.casefold() in EXCLUDED_SUFFIXES:
        return False
    return not path.name.startswith(EXCLUDED_PREFIXES)


def _files(root: Path) -> dict[str, Path]:
    if not root.is_dir():
        return {}
    return {
        path.relative_to(root).as_posix(): path
        for path in sorted(root.rglob("*"), key=lambda item: item.as_posix().casefold())
        if _projectable(path)
    }


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def generate(project_root: Path, *, check: bool = False) -> tuple[list[str], list[str], int]:
    """Project baseline skills into .claude.

    Returns ``(written, removed, total)`` where written and removed are
    repo-relative paths and total is the baseline file count.
    """
    root = project_root.resolve()
    source_root = root / BASELINE_SKILLS
    target_root = root / CLAUDE_SKILLS

    if not source_root.is_dir():
        raise ClaudeProjectionError(f"harness baseline is absent: {BASELINE_SKILLS.as_posix()}")

    source = _files(source_root)
    if not source:
        raise ClaudeProjectionError(
            f"harness baseline {BASELINE_SKILLS.as_posix()} is empty; refusing to erase {CLAUDE_SKILLS.as_posix()}"
        )
    target = _files(target_root)

    written: list[str] = []
    for relative, path in source.items():
        payload = path.read_bytes()
        # Helper routes are a per-harness runtime fact. Claude Code executes its own
        # helper copies, so baseline helper references are rewritten to .claude.
        # References are documentation and stay on the baseline.
        # WI-6228 Change C — rewrite from the current baseline prefix. A stale
        # prefix here fails silently: the pattern simply stops matching and the
        # projected body keeps a baseline path that does not resolve for Claude.
        payload = re.sub(
            re.escape(b".harness-baseline-configuration") + rb"(/skills/[A-Za-z0-9._-]+/helpers/)",
            rb".claude\1",
            payload,
        )
        destination = target_root / relative
        existing = destination.read_bytes() if destination.is_file() else None
        if existing is not None and _sha256(existing) == _sha256(payload):
            continue
        written.append((CLAUDE_SKILLS / relative).as_posix())
        if not check:
            destination.parent.mkdir(parents=True, exist_ok=True)
            _atomic_write_bytes(destination, payload)

    removed: list[str] = []
    for relative in sorted(set(target) - set(source)):
        removed.append((CLAUDE_SKILLS / relative).as_posix())
        if not check:
            (target_root / relative).unlink(missing_ok=True)

    return written, removed, len(source)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--check", action="store_true", help="Report drift without writing files.")
    args = parser.parse_args(argv)

    try:
        written, removed, total = generate(args.project_root, check=args.check)
    except ClaudeProjectionError as exc:
        print(f"Claude skill projection: FAIL ({exc})", file=sys.stderr)
        return 2

    changed = written + removed
    if changed:
        verb = "would update" if args.check else "updated"
        print(f"Claude skill projection: {verb} {len(changed)} file(s)")
        for path in written:
            print(f"- {path}")
        for path in removed:
            print(f"- {path} (removed: absent from baseline)")
        return 1 if args.check else 0

    print(f"Claude skill projection: PASS ({total} files current with the baseline)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
