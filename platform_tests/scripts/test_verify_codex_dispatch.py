from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import verify_codex_dispatch as verify


def _record(argv=None, **overrides):
    return {
        "id": "A",
        "harness_name": "codex",
        "harness_type": "codex",
        "status": "registered",
        "invocation_surfaces": {
            "headless": {
                "argv": argv
                if argv is not None
                else ["codex", "exec", "--model", "fixture-model", "{{PROMPT}}", "--cd", "{{PROJECT_ROOT}}"]
            }
        },
        **overrides,
    }


def _acl_ok(root):
    return {"ok": True, "needs_repair": False, "risky_deny_count": 0, "errors": [], "checked_count": 1}


# c123 (batch design WP2 2.5): the hook-trust check reads what Codex's app-server reports for the root's hooks.json.
# A listing has the measured hooks/list shape (codex-hooks-schema-01561/native-hook-load-r4.json).
def _listing(root, statuses=("trusted", "trusted"), *, events=None, source=None, errors=(), warnings=()):
    path = str(source or Path(root) / ".codex" / "hooks.json")
    hooks = [
        {"sourcePath": path, "eventName": event, "trustStatus": status}
        for status, event in zip(statuses, events or ["preToolUse"] * len(statuses), strict=True)
    ]
    entry = {"cwd": str(root), "hooks": hooks, "errors": list(errors), "warnings": list(warnings)}
    return {"entry": entry, "user_agent": "codex_cli_rs/0.156.1"}


def _hooks_trusted(executable, root, timeout):
    return _listing(root)


def _evaluate(root, **kwargs):
    kwargs.setdefault("hook_lister", _hooks_trusted)
    return verify.evaluate_readiness(
        project_root=root, executable_resolver=lambda name: "fixture-codex", acl_checker=_acl_ok, **kwargs
    )


# c123 (batch design WP2 2.5): the --live probe is the enforcement canary of item 2 (owner decision B4). These answers
# are what the registered argv's final message carries: the effect gate's refusal of an unbound write into scratch, and
# a session read's error (which a model may quote without any hook having refused the patch).
GT_KB_REFUSAL = (
    "Command blocked by PreToolUse hook: foreign_context_material: A context uses only its own scratch and checkout; "
    "scratchpad/gtkb-codex-canary-x belongs to another context."
)
SESSION_READ_ERROR = "no_session_binding: The native context has no immutable binding; initialize that exact context"


def _scratch(root):
    scratch = root / "scratchpad"
    scratch.mkdir()
    return scratch


def _markers(root):
    return sorted((root / "scratchpad").glob("gtkb-codex-canary-*/marker.txt"))


def _canary_runner(calls, *, stdout=GT_KB_REFUSAL, returncode=0, effect=None):
    """A stand-in for the registered Codex run: it records the call, may act on the marker, and answers."""

    def runner(command, **kwargs):
        (marker,) = _markers(Path(kwargs["cwd"]))
        calls.append({"command": command, "kwargs": kwargs, "marker": marker, "content": marker.read_bytes()})
        if effect is not None:
            effect(marker)
        return subprocess.CompletedProcess(command, returncode, stdout=stdout, stderr="private stderr")

    return runner


def test_native_launch_checks_do_not_establish_dispatch_or_runtime_qualification(tmp_path, native_harness_record):
    native_harness_record(tmp_path, _record(can_receive_dispatch=True, role="prime-builder"))
    result = _evaluate(tmp_path)
    assert result["probe_passed"] is True
    assert result["authority_source"] == "native_harness_record"
    assert result["status"] == "registered"
    for field in ("harness_qualification", "model_profile_conformance", "permissions_behavior", "window_behavior"):
        assert result[field] == "unqualified"
    assert (
        not {"dispatchable", "static_dispatchable", "can_receive_dispatch", "role", "headless_argv", "required_model"}
        & result.keys()
    )


