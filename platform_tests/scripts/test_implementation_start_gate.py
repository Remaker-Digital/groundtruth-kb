"""Native effect boundary and command-classification regressions.

Current binding, exact artifact claims, registered checkout, live scope, scratch
confinement, redirected paths and unavailable authority are exercised through
PostgreSQL and separate CLI processes in test_native_bridge.py. This suite also
checks the hook's concrete-target request and fail-closed CLI result handling.
Retired permission packets, PAUTH, raw file claims and finalizer exceptions have
no surviving gate obligations; they are not used as fixtures.
"""

from __future__ import annotations

import io
import json
import subprocess
import sys
from pathlib import Path

import pytest
from groundtruth_kb.bridge import effect_gate as gate

_WI3357_PARSER_CASES = [
    # (case_id, command, expected_span_count)
    (
        "documented-single-heredoc",
        "git commit -m \"$(cat <<'EOF'\nmsg body\nEOF\n)\"",
        1,
    ),
    ("unquoted-delimiter", 'git commit -m "$(cat <<EOF\nmsg\nEOF\n)"', 0),
    (
        "non-cat-opener",
        "git commit -m \"$(rm scripts/sample.py <<'EOF'\nx\nEOF\n)\"",
        0,
    ),
    (
        "early-delimiter-then-command",
        "git commit -m \"$(cat <<'EOF'\nmsg\nEOF\nSet-Content -Path scripts/sample.py -Value z\nEOF\n)\"",
        0,
    ),
    (
        "early-delimiter-then-separator",
        "git commit -m \"$(cat <<'EOF'\nmsg\nEOF\n; rm -rf x\nEOF\n)\"",
        0,
    ),
    (
        "opener-redirect-tail",
        "git commit -m \"$(cat <<'EOF' > scripts/sample.py\nmsg\nEOF\n)\"",
        0,
    ),
    (
        "opener-separator-tail",
        "git commit -m \"$(cat <<'EOF'; rm -rf x\nmsg\nEOF\n)\"",
        0,
    ),
    (
        "opener-pipeline-tail",
        "git commit -m \"$(cat <<'EOF' | tee scripts/sample.py\nmsg\nEOF\n)\"",
        0,
    ),
    ("no-delimiter-line", "git commit -m \"$(cat <<'EOF'\njust body text\n)\"", 0),
    ("multi-cat-heredoc", "git commit -m \"$(cat <<'A' <<'B'\nbody\nA\nB\n)\"", 0),
    ("crlf-heredoc", "git commit -m \"$(cat <<'EOF'\r\nmsg\r\nEOF\r\n)\"", 0),
    (
        "two-independent-heredocs",
        "git commit -m \"$(cat <<'A'\nfirst\nA\n)$(cat <<'B'\nsecond\nB\n)\"",
        2,
    ),
]

PROTECTED_GATE_PATH = "scripts/implementation_start_gate" + ".py"


@pytest.fixture(autouse=True)
def clear_native_context(monkeypatch):
    monkeypatch.delenv("GTKB_NATIVE_CONTEXT_ID", raising=False)
    monkeypatch.delenv("GTKB_PROJECT_ROOT", raising=False)
    monkeypatch.delenv("RUFF_OUTPUT_FILE", raising=False)


