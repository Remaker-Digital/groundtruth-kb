"""W0 of GTKB-WRAPUP-ENHANCEMENTS Slice 1: transcript-snapshot precursor (manifest-only).

Per bridge/gtkb-wrapup-enhancements-slice1-005.md (REVISED-2, GO at -006), Slice 1
is **manifest-only**: no transcript content is captured. The manifest carries the
metadata W1/W2 actually consume (git HEAD/branch/uncommitted/untracked paths).
Transcript-content handling is deferred to a future WRAPUP-Slice-2A as a complete
unit (redaction + retention + ignore policy + W1 detection).

Output: ``.groundtruth/session/snapshots/<session-id>/manifest.json`` (atomic).
The snapshots directory itself is gitignored (matching the existing
``.groundtruth/session/overlays/`` precedent at .gitignore:345).

EXIT CODES:
    0  Success (manifest written; transcript metadata captured).
    2  Filesystem error (manifest could not be written).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _wrap_io import _atomic_write_text  # noqa: E402

MANIFEST_SCHEMA_VERSION = 1
DEFAULT_SNAPSHOT_ROOT = ".groundtruth/session/snapshots"

EXIT_OK = 0
EXIT_ERROR = 2


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _run_git(args: list[str], project_root: Path) -> str:
    """Run a git command and return stdout. Empty string on non-zero exit."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=10,
        )
        if result.returncode != 0:
            return ""
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, OSError):
        return ""


def _git_head(project_root: Path) -> str:
    return _run_git(["rev-parse", "HEAD"], project_root)


def _git_branch(project_root: Path) -> str:
    return _run_git(["rev-parse", "--abbrev-ref", "HEAD"], project_root)


def _git_uncommitted(project_root: Path) -> list[str]:
    """Return list of paths with staged or unstaged changes (not untracked)."""
    output = _run_git(["status", "--porcelain"], project_root)
    paths: list[str] = []
    for line in output.splitlines():
        if not line or len(line) < 4:
            continue
        status_code = line[:2]
        path = line[3:]
        # `??` means untracked; we list those separately
        if status_code.strip() and not status_code.startswith("??"):
            paths.append(path)
    return paths


def _git_untracked(project_root: Path) -> list[str]:
    """Return list of untracked paths (not gitignored)."""
    output = _run_git(["ls-files", "--others", "--exclude-standard"], project_root)
    return [line for line in output.splitlines() if line]


def build_manifest(session_id: str, project_root: Path) -> dict:
    """Assemble the manifest dict. Pure-functional; safe to call without I/O."""
    return {
        "manifest_schema_version": MANIFEST_SCHEMA_VERSION,
        "session_id": session_id,
        "captured_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git_head": _git_head(project_root),
        "git_branch": _git_branch(project_root),
        "uncommitted_paths": _git_uncommitted(project_root),
        "untracked_paths": _git_untracked(project_root),
    }


def write_manifest(session_id: str, snapshot_root: Path, project_root: Path) -> Path:
    """Build manifest and write atomically. Returns the manifest path."""
    manifest = build_manifest(session_id, project_root)
    manifest_path = snapshot_root / session_id / "manifest.json"
    _atomic_write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
    return manifest_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--session-id", required=True, help="Session identifier (e.g., S310)")
    parser.add_argument(
        "--snapshot-root",
        default=None,
        help=f"Snapshot root path (default: <project-root>/{DEFAULT_SNAPSHOT_ROOT})",
    )
    args = parser.parse_args(argv)

    project_root = _project_root()
    snapshot_root = Path(args.snapshot_root) if args.snapshot_root else project_root / DEFAULT_SNAPSHOT_ROOT

    try:
        manifest_path = write_manifest(args.session_id, snapshot_root, project_root)
    except OSError as exc:
        print(f"wrap_capture_transcript: failed to write manifest: {exc}", file=sys.stderr)
        return EXIT_ERROR

    print(f"Manifest written: {manifest_path}")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
