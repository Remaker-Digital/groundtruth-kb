"""Commit validation uses staged source bytes, not installed projection state."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


GATE = load(REPO_ROOT / "scripts/check_projection_drift.py", "projection_gate")
PROJECTOR = load(REPO_ROOT / "scripts/harness_projection/project_harness.py", "projection_engine")


@pytest.mark.parametrize("harness", GATE.renderable_harnesses(REPO_ROOT))
def test_rendered_harness_does_not_require_registry_observation_receipts(harness):
    plan = PROJECTOR.build_plan(harness)
    assert not plan.gaps, plan.gaps
    assert plan.writes
    assert all("registry_observation_hook.py" not in content for content in plan.writes.values())


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True)


def write(root, rel, text):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture
def project(tmp_path):
    git(tmp_path, "init", "-q")
    write(
        tmp_path,
        "scripts/harness_projection/profiles.toml",
        "[harnesses.claude]\n[harnesses.pending]\nstatus='profile_pending'\n",
    )
    write(
        tmp_path,
        "scripts/harness_projection/project_harness.py",
        """import sys
from pathlib import Path
assert sys.argv[-1] == '--validate'
source = Path('.harness-baseline-configuration/rules/rule.md').read_text()
if source != 'valid':
    print('unresolved source token', file=sys.stderr)
    sys.exit(2)
""",
    )
    write(tmp_path, ".harness-baseline-configuration/rules/rule.md", "valid")
    git(tmp_path, "add", ".")
    return tmp_path


def test_absent_and_stale_projections_do_not_gate_source_commit(project):
    assert not (project / ".claude").exists()
    assert GATE.main(["--staged", "--project-root", str(project)]) == 0
    write(project, ".claude/rules/rule.md", "stale installed output")
    assert GATE.main(["--staged", "--project-root", str(project)]) == 0
    assert (project / ".claude/rules/rule.md").read_text() == "stale installed output"


def test_unstaged_source_defect_does_not_replace_staged_bytes(project):
    write(project, ".harness-baseline-configuration/rules/rule.md", "broken unstaged source")
    assert GATE.main(["--staged", "--project-root", str(project)]) == 0


def test_unstaged_repair_does_not_hide_staged_defect(project, capsys):
    write(project, ".harness-baseline-configuration/rules/rule.md", "broken staged source")
    git(project, "add", ".harness-baseline-configuration/rules/rule.md")
    write(project, ".harness-baseline-configuration/rules/rule.md", "valid")
    assert GATE.main(["--staged", "--project-root", str(project)]) == 1
    assert "unresolved source token" in capsys.readouterr().err


def test_staged_profile_removal_is_a_failure(project):
    git(project, "rm", "-f", "scripts/harness_projection/profiles.toml")
    assert GATE.main(["--staged", "--project-root", str(project)]) == 1


@pytest.mark.parametrize(
    "staged, validated",
    [(".agents/skills/x/SKILL.md", True), ("AGENTS.md", False), ("CLAUDE.md", False), (".goosehints", False)],
)
def test_staged_skill_source_triggers_validation(project, monkeypatch, staged, validated):
    """D15: a staged stub source re-validates every profile; the root carriers are not projection inputs."""
    assert GATE.projection_source(".agents/skills/x/SKILL.md") and GATE.projection_source(
        ".harness-baseline-configuration/rules/r.md"
    )
    assert not any(
        GATE.projection_source(path) for path in ("AGENTS.md", "CLAUDE.md", ".goosehints", ".agents/other.md")
    )
    git(project, "-c", "user.email=test@invalid.example", "-c", "user.name=Test", "commit", "-qm", "base")
    write(project, staged, "---\nname: x\ndescription: X.\n---\n" if validated else "pointer bytes\n")
    git(project, "add", "--", staged)
    calls: list[str] = []
    monkeypatch.setattr(GATE, "check_harness", lambda _root, harness: (calls.append(harness), (0, ""))[1])
    assert GATE.main(["--staged", "--project-root", str(project)]) == 0
    assert calls == (["claude"] if validated else [])


def test_no_sources_staged_does_not_run_projector(tmp_path, monkeypatch):
    git(tmp_path, "init", "-q")
    write(tmp_path, "unrelated.py", "pass")
    git(tmp_path, "add", ".")
    monkeypatch.setattr(GATE, "check_harness", lambda *_: pytest.fail("unexpected projector run"))
    assert GATE.main(["--staged", "--project-root", str(tmp_path)]) == 0


def test_index_failure_is_not_a_pass(tmp_path):
    # A pytest temp directory may be inside the repository. Make this a real
    # independent repository and corrupt its index instead of relying on Git
    # failing to discover an ancestor checkout.
    git(tmp_path, "init", "-q")
    (tmp_path / ".git/index").write_bytes(b"invalid git index")
    assert GATE.main(["--staged", "--project-root", str(tmp_path)]) == 1


def test_only_implemented_profiles_are_validated(project):
    assert GATE.renderable_harnesses(project) == ["claude"]


@pytest.mark.parametrize("gaps, expected", [([], 0), (["unresolved baseline token"], 2)])
def test_validate_mode_checks_derivation_without_touching_output(tmp_path, monkeypatch, gaps, expected):
    plan = PROJECTOR.Plan(writes={".claude/rules/rule.md": "rendered"}, removes=[".claude/old.md"], gaps=gaps)
    write(tmp_path, ".claude/old.md", "existing output")
    monkeypatch.setattr(PROJECTOR, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(PROJECTOR, "build_plan", lambda _: plan)
    assert PROJECTOR.run("claude", "validate") == expected
    assert not (tmp_path / ".claude/rules/rule.md").exists()
    assert (tmp_path / ".claude/old.md").read_text() == "existing output"
