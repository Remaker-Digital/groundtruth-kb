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
            "curl https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io/health"
        )
        assert result is not None
        assert "Production environment" in result

    def test_blocks_production_cosmos_db_name(self, check_destructive):
        """Commands referencing production Cosmos database name are blocked."""
        result = check_destructive("""python -c "DB = 'agentred'; print(DB)" """)
        assert result is not None
        assert "Production" in result

    def test_allows_staging_cosmos_db_name(self, check_destructive):
        """Commands referencing staging database are NOT blocked."""
        result = check_destructive("""python -c "DB = 'agentred-staging'; print(DB)" """)
        # Should NOT be blocked (staging is safe)
        assert result is None or "Production" not in result

    def test_blocks_production_deploy(self, check_destructive):
        """deploy.py --env prod is blocked."""
        result = check_destructive("python deploy.py --env prod")
        assert result is not None
        assert "Production" in result

    def test_allows_staging_deploy(self, check_destructive):
        """deploy.py --env staging is NOT blocked."""
        result = check_destructive("python deploy.py --env staging")
        # deploy.py --env staging should not trigger prod patterns
        assert result is None or "Production" not in result

    def test_blocks_production_container_app(self, check_destructive):
        """Commands referencing agent-red-api-gateway are blocked."""
        result = check_destructive("az containerapp update --name agent-red-api-gateway")
        assert result is not None


# ---------------------------------------------------------------------------
# Azure destructive operations
# ---------------------------------------------------------------------------


class TestAzureDestructiveBlocking:
    """Cosmos delete_item and other Azure destructive ops are blocked."""

    def test_blocks_cosmos_delete_item(self, check_destructive):
        result = check_destructive("container.delete_item(item=tid, partition_key=tid)")
        assert result is not None
        assert "Destructive Azure" in result

    def test_blocks_keyvault_delete(self, check_destructive):
        result = check_destructive("az keyvault secret delete --name my-secret")
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
        assert "customer_phone" in sig.parameters, "provision_tenant must accept customer_phone parameter (SPEC-1882)"

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
        result = check_destructive("""python -c "import shutil; shutil.rmtree('GT-KB')" """)
        assert result is not None
        assert "destructive" in result.lower() or "delete" in result.lower()

    def test_blocks_shutil_rmtree_with_ignore_errors(self, check_destructive):
        """shutil.rmtree variant with ignore_errors=True must also be blocked."""
        result = check_destructive("""python -c "import shutil; shutil.rmtree('x', ignore_errors=True)" """)
        assert result is not None

    def test_blocks_os_removedirs(self, check_destructive):
        """os.removedirs (recursive empty-dir cleanup) must be blocked."""
        result = check_destructive("""python -c "import os; os.removedirs('a/b/c')" """)
        assert result is not None

    def test_blocks_subprocess_rm_rf_via_python(self, check_destructive):
        """subprocess invocation of `rm -rf` from Python must be blocked."""
        result = check_destructive("""python -c "import subprocess; subprocess.run(['rm', '-rf', 'x'])" """)
        assert result is not None

    def test_blocks_subprocess_remove_item_recurse_via_python(self, check_destructive):
        """subprocess invocation of `Remove-Item -Recurse` from Python must be blocked."""
        result = check_destructive(
            """python -c "import subprocess; subprocess.run(['Remove-Item', '-Recurse', 'x'])" """
        )
        assert result is not None

    def test_allows_pathlib_unlink_single_file(self, check_destructive):
        """pathlib.Path.unlink (single-file delete, non-recursive) is NOT blocked."""
        result = check_destructive("""python -c "from pathlib import Path; Path('tmp.txt').unlink()" """)
        # Single-file deletes are not in the recursive class; should not be blocked
        # by the recursive-deletion patterns. May still be blocked by other
        # patterns (e.g., production targeting), but not by _DELETE_PATTERNS.
        assert result is None or "destructive" not in result.lower() or "rmtree" not in result.lower()

    def test_blocks_shutil_rmtree_with_unrelated_safe_path_substring(self, check_destructive):
        """Per bridge/destructive-gate-coverage-shutil-rmtree-2026-04-27-004 NO-GO:
        Python recursive-deletion must NOT be bypassed by an unrelated safe-path
        substring elsewhere in the command. Critical bypass test #1.
        """
        result = check_destructive("""python -c "import shutil; print('node_modules'); shutil.rmtree('GT-KB')" """)
        assert result is not None, (
            "shutil.rmtree must remain blocked even when an unrelated safe-path "
            "substring (node_modules) appears in a print statement. "
            "Got: result is None (would have allowed the deletion)."
        )

    def test_blocks_shutil_rmtree_with_safe_path_in_comment(self, check_destructive):
        """Per bridge/destructive-gate-coverage-shutil-rmtree-2026-04-27-004 NO-GO:
        Critical bypass test #2 — safe-path substring in a Python comment must
        not suppress the block.
        """
        result = check_destructive("""python -c "import shutil; shutil.rmtree('GT-KB') # node_modules" """)
        assert result is not None, (
            "shutil.rmtree must remain blocked even when an unrelated safe-path "
            "substring (node_modules) appears in a comment. "
            "Got: result is None (would have allowed the deletion)."
        )


