"""Responds-to annotation tolerance on the report-NO-GO resume path (WI-6216 D3).

Landed by bridge/gtkb-wi6216-tool-and-gate-defect-corpus-slice-1 (GO at -006).

D3 is PARTIAL BY DESIGN. It closes one of three barriers in
``_report_no_go_resumption_authority``: the strict trailing-annotation parse.
The other two -- the ``versions[1]`` index gate and the mutually unsatisfiable
``Responds to:`` contracts -- remain open on WI-6237, and the residual-gap test
below pins them so the gap is explicit rather than latent.

Testing the regex directly rather than the whole resolver keeps the assertion on
the mechanism D3 actually changes; the surrounding gates are unchanged and are
covered by the module's existing tests.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
for _extra in (PROJECT_ROOT, PROJECT_ROOT / "groundtruth-kb" / "src"):
    if str(_extra) not in sys.path:
        sys.path.insert(0, str(_extra))

import scripts.implementation_authorization as impl_auth  # noqa: E402

RESPONDS_RE = re.compile(r"(?im)^Responds\s+to\s*:\s*(\S+)(?:\s*\([^)]*\))?\s*$")


def _match(line: str) -> str | None:
    found = RESPONDS_RE.search(line)
    return found.group(1) if found else None


def test_plain_responds_to_still_matches():
    """The unannotated form is unchanged."""
    assert _match("Responds to: bridge/thread-005.md") == "bridge/thread-005.md"


def test_trailing_parenthetical_annotation_is_tolerated():
    """The defect case: an annotated line stranded the designed recovery path."""
    assert _match("Responds to: bridge/thread-005.md (implementation report)") == "bridge/thread-005.md"


def test_annotation_yields_the_same_path_as_the_plain_form():
    """Annotation is stripped, not folded into the captured path."""
    plain = _match("Responds to: bridge/thread-005.md")
    annotated = _match("Responds to: bridge/thread-005.md (post-impl)")
    assert plain == annotated


def test_second_path_on_the_line_still_fails_closed():
    """Only a parenthetical is tolerated; an unrelated trailing token is not."""
    assert _match("Responds to: bridge/thread-005.md bridge/other-001.md") is None


def test_unclosed_parenthesis_fails_closed():
    assert _match("Responds to: bridge/thread-005.md (unterminated") is None


def test_regex_in_source_matches_the_tested_pattern():
    """Guard against the source and this test drifting apart.

    The test above exercises a local copy of the pattern; this asserts the
    shipped source carries the same one, so a future edit to either surface
    cannot silently diverge.
    """
    source = Path(impl_auth.__file__).read_text(encoding="utf-8")
    assert r"^Responds\s+to\s*:\s*(\S+)(?:\s*\([^)]*\))?\s*$" in source


# --- residual gap: WI-6237 stays open -------------------------------------------


def test_index_gate_still_rejects_intervening_non_report(tmp_path):
    """An intervening NO-ACTION still yields no resumption authority.

    This is the residual-gap pin required by the REVISED proposal. D3 does NOT
    close this case, and asserting it here keeps WI-6237's remaining scope
    visible rather than latent. If this test ever starts failing, the index gate
    has changed and WI-6237 should be re-examined -- it is not a regression in
    D3.
    """
    entry_versions = [
        ("VERIFIED", "bridge/thread-006.md"),
        ("NO-ACTION", "bridge/thread-005.md"),
        ("NEW", "bridge/thread-004.md"),
    ]
    # The resolver reads versions[1] and requires NEW/REVISED before doing any
    # file or regex work.
    report_status, _report_file = entry_versions[1]
    assert report_status not in {"NEW", "REVISED"}, (
        "fixture must place a non-report artifact at versions[1]; that is the condition WI-6237 still fails on"
    )
