"""
Hook regression tests for credential-scan.py (WI-3142).

Tests the unified key detection, value-scoped suppression, and boundary
handling. Covers both direct helper functions AND the JSON stdin/stdout
hook entrypoint via subprocess.

Sample key values are constructed at runtime to avoid triggering the
credential scanner during test file writes. No blanket file exclusion
is used for this test file.

Codex GO: bridge/credential-scan-narrowing-012.md

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Import the hook module directly
# ---------------------------------------------------------------------------

HOOK_PATH = Path(__file__).resolve().parents[2] / ".claude" / "hooks" / "credential-scan.py"

spec = importlib.util.spec_from_file_location("credential_scan", HOOK_PATH)
credential_scan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(credential_scan)

_scan_content = credential_scan._scan_content
_is_fixture_suppressed = credential_scan._is_fixture_suppressed
_FIXTURE_VALUES = credential_scan._FIXTURE_VALUES
_DOCSTRING_EXAMPLE_VALUES = credential_scan._DOCSTRING_EXAMPLE_VALUES

# ---------------------------------------------------------------------------
# Runtime-constructed sample values (avoids triggering hook during writes)
# ---------------------------------------------------------------------------

# Non-fixture key for detection tests — NOT in _FIXTURE_VALUES
_SAMPLE_REAL = "ar_user" + "_prod_REAL_SECRET_KEY_12345"
_SAMPLE_NEW_CONFTEST = "ar_user" + "_brand_new_production_key_abc"
_SAMPLE_NEW_MW = "pk_live" + "_brand_new_widget_key_xyz"
_SAMPLE_DEMO = "ar_user" + "_demo_abc123def456"
_SAMPLE_HYPHEN_QUOTED = "ar_user" + "_rema_yZR6wMz-VDlV-JhbdRPW1"
_SAMPLE_HYPHEN_BARE = "ar_spa" + "_plat_mdbq-Sm3vE5Qj3d4H2Dk82juVsB42wg3"

# Fixture values (safe to reference — they're IN the allowlist)
_FIX_LIVE = "ar_live" + "_abc123def456"
_FIX_ARSK = "arsk_test" + "_pro_key_002"
_FIX_SPA = "ar_spa_plat" + "_INVALID_STALE_TOKEN"
_FIX_PKLIVE = "pk_live" + "_invalid_key_00000000"

# FQDN sample (join avoids pre-commit hook literal detection)
_FQDN = "".join(
    [
        '"https://agent-red-api',
        "-gateway.abc123.eastus",
        '.azurecontainerapps.io/api"',
    ]
)

# Connection string sample (join avoids pre-commit hook literal detection)
_CONN = "".join(
    [
        '"AccountEndpoint=https://',
        "mydb.documents.azure.com",
        ';AccountKey=secret123=="',
    ]
)


# ---------------------------------------------------------------------------
# Helper: run hook via subprocess (JSON entrypoint tests)
# ---------------------------------------------------------------------------


def _run_hook(tool_name: str, file_path: str, content: str) -> dict:
    """Execute credential-scan.py via subprocess with JSON stdin."""
    payload = {
        "tool_name": tool_name,
        "tool_input": {"file_path": file_path},
    }
    if tool_name == "Write":
        payload["tool_input"]["content"] = content
    elif tool_name == "Edit":
        payload["tool_input"]["new_string"] = content
    result = subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0
    return json.loads(result.stdout)


# ===================================================================
# HELPER-LEVEL TESTS (direct function calls)
# ===================================================================


class TestFixtureSuppression:
    """Value-scoped suppression for approved test fixtures."""

    def test_fixture_in_test_path_allowed(self):
        content = f'"{_FIX_LIVE}"'
        findings = _scan_content(content, "tests/flows/test_something.py")
        assert findings == []

    def test_fixture_in_conftest_allowed(self):
        content = f'"{_FIX_ARSK}"'
        findings = _scan_content(content, "tests/conftest.py")
        assert findings == []

    def test_fixture_in_middleware_pipeline_allowed(self):
        content = f'"{_FIX_SPA}"'
        path = "tests/multi_tenant/test_middleware_pipeline.py"
        findings = _scan_content(content, path)
        assert findings == []

    def test_fixture_in_test_script_allowed(self):
        content = f'"{_FIX_PKLIVE}"'
        findings = _scan_content(content, "scripts/test_e2e_flows.py")
        assert findings == []


class TestNonFixtureBlocked:
    def test_unknown_key_in_test_path_blocked(self):
        content = f'"{_SAMPLE_REAL}"'
        findings = _scan_content(content, "tests/some_test.py")
        assert len(findings) > 0
        assert "Hardcoded API key" in findings[0]


class TestFixtureWrongPath:
    def test_fixture_in_src_blocked(self):
        content = f'"{_FIX_LIVE}"'
        findings = _scan_content(content, "src/some_module.py")
        assert len(findings) > 0


class TestNoBlanketExclusions:
    def test_new_key_in_conftest_blocked(self):
        content = f'"{_SAMPLE_NEW_CONFTEST}"'
        findings = _scan_content(content, "tests/conftest.py")
        assert len(findings) > 0

    def test_new_key_in_middleware_blocked(self):
        content = f'"{_SAMPLE_NEW_MW}"'
        path = "tests/multi_tenant/test_middleware_pipeline.py"
        findings = _scan_content(content, path)
        assert len(findings) > 0


class TestFQDNAndConnStringDetection:
    def test_azure_fqdn_blocked(self):
        findings = _scan_content(_FQDN, "src/config.py")
        assert any("FQDN" in f for f in findings)

    def test_cosmos_connection_string_blocked(self):
        findings = _scan_content(_CONN, "src/config.py")
        assert any("connection string" in f for f in findings)


class TestUnquotedDetection:
    def test_yaml_value_blocked(self):
        content = f"value: {_SAMPLE_DEMO}"
        findings = _scan_content(content, "config/settings.yaml")
        assert len(findings) > 0

    def test_env_assignment_blocked(self):
        content = f"ADMIN_KEY={_SAMPLE_DEMO}"
        findings = _scan_content(content, "scripts/setup.sh")
        assert len(findings) > 0


class TestBareEditPayload:
    def test_bare_key_blocked(self):
        findings = _scan_content(_SAMPLE_DEMO, "src/config.py")
        assert len(findings) > 0


class TestHyphenKeys:
    def test_quoted_hyphen_key_blocked(self):
        content = f'"{_SAMPLE_HYPHEN_QUOTED}"'
        findings = _scan_content(content, "src/config.py")
        assert len(findings) > 0

    def test_bare_hyphen_key_blocked(self):
        findings = _scan_content(_SAMPLE_HYPHEN_BARE, "src/config.py")
        assert len(findings) > 0


class TestPunctuationBoundary:
    def test_period_terminated(self):
        content = f"Staging key: {_SAMPLE_HYPHEN_BARE}."
        findings = _scan_content(content, "docs/setup.md")
        assert len(findings) > 0

    def test_semicolon_terminated(self):
        content = f"KEY={_SAMPLE_HYPHEN_QUOTED};"
        findings = _scan_content(content, "scripts/setup.sh")
        assert len(findings) > 0

    def test_paren_terminated(self):
        content = f"({_SAMPLE_DEMO})"
        findings = _scan_content(content, "src/config.py")
        assert len(findings) > 0

    def test_bracket_terminated(self):
        content = f"[{_SAMPLE_DEMO}]"
        findings = _scan_content(content, "src/config.py")
        assert len(findings) > 0

    def test_newline_terminated(self):
        content = f"{_SAMPLE_DEMO}\nnext_line"
        findings = _scan_content(content, "src/config.py")
        assert len(findings) > 0


class TestInventoryCoverage:
    def test_fixture_set_count(self):
        assert len(_FIXTURE_VALUES) == 52

    def test_docstring_example_set_count(self):
        assert len(_DOCSTRING_EXAMPLE_VALUES) == 5

    def test_source_examples_suppressed_in_approved_paths(self):
        for value in _DOCSTRING_EXAMPLE_VALUES:
            assert _is_fixture_suppressed(value, "src/multi_tenant/auth.py")

    def test_source_examples_blocked_outside_approved_paths(self):
        for value in _DOCSTRING_EXAMPLE_VALUES:
            assert not _is_fixture_suppressed(value, "src/some_other_module.py")

    def test_fixture_inventory_covers_repo(self):
        """Verify _FIXTURE_VALUES covers actual repo test fixtures.

        Runs rg to find all key-shaped values in tests/ and scripts/test_*,
        then asserts they are all in the allowlist.
        """
        import re as _re

        pattern = _re.compile(
            r"(ar_user|ar_live|ar_spa_plat|ar_spa|ar_tenant"
            r"|ar_widget|pk_live|arsk)_[A-Za-z0-9_-]{10,}"
        )
        repo_root = Path(__file__).resolve().parents[2]
        tests_dir = repo_root / "tests"
        scripts_dir = repo_root / "scripts"

        repo_values: set[str] = set()
        # Scan test files
        for py_file in tests_dir.rglob("*.py"):
            if "results" in py_file.parts:
                continue
            try:
                text = py_file.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for m in pattern.finditer(text):
                repo_values.add(m.group(0))
        # Scan test scripts
        for py_file in scripts_dir.glob("test_*.py"):
            try:
                text = py_file.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for m in pattern.finditer(text):
                repo_values.add(m.group(0))

        missing = repo_values - _FIXTURE_VALUES
        assert not missing, f"Repo has {len(missing)} key-shaped values not in _FIXTURE_VALUES: {sorted(missing)[:5]}"

    def test_docstring_inventory_covers_repo(self):
        """Verify _DOCSTRING_EXAMPLE_VALUES covers actual source examples."""
        import re as _re

        pattern = _re.compile(
            r"(ar_user|ar_live|ar_spa_plat|ar_spa|ar_tenant"
            r"|ar_widget|pk_live|arsk)_[A-Za-z0-9_-]{10,}"
        )
        repo_root = Path(__file__).resolve().parents[2]
        approved_files = [
            repo_root / "src" / "multi_tenant" / "auth.py",
            repo_root / "src" / "multi_tenant" / "admin_apikey_api.py",
        ]
        repo_values: set[str] = set()
        for src_file in approved_files:
            text = src_file.read_text(encoding="utf-8")
            for m in pattern.finditer(text):
                repo_values.add(m.group(0))

        missing = repo_values - _DOCSTRING_EXAMPLE_VALUES
        assert not missing, (
            f"Source files have {len(missing)} example values not in _DOCSTRING_EXAMPLE_VALUES: {sorted(missing)}"
        )


# ===================================================================
# ENTRYPOINT TESTS (subprocess JSON stdin/stdout)
# ===================================================================


class TestEntrypointWrite:
    """Test the hook's main() via subprocess for Write tool."""

    def test_write_fixture_in_test_path_allowed(self):
        result = _run_hook("Write", "tests/conftest.py", f'"{_FIX_ARSK}"')
        assert result == {}

    def test_write_non_fixture_in_test_path_blocked(self):
        result = _run_hook("Write", "tests/conftest.py", f'"{_SAMPLE_NEW_CONFTEST}"')
        assert result.get("decision") == "block"

    def test_write_excluded_path_allowed(self):
        result = _run_hook("Write", "memory/notes.md", f'"{_SAMPLE_REAL}"')
        assert result == {}

    def test_write_fqdn_blocked(self):
        result = _run_hook("Write", "src/config.py", _FQDN)
        assert result.get("decision") == "block"


class TestEntrypointEdit:
    """Test the hook's main() via subprocess for Edit tool."""

    def test_edit_bare_key_blocked(self):
        result = _run_hook("Edit", "src/config.py", _SAMPLE_DEMO)
        assert result.get("decision") == "block"

    def test_edit_fixture_in_test_allowed(self):
        result = _run_hook("Edit", "tests/some_test.py", f'"{_FIX_LIVE}"')
        assert result == {}

    def test_edit_non_write_tool_ignored(self):
        """Non-Write/Edit tools are not scanned."""
        payload = {
            "tool_name": "Read",
            "tool_input": {"file_path": "src/config.py"},
        }
        result = subprocess.run(
            [sys.executable, str(HOOK_PATH)],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert json.loads(result.stdout) == {}
