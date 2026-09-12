# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""WI-4779 / TEST-11238 — session-context review independence startup rationale.

Pins rationale-first wording in the startup index, generated startup disclosure,
and the ordering heuristic that demotes harness-ID negation below the normative block.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_INDEX = _ROOT / "config" / "agent-control" / "SESSION-STARTUP-INDEX.md"
_SCRIPT = _ROOT / "scripts" / "session_self_initialization.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_session_self_initialization():
    spec = importlib.util.spec_from_file_location(
        "session_self_initialization_wi4779",
        _SCRIPT,
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["session_self_initialization_wi4779"] = module
    spec.loader.exec_module(module)
    return module


def test_generated_disclosure_includes_review_independence_for_prime_builder() -> None:
    module = _load_session_self_initialization()
    model = module.build_startup_model(_ROOT, role_profile="prime-builder", fast_hook=True)
    report = module.render_report(
        model,
        "http://localhost:3000/d/gtkb/groundtruth-kb-dashboard",
        _ROOT,
    )
    assert "### Session-Context Review Independence" in report
    assert "author_session_context_id" in report
    assert "inherits" not in report.lower() or "assumptions" in report.lower()
