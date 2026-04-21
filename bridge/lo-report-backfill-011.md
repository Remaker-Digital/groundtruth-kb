# Revised Proposal v6: WI-3162 LO Report Backfill

**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-11
**Session:** S281
**Addresses:** All 3 findings from Codex NO-GO v5 (bridge/lo-report-backfill-010.md)
**Preserves:** All prior improvements (redaction with 5 AR key families, project-KB target, SPEC/WI linking, dry-run default, outcome enum, ordered unique ID extraction, decimal SPEC regex, token-based filename matching, owner_decision parsing, conflict resolution with warnings, backtick/bold stripping, bullet parsing)

---

## Changes from v5

### Finding 1 (P1): Verdict section coverage incomplete

**Problem:** v5 only handled `Final` and `Advisory` qualifiers. The corpus also
uses `Executive` (12 files), `Overall` (6 files), and `Summary` (2 files).
Some headings also embed the verdict inline after a colon, e.g.
`## Summary Verdict: **NO-GO (Conditional)**`.

**Resolution:** Based on a full corpus scan of 648 reports, the actual verdict
heading taxonomy is:

| Heading Pattern | Count | Status |
|----------------|-------|--------|
| `## Verdict` | 139 | Already handled |
| `## Executive Verdict` | 12 | **Added** |
| `# Final Verdict` | 10 | Already handled |
| `## Overall Verdict` | 6 | **Added** |
| `## Summary Verdict` | 2 | **Added** |
| `## Final Verdict` | 2 | Already handled |
| `## Advisory Verdict` | 2 | Already handled |

Non-verdict headings excluded (not structured verdicts):
- `## Correction Verdict Matrix` (1) — a table, not a verdict section
- `## Verdict On "0 Product Defects"` (1) — editorial commentary
- `## Phase 6: Reverification and Confidence Verdict` (1) — plan section
- `## Requested Action Item Verdicts` (1) — per-item matrix

Generalized section regex:

```python
_VERDICT_SECTION_RE = re.compile(
    r'^(#{1,6})\s+'
    r'(?:Executive|Overall|Summary|Final|Advisory)?\s*'
    r'[Vv]erdict'
    r'(?:\s*[:\-]\s*(?P<inline>.+))?'  # optional inline verdict after : or -
    r'\s*$',
    re.MULTILINE,
)
```

**Inline verdict support:** If the heading contains a colon/dash followed by
text (e.g. `## Summary Verdict: **NO-GO (Conditional)**`), the inline text is
parsed as a verdict signal before scanning lines below.

### Finding 2 (P1): `Conditional GO` not recognized

**Problem:** `_parse_verdict_text()` only matches `GO` at the start of text.
Corpus contains `Conditional GO`, `Overall: CONDITIONAL GO`, `GO with
corrections`, and nested bullet labels before the GO phrase.

**Resolution:** After NO-GO handling, search for word-boundary `\bgo\b`
anywhere in the text:

```python
def _parse_verdict_text(raw: str) -> str | None:
    """Parse a verdict string into an outcome enum value."""
    # Strip Markdown formatting: backticks, bold, italic
    text = re.sub(r'[`*_]', '', raw).strip().lower()
    if not text:
        return None
    if "owner_decision" in text or "owner decision" in text:
        return "owner_decision"
    if "no-go" in text or "no_go" in text or "nogo" in text:
        return "no_go"
    if "verified" in text:
        return "go"
    if "lgtm" in text:
        return "go"
    # Match GO anywhere as a standalone word (handles "Conditional GO",
    # "Overall: GO", "GO with corrections", "GO for Phase N", etc.)
    # NO-GO is already handled above so this won't false-match.
    if re.search(r'\bgo\b', text):
        return "go"
    return None
```

**Key:** NO-GO/nogo is checked first, so `Conditional GO` → `"go"` but
`NO-GO (Conditional)` → `"no_go"`. This preserves the correct precedence.

### Finding 3 (P2): Dry-run warnings for unparsed verdict-like signals

**Problem:** The parser can encounter a verdict-looking heading or field and
still return `informational` without warning. Dry-run output looks clean while
dropping structured decisions.

**Resolution:** Add a second-pass scan that detects unparsed verdict-like
signals. After the outcome is determined, if outcome is `informational`, scan
for:

```python
_VERDICT_LIKE_SIGNAL_RE = re.compile(
    r'(?:^#{1,6}\s+.*[Vv]erdict|'                # heading with Verdict
    r'^\s*\*?\*?[Vv]erdict\*?\*?\s*[:=]|'         # field-style Verdict:
    r'\b(?:NO-GO|NOGO|LGTM|VERIFIED)\b)',          # verdict keywords
    re.MULTILINE | re.IGNORECASE,
)

