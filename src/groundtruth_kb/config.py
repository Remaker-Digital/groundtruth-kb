"""
GroundTruth KB — Configuration.

Resolution order: constructor arg > env var (GT_*) > groundtruth.toml > defaults.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    import tomli as tomllib  # type: ignore[no-redef]


_DEFAULT_BRAND_COLOR = "#2563eb"
_DEFAULT_APP_TITLE = "GroundTruth KB"
_DEFAULT_BRAND_MARK = "GT"


@dataclass
class GTConfig:
    """Configuration for a GroundTruth KB project."""

    db_path: Path = field(default_factory=lambda: Path("./groundtruth.db"))
    project_root: Path = field(default_factory=lambda: Path("."))
    app_title: str = _DEFAULT_APP_TITLE
    brand_mark: str = _DEFAULT_BRAND_MARK
    brand_color: str = _DEFAULT_BRAND_COLOR
    logo_url: str | None = None
    legal_footer: str = ""
    governance_gates: list[str] = field(default_factory=list)
    gate_config: dict[str, dict] = field(default_factory=dict)

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
        for key in ("db_path", "project_root"):
            if key in merged and isinstance(merged[key], str):
                p = Path(merged[key])
                if not p.is_absolute():
                    p = anchor / p
                merged[key] = p

        # Convert governance_gates string to list if needed
        if "governance_gates" in merged and isinstance(merged["governance_gates"], str):
            merged["governance_gates"] = [g.strip() for g in merged["governance_gates"].split(",") if g.strip()]

        return cls(**{k: v for k, v in merged.items() if k in cls.__dataclass_fields__})


def _load_toml(config_path: Path | None) -> dict:
    """Load values from groundtruth.toml."""
    if config_path is None:
        config_path = _find_config()
    if config_path is None or not config_path.exists():
        return {}

    with open(config_path, "rb") as f:
        data = tomllib.load(f)

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


def _load_env() -> dict:
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
