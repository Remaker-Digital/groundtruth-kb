"""Tests for ``scripts/gtkb_dashboard/generate_bridge_swimlane.py``.

Slice 2.1 of GTKB-DASHBOARD-002 — see
``bridge/gtkb-dashboard-industry-alignment-slice2a-visibility-005.md``.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.gtkb_dashboard import generate_bridge_swimlane as gbs


# ----------------------------- helpers -----------------------------


def _seed_index(project_root: Path, body: str) -> Path:
    bridge = project_root / "bridge"
    bridge.mkdir(parents=True, exist_ok=True)
    index = bridge / "INDEX.md"
    index.write_text(body, encoding="utf-8")
    return index


def _seed_bridge_file(project_root: Path, name: str, content: str = "stub") -> Path:
    path = project_root / "bridge" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _git(args: list[str], cwd: Path) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, "GIT_AUTHOR_NAME": "Test", "GIT_AUTHOR_EMAIL": "t@t",
             "GIT_COMMITTER_NAME": "Test", "GIT_COMMITTER_EMAIL": "t@t"},
    )
    return completed.stdout.strip()


def _init_repo(project_root: Path) -> None:
    _git(["init", "-q"], project_root)
    _git(["config", "user.email", "t@t"], project_root)
    _git(["config", "user.name", "Test"], project_root)
    _git(["config", "commit.gpgsign", "false"], project_root)


def _commit_all(project_root: Path, *, message: str, when: str | None = None) -> str:
    _git(["add", "-A"], project_root)
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "Test",
        "GIT_AUTHOR_EMAIL": "t@t",
        "GIT_COMMITTER_NAME": "Test",
        "GIT_COMMITTER_EMAIL": "t@t",
    }
    if when:
        env["GIT_AUTHOR_DATE"] = when
        env["GIT_COMMITTER_DATE"] = when
    completed = subprocess.run(
        ["git", "commit", "--quiet", "-m", message],
        cwd=str(project_root),
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    return completed.stdout


# ----------------------------- tests -----------------------------


def test_generate_swimlane_empty_index(tmp_path: Path) -> None:
    _seed_index(tmp_path, "")
    snapshot = gbs.generate_swimlane(tmp_path)
    assert snapshot["threads"] == []
    assert snapshot["summary"]["thread_count"] == 0
    assert snapshot["summary"]["open_count"] == 0
    assert snapshot["summary"]["oldest_open_minutes"] is None


def test_generate_swimlane_single_thread(tmp_path: Path) -> None:
    body = (
        "Document: foo-bar\n"
        "NEW: bridge/foo-bar-001.md\n"
    )
    _seed_index(tmp_path, body)
    _seed_bridge_file(tmp_path, "foo-bar-001.md")
    snapshot = gbs.generate_swimlane(tmp_path)
    assert len(snapshot["threads"]) == 1
    thread = snapshot["threads"][0]
    assert thread["document"] == "foo-bar"
    assert thread["latest_status"] == "NEW"
    assert thread["latest_filename"] == "foo-bar-001.md"
    assert thread["latest_version"] == 1
    assert thread["version_count"] == 1
    assert thread["is_terminal"] is False
    assert thread["awaiting_lo"] is True
    assert thread["awaiting_prime"] is False


def test_generate_swimlane_multi_version(tmp_path: Path) -> None:
    body_lines = ["Document: alpha"]
    statuses = ["VERIFIED", "NEW", "GO", "REVISED", "NO-GO"]
    for idx, status in enumerate(statuses, start=1):
        version = len(statuses) - idx + 1
        body_lines.append(f"{status}: bridge/alpha-{version:03d}.md")
        _seed_bridge_file(tmp_path, f"alpha-{version:03d}.md")
    _seed_index(tmp_path, "\n".join(body_lines) + "\n")
    snapshot = gbs.generate_swimlane(tmp_path)
    thread = snapshot["threads"][0]
    assert thread["latest_status"] == "VERIFIED"
    assert thread["latest_version"] == 5
    assert thread["version_count"] == 5
    assert thread["is_terminal"] is True


def test_generate_swimlane_terminality(tmp_path: Path) -> None:
    body = "\n".join([
        "Document: aa",
        "VERIFIED: bridge/aa-001.md",
        "",
        "Document: bb",
        "NO-GO: bridge/bb-001.md",
        "",
        "Document: cc",
        "GO: bridge/cc-001.md",
        "",
        "Document: dd",
        "NEW: bridge/dd-001.md",
        "",
        "Document: ee",
        "REVISED: bridge/ee-001.md",
        "",
    ]) + "\n"
    _seed_index(tmp_path, body)
    for name in ("aa-001.md", "bb-001.md", "cc-001.md", "dd-001.md", "ee-001.md"):
        _seed_bridge_file(tmp_path, name)
    snapshot = gbs.generate_swimlane(tmp_path)
    by_doc = {t["document"]: t for t in snapshot["threads"]}
    assert by_doc["aa"]["is_terminal"] is True and by_doc["aa"]["awaiting_prime"] is False
    assert by_doc["bb"]["awaiting_prime"] is True and by_doc["bb"]["awaiting_lo"] is False
    assert by_doc["cc"]["awaiting_prime"] is True and by_doc["cc"]["is_terminal"] is False
    assert by_doc["dd"]["awaiting_lo"] is True and by_doc["dd"]["awaiting_prime"] is False
    assert by_doc["ee"]["awaiting_lo"] is True


def test_generate_swimlane_summary_counts(tmp_path: Path) -> None:
    statuses = ["VERIFIED", "VERIFIED", "VERIFIED", "VERIFIED",
                "NO-GO", "GO", "NEW", "NEW", "REVISED", "REVISED"]
    body_lines: list[str] = []
    for idx, status in enumerate(statuses, start=1):
        body_lines.append(f"Document: thread-{idx:02d}")
        body_lines.append(f"{status}: bridge/thread-{idx:02d}-001.md")
        body_lines.append("")
        _seed_bridge_file(tmp_path, f"thread-{idx:02d}-001.md")
    _seed_index(tmp_path, "\n".join(body_lines) + "\n")
    snapshot = gbs.generate_swimlane(tmp_path)
    summary = snapshot["summary"]
    assert summary["thread_count"] == 10
    assert summary["terminal_count"] == 4
    assert summary["open_count"] == 6
    assert summary["awaiting_prime_count"] == 2  # NO-GO + GO
    assert summary["awaiting_lo_count"] == 4  # 2 NEW + 2 REVISED


def test_generate_swimlane_age_from_git(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    body = "Document: zz\nNEW: bridge/zz-001.md\n"
    _seed_index(tmp_path, body)
    _seed_bridge_file(tmp_path, "zz-001.md", "v1")
    # Commit with controlled timestamp 10 minutes ago.
    when = "2026-04-24T15:00:00+0000"
    _commit_all(tmp_path, message="seed", when=when)
    snapshot = gbs.generate_swimlane(tmp_path)
    thread = snapshot["threads"][0]
    assert thread["last_updated_at"] is not None
    # Age computed from now → at least many minutes since 2026-04-24.
    # We just assert it's an integer ≥ 0 and last_updated_at parses.
    assert thread["age_in_state_minutes"] is not None
    assert thread["age_in_state_minutes"] >= 0
    # Check git committer ISO format roundtrip.
    parsed = gbs._parse_iso(thread["last_updated_at"])
    assert parsed is not None


def test_generate_swimlane_age_fallback_to_mtime(tmp_path: Path) -> None:
    body = "Document: yy\nNEW: bridge/yy-001.md\n"
    _seed_index(tmp_path, body)
    bridge_file = _seed_bridge_file(tmp_path, "yy-001.md")
    # No git repo initialized → git log returns nothing → fall back to mtime.
    # Force mtime to a known recent value.
    past = time.time() - 600  # 10 minutes ago
    os.utime(bridge_file, (past, past))
    snapshot = gbs.generate_swimlane(tmp_path)
    thread = snapshot["threads"][0]
    assert thread["last_updated_at"] is not None
    age = thread["age_in_state_minutes"]
    assert age is not None and age >= 8


def test_generate_swimlane_index_sha(tmp_path: Path) -> None:
    body = "Document: hh\nNEW: bridge/hh-001.md\n"
    _seed_index(tmp_path, body)
    _seed_bridge_file(tmp_path, "hh-001.md")
    snapshot = gbs.generate_swimlane(tmp_path)
    expected = hashlib.sha256(body.encode("utf-8")).hexdigest()
    assert snapshot["source_index_sha"] == expected


def test_write_swimlane_atomic(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    body = "Document: ii\nNEW: bridge/ii-001.md\n"
    _seed_index(tmp_path, body)
    _seed_bridge_file(tmp_path, "ii-001.md")
    out = tmp_path / "out" / "bridge-swimlane.json"
    # First, write it once successfully.
    gbs.write_swimlane(tmp_path, out)
    original = out.read_text(encoding="utf-8")
    assert "ii" in original

    def _boom(_src: str, _dst: str) -> None:
        raise OSError("simulated atomic-write crash")

    monkeypatch.setattr(gbs.os, "replace", _boom)
    with pytest.raises(OSError):
        gbs.write_swimlane(tmp_path, out)
    # Original target file is intact.
    assert out.read_text(encoding="utf-8") == original


def test_generate_swimlane_handles_malformed_index(tmp_path: Path) -> None:
    body = (
        "Document: good\n"
        "NEW: bridge/good-001.md\n"
        "garbage line that is not a valid status\n"
        "NEW: NOT-A-VALID-PATH\n"
        "Document: also-good\n"
        "NEW: bridge/also-good-001.md\n"
    )
    _seed_index(tmp_path, body)
    _seed_bridge_file(tmp_path, "good-001.md")
    _seed_bridge_file(tmp_path, "also-good-001.md")
    snapshot = gbs.generate_swimlane(tmp_path)
    docs = sorted(t["document"] for t in snapshot["threads"])
    assert docs == ["also-good", "good"]
    # Sanity: even a totally-binary index doesn't crash.
    binary_index = tmp_path / "bridge" / "INDEX.md"
    binary_index.write_bytes(b"\x00\x01\x02not utf at all\xff")
    snapshot2 = gbs.generate_swimlane(tmp_path)
    assert snapshot2["threads"] == []
