"""Spec-derived tests for WI-6307: verdict publish must resolve the acting harness.

Governing specifications (carried forward from
``bridge/gtkb-wi6307-verdict-publish-acting-harness-resolution-001.md`` and the
GO verdict at ``-002``):

- ``DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`` -- rows 1 and 2.
- ``GOV-FILE-BRIDGE-AUTHORITY-001`` -- row 2.
- ``WI-6211`` no-vendor-default constraint -- row 3.
- ``GOV-SESSION-ROLE-AUTHORITY-001`` env precedence -- row 4.
- ``WI-6277`` author-identity degradation guard -- row 5.
- Owner-excluded scope boundary -- row 6.
- Scope amendment (line 330 durable-id lookup) -- row 7.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if str(SRC) not in os.sys.path:
    os.sys.path.insert(0, str(SRC))

from groundtruth_kb.bridge import verdict_filing as vf  # noqa: E402
from groundtruth_kb.session import envelope as env_mod  # noqa: E402

# A session id that exists in more than one harness envelope tree. This is the
# condition that made publication fail session-scoped for every thread.
COLLIDING_SESSION_ID = "a0dbbe63-b24f-42eb-9274-e0fec8b23a00"


@pytest.fixture(autouse=True)
def _clear_harness_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Each test states its own GTKB_HARNESS_NAME condition explicitly."""
    monkeypatch.delenv("GTKB_HARNESS_NAME", raising=False)


def _colliding_trees(session_id: str) -> list[str]:
    """Harness trees holding an envelope for ``session_id``."""
    trees: list[str] = []
    state = PROJECT_ROOT / "harness-state"
    for tree in sorted(p for p in state.iterdir() if p.is_dir()):
        if (tree / "session-envelopes" / f"{session_id}.json").is_file():
            trees.append(tree.name)
    return trees


# Row 1 -- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
def test_publish_resolves_harness_on_colliding_session_id() -> None:
    """The acting harness resolves even when the session id collides.

    Pre-change, ``_harness_name()`` returned ``None`` here and
    ``resolve_worker_role_provenance`` raised "Worker role provenance is
    ambiguous across session envelopes". The selector is what was missing.
    """
    if len(_colliding_trees(COLLIDING_SESSION_ID)) < 2:
        pytest.skip("fixture session id no longer collides across harness trees")

    resolved = vf._harness_name(PROJECT_ROOT)
    assert resolved, "acting harness must resolve when GTKB_HARNESS_NAME is unset"

    # With a selector present the glob branch is not taken, so the ambiguity
    # error cannot be raised for this session id.
    env_mod.resolve_worker_role_provenance(
        PROJECT_ROOT,
        current_session_id=COLLIDING_SESSION_ID,
        harness_name=resolved,
    )


# Row 2 -- GOV-FILE-BRIDGE-AUTHORITY-001
def test_lo_verdict_publication_end_to_end_unblocked() -> None:
    """Author metadata derived for a verdict carries a resolved harness."""
    derived = vf._metadata_from_envelope(COLLIDING_SESSION_ID, PROJECT_ROOT, "")
    assert derived["author_session_context_id"] == COLLIDING_SESSION_ID
    identity = derived["author_identity"]
    assert identity, "author_identity must not be empty"
    assert not identity.endswith("/unknown"), (
        "publication must not fall through to an unknown harness once the "
        f"acting harness is resolvable; got {identity!r}"
    )


# Row 3 -- WI-6211 no-vendor-default constraint
def test_harness_name_returns_none_when_identity_unresolvable() -> None:
    """No project_root means no fallback, and never a hardcoded vendor default."""
    assert vf._harness_name() is None
    assert vf._harness_name(None) is None


def test_harness_name_returns_none_on_envelope_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """EnvelopeError degrades to None -- the pre-change behaviour, not a default."""

    def _raise(*_args: object, **_kwargs: object) -> tuple[str, str]:
        raise env_mod.EnvelopeError("conflicting runtime markers")

    monkeypatch.setattr(env_mod, "resolve_acting_harness_identity", _raise)
    assert vf._harness_name(PROJECT_ROOT) is None


# Row 4 -- GTKB_HARNESS_NAME precedence
def test_explicit_env_var_retains_precedence(monkeypatch: pytest.MonkeyPatch) -> None:
    """An explicit host declaration wins; the fallback is not consulted."""
    monkeypatch.setenv("GTKB_HARNESS_NAME", "codex")

    def _must_not_run(*_args: object, **_kwargs: object) -> tuple[str, str]:
        raise AssertionError("fallback consulted despite GTKB_HARNESS_NAME being set")

    monkeypatch.setattr(env_mod, "resolve_acting_harness_identity", _must_not_run)
    assert vf._harness_name(PROJECT_ROOT) == "codex"


# Row 5 -- WI-6277 author-identity degradation guard
def test_author_identity_not_degraded_by_fallback() -> None:
    """The fallback must not strip the role prefix from author_identity."""
    derived = vf._metadata_from_envelope(COLLIDING_SESSION_ID, PROJECT_ROOT, "")
    identity = derived["author_identity"]
    assert "/" in identity, (
        "author_identity must keep its <role>/<harness> shape; a bare harness "
        f"name is the WI-6277 degradation that strands threads later; got {identity!r}"
    )
    assert identity.split("/", 1)[0], "role component must be present"


# Row 6 -- owner-excluded scope boundary
def test_marker_continuity_order_unchanged() -> None:
    """MARKER_CONTINUITY_ORDER is byte-identical to HEAD (owner exclusion)."""
    rel = "scripts/gtkb_session_id.py"
    head = subprocess.run(
        ["git", "show", f"HEAD:{rel}"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout

    def _block(text: str) -> str:
        marker = "MARKER_CONTINUITY_ORDER"
        start = text.index(marker)
        end = text.index("]", start)
        return text[start : end + 1]

    current = (PROJECT_ROOT / rel).read_text(encoding="utf-8")
    assert _block(current) == _block(head), (
        "MARKER_CONTINUITY_ORDER was modified; the owner excluded it from this change"
    )


# Row 7 -- scope amendment: durable-registry id, not the name initial
@pytest.mark.parametrize(
    ("harness_name", "expected_id", "name_initial"),
    [("claude", "B", "C"), ("codex", "A", "C"), ("antigravity", "C", "A")],
)
def test_author_harness_id_uses_durable_registry_not_name_initial(
    harness_name: str, expected_id: str, name_initial: str
) -> None:
    """harness_id comes from the owner-assigned identity map, never the initial.

    ``(harness or "").upper()[:1]`` was latent only because ``_harness_name()``
    returned ``None``. Resolving the acting harness activates it, so the
    heuristic had to go with the fix or it would emit a wrong id.
    """
    resolved = vf._harness_id_for(harness_name, PROJECT_ROOT)
    assert resolved == expected_id, f"{harness_name} must map to durable id {expected_id!r}, got {resolved!r}"
    if expected_id != name_initial:
        assert resolved != name_initial, (
            f"{harness_name} resolved to the name initial {name_initial!r}, which "
            "is the fabricated-id defect this row exists to prevent"
        )
