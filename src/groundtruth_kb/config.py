"""
GroundTruth KB — Configuration.

Resolution order: constructor arg > env var (GT_*) > groundtruth.toml > defaults.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import os
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import tomllib  # stdlib since Python 3.11 (project requires >=3.11)


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

    @classmethod
    def load(cls, config_path: Path | None = None, **overrides: object) -> GTConfig:
        """Load config from groundtruth.toml + env vars + overrides.

        Args:
            config_path: Explicit path to groundtruth.toml. If None, searches
                         current directory and parent directories.
            **overrides: Keyword arguments that override all other sources.

        Relative paths (db_path, project_root) are resolved against the
        directory containing groundtruth.toml, not the caller's cwd. This
        ensures ``gt --config /path/to/project/groundtruth.toml summary``
        works correctly from any working directory.
        """
        resolved_config_path = config_path if config_path is not None else _find_config()
        file_values = _load_toml(resolved_config_path)
        env_values = _load_env()

        # Determine the anchor directory for relative paths
        if resolved_config_path is not None and resolved_config_path.exists():
            anchor = resolved_config_path.resolve().parent
        else:
            anchor = Path.cwd().resolve()

        # Merge: file < env < overrides
        merged = {**file_values, **env_values, **{k: v for k, v in overrides.items() if v is not None}}

        # Convert path strings to Path objects, anchored to config file directory
        for key in ("db_path", "project_root", "chroma_path"):
            if key in merged and isinstance(merged[key], str):
                p = Path(merged[key])
                if not p.is_absolute():
                    p = anchor / p
                merged[key] = p

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

        return cls(**{k: v for k, v in merged.items() if k in cls.__dataclass_fields__})


def _load_toml(config_path: Path | None) -> dict[str, Any]:
    """Load values from groundtruth.toml.

    Raises:
        FileNotFoundError: When ``config_path`` is explicitly supplied but
            the file does not exist. Auto-discovery (``config_path is None``)
            still returns ``{}`` when no config is found, per the historical
            "exploration mode" contract.
        GTConfigError: When the file exists but contains invalid TOML. The
            original :class:`tomllib.TOMLDecodeError` is chained via
            ``__cause__``.
    """
    # Phase 4B.1, Finding 2: distinguish auto-discovery (silent defaults)
    # from an explicit caller-supplied path (hard error). Programmatic
    # callers get a FileNotFoundError with a recovery hint instead of
    # silently falling back to defaults.
    if config_path is None:
        discovered = _find_config()
        if discovered is None:
            return {}
        config_path = discovered
    elif not config_path.exists():
        raise FileNotFoundError(
            f"GroundTruth config file not found: {config_path}. Check the --config path or create the file."
        )

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

    section = data.get("groundtruth", {})
    result = dict(section)

    # Gates section is separate
    gates_section = data.get("gates", {})
    if "plugins" in gates_section:
        result["governance_gates"] = gates_section["plugins"]

    # Gate-specific config: [gates.config.GateClassName]
    gate_config_section = gates_section.get("config", {})
    if gate_config_section:
        result["gate_config"] = dict(gate_config_section)

    # Search section: [search]
    search_section = data.get("search", {})
    if "chroma_path" in search_section:
        result["chroma_path"] = search_section["chroma_path"]

    return result


def _find_config() -> Path | None:
    """Search current and parent directories for groundtruth.toml."""
    current = Path.cwd().resolve()
    for _ in range(10):  # limit depth
        candidate = current / "groundtruth.toml"
        if candidate.exists():
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
    }
    result = {}
    for env_key, config_key in mapping.items():
        val = os.environ.get(env_key)
        if val is not None:
            result[config_key] = val
    return result
