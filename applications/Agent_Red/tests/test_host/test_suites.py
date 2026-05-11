# tests/test_host/test_suites.py — Suite configuration tests
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

"""Tests for test_host.suites — suite definitions, composite logic, and metadata."""

from __future__ import annotations

import pytest

from test_host.suites import (
    SUITE_CONFIGS,
    SuiteConfig,
    get_suite,
    list_suites,
)


# ---------------------------------------------------------------------------
# Suite registry completeness
# ---------------------------------------------------------------------------

class TestSuiteRegistry:
    """Verify the suite registry is complete and internally consistent."""

    EXPECTED_INDIVIDUAL = {
        "unit", "core", "integration", "agents", "security",
        "regression", "ops", "widget", "e2e", "load",
        "fuzzing", "property",
    }
    EXPECTED_COMPOSITE = {"pipeline", "full"}

    def test_all_individual_suites_defined(self):
        """Every expected individual suite exists in SUITE_CONFIGS."""
        for name in self.EXPECTED_INDIVIDUAL:
            assert name in SUITE_CONFIGS, f"Missing individual suite: {name}"

    def test_all_composite_suites_defined(self):
        """Both composite suites exist."""
        for name in self.EXPECTED_COMPOSITE:
            assert name in SUITE_CONFIGS, f"Missing composite suite: {name}"

    def test_total_suite_count(self):
        """Total suite count = individual + composite."""
        total = len(self.EXPECTED_INDIVIDUAL) + len(self.EXPECTED_COMPOSITE)
        assert len(SUITE_CONFIGS) == total

    def test_no_unknown_suites(self):
        """No unexpected suites in the registry."""
        expected = self.EXPECTED_INDIVIDUAL | self.EXPECTED_COMPOSITE
        actual = set(SUITE_CONFIGS.keys())
        assert actual == expected, f"Unexpected suites: {actual - expected}"


# ---------------------------------------------------------------------------
# Individual suite properties
# ---------------------------------------------------------------------------

class TestSuiteConfigProperties:
    """Every suite config has required properties set correctly."""

    @pytest.mark.parametrize("name", list(SUITE_CONFIGS.keys()))
    def test_suite_has_name(self, name):
        """Suite name field matches its key in the registry."""
        cfg = SUITE_CONFIGS[name]
        assert cfg.name == name

    @pytest.mark.parametrize("name", list(SUITE_CONFIGS.keys()))
    def test_suite_has_label(self, name):
        """Every suite has a non-empty human-readable label."""
        assert SUITE_CONFIGS[name].label, f"Suite {name} has no label"

    @pytest.mark.parametrize("name", list(SUITE_CONFIGS.keys()))
    def test_suite_has_timeout(self, name):
        """Every suite has a positive timeout."""
        assert SUITE_CONFIGS[name].timeout_s > 0

    @pytest.mark.parametrize("name", list(SUITE_CONFIGS.keys()))
    def test_suite_has_estimated_tests(self, name):
        """Every suite has a non-negative estimated test count."""
        assert SUITE_CONFIGS[name].estimated_tests >= 0


class TestIndividualSuiteArgs:
    """Individual suites must have valid pytest args."""

    INDIVIDUAL_SUITES = [
        name for name, cfg in SUITE_CONFIGS.items()
        if not cfg.is_composite and not cfg.requires_locust
    ]

    @pytest.mark.parametrize("name", INDIVIDUAL_SUITES)
    def test_individual_suite_has_pytest_args(self, name):
        """Non-locust individual suites must have pytest_args."""
        cfg = SUITE_CONFIGS[name]
        assert len(cfg.pytest_args) > 0, f"Suite {name} has no pytest_args"

    @pytest.mark.parametrize("name", INDIVIDUAL_SUITES)
    def test_pytest_args_include_test_path(self, name):
        """pytest_args must include at least one tests/ directory."""
        cfg = SUITE_CONFIGS[name]
        has_path = any(arg.startswith("tests/") for arg in cfg.pytest_args)
        assert has_path, f"Suite {name} pytest_args has no tests/ path"


# ---------------------------------------------------------------------------
# Composite suite integrity
# ---------------------------------------------------------------------------

