"""Regression tests for role-neutral, non-dispatchable ADVISORY entries."""

from __future__ import annotations

from pathlib import Path

import pytest
from groundtruth_kb.bridge.notify import _derive_dispatchable

from scripts import bridge_lifecycle_resolver as resolver
from scripts import gtkb_bridge_writer as writer


def _write_advisory(root: Path, author_identity: str) -> None:
    bridge_dir = root / "bridge"
    bridge_dir.mkdir(parents=True, exist_ok=True)
    (bridge_dir / "role-neutral-advisory-001.md").write_text(
        "\n".join(
            (
                "ADVISORY",
                f"author_identity: {author_identity}",
                "Document: role-neutral-advisory",
                "Version: 001",
                "",
                "# Informational finding",
                "",
            )
        ),
        encoding="utf-8",
    )


@pytest.mark.parametrize(
    "author_identity",
    ("prime-builder/codex", "loyal-opposition/claude", "owner"),
)
def test_advisory_accepts_every_authoring_role(tmp_path: Path, author_identity: str) -> None:
    _write_advisory(tmp_path, author_identity)

    result = resolver.resolve_bridge_lifecycle(tmp_path, "role-neutral-advisory")

    assert result.latest_strict_state.status == "ADVISORY"
    assert result.latest_strict_state.author_identity == author_identity


@pytest.mark.parametrize(
    ("status", "accepted_role", "rejected_role"),
    (
        ("NEW", "prime-builder", "loyal-opposition"),
        ("REVISED", "prime-builder", "loyal-opposition"),
        ("NO-ACTION", "prime-builder", "loyal-opposition"),
        ("GO", "loyal-opposition", "prime-builder"),
        ("NO-GO", "loyal-opposition", "prime-builder"),
        ("VERIFIED", "loyal-opposition", "prime-builder"),
        ("DEFERRED", "prime-builder", "loyal-opposition"),
        ("WITHDRAWN", "owner", "loyal-opposition"),
    ),
)
def test_other_status_role_bindings_are_unchanged(
    status: str,
    accepted_role: str,
    rejected_role: str,
) -> None:
    resolver._validate_author_role(status, accepted_role, rel_path="bridge/fixture-001.md", version=1)

    with pytest.raises(resolver.BridgeLifecycleResolutionError) as exc_info:
        resolver._validate_author_role(status, rejected_role, rel_path="bridge/fixture-001.md", version=1)

    assert exc_info.value.code == "WRONG_STATUS_AUTHOR_ROLE"


def test_advisory_has_no_formal_responder_role() -> None:
    content = "ADVISORY\n\nbridge_kind: advisory\n"

    assert "ADVISORY" not in writer.LOYAL_OPPOSITION_STATUSES
    assert "ADVISORY" not in writer.ENVELOPE_RESPONDER_BY_STATUS
    assert writer.normalize_bridge_envelope_head(content) == content

    with pytest.raises(writer.BridgeEnvelopeError, match="no formal responder-role"):
        writer.validate_bridge_envelope_head("ADVISORY\n::init gtkb pb\n::open build\n\nbridge_kind: advisory\n")


@pytest.mark.parametrize("classification", ("implementation", "terminal", "ambiguous"))
def test_advisory_remains_non_dispatchable(classification: str) -> None:
    assert _derive_dispatchable("ADVISORY", classification) is False
