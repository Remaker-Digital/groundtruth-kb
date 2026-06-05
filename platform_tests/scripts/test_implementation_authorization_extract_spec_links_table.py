"""Tests for extract_spec_links table-format fallback per DCL-IMPL-AUTH-EXTRACT-SPEC-LINKS-TABLE-FORMAT-001.

Acceptance assertions verbatim from the DCL constraint body:
- BULLET_ONLY_PROPOSAL: bullet branch returns existing spec IDs (regression)
- TABLE_ONLY_PROPOSAL: table fallback returns first-cell tokens
- MIXED_BULLET_AND_TABLE_PROPOSAL: bullet results only (table dormant)
- EMPTY_TABLE_PROPOSAL: raises AuthorizationError
- TABLE_WITH_HEADER_AND_SEPARATOR: correctly filters header + separator
- TABLE_ROW_WITH_PLACEHOLDER_TEXT: raises AuthorizationError
- SLICE_2A_PROPOSAL_003_CONTENT: real-world self-verification
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.implementation_authorization import (
    AuthorizationError,
    _extract_spec_links_from_table,
    extract_spec_links,
)

# ---------------------------------------------------------------------------
# Bullet-only proposal (regression: existing behavior preserved)
# ---------------------------------------------------------------------------

BULLET_ONLY_PROPOSAL = """# Some bridge proposal

## Specification Links

- `GOV-FOO-001` — blocking — A bullet citation.
- `DCL-BAR-002` — blocking — Another bullet citation.
- `ADR-BAZ-003` — advisory — Third bullet citation.

## Other Section

Body.
"""


def test_bullet_only_proposal_returns_bullet_results() -> None:
    links = extract_spec_links(BULLET_ONLY_PROPOSAL)
    assert "GOV-FOO-001" in links
    assert "DCL-BAR-002" in links
    assert "ADR-BAZ-003" in links


# ---------------------------------------------------------------------------
# Table-only proposal (new behavior: table fallback)
# ---------------------------------------------------------------------------

TABLE_ONLY_PROPOSAL = """# Some bridge proposal

## Specification Links