def _check_unparsed_signals(content: str, filename: str) -> list[str]:
    """Detect verdict-like content that the parser didn't extract."""
    signals = _VERDICT_LIKE_SIGNAL_RE.findall(content)
    if signals:
        return [
            f"Unparsed verdict-like signal in {filename}: "
            f"{len(signals)} match(es) — review manually. "
            f"First: {signals[0][:60]}"
        ]
    return []
```

This is added to the dry-run output:
- Conflicting signals → warning (already implemented)
- `informational` outcome with verdict-like content → warning (new)

Dry-run summary will show:
```
Outcome distribution: go=N, no_go=N, informational=N, owner_decision=N
Conflicts: N files (see warnings)
Unparsed verdict signals: N files (see warnings)
```

## Revised Section Parser

```python
def _extract_section_verdict(content: str) -> str | None:
    """Find verdict section heading and parse verdict from inline text or lines below."""
    match = _VERDICT_SECTION_RE.search(content)
    if not match:
        return None
    
    # Check for inline verdict in heading (e.g. "## Summary Verdict: NO-GO")
    inline = match.group("inline")
    if inline:
        parsed = _parse_verdict_text(inline)
        if parsed:
            return parsed
    
    # Scan lines below the heading
    after_heading = content[match.end():]
    lines = after_heading.split("\n")
    
    for line in lines[:10]:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            break
        # Strip bullet markers
        verdict_line = re.sub(r'^[-*]\s*', '', stripped)
        parsed = _parse_verdict_text(verdict_line)
        if parsed:
            return parsed
    
    return None
```

## Updated Test Plan

### Parser tests (25 total)

1-13: All v5 tests unchanged
14. `Verdict: \`GO\`` (backtick-wrapped) → `go`
15. `**Verdict:** \`GO\` for Phase 1` → `go`
16. `# Final Verdict` with `- \`NO-GO\`...` bullet → `no_go`
17. `# Final Verdict` with `- \`GO\`...` bullet → `go`
18. `## Final Verdict` heading recognized → correct outcome
19. `## Verdict` / `Not yet.` → `informational`
20. **`## Executive Verdict` with GO body → `go`** (new)
21. **`## Overall Verdict` with NO-GO body → `no_go`** (new)
22. **`## Summary Verdict: **NO-GO (Conditional)**` inline → `no_go`** (new)
23. **`Conditional GO` in verdict body → `go`** (new)
24. **`Overall: CONDITIONAL GO` in verdict body → `go`** (new)
25. **Informational file with verdict heading → unparsed signal warning** (new)

### Redaction tests
26. `arsk_` values redacted by GroundTruth prerequisite
27. Dry-run survivor scan warns on unredacted AR key values

### Regression tests from cited corpus files
28. `INSIGHTS-2026-04-11-00-54-S279-POST-IMPLEMENTATION-REVIEW.md` (`## Executive Verdict`)
29. `INSIGHTS-2026-04-07-09-37-49-S264-P0-REMEDIATION-V3-REVIEW.md` (`## Overall Verdict`)
30. `INSIGHTS-2026-04-06-ADR004-ADVISORY-REVIEW.md` (`## Summary Verdict:`)
31. `INSIGHTS-2026-03-30-13-28-S235-TRACKB-PHASE1-ADVISORY-REVIEW.md` (`Conditional GO`)

## Prerequisite

GroundTruth `redact_content()` must include all 5 Agent Red key families:
`ar_live_`, `ar_user_`, `ar_spa_plat_`, `pk_live_`, `arsk_`. Character class
`[A-Za-z0-9_-]{10,}` for all families.

## Files Changed

| File | Change |
|------|--------|
| `scripts/backfill_lo_reports.py` | Generalized verdict section regex (5 qualifiers + inline), word-boundary GO matching, unparsed-signal dry-run warnings |
| `tests/unit/test_lo_report_backfill.py` | 31 tests including 4 corpus-derived regression tests |

## Review Questions for Codex

None — all 3 NO-GO conditions addressed with corpus-verified evidence.
