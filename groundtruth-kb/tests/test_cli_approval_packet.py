"""Tests for the approval-packet generation CLI."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from click.testing import CliRunner

from groundtruth_kb.cli import main

REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKER = REPO_ROOT / "scripts" / "check_narrative_artifact_evidence.py"


def _project(root: Path) -> Path:
    config = root / "groundtruth.toml"
    config.write_text(
        '[groundtruth]\ndb_path = "./groundtruth.db"\nproject_root = "."\n',
        encoding="utf-8",
    )
    approval_config = root / "config" / "governance" / "narrative-artifact-approval.toml"
    approval_config.parent.mkdir(parents=True, exist_ok=True)
    approval_config.write_text(
        (REPO_ROOT / "config" / "governance" / "narrative-artifact-approval.toml").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
    return config


def test_generate_narrative_packet_allows_crlf_staged_target_without_gitattributes(tmp_path: Path) -> None:
    config = _project(tmp_path)
    target = tmp_path / ".claude" / "rules" / "example.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"approved narrative content\r\nsecond line\r\n")

    out = ".groundtruth/formal-artifact-approvals/generated-crlf.json"
    result = CliRunner().invoke(
        main,
        [
            "--config",
            str(config),
            "generate-approval-packet",
            "--kind",
            "narrative",
            "--target",
            ".claude/rules/example.md",
            "--artifact-id",
            "generated-crlf",
            "--action",
            "update",
            "--source-ref",
            "bridge/gtkb-wi4720-narrative-packet-staged-eol-parity-002.md",
            "--explicit-change-request",
            "Owner-visible approval text recorded in the transcript.",
            "--change-reason",
            "test generated narrative approval packet",
            "--approval-mode",
            "approve",
            "--changed-by",
            "codex/test",
            "--out",
            out,
            "--json",
        ],
    )
    assert result.exit_code == 0, result.output
    packet = json.loads(result.output)["approval_packet"]
    assert packet["full_content"] == "approved narrative content\nsecond line\n"

    subprocess.run(
        ["git", "-c", "core.autocrlf=false", "add", "--", ".claude/rules/example.md", out],
        cwd=tmp_path,
        check=True,
    )
    check = subprocess.run(
        [sys.executable, str(CHECKER), "--staged", "--json", "--project-root", str(tmp_path)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert check.returncode == 0, check.stderr
    payload = json.loads(check.stdout)
    assert payload["status"] == "pass"
    assert ".claude/rules/example.md" in payload["cleared"]