@pytest.mark.parametrize(
    "command,targets",
    [
        ("python -m ruff check --fix foreign.py", ["foreign.py"]),
        ("ruff check foreign.py --fix-only", ["foreign.py"]),
        ("ruff check --add-noqa foreign.py", ["foreign.py"]),
        ('ruff check --config "fix=true" foreign.py', ["foreign.py"]),
        ("ruff check foreign.py", ["foreign.py"]),  # Configuration may enable fixes.
        ("ruff format foreign.py", ["foreign.py"]),
        ('"C:\\tools\\ruff.exe" check --fix "foreign path.py"', ["foreign path.py"]),
        ("ruff check --no-fix --no-fix-only --output-file report.json input.py", ["report.json"]),
        ("ruff check --diff --output-file=report.json input.py", ["report.json"]),
        ("ruff check --fix --select F401 --output-file report.json code.py", ["code.py", "report.json"]),
        ("python -m ruff check --fix -- -literal.py", ["-literal.py"]),
    ],
)
def test_ruff_effects_require_native_check_of_all_literal_targets(tmp_path, monkeypatch, command, targets):
    calls = []

    def refused(argv, **_kwargs):
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 1, "", "artifact_out_of_scope")

    monkeypatch.setattr(gate.subprocess, "run", refused)
    result = gate.gate_decision(
        {"cwd": str(tmp_path), "session_id": "native", "tool_name": "Bash", "tool_input": {"command": command}}
    )
    assert result["decision"] == "block"
    assert result["reason_code"] == "native_effect_refused"
    assert len(calls) == 1
    argv = calls[0]
    assert [argv[i + 1] for i, arg in enumerate(argv) if arg == "--path"] == targets
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize(
    "command",
    [
        "ruff check --fix",
        "ruff check --fix --unknown-option foreign.py",
        "ruff check --fix --output-file",
        "ruff check --fix code.py; Set-Content foreign.py x",
        "python -m ruff check --fix code.py > foreign.txt",
    ],
)
def test_ruff_incomplete_effects_refuse_before_cli(tmp_path, monkeypatch, command):
    monkeypatch.setattr(gate.subprocess, "run", lambda *_a, **_k: pytest.fail("No complete target set"))
    result = gate.gate_decision(
        {"cwd": str(tmp_path), "session_id": "native", "tool_name": "Bash", "tool_input": {"command": command}}
    )
    assert result["reason_code"] == "unknown_effect_targets"


@pytest.mark.parametrize(
    "command",
    [
        "ruff check --no-fix --no-fix-only input.py",
        "python -m ruff check --diff input.py",
        "python -m ruff check --fix --diff input.py",
        "ruff format --check input.py",
        "ruff format --diff input.py",
        "ruff check --help",
    ],
)
def test_explicit_read_only_ruff_inspection_needs_no_claim(tmp_path, monkeypatch, command):
    monkeypatch.setattr(gate.subprocess, "run", lambda *_a, **_k: pytest.fail("Read-only command"))
    assert gate.gate_decision({"cwd": str(tmp_path), "tool_name": "Bash", "tool_input": {"command": command}}) == {}


def test_ruff_environment_output_is_not_read_only(tmp_path, monkeypatch):
    monkeypatch.setenv("RUFF_OUTPUT_FILE", "foreign-report.json")
    result = gate.gate_decision(
        {"cwd": str(tmp_path), "tool_name": "Bash", "tool_input": {"command": "ruff check --diff code.py"}}
    )
    assert result["reason_code"] == "invalid_native_context"
    assert not (tmp_path / "foreign-report.json").exists()


@pytest.mark.parametrize("path", ["analysis.ipynb", None])
def test_notebook_mutation_requires_a_current_native_effect_check(tmp_path, monkeypatch, path):
    calls = []

    def refused(argv, **kwargs):
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 1, "", "checkout_not_registered")

    monkeypatch.setenv("GTKB_NATIVE_CONTEXT_ID", "current-context")
    monkeypatch.setattr(gate.subprocess, "run", refused)
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "NotebookEdit",
        "tool_input": {"notebook_path": path, "new_source": "changed = True"},
    }
    result = gate.gate_decision(payload)
    assert result["decision"] == "block"
    if path:
        assert len(calls) == 1
        assert calls[0][-2:] == ["--path", path]
        assert "checkout_not_registered" in result["reason"]
    else:
        assert calls == []
        assert result["reason_code"] == "unknown_effect_targets"
    assert not (tmp_path / "analysis.ipynb").exists()


