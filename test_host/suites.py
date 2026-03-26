# test_host/suites.py — Suite-to-pytest mapping for cloud-native test runner
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

"""
Maps suite names (selected in the SPA) to pytest arguments and metadata.
Each suite defines the test paths, timeout, environment variables needed,
and whether it requires special tooling (Playwright, Locust, etc.).
"""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Suites safe for pytest-xdist parallelization.
# These use mocks/fakes with no shared mutable state across workers.
# Excludes: e2e_live (shared Chromium + staging mutations),
#           load (Locust multiplied load), fuzzing (multiplied HTTP volume).
# ---------------------------------------------------------------------------
PARALLELIZABLE_SUITES = frozenset({
    "unit", "core", "integration", "agents", "security",
    "regression", "ops", "property",
    # S220: widget removed — 723 source-inspection tests run in <1s without
    # xdist. xdist adds worker-spawning overhead and the composite was
    # stalling during widget phase (workers holding stdout pipe open after
    # killpg). Not worth parallelizing for sub-second tests.
})


@dataclass(frozen=True)
class SuiteConfig:
    """Configuration for a test suite."""

    name: str
    label: str
    pytest_args: list[str]
    timeout_s: int = 300
    env_vars: dict[str, str] = field(default_factory=dict)
    requires_playwright: bool = False
    requires_locust: bool = False
    is_composite: bool = False
    composite_suites: list[str] = field(default_factory=list)
    estimated_tests: int = 0
    estimated_duration_s: int = 0

    def can_run(self) -> tuple[bool, str]:
        """Pre-flight check: can this suite run in the current environment?

        Returns (True, '') if runnable, or (False, reason) if not.
        For composite suites, checks all sub-suites and reports any that can't run.
        """
        if self.is_composite:
            # A composite suite can run if ALL its sub-suites can run
            for sub_name in self.composite_suites:
                sub = SUITE_CONFIGS.get(sub_name)
                if not sub:
                    return False, f"Sub-suite '{sub_name}' not found"
                ok, reason = sub.can_run()
                if not ok:
                    return False, f"Sub-suite '{sub_name}': {reason}"
            return True, ""

        if self.requires_playwright:
            # Playwright + chromium must be installed
            if not shutil.which("playwright"):
                return False, "Playwright CLI not installed"
        if self.requires_locust:
            # Locust must be importable
            if not shutil.which("locust"):
                return False, "Locust not installed"
        return True, ""


# ---------------------------------------------------------------------------
# Individual suites — each maps to a pytest invocation
# ---------------------------------------------------------------------------