| Spec | Severity | Trigger | How |
|------|----------|---------|-----|
| `GOV-TABLE-001` | blocking | path:bridge/** | satisfied |
| `DCL-TABLE-002` | blocking | content:Specification Links | satisfied |
| `ADR-TABLE-003` | advisory | content:artifact | acknowledged |

## Other Section

Body.
"""


def test_table_only_proposal_returns_first_cell_tokens() -> None:
    links = extract_spec_links(TABLE_ONLY_PROPOSAL)
    assert "GOV-TABLE-001" in links
    assert "DCL-TABLE-002" in links
    assert "ADR-TABLE-003" in links


# ---------------------------------------------------------------------------
# Mixed bullet + table proposal (bullet branch has precedence; table dormant)
# ---------------------------------------------------------------------------

MIXED_BULLET_AND_TABLE_PROPOSAL = """# Some bridge proposal

## Specification Links

- `GOV-BULLET-001` — blocking — A bullet that wins.
- `DCL-BULLET-002` — blocking — Another bullet.

| Spec | Severity |
|------|----------|
| `GOV-TABLE-DORMANT-001` | blocking |
| `DCL-TABLE-DORMANT-002` | blocking |

## Other Section

Body.
"""


def test_mixed_proposal_returns_bullet_results_only() -> None:
    links = extract_spec_links(MIXED_BULLET_AND_TABLE_PROPOSAL)
    assert "GOV-BULLET-001" in links
    assert "DCL-BULLET-002" in links
    # Table results are dormant when bullet branch found at least one link.
    assert "GOV-TABLE-DORMANT-001" not in links
    assert "DCL-TABLE-DORMANT-002" not in links


# ---------------------------------------------------------------------------
# Empty proposal (no spec-link citations in either format) → AuthorizationError
# ---------------------------------------------------------------------------

EMPTY_PROPOSAL = """# Some bridge proposal

## Specification Links

(intentionally empty)

## Other Section

Body.
"""


def test_empty_proposal_raises_authorization_error() -> None:
    with pytest.raises(AuthorizationError, match="no concrete specification links"):
        extract_spec_links(EMPTY_PROPOSAL)


# ---------------------------------------------------------------------------
# Table with header + separator: filters header row + separator row
# ---------------------------------------------------------------------------

TABLE_WITH_HEADER_AND_SEPARATOR = """# Some proposal

## Specification Links

| Spec | Severity | Notes |
|------|----------|-------|
| `GOV-HEADER-FILTER-001` | blocking | first data row |
| `DCL-HEADER-FILTER-002` | blocking | second data row |
"""


def test_table_filters_header_and_separator_rows() -> None:
    links = extract_spec_links(TABLE_WITH_HEADER_AND_SEPARATOR)
    # Header row "Spec" should NOT be in results; only the citations.
    assert "GOV-HEADER-FILTER-001" in links
    assert "DCL-HEADER-FILTER-002" in links
    assert "Spec" not in links


# ---------------------------------------------------------------------------
# Table row with placeholder text: raises AuthorizationError
# ---------------------------------------------------------------------------

TABLE_WITH_PLACEHOLDER_TEXT = """# Some proposal

## Specification Links

| Spec | Severity |
|------|----------|
| TBD | blocking |
| `GOV-CONCRETE-001` | blocking |
"""


def test_table_row_with_placeholder_raises() -> None:
    # The "TBD" row has no concrete citation AND matches PLACEHOLDER_RE
    with pytest.raises(AuthorizationError, match="placeholder"):
        extract_spec_links(TABLE_WITH_PLACEHOLDER_TEXT)


# ---------------------------------------------------------------------------
# Slice 2A -003 self-verification (real-world end-to-end)
# ---------------------------------------------------------------------------

SLICE_2A_003_PATH = Path("bridge/gtkb-platform-sot-consolidation-slice-2a-read-discipline-003.md")


@pytest.mark.skipif(not SLICE_2A_003_PATH.exists(), reason="Slice 2A -003 fixture not present")
def test_extract_spec_links_on_slice_2a_003() -> None:
    content = SLICE_2A_003_PATH.read_text(encoding="utf-8")
    links = extract_spec_links(content)
    # Per the DCL acceptance assertion: expected ~21 spec-ID tokens
    assert len(links) >= 15, f"expected at least 15 links from Slice 2A -003 table, got {len(links)}"
    # Spot-check some expected spec IDs
    assert "GOV-FILE-BRIDGE-AUTHORITY-001" in links
    assert "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001" in links
    assert "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001" in links


# ---------------------------------------------------------------------------
# Direct _extract_spec_links_from_table helper tests
# ---------------------------------------------------------------------------


def test_helper_empty_body_returns_empty() -> None:
    assert _extract_spec_links_from_table("") == []


def test_helper_prose_without_pipes_returns_empty() -> None:
    body = "Just some prose text\nwith no pipes at all\n"
    assert _extract_spec_links_from_table(body) == []


def test_helper_pipe_row_without_separator_skipped() -> None:
    # Single pipe row with no following separator: skipped.
    body = "| just-text | no-separator-follows |\nmore prose"
    assert _extract_spec_links_from_table(body) == []


def test_helper_inline_pipes_in_prose_not_table() -> None:
    # Prose that happens to mention pipes inline but has no separator row
    body = "Some sentence with | a | pipe | inline."
    assert _extract_spec_links_from_table(body) == []


def test_helper_data_row_with_no_first_cell_citation() -> None:
    # Row where first cell has no backtick-quoted token (just prose with no citation)
    # The bullet check requires PLACEHOLDER_RE match to raise; if no placeholder, just skip.
    body = "| Spec | Notes |\n|------|-------|\n| just prose first cell with no backticks | notes |\n"
    # No citation, no placeholder → just skipped (no error, no links)
    result = _extract_spec_links_from_table(body)
    assert result == []
