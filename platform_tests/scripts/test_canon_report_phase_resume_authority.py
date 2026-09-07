"""Implementation authorization recognizes the canon section 6 report phase (WI-7744).

Canon section 6 gives a thread a report phase after its ``GO``: the post-implementation report is
``READY`` and its rejection is ``NOT-READY``, with ``READY`` the lawful successor to ``NOT-READY``.
Correcting a rejected report therefore means implementing again and refiling ``READY``.

Three gates in ``scripts/implementation_authorization.py`` were written against the retired
vocabulary and refused every canon-conformant thread:

1. ``_post_go_chain_state`` had no ``NOT-READY`` branch, so it fell through to its defensive
   ``awaiting_review``.
2. ``_report_no_go_resumption_authority`` required ``entry.latest_status == "NO-GO"``.
3. the same function required the reviewed report to be ``NEW`` or ``REVISED``.

Each alone closes the path, and gate 1 is called from inside the function gates 2 and 3 guard, so all
three had to move together. The asymmetry they produced was exact: ``['NO-GO', 'NEW']`` classified as
``resumable`` while the identical canon shape ``['NOT-READY', 'READY']`` classified as
``awaiting_review``.

**The guard against over-fixing is as load-bearing as the fix.** A latest status of ``READY`` means a
report is under review; authorizing mutation then would invalidate the snapshot the reviewer is
reading. ``test_a_report_under_review_is_still_protected`` asserts that ``READY`` stays
``awaiting_review``, and per the GO's condition 1, if it ever reports ``resumable`` the change must be
reverted rather than adjusted.

Bound to TEST-12611.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

import implementation_authorization as ia  # noqa: E402

#: Chains carrying a live canon-conformant shape: a ``GO``, a ``READY`` report after it, and a
#: ``NOT-READY`` rejection latest. Used for the live-state assertion the GO required rather than only
#: a fixture. If both are later corrected past ``NOT-READY`` the test skips rather than failing, since
#: its subject is the classifier and not these particular threads.
LIVE_NOT_READY_CHAINS = (
    "gtkb-wi6252-disposable-postgresql-integration-bootstrap",
    "gtkb-wi6252-native-postgresql-integration-verification",
)


# --- classification family --------------------------------------------------------------------


@pytest.mark.parametrize(
    ("statuses_after_go", "expected"),
    [
        # The defect: identical events, two spellings, one answer before this change.
        (["NOT-READY", "READY"], "resumable"),
        (["NO-GO", "NEW"], "resumable"),
        (["NO-GO", "REVISED"], "resumable"),
        # The guard: a report under review must never be resumable.
        (["READY"], "awaiting_review"),
        (["NEW"], "awaiting_review"),
        (["REVISED"], "awaiting_review"),
        # Unchanged by this work.
        (["VERIFIED", "READY"], "terminal"),
        ([], "latest_is_go"),
    ],
)
def test_post_go_chain_state_classifies_both_vocabularies(statuses_after_go: list[str], expected: str) -> None:
    """The canon and legacy spellings of the same event classify the same way.

    ``statuses_after_go`` is newest-first, matching the caller.
    """
    assert ia._post_go_chain_state(statuses_after_go) == expected


def test_a_report_under_review_is_still_protected() -> None:
    """The over-fix guard, asserted on its own rather than only as a parametrization.

    Stated separately because it is the row that decides whether this change was correct or merely
    permissive. Per the GO's condition 1: if this ever reports ``resumable``, the change authorized
    mutation while a report was under review and must be reverted, not adjusted.
    """
    assert ia._post_go_chain_state(["READY"]) == "awaiting_review"
    assert ia._post_go_chain_state(["NEW"]) == "awaiting_review"


# --- resume-authority family ------------------------------------------------------------------


def _live_resume(slug: str) -> object | None:
    entry = ia.bridge_entry(REPO_ROOT, slug)
    if entry.latest_status != "NOT-READY":
        pytest.skip(f"{slug} is no longer at NOT-READY (now {entry.latest_status})")
    go_files = [path for status, path in entry.versions if status == "GO"]
    if not go_files:
        pytest.skip(f"{slug} has no GO in its chain")
    return ia._report_no_go_resumption_authority(REPO_ROOT, {"bridge_id": slug, "go_file": go_files[0]})


@pytest.mark.parametrize("slug", LIVE_NOT_READY_CHAINS)
def test_a_live_canon_chain_at_not_ready_can_resume(slug: str) -> None:
    """Against real bridge state, not a fixture, per the GO's condition 4.

    Before this change both chains returned ``None`` here, which is what made a corrected report
    unauthorizable through any canon-conformant route.
    """
    authority = _live_resume(slug)
    assert authority is not None, f"{slug}: a canon-conformant NOT-READY chain must be resumable"
    assert authority["state"] == "resumable_report_no_go"
    assert authority["originating_go_file"].startswith("bridge/")


def test_the_resume_predicate_still_refuses_a_thread_with_no_go() -> None:
    """A chain with no ``GO`` cannot resume, whatever its latest status.

    The complement of the tests above: widening which rejections resume must not widen *what* they
    resume from.
    """
    assert ia._report_no_go_resumption_authority(REPO_ROOT, {"bridge_id": "", "go_file": ""}) is None
    assert (
        ia._report_no_go_resumption_authority(
            REPO_ROOT, {"bridge_id": "gtkb-wi7744-canon-report-phase-resume-authority", "go_file": ""}
        )
        is None
    )


# --- derivation family ------------------------------------------------------------------------


def test_the_status_sets_derive_from_the_vocabulary_module() -> None:
    """The sets are derived, not restated, which is the point of the fix.

    A hand-maintained copy in this module is what produced the defect: WI-7684 already replaced one
    status literal here with a derivation and left a comment naming ``READY`` and ``NOT-READY`` as the
    omitted tokens, while the predicate forty lines below still carried them.
    """
    from groundtruth_kb.bridge.vocabulary import (
        LOYAL_OPPOSITION_ACTIONABLE_STATUSES,
        PRIME_ACTIONABLE_STATUSES,
    )

    assert PRIME_ACTIONABLE_STATUSES - {"GO"} == ia._RESUMABLE_REJECTION_STATUSES
    assert ia._AWAITING_REVIEW_STATUSES == LOYAL_OPPOSITION_ACTIONABLE_STATUSES
    # The canon tokens are present in the derived sets rather than assumed.
    assert "NOT-READY" in ia._RESUMABLE_REJECTION_STATUSES
    assert "NO-GO" in ia._RESUMABLE_REJECTION_STATUSES
    assert "GO" not in ia._RESUMABLE_REJECTION_STATUSES
    assert "READY" in ia._AWAITING_REVIEW_STATUSES


def test_no_literal_status_set_survives_in_the_two_repaired_functions() -> None:
    """The literals are gone from the functions that carried them.

    Scoped to the two repaired functions rather than the whole file: other functions legitimately
    compare against a single status, and a file-wide ban would fail on unrelated correct code.
    """
    source = (REPO_ROOT / "scripts" / "implementation_authorization.py").read_text(encoding="utf-8")

    offenders: list[str] = []
    for name in ("_post_go_chain_state", "_report_no_go_resumption_authority"):
        start = source.index(f"def {name}(")
        end = source.index("\ndef ", start + 1)
        body = source[start:end]
        for literal in ('{"NEW", "REVISED"}', '!= "NO-GO"', '== "NO-GO"'):
            if literal in body:
                offenders.append(f"{name}: {literal}")

    assert offenders == [], f"a hand-maintained status literal returned: {offenders}"