@pytest.mark.parametrize("tool", ["Write", "Edit", "MultiEdit", "StrReplace", "Delete", "Move", "Copy"])
def test_declared_file_mutations_never_skip_effect_validation(tmp_path, monkeypatch, tool):
    monkeypatch.setenv("GTKB_NATIVE_CONTEXT_ID", "current-context")
    calls = []

    def refused(argv, **kwargs):
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 1, "", "artifact_out_of_scope")

    monkeypatch.setattr(gate.subprocess, "run", refused)
    result = gate.gate_decision({"cwd": str(tmp_path), "tool_name": tool, "tool_input": {"file_path": "foreign.py"}})
    assert result["decision"] == "block"
    if tool in {"Move", "Copy"}:
        # A single path does not identify both effects of these operations.
        assert result["reason_code"] == "unknown_effect_targets"
        assert calls == []
    else:
        assert len(calls) == 1
        assert calls[0][-2:] == ["--path", "foreign.py"]
        assert "artifact_out_of_scope" in result["reason"]


@pytest.mark.parametrize("scope", ["implementation", "scratch"])
def test_effect_check_uses_actual_cwd_and_complete_literal_targets(tmp_path, monkeypatch, scope):
    cwd = tmp_path / "nested"
    cwd.mkdir()
    monkeypatch.setenv("GTKB_NATIVE_CONTEXT_ID", "native-current")
    calls = []

    def run(argv, **kwargs):
        calls.append((argv, kwargs))
        return subprocess.CompletedProcess(argv, 0, json.dumps({"status": "current", "scope": scope}), "")

    monkeypatch.setattr(gate.subprocess, "run", run)
    payload = {
        "project_root": str(tmp_path),
        "cwd": str(cwd),
        "session_id": "native-current",
        "tool_name": "apply_patch",
        "tool_input": {
            "patch": "*** Begin Patch\n*** Update File: code.py\n@@\n+x\n*** Add File: 'second.py'\n+y\n*** End Patch\n"
        },
    }
    assert gate.gate_decision(payload) == {}
    argv, kwargs = calls.pop()
    assert argv[:5] == [sys.executable, "-m", "groundtruth_kb", "bridge", "check-effects"]
    assert argv[5:] == [
        "--native-context-id",
        "native-current",
        "--cwd",
        str(cwd),
        "--json",
        "--path",
        "code.py",
        "--path",
        "'second.py'",
    ]
    assert kwargs["cwd"] == tmp_path
    assert kwargs["env"]["GT_PROJECT_ROOT"] == str(tmp_path)
    assert kwargs["env"]["PYTHONIOENCODING"] == kwargs["encoding"] == "utf-8"
    assert kwargs["timeout"] == 10
    assert not calls


@pytest.mark.parametrize("native,supplied", [(None, None), ("actual", "foreign")])
def test_unbound_or_conflicting_native_identity_refuses_before_cli(tmp_path, monkeypatch, native, supplied):
    if native:
        monkeypatch.setenv("GTKB_NATIVE_CONTEXT_ID", native)
    monkeypatch.setattr(gate.subprocess, "run", lambda *_a, **_k: pytest.fail("CLI must not run"))
    payload = {"cwd": str(tmp_path), "tool_name": "Write", "tool_input": {"path": "code.py"}}
    if supplied:
        payload["session_id"] = supplied
    assert gate.gate_decision(payload)["reason_code"] == "invalid_native_context"