@pytest.mark.parametrize("model,profile", [("fixture-model-one", ":workspace"), ("fixture-model-two", ":read-only")])
def test_native_model_and_profile_arguments_are_preserved_without_claiming_conformance(
    tmp_path, native_harness_record, model, profile
):
    argv = ["codex", "exec", "--model", model, "-c", f'default_permissions="{profile}"', "{{PROMPT}}"]
    native_harness_record(tmp_path, _record(argv))
    _scratch(tmp_path)
    calls = []

    report = _evaluate(tmp_path, require_live=True, live_runner=_canary_runner(calls), canary_timeout=5)
    (call,) = calls
    assert call["command"][:-1] == ["fixture-codex", *argv[1:-1]]
    assert str(call["marker"]) in call["command"][-1] and "apply_patch" in call["command"][-1]
    assert call["kwargs"]["cwd"] == tmp_path.resolve()
    assert call["kwargs"]["stdin"] is subprocess.DEVNULL
    assert call["kwargs"]["timeout"] == 5
    assert report["probe_passed"] is True
    assert report["model_profile_conformance"] == "unqualified"
    assert report["permissions_behavior"] == "unqualified"
    assert report["window_behavior"] == "unqualified"


@pytest.mark.parametrize("root_args", [["--cd", "{{PROJECT_ROOT}}"], [], ["--cd", "selected-absolute"]])
def test_selected_project_root_and_default_cwd_are_accepted(tmp_path, native_harness_record, root_args):
    args = [str(tmp_path) if p == "selected-absolute" else p for p in root_args]
    native_harness_record(tmp_path, _record(["codex", "exec", "{{PROMPT}}", *args]))
    assert _evaluate(tmp_path)["probe_passed"] is True


@pytest.mark.parametrize(
    "argv",
    [
        [],
        ["codex", None],
        ["codex", ""],
        "codex exec",
        ["codex", "exec", "--cd"],
        ["codex", "exec", "--cd", "foreign-root"],
        ["codex", "exec", "--cd", "{{PROJECT_ROOT}}", "--cd", "foreign-root"],
        ["codex", "exec", "--dangerously-bypass-approvals-and-sandbox"],
    ],
)
def test_invalid_launch_prerequisites_prevent_acl_and_prompt_operations(tmp_path, native_harness_record, argv):
    native_harness_record(tmp_path, _record(argv))

    def forbidden(*args, **kwargs):
        pytest.fail("Invalid prerequisites must prevent ACL, hook-trust and prompt operations")

    result = verify.evaluate_readiness(
        project_root=tmp_path,
        executable_resolver=lambda name: "fixture-codex",
        acl_checker=forbidden,
        require_live=True,
        live_runner=forbidden,
        hook_lister=forbidden,
    )
    assert result["probe_passed"] is False
    assert result["acl_probe"] is None and result["live_probe"] is None
    assert result["hook_trust"] is None


def test_missing_executable_prevents_acl_and_prompt_operations(tmp_path, native_harness_record):
    native_harness_record(tmp_path, _record())
    calls = []
    result = verify.evaluate_readiness(
        project_root=tmp_path,
        executable_resolver=lambda name: None,
        acl_checker=lambda root: calls.append(root),
        hook_lister=lambda *args: calls.append(args),
    )
    assert result["probe_passed"] is False
    assert result["first_failed_check"] == "executable"
    assert not calls


def test_wrong_harness_type_fails_before_acl_or_launch(tmp_path, native_harness_record):
    native_harness_record(tmp_path, _record(harness_type="claude"))
    with pytest.raises(verify.VerificationError, match="not codex"):
        _evaluate(tmp_path)


