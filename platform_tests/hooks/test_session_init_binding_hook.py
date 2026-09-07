from __future__ import annotations

import importlib.util
import io
import json
import sqlite3
import sys
import tomllib
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
HOOK_PATHS = (
    PROJECT_ROOT / ".harness-baseline-configuration" / "hooks" / "session-init-binding.py",
    PROJECT_ROOT / ".claude" / "hooks" / "session-init-binding.py",
    PROJECT_ROOT / ".codex" / "gtkb-hooks" / "session-init-binding.py",
)


def test_exact_init_hook_is_first_in_live_prompt_registrations():
    with (PROJECT_ROOT / ".harness-baseline-configuration" / "hooks" / "manifest.toml").open("rb") as handle:
        manifest = tomllib.load(handle)
    prompt_hooks = [hook for hook in manifest["hook"] if hook["event"] == "prompt_submit"]
    assert prompt_hooks[0]["script"] == "session-init-binding.py"

    settings = json.loads((PROJECT_ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
    claude_first = settings["hooks"]["UserPromptSubmit"][0]["hooks"][0]["command"]
    assert claude_first.endswith('/.claude/hooks/session-init-binding.py"')

    for runner_path in (
        PROJECT_ROOT / ".harness-baseline-configuration" / "gtkb-hooks" / "run_py_no_window.py",
        PROJECT_ROOT / ".codex" / "gtkb-hooks" / "run_py_no_window.py",
    ):
        runner = _load_hook(runner_path)
        assert runner.BATCHES["user-prompt-submit"][0] == (
            "py",
            ".codex/gtkb-hooks/session-init-binding.py",
        )


def _load_hook(path: Path):
    spec = importlib.util.spec_from_file_location(f"session_init_binding_{path.parent.name}", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run(module, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], root: Path, payload: dict):
    monkeypatch.setattr(module, "discover_project_root", lambda start=None: root)
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(payload)))
    assert module.main() == 0
    return json.loads(capsys.readouterr().out)


def _rows(db: Path) -> list[tuple]:
    """Read what the hook actually wrote: the immutable binding, role included.

    This previously also read a separate ``session_role_attestations`` table.
    WI-6940 (commit ``e1bdcf0f5``) removed that surface because the retirement of
    ``ADR-SESSION-ROLE-ATTESTATION-SERVICE-001`` forbids retaining "its separate
    attestation log, role-change, registry fallback, or migration design", and
    ``DCL-SESSION-ROLE-RESOLUTION-001`` v9 resolves role from the immutable
    binding alone. The live table held zero rows when it went.

    The role assertion is kept rather than dropped, sourced from the binding's
    own ``role`` column, which is where the DCL says it lives. Only the retired
    table's ``source_event`` is gone.
    """
    with sqlite3.connect(db) as conn:
        return conn.execute(
            "SELECT native_context_id, subject, role FROM session_init_bindings ORDER BY native_context_id"
        ).fetchall()


@pytest.mark.parametrize("hook_path", HOOK_PATHS, ids=lambda path: path.parent.as_posix())
def test_exact_complete_prompt_binds_once(hook_path, tmp_path, monkeypatch, capsys):
    module = _load_hook(hook_path)
    payload = {"session_id": "ctx-exact", "prompt": "::init gtkb pb"}

    output = _run(module, monkeypatch, capsys, tmp_path, payload)

    assert output == {"systemMessage": "GT-KB exact-init session binding established."}
    assert _rows(tmp_path / "groundtruth.db") == [("ctx-exact", "gtkb", "prime-builder")]

    output = _run(module, monkeypatch, capsys, tmp_path, payload)
    assert output == {}
    assert _rows(tmp_path / "groundtruth.db") == [("ctx-exact", "gtkb", "prime-builder")]


