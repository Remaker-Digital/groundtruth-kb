"""Tests for GTConfig loading and resolution.

Phase 4B.1 (2026-04-14) introduced two new defensive behaviors in
``GTConfig.load()``:

1. **Explicit missing config_path raises FileNotFoundError.** Previously,
   passing a non-existent path as ``config_path`` silently returned
   defaults. That hid typo errors from programmatic callers. The CLI
   layer was already guarded by ``click.Path(exists=True)``, so only
   library callers are affected by the behavior change.

2. **Invalid TOML raises GTConfigError.** Previously, an invalid TOML
   file propagated a raw :class:`tomllib.TOMLDecodeError` with no
   context. The new wrapper attaches the file path to the message and
   chains the original exception.

The "no config anywhere" path (auto-discovery with
``config_path=None``) is unchanged: it still falls back to defaults.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

import groundtruth_kb
from groundtruth_kb.config import GTConfig, GTConfigError


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
        "[groundtruth]\n"
        'db_path = "my_project.db"\n'
        'app_title = "My Project KB"\n'
        'brand_mark = "MP"\n'
        'brand_color = "#ff0000"\n'
        "\n"
        "[gates]\n"
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
    toml_file.write_text('[groundtruth]\napp_title = "From TOML"\n')
    monkeypatch.setenv("GT_APP_TITLE", "From Env")
    cfg = GTConfig.load(config_path=toml_file)
    assert cfg.app_title == "From Env"


def test_constructor_overrides_all(tmp_path, monkeypatch):
    """Constructor kwargs override both TOML and env."""
    toml_file = tmp_path / "groundtruth.toml"
    toml_file.write_text('[groundtruth]\napp_title = "From TOML"\n')
    monkeypatch.setenv("GT_APP_TITLE", "From Env")
    cfg = GTConfig.load(config_path=toml_file, app_title="From Constructor")
    assert cfg.app_title == "From Constructor"


def test_auto_discovery_no_match_uses_defaults(tmp_path, monkeypatch):
    """When no explicit path is provided and auto-discovery finds nothing,
    GTConfig returns defaults. Phase 4B.1 preserves this contract for the
    auto-discovery path even though explicit missing paths now raise."""
    # Create an isolated deep directory tree so _find_config's 10-level parent
    # walk has no chance of encountering an unrelated groundtruth.toml.
    deep = tmp_path / "a" / "b" / "c" / "d" / "e"
    deep.mkdir(parents=True)
    monkeypatch.chdir(deep)
    cfg = GTConfig.load()  # no config_path → auto-discovery
    assert cfg.app_title == "GroundTruth KB"
    assert cfg.db_path == Path("./groundtruth.db")


def test_env_governance_gates_string(tmp_path, monkeypatch):
    """GT_GOVERNANCE_GATES as comma-separated string is parsed to list.

    Phase 4B.1: previously this test passed ``Path("/nonexistent")`` as a
    dummy config_path. Now it creates a real empty TOML file so the test
    doesn't trip over the new explicit-missing-path guard.
    Phase 4B.2: file now includes a [groundtruth] header to avoid the
    missing-section UserWarning (the section's content is irrelevant to
    what this test exercises).
    """
    toml_file = tmp_path / "groundtruth.toml"
    toml_file.write_text("[groundtruth]\n")  # empty section; env var overrides everything
    monkeypatch.setenv("GT_GOVERNANCE_GATES", "mod1:Gate1, mod2:Gate2")
    cfg = GTConfig.load(config_path=toml_file)
    assert cfg.governance_gates == ["mod1:Gate1", "mod2:Gate2"]


def test_db_path_string_converted_to_path(tmp_path):
    """String db_path from constructor override is converted to Path.

    Phase 4B.1: previously this test passed ``Path("/nonexistent")``. Now
    it creates a real empty TOML file (constructor override wins anyway).
    Phase 4B.2: file now includes a [groundtruth] header to avoid the
    missing-section UserWarning (the file's content is irrelevant here).
    """
    toml_file = tmp_path / "groundtruth.toml"
    toml_file.write_text("[groundtruth]\n")  # empty section; override takes precedence
    cfg = GTConfig.load(config_path=toml_file, db_path="./test.db")
    assert isinstance(cfg.db_path, Path)


def test_relative_paths_anchored_to_config_dir(tmp_path):
    """Relative db_path and project_root resolve against config file directory, not cwd."""
    project_dir = tmp_path / "my-project"
    project_dir.mkdir()
    toml_file = project_dir / "groundtruth.toml"
    toml_file.write_text(
        '[groundtruth]\ndb_path = "./groundtruth.db"\nproject_root = "."\n',
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
        f'[groundtruth]\ndb_path = "{abs_db.as_posix()}"\n',
    )
    cfg = GTConfig.load(config_path=toml_file)
    assert cfg.db_path == abs_db


# ---------------------------------------------------------------------------
# Phase 4B.1: Finding 2 — explicit missing config_path raises FileNotFoundError
# ---------------------------------------------------------------------------


def test_explicit_config_path_nonexistent_raises(tmp_path):
    """When the caller supplies an explicit config_path that doesn't exist,
    GTConfig.load raises FileNotFoundError (Phase 4B.1, Finding 2)."""
    missing = tmp_path / "does-not-exist.toml"
    with pytest.raises(FileNotFoundError) as exc_info:
        GTConfig.load(config_path=missing)
    assert str(missing) in str(exc_info.value)


def test_explicit_config_path_nonexistent_message_contains_hint(tmp_path):
    """The FileNotFoundError message contains a recovery hint so that
    programmatic callers get actionable guidance."""
    missing = tmp_path / "does-not-exist.toml"
    with pytest.raises(FileNotFoundError) as exc_info:
        GTConfig.load(config_path=missing)
    message = str(exc_info.value)
    # Recovery hint: message should mention --config flag or "Check"
    assert "--config" in message or "Check" in message


# ---------------------------------------------------------------------------
# Phase 4B.1: Finding 3 — invalid TOML raises GTConfigError (wrapping TOMLDecodeError)
# ---------------------------------------------------------------------------


def test_invalid_toml_raises_gtconfigerror(tmp_path):
    """Invalid TOML syntax triggers a typed GTConfigError (Phase 4B.1, Finding 3)."""
    toml_file = tmp_path / "groundtruth.toml"
    toml_file.write_text("invalid toml = [\n")  # unterminated array = parse error
    with pytest.raises(GTConfigError):
        GTConfig.load(config_path=toml_file)


def test_invalid_toml_error_chains_original(tmp_path):
    """GTConfigError.__cause__ is the original TOMLDecodeError so the full
    traceback remains available for debuggers."""
    toml_file = tmp_path / "groundtruth.toml"
    toml_file.write_text("invalid toml = [\n")
    with pytest.raises(GTConfigError) as exc_info:
        GTConfig.load(config_path=toml_file)
    assert exc_info.value.__cause__ is not None
    assert isinstance(exc_info.value.__cause__, tomllib.TOMLDecodeError)


def test_invalid_toml_message_contains_path(tmp_path):
    """The GTConfigError message contains the offending file path so the
    user knows which file has the syntax error."""
    toml_file = tmp_path / "groundtruth.toml"
    toml_file.write_text("still = not valid = toml\n")  # TOML doesn't allow reassignment
    with pytest.raises(GTConfigError) as exc_info:
        GTConfig.load(config_path=toml_file)
    assert str(toml_file) in str(exc_info.value)


# ---------------------------------------------------------------------------
# Phase 4B.1: Public API surface — GTConfigError is exported
# ---------------------------------------------------------------------------


def test_gtconfigerror_is_public_api():
    """GTConfigError is exposed via groundtruth_kb.__all__ and is the same
    object as groundtruth_kb.config.GTConfigError (single-source of truth).
    """
    import groundtruth_kb.config as config_mod

    assert "GTConfigError" in groundtruth_kb.__all__
    assert groundtruth_kb.GTConfigError is config_mod.GTConfigError
    # And the count grew from 15 → 16
    assert len(groundtruth_kb.__all__) == 16


# ---------------------------------------------------------------------------
# Phase 4B.2: Finding 4 — PermissionError on open() is wrapped in GTConfigError
# ---------------------------------------------------------------------------


def test_permission_denied_raises_gtconfigerror(tmp_path, monkeypatch):
    """PermissionError from open() is wrapped in GTConfigError with the
    file path and a permissions hint in the message (Phase 4B.2, Finding 4).

    Uses monkeypatch on builtins.open to avoid platform-specific ACL
    manipulation — the mock raises PermissionError only for the target
    config file, leaving other open() calls intact.
    """
    toml_file = tmp_path / "groundtruth.toml"
    toml_file.write_text("[groundtruth]\napp_title = 'test'\n")

    original_open = open

    def mock_open(path, *args, **kwargs):
        if str(path) == str(toml_file):
            raise PermissionError(13, "Permission denied", str(toml_file))
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr("builtins.open", mock_open)
    with pytest.raises(GTConfigError) as exc_info:
        GTConfig.load(config_path=toml_file)
    assert str(toml_file) in str(exc_info.value)
    assert "permission" in str(exc_info.value).lower()


def test_permission_denied_error_chains_original(tmp_path, monkeypatch):
    """GTConfigError.__cause__ is the original PermissionError so debuggers
    can trace the underlying OS failure (Phase 4B.2, Finding 4)."""
    toml_file = tmp_path / "groundtruth.toml"
    toml_file.write_text("[groundtruth]\napp_title = 'test'\n")

    original_open = open
    original_perm_error = PermissionError(13, "Permission denied", str(toml_file))

    def mock_open(path, *args, **kwargs):
        if str(path) == str(toml_file):
            raise original_perm_error
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr("builtins.open", mock_open)
    with pytest.raises(GTConfigError) as exc_info:
        GTConfig.load(config_path=toml_file)
    assert exc_info.value.__cause__ is not None
    assert isinstance(exc_info.value.__cause__, PermissionError)


# ---------------------------------------------------------------------------
# Phase 4B.2: Finding 5 — missing [groundtruth] section emits UserWarning
# ---------------------------------------------------------------------------


def test_missing_groundtruth_section_warns(tmp_path):
    """A TOML file with no [groundtruth] section triggers a UserWarning
    mentioning the section name (Phase 4B.2, Finding 5).

    Defaults still apply — the warning is advisory, not fatal. The wording
    must not imply that [gates] or [search] sections are ignored.
    """
    toml_file = tmp_path / "groundtruth.toml"
    # Realistic typo: [groundtuh] instead of [groundtruth]
    toml_file.write_text("[groundtuh]\napp_title = 'typo-section'\n")
    with pytest.warns(UserWarning, match=r"\[groundtruth\]"):
        cfg = GTConfig.load(config_path=toml_file)
    # Core defaults still apply — the file's content under the wrong section
    # name is not routed anywhere.
    assert cfg.app_title == "GroundTruth KB"


# ---------------------------------------------------------------------------
# Phase 4B.2: Finding 6 — unknown keys in [groundtruth] section emit UserWarning
# ---------------------------------------------------------------------------


def test_unknown_toml_key_warns(tmp_path):
    """A TOML [groundtruth] section with unknown keys triggers a UserWarning
    that names the offending keys (Phase 4B.2, Finding 6).

    Known keys are still applied. The warning only fires for keys that are
    not dataclass fields (e.g. typos like 'bran_color' for 'brand_color').
    """
    toml_file = tmp_path / "groundtruth.toml"
    # Typo: 'bran_color' instead of 'brand_color'
    toml_file.write_text("[groundtruth]\nbran_color = '#ff0000'\napp_title = 'Test'\n")
    with pytest.warns(UserWarning, match="bran_color"):
        cfg = GTConfig.load(config_path=toml_file)
    # Known key was applied correctly
    assert cfg.app_title == "Test"
    # Unknown key had no effect — brand_color remains the default
    assert cfg.brand_color == "#2563eb"
