from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from groundtruth_kb import cursor_harness
from groundtruth_kb import cursor_readiness as verify_cursor_dispatch
from groundtruth_kb.cursor_readiness import evaluate_readiness

# c123 (batch design WP2 2.1): E's corrected headless argv runs the shim with the dispatched prompt and nothing else.
_SHIM_ARGV = ["groundtruth-kb/.venv/Scripts/python.exe", "scripts/cursor_harness.py", "-p", "{{PROMPT}}"]


def _cursor_record(**overrides):
    record = {
        "can_receive_dispatch": False,
        "harness_name": "cursor",
        "harness_type": "cursor",
        "id": "E",
        "invocation_surfaces": {
            # c123 (batch design WP2 2.1): the corrected E row, with no --skill and no role-named dispatch tag.
            "dispatch": {"dispatch_tags": []},
            "headless": {"argv": list(_SHIM_ARGV)},
        },
        "role": ["prime-builder"],
        "status": "active",
    }
    record.update(overrides)
    return record


def _write_cursor_shim(root: Path) -> None:
    # c123 (batch design WP2 2.1): readiness loads no review instructions, so the fixture root holds no skills.
    scripts = root / "scripts"
    scripts.mkdir(exist_ok=True)
    (scripts / "cursor_harness.py").write_text("# fixture shim\n", encoding="utf-8")


def _auth_runner(authenticated: bool = True):
    def runner(command, **kwargs):
        assert command[-2:] == ["--format", "json"]
        assert "status" in command
        assert kwargs["stdin"] == subprocess.DEVNULL
        payload = {
            "status": "authenticated" if authenticated else "unauthenticated",
            "isAuthenticated": authenticated,
            "message": "OK" if authenticated else "Not logged in",
        }
        return subprocess.CompletedProcess(command, 0, stdout=json.dumps(payload), stderr="")

    return runner


@pytest.fixture(autouse=True)
def clear_registry_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GTKB_HARNESS_REGISTRY_PATH", raising=False)
    monkeypatch.setattr(cursor_harness, "load_env_local", lambda **_kwargs: {})


def test_readiness_fails_closed_when_agent_cli_missing(tmp_path: Path, native_harness_record) -> None:
    native_harness_record(tmp_path, _cursor_record())
    _write_cursor_shim(tmp_path)

    def missing_agent() -> list[str]:
        raise cursor_harness.CursorHarnessError("Cursor Agent CLI not found")

    result = evaluate_readiness(project_root=tmp_path, agent_resolver=missing_agent)

    assert result["probe_passed"] is False
    assert result["first_failed_check"].startswith("headless Cursor Agent CLI")


def test_prerequisite_checks_do_not_qualify_harness_or_dispatchability(tmp_path: Path, native_harness_record) -> None:
    native_harness_record(tmp_path, _cursor_record())
    _write_cursor_shim(tmp_path)

    result = evaluate_readiness(
        project_root=tmp_path,
        agent_resolver=lambda: ["C:/Tools/cursor-agent.exe"],
        auth_runner=_auth_runner(),
    )

    assert result["probe_passed"] is True
    assert result["harness_qualification"] == "unqualified"
    assert not ({"ready", "dispatchable", "dispatchable_now", "can_receive_dispatch", "role"} & result.keys())
    assert "role" not in result
    assert result["cursor_adaptation"]["harness_id"] == "E"
    assert result["cursor_adaptation"]["raw_prompt_included"] is False
    assert "publication_contract" not in result


