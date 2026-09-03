"""TEST-12476 - session-envelope harness resolution must not default to a vendor.

Work item: WI-7531
Bridge:    bridge/gtkb-wi7531-session-envelope-harness-name-default-002.md (GO)

Specs under test:
  SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 - `::init` must bind the envelope of the
      harness that is actually acting, so the acting harness has to be resolvable.
  DCL-SESSION-ROLE-RESOLUTION-001 - worker-role provenance resolves from the open
      envelope; opening a wrong-harness envelope corrupts `changed_by` attribution
      and the review-independence signal.
  GOV-RELIABILITY-FAST-LANE-001 - governs this single-concern defect fix.

The defect: ``resolve_harness_identity`` fell back to the literal ``"codex"``
whenever no harness name was supplied, so an unresolved harness silently became
one named vendor instead of failing closed. Seven public entrypoints additionally
carried ``harness_name: str = "codex"`` signature defaults.
"""

from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from groundtruth_kb.session.envelope import (
    RUNTIME_HARNESS_MARKERS,
    EnvelopeError,
    close_current_topic,
    close_session,
    close_topic,
    ensure_current,
    open_session,
    open_topic,
    resolve_harness_identity,
    route_prompt_resources,
)

# The seven entrypoints that carried a vendor default before WI-7531.
_HARNESS_NAME_ENTRYPOINTS = (
    open_session,
    ensure_current,
    route_prompt_resources,
    open_topic,
    close_topic,
    close_current_topic,
    close_session,
)

_IDENTITY_RELATIVE = Path("harness-state") / "harness-identities.json"


def _fixture_root(tmp_path: Path) -> Path:
    """A checkout whose durable identity record names two harnesses."""
    identities = tmp_path / _IDENTITY_RELATIVE
    identities.parent.mkdir(parents=True, exist_ok=True)
    identities.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": {
                    "claude": {"id": "B"},
                    "codex": {"id": "A"},
                },
            }
        ),
        encoding="utf-8",
    )
    return tmp_path


def _clear_harness_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove every signal the acting-harness resolver reads.

    Without this the test inherits the real session's own runtime marker and
    would resolve a harness by accident rather than by construction.
    """
    for markers in RUNTIME_HARNESS_MARKERS.values():
        for marker in markers:
            monkeypatch.delenv(marker, raising=False)
    monkeypatch.delenv("GTKB_HARNESS_NAME", raising=False)
    monkeypatch.delenv("GTKB_HARNESS_ID", raising=False)


def test_absent_harness_name_fails_closed_instead_of_defaulting(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The regression: no name and no marker must raise, not become 'codex'."""
    root = _fixture_root(tmp_path)
    _clear_harness_environment(monkeypatch)

    with pytest.raises(EnvelopeError) as excinfo:
        resolve_harness_identity(root)

    # Fail closed on the identity, and do not name a vendor as the reason.
    assert "Acting harness identity is unavailable" in str(excinfo.value)


def test_absent_harness_name_never_resolves_to_codex(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Guards the exact defect shape: an empty name resolving to harness 'codex'.

    The durable record in this fixture *does* contain a `codex` entry, so a
    surviving fallback would resolve successfully and silently. The only correct
    outcome is a raise.
    """
    root = _fixture_root(tmp_path)
    _clear_harness_environment(monkeypatch)

    for empty in (None, "", "   "):
        with pytest.raises(EnvelopeError):
            resolve_harness_identity(root, harness_name=empty)


def test_runtime_marker_resolves_the_acting_harness(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A non-codex runtime marker must select that harness, not the old default."""
    root = _fixture_root(tmp_path)
    _clear_harness_environment(monkeypatch)
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "session-under-test")

    name, harness_id = resolve_harness_identity(root)

    assert name == "claude"
    assert harness_id == "B"


def test_explicit_harness_name_is_still_honoured(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The fix removes a fallback; it must not change explicit resolution."""
    root = _fixture_root(tmp_path)
    _clear_harness_environment(monkeypatch)

    assert resolve_harness_identity(root, harness_name="claude") == ("claude", "B")
    # An explicitly requested codex is legitimate; only the *implicit* one was not.
    assert resolve_harness_identity(root, harness_name="codex") == ("codex", "A")


def test_explicit_name_wins_over_a_conflicting_marker_by_failing_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Delegation must not let a marker silently override an explicit producer."""
    root = _fixture_root(tmp_path)
    _clear_harness_environment(monkeypatch)
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "session-under-test")

    # Explicit name is respected directly (no delegation, so no marker conflict).
    assert resolve_harness_identity(root, harness_name="codex") == ("codex", "A")


@pytest.mark.parametrize("entrypoint", _HARNESS_NAME_ENTRYPOINTS, ids=lambda fn: fn.__name__)
def test_no_entrypoint_declares_a_vendor_harness_default(entrypoint) -> None:
    """No public entrypoint may carry a hardcoded vendor name as its default."""
    parameter = inspect.signature(entrypoint).parameters["harness_name"]

    assert parameter.default is None, (
        f"{entrypoint.__name__} declares harness_name default "
        f"{parameter.default!r}; an unresolved harness must be resolved or fail "
        "closed, never assumed"
    )


def test_module_declares_no_vendor_fallback_literal() -> None:
    """Textual guard: the `or "codex"` fallback must not reappear."""
    source = Path(inspect.getsourcefile(resolve_harness_identity)).read_text(encoding="utf-8")

    assert 'or "codex"' not in source
    assert '= "codex"' not in source
