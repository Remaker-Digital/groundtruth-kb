"""The canonical reconciliation guidance exposes working read-only CLI routes."""

from __future__ import annotations

import re
import shlex
from pathlib import Path

import pytest
from click.testing import CliRunner
from groundtruth_kb.cli import main

REPO_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_SKILL = REPO_ROOT / ".harness-baseline-configuration/skills/gtkb-bridge-reconciliation/SKILL.md"


@pytest.mark.parametrize("native", [False, True])
def test_reconciliation_examples_resolve_in_the_configured_cli(native, tmp_path):
    config = tmp_path / "groundtruth.toml"
    config.write_text('authority_url = "http://127.0.0.1:1"\n' if native else "", encoding="utf-8")
    commands = re.findall(r"^gt (.+)$", CANONICAL_SKILL.read_text(encoding="utf-8"), re.MULTILINE)
    assert len(commands) == 3
    runner = CliRunner()
    for command in commands:
        result = runner.invoke(main, ["--config", str(config), *shlex.split(command), "--help"])
        assert result.exit_code == 0, result.output
        assert "--json" in result.output
    assert sorted(path.name for path in tmp_path.iterdir()) == ["groundtruth.toml"]
