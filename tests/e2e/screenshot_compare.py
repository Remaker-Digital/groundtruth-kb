"""Pixel-based screenshot comparison using Pillow (SPEC-2104 / WI-3167).

Compares a captured screenshot against a committed baseline PNG.
Pillow-only — no numpy dependency.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageChops

BASELINE_DIR = Path(__file__).parent / "screenshots"
MAX_DIFF_PERCENT = 0.5  # 0.5% pixel difference threshold


def compare_screenshot(actual_path: Path, baseline_name: str) -> tuple[bool, float]:
    """Compare actual screenshot against baseline.

    Returns (passed, diff_percent).
    """
    baseline_path = BASELINE_DIR / baseline_name
    if not baseline_path.exists():
        return False, 100.0  # No baseline = fail

    actual = Image.open(actual_path).convert("RGB")
    baseline = Image.open(baseline_path).convert("RGB")

    if actual.size != baseline.size:
        return False, 100.0  # Size mismatch

    diff = ImageChops.difference(actual, baseline)
    diff_pixels = sum(1 for pixel in diff.getdata() if any(c > 0 for c in pixel))
    total_pixels = actual.size[0] * actual.size[1]
    diff_percent = (diff_pixels / total_pixels) * 100

    return diff_percent <= MAX_DIFF_PERCENT, diff_percent
