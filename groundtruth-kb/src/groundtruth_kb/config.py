"""
GroundTruth KB — Configuration.

Resolution order: constructor arg > env var (GT_*) > groundtruth.toml > defaults.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import os
import re
import tomllib  # stdlib since Python 3.11 (project requires >=3.11)
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

_DEFAULT_BRAND_COLOR = "#2563eb"
_DEFAULT_APP_TITLE = "GroundTruth KB"
_DEFAULT_BRAND_MARK = "GT"


class GTConfigError(Exception):
    """Raised when a GroundTruth KB config file cannot be read or parsed.

    Wraps the following error surfaces with a message that identifies the
    offending file:

    * :class:`tomllib.TOMLDecodeError` — invalid TOML syntax.
    * :class:`PermissionError` — unreadable file (ownership or ACL).

    The original exception is chained via ``__cause__`` so debuggers see
    the underlying location. :class:`FileNotFoundError` is still raised
    directly (not wrapped) by :meth:`GTConfig.load` when an explicit
    ``config_path`` does not exist, because that is Python's idiomatic
    exception for a missing file.
    """


@dataclass
class BackupConfig:
    """Database snapshot configuration."""

    snapshot_output_dir: Path | None = None
    snapshot_staging_dir: Path | None = None
    retain_recent: int = 7
    retain_daily_days: int = 30
    include_chroma: bool = False
    sync_paths: tuple[Path, ...] = ()


@dataclass(frozen=True)
class PostgreSQLConfig:
    """Secret-free PostgreSQL client settings.

    Host, database, user, TLS, and password settings belong to host-managed
    libpq service and password files.  GT-KB stores only the service name and
    bounded client timeouts.
    """

    service: str = "gtkb"
    connect_timeout_seconds: int = 10
    lock_timeout_ms: int = 5000
    statement_timeout_ms: int = 30000


@dataclass
class GTConfig:
    """Configuration for a GroundTruth KB project."""

    db_path: Path = field(default_factory=lambda: Path("./groundtruth.db"))
    project_root: Path = field(default_factory=lambda: Path("."))
    chroma_path: Path | None = None
    app_title: str = _DEFAULT_APP_TITLE
    brand_mark: str = _DEFAULT_BRAND_MARK
    brand_color: str = _DEFAULT_BRAND_COLOR
    logo_url: str | None = None
    legal_footer: str = ""
    governance_gates: list[str] = field(default_factory=list)
    gate_config: dict[str, dict[str, Any]] = field(default_factory=dict)
    backup: BackupConfig = field(default_factory=BackupConfig)
    postgresql: PostgreSQLConfig = field(default_factory=PostgreSQLConfig)
    authority_url: str | None = None

    @classmethod
    def load(cls, config_path: Path | None = None, *, discover: bool = True, **overrides: object) -> GTConfig:
        """Load config from groundtruth.toml + env vars + overrides.

        Args:
            config_path: Explicit path to groundtruth.toml. If None, searches
                         current directory and parent directories.
            discover: Search the caller's directories when no file is selected.
                      Disable for operations on an explicitly selected project.
            **overrides: Keyword arguments that override all other sources.

        Relative paths (db_path, project_root) are resolved against the
        directory containing groundtruth.toml, not the caller's cwd. This
        ensures ``gt --config /path/to/project/groundtruth.toml summary``
        works correctly from any working directory.
        """
        resolved_config_path = config_path if config_path is not None else (_find_config() if discover else None)
        file_values = _load_toml(resolved_config_path)
        env_values = _load_env()

        # Determine the anchor directory for relative paths
        if resolved_config_path is not None and resolved_config_path.exists():
            anchor = resolved_config_path.resolve().parent
        else:
            anchor = Path.cwd().resolve()

        explicit_values = {k: v for k, v in overrides.items() if v is not None}

        # Merge ordinary settings at the top level. PostgreSQL settings merge
        # per field so one environment override cannot erase TOML values for
        # the other timeouts.
        file_postgresql = file_values.pop("postgresql", {})
        env_postgresql = env_values.pop("postgresql", {})
        explicit_postgresql = explicit_values.pop("postgresql", {})
        merged = {**file_values, **env_values, **explicit_values}
        merged["postgresql"] = _coerce_postgresql_config(
            file_postgresql,
            env_postgresql,
            explicit_postgresql,
        )

        # Convert path strings to Path objects, anchored to config file directory
        for key in ("db_path", "project_root", "chroma_path"):
            if key in merged and isinstance(merged[key], str):
                p = Path(merged[key])
                if not p.is_absolute():
                    p = anchor / p
                merged[key] = p

        if "backup" in merged:
            merged["backup"] = _coerce_backup_config(merged["backup"], anchor=anchor)

        # Convert governance_gates string to list if needed
        if "governance_gates" in merged and isinstance(merged["governance_gates"], str):
            merged["governance_gates"] = [g.strip() for g in merged["governance_gates"].split(",") if g.strip()]

        # Phase 4B.2, Finding 6: warn on unknown keys so typos in
        # [groundtruth] (e.g. 'bran_color') are surfaced rather than silently
        # dropped. Keys from [gates] and [search] sections map to known fields
        # (governance_gates, gate_config, chroma_path) and never appear here.
        # stacklevel=2 points at the caller's GTConfig.load() invocation.
        known_fields = set(cls.__dataclass_fields__.keys())
        unknown_keys = sorted(k for k in merged if k not in known_fields)
        if unknown_keys:
            warnings.warn(
                f"groundtruth config has unknown keys that will be ignored: "
                f"{unknown_keys}. Check for typos in your groundtruth.toml.",
                UserWarning,
                stacklevel=2,
            )

        config = cls(**{k: v for k, v in merged.items() if k in cls.__dataclass_fields__})
        if config.authority_url is not None:
            config.authority_url = validate_authority_url(config.authority_url)
        # A selected configuration anchors its defaults as well as explicit paths.
        # Otherwise an omitted project_root or db_path silently targets the caller's cwd.
        for key in ("project_root", "db_path", "chroma_path"):
            value = getattr(config, key)
            if (resolved_config_path is not None or key in merged) and value is not None and not value.is_absolute():
                setattr(config, key, anchor / value)
        return config


def _load_toml(config_path: Path | None) -> dict[str, Any]:
    """Read the selected file; GTConfig.load alone owns configuration discovery.

    Raises:
        FileNotFoundError: When ``config_path`` is explicitly supplied but
            the file does not exist. No selected file (``config_path is None``)
            returns ``{}`` without searching the caller's directories.
        GTConfigError: When the file exists but contains invalid TOML. The
            original :class:`tomllib.TOMLDecodeError` is chained via
            ``__cause__``.
    """
    # Phase 4B.1, Finding 2: distinguish auto-discovery (silent defaults)
    # from an explicit caller-supplied path (hard error). Programmatic
    # callers get a FileNotFoundError with a recovery hint instead of
    # silently falling back to defaults.
    if config_path is None:
        return {}
    elif not config_path.exists():
        raise FileNotFoundError(
            f"GroundTruth config file not found: {config_path}. Check the --config path or create the file."
        )
    elif not config_path.is_file():
        raise GTConfigError(f"GroundTruth config path is not a regular file: {config_path}")

    # Phase 4B.1, Finding 3: wrap TOML decode errors so the user sees the
    # offending file name instead of a raw parser traceback.
    # Phase 4B.2, Finding 4: also wrap PermissionError — must be caught
    # before TOMLDecodeError because open() raises it before any TOML parsing.
    try:
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
    except PermissionError as exc:
        raise GTConfigError(
            f"Cannot read config file {config_path}: permission denied. Check file ownership and permissions."
        ) from exc
    except tomllib.TOMLDecodeError as exc:
        raise GTConfigError(f"Invalid TOML in {config_path}: {exc}. Check your groundtruth.toml syntax.") from exc
    except OSError as exc:
        raise GTConfigError(f"Cannot read config file {config_path}: {exc}") from exc

    # Phase 4B.2, Finding 5: warn when [groundtruth] section is absent so
    # typos like [groundtuh] are caught early. stacklevel=3 surfaces the
    # warning at the external GTConfig.load() call site (user code), not
    # inside this helper or in GTConfig.load itself.
    # Wording clarifies that only core [groundtruth] settings use defaults;
    # [gates] and [search] sections, if present, remain active.
    if "groundtruth" not in data:
        warnings.warn(
            f"{config_path}: no [groundtruth] section found. "
            f"Core GroundTruth settings will use env vars and defaults; "
            f"[gates] and [search] sections, if present, are still applied. "
            f"Check your section name if this is unexpected.",
            UserWarning,
            stacklevel=3,
        )

    def table_section(name: str) -> dict[str, object]:
        value = data.get(name, {})
        if not isinstance(value, dict):
            raise GTConfigError(f"[{name}] must be a TOML table")
        return value

    section = table_section("groundtruth")
    result = dict(section)

    # Gates section is separate
    gates_section = table_section("gates")
    if "plugins" in gates_section:
        result["governance_gates"] = gates_section["plugins"]

    # Gate-specific config: [gates.config.GateClassName]
    gate_config_section = gates_section.get("config", {})
    if not isinstance(gate_config_section, dict):
        raise GTConfigError("[gates.config] must be a TOML table")
    if gate_config_section:
        result["gate_config"] = dict(gate_config_section)

    # Search section: [search]
    search_section = table_section("search")
    if "chroma_path" in search_section:
        result["chroma_path"] = search_section["chroma_path"]

    backup_section = table_section("backup")
    if backup_section:
        result["backup"] = dict(backup_section)

    if "postgresql" in data:
        postgresql_section = table_section("postgresql")
        result["postgresql"] = dict(postgresql_section)

    return result


def _coerce_backup_config(value: object, *, anchor: Path) -> BackupConfig:
    """Convert raw TOML/Python backup config values into ``BackupConfig``."""
    if isinstance(value, BackupConfig):
        return value
    if not isinstance(value, dict):
        raise TypeError("backup config must be a mapping or BackupConfig")

    raw = dict(value)
    for key in ("snapshot_output_dir", "snapshot_staging_dir"):
        if key in raw and raw[key] is not None:
            raw[key] = _anchor_path(raw[key], anchor=anchor)

    if "sync_paths" in raw and raw["sync_paths"] is not None:
        raw["sync_paths"] = tuple(_anchor_path(path, anchor=anchor) for path in raw["sync_paths"])

    return BackupConfig(**{k: v for k, v in raw.items() if k in BackupConfig.__dataclass_fields__})


_POSTGRESQL_FIELDS = frozenset(PostgreSQLConfig.__dataclass_fields__)
_POSTGRESQL_TIMEOUT_FIELDS = (
    "connect_timeout_seconds",
    "lock_timeout_ms",
    "statement_timeout_ms",
)
_POSTGRESQL_TIMEOUT_MAX = 2_147_483_647
_POSTGRESQL_SERVICE_RE = re.compile(r"[A-Za-z0-9_.-]+\Z")


def _postgresql_mapping(value: object, *, source: str) -> dict[str, object]:
    if value is None:
        return {}
    if isinstance(value, PostgreSQLConfig):
        return {
            "service": value.service,
            "connect_timeout_seconds": value.connect_timeout_seconds,
            "lock_timeout_ms": value.lock_timeout_ms,
            "statement_timeout_ms": value.statement_timeout_ms,
        }
    if not isinstance(value, dict):
        raise GTConfigError(f"{source} PostgreSQL configuration must be a mapping")
    unknown = sorted(str(key) for key in value if key not in _POSTGRESQL_FIELDS)
    if unknown:
        raise GTConfigError(f"{source} PostgreSQL configuration contains forbidden or unknown keys: {unknown}")
    return dict(value)


def _coerce_postgresql_config(*layers: object) -> PostgreSQLConfig:
    merged: dict[str, object] = {}
    labels = ("TOML", "environment", "override")
    for label, layer in zip(labels, layers, strict=True):
        merged.update(_postgresql_mapping(layer, source=label))

    service = merged.get("service", "gtkb")
    if not isinstance(service, str) or not service or not _POSTGRESQL_SERVICE_RE.fullmatch(service):
        raise GTConfigError(
            "PostgreSQL service must be a non-empty libpq service name containing only "
            "letters, digits, '.', '_', or '-'"
        )

    values: dict[str, int] = {}
    defaults = PostgreSQLConfig()
    for field_name in _POSTGRESQL_TIMEOUT_FIELDS:
        raw = merged.get(field_name, getattr(defaults, field_name))
        if isinstance(raw, bool):
            raise GTConfigError(f"PostgreSQL {field_name} must be a positive integer")
        if isinstance(raw, str):
            if not raw.isascii() or not raw.isdecimal():
                raise GTConfigError(f"PostgreSQL {field_name} must be a positive integer")
            significant = raw.lstrip("0") or "0"
            if len(significant) > 10:
                raise GTConfigError(
                    f"PostgreSQL {field_name} must be a positive integer no greater than {_POSTGRESQL_TIMEOUT_MAX}"
                )
            try:
                raw = int(significant, 10)
            except ValueError as exc:
                raise GTConfigError(f"PostgreSQL {field_name} must be a positive integer") from exc
        if not isinstance(raw, int) or raw <= 0 or raw > _POSTGRESQL_TIMEOUT_MAX:
            raise GTConfigError(
                f"PostgreSQL {field_name} must be a positive integer no greater than {_POSTGRESQL_TIMEOUT_MAX}"
            )
        values[field_name] = raw

    return PostgreSQLConfig(service=service, **values)


def _anchor_path(value: object, *, anchor: Path) -> Path:
    if isinstance(value, Path):
        path = value
    elif isinstance(value, str):
        path = Path(value)
    else:
        path = Path(str(value))
    if not path.is_absolute():
        path = anchor / path
    return path


def _find_config() -> Path | None:
    """Search current and parent directories for groundtruth.toml."""
    current = Path.cwd().resolve()
    for _ in range(10):  # limit depth
        candidate = current / "groundtruth.toml"
        if candidate.is_file():
            return candidate
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def _load_env() -> dict[str, Any]:
    """Load configuration from GT_* environment variables."""
    mapping = {
        "GT_DB_PATH": "db_path",
        "GT_PROJECT_ROOT": "project_root",
        "GT_APP_TITLE": "app_title",
        "GT_BRAND_MARK": "brand_mark",
        "GT_BRAND_COLOR": "brand_color",
        "GT_LOGO_URL": "logo_url",
        "GT_LEGAL_FOOTER": "legal_footer",
        "GT_GOVERNANCE_GATES": "governance_gates",
        "GT_AUTHORITY_URL": "authority_url",
    }
    result: dict[str, Any] = {}
    for env_key, config_key in mapping.items():
        val = os.environ.get(env_key)
        if val is not None:
            result[config_key] = val

    postgresql_mapping = {
        "GT_POSTGRES_SERVICE": "service",
        "GT_POSTGRES_CONNECT_TIMEOUT_SECONDS": "connect_timeout_seconds",
        "GT_POSTGRES_LOCK_TIMEOUT_MS": "lock_timeout_ms",
        "GT_POSTGRES_STATEMENT_TIMEOUT_MS": "statement_timeout_ms",
    }
    unknown_postgresql = sorted(
        key for key in os.environ if key.startswith("GT_POSTGRES_") and key not in postgresql_mapping
    )
    if unknown_postgresql:
        raise GTConfigError(f"Unknown PostgreSQL environment settings: {unknown_postgresql}")
    postgresql = {
        config_key: os.environ[env_key] for env_key, config_key in postgresql_mapping.items() if env_key in os.environ
    }
    if postgresql:
        result["postgresql"] = postgresql
    return result


def validate_authority_url(value: str) -> str:
    """Permit only the installed loopback transport, with no embedded secrets."""
    try:
        parsed = urlsplit(value)
        valid = (
            parsed.scheme == "http"
            and parsed.hostname == "127.0.0.1"
            and parsed.port is not None
            and 1 <= parsed.port <= 65535
            and parsed.username is None
            and parsed.password is None
            and parsed.path in {"", "/"}
            and not parsed.query
            and not parsed.fragment
        )
    except (TypeError, ValueError, AttributeError):
        valid = False
    if not valid:
        raise GTConfigError("authority_url must be an HTTP loopback URL with an explicit port and no credentials")
    return f"http://127.0.0.1:{parsed.port}"
