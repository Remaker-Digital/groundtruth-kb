# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for the bridge authority-direction switch + reversibility backstop.

Covers ``DCL-INDEX-GENERATED-VIEW-001`` #3 (single canonical direction surface +
safe default) and #4 (reversibility backstop: a timestamped immutable frozen
INDEX copy + a coded revert) for the WI-4510 Phase-3 default-OFF slice.

Authority: ``bridge/gtkb-wi4510-phase-3-authority-flip-003.md`` (Loyal Opposition
GO at ``-004``). The flip path (#6-#11) is covered by the deferred
``test_tafe_authoritative_write_path.py``; this module tests only the switch +
backstop shipped in ``scripts/bridge_authority_cutover.py``.
"""

from __future__ import annotations

import importlib.util
import os
import stat
import sys
from datetime import UTC, datetime
from pathlib import Path
from types import ModuleType

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = PROJECT_ROOT / "scripts" / "bridge_authority_cutover.py"
FIXED_NOW = datetime(2026, 6, 15, 13, 0, 0, tzinfo=UTC)


def _load_module() -> ModuleType:
    assert MODULE_PATH.is_file(), f"expected cutover module at {MODULE_PATH}"
    module_name = "bridge_authority_cutover"
    if module_name in sys.modules:
        return sys.modules[module_name]
    if str(PROJECT_ROOT / "scripts") not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location(module_name, MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _write_index(root: Path, text: str = "Document: demo\nNEW: bridge/demo-001.md\n") -> Path:
    index_path = root / "bridge" / "INDEX.md"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(text, encoding="utf-8")
    return index_path


# ── DCL-INDEX-GENERATED-VIEW-001 #3: single direction surface + safe default ──


def test_absent_state_file_is_index_canonical(tmp_path: Path) -> None:
    """Absence of the state file resolves to index_canonical (safe default)."""
    mod = _load_module()
    assert not mod.direction_state_path(tmp_path).exists()
    assert mod.read_authority_direction(tmp_path) == mod.DIRECTION_INDEX_CANONICAL


def test_reader_returns_written_canonical_value(tmp_path: Path) -> None:
    """The reader returns exactly the written canonical value, both directions."""
    mod = _load_module()
    mod.write_authority_direction(tmp_path, mod.DIRECTION_TAFE_CANONICAL, now=FIXED_NOW)
    assert mod.read_authority_direction(tmp_path) == mod.DIRECTION_TAFE_CANONICAL
    mod.write_authority_direction(tmp_path, mod.DIRECTION_INDEX_CANONICAL, now=FIXED_NOW)
    assert mod.read_authority_direction(tmp_path) == mod.DIRECTION_INDEX_CANONICAL


def test_malformed_state_fails_safe_to_index_canonical(tmp_path: Path) -> None:
    """Garbage JSON resolves to index_canonical rather than engaging the flip path."""
    mod = _load_module()
    path = mod.direction_state_path(tmp_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{ this is not valid json", encoding="utf-8")
    assert mod.read_authority_direction(tmp_path) == mod.DIRECTION_INDEX_CANONICAL


def test_unrecognized_direction_fails_safe(tmp_path: Path) -> None:
    """An unknown authority_direction value fails safe to index_canonical."""
    mod = _load_module()
    path = mod.direction_state_path(tmp_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('{"authority_direction": "tafe_supreme"}', encoding="utf-8")
    assert mod.read_authority_direction(tmp_path) == mod.DIRECTION_INDEX_CANONICAL


def test_write_rejects_invalid_direction(tmp_path: Path) -> None:
    """write_authority_direction refuses to persist an invalid direction token."""
    mod = _load_module()
    with pytest.raises(ValueError, match="invalid authority direction"):
        mod.write_authority_direction(tmp_path, "sideways", now=FIXED_NOW)
    assert not mod.direction_state_path(tmp_path).exists()


# ── DCL-INDEX-GENERATED-VIEW-001 #4: reversibility backstop ──


def test_freeze_creates_immutable_matching_copy(tmp_path: Path) -> None:
    """freeze_index writes a read-only frozen copy whose content matches INDEX."""
    mod = _load_module()
    original = "Document: demo\nNEW: bridge/demo-001.md\n"
    _write_index(tmp_path, original)
    frozen = mod.freeze_index(tmp_path, now=FIXED_NOW)
    try:
        assert frozen.is_file()
        assert frozen.parent == tmp_path / "bridge" / ".authority-cutover"
        assert frozen.read_text(encoding="utf-8") == original
        # Immutability: the frozen copy is not writable by the owner.
        assert not (frozen.stat().st_mode & stat.S_IWUSR)
    finally:
        # Restore writability so the tmp_path teardown can remove the file.
        os.chmod(frozen, 0o644)


def test_freeze_raises_when_index_absent(tmp_path: Path) -> None:
    """freeze_index fails closed when there is no INDEX to freeze."""
    mod = _load_module()
    with pytest.raises(FileNotFoundError):
        mod.freeze_index(tmp_path, now=FIXED_NOW)


def test_flip_freezes_then_sets_tafe_canonical(tmp_path: Path) -> None:
    """flip_to_tafe_canonical freezes the INDEX then engages tafe_canonical."""
    mod = _load_module()
    _write_index(tmp_path)
    assert mod.read_authority_direction(tmp_path) == mod.DIRECTION_INDEX_CANONICAL
    frozen = mod.flip_to_tafe_canonical(tmp_path, now=FIXED_NOW)
    try:
        assert mod.read_authority_direction(tmp_path) == mod.DIRECTION_TAFE_CANONICAL
        assert frozen.is_file()
    finally:
        os.chmod(frozen, 0o644)


def test_revert_restores_index_canonical_and_optional_frozen(tmp_path: Path) -> None:
    """revert flips direction back and, when asked, restores the frozen INDEX content."""
    mod = _load_module()
    original = "Document: demo\nNEW: bridge/demo-001.md\n"
    _write_index(tmp_path, original)
    frozen = mod.flip_to_tafe_canonical(tmp_path, now=FIXED_NOW)
    try:
        # Simulate a suspect post-flip INDEX being overwritten.
        index_path = tmp_path / "bridge" / "INDEX.md"
        index_path.write_text("CORRUPT POST-FLIP STATE\n", encoding="utf-8")

        restored = mod.revert_to_index_canonical(tmp_path, restore_frozen=frozen)
        assert mod.read_authority_direction(tmp_path) == mod.DIRECTION_INDEX_CANONICAL
        assert restored == index_path
        assert index_path.read_text(encoding="utf-8") == original
    finally:
        os.chmod(frozen, 0o644)


def test_revert_without_frozen_only_flips_direction(tmp_path: Path) -> None:
    """A plain revert flips the direction and does not require a frozen copy."""
    mod = _load_module()
    mod.write_authority_direction(tmp_path, mod.DIRECTION_TAFE_CANONICAL, now=FIXED_NOW)
    restored = mod.revert_to_index_canonical(tmp_path)
    assert restored is None
    assert mod.read_authority_direction(tmp_path) == mod.DIRECTION_INDEX_CANONICAL


# ── Live default-OFF invariant ──


def test_live_state_file_is_tafe_canonical() -> None:
    """The committed live switch ships default-ON (tafe_canonical) after cutover."""
    mod = _load_module()
    if not mod.direction_state_path(PROJECT_ROOT).is_file():
        pytest.skip("live bridge-authority-direction.json absent; default-OFF still holds by absence.")
    assert mod.read_authority_direction(PROJECT_ROOT) == mod.DIRECTION_TAFE_CANONICAL
