"""The worktree scope gate keeps a session's writes inside its own checkout.

The gate is self-migrating by design, so the tests that matter most are the
three allow paths: an unbound actor writes freely, a bound session without a
checkout keeps working and is told how to get one, and only a session that
actually has a checkout is held to it. A gate that denied on day one would have
stopped every session that was already running when it landed.

The deny path is the recurrence guard for commit ``2f688c4ca``.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
GATE_SOURCE = REPO_ROOT / ".harness-baseline-configuration" / "hooks" / "worktree-scope-gate.py"

SENV = "SENV-" + "c" * 32


@pytest.fixture(scope="module")
def gate_script(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """The baseline carries a projection token; substitute it as the projector does."""
    text = GATE_SOURCE.read_text(encoding="utf-8")
    rendered = text.replace("{{HARNESS_PROJECT_DIR_VAR}}", "GTKB_TEST_PROJECT_DIR")
    path = tmp_path_factory.mktemp("gate") / "worktree_scope_gate.py"
    path.write_text(rendered, encoding="utf-8")
    return path


def _run(gate_script: Path, payload: dict, project_root: Path, env_extra: dict | None = None) -> dict:
    env = {
        "GTKB_TEST_PROJECT_DIR": str(project_root),
        "PATH": __import__("os").environ.get("PATH", ""),
        "SYSTEMROOT": __import__("os").environ.get("SYSTEMROOT", ""),
    }
    env.update(env_extra or {})
    result = subprocess.run(
        [sys.executable, str(gate_script)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=env,
        timeout=120,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout or "{}")


def _write_payload(path: Path, tool: str = "Write") -> dict:
    return {"tool_name": tool, "tool_input": {"file_path": str(path), "content": "x"}, "cwd": ""}


@pytest.fixture
def project(tmp_path: Path) -> Path:
    root = tmp_path / "root"
    (root / "scripts").mkdir(parents=True)
    (root / "scripts" / "thing.py").write_text("x = 1\n", encoding="utf-8")
    return root


def test_a_non_write_tool_is_ignored(gate_script: Path, project: Path) -> None:
    payload = {"tool_name": "Read", "tool_input": {"file_path": str(project / "scripts" / "thing.py")}}
    assert _run(gate_script, payload, project) == {}


def test_an_unbound_actor_writes_freely(gate_script: Path, project: Path) -> None:
    """The owner has no init binding, and must not be gated by a session rule."""
    out = _run(gate_script, _write_payload(project / "scripts" / "thing.py"), project)
    assert out == {}


def test_a_write_outside_the_project_root_is_not_this_gates_business(
    gate_script: Path, project: Path, tmp_path: Path
) -> None:
    outside = tmp_path / "elsewhere.txt"
    assert _run(gate_script, _write_payload(outside), project) == {}


def test_the_session_scratch_root_stays_writable(gate_script: Path, project: Path) -> None:
    """Scratch is per-session by contract and is not repository content."""
    target = project / "scratchpad" / "anything" / "file.txt"
    assert _run(gate_script, _write_payload(target), project) == {}


def _install_stub_session(project: Path, session_context_id: str | None) -> dict[str, str]:
    """Give the gate an importable session surface resolving to one binding."""
    src = project / "groundtruth-kb" / "src" / "groundtruth_kb" / "session" / "attestation"
    src.mkdir(parents=True, exist_ok=True)
    for package in (
        project / "groundtruth-kb" / "src" / "groundtruth_kb",
        project / "groundtruth-kb" / "src" / "groundtruth_kb" / "session",
        src,
    ):
        (package / "__init__.py").write_text("", encoding="utf-8")

    resolved = "None" if session_context_id is None else repr(session_context_id)
    (src / "service.py").write_text(
        "class RoleAttestationError(Exception):\n"
        "    pass\n"
        "\n"
        "\n"
        "class _Binding:\n"
        f"    session_context_id = {resolved}\n"
        "\n"
        "\n"
        "def binding_for_context(db_path, native_context_id):\n"
        f"    if {resolved} is None:\n"
        '        raise RoleAttestationError("no_session_binding")\n'
        "    return _Binding()\n",
        encoding="utf-8",
    )

    scripts = project / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    (scripts / "__init__.py").write_text("", encoding="utf-8")
    (scripts / "gtkb_session_id.py").write_text(
        "MARKER_CONTINUITY_ORDER = ('GTKB_SESSION_ID',)\n"
        "\n"
        "\n"
        "def resolve_session_id(explicit=None, *, order=(), environ=None):\n"
        "    return 'native-context'\n",
        encoding="utf-8",
    )
    return {}


def test_a_bound_session_without_a_checkout_keeps_working(gate_script: Path, project: Path) -> None:
    """Self-migrating: sessions already running when this landed are not broken."""
    _install_stub_session(project, SENV)
    out = _run(gate_script, _write_payload(project / "scripts" / "thing.py"), project)
    assert "decision" not in out
    assert "gt session worktree open" in out["systemMessage"]


def test_a_session_with_a_checkout_may_write_inside_it(gate_script: Path, project: Path) -> None:
    _install_stub_session(project, SENV)
    own = project / ".worktrees" / SENV
    (own / "scripts").mkdir(parents=True)
    out = _run(gate_script, _write_payload(own / "scripts" / "thing.py"), project)
    assert out == {}


def test_a_session_with_a_checkout_is_denied_the_shared_tree(gate_script: Path, project: Path) -> None:
    """The recurrence guard: an edit here is live for every concurrent session."""
    _install_stub_session(project, SENV)
    (project / ".worktrees" / SENV).mkdir(parents=True)
    out = _run(gate_script, _write_payload(project / "scripts" / "thing.py"), project)
    assert out["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert f".worktrees/{SENV}" in out["hookSpecificOutput"]["permissionDecisionReason"]
    assert "2f688c4ca" in out["hookSpecificOutput"]["permissionDecisionReason"]


def test_another_sessions_checkout_is_also_denied(gate_script: Path, project: Path) -> None:
    """Isolation runs both ways: a peer's bytes are as protected as the main tree's."""
    _install_stub_session(project, SENV)
    (project / ".worktrees" / SENV).mkdir(parents=True)
    peer = project / ".worktrees" / ("SENV-" + "d" * 32) / "file.txt"
    peer.parent.mkdir(parents=True)
    out = _run(gate_script, _write_payload(peer), project)
    assert out["hookSpecificOutput"]["permissionDecision"] == "deny"


@pytest.mark.parametrize("tool", ["Write", "Edit", "MultiEdit", "NotebookEdit"])
def test_every_write_tool_is_covered(gate_script: Path, project: Path, tool: str) -> None:
    _install_stub_session(project, SENV)
    (project / ".worktrees" / SENV).mkdir(parents=True)
    payload = {"tool_name": tool, "tool_input": {"file_path": str(project / "scripts" / "thing.py")}}
    out = _run(gate_script, payload, project)
    assert out["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_a_broken_session_surface_never_blocks_a_write(gate_script: Path, project: Path) -> None:
    """A partial install must not make the platform unwritable."""
    out = _run(gate_script, _write_payload(project / "scripts" / "thing.py"), project)
    assert out == {}


def test_malformed_input_is_ignored(gate_script: Path, project: Path) -> None:
    assert _run(gate_script, {}, project) == {}
