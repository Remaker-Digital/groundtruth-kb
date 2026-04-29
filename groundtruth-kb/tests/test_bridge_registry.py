# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for groundtruth_kb.bridge.registry.

Per ``bridge/gtkb-bridge-poller-p2-registry-005.md`` section 4.1, these tests
cover atomic writes, harness_kind enum validation, active_role capture,
recording_pid/ppid honesty, path-traversal guard, list-all-registrations
sorting + ``since_days`` filter, and a subprocess test that proves the
shipped sample command works end-to-end.

Bridge imports are lazy per tests/test_bridge_import_hygiene.py rule.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import pytest


def _registry() -> SimpleNamespace:
    """Lazy-import bridge.registry per test_bridge_import_hygiene rule."""
    from groundtruth_kb.bridge.registry import (
        HARNESS_KINDS,
        REGISTRY_SUBDIR,
        HarnessRegistration,
        list_all_registrations,
        register_harness,
    )

    return SimpleNamespace(
        HARNESS_KINDS=HARNESS_KINDS,
        REGISTRY_SUBDIR=REGISTRY_SUBDIR,
        HarnessRegistration=HarnessRegistration,
        list_all_registrations=list_all_registrations,
        register_harness=register_harness,
    )


def _paths() -> SimpleNamespace:
    from groundtruth_kb.bridge.paths import GROUNDTRUTH_MARKER, PROJECT_ROOT_ENV_VAR

    return SimpleNamespace(
        GROUNDTRUTH_MARKER=GROUNDTRUTH_MARKER,
        PROJECT_ROOT_ENV_VAR=PROJECT_ROOT_ENV_VAR,
    )


@pytest.fixture
def synthetic_gtkb_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    p = _paths()
    synth = tmp_path / "synth_gtkb"
    synth.mkdir()
    (synth / p.GROUNDTRUTH_MARKER).write_text("# synthetic GT-KB root for tests\n")
    monkeypatch.setenv(p.PROJECT_ROOT_ENV_VAR, str(synth))
    return synth


def test_register_writes_atomic_record(synthetic_gtkb_root: Path) -> None:
    r = _registry()
    record = r.register_harness(harness_kind="claude-code")
    target = synthetic_gtkb_root / ".gtkb-state" / "bridge-poller" / r.REGISTRY_SUBDIR / f"{record.harness_id}.json"
    assert target.is_file()
    payload = json.loads(target.read_text(encoding="utf-8"))
    assert payload["harness_kind"] == "claude-code"
    assert payload["schema_version"] == 1


def test_register_validates_harness_kind_enum(synthetic_gtkb_root: Path) -> None:
    r = _registry()
    with pytest.raises(ValueError):
        r.register_harness(harness_kind="bogus-harness")


def test_register_captures_active_role_from_durable_record(
    synthetic_gtkb_root: Path,
) -> None:
    r = _registry()
    role_dir = synthetic_gtkb_root / "harness-state" / "claude"
    role_dir.mkdir(parents=True)
    (role_dir / "operating-role.md").write_text("active_role: prime-builder\n", encoding="utf-8")
    record = r.register_harness(harness_kind="claude-code")
    assert record.active_role == "prime-builder"


def test_register_active_role_unknown_when_record_missing(
    synthetic_gtkb_root: Path,
) -> None:
    r = _registry()
    record = r.register_harness(harness_kind="claude-code")
    assert record.active_role == "unknown"


def test_register_captures_recording_pid_and_ppid_honestly(
    synthetic_gtkb_root: Path,
) -> None:
    r = _registry()
    record = r.register_harness(harness_kind="claude-code")
    assert record.recording_pid == os.getpid()
    assert record.recording_ppid == os.getppid()


def test_register_does_not_describe_either_pid_as_harness_pid(
    synthetic_gtkb_root: Path,
) -> None:
    """Negative assertion: code/JSON must not call recording_pid the harness PID."""
    r = _registry()
    record = r.register_harness(harness_kind="claude-code")
    target = synthetic_gtkb_root / ".gtkb-state" / "bridge-poller" / r.REGISTRY_SUBDIR / f"{record.harness_id}.json"
    raw = target.read_text(encoding="utf-8")
    assert "harness_pid" not in raw
    assert "session_pid" not in raw


def test_register_path_traversal_guard_keeps_harness_id_safe(
    synthetic_gtkb_root: Path,
) -> None:
    """Workspace roots with path-traversal-y names produce safe harness_ids.

    The slugify+guard combination ensures the constructed harness_id never
    contains '/', '\\', '..', or null bytes regardless of input.
    """
    r = _registry()
    bad_root = synthetic_gtkb_root / "weird name with spaces & symbols!"
    bad_root.mkdir()
    record = r.register_harness(harness_kind="claude-code", workspace_root=bad_root)
    assert "/" not in record.harness_id
    assert "\\" not in record.harness_id
    assert ".." not in record.harness_id
    assert "\x00" not in record.harness_id


