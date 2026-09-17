"""Regression checks for GroundTruth-KB platform adoption configuration and workflows.

The record and guidance checks live in platform_tests/groundtruth_kb/specs/test_governance_adoption_records.py
and platform_tests/scripts/test_governance_adoption_guidance.py.
"""

from __future__ import annotations

import subprocess
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def _load_toml(path: str) -> dict:
    return tomllib.loads(_read(path))


def _one_line(text: str) -> str:
    return " ".join(text.split())


def _assert_not_git_ignored(paths: list[str]) -> None:
    result = subprocess.run(
        ["git", "check-ignore"] + paths,
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    ignored = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    assert not ignored, f"GroundTruth governance artifacts are still git-ignored: {ignored}"


def test_groundtruth_adopter_profile_is_pinned() -> None:
    config = _load_toml("groundtruth.toml")

    assert config["groundtruth"]["db_path"] == "groundtruth.db"
    assert config["project"]["project_name"] == "GroundTruth-KB Platform"
    assert config["project"]["owner"] == "Remaker Digital"
    assert config["project"]["profile"] == "dual-agent"
    assert config["project"]["cloud_provider"] == "azure"
    assert config["project"]["scaffold_version"] == "0.7.0rc1"
    assert config["scoped_service"]["application_id"] == "agent-red"


def test_release_candidate_gate_runs_governance_adoption_tests() -> None:
    gate = _read("scripts/release_candidate_gate.py")

    assert "tests/scripts/test_groundtruth_governance_adoption.py" in gate
    assert "tests/scripts/test_codex_hook_parity.py" in gate
    assert "tests/hooks/test_formal_artifact_approval_gate.py" in gate
    assert "tests/hooks/test_workstream_focus.py" in gate
    assert "scripts/check_harness_parity.py" in gate


def test_release_candidate_gate_workflow_has_python_and_frontend_lanes() -> None:
    workflow = _read(".github/workflows/release-candidate-gate.yml")

    assert "--require-python 3.12 --skip-frontend" in workflow
    assert "--skip-python --include-frontend" in workflow
    assert "windows-latest" in workflow


def test_sonarcloud_workflow_can_verify_exact_release_candidate() -> None:
    workflow = _read(".github/workflows/sonarcloud.yml")
    sonar_properties = _read("sonar-project.properties")

    assert "branches: [main, develop]" in workflow
    assert "workflow_dispatch:" in workflow
    assert "timeout-minutes: 15" in workflow
    assert "grep -v '^agntcy-app-sdk' requirements.txt" in workflow
    assert "sonar.organization=mike-remakerdigital" in sonar_properties
    assert "Validate SonarCloud token" in workflow
    assert "SONAR_TOKEN" in workflow


def test_security_scan_uses_scan_only_acr_secrets_for_docker_scout() -> None:
    workflow = _read(".github/workflows/security-scan.yml")

    assert "Validate Docker Scout ACR secrets" in workflow
    assert "ACR_SCOUT_USERNAME" in workflow
    assert "ACR_SCOUT_PASSWORD" in workflow
    assert "DOCKER_SCOUT_HUB_USER" in workflow
    assert "DOCKER_SCOUT_HUB_PAT" in workflow
    assert "Login to Docker Hub for Docker Scout" in workflow
    assert "docker/login-action@v4" in workflow
    assert "username: ${{ secrets.ACR_SCOUT_USERNAME }}" in workflow
    assert "password: ${{ secrets.ACR_SCOUT_PASSWORD }}" in workflow
    assert "username: ${{ secrets.ACR_USERNAME }}" not in workflow
    assert "password: ${{ secrets.ACR_PASSWORD }}" not in workflow
