# GO - Mojibake Cleanup REVISED-1

**Status:** GO  
**Reviewer:** Codex Loyal Opposition  
**Reviewed proposal:** `bridge/mojibake-cleanup-2026-04-29-003.md`  
**Date:** 2026-04-29

## Verdict

GO. REVISED-1 closes both blocking findings from `-002`.

## Evidence

I reran a live codepoint inventory against the eight target files. The revised seven-pattern model accounts for all 83 mojibake-leading characters:

```text
scripts/workstream_focus.py: leaders 22; em_dash 8; section 8; arrow 5; ellipsis 1
scripts/rehearse/_dashboard_regen.py: leaders 16; em_dash 3; section 8; arrow 1; check 2; x 2
docs/gtkb-dashboard/index.html: leaders 1; em_dash 1
tests/scripts/test_rehearse_dashboard_regen.py: leaders 28; em_dash 2; section 9; arrow 17
tests/hooks/test_workstream_focus.py: leaders 8; em_dash 4; section 4
tests/scripts/test_gtkb_dashboard_alerting.py: leaders 5; section 4; copyright 1
tests/scripts/test_gtkb_dashboard_grafana.py: leaders 2; em_dash 1; section 1
tests/scripts/test_codex_hook_parity.py: leaders 1; section 1
TOTAL_LEADERS: 83
```

The test-path correction is also verified:

```text
Test-Path tests/scripts/test_workstream_focus.py -> False
Test-Path tests/hooks/test_workstream_focus.py -> True
```

## Conditions

Implementation may proceed as a single mechanical cleanup commit if the final post-cleanup scan exits nonzero unless every target file reports `0` for `U+00E2` and `U+00C2`.

The corrected pytest command should exclude the nonexistent `tests/scripts/test_workstream_focus.py` path and include `tests/hooks/test_workstream_focus.py`.

## Notes

The revision's scope remains mechanical and limited to the eight named target files. No additional owner decision is needed.

