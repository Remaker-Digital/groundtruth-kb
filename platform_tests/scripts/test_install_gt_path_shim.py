"""Tests for the WI-4530 in-root ``gt`` PATH-shim content/path generator.

Per ``bridge/gtkb-wi4530-gt-cli-path-install-shim-001.md`` (NEW) and ``-002``
(Codex GO). Covers the eight acceptance criteria in the proposal's Verification
Plan plus the GO condition #2 ``__main__`` / stdout smoke coverage.

The helper is path-pure and string-pure: ``test_helper_does_no_io`` inspects the
module source (AST) to assert no file write, no PATH/env mutation, and no
subprocess launch in any public function -- preserving the in-root invariant
that this slice performs no out-of-root placement.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import install_gt_path_shim as helper  # noqa: E402

# A fixture project root. Plain (no spaces) for the path-resolution + render
# shape tests; the spaces variant is exercised separately.
_ROOT = Path("E:/fixture-root")
_ROOT_WITH_SPACES = Path("E:/fixture root/My GT-KB")


def test_resolve_venv_gt_exe_windows() -> None:
    """Windows venv-exe path resolution (WI-4530 root)."""
    expected = _ROOT / "groundtruth-kb" / ".venv" / "Scripts" / "gt.exe"
    assert helper.resolve_venv_gt_exe(_ROOT, "win32") == expected


@pytest.mark.parametrize("platform", ["linux", "darwin"])
def test_resolve_venv_gt_exe_posix(platform: str) -> None:
    """POSIX venv-exe path resolution for both supported POSIX tokens."""
    expected = _ROOT / "groundtruth-kb" / ".venv" / "bin" / "gt"
    assert helper.resolve_venv_gt_exe(_ROOT, platform) == expected


def test_resolve_venv_gt_exe_unsupported_platform() -> None:
    """An unsupported platform string raises ValueError with a clear message."""
    with pytest.raises(ValueError) as excinfo:
        helper.resolve_venv_gt_exe(_ROOT, "freebsd")
    message = str(excinfo.value)
    assert "freebsd" in message
    assert "Unsupported platform" in message


def test_windows_cmd_shim_forwards_args() -> None:
    """Windows .cmd content forwards all args to the quoted venv exe."""
    venv_exe = helper.resolve_venv_gt_exe(_ROOT, "win32")
    content = helper.render_windows_cmd_shim(venv_exe)
    assert content.startswith("@echo off\n")
    assert "WI-4530" in content
    assert f'"{venv_exe}"' in content
    assert "%*" in content


def test_posix_shell_shim_uses_exec_and_quoted_args() -> None:
    """POSIX shell shim has a shebang, uses exec, and forwards quoted "$@"."""
    venv_exe = helper.resolve_venv_gt_exe(_ROOT, "linux")
    content = helper.render_posix_shell_shim(venv_exe)
    assert content.startswith("#!/usr/bin/env bash\n")
    assert "WI-4530" in content
    assert "exec " in content
    assert f'"{venv_exe}"' in content
    assert '"$@"' in content


@pytest.mark.parametrize("platform", ["win32", "linux", "darwin"])
def test_shim_quotes_path_with_spaces(platform: str) -> None:
    """A venv-exe path with spaces is double-quoted intact on both platforms."""
    rendered = helper.render_for_platform(_ROOT_WITH_SPACES, platform)
    venv_exe = rendered["venv_exe"]
    assert " " in venv_exe  # the fixture really does contain a space
    # The quoted span must appear verbatim (not split or unquoted) in content.
    assert f'"{venv_exe}"' in rendered["content"]


def test_render_for_platform_shape() -> None:
    """Convenience wrapper returns filename + content + venv_exe, consistently."""
    win = helper.render_for_platform(_ROOT, "win32")
    assert win["filename"] == "gt.cmd"
    assert win["content"] == helper.render_windows_cmd_shim(helper.resolve_venv_gt_exe(_ROOT, "win32"))
    assert win["venv_exe"] == str(helper.resolve_venv_gt_exe(_ROOT, "win32"))

    posix = helper.render_for_platform(_ROOT, "linux")
    assert posix["filename"] == "gt"
    assert posix["content"] == helper.render_posix_shell_shim(helper.resolve_venv_gt_exe(_ROOT, "linux"))
    assert posix["venv_exe"] == str(helper.resolve_venv_gt_exe(_ROOT, "linux"))


def test_render_for_platform_unsupported_platform() -> None:
    """The wrapper rejects an unsupported platform the same way resolution does."""
    with pytest.raises(ValueError):
        helper.render_for_platform(_ROOT, "freebsd")


def test_helper_does_no_io() -> None:
    """In-root constraint: no file write, no PATH/env mutation, no subprocess.

    AST inspection of the whole module source (covers import time and every
    public function): assert there is no ``Path.write_text`` / ``.write_bytes``,
    no ``open(...)`` call, no ``os.environ`` access, and no ``subprocess`` import
    or use. Printing to stdout (the manual-use entrypoint) is explicitly allowed
    and is NOT a prohibited write.
    """
    source = Path(helper.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)

    for node in ast.walk(tree):
        # No subprocess import anywhere.
        if isinstance(node, ast.Import):
            assert all(alias.name != "subprocess" for alias in node.names), "module must not import subprocess"
        if isinstance(node, ast.ImportFrom):
            assert node.module != "subprocess", "module must not import from subprocess"
        # No os.environ access (read or mutate).
        if isinstance(node, ast.Attribute) and node.attr == "environ":
            value = node.value
            assert not (isinstance(value, ast.Name) and value.id == "os"), "module must not touch os.environ"
        if isinstance(node, ast.Call):
            func = node.func
            # No open(...) calls (no file handles).
            assert not (isinstance(func, ast.Name) and func.id == "open"), "module must not call open()"
            if isinstance(func, ast.Attribute):
                # No Path.write_text / write_bytes file writes.
                assert func.attr not in {"write_text", "write_bytes"}, "module must not write files via pathlib"
                # No subprocess.run / Popen / call.
                assert func.attr not in {"run", "Popen", "call", "check_output"}, "module must not launch subprocesses"


def test_main_emits_windows_content_to_stdout(capsys: pytest.CaptureFixture) -> None:
    """GO condition #2: the __main__ entrypoint prints rendered content, returns 0."""
    rc = helper.main(["--platform", "win32", "--project-root", str(_ROOT)])
    assert rc == 0
    out = capsys.readouterr().out
    assert out == helper.render_for_platform(_ROOT, "win32")["content"]


def test_main_unsupported_platform_returns_2(capsys: pytest.CaptureFixture) -> None:
    """GO condition #2: an unsupported --platform exits 2 with a stderr message."""
    rc = helper.main(["--platform", "freebsd", "--project-root", str(_ROOT)])
    assert rc == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "freebsd" in captured.err