@pytest.mark.parametrize(
    "response,expected",
    [
        (subprocess.CompletedProcess([], 1, "", "claim_expired"), "native_effect_refused"),
        (
            subprocess.CompletedProcess([], 1, '{"status":"current","scope":"implementation"}', ""),
            "native_effect_refused",
        ),
        (subprocess.CompletedProcess([], 0, "{}", ""), "invalid_effect_response"),
        (subprocess.CompletedProcess([], 0, "[]", ""), "invalid_effect_response"),
        (subprocess.CompletedProcess([], 0, '{"status":"current","scope":"all"}', ""), "invalid_effect_response"),
        (
            subprocess.CompletedProcess([], 0, '{"status":"stale","scope":"implementation"}', ""),
            "invalid_effect_response",
        ),
        (subprocess.CompletedProcess([], 0, "malformed", ""), "effect_check_unavailable"),
        (OSError("CLI unavailable"), "effect_check_unavailable"),
        (subprocess.TimeoutExpired("gt", 10), "effect_check_unavailable"),
    ],
)
def test_invalid_or_unavailable_cli_refuses_without_fallback(tmp_path, monkeypatch, response, expected):
    def run(*_args, **_kwargs):
        if isinstance(response, Exception):
            raise response
        return response

    monkeypatch.setattr(gate.subprocess, "run", run)
    result = gate.gate_decision(
        {
            "cwd": str(tmp_path),
            "session_id": "native",
            "tool_name": "Write",
            "tool_input": {"path": "code.py", "content": "must not be written"},
        }
    )
    assert result["decision"] == "block"
    assert result["reason_code"] == expected
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("target", ["code.py", "bridge/entry-001.md", "bridge/note.md", "scratchpad/draft.md"])
def test_effects_have_no_unbound_path_exemption(tmp_path, target):
    result = gate.gate_decision(
        {
            "cwd": str(tmp_path),
            "tool_name": "Write",
            "tool_input": {"path": target, "content": "x"},
        }
    )
    assert result["reason_code"] == "invalid_native_context"


def test_unknown_mutating_targets_refuse_before_cli(tmp_path, monkeypatch):
    monkeypatch.setattr(gate.subprocess, "run", lambda *_a, **_k: pytest.fail("CLI must not run"))
    result = gate.gate_decision(
        {
            "cwd": str(tmp_path),
            "session_id": "native",
            "tool_name": "Write",
            "tool_input": {"content": "x"},
        }
    )
    assert result["reason_code"] == "unknown_effect_targets"


@pytest.mark.parametrize("target", ["code.py", "'code.py'", " code.py", "code.py "])
def test_native_tool_paths_preserve_literal_target_names(tmp_path, target):
    paths, mutating = gate.changed_paths(
        {"project_root": str(tmp_path), "cwd": str(tmp_path), "tool_name": "Write", "tool_input": {"path": target}}
    )
    assert mutating
    assert paths == [target]


def test_shell_target_quotes_do_not_strip_literal_inner_filename_quotes(tmp_path):
    assert gate._paths_from_shell(tmp_path, 'Set-Content -Path "code.py" -Value x') == ["code.py"]
    assert gate._paths_from_shell(tmp_path, "Set-Content -Path \"'code.py'\" -Value x") == ["'code.py'"]


def test_read_only_shell_command_is_allowed_without_authorization(
    tmp_path: Path,
) -> None:
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Bash",
        "tool_input": {"command": 'rg -n "hello" scripts/sample.py'},
    }

    assert gate.gate_decision(payload) == {}


@pytest.mark.parametrize(
    "command",
    [
        "python -m pytest platform_tests/scripts/test_sample.py -q",
        "git status --short",
        'rg -n "hello" scripts/sample.py',
    ],
)
def test_structurally_single_read_only_commands_remain_allowed(command: str, tmp_path: Path) -> None:
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Bash",
        "tool_input": {"command": command},
    }

    assert gate._is_safe_command(command) is True
    assert gate.gate_decision(payload) == {}


@pytest.mark.parametrize(
    ("command", "reason_code"),
    [
        (
            "python -m pytest -q; Set-Content -Path scripts/bypass.py -Value x",
            "invalid_native_context",
        ),
        (
            "git status; git add scripts/bypass.py",
            "direct_git_effect_requires_lifecycle",
        ),
    ],
)
def test_safe_prefix_does_not_exempt_appended_mutating_stage(command: str, reason_code: str, tmp_path: Path) -> None:
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Bash",
        "tool_input": {"command": command},
    }

    assert gate._is_safe_command(command) is False
    paths, mutating = gate.changed_paths(payload)
    assert mutating is True
    assert "scripts/bypass.py" in paths
    result = gate.gate_decision(payload)
    assert result["decision"] == "block"
    assert result["reason_code"] == reason_code


