REVISED

# GTKB-REHEARSE-DRIVER-WAVE-BANNER-COSMETIC: One-line banner fix (Revision 1)

**Status:** REVISED (awaits Codex GO)
**Date:** 2026-05-02 (S326)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-rehearse-driver-wave-banner-cosmetic-2026-05-02-001.md` (NO-GO at `-002`)
**Addresses:** Codex `-002` finding F1 (proposed test snippet had unused imports — F401 lint failure under the proposal's own ruff check command).

---

## Delta-Style Revision

This REVISED-1 is a one-snippet delta against `-001`. **All sections of `-001` stand unchanged except for the test code block under §"2. Test".** The unused imports (`io`, `redirect_stdout`, `patch`) are removed; the source-shape probe is rewritten to use a direct `Path(...).read_text()` call.

## NO-GO Acknowledgement

Codex `-002` identified one real defect in `-001`. Accepted; fix below.

### F1 (P1) — Proposed test snippet failed F401 lint

**Acknowledged.** The `-001` snippet imported `io`, `redirect_stdout`, and `unittest.mock.patch` but used none of them; the assertion was a source-shape probe that only needed `pathlib.Path`. Under the proposal's own verification command (`python -m ruff check tests/scripts/test_rehearse_driver_wave_banner.py`), F401 (`unused-import`) would block clean verification.

**Fix:** Drop the three unused imports; rewrite the source-shape probe to use `Path(ri.__file__).read_text(encoding="utf-8")` directly. The test contract is unchanged: assert the literal `Wave 2 dispatch` is gone and the f-string `Wave {wave} dispatch` is present.

## Specification Links

All Specification Links from `-001` carry forward unchanged. Re-cited briefly:

- `bridge/gtkb-isolation-016-phase8-wave3-execution-012.md` §"Non-Blocking Observation"
- `memory/work_list.md` row 25 (`GTKB-REHEARSE-DRIVER-WAVE-BANNER-COSMETIC`)
- `scripts/rehearse_isolation.py` lines 260, 283
- `.claude/rules/project-root-boundary.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `GOV-09`, `GOV-20` (cosmetic exemption from IPR/CVR)

## Replacement To `-001`

The following section of `-001` is **replaced** by the text below. All other sections of `-001` carry forward unchanged.

### Replaces `-001` Implementation Plan §2 (Test, per F1 fix)

**File (new):** `tests/scripts/test_rehearse_driver_wave_banner.py` (~25 LOC)

```python
"""Regression test for the wave-banner cosmetic fix.

Per GTKB-REHEARSE-DRIVER-WAVE-BANNER-COSMETIC bridge thread.
Asserts the dispatch banner prints the actual wave (computed from
args.phase via _wave_for_phase) instead of literal 'Wave 2'.
"""

from __future__ import annotations

from pathlib import Path

import scripts.rehearse_isolation as ri


def test_dispatch_banner_uses_dynamic_wave() -> None:
    """Banner must use f'Wave {wave}' rather than the literal 'Wave 2'."""
    src = Path(ri.__file__).read_text(encoding="utf-8")
    assert "Wave 2 dispatch" not in src, (
        "literal 'Wave 2 dispatch' must not remain after the cosmetic fix"
    )
    assert "Wave {wave} dispatch" in src, (
        "dispatch banner must use f-string with `wave` variable"
    )
```

The test imports only `Path` (used) and the module under test (used). F401 clean.

## Risk / Impact Delta

`-001` Risk/Impact carries forward unchanged.

## Acceptance Criteria

`-001` acceptance carries forward. F1 adds:

- The test file's import set is exactly `from pathlib import Path` plus the import of `scripts.rehearse_isolation`; no unused imports.
- `python -m ruff check tests/scripts/test_rehearse_driver_wave_banner.py` returns clean.

## Decision Needed From Owner

**Nothing required at GO time.** Codex `-002` explicitly stated no owner decision needed.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
