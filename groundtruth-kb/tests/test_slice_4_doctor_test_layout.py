# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""T-4-doctor-test-rename-archive (Slice 4 REVISED-7 F2 fix).

Post-implementation file-presence regression test for the doctor test
layout produced by Slice 4 D4. The four assertions below catch silent
drift in the four file moves the slice performs:

  (a) ``test_doctor_bridge_poller.py`` is renamed to
      ``test_doctor_bridge_dispatch_liveness.py`` — old path gone.
  (b) ``test_doctor_bridge_dispatch_liveness.py`` exists at its new live path.
  (c) ``test_doctor_smart_poller.py`` is archived — old live path gone.
  (d) ``test_doctor_smart_poller.py`` exists at its archive target,
      ``archive/smart-poller-2026-05-09/groundtruth-kb/tests/test_doctor_smart_poller.py``.

If any of these regress (e.g., a future refactor re-creates the legacy
path or moves the archive target), this test fails with a clear pointer
to the slice that established the layout.
"""

from __future__ import annotations

from pathlib import Path

# This test lives at <gt-kb-root>/groundtruth-kb/tests/, so
# parents[2] is the GT-KB root.
_GT_KB_ROOT = Path(__file__).resolve().parents[2]
_TESTS_DIR = _GT_KB_ROOT / "groundtruth-kb" / "tests"
_ARCHIVE_DIR = _GT_KB_ROOT / "archive" / "smart-poller-2026-05-09"


def test_legacy_bridge_poller_test_path_absent() -> None:
    """(a) Old ``test_doctor_bridge_poller.py`` no longer exists."""
    legacy = _TESTS_DIR / "test_doctor_bridge_poller.py"
    assert not legacy.exists(), (
        f"Legacy test path {legacy} still exists — Slice 4 D4 renamed it to "
        f"test_doctor_bridge_dispatch_liveness.py."
    )


def test_renamed_bridge_dispatch_liveness_test_path_exists() -> None:
    """(b) ``test_doctor_bridge_dispatch_liveness.py`` exists at the new live path."""
    renamed = _TESTS_DIR / "test_doctor_bridge_dispatch_liveness.py"
    assert renamed.is_file(), (
        f"Renamed test path {renamed} does not exist — Slice 4 D4 was meant to "
        f"rename test_doctor_bridge_poller.py to this path."
    )


def test_legacy_smart_poller_doctor_test_path_absent() -> None:
    """(c) Old ``test_doctor_smart_poller.py`` no longer exists at its live tests/ path."""
    legacy = _TESTS_DIR / "test_doctor_smart_poller.py"
    assert not legacy.exists(), (
        f"Legacy test path {legacy} still exists at its live location — Slice 4 D4 "
        f"archived it to {_ARCHIVE_DIR}."
    )


def test_archived_smart_poller_doctor_test_path_exists() -> None:
    """(d) ``test_doctor_smart_poller.py`` exists at its archive target."""
    archived = _ARCHIVE_DIR / "groundtruth-kb" / "tests" / "test_doctor_smart_poller.py"
    assert archived.is_file(), (
        f"Archived test path {archived} does not exist — Slice 4 D4 was meant to "
        f"archive test_doctor_smart_poller.py to this exact path."
    )