@pytest.mark.parametrize("require_live", [False, True])
def test_readiness_checks_launch_prerequisites_and_loads_no_review_instructions(
    tmp_path: Path, require_live: bool, native_harness_record
) -> None:
    """c123 (batch design WP2 2.1): the "local review instructions" check is gone; a root without skills passes."""
    native_harness_record(tmp_path, _cursor_record())
    _write_cursor_shim(tmp_path)

    def ready(command, **kwargs):
        return subprocess.CompletedProcess(command, 0, stdout="READY\n", stderr="")

    result = evaluate_readiness(
        project_root=tmp_path,
        agent_resolver=lambda: ["C:/Tools/cursor-agent.exe"],
        auth_runner=_auth_runner(),
        require_live=require_live,
        live_runner=ready,
    )
    assert not (tmp_path / ".agents").exists()
    assert result["probe_passed"] is True
    assert [check["name"] for check in result["checks"]] == [
        "native cursor record",
        "native headless argv",
        "cursor harness shim",
        "headless Cursor Agent CLI",
        "headless Cursor Agent authentication",
        *(["live prompt probe"] if require_live else []),
    ]


@pytest.mark.parametrize("legacy_role", [None, [], ["prime-builder"], ["loyal-opposition"]])
def test_legacy_fields_supply_no_context_role_or_dispatchability(
    tmp_path: Path, legacy_role, native_harness_record
) -> None:
    native_harness_record(
        tmp_path,
        _cursor_record(
            can_receive_dispatch=True,
            role=legacy_role,
        ),
    )
    _write_cursor_shim(tmp_path)

    result = evaluate_readiness(
        project_root=tmp_path,
        agent_resolver=lambda: ["C:/Tools/cursor-agent.exe"],
        auth_runner=_auth_runner(),
    )

    assert result["probe_passed"] is True
    assert result["harness_qualification"] == "unqualified"
    assert not ({"ready", "dispatchable", "dispatchable_now", "can_receive_dispatch", "role"} & result.keys())


def test_readiness_fails_closed_when_agent_is_unauthenticated(tmp_path: Path, native_harness_record) -> None:
    native_harness_record(tmp_path, _cursor_record(can_receive_dispatch=True, role=["prime-builder"]))
    _write_cursor_shim(tmp_path)

    result = evaluate_readiness(
        project_root=tmp_path,
        agent_resolver=lambda: ["C:/Tools/cursor-agent.exe"],
        auth_runner=_auth_runner(authenticated=False),
    )

    assert result["probe_passed"] is False
    assert result["auth_probe"]["authenticated"] is False
    assert result["first_failed_check"].startswith("headless Cursor Agent authentication")


def test_auth_probe_injects_cursor_api_key_from_env_local(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, native_harness_record
) -> None:
    native_harness_record(tmp_path, _cursor_record(can_receive_dispatch=True, role=["prime-builder"]))
    _write_cursor_shim(tmp_path)
    monkeypatch.delenv("CURSOR_API_KEY", raising=False)
    monkeypatch.setattr(cursor_harness, "load_env_local", lambda **_kwargs: {"CURSOR_API_KEY": "fixture-key"})

    def runner(command, **kwargs):
        assert kwargs["cwd"] == tmp_path
        assert kwargs["env"]["CURSOR_API_KEY"] == "fixture-key"
        payload = {"status": "authenticated", "isAuthenticated": True, "message": "OK"}
        return subprocess.CompletedProcess(command, 0, stdout=json.dumps(payload), stderr="")

    result = evaluate_readiness(
        project_root=tmp_path,
        agent_resolver=lambda: ["C:/Tools/cursor-agent.exe"],
        auth_runner=runner,
    )

    assert result["probe_passed"] is True
    assert result["harness_qualification"] == "unqualified"
    assert not ({"ready", "dispatchable", "dispatchable_now", "can_receive_dispatch", "role"} & result.keys())
    assert result["auth_probe"]["cursor_api_key_available"] is True


