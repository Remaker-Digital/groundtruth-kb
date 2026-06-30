#!/usr/bin/env python3
"""Generate the bridge state swimlane JSON for the GT-KB dashboard.

Reads status-bearing numbered bridge files, attaches per-thread timestamps
from ``git log`` (with mtime fallback), and classifies each thread as
terminal, awaiting Prime Builder, or awaiting Loyal Opposition.

Output shape: see :func:`generate_swimlane`.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_THIS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _THIS_DIR.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
_GTKB_SRC = _REPO_ROOT / "groundtruth-kb" / "src"
if str(_GTKB_SRC) not in sys.path:
    sys.path.insert(0, str(_GTKB_SRC))

from groundtruth_kb.bridge.versioned_files import scan_expected_documents, status_from_bridge_file  # noqa: E402

TERMINAL_STATUSES = frozenset({"VERIFIED"})
AWAITING_PRIME_STATUSES = frozenset({"NO-GO", "GO"})
AWAITING_LO_STATUSES = frozenset({"NEW", "REVISED"})
AWAITING_PRIME_DIALOGUE_STATUSES = frozenset({"ADVISORY"})
_TRUE_ENV_VALUES = {"1", "true", "yes", "on"}


def _now_utc() -> datetime:
    return datetime.now(UTC)


def _bridge_dir(project_root: Path) -> Path:
    return project_root / "bridge"


def _state_sha256(rows: list[dict[str, Any]]) -> str:
    payload = json.dumps(rows, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _git_committer_iso(path: Path, project_root: Path, *, reverse: bool = False) -> str | None:
    if os.environ.get("GTKB_BRIDGE_SWIMLANE_USE_GIT_TIMESTAMPS", "").strip().lower() not in _TRUE_ENV_VALUES:
        return None
    if "PYTEST_CURRENT_TEST" in os.environ and project_root.resolve() == _REPO_ROOT.resolve():
        return None
    rel = path.relative_to(project_root).as_posix() if path.is_absolute() else str(path)
    args = ["git", "log", "--format=%cI"]
    if reverse:
        args.append("--reverse")
    args.extend(["--", rel])
    try:
        completed = subprocess.run(
            args,
            cwd=str(project_root),
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if completed.returncode != 0:
        return None
    out = completed.stdout.strip()
    if not out:
        return None
    return out.splitlines()[0].strip() or None


def _mtime_iso(path: Path) -> str | None:
    try:
        ts = path.stat().st_mtime
    except OSError:
        return None
    return datetime.fromtimestamp(ts, UTC).isoformat()


def _resolve_timestamp(
    bridge_path: Path,
    project_root: Path,
    *,
    reverse: bool = False,
) -> str | None:
    """Prefer git committer date; fall back to filesystem mtime."""
    git_value = _git_committer_iso(bridge_path, project_root, reverse=reverse)
    if git_value:
        return git_value
    return _mtime_iso(bridge_path)


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    text = value.strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed


def _age_in_state_minutes(last_updated: str | None, now: datetime) -> int | None:
    parsed = _parse_iso(last_updated)
    if parsed is None:
        return None
    delta = now - parsed
    return max(int(delta.total_seconds() // 60), 0)


def _classify(status: str) -> tuple[bool, bool, bool, bool]:
    """Return (is_terminal, awaiting_prime, awaiting_lo, awaiting_prime_dialogue)."""
    return (
        status in TERMINAL_STATUSES,
        status in AWAITING_PRIME_STATUSES,
        status in AWAITING_LO_STATUSES,
        status in AWAITING_PRIME_DIALOGUE_STATUSES,
    )


def _thread_record(
    slug: str,
    files: tuple[str, ...],
    latest_version: int,
    project_root: Path,
    now: datetime,
) -> dict[str, Any] | None:
    if not files:
        return None
    latest_rel = files[-1]
    latest_filename = Path(latest_rel).name
    bridge_path = project_root / latest_rel
    status = status_from_bridge_file(bridge_path)
    if status is None:
        return None
    first_filename = f"{slug}-001.md"
    first_path = _bridge_dir(project_root) / first_filename

    last_updated_at = _resolve_timestamp(bridge_path, project_root, reverse=False)
    first_seen_at = _resolve_timestamp(first_path, project_root, reverse=True)
    is_terminal, awaiting_prime, awaiting_lo, awaiting_prime_dialogue = _classify(status)

    return {
        "document": slug,
        "latest_status": status,
        "latest_filename": latest_filename,
        "latest_version": latest_version,
        "version_count": len(files),
        "first_seen_at": first_seen_at,
        "last_updated_at": last_updated_at,
        "age_in_state_minutes": _age_in_state_minutes(last_updated_at, now),
        "is_terminal": is_terminal,
        "awaiting_prime": awaiting_prime,
        "awaiting_lo": awaiting_lo,
        "awaiting_prime_dialogue": awaiting_prime_dialogue,
    }


def _summarize(threads: list[dict[str, Any]]) -> dict[str, Any]:
    open_threads = [t for t in threads if not t["is_terminal"]]
    awaiting_prime = sum(1 for t in threads if t["awaiting_prime"])
    awaiting_lo = sum(1 for t in threads if t["awaiting_lo"])
    awaiting_prime_dialogue = sum(1 for t in threads if t["awaiting_prime_dialogue"])
    open_ages = [t["age_in_state_minutes"] for t in open_threads if t["age_in_state_minutes"] is not None]
    return {
        "thread_count": len(threads),
        "terminal_count": sum(1 for t in threads if t["is_terminal"]),
        "open_count": len(open_threads),
        "awaiting_prime_count": awaiting_prime,
        "awaiting_lo_count": awaiting_lo,
        "awaiting_prime_dialogue_count": awaiting_prime_dialogue,
        "advisory_count": awaiting_prime_dialogue,
        "oldest_open_minutes": max(open_ages) if open_ages else None,
    }


def generate_swimlane(project_root: Path) -> dict[str, Any]:
    """Read numbered bridge files fresh and return the swimlane snapshot dict."""
    project_root = project_root.resolve()
    documents = scan_expected_documents(project_root)
    now = _now_utc()
    threads: list[dict[str, Any]] = []
    state_rows: list[dict[str, Any]] = []
    for slug, doc in sorted(documents.items()):
        record = _thread_record(slug, doc.files, doc.latest_version, project_root, now)
        if record is not None:
            threads.append(record)
            state_rows.append(
                {
                    "document": slug,
                    "latest_status": record["latest_status"],
                    "latest_file": record["latest_filename"],
                    "latest_version": record["latest_version"],
                    "version_count": record["version_count"],
                }
            )
    return {
        "generated_at": now.isoformat(),
        "source_state_sha": _state_sha256(state_rows),
        "threads": threads,
        "summary": _summarize(threads),
    }


def _atomic_write_text(target: Path, text: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, target)


def write_swimlane(project_root: Path, out_path: Path) -> dict[str, Any]:
    """Generate the swimlane snapshot and write it atomically to ``out_path``."""
    snapshot = generate_swimlane(project_root)
    _atomic_write_text(out_path, json.dumps(snapshot, indent=2, sort_keys=True) + "\n")
    return snapshot


def _default_out_path(project_root: Path) -> Path:
    return project_root / "docs" / "gtkb-dashboard" / "bridge-swimlane.json"


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Generate bridge state swimlane JSON.")
    parser.add_argument("--project-root", type=Path, default=_REPO_ROOT)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)
    out_path = args.out or _default_out_path(args.project_root.resolve())
    snapshot = write_swimlane(args.project_root.resolve(), out_path)
    print(json.dumps({"out": str(out_path), "thread_count": snapshot["summary"]["thread_count"]}))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())
