# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for the WI-4804 kill-switch-staleness doctor check.

Verifies ``_check_kill_switch_staleness`` (``groundtruth_kb.project.doctor``):
- not set -> PASS and the first-seen bookkeeping is cleared;
- set, first observation -> records first-seen, INFO (recent);
- set, recent first-seen -> INFO (under threshold);
- set, first-seen beyond threshold -> WARNING; the env var is never modified
  (visibility only, never auto-clear).

Specification Links:
- SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001 (visibility, never auto-clear)
- DELIB-20266140 (visibility-not-auto-clear policy); DELIB-20266166 (scope split)
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from groundtruth_kb.project.doctor import (
    _KILL_SWITCH_ENV_VAR,
    _KILL_SWITCH_FIRST_SEEN_REL,
    _KILL_SWITCH_STALE_SECONDS,
    _check_kill_switch_staleness,
)


def _first_seen_path(target: Path) -> Path:
    return target / _KILL_SWITCH_FIRST_SEEN_REL


def _write_first_seen(target: Path, when: datetime) -> None:
    path = _first_seen_path(target)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"first_seen": when.isoformat()}), encoding="utf-8")


def test_pass_and_clears_when_kill_switch_unset(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(_KILL_SWITCH_ENV_VAR, raising=False)
    _write_first_seen(tmp_path, datetime.now(UTC) - timedelta(hours=5))  # stale leftover record
    result = _check_kill_switch_staleness(tmp_path)
    assert result.status == "pass"
    assert not _first_seen_path(tmp_path).exists()  # bookkeeping cleared


def test_records_first_seen_on_first_observation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(_KILL_SWITCH_ENV_VAR, "1")
    assert not _first_seen_path(tmp_path).exists()
    result = _check_kill_switch_staleness(tmp_path)
    assert result.status == "info"  # just observed -> recent, not yet stale
    assert _first_seen_path(tmp_path).exists()  # first-seen recorded


def test_info_when_kill_switch_set_recently(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(_KILL_SWITCH_ENV_VAR, "1")
    _write_first_seen(tmp_path, datetime.now(UTC) - timedelta(seconds=60))
    result = _check_kill_switch_staleness(tmp_path)
    assert result.status == "info"


def test_warns_when_kill_switch_set_beyond_threshold(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(_KILL_SWITCH_ENV_VAR, "1")
    old = datetime.now(UTC) - timedelta(seconds=_KILL_SWITCH_STALE_SECONDS + 3600)
    _write_first_seen(tmp_path, old)
    result = _check_kill_switch_staleness(tmp_path)
    assert result.status == "warning"
    # Visibility only: the check must NEVER auto-clear the manual env var.
    assert os.environ.get(_KILL_SWITCH_ENV_VAR) == "1"
