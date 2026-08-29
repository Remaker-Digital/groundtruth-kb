"""WI-7129: protected-commit clearance derives from canonical evidence.

``scripts/check_protected_commit_authorization.py`` resolved live GO evidence
only from the named packet cache under the forbidden runtime state directory. As
that surface is purged, the gate's sole clearance source disappears: WI-5183
passed independent source review, exact-byte review, every specification-derived
test, both mandatory preflights and the quality gates, with project-authorization
evaluation returning allowed -- and staging its six reviewed paths still returned
``live_go_packets_valid 0`` with every path denied.

The controlling verdict forbids weakening or bypassing the gate, so these tests
pin both halves of the acceptance criteria in equal measure:

* an authorized cohort clears **and** the forbidden directory is never read;
* an unauthorized cohort is still denied.

The second is the one that matters if this route is ever edited carelessly. A
change that made clearance easier would satisfy the first test alone.
"""

from __future__ import annotations

import pathlib
from pathlib import Path

import pytest

from scripts.check_protected_commit_authorization import _load_live_go_evidence
from scripts.implementation_authorization import (
    BY_BRIDGE_DIRECTORY_RELATIVE_PATH,
    _implementable_thread_slugs,
    canonical_go_authorizations,
    path_authorized,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


def _write_thread(bridge_dir: Path, slug: str, statuses: list[str]) -> None:
    """Write a versioned thread whose files carry ``statuses`` in order."""
    for index, status in enumerate(statuses, start=1):
        (bridge_dir / f"{slug}-{index:03d}.md").write_text(
            f"{status}\n::init gtkb lo\n::open build\n\nbody\n", encoding="utf-8"
        )


# ---------------------------------------------------------------------------
# Cheap pre-filter: only a latest GO / post-GO NO-GO can authorize anything
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("statuses", "implementable"),
    [
        (["NEW", "GO"], True),
        (["NEW", "GO", "NO-GO"], True),
        (["NEW"], False),
        (["NEW", "GO", "NEW"], False),
        (["NEW", "GO", "NEW", "VERIFIED"], False),
        (["NEW", "GO", "DEFERRED"], False),
        (["NEW", "GO", "NO-ACTION"], False),
        (["NEW", "WITHDRAWN"], False),
    ],
)
def test_prefilter_admits_only_implementable_latest_statuses(
    tmp_path: Path, statuses: list[str], implementable: bool
) -> None:
    bridge = tmp_path / "bridge"
    bridge.mkdir()
    _write_thread(bridge, "probe-thread", statuses)

    slugs = _implementable_thread_slugs(tmp_path)

    assert ("probe-thread" in slugs) is implementable, (
        f"latest={statuses[-1]!r} should {'admit' if implementable else 'exclude'} the thread"
    )


def test_prefilter_uses_the_highest_version_not_file_order(tmp_path: Path) -> None:
    """Version 010 must beat 009; lexical ordering would pick the wrong latest."""
    bridge = tmp_path / "bridge"
    bridge.mkdir()
    _write_thread(bridge, "many-versions", ["NEW"] * 9 + ["GO"])
    assert "many-versions" in _implementable_thread_slugs(tmp_path)

    _write_thread(bridge, "verified-tail", ["NEW"] * 9 + ["GO"] + ["VERIFIED"])
    assert "verified-tail" not in _implementable_thread_slugs(tmp_path)


def test_prefilter_is_empty_without_a_bridge_directory(tmp_path: Path) -> None:
    assert _implementable_thread_slugs(tmp_path) == []


# ---------------------------------------------------------------------------
# Acceptance 1: an authorized cohort clears without touching the forbidden dir
# ---------------------------------------------------------------------------


def _live_authorized_path() -> str:
    rows, _errors = canonical_go_authorizations(REPO_ROOT)
    if not rows:
        pytest.skip("no live GO thread in this checkout to derive an authorized path from")
    return str(rows[0]["target_path_globs"][0])


def test_authorized_cohort_clears_from_canonical_evidence() -> None:
    probe = _live_authorized_path()
    packets, _errors, _count = _load_live_go_evidence(REPO_ROOT, candidate_paths=[probe])
    assert any(path_authorized(packet, probe) for packet in packets)


def test_clearance_reads_nothing_under_the_forbidden_directory(monkeypatch) -> None:
    """The acceptance criterion, enforced rather than asserted in prose.

    A trip-wire on ``Path.read_text`` records any access below the packet
    directory. Checking the returned rows would not catch a read that happened
    and was then discarded; this catches the access itself.
    """
    probe = _live_authorized_path()
    forbidden = BY_BRIDGE_DIRECTORY_RELATIVE_PATH.as_posix()
    touched: list[str] = []
    original = pathlib.Path.read_text

    def spy(self, *args, **kwargs):  # noqa: ANN001, ANN202 - test double
        if forbidden in self.as_posix():
            touched.append(self.as_posix())
        return original(self, *args, **kwargs)

    monkeypatch.setattr(pathlib.Path, "read_text", spy)
    _load_live_go_evidence(REPO_ROOT, candidate_paths=[probe])

    assert touched == [], f"clearance read the forbidden packet directory: {touched}"


# ---------------------------------------------------------------------------
# Acceptance 2: unauthorized cohorts are still denied
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "probe",
    [
        "CLAUDE.md",
        "groundtruth-kb/src/groundtruth_kb/db.py",
        "scripts/check_protected_commit_authorization.py",
        "some/entirely/invented/path.py",
        "",
    ],
)
def test_unauthorized_cohort_is_denied(probe: str) -> None:
    packets, _errors, _count = _load_live_go_evidence(REPO_ROOT, candidate_paths=[probe])
    assert not any(path_authorized(packet, probe) for packet in packets), (
        f"{probe!r} cleared without a live GO authorizing it"
    )


def test_derivation_grants_nothing_when_no_thread_is_implementable(tmp_path: Path) -> None:
    """Deny-by-default: an empty project clears nothing and raises nothing."""
    (tmp_path / "bridge").mkdir()
    rows, errors = canonical_go_authorizations(tmp_path, candidate_paths=["anything.py"])
    assert rows == []
    assert isinstance(errors, list)


def test_errors_never_grant_clearance(tmp_path: Path) -> None:
    """A thread that fails to resolve must produce a diagnostic, not a row.

    The packet route's fail-closed contract is that a broken row still reports
    ``valid=False``; the canonical route's equivalent is that it emits no row at
    all. Both deny. This pins that a resolution failure cannot become clearance.
    """
    bridge = tmp_path / "bridge"
    bridge.mkdir()
    # Latest is GO, so the prefilter admits it, but there is no resolvable
    # proposal/GO pair behind it.
    (bridge / "broken-thread-001.md").write_text("GO\n", encoding="utf-8")

    rows, errors = canonical_go_authorizations(tmp_path)

    assert rows == []
    assert errors, "a thread that fails resolution must be reported, not silently dropped"
