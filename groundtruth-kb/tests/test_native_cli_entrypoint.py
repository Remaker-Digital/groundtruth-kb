"""Cold native CLI loading must not import dormant legacy command machinery."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import groundtruth_kb


def test_every_ordinary_command_help_loads_without_legacy_consumers(tmp_path):
    script = r"""
import importlib.abc
import json
import sys
from click.testing import CliRunner

retired = (
    "groundtruth_kb.cli_approval_packet", "groundtruth_kb.cli_session_handoff",
    "groundtruth_kb.cli_skills", "groundtruth_kb.cli_bridge_propose",
    "groundtruth_kb.activity.profiles", "groundtruth_kb.policy",
    "groundtruth_kb.owner_approval_surface", "groundtruth_kb.typed_artifact_flow",
    "groundtruth_kb.session.topic_router",
)
class RefuseLegacy(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if any(fullname == name or fullname.startswith(name + ".") for name in retired):
            raise AssertionError("Ordinary CLI imported a retired consumer: " + fullname)
        return None
sys.meta_path.insert(0, RefuseLegacy())
from groundtruth_kb.cli import main

runner = CliRunner()
results = []
def check(command, arguments):
    result = runner.invoke(main, [*arguments, "--help"])
    assert result.exit_code == 0, (arguments, result.output, result.exception)
    assert "Usage:" in result.output
    results.append(" ".join(arguments))
    if hasattr(command, "commands"):
        for name, child in command.commands.items():
            check(child, [*arguments, name])
for name, command in main._commands().items():
    check(command, [name])
assert "hygiene worktrees" in results
assert "bridge check-effects" in results
assert "test-phases list" in results
assert "session bind" in results
assert not any(name in sys.modules for name in retired)
print(json.dumps(results))
"""
    env = dict(os.environ, PYTHONPATH=str(Path(groundtruth_kb.__file__).resolve().parent.parent))
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=tmp_path,
        env=env,
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=30,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    assert result.returncode == 0, result.stdout + result.stderr
    commands = json.loads(result.stdout)
    assert len(commands) == len(set(commands))
    assert not list(tmp_path.iterdir())