@pytest.mark.parametrize("hook_input", ["", "{}", "[]", "{malformed-json"])
def test_hook_denies_empty_or_malformed_json_payload(
    hook_input: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO(hook_input))

    assert gate.main() == 0
    output = json.loads(capsys.readouterr().out)
    hook_output = output["hookSpecificOutput"]
    assert hook_output["permissionDecision"] == "deny"
    assert "payload" in hook_output["permissionDecisionReason"].lower()


@pytest.mark.parametrize(
    ("command", "subcommand"),
    [
        ('git commit -m "feat(gtkb): finalize verified bridge work"', "commit"),
        ('git commit -m "literal ; | && message punctuation"', "commit"),
        ("git commit --amend --no-edit", "commit"),
        ('git -C . commit -m "scoped change"', "commit"),
        ('git -c user.name="GT-KB" commit -m "scoped change"', "commit"),
        ("git push origin develop", "push"),
        ("git.exe push --porcelain origin HEAD", "push"),
        ("git --git-dir=.git push --force-with-lease origin HEAD", "push"),
        ("git switch -c bypass", "switch"),
        ("git branch bypass", "branch"),
        ("git cherry-pick HEAD~1", "cherry-pick"),
        ("git revert HEAD", "revert"),
        ("git update-ref refs/heads/main HEAD", "update-ref"),
        ("git clean -fd", "clean"),
        ("git worktree add ../bypass", "worktree"),
        ("git checkout -b bypass", "checkout"),
        ("git config user.name bypass", "config"),
        ("git fetch origin", "fetch"),
    ],
)
def test_direct_git_effects_require_lifecycle_command(
    tmp_path: Path,
    command: str,
    subcommand: str,
) -> None:
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Bash",
        "tool_input": {"command": command},
    }

    assert gate.changed_paths(payload) == ([], True)
    result = gate.gate_decision(payload)

    assert result["decision"] == "block"
    assert result["reason_code"] == "direct_git_effect_requires_lifecycle"
    assert "gt project commit" in result["reason"]
    assert "gt project commit" in result["reason"]


@pytest.mark.parametrize(
    ("command", "subcommand"),
    [
        ('cmd /c "git.exe commit -m nested"', "commit"),
        ('cmd.exe /s /c "git.exe push origin HEAD"', "push"),
        ('powershell.exe -NoProfile -Command "git.exe commit -m nested"', "commit"),
        ('pwsh -c "& git.exe push origin HEAD"', "push"),
        ('bash -c "git commit -m nested"', "commit"),
        ("Write-Output inspected\ngit.exe commit -m nested", "commit"),
    ],
)
def test_shell_wrapped_direct_git_effects_require_lifecycle(
    tmp_path: Path,
    command: str,
    subcommand: str,
) -> None:
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Shell",
        "tool_input": {"command": command},
    }

    result = gate.gate_decision(payload)

    assert result["decision"] == "block"
    assert result["reason_code"] == "direct_git_effect_requires_lifecycle"
    assert "gt project commit" in result["reason"]


@pytest.mark.parametrize(
    "command",
    [
        "powershell.exe -EncodedCommand ZgBvAG8A",
        "pwsh -Command",
        "cmd.exe /c",
        "bash -c",
    ],
)
def test_uninspectable_nested_shell_commands_fail_closed(tmp_path: Path, command: str) -> None:
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Shell",
        "tool_input": {"command": command},
    }

    result = gate.gate_decision(payload)

    assert result["decision"] == "block"
    assert result["reason_code"] == "direct_git_effect_requires_lifecycle"


@pytest.mark.parametrize(
    "command",
    [
        "cmd /c git.exe status --short",
        'powershell.exe -Command "git.exe diff --stat"',
        'bash -c "git log -1"',
    ],
)
def test_shell_wrapped_read_only_git_commands_remain_allowed(tmp_path: Path, command: str) -> None:
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Shell",
        "tool_input": {"command": command},
    }

    assert gate.gate_decision(payload) == {}


