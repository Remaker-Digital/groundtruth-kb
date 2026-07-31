"""Tests for mode-switch bridge substrate validation.

Covers SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from pathlib import Path

from groundtruth_kb.mode_switch.validation import validate_bridge_substrate, validate_role_artifact


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_substrate_artifact_validator_reports_missing_daemon_script(tmp_path: Path) -> None:
    res = validate_bridge_substrate(tmp_path, "dispatcher_daemon", "single_harness")
    assert res.is_valid is False
    assert "scripts/gtkb_dispatcher_daemon.py is missing" in res.errors[0]


def test_role_artifact_validator_required_before_substrate_write(tmp_path: Path) -> None:
    # Validate missing role artifact behavior
    res = validate_role_artifact(tmp_path)
    assert res.is_valid is False
    assert "role artifact missing" in res.errors[0]


def test_validate_dispatcher_daemon_substrate_requires_fresh_heartbeat(tmp_path: Path) -> None:
    from groundtruth_kb.mode_switch.validation import (
        DISPATCHER_DAEMON_HEARTBEAT_MAX_AGE_SECONDS,
        DISPATCHER_DAEMON_SUBSTRATE,
        validate_bridge_substrate,
    )

    state_dir = tmp_path / ".gtkb-state" / "dispatcher-daemon"
    state_dir.mkdir(parents=True)
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "gtkb_dispatcher_daemon.py").write_text("# stub\n", encoding="utf-8")
    res = validate_bridge_substrate(tmp_path, DISPATCHER_DAEMON_SUBSTRATE, "single_harness")
    assert res.is_valid is False
    assert "lock is absent" in res.errors[0]

    (state_dir / "daemon.lock").write_text("{}", encoding="utf-8")
    res = validate_bridge_substrate(tmp_path, DISPATCHER_DAEMON_SUBSTRATE, "single_harness")
    assert res.is_valid is False
    assert "heartbeat" in res.errors[0].lower()

    fresh = (
        __import__("datetime")
        .datetime.now(__import__("datetime").UTC)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )
    (state_dir / "heartbeat.txt").write_text(fresh + "\n", encoding="utf-8")
    res = validate_bridge_substrate(tmp_path, DISPATCHER_DAEMON_SUBSTRATE, "single_harness")
    assert res.is_valid is True
    assert DISPATCHER_DAEMON_HEARTBEAT_MAX_AGE_SECONDS == 120


def test_validate_rejects_unknown_substrate(tmp_path: Path) -> None:
    from groundtruth_kb.mode_switch.validation import validate_bridge_substrate

    res = validate_bridge_substrate(tmp_path, "not_a_real_substrate", "single_harness")
    assert res.is_valid is False
    assert "unknown bridge substrate" in res.errors[0]
