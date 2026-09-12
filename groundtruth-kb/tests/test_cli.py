"""Tests for groundtruth_kb.cli module."""

from __future__ import annotations

import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

from groundtruth_kb.cli import main
from groundtruth_kb.db import KnowledgeDB


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
# gt summary
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# gt history
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# gt assert
# ---------------------------------------------------------------------------


class TestAssert:
    def test_assert_no_specs(self, runner: CliRunner, project_dir: Path) -> None:
        result = runner.invoke(main, ["--config", str(project_dir / "groundtruth.toml"), "assert"])
        assert result.exit_code == 0

    def test_assert_with_passing_spec(self, runner: CliRunner, project_dir: Path) -> None:
        config_flag = ["--config", str(project_dir / "groundtruth.toml")]
        runner.invoke(main, [*config_flag, "seed"])
        result = runner.invoke(main, [*config_flag, "assert"])
        assert result.exit_code == 0
        assert "PASSED" in result.output

    def test_assert_single_spec(self, runner: CliRunner, project_dir: Path) -> None:
        config_flag = ["--config", str(project_dir / "groundtruth.toml")]
        runner.invoke(main, [*config_flag, "seed"])
        result = runner.invoke(main, [*config_flag, "assert", "--spec", "GOV-01"])
        assert result.exit_code == 0


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

    def test_config_chroma_path_unset_chromadb_installed(self, runner: CliRunner, project_dir: Path) -> None:
        """When chroma_path is unset and chromadb is importable, show runtime fallback.

        Requires the `search` extra (chromadb). Skipped in the base no-search
        install state — the base state's behavior is covered by
        `test_config_chroma_path_unset_no_chromadb` below.
        """
        pytest.importorskip("chromadb")
        result = runner.invoke(main, ["--config", str(project_dir / "groundtruth.toml"), "config"])
        assert result.exit_code == 0
        assert "unset" in result.output
        assert "runtime fallback" in result.output

    def test_config_chroma_path_unset_no_chromadb(
        self,
        runner: CliRunner,
        project_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """When chroma_path is unset and chromadb is absent, show not-installed."""
        import builtins

        real_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "chromadb":
                raise ImportError("mocked")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", mock_import)
        result = runner.invoke(main, ["--config", str(project_dir / "groundtruth.toml"), "config"])
        assert result.exit_code == 0
        assert "chromadb not installed" in result.output


# ---------------------------------------------------------------------------
# gt serve
# ---------------------------------------------------------------------------


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
# gt bootstrap-desktop
# ---------------------------------------------------------------------------


class TestBootstrapDesktop:
    def test_bootstrap_desktop_creates_scaffold(self, runner: CliRunner, tmp_path: Path) -> None:
        target = tmp_path / "client-prototype"
        result = runner.invoke(
            main,
            [
                "bootstrap-desktop",
                "client-prototype",
                "--dir",
                str(target),
                "--owner",
                "Acme Labs",
            ],
        )
        assert result.exit_code == 0
        assert (target / "groundtruth.toml").exists()
        assert (target / "groundtruth.db").exists()
        assert (target / "CLAUDE.md").exists()
        assert (target / "MEMORY.md").exists()
        assert (target / "BRIDGE-INVENTORY.md").exists()
        assert (target / "bridge-os-poller-setup-prompt.md").exists()
        assert (target / ".claude" / "hooks" / "assertion-check.py").exists()
        assert (target / ".claude" / "rules" / "prime-builder.md").exists()
        assert (target / ".github" / "workflows" / "test.yml").exists()

        claude_text = (target / "CLAUDE.md").read_text(encoding="utf-8")
        bridge_text = (target / "BRIDGE-INVENTORY.md").read_text(encoding="utf-8")
        bridge_prompt = (target / "bridge-os-poller-setup-prompt.md").read_text(encoding="utf-8")
        gitignore_text = (target / ".gitignore").read_text(encoding="utf-8")
        assert "{{PROJECT_NAME}}" not in claude_text
        assert "client-prototype" in claude_text
        assert "Acme Labs" in claude_text
        assert "{{AGENT_OR_PROCESS_1}}" not in bridge_text
        assert "bridge/INDEX.md" not in bridge_prompt
        assert "PRIME_BRIDGE_DB" not in gitignore_text

        db = KnowledgeDB(db_path=target / "groundtruth.db")
        try:
            summary = db.get_summary()
            assert summary["spec_total"] == 8
            assert summary["test_artifact_count"] >= 3
        finally:
            db.close()

    def test_bootstrap_desktop_rejects_non_empty_target(self, runner: CliRunner, tmp_path: Path) -> None:
        target = tmp_path / "occupied"
        target.mkdir()
        (target / "notes.txt").write_text("already here", encoding="utf-8")

        result = runner.invoke(main, ["bootstrap-desktop", "occupied", "--dir", str(target)])
        assert result.exit_code != 0
        assert "not empty" in result.output


# ---------------------------------------------------------------------------
# Regression: --config from outside project directory (Codex P1)
# ---------------------------------------------------------------------------


class TestConfigRelativePaths:
    """Verify that relative paths in groundtruth.toml resolve against the
    config file's directory, NOT the caller's cwd."""

    def _init_and_seed(self, runner: CliRunner, project_path: Path) -> None:
        """Create and seed a project at the given path."""
        result = runner.invoke(main, ["init", "proj", "--dir", str(project_path)])
        assert result.exit_code == 0
        toml = str(project_path / "groundtruth.toml")
        result = runner.invoke(main, ["--config", toml, "seed", "--example"])
        assert result.exit_code == 0

    def test_assert_spec_from_outside_project_dir(
        self, runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """gt --config <project>/groundtruth.toml assert --spec GOV-01 must resolve correctly."""
        project = tmp_path / "my-project"
        self._init_and_seed(runner, project)

        other_dir = tmp_path / "elsewhere"
        other_dir.mkdir()
        monkeypatch.chdir(other_dir)

        result = runner.invoke(main, ["--config", str(project / "groundtruth.toml"), "assert", "--spec", "GOV-01"])
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# Regression: import validation (Codex P2)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Regression: CLI gate_config wiring (Codex P1)
# ---------------------------------------------------------------------------


class TestCLIGateConfigWiring:
    """Verify that _open_db() passes gate_config so TOML-configured gates are active."""

    def test_cli_path_wires_transport_gate(self, tmp_path: Path) -> None:
        """A TOML-configured TransportEvidenceGate must block pass on the CLI path."""
        from groundtruth_kb.cli import _open_db
        from groundtruth_kb.config import GTConfig
        from groundtruth_kb.gates_transport import TransportEvidenceGateError

        toml = tmp_path / "groundtruth.toml"
        toml.write_text(
            f"""[groundtruth]
db_path = "{(tmp_path / "test.db").as_posix()}"
project_root = "{tmp_path.as_posix()}"

[gates]
plugins = ["groundtruth_kb.gates_transport:TransportEvidenceGate"]

[gates.config.TransportEvidenceGate]
spec_ids = ["SPEC-1524"]
""",
            encoding="utf-8",
        )
        config = GTConfig.load(config_path=toml)
        db = _open_db(config)

        # Verify gate is wired with config
        gate_names = [g.name() for g in db._gate_registry._gates]
        assert "Transport Evidence Gate" in gate_names

        # Verify spec_ids are populated (not empty frozenset)
        transport_gates = [g for g in db._gate_registry._gates if g.name() == "Transport Evidence Gate"]
        assert len(transport_gates) == 1
        assert "SPEC-1524" in transport_gates[0]._spec_ids

        # Verify enforcement
        db.insert_spec("SPEC-1524", "Transport test", "implemented", "test", "test")
        with pytest.raises(TransportEvidenceGateError, match="test_file is required"):
            db.insert_test(
                "TEST-CLI-001",
                "CLI path test",
                "SPEC-1524",
                "e2e",
                "pass expected",
                "test",
                "regression",
                last_result="pass",
            )
        db.close()

    def test_cli_path_inherits_project_root(self, tmp_path: Path) -> None:
        """Gate must inherit project_root from GTConfig when not set in gate config."""
        from groundtruth_kb.cli import _open_db
        from groundtruth_kb.config import GTConfig

        toml = tmp_path / "groundtruth.toml"
        toml.write_text(
            f"""[groundtruth]
db_path = "{(tmp_path / "test.db").as_posix()}"
project_root = "{tmp_path.as_posix()}"

[gates]
plugins = ["groundtruth_kb.gates_transport:TransportEvidenceGate"]

[gates.config.TransportEvidenceGate]
spec_ids = ["SPEC-1524"]
""",
            encoding="utf-8",
        )
        config = GTConfig.load(config_path=toml)
        db = _open_db(config)

        transport_gates = [g for g in db._gate_registry._gates if g.name() == "Transport Evidence Gate"]
        assert transport_gates[0]._project_root == tmp_path
        db.close()
