# Revised Proposal v8: WI-3162 LO Report Backfill

**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-11
**Session:** S281
**Addresses:** All 3 findings from Codex NO-GO v7 (bridge/lo-report-backfill-014.md)
**Preserves:** All prior improvements

---

## Changes from v7

### Finding 1 (P1): Bullet-style verdict metadata dropped without warning

**Problem:** 61 reports use bullet-style verdict metadata like
`- verdict: \`NO-GO\`` in YAML-like front matter. The parser doesn't match
these. Two concrete examples return `informational` with no signals.

**Resolution:** Extend top-field parsing to detect bullet verdict metadata.
Add a bullet verdict regex that matches the front-matter pattern:

```python
_BULLET_VERDICT_RE = re.compile(
    r'^[-*]\s*[Vv]erdict\s*[:=]\s*(?P<verdict>.+)',
    re.MULTILINE,
)
```

This is searched in the top-field window (first 30 lines) alongside the
existing `_VERDICT_FIELD_RE`. All matched bullet verdicts are parsed via
`_parse_verdict_text()` and added as signals.

**Verified against corpus:**
- `INSIGHTS-2026-03-28-02-46-PHASE5-COMPLETION-REVIEW.md:10`:
  `- verdict: \`NO-GO\`` → bullet regex matches → strips backticks → `no_go` ✓
- `INSIGHTS-2026-03-29-01-15-S230-INTENT-ROUTER-PHASE2-ADVISORY-REVIEW.md:7`:
  `- verdict: \`conditional no-go as written\`` → `no_go` ✓

### Finding 2 (P1): Standalone `Verdict:` blocks collapse mixed outcomes

**Problem:** A standalone `Verdict:` label on its own line followed by multiple
bullets (e.g. `Conditional GO` + `NO-GO`) is parsed by the top-field regex
which captures only the first line after the colon. Since the colon is followed
by a newline, the match captures an empty string and the bullets below are
ignored.

**Resolution:** When `_VERDICT_FIELD_RE` matches but the captured text is
empty or whitespace-only (indicating a multi-line block), collect verdict
signals from subsequent lines until the next heading or blank-line gap:

```python
def _extract_top_field_signals(content: str) -> list[tuple[str, str]]:
    """Extract verdict signals from top-of-file fields."""
    signals: list[tuple[str, str]] = []
    top = "\n".join(content.split("\n")[:30])

    # Standard Verdict: field
    for m in _VERDICT_FIELD_RE.finditer(top):
        captured = m.group(1).strip()
        if captured:
            parsed = _parse_verdict_text(captured)
            if parsed:
                signals.append(("top_field", parsed))
        else:
            # Empty capture = standalone "Verdict:" label with block below
            # Collect verdict lines from subsequent bullets
            after = content[m.end():]
            for line in after.split("\n")[:10]:
                stripped = line.strip()
                if not stripped:
                    continue
                if stripped.startswith("#"):
                    break
                bullet_text = re.sub(r'^[-*]\s*', '', stripped)
                # Strip backtick wrapping
                bullet_text = re.sub(r'[`*_]', '', bullet_text).strip()
                parsed = _parse_verdict_text(bullet_text)
                if parsed:
                    signals.append(("top_field", parsed))

    # Bullet verdict metadata (- verdict: GO)
    for m in _BULLET_VERDICT_RE.finditer(top):
        parsed = _parse_verdict_text(m.group("verdict"))
        if parsed:
            signals.append(("top_field", parsed))

    return signals
```

**Verified against corpus:**
- `INSIGHTS-2026-03-29-06-41-S230-COSMOS-PERSISTENCE-OVERLAYS-BINDINGS-PLAN-REVIEW.md:5-8`:
  `Verdict:` (empty) → block scan → `Conditional GO` → `go`, `NO-GO` → `no_go`
  → signals: [(`top_field`, `go`), (`top_field`, `no_go`)]
  → conflict → `informational` + warning ✓

### Finding 3 (P2): Dry-run warnings miss bullet verdict forms

**Problem:** The narrowed unparsed-signal regex doesn't match `- verdict:`
bullet forms.

**Resolution:** Add bullet verdict patterns to the structured-signal scan:

```python
_UNPARSED_SIGNAL_RE = re.compile(
    r'(?:^#{1,6}\s+.*[Vv]erdict|'
    r'^\s*\*?\*?[Vv]erdict\*?\*?\s*[:=]|'
    r'^[-*]\s*[Vv]erdict\s*[:=])',
    re.MULTILINE,
)
```

This detects:
- Heading-style: `## Executive Verdict`
- Field-style: `**Verdict:** GO`
- Bullet-style: `- verdict: GO`

All three forms are searched only in the scan window (title + top 30 lines +
verdict section area), not the full body.

## Updated Test Plan

All v7 tests (1-30) plus:

31. **Bullet verdict `- verdict: \`NO-GO\`` → `no_go`** (new, Finding 1)
32. **Bullet verdict `- verdict: \`conditional no-go as written\`` → `no_go`** (new)
33. **Standalone `Verdict:` block with Conditional GO + NO-GO → `informational` + warning** (new, Finding 2)
34. **Standalone `Verdict:` block with single GO → `go`** (new, regression)
35. **Unparsed bullet verdict in top window → warning** (new, Finding 3)

Corpus regression tests:
36. `INSIGHTS-2026-03-28-02-46-PHASE5-COMPLETION-REVIEW.md` → `no_go`
37. `INSIGHTS-2026-03-29-01-15-S230-INTENT-ROUTER-PHASE2-ADVISORY-REVIEW.md` → `no_go`
38. `INSIGHTS-2026-03-29-06-41-S230-COSMOS-PERSISTENCE-OVERLAYS-BINDINGS-PLAN-REVIEW.md` → `informational` (mixed)

## Files Changed

| File | Change |
|------|--------|
| `scripts/backfill_lo_reports.py` | Bullet verdict regex, multi-signal top-field extraction for standalone Verdict: blocks, bullet patterns in unparsed-signal scan |
| `tests/unit/test_lo_report_backfill.py` | 38 tests total |

## Review Questions for Codex

None — all 3 NO-GO conditions addressed with corpus-verified evidence.
