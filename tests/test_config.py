"""Tests for GTConfig loading and resolution."""

from __future__ import annotations

from pathlib import Path

from groundtruth_kb.config import GTConfig


def test_defaults():
    """Config with no sources uses sensible defaults."""
    cfg = GTConfig()
    assert cfg.db_path == Path("./groundtruth.db")
    assert cfg.project_root == Path(".")
    assert cfg.app_title == "GroundTruth KB"
    assert cfg.brand_mark == "GT"
    assert cfg.brand_color == "#2563eb"
    assert cfg.logo_url is None
    assert cfg.legal_footer == ""
    assert cfg.governance_gates == []


def test_load_from_toml(tmp_path):
    """Config loads values from groundtruth.toml, resolving relative paths against config dir."""
    toml_file = tmp_path / "groundtruth.toml"
    toml_file.write_text(
        '[groundtruth]\n'
        'db_path = "my_project.db"\n'
        'app_title = "My Project KB"\n'
        'brand_mark = "MP"\n'
        'brand_color = "#ff0000"\n'
        '\n'
        '[gates]\n'
        'plugins = ["my_module:MyGate"]\n'
    )
    cfg = GTConfig.load(config_path=toml_file)
    # Relative db_path resolved against the TOML file's directory
    assert cfg.db_path == tmp_path / "my_project.db"
    assert cfg.app_title == "My Project KB"
    assert cfg.brand_mark == "MP"
    assert cfg.brand_color == "#ff0000"
    assert cfg.governance_gates == ["my_module:MyGate"]


def test_env_overrides_toml(tmp_path, monkeypatch):
    """Environment variables override TOML values."""
    toml_file = tmp_path / "groundtruth.toml"
    toml_file.write_text(
        '[groundtruth]\n'
        'app_title = "From TOML"\n'
    )
    monkeypatch.setenv("GT_APP_TITLE", "From Env")
    cfg = GTConfig.load(config_path=toml_file)
    assert cfg.app_title == "From Env"


def test_constructor_overrides_all(tmp_path, monkeypatch):
    """Constructor kwargs override both TOML and env."""
    toml_file = tmp_path / "groundtruth.toml"
    toml_file.write_text(
        '[groundtruth]\n'
        'app_title = "From TOML"\n'
    )
    monkeypatch.setenv("GT_APP_TITLE", "From Env")
    cfg = GTConfig.load(config_path=toml_file, app_title="From Constructor")
    assert cfg.app_title == "From Constructor"


def test_missing_toml_uses_defaults():
    """Config with nonexistent TOML file uses defaults."""
    cfg = GTConfig.load(config_path=Path("/nonexistent/groundtruth.toml"))
    assert cfg.app_title == "GroundTruth KB"


def test_env_governance_gates_string(monkeypatch):
    """GT_GOVERNANCE_GATES as comma-separated string is parsed to list."""
    monkeypatch.setenv("GT_GOVERNANCE_GATES", "mod1:Gate1, mod2:Gate2")
    cfg = GTConfig.load(config_path=Path("/nonexistent"))
    assert cfg.governance_gates == ["mod1:Gate1", "mod2:Gate2"]


def test_db_path_string_converted_to_path():
    """String db_path from TOML is converted to Path."""
    cfg = GTConfig.load(config_path=Path("/nonexistent"), db_path="./test.db")
    assert isinstance(cfg.db_path, Path)


def test_relative_paths_anchored_to_config_dir(tmp_path):
    """Relative db_path and project_root resolve against config file directory, not cwd."""
    project_dir = tmp_path / "my-project"
    project_dir.mkdir()
    toml_file = project_dir / "groundtruth.toml"
    toml_file.write_text(
        '[groundtruth]\n'
        'db_path = "./groundtruth.db"\n'
        'project_root = "."\n',
    )
    cfg = GTConfig.load(config_path=toml_file)
    # Paths must resolve to the config file's directory, not cwd
    assert cfg.db_path.resolve() == (project_dir / "groundtruth.db").resolve()
    assert cfg.project_root.resolve() == project_dir.resolve()


def test_absolute_paths_not_reanchored(tmp_path):
    """Absolute paths in TOML are used as-is, not re-anchored."""
    abs_db = tmp_path / "custom" / "my.db"
    toml_file = tmp_path / "groundtruth.toml"
    toml_file.write_text(
        f'[groundtruth]\n'
        f'db_path = "{abs_db.as_posix()}"\n',
    )
    cfg = GTConfig.load(config_path=toml_file)
    assert cfg.db_path == abs_db
