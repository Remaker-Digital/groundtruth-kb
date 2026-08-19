# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Regression test for the wave-banner cosmetic fix.

Per GTKB-REHEARSE-DRIVER-WAVE-BANNER-COSMETIC bridge thread
(`bridge/gtkb-rehearse-driver-wave-banner-cosmetic-2026-05-02-004.md` GO).
Asserts the dispatch banner prints the actual wave (computed from
``args.phase`` via ``_wave_for_phase``) instead of literal ``Wave 2``.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

_ISOLATION_PATH = (
    Path(__file__).resolve().parents[2] / "scripts" / "rehearse_isolation.py"
)
if not _ISOLATION_PATH.is_file():
    pytest.skip("scripts/rehearse_isolation.py is absent", allow_module_level=True)

# Read source by path only. Executing scripts/rehearse_isolation.py inserts
# scripts/ onto sys.path and imports the absent rehearse package.
ri = SimpleNamespace(__file__=str(_ISOLATION_PATH))


def test_dispatch_banner_uses_dynamic_wave() -> None:
    """Banner must use f'Wave {wave}' rather than the literal 'Wave 2'."""
    src = Path(ri.__file__).read_text(encoding="utf-8")
    assert "Wave 2 dispatch" not in src, (
        "literal 'Wave 2 dispatch' must not remain after the cosmetic fix"
    )
    assert "Wave {wave} dispatch" in src, (
        "dispatch banner must use f-string with `wave` variable"
    )