@pytest.mark.parametrize(
    "cache",
    [
        {
            "result": "pass",
            "schema_version": 3,
            "verified_at": "2999-01-01T00:00:00Z",
            "visible_window_detected": False,
        },
        {"result": "fail", "visible_window_detected": True},
    ],
)
def test_old_qualification_cache_cannot_supply_or_deny_runtime_facts(
    tmp_path, native_harness_record, monkeypatch, cache
):
    native_harness_record(tmp_path, _record())
    path = tmp_path / ".gtkb-state/bridge-poller/codex-no-window-verification.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(cache), encoding="utf-8")
    before = path.read_bytes()
    original = Path.read_text

    def guarded_read(selected, *args, **kwargs):
        assert selected != path, "The retired cache must not be read"
        return original(selected, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", guarded_read)
    result = _evaluate(tmp_path)
    assert result["probe_passed"] is True
    assert result["window_behavior"] == "unqualified"
    assert path.read_bytes() == before


@pytest.mark.parametrize(
    "payload",
    [
        None,
        {},
        {"ok": "true"},
        {"ok": True, "needs_repair": "false", "checked_count": 1},
        {"ok": True, "needs_repair": False, "checked_count": "1", "errors": []},
        {"ok": True, "needs_repair": False, "checked_count": 1, "errors": [], "returncode": 1},
    ],
)
def test_malformed_or_failed_acl_reports_never_pass(payload):
    assert verify._normalize_acl_check(payload)["ok"] is False


def test_acl_failure_prevents_prompt_launch_and_does_not_echo_error(tmp_path, native_harness_record):
    native_harness_record(tmp_path, _record())

    def acl_failure(root):
        return {
            "ok": False,
            "needs_repair": True,
            "risky_deny_count": 1,
            "checked_count": 1,
            "errors": [],
            "error": "private diagnostic detail",
        }

    def forbidden(*args, **kwargs):
        pytest.fail("ACL failure must prevent prompt launch")

    report = verify.evaluate_readiness(
        project_root=tmp_path,
        executable_resolver=lambda name: "fixture-codex",
        acl_checker=acl_failure,
        require_live=True,
        live_runner=forbidden,
        hook_lister=_hooks_trusted,
    )
    assert report["probe_passed"] is False
    assert report["acl_probe"]["needs_repair"] is True
    assert "private diagnostic" not in json.dumps(report)


@pytest.mark.parametrize("returncode,stdout", [(1, "READY"), (0, "")])
def test_failed_or_empty_live_process_does_not_pass(tmp_path, native_harness_record, returncode, stdout):
    native_harness_record(tmp_path, _record())
    _scratch(tmp_path)
    report = _evaluate(
        tmp_path,
        require_live=True,
        live_runner=lambda command, **kwargs: subprocess.CompletedProcess(
            command, returncode, stdout=stdout, stderr="private output"
        ),
    )
    assert report["probe_passed"] is False
    assert report["live_probe"]["refusal_recognized"] is False
    assert "private output" not in json.dumps(report)


def test_prompt_timeout_remains_private_and_unqualified(tmp_path, native_harness_record, monkeypatch):
    native_harness_record(tmp_path, _record())
    _scratch(tmp_path)
    monkeypatch.setattr(verify, "no_window_subprocess_kwargs", lambda: {"creationflags": 0x08000000})

    def timeout(command, **kwargs):
        assert kwargs["creationflags"] == 0x08000000
        raise subprocess.TimeoutExpired(command, kwargs["timeout"], output="private response", stderr="private error")

    report = _evaluate(tmp_path, require_live=True, live_runner=timeout)
    assert report["probe_passed"] is False
    assert report["live_probe"]["error"] == "TimeoutExpired"
    assert "private" not in json.dumps(report)
    assert report["window_behavior"] == "unqualified"
    assert _markers(tmp_path) == [], "an untouched canary directory is removed"


@pytest.mark.parametrize(
    "extra",
    [["--init", "{{INIT_LINE}}"], ["--report={{REPORT}}"], ["--model", "{{MODEL}}"]],
    ids=["unfilled-binding", "unfilled-report", "unknown-placeholder"],
)
def test_live_probe_refuses_a_template_it_cannot_fill_without_starting_a_process(
    tmp_path, native_harness_record, extra
):
    """c123 (batch design WP2 2.1): the probe fills PROMPT and PROJECT_ROOT only; any other placeholder is refused."""
    native_harness_record(tmp_path, _record(["codex", "exec", *extra, "{{PROMPT}}"]))
    scratch = _scratch(tmp_path)

    def forbidden(*args, **kwargs):
        pytest.fail("A template the live probe cannot fill must not start a process")

    report = _evaluate(tmp_path, require_live=True, live_runner=forbidden)
    assert report["probe_passed"] is False
    assert report["acl_probe"]["ok"] is True
    assert report["live_probe"] == {"ok": False, "error": "InvocationError"}
    assert report["first_failed_check"] == "Codex enforcement canary"
    assert list(scratch.iterdir()) == [], "the template is rendered before the canary writes anything"


def test_repair_flag_is_not_an_operation_of_the_diagnostic_cli():
    with pytest.raises(SystemExit) as error:
        verify.main(["--repair-acl"])
    assert error.value.code == 2


# c123 (batch design WP2 2.5): Codex runs the tool call of an untrusted or failed hook, so readiness reads the trust
# Codex reports for the selected root's hooks.json and passes only when every PreToolUse entry is trusted.


def test_all_trusted_pretooluse_hooks_pass_and_record_the_build_file_and_root(tmp_path, native_harness_record):
    native_harness_record(tmp_path, _record())
    hooks_json = tmp_path / ".codex" / "hooks.json"
    hooks_json.parent.mkdir()
    hooks_json.write_bytes(b'{"hooks": {}}\n')
    calls = []

    def lister(executable, root, timeout):
        calls.append((executable, root, timeout))
        return _listing(root)

    report = _evaluate(tmp_path, hook_lister=lister, timeout=7)
    assert report["probe_passed"] is True
    assert report["probe_scope"] == "launch_prerequisites_acl_and_hook_trust"
    assert calls == [("fixture-codex", tmp_path.resolve(), 7)]
    trust = report["hook_trust"]
    assert trust["ok"] is True and "instruction" not in trust
    assert (trust["pretooluse_hooks"], trust["untrusted"], trust["errors"], trust["warnings"]) == (2, 0, 0, 0)
    assert trust["hooks_json"] == str(hooks_json.resolve())
    assert trust["hooks_json_sha256"] == hashlib.sha256(b'{"hooks": {}}\n').hexdigest()
    assert (trust["project_root"], trust["codex_build"]) == (str(tmp_path.resolve()), "codex_cli_rs/0.156.1")
    assert report["harness_qualification"] == "unqualified"


@pytest.mark.parametrize(
    "listing,count_text",
    [
        (lambda root: _listing(root, ("trusted", "untrusted")), "the 1 untrusted GT-KB entries"),
        (lambda root: _listing(root, ("untrusted", "untrusted", "untrusted")), "the 3 untrusted GT-KB entries"),
        (
            lambda root: _listing(
                root, (), warnings=[f"failed to parse hooks config {Path(root) / '.codex' / 'hooks.json'}: x"]
            ),
            "(0 errors, 1 warnings)",
        ),
        (
            lambda root: _listing(
                root, ("trusted",), errors=[{"path": str(Path(root) / ".codex" / "hooks.json"), "message": "x"}]
            ),
            "(1 errors, 0 warnings)",
        ),
        (lambda root: _listing(root, ()), "loaded no GT-KB PreToolUse hooks"),
        (lambda root: _listing(root, ("trusted",), source=Path(root) / "elsewhere" / "hooks.json"), "loaded no GT-KB"),
        (lambda root: _listing(root, ("trusted",), events=["postToolUse"]), "loaded no GT-KB PreToolUse hooks"),
    ],
    ids=["one_untrusted", "all_untrusted", "parse_warning", "load_error", "no_hooks", "other_file", "other_event"],
)
def test_untrusted_failed_or_missing_hooks_fail_before_any_prompt(tmp_path, native_harness_record, listing, count_text):
    native_harness_record(tmp_path, _record())

    def forbidden(*args, **kwargs):
        pytest.fail("A failed hook-trust check must prevent the prompt launch")

    report = _evaluate(
        tmp_path, hook_lister=lambda executable, root, timeout: listing(root), require_live=True, live_runner=forbidden
    )
    assert report["probe_passed"] is False
    assert report["first_failed_check"] == "Codex hooks trusted"
    assert report["live_probe"] is None
    instruction = report["hook_trust"]["instruction"]
    assert str((tmp_path / ".codex" / "hooks.json").resolve()) in instruction
    assert count_text in instruction
    assert "verify_codex_dispatch.py --json" in instruction


@pytest.mark.parametrize("error", [FileNotFoundError, TimeoutError, RuntimeError])
def test_an_unavailable_app_server_fails_and_never_passes(tmp_path, native_harness_record, error):
    native_harness_record(tmp_path, _record())

    def unavailable(executable, root, timeout):
        raise error("private-detail")

    report = _evaluate(tmp_path, hook_lister=unavailable)
    assert report["probe_passed"] is False
    assert report["first_failed_check"] == "Codex hooks trusted"
    trust = report["hook_trust"]
    assert trust["ok"] is False and trust["error"] == error.__name__
    assert str((tmp_path / ".codex" / "hooks.json").resolve()) in trust["instruction"]
    assert "private-detail" not in json.dumps(report)


# A stand-in app-server: run as `python app-server --stdio` from the root, it answers the measured exchange and logs
# each method it receives. Before its initialize reply it sends a notification and a server request that reuses id 1;
# only the reply may be matched.
FAKE_APP_SERVER = """\
import json, sys
from pathlib import Path
for line in sys.stdin:
    message = json.loads(line)
    method = message.get("method")
    with Path("methods.log").open("a", encoding="utf-8") as log:
        log.write(method + "\\n")
    if method == "initialize":
        print(json.dumps({"method": "codex/event", "params": {}}), flush=True)
        print(json.dumps({"id": 1, "method": "item/tool/requestUserInput", "params": {}}), flush=True)
        print(json.dumps({"id": 1, "result": {"userAgent": "codex_cli_rs/0.156.1"}}), flush=True)
    elif method == "hooks/list":
        root = message["params"]["cwds"][0]
        hook = {"sourcePath": root + "/.codex/hooks.json", "eventName": "preToolUse", "trustStatus": "trusted"}
        rows = [{"cwd": root, "hooks": [hook], "errors": [], "warnings": []}]
        print(json.dumps({"id": message["id"], "result": {"data": rows}}), flush=True)
"""
NEVER_ANSWERS = "import sys\nfor line in sys.stdin:\n    pass\n"
EXITS_EARLY = "import sys\nsys.stdin.readline()\n"
ANSWERS_AN_ERROR = (
    "import json, sys\nfor line in sys.stdin:\n    print(json.dumps({'id': 1, 'error': {'code': -1}}), flush=True)\n"
)


def test_the_lister_speaks_the_measured_exchange_and_only_reads(tmp_path):
    (tmp_path / "app-server").write_text(FAKE_APP_SERVER, encoding="utf-8")
    listing = verify._list_project_hooks(sys.executable, tmp_path, 30)
    assert listing["user_agent"] == "codex_cli_rs/0.156.1"
    assert Path(listing["entry"]["cwd"]).resolve() == tmp_path.resolve()
    assert verify._evaluate_hook_trust(tmp_path.resolve(), listing)["ok"] is True
    # Trust is granted only in Codex's /hooks screen: the lister sends the three read calls and nothing else.
    assert (tmp_path / "methods.log").read_text(encoding="utf-8").split() == ["initialize", "initialized", "hooks/list"]


@pytest.mark.parametrize(
    "server,error",
    [(NEVER_ANSWERS, TimeoutError), (EXITS_EARLY, RuntimeError), (ANSWERS_AN_ERROR, RuntimeError)],
    ids=["never_answers", "exits_before_answering", "json_rpc_error"],
)
def test_the_lister_refuses_a_server_that_does_not_answer(tmp_path, server, error):
    (tmp_path / "app-server").write_text(server, encoding="utf-8")
    with pytest.raises(error):
        verify._list_project_hooks(sys.executable, tmp_path, 2)


# c123 (batch design WP2 2.5): trust is necessary but not sufficient (on 0.130 a trusted hook did not enforce), so
# --live drives the registered argv through one unbound apply_patch to a disposable marker in the root's scratch: a
# GT-KB hook must refuse it and the marker must keep its bytes (item 2, owner decision B4).


def test_the_enforcement_canary_passes_on_a_gt_kb_refusal_and_leaves_no_trace(tmp_path, native_harness_record):
    native_harness_record(tmp_path, _record())
    hooks_json = tmp_path / ".codex" / "hooks.json"
    hooks_json.parent.mkdir()
    hooks_json.write_bytes(b'{"hooks": {}}\n')
    scratch = _scratch(tmp_path)
    calls = []

    report = _evaluate(tmp_path, require_live=True, live_runner=_canary_runner(calls), canary_timeout=9)

    assert report["probe_passed"] is True, report["first_failed_check"]
    assert report["probe_scope"] == "launch_prerequisites_acl_hook_trust_and_enforcement_canary"
    assert [check["name"] for check in report["checks"]][-2:] == ["Codex hooks trusted", "Codex enforcement canary"]
    (call,) = calls
    marker = call["marker"]
    assert marker.parent.parent == scratch.resolve() and marker.parent.name.startswith("gtkb-codex-canary-")
    assert call["content"].startswith(b"GT-KB Codex enforcement canary marker "), "the marker exists during the run"
    assert call["kwargs"]["timeout"] == 9 and call["kwargs"]["cwd"] == tmp_path.resolve()
    prompt = call["command"][4]
    assert "apply_patch" in prompt and str(marker) in prompt and "::init" not in prompt, "the canary binds nothing"
    canary = report["live_probe"]
    assert canary["ok"] is True and canary["kept"] is False and "instruction" not in canary
    assert (canary["marker_unchanged"], canary["scratch_clean"], canary["refusal_recognized"]) == (True, True, True)
    assert canary["hooks_json_unchanged"] is True
    trust = report["hook_trust"]
    assert canary["hooks_json_sha256"] == trust["hooks_json_sha256"] == hashlib.sha256(b'{"hooks": {}}\n').hexdigest()
    assert (canary["codex_build"], canary["project_root"]) == ("codex_cli_rs/0.156.1", str(tmp_path.resolve()))
    assert canary["expected_refusal_code"] == "foreign_context_material"
    assert list(scratch.iterdir()) == [], "a passing canary removes its marker and directory"
    serialized = json.dumps(report)
    assert GT_KB_REFUSAL not in serialized and "private stderr" not in serialized and prompt not in serialized


def _append(marker):
    with marker.open("ab") as stream:
        stream.write(b"GTKB-CANARY applied\n")


def _add_neighbour(marker):
    (marker.parent / "other.txt").write_text("created by the session", encoding="utf-8")


@pytest.mark.parametrize(
    ("effect", "stdout"),
    [(_append, "APPLIED"), (lambda marker: marker.unlink(), "APPLIED"), (_add_neighbour, GT_KB_REFUSAL)],
    ids=["patch_applied", "marker_removed", "neighbour_created"],
)
def test_a_write_that_reaches_the_canary_directory_fails_and_keeps_the_evidence(
    tmp_path, native_harness_record, effect, stdout
):
    native_harness_record(tmp_path, _record())
    _scratch(tmp_path)
    calls = []

    report = _evaluate(tmp_path, require_live=True, live_runner=_canary_runner(calls, stdout=stdout, effect=effect))

    assert report["probe_passed"] is False
    assert report["first_failed_check"] == "Codex enforcement canary"
    canary = report["live_probe"]
    assert canary["ok"] is False and canary["kept"] is True
    assert not (canary["marker_unchanged"] and canary["scratch_clean"])
    directory = calls[0]["marker"].parent
    assert directory.is_dir(), "the evidence stays"
    assert f"The unbound apply_patch reached {directory}" in canary["instruction"]
    assert "Do not dispatch Codex into this root" in canary["instruction"]


@pytest.mark.parametrize("stdout", [SESSION_READ_ERROR, "I will not write without an init line.", ""])
def test_an_unchanged_marker_without_the_gt_kb_refusal_does_not_pass(tmp_path, native_harness_record, stdout):
    """A model that stops on its own, or quotes a session read, shows nothing about the hooks."""
    native_harness_record(tmp_path, _record())
    scratch = _scratch(tmp_path)

    report = _evaluate(tmp_path, require_live=True, live_runner=_canary_runner([], stdout=stdout))

    canary = report["live_probe"]
    assert report["probe_passed"] is False
    assert (canary["marker_unchanged"], canary["scratch_clean"], canary["refusal_recognized"]) == (True, True, False)
    assert canary["kept"] is False and list(scratch.iterdir()) == []
    assert "carries no foreign_context_material refusal" in canary["instruction"]


def test_hooks_json_that_changes_during_the_canary_does_not_pass(tmp_path, native_harness_record):
    native_harness_record(tmp_path, _record())
    hooks_json = tmp_path / ".codex" / "hooks.json"
    hooks_json.parent.mkdir()
    hooks_json.write_bytes(b'{"hooks": {}}\n')
    _scratch(tmp_path)

    def rewrite_hooks(marker):
        hooks_json.write_bytes(b'{"hooks": {"PreToolUse": []}}\n')

    report = _evaluate(tmp_path, require_live=True, live_runner=_canary_runner([], effect=rewrite_hooks))

    canary = report["live_probe"]
    assert report["probe_passed"] is False
    assert canary["refusal_recognized"] is True and canary["hooks_json_unchanged"] is False
    assert "changed while the canary ran" in canary["instruction"]


@pytest.mark.parametrize("error", [OSError, subprocess.SubprocessError])
def test_a_canary_run_that_cannot_start_fails_and_removes_its_untouched_directory(
    tmp_path, native_harness_record, error
):
    native_harness_record(tmp_path, _record())
    scratch = _scratch(tmp_path)

    def failing(command, **kwargs):
        raise error("private-detail")

    report = _evaluate(tmp_path, require_live=True, live_runner=failing)

    canary = report["live_probe"]
    assert report["probe_passed"] is False
    assert canary["error"] == error.__name__ and canary["returncode"] is None
    assert list(scratch.iterdir()) == []
    assert "private-detail" not in json.dumps(report)


@pytest.mark.parametrize("parent", [None, "outside"], ids=["root_has_no_scratch", "scratch_outside_the_root"])
def test_the_canary_writes_only_in_the_roots_existing_scratch(tmp_path, native_harness_record, parent):
    root = tmp_path / "root"
    root.mkdir()
    native_harness_record(root, _record())
    outside = tmp_path / "outside"
    outside.mkdir()
    before = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))

    def forbidden(*args, **kwargs):
        pytest.fail("Without the root's scratch the canary must not start Codex")

    report = _evaluate(
        root, require_live=True, live_runner=forbidden, canary_scratch=outside if parent == "outside" else None
    )

    canary = report["live_probe"]
    assert report["probe_passed"] is False and canary["ok"] is False
    assert "must be an existing directory inside" in canary["instruction"]
    assert sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*")) == before


@pytest.mark.parametrize("canary_timeout", [0, -1, float("inf"), float("nan")])
def test_an_invalid_canary_timeout_refuses_before_any_native_or_launch_operation(tmp_path, canary_timeout):
    with pytest.raises(verify.VerificationError, match="canary timeout must be finite and positive"):
        verify.evaluate_readiness(project_root=tmp_path, canary_timeout=canary_timeout)


def test_the_cli_runs_the_canary_with_its_own_timeout_and_takes_no_prompt(monkeypatch, capsys):
    seen = {}

    def fake(**kwargs):
        seen.update(kwargs)
        return {"probe_passed": True, "first_failed_check": "", "live_probe": {"ok": True}}

    monkeypatch.setattr(verify, "evaluate_readiness", fake)
    assert verify.main(["--live", "--canary-timeout", "120", "--timeout", "7"]) == 0
    assert (seen["require_live"], seen["canary_timeout"], seen["timeout"]) == (True, 120.0, 7.0)
    assert "live_prompt" not in seen
    capsys.readouterr()
    with pytest.raises(SystemExit) as error:
        verify.main(["--live", "--prompt", "Reply with READY only."])
    assert error.value.code == 2
