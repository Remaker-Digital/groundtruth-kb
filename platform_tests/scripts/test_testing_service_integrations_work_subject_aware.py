"""Regression tests for the work-subject-aware testing/tool integration probe.

Per WI-3409 / ``bridge/gtkb-work-subject-aware-testing-integration-probe-003.md``
GO at ``-004``: the testing/tool integration probe must respect the active work
subject when selecting the GitHub repository query target. Before this fix,
``_testing_service_integrations`` unconditionally queried ``AGENT_RED_GITHUB_REPO``
regardless of session work subject, producing the symptom where a
``gtkb_infrastructure`` session saw Agent Red CI labeled as
"GT-KB Testing/tool rollup."

This module verifies four invariants:

1. ``gtkb_infrastructure`` session selects the GROUND_TRUTH_GITHUB_REPO env var.
2. ``application`` session selects the AGENT_RED_GITHUB_REPO env var.
3. Missing/malformed canonical work-subject state fails soft to ``gtkb_infrastructure``.
4. The startup rollup label includes the ``queried_repo`` identity so the data
   source is unambiguous regardless of which work subject is active.

The tests use ``unittest.mock.patch`` to isolate the probe from the live
``.claude/session/work-subject.json`` and the live ``gh`` CLI subprocess.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

# Place project root on sys.path so ``from scripts...`` resolves when this
# test runs under pytest from various working directories.
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.session_self_initialization import (  # noqa: E402
    _active_work_subject,
    _latest_github_workflow_runs,
    _render_current_project_state,
    _render_session_startup_briefing,
)
from scripts.workstream_focus import (  # noqa: E402
    FOCUS_APPLICATION,
    FOCUS_GTKB_INFRASTRUCTURE,
)


def _make_gh_run_result(stdout_json: str = "[]") -> object:
    """Return a fake subprocess.CompletedProcess for gh run list."""

    class _FakeCompleted:
        returncode = 0
        stdout = stdout_json
        stderr = ""

    return _FakeCompleted()


def test_gtkb_infrastructure_session_queries_gt_kb_repo(tmp_path: Path) -> None:
    """A session whose current_subject is gtkb_infrastructure must query
    GROUND_TRUTH_GITHUB_REPO, not AGENT_RED_GITHUB_REPO.

    Maps to GOV-SESSION-SELF-INITIALIZATION-001 (correct rollup data source).
    """
    captured_commands: list[list[str]] = []

    def _fake_run(cmd, **kwargs):  # noqa: ARG001
        captured_commands.append(list(cmd))
        return _make_gh_run_result(stdout_json="[]")

    fake_state = {"current_subject": FOCUS_GTKB_INFRASTRUCTURE}
    fake_env = {
        "GROUND_TRUTH_GITHUB_REPO": "Remaker-Digital/groundtruth-kb",
        "AGENT_RED_GITHUB_REPO": "mike-remakerdigital/agent-red",
    }
    with (
        patch("scripts.session_self_initialization._workstream_load_state", return_value=fake_state),
        patch(
            "scripts.session_self_initialization._local_env_value",
            side_effect=lambda _root, name: fake_env.get(name, ""),
        ),
        patch("scripts.session_self_initialization.subprocess.run", side_effect=_fake_run),
    ):
        result = _latest_github_workflow_runs(tmp_path, "authenticated")

    assert result["available"] is True
    assert result["queried_work_subject"] == FOCUS_GTKB_INFRASTRUCTURE
    assert result["queried_env_var"] == "GROUND_TRUTH_GITHUB_REPO"
    assert result["queried_repo"] == "Remaker-Digital/groundtruth-kb"
    # Verify the gh command was invoked with the GT-KB repo, not Agent Red.
    assert captured_commands, "subprocess.run was not invoked"
    cmd = captured_commands[0]
    assert "--repo" in cmd
    repo_index = cmd.index("--repo")
    assert cmd[repo_index + 1] == "Remaker-Digital/groundtruth-kb"


def test_application_session_queries_agent_red_repo(tmp_path: Path) -> None:
    """A session whose current_subject is application must query
    AGENT_RED_GITHUB_REPO, not GROUND_TRUTH_GITHUB_REPO.

    Maps to DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (each acceptance has a test).
    """
    captured_commands: list[list[str]] = []

    def _fake_run(cmd, **kwargs):  # noqa: ARG001
        captured_commands.append(list(cmd))
        return _make_gh_run_result(stdout_json="[]")

    fake_state = {"current_subject": FOCUS_APPLICATION}
    fake_env = {
        "GROUND_TRUTH_GITHUB_REPO": "Remaker-Digital/groundtruth-kb",
        "AGENT_RED_GITHUB_REPO": "mike-remakerdigital/agent-red",
    }
    with (
        patch("scripts.session_self_initialization._workstream_load_state", return_value=fake_state),
        patch(
            "scripts.session_self_initialization._local_env_value",
            side_effect=lambda _root, name: fake_env.get(name, ""),
        ),
        patch("scripts.session_self_initialization.subprocess.run", side_effect=_fake_run),
    ):
        result = _latest_github_workflow_runs(tmp_path, "authenticated")

    assert result["available"] is True
    assert result["queried_work_subject"] == FOCUS_APPLICATION
    assert result["queried_env_var"] == "AGENT_RED_GITHUB_REPO"
    assert result["queried_repo"] == "mike-remakerdigital/agent-red"
    # Verify the gh command was invoked with the Agent Red repo, not GT-KB.
    assert captured_commands, "subprocess.run was not invoked"
    cmd = captured_commands[0]
    assert "--repo" in cmd
    repo_index = cmd.index("--repo")
    assert cmd[repo_index + 1] == "mike-remakerdigital/agent-red"


def test_application_session_falls_back_to_agent_red_remote_when_env_empty(tmp_path: Path) -> None:
    """When AGENT_RED_GITHUB_REPO is empty AND an `agent-red` git remote
    exists, the application branch must use that remote's URL as the query
    target — per the proposal -003 IP-2 fallback chain and the LO -006
    NO-GO finding P1-001.

    Maps to GOV-SESSION-SELF-INITIALIZATION-001 (correct rollup data source
    even under partially-configured environments).
    """
    captured_commands: list[list[str]] = []

    def _fake_run(cmd, **kwargs):  # noqa: ARG001
        captured_commands.append(list(cmd))
        # Distinguish the `git remote get-url agent-red` probe from the gh call.
        if len(cmd) >= 4 and cmd[0] == "git" and cmd[1] == "remote":

            class _GitRemoteResult:
                returncode = 0
                stdout = "https://github.com/mike-remakerdigital/agent-red.git\n"
                stderr = ""

            return _GitRemoteResult()
        return _make_gh_run_result(stdout_json="[]")

    fake_state = {"current_subject": FOCUS_APPLICATION}
    # AGENT_RED_GITHUB_REPO intentionally empty to exercise the git-remote fallback.
    fake_env = {
        "GROUND_TRUTH_GITHUB_REPO": "Remaker-Digital/groundtruth-kb",
        "AGENT_RED_GITHUB_REPO": "",
    }
    with (
        patch("scripts.session_self_initialization._workstream_load_state", return_value=fake_state),
        patch(
            "scripts.session_self_initialization._local_env_value",
            side_effect=lambda _root, name: fake_env.get(name, ""),
        ),
        patch("scripts.session_self_initialization.subprocess.run", side_effect=_fake_run),
    ):
        result = _latest_github_workflow_runs(tmp_path, "authenticated")

    assert result["available"] is True
    assert result["queried_work_subject"] == FOCUS_APPLICATION
    assert result["queried_env_var"] == "AGENT_RED_GITHUB_REPO"
    assert result["queried_repo"] == "mike-remakerdigital/agent-red"
    # Verify the git remote probe and gh call were both made; gh must use the
    # agent-red remote URL slug, NOT the current origin.
    git_remote_calls = [c for c in captured_commands if c[:2] == ["git", "remote"]]
    gh_calls = [c for c in captured_commands if c[:1] == ["gh"]]
    assert git_remote_calls, "expected git remote get-url agent-red probe"
    assert git_remote_calls[0] == ["git", "remote", "get-url", "agent-red"]
    assert gh_calls, "expected gh run list invocation"
    assert "--repo" in gh_calls[0]
    repo_index = gh_calls[0].index("--repo")
    assert gh_calls[0][repo_index + 1] == "mike-remakerdigital/agent-red"


def test_application_session_returns_no_query_when_no_target(tmp_path: Path) -> None:
    """When AGENT_RED_GITHUB_REPO is empty AND no `agent-red` git remote
    exists, the application branch must return a no-recent-run result
    rather than invoking `gh run list` (which would silently query the
    current `origin` remote). Per LO -006 NO-GO finding P1-001.

    Maps to GOV-SESSION-SELF-INITIALIZATION-001 (avoid cross-subject coupling).
    """
    captured_commands: list[list[str]] = []

    def _fake_run(cmd, **kwargs):  # noqa: ARG001
        captured_commands.append(list(cmd))
        # `agent-red` remote does not exist: git returns non-zero.
        if len(cmd) >= 4 and cmd[0] == "git" and cmd[1] == "remote":

            class _GitRemoteMissing:
                returncode = 2
                stdout = ""
                stderr = "fatal: No such remote 'agent-red'\n"

            return _GitRemoteMissing()
        return _make_gh_run_result(stdout_json="[]")

    fake_state = {"current_subject": FOCUS_APPLICATION}
    fake_env = {
        "GROUND_TRUTH_GITHUB_REPO": "Remaker-Digital/groundtruth-kb",
        "AGENT_RED_GITHUB_REPO": "",
    }
    with (
        patch("scripts.session_self_initialization._workstream_load_state", return_value=fake_state),
        patch(
            "scripts.session_self_initialization._local_env_value",
            side_effect=lambda _root, name: fake_env.get(name, ""),
        ),
        patch("scripts.session_self_initialization.subprocess.run", side_effect=_fake_run),
    ):
        result = _latest_github_workflow_runs(tmp_path, "authenticated")

    # Must return a no-recent-run result (no implicit gh query against origin).
    assert result["available"] is False
    assert result["reason"] == "application_session_missing_agent_red_target"
    assert result["queried_work_subject"] == FOCUS_APPLICATION
    assert result["queried_env_var"] == "AGENT_RED_GITHUB_REPO"
    assert result["queried_repo"] is None
    # CRITICAL: gh run list MUST NOT have been invoked when no target was found.
    gh_calls = [c for c in captured_commands if c[:1] == ["gh"]]
    assert not gh_calls, f"gh was invoked when no agent-red target exists: {gh_calls}"


def test_missing_work_subject_defaults_to_gtkb_infrastructure(tmp_path: Path) -> None:
    """When the canonical work-subject state is missing or malformed, the
    probe must fail-soft to gtkb_infrastructure (the canonical default for
    a clean GT-KB checkout).

    Maps to GOV-SESSION-SELF-INITIALIZATION-001 (graceful default behavior).
    """

    # Simulate load_state raising (file not present / unreadable / parse error).
    def _raising_load(*_args, **_kwargs):
        raise FileNotFoundError("simulated missing canonical state")

    fake_env = {
        "GROUND_TRUTH_GITHUB_REPO": "Remaker-Digital/groundtruth-kb",
        "AGENT_RED_GITHUB_REPO": "mike-remakerdigital/agent-red",
    }
    with (
        patch("scripts.session_self_initialization._workstream_load_state", side_effect=_raising_load),
        patch(
            "scripts.session_self_initialization._local_env_value",
            side_effect=lambda _root, name: fake_env.get(name, ""),
        ),
        patch("scripts.session_self_initialization.subprocess.run", return_value=_make_gh_run_result()),
    ):
        subject = _active_work_subject(tmp_path)
        result = _latest_github_workflow_runs(tmp_path, "authenticated")

    assert subject == FOCUS_GTKB_INFRASTRUCTURE
    assert result["queried_work_subject"] == FOCUS_GTKB_INFRASTRUCTURE
    assert result["queried_env_var"] == "GROUND_TRUTH_GITHUB_REPO"
    assert result["queried_repo"] == "Remaker-Digital/groundtruth-kb"

    # Also assert the unrecognized-value case: state with a value not in the
    # canonical schema (e.g., 'something_else') falls back to gtkb_infrastructure.
    with (
        patch(
            "scripts.session_self_initialization._workstream_load_state",
            return_value={"current_subject": "something_unrecognized"},
        ),
    ):
        assert _active_work_subject(tmp_path) == FOCUS_GTKB_INFRASTRUCTURE


def test_rollup_label_includes_queried_repo() -> None:
    """The startup rollup label must include the ``queried_repo`` identity
    so the data source is unambiguous regardless of work subject.

    Maps to GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (rollup labeling matches data source).

    This test exercises the label-format invariant directly by constructing a
    ``quality_rollup`` dict matching the runtime shape and asserting the
    rendered string includes the queried_repo identity. The runtime rendering
    sites live in ``session_self_initialization.py`` around the Operating
    State and Current Project State sections (per the proposal IP-3 surface).
    """
    # Build a representative quality_rollup matching the runtime shape.
    quality = {
        "total": 22,
        "failing": 6,
        "manual": 6,
        "unknown": 2,
        "ready_or_passing": 6,
        "queried_repo": "Remaker-Digital/groundtruth-kb",
        "queried_work_subject": FOCUS_GTKB_INFRASTRUCTURE,
    }

    # Mirror the runtime rendering sites' label format (per WI-3409 final
    # implementation: queried_repo appended as parenthetical SUFFIX so the
    # pre-existing "Testing/tool rollup:" / "Testing/tools:" label-format
    # contracts are preserved for downstream parsing).
    operating_state_label = (
        f"- Testing/tools: "
        f"{quality.get('failing', 'unknown')} failing, "
        f"{quality.get('manual', 'unknown')} manual, "
        f"{quality.get('ready_or_passing', 'unknown')} ready/passing "
        f"(queried repo: {quality.get('queried_repo') or 'unknown'})."
    )
    subject_label = "GT-KB"
    current_state_label = (
        f"- {subject_label} Testing/tool rollup: "
        f"{quality.get('failing', 'unknown')} failing, "
        f"{quality.get('manual', 'unknown')} manual, "
        f"{quality.get('ready_or_passing', 'unknown')} ready/passing "
        f"(queried repo: {quality.get('queried_repo') or 'unknown'})"
    )

    # Both rendering sites must include the queried_repo identity.
    assert "queried repo: Remaker-Digital/groundtruth-kb" in operating_state_label
    assert "queried repo: Remaker-Digital/groundtruth-kb" in current_state_label

    # Pre-existing label-format contracts must be preserved (the colon
    # immediately follows "Testing/tools" / "Testing/tool rollup").
    assert "Testing/tools:" in operating_state_label
    assert "Testing/tool rollup:" in current_state_label

    # Fallback case: when queried_repo is None/missing, label must surface
    # "unknown" rather than a stale-looking literal repo name.
    quality_unknown = dict(quality)
    quality_unknown["queried_repo"] = None
    fallback_label = (
        f"- Testing/tools: "
        f"{quality_unknown.get('failing', 'unknown')} failing "
        f"(queried repo: {quality_unknown.get('queried_repo') or 'unknown'})"
    )
    assert "queried repo: unknown" in fallback_label


def _build_minimal_model(queried_repo: str | None = "Remaker-Digital/groundtruth-kb") -> dict:
    """Build a minimal but valid model dict for _render_session_startup_briefing
    and _render_current_project_state, populated with a quality_rollup that
    exposes queried_repo.
    """
    return {
        "role": {
            "assumed_role": "Prime Builder",
            "role_mapping_source": "harness-state/role-assignments.json",
            "harness_id": "B",
            "harness_identity_source": "harness-state/harness-identities.json",
        },
        "metrics": {
            "contention": {"raw_latest_status_counts": {}, "actionable_count": 0},
            "regression": {"release_blocker_count": 0},
            "drift": {"changed_path_count": 0},
            "membase": {
                "project_state_rollup": {"active_project_count": 0, "non_terminal_work_items": 0, "projects": []}
            },
            "backlog": {"active_item_count": 0},
        },
        "infrastructure": {
            "dev_environment_inventory": {},
            "harness_parity": {},
            "gtkb_upgrade_posture": {"package_version": "test", "upgrade_plan": {"mutating_action_count": 0}},
            "testing_service_integrations": {
                "github": {"queried_repo": queried_repo, "queried_work_subject": FOCUS_GTKB_INFRASTRUCTURE}
            },
            "release_inventory": {},
        },
        "dashboard_intelligence": {
            "release_readiness": {"status": "green", "blocker_count": 0, "blockers": []},
            "quality_rollup": {
                "total": 22,
                "failing": 6,
                "manual": 6,
                "unknown": 2,
                "ready_or_passing": 6,
                "queried_repo": queried_repo,
                "queried_work_subject": FOCUS_GTKB_INFRASTRUCTURE,
            },
            "action_center": [],
            "data_freshness": {"generated_at": "2026-05-28T00:00:00Z"},
        },
        "workstream_focus": {
            "current_label": "GT-KB Infrastructure Focus",
            "topology_mode": "multi_harness",
            "bridge_role_slot": "shared",
            "application_label": "Agent Red demo adopter",
        },
        "dashboard_opening": {"startup_open_requested": True, "mode": "harness_browser"},
        "generated_at": "2026-05-28T00:00:00Z",
        "top_priority_actions": [],
    }


def test_render_session_startup_briefing_includes_queried_repo_at_runtime() -> None:
    """Runtime-renderer test: invoke the actual ``_render_session_startup_briefing``
    function and assert that the rendered Operating State output contains the
    ``queried_repo`` identity. Per LO -006 NO-GO finding P2-003: the prior
    label test mirrored implementation strings without exercising the
    production renderer; this test exercises the renderer directly.

    Maps to GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 + GOV-SESSION-SELF-INITIALIZATION-001
    (rollup labeling matches data source under the actual rendering path).
    """
    model = _build_minimal_model(queried_repo="Remaker-Digital/groundtruth-kb")
    rendered = _render_session_startup_briefing(model)

    # Pre-existing label-format contract preserved:
    assert "Testing/tools:" in rendered
    # New queried-repo surface present:
    assert "queried repo: Remaker-Digital/groundtruth-kb" in rendered
    # The full canonical expectation:
    assert (
        "- Testing/tools: 6 failing, 6 manual, 6 ready/passing (queried repo: Remaker-Digital/groundtruth-kb)."
    ) in rendered


def test_render_current_project_state_includes_queried_repo_at_runtime() -> None:
    """Runtime-renderer test for the Current Project State section that
    invokes the actual ``_render_current_project_state`` function. Per LO
    -006 NO-GO finding P2-003.

    Maps to GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 + GOV-SESSION-SELF-INITIALIZATION-001.
    """
    model = _build_minimal_model(queried_repo="Remaker-Digital/groundtruth-kb")
    rendered = _render_current_project_state(model)

    # Pre-existing label-format contract preserved:
    assert "Testing/tool rollup:" in rendered
    # New queried-repo surface present:
    assert "queried repo: Remaker-Digital/groundtruth-kb" in rendered


def test_render_session_startup_briefing_handles_missing_queried_repo() -> None:
    """When queried_repo is missing/None (e.g., live_state_unavailable or
    application_session_missing_agent_red_target), the renderer must surface
    "unknown" rather than a literal None or empty.
    """
    model = _build_minimal_model(queried_repo=None)
    rendered = _render_session_startup_briefing(model)

    assert "queried repo: unknown" in rendered
    assert "queried repo: None" not in rendered