SUITE_CONFIGS: dict[str, SuiteConfig] = {
    "unit": SuiteConfig(
        name="unit",
        label="Unit Tests",
        pytest_args=["tests/unit/", "-x", "--timeout=30", "-q"],
        timeout_s=300,
        estimated_tests=950,
        estimated_duration_s=120,
    ),
    "core": SuiteConfig(
        name="core",
        label="Core / Multi-Tenant Tests",
        pytest_args=[
            "tests/multi_tenant/",
            "tests/migrations/",
            # Exclude tests that read dev-only files not in the container
            # (.claude/, branding/, docs-site/, .env.local, knowledge.db, memory/)
            "--ignore-glob=tests/multi_tenant/test_s153_batch*_spec_verification.py",
            "--ignore=tests/multi_tenant/test_s153_documentation_specs.py",
            "--ignore=tests/multi_tenant/test_s153_future_feature_verification.py",
            "--ignore=tests/multi_tenant/test_s153_testing_quality_specs.py",
            "--ignore=tests/multi_tenant/test_document_parser_files.py",
            "--ignore=tests/multi_tenant/test_mutation_tenant_admin.py",
            "--ignore=tests/multi_tenant/test_phase6_deferred.py",
            "--ignore=tests/multi_tenant/test_build_orchestrator.py",
            "--ignore=tests/multi_tenant/test_s175_scaling_680.py",
            "-x",
            "--timeout=30",
            "-q",
        ],
        timeout_s=600,
        estimated_tests=3700,
        estimated_duration_s=300,
    ),
    "integration": SuiteConfig(
        name="integration",
        label="Integration Tests",
        pytest_args=[
            "tests/integration/",
            "tests/integrations/",
            # Exclude tests requiring external services not available in container
            "--ignore=tests/integration/test_azure_services.py",  # Azure SDK calls
            "--ignore=tests/integration/test_integration_real_services.py",  # Live service endpoints
            "--ignore=tests/integration/test_nats_jetstream.py",  # NATS broker connection
            "-x",
            "--timeout=30",
            "-q",
        ],
        timeout_s=600,
        estimated_tests=270,
        estimated_duration_s=180,
    ),
    "agents": SuiteConfig(
        name="agents",
        label="Agent & Chat Tests",
        pytest_args=[
            "tests/agents/",
            "tests/chat/",
            "tests/persistent_memory/",
            "-x",
            "--timeout=30",
            "-q",
        ],
        timeout_s=600,
        estimated_tests=300,
        estimated_duration_s=180,
    ),
    "security": SuiteConfig(
        name="security",
        label="Security & Penetration",
        pytest_args=[
            "tests/security/",
            # Exclude tests requiring external services/files not in container
            "--ignore=tests/security/test_ci_tooling.py",  # CI pipeline tooling
            "--ignore=tests/security/test_documentation_cleanup.py",  # Docs filesystem scan
            "--ignore=tests/security/test_data_integrity_live.py",  # Live Cosmos data checks
            "--ignore=tests/security/test_resilience_live.py",  # Live resilience probes
            "--ignore=tests/security/test_tenant_isolation_live.py",  # Live tenant boundary tests
            "--timeout=60",
            "-q",
        ],
        timeout_s=600,
        estimated_tests=150,
        estimated_duration_s=180,
    ),
    "regression": SuiteConfig(
        name="regression",
        label="Regression (Tier 0/1/2)",
        pytest_args=["tests/regression/", "--timeout=30", "-q"],
        timeout_s=300,
        estimated_tests=47,
        estimated_duration_s=60,
    ),
    "e2e_live": SuiteConfig(
        name="e2e_live",
        label="E2E Live — Playwright",
        pytest_args=[
            "tests/e2e_live/",
            "--timeout=120",
            # Bail after 100 failures so we capture partial results before
            # OOM kills the entire suite (273 classes × Chromium in 4 GB).
            "--maxfail=100",
            "-q",
        ],
        timeout_s=3600,
        requires_playwright=True,
        estimated_tests=1100,
        estimated_duration_s=900,
    ),
    "widget": SuiteConfig(
        name="widget",
        label="Widget Tests",
        pytest_args=[
            "tests/widget/",
            # Exclude tests reading admin source .tsx (only dist/ in container)
            "--ignore=tests/widget/test_admin_ui_labels.py",
            "--ignore=tests/widget/test_auth_interceptor.py",
            "--timeout=30",
            "-q",
        ],
        timeout_s=60,  # S220: 723 source-inspection tests run in <1s; 60s generous
        estimated_tests=60,
        estimated_duration_s=5,
    ),
    "load": SuiteConfig(
        name="load",
        label="Load Testing — Locust",
        # Locust runs via a wrapper script, not pytest directly
        pytest_args=[],
        timeout_s=900,
        requires_locust=True,
        estimated_tests=1,
        estimated_duration_s=300,
    ),
    "fuzzing": SuiteConfig(
        name="fuzzing",
        label="API Fuzzing -- Schemathesis",
        pytest_args=["tests/fuzzing/", "--timeout=300", "-q"],
        timeout_s=2400,
        estimated_tests=10,
        estimated_duration_s=600,
        env_vars={
            # Point Schemathesis at the live staging API so fuzzing tests
            # the real deployed stack (Cosmos, Redis, middleware).
            "FUZZ_TARGET_URL": os.environ.get("STAGING_URL", ""),  # SPEC-0058: No hardcoded FQDNs
            # SPEC-0058: API key from env var, not hardcoded.
            "FUZZ_API_KEY": os.environ.get("STAGING_SPA_KEY", os.environ.get("SUPERADMIN_PREVIEW_API_KEY", "")),
        },
    ),
    "property": SuiteConfig(
        name="property",
        label="Property Tests — Hypothesis",
        pytest_args=["tests/property/", "--timeout=60", "-q"],
        timeout_s=600,
        estimated_tests=46,
        estimated_duration_s=120,
    ),
    "ops": SuiteConfig(
        name="ops",
        label="Operations & Resilience",
        pytest_args=[
            "tests/ops/",
            # Exclude tests reading .claude/ hooks (not in container image)
            "--ignore=tests/ops/test_hooks_specs.py",
            # Exclude Dockerfile coverage test (reads Dockerfile.test, not in container)
            "--ignore=tests/ops/test_dockerfile_test_coverage.py",
            "--timeout=60",
            "-q",
        ],
        timeout_s=600,
        estimated_tests=80,
        estimated_duration_s=240,
    ),
}

# ---------------------------------------------------------------------------
# Composite suites — run multiple individual suites sequentially
# ---------------------------------------------------------------------------

SUITE_CONFIGS["full"] = SuiteConfig(
    name="full",
    label="Complete Suite — Everything",
    pytest_args=[],  # Uses composite execution
    timeout_s=7200,
    is_composite=True,
    composite_suites=[
        "unit",
        "core",
        "integration",
        "agents",
        "security",
        "regression",
        "ops",
        # S220: widget moved after heavy suites — 723 source-inspection
        # tests that don't need deployed services.  Prevents container
        # stalls from blocking e2e_live/load/fuzzing/property.
        "e2e_live",
        "load",
        "fuzzing",
        "property",
        "widget",
    ],
    estimated_tests=7100,
    estimated_duration_s=3000,
)


def get_suite(name: str) -> SuiteConfig | None:
    """Get suite configuration by name."""
    return SUITE_CONFIGS.get(name)


def list_suites() -> list[dict]:
    """Return suite metadata for SPA display, including runnability."""
    result = []
    for cfg in SUITE_CONFIGS.values():
        runnable, reason = cfg.can_run()
        result.append({
            "name": cfg.name,
            "label": cfg.label,
            "estimated_tests": cfg.estimated_tests,
            "estimated_duration_s": cfg.estimated_duration_s,
            "is_composite": cfg.is_composite,
            "requires_playwright": cfg.requires_playwright,
            "requires_locust": cfg.requires_locust,
            "runnable": runnable,
            "reason": reason,
        })
    return result
