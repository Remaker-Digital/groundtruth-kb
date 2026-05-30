"""Tests for groundtruth_kb.owner_decision.auto_archive (Slice 4).

Covers the deterministic classifier and the in-process integration with
the Slice 1 ``record_deliberation`` service. Patches the service in tests
that exercise ``archive_decision()`` so the unit tests are independent of
MemBase state. A separate Slice 1 test exercises the real service.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
from groundtruth_kb.owner_decision import (
    DecisionForArchive,
    archive_decision,
    should_auto_archive,
)


def _in_scope_decision() -> DecisionForArchive:
    return DecisionForArchive(
        decision_id="DECISION-0001",
        question="Which continuation track should this session pursue?",
        options=("Track A", "Track B", "Track C"),
        answer="Track B",
        resolved_at="2026-05-30T15:30:00Z",
        session_id="S373",
        detected_via="ask_user_question",
    )


def test_in_scope_resolved_decision_archives(tmp_path: Path) -> None:
    decision = _in_scope_decision()

    captured: dict[str, Any] = {}

    def fake_record(_config: Any, request: Any) -> dict[str, Any]:
        captured["request"] = request
        return {"id": "DELIB-9999", "status": "created"}

    with (
        patch(
            "groundtruth_kb.cli_deliberations_record.record_deliberation",
            new=fake_record,
        ),
        patch(
            "groundtruth_kb.config.GTConfig.load",
            return_value=object(),
        ),
    ):
        result = archive_decision(decision, project_root=tmp_path)

    assert result["id"] == "DELIB-9999"
    request = captured["request"]
    assert request.source_type == "owner_conversation"
    assert request.outcome == "owner_decision"
    assert request.auq_id == decision.decision_id
    assert request.source_ref == decision.decision_id
    assert request.auq_answer == decision.answer


def test_unresolved_decision_skipped() -> None:
    decision = replace(_in_scope_decision(), resolved_at="")
    ok, reason = should_auto_archive(decision)
    assert ok is False
    assert reason == "unresolved"


def test_out_of_scope_answer_skipped() -> None:
    for answer in ("Tool loaded.", "ack", "OK", "Thanks"):
        decision = replace(_in_scope_decision(), answer=answer)
        ok, reason = should_auto_archive(decision)
        assert ok is False, f"answer {answer!r} should be out-of-scope"
        assert reason == "out-of-scope content"


def test_non_auq_decision_skipped() -> None:
    decision = replace(_in_scope_decision(), detected_via="prose_pattern")
    ok, reason = should_auto_archive(decision)
    assert ok is False
    assert reason == "not an AUQ"


def test_idempotency_same_decision_id_no_double_archive(tmp_path: Path) -> None:
    decision = _in_scope_decision()

    call_log: list[Any] = []

    def fake_record(_config: Any, request: Any) -> dict[str, Any]:
        call_log.append(request)
        return {"id": "DELIB-9999", "status": "existing"}

    fake_config_cls = type("FakeConfig", (), {"load": staticmethod(lambda: object())})

    with (
        patch(
            "groundtruth_kb.cli_deliberations_record.record_deliberation",
            new=fake_record,
        ),
        patch(
            "groundtruth_kb.config.GTConfig.load",
            return_value=fake_config_cls,
        ),
    ):
        first = archive_decision(decision, project_root=tmp_path)
        second = archive_decision(decision, project_root=tmp_path)

    assert first["id"] == second["id"] == "DELIB-9999"
    assert len(call_log) == 2
    assert call_log[0].source_ref == call_log[1].source_ref == decision.decision_id


def test_classification_is_deterministic() -> None:
    decision = _in_scope_decision()
    results = {should_auto_archive(decision) for _ in range(50)}
    assert results == {(True, "in-scope owner decision")}


def test_archive_decision_uses_record_deliberation_service(tmp_path: Path) -> None:
    decision = _in_scope_decision()

    captured_calls: list[Any] = []

    def fake_record(_config: Any, request: Any) -> dict[str, Any]:
        captured_calls.append(request)
        assert request.content_file.exists(), "service must observe body file"
        assert request.owner_presented is True
        assert request.outcome == "owner_decision"
        assert request.source_type == "owner_conversation"
        return {"id": "DELIB-1234"}

    fake_config_cls = type("FakeConfig", (), {"load": staticmethod(lambda: object())})

    with (
        patch(
            "groundtruth_kb.cli_deliberations_record.record_deliberation",
            new=fake_record,
        ),
        patch(
            "groundtruth_kb.config.GTConfig.load",
            return_value=fake_config_cls,
        ),
    ):
        result = archive_decision(decision, project_root=tmp_path)

    assert result["id"] == "DELIB-1234"
    assert len(captured_calls) == 1


def test_helper_module_imports_no_llm_library() -> None:
    import sys

    forbidden_prefixes = (
        "chromadb",
        "openai",
        "anthropic",
        "transformers",
        "sentence_transformers",
        "tiktoken",
    )

    pre_import_modules = set(sys.modules)
    import groundtruth_kb.owner_decision.auto_archive as auto_archive_module  # noqa: F401

    new_modules = set(sys.modules) - pre_import_modules
    for name in new_modules:
        for prefix in forbidden_prefixes:
            assert not name.startswith(prefix), f"helper transitively imported forbidden LLM module {name!r}"


def test_empty_answer_skipped() -> None:
    decision = replace(_in_scope_decision(), answer="")
    ok, reason = should_auto_archive(decision)
    assert ok is False
    assert reason == "empty answer"


def test_archive_decision_requires_project_root() -> None:
    """Slice 4 NO-GO -007 F1 fix: archive_decision rejects implicit cwd resolution.

    Without an explicit project_root, the helper would silently use Path.cwd()
    and potentially write into a live GT-KB checkout. The post-fix contract is
    explicit: project_root is required.
    """
    decision = _in_scope_decision()
    with pytest.raises(ValueError, match="explicit project_root"):
        archive_decision(decision)


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
