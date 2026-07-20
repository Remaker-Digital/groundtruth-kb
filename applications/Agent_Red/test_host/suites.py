"""Suite-to-pytest mapping for the Agent Red test host."""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass, field

PARALLELIZABLE_SUITES = frozenset(
    {
        "unit",
        "core",
        "integration",
        "agents",
        "security",
        "regression",
        "ops",
        "property",
    }
)


@dataclass(frozen=True)
class SuiteConfig:
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
        if self.is_composite:
            for name in self.composite_suites:
                suite = SUITE_CONFIGS.get(name)
                if suite is None:
                    return False, f"Sub-suite '{name}' not found"
                runnable, reason = suite.can_run()
                if not runnable:
                    return False, f"Sub-suite '{name}': {reason}"
            return True, ""
        if self.requires_playwright and not shutil.which("playwright"):
            return False, "Playwright CLI not installed"
        if self.requires_locust and not shutil.which("locust"):
            return False, "Locust not installed"
        return True, ""


SUITE_CONFIGS: dict[str, SuiteConfig] = {
    "unit": SuiteConfig("unit", "Unit Tests", ["tests/unit/", "-x", "--timeout=30", "-q"], 300, estimated_tests=950),
    "core": SuiteConfig(
        "core",
        "Core / Multi-Tenant Tests",
        [
            "tests/multi_tenant/",
            "tests/migrations/",
            # Documentation fixtures are intentionally outside the container contract.
            "--ignore=tests/multi_tenant/test_s153_documentation_specs.py",
            # Live mutation tests require external service state.
            "--ignore=tests/multi_tenant/test_mutation_tenant_admin.py",
            "-x",
            "--timeout=30",
            "-q",
        ],
        600,
        estimated_tests=3700,
    ),
    "integration": SuiteConfig(
        "integration",
        "Integration Tests",
        [
            "tests/integration/",
            "tests/integrations/",
            # Live Azure checks are covered by deployment smoke suites.
            "--ignore=tests/integration/test_azure_services.py",
            "-x",
            "--timeout=30",
            "-q",
        ],
        600,
        estimated_tests=270,
    ),
    "agents": SuiteConfig(
        "agents",
        "Agent and Chat Tests",
        ["tests/agents/", "tests/chat/", "tests/persistent_memory/", "-x", "--timeout=30", "-q"],
        600,
        estimated_tests=300,
    ),
    "security": SuiteConfig(
        "security",
        "Security and Penetration",
        [
            "tests/security/",
            # Live tenant boundary checks require external deployed services.
            "--ignore=tests/security/test_tenant_isolation_live.py",
            "--timeout=60",
            "-q",
        ],
        600,
        estimated_tests=150,
    ),
    "regression": SuiteConfig(
        "regression", "Regression", ["tests/regression/", "--timeout=30", "-q"], 300, estimated_tests=47
    ),
    "ops": SuiteConfig(
        "ops",
        "Operations and Resilience",
        [
            "tests/ops/",
            # Hook source is intentionally absent from application containers.
            "--ignore=tests/ops/test_hooks_specs.py",
            "--timeout=60",
            "-q",
        ],
        600,
        estimated_tests=80,
    ),
    "widget": SuiteConfig("widget", "Widget Tests", ["tests/widget/", "--timeout=30", "-q"], 60, estimated_tests=60),
    "e2e": SuiteConfig(
        "e2e",
        "E2E Playwright",
        ["tests/e2e/", "--timeout=120", "--maxfail=100", "-q"],
        3600,
        requires_playwright=True,
        estimated_tests=400,
    ),
    "load": SuiteConfig("load", "Load Testing", [], 900, requires_locust=True, estimated_tests=1),
    "fuzzing": SuiteConfig(
        "fuzzing",
        "API Fuzzing",
        ["tests/fuzzing/", "--timeout=300", "-q"],
        2400,
        env_vars={
            "FUZZ_TARGET_URL": os.environ.get("STAGING_URL", ""),
            "FUZZ_API_KEY": os.environ.get("STAGING_SPA_KEY", os.environ.get("SUPERADMIN_PREVIEW_API_KEY", "")),
        },
        estimated_tests=10,
    ),
    "property": SuiteConfig(
        "property", "Property Tests", ["tests/property/", "--timeout=60", "-q"], 600, estimated_tests=46
    ),
}

SUITE_CONFIGS["pipeline"] = SuiteConfig(
    "pipeline",
    "Pipeline Suite",
    [],
    3600,
    is_composite=True,
    composite_suites=["unit", "core", "integration", "agents", "security", "regression", "ops", "property"],
    estimated_tests=5503,
)

SUITE_CONFIGS["full"] = SuiteConfig(
    "full",
    "Complete Suite",
    [],
    7200,
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
    estimated_tests=6024,
)


def get_suite(name: str) -> SuiteConfig | None:
    return SUITE_CONFIGS.get(name)


def list_suites() -> list[dict]:
    result = []
    for config in SUITE_CONFIGS.values():
        runnable, reason = config.can_run()
        result.append(
            {
                "name": config.name,
                "label": config.label,
                "estimated_tests": config.estimated_tests,
                "estimated_duration_s": config.estimated_duration_s,
                "is_composite": config.is_composite,
                "requires_playwright": config.requires_playwright,
                "requires_locust": config.requires_locust,
                "runnable": runnable,
                "reason": reason,
            }
        )
    return result
