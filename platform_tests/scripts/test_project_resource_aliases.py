"""Tests for the GT-KB governed project resource alias registry."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "resolve_project_resource.py"
REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_module():
    spec = importlib.util.spec_from_file_location("resolve_project_resource", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["resolve_project_resource"] = module
    spec.loader.exec_module(module)
    return module


def test_governed_registry_is_valid_and_pointer_is_not_competing_registry() -> None:
    module = _load_module()

    registry = module.load_registry()

    assert module.validate_registry(registry) == []
    assert module.validate_pointer() == []
    assert len(module.resource_rows(registry)) >= 10


def test_human_companion_points_to_governed_registry() -> None:
    companion = REPO_ROOT / "memory" / "project_external_resource_registry.md"
    text = companion.read_text(encoding="utf-8")

    assert "config/agent-control/project-resource-aliases.toml" in text
    assert "two competing resource" in text


def test_unqualified_repo_resolves_to_gtkb_repository() -> None:
    module = _load_module()

    result = module.resolve_alias("repo")

    assert result["status"] == "resolved"
    assert result["resource"]["id"] == "gtkb.github.repo"
    assert result["resource"]["identity"] == "Remaker-Digital/groundtruth-kb"


def test_separate_project_resource_requires_explicit_scope() -> None:
    module = _load_module()

    default_result = module.resolve_alias("Agent Red repo")
    scoped_result = module.resolve_alias("Agent Red repo", scope="agent-red")

    assert default_result["status"] == "separate_project_warning"
    assert default_result["resource"]["id"] == "agentred.github.repo"
    assert scoped_result["status"] == "resolved"
    assert scoped_result["resource"]["id"] == "agentred.github.repo"


def test_ambiguous_alias_fails_closed() -> None:
    module = _load_module()
    registry = {
        "schema_version": 1,
        "project": {"canonical_name": "GroundTruth-KB"},
        "resources": [
            {
                "id": "gtkb.github.repo",
                "kind": "github_repository",
                "name": "GT-KB repo",
                "url": "https://github.com/Remaker-Digital/groundtruth-kb",
                "identity": "Remaker-Digital/groundtruth-kb",
                "aliases": ["shared"],
                "status": "canonical",
            },
            {
                "id": "gtkb.github.issues",
                "kind": "github_issues",
                "name": "GT-KB issues",
                "url": "https://github.com/Remaker-Digital/groundtruth-kb/issues",
                "identity": "Remaker-Digital/groundtruth-kb/issues",
                "aliases": ["shared"],
                "status": "canonical",
            },
        ],
    }

    result = module.resolve_alias("shared", registry=registry)

    assert result["status"] == "ambiguous"
    assert {candidate["id"] for candidate in result["candidates"]} == {"gtkb.github.repo", "gtkb.github.issues"}


def test_git_remote_drift_check_binds_origin_to_gtkb_repo(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    module = _load_module()
    registry = module.load_registry()

    def fake_run(command, **_kwargs):
        if command == ["git", "remote", "get-url", "origin"]:
            return subprocess.CompletedProcess(
                command, 0, stdout="https://github.com/Remaker-Digital/groundtruth-kb.git\n"
            )
        if command == ["git", "remote", "get-url", "agent-red"]:
            return subprocess.CompletedProcess(
                command, 0, stdout="https://github.com/mike-remakerdigital/agent-red.git\n"
            )
        raise AssertionError(f"unexpected command: {command}")

    monkeypatch.setattr(module.subprocess, "run", fake_run)

    result = module.check_git_remote_drift(registry, repo_root=tmp_path)

    assert result["status"] == "pass"
    assert result["expected_identity"] == "Remaker-Digital/groundtruth-kb"
    assert result["agent_red"] == "https://github.com/mike-remakerdigital/agent-red.git"


def test_git_remote_drift_check_fails_for_agent_red_origin(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    module = _load_module()
    registry = module.load_registry()

    def fake_run(command, **_kwargs):
        if command == ["git", "remote", "get-url", "origin"]:
            return subprocess.CompletedProcess(
                command, 0, stdout="https://github.com/mike-remakerdigital/agent-red.git\n"
            )
        return subprocess.CompletedProcess(command, 2, stdout="")

    monkeypatch.setattr(module.subprocess, "run", fake_run)

    result = module.check_git_remote_drift(registry, repo_root=tmp_path)

    assert result["status"] == "fail"
    assert result["origin"] == "https://github.com/mike-remakerdigital/agent-red.git"


def test_ci_evidence_requires_exact_release_binding() -> None:
    module = _load_module()
    valid = {
        "resource_id": "gtkb.github.actions",
        "repo": "Remaker-Digital/groundtruth-kb",
        "branch": "develop",
        "event": "push",
        "head_sha": "a" * 40,
        "workflow": "GroundTruth KB Tests",
        "job": "tests",
        "run_url": "https://github.com/Remaker-Digital/groundtruth-kb/actions/runs/123456",
    }
    invalid = {**valid, "repo": "mike-remakerdigital/agent-red", "head_sha": "abc"}

    assert module.validate_ci_evidence(valid) == []
    errors = module.validate_ci_evidence(invalid)
    assert any("does not match governed GT-KB repo" in error for error in errors)
    assert any("full 40-character commit SHA" in error for error in errors)


def test_scanner_warns_on_historical_unqualified_terms_without_blocking() -> None:
    module = _load_module()

    findings = module.scan_text_for_unqualified_terms(
        "Historical note: CI is green on the repo.\nNew row: resource_id=gtkb.github.actions CI is green.",
        path="bridge/old.md",
    )

    assert len(findings) == 1
    assert findings[0]["status"] == "warning"
    assert findings[0]["path"] == "bridge/old.md"


def test_cli_resolves_json_alias() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "repo", "--json"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "resolved"
    assert payload["resource"]["id"] == "gtkb.github.repo"
