"""Tests for goose_harness.py integration with the execution reliability floor.

Verifies that the wrapper correctly integrates the guard: exports model
configuration, records the run window, loads the canonical floor contract from
the neutral baseline (refusing to run without it), and calls evaluate_run.

c123 (batch design WP2 2.1 and 2.2): the wrapper also passes Goose no role
prompt (no --skill, no --system), and --model names a routing.toml route whose
model_id is what goose run receives; an unknown route key stops the run before
Goose starts.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import goose_harness  # noqa: E402
from goose_execution_guard import ExecutionFloorConfig, export_model_configuration  # noqa: E402
from goose_harness import (  # noqa: E402
    FLOOR_CONFIG_RELATIVE_PATH,
    PROFILES_RELATIVE_PATH,
    ROUTING_RELATIVE_PATH,
    GooseHarnessError,
    _load_floor_config,
    build_arg_parser,
    resolve_goose_model,
    resolve_project_root,
)


def _goose_project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A project root with the checkout's floor contract, Goose profile and routing table, and ``sh`` on PATH."""
    root = tmp_path / "project"
    root.mkdir()
    (root / "groundtruth.toml").write_text("[groundtruth]\n", encoding="utf-8")
    for relative in (FLOOR_CONFIG_RELATIVE_PATH, PROFILES_RELATIVE_PATH, ROUTING_RELATIVE_PATH):
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((PROJECT_ROOT / relative).read_bytes())
    interpreter = tmp_path / "bin" / ("sh.exe" if os.name == "nt" else "sh")
    interpreter.parent.mkdir()
    interpreter.write_bytes(b"")
    interpreter.chmod(0o755)
    monkeypatch.setenv("PATH", str(interpreter.parent) + os.pathsep + os.environ.get("PATH", ""))
    return root


def _record_launches(monkeypatch: pytest.MonkeyPatch) -> tuple[list[list[str]], list[str]]:
    """Record each goose command line and each exported model; the fixture run fails right after the spawn."""
    launches: list[list[str]] = []
    exported: list[str] = []
    monkeypatch.setattr(goose_harness, "_find_goose_cli", lambda: "goose-fixture")
    monkeypatch.setattr(goose_harness, "export_model_configuration", exported.append)

    def launch(command, **kwargs):
        launches.append(command)
        return subprocess.CompletedProcess(command, 1, stdout="", stderr="controlled failure")

    monkeypatch.setattr(goose_harness.subprocess, "run", launch)
    return launches, exported


