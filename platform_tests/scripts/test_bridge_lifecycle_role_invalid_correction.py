"""Correction eligibility for strict-but-role-invalid verdicts (WI-5967 C2).

Per ``bridge/gtkb-wi5967-verdict-role-transition-guard-and-correction-001.md``
(Loyal Opposition GO at ``-002.md``).

WI-5629 landed a sanctioned recovery for **malformed** verdicts: append a strict
Prime ``NO-ACTION``, then a role-correct Loyal Opposition verdict. It was
reachable only from ``classification="malformed"``, which is set solely when the
FIRST LINE is not a canonical status token. An out-of-role verdict has a
perfectly canonical first line, so it classified ``strict``, failed the role
check, and wedged its thread with no way out.

C2 widens correction eligibility to cover it. These tests pin that the widening
is a *recovery path*, not a relaxation: an uncorrected chain still fails closed,
an incorrectly-corrected chain still fails closed, and the single-correction
invariant still holds.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
for _extra in (REPO_ROOT / "scripts", REPO_ROOT / "groundtruth-kb" / "src"):
    if str(_extra) not in sys.path:
        sys.path.insert(0, str(_extra))

import bridge_lifecycle_resolver as blr  # noqa: E402

SLUG = "wi5967-fixture-thread"


def _write(bridge_dir: Path, version: int, status: str, identity: str, responds_to: str | None = None) -> Path:
    lines = [
        status,
        "",
        f"author_identity: {identity}",
        "author_harness_id: X",
        f"author_session_context_id: X-2026-08-06T00-00-{version:02d}Z",
        "",
        "bridge_kind: lo_verdict" if identity.startswith("loyal") else "bridge_kind: prime_proposal",
        f"Document: {SLUG}",
        f"Version: {version:03d}",
    ]
    if responds_to:
        lines.append(f"Responds to: bridge/{SLUG}-{responds_to}.md")
    path = bridge_dir / f"{SLUG}-{version:03d}.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


@pytest.fixture
def project(tmp_path: Path) -> Path:
    (tmp_path / "bridge").mkdir()
    return tmp_path


def _seed_role_invalid_chain(project: Path) -> Path:
    """NEW (Prime) -> VERIFIED authored by Prime: the v013 defect shape."""
    bridge = project / "bridge"
    _write(bridge, 1, "NEW", "prime-builder/claude/B")
    _write(bridge, 2, "VERIFIED", "prime-builder/goose/G", responds_to="001")
    return bridge


# --------------------------------------------------------------------------
# T8 - correction-eligible, not a hard failure
# --------------------------------------------------------------------------


def test_t8_role_invalid_verdict_is_correction_eligible(project):
    _seed_role_invalid_chain(project)
    with pytest.raises(blr.BridgeLifecycleResolutionError) as exc:
        blr.resolve_bridge_lifecycle(project, SLUG)
    message = str(exc.value)
    # It must NOT fail with the old hard role error; it must reach the
    # correction machinery and complain about the missing corrective tail.
    assert "wrong or unreadable author role" not in message
    assert "NO-ACTION" in message or "TAIL" in message.upper()


# --------------------------------------------------------------------------
# T9 - pending correction confers NO implementation authority
# --------------------------------------------------------------------------


def test_t9_no_action_alone_yields_pending_correction_without_authority(project):
    bridge = _seed_role_invalid_chain(project)
    _write(bridge, 3, "NO-ACTION", "prime-builder/claude/B", responds_to="002")

    result = blr.resolve_bridge_lifecycle(project, SLUG)
    codes = {d.code for d in result.blocking_diagnostics}
    assert blr.PENDING_CORRECTION_DIAGNOSTIC in codes
    assert result.implementation_artifact is None, "pending correction must confer no implementation authority"
    assert result.implementation_verdict is None


# --------------------------------------------------------------------------
# T10 - completed correction resolves
# --------------------------------------------------------------------------


def test_t10_completed_correction_resolves_with_the_corrected_verdict(project):
    bridge = _seed_role_invalid_chain(project)
    _write(bridge, 3, "NO-ACTION", "prime-builder/claude/B", responds_to="002")
    _write(bridge, 4, "GO", "loyal-opposition/goose/G", responds_to="003")

    result = blr.resolve_bridge_lifecycle(project, SLUG)
    assert not result.blocking_diagnostics
    assert result.latest_strict_state.status == "GO"
    assert result.latest_strict_state.author_role == "loyal-opposition"


# --------------------------------------------------------------------------
# T11 - fail-closed preserved: an incorrect corrected verdict is rejected
# --------------------------------------------------------------------------


def test_t11_role_incorrect_corrected_verdict_still_fails_closed(project):
    bridge = _seed_role_invalid_chain(project)
    _write(bridge, 3, "NO-ACTION", "prime-builder/claude/B", responds_to="002")
    # The "correction" is itself authored by the wrong role.
    _write(bridge, 4, "GO", "prime-builder/claude/B", responds_to="003")

    with pytest.raises(blr.BridgeLifecycleResolutionError):
        blr.resolve_bridge_lifecycle(project, SLUG)


def test_t11b_correction_requires_a_prime_no_action_not_any_entry(project):
    bridge = _seed_role_invalid_chain(project)
    # An LO entry where the strict Prime NO-ACTION belongs.
    _write(bridge, 3, "NO-GO", "loyal-opposition/goose/G", responds_to="002")

    with pytest.raises(blr.BridgeLifecycleResolutionError) as exc:
        blr.resolve_bridge_lifecycle(project, SLUG)
    assert "NO-ACTION" in str(exc.value)


# --------------------------------------------------------------------------
# T12 - single-correction invariant preserved
# --------------------------------------------------------------------------


def test_t12_two_correction_eligible_entries_still_fail(project):
    bridge = project / "bridge"
    _write(bridge, 1, "NEW", "prime-builder/claude/B")
    _write(bridge, 2, "VERIFIED", "prime-builder/goose/G", responds_to="001")
    _write(bridge, 3, "NEW", "prime-builder/claude/B", responds_to="002")
    _write(bridge, 4, "GO", "prime-builder/claude/B", responds_to="003")

    with pytest.raises(blr.BridgeLifecycleResolutionError) as exc:
        blr.resolve_bridge_lifecycle(project, SLUG)
    assert "MULTIPLE_MALFORMED" in str(exc.value).upper() or "multiple malformed" in str(exc.value)


# --------------------------------------------------------------------------
# Predicate contract consumed by the write-time guard
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("status", "role", "expected"),
    [
        ("VERIFIED", "loyal-opposition", True),
        ("VERIFIED", "prime-builder", False),
        ("GO", "loyal-opposition", True),
        ("GO", "prime-builder", False),
        ("NO-GO", "loyal-opposition", True),
        ("NEW", "prime-builder", True),
        ("NEW", "loyal-opposition", False),
        ("REVISED", "prime-builder", True),
        ("NO-ACTION", "prime-builder", True),
        ("NO-ACTION", "loyal-opposition", False),
        ("DEFERRED", "owner", True),
        ("WITHDRAWN", "prime-builder", True),
    ],
)
def test_author_role_predicate_matches_protocol_status_table(status, role, expected):
    assert blr.author_role_is_valid_for_status(status, role) is expected