@pytest.mark.parametrize(
    ("tool_name", "tool_input", "subcommand"),
    [
        ("Shell", {"command": ["git", "commit", "--amend", "--no-edit"]}, "commit"),
        ("git", {"argv": ["push", "origin", "HEAD"]}, "push"),
        ("git.exe", {"args": ["-C", ".", "commit", "-m", "shell-free"]}, "commit"),
    ],
)
def test_shell_free_direct_git_effect_payloads_fail_closed(
    tmp_path: Path,
    tool_name: str,
    tool_input: dict[str, object],
    subcommand: str,
) -> None:
    payload = {"cwd": str(tmp_path), "tool_name": tool_name, "tool_input": tool_input}

    result = gate.gate_decision(payload)

    assert result["decision"] == "block"
    assert result["reason_code"] == "direct_git_effect_requires_lifecycle"
    assert "gt project commit" in result["reason"]


@pytest.mark.parametrize(
    "tool_input",
    [
        {"argv": ["status", "--short"]},
        {"args": ["-C", ".", "diff", "--stat"]},
    ],
)
def test_shell_free_read_only_git_commands_remain_allowed(
    tmp_path: Path,
    tool_input: dict[str, object],
) -> None:
    payload = {"cwd": str(tmp_path), "tool_name": "git", "tool_input": tool_input}

    assert gate.gate_decision(payload) == {}


def test_chained_git_commit_with_protected_write_still_blocks(tmp_path: Path) -> None:
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Bash",
        "tool_input": {"command": 'git commit -m "x"; Set-Content -Path scripts/sample.py -Value "x"'},
    }

    result = gate.gate_decision(payload)

    assert result["decision"] == "block"
    assert result["reason_code"] == "direct_git_effect_requires_lifecycle"


def test_gate_allows_stderr_redirect_to_dev_null() -> None:
    assert gate._is_mutating_command("python script.py 2>/dev/null") is False


def test_gate_allows_stderr_redirect_to_powershell_null() -> None:
    assert gate._is_mutating_command("python script.py 2>$null") is False


def test_gate_allows_stderr_redirect_to_windows_nul() -> None:
    assert gate._is_mutating_command("python script.py 2>NUL") is False


def test_gate_blocks_unnumbered_redirect_to_file() -> None:
    assert gate._is_mutating_command("cmd > out.txt") is True


def test_gate_blocks_stderr_numbered_redirect_to_real_file() -> None:
    assert gate._is_mutating_command("cmd 2> err.txt") is True


def test_gate_blocks_stdout_numbered_redirect_to_file() -> None:
    assert gate._is_mutating_command("cmd 1> out.txt") is True


def test_gate_blocks_combined_redirect_to_file() -> None:
    assert gate._is_mutating_command("cmd &> out.txt") is True


def test_gate_allows_python_format_spec_right_align() -> None:
    # `:>` is Python format-spec right alignment, not a shell redirect.
    assert gate._is_mutating_command("python -c \"print(f'{n:>2}')\"") is False


def test_gate_allows_python_arrow_token() -> None:
    # `->` is a Python return-annotation arrow, not a shell redirect.
    assert gate._is_mutating_command('python -c "def f() -> int: return 1"') is False


def test_gate_blocks_append_redirect_to_file() -> None:
    assert gate._is_mutating_command("cmd >> out.txt") is True


def test_gate_blocks_no_space_redirect_to_file() -> None:
    # A redirect with no space before `>` is still a real file write.
    assert gate._is_mutating_command("cmd>out.txt") is True


def test_gate_allows_python_ge_comparison() -> None:
    # `>=` is a Python comparison operator, not a shell redirect.
    assert gate._is_mutating_command('python -c "print(1 if i>=0 else 2)"') is False


def test_gate_allows_python_ge_comparison_with_spaces() -> None:
    # A spaced `>=` comparison is still not a shell redirect.
    assert gate._is_mutating_command('python -c "assert x >= 0"') is False


def test_gate_allows_python_rshift_augmented_assignment() -> None:
    # `>>=` is the Python augmented right-shift assignment operator.
    assert gate._is_mutating_command('python -c "x=8; x>>=2; print(x)"') is False


