"""Executable advisory-prompt assertions for SPEC-INTAKE-8161dc.

Maps TEST-11408, TEST-11418, TEST-11419, and TEST-11420 to generated role,
startup, deliberation, and build envelope surfaces.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from groundtruth_kb.activity.profiles import ADVISORY_PROPOSAL_SEMANTIC_MARKERS, load_activity_profiles
from groundtruth_kb.session.envelope import PRELOAD_STATES
from groundtruth_kb.session.topic_router import render_topic_context

REPO_ROOT = Path(__file__).resolve().parents[2]
ADVISORY_DISCOVERY_COMMAND = ("gt", "bridge", "dispatch", "report", "--json", "--compact")
ADVISORY_DISCOVERY_COMMAND_TEXT = " ".join(ADVISORY_DISCOVERY_COMMAND)


def _read(relative: str) -> str:
    return (REPO_ROOT / relative).read_text(encoding="utf-8")


def _joined(values: object) -> str:
    if isinstance(values, dict):
        return " ".join(_joined(value) for value in values.values())
    if isinstance(values, list):
        return " ".join(_joined(value) for value in values)
    return str(values)


def _rendered_activity_context(activity: str) -> str:
    return render_topic_context(
        {
            "action": "open",
            "topic_type": activity,
            "project_root": str(REPO_ROOT),
            "topic": {"route_target": f"{activity}-route"},
        }
    )


def _assert_required_semantics(surface_name: str, text: str) -> None:
    normalized_text = " ".join(text.split())
    required_fragments = [
        "Advisory Proposal",
        "governed bridge artifact",
        "ADVISORY",
        "non-dispatchable",
        "not implementation approval",
        "bridge/TAFE/dispatcher status surfaces",
        "status-bearing",
        "bridge/",
        "primary Loyal Opposition mechanism for future-work initiation",
        "governed advisory intake/disposition",
        "CODEX-INSIGHT-DROPBOX",
        "independent-progress-assessments",
        "non-canonical session evidence",
    ]
    missing = [fragment for fragment in required_fragments if fragment not in normalized_text]
    assert not missing, f"{surface_name} missing advisory semantics: {missing}"


def _assert_advisory_discovery_command_executes() -> None:
    registered_cli_command = (
        sys.executable,
        "-m",
        "groundtruth_kb.cli",
        *ADVISORY_DISCOVERY_COMMAND[1:],
    )
    result = subprocess.run(
        registered_cli_command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, (
        f"{ADVISORY_DISCOVERY_COMMAND_TEXT!r} failed with stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    payload = json.loads(result.stdout)
    assert payload["schema_version"] == "gtkb.dispatch_workflow.v1"
    candidate_text = json.dumps(payload["queues"].get("prime_builder", {}).get("candidate_next", []))
    assert "ADVISORY" in candidate_text


def test_test11418_role_and_startup_scaffolds_teach_advisory_bridge_semantics() -> None:
    """TEST-11418: role/startup prompt surfaces carry Advisory Proposal semantics."""
    surfaces = {
        "startup index": _read("config/agent-control/SESSION-STARTUP-INDEX.md"),
        "Prime Builder overlay": _read("config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md"),
        "Loyal Opposition overlay": _read("config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md"),
    }

    for name, text in surfaces.items():
        _assert_required_semantics(name, text)


def test_test11419_deliberation_and_build_profiles_teach_advisory_progression() -> None:
    """TEST-11419: activity profiles render Advisory Proposal intake/disposition semantics."""
    profiles = load_activity_profiles(REPO_ROOT / "config" / "agent-control" / "activity-disposition-profiles.toml")
    for activity in ("deliberation", "build"):
        profile = profiles[activity]
        profile_text = " ".join(
            [
                " ".join(profile.terminology),
                _joined(profile.history_state),
                _joined(profile.direction),
            ]
        )
        _assert_required_semantics(f"{activity} activity profile", profile_text)
        _assert_required_semantics(f"{activity} rendered topic context", _rendered_activity_context(activity))


def test_test11408_session_envelope_preload_states_expose_advisory_access_path() -> None:
    """TEST-11408: generated session envelopes expose governed advisory access paths."""
    for activity in ("deliberation", "build"):
        preload_text = _joined(PRELOAD_STATES[activity])
        _assert_required_semantics(f"{activity} PRELOAD_STATES", preload_text)
        assert "gt bridge show <advisory-slug>" in preload_text
        assert ADVISORY_DISCOVERY_COMMAND_TEXT in preload_text

    _assert_advisory_discovery_command_executes()


def test_test11420_executable_assertion_covers_required_advisory_prompt_markers() -> None:
    """TEST-11420: the executable assertion owns all required semantic markers."""
    marker_text = " ".join(ADVISORY_PROPOSAL_SEMANTIC_MARKERS)
    _assert_required_semantics("ADVISORY_PROPOSAL_SEMANTIC_MARKERS", marker_text)
    for test_id in ("TEST-11408", "TEST-11418", "TEST-11419", "TEST-11420"):
        assert test_id in __doc__
