"""Specification-derived regression coverage for DCL correction-state v2."""

from __future__ import annotations

import itertools
from pathlib import Path

import pytest

from groundtruth_kb.bridge.versioned_files import status_from_bridge_text
from scripts import adr_dcl_clause_preflight as clause_preflight
from scripts import bridge_applicability_preflight as applicability
from scripts import bridge_author_metadata as author_metadata
from scripts import bridge_lifecycle_resolver as lifecycle
from scripts import bridge_work_intent_registry as work_intent
from scripts import gtkb_bridge_writer as writer


AUTHOR_METADATA = {
    "author_identity": "prime-builder/codex",
    "author_harness_id": "A",
    "author_session_context_id": "pb-session",
    "author_model": "test-model",
    "author_model_version": "test-model-v1",
    "author_model_configuration": "pytest",
}


def _metadata(role: str, session_id: str) -> str:
    identity = "prime-builder/codex" if role == "prime-builder" else "loyal-opposition/codex"
    return (
        f"author_identity: {identity}\n"
        "author_harness_id: codex\n"
        f"author_session_context_id: {session_id}\n"
        "author_model: test-model\n"
        "author_model_version: test-model-v1\n"
        "author_model_configuration: pytest\n"
    )


def _write_version(
    root: Path,
    slug: str,
    version: int,
    status: str,
    *,
    role: str,
    responds_to: int | None,
    header: tuple[str, ...] | None = None,
) -> Path:
    bridge = root / "bridge"
    bridge.mkdir(parents=True, exist_ok=True)
    head = header or (status, "::init gtkb lo", "::open build")
    response = "" if responds_to is None else f"Responds to: bridge/{slug}-{responds_to:03d}.md\n"
    path = bridge / f"{slug}-{version:03d}.md"
    path.write_text(
        "\n".join(head)
        + "\n\n"
        + _metadata(role, f"{role}-{version}")
        + f"Document: {slug}\nVersion: {version:03d}\n"
        + response
        + "\n# Fixture\n",
        encoding="utf-8",
    )
    return path


def _write_correction_chain(root: Path, slug: str, *, historical: bool = False) -> None:
    _write_version(
        root,
        slug,
        1,
        "NEW",
        role="prime-builder",
        responds_to=None,
    )
    _write_version(
        root,
        slug,
        2,
        "NO-GO",
        role="loyal-opposition",
        responds_to=1,
        header=("NO-GO", "::init gtkb pb", "::open build"),
    )
    correction = "NO-ACTION" if historical else "VERDICT-REJECTED"
    _write_version(
        root,
        slug,
        3,
        correction,
        role="prime-builder",
        responds_to=2,
    )


def test_historical_no_action_normalizes_without_new_output(tmp_path: Path) -> None:
    content = "NO-ACTION\n::init gtkb lo\n::open build\n"
    assert status_from_bridge_text(content) == "VERDICT-REJECTED"
    path = tmp_path / "historical.md"
    path.write_text(content, encoding="utf-8")
    assert work_intent._bridge_file_status(path) == "VERDICT-REJECTED"


