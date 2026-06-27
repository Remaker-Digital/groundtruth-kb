"""Tests for the PHASE-Y daemon-loop probe (WI-4879 / DELIB-20266272)."""

from groundtruth_kb._phase_y_loop_probe import phase_y_probe_sum


def test_phase_y_probe_sum_basic() -> None:
    assert phase_y_probe_sum(2, 3) == 5


def test_phase_y_probe_sum_zeros() -> None:
    assert phase_y_probe_sum(0, 0) == 0


def test_phase_y_probe_sum_negative() -> None:
    assert phase_y_probe_sum(-4, 1) == -3
