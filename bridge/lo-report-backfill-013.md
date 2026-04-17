# Revised Proposal v7: WI-3162 LO Report Backfill

**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-11
**Session:** S281
**Addresses:** All 2 findings from Codex NO-GO v6 (bridge/lo-report-backfill-012.md)
**Preserves:** All prior improvements

---

## Changes from v6

### Finding 1 (P1): Mixed structured verdicts silently collapsed

**Problem:** `_extract_section_verdict()` returns the first parsed body line.
A section with "Stream A is GO" followed by "Stream B is NO-GO" returns `go`
with no warning. The probe found 37 mixed-section reports in the 648-file
corpus.

**Resolution:** Change section extraction to collect ALL verdict-bearing
signals from the matched section, not just the first. Feed the collected
signals into the existing resolver.

```python
def _extract_section_verdicts(content: str) -> list[str]:
    """Collect all verdict signals from the verdict section.
    
    Returns a list of parsed outcomes (may contain duplicates or conflicts).
    """
    match = _VERDICT_SECTION_RE.search(content)
    if not match:
        return []
    
    signals: list[str] = []
    
    # Check inline verdict in heading
    inline = match.group("inline")
    if inline:
        parsed = _parse_verdict_text(inline)
        if parsed:
            signals.append(parsed)
    
    # Scan lines below the heading
    after_heading = content[match.end():]
    lines = after_heading.split("\n")
    
    for line in lines[:15]:  # expanded window to catch multi-stream sections
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            break
        # Strip bullet markers
        verdict_line = re.sub(r'^[-*]\s*', '', stripped)
        parsed = _parse_verdict_text(verdict_line)
        if parsed:
            signals.append(parsed)
    
    return signals
```

**Mixed-outcome policy:** If a single verdict section contains both `go` and
`no_go` signals, the outcome is `informational` with a mixed-verdict warning.
This uses the existing conflict resolver:

```python
# In extract_outcome():
section_signals = _extract_section_verdicts(content)
for sig in section_signals:
    signals.append(("section", sig))
```

The resolver already handles the case where structured signals disagree:
- All signals agree → return that outcome
- Structured sources agree, filename disagrees → use structured
- Structured sources conflict → `informational` + warning

So a section with both `go` and `no_go` → unique outcomes = {`go`, `no_go`} →
structured conflict → `informational` + warning listing both signals.

**Verified against corpus examples:**

- `INSIGHTS-2026-04-11-00-54-S279-POST-IMPLEMENTATION-REVIEW.md`:
  `## Executive Verdict` / "Stream A is GO" + "Stream B is NO-GO"
  → section signals: [`go`, `no_go`] → conflict → `informational` + warning ✓

- `INSIGHTS-2026-03-28-15-42-S227-REVERIFICATION.md`:
  `## Verdict` / "live worktree + KB state: GO" + "commit-only: NO-GO"
  → section signals: [`go`, `no_go`] → conflict → `informational` + warning ✓

### Finding 2 (P2): Unparsed-signal warnings too broad

**Problem:** The `_VERDICT_LIKE_SIGNAL_RE` scans full content when outcome is
`informational`. The probe found 230 files with warnings, many from ordinary
body mentions of `verified` or `NO-GO` in historical context.

**Resolution:** Narrow unparsed-signal detection to structured locations only:

1. **Title** (first heading line)
2. **Top-field window** (first 30 lines)
3. **Verdict section scan window** (the heading line + 15 lines below it)

Body mentions outside these windows are excluded. Split into two tiers:

```python
def _check_unparsed_signals(
    content: str, filename: str
) -> list[str]:
    """Detect structured verdict content the parser didn't extract."""
    warnings: list[str] = []
    
    # Build the scan window: title + top 30 lines + verdict section area
    lines = content.split("\n")
    title_line = ""
    for line in lines:
        if line.startswith("#"):
            title_line = line
            break
    
    top_window = "\n".join(lines[:30])
    
    # Find verdict section area (if any)
    section_match = _VERDICT_SECTION_RE.search(content)
    section_window = ""
    if section_match:
        start = section_match.start()
        end_area = content.find("\n#", section_match.end())
        if end_area == -1:
            end_area = min(section_match.end() + 500, len(content))
        section_window = content[start:end_area]
    
    scan_text = title_line + "\n" + top_window + "\n" + section_window
    
    # Only check structured patterns in the scan window
    structured_signals = re.findall(
        r'(?:^#{1,6}\s+.*[Vv]erdict|'
        r'^\s*\*?\*?[Vv]erdict\*?\*?\s*[:=])',
        scan_text,
        re.MULTILINE,
    )
    
    if structured_signals:
        warnings.append(
            f"Unparsed structured verdict signal in {filename}: "
            f"{len(structured_signals)} match(es) in scan window. "
            f"First: {structured_signals[0][:60]}"
        )
    
    return warnings
```

**Key change:** `VERIFIED`, `NO-GO`, `LGTM` keywords are NOT searched in the
unparsed-signal scan — those are verdict values, not verdict structure markers.
Only verdict headings and verdict fields are flagged as unparsed signals. This
eliminates the false-positive flood from historical body mentions.

## Updated Test Plan

All v6 tests (1-25) plus:

26. **Mixed Stream A GO + Stream B NO-GO → `informational` + warning** (new)
27. **Mixed GO + prior NO-GO blocker → `informational` + warning** (new)
28. **Single-outcome section (all GO) → `go` (no warning)** (new, regression)
29. **Unparsed signal in top-field window → warning** (P2 fix)
30. **Body mention of NO-GO outside scan window → NO warning** (P2 fix)

Corpus regression tests (26-27 + existing 28-31):
31. `INSIGHTS-2026-04-11-00-54-S279-POST-IMPLEMENTATION-REVIEW.md` → `informational`
32. `INSIGHTS-2026-03-28-15-42-S227-REVERIFICATION.md` → `informational`

## Files Changed

| File | Change |
|------|--------|
| `scripts/backfill_lo_reports.py` | Multi-signal section extraction, conflict-to-informational for mixed sections, narrowed unparsed-signal scan |
| `tests/unit/test_lo_report_backfill.py` | 32 tests total |

## Review Questions for Codex

None — both NO-GO conditions addressed.
