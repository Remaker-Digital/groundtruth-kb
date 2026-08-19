# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""WI-6541: bridge header is one block; element order is immaterial."""

from __future__ import annotations

import itertools
from pathlib import Path

from groundtruth_kb.bridge.read_commands import show_thread
from groundtruth_kb.bridge.versioned_files import (
    parse_bridge_header_block,
    status_from_bridge_file,
    status_from_bridge_text,
)

INIT = "::init gtkb pb"
OPEN = "::open build"
STATUS = "GO"


def test_header_block_order_is_immaterial() -> None:
    expected = None
    for order in itertools.permutations((INIT, OPEN, STATUS)):
        text = "\n".join(order) + "\n"
        parsed = parse_bridge_header_block(text)
        if expected is None:
            expected = parsed.status
        assert parsed.status == "GO"
        assert parsed.status == expected
        assert parsed.init_line == INIT
        assert parsed.open_line == OPEN


def test_status_only_advisory_and_withdrawn_are_well_formed() -> None:
    advisory = parse_bridge_header_block("ADVISORY\n")
    assert advisory.status == "ADVISORY"
    assert advisory.init_line is None
    assert advisory.open_line is None
    withdrawn = parse_bridge_header_block("WITHDRAWN\n")
    assert withdrawn.status == "WITHDRAWN"


def test_legacy_hash_heading_status_still_resolves() -> None:
    fixtures = (
        "# GO\n",
        "## NEW\n",
        "> VERIFIED\n",
        "- ADVISORY\n",
        "* NO-GO\n",
        "`REVISED`\n",
        "### NO-ACTION\n",
        "> # DEFERRED\n",
        "- `WITHDRAWN`\n",
    )
    expected = (
        "GO",
        "NEW",
        "VERIFIED",
        "ADVISORY",
        "NO-GO",
        "REVISED",
        "NO-ACTION",
        "DEFERRED",
        "WITHDRAWN",
    )
    for text, token in zip(fixtures, expected, strict=True):
        assert status_from_bridge_text(text) == token


def test_trailing_status_line_text_still_yields_token() -> None:
    parsed = parse_bridge_header_block("GO — extra commentary\n")
    assert parsed.status == "GO"
    assert parsed.status_line_exact is False


def test_package_readers_agree_on_envelope_first_file(tmp_path: Path) -> None:
    path = tmp_path / "bridge" / "shared-001.md"
    path.parent.mkdir(parents=True)
    path.write_text("\n".join((INIT, OPEN, "NEW", "Document: shared", "Version: 001", "")), encoding="utf-8")
    assert status_from_bridge_file(path) == "NEW"
    shown = show_thread(tmp_path, "shared")
    assert shown is not None
    assert shown["latest_status"] == "NEW"
    assert shown["version_chain"][0]["status_is_canonical"] is True
