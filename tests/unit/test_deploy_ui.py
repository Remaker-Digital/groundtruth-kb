"""Unit tests for scripts/deploy_ui.py (SPEC-1705).

Tests the UI-only deployment tooling: component registry, hashing,
build orchestration, deploy dry-run, verification, and CLI.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys
from unittest import mock

import pytest

import pytest

# Ensure the scripts directory is importable
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent.parent / "scripts"))
import deploy_ui


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def fake_dist(tmp_path: pathlib.Path):
    """Create a fake project tree with dist directories for all 4 components."""
    # Create dist dirs with known content
    for comp_name in ("standalone", "provider", "shopify"):
        dist = tmp_path / "admin" / comp_name / "dist"
        dist.mkdir(parents=True)
        (dist / "index.html").write_text(f"<html>{comp_name}</html>")
        assets = dist / "assets"
        assets.mkdir()
        (assets / "main.js").write_text(f"console.log('{comp_name}')")

    widget_dist = tmp_path / "widget" / "dist"
    widget_dist.mkdir(parents=True)
    (widget_dist / "agent-red-widget.iife.js").write_text("(function(){})();")

    # Also create source dirs with package.json and node_modules
    for comp_name in ("standalone", "provider", "shopify"):
        src = tmp_path / "admin" / comp_name
        (src / "package.json").write_text('{"name":"test"}')
        (src / "node_modules").mkdir(exist_ok=True)

    widget_src = tmp_path / "widget"
    (widget_src / "package.json").write_text('{"name":"widget-test"}')
    (widget_src / "node_modules").mkdir(exist_ok=True)

    # Create Dockerfile.ui
    (tmp_path / "Dockerfile.ui").write_text("FROM base\nCOPY dist/ .\n")

    return tmp_path


@pytest.fixture()
def patched_components(fake_dist):
    """Patch COMPONENTS and ROOT to use the fake dist tree."""
    fake_components = {}
    for name, orig in deploy_ui.COMPONENTS.items():
        if name == "widget":
            fake_components[name] = {
                **orig,
                "source_dir": fake_dist / "widget",
                "dist_dir": fake_dist / "widget" / "dist",
            }
        else:
            fake_components[name] = {
                **orig,
                "source_dir": fake_dist / "admin" / name,
                "dist_dir": fake_dist / "admin" / name / "dist",
            }

    with mock.patch.object(deploy_ui, "COMPONENTS", fake_components), \
         mock.patch.object(deploy_ui, "ROOT", fake_dist):
        yield fake_components


# ---------------------------------------------------------------------------
# Component registry tests
# ---------------------------------------------------------------------------


class TestComponentRegistry:
    """Tests for the COMPONENTS dict structure."""

    def test_four_components_registered(self):
        assert len(deploy_ui.COMPONENTS) == 4

    def test_expected_component_names(self):
        assert set(deploy_ui.COMPONENTS.keys()) == {"standalone", "provider", "shopify", "widget"}

    def test_each_component_has_required_keys(self):
        required = {"source_dir", "dist_dir", "build_cmd", "dev_port", "label"}
        for name, comp in deploy_ui.COMPONENTS.items():
            missing = required - set(comp.keys())
            assert not missing, f"{name} missing keys: {missing}"

    def test_dist_dir_is_child_of_source_dir(self):
        for name, comp in deploy_ui.COMPONENTS.items():
            assert str(comp["dist_dir"]).startswith(str(comp["source_dir"])), (
                f"{name}: dist_dir should be under source_dir"
            )

    def test_build_cmd_uses_npm(self):
        for name, comp in deploy_ui.COMPONENTS.items():
            assert "npm run build" in comp["build_cmd"], f"{name}: expected npm build command"


# ---------------------------------------------------------------------------
# Environment registry tests
# ---------------------------------------------------------------------------


class TestEnvironmentRegistry:
    """Tests for the ENVIRONMENTS dict structure."""

    def test_two_environments(self):
        assert set(deploy_ui.ENVIRONMENTS.keys()) == {"staging", "production"}

    def test_staging_container_app(self):
        assert deploy_ui.ENVIRONMENTS["staging"]["container_app"] == "agent-red-staging"

    def test_production_container_app(self):
        assert deploy_ui.ENVIRONMENTS["production"]["container_app"] == "agent-red-api-gateway"

    def test_same_resource_group(self):
        for env, cfg in deploy_ui.ENVIRONMENTS.items():
            assert cfg["resource_group"] == "Agent-Red"

    def test_same_registry(self):
        for env, cfg in deploy_ui.ENVIRONMENTS.items():
            assert cfg["registry"] == "acragentredeastus.azurecr.io"


# ---------------------------------------------------------------------------
# Hashing utility tests
# ---------------------------------------------------------------------------


class TestHashDirectory:
    """Tests for _hash_directory()."""

    def test_missing_directory_returns_missing(self, tmp_path):
        result = deploy_ui._hash_directory(tmp_path / "nonexistent")
        assert result == "missing"

    def test_returns_12_char_hex(self, tmp_path):
        d = tmp_path / "testdir"
        d.mkdir()
        (d / "file.txt").write_text("hello")
        result = deploy_ui._hash_directory(d)
        assert len(result) == 12
        assert all(c in "0123456789abcdef" for c in result)

    def test_same_content_same_hash(self, tmp_path):
        d1 = tmp_path / "dir1"
        d1.mkdir()
        (d1 / "a.txt").write_text("content")

        d2 = tmp_path / "dir2"
        d2.mkdir()
        (d2 / "a.txt").write_text("content")

        assert deploy_ui._hash_directory(d1) == deploy_ui._hash_directory(d2)

    def test_different_content_different_hash(self, tmp_path):
        d1 = tmp_path / "dir1"
        d1.mkdir()
        (d1 / "a.txt").write_text("content1")

        d2 = tmp_path / "dir2"
        d2.mkdir()
        (d2 / "a.txt").write_text("content2")

        assert deploy_ui._hash_directory(d1) != deploy_ui._hash_directory(d2)


# ---------------------------------------------------------------------------
# Size utility tests
# ---------------------------------------------------------------------------


class TestDirSize:
    """Tests for _dir_size()."""

    def test_missing_directory_returns_zero(self, tmp_path):
        assert deploy_ui._dir_size(tmp_path / "missing") == 0

    def test_counts_all_files(self, tmp_path):
        d = tmp_path / "sized"
        d.mkdir()
        (d / "a.txt").write_bytes(b"x" * 100)
        (d / "b.txt").write_bytes(b"y" * 200)
        assert deploy_ui._dir_size(d) == 300


class TestHumanSize:
    """Tests for _human_size()."""

    def test_bytes(self):
        assert deploy_ui._human_size(500) == "500.0 B"

    def test_kilobytes(self):
        result = deploy_ui._human_size(2048)
        assert "KB" in result

    def test_megabytes(self):
        result = deploy_ui._human_size(2 * 1024 * 1024)
        assert "MB" in result

    def test_zero(self):
        assert deploy_ui._human_size(0) == "0.0 B"


# ---------------------------------------------------------------------------
# Build tests
# ---------------------------------------------------------------------------


class TestBuildComponent:
    """Tests for build_component()."""

    def test_unknown_component_raises(self):
        with pytest.raises(ValueError, match="Unknown component"):
            deploy_ui.build_component("nonexistent")

    def test_missing_source_dir_raises(self, patched_components):
        # Remove a source dir
        import shutil
        src = patched_components["standalone"]["source_dir"]
        shutil.rmtree(src)
        with pytest.raises(FileNotFoundError, match="Source directory not found"):
            deploy_ui.build_component("standalone")

    def test_successful_build_returns_metadata(self, patched_components):
        with mock.patch.object(deploy_ui, "_run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(args="", returncode=0)
            result = deploy_ui.build_component("standalone")

        assert result["name"] == "standalone"
        assert "hash" in result
        assert "size" in result
        assert "duration_s" in result
        assert result["size"] > 0

    def test_build_skips_npm_install_when_node_modules_exists(self, patched_components):
        with mock.patch.object(deploy_ui, "_run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(args="", returncode=0)
            deploy_ui.build_component("widget")

        # Should only call npm run build, not npm install
        calls = [str(c) for c in mock_run.call_args_list]
        assert len(mock_run.call_args_list) == 1  # Only build, no install
        assert "npm run build" in str(mock_run.call_args_list[0])


class TestBuildAll:
    """Tests for build_all()."""

    def test_builds_all_four_by_default(self, patched_components):
        with mock.patch.object(deploy_ui, "build_component") as mock_build:
            mock_build.return_value = {"name": "test", "hash": "abc", "size": 100, "size_human": "100 B", "duration_s": 1.0, "dist_dir": "/tmp"}
            results = deploy_ui.build_all()
        assert len(results) == 4

    def test_builds_subset(self, patched_components):
        with mock.patch.object(deploy_ui, "build_component") as mock_build:
            mock_build.return_value = {"name": "test", "hash": "abc", "size": 100, "size_human": "100 B", "duration_s": 1.0, "dist_dir": "/tmp"}
            results = deploy_ui.build_all(["standalone", "widget"])
        assert len(results) == 2
        assert mock_build.call_count == 2


# ---------------------------------------------------------------------------
# Status tests
# ---------------------------------------------------------------------------


class TestGetUiStatus:
    """Tests for get_ui_status()."""

    def test_returns_all_components(self, patched_components):
        status = deploy_ui.get_ui_status()
        assert set(status.keys()) == {"standalone", "provider", "shopify", "widget"}

    def test_existing_dist_shows_ok(self, patched_components):
        status = deploy_ui.get_ui_status()
        for name, info in status.items():
            assert info["exists"] is True
            assert info["hash"] is not None
            assert info["size"] > 0

    def test_missing_dist_shows_missing(self, patched_components):
        import shutil
        shutil.rmtree(patched_components["widget"]["dist_dir"])
        status = deploy_ui.get_ui_status()
        assert status["widget"]["exists"] is False
        assert status["widget"]["hash"] is None


class TestGetCombinedUiHash:
    """Tests for get_combined_ui_hash()."""

    def test_returns_8_char_hex(self, patched_components):
        result = deploy_ui.get_combined_ui_hash()
        assert len(result) == 8
        assert all(c in "0123456789abcdef" for c in result)

    def test_deterministic(self, patched_components):
        h1 = deploy_ui.get_combined_ui_hash()
        h2 = deploy_ui.get_combined_ui_hash()
        assert h1 == h2


# ---------------------------------------------------------------------------
# Deploy tests
# ---------------------------------------------------------------------------


class TestDeployUi:
    """Tests for deploy_ui()."""

    def test_unknown_env_raises(self, patched_components):
        with pytest.raises(ValueError, match="Unknown environment"):
            deploy_ui.deploy_ui("invalid", "v1.81.2")

    def test_missing_dist_raises(self, patched_components):
        import shutil
        shutil.rmtree(patched_components["standalone"]["dist_dir"])
        with pytest.raises(FileNotFoundError, match="Missing dist directories"):
            deploy_ui.deploy_ui("staging", "v1.81.2")

    def test_dry_run_returns_commands(self, patched_components):
        result = deploy_ui.deploy_ui("staging", "v1.81.2", dry_run=True)
        assert result["status"] == "dry_run"
        assert "acragentredeastus.azurecr.io/api-gateway:v1.81.2" in result["base_image"]
        assert "v1.81.2-ui" in result["new_image"]
        assert "az acr build" in result["acr_cmd"]
        assert "az containerapp update" in result["deploy_cmd"]
        assert "agent-red-staging" in result["deploy_cmd"]

    def test_dry_run_production_uses_correct_app(self, patched_components):
        result = deploy_ui.deploy_ui("production", "v1.80.5", dry_run=True)
        assert "agent-red-api-gateway" in result["deploy_cmd"]

    def test_custom_suffix(self, patched_components):
        result = deploy_ui.deploy_ui("staging", "v1.81.2", suffix="hotfix1", dry_run=True)
        assert "v1.81.2-hotfix1" in result["new_image"]

    def test_dry_run_does_not_call_subprocess(self, patched_components):
        with mock.patch.object(deploy_ui, "_run") as mock_run:
            deploy_ui.deploy_ui("staging", "v1.81.2", dry_run=True)
        mock_run.assert_not_called()

    def test_deploy_calls_acr_then_containerapp(self, patched_components):
        with mock.patch.object(deploy_ui, "_run") as mock_run, \
             mock.patch("time.sleep"):
            mock_run.return_value = subprocess.CompletedProcess(args="", returncode=0)
            result = deploy_ui.deploy_ui("staging", "v1.81.2")

        assert result["status"] == "deployed"
        assert mock_run.call_count == 2
        # First call: ACR build
        assert "az acr build" in str(mock_run.call_args_list[0])
        # Second call: Container App update
        assert "az containerapp update" in str(mock_run.call_args_list[1])

    def test_deploy_includes_no_logs_flag(self, patched_components):
        result = deploy_ui.deploy_ui("staging", "v1.81.2", dry_run=True)
        assert "--no-logs" in result["acr_cmd"]

    def test_deploy_includes_dockerfile_ui(self, patched_components):
        result = deploy_ui.deploy_ui("staging", "v1.81.2", dry_run=True)
        assert "--file Dockerfile.ui" in result["acr_cmd"]


# ---------------------------------------------------------------------------
# Verify tests
# ---------------------------------------------------------------------------


class TestVerifyDeployment:
    """Tests for verify_deployment()."""

    def test_unknown_env_raises(self):
        with pytest.raises(ValueError, match="Unknown environment"):
            deploy_ui.verify_deployment("invalid")

    def test_all_healthy(self):
        mock_resp = mock.MagicMock()
        mock_resp.getcode.return_value = 200
        mock_resp.__enter__ = mock.MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = mock.MagicMock(return_value=False)

        with mock.patch("urllib.request.urlopen", return_value=mock_resp):
            result = deploy_ui.verify_deployment("staging")

        assert result["summary"]["all_ok"] is True
        assert result["summary"]["passed"] == 5
        assert result["health"]["ok"] is True
        assert result["widget_js"]["ok"] is True

    def test_checks_five_endpoints(self):
        mock_resp = mock.MagicMock()
        mock_resp.getcode.return_value = 200
        mock_resp.__enter__ = mock.MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = mock.MagicMock(return_value=False)

        with mock.patch("urllib.request.urlopen", return_value=mock_resp):
            result = deploy_ui.verify_deployment("staging")

        # 5 endpoint checks + 1 summary
        assert result["summary"]["total"] == 5

    def test_http_error_marks_fail(self):
        import urllib.error
        def side_effect(req, **kwargs):
            raise urllib.error.HTTPError(req.full_url, 500, "Error", {}, None)

        with mock.patch("urllib.request.urlopen", side_effect=side_effect):
            result = deploy_ui.verify_deployment("staging")

        assert result["summary"]["all_ok"] is False
        assert result["summary"]["passed"] == 0


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------


class TestCli:
    """Tests for the CLI main() function."""

    def test_status_command(self, patched_components):
        rc = deploy_ui.main(["status"])
        assert rc == 0

    def test_build_command(self, patched_components):
        with mock.patch.object(deploy_ui, "_run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(args="", returncode=0)
            rc = deploy_ui.main(["build"])
        assert rc == 0

    def test_build_only_one(self, patched_components):
        with mock.patch.object(deploy_ui, "_run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(args="", returncode=0)
            rc = deploy_ui.main(["build", "--only", "widget"])
        assert rc == 0
        # Should only have 1 build call (widget has node_modules)
        assert mock_run.call_count == 1

    def test_deploy_dry_run(self, patched_components):
        rc = deploy_ui.main(["deploy", "--env", "staging", "--base-version", "v1.81.2", "--dry-run"])
        assert rc == 0

    def test_verify_command_success(self):
        mock_resp = mock.MagicMock()
        mock_resp.getcode.return_value = 200
        mock_resp.__enter__ = mock.MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = mock.MagicMock(return_value=False)

        with mock.patch("urllib.request.urlopen", return_value=mock_resp):
            rc = deploy_ui.main(["verify", "--env", "staging"])
        assert rc == 0

    def test_verify_command_failure_returns_1(self):
        import urllib.error
        def side_effect(req, **kwargs):
            raise urllib.error.HTTPError(req.full_url, 500, "Error", {}, None)

        with mock.patch("urllib.request.urlopen", side_effect=side_effect):
            rc = deploy_ui.main(["verify", "--env", "staging"])
        assert rc == 1

    def test_deploy_requires_env(self, patched_components):
        with pytest.raises(SystemExit):
            deploy_ui.main(["deploy", "--base-version", "v1.81.2"])

    def test_deploy_requires_base_version(self, patched_components):
        with pytest.raises(SystemExit):
            deploy_ui.main(["deploy", "--env", "staging"])


# ---------------------------------------------------------------------------
# Dockerfile.ui structure test
# ---------------------------------------------------------------------------


_dockerfile_ui = deploy_ui.ROOT / "Dockerfile.ui"


@pytest.mark.skipif(
    not _dockerfile_ui.is_file(),
    reason="Dockerfile.ui not present (container environment)",
)
class TestDockerfileUi:
    """Tests for the Dockerfile.ui file itself."""

    def test_dockerfile_exists(self):
        assert _dockerfile_ui.is_file(), "Dockerfile.ui must exist at project root"

    def test_uses_arg_base_image(self):
        content = (deploy_ui.ROOT / "Dockerfile.ui").read_text()
        assert "ARG BASE_IMAGE" in content
        assert "FROM ${BASE_IMAGE}" in content

    def test_copies_all_four_dist_dirs(self):
        content = (deploy_ui.ROOT / "Dockerfile.ui").read_text()
        assert "admin/shopify/dist/" in content
        assert "admin/standalone/dist/" in content
        assert "admin/provider/dist/" in content
        assert "widget/dist/" in content

    def test_restores_non_root_user(self):
        content = (deploy_ui.ROOT / "Dockerfile.ui").read_text()
        lines = content.strip().split("\n")
        # Last non-empty line should restore non-root user
        last_line = [l.strip() for l in lines if l.strip()][-1]
        assert last_line == "USER agentred"

    def test_copyright_notice(self):
        content = (deploy_ui.ROOT / "Dockerfile.ui").read_text()
        assert "Remaker Digital" in content