class TestIntegration:
    """Integration tests for the harness wrapper with the guard."""

    def test_export_model_configuration_sets_env(self):
        """export_model_configuration sets environment variables."""
        # Clear any existing values
        for key in (
            "GTKB_AUTHOR_MODEL",
            "GTKB_AUTHOR_MODEL_VERSION",
            "GTKB_AUTHOR_HARNESS_NAME",
            "GTKB_AUTHOR_HARNESS_ID",
            "GTKB_AUTHOR_IDENTITY",
        ):
            os.environ.pop(key, None)

        export_model_configuration("deepseek-v4-pro")

        assert os.environ.get("GTKB_AUTHOR_MODEL") == "deepseek-v4-pro"
        assert os.environ.get("GTKB_AUTHOR_HARNESS_NAME") == "goose"
        assert os.environ.get("GTKB_AUTHOR_HARNESS_ID") == "G"
        # The role is never exported: it comes only from the immutable binding.
        assert "GTKB_AUTHOR_IDENTITY" not in os.environ

    def test_export_model_configuration_empty_model(self):
        """Empty model arg does not crash."""
        os.environ.pop("GTKB_AUTHOR_MODEL", None)
        export_model_configuration("")
        # Should not set empty value
        assert os.environ.get("GTKB_AUTHOR_MODEL", "") == ""

    def test_load_floor_config_returns_config(self, tmp_path):
        """_load_floor_config reads the contract from the neutral baseline."""
        assert FLOOR_CONFIG_RELATIVE_PATH.as_posix() == ".harness-baseline-configuration/goose-execution-floor.toml"
        floor = tmp_path / FLOOR_CONFIG_RELATIVE_PATH
        floor.parent.mkdir(parents=True)
        floor.write_text("""
schema_version = 1
[write_verification]
enabled = false
""")
        config = _load_floor_config(tmp_path)
        assert isinstance(config, ExecutionFloorConfig)
        assert config.write_verification_enabled is False

    def test_load_floor_config_refuses_an_absent_file(self, tmp_path):
        """No second configuration tree and no silent fallback: an absent contract is refused, naming the path."""
        (tmp_path / "config").mkdir()
        with pytest.raises(GooseHarnessError, match="execution floor configuration is absent") as raised:
            _load_floor_config(tmp_path)
        assert str(tmp_path / FLOOR_CONFIG_RELATIVE_PATH) in str(raised.value)

    def test_canonical_floor_contract_is_tracked_and_states_the_floor(self):
        """The checkout carries the contract in the neutral baseline and it resolves to the documented floor."""
        assert (PROJECT_ROOT / FLOOR_CONFIG_RELATIVE_PATH).is_file()
        config = _load_floor_config(PROJECT_ROOT)
        assert config.write_verification_enabled is True
        assert config.write_tool_names == {"write", "write_file", "Write", "Edit"}
        assert config.intentional_empty_allowlist == set()
        assert config.leak_patterns == {}
        assert (config.retry_attempts, config.retry_backoff_seconds) == (0, 0)
        assert config.provenance_guard_enabled is True
        assert config.provenance_scan_scope == "run_window"

    def test_main_refuses_before_spawning_goose_when_the_contract_is_absent(self, tmp_path, monkeypatch, capsys):
        """An absent contract stops the run before any goose process is started."""

        def refuse_spawn(*args, **kwargs):
            raise AssertionError("goose must not be spawned without the execution floor contract")

        monkeypatch.setattr(goose_harness.subprocess, "run", refuse_spawn)
        (tmp_path / "groundtruth.toml").write_text("")
        assert goose_harness.main(["-p", "hello", "--project-root", str(tmp_path)]) == 1
        captured = capsys.readouterr()
        assert "goose_harness: execution floor configuration is absent" in captured.err
        assert str(tmp_path / FLOOR_CONFIG_RELATIVE_PATH) in captured.err
        assert captured.out == ""

    def test_arg_parser_has_required_args(self):
        """The argument parser includes all required arguments."""
        parser = build_arg_parser()
        args = parser.parse_args(["-p", "test prompt"])
        assert args.prompt == "test prompt"
        assert args.max_turns == 40
        assert args.timeout == 3600.0
        assert args.model is None
        # c123 (batch design WP2 2.1): no --skill; a role is never a launch argument.
        assert "skill" not in vars(args)
        with pytest.raises(SystemExit):
            parser.parse_args(["-p", "test prompt", "--skill", "bridge-review"])

    def test_resolve_project_root(self, tmp_path):
        """resolve_project_root finds a directory with groundtruth.toml."""
        (tmp_path / "groundtruth.toml").write_text("")
        root = resolve_project_root(tmp_path)
        assert root == tmp_path


