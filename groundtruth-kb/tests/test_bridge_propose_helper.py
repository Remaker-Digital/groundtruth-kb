# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for the governed bridge-propose helper."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
HELPER_PATH = PROJECT_ROOT / ".claude" / "skills" / "bridge-propose" / "helpers" / "write_bridge.py"


def _load_helper() -> ModuleType:
    module_name = "gtkb_test_bridge_propose_helper"
    cached = sys.modules.get(module_name)
    if cached is not None:
        return cached
    spec = importlib.util.spec_from_file_location(module_name, HELPER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(autouse=True)
def _work_intent_session_env(monkeypatch: pytest.MonkeyPatch) -> None:
    helper = _load_helper()
    for name in helper.WORK_INTENT_SESSION_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("CODEX_THREAD_ID", "gtkb-template-helper-test-session")


def _synthetic_ar_live_key() -> str:
    return "ar" + "_live_" + "TESTTOKEN123456"


def _synthetic_aws_key() -> str:
    return "AK" + "IA" + "ABCDEFGHIJKLMNOP"


def _proposal_body(text: str) -> str:
    return "\n".join(
        [
            text,
            "",
            "## Specification Links",
            "- SPEC-TEST-BRIDGE-PROPOSE-001",
            "- .claude/rules/file-bridge-protocol.md",
            "",
        ]
    )


def test_scan_allows_pii_only_samples() -> None:
    helper = _load_helper()
    assert helper.scan_credential_hits("Contact support@example.com for details.") == []
    assert helper.scan_credential_hits("Call +15551234567 or +442012345678.") == []


def test_scan_detects_credential_shapes() -> None:
    helper = _load_helper()
    hits = helper.scan_credential_hits(f"Key: {_synthetic_ar_live_key()} AWS: {_synthetic_aws_key()}")
    names = {hit["pattern_name"] for hit in hits}
    assert "ar_live_key" in names
    assert "aws_key" in names


def test_redact_residual_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    helper = _load_helper()
    body = f"key={_synthetic_ar_live_key()} end"
    hits = helper.scan_credential_hits(body)

    def _broken_redact(content: str, hits: list[dict[str, Any]]) -> str:  # noqa: ARG001
        return content

    monkeypatch.setattr(helper, "redact_credential_hits", _broken_redact)
    with pytest.raises(helper.RedactionResidualError):
        helper.handle_hits_abort_or_redact(body, hits, mode="redact")


def test_propose_bridge_writes_numbered_file(tmp_path: Path) -> None:
    helper = _load_helper()
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()

    body = _proposal_body("Clean proposal body with no credentials.")
    result_path = helper.propose_bridge(
        "clean-topic",
        body,
        mode="abort",
        bridge_dir=bridge_dir,
        pre_populate_prior_deliberations=False,
    )

    assert result_path == bridge_dir / "clean-topic-001.md"
    assert result_path.read_text(encoding="utf-8") == body


def test_propose_bridge_refuses_silent_overwrite(tmp_path: Path) -> None:
    helper = _load_helper()
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    target = bridge_dir / "occupied-topic-001.md"
    target.write_text("Previous content that must not be overwritten.", encoding="utf-8")

    with pytest.raises(helper.BridgeFileAlreadyExistsError):
        helper.propose_bridge(
            "occupied-topic",
            _proposal_body("New body that should not be written."),
            mode="abort",
            bridge_dir=bridge_dir,
            pre_populate_prior_deliberations=False,
        )

    assert target.read_text(encoding="utf-8") == "Previous content that must not be overwritten."


def test_propose_bridge_aborts_on_credential_hits(tmp_path: Path) -> None:
    helper = _load_helper()
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()

    body = _proposal_body(f"Forbidden content: {_synthetic_ar_live_key()}")
    with pytest.raises(helper.CredentialHitsFoundError):
        helper.propose_bridge(
            "abort-topic",
            body,
            mode="abort",
            bridge_dir=bridge_dir,
            pre_populate_prior_deliberations=False,
        )

    assert not (bridge_dir / "abort-topic-001.md").exists()


def test_propose_bridge_redacts_and_writes_when_clean_after_redaction(tmp_path: Path) -> None:
    helper = _load_helper()
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()

    synthetic = _synthetic_ar_live_key()
    result_path = helper.propose_bridge(
        "redact-topic",
        _proposal_body(f"Rotate {synthetic} and report."),
        mode="redact",
        bridge_dir=bridge_dir,
        pre_populate_prior_deliberations=False,
    )

    written = result_path.read_text(encoding="utf-8")
    assert synthetic not in written
    assert "[REDACTED:ar_live_key]" in written


def test_template_helper_exposes_work_intent_session_resolution() -> None:
    helper = _load_helper()
    env = {
        "GTKB_BRIDGE_POLLER_RUN_ID": "dispatch-session",
        "CLAUDE_SESSION_ID": "claude-session",
        "GTKB_INHERITED_SESSION_ID": "inherited-session",
        "CODEX_SESSION_ID": "codex-session",
        "CODEX_THREAD_ID": "codex-thread",
        "ANTIGRAVITY_SESSION_ID": "antigravity-session",
        "GTKB_SESSION_ID": "gtkb-session",
    }
    assert helper.resolve_work_intent_session_id(env) == "dispatch-session"

    for expected in (
        "claude-session",
        "inherited-session",
        "codex-session",
        "codex-thread",
        "antigravity-session",
        "gtkb-session",
    ):
        env.pop(next(iter(env)))
        assert helper.resolve_work_intent_session_id(env) == expected

    with pytest.raises(helper.BridgeWorkIntentError):
        helper.resolve_work_intent_session_id({})


def test_propose_bridge_acquires_and_releases_work_intent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    helper = _load_helper()
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()

    class _RecordingRegistry:
        def __init__(self) -> None:
            self.events: list[tuple[Any, ...]] = []

        def current_holder(self, thread_slug: str, *, project_root: Path) -> None:
            self.events.append(("current_holder", thread_slug, project_root))
            return None

        def acquire(self, thread_slug: str, session_id: str, ttl_seconds: int, *, project_root: Path) -> bool:
            self.events.append(("acquire", thread_slug, session_id, ttl_seconds, project_root))
            return True

        def release(self, thread_slug: str, session_id: str, *, project_root: Path) -> None:
            self.events.append(("release", thread_slug, session_id, project_root))

    fake_registry = _RecordingRegistry()
    monkeypatch.setenv("CLAUDE_SESSION_ID", "template-session")
    monkeypatch.setattr(helper, "_load_work_intent_registry", lambda project_root: fake_registry)

    result = helper.propose_bridge(
        "template-work-intent-topic",
        _proposal_body("Template work-intent body."),
        mode="abort",
        bridge_dir=bridge_dir,
        pre_populate_prior_deliberations=False,
    )

    assert result.exists()
    assert fake_registry.events == [
        ("current_holder", "template-work-intent-topic", tmp_path.resolve()),
        ("acquire", "template-work-intent-topic", "template-session", 300, tmp_path.resolve()),
        ("release", "template-work-intent-topic", "template-session", tmp_path.resolve()),
    ]
