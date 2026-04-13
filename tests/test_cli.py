"""Tests for groundtruth_kb.cli module."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from groundtruth_kb.cli import main
from groundtruth_kb.db import KnowledgeDB

# ---------------------------------------------------------------------------
# gt init
# ---------------------------------------------------------------------------


class TestInit:
    def test_init_creates_project(self, runner: CliRunner, tmp_path: Path) -> None:
        target = tmp_path / "new-project"
        result = runner.invoke(main, ["init", "new-project", "--dir", str(target)])
        assert result.exit_code == 0
        assert (target / "groundtruth.toml").exists()
        assert (target / "groundtruth.db").exists()
        assert "Initialized" in result.output

    def test_init_default_dir(self, runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(main, ["init", "my-app"])
        assert result.exit_code == 0
        assert (tmp_path / "my-app" / "groundtruth.toml").exists()

    def test_init_already_exists(self, runner: CliRunner, tmp_path: Path) -> None:
        target = tmp_path / "existing"
        target.mkdir()
        (target / "groundtruth.toml").write_text("exists", encoding="utf-8")
        result = runner.invoke(main, ["init", "existing", "--dir", str(target)])
        assert result.exit_code == 1
        assert "already exists" in result.output


# ---------------------------------------------------------------------------
# gt seed
# ---------------------------------------------------------------------------


class TestSeed:
    def test_seed_governance(self, runner: CliRunner, project_dir: Path) -> None:
        result = runner.invoke(main, ["--config", str(project_dir / "groundtruth.toml"), "seed"])
        assert result.exit_code == 0
        assert "5 governance specs" in result.output

    def test_seed_with_examples(self, runner: CliRunner, project_dir: Path) -> None:
        result = runner.invoke(main, ["--config", str(project_dir / "groundtruth.toml"), "seed", "--example"])
        assert result.exit_code == 0
        assert "governance specs" in result.output
        assert "example specs" in result.output

    def test_seed_idempotent(self, runner: CliRunner, project_dir: Path) -> None:
        config_flag = ["--config", str(project_dir / "groundtruth.toml")]
        runner.invoke(main, [*config_flag, "seed", "--example"])
        result = runner.invoke(main, [*config_flag, "seed", "--example"])
        assert result.exit_code == 0
        assert "0 governance specs" in result.output
        assert "0 example specs" in result.output


# ---------------------------------------------------------------------------
# gt summary
# ---------------------------------------------------------------------------


class TestSummary:
    def test_summary_empty_db(self, runner: CliRunner, project_dir: Path) -> None:
        result = runner.invoke(main, ["--config", str(project_dir / "groundtruth.toml"), "summary"])
        assert result.exit_code == 0
        assert "0 total" in result.output

    def test_summary_with_data(self, runner: CliRunner, project_dir: Path) -> None:
        config_flag = ["--config", str(project_dir / "groundtruth.toml")]
        runner.invoke(main, [*config_flag, "seed", "--example"])
        result = runner.invoke(main, [*config_flag, "summary"])
        assert result.exit_code == 0
        assert "8 total" in result.output  # 5 GOV + 3 example


# ---------------------------------------------------------------------------
# gt history
# ---------------------------------------------------------------------------


class TestHistory:
    def test_history_empty(self, runner: CliRunner, project_dir: Path) -> None:
        result = runner.invoke(main, ["--config", str(project_dir / "groundtruth.toml"), "history"])
        assert result.exit_code == 0
        assert "No changes" in result.output

    def test_history_with_data(self, runner: CliRunner, project_dir: Path) -> None:
        config_flag = ["--config", str(project_dir / "groundtruth.toml")]
        runner.invoke(main, [*config_flag, "seed"])
        result = runner.invoke(main, [*config_flag, "history", "--limit", "3"])
        assert result.exit_code == 0
        assert "GOV-" in result.output


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


class TestExportImport:
    def test_export_creates_file(self, runner: CliRunner, project_dir: Path) -> None:
        config_flag = ["--config", str(project_dir / "groundtruth.toml")]
        runner.invoke(main, [*config_flag, "seed"])
        output_path = project_dir / "export.json"
        result = runner.invoke(main, [*config_flag, "export", "--output", str(output_path)])
        assert result.exit_code == 0
        assert output_path.exists()
        data = json.loads(output_path.read_text(encoding="utf-8"))
        assert "tables" in data
        assert len(data["tables"]["specifications"]) >= 5

    def test_import_from_export(self, runner: CliRunner, project_dir: Path, tmp_path: Path) -> None:
        config_flag = ["--config", str(project_dir / "groundtruth.toml")]
        runner.invoke(main, [*config_flag, "seed"])
        export_path = project_dir / "export.json"
        runner.invoke(main, [*config_flag, "export", "--output", str(export_path)])

        # Create a fresh DB and import
        fresh_dir = tmp_path / "fresh"
        fresh_dir.mkdir()
        fresh_toml = fresh_dir / "groundtruth.toml"
        fresh_toml.write_text(
            f'[groundtruth]\ndb_path = "{(fresh_dir / "groundtruth.db").as_posix()}"\n',
            encoding="utf-8",
        )
        # Create the empty DB first
        db = KnowledgeDB(db_path=fresh_dir / "groundtruth.db")
        db.close()

        result = runner.invoke(main, ["--config", str(fresh_toml), "import", str(export_path)])
        assert result.exit_code == 0
        assert "Imported" in result.output

    def test_import_merge_mode(self, runner: CliRunner, project_dir: Path) -> None:
        config_flag = ["--config", str(project_dir / "groundtruth.toml")]
        runner.invoke(main, [*config_flag, "seed"])
        export_path = project_dir / "export.json"
        runner.invoke(main, [*config_flag, "export", "--output", str(export_path)])
        # Import into same DB with merge — should skip duplicates
        result = runner.invoke(main, [*config_flag, "import", str(export_path), "--merge"])
        assert result.exit_code == 0


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
        """When chroma_path is unset and chromadb is importable, show runtime fallback."""
        result = runner.invoke(main, ["--config", str(project_dir / "groundtruth.toml"), "config"])
        assert result.exit_code == 0
        # chromadb is installed in the test environment
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


class TestServe:
    def test_serve_imports_create_app(
        self,
        runner: CliRunner,
        project_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Verify gt serve wires up create_app and uvicorn (without blocking)."""
        captured: dict = {}

        def fake_run(app, *, host, port, log_level):
            captured["host"] = host
            captured["port"] = port

        monkeypatch.setattr("uvicorn.run", fake_run)
        result = runner.invoke(main, ["--config", str(project_dir / "groundtruth.toml"), "serve"])
        assert result.exit_code == 0
        assert captured["host"] == "127.0.0.1"
        assert captured["port"] == 8090

    def test_serve_custom_port(self, runner: CliRunner, project_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        captured: dict = {}

        def fake_run(app, *, host, port, log_level):
            captured["port"] = port

        monkeypatch.setattr("uvicorn.run", fake_run)
        result = runner.invoke(main, ["--config", str(project_dir / "groundtruth.toml"), "serve", "--port", "9999"])
        assert result.exit_code == 0
        assert captured["port"] == 9999


# ---------------------------------------------------------------------------
# gt --version
# ---------------------------------------------------------------------------


class TestVersion:
    def test_version(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        from groundtruth_kb import __version__

        assert __version__ in result.output


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
        assert "bridge/INDEX.md" in bridge_prompt
        assert "PRIME_BRIDGE_DB" not in gitignore_text

        db = KnowledgeDB(db_path=target / "groundtruth.db")
        try:
            summary = db.get_summary()
            assert summary["spec_total"] == 8
            assert summary["test_artifact_count"] >= 3
        finally:
            db.close()

    def test_project_init_dual_agent_uses_file_bridge_defaults(self, runner: CliRunner, tmp_path: Path) -> None:
        target = tmp_path / "dual-agent-project"
        result = runner.invoke(
            main,
            [
                "project",
                "init",
                "dual-agent-project",
                "--profile",
                "dual-agent",
                "--dir",
                str(target),
                "--owner",
                "Acme Labs",
                "--no-include-ci",
            ],
        )
        assert result.exit_code == 0
        assert (target / "BRIDGE-INVENTORY.md").exists()
        assert (target / "bridge-os-poller-setup-prompt.md").exists()

        bridge_text = (target / "BRIDGE-INVENTORY.md").read_text(encoding="utf-8")
        gitignore_text = (target / ".gitignore").read_text(encoding="utf-8")
        assert "bridge/INDEX.md" in bridge_text
        assert "gt bridge serve" not in bridge_text
        assert "groundtruth_kb.bridge.worker" not in bridge_text
        assert "bridge.db" not in gitignore_text
        assert "bridge-automation/logs" in gitignore_text

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

    def test_summary_from_outside_project_dir(
        self, runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """gt --config <project>/groundtruth.toml summary must work from any cwd."""
        project = tmp_path / "my-project"
        self._init_and_seed(runner, project)

        # Change to a completely different directory
        other_dir = tmp_path / "other"
        other_dir.mkdir()
        monkeypatch.chdir(other_dir)

        result = runner.invoke(main, ["--config", str(project / "groundtruth.toml"), "summary"])
        assert result.exit_code == 0
        assert "8 total" in result.output  # 5 GOV + 3 example

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

    def test_history_from_outside_project_dir(
        self, runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """gt --config <project>/groundtruth.toml history must show seeded data."""
        project = tmp_path / "my-project"
        self._init_and_seed(runner, project)

        other_dir = tmp_path / "away"
        other_dir.mkdir()
        monkeypatch.chdir(other_dir)

        result = runner.invoke(main, ["--config", str(project / "groundtruth.toml"), "history"])
        assert result.exit_code == 0
        assert "GOV-" in result.output


# ---------------------------------------------------------------------------
# Regression: import validation (Codex P2)
# ---------------------------------------------------------------------------


class TestImportValidation:
    """Verify that gt import rejects malformed input instead of silently succeeding."""

    def test_import_unknown_table_warns(self, runner: CliRunner, project_dir: Path) -> None:
        """Import with an unknown table name should warn and skip it."""
        bad_json = project_dir / "bad.json"
        bad_json.write_text(
            json.dumps({"tables": {"nonexistent_table": [{"col": "val"}]}}),
            encoding="utf-8",
        )
        result = runner.invoke(
            main,
            [
                "--config",
                str(project_dir / "groundtruth.toml"),
                "import",
                str(bad_json),
                "--merge",
            ],
        )
        assert result.exit_code == 0
        assert "Skipped unknown tables" in result.output or "Imported 0" in result.output

    def test_import_unknown_columns_rejects_without_merge(self, runner: CliRunner, project_dir: Path) -> None:
        """Import with unknown columns should fail loudly without --merge."""
        bad_json = project_dir / "bad_cols.json"
        bad_json.write_text(
            json.dumps({"tables": {"specifications": [{"bogus_column": "val"}]}}),
            encoding="utf-8",
        )
        result = runner.invoke(
            main,
            [
                "--config",
                str(project_dir / "groundtruth.toml"),
                "import",
                str(bad_json),
            ],
        )
        assert result.exit_code != 0
        assert "Unknown columns" in result.output

    def test_import_unknown_columns_skips_in_merge(self, runner: CliRunner, project_dir: Path) -> None:
        """Import with unknown columns in merge mode should skip and warn."""
        bad_json = project_dir / "bad_cols_merge.json"
        bad_json.write_text(
            json.dumps({"tables": {"specifications": [{"bogus_column": "val"}]}}),
            encoding="utf-8",
        )
        result = runner.invoke(
            main,
            [
                "--config",
                str(project_dir / "groundtruth.toml"),
                "import",
                str(bad_json),
                "--merge",
            ],
        )
        assert result.exit_code == 0
        assert "WARNING" in result.output or "rejected" in result.output


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