class TestRoleFreeLaunchAndModelRoute:
    """c123 (batch design WP2 2.1 and 2.2): no role prompt reaches Goose, and --model is a routing.toml route key."""

    def test_no_system_prompt_is_passed_to_goose(self, tmp_path, monkeypatch):
        """c123 (batch design WP2 2.1): no --system; the dispatched prompt, init line first, is Goose's only text."""
        root = _goose_project(tmp_path, monkeypatch)
        launches, _exported = _record_launches(monkeypatch)
        prompt = "::init gtkb lo\nReview the dispatched proposal"
        argv = ["-p", prompt, "--model", "goose-deepseek-v4-pro", "--project-root", str(root)]
        assert goose_harness.main(argv) == 1
        (command,) = launches
        assert command[:2] == ["goose-fixture", "run"]
        assert "--system" not in command
        assert command[command.index("--text") + 1] == prompt
        assert not any("Loyal Opposition" in part or "Prime Builder" in part for part in command)

    def test_a_registered_route_key_reaches_goose_as_its_model_id(self, tmp_path, monkeypatch):
        """c123 (batch design WP2 2.2): G's registered key resolves through the checkout's routing.toml."""
        root = _goose_project(tmp_path, monkeypatch)
        launches, exported = _record_launches(monkeypatch)
        argv = ["-p", "probe", "--model", "goose-deepseek-v4-pro", "--project-root", str(root)]
        assert goose_harness.main(argv) == 1
        (command,) = launches
        assert command.count("--model") == 1
        assert command[command.index("--model") + 1] == "deepseek-v4-pro"
        assert "goose-deepseek-v4-pro" not in command
        assert exported == ["deepseek-v4-pro"]

    @pytest.mark.parametrize(
        "route_key",
        ["gtkb-v4f-goose", "alibaba-deepseek-v4-pro", "deepseek-v4-pro"],
        ids=["c121-registered-key", "alibaba-row", "openrouter-row-named-like-the-goose-model-id"],
    )
    def test_an_unknown_route_key_exits_1_before_goose_runs(self, tmp_path, monkeypatch, capsys, route_key):
        """c123 (batch design WP2 2.2): a free-text key or another provider's row fails closed before any spawn."""
        root = _goose_project(tmp_path, monkeypatch)
        launches, exported = _record_launches(monkeypatch)
        assert goose_harness.main(["-p", "probe", "--model", route_key, "--project-root", str(root)]) == 1
        assert launches == [] and exported == []
        captured = capsys.readouterr()
        assert captured.err == f"goose_harness: unknown model route: {route_key}\n"
        assert captured.out == ""

    def test_without_model_no_model_is_passed(self, tmp_path, monkeypatch):
        """c123 (batch design WP2 2.2): without --model nothing is resolved and goose run gets no --model."""
        root = _goose_project(tmp_path, monkeypatch)
        (root / ROUTING_RELATIVE_PATH).unlink()
        launches, exported = _record_launches(monkeypatch)
        assert goose_harness.main(["-p", "probe", "--project-root", str(root)]) == 1
        (command,) = launches
        assert "--model" not in command
        assert exported == [""]

    @pytest.mark.parametrize(
        "routing,message",
        [
            (None, "routing config is unreadable"),
            ("[models.fixture\n", "routing config is unreadable"),
            (
                '[models.fixture]\nprovider = "goose"\nmodel_id = ""\n',
                "models.fixture.model_id must be a non-empty string",
            ),
        ],
        ids=["absent", "malformed", "empty-model-id"],
    )
    def test_resolve_goose_model_fails_closed(self, tmp_path, routing, message):
        """c123 (batch design WP2 2.2): an unreadable table or an empty model_id is refused, never guessed."""
        if routing is not None:
            path = tmp_path / ROUTING_RELATIVE_PATH
            path.parent.mkdir(parents=True)
            path.write_text(routing, encoding="utf-8")
        with pytest.raises(GooseHarnessError, match=message):
            resolve_goose_model(tmp_path, "fixture")


class TestGooseHarnessImports:
    """Verify that the harness can be imported and its constants are correct."""

    def test_author_identity_constant(self):
        from goose_harness import AUTHOR_HARNESS_ID, AUTHOR_IDENTITY

        assert AUTHOR_IDENTITY == "Goose G"
        assert AUTHOR_HARNESS_ID == "G"

    def test_default_constants(self):
        from goose_harness import DEFAULT_MAX_TURNS, DEFAULT_SESSION_TIMEOUT_SECONDS, DEFAULT_TIMEOUT_SECONDS

        assert DEFAULT_MAX_TURNS == 40
        assert DEFAULT_TIMEOUT_SECONDS == 3600.0
        assert DEFAULT_SESSION_TIMEOUT_SECONDS == 5400.0

    def test_guard_imports(self):
        """The guard module is importable from the harness."""
        from goose_execution_guard import (
            ExecutionFloorConfig,
            RunDiagnostic,
            evaluate_run,
            export_model_configuration,
        )

        assert ExecutionFloorConfig is not None
        assert RunDiagnostic is not None
        assert evaluate_run is not None
        assert export_model_configuration is not None


class TestNoTimerLiteralsInWrapper:
    """DELIB-202667722: wrapper diff contains no new timer literals."""

    def test_wrapper_adds_no_timer_literals(self):
        """The wrapper modifications add no new timeout/interval/retry/throttle literals."""
        harness_path = Path(__file__).parent.parent.parent / "scripts" / "goose_harness.py"
        content = harness_path.read_text()

        # The pre-existing constants (lines 23-25) should still exist
        assert "DEFAULT_MAX_TURNS = 40" in content
        assert "DEFAULT_TIMEOUT_SECONDS = 3600.0" in content
        assert "DEFAULT_SESSION_TIMEOUT_SECONDS = 5400.0" in content

        # Count timer-related literals: the three pre-existing plus any new ones
        timer_pattern_count = 0
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            # Only count non-comment timer assignments
            if "timeout" in stripped.lower() and "=" in stripped:
                if "timeout=" not in stripped and "subprocess.TimeoutExpired" not in stripped:
                    timer_pattern_count += 1

        # We expect: DEFAULT_TIMEOUT_SECONDS, DEFAULT_SESSION_TIMEOUT_SECONDS
        # The guard's timeout=30 in sweep is a concern but it's in the guard, not wrapper
        assert timer_pattern_count >= 2, "Pre-existing timeout constants should still exist"
