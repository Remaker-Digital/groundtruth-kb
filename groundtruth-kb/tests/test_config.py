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

import dataclasses
import re
import tomllib
from pathlib import Path

import pytest

import groundtruth_kb
from groundtruth_kb.config import GTConfig, GTConfigError, PostgreSQLConfig


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
    assert cfg.backup.retain_recent == 7
    assert cfg.backup.retain_daily_days == 30
    assert cfg.backup.include_chroma is False


@pytest.mark.parametrize("discover", [False, True])
def test_config_anchors_default_paths_to_selected_file(tmp_path, monkeypatch, discover):
    for name in ("GT_PROJECT_ROOT", "GT_DB_PATH", "GT_CHROMA_PATH"):
        monkeypatch.delenv(name, raising=False)
    config = tmp_path / "groundtruth.toml"
    config.write_text('[groundtruth]\napp_title = "Selected project"\n', encoding="utf-8")
    caller = tmp_path / "nested"
    caller.mkdir()
    monkeypatch.chdir(caller)

    cfg = GTConfig.load() if discover else GTConfig.load(config_path=config)

    assert cfg.project_root == tmp_path
    assert cfg.db_path == tmp_path / "groundtruth.db"
    assert not cfg.db_path.exists()


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


def test_loads_backup_section(tmp_path):
    """Config loads optional [backup] values and anchors relative paths."""
    toml_file = tmp_path / "groundtruth.toml"
    toml_file.write_text(
        "[groundtruth]\n"
        'db_path = "groundtruth.db"\n'
        "\n"
        "[backup]\n"
        'snapshot_output_dir = "snapshots"\n'
        'snapshot_staging_dir = "stage"\n'
        "retain_recent = 3\n"
        "retain_daily_days = 14\n"
        "include_chroma = true\n"
        'sync_paths = ["cloud"]\n'
    )

    cfg = GTConfig.load(config_path=toml_file)

    assert cfg.backup.snapshot_output_dir == tmp_path / "snapshots"
    assert cfg.backup.snapshot_staging_dir == tmp_path / "stage"
    assert cfg.backup.retain_recent == 3
    assert cfg.backup.retain_daily_days == 14
    assert cfg.backup.include_chroma is True
    assert cfg.backup.sync_paths == (tmp_path / "cloud",)


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
    # Exceed _find_config's 10-level walk even when pytest's temporary root is
    # inside a repository that contains groundtruth.toml.
    deep = tmp_path.joinpath(*(["x"] * 12))
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
    # 15 -> 16 when GTConfigError was exported; 16 -> 12 when c103 (owner ruling D23, 2026-09-18) removed the
    # KnowledgeDB / get_depth / get_parent_id / spec_sort_key re-exports of the frozen groundtruth_kb.db schema
    assert len(groundtruth_kb.__all__) == 12


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


# --- PostgreSQL client settings (WI-7707) ---------------------------------
#
# ``postgres_kernel.py`` carries exactly one first-party import,
# ``from groundtruth_kb.config import PostgreSQLConfig``. Until that name existed here the entire
# PostgreSQL surface — kernel, target DDL and all three test files — could not be imported,
# collected or run.


def test_postgresql_config_carries_the_kernel_contract():
    """The four attributes the kernel reads exist and are defaulted.

    Enumerated from the kernel rather than assumed: ``service``, ``connect_timeout_seconds``,
    ``lock_timeout_ms`` and ``statement_timeout_ms`` are the only ``self.settings.*`` reads in
    ``postgres_kernel.py``. Defaults matter because they are what makes the type constructible
    without configuration, which is what restores importability.
    """
    settings = PostgreSQLConfig()
    assert settings.service == "gtkb"
    assert settings.connect_timeout_seconds == 10
    assert settings.lock_timeout_ms == 5000
    assert settings.statement_timeout_ms == 30000


def test_postgresql_config_is_frozen_and_holds_no_secrets():
    """Frozen, and carrying no credential-bearing field.

    Host, database, user, TLS and password belong to host-managed libpq service and password files.
    A field named for any of them appearing here would be a credential surface this type is
    specifically designed not to have.
    """
    settings = PostgreSQLConfig()
    with pytest.raises(dataclasses.FrozenInstanceError):
        settings.service = "other"  # type: ignore[misc]

    forbidden = {"host", "password", "passwd", "user", "username", "dbname", "database", "sslmode", "tls"}
    present = {f.name for f in dataclasses.fields(PostgreSQLConfig)}
    assert not (present & forbidden), f"credential-bearing fields must not live here: {sorted(present & forbidden)}"