class TestCompositeSuites:
    """Composite suites reference only valid individual suites."""

    def test_pipeline_references_valid_suites(self):
        """pipeline's composite_suites all exist as individual suites."""
        cfg = SUITE_CONFIGS["pipeline"]
        assert cfg.is_composite
        for sub in cfg.composite_suites:
            assert sub in SUITE_CONFIGS, f"pipeline references missing suite: {sub}"
            assert not SUITE_CONFIGS[sub].is_composite, f"pipeline references composite: {sub}"

    def test_full_references_valid_suites(self):
        """full's composite_suites all exist as individual suites."""
        cfg = SUITE_CONFIGS["full"]
        assert cfg.is_composite
        for sub in cfg.composite_suites:
            assert sub in SUITE_CONFIGS, f"full references missing suite: {sub}"

    def test_full_is_superset_of_pipeline(self):
        """The 'full' suite includes everything in 'pipeline' plus more."""
        pipeline_subs = set(SUITE_CONFIGS["pipeline"].composite_suites)
        full_subs = set(SUITE_CONFIGS["full"].composite_suites)
        assert pipeline_subs.issubset(full_subs)

    def test_full_includes_load(self):
        """'full' includes load testing, 'pipeline' does not."""
        assert "load" in SUITE_CONFIGS["full"].composite_suites
        assert "load" not in SUITE_CONFIGS["pipeline"].composite_suites

    def test_composite_estimated_tests_reasonable(self):
        """Composite estimated_tests >= sum of components."""
        for name in ["pipeline", "full"]:
            cfg = SUITE_CONFIGS[name]
            sub_sum = sum(
                SUITE_CONFIGS[s].estimated_tests
                for s in cfg.composite_suites
                if s in SUITE_CONFIGS
            )
            # Allow 10% tolerance for rounding
            assert cfg.estimated_tests >= sub_sum * 0.8, (
                f"{name} estimated_tests={cfg.estimated_tests} "
                f"but sub-suite sum={sub_sum}"
            )


# ---------------------------------------------------------------------------
# Special suite flags
# ---------------------------------------------------------------------------

class TestSuiteFlags:
    """Suite flags for special tooling requirements."""

    def test_e2e_requires_playwright(self):
        assert SUITE_CONFIGS["e2e"].requires_playwright

    def test_load_requires_locust(self):
        assert SUITE_CONFIGS["load"].requires_locust

    def test_load_has_no_pytest_args(self):
        """Load tests use Locust, not pytest."""
        assert SUITE_CONFIGS["load"].pytest_args == []

    def test_non_special_suites_no_playwright(self):
        """Regular suites don't require Playwright."""
        for name, cfg in SUITE_CONFIGS.items():
            if name not in {"e2e"}:
                assert not cfg.requires_playwright, f"{name} shouldn't require Playwright"

    def test_non_special_suites_no_locust(self):
        """Regular suites don't require Locust."""
        for name, cfg in SUITE_CONFIGS.items():
            if name not in {"load"}:
                assert not cfg.requires_locust, f"{name} shouldn't require Locust"


# ---------------------------------------------------------------------------
# get_suite() and list_suites() functions
# ---------------------------------------------------------------------------

class TestSuiteAccessors:
    """Tests for public accessor functions."""

    def test_get_suite_returns_config(self):
        """get_suite() returns SuiteConfig for valid names."""
        cfg = get_suite("unit")
        assert isinstance(cfg, SuiteConfig)
        assert cfg.name == "unit"

    def test_get_suite_returns_none_for_unknown(self):
        """get_suite() returns None for non-existent suite."""
        assert get_suite("nonexistent") is None

    def test_list_suites_returns_all(self):
        """list_suites() returns metadata for all registered suites."""
        result = list_suites()
        assert isinstance(result, list)
        assert len(result) == len(SUITE_CONFIGS)

    def test_list_suites_has_required_fields(self):
        """Each entry in list_suites() has expected keys."""
        required_keys = {
            "name", "label", "estimated_tests",
            "estimated_duration_s", "is_composite",
            "requires_playwright", "requires_locust",
        }
        for entry in list_suites():
            missing = required_keys - set(entry.keys())
            assert not missing, f"Missing keys in {entry['name']}: {missing}"

    def test_list_suites_names_match_registry(self):
        """list_suites() names match SUITE_CONFIGS keys."""
        names = {s["name"] for s in list_suites()}
        assert names == set(SUITE_CONFIGS.keys())


# ---------------------------------------------------------------------------
# Frozen dataclass enforcement
# ---------------------------------------------------------------------------

class TestSuiteConfigImmutability:
    """SuiteConfig is frozen — test that mutations are blocked."""

    def test_frozen_cannot_set_name(self):
        """Frozen dataclass prevents attribute mutation."""
        cfg = get_suite("unit")
        assert cfg is not None
        with pytest.raises(AttributeError):
            cfg.name = "hacked"  # type: ignore

    def test_frozen_cannot_set_timeout(self):
        """Frozen dataclass prevents timeout mutation."""
        cfg = get_suite("unit")
        assert cfg is not None
        with pytest.raises(AttributeError):
            cfg.timeout_s = 9999  # type: ignore