def test_verdict_rejected_new_output_accepted(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(writer, "run_bridge_compliance_audit", lambda **_kwargs: {"decision": "pass"})
    monkeypatch.setattr(writer, "_registry_publication_enabled", lambda _root: False)
    content = (
        "VERDICT-REJECTED\n::init gtkb lo\n::open build\n\n"
        "bridge_kind: prime_response\nDocument: correction\nVersion: 003\n"
    )
    path = writer.write_bridge_file(
        "correction",
        3,
        content,
        tmp_path,
        author_metadata=AUTHOR_METADATA,
        require_author_metadata=False,
        release_claim=False,
    )
    assert path.read_text(encoding="utf-8").startswith("VERDICT-REJECTED\n::init gtkb lo\n::open build\n")


def test_new_no_action_output_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(writer, "_registry_publication_enabled", lambda _root: True)
    with pytest.raises(writer.BridgeTransitionError, match="must use VERDICT-REJECTED"):
        writer.write_bridge_file(
            "obsolete",
            1,
            "NO-ACTION\n::init gtkb lo\n::open build\n",
            tmp_path,
            author_metadata=AUTHOR_METADATA,
            release_claim=False,
        )


def test_verdict_rejected_is_latest_thread_head(tmp_path: Path) -> None:
    slug = "correction-head"
    _write_correction_chain(tmp_path, slug, historical=True)
    resolved = lifecycle.resolve_bridge_lifecycle(tmp_path, slug)
    assert resolved.latest_strict_state.status == "VERDICT-REJECTED"
    assert resolved.latest_strict_state.path.endswith("-003.md")
    assert resolved.review_artifact == resolved.latest_strict_state
    assert resolved.implementation_artifact is None


@pytest.mark.parametrize("successor", ["GO", "NO-GO"])
def test_successor_verdict_exact_predecessor_passes_all_gates(tmp_path: Path, successor: str) -> None:
    slug = f"exact-{successor.lower()}"
    _write_correction_chain(tmp_path, slug)
    _write_version(
        tmp_path,
        slug,
        4,
        successor,
        role="loyal-opposition",
        responds_to=3,
        header=(successor, "::init gtkb pb", "::open build"),
    )

    resolved = lifecycle.resolve_bridge_lifecycle(tmp_path, slug)
    assert resolved.latest_strict_state.status == successor
    versions = applicability.parse_versioned_files_for_document(tmp_path / "bridge", slug)
    assert applicability.choose_operative_version(versions).version_number == 4
    assert clause_preflight.resolve_operative_file_lifecycle_aware(slug, tmp_path / "bridge").is_file()
    writer._validate_provider_transition(
        latest_status="VERDICT-REJECTED",
        latest_content="bridge_kind: prime_response\n",
        verdict=successor,
    )


def test_header_orderings_preserve_routing_and_attribution(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        author_metadata,
        "load_author_metadata",
        lambda *_args, **_kwargs: dict(AUTHOR_METADATA),
    )
    header_lines = ("VERDICT-REJECTED", "::init gtkb lo", "::open build")
    for ordering in itertools.permutations(header_lines):
        content = "\n".join(ordering) + "\n\n# Correction\n"
        assert status_from_bridge_text(content) == "VERDICT-REJECTED"
        assert author_metadata.bridge_artifact_status(content) == "VERDICT-REJECTED"
        assert set(author_metadata.author_metadata_gaps_for_content(content)) >= set(
            author_metadata.REQUIRED_AUTHOR_METADATA_FIELDS
        )

        enriched = author_metadata.ensure_author_metadata(content, explicit=AUTHOR_METADATA)
        assert author_metadata.author_metadata_gaps_for_content(enriched) == []
        normalized = writer.normalize_bridge_envelope_head(enriched)
        assert normalized.startswith("VERDICT-REJECTED\n::init gtkb lo\n::open build\n")


def test_stale_skipped_contradictory_evidence_never_passes(tmp_path: Path) -> None:
    stale_root = tmp_path / "stale"
    stale_slug = "stale"
    _write_correction_chain(stale_root, stale_slug)
    stale_path = stale_root / "bridge" / f"{stale_slug}-003.md"
    stale_path.write_text(
        stale_path.read_text(encoding="utf-8").replace(f"bridge/{stale_slug}-002.md", f"bridge/{stale_slug}-001.md"),
        encoding="utf-8",
    )
    with pytest.raises(lifecycle.BridgeLifecycleResolutionError) as stale:
        lifecycle.resolve_bridge_lifecycle(stale_root, stale_slug)
    assert stale.value.code == "WRONG_RESPONDS_TO_LINK"

    contradictory_root = tmp_path / "contradictory"
    contradictory_slug = "contradictory"
    _write_correction_chain(contradictory_root, contradictory_slug)
    contradictory = contradictory_root / "bridge" / f"{contradictory_slug}-003.md"
    contradictory.write_text(
        contradictory.read_text(encoding="utf-8").replace(
            "author_identity: prime-builder/codex",
            "author_identity: loyal-opposition/codex",
        ),
        encoding="utf-8",
    )
    with pytest.raises(lifecycle.BridgeLifecycleResolutionError) as wrong_role:
        lifecycle.resolve_bridge_lifecycle(contradictory_root, contradictory_slug)
    assert wrong_role.value.code == "WRONG_STATUS_AUTHOR_ROLE"

    skipped_root = tmp_path / "skipped"
    skipped_slug = "skipped"
    _write_correction_chain(skipped_root, skipped_slug)
    versions = applicability.parse_versioned_files_for_document(skipped_root / "bridge", skipped_slug)
    operative = applicability.choose_operative_version(versions)
    assert operative.status == "VERDICT-REJECTED"
    assert operative.version_number == 3