def test_gate_allows_python_sqlite_select_read() -> None:
    cmd = "python -c \"import sqlite3; sqlite3.connect('a.db').execute('SELECT COUNT(*) FROM t').fetchone()\""
    assert gate._is_mutating_command(cmd) is False


def test_gate_allows_python_sqlite_with_read() -> None:
    cmd = (
        'python -c "import sqlite3; '
        "sqlite3.connect('a.db').execute('WITH cte AS (SELECT id FROM t) SELECT * FROM cte')\""
    )
    assert gate._is_mutating_command(cmd) is False


def test_gate_blocks_python_sqlite_pragma_function_call_form() -> None:
    cmd = "python -c \"import sqlite3; sqlite3.connect('a.db').execute('PRAGMA table_info(t)')\""
    assert gate._is_mutating_command(cmd) is True


def test_gate_blocks_python_sqlite_pragma_assignment() -> None:
    cmd = "python -c \"import sqlite3; sqlite3.connect('a.db').execute('PRAGMA journal_mode = WAL')\""
    assert gate._is_mutating_command(cmd) is True


def test_gate_blocks_python_sqlite_user_version_assignment() -> None:
    cmd = "python -c \"import sqlite3; sqlite3.connect('a.db').execute('PRAGMA user_version = 7')\""
    assert gate._is_mutating_command(cmd) is True


def test_gate_blocks_python_sqlite_literal_insert() -> None:
    cmd = "python -c \"import sqlite3; sqlite3.connect('a.db').execute('INSERT INTO t VALUES (1)')\""
    assert gate._is_mutating_command(cmd) is True


def test_gate_blocks_python_sqlite_commit_after_select() -> None:
    cmd = "python -c \"import sqlite3; c=sqlite3.connect('a.db'); c.execute('SELECT * FROM t'); c.commit()\""
    assert gate._is_mutating_command(cmd) is True


@pytest.mark.parametrize(
    "cmd",
    [
        "python -c 'msg = \"sqlite3.connect(a.db).execute(INSERT INTO t VALUES (1))\"; print(msg)'",
        "python -c 'msg = \"Path(x).write_text(y)\"; print(msg)'",
        'python -c \'msg = """open(x, "w")"""; print(msg)\'',
    ],
)
def test_gate_allows_quoted_python_mutation_literals(cmd: str, tmp_path: Path) -> None:
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Bash",
        "tool_input": {"command": cmd},
    }

    assert gate._is_mutating_command(cmd) is False
    assert gate.gate_decision(payload) == {}


@pytest.mark.parametrize(
    "cmd",
    [
        "python -c \"from pathlib import Path; Path('scripts/foo.py').write_text('x')\"",
        "python -c \"open('scripts/foo.py', 'w').write('x')\"",
        "python -c \"import sqlite3; sqlite3.connect('a.db').execute('INSERT INTO t VALUES (1)')\"",
        "python -c \"db.insert_work_item('WI-1')\"",
    ],
)
def test_gate_preserves_python_mutation_true_positives(cmd: str, tmp_path: Path) -> None:
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Bash",
        "tool_input": {"command": cmd},
    }

    assert gate._is_mutating_command(cmd) is True
    result = gate.gate_decision(payload)
    assert result["decision"] == "block"
    assert result["reason_code"] == "unknown_effect_targets"


@pytest.mark.parametrize(("case_id", "command", "expected_spans"), _WI3357_PARSER_CASES)
def test_wi3357_heredoc_parser_recognizes_only_safe_spans(case_id: str, command: str, expected_spans: int) -> None:
    """WI-3357: _find_heredoc_message_substitution_spans recognizes a span only
    when every boundary -- opener, opener-line tail, first delimiter line, and
    post-delimiter close paren -- is validated; every other shape fails closed
    (no span), so the $( stays visible to the control-marker scan."""
    spans = gate._find_heredoc_message_substitution_spans(command)
    assert len(spans) == expected_spans, case_id


