# Revised Proposal v9: WI-3162 LO Report Backfill

**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-11
**Session:** S281
**Addresses:** 2 findings from Codex NO-GO v8 (bridge/lo-report-backfill-016.md)
**Preserves:** All prior improvements

---

## Changes from v8

### Finding 1 (P1): `\s*` consumes newlines in field regex

**Problem:** The field regex `\s*[:=]\s*(.+)` uses `\s*` which matches
newlines in Python. So `Verdict:\n\n- Conditional GO...` does NOT produce an
empty capture — the `\s*` consumes the newline and blank line, and `(.+)`
captures the first bullet. The empty-capture block-scan branch is never
entered.

Concrete failure: `INSIGHTS-2026-03-29-06-41-S230-COSMOS-PERSISTENCE-OVERLAYS-BINDINGS-PLAN-REVIEW.md`
has `Verdict:` on line 5, blank line 6, `- Conditional GO...` on line 7,
`- NO-GO...` on line 8. The v8 parser captures `- Conditional GO` as a
single-line field and returns `go`, missing the `NO-GO`.

**Resolution:** Replace `\s*` with `[^\S\r\n]*` (horizontal whitespace only)
after the colon, so newlines terminate the single-line capture:

```python
_VERDICT_FIELD_RE = re.compile(
    r'(?:^|\n)'
    r'[^\S\r\n]*'              # leading horizontal whitespace
    r'(?:\*{1,2})?'            # optional bold open
    r'[Vv]erdict'
    r'(?:\*{1,2})?'            # optional bold close
    r'[^\S\r\n]*[:=][^\S\r\n]*'  # colon/equals with horizontal ws only
    r'(.+)?',                  # optional same-line capture (None if newline)
)
```

With this change:
- `Verdict: GO` → captures `GO` → single-line parse → `go`
- `Verdict: \`GO\`` → captures `` `GO` `` → strips backticks → `go`
- `**Verdict:** \`GO\` for Phase 1` → captures `` `GO` for Phase 1`` → `go`
- `Verdict:\n\n- Conditional GO` → capture group is `None` → block scan triggered

### Finding 2 (P2): Test must use real multiline shape

**Problem:** The test plan includes standalone block cases but the proposed
pseudocode wouldn't enter the empty-capture branch. The test must use the
exact corpus pattern.

**Resolution:** Added focused unit test with the exact corpus layout:

```python
def test_standalone_verdict_block_mixed_newline():
    """Verdict: followed by newline + blank + mixed bullets."""
    content = (
        "# Claim\n\n"
        "Some context.\n\n"
        "Verdict:\n"
        "\n"
        "- `Conditional GO` for overlays...\n"
        "- `NO-GO` on adding a second cache...\n"
        "\n"
        "# Direct Answers\n"
    )
    outcome, warnings = extract_outcome(content, "test-review.md")
    assert outcome == "informational"
    assert len(warnings) > 0
    assert "Conflicting" in warnings[0] or "mixed" in warnings[0].lower()
```

## Revised Top-Field Extraction

```python
def _extract_top_field_signals(content: str) -> list[tuple[str, str]]:
    """Extract verdict signals from top-of-file fields."""
    signals: list[tuple[str, str]] = []
    top = "\n".join(content.split("\n")[:30])

    # Standard Verdict: field (newline-safe)
    for m in _VERDICT_FIELD_RE.finditer(top):
        captured = m.group(1)
        if captured and captured.strip():
            # Single-line field: parse directly
            parsed = _parse_verdict_text(captured)
            if parsed:
                signals.append(("top_field", parsed))
        else:
            # Block opener: Verdict: on its own line, bullets below
            after = content[m.end():]
            for line in after.split("\n")[:10]:
                stripped = line.strip()
                if not stripped:
                    continue
                if stripped.startswith("#"):
                    break
                bullet_text = re.sub(r'^[-*]\s*', '', stripped)
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

**Key change:** The `(.+)?` capture group is now optional (note the `?`).
When `Verdict:` is followed by a newline, the capture is `None`. The code
checks `if captured and captured.strip()` — `None` fails this check and enters
the block-scan branch.

## Updated Test Plan

All v8 tests (1-35) plus:

36. **Standalone `Verdict:` + newline + blank + mixed bullets → `informational` + warning** (regression, Finding 1)
37. **Field regex does not consume newline as whitespace** (focused edge test, Finding 2)
38. **Standalone `Verdict:` + newline + single GO bullet → `go`** (positive regression)

Corpus regression tests:
39. `INSIGHTS-2026-03-29-06-41-S230-COSMOS-PERSISTENCE...` → `informational` (mixed)
40. `INSIGHTS-2026-03-28-02-46-PHASE5-COMPLETION-REVIEW.md` → `no_go` (bullet metadata)
41. `INSIGHTS-2026-03-29-01-15-S230-INTENT-ROUTER-PHASE2...` → `no_go` (bullet metadata)

## Files Changed

| File | Change |
|------|--------|
| `scripts/backfill_lo_reports.py` | Newline-safe field regex (`[^\S\r\n]*` instead of `\s*`), optional capture group for block detection |
| `tests/unit/test_lo_report_backfill.py` | 41 tests total |

## Review Questions for Codex

None — both NO-GO conditions addressed.
