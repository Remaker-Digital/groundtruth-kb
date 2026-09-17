"""Regression tests for the in-root ``gt`` launcher's argument forwarding (WI-5845).

The launcher at ``scripts/gt.ps1`` must hand every argument to the project CLI
byte-for-byte, including arguments that contain embedded newlines. The defect
under repair is truncation at the first newline, which happens when a launcher
reconstructs a command string instead of splatting the argument array.

Cases 1-4 are behavioural against the real launcher rather than assertions about
its text, per SPEC-1662 (GOV-18). Case 5 is deliberately structural: the
property under test is a root-boundary invariant of the file itself, which no
behavioural assertion can express.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LAUNCHER = PROJECT_ROOT / "scripts" / "gt.ps1"
VENV_PYTHON = PROJECT_ROOT / "groundtruth-kb" / ".venv" / "Scripts" / "python.exe"

MULTILINE_ARG = "alpha\nbeta"
# Click's usage error for an unknown command, or the CLI group's own refusal of a name with no native route.
NO_SUCH_COMMAND = re.compile(r"No such command '(.*?)'\.|'(.*?)' has no native authority route\.", re.DOTALL)


def _powershell() -> str:
    for candidate in ("pwsh", "powershell"):
        found = shutil.which(candidate)
        if found:
            return found
    pytest.skip("no PowerShell interpreter available on this host")
    raise AssertionError("unreachable")


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    """Invoke the real launcher with the given argument vector."""
    if sys.platform != "win32":
        pytest.skip("the gt.ps1 launcher targets the Windows project venv layout")
    if not LAUNCHER.is_file():
        pytest.fail(f"launcher missing at {LAUNCHER}")
    if not VENV_PYTHON.is_file():
        # The launcher resolves the interpreter by in-root relative path; a qualification clone has no project
        # interpreter, so the forwarding cases are measured only where the production layout exists.
        pytest.skip(f"project interpreter missing at {VENV_PYTHON}; the launcher is exercised on the production host")
    return subprocess.run(
        [_powershell(), "-NoProfile", "-File", str(LAUNCHER), *args],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
        timeout=180,
    )


def _run_direct(*args: str) -> subprocess.CompletedProcess[str]:
    """Invoke the CLI with the launcher entirely out of the path.

    This is the transparency oracle: whatever the launcher produces must match
    what the interpreter produces when handed the identical argument vector.
    """
    if not VENV_PYTHON.is_file():
        pytest.skip(f"project interpreter missing at {VENV_PYTHON}")
    return subprocess.run(
        [str(VENV_PYTHON), "-m", "groundtruth_kb.cli", *args],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
        timeout=180,
    )


def _rejected_command_payload(result: subprocess.CompletedProcess[str]) -> str:
    """Return the argument the CLI echoes back when it rejects it as a command.

    Click escapes control characters when rendering this message, so an embedded
    newline appears as a literal backslash-n. The payload is therefore compared
    against the direct-invocation payload rather than against the raw argument.
    """
    stream = result.stderr + "\n" + result.stdout
    match = NO_SUCH_COMMAND.search(stream)
    assert match is not None, "CLI did not echo the rejected command back:\n" + stream
    return next(group for group in match.groups() if group is not None)


def test_newline_bearing_argument_arrives_as_a_single_argument() -> None:
    """Case 1: an argument containing a newline survives as one argument."""
    payload = _rejected_command_payload(_run(MULTILINE_ARG))
    assert "alpha" in payload and "beta" in payload, (
        f"both halves of the newline-bearing argument must arrive: {payload!r}"
    )
    assert payload == _rejected_command_payload(_run_direct(MULTILINE_ARG)), (
        "launcher must be transparent: its argument boundary must match direct invocation"
    )


def test_multiline_argument_is_not_truncated_at_the_first_newline() -> None:
    """Case 2: the argument arrives byte-identical, not cut at the newline."""
    payload = _rejected_command_payload(_run(MULTILINE_ARG))
    assert payload != "alpha", "argument was truncated at the first newline"
    assert payload == _rejected_command_payload(_run_direct(MULTILINE_ARG))


def test_trailing_flag_survives_after_a_newline_bearing_argument(tmp_path: Path) -> None:
    """Case 3: trailing flags after a multi-line value survive.

    ``--format json`` stands in as the observable trailing flag on an authority-free
    read-only command: when it reaches the CLI the tree classification is emitted
    as JSON, and when it is discarded the same command emits the Markdown report.
    """
    tree = tmp_path / "tree"
    tree.mkdir()
    (tree / MULTILINE_ARG.replace("\n", "_")).write_text("x\n", encoding="utf-8")
    result = _run("project", "classify-tree", "--dir", str(tree), "--ignore-glob", MULTILINE_ARG, "--format", "json")
    assert result.returncode == 0, result.stderr
    assert result.stdout.lstrip().startswith("{"), (
        f"trailing --format json did not reach the CLI after a newline-bearing argument; got: {result.stdout!r}"
    )


def test_special_characters_are_forwarded_without_reinterpretation() -> None:
    """Case 4: spaces, double quotes and a literal ``@`` pass through intact."""
    special = 'spa ce "q" @at'
    assert _rejected_command_payload(_run(special)) == special


def test_launcher_resolves_the_interpreter_by_in_root_relative_path() -> None:
    """Case 5: structural root-boundary invariant of the launcher file itself."""
    text = LAUNCHER.read_text(encoding="utf-8")
    assert "$PSScriptRoot" in text, "launcher must anchor on its own location"
    assert "groundtruth-kb/.venv/Scripts/python.exe" in text
    assert "@args" in text, "launcher must splat the argument array, not rebuild a string"
    offenders = re.findall(r"[A-Za-z]:[\/][^\s'\"]*", text)
    assert not offenders, f"out-of-root absolute path literal in launcher: {offenders}"
    assert ".local" not in text
