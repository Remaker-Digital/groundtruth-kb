"""A program run needs a live claim of the bound context (c123, owner decision A1; batch design WP1 item 5, option A).

M13 on c121: the GT-KB Home's bound Q1 context, holding no claim, ran
`.\\groundtruth-kb\\.venv\\Scripts\\python.exe .tmp\\m13-probe\\program-write-probe.py`, and the script wrote its file:
the gate judges a command's text, and what a program writes is not in it. Owner decision 2026-10-01 05:32 (A1, option
A): a program run needs a live claim of the bound context, of any intended status, so a verifier's verdict claim counts;
`python -m pytest` included. The native `gt bridge check-program` confirms the claim, an unbound context is refused, and
a command with a write and a program has both checked. A claim ties the run to a delivery and does not bound the program,
so the refusal says that inside a claim the program can still write outside the claim's targets. Every command here is
judged, never run; the native checks are a recorder.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from groundtruth_kb.bridge import effect_gate

OWN = "SENV-" + "a1" * 16
M13_PROGRAM = r".\groundtruth-kb\.venv\Scripts\python.exe .tmp\m13-probe\program-write-probe.py"
CLAIM_REFUSAL = "Error: program_claim_required: A program run needs a live claim of this context.\n"


class _NativeChecks:
    """Stands in for `gt bridge check-effects` and `gt bridge check-program`: records each call and answers as the
    native checks do for a context that holds a live claim, or holds none."""

    def __init__(self, claimed: bool = True, program_stderr: str = CLAIM_REFUSAL) -> None:
        self.claimed = claimed
        self.program_stderr = program_stderr
        self.calls: list[tuple[list[str], dict]] = []

    def __call__(self, argv, **kwargs):
        self.calls.append((list(argv), kwargs))
        if "check-program" in argv:
            if self.claimed:
                answer = {"status": "current", "scope": "program", "claims": 1}
                return subprocess.CompletedProcess(argv, 0, json.dumps(answer), "")
            return subprocess.CompletedProcess(argv, 1, "", self.program_stderr)
        if self.claimed:
            return subprocess.CompletedProcess(
                argv, 0, json.dumps({"status": "current", "scope": "implementation"}), ""
            )
        return subprocess.CompletedProcess(argv, 1, "", "Error: implementation_claim_required: no claim covers it\n")

    def verbs(self) -> list[str]:
        return [argv[4] for argv, _kwargs in self.calls]


@pytest.fixture(autouse=True)
def _payload_context(monkeypatch):
    # The gate prefers the harness's own context variable to the payload's session id; these payloads carry the id.
    monkeypatch.delenv("GTKB_NATIVE_CONTEXT_ID", raising=False)
    monkeypatch.setattr(effect_gate, "_bound_session_context", lambda payload, project: (OWN, True))


def _payload(project: Path, command: object, *, session: str | None = "program-runs-test") -> dict:
    payload = {
        "tool_name": "Bash",
        "tool_input": {"command": command},
        "cwd": str(project),
        "project_root": str(project),
    }
    if session:
        payload["session_id"] = session
    return payload


def _decide(project: Path, command: object, **kwargs) -> dict:
    return effect_gate.gate_decision(_payload(project, command, **kwargs))


def _no_cli(monkeypatch) -> None:
    monkeypatch.setattr(effect_gate.subprocess, "run", lambda *_a, **_k: pytest.fail("the native check must not run"))


# ---- the M13 command, verbatim ----------------------------------------------------------------------------------------
def test_the_m13_command_is_refused_for_an_unbound_context(tmp_path, monkeypatch):
    _no_cli(monkeypatch)
    result = _decide(tmp_path, M13_PROGRAM, session=None)
    assert result["reason_code"] == "invalid_native_context", result
    assert "program-write-probe.py" in result["reason"] and "live claim" in result["reason"]


def test_the_m13_command_needs_a_live_claim_of_the_bound_context(tmp_path, monkeypatch):
    native = _NativeChecks(claimed=False)
    monkeypatch.setattr(effect_gate.subprocess, "run", native)
    result = _decide(tmp_path, M13_PROGRAM)
    assert result["reason_code"] == "program_claim_required", result
    assert "Error" not in result["reason"] and "program-write-probe.py" in result["reason"]
    # The residual: a claim does not bound the program.
    assert "can still write outside the claim's targets" in result["reason"]
    assert native.verbs() == ["check-program"]


def test_the_m13_command_runs_inside_a_claim(tmp_path, monkeypatch):
    native = _NativeChecks(claimed=True)
    monkeypatch.setattr(effect_gate.subprocess, "run", native)
    assert _decide(tmp_path, M13_PROGRAM) == {}
    assert native.verbs() == ["check-program"]


def test_an_unbound_native_context_gets_the_binding_error_the_check_raises(tmp_path, monkeypatch):
    native = _NativeChecks(
        claimed=False, program_stderr="Error: no_session_binding: The native context is not bound.\n"
    )
    monkeypatch.setattr(effect_gate.subprocess, "run", native)
    result = _decide(tmp_path, M13_PROGRAM)
    assert result["reason_code"] == "no_session_binding", result
    assert result["reason"].startswith("The native context is not bound.")


def test_the_program_check_is_called_as_the_effect_check_is(tmp_path, monkeypatch):
    native = _NativeChecks(claimed=True)
    monkeypatch.setattr(effect_gate.subprocess, "run", native)
    monkeypatch.setenv("GTKB_NATIVE_CONTEXT_ID", "native-current")
    assert _decide(tmp_path, "python x.py", session="native-current") == {}
    (argv, kwargs), *rest = native.calls
    assert not rest
    # Any live claim counts, of any intended status: the gate asks for none.
    assert argv == [
        sys.executable,
        "-m",
        "groundtruth_kb",
        "bridge",
        "check-program",
        "--native-context-id",
        "native-current",
        "--json",
    ]
    assert kwargs["cwd"] == tmp_path.resolve()
    assert kwargs["env"]["GT_PROJECT_ROOT"] == str(tmp_path.resolve())
    assert kwargs["env"]["PYTHONIOENCODING"] == kwargs["encoding"] == "utf-8"
    assert kwargs["timeout"] == 10


@pytest.mark.parametrize(
    ("response", "code", "cause"),
    [
        (subprocess.TimeoutExpired("gt", 10), "effect_check_unavailable", "did not answer within 10 seconds"),
        (FileNotFoundError("gt"), "effect_check_unavailable", "could not start (FileNotFoundError)"),
        (subprocess.CompletedProcess([], 0, "not json", ""), "effect_check_unavailable", "not JSON"),
        (
            subprocess.CompletedProcess([], 0, '{"status": "current", "scope": "implementation"}', ""),
            "invalid_effect_response",
            "current program check",
        ),
        (subprocess.CompletedProcess([], 0, "{}", ""), "invalid_effect_response", "current program check"),
        (subprocess.CompletedProcess([], 1, "", "claim_expired"), "native_effect_refused", "claim_expired"),
        (subprocess.CompletedProcess([], 1, "", ""), "native_effect_refused", "refused the program check"),
    ],
)
def test_an_unavailable_or_invalid_program_check_refuses(tmp_path, monkeypatch, response, code, cause):
    def run(*_args, **_kwargs):
        if isinstance(response, BaseException):
            raise response
        return response

    monkeypatch.setattr(effect_gate.subprocess, "run", run)
    result = _decide(tmp_path, "python x.py")
    assert result["decision"] == "block" and result["reason_code"] == code, result
    assert cause in result["reason"]


# ---- every form section 5 lists as a program run ----------------------------------------------------------------------
PROGRAM_RUNS = [
    # an interpreter given code
    "python x.py",
    "py -3 x.py",
    "Get-Content x.py | python -",
    "python",
    "python -m pytest -q",
    "python -m pytest platform_tests/scripts/test_sample.py -q",
    "python -m pip install x",
    "python -X utf8 -m http.server",
    "pytest -q",
    "python -c \"import subprocess; subprocess.run(['x'])\"",
    "node x.js",
    "node -e \"require('fs').writeFileSync('x','y')\"",
    "node -p 1+1",
    "deno run x.ts",
    "bun x.ts",
    "perl -i -pe s/a/b/ f.txt",
    "pwsh -File x.ps1",
    r"powershell -NoProfile -ExecutionPolicy Bypass -File .\x.ps1",
    "pwsh x.ps1",
    "bash x.sh",
    "sh x.sh",
    'bash -lc "rm x"',
    # a script or an executable inside the project, a checkout or scratch
    r".\build.bat",
    "build.cmd",
    r".\x.ps1",
    r"& .\x.ps1",
    r". .\x.ps1",
    r".\tools\x.exe",
    r"scratchpad\x\tool.exe",
    # package and build runners
    "npm run build",
    "npm test",
    "npm start",
    "npm exec x",
    "npm install",
    "npm.cmd run build",
    "pnpm run x",
    "yarn run x",
    "yarn build",
    "npx eslint .",
    "uvx ruff check x.py",
    "uv run python x.py",
    "uv run ruff check --fix x.py",
    "uv sync",
    "pip install x",
    "make",
    "cargo run",
    "cargo build",
    "dotnet run",
    "dotnet test",
    "go run x.go",
    # PowerShell code loaders
    r"Import-Module .\m.psm1",
    "Import-Module -Name ./tools/m.psd1",
    "Add-Type -TypeDefinition 'public class X {}'",
    "New-Object -ComObject WScript.Shell",
    # gt commands that write local files
    "gt harness project codex",
    "gt harness project codex --check",
    "gt scaffold iac --apply",
    "gt controls propose --control x --value 1 --output p.toml",
    "gt dashboard init",
    "gt dashboard refresh",
    "gt db postgres export-current --sqlite-snapshot a.db --transform-plan t.json --output m.json",
    "gt db postgres readback-current --output m.json",
    "gt validate spec-coherence --output out",
    "gt project init app --project-id P --host-root . --owner o",
    "gt project chroma regenerate",
    "gt project classify-tree --dir . --output report.md",
    "gt project upgrade app --project-id P --host-root . --apply",
    "gt application register app --host-root .",
    "gt env migrate --apply",
    "gt registry reconcile --batch-output b.json",
    "gt registry register --record-json '{}'",
    "gt secrets scan --tracked --redacted --report-json r.json",
    "gt commit preflight",
    "gt push readiness --evidence-out e.json",
    "python -m groundtruth_kb dashboard init",
    r"E:\GT-KB\groundtruth-kb\.venv\Scripts\gt.exe harness project codex",
    # rg's preprocessor
    "rg --pre ./pre.sh x",
    # launched and handed programs
    "Start-Process python -ArgumentList x.py",
    'cmd /c "python x.py"',
    'pwsh -NoProfile -Command "python x.py"',
    "bash -c 'python x.py'",
    "if true; then python x.py; fi",
]


@pytest.mark.parametrize("command", PROGRAM_RUNS)
def test_each_program_run_needs_a_live_claim(tmp_path, monkeypatch, command):
    native = _NativeChecks(claimed=False)
    monkeypatch.setattr(effect_gate.subprocess, "run", native)
    result = _decide(tmp_path, command)
    assert result["reason_code"] == "program_claim_required", result
    assert native.verbs() == ["check-program"]


@pytest.mark.parametrize(
    "source",
    [
        "import os; os.system('x')",
        "import os; os.popen('x')",
        "import os; os.execv('x', ['x'])",
        "import os; os.spawnl(os.P_WAIT, 'x')",
        "import os; os.startfile('x')",
        "from os import system as s; s('x')",
        "import subprocess as sp; sp.Popen(['x'])",
        "from subprocess import check_output; check_output(['x'])",
        "import runpy; runpy.run_path('x.py')",
        "exec(open('x.py').read())",
        "eval('1')",
        "compile('1', 'x', 'eval')",
        "__import__('os')",
        "import importlib; importlib.import_module('x')",
        "import ctypes; ctypes.CDLL('x.dll')",
        # A module from outside the standard library runs its code on import: this runs probe.py from the working
        # directory exactly as `python probe.py` does.
        "import probe",
        "from groundtruth_kb import cli",
        "from . import x",
    ],
)
def test_a_python_c_source_that_starts_a_process_or_loads_code_is_a_program_run(tmp_path, source):
    assert effect_gate._program_run(_payload(tmp_path, f'python -c "{source}"')) is not None


@pytest.mark.parametrize(
    "source",
    [
        "print(1)",
        "import json; print(json.dumps({}))",
        "import os; print(os.getcwd())",
        "import subprocess; print(subprocess.list2cmdline(['a', 'b']))",
        "from pathlib import Path; print(Path('x').read_text())",
    ],
)
def test_a_python_c_source_that_only_computes_is_no_program_run(tmp_path, source):
    assert effect_gate._program_run(_payload(tmp_path, f'python -c "{source}"')) is None


# ---- what stays allowed -----------------------------------------------------------------------------------------------
NOT_PROGRAMS = [
    'python -c "print(1)"',
    "python --version",
    "py --list",
    "python -m json.tool a.json",
    "python -m pip show x",
    "python -X utf8 -m groundtruth_kb services status",
    'python -c "import json; print(json.dumps({\\"a\\": 1}))"',
    "gt bridge show x --content --json",
    "gt projects list",
    "gt services status",
    "gt home status",
    "gt db postgres status",
    "gt harness diagnostic --harness-id x",
    "gt scaffold iac",
    r".\groundtruth-kb\.venv\Scripts\gt.exe --help",
    "rg x",
    "Get-Content x",
    "git status",
    "node --version",
    "node --check x.js",
    "pytest --version",
    "npm --version",
    "npm ls",
    "uv --version",
    "uv pip list",
    "pip list",
    "cargo --version",
    "dotnet --info",
    "go version",
    "make --version",
    "Import-Module PSReadLine",
    "Start-Process notepad",
    'pwsh -NoProfile -Command "Get-ChildItem"',
    'cmd /c "dir"',
    "bash -c 'ls'",
    "python -m ruff check --no-fix --no-fix-only x.py",
    "ruff check --diff x.py",
    r"& 'C:\Program Files\Git\cmd\git.exe' --version 2>&1 | Out-String",
]


@pytest.mark.parametrize("command", NOT_PROGRAMS)
def test_reads_and_non_programs_need_no_claim(tmp_path, monkeypatch, command):
    _no_cli(monkeypatch)
    assert _decide(tmp_path, command) == {}


def test_pytest_left_the_safe_prefixes(tmp_path):
    command = "python -m pytest -q"
    assert "python -m pytest" not in effect_gate.SAFE_COMMAND_PREFIXES
    assert effect_gate._is_safe_command(command) is False
    # A test run writes nothing the command names: it is a program run, not a write.
    assert effect_gate.changed_paths(_payload(tmp_path, command)) == ([], False)
    assert effect_gate._program_run(_payload(tmp_path, command)) == command


# ---- a command with a write and a program -----------------------------------------------------------------------------
def test_a_command_with_a_write_and_a_program_has_both_checked(tmp_path, monkeypatch):
    command = "Set-Content notes.txt x; python x.py"
    claimed = _NativeChecks(claimed=True)
    monkeypatch.setattr(effect_gate.subprocess, "run", claimed)
    assert _decide(tmp_path, command) == {}
    assert claimed.verbs() == ["check-effects", "check-program"]
    assert claimed.calls[0][0][-2:] == ["--path", "notes.txt"]


def test_the_writes_are_checked_before_the_program(tmp_path, monkeypatch):
    native = _NativeChecks(claimed=False)
    monkeypatch.setattr(effect_gate.subprocess, "run", native)
    result = _decide(tmp_path, "Set-Content notes.txt x; python x.py")
    assert result["reason_code"] == "implementation_claim_required", result
    assert native.verbs() == ["check-effects"]


def test_a_program_with_a_write_the_gate_cannot_read_is_refused_before_any_check(tmp_path, monkeypatch):
    _no_cli(monkeypatch)
    assert _decide(tmp_path, "python x.py > $out")["reason_code"] == "unknown_effect_targets"


def test_a_program_named_by_a_variable_fails_the_program_rule_closed_on_its_own(tmp_path):
    # The Git rule refuses this first; the program rule does not depend on it.
    assert effect_gate._program_run(_payload(tmp_path, "& $tool x.py")) == "a command the gate cannot inspect"
    assert _decide(tmp_path, "& $tool x.py")["reason_code"] == "direct_git_effect_requires_lifecycle"
