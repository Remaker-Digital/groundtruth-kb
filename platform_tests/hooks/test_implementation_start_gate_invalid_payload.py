"""W0.3 item 3: implementation-start-gate invalid-payload fail-open.

Empty/unparseable PreToolUse payloads are infrastructure faults, not policy
violations: the gate fails OPEN and appends a warning record to the denial log
(pattern_id=invalid-payload-fail-open). Parseable protected-target mutations
without a GO still BLOCK and name the resolved target.

Authority: bridge/gtkb-w0-gate-false-positive-repair-001.md item 3 (GO at -002);
GOV-17.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, _ROOT / rel)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_GATE = _load("impl_start_gate_under_test", "scripts/implementation_start_gate.py")


def test_empty_payload_fails_open_with_log_record(tmp_path: Path) -> None:
    import os

    log = tmp_path / "gate-denials.jsonl"
    os.environ["GTKB_GATE_DENIALS_PATH"] = str(log)
    result = _GATE.gate_decision({_GATE.PAYLOAD_FAIL_OPEN_KEY: "Hook input was empty."})
    assert result["decision"] == "allow"
    records = [json.loads(l) for l in log.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert any(r["pattern_id"] == "invalid-payload-fail-open" for r in records)


def test_malformed_json_fails_open(tmp_path: Path) -> None:
    import os

    log = tmp_path / "gate-denials.jsonl"
    os.environ["GTKB_GATE_DENIALS_PATH"] = str(log)
    result = _GATE.gate_decision({_GATE.PAYLOAD_FAIL_OPEN_KEY: "Hook input was malformed JSON"})
    assert result["decision"] == "allow"


def test_parseable_invalid_shape_keeps_fail_closed() -> None:
    result = _GATE.gate_decision({_GATE.INVALID_HOOK_PAYLOAD_KEY: "Hook input must be a non-empty JSON object."})
    assert result["decision"] == "block"
    assert result["reason_code"] == "invalid_hook_payload"
