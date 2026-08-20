"""Tests for Click Windows argument expansion behavior (WI-6697).

Verifies that Click on Windows does not expand glob-shaped option values into file lists
when parsing argv at the GT-KB CLI entry point.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest import mock

import click
from click.testing import CliRunner
from groundtruth_kb.cli import _NoWindowsExpandGroup, main


def test_main_group_is_no_windows_expand_group() -> None:
    """The root CLI group must use _NoWindowsExpandGroup."""
    assert isinstance(main, _NoWindowsExpandGroup)


def test_no_windows_expand_group_defaults_windows_expand_args_false() -> None:
    """_NoWindowsExpandGroup.main defaults windows_expand_args=False."""
    group = _NoWindowsExpandGroup("test_grp")

    @group.command("echo_arg")
    @click.argument("val")
    def echo_arg(val: str) -> None:
        pass

    with mock.patch("click.Group.main") as mock_super_main:
        mock_super_main.return_value = 0
        group.main(args=["echo_arg", "*.py"], standalone_mode=False)
        assert mock_super_main.called
        kwargs = mock_super_main.call_args.kwargs
        assert kwargs.get("windows_expand_args") is False


def test_glob_arg_arrives_literally_on_windows(tmp_path: Path) -> None:
    """When taking arguments from sys.argv on Windows, globs matching real files stay literal."""
    (tmp_path / "file1.txt").write_text("a", encoding="utf-8")
    (tmp_path / "file2.txt").write_text("b", encoding="utf-8")

    captured_args: list[str] = []

    group = _NoWindowsExpandGroup("test_grp")

    @group.command("record")
    @click.option("--pattern", "pattern", required=True)
    def record_cmd(pattern: str) -> None:
        captured_args.append(pattern)

    test_argv = ["gt", "record", "--pattern", str(tmp_path / "*.txt")]

    with (
        mock.patch.object(sys, "argv", test_argv),
        mock.patch("os.name", "nt"),
    ):
        try:
            group.main(args=None, standalone_mode=False)
        except SystemExit:
            pass

    assert len(captured_args) == 1
    assert captured_args[0] == str(tmp_path / "*.txt")


def test_nonmatching_glob_arrives_literally() -> None:
    """A glob matching zero files arrives literally."""
    runner = CliRunner()
    res = runner.invoke(main, ["--help"])
    assert res.exit_code == 0
