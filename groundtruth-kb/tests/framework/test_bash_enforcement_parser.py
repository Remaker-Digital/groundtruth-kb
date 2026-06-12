"""Tests for the bash command enforcement parser."""

from __future__ import annotations

from pathlib import Path

from groundtruth_kb.enforcement import check_bash_command

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_bash_parser_allowed_cmd() -> None:
    allowed, reason = check_bash_command("git status", REPO_ROOT)
    assert allowed is True
    assert reason == ""

    allowed, reason = check_bash_command("python -m pytest tests/", REPO_ROOT)
    assert allowed is True
    assert reason == ""


def test_bash_parser_blocked_path() -> None:
    # Commands trying to write outside the root using redirection or referencing blocked paths
    allowed, reason = check_bash_command(
        "cat bridge/INDEX.md > C:\\Users\\Administrator\\Desktop\\index.txt", REPO_ROOT
    )
    assert allowed is False
    assert "Command contains blocked redirection target" in reason

    allowed, reason = check_bash_command("ls /etc/passwd", REPO_ROOT)
    assert allowed is False
    assert "Command contains blocked path argument" in reason