def test_gtconfig_exposes_a_postgresql_section():
    """``GTConfig`` carries the section, defaulted, without disturbing existing construction."""
    cfg = GTConfig()
    assert isinstance(cfg.postgresql, PostgreSQLConfig)
    assert cfg.postgresql.service == "gtkb"


# --- PostgreSQL configuration, ported from the WI-6252 cohort suite (WI-7739) ------------
# The config port at WI-7742 landed the PostgreSQLConfig dataclass and named the merge-logic
# rework a non-goal. These twelve tests were written against that rework and are ported with it,
# unmodified. The three dataclass-contract tests above are kept: they assert a different property
# and removing reviewed passing tests to match a file is not a port.


def test_postgresql_defaults_are_secret_free():
    """PostgreSQL uses a named libpq service and bounded, non-secret timeouts."""
    cfg = GTConfig()

    assert cfg.postgresql.service == "gtkb"
    assert cfg.postgresql.connect_timeout_seconds == 10
    assert cfg.postgresql.lock_timeout_ms == 5000
    assert cfg.postgresql.statement_timeout_ms == 30000


def test_postgresql_toml_and_environment_merge_per_field(tmp_path, monkeypatch):
    toml_file = tmp_path / "groundtruth.toml"
    toml_file.write_text(
        "[groundtruth]\n[postgresql]\nservice='reviewed'\nlock_timeout_ms=7000\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("GT_POSTGRES_STATEMENT_TIMEOUT_MS", "45000")

    cfg = GTConfig.load(config_path=toml_file)

    assert cfg.postgresql.service == "reviewed"
    assert cfg.postgresql.connect_timeout_seconds == 10
    assert cfg.postgresql.lock_timeout_ms == 7000
    assert cfg.postgresql.statement_timeout_ms == 45000


@pytest.mark.parametrize("key", ["password", "dsn", "url", "host", "database", "user", "sslmode"])
def test_postgresql_toml_rejects_secret_or_connection_keys(tmp_path, key):
    toml_file = tmp_path / "groundtruth.toml"
    toml_file.write_text(f"[groundtruth]\n[postgresql]\n{key}='forbidden'\n", encoding="utf-8")

    with pytest.raises(GTConfigError, match="forbidden or unknown"):
        GTConfig.load(config_path=toml_file)


@pytest.mark.parametrize("value", ["", "postgres://host/db", "name with space", "x=y", "line\\nbreak"])
def test_postgresql_rejects_non_service_values(value):
    with pytest.raises(GTConfigError, match="libpq service name"):
        GTConfig.load(postgresql={"service": value})


@pytest.mark.parametrize("value", [0, -1, 2_147_483_648, True, "1.5", "ten"])
def test_postgresql_rejects_invalid_timeouts(value):
    with pytest.raises(GTConfigError, match="positive integer"):
        GTConfig.load(postgresql={"connect_timeout_seconds": value})


def test_postgresql_environment_values_are_typed(monkeypatch):
    monkeypatch.setenv("GT_POSTGRES_SERVICE", "test-service")
    monkeypatch.setenv("GT_POSTGRES_CONNECT_TIMEOUT_SECONDS", "12")
    monkeypatch.setenv("GT_POSTGRES_LOCK_TIMEOUT_MS", "6000")
    monkeypatch.setenv("GT_POSTGRES_STATEMENT_TIMEOUT_MS", "36000")

    cfg = GTConfig.load()

    assert cfg.postgresql.service == "test-service"
    assert cfg.postgresql.connect_timeout_seconds == 12
    assert cfg.postgresql.lock_timeout_ms == 6000
    assert cfg.postgresql.statement_timeout_ms == 36000


def test_postgresql_timeout_accepts_in_range_decimal_with_leading_zeroes():
    cfg = GTConfig.load(postgresql={"connect_timeout_seconds": "00000000001"})

    assert cfg.postgresql.connect_timeout_seconds == 1


def test_postgresql_unknown_environment_key_fails_closed(monkeypatch):
    monkeypatch.setenv("GT_POSTGRES_PASSWORD", "must-not-be-read")

    with pytest.raises(GTConfigError, match="Unknown PostgreSQL environment settings"):
        GTConfig.load()


def test_postgresql_long_timeout_environment_value_fails_with_typed_error(monkeypatch):
    monkeypatch.setenv("GT_POSTGRES_CONNECT_TIMEOUT_SECONDS", "9" * 5000)

    with pytest.raises(GTConfigError, match="positive integer no greater than"):
        GTConfig.load()


def test_postgresql_non_table_toml_value_fails_closed(tmp_path):
    toml_file = tmp_path / "groundtruth.toml"
    toml_file.write_text('postgresql="not-a-table"\n[groundtruth]\n', encoding="utf-8")

    with pytest.raises(GTConfigError, match="must be a TOML table"):
        GTConfig.load(config_path=toml_file)


@pytest.mark.parametrize(
    "content,section",
    [
        ('groundtruth="not-a-table"\n', "groundtruth"),
        ("gates=1\n[groundtruth]\n", "gates"),
        ("search=[]\n[groundtruth]\n", "search"),
        ('backup="not-a-table"\n[groundtruth]\n', "backup"),
        ("[groundtruth]\n[gates]\nconfig=1\n", "gates.config"),
    ],
)
def test_postgresql_config_rejects_every_consumed_non_table_section(tmp_path, content, section):
    toml_file = tmp_path / "groundtruth.toml"
    toml_file.write_text(content, encoding="utf-8")

    with pytest.raises(GTConfigError, match=rf"\[{re.escape(section)}\] must be a TOML table"):
        GTConfig.load(config_path=toml_file)


def test_postgresql_config_preserves_programmatic_missing_groundtruth_warning(tmp_path):
    toml_file = tmp_path / "groundtruth.toml"
    toml_file.write_text("[groundtuh]\napp_title='typo'\n[postgresql]\nservice='reviewed'\n", encoding="utf-8")

    with pytest.warns(UserWarning, match=r"no \[groundtruth\] section found"):
        cfg = GTConfig.load(config_path=toml_file)

    assert cfg.postgresql.service == "reviewed"


@pytest.mark.parametrize("caller_file", ["valid", "malformed"])
def test_disabled_discovery_never_loads_a_callers_configuration(tmp_path, monkeypatch, caller_file):
    for key in ("GT_AUTHORITY_URL", "GT_PROJECT_ROOT", "GT_DB_PATH", "GT_APP_TITLE", "GT_POSTGRES_SERVICE"):
        monkeypatch.delenv(key, raising=False)
    caller = tmp_path / "caller"
    caller.mkdir()
    config = caller / "groundtruth.toml"
    content = (
        '[groundtruth]\nauthority_url="http://127.0.0.1:1"\n'
        'app_title="Unselected caller"\n[postgresql]\nservice="unselected"\n'
        if caller_file == "valid"
        else "[not valid TOML"
    )
    config.write_text(content, encoding="utf-8")
    nested = caller / "nested"
    nested.mkdir()
    selected = tmp_path / "selected"
    selected.mkdir()
    monkeypatch.chdir(nested)
    before = config.read_bytes()

    result = GTConfig.load(discover=False, project_root=selected)

    assert result.project_root == selected
    assert result.authority_url is None
    assert result.app_title == "GroundTruth KB"
    assert result.postgresql.service == "gtkb"
    assert config.read_bytes() == before and not list(selected.iterdir())


def test_disabled_discovery_retains_explicit_configuration_and_layer_precedence(tmp_path, monkeypatch):
    caller = tmp_path / "caller"
    caller.mkdir()
    (caller / "groundtruth.toml").write_text("[invalid caller TOML", encoding="utf-8")
    selected = tmp_path / "selected"
    selected.mkdir()
    config = selected / "groundtruth.toml"
    config.write_text(
        '[groundtruth]\nauthority_url="http://127.0.0.1:11"\n'
        'app_title="Selected file"\n[postgresql]\nservice="selected"\nlock_timeout_ms=701\n',
        encoding="utf-8",
    )
    monkeypatch.chdir(caller)
    monkeypatch.setenv("GT_AUTHORITY_URL", "http://127.0.0.1:12")
    monkeypatch.setenv("GT_POSTGRES_SERVICE", "environment")
    result = GTConfig.load(config_path=config, discover=False, authority_url="http://127.0.0.1:13")
    assert result.authority_url == "http://127.0.0.1:13"
    assert result.project_root == selected and result.app_title == "Selected file"
    assert result.postgresql.service == "environment" and result.postgresql.lock_timeout_ms == 701
    from_environment = GTConfig.load(discover=False, project_root=selected)
    assert from_environment.authority_url == "http://127.0.0.1:12"
    assert from_environment.postgresql.service == "environment"
    assert from_environment.postgresql.lock_timeout_ms == 5000
