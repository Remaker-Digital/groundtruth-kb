# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""WI-5083: _SESSION_CONTINUATION_SOURCES is intentionally duplicated (not
imported) across the SessionStart hot-path modules. This parity test asserts
the copies stay equal (mirrors the _SESSION_ROLE_MARKER_NAME parity contract)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EXPECTED = frozenset({"resume", "compact"})


def _load(name: str, rel: str):
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / rel)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_session_continuation_sources_parity():
    wf = _load("workstream_focus", "scripts/workstream_focus.py")
    ssi = _load("session_self_initialization", "scripts/session_self_initialization.py")
    assert wf._SESSION_CONTINUATION_SOURCES == EXPECTED
    assert ssi._SESSION_CONTINUATION_SOURCES == EXPECTED
    # Codex hook read textually to avoid its module-load side effects.
    codex_src = (REPO_ROOT / ".codex/gtkb-hooks/session_wrapup_trigger_dispatch.py").read_text(encoding="utf-8")
    assert '_SESSION_CONTINUATION_SOURCES = frozenset({"resume", "compact"})' in codex_src