def test_live_probe_requires_non_empty_output(tmp_path: Path, native_harness_record) -> None:
    native_harness_record(tmp_path, _cursor_record(can_receive_dispatch=True, role=["loyal-opposition"]))
    _write_cursor_shim(tmp_path)

    def blank_runner(command, **kwargs):
        assert kwargs["stdin"] == subprocess.DEVNULL
        assert kwargs["capture_output"] is True
        # c123 (batch design WP2 2.1): the probe sends the prompt and the timeout to the shim, and no skill.
        assert command == [
            sys.executable,
            str(tmp_path / "scripts" / "cursor_harness.py"),
            "--prompt",
            verify_cursor_dispatch.DEFAULT_LIVE_PROMPT,
            "--timeout",
            str(verify_cursor_dispatch.DEFAULT_TIMEOUT_SECONDS),
        ]
        return subprocess.CompletedProcess(command, 0, stdout=" \n", stderr="")

    result = evaluate_readiness(
        project_root=tmp_path,
        agent_resolver=lambda: ["C:/Tools/cursor-agent.exe"],
        auth_runner=_auth_runner(),
        require_live=True,
        live_runner=blank_runner,
    )

    assert result["probe_passed"] is False
    assert result["live_probe"]["stdout_bytes"] == 2
    # c123 (batch design WP2 2.1): renamed from "live bridge-review probe".
    assert result["first_failed_check"].startswith("live prompt probe")


@pytest.mark.parametrize("value,exit_code", [("false", 0), ("true", 0), (1, 0), (True, 1), (None, 0)])
def test_authentication_requires_true_boolean_and_successful_exit(tmp_path, native_harness_record, value, exit_code):
    native_harness_record(tmp_path, _cursor_record())
    _write_cursor_shim(tmp_path)

    def runner(command, **kwargs):
        return subprocess.CompletedProcess(command, exit_code, stdout=json.dumps({"isAuthenticated": value}), stderr="")

    result = evaluate_readiness(project_root=tmp_path, agent_resolver=lambda: ["fixture-agent"], auth_runner=runner)
    assert result["probe_passed"] is False
    assert result["auth_probe"]["authenticated"] is False
    assert result["first_failed_check"].startswith("headless Cursor Agent authentication")


def test_auth_uses_selected_root_without_mutating_environment_or_retaining_private_output(tmp_path, monkeypatch):
    import os

    private = "private-fixture-value"
    monkeypatch.delenv("CURSOR_API_KEY", raising=False)
    before = dict(os.environ)

    def load(**kwargs):
        assert kwargs == {"check_only": True, "env_file": tmp_path / ".env.local"}
        return {"CURSOR_API_KEY": private}

    def runner(command, **kwargs):
        assert kwargs["env"]["CURSOR_API_KEY"] == private
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=json.dumps({"isAuthenticated": True, "message": private, "status": private}),
            stderr=private,
        )

    monkeypatch.setattr(cursor_harness, "load_env_local", load)
    result = verify_cursor_dispatch._run_auth_probe(["fixture-agent"], project_root=tmp_path, runner=runner)
    assert result["authenticated"] is True
    assert private not in json.dumps(result)
    assert "command" not in result and "message" not in result
    assert dict(os.environ) == before


@pytest.mark.parametrize(
    "record",
    [
        _cursor_record(harness_type="claude"),
        _cursor_record(invocation_surfaces={"headless": {"argv": ["fixture-agent", None]}}),
    ],
)
def test_invalid_native_launch_record_prevents_auth_and_prompt_subprocesses(tmp_path, native_harness_record, record):
    native_harness_record(tmp_path, record)
    _write_cursor_shim(tmp_path)

    def forbidden(*args, **kwargs):
        pytest.fail("Invalid launch prerequisites must fail before any subprocess")

    report = evaluate_readiness(
        project_root=tmp_path,
        agent_resolver=lambda: ["fixture-agent"],
        auth_runner=forbidden,
        live_runner=forbidden,
        require_live=True,
    )
    assert report["probe_passed"] is False
    assert report["auth_probe"] is None and report["live_probe"] is None


_NAMES_A_ROLE = "the registration names a role: "
_SHIM_REFUSES = "the template does not run the shim with arguments it accepts"


