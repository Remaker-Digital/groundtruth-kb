"""Regression: harness G (goose) is host-attested, and no harness may attest
placeholder model metadata (WI-5812).

Background. ``_HOST_MODEL_METADATA_SOURCE_BY_HARNESS`` previously listed only
``codex`` and ``cursor``. Because host attestation is a precondition of the
governed bridge filing path, every Goose run fell back to writing ``bridge/``
files directly, bypassing status-token validation, receipts, and
publication-capability minting. Measured consequence: 133 direct ``write``-tool
calls into ``bridge/`` across eight Goose transcripts, and 14 uncommitted chain
files with no capability row -- all authored by ``loyal-opposition/goose/G``
(``DELIB-20260808-WI5825-HARNESS-G-ROOT-CAUSE``, ``WI-6076``).

These tests lock in both halves of the contract: goose is admitted, and the
placeholder rejection that keeps admission from becoming a silent false
attestation stays harness-symmetric.
"""

from __future__ import annotations

import click
import pytest
from groundtruth_kb.cli_session_handoff import (
    _HOST_MODEL_METADATA_SOURCE_BY_HARNESS,
    _HOST_SESSION_ID_ENV_BY_HARNESS,
    _PLACEHOLDER_TURN_METADATA,
    _required_turn_metadata,
)

ATTESTED_HARNESSES = ("codex", "cursor", "goose")


def test_goose_is_host_attested() -> None:
    """Harness G resolves a model-metadata source, so attestation no longer rejects it."""
    assert "goose" in _HOST_MODEL_METADATA_SOURCE_BY_HARNESS
    assert _HOST_MODEL_METADATA_SOURCE_BY_HARNESS["goose"] == "goose-session-envelope-metadata"


@pytest.mark.parametrize("harness", ATTESTED_HARNESSES)
def test_attested_harness_has_nonempty_metadata_source(harness: str) -> None:
    """Every attested harness names a concrete provenance source, never a placeholder."""
    source = _HOST_MODEL_METADATA_SOURCE_BY_HARNESS[harness]
    assert isinstance(source, str) and source.strip()
    assert source.strip().lower() not in _PLACEHOLDER_TURN_METADATA


def test_pre_existing_harness_sources_unchanged() -> None:
    """Admitting goose must not alter codex or cursor resolution (parity assertion)."""
    assert _HOST_MODEL_METADATA_SOURCE_BY_HARNESS["codex"] == "x-codex-turn-metadata"
    assert _HOST_MODEL_METADATA_SOURCE_BY_HARNESS["cursor"] == "cursor-conversation-metadata"


@pytest.mark.parametrize("placeholder", ["unknown", "UNKNOWN", "Unknown", "unspecified", "n/a", "tbd", "none", "-", ""])
def test_placeholder_model_metadata_is_rejected(placeholder: str) -> None:
    """A placeholder model value is never acceptable turn metadata.

    Goose's live session envelope records ``model_id: unknown``. Admitting goose
    without this rejection would convert a hard attestation failure into a silent
    false attestation -- the WI-5234 / WI-5406 defect class.
    """
    with pytest.raises(click.ClickException):
        _required_turn_metadata(placeholder, "--model")


def test_placeholder_rejection_is_harness_symmetric() -> None:
    """The rejection is a property of the value, not of the harness.

    Guards that key on harness name drift apart; this asserts goose is held to the
    same standard as the harnesses admitted before it.
    """
    for harness in ATTESTED_HARNESSES:
        assert harness in _HOST_MODEL_METADATA_SOURCE_BY_HARNESS
    with pytest.raises(click.ClickException):
        _required_turn_metadata("unknown", "--model")
    assert _required_turn_metadata("claude-opus-5", "--model") == "claude-opus-5"


def test_goose_session_id_env_mapping_present() -> None:
    """Session-id resolution for goose was already wired by WI-6055; assert it stayed."""
    assert _HOST_SESSION_ID_ENV_BY_HARNESS["goose"] == "GOOSE_SESSION_ID"


def test_valid_model_metadata_still_accepted() -> None:
    """The guard rejects placeholders without rejecting real values."""
    assert _required_turn_metadata("  deepseek-v4-flash-0731  ", "--model") == "deepseek-v4-flash-0731"
    assert _required_turn_metadata("@preset/gtkb-v4f", "--model") == "@preset/gtkb-v4f"


@pytest.mark.parametrize("bad", ["line\nbreak", "carriage\rreturn", "x" * 257])
def test_malformed_turn_metadata_rejected(bad: str) -> None:
    """Multi-line and over-long values remain unusable host turn metadata."""
    with pytest.raises(click.ClickException):
        _required_turn_metadata(bad, "--model")
