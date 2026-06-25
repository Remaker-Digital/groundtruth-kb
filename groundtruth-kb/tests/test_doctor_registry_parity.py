# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Deterministic doctor parity gate — registry-affected checks only.

Per the GO review at ``bridge/gtkb-managed-artifact-registry-008.md``
Condition 1, a raw full-output golden snapshot of ``format_doctor_report``
is unsafe because ``run_doctor`` concatenates messages from:

- External tool availability/version checks (host-dependent)
- Bridge poller checks with wall-clock age messaging (time-dependent)
- GitHub / Codex CLI / Claude Code auth probes

This gate picks approach (b) from the review: assert exact parity only
for registry-affected project checks (``_check_hooks``,
``_check_file_bridge_setup``, ``_check_scanner_safe_writer_drift``, and
the three registry-backed skill checks). Tool/poller/auth sections are
excluded — they are orthogonal to the registry refactor.

The per-profile doctor-axis matrix tests in ``test_managed_registry.py``
remain the sharper regression guard on the registry itself.
"""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import pytest

from groundtruth_kb import get_templates_dir
from groundtruth_kb.project.doctor import (
    DoctorReport,
    ToolCheck,
    _check_bridge_propose_skill_present,
    _check_file_bridge_setup,
    _check_hooks,
    _check_scanner_safe_writer_drift,
    _check_skill_present,
    _check_spec_intake_skill_present,
)
from groundtruth_kb.project.scaffold import ScaffoldOptions, scaffold_project


def _project_check_names() -> frozenset[str]:
    """Return the stable names of registry-affected project-level checks."""
    return frozenset(
        {
            "Hooks",
            "File Bridge Config",
            "scanner-safe-writer",
            "skill:decision-capture",
            "skill:bridge-propose",
            "skill:spec-intake",
        }
    )


def _scaffold(tmp_path: Path, profile: str) -> Path:
    """Create a fresh scaffold for *profile* and return its path."""
    target = tmp_path / "project"
    opts = ScaffoldOptions(
        project_name="Parity Project",
        profile=profile,
        owner="Test Owner",
        target_dir=target,
        seed_example=False,
        include_ci=False,
    )
    scaffold_project(opts)
    return target


def _project_checks(target: Path, profile: str) -> list[ToolCheck]:
    """Invoke registry-affected project-level checks directly.

    Bypasses ``run_doctor`` so that tool/poller/auth checks are not
    executed. This keeps the gate fully deterministic.
    """
    checks: list[ToolCheck] = [_check_hooks(target, profile)]
    if profile in ("dual-agent", "dual-agent-webapp"):
        checks.append(_check_file_bridge_setup(target))
        checks.append(_check_scanner_safe_writer_drift(target, profile))
        checks.append(_check_skill_present(target, profile))
        checks.append(_check_bridge_propose_skill_present(target, profile))
        checks.append(_check_spec_intake_skill_present(target, profile))
    return checks


def _normalize(checks: list[ToolCheck]) -> list[tuple[str, str, bool, str]]:
    """Normalize to a stable tuple projection used in parity assertions."""
    return [(c.name, c.status, c.required, c.message) for c in checks]


@pytest.mark.parametrize(
    "profile",
    ["local-only", "dual-agent", "dual-agent-webapp"],
)
def test_registry_affected_checks_pass_on_fresh_scaffold(tmp_path: Path, profile: str) -> None:
    """A fresh scaffold passes every registry-affected project-level check."""
    target = _scaffold(tmp_path, profile)
    checks = _project_checks(target, profile)
    failed = [c for c in checks if c.status != "pass"]
    assert failed == [], (
        f"fresh {profile!r} scaffold should pass every registry-affected check; "
        f"failures: {[(c.name, c.status, c.message) for c in failed]}"
    )


@pytest.mark.parametrize(
    "profile",
    ["local-only", "dual-agent", "dual-agent-webapp"],
)
def test_registry_affected_check_names_are_stable(tmp_path: Path, profile: str) -> None:
    """Every registry-affected check name remains in the allowed stable set."""
    target = _scaffold(tmp_path, profile)
    checks = _project_checks(target, profile)
    names = {c.name for c in checks}
    allowed = _project_check_names()
    unexpected = names - allowed
    assert unexpected == set(), f"{profile!r} produced unexpected check names: {sorted(unexpected)}"


def test_registry_affected_normalized_projection_roundtrips(tmp_path: Path) -> None:
    """DoctorReport.checks filtered to registry-affected names roundtrips through _normalize."""
    target = _scaffold(tmp_path, "dual-agent")
    checks = _project_checks(target, "dual-agent")
    report = DoctorReport(checks=checks, profile="dual-agent")
    filtered = [c for c in report.checks if c.name in _project_check_names()]
    projection = _normalize(filtered)
    # Names must appear in projection order matching check order.
    assert [t[0] for t in projection] == [c.name for c in checks]
    # Status field must be one of the three canonical values.
    assert all(t[1] in {"pass", "fail", "warning"} for t in projection)


def test_dual_agent_registry_affected_count_is_six(tmp_path: Path) -> None:
    """dual-agent scaffold exercises exactly 6 registry-affected project checks."""
    target = _scaffold(tmp_path, "dual-agent")
    checks = _project_checks(target, "dual-agent")
    assert len(checks) == 6


def test_local_only_registry_affected_count_is_one(tmp_path: Path) -> None:
    """local-only scaffold exercises only the ``Hooks`` project check."""
    target = _scaffold(tmp_path, "local-only")
    checks = _project_checks(target, "local-only")
    assert len(checks) == 1
    assert checks[0].name == "Hooks"
    assert checks[0].status == "pass"


_REFRESHED_ARTIFACTS = [
    ("hooks/assertion-check.py", ".claude/hooks/assertion-check.py"),
    ("hooks/spec-event-surfacer.py", ".claude/hooks/spec-event-surfacer.py"),
    ("hooks/_delib_common.py", ".claude/hooks/_delib_common.py"),
    ("hooks/gov09-capture.py", ".claude/hooks/gov09-capture.py"),
    ("rules/file-bridge-protocol.md", ".claude/rules/file-bridge-protocol.md"),
]

_REPO_ROOT = Path(__file__).parent.parent.parent


@pytest.mark.parametrize("template_rel,live_rel", _REFRESHED_ARTIFACTS)
def test_managed_artifact_templates_match_live(template_rel: str, live_rel: str) -> None:
    """CRLF-normalized template hash must equal CRLF-normalized live hash after refresh."""
    templates_dir = get_templates_dir()
    template_path = templates_dir / template_rel
    live_path = _REPO_ROOT / live_rel
    if not live_path.exists():
        pytest.skip(f"live file not available: {live_rel}")
    assert template_path.exists(), f"template not found: {template_path}"

    def norm_hash(p: Path) -> str:
        return hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()

    assert norm_hash(template_path) == norm_hash(live_path), (
        f"CRLF-normalized template {template_rel!r} does not match live {live_rel!r}"
    )


@pytest.mark.parametrize("live_rel", [pair[1] for pair in _REFRESHED_ARTIFACTS])
def test_managed_artifact_refresh_leaves_live_files_unchanged(live_rel: str) -> None:
    """Template refresh must not modify any live .claude/ file (CRLF-normalized comparison)."""
    live_path = _REPO_ROOT / live_rel
    if not live_path.exists():
        pytest.skip(f"live file not available: {live_rel}")
    result = subprocess.run(
        ["git", "show", f"HEAD:{live_rel}"],
        capture_output=True,
        cwd=_REPO_ROOT,
    )
    if result.returncode != 0:
        pytest.skip(f"git not available or file not tracked: {live_rel}")

    def norm(b: bytes) -> bytes:
        return b.replace(b"\r\n", b"\n")

    assert norm(live_path.read_bytes()) == norm(result.stdout), (
        f"live file {live_rel} was unexpectedly modified (content differs from git HEAD after EOL normalization)"
    )
