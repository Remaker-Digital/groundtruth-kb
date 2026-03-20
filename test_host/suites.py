# test_host/suites.py — Suite-to-pytest mapping for cloud-native test runner
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

"""
Maps suite names (selected in the SPA) to pytest arguments and metadata.
Each suite defines the test paths, timeout, environment variables needed,
and whether it requires special tooling (Playwright, Locust, etc.).
"""

from __future__ import annotations

from dataclasses import dataclass, field


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
            # Exclude tests that read project files not in container
            "--ignore=tests/multi_tenant/test_s153_batch10_spec_verification.py",
            "--ignore=tests/multi_tenant/test_s153_batch11_spec_verification.py",
            "--ignore=tests/multi_tenant/test_s153_batch12_spec_verification.py",
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
    "e2e": SuiteConfig(
        name="e2e",
        label="E2E Live — Playwright",
        pytest_args=[
            "tests/e2e_live/",
            "--timeout=120",
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
        pytest_args=["tests/widget/", "--timeout=30", "-q"],
        timeout_s=300,
        estimated_tests=60,
        estimated_duration_s=120,
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
        label="API Fuzzing — Schemathesis",
        pytest_args=["tests/fuzzing/", "--timeout=120", "-q"],
        timeout_s=1200,
        estimated_tests=10,
        estimated_duration_s=300,
        env_vars={
            # Point Schemathesis at the live staging API so fuzzing tests
            # the real deployed stack (Cosmos, Redis, middleware).
            "FUZZ_TARGET_URL": "https://agent-red-staging.orangeglacier-f566a4e7.eastus.azurecontainerapps.io",
            # SPA platform admin key for authenticated fuzzing.
            # Safe to embed: staging-only key, test host is internal-ingress-only.
            "FUZZ_API_KEY": "ar_spa_plat_ukgY1GK594QUxICKJfIXFWiNrWxnkhvB",
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
        pytest_args=["tests/ops/", "--timeout=60", "-q"],
        timeout_s=600,
        estimated_tests=80,
        estimated_duration_s=240,
    ),
}

# ---------------------------------------------------------------------------
# Composite suites — run multiple individual suites sequentially
# ---------------------------------------------------------------------------

SUITE_CONFIGS["pipeline"] = SuiteConfig(
    name="pipeline",
    label="Full Pipeline — All 16 Phases",
    pytest_args=[],  # Uses composite execution
    timeout_s=3600,
    is_composite=True,
    composite_suites=[
        "unit",
        "core",
        "integration",
        "agents",
        "security",
        "regression",
        "ops",
        "widget",
        "e2e",
        "fuzzing",
        "property",
    ],
    estimated_tests=6700,
    estimated_duration_s=1800,
)

SUITE_CONFIGS["full"] = SuiteConfig(
    name="full",
    label="Complete Suite — Everything",
    pytest_args=[],  # Uses composite execution
    timeout_s=5400,
    is_composite=True,
    composite_suites=[
        "unit",
        "core",
        "integration",
        "agents",
        "security",
        "regression",
        "ops",
        "widget",
        "e2e",
        "load",
        "fuzzing",
        "property",
    ],
    estimated_tests=6920,
    estimated_duration_s=2700,
)


def get_suite(name: str) -> SuiteConfig | None:
    """Get suite configuration by name."""
    return SUITE_CONFIGS.get(name)


def list_suites() -> list[dict]:
    """Return suite metadata for SPA display."""
    return [
        {
            "name": cfg.name,
            "label": cfg.label,
            "estimated_tests": cfg.estimated_tests,
            "estimated_duration_s": cfg.estimated_duration_s,
            "is_composite": cfg.is_composite,
            "requires_playwright": cfg.requires_playwright,
            "requires_locust": cfg.requires_locust,
        }
        for cfg in SUITE_CONFIGS.values()
    ]
