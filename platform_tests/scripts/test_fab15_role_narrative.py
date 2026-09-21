"""FAB-15 regression coverage for role narrative/spec reconciliation."""

from __future__ import annotations

import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_codex_interactive_config_uses_split_posture() -> None:
    """FAB-15: project config is interactive-safe; headless carve-out is documented."""
    text = (REPO_ROOT / ".codex" / "config.toml").read_text(encoding="utf-8")
    data = tomllib.loads(text)

    assert data["approval_policy"] == "on-request"
    assert data["sandbox_workspace_write"]["network_access"] is False
    # The config is projected from the profile; deliberation-archive provenance comments are retired.
    assert "PROJECTION, NOT CANONICAL" in text
