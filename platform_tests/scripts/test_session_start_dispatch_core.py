# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for scripts/session_start_dispatch_core.py — WI-4564 Part A.

Part A of the WI-4564 startup-service timeout alignment (bridge thread
``gtkb-wi4564-startup-service-timeout-and-fanout``, GO at -004) makes the inner
subprocess timeout env-configurable and raises its default so the inner bound
no longer fires ~3.6x short of the 180 s ``asyncTimeout`` the SessionStart hook
allows. These spec-derived tests cover the resolver
``_startup_service_timeout_seconds`` and the budget-aligned default.

Spec linkage (per the GO'd proposal -003 verification plan):
- GOV-RELIABILITY-FAST-LANE-001 / PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001:
  the timeout resolves from ``GTKB_STARTUP_SERVICE_TIMEOUT_SECONDS`` when set
  and falls back to the raised 150.0 default when unset/invalid/non-positive.
"""

from __future__ import annotations

import importlib.util
import io
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "session_start_dispatch_core.py"


def _load_module():
    # The core module imports in-root ``scripts.*`` helpers, so REPO_ROOT must
    # be importable as the ``scripts`` package parent.
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    spec = importlib.util.spec_from_file_location("session_start_dispatch_core", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["session_start_dispatch_core"] = module
    spec.loader.exec_module(module)
    return module


def test_timeout_env_name_and_default_constant() -> None:
    """The env var name is canonical and the default is the raised 150.0 budget."""

    module = _load_module()
    assert module.STARTUP_SERVICE_TIMEOUT_ENV == "GTKB_STARTUP_SERVICE_TIMEOUT_SECONDS"
    # Raised from the prior 50.0 to ~30 s under the 180 s asyncTimeout budget.
    assert module.STARTUP_SERVICE_TIMEOUT_SECONDS == 150.0


def test_timeout_falls_back_to_default_when_unset(monkeypatch) -> None:
    module = _load_module()
    monkeypatch.delenv(module.STARTUP_SERVICE_TIMEOUT_ENV, raising=False)
    assert module._startup_service_timeout_seconds() == pytest.approx(150.0)


def test_timeout_reads_env_when_set(monkeypatch) -> None:
    module = _load_module()
    monkeypatch.setenv(module.STARTUP_SERVICE_TIMEOUT_ENV, "200")
    assert module._startup_service_timeout_seconds() == pytest.approx(200.0)


def test_harness_timeout_keeps_codex_default(monkeypatch) -> None:
    module = _load_module()
    monkeypatch.delenv(module.STARTUP_SERVICE_TIMEOUT_ENV, raising=False)
    monkeypatch.setattr(module, "HARNESS_NAME", "codex")

    assert module._startup_service_timeout_seconds_for_harness() == pytest.approx(150.0)


def test_harness_timeout_caps_claude_default(monkeypatch) -> None:
    module = _load_module()
    monkeypatch.delenv(module.STARTUP_SERVICE_TIMEOUT_ENV, raising=False)
    monkeypatch.setattr(module, "HARNESS_NAME", "claude")

    assert module._startup_service_timeout_seconds_for_harness() == pytest.approx(55.0)


def test_harness_timeout_caps_claude_env_above_hook_budget(monkeypatch) -> None:
    module = _load_module()
    monkeypatch.setenv(module.STARTUP_SERVICE_TIMEOUT_ENV, "200")
    monkeypatch.setattr(module, "HARNESS_NAME", "claude")

    assert module._startup_service_timeout_seconds_for_harness() == pytest.approx(55.0)


def test_harness_timeout_honors_claude_env_below_hook_budget(monkeypatch) -> None:
    module = _load_module()
    monkeypatch.setenv(module.STARTUP_SERVICE_TIMEOUT_ENV, "45")
    monkeypatch.setattr(module, "HARNESS_NAME", "claude")

    assert module._startup_service_timeout_seconds_for_harness() == pytest.approx(45.0)


def test_timeout_reads_fractional_env(monkeypatch) -> None:
    module = _load_module()
    monkeypatch.setenv(module.STARTUP_SERVICE_TIMEOUT_ENV, "75.5")
    assert module._startup_service_timeout_seconds() == pytest.approx(75.5)


def test_timeout_invalid_value_falls_back(monkeypatch) -> None:
    module = _load_module()
    monkeypatch.setenv(module.STARTUP_SERVICE_TIMEOUT_ENV, "not-a-number")
    assert module._startup_service_timeout_seconds() == pytest.approx(150.0)


def test_timeout_blank_value_falls_back(monkeypatch) -> None:
    module = _load_module()
    monkeypatch.setenv(module.STARTUP_SERVICE_TIMEOUT_ENV, "   ")
    assert module._startup_service_timeout_seconds() == pytest.approx(150.0)


@pytest.mark.parametrize("value", ["0", "-5", "-0.1"])
def test_timeout_non_positive_falls_back(monkeypatch, value) -> None:
    """A non-positive override is rejected so the wait is never zero/negative."""

    module = _load_module()
    monkeypatch.setenv(module.STARTUP_SERVICE_TIMEOUT_ENV, value)
    assert module._startup_service_timeout_seconds() == pytest.approx(150.0)


def test_read_session_start_source_extracts_source(monkeypatch) -> None:
    module = _load_module()
    stream = io.StringIO(json.dumps({"source": "resume", "hook_event_name": "SessionStart"}))
    stream.isatty = lambda: False  # type: ignore[method-assign]
    monkeypatch.setattr(module.sys, "stdin", stream)
    assert module._read_session_start_source() == "resume"


def test_read_session_start_source_none_when_source_absent(monkeypatch) -> None:
    module = _load_module()
    stream = io.StringIO(json.dumps({"hook_event_name": "SessionStart"}))
    stream.isatty = lambda: False  # type: ignore[method-assign]
    monkeypatch.setattr(module.sys, "stdin", stream)
    assert module._read_session_start_source() is None


def test_read_session_start_source_none_on_tty_or_empty(monkeypatch) -> None:
    module = _load_module()
    tty = io.StringIO("")
    tty.isatty = lambda: True  # type: ignore[method-assign]
    monkeypatch.setattr(module.sys, "stdin", tty)
    assert module._read_session_start_source() is None
    empty = io.StringIO("")
    empty.isatty = lambda: False  # type: ignore[method-assign]
    monkeypatch.setattr(module.sys, "stdin", empty)
    assert module._read_session_start_source() is None


def test_read_session_start_source_none_on_bad_json(monkeypatch) -> None:
    module = _load_module()
    bad = io.StringIO("not json{")
    bad.isatty = lambda: False  # type: ignore[method-assign]
    monkeypatch.setattr(module.sys, "stdin", bad)
    assert module._read_session_start_source() is None


def _fake_packet(kind: str, *, cap: int = 900, estimated: int = 80, status: str = "ready") -> dict[str, object]:
    packet: dict[str, object] = {
        "packet_kind": kind,
        "status": status,
        "budget": {
            "estimated_tokens": estimated,
            "cap_estimated_tokens": cap,
        },
        "cache": {
            "status": "miss",
            "cache_path": f".gtkb-state/session-envelope/packet-cache/{kind}.json",
        },
        "source_pointers": [],
    }
    if status == "over_budget_pointer_only":
        packet["diagnostic"] = {"pointer_only": True}
    return packet


def test_packet_receipt_precedes_activity_context_for_full_hook(monkeypatch) -> None:
    module = _load_module()
    calls: list[tuple[str, str, str | None]] = []

    def _fake_compose(*, packet_kind: str, role: str, activity: str | None = None) -> dict[str, object]:
        calls.append((packet_kind, role, activity))
        cap = 500 if packet_kind == "activity-packet" else 900
        return _fake_packet(packet_kind, cap=cap)

    monkeypatch.setattr(module, "HARNESS_NAME", "claude")
    monkeypatch.setattr(module, "_compose_session_envelope_packet", _fake_compose)

    rendered = module._with_envelope_packet_receipt("activity specialization body", role_mode="pb", activity="build")

    assert rendered.startswith("# GroundTruth-KB Envelope Packet Receipt")
    assert rendered.index("Envelope Packet Receipt") < rendered.index("activity specialization body")
    assert "- packet_injection_order: before_activity_specialization" in rendered
    assert "- hook_disposition: full_sessionstart_packet_injection" in rendered
    assert "- role_bootstrap: prime-builder" in rendered
    assert "- activity: build" in rendered
    assert "session_packet: status=ready; estimated_tokens=80; cap=900" in rendered
    assert "activity_packet: status=ready; estimated_tokens=80; cap=500" in rendered
    assert calls == [
        ("session-envelope", "prime-builder", None),
        ("activity-packet", "prime-builder", "build"),
    ]


def test_packet_receipt_marks_weak_hook_fallback_as_non_parity(monkeypatch) -> None:
    module = _load_module()
    monkeypatch.delenv(module._SESSION_ENVELOPE_ROLE_ENV, raising=False)
    monkeypatch.delenv(module._SESSION_ENVELOPE_ACTIVITY_ENV, raising=False)
    monkeypatch.delenv(module._DISPATCH_ACTIVITY_ENV, raising=False)

    def _fake_compose(*, packet_kind: str, role: str, activity: str | None = None) -> dict[str, object]:
        cap = 500 if packet_kind == "activity-packet" else 900
        return _fake_packet(packet_kind, cap=cap, status="over_budget_pointer_only")

    monkeypatch.setattr(module, "HARNESS_NAME", "cursor")
    monkeypatch.setattr(module, "_compose_session_envelope_packet", _fake_compose)

    rendered = module._with_envelope_packet_receipt("activity specialization body", role_mode="lo", activity="test")

    assert "- hook_disposition: fallback_receipt_pointer" in rendered
    assert "- fallback_is_parity: false" in rendered
    assert "- role_bootstrap: loyal-opposition" in rendered
    assert "- activity: test" in rendered
    assert "pointer_only=true" in rendered


def test_session_start_context_id_accepts_only_canonical_uuid() -> None:
    module = _load_module()
    session_id = "12a16794-f84d-457f-81b4-8e803034e4d5"

    assert module._session_start_context_id({"session_id": session_id.upper()}) == session_id
    assert module._session_start_context_id({"session_id": "not-a-session"}) is None
    assert module._session_start_context_id({"session_id": 42}) is None
    assert module._session_start_context_id({}) is None


def _run_normal_startup(module, monkeypatch, tmp_path, payload: dict[str, object]) -> dict[str, object]:
    from groundtruth_kb.mode_switch import pending

    captured: dict[str, object] = {}
    stream = io.StringIO(json.dumps(payload))
    stream.isatty = lambda: False  # type: ignore[method-assign]
    monkeypatch.setattr(module.sys, "stdin", stream)
    monkeypatch.setattr(module, "OUT_DIR", tmp_path / "out")
    monkeypatch.setattr(module, "HARNESS_NAME", "claude")
    monkeypatch.setattr(module, "_persistent_harness_id", lambda: "B")
    monkeypatch.setattr(module, "_invalidate_session_role_marker", lambda: None)
    monkeypatch.setattr(module, "_sweep_stale_per_session_role_markers", lambda **_kwargs: None)
    monkeypatch.setattr(pending, "apply_pending", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        module,
        "_bridge_dispatch_keyword_check",
        lambda: (module.StartupDecision.NORMAL_STARTUP, "normal"),
    )
    monkeypatch.setattr(module, "_valid_session_start_payload", lambda *_args: True)
    # WI-7318: the SessionStart path no longer writes a startup-disclosure relay
    # cache, so there are no cache writers left to stub here.

    def _fake_run(command, **kwargs):
        captured["command"] = command
        captured["env"] = kwargs["env"]
        return SimpleNamespace(
            returncode=0,
            stdout=json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "SessionStart",
                        "additionalContext": "startup",
                    }
                }
            ),
            stderr="",
        )

    monkeypatch.setattr(module.subprocess, "run", _fake_run)
    assert module.main() == 0
    return captured


def test_main_passes_valid_session_context_as_startup_guard_id(monkeypatch, tmp_path) -> None:
    module = _load_module()
    session_id = "12a16794-f84d-457f-81b4-8e803034e4d5"

    captured = _run_normal_startup(module, monkeypatch, tmp_path, {"source": "startup", "session_id": session_id})

    assert captured["env"]["GTKB_STARTUP_GUARD_ID"] == session_id
    assert captured["command"][-2:] == ["--session-start-source", "startup"]


@pytest.mark.parametrize("session_id", [None, "not-a-session", 42])
def test_main_drops_inherited_guard_id_without_valid_session_context(monkeypatch, tmp_path, session_id) -> None:
    module = _load_module()
    monkeypatch.setenv("GTKB_STARTUP_GUARD_ID", "inherited-other-session")
    payload: dict[str, object] = {"source": "startup"}
    if session_id is not None:
        payload["session_id"] = session_id

    captured = _run_normal_startup(module, monkeypatch, tmp_path, payload)

    assert "GTKB_STARTUP_GUARD_ID" not in captured["env"]
