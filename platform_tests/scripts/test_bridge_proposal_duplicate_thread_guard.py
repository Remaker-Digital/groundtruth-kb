"""Tests for scripts/bridge_proposal_duplicate_thread_guard.py (WI-4573, B#3)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "bridge_proposal_duplicate_thread_guard.py"


def _load_module():
    scripts_dir = PROJECT_ROOT / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    spec = importlib.util.spec_from_file_location("bridge_proposal_duplicate_thread_guard", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["bridge_proposal_duplicate_thread_guard"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def module():
    return _load_module()


def _write_thread(tmp_path: Path, slug: str, status: str, work_item: str) -> Path:
    path = tmp_path / "bridge" / f"{slug}-001.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"{status}\n\nbridge_kind: prime_proposal\nWork Item: {work_item}\n\nbody\n",
        encoding="utf-8",
    )
    return path


def _write_draft(tmp_path: Path, work_item: str | None) -> Path:
    draft = tmp_path / "draft.md"
    wi_line = f"Work Item: {work_item}\n" if work_item else ""
    draft.write_text(f"NEW\n\nbridge_kind: prime_proposal\n{wi_line}\nbody\n", encoding="utf-8")
    return draft


def test_duplicate_live_thread_detected(module, tmp_path) -> None:
    _write_thread(tmp_path, "existing-thread", "NEW", "WI-9001")
    draft = _write_draft(tmp_path, "WI-9001")

    result, exit_code = module.run_guard(tmp_path, content_file=str(draft), own_slug="my-new-thread")

    assert result["verdict"] == "duplicates"
    assert [d["slug"] for d in result["duplicate_threads"]] == ["existing-thread"]
    assert exit_code == module.EXIT_OK  # advisory by default


def test_terminal_verified_thread_not_flagged(module, tmp_path) -> None:
    _write_thread(tmp_path, "done-thread", "VERIFIED", "WI-9001")
    draft = _write_draft(tmp_path, "WI-9001")

    result, _exit_code = module.run_guard(tmp_path, content_file=str(draft), own_slug="my-new-thread")

    assert result["verdict"] == "clean"
    assert result["duplicate_threads"] == []


def test_deferred_and_withdrawn_not_flagged(module, tmp_path) -> None:
    _write_thread(tmp_path, "parked-thread", "DEFERRED", "WI-9002")
    _write_thread(tmp_path, "gone-thread", "WITHDRAWN", "WI-9002")
    draft = _write_draft(tmp_path, "WI-9002")

    result, _exit_code = module.run_guard(tmp_path, content_file=str(draft), own_slug="my-new-thread")

    assert result["verdict"] == "clean"


def test_same_slug_self_excluded(module, tmp_path) -> None:
    _write_thread(tmp_path, "my-new-thread", "NEW", "WI-9003")
    draft = _write_draft(tmp_path, "WI-9003")

    result, _exit_code = module.run_guard(tmp_path, content_file=str(draft), own_slug="my-new-thread")

    assert result["verdict"] == "clean"
    assert result["duplicate_threads"] == []


def test_unrelated_work_item_clean(module, tmp_path) -> None:
    _write_thread(tmp_path, "unrelated-thread", "NEW", "WI-8000")
    draft = _write_draft(tmp_path, "WI-9004")

    result, _exit_code = module.run_guard(tmp_path, content_file=str(draft), own_slug="my-new-thread")

    assert result["verdict"] == "clean"
    assert result["duplicate_threads"] == []


def test_strict_exits_nonzero_on_duplicate(module, tmp_path) -> None:
    _write_thread(tmp_path, "existing-thread", "GO", "WI-9005")
    draft = _write_draft(tmp_path, "WI-9005")

    result, exit_code = module.run_guard(tmp_path, content_file=str(draft), own_slug="my-new-thread", strict=True)

    assert result["verdict"] == "duplicates"
    assert exit_code == module.EXIT_STRICT_DUPLICATES


def test_no_declared_work_item_skipped(module, tmp_path) -> None:
    _write_thread(tmp_path, "existing-thread", "NEW", "WI-9006")
    draft = _write_draft(tmp_path, None)

    result, exit_code = module.run_guard(tmp_path, content_file=str(draft), own_slug="my-new-thread")

    assert result["verdict"] == "no_work_item"
    assert exit_code == module.EXIT_OK
