# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""FAB-08 (HYG-053) spec-derived tests: robust sandbox removal + doctor auto-prune.

Covers the GO'd acceptance criteria for ``bridge/gtkb-fab-08-slot-leak-fix-001.md``
(GO at ``-002``):

- ``_force_remove_tree`` removes a read-only ``.git``-style tree without a silent
  failure, and fails LOUDLY (does not swallow real errors like
  ``ignore_errors=True`` did) — the GO constraint.
- ``_check_stale_test_slots`` prunes ``applications/_test_*`` slots older than 24h,
  emits a WARN, and never touches a non-``_test_*`` sibling or a fresh slot.
"""

from __future__ import annotations

import os
import stat
import time
from pathlib import Path

import pytest
from groundtruth_kb.project.checks import stale_test_slots as doctor_mod
from groundtruth_kb.project.checks.stale_test_slots import (
    check_stale_test_slots as _check_stale_test_slots,
    _force_remove_tree,
)

# Repo root, used by the runtime-floor source-scan test below.
_GT_KB_ROOT = Path(__file__).resolve().parents[2]

# Every file that defines a force-remove helper calling shutil.rmtree. The FAB-08
# NO-GO (-004) found these used the py3.12+ ``onexc`` keyword unconditionally,
# which raises ``TypeError`` on the package's declared ``requires-python = ">=3.11"``
# floor. The fix is a version-adaptive dispatch (onexc on 3.12+, onerror on 3.11).
_RMTREE_HELPER_FILES = [
    _GT_KB_ROOT / "groundtruth-kb" / "src" / "groundtruth_kb" / "project" / "checks" / "stale_test_slots.py",
    _GT_KB_ROOT / "groundtruth-kb" / "tests" / "adopter" / "conftest.py",
    _GT_KB_ROOT / "groundtruth-kb" / "tests" / "test_cli.py",
    _GT_KB_ROOT / "groundtruth-kb" / "tests" / "test_scaffold_isolation.py",
]


def _make_readonly_git_tree(root: Path) -> Path:
    """Create a dir tree with a read-only file, mimicking Windows ``.git`` objects."""
    objects = root / ".git" / "objects"
    objects.mkdir(parents=True)
    obj = objects / "deadbeef"
    obj.write_bytes(b"x")
    os.chmod(obj, stat.S_IREAD)
    return root


def test_force_remove_tree_clears_readonly(tmp_path: Path) -> None:
    """A read-only .git tree is removed (onexc clears the bit on Windows)."""
    slot = _make_readonly_git_tree(tmp_path / "slot")
    assert slot.exists()
    _force_remove_tree(slot)
    assert not slot.exists()


def test_force_remove_tree_fails_loudly_on_missing(tmp_path: Path) -> None:
    """Unlike ignore_errors=True, a removal that cannot proceed raises (loud)."""
    with pytest.raises(OSError):
        _force_remove_tree(tmp_path / "does-not-exist")


def test_check_stale_test_slots_prunes_old_keeps_fresh(tmp_path: Path) -> None:
    apps = tmp_path / "applications"
    apps.mkdir()

    stale = _make_readonly_git_tree(apps / "_test_deadbeef")
    old = time.time() - (25 * 3600)
    os.utime(stale, (old, old))

    fresh = apps / "_test_cafef00d"
    fresh.mkdir()

    real_app = apps / "Agent_Red"
    real_app.mkdir()

    old_non_test = apps / "_keep_me"  # old but NOT _test_*
    old_non_test.mkdir()
    os.utime(old_non_test, (old, old))

    result = _check_stale_test_slots(tmp_path)

    assert result.status == "warning"
    assert "_test_deadbeef" in result.message
    assert not stale.exists(), "stale _test_* slot must be pruned"
    assert fresh.exists(), "fresh _test_* slot must NOT be pruned"
    assert real_app.exists(), "real application subtree must NEVER be pruned"
    assert old_non_test.exists(), "non-_test_* dir must NEVER be pruned, even when old"


def test_check_stale_test_slots_pass_when_clean(tmp_path: Path) -> None:
    (tmp_path / "applications").mkdir()
    result = _check_stale_test_slots(tmp_path)
    assert result.status == "pass"


def test_check_stale_test_slots_pass_when_no_applications_dir(tmp_path: Path) -> None:
    result = _check_stale_test_slots(tmp_path)
    assert result.status == "pass"


# --- FAB-08 NO-GO (-004) runtime-floor regression: onexc is py3.12+ only ----


def test_force_remove_tree_uses_onerror_on_py311_floor(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """On the declared >=3.11 floor, the helper MUST use onerror, not onexc.

    ``shutil.rmtree(..., onexc=...)`` is a Python 3.12+ keyword; on 3.11 it raises
    ``TypeError``. This test simulates the runtime floor and asserts the helper
    dispatches to the 3.11-compatible ``onerror`` path. It would fail against the
    pre-fix unconditional-``onexc`` implementation regardless of the interpreter
    actually running the test.
    """
    recorded: list[dict] = []
    monkeypatch.setattr(doctor_mod.shutil, "rmtree", lambda path, **kw: recorded.append(kw))
    monkeypatch.setattr(doctor_mod.sys, "version_info", (3, 11, 5, "final", 0))

    _force_remove_tree(Path("does-not-need-to-exist"))

    assert len(recorded) == 1
    assert "onexc" not in recorded[0], "onexc is py3.12+ only; would TypeError on >=3.11 floor"
    assert "onerror" in recorded[0], "py3.11 floor must dispatch to the onerror callback"


def test_force_remove_tree_uses_onexc_on_py312_plus(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """On 3.12+, the helper uses the modern onexc keyword."""
    recorded: list[dict] = []
    monkeypatch.setattr(doctor_mod.shutil, "rmtree", lambda path, **kw: recorded.append(kw))
    monkeypatch.setattr(doctor_mod.sys, "version_info", (3, 12, 0, "final", 0))

    _force_remove_tree(Path("does-not-need-to-exist"))

    assert len(recorded) == 1
    assert "onexc" in recorded[0], "py3.12+ should use the onexc keyword"
    assert "onerror" not in recorded[0]


@pytest.mark.parametrize("src", _RMTREE_HELPER_FILES, ids=lambda p: p.name)
def test_rmtree_helpers_are_runtime_floor_compatible(src: Path) -> None:
    """Source-level guard: every rmtree helper carries a version-adaptive dispatch.

    Interpreter-independent (so it catches the >=3.11 regression even when the
    verifier runs 3.12+): each helper file must contain BOTH the py3.12+ ``onexc``
    branch AND a py3.11 ``onerror`` fallback, gated by a ``sys.version_info`` check.
    """
    text = src.read_text(encoding="utf-8")
    assert "onexc=" in text, f"{src.name}: missing the py3.12+ onexc branch"
    assert "onerror=" in text, f"{src.name}: missing the py3.11 onerror fallback (would TypeError on 3.11)"
    assert "version_info" in text, f"{src.name}: rmtree dispatch is not guarded by a sys.version_info check"
