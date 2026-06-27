"""Throwaway PHASE-Y daemon-loop probe (WI-4879 / DELIB-20266272).

This module is the acceptance test artifact for the dispatcher-daemon go-live
loop.  It has no production callers and is safe to retire after the loop
demonstration is complete.
"""

from __future__ import annotations


def phase_y_probe_sum(a: int, b: int) -> int:
    """Return the sum of *a* and *b* (pure, side-effect-free)."""
    return a + b
