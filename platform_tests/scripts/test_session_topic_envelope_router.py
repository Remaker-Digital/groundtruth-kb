"""Spec-derived tests for the Claude ::open/::close topic-envelope router
(WI-4891, Slice 5 of PROJECT-GTKB-CROSS-HARNESS-PARITY — first conformance case).

Verifies:

- **ADR-CROSS-HARNESS-PARITY-001 Q1 (behavioral routing):** the Claude adapter
  ``.claude/hooks/session-topic-envelope-router.py`` routes a ``::open <type>``
  prompt through the shared ``groundtruth_kb.session.topic_router`` and emits a
  ``hookSpecificOutput.additionalContext`` payload; non-topic prompts and the
  startup-input gate emit no context.
- **PARITY-DIFF-EXISTS / advisory §6 criterion 1 (diff green):** after the
  Claude adapter is registered in ``.claude/settings.json`` and the registry,
  the Slice-3 discovery-diff no longer reports the
  ``session_wrapup_trigger_dispatch`` / ``hook.session-topic-envelope-routing``
  asymmetry.

The hook-routing tests monkeypatch the envelope runtime
(``handle_topic_command`` / ``render_topic_context``) so they stay hermetic; the
discovery-diff test reads the live tree.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import importlib.util
import io
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK_PATH = REPO_ROOT / ".claude" / "hooks" / "session-topic-envelope-router.py"
_SCRIPTS = REPO_ROOT / "scripts"
_GT_SRC = REPO_ROOT / "groundtruth-kb" / "src"
for _extra in (str(_SCRIPTS), str(_GT_SRC)):
    if _extra not in sys.path:
        sys.path.insert(0, _extra)


def _load_hook() -> ModuleType:
    spec = importlib.util.spec_from_file_location("claude_topic_envelope_router", HOOK_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _valid_topic_type() -> str:
    from groundtruth_kb.session.envelope import TOPIC_TYPES

    return sorted(TOPIC_TYPES)[0]


def _run_main(hook: ModuleType, prompt: str, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture) -> dict:
    monkeypatch.setattr("sys.stdin", io.StringIO(prompt))
    rc = hook.main()
    assert rc == 0
    out = capsys.readouterr().out.strip()
    return json.loads(out)


def test_non_topic_prompt_emits_no_context(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture) -> None:
    hook = _load_hook()
    payload = _run_main(hook, "Please continue the task as normal.", monkeypatch, capsys)
    assert payload == {}


def test_topic_open_emits_additional_context(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture) -> None:
    hook = _load_hook()
    monkeypatch.setattr(hook, "handle_topic_command", lambda *a, **k: {"action": "open"})
    monkeypatch.setattr(hook, "render_topic_context", lambda result: "RENDERED-TOPIC-CONTEXT")
    payload = _run_main(hook, f"::open {_valid_topic_type()}", monkeypatch, capsys)
    assert payload["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"
    assert payload["hookSpecificOutput"]["additionalContext"] == "RENDERED-TOPIC-CONTEXT"


def test_startup_gate_suppresses_routing(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture, tmp_path: Path
) -> None:
    guard = tmp_path / "session-lifecycle-guard.json"
    guard.write_text(json.dumps({"discard_next_user_prompt": True}), encoding="utf-8")
    monkeypatch.setenv("GTKB_LIFECYCLE_GUARD_PATH", str(guard))
    hook = _load_hook()
    # Even a valid topic command is suppressed while the startup gate is active.
    payload = _run_main(hook, f"::open {_valid_topic_type()}", monkeypatch, capsys)
    assert payload == {}


def test_envelope_error_emits_bounded_failure(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture) -> None:
    hook = _load_hook()
    from groundtruth_kb.session.envelope import EnvelopeError

    def _raise(*_a, **_k):
        raise EnvelopeError("synthetic envelope failure")

    monkeypatch.setattr(hook, "handle_topic_command", _raise)
    payload = _run_main(hook, f"::open {_valid_topic_type()}", monkeypatch, capsys)
    assert "Topic Envelope Command Failed" in payload["hookSpecificOutput"]["additionalContext"]


# --- Discovery-diff green (PARITY-DIFF-EXISTS / advisory §6.1) -----------------


def test_discovery_diff_no_longer_reports_open_asymmetry() -> None:
    import parity_discovery_diff as diff

    report = diff.run_discovery_diff(REPO_ROOT)
    offending = {
        f.capability_key
        for f in report.findings
        if f.capability_key in {"hook:session_wrapup_trigger_dispatch", "hook.session-topic-envelope-routing"}
    }
    assert not offending, f"::open conformance asymmetry still reported: {offending}"
