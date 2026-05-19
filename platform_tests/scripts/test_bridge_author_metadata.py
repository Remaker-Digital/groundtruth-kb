"""Tests for bridge artifact author/model audit metadata helpers."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.bridge_author_metadata import (
    BridgeAuthorMetadataError,
    author_metadata_gaps_for_content,
    ensure_author_metadata,
    load_author_metadata,
)

AUTHOR_METADATA = {
    "author_identity": "Codex",
    "author_harness_id": "A",
    "author_session_context_id": "session-123",
    "author_model": "GPT-5.5",
    "author_model_version": "5.5",
    "author_model_configuration": "Extra High",
}


def test_author_metadata_gaps_for_bridge_artifact() -> None:
    content = "NO-GO\n\n## Findings\n"
    assert author_metadata_gaps_for_content(content) == [
        "author_identity",
        "author_harness_id",
        "author_session_context_id",
        "author_model",
        "author_model_version",
        "author_model_configuration",
    ]


def test_ensure_author_metadata_inserts_after_status_line(tmp_path: Path) -> None:
    content = "NEW\n\n# Proposal\n"

    updated = ensure_author_metadata(content, project_root=tmp_path, explicit=AUTHOR_METADATA)

    assert updated.startswith(
        "NEW\n"
        "author_identity: Codex\n"
        "author_harness_id: A\n"
        "author_session_context_id: session-123\n"
        "author_model: GPT-5.5\n"
        "author_model_version: 5.5\n"
        "author_model_configuration: Extra High\n"
        "\n# Proposal\n"
    )


def test_ensure_author_metadata_rejects_missing_runtime_source(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "GTKB_AUTHOR_IDENTITY",
        "GTKB_AUTHOR_HARNESS_ID",
        "GTKB_AUTHOR_SESSION_CONTEXT_ID",
        "GTKB_AUTHOR_MODEL",
        "GTKB_AUTHOR_MODEL_VERSION",
        "GTKB_AUTHOR_MODEL_CONFIGURATION",
    ):
        monkeypatch.delenv(name, raising=False)

    with pytest.raises(BridgeAuthorMetadataError, match="missing or invalid"):
        ensure_author_metadata("GO\n\n## Verdict\n", project_root=tmp_path)


def test_ensure_author_metadata_rejects_placeholder_existing_value(tmp_path: Path) -> None:
    content = (
        "NO-GO\n"
        "author_identity: Codex\n"
        "author_harness_id: A\n"
        "author_session_context_id: session-123\n"
        "author_model: unknown\n"
        "author_model_version: 5.5\n"
        "author_model_configuration: Extra High\n"
        "\n## Findings\n"
    )

    with pytest.raises(BridgeAuthorMetadataError, match="partial or invalid"):
        ensure_author_metadata(content, project_root=tmp_path, explicit=AUTHOR_METADATA)


def test_load_author_metadata_uses_project_session_file(tmp_path: Path) -> None:
    metadata_path = tmp_path / ".gtkb-state" / "bridge-author-metadata" / "current.json"
    metadata_path.parent.mkdir(parents=True)
    metadata_path.write_text(json.dumps(AUTHOR_METADATA), encoding="utf-8")

    assert load_author_metadata(tmp_path) == AUTHOR_METADATA
