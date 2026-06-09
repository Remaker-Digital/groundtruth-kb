# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for scripts/bridge_notify_reader.py.

Per ``bridge/gtkb-bridge-poller-notify-activation-2026-04-29-004.md`` GO
conditions + -003 §3.2 test matrix:

- absent file → returns None
- valid single REVISED action for prime
- valid multiple actions for codex
- empty pending_actions → empty string (no header-with-empty-table)
- malformed JSON → canonical reader returns None; format returns empty
- schema_version mismatch → defensive empty (no garbled rows)
- canonical-API drift guard (structural — by importing the canonical
  dataclass, parser drift is impossible)

The reader is loaded via importlib (it lives under scripts/, not the package
proper) following the same pattern as test_bridge_poller_runner.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

_READER_PATH = Path(__file__).resolve().parents[2] / "scripts" / "bridge_notify_reader.py"


def _load_reader() -> ModuleType:
    """Load scripts/bridge_notify_reader.py with sys.modules registration."""
    assert _READER_PATH.is_file(), f"Expected reader at {_READER_PATH}"
    module_name = "bridge_notify_reader"
    if module_name in sys.modules:
        return sys.modules[module_name]
    spec = importlib.util.spec_from_file_location(module_name, _READER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _notify() -> SimpleNamespace:
    """Lazy-import canonical notify symbols per the import-hygiene rule."""
    from groundtruth_kb.bridge.notify import (
        NOTIFY_SCHEMA_VERSION,
        NOTIFY_SUBDIR,
        ActionablePending,
        NotificationArtifact,
        update_notification,
    )
    from groundtruth_kb.bridge.routing import BridgeAgent

    return SimpleNamespace(
        NOTIFY_SCHEMA_VERSION=NOTIFY_SCHEMA_VERSION,
        NOTIFY_SUBDIR=NOTIFY_SUBDIR,
        ActionablePending=ActionablePending,
        BridgeAgent=BridgeAgent,
        NotificationArtifact=NotificationArtifact,
        update_notification=update_notification,
    )


def _state_dir(project_root: Path) -> Path:
    return project_root / ".gtkb-state" / "bridge-poller"


def _write_notification(
    project_root: Path,
    recipient,
    items,
    poller_run_id: str = "test-run-001",
) -> None:
    n = _notify()
    state = _state_dir(project_root)
    state.mkdir(parents=True, exist_ok=True)
    n.update_notification(state, recipient, items, poller_run_id=poller_run_id)


# --- Test 1: absent file → returns None -------------------------------------


def test_absent_file_returns_none(tmp_path: Path) -> None:
    reader = _load_reader()
    n = _notify()
    artifact = reader.read_for_recipient(tmp_path, n.BridgeAgent.PRIME)
    assert artifact is None
    assert reader.format_orient_section(artifact) == ""


# --- Test 2: valid single REVISED action for prime --------------------------


def test_valid_single_action_for_codex(tmp_path: Path) -> None:
    reader = _load_reader()
    n = _notify()
    items = [
        n.ActionablePending(
            document_name="foo-thread",
            top_status="REVISED",
            top_file="bridge/foo-thread-002.md",
            index_line_number=42,
        )
    ]
    _write_notification(tmp_path, n.BridgeAgent.CODEX, items)

    artifact = reader.read_for_recipient(tmp_path, n.BridgeAgent.CODEX)
    assert artifact is not None
    assert len(artifact.pending_actions) == 1

    section = reader.format_orient_section(artifact)
    assert "1 pending action(s)" in section
    assert "`foo-thread`" in section
    assert "**REVISED**" in section
    assert "`bridge/foo-thread-002.md`" in section
    assert "42" in section


# --- Test 3: valid multiple actions ----------------------------------------


def test_valid_multiple_actions_for_prime(tmp_path: Path) -> None:
    reader = _load_reader()
    n = _notify()
    items = [
        n.ActionablePending(
            document_name="thread-a",
            top_status="GO",
            top_file="bridge/thread-a-003.md",
            index_line_number=10,
        ),
        n.ActionablePending(
            document_name="thread-b",
            top_status="NO-GO",
            top_file="bridge/thread-b-002.md",
            index_line_number=15,
        ),
    ]
    _write_notification(tmp_path, n.BridgeAgent.PRIME, items)

    artifact = reader.read_for_recipient(tmp_path, n.BridgeAgent.PRIME)
    assert artifact is not None
    assert len(artifact.pending_actions) == 2

    section = reader.format_orient_section(artifact)
    assert "2 pending action(s)" in section
    assert "`thread-a`" in section
    assert "`thread-b`" in section
    assert "**GO**" in section
    assert "**NO-GO**" in section
    # Order preserved
    assert section.index("thread-a") < section.index("thread-b")


# --- Test 4: empty pending_actions → empty string ---------------------------


def test_empty_pending_actions_returns_empty_string(tmp_path: Path) -> None:
    reader = _load_reader()
    n = _notify()
    # Force-write a file with empty pending_actions by writing then clearing.
    # Easier: write directly via canonical API with empty list — but that
    # removes the file. So we manually craft an empty-actions file on disk.
    state = _state_dir(tmp_path)
    notify_dir = state / n.NOTIFY_SUBDIR
    notify_dir.mkdir(parents=True, exist_ok=True)
    json_path = notify_dir / "pending-bridge-action-prime.json"
    json_path.write_text(
        json.dumps(
            {
                "schema_version": n.NOTIFY_SCHEMA_VERSION,
                "recipient": "prime",
                "written_at": "2026-04-29T00:00:00Z",
                "poller_run_id": "test",
                "pending_actions": [],
                "summary": "no pending actions",
            }
        ),
        encoding="utf-8",
    )

    artifact = reader.read_for_recipient(tmp_path, n.BridgeAgent.PRIME)
    assert artifact is not None
    assert len(artifact.pending_actions) == 0
    assert reader.format_orient_section(artifact) == ""


# --- Test 5: malformed JSON → canonical returns None; format empty ---------


def test_malformed_json_returns_none(tmp_path: Path) -> None:
    reader = _load_reader()
    n = _notify()
    state = _state_dir(tmp_path)
    notify_dir = state / n.NOTIFY_SUBDIR
    notify_dir.mkdir(parents=True, exist_ok=True)
    json_path = notify_dir / "pending-bridge-action-prime.json"
    json_path.write_text("{{ not valid json", encoding="utf-8")

    artifact = reader.read_for_recipient(tmp_path, n.BridgeAgent.PRIME)
    assert artifact is None
    assert reader.format_orient_section(artifact) == ""


# --- Test 6: schema_version mismatch → defensive empty ---------------------


def test_schema_version_mismatch_returns_empty(tmp_path: Path) -> None:
    reader = _load_reader()
    n = _notify()
    state = _state_dir(tmp_path)
    notify_dir = state / n.NOTIFY_SUBDIR
    notify_dir.mkdir(parents=True, exist_ok=True)
    json_path = notify_dir / "pending-bridge-action-codex.json"
    # Future schema bump (v99) — reader should refuse to render rather than
    # surface potentially garbled fields.
    json_path.write_text(
        json.dumps(
            {
                "schema_version": 99,
                "recipient": "codex",
                "written_at": "2026-04-29T00:00:00Z",
                "poller_run_id": "test",
                "pending_actions": [
                    {
                        "document_name": "x",
                        "top_status": "REVISED",
                        "top_file": "bridge/x-001.md",
                        "index_line_number": 1,
                    }
                ],
                "summary": "future schema",
            }
        ),
        encoding="utf-8",
    )

    artifact = reader.read_for_recipient(tmp_path, n.BridgeAgent.CODEX)
    # Alignment check: reader surfaces the artifact regardless of schema version.
    assert artifact is not None
    assert artifact.schema_version == 99
    # But the formatter defensively returns empty for schema mismatch.
    assert reader.format_orient_section(artifact) == ""


# --- Test 7: canonical-API drift guard --------------------------------------


def test_canonical_api_drift_guard() -> None:
    """Structural guard: by importing the canonical dataclass + reader,
    parser drift between this module and groundtruth_kb.bridge.notify is
    impossible. This test asserts the imports + dataclass attribute access
    still work, which is the durable surface contract."""
    reader = _load_reader()
    from groundtruth_kb.bridge.notify import (
        NOTIFY_SCHEMA_VERSION,
        NOTIFY_SUBDIR,
        NotificationArtifact,
        read_notification,
    )

    # The reader module must reference the same canonical symbols.
    assert reader.NOTIFY_SCHEMA_VERSION == NOTIFY_SCHEMA_VERSION
    assert reader.NOTIFY_SUBDIR == NOTIFY_SUBDIR
    assert reader.NotificationArtifact is NotificationArtifact
    assert reader.read_notification is read_notification

    # NotificationArtifact dataclass attribute access continues to work.
    sample_attrs = {"schema_version", "recipient", "written_at", "poller_run_id", "pending_actions", "summary"}
    assert sample_attrs.issubset({f.name for f in NotificationArtifact.__dataclass_fields__.values()})


# --- Bonus: invalid recipient handling --------------------------------------


def test_invalid_recipient_returns_none(tmp_path: Path) -> None:
    """Canonical API is permissive on recipient strings — it builds a path
    using whatever string is supplied and returns None for absent file. This
    is fail-open behavior per activation guardrail 1 (startup must not break
    on bad input). The reader inherits this behavior unchanged."""
    reader = _load_reader()
    artifact = reader.read_for_recipient(tmp_path, "bogus-recipient")
    assert artifact is None
    assert reader.format_orient_section(artifact) == ""