def test_validate_harness_id_rejects_forbidden_chars() -> None:
    """The path-traversal guard rejects harness_id values containing forbidden tokens."""
    from groundtruth_kb.bridge.registry import _validate_harness_id

    for bad_id in ("foo/bar-001", "foo\\bar-001", "foo..bar-001", "foo\x00bar"):
        with pytest.raises(ValueError):
            _validate_harness_id(bad_id)


def test_list_all_registrations_returns_records_sorted_by_recorded_at(
    synthetic_gtkb_root: Path,
) -> None:
    r = _registry()
    rec1 = r.register_harness(harness_kind="claude-code")
    time.sleep(1.1)  # ensure recorded_at differs at second precision
    rec2 = r.register_harness(harness_kind="codex")
    items = r.list_all_registrations()
    assert len(items) >= 2
    ids = [item.harness_id for item in items]
    # rec2 (later) must appear before rec1 (earlier) in descending sort
    assert ids.index(rec2.harness_id) < ids.index(rec1.harness_id)


def test_list_all_registrations_since_days_filter_works(
    synthetic_gtkb_root: Path,
) -> None:
    r = _registry()
    r.register_harness(harness_kind="claude-code")
    items_recent = r.list_all_registrations(since_days=7)
    items_no_filter = r.list_all_registrations(since_days=None)
    assert len(items_recent) == len(items_no_filter) == 1

    # Manually backdate the record to before the cutoff
    target = synthetic_gtkb_root / ".gtkb-state" / "bridge-poller" / r.REGISTRY_SUBDIR
    [json_file] = list(target.glob("*.json"))
    raw = json.loads(json_file.read_text(encoding="utf-8"))
    raw["recorded_at"] = "2020-01-01T00:00:00+00:00"
    json_file.write_text(json.dumps(raw), encoding="utf-8")

    items_filtered = r.list_all_registrations(since_days=7)
    items_unfiltered = r.list_all_registrations(since_days=None)
    assert len(items_filtered) == 0
    assert len(items_unfiltered) == 1


def test_invoke_template_round_trip_preserves_placeholders(
    synthetic_gtkb_root: Path,
) -> None:
    r = _registry()
    record = r.register_harness(harness_kind="claude-code")
    [item] = r.list_all_registrations()
    assert item.invoke_command_template == record.invoke_command_template
    assert "{prompt}" in item.invoke_command_template
    assert "{workspace_root}" in item.invoke_command_template


def test_registry_cli_via_subprocess_creates_record(
    synthetic_gtkb_root: Path,
) -> None:
    """The shipped sample hook command actually works end-to-end."""
    p = _paths()
    env = {**os.environ, p.PROJECT_ROOT_ENV_VAR: str(synthetic_gtkb_root)}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "groundtruth_kb.bridge.registry",
            "register",
            "--harness-kind",
            "claude-code",
        ],
        cwd=str(synthetic_gtkb_root),
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    registry_dir = synthetic_gtkb_root / ".gtkb-state" / "bridge-poller" / "registry"
    json_files = list(registry_dir.glob("*.json"))
    assert len(json_files) == 1
    payload = json.loads(json_files[0].read_text(encoding="utf-8"))
    assert payload["harness_kind"] == "claude-code"
    assert payload["schema_version"] == 1
    assert "recording_pid" in payload


def test_registry_cli_via_subprocess_codex_kind(
    synthetic_gtkb_root: Path,
) -> None:
    p = _paths()
    env = {**os.environ, p.PROJECT_ROOT_ENV_VAR: str(synthetic_gtkb_root)}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "groundtruth_kb.bridge.registry",
            "register",
            "--harness-kind",
            "codex",
        ],
        cwd=str(synthetic_gtkb_root),
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    payload = json.loads(
        next((synthetic_gtkb_root / ".gtkb-state" / "bridge-poller" / "registry").glob("*.json")).read_text(
            encoding="utf-8"
        )
    )
    assert payload["harness_kind"] == "codex"


def test_registry_cli_rejects_invalid_harness_kind(
    synthetic_gtkb_root: Path,
) -> None:
    p = _paths()
    env = {**os.environ, p.PROJECT_ROOT_ENV_VAR: str(synthetic_gtkb_root)}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "groundtruth_kb.bridge.registry",
            "register",
            "--harness-kind",
            "bogus",
        ],
        cwd=str(synthetic_gtkb_root),
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
