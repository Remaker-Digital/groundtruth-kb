"""Tests for the Phase 6 session-overlay baseline library and checker.

These tests only exercise the first-slice contract: copy-only builder, fixed
allowlist, non-authoritative metadata, stale-status evaluation, current-pointer
shape, policy validation failure modes, ``.gitignore`` coverage, and the
release-gate policy checker exit code.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
OVERLAY_SCRIPT = REPO_ROOT / "scripts" / "gtkb_overlay.py"
CHECKER_SCRIPT = REPO_ROOT / "scripts" / "check_session_overlay_policy.py"


def _load_module(name: str, script_path: Path):
    spec = importlib.util.spec_from_file_location(name, script_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def overlay_module():
    return _load_module("gtkb_overlay", OVERLAY_SCRIPT)


@pytest.fixture()
def fake_project(tmp_path: Path) -> Path:
    (tmp_path / "docs" / "gtkb-dashboard").mkdir(parents=True)
    (tmp_path / "memory").mkdir(parents=True)
    (tmp_path / "docs" / "gtkb-dashboard" / "dashboard-data.json").write_text(
        json.dumps({"generated_at": "2026-04-23T00:00:00Z"}) + "\n",
        encoding="utf-8",
    )
    (tmp_path / "docs" / "gtkb-dashboard" / "session-startup-report.md").write_text("# startup\n", encoding="utf-8")
    (tmp_path / "docs" / "gtkb-dashboard" / "session-wrapup-report.md").write_text("# wrapup\n", encoding="utf-8")
    (tmp_path / "memory" / "gtkb-dashboard-history.json").write_text(json.dumps([]) + "\n", encoding="utf-8")
    return tmp_path


def test_build_overlay_is_copy_only_and_non_authoritative(overlay_module, fake_project):
    now = datetime(2026, 4, 23, 12, 0, 0, tzinfo=UTC)

    manifest = overlay_module.build_overlay(
        project_root=fake_project,
        subject="application",
        role_slot="prime-builder",
        harness_id="claude-local",
        now=now,
    )

    assert manifest.authoritative is False
    assert manifest.schema_version == overlay_module.OVERLAY_SCHEMA_VERSION
    assert manifest.overlay_id.startswith("20260423T120000Z-")
    assert manifest.application_root == str(fake_project.resolve())

    overlay_dir = overlay_module.overlay_root(fake_project) / manifest.overlay_id
    assert (overlay_dir / "manifest.json").is_file()
    files_dir = overlay_dir / overlay_module.OVERLAY_FILES_DIRNAME
    copied = sorted(p.name for p in files_dir.iterdir())
    assert copied == [
        "dashboard-data.json",
        "gtkb-dashboard-history.json",
        "session-startup-report.md",
        "session-wrapup-report.md",
    ]

    assert len(manifest.entries) == 4
    for entry in manifest.entries:
        assert entry.authoritative is False
        assert entry.source_kind == "file"
        assert entry.overlay_path.startswith(overlay_module.OVERLAY_FILES_DIRNAME + "/")
        assert len(entry.source_hash) == 64

    # Source files are unchanged; mtime/content identical. Sanity-check content.
    dashboard_source = (fake_project / "docs" / "gtkb-dashboard" / "dashboard-data.json").read_text(encoding="utf-8")
    dashboard_overlay = (files_dir / "dashboard-data.json").read_text(encoding="utf-8")
    assert dashboard_source == dashboard_overlay


def test_build_overlay_updates_current_pointer(overlay_module, fake_project):
    manifest = overlay_module.build_overlay(project_root=fake_project)
    pointer_path = overlay_module.overlay_root(fake_project) / overlay_module.OVERLAY_CURRENT_POINTER_NAME

    assert pointer_path.is_file()
    payload = json.loads(pointer_path.read_text(encoding="utf-8"))
    assert payload["authoritative"] is False
    assert payload["overlay_id"] == manifest.overlay_id
    assert payload["overlay_dir"].endswith(manifest.overlay_id)
    assert payload["manifest_path"].endswith("manifest.json")


def test_build_overlay_rejects_non_allowlisted_source(overlay_module, fake_project):
    with pytest.raises(overlay_module.OverlayPolicyError, match="not in overlay allowlist"):
        overlay_module.build_overlay(
            project_root=fake_project,
            sources=(("scripts/release_candidate_gate.py", "release_candidate_gate.py"),),
        )


def test_build_overlay_rejects_forbidden_patterns(overlay_module, fake_project):
    # Caller fabricates a bypass of the allowlist second-element check; the
    # denylist must still catch executable content.
    with pytest.raises(overlay_module.OverlayPolicyError):
        overlay_module.build_overlay(
            project_root=fake_project,
            sources=(("scripts/release_candidate_gate.py", "dashboard-data.json"),),
        )


def test_build_overlay_skips_missing_sources(overlay_module, fake_project):
    (fake_project / "memory" / "gtkb-dashboard-history.json").unlink()

    manifest = overlay_module.build_overlay(project_root=fake_project)

    overlay_uris = {entry.source_uri for entry in manifest.entries}
    assert "memory/gtkb-dashboard-history.json" not in overlay_uris
    assert len(manifest.entries) == 3


def test_evaluate_staleness_detects_hash_drift(overlay_module, fake_project):
    now = datetime(2026, 4, 23, 0, 0, 0, tzinfo=UTC)
    manifest = overlay_module.build_overlay(project_root=fake_project, now=now)
    overlay_dir = overlay_module.overlay_root(fake_project) / manifest.overlay_id

    # Fresh immediately after build.
    fresh = overlay_module.evaluate_staleness(overlay_dir, project_root=fake_project, now=now)
    assert fresh.is_stale is False
    assert fresh.entries_stale == 0
    assert fresh.expired is False

    # Mutate one source: overlay must now report stale.
    (fake_project / "docs" / "gtkb-dashboard" / "dashboard-data.json").write_text(
        json.dumps({"generated_at": "2026-04-23T99:00:00Z", "mutated": True}) + "\n",
        encoding="utf-8",
    )
    drifted = overlay_module.evaluate_staleness(overlay_dir, project_root=fake_project, now=now)
    assert drifted.is_stale is True
    assert drifted.entries_stale == 1
    drifted_entry = next(e for e in drifted.entries if e.source_uri.endswith("dashboard-data.json"))
    assert drifted_entry.reason == "hash_changed"

    # Time past expiry flips expired even without source drift.
    much_later = now + timedelta(days=7)
    aged = overlay_module.evaluate_staleness(overlay_dir, project_root=fake_project, now=much_later)
    assert aged.expired is True
    assert aged.is_stale is True


def test_validate_manifest_rejects_authoritative(overlay_module, fake_project):
    manifest = overlay_module.build_overlay(project_root=fake_project)
    overlay_dir = overlay_module.overlay_root(fake_project) / manifest.overlay_id
    manifest_path = overlay_dir / "manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload["authoritative"] = True
    manifest_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    reloaded = overlay_module.load_manifest(overlay_dir)
    with pytest.raises(overlay_module.OverlayPolicyError, match="authoritative"):
        overlay_module.validate_manifest(reloaded, project_root=fake_project)


def test_validate_manifest_rejects_application_root_escape(overlay_module, fake_project, tmp_path):
    manifest = overlay_module.build_overlay(project_root=fake_project)
    overlay_dir = overlay_module.overlay_root(fake_project) / manifest.overlay_id
    manifest_path = overlay_dir / "manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload["application_root"] = str(tmp_path / "different-app")
    manifest_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    reloaded = overlay_module.load_manifest(overlay_dir)
    with pytest.raises(overlay_module.OverlayPolicyError, match="application_root"):
        overlay_module.validate_manifest(reloaded, project_root=fake_project)


def test_current_overlay_status_absent_when_no_overlay(overlay_module, fake_project):
    status = overlay_module.current_overlay_status(fake_project)
    assert status["overlay_present"] is False
    assert status["authoritative"] is False
    assert status["is_stale"] is False


def test_current_overlay_status_reports_built_overlay(overlay_module, fake_project):
    now = datetime(2026, 4, 23, 0, 0, 0, tzinfo=UTC)
    manifest = overlay_module.build_overlay(project_root=fake_project, now=now)
    status = overlay_module.current_overlay_status(fake_project)
    assert status["overlay_present"] is True
    assert status["authoritative"] is False
    assert status["overlay_id"] == manifest.overlay_id
    assert status["entries_total"] == 4
    assert any("non-authoritative" in note for note in status["notes"])


def test_gitignore_covers_overlay_runtime_root():
    contents = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    assert ".groundtruth/session/overlays/" in contents


def test_checker_passes_on_clean_overlay(overlay_module, fake_project):
    overlay_module.build_overlay(project_root=fake_project)
    result = subprocess.run(
        [sys.executable, str(CHECKER_SCRIPT), "--project-root", str(fake_project), "--json"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["pass"] is True
    assert report["overlay_count"] == 1
    assert report["pointer_present"] is True
    assert report["overlays"][0]["valid"] is True


def test_checker_fails_on_authoritative_overlay(overlay_module, fake_project):
    manifest = overlay_module.build_overlay(project_root=fake_project)
    overlay_dir = overlay_module.overlay_root(fake_project) / manifest.overlay_id
    manifest_path = overlay_dir / "manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload["authoritative"] = True
    manifest_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(CHECKER_SCRIPT), "--project-root", str(fake_project)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 1
    assert "Session overlay policy: FAIL" in result.stderr
    assert "authoritative" in result.stderr
