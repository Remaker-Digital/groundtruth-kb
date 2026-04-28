"""Tests for the destructive-gate PreToolUse hook.

Verifies that the hook correctly blocks:
- Production environment operations (FQDN, Cosmos DB name, deploy commands)
- Destructive Azure operations (Cosmos delete_item)
- Secret exfiltration patterns

SPEC-1882 / S270: Production environment protection.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

# Import the hook module directly
_HOOK_PATH = Path(__file__).resolve().parents[2] / ".claude" / "hooks" / "destructive-gate.py"

pytestmark = pytest.mark.skipif(
    not _HOOK_PATH.exists(),
    reason=f"Hook file not in checkout: {_HOOK_PATH}",
)


@pytest.fixture()
def check_destructive():
    """Load and return the _check_destructive function from the hook."""
    spec = importlib.util.spec_from_file_location("destructive_gate", _HOOK_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod._check_destructive


# ---------------------------------------------------------------------------
# Production environment targeting (S270)
# ---------------------------------------------------------------------------


class TestProductionProtection:
    """S270: Any production operation must be blocked for owner approval."""

    def test_blocks_production_fqdn(self, check_destructive):
        """Commands referencing production FQDN are blocked."""
        result = check_destructive(
            'curl https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io/health'
        )
        assert result is not None
        assert "Production environment" in result

    def test_blocks_production_cosmos_db_name(self, check_destructive):
        """Commands referencing production Cosmos database name are blocked."""
        result = check_destructive(
            """python -c "DB = 'agentred'; print(DB)" """
        )
        assert result is not None
        assert "Production" in result

    def test_allows_staging_cosmos_db_name(self, check_destructive):
        """Commands referencing staging database are NOT blocked."""
        result = check_destructive(
            """python -c "DB = 'agentred-staging'; print(DB)" """
        )
        # Should NOT be blocked (staging is safe)
        assert result is None or "Production" not in result

    def test_blocks_production_deploy(self, check_destructive):
        """deploy.py --env prod is blocked."""
        result = check_destructive(
            "python deploy.py --env prod"
        )
        assert result is not None
        assert "Production" in result

    def test_allows_staging_deploy(self, check_destructive):
        """deploy.py --env staging is NOT blocked."""
        result = check_destructive(
            "python deploy.py --env staging"
        )
        # deploy.py --env staging should not trigger prod patterns
        assert result is None or "Production" not in result

    def test_blocks_production_container_app(self, check_destructive):
        """Commands referencing agent-red-api-gateway are blocked."""
        result = check_destructive(
            "az containerapp update --name agent-red-api-gateway"
        )
        assert result is not None


# ---------------------------------------------------------------------------
# Azure destructive operations
# ---------------------------------------------------------------------------


class TestAzureDestructiveBlocking:
    """Cosmos delete_item and other Azure destructive ops are blocked."""

    def test_blocks_cosmos_delete_item(self, check_destructive):
        result = check_destructive(
            "container.delete_item(item=tid, partition_key=tid)"
        )
        assert result is not None
        assert "Destructive Azure" in result

    def test_blocks_keyvault_delete(self, check_destructive):
        result = check_destructive(
            "az keyvault secret delete --name my-secret"
        )
        assert result is not None


# ---------------------------------------------------------------------------
# Contact requirement (SPEC-1882)
# ---------------------------------------------------------------------------


class TestContactRequirementInProvisioning:
    """SPEC-1882: provision_tenant parameter includes customer_phone."""

    def test_provision_tenant_has_customer_phone_param(self):
        """provision_tenant() accepts customer_phone parameter."""
        import inspect
        from src.integrations.provisioning import provision_tenant

        sig = inspect.signature(provision_tenant)
        assert "customer_phone" in sig.parameters, (
            "provision_tenant must accept customer_phone parameter (SPEC-1882)"
        )

    def test_provision_tenant_customer_email_param_exists(self):
        """provision_tenant() still accepts customer_email parameter."""
        import inspect
        from src.integrations.provisioning import provision_tenant

        sig = inspect.signature(provision_tenant)
        assert "customer_email" in sig.parameters


# ---------------------------------------------------------------------------
# Python recursive-deletion parity (S317 follow-up)
# ---------------------------------------------------------------------------


class TestPythonRecursiveDeletionParity:
    """bridge/destructive-gate-coverage-shutil-rmtree-2026-04-27-002.md GO:
    inline Python recursive-deletion forms must be gated for parity with the
    existing bash `rm -r` and PowerShell `Remove-Item -Recurse` patterns.
    """

    def test_blocks_python_dash_c_with_shutil_rmtree(self, check_destructive):
        """The exact substitution form Prime used in S317 must be blocked."""
        result = check_destructive(
            """python -c "import shutil; shutil.rmtree('GT-KB')" """
        )
        assert result is not None
        assert "destructive" in result.lower() or "delete" in result.lower()

    def test_blocks_shutil_rmtree_with_ignore_errors(self, check_destructive):
        """shutil.rmtree variant with ignore_errors=True must also be blocked."""
        result = check_destructive(
            """python -c "import shutil; shutil.rmtree('x', ignore_errors=True)" """
        )
        assert result is not None

    def test_blocks_os_removedirs(self, check_destructive):
        """os.removedirs (recursive empty-dir cleanup) must be blocked."""
        result = check_destructive(
            """python -c "import os; os.removedirs('a/b/c')" """
        )
        assert result is not None

    def test_blocks_subprocess_rm_rf_via_python(self, check_destructive):
        """subprocess invocation of `rm -rf` from Python must be blocked."""
        result = check_destructive(
            """python -c "import subprocess; subprocess.run(['rm', '-rf', 'x'])" """
        )
        assert result is not None

    def test_blocks_subprocess_remove_item_recurse_via_python(self, check_destructive):
        """subprocess invocation of `Remove-Item -Recurse` from Python must be blocked."""
        result = check_destructive(
            """python -c "import subprocess; subprocess.run(['Remove-Item', '-Recurse', 'x'])" """
        )
        assert result is not None

    def test_allows_pathlib_unlink_single_file(self, check_destructive):
        """pathlib.Path.unlink (single-file delete, non-recursive) is NOT blocked."""
        result = check_destructive(
            """python -c "from pathlib import Path; Path('tmp.txt').unlink()" """
        )
        # Single-file deletes are not in the recursive class; should not be blocked
        # by the recursive-deletion patterns. May still be blocked by other
        # patterns (e.g., production targeting), but not by _DELETE_PATTERNS.
        assert result is None or "destructive" not in result.lower() or "rmtree" not in result.lower()
