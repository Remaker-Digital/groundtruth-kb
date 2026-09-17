"""Profile-config resolution for the projected terminology guidance (retained from the legacy doctor suite)."""

from __future__ import annotations

from pathlib import Path

from groundtruth_kb.project.doctor import _resolve_profile_config


def test_resolve_profile_config_extends_inheritance() -> None:
    """Config resolver merges extended parent profile into child overrides (read from the neutral baseline)."""
    import tomllib

    baseline = Path(__file__).resolve().parents[2] / ".harness-baseline-configuration/rules/canonical-terminology.toml"
    with open(baseline, "rb") as f:
        config = tomllib.load(f)

    effective = _resolve_profile_config(config, "dual-agent-webapp")
    assert effective is not None
    assert effective.get("missing_severity") == "ERROR"
    assert "required_startup_terms" not in effective and "required_primer_terms" not in effective
