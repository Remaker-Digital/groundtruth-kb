"""Statistical significance testing for A/B experiments (WI-1524 / SPEC-0621).

Pure Python implementations that work without scipy.  These provide
approximate p-values and confidence intervals suitable for the experiment
dashboard.  For production-grade analysis, scipy can optionally be used.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class StatResult:
    """Result of a statistical test."""

    test_name: str
    statistic: float
    p_value: float
    effect_size: float
    ci_lower: float
    ci_upper: float
    significant: bool  # True if p_value < alpha
    sample_size_control: int
    sample_size_treatment: int


# ---------------------------------------------------------------------------
# Normal distribution helpers (no scipy needed)
# ---------------------------------------------------------------------------

def _phi(x: float) -> float:
    """Standard normal CDF approximation (Abramowitz & Stegun 26.2.17)."""
    if x < -8.0:
        return 0.0
    if x > 8.0:
        return 1.0
    a1 = 0.254829592
    a2 = -0.284496736
    a3 = 1.421413741
    a4 = -1.453152027
    a5 = 1.061405429
    p = 0.3275911
    sign = 1 if x >= 0 else -1
    x_abs = abs(x)
    t = 1.0 / (1.0 + p * x_abs)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(
        -x_abs * x_abs / 2.0
    )
    return 0.5 * (1.0 + sign * y)


def _z_critical(alpha: float = 0.05) -> float:
    """Return the z-value for a two-tailed test at the given alpha."""
    # Common values
    z_map = {0.01: 2.576, 0.05: 1.96, 0.10: 1.645}
    return z_map.get(alpha, 1.96)


# ---------------------------------------------------------------------------
# Two-proportion z-test (for rates: escalation, conversion, etc.)
# ---------------------------------------------------------------------------


def two_proportion_z_test(
    successes_control: int,
    n_control: int,
    successes_treatment: int,
    n_treatment: int,
    alpha: float = 0.05,
) -> StatResult:
    """Two-proportion z-test for comparing rates between variants.

    Suitable for: escalation rate, conversion rate, satisfaction binary.

    Args:
        successes_control: Number of 'success' events in control.
        n_control: Total observations in control.
        successes_treatment: Number of 'success' events in treatment.
        n_treatment: Total observations in treatment.
        alpha: Significance level (default 0.05).

    Returns:
        StatResult with z-statistic, p-value, and confidence interval
        for the difference in proportions.
    """
    if n_control == 0 or n_treatment == 0:
        return StatResult(
            test_name="two_proportion_z",
            statistic=0.0,
            p_value=1.0,
            effect_size=0.0,
            ci_lower=0.0,
            ci_upper=0.0,
            significant=False,
            sample_size_control=n_control,
            sample_size_treatment=n_treatment,
        )

    p1 = successes_control / n_control
    p2 = successes_treatment / n_treatment
    diff = p2 - p1

    # Pooled proportion
    p_pool = (successes_control + successes_treatment) / (n_control + n_treatment)

    se_pooled = math.sqrt(p_pool * (1 - p_pool) * (1 / n_control + 1 / n_treatment))
    if se_pooled == 0:
        z_stat = 0.0
        p_value = 1.0
    else:
        z_stat = diff / se_pooled
        p_value = 2.0 * (1.0 - _phi(abs(z_stat)))

    # CI for the difference (unpooled SE)
    se_diff = math.sqrt(
        p1 * (1 - p1) / max(n_control, 1) + p2 * (1 - p2) / max(n_treatment, 1)
    )
    z_crit = _z_critical(alpha)
    ci_lower = diff - z_crit * se_diff
    ci_upper = diff + z_crit * se_diff

    # Cohen's h (effect size for proportions)
    h = 2.0 * (math.asin(math.sqrt(p2)) - math.asin(math.sqrt(p1)))

    return StatResult(
        test_name="two_proportion_z",
        statistic=round(z_stat, 4),
        p_value=round(max(p_value, 1e-10), 6),
        effect_size=round(h, 4),
        ci_lower=round(ci_lower, 6),
        ci_upper=round(ci_upper, 6),
        significant=p_value < alpha,
        sample_size_control=n_control,
        sample_size_treatment=n_treatment,
    )


# ---------------------------------------------------------------------------
# Two-sample z-test for means (for continuous: quality score, session length)
# ---------------------------------------------------------------------------


def two_sample_z_test(
    mean_control: float,
    std_control: float,
    n_control: int,
    mean_treatment: float,
    std_treatment: float,
    n_treatment: int,
    alpha: float = 0.05,
) -> StatResult:
    """Two-sample z-test for comparing means between variants.

    Suitable for: quality scores, session length, any continuous metric.

    Uses the z-test (large sample approximation) rather than t-test, which
    is appropriate when n > 30.

    Args:
        mean_control: Mean of control group.
        std_control: Standard deviation of control group.
        n_control: Sample size of control.
        mean_treatment: Mean of treatment group.
        std_treatment: Standard deviation of treatment group.
        n_treatment: Sample size of treatment.
        alpha: Significance level.

    Returns:
        StatResult with z-statistic, p-value, CI for difference of means.
    """
    if n_control == 0 or n_treatment == 0:
        return StatResult(
            test_name="two_sample_z",
            statistic=0.0,
            p_value=1.0,
            effect_size=0.0,
            ci_lower=0.0,
            ci_upper=0.0,
            significant=False,
            sample_size_control=n_control,
            sample_size_treatment=n_treatment,
        )

    diff = mean_treatment - mean_control

    se = math.sqrt(
        (std_control**2 / max(n_control, 1)) + (std_treatment**2 / max(n_treatment, 1))
    )
    if se == 0:
        z_stat = 0.0
        p_value = 1.0
    else:
        z_stat = diff / se
        p_value = 2.0 * (1.0 - _phi(abs(z_stat)))

    z_crit = _z_critical(alpha)
    ci_lower = diff - z_crit * se
    ci_upper = diff + z_crit * se

    # Cohen's d (pooled std)
    pooled_std = math.sqrt(
        (
            (n_control - 1) * std_control**2
            + (n_treatment - 1) * std_treatment**2
        )
        / max(n_control + n_treatment - 2, 1)
    )
    cohens_d = diff / pooled_std if pooled_std > 0 else 0.0

    return StatResult(
        test_name="two_sample_z",
        statistic=round(z_stat, 4),
        p_value=round(max(p_value, 1e-10), 6),
        effect_size=round(cohens_d, 4),
        ci_lower=round(ci_lower, 6),
        ci_upper=round(ci_upper, 6),
        significant=p_value < alpha,
        sample_size_control=n_control,
        sample_size_treatment=n_treatment,
    )


# ---------------------------------------------------------------------------
# Sample size estimation
# ---------------------------------------------------------------------------


def compute_sample_size_needed(
    baseline_rate: float,
    minimum_detectable_effect: float,
    alpha: float = 0.05,
    power: float = 0.80,
) -> int:
    """Estimate minimum sample size per group for a proportion comparison.

    Uses the normal approximation formula for sample size estimation.

    Args:
        baseline_rate: Expected proportion in control (e.g., 0.10 for 10%).
        minimum_detectable_effect: Smallest difference to detect (absolute).
        alpha: Significance level (default 0.05).
        power: Statistical power (default 0.80).

    Returns:
        Minimum observations per group.
    """
    if minimum_detectable_effect <= 0:
        return 0

    z_alpha = _z_critical(alpha)
    # z_beta for common power levels
    z_beta_map = {0.80: 0.842, 0.90: 1.282, 0.95: 1.645}
    z_beta = z_beta_map.get(power, 0.842)

    p1 = baseline_rate
    p2 = baseline_rate + minimum_detectable_effect
    p_bar = (p1 + p2) / 2.0

    numerator = (
        z_alpha * math.sqrt(2 * p_bar * (1 - p_bar))
        + z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))
    ) ** 2
    denominator = minimum_detectable_effect**2

    return max(1, math.ceil(numerator / denominator))
