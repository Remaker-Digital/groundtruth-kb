# (C) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for SPEC-1705 mock development environment.

Validates build integrity, endpoint coverage, config structure, fixture validity.
"""
import json
import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ADMIN_STANDALONE = PROJECT_ROOT / "admin" / "standalone"
MOCK_DIR = ADMIN_STANDALONE / "mocks"
HANDLER_DIR = MOCK_DIR / "handlers"
FIXTURE_DIR = MOCK_DIR / "fixtures"
HOOKS_DIR = PROJECT_ROOT / "admin" / "shared" / "hooks"


class TestBuildIntegrity:
    """Verify production build excludes all mock code."""

    @pytest.fixture(scope="class")
    def build_output(self):
        dist_dir = ADMIN_STANDALONE / "dist"
        js_files = list(dist_dir.glob("assets/*.js"))
        if not js_files:
            pytest.skip("No production build output found")
        main_bundle = max(js_files, key=lambda f: f.stat().st_size)
        return main_bundle.read_text(encoding="utf-8", errors="replace")

    def test_no_mock_tenant_id_in_bundle(self, build_output):
        assert "mock-tenant-001" not in build_output

    def test_no_mock_api_plugin_in_bundle(self, build_output):
        assert "MockApiPlugin" not in build_output

    def test_no_mock_store_in_bundle(self, build_output):
        assert "initializeStore" not in build_output

    def test_no_fixture_emails_in_bundle(self, build_output):
        for email in ["admin@mockstore.com", "jane@mockstore.com", "bob@mockstore.com"]:
            assert email not in build_output, f"Fixture email in bundle: {email}"

    def test_no_fixture_ids_in_bundle(self, build_output):
        for fid in ["mock-conv-", "pk_live_mock_", "member-00"]:
            assert fid not in build_output, f"Fixture ID in bundle: {fid}"

    def test_bundle_size_within_range(self, build_output):
        size_kb = len(build_output.encode("utf-8")) / 1024
        assert 500 < size_kb < 1400, f"Bundle {size_kb:.0f} KB outside 500-1400 KB range"


class TestMockEndpointCoverage:
    """Verify mock handlers cover core API endpoints."""

    @staticmethod
    def _extract_mock_endpoints():
        """Extract API paths from handler files.

        Handler files use imported uppercase helpers from router.ts::

            GET("/api/admin/team", (req) => { ... })
            POST("/api/admin/team/:id", (req) => { ... })
        """
        endpoints = set()
        if not HANDLER_DIR.exists():
            return endpoints
        # Handlers import GET/POST/PUT/DELETE from router.ts as uppercase helpers
        ep_pattern = re.compile(
            r"""(GET|POST|PUT|DELETE)\(\s*["'](/api/[^"']+)["']"""
        )
        for hf in HANDLER_DIR.glob("*.ts"):
            text = hf.read_text(encoding="utf-8", errors="replace")
            for m in ep_pattern.finditer(text):
                path = m.group(2)
                normalized = re.sub(r":([a-zA-Z_]+)", "{}", path)
                endpoints.add(normalized)
        return endpoints

    def test_core_admin_endpoints_have_handlers(self):
        mock_eps = self._extract_mock_endpoints()
        mock_flat = " ".join(mock_eps)
        core = [
            "/api/admin/team", "/api/admin/knowledge", "/api/admin/conversations",
            "/api/admin/quick-actions", "/api/admin/memory", "/api/config",
            "/api/billing/status", "/api/dashboard/usage", "/api/health",
        ]
        missing = [p for p in core if p not in mock_flat]
        assert not missing, f"Core endpoints missing: {missing}"

    def test_handler_files_exist_for_all_pages(self):
        expected = [
            "tenant.ts", "dashboard.ts", "team.ts", "inbox.ts",
            "config.ts", "knowledge.ts", "quick-actions.ts",
            "widget.ts", "billing.ts", "memory.ts",
        ]
        for h in expected:
            assert (HANDLER_DIR / h).exists(), f"Missing: mocks/handlers/{h}"

    def test_handler_files_have_register_function(self):
        for hf in HANDLER_DIR.glob("*.ts"):
            content = hf.read_text(encoding="utf-8", errors="replace")
            assert "export function register" in content, f"{hf.name} missing register export"

    def test_mock_endpoint_count_reasonable(self):
        eps = self._extract_mock_endpoints()
        assert len(eps) >= 40, f"Only {len(eps)} endpoints found, expected >= 40"


@pytest.mark.skipif(
    not (ADMIN_STANDALONE / ".env.mock").is_file(),
    reason=".env.mock not present (container environment)",
)
class TestConfigStructure:
    """Verify mock system config files."""

    def test_env_mock_exists(self):
        assert (ADMIN_STANDALONE / ".env.mock").exists()

    def test_env_mock_has_vite_mock_flag(self):
        assert "VITE_MOCK=true" in (ADMIN_STANDALONE / ".env.mock").read_text()

    def test_package_json_has_dev_mock_script(self):
        pkg = json.loads((ADMIN_STANDALONE / "package.json").read_text())
        assert "dev:mock" in pkg.get("scripts", {})

    def test_dev_mock_script_uses_mock_mode(self):
        pkg = json.loads((ADMIN_STANDALONE / "package.json").read_text())
        assert "--mode mock" in pkg["scripts"].get("dev:mock", "")

    def test_vite_config_has_dynamic_import(self):
        content = (ADMIN_STANDALONE / "vite.config.ts").read_text()
        assert "import(" in content.replace(" ", "")

    def test_vite_config_preserves_proxy(self):
        assert "proxy" in (ADMIN_STANDALONE / "vite.config.ts").read_text()


class TestFixtureValidity:
    """Verify fixture files are well-formed."""

    EXPECTED = [
        "tenant.ts", "dashboard.ts", "team.ts", "inbox.ts",
        "config.ts", "knowledge.ts", "quick-actions.ts",
        "widget.ts", "billing.ts", "memory.ts",
    ]

    def test_all_fixture_files_exist(self):
        for f in self.EXPECTED:
            assert (FIXTURE_DIR / f).exists(), f"Missing: mocks/fixtures/{f}"

    def test_fixture_files_have_exports(self):
        for ff in FIXTURE_DIR.glob("*.ts"):
            assert "export" in ff.read_text(encoding="utf-8", errors="replace")

    def test_fixture_files_are_non_trivial(self):
        for ff in FIXTURE_DIR.glob("*.ts"):
            lc = len(ff.read_text(encoding="utf-8", errors="replace").strip().splitlines())
            assert lc > 10, f"{ff.name} only {lc} lines"

    def test_no_fixture_imports_production_code(self):
        for ff in FIXTURE_DIR.glob("*.ts"):
            content = ff.read_text(encoding="utf-8", errors="replace")
            has_prod = re.search(r"from .+\.\.\./(src|layouts|hooks|pages)", content)
            assert not has_prod, f"{ff.name} imports production code"


class TestCoreInfrastructure:
    """Verify mock core files."""

    def test_router_exists(self):
        assert (MOCK_DIR / "router.ts").exists()

    def test_store_exists(self):
        assert (MOCK_DIR / "store.ts").exists()

    def test_plugin_exists(self):
        assert (MOCK_DIR / "plugin.ts").exists()

    def test_index_exists(self):
        assert (MOCK_DIR / "index.ts").exists()

    def test_plugin_exports_mock_api_plugin(self):
        assert "mockApiPlugin" in (MOCK_DIR / "plugin.ts").read_text(encoding="utf-8", errors="replace")

    def test_store_exports_get_store(self):
        assert "getStore" in (MOCK_DIR / "store.ts").read_text(encoding="utf-8", errors="replace")

    def test_router_has_method_registration(self):
        content = (MOCK_DIR / "router.ts").read_text(encoding="utf-8", errors="replace")
        for method in ["GET", "POST", "PUT", "DELETE"]:
            assert f"export const {method}" in content, f"Router missing {method} export"

    def test_ts_nocheck_on_all_mock_files(self):
        for ts_file in MOCK_DIR.rglob("*.ts"):
            head = ts_file.read_text(encoding="utf-8").splitlines()[:3]
            assert any("ts-nocheck" in line for line in head), \
                f"{ts_file.relative_to(ADMIN_STANDALONE)} missing @ts-nocheck in first 3 lines"
