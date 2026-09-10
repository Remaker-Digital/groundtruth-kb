"""Native project finalization executes the complete current normal hook sequence."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import groundtruth_kb
import pytest

from platform_tests.groundtruth_kb.test_native_commit_boundary import (
    base,
    git,
    integration,
    invoke,
)
from platform_tests.groundtruth_kb.test_native_commit_boundary import (
    bridge as bridge,
)
from platform_tests.groundtruth_kb.test_native_commit_boundary import (
    commit_environment as commit_environment,
)
from platform_tests.groundtruth_kb.test_native_commit_boundary import (
    native as native,
)

ROOT = Path(__file__).resolve().parents[2]
pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]


@pytest.mark.parametrize("commit_environment", [False, True], indirect=True, ids=["content", "executable"])
def test_native_project_commit_runs_actual_normal_hooks_preserving_foreign_index(
    commit_environment, monkeypatch, request
):
    client, root, parent, checkout, hooks, config, message = commit_environment
    for name in [
        "pre-commit",
        "pre-commit-ps1-parse.ps1",
    ]:
        shutil.copyfile(ROOT / ".githooks" / name, hooks / name)
    for name in [
        "scan_secrets.py",
        "check_ruff_format.py",
        "check_commit_pathspec_safety.py",
        "check_projection_drift.py",
    ]:
        target = checkout / "scripts" / name
        target.parent.mkdir(exist_ok=True)
        shutil.copyfile(ROOT / "scripts" / name, target)
    (hooks / "pre-commit").chmod(0o755)
    monkeypatch.setenv("PYTHON", sys.executable)
    monkeypatch.setenv("PYTHONPATH", str(Path(groundtruth_kb.__file__).resolve().parent.parent))
    monkeypatch.setenv("PYTHONIOENCODING", "utf-8")
    foreign = checkout / "foreign_tracked.txt"
    foreign.write_text("foreign staged work\n", encoding="utf-8", newline="\n")
    git(checkout, "add", "--", foreign.name)
    foreign.write_bytes(b"foreign unstaged work\x00")
    foreign_index = git(checkout, "ls-files", "--stage", "--", foreign.name).stdout
    result = invoke(config, message)
    assert result.exit_code == 0, (result.output, result.exception)
    assert base(checkout) != parent
    assert base(checkout) == base(integration(root))
    assert git(checkout, "ls-files", "--stage", "--", foreign.name).stdout == foreign_index
    assert git(checkout, "diff", "--cached", "--name-only").stdout.strip() == foreign.name
    assert foreign.read_bytes() == b"foreign unstaged work\x00"
    assert git(checkout, "show", ":foreign_tracked.txt").stdout == "foreign staged work\n"
    assert git(checkout, "diff", "--name-only", parent, "HEAD").stdout.splitlines() == ["code.py", "second.py"]
    mode = "100755" if request.node.callspec.params["commit_environment"] else "100644"
    assert git(checkout, "ls-tree", "HEAD", "--", "code.py").stdout.startswith(mode + " blob ")
    assert client.get("/v1/projects/PROJECT-1").json()["project"]["status"] == "verified"