@pytest.mark.parametrize("hook_path", HOOK_PATHS, ids=lambda path: path.parent.as_posix())
@pytest.mark.parametrize(
    "prompt",
    (
        "::init gtkb pb\nextra",
        "prefix\n::init gtkb pb",
        " ::init gtkb pb",
        "::init gtkb pb ",
        "::init gtkb",
    ),
)
def test_non_exact_or_multiline_prompt_creates_nothing(hook_path, prompt, tmp_path, monkeypatch, capsys):
    """A near miss still binds nothing, and now says so (WI-6499).

    The strictness under test is unchanged: none of these forms may create a
    binding, a session id, or a role. What changed is that the refusal is
    audible. Each of these was previously answered with an empty payload, so a
    session that typed the init line alongside anything else carried on
    believing it had declared a role.
    """
    module = _load_hook(hook_path)

    output = _run(module, monkeypatch, capsys, tmp_path, {"session_id": "ctx-invalid", "prompt": prompt})

    assert "no session binding was created" in output["systemMessage"]
    assert "::init <gtkb|application> <pb|lo>" in output["systemMessage"]
    assert not (tmp_path / "groundtruth.db").exists()


@pytest.mark.parametrize("hook_path", HOOK_PATHS, ids=lambda path: path.parent.as_posix())
@pytest.mark.parametrize("prompt", ("fix the failing test", "", "init gtkb pb", "look at ::open build"))
def test_prompt_that_does_not_resemble_init_stays_silent(hook_path, prompt, tmp_path, monkeypatch, capsys):
    """Disclosure is scoped to near misses, so ordinary prompts cost nothing.

    Without this the branch would narrate on every turn, and a message that
    appears constantly is one nobody reads by the time it matters.
    """
    module = _load_hook(hook_path)

    output = _run(module, monkeypatch, capsys, tmp_path, {"session_id": "ctx-plain", "prompt": prompt})

    assert output == {}
    assert not (tmp_path / "groundtruth.db").exists()


@pytest.mark.parametrize("hook_path", HOOK_PATHS, ids=lambda path: path.parent.as_posix())
def test_exact_prompt_without_session_id_is_visible_and_writes_nothing(hook_path, tmp_path, monkeypatch, capsys):
    module = _load_hook(hook_path)

    output = _run(module, monkeypatch, capsys, tmp_path, {"prompt": "::init gtkb lo"})

    assert "could not create its immutable session binding" in output["systemMessage"]
    assert not (tmp_path / "groundtruth.db").exists()


@pytest.mark.parametrize("hook_path", HOOK_PATHS, ids=lambda path: path.parent.as_posix())
def test_exact_hook_binding_unblocks_go_implementation_claim_admission(hook_path, tmp_path, monkeypatch, capsys):
    """Exercise the claim admission boundary without depending on bridge parsing.

    WI-6541 owns marker-first bridge-head resolution. This fixture isolates the
    WI-6496/WI-6499 defect by supplying the already-resolved GO state and proving
    the binding written by the live hook is sufficient for a real persisted
    go_implementation claim.
    """
    module = _load_hook(hook_path)
    session_id = "ctx-go-claim"
    output = _run(
        module,
        monkeypatch,
        capsys,
        tmp_path,
        {"session_id": session_id, "prompt": "::init gtkb pb"},
    )
    assert output == {"systemMessage": "GT-KB exact-init session binding established."}

    from scripts import bridge_work_intent_registry as registry

    monkeypatch.setattr(registry, "_latest_status", lambda slug, project_root=None: "GO")
    monkeypatch.setattr(registry, "project_id_for_thread", lambda slug, project_root=None: "PROJECT-FIXTURE")

    assert registry.acquire("exact-init-go-claim", session_id, project_root=tmp_path)
    holder = registry.current_holder("exact-init-go-claim", project_root=tmp_path)
    assert holder is not None
    assert holder["claim_kind"] == registry.CLAIM_KIND_GO_IMPLEMENTATION
    assert holder["acting_role"] == "prime-builder"
    assert holder["session_envelope_id"]
    # WI-6940 replaced the retired "role-attestation:" prefix with one naming the
    # immutable binding the role now resolves from.
    assert holder["acting_role_attestation"].startswith("session-binding:")

    registry.release("exact-init-go-claim", session_id, project_root=tmp_path)
    assert registry.current_holder("exact-init-go-claim", project_root=tmp_path) is None