@pytest.mark.parametrize(
    "surfaces,detail",
    [
        # c121's installed E row: --skill bridge-review in the argv and a role-named dispatch tag.
        (
            {
                "dispatch": {"dispatch_tags": ["prime-builder"]},
                "headless": {"argv": [*_SHIM_ARGV, "--skill", "bridge-review"]},
            },
            _NAMES_A_ROLE + "role_value, skill_selector",
        ),
        ({"headless": {"argv": [*_SHIM_ARGV, "--skill=verification"]}}, _NAMES_A_ROLE + "skill_selector"),
        (
            {"dispatch": {"dispatch_tags": ["loyal-opposition"]}, "headless": {"argv": _SHIM_ARGV}},
            _NAMES_A_ROLE + "role_value",
        ),
        ({"headless": {"argv": [*_SHIM_ARGV[:3], "::init gtkb lo"]}}, _NAMES_A_ROLE + "init_marker_in_argv"),
        (
            {"dispatch": {"dispatch_tags": [], "role": "lo"}, "headless": {"argv": _SHIM_ARGV}},
            _NAMES_A_ROLE + "role_key",
        ),
        ({"headless": {"argv": _SHIM_ARGV[:2]}}, _SHIM_REFUSES),
        ({"headless": {"argv": [*_SHIM_ARGV, "--mode", "agent"]}}, _SHIM_REFUSES),
        ({"headless": {"argv": ["python", "foreign/scripts/cursor_harness.py", "-p", "{{PROMPT}}"]}}, _SHIM_REFUSES),
    ],
    ids=[
        "c121-row",
        "skill-equals-form",
        "role-tag",
        "init-marker",
        "role-key",
        "no-prompt",
        "mode-the-shim-refuses",
        "not-the-shim",
    ],
)
def test_native_headless_argv_refuses_roles_and_arguments_the_shim_rejects(
    tmp_path, native_harness_record, surfaces, detail
):
    """c123 (batch design WP2 2.1): inverted. c121's --skill bridge-review and a role-named tag now fail this check, and
    so does a template the shim's own parser refuses, before any authentication or prompt subprocess."""
    native_harness_record(tmp_path, _cursor_record(invocation_surfaces=surfaces))
    _write_cursor_shim(tmp_path)

    def forbidden(*args, **kwargs):
        pytest.fail("A failed argv check must stop readiness before any subprocess")

    result = evaluate_readiness(
        project_root=tmp_path,
        agent_resolver=lambda: ["C:/Tools/cursor-agent.exe"],
        auth_runner=forbidden,
        live_runner=forbidden,
        require_live=True,
    )
    assert result["probe_passed"] is False
    assert result["first_failed_check"] == f"native headless argv: {detail}"
    assert result["auth_probe"] is None and result["live_probe"] is None


@pytest.mark.parametrize(
    "argv,parses",
    [
        (_SHIM_ARGV, True),
        (["python", "scripts\\cursor_harness.py", "--prompt", "{{PROMPT}}", "--mode", "plan"], True),
        ([*_SHIM_ARGV, "--output-format", "json", "--timeout", "30"], True),
        (_SHIM_ARGV[:2], False),
        ([*_SHIM_ARGV, "--skill", "bridge-review"], False),
        ([*_SHIM_ARGV, "--mode", "agent"], False),
        ([*_SHIM_ARGV[:3], "{{MODEL}}"], False),
        (["python", "-p", "{{PROMPT}}"], False),
        # The shim's main refuses these timeouts after parsing, and a --help would print instead of launching.
        ([*_SHIM_ARGV, "--timeout", "0"], False),
        ([*_SHIM_ARGV, "--timeout", "nan"], False),
        ([*_SHIM_ARGV, "--help"], False),
    ],
)
def test_shim_arguments_must_parse_with_the_shims_own_parser(tmp_path, capsys, argv, parses):
    """c123 (batch design WP2 2.1): replaces the exact --skill check. The template's shim arguments, rendered with the
    contract's sample values, must parse with cursor_harness.build_arg_parser() and pass the shim's timeout check."""
    assert verify_cursor_dispatch._shim_arguments_parse(argv, tmp_path) is parses
    assert capsys.readouterr() == ("", ""), "the check never prints into --json or doctor output"
