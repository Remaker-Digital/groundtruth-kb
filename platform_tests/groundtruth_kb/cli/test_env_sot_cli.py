"""Platform CLI coverage for ``gt env`` Agent Red env SoT commands.

Authority: bridge/gtkb-wi3430-3431-env-sot-migration-cli-slice-002.md.
Source work items: WI-3430 and WI-3431.
"""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner
from groundtruth_kb.cli import main

SECRET_VALUE = "platform-secret-value"


def _write_config(root: Path) -> Path:
    config = root / "groundtruth.toml"
    config.write_text(
        f'[groundtruth]\ndb_path = "{(root / "groundtruth.db").as_posix()}"\nproject_root = "{root.as_posix()}"\n',
        encoding="utf-8",
    )
    return config


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_env_plan_json_reports_counts_without_secret_values(tmp_path: Path) -> None:
    config = _write_config(tmp_path)
    _write(tmp_path / ".env.local", f"GTKB_MODE=platform\nAGENT_RED_TOKEN={SECRET_VALUE}\n")

    result = CliRunner().invoke(main, ["--config", str(config), "env", "plan", "--app", "agent-red", "--json"])

    assert result.exit_code == 0
    assert SECRET_VALUE not in result.output
    payload = json.loads(result.output)
    assert payload["root"]["platform_key_count"] == 1
    assert payload["root"]["app_key_count"] == 1


def test_env_check_exits_nonzero_for_independent_admin_sot(tmp_path: Path) -> None:
    config = _write_config(tmp_path)
    _write(tmp_path / "applications" / "Agent_Red" / ".env.local", f"AGENT_RED_TOKEN={SECRET_VALUE}\n")
    _write(tmp_path / "applications" / "Agent_Red" / "admin" / "provider" / ".env.local", "PROVIDER_MODE=local\n")

    result = CliRunner().invoke(main, ["--config", str(config), "env", "check", "--app", "agent-red", "--json"])

    assert result.exit_code == 1
    assert SECRET_VALUE not in result.output
    payload = json.loads(result.output)
    assert payload["summary"]["independent_admin_sot_count"] == 1


def test_env_migrate_dry_run_does_not_mutate_or_render_values(tmp_path: Path) -> None:
    config = _write_config(tmp_path)
    root_env = tmp_path / ".env.local"
    _write(root_env, f"AGENT_RED_TOKEN={SECRET_VALUE}\n")

    result = CliRunner().invoke(main, ["--config", str(config), "env", "migrate", "--app", "agent-red", "--dry-run"])

    assert result.exit_code == 0
    assert SECRET_VALUE not in result.output
    assert root_env.read_text(encoding="utf-8") == f"AGENT_RED_TOKEN={SECRET_VALUE}\n"


def test_env_migrate_apply_moves_values_without_printing_them(tmp_path: Path) -> None:
    config = _write_config(tmp_path)
    _write(tmp_path / ".env.local", f"GTKB_MODE=platform\nAGENT_RED_TOKEN={SECRET_VALUE}\n")

    result = CliRunner().invoke(
        main,
        ["--config", str(config), "env", "migrate", "--app", "agent-red", "--apply", "--json"],
    )

    assert result.exit_code == 0
    assert SECRET_VALUE not in result.output
    payload = json.loads(result.output)
    assert payload["applied"] is True
    assert payload["moved_key_count"] == 1
    assert "AGENT_RED_TOKEN" not in (tmp_path / ".env.local").read_text(encoding="utf-8")
    assert SECRET_VALUE in (tmp_path / "applications" / "Agent_Red" / ".env.local").read_text(encoding="utf-8")
