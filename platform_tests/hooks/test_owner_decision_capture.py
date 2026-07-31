"""Focused WI-5118 regressions for completed AUQ startup-gate acknowledgement."""

from __future__ import annotations

import importlib.util
import io
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK_PATH = REPO_ROOT / ".claude" / "hooks" / "owner-decision-capture.py"
TEMPLATE_PATH = REPO_ROOT / "groundtruth-kb" / "templates" / "hooks" / "owner-decision-capture.py"


def _load_hook():
    hooks_dir = str(HOOK_PATH.parent)
    if hooks_dir not in sys.path:
        sys.path.insert(0, hooks_dir)
    spec = importlib.util.spec_from_file_location("owner_decision_capture_under_test", HOOK_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_completed_auq_acknowledges_only_the_session_id(monkeypatch, capsys) -> None:
    module = _load_hook()
    acknowledgements: list[object] = []
    archived: list[dict[str, object]] = []
    payload = {
        "tool_name": "AskUserQuestion",
        "session_id": "12a16794-f84d-457f-81b4-8e803034e4d5",
        "tool_input": {"questions": [{"question": "Approve the change?"}]},
        "tool_result": {"answers": {"approval": "yes"}},
    }

    monkeypatch.setattr(module, "_acknowledge_completed_auq", acknowledgements.append)
    monkeypatch.setattr(module, "insert_deliberation", lambda **kwargs: archived.append(kwargs))
    monkeypatch.setattr(module.sys, "stdin", io.StringIO(json.dumps(payload)))

    assert module.main() == 0
    assert acknowledgements == [payload["session_id"]]
    assert archived[0]["session_id"] == payload["session_id"]
    assert json.loads(capsys.readouterr().out) == {}


def test_incomplete_auq_does_not_acknowledge_or_archive(monkeypatch) -> None:
    module = _load_hook()
    acknowledgements: list[object] = []
    archived: list[dict[str, object]] = []
    payload = {
        "tool_name": "AskUserQuestion",
        "session_id": "12a16794-f84d-457f-81b4-8e803034e4d5",
        "tool_input": {"questions": [{"question": "Approve the change?"}]},
        "tool_result": {},
    }

    monkeypatch.setattr(module, "_acknowledge_completed_auq", acknowledgements.append)
    monkeypatch.setattr(module, "insert_deliberation", lambda **kwargs: archived.append(kwargs))
    monkeypatch.setattr(module.sys, "stdin", io.StringIO(json.dumps(payload)))

    assert module.main() == 0
    assert acknowledgements == []
    assert archived == []


def test_owner_decision_capture_template_stays_byte_identical() -> None:
    assert HOOK_PATH.read_text(encoding="utf-8") == TEMPLATE_PATH.read_text(encoding="utf-8")
