# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for scripts/autonomous_dispatch_loop_health.py.

Authority: bridge/gtkb-wi4742-autonomous-dispatch-loop-health-001.md GO at -002.
Specs: GOV-FILE-BRIDGE-AUTHORITY-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Import the module under test
# ---------------------------------------------------------------------------

_SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import autonomous_dispatch_loop_health as adlh  # noqa: E402

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_bridge(bridge_dir: Path, slug: str, number: int, status: str, body: str = "") -> Path:
    """Write a minimal bridge file with the given status token as the first line."""
    p = bridge_dir / f"{slug}-{number:03d}.md"
    content = f"{status}\n\n{body}"
    p.write_text(content, encoding="utf-8")
    return p


def _complete_chain(bridge_dir: Path, slug: str, *, wi: str = "WI-9999", session_id: str = "abc123") -> None:
    """Write a minimal complete lifecycle chain: proposal → GO → impl report → VERIFIED."""
    _write_bridge(bridge_dir, slug, 1, "NEW", f"Work Item: {wi}")
    _write_bridge(bridge_dir, slug, 2, "GO")
    _write_bridge(
        bridge_dir,
        slug,
        3,
        "NEW",
        f"Work Item: {wi}\nauthor_session_context_id: {session_id}",
    )
    _write_bridge(bridge_dir, slug, 4, "VERIFIED")


# ---------------------------------------------------------------------------
# _extract_status
# ---------------------------------------------------------------------------


def test_extract_status_basic_tokens():
    for status in ("NEW", "REVISED", "GO", "NO-GO", "VERIFIED", "ADVISORY", "DEFERRED"):
        assert adlh._extract_status(f"{status}\n\nsome body") == status


def test_extract_status_lowercase_accepted():
    assert adlh._extract_status("go\n\nbody") == "GO"


def test_extract_status_unknown_first_line():
    assert adlh._extract_status("## This is a heading\nsome body") == "UNKNOWN"


def test_extract_status_empty_file():
    assert adlh._extract_status("") == "EMPTY"


def test_extract_status_leading_blank_lines():
    assert adlh._extract_status("\n\n  \nNEW\nbody") == "NEW"


# ---------------------------------------------------------------------------
# _classify_version
# ---------------------------------------------------------------------------


def test_classify_version_first_new_is_proposal():
    v = adlh.BridgeVersion(path=Path("x-001.md"), number=1, status="NEW", raw_text="")
    assert adlh._classify_version(v, None) == "proposal"


def test_classify_version_new_after_go_is_implementation_report():
    v = adlh.BridgeVersion(path=Path("x-003.md"), number=3, status="NEW", raw_text="")
    assert adlh._classify_version(v, "GO") == "implementation_report"


def test_classify_version_revised():
    v = adlh.BridgeVersion(path=Path("x-003.md"), number=3, status="REVISED", raw_text="")
    assert adlh._classify_version(v, "NO-GO") == "revised_report"


def test_classify_version_go():
    v = adlh.BridgeVersion(path=Path("x-002.md"), number=2, status="GO", raw_text="")
    assert adlh._classify_version(v, "NEW") == "go"


def test_classify_version_no_go():
    v = adlh.BridgeVersion(path=Path("x-004.md"), number=4, status="NO-GO", raw_text="")
    assert adlh._classify_version(v, "NEW") == "no_go"


def test_classify_version_verified():
    v = adlh.BridgeVersion(path=Path("x-005.md"), number=5, status="VERIFIED", raw_text="")
    assert adlh._classify_version(v, "NEW") == "verified"


# ---------------------------------------------------------------------------
# validate_loop — no files
# ---------------------------------------------------------------------------


def test_validate_loop_no_files(tmp_path):
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    result = adlh.validate_loop(bridge_dir, "nonexistent-slug")
    assert result.complete is False
    assert result.version_count == 0
    assert "nonexistent-slug" in result.errors[0]
    assert set(result.phases_missing) == set(adlh.REQUIRED_LIFECYCLE_PHASES)


# ---------------------------------------------------------------------------
# validate_loop — complete chain
# ---------------------------------------------------------------------------


def test_validate_loop_complete_chain(tmp_path):
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    _complete_chain(bridge_dir, "test-slug", wi="WI-1234", session_id="sess-abc")
    result = adlh.validate_loop(bridge_dir, "test-slug", expected_wi="WI-1234", expected_session_id="sess-abc")
    assert result.complete is True
    assert result.phases_missing == []
    assert set(result.phases_present) == {"proposal", "go", "implementation_report", "verified"}
    assert result.wi_found is True
    assert result.session_found is True
    assert result.version_count == 4
    assert result.errors == []


def test_validate_loop_complete_without_expected_wi(tmp_path):
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    _complete_chain(bridge_dir, "test-slug", wi="WI-5555")
    result = adlh.validate_loop(bridge_dir, "test-slug")
    # wi_found is True when any WI is present and no expected_wi is given
    assert result.wi_found is True
    assert result.complete is True


# ---------------------------------------------------------------------------
# validate_loop — missing phases
# ---------------------------------------------------------------------------


def test_validate_loop_missing_go(tmp_path):
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    _write_bridge(bridge_dir, "test-slug", 1, "NEW", "Work Item: WI-1")
    _write_bridge(bridge_dir, "test-slug", 2, "NO-GO")
    _write_bridge(bridge_dir, "test-slug", 3, "REVISED", "Work Item: WI-1")
    # NO-GO branch: no GO → no implementation_report → no verified
    result = adlh.validate_loop(bridge_dir, "test-slug", expected_wi="WI-1")
    assert result.complete is False
    assert "go" in result.phases_missing
    assert "implementation_report" in result.phases_missing
    assert "verified" in result.phases_missing


