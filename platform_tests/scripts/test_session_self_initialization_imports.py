"""Regression guards for ``session_self_initialization.py`` import + encoding fix.

Per ``bridge/gtkb-startup-evidence-restoration-001.md`` (REVISED-1 GO at
``-002``): two regression guards required.

1. Importlib load succeeds without ``scripts/`` on ``sys.path``.
2. Module load + hook-context emit succeed when ``sys.stdout`` has a
   non-UTF-8 encoding (cp1252 simulation; cross-platform via stream
   substitution per Codex GO -002 condition 5).

These tests are kept in a dedicated file so the existing
``tests/scripts/test_session_self_initialization.py`` remains intact.
"""

from __future__ import annotations

import importlib.util
import io
import sys
from pathlib import Path
from unittest.mock import patch

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT_PATH = _REPO_ROOT / "scripts" / "session_self_initialization.py"


def _load_module_with_unique_name(unique_suffix: str):
    """Load session_self_initialization.py via importlib with a unique
    module name so each test gets a fresh module without collision.

    Clears ``_wrap_io`` from sys.modules pre-load so the conditional
    sys.path insert is exercised; restores it post-load to avoid
    contaminating other tests.
    """
    saved_wrap_io = sys.modules.pop("_wrap_io", None)
    spec = importlib.util.spec_from_file_location(f"session_self_initialization_test_{unique_suffix}", _SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    finally:
        if saved_wrap_io is not None and "_wrap_io" not in sys.modules:
            sys.modules["_wrap_io"] = saved_wrap_io
    return module


def test_module_loads_via_importlib_without_scripts_on_sys_path() -> None:
    """Importlib load succeeds even when ``scripts/`` is absent from sys.path.

    This is the primary regression guard for the P1 finding: prior to
    the fix, all 33 tests in test_session_self_initialization.py failed
    with ModuleNotFoundError at the bare ``from _wrap_io`` import.
    """
    saved_path = sys.path[:]
    try:
        scripts_dir = str(_REPO_ROOT / "scripts")
        sys.path = [p for p in saved_path if p != scripts_dir]
        # Module load must succeed without ModuleNotFoundError.
        module = _load_module_with_unique_name("isolated_load")
        # Sanity check: _atomic_write_text imported via the conditional-path block.
        assert hasattr(module, "_atomic_write_text")
    finally:
        sys.path = saved_path


def test_sys_path_insert_is_idempotent_on_repeated_load() -> None:
    """Repeated importlib loads do not duplicate the scripts dir in sys.path.

    Per Codex GO -002 condition 1 (Insert only if not already present).
    """
    pre_count_in_path = sum(1 for p in sys.path if p == str(_REPO_ROOT / "scripts"))
    _load_module_with_unique_name("idempotency_a")
    _load_module_with_unique_name("idempotency_b")
    _load_module_with_unique_name("idempotency_c")
    post_count_in_path = sum(1 for p in sys.path if p == str(_REPO_ROOT / "scripts"))
    # Should be the same — at most one entry, regardless of load count.
    assert post_count_in_path == pre_count_in_path or post_count_in_path == 1


def test_module_load_succeeds_with_cp1252_stdout() -> None:
    """Module load succeeds even when sys.stdout has a non-UTF-8 encoding.

    Substitutes stdout with a cp1252-encoded TextIOWrapper before load,
    then loads the module. The top-of-module reconfigure block must
    convert the stream to UTF-8 so subsequent non-ASCII emits succeed.

    Per Codex GO -002 condition 5: regression guard for cp1252-like
    stdout using a controlled text stream; cross-platform.
    """
    cp1252_stream = io.TextIOWrapper(io.BytesIO(), encoding="cp1252", errors="strict", write_through=True)
    with patch.object(sys, "stdout", cp1252_stream):
        # Module load must not raise; reconfigure handles the encoding.
        module = _load_module_with_unique_name("cp1252_load")
        # Verify reconfigure ran: stdout encoding is now utf-8.
        assert sys.stdout.encoding.lower() == "utf-8"
        # Sanity check: hook-context emit with non-ASCII does not raise.
        module._emit_hook_context("test ★ insight ─ marker")


def test_emit_hook_context_emits_valid_json_with_non_ascii() -> None:
    """The hook-context output is valid JSON containing non-ASCII payload.

    Per Codex GO -002 condition 6: encoding mitigation must cover line ~4900
    `_emit_hook_context` path. This test exercises that path end-to-end.
    """
    import json

    module = _load_module_with_unique_name("json_emit")
    captured = io.StringIO()
    with patch.object(sys, "stdout", captured):
        module._emit_hook_context("test ★ insight ─ marker")
    output = captured.getvalue().strip()
    parsed = json.loads(output)
    assert "additionalContext" in parsed
    # Non-ASCII chars round-trip correctly.
    assert "★" in parsed["additionalContext"]
    assert "─" in parsed["additionalContext"]
