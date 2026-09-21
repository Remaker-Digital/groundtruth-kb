"""Tests for groundtruth_kb.cli module."""

from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner
from platform_tests.groundtruth_kb.native_fixtures import assertion_source as assertion_source
from platform_tests.groundtruth_kb.native_fixtures import native as native

from groundtruth_kb.cli import main


def test_cli_module_invocation_dispatches_help() -> None:
    package = subprocess.run(
        [sys.executable, "-m", "groundtruth_kb", "--help"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    module = subprocess.run(
        [sys.executable, "-m", "groundtruth_kb.cli", "--help"],
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert package.returncode == 0, package.stderr
    assert module.returncode == 0, module.stderr
    assert "Usage:" in module.stdout
    assert "Commands:" in module.stdout
    assert "backlog" in module.stdout
    assert module.stdout.replace("groundtruth_kb.cli", "groundtruth_kb") == package.stdout


def _force_rmtree(path: Path) -> None:
    """Remove a sandbox tree, clearing read-only bits then retrying; fails loudly.

    Replaces ``shutil.rmtree(path, ignore_errors=True)`` at the in-root
    ``applications/_test_*`` cleanup site (FAB-08 / HYG-053). On Windows, git
    object files under ``.git`` are read-only and make ``shutil.rmtree`` raise;
    the ``onexc`` handler clears the read-only bit and retries. Unlike
    ``ignore_errors=True``, a real failure propagates (cleanup must fail loudly
    per the FAB-08 GO constraint). Defined self-contained here because the three
    FAB-08 target files cannot share a new helper module without expanding the
    GO'd ``target_paths``; consolidation is a follow-on.
    """

    def _on_rm_error(func, p, exc):  # exc = the raised exception instance
        os.chmod(p, stat.S_IWRITE)
        func(p)

    if not path.exists():
        return
    if sys.version_info >= (3, 12):
        # py3.12+ shutil.rmtree onexc signature (exc is the exception instance)
        shutil.rmtree(path, onexc=_on_rm_error)
    else:
        # py3.11 shutil.rmtree onerror passes an exc_info tuple; adapt it to the
        # (func, path, exc) handler above so behavior matches across runtimes.
        shutil.rmtree(
            path,
            onerror=lambda func, p, exc_info: _on_rm_error(func, p, exc_info[1]),
        )


# ---------------------------------------------------------------------------
# gt init
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# gt seed
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# gt history
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# gt assert
# ---------------------------------------------------------------------------


class TestAssert:
    pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]

    def test_assert_no_specs(self, runner: CliRunner, assertion_source) -> None:
        config, _, snapshot, calls = assertion_source
        before = snapshot()
        result = runner.invoke(main, ["--config", str(config), "assert", "--json"])
        assert result.exit_code == 1, result.output
        report = json.loads(result.output)
        assert report["total_specs"] == report["passed"] == 0
        assert report["aggregate_result"] == "UNASSESSED"
        assert snapshot() == before and all(method == "GET" for method, _ in calls)

    def test_assert_with_passing_spec(self, runner: CliRunner, assertion_source) -> None:
        config, record, snapshot, calls = assertion_source
        record(
            "GOV-01",
            {
                "title": "Required effect",
                "status": "active",
                "assertions": [{"type": "grep", "file": "effect.py", "pattern": "value = 1"}],
            },
        )
        before = snapshot()
        result = runner.invoke(main, ["--config", str(config), "assert"])
        assert result.exit_code == 0, result.output
        assert "PASSED" in result.output and "GOV-01" in result.output
        assert snapshot() == before and all(method == "GET" for method, _ in calls)

    def test_assert_single_spec(self, runner: CliRunner, assertion_source) -> None:
        config, record, snapshot, calls = assertion_source
        record(
            "GOV-01",
            {
                "title": "Selected effect",
                "status": "active",
                "assertions": [{"type": "grep", "file": "effect.py", "pattern": "value = 1"}],
            },
        )
        record(
            "GOV-02",
            {
                "title": "Unselected effect",
                "status": "active",
                "assertions": [{"type": "file_exists", "file": "missing.py"}],
            },
        )
        before = snapshot()
        result = runner.invoke(main, ["--config", str(config), "assert", "--spec", "GOV-01", "--json"])
        assert result.exit_code == 0, result.output
        report = json.loads(result.output)
        assert report["aggregate_result"] == "PASS" and report["total_specs"] == 1
        assert report["details"][0]["spec_id"] == "GOV-01" and report["details"][0]["spec_version"] == 1
        assert snapshot() == before and all(method == "GET" for method, _ in calls)


# ---------------------------------------------------------------------------
# gt export / import
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# gt config
# ---------------------------------------------------------------------------


class TestConfig:
    def test_config_shows_values(self, runner: CliRunner, project_dir: Path) -> None:
        result = runner.invoke(main, ["--config", str(project_dir / "groundtruth.toml"), "config"])
        assert result.exit_code == 0
        assert "Test Project" in result.output
        assert "db_path" in result.output

    def test_config_chroma_path_explicit(self, runner: CliRunner, project_dir: Path) -> None:
        """When chroma_path is set in config, gt config shows the explicit path."""
        toml_path = project_dir / "groundtruth.toml"
        text = toml_path.read_text()
        text += '\n[search]\nchroma_path = "./my-chroma"\n'
        toml_path.write_text(text)
        result = runner.invoke(main, ["--config", str(toml_path), "config"])
        assert result.exit_code == 0
        assert "my-chroma" in result.output
        assert "unset" not in result.output

    @pytest.mark.parametrize("present", [False, True], ids=["missing-module", "present-module"])
    def test_config_chroma_path_unset_does_not_probe_dependency(
        self, runner: CliRunner, project_dir: Path, monkeypatch: pytest.MonkeyPatch, present: bool
    ) -> None:
        """An unset legacy path is reported independently of a controlled module state."""
        import builtins
        import types

        attempts = []
        if present:
            module = types.ModuleType("chromadb")

            def deny_client(*args, **kwargs):
                pytest.fail("Configuration reporting started a Chroma client")

            monkeypatch.setattr(module, "PersistentClient", deny_client, raising=False)
            monkeypatch.setitem(sys.modules, "chromadb", module)
        else:
            monkeypatch.delitem(sys.modules, "chromadb", raising=False)
        real_import = builtins.__import__

        def observe_import(name, *args, **kwargs):
            if name == "chromadb" or name.startswith("chromadb."):
                attempts.append(name)
                if not present:
                    raise ImportError("controlled missing dependency")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", observe_import)
        result = runner.invoke(main, ["--config", str(project_dir / "groundtruth.toml"), "config"])
        assert result.exit_code == 0, result.output
        assert "Legacy helper chroma_path: unset" in result.output
        assert "runtime fallback" not in result.output
        assert "chromadb not installed" not in result.output
        assert not attempts


# ---------------------------------------------------------------------------
# gt --version
# ---------------------------------------------------------------------------


class TestVersion:
    def test_version(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        from groundtruth_kb import __version__

        assert __version__ in result.output

    def test_python_m_groundtruth_kb_runs(self) -> None:
        """Phase 4B-housekeeping Item 2: ``python -m groundtruth_kb --version``
        must exit 0 and emit the package __version__.

        This test exercises the full module-execution path via a subprocess,
        which is the thing that failed with ``No module named
        groundtruth_kb.__main__`` before the Phase 4B-housekeeping shim was
        added. An in-process CliRunner test cannot catch this regression
        because it imports ``cli.main`` directly and never hits the
        ``python -m`` dispatch.
        """
        import subprocess
        import sys

        from groundtruth_kb import __version__

        result = subprocess.run(
            [sys.executable, "-m", "groundtruth_kb", "--version"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"exit={result.returncode}\nstdout={result.stdout}\nstderr={result.stderr}"
        assert __version__ in result.stdout, f"Expected {__version__!r} in stdout, got: {result.stdout!r}"


# ---------------------------------------------------------------------------
# Regression: --config from outside project directory (Codex P1)
# ---------------------------------------------------------------------------


class TestConfigRelativePaths:
    """Assertion paths resolve against the selected configuration, not caller cwd."""

    pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]

    def test_assert_spec_from_outside_project_dir(
        self, runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, assertion_source
    ) -> None:
        config, record, snapshot, calls = assertion_source
        record(
            "GOV-01",
            {
                "title": "Selected-root effect",
                "status": "active",
                "assertions": [{"type": "grep", "file": "effect.py", "pattern": "value = 1"}],
            },
        )
        other_dir = tmp_path / "elsewhere"
        other_dir.mkdir()
        (other_dir / "effect.py").write_text("value = 2\n", encoding="utf-8")
        monkeypatch.chdir(other_dir)
        before = snapshot()
        result = runner.invoke(main, ["--config", str(config), "assert", "--spec", "GOV-01", "--json"])
        assert result.exit_code == 0, result.output
        assert json.loads(result.output)["aggregate_result"] == "PASS"
        assert (other_dir / "effect.py").read_text(encoding="utf-8") == "value = 2\n"
        assert snapshot() == before and all(method == "GET" for method, _ in calls)