def test_validate_loop_missing_verified(tmp_path):
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    _write_bridge(bridge_dir, "test-slug", 1, "NEW", "Work Item: WI-2")
    _write_bridge(bridge_dir, "test-slug", 2, "GO")
    _write_bridge(bridge_dir, "test-slug", 3, "NEW", "Work Item: WI-2")
    result = adlh.validate_loop(bridge_dir, "test-slug", expected_wi="WI-2")
    assert result.complete is False
    assert "verified" in result.phases_missing
    assert "go" in result.phases_present
    assert "implementation_report" in result.phases_present


# ---------------------------------------------------------------------------
# validate_loop — WI and session evidence
# ---------------------------------------------------------------------------


def test_validate_loop_wrong_wi(tmp_path):
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    _complete_chain(bridge_dir, "test-slug", wi="WI-9999")
    result = adlh.validate_loop(bridge_dir, "test-slug", expected_wi="WI-0001")
    assert result.wi_found is False
    assert result.complete is False
    assert any("WI-0001" in e for e in result.errors)


def test_validate_loop_missing_session_id(tmp_path):
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    _complete_chain(bridge_dir, "test-slug", wi="WI-9999", session_id="known-session")
    result = adlh.validate_loop(bridge_dir, "test-slug", expected_wi="WI-9999", expected_session_id="other-session")
    # session mismatch → warning, not error; complete may still be False due to session
    assert result.session_found is False
    assert any("other-session" in w for w in result.warnings)


# ---------------------------------------------------------------------------
# validate_loop — NO-GO/REVISED cycle still passes if VERIFIED reached
# ---------------------------------------------------------------------------


def test_validate_loop_with_nogo_revised_cycle(tmp_path):
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    slug = "test-slug"
    _write_bridge(bridge_dir, slug, 1, "NEW", "Work Item: WI-7")
    _write_bridge(bridge_dir, slug, 2, "GO")
    _write_bridge(bridge_dir, slug, 3, "NEW", "Work Item: WI-7\nauthor_session_context_id: sess1")
    _write_bridge(bridge_dir, slug, 4, "NO-GO")
    _write_bridge(bridge_dir, slug, 5, "REVISED", "Work Item: WI-7")
    _write_bridge(bridge_dir, slug, 6, "VERIFIED")
    result = adlh.validate_loop(bridge_dir, slug, expected_wi="WI-7", expected_session_id="sess1")
    assert result.complete is True
    assert "no_go" in result.phases_present
    assert "revised_report" in result.phases_present
    assert "verified" in result.phases_present


# ---------------------------------------------------------------------------
# JSON output
# ---------------------------------------------------------------------------


def test_validate_loop_json_output(tmp_path):
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    _complete_chain(bridge_dir, "test-slug")
    result = adlh.validate_loop(bridge_dir, "test-slug")
    d = result.to_dict()
    assert isinstance(d, dict)
    required_keys = {
        "slug",
        "complete",
        "phases_present",
        "phases_missing",
        "wi_found",
        "session_found",
        "version_count",
        "lifecycle",
        "errors",
        "warnings",
    }
    assert required_keys.issubset(set(d.keys()))
    # Ensure it serialises to valid JSON
    assert json.loads(json.dumps(d)) == d


# ---------------------------------------------------------------------------
# CLI — exit code
# ---------------------------------------------------------------------------


def test_main_exit_code_zero_on_complete(tmp_path):
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    _complete_chain(bridge_dir, "test-slug", wi="WI-1")
    rc = adlh.main(
        [
            "--bridge-id",
            "test-slug",
            "--expected-wi",
            "WI-1",
            "--bridge-dir",
            str(bridge_dir),
        ]
    )
    assert rc == 0


def test_main_exit_code_nonzero_on_incomplete(tmp_path):
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    _write_bridge(bridge_dir, "test-slug", 1, "NEW")
    rc = adlh.main(["--bridge-id", "test-slug", "--bridge-dir", str(bridge_dir)])
    assert rc != 0


def test_main_json_flag_produces_valid_json(tmp_path, capsys):
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    _complete_chain(bridge_dir, "test-slug")
    adlh.main(["--bridge-id", "test-slug", "--bridge-dir", str(bridge_dir), "--json"])
    captured = capsys.readouterr()
    d = json.loads(captured.out)
    assert d["complete"] is True


# ---------------------------------------------------------------------------
# Live reference chain (soft test — skip if bridge/ not present)
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parents[2]
_BRIDGE_DIR = _REPO_ROOT / "bridge"
_REFERENCE_SLUG = adlh.REFERENCE_BRIDGE_ID


@pytest.mark.skipif(
    not (_BRIDGE_DIR / f"{_REFERENCE_SLUG}-001.md").is_file(),
    reason="Live reference bridge chain not present",
)
def test_live_reference_chain_is_complete():
    result = adlh.validate_loop(
        _BRIDGE_DIR,
        _REFERENCE_SLUG,
        expected_wi=adlh.REFERENCE_WI,
        expected_session_id=adlh.REFERENCE_SESSION_ID,
    )
    assert result.complete is True, (
        f"Reference chain incomplete: phases_missing={result.phases_missing}, errors={result.errors}"
    )
