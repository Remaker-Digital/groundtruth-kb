"""Structural absence check for the retired secondary baseline.

This asserts only directory absence in the selected checkout. Complete reader,
writer, registration, migration and recovery qualification remains the broader
WI-6260 / TEST-11922 obligation, including the cases retained by TEST-12124.
A literal reference scan cannot distinguish a dependency from a prohibition,
and historical permission or collision exemptions do not establish completion.
"""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PURGE_DIR = "config/agent-control"


def test_config_agent_control_directory_is_absent() -> None:
    """TEST-12124 clause 1: the obsolete second baseline directory must not exist."""
    purge_path = PROJECT_ROOT / PURGE_DIR
    surviving = (
        sorted(p.relative_to(PROJECT_ROOT).as_posix() for p in purge_path.rglob("*") if p.is_file())
        if purge_path.exists()
        else []
    )

    assert not purge_path.exists(), (
        f"{PURGE_DIR} still exists with {len(surviving)} file(s). "
        "GOV-SOT-SINGLETON-001 permits exactly one baseline; "
        ".harness-baseline-configuration is canonical. "
        f"First surviving paths: {surviving[:10]}"
    )
