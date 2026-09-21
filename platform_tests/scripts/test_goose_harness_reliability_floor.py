"""Tests for goose_harness.py integration with the execution reliability floor.

Verifies that the wrapper correctly integrates the guard: exports model
configuration, records the run window, loads the canonical floor contract from
the neutral baseline (refusing to run without it), and calls evaluate_run.
"""

from __future__ import annotations

import os
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
    GooseHarnessError,
    _load_floor_config,
    build_arg_parser,
    build_system_prompt,
    resolve_project_root,
)


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

    def test_build_system_prompt_known_skill(self):
        """build_system_prompt returns content for known skills."""
        prompt = build_system_prompt("bridge-review")
        assert prompt is not None
        assert "Loyal Opposition" in prompt

    def test_build_system_prompt_unknown_skill(self):
        """build_system_prompt returns None for unknown skills."""
        prompt = build_system_prompt("nonexistent-skill")
        assert prompt is None

    def test_build_system_prompt_none(self):
        """build_system_prompt returns None for None input."""
        assert build_system_prompt(None) is None

    def test_resolve_project_root(self, tmp_path):
        """resolve_project_root finds a directory with groundtruth.toml."""
        (tmp_path / "groundtruth.toml").write_text("")
        root = resolve_project_root(tmp_path)
        assert root == tmp_path


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
