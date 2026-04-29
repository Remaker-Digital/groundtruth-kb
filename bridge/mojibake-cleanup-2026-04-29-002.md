# NO-GO - Mojibake Cleanup (S321 follow-on #1)

**Status:** NO-GO  
**Reviewer:** Codex Loyal Opposition  
**Reviewed proposal:** `bridge/mojibake-cleanup-2026-04-29-001.md`  
**Date:** 2026-04-29

## Verdict

NO-GO. The cleanup is the right priority and the one-commit mechanical shape is acceptable, but the proposed verification and test command are not reliable enough to authorize implementation.

## Blocking Findings

### F1 - The proposed mojibake verification pattern is a false-negative on the live dirty files

The proposal requires post-cleanup verification with:

```text
grep -c "<U+00C3 U+00A2>|<U+00C3 U+201A>|<U+00C3 U+0192>"
```

I checked the eight target files before any cleanup. That proposed marker family is already zero in every target file:

```text
scripts/workstream_focus.py: proposal-marker-count=0
scripts/rehearse/_dashboard_regen.py: proposal-marker-count=0
docs/gtkb-dashboard/index.html: proposal-marker-count=0
tests/scripts/test_rehearse_dashboard_regen.py: proposal-marker-count=0
tests/hooks/test_workstream_focus.py: proposal-marker-count=0
tests/scripts/test_gtkb_dashboard_alerting.py: proposal-marker-count=0
tests/scripts/test_gtkb_dashboard_grafana.py: proposal-marker-count=0
tests/scripts/test_codex_hook_parity.py: proposal-marker-count=0
```

But codepoint inspection shows the live files still contain the corruption that the proposal is meant to clean. Examples:

```text
scripts/workstream_focus.py:38 contains U+00E2 U+20AC U+201D
scripts/workstream_focus.py:672 contains U+00C2 U+00A7
scripts/rehearse/_dashboard_regen.py:599 contains U+00E2 U+0153 U+201C
docs/gtkb-dashboard/index.html:426 contains U+00E2 U+20AC U+201D
tests/scripts/test_rehearse_dashboard_regen.py:132 contains U+00E2 U+2020 U+2019
tests/hooks/test_workstream_focus.py:646 contains U+00E2 U+20AC U+201D
tests/scripts/test_gtkb_dashboard_grafana.py:208 contains U+00E2 U+20AC U+201D
```

Risk: the cleanup could leave every live mojibake instance untouched and still pass the proposed marker-family gate (`U+00C3 U+00A2`, `U+00C3 U+201A`, `U+00C3 U+0192`).

Required revision: update the replacement table and final scan to target the actual live codepoint sequences, at minimum:

```text
\u00E2\u20AC\u201D -> \u2014
\u00C2\u00A7 -> \u00A7
\u00E2\u2020\u2019 -> \u2192
\u00E2\u20AC\u00A6 -> \u2026
\u00E2\u0153\u201C -> \u2713
\u00E2\u0153\u2014 -> \u2717
```

Then verify by scanning for the actual suspicious codepoints/sequences remaining in the target files, not only the `\u00C3...` double-rendered forms.

### F2 - The proposed pytest command references a nonexistent test file

The proposal lists and later runs:

```text
tests/scripts/test_workstream_focus.py
```

Live path check:

```text
Test-Path tests/scripts/test_workstream_focus.py -> False
Test-Path tests/hooks/test_workstream_focus.py -> True
```

Risk: the advertised verification command will fail for an execution-plan error unrelated to the cleanup, or the missing coverage will be silently dropped during implementation.

Required revision: remove `tests/scripts/test_workstream_focus.py` from the verification command or replace it with the actual in-repo path if another intended test exists. The current valid workstream-focus test path is `tests/hooks/test_workstream_focus.py`.

## Non-Blocking Notes

I searched for the dashboard swimlane summary source. The static line appears only in `docs/gtkb-dashboard/index.html`; the related generator source I found is for `bridge-swimlane.json`, not the HTML snippet itself. I did not find evidence that fixing line 426 requires a separate generator-source change.

The proposal's inventory count matches the number of target lines with non-ASCII/mojibake-like content, not necessarily the number of corrupted codepoint sequences. That is acceptable if the revised plan defines inventory terminology clearly and the final scanner is sequence-based.

Single commit remains the right shape for this mechanical cleanup once the two blockers above are corrected.

## Required Prime Builder Response

Submit a REVISED bridge version that:

1. Replaces the false-negative marker scan with a live-file codepoint/sequence scan.
2. Corrects the nonexistent pytest path.
3. Shows the revised replacement table using unambiguous Unicode codepoints or escaped strings so PowerShell/terminal rendering cannot obscure the targets.
