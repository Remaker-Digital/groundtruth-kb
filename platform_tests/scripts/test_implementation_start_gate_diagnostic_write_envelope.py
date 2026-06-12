"""Regression coverage for WI-4251 diagnostic-write envelope handling."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import implementation_start_gate as gate  # noqa: E402


def _shell_payload(command: str) -> dict[str, object]:
    return {
        "cwd": str(ROOT),
        "tool_name": "Bash",
        "tool_input": {"command": command},
    }


def test_wrap_capture_transcript_manifest_write_is_allowed_without_authorization() -> None:
    payload = _shell_payload("python scripts/wrap_capture_transcript.py --session-id S4251")

    assert gate.changed_paths(payload) == ([".groundtruth/session/snapshots/S4251/manifest.json"], True)
    assert gate.gate_decision(payload) == {}


def test_wrap_capture_transcript_custom_snapshot_root_inside_envelope_is_allowed() -> None:
    payload = _shell_payload(
        "python scripts/wrap_capture_transcript.py "
        "--session-id S4251 --snapshot-root .groundtruth/session/snapshots/custom-root"
    )

    assert gate.changed_paths(payload) == (
        [".groundtruth/session/snapshots/custom-root/S4251/manifest.json"],
        True,
    )
    assert gate.gate_decision(payload) == {}


def test_wrap_scan_hygiene_write_report_under_gtkb_state_is_allowed_without_authorization() -> None:
    payload = _shell_payload(
        "python scripts/wrap_scan_hygiene.py --report-format json --write-report .gtkb-state/wrap/hygiene.json"
    )

    assert gate.changed_paths(payload) == ([".gtkb-state/wrap/hygiene.json"], True)
    assert gate.gate_decision(payload) == {}


def test_wrap_scan_consistency_redirect_under_gtkb_state_is_allowed_without_authorization() -> None:
    payload = _shell_payload(
        "python scripts/wrap_scan_consistency.py --report-format markdown > .gtkb-state/wrap/consistency.md"
    )

    assert gate.changed_paths(payload) == ([".gtkb-state/wrap/consistency.md"], True)
    assert gate.gate_decision(payload) == {}


def test_wrap_scan_hygiene_mixed_diagnostic_and_protected_writes_still_blocks() -> None:
    payload = _shell_payload(
        "python scripts/wrap_scan_hygiene.py --report-format json "
        "--write-report .gtkb-state/wrap/hygiene.json > config/wrap-hygiene.json"
    )

    result = gate.gate_decision(payload)

    assert result["decision"] == "block"
    assert "authorization packet" in result["reason"]


def test_wrap_capture_transcript_snapshot_root_outside_envelope_still_blocks() -> None:
    payload = _shell_payload(
        "python scripts/wrap_capture_transcript.py --session-id S4251 --snapshot-root config/wrap-snapshots"
    )

    result = gate.gate_decision(payload)

    assert result["decision"] == "block"
    assert "authorization packet" in result["reason"]