def test_impl_start_gate_python_operator_not_mutating() -> None:
    """W4 IP-4 (false-positive removed): a quoted Python comparison or shift
    operator is not misread as a shell redirect, so the command is not flagged
    mutating."""
    assert gate._is_mutating_command('python -c "print(1 if a>b else 0)"') is False
    assert gate._is_mutating_command('python -c "x = value >> 2"') is False
    assert gate._is_mutating_command("python -c 'assert score >= 0'") is False


def test_impl_start_gate_genuine_redirect_still_mutating() -> None:
    """W4 IP-4 (genuine-positive preserved): a standalone shell redirect
    operator token is still flagged mutating, and named-command mutations are
    unaffected by the shlex-based redirect detection."""
    assert gate._is_mutating_command("echo data > out.txt") is True
    assert gate._is_mutating_command("echo data>>out.txt") is True
    assert gate._is_mutating_command("Set-Content -Path scripts/sample.py -Value x") is True


@pytest.mark.parametrize(
    ("command", "expected", "rationale"),
    [
        ("python -m groundtruth_kb projects commit --help", True, "help on a governed CLI"),
        ("gt bridge dispatch report --help", True, "help on the gt CLI"),
        ("sometool --usage", True, "usage flag"),
        ("sometool --help > out.txt", False, "redirection writes a file"),
        ("sometool --help >> out.txt", False, "append redirection writes a file"),
        ("git commit --help && mkdir newdir", False, "chaining is disqualifying"),
        ("chown -h user file", False, "-h is a real operation modifier, not help"),
        ("mkdir /tmp/newdir", False, "plain mutation with no help flag"),
        ("git push origin main", False, "mutation with no help flag"),
    ],
)
def test_help_output_is_classified_read_only(command: str, expected: bool, rationale: str) -> None:
    """WI-6674: a --help/--usage request prints usage text and mutates nothing.

    The WI-3291 prefix allowlist enumerates command verbs, so it cannot express
    help output on an arbitrary governed CLI; such invocations previously fell
    through to ``<unknown-mutating-target>`` and were denied. Redirection and
    chaining must still deny, and ``-h`` must not be admitted as help because it
    is a real operation modifier for some verbs.
    """
    assert gate._is_safe_command(command) is expected, rationale


@pytest.mark.parametrize(
    ("template", "rationale"),
    [
        ("rm -rf {p}", "bare verb at start of command"),
        ("cat payload | tee {p}", "tee reached through a pipe; the pipe alternative must cover it"),
        ("cp a.py {p}", "copy onto a protected path"),
        ("mv a.py {p}", "move onto a protected path"),
        ("true && rm {p}", "verb after an && chain"),
        ("echo hi; touch {p}", "verb after a semicolon"),
        ("(cd scripts && rm {p})", "verb inside a subshell, after an opening paren"),
    ],
)
def test_change7_preserves_command_position_mutation_detection(template: str, rationale: str) -> None:
    """WI-6821: every real mutation sits at command position and must still fire.

    This is the anti-regression half of Change 7. The narrowing is acceptable
    only if it drops argument-position prose WITHOUT dropping any of these; a
    miss here means the F10 enforcement hole has been reopened.
    """
    assert gate._has_mutating_signal(template.format(p=PROTECTED_GATE_PATH)), rationale


@pytest.mark.parametrize(
    ("command", "rationale"),
    [
        ("git log --grep=rm", "write verb inside a --grep value is prose, not a command"),
        ("git log --grep=cp --oneline", "same, with a trailing flag"),
        ("git log --format=%h --grep=install", "write verb inside a --grep value"),
        ("grep -rn dd scripts/", "a write verb used as a search pattern operand"),
        ("git for-each-ref --format=%(refname)", "read-only ref enumeration (F3)"),
    ],
)
def test_change7_drops_argument_position_false_positives(command: str, rationale: str) -> None:
    """WI-6821: a write verb in argument position is prose and must not fire.

    These are the materialized false positives that motivated Change 7: the
    unanchored form blocked read-only inspection commands whose only offense
    was carrying a write verb inside a flag value.
    """
    assert not gate._has_mutating_signal(command), rationale
