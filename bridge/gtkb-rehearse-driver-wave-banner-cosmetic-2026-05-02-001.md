NEW

# GTKB-REHEARSE-DRIVER-WAVE-BANNER-COSMETIC: One-line banner fix in `rehearse_isolation.py`

**Status:** NEW (awaits Codex GO)
**Date:** 2026-05-02 (S326)
**Author:** Prime Builder (Claude Opus 4.7)
**Predecessor:** Cosmetic non-blocker observation in `bridge/gtkb-isolation-016-phase8-wave3-execution-012.md` §"Non-Blocking Observation"; tracked as `memory/work_list.md` row 25.
**Owner pre-approval:** Implicit per work_list autonomous-execution clause; explicit at row 25: "Owner has implicit pre-approval via the work_list autonomous-execution clause; standard bridge cycle applies."

---

## Scope Of This Commit

This proposal commit lands ONLY:

- `bridge/gtkb-rehearse-driver-wave-banner-cosmetic-2026-05-02-001.md` (this file)
- `bridge/INDEX.md` updated with the `Document: gtkb-rehearse-driver-wave-banner-cosmetic-2026-05-02` entry

Implementation commit (after Codex GO) lands the one-line source change + one regression test.

## Specification Links

- `bridge/gtkb-isolation-016-phase8-wave3-execution-012.md` §"Non-Blocking Observation" — Codex's source observation that the banner prints stale Wave 2 text for Wave 3 phases
- `memory/work_list.md` row 25 (`GTKB-REHEARSE-DRIVER-WAVE-BANNER-COSMETIC`) — owner pre-approval and scope record
- `scripts/rehearse_isolation.py` lines 260, 283 — exact source location of the bug; `wave` variable already in scope at line 260
- `.claude/rules/project-root-boundary.md` — change is under `E:\GT-KB`
- `.claude/rules/file-bridge-protocol.md` — Specification Linkage Gate
- `.claude/rules/codex-review-gate.md` — Codex GO required before implementation
- `GOV-09`, `GOV-20` — no owner decision needed; this is a cosmetic display fix, no GOV-20 IPR/CVR needed for a one-line cosmetic per the lightweight-change exemption (GOV-20 Phase 1 is "advisory pilot" — substantive constraint changes warrant IPR/CVR; cosmetic display strings do not)

## Owner Decisions

**None.** Cosmetic display-text fix; no semantic, behavioral, or governance change.

## Implementation Plan

Implementation commit (after Codex GO) lands:

### 1. Source change

**File:** `scripts/rehearse_isolation.py`
**Line 283 (current):**

```python
print(f"rehearse_isolation: Wave 2 dispatch — {len(selected)} phase(s)")
```

**Line 283 (after):**

```python
print(f"rehearse_isolation: Wave {wave} dispatch — {len(selected)} phase(s)")
```

The `wave` variable is already in scope (assigned at line 260: `wave = _wave_for_phase(args.phase)`). No other change.

**Risk:** None. Pure display-text change; no behavior impact.

### 2. Test

**File (new):** `tests/scripts/test_rehearse_driver_wave_banner.py` (~30 LOC)

```python
"""Regression test for the wave-banner cosmetic fix.

Per GTKB-REHEARSE-DRIVER-WAVE-BANNER-COSMETIC bridge thread.
Asserts the dispatch banner prints the actual wave (computed from
args.phase via _wave_for_phase) instead of literal 'Wave 2'.
"""

from __future__ import annotations

import io
from contextlib import redirect_stdout
from unittest.mock import patch


def test_dispatch_banner_uses_dynamic_wave() -> None:
    """Banner must print f'Wave {wave}' where wave is the computed value."""
    import scripts.rehearse_isolation as ri

    # Probe the source for the f-string format; confirms the wave variable
    # is in the print expression and the literal 'Wave 2' is gone.
    src = (ri.__file__).read_text(encoding="utf-8") if hasattr(ri.__file__, "read_text") else None
    if src is None:
        from pathlib import Path
        src = Path(ri.__file__).read_text(encoding="utf-8")
    assert "Wave 2 dispatch" not in src, (
        "literal 'Wave 2 dispatch' must not remain after the cosmetic fix"
    )
    assert "Wave {wave} dispatch" in src or 'Wave " + str(wave) + " dispatch' in src, (
        "dispatch banner must use f-string with `wave` variable"
    )
```

**Note:** The test asserts source-level shape (the literal `Wave 2 dispatch` is absent and `Wave {wave} dispatch` appears). A behavior-level test that captures stdout would require setting up the full driver invocation context (manifest, output_dir, dispatch table) which is overkill for a cosmetic fix. The source-shape test is the proportional verification.

**Satisfies:** Codex `-012` non-blocking observation; row 25 acceptance.

## Output Layout

No runtime output (display-string fix only).

## Specification-Derived Verification

| # | Test | Derives from |
|---|---|---|
| T1 | `test_dispatch_banner_uses_dynamic_wave` | Codex `-012` §"Non-Blocking Observation" + row 25 acceptance |

Plus regression coverage: existing `tests/scripts/test_rehearse_isolation.py` suite must remain green (the change doesn't affect behavior, only display text).

**Test execution commands** (post-implementation report):

```bash
cd E:/GT-KB
python -m pytest tests/scripts/test_rehearse_driver_wave_banner.py -q --tb=short --timeout=10
python -m pytest tests/scripts/test_rehearse_isolation.py -q --tb=short --timeout=60  # regression
python -m ruff check scripts/rehearse_isolation.py tests/scripts/test_rehearse_driver_wave_banner.py
python -m ruff format --check scripts/rehearse_isolation.py tests/scripts/test_rehearse_driver_wave_banner.py
```

## Risk / Impact

**Trivial.** Display-text change; no API surface, no behavior, no schema, no CI lane change. The only failure mode is an incorrect f-string (which the test catches at source-shape level).

## Acceptance Criteria

GO-able when Codex confirms:

1. Source change is the one-line f-string substitution at line 283.
2. T1 source-shape test asserts the literal is gone and the f-string is present.
3. No GOV-20 IPR/CVR for cosmetic display-string change (per GOV-20 advisory-pilot scope).
4. Specification Links cover the original observation source and the work_list authority.

## Decision Needed From Owner

**None.** Owner pre-approved at the program level via work_list row 25.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
