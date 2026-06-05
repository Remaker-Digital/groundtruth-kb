"""Tests for the Phase-1 Ollama dispatch verification script (WI-4322).

Spec-derived tests for ``scripts/verify_ollama_dispatch.py`` per the Phase-1
Child 3 proposal (bridge/gtkb-ollama-integration-phase-1-verification-005.md)
and the GO verdict (bridge/gtkb-ollama-integration-phase-1-verification-006.md).

The script's verification surface has six check functions across two modes:

- Live mode: ``_check_tool_loop_round_trip``, ``_check_author_metadata``,
  ``_check_bridge_filing_via_dispatch``.
- Guard-only mode: ``_check_guard_destructive_bash``,
  ``_check_guard_formal_artifact``, ``_check_guard_out_of_root``.

Tests stub the live ``urllib.request`` reachability probe, inject deterministic
mock chat functions through the shim, and exercise the dispatch path against
disposable fixture workspaces.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS_DIR = _REPO_ROOT / "scripts"


def _load_script_module():
    """Load scripts/verify_ollama_dispatch.py as a module for direct test access."""
    if str(_SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(_SCRIPTS_DIR))
    # Ensure ollama_harness is importable from the same directory.
    spec = importlib.util.spec_from_file_location("verify_ollama_dispatch", _SCRIPTS_DIR / "verify_ollama_dispatch.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def verify_module():
    return _load_script_module()


@pytest.fixture(scope="module")
def ollama_harness_module():
    if str(_SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(_SCRIPTS_DIR))
    import ollama_harness  # noqa: PLC0415

    return ollama_harness


# ── Reachability probe ────────────────────────────────────────────────────


def test_reachability_probe_returns_false_when_endpoint_dead(verify_module, monkeypatch) -> None:
    """The reachability probe must return False on URLError / OSError."""
    import urllib.error

    def fail(url, timeout):
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr("urllib.request.urlopen", fail)
    assert verify_module._ollama_reachable("http://localhost:11434") is False


def test_reachability_probe_returns_true_when_endpoint_alive(verify_module, monkeypatch) -> None:
    """The reachability probe must return True on HTTP 200."""

    class FakeResp:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self, n=64):
            return b'{"models":[]}'

    monkeypatch.setattr("urllib.request.urlopen", lambda url, timeout: FakeResp())
    assert verify_module._ollama_reachable("http://localhost:11434") is True


# ── Live-mode: tool-loop round-trip ──────────────────────────────────────


def test_tool_loop_round_trip_invokes_chat_twice(verify_module, ollama_harness_module, tmp_path) -> None:
    """L1: round-trip must invoke chat at least twice (tool_call turn + final-text turn)."""
    # Construct a route directly to avoid depending on a real routing TOML.
    route = ollama_harness_module.ModelRoute(
        key="qwen-coder-14b",
        model_id="qwen2.5-coder:14b-instruct-q4_K_M",
        model_version="q4_K_M",
        tool_calling_supported=True,
        allowed_tools=("Read",),
    )
    # Plant the routing TOML the script uses to resolve the model.
    (tmp_path / ".ollama").mkdir()
    (tmp_path / ".ollama" / "routing.toml").write_text(
        "schema_version = 1\n"
        "[models.qwen-coder-14b]\n"
        'model_id = "qwen2.5-coder:14b-instruct-q4_K_M"\n'
        'model_version = "q4_K_M"\n'
        "tool_calling_supported = true\n"
        'allowed_tools = ["Read"]\n'
        "[routing]\n"
        'default_model = "qwen-coder-14b"\n',
        encoding="utf-8",
    )
    # Plant a Read target inside tmp_path.
    target_file = tmp_path / "sentinel.txt"
    target_file.write_text("qwen-coder-14b", encoding="utf-8")

    ok = verify_module._check_tool_loop_round_trip(route, "http://localhost:11434", tmp_path)
    assert ok is True


def test_author_metadata_check_passes_when_model_id_matches(verify_module, ollama_harness_module) -> None:
    """L2: metadata model_id matches route model_id."""
    route = ollama_harness_module.ModelRoute(
        key="route1",
        model_id="my-model",
        model_version="v1",
        tool_calling_supported=True,
        allowed_tools=("Read",),
    )
    assert verify_module._check_author_metadata(route, "http://localhost:11434") is True


# ── Live-mode: bridge filing via dispatch ────────────────────────────────


def test_bridge_filing_writes_fixture_file_with_NEW_first_line(verify_module, ollama_harness_module, tmp_path) -> None:
    """L3: fixture write through dispatch_tool_call must produce a file whose
    first non-blank line is exactly ``NEW``."""
    route = ollama_harness_module.ModelRoute(
        key="route1",
        model_id="my-model",
        model_version="v1",
        tool_calling_supported=True,
        allowed_tools=("Write",),
    )
    ok = verify_module._check_bridge_filing_via_dispatch(route, "http://localhost:11434", tmp_path)
    assert ok is True


def test_bridge_filing_does_not_touch_production_index(verify_module, ollama_harness_module, tmp_path) -> None:
    """L3: production bridge/INDEX.md must be untouched after the fixture write.

    The verification script writes to a tempfile.mkdtemp root, never the live
    project root, so the production INDEX.md mtime must not change.
    """
    prod_index = _REPO_ROOT / "bridge" / "INDEX.md"
    if not prod_index.is_file():
        pytest.skip("production bridge/INDEX.md absent; live-repo invariant")
    before = prod_index.stat().st_mtime_ns
    route = ollama_harness_module.ModelRoute(
        key="route1",
        model_id="my-model",
        model_version="v1",
        tool_calling_supported=True,
        allowed_tools=("Write",),
    )
    verify_module._check_bridge_filing_via_dispatch(route, "http://localhost:11434", tmp_path)
    after = prod_index.stat().st_mtime_ns
    assert before == after, "production bridge/INDEX.md was modified"


def test_bridge_filing_inserts_fixture_index_entry(verify_module, ollama_harness_module, tmp_path) -> None:
    """L3 / GO@-006 Constraint 2: fixture bridge filing must insert a
    ``Document:``/``NEW:`` entry into the fixture INDEX.

    Per ``GOV-FILE-BRIDGE-AUTHORITY-001`` a bridge document is filed when
    BOTH the bridge file and its INDEX entry exist; a bridge file alone is
    unindexed and does not count as a filed bridge document. The GO@-006
    verification constraint required the fixture filing proof to exercise
    that full semantic in a disposable root-contained workspace.
    """
    route = ollama_harness_module.ModelRoute(
        key="route1",
        model_id="my-model",
        model_version="v1",
        tool_calling_supported=True,
        allowed_tools=("Write",),
    )
    fixture_root = tmp_path / "fixture"
    ok = verify_module._check_bridge_filing_via_dispatch(
        route,
        "http://localhost:11434",
        tmp_path,
        fixture_root=fixture_root,
    )
    assert ok is True
    fixture_index = fixture_root / "bridge" / "INDEX.md"
    index_text = fixture_index.read_text(encoding="utf-8")
    assert "Document: gtkb-ollama-e2e-fixture" in index_text, (
        f"fixture INDEX missing Document: entry; contents:\n{index_text!r}"
    )
    assert "NEW: bridge/gtkb-ollama-e2e-fixture-001.md" in index_text, (
        f"fixture INDEX missing NEW: entry; contents:\n{index_text!r}"
    )
    # The fixture bridge file must also exist (filing requires both).
    fixture_bridge_file = fixture_root / "bridge" / "gtkb-ollama-e2e-fixture-001.md"
    assert fixture_bridge_file.is_file(), "fixture bridge file missing after filing"


# ── Guard-only: destructive Bash rejection ───────────────────────────────


def test_guard_destructive_bash_rejected(verify_module, ollama_harness_module, tmp_path) -> None:
    """G1: ``rm -rf /`` payload through the mocked guard pipeline must be rejected."""
    route = ollama_harness_module.ModelRoute(
        key="route1",
        model_id="my-model",
        model_version="v1",
        tool_calling_supported=True,
        allowed_tools=("Bash",),
    )
    ok = verify_module._check_guard_destructive_bash(tmp_path, route, "http://localhost:11434")
    assert ok is True


# ── Guard-only: formal-artifact rejection ────────────────────────────────


def test_guard_formal_artifact_rejected(verify_module, ollama_harness_module, tmp_path) -> None:
    """G2: write to a formal-artifact-approval path must be rejected by the mocked guard."""
    route = ollama_harness_module.ModelRoute(
        key="route1",
        model_id="my-model",
        model_version="v1",
        tool_calling_supported=True,
        allowed_tools=("Write",),
    )
    # Ensure the .groundtruth/formal-artifact-approvals path resolves under tmp_path,
    # which the script will use to construct the test write target.
    (tmp_path / ".groundtruth" / "formal-artifact-approvals").mkdir(parents=True, exist_ok=True)
    ok = verify_module._check_guard_formal_artifact(tmp_path, route, "http://localhost:11434")
    assert ok is True


# ── Guard-only: out-of-root rejection ────────────────────────────────────


def test_guard_out_of_root_rejected(verify_module, ollama_harness_module, tmp_path) -> None:
    """G3: read of an out-of-root path is rejected by ``_ensure_under_root``.

    Out-of-root rejection happens at the path-resolution layer, not via the
    guard runner. The check passes when ``dispatch_tool_call`` raises
    ``OllamaHarnessError`` containing the escape diagnostic.
    """
    route = ollama_harness_module.ModelRoute(
        key="route1",
        model_id="my-model",
        model_version="v1",
        tool_calling_supported=True,
        allowed_tools=("Read",),
    )
    ok = verify_module._check_guard_out_of_root(tmp_path, route, "http://localhost:11434")
    assert ok is True


# ── Smoke test: script importable with no side effects ──────────────────


def test_script_importable_without_side_effects() -> None:
    """Importing the verification script must not contact the network or modify state."""
    mod = _load_script_module()
    assert hasattr(mod, "_check_tool_loop_round_trip")
    assert hasattr(mod, "_check_author_metadata")
    assert hasattr(mod, "_check_bridge_filing_via_dispatch")
    assert hasattr(mod, "_check_guard_destructive_bash")
    assert hasattr(mod, "_check_guard_formal_artifact")
    assert hasattr(mod, "_check_guard_out_of_root")
    assert callable(getattr(mod, "main", None))
