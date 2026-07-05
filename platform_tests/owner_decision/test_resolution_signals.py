"""Tests for cross-session owner-decision resolution signals."""

from __future__ import annotations

import sys
from types import SimpleNamespace

from groundtruth_kb.owner_decision.resolution_signals import (
    RESOLVING_BRIDGE_STATUSES,
    extract_bridge_slugs,
    resolve_pending_entries,
)


def _entry(
    decision_id: str = "DECISION-1219",
    *,
    thread_ref: str = "",
    question: str = "Should Slice C continue?",
    notes: str = "",
) -> SimpleNamespace:
    return SimpleNamespace(id=decision_id, thread_ref=thread_ref, question=question, notes=notes)


def _resolve(entry: SimpleNamespace, rows: list[dict], statuses: dict[str, str | None]) -> dict:
    return resolve_pending_entries(
        [entry],
        deliberation_reader=lambda: rows,
        bridge_status_reader=lambda slug: statuses.get(slug),
    )


def test_exact_source_ref_owner_decision_resolves() -> None:
    rows = [
        {
            "id": "DELIB-DECISION-1219",
            "outcome": "owner_decision",
            "source_ref": "DECISION-1219",
            "summary": "Owner approved continuation.",
        }
    ]

    signals = _resolve(_entry(), rows, {})

    signal = signals["DECISION-1219"]
    assert signal.resolved_via == "cross_session_deliberation_resolution"
    assert "DELIB-DECISION-1219" in signal.answer


def test_mention_only_owner_decision_row_does_not_resolve() -> None:
    rows = [
        {
            "id": "DELIB-OTHER",
            "outcome": "owner_decision",
            "source_ref": "DECISION-9999",
            "summary": "Mentions DECISION-1219 while deciding another issue.",
            "content": "DECISION-1219 appears here only as background.",
        }
    ]

    signals = _resolve(_entry(), rows, {})

    assert signals == {}


def test_auq_id_owner_decision_resolves() -> None:
    rows = [
        {
            "id": "DELIB-AUQ",
            "outcome": "owner_decision",
            "source_ref": "",
            "auq_id": "DECISION-1219",
        }
    ]

    signals = _resolve(_entry(), rows, {})

    assert signals["DECISION-1219"].evidence_id == "DELIB-AUQ"


def test_bridge_status_matrix() -> None:
    for status in sorted(RESOLVING_BRIDGE_STATUSES):
        entry = _entry(thread_ref="bridge/gtkb-tafe-slice-c-ingestion-consolidated-004.md")
        signals = _resolve(entry, [], {"gtkb-tafe-slice-c-ingestion-consolidated": status})
        assert signals["DECISION-1219"].resolved_via == "cross_session_bridge_resolution"

    for status in ("NEW", "REVISED", "NO-GO", "ADVISORY", "DEFERRED"):
        entry = _entry(thread_ref="bridge/gtkb-tafe-slice-c-ingestion-consolidated-004.md")
        signals = _resolve(entry, [], {"gtkb-tafe-slice-c-ingestion-consolidated": status})
        assert signals == {}, status


def test_stale_generated_summary_text_alone_does_not_resolve() -> None:
    entry = _entry(
        question='Cached startup summary says "gtkb-tafe-slice-c-ingestion-consolidated is GO".',
        notes="No live bridge status is available.",
    )

    signals = _resolve(entry, [], {"gtkb-tafe-slice-c-ingestion-consolidated": None})

    assert signals == {}


def test_reader_failures_leave_entry_pending() -> None:
    entry = _entry(thread_ref="bridge/gtkb-tafe-slice-c-ingestion-consolidated-004.md")

    da_failed = resolve_pending_entries(
        [entry],
        deliberation_reader=lambda: (_ for _ in ()).throw(RuntimeError("db unavailable")),
        bridge_status_reader=lambda _slug: "GO",
    )

    bridge_failed = resolve_pending_entries(
        [entry],
        deliberation_reader=lambda: [],
        bridge_status_reader=lambda _slug: (_ for _ in ()).throw(RuntimeError("bridge unavailable")),
    )

    assert da_failed == {}
    assert bridge_failed == {}


def test_extracts_thread_ref_bridge_file_and_slug_tokens() -> None:
    entry = _entry(
        thread_ref="bridge/gtkb-direct-thread-003.md",
        question="See bridge/gtkb-question-thread-002.md for the active decision.",
        notes="Follow-up slug gtkb-notes-thread is exact and explicit.",
    )

    assert extract_bridge_slugs(entry) == (
        "gtkb-direct-thread",
        "gtkb-question-thread",
        "gtkb-notes-thread",
    )


def test_helper_imports_no_llm_or_api_classifier_dependencies() -> None:
    forbidden_prefixes = (
        "chromadb",
        "openai",
        "anthropic",
        "transformers",
        "sentence_transformers",
        "tiktoken",
    )

    pre_import_modules = set(sys.modules)
    import groundtruth_kb.owner_decision.resolution_signals as resolution_signals_module  # noqa: F401

    new_modules = set(sys.modules) - pre_import_modules
    for name in new_modules:
        assert not any(name.startswith(prefix) for prefix in forbidden_prefixes), (
            f"helper transitively imported forbidden LLM/API module {name!r}"
        )
