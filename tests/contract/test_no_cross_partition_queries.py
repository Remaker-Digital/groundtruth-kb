"""Regression test: no cross-partition queries in production code paths.

SPEC-1644 mandates that tenant lookups by external identifiers (Shopify
domain, Stripe customer ID) MUST use the domain_index collection for O(1)
point reads, not cross-partition scans against the tenants collection.

This test statically verifies that:
1. No production code (outside of TenantRepository itself) calls the
   deprecated cross-partition methods.
2. The domain_index collection is properly defined in the schema.
3. All lifecycle wiring passes domain_index_repo to consuming services.
4. The DomainIndexRepository.lookup() never uses cross-partition queries.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import ast
import os
import re

import pytest

# Root of the source tree
SRC_ROOT = os.path.join(
    os.path.dirname(__file__), os.pardir, os.pardir, "src",
)
SRC_ROOT = os.path.normpath(SRC_ROOT)

# Files that are ALLOWED to define cross-partition methods (the repository
# itself) — but callers must NOT invoke them.
ALLOWED_DEFINITION_FILES = {
    os.path.normpath("src/multi_tenant/repositories/tenant.py"),
}

# The deprecated method names that perform cross-partition queries.
CROSS_PARTITION_METHODS = {
    "find_by_shopify_domain",
    "find_by_stripe_customer_id",
}


def _python_files_in(root: str) -> list[str]:
    """Yield all .py files under *root*."""
    result = []
    for dirpath, _dirs, files in os.walk(root):
        for fname in files:
            if fname.endswith(".py"):
                result.append(os.path.join(dirpath, fname))
    return result


def _relative(path: str) -> str:
    """Return path relative to the repo root for readable messages."""
    repo_root = os.path.normpath(os.path.join(SRC_ROOT, os.pardir))
    return os.path.relpath(path, repo_root)


class TestNoCrossPartitionQueries:
    """Static analysis: cross-partition queries must not appear in callers."""

    def test_no_caller_invokes_cross_partition_methods(self) -> None:
        """No production file outside the repository definition may call
        find_by_shopify_domain or find_by_stripe_customer_id.

        The only legitimate call sites are:
        - The method definitions themselves (in tenant.py)
        - Fallback paths in lifecycle.py (wrapped by domain-index-first logic)
        - GDPR webhook fallback (wrapped by domain-index-first logic)

        Any NEW direct call to these methods is a regression.
        """
        violations: list[str] = []

        # Files that are allowed to reference these methods (they wrap them
        # behind domain-index-first logic with fallback).
        ALLOWED_CALLERS = {
            os.path.normpath("src/multi_tenant/repositories/tenant.py"),
            os.path.normpath("src/app/lifecycle.py"),
            os.path.normpath("src/integrations/shopify_gdpr_webhooks.py"),
        }

        for filepath in _python_files_in(SRC_ROOT):
            rel = _relative(filepath)
            norm_rel = os.path.normpath(rel)
            if norm_rel in ALLOWED_CALLERS:
                continue

            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            for method in CROSS_PARTITION_METHODS:
                # Look for .method_name( calls — not just the string in comments
                pattern = rf"\.{method}\s*\("
                for match in re.finditer(pattern, content):
                    line_num = content[:match.start()].count("\n") + 1
                    violations.append(
                        f"{rel}:{line_num} calls .{method}() — "
                        f"use DomainIndexRepository.lookup() instead"
                    )

        assert not violations, (
            "Cross-partition query methods called from production code "
            "(SPEC-1644 violation):\n" + "\n".join(violations)
        )

    def test_domain_index_collection_exists_in_schema(self) -> None:
        """The domain_index collection must be defined in cosmos_schema.py."""
        from src.multi_tenant.cosmos_schema import COLLECTION_DOMAIN_INDEX

        assert COLLECTION_DOMAIN_INDEX == "domain_index"

    def test_domain_index_collection_has_correct_partition_key(self) -> None:
        """domain_index partition key must be /domain for point reads."""
        from src.multi_tenant.cosmos_schema import get_collection_configs

        configs = get_collection_configs()
        domain_config = None
        for cfg in configs:
            if cfg.name == "domain_index":
                domain_config = cfg
                break

        assert domain_config is not None, "domain_index not in collection configs"
        assert domain_config.partition_key == "/domain", (
            f"Expected /domain partition key, got {domain_config.partition_key}"
        )

    def test_domain_index_repository_uses_point_reads(self) -> None:
        """DomainIndexRepository.lookup() must use read_item (point read),
        NOT query_items (which could be cross-partition)."""
        repo_path = os.path.join(
            SRC_ROOT, "multi_tenant", "repositories", "domain_index.py",
        )
        with open(repo_path, "r", encoding="utf-8") as f:
            content = f.read()

        # lookup() must use read_item
        assert "read_item" in content, (
            "DomainIndexRepository must use read_item for O(1) point reads"
        )

        # lookup() must NOT use query_items
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "lookup":
                # Check that the lookup method body does not contain query_items
                source_lines = content.splitlines()
                func_source = "\n".join(
                    source_lines[node.lineno - 1:node.end_lineno]
                )
                assert "query_items" not in func_source, (
                    "DomainIndexRepository.lookup() must NOT use query_items — "
                    "use read_item for O(1) point reads"
                )
                break

    def test_provisioning_wired_with_domain_index(self) -> None:
        """provisioning.py must accept and store domain_index_repo."""
        prov_path = os.path.join(SRC_ROOT, "integrations", "provisioning.py")
        with open(prov_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "domain_index_repo" in content, (
            "provisioning.py must accept domain_index_repo parameter"
        )
        assert "_domain_index_repo" in content, (
            "provisioning.py must store domain_index_repo for lookups"
        )

    def test_lifecycle_passes_domain_index_to_provisioning(self) -> None:
        """lifecycle.py must pass domain_index_repo to configure_provisioning_repo."""
        lifecycle_path = os.path.join(SRC_ROOT, "app", "lifecycle.py")
        with open(lifecycle_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "domain_index_repo=" in content, (
            "lifecycle.py must pass domain_index_repo to configure_provisioning_repo"
        )

    def test_no_new_cross_partition_query_patterns(self) -> None:
        """Scan for raw cross-partition query patterns that bypass the index.

        Any query_items call on the tenants collection without a partition_key
        is suspicious. We check for the known anti-patterns.
        """
        violations: list[str] = []

        # Patterns that indicate a cross-partition query on tenants
        SUSPICIOUS_PATTERNS = [
            # SQL query filtering by shopify_shop_domain without partition key
            r"shopify_shop_domain\s*=\s*@",
            # SQL query filtering by stripe_customer_id without partition key
            r"stripe_customer_id\s*=\s*@",
        ]

        for filepath in _python_files_in(SRC_ROOT):
            rel = _relative(filepath)
            norm_rel = os.path.normpath(rel)

            # Skip the repository definition file and test files
            if norm_rel in ALLOWED_DEFINITION_FILES:
                continue

            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            for pattern in SUSPICIOUS_PATTERNS:
                for match in re.finditer(pattern, content):
                    line_num = content[:match.start()].count("\n") + 1
                    violations.append(
                        f"{rel}:{line_num} contains cross-partition query "
                        f"pattern: {match.group()} — use domain_index instead"
                    )

        assert not violations, (
            "New cross-partition query patterns detected (SPEC-1644 violation):\n"
            + "\n".join(violations)
        )
