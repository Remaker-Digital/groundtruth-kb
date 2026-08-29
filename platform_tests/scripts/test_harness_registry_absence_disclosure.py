"""WI-7526: an absent harness registry projection must be disclosed, not silent.

The registry projection (``harness-state/harness-registry.json``) is absent by
design: ``ADR-ELIMINATE-DURABLE-ROLE-ASSIGNMENT-001`` and
``DCL-NO-DURABLE-ROLE-IN-REGISTRY-001`` retired it as identity and role
authority. The defect is not the absence; it is that the readers are fail-soft
and say nothing, so the first signal an operator receives is a downstream error
naming the wrong cause.

Measured before this fix: ``gt bridge file-implementation-proposal`` failed with
"exact bridge author context requires both an invoking session id and acting
harness identity". Session identity was fine. The registry was the cause. The
message pointed at the half that worked.

These tests pin the two disclosure behaviors and, equally important, pin that the
diagnostic stays quiet about the registry when the registry is not implicated --
an error that always blames the registry is no better than one that never does.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.bridge_author_metadata import _author_context_failure_reason
from scripts.harness_identity import load_harness_identities
from scripts.harness_projection_reader import harness_registry_path


def _project_without_registry(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    (root / "harness-state").mkdir(parents=True)
    return root


def _project_with_registry(tmp_path: Path, harnesses: list[dict]) -> Path:
    root = tmp_path / "project"
    state = root / "harness-state"
    state.mkdir(parents=True)
    (state / "harness-registry.json").write_text(
        json.dumps({"schema_version": 1, "harnesses": harnesses}),
        encoding="utf-8",
    )
    return root


# ---------------------------------------------------------------------------
# Reader disclosure
# ---------------------------------------------------------------------------


def test_absent_registry_is_disclosed_in_the_identity_document(tmp_path: Path) -> None:
    root = _project_without_registry(tmp_path)
    document = load_harness_identities(root)

    assert document["harnesses"] == {}
    description = document["description"].lower()
    assert "absent" in description, f"absence not disclosed: {document['description']!r}"
    assert "fail-soft" in description, "the empty result must be marked as fail-soft, not as fact"


def test_disclosure_states_the_projection_is_not_the_fix(tmp_path: Path) -> None:
    """A reader told only 'absent' would reasonably restore the file.

    The governing records retired the projection, so the disclosure has to say
    which direction the correction runs or it invites the wrong repair.
    """
    document = load_harness_identities(_project_without_registry(tmp_path))
    description = document["description"]
    assert "ADR-ELIMINATE-DURABLE-ROLE-ASSIGNMENT-001" in description
    assert "DCL-NO-DURABLE-ROLE-IN-REGISTRY-001" in description


def test_populated_registry_keeps_its_normal_description(tmp_path: Path) -> None:
    """The disclosure must not fire when the projection is present."""
    root = _project_with_registry(tmp_path, [{"id": "A", "harness_name": "codex"}])
    document = load_harness_identities(root)

    assert document["harnesses"] == {"codex": {"id": "A"}}
    assert "absent" not in document["description"].lower()


def test_present_but_empty_registry_is_not_reported_as_absent(tmp_path: Path) -> None:
    """A projection that legitimately lists no harness is not the absence case.

    Distinguishing these is the whole point: conflating them is what made an
    empty document indistinguishable from a missing file.
    """
    root = _project_with_registry(tmp_path, [])
    document = load_harness_identities(root)

    assert document["harnesses"] == {}
    assert "absent" not in document["description"].lower()


# ---------------------------------------------------------------------------
# Operator-facing diagnostic
# ---------------------------------------------------------------------------


def test_diagnostic_names_the_missing_half_only(tmp_path: Path) -> None:
    root = _project_without_registry(tmp_path)

    session_missing = _author_context_failure_reason(root, session_context_id="", harness_name="claude")
    assert "missing: invoking session id" in session_missing
    assert "acting harness identity" not in session_missing.split("missing:", 1)[1]


def test_absent_registry_diagnostic_names_the_registry_as_cause(tmp_path: Path) -> None:
    """The regression this work item exists to prevent."""
    root = _project_without_registry(tmp_path)

    reason = _author_context_failure_reason(root, session_context_id="ctx-1", harness_name="")

    assert "missing: acting harness identity" in reason
    assert str(harness_registry_path(root)) in reason, "the diagnostic must name the actual file"
    assert "fail-soft" in reason, "it must explain why nothing upstream reported the absence"
    assert "restoring the file is NOT the fix" in reason
    assert "GTKB_AUTHOR_HARNESS_ID" in reason, "an operator needs a route to proceed"


def test_diagnostic_stays_quiet_about_the_registry_when_it_is_present(tmp_path: Path) -> None:
    """An error that always blames the registry is no better than one that never does."""
    root = _project_with_registry(tmp_path, [{"id": "A", "harness_name": "codex"}])

    reason = _author_context_failure_reason(root, session_context_id="ctx-1", harness_name="")

    assert "missing: acting harness identity" in reason
    assert "harness-registry.json" not in reason
    assert "GTKB_AUTHOR_HARNESS_ID" not in reason


@pytest.mark.parametrize(
    ("session_id", "harness"),
    [("", ""), ("", "claude"), ("ctx-1", "")],
)
def test_diagnostic_always_reports_at_least_one_missing_half(tmp_path: Path, session_id: str, harness: str) -> None:
    reason = _author_context_failure_reason(
        _project_without_registry(tmp_path),
        session_context_id=session_id,
        harness_name=harness,
    )
    assert "missing: " in reason
    assert reason.split("missing: ", 1)[1].strip(), "the missing list must never be empty"