# ---------------------------------------------------------------------------
# WI-3493: quote-aware git / hook-bypass verb families.
# bridge/gtkb-bash-hook-destructive-substring-false-positive-002.md (GO, option b).
# ---------------------------------------------------------------------------


@pytest.fixture()
def gate_module():
    """Load and return the full destructive-gate module (for helper-level tests)."""
    spec = importlib.util.spec_from_file_location("destructive_gate_full", _HOOK_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestWI3493QuoteAwareDestructiveVerbs:
    """A destructive verb inside a quoted span / scope text must not false-block,
    while a genuine unquoted destructive command still blocks (GO -002 option b:
    mask _GIT_DESTRUCTIVE + _HOOK_BYPASS; keep _DB_DESTRUCTIVE raw)."""

    # --- False positive removed (quoted / scope text) ---

    def test_quoted_git_rm_scope_text_not_blocked(self, check_destructive):
        result = check_destructive('echo "remember to git rm the stale fixture before promotion"')
        assert result is None

    def test_quoted_git_reset_hard_in_python_literal_not_blocked(self, check_destructive):
        result = check_destructive("""python -c "msg = 'git reset --hard rewrites history'; print(msg)" """)
        assert result is None

    def test_quoted_no_verify_in_commit_message_not_blocked(self, check_destructive):
        result = check_destructive('git commit -m "WIP: never pass --no-verify on this repo"')
        assert result is None

    def test_quoted_force_push_scope_text_not_blocked(self, check_destructive):
        result = check_destructive('echo "the proposal forbids git push --force to develop"')
        assert result is None

    # --- True positive preserved (genuine unquoted command) ---

    def test_genuine_unquoted_git_rm_still_blocks(self, check_destructive):
        result = check_destructive("git rm --cached secrets.env")
        assert result is not None
        assert "git" in result.lower()

    def test_genuine_unquoted_git_reset_hard_still_blocks(self, check_destructive):
        result = check_destructive("git reset --hard HEAD~3")
        assert result is not None

    def test_genuine_unquoted_no_verify_commit_still_blocks(self, check_destructive):
        result = check_destructive('git commit --no-verify -m "skip the gates"')
        assert result is not None
        assert "bypass" in result.lower()

    def test_genuine_unquoted_force_push_still_blocks(self, check_destructive):
        result = check_destructive("git push --force origin main")
        assert result is not None

    # --- R3 option b: _DB_DESTRUCTIVE stays RAW (quoted DROP TABLE still blocks) ---

    def test_db_destructive_remains_raw_blocks_quoted_drop_table(self, check_destructive):
        result = check_destructive("""python -c "cur.execute('DROP TABLE users')" """)
        assert result is not None
        assert "database" in result.lower()

    # --- Helper-level coverage ---

    def test_mask_blanks_quoted_interior_preserves_quotes(self, gate_module):
        # Interior "git rm x" is 8 characters -> 8 blanks; quote chars preserved.
        masked = gate_module._mask_quoted_spans('echo "git rm x"')
        assert masked == 'echo "        "'

    def test_mask_leaves_unquoted_text_intact(self, gate_module):
        masked = gate_module._mask_quoted_spans("git rm --cached f")
        assert masked == "git rm --cached f"

    def test_mask_unbalanced_quote_blanks_to_end(self, gate_module):
        # Fail-closed: an unbalanced quote masks to end-of-string (exposes nothing
        # structural that was outside the quote).
        masked = gate_module._mask_quoted_spans('git rm "oops unterminated')
        assert masked == 'git rm "                 '
