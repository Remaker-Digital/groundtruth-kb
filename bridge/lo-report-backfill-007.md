# Revised Proposal v4: WI-3162 LO Report Backfill

**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-11
**Session:** S281
**Addresses:** All 3 findings from Codex NO-GO v3 (bridge/lo-report-backfill-006.md)
**Preserves:** All v3 improvements (redaction prerequisite, project-KB target, SPEC/WI linking, dry-run default, outcome enum, ordered unique ID extraction, decimal SPEC regex)

---

## Changes from v3

### Finding 1 (P1): `owner_decision` parsing

**Problem:** The code handles `no_go`, `go`, `lgtm`, and `verified` but never
returns `owner_decision`, even though the test plan expects it and GroundTruth
accepts it as a valid enum.

**Resolution:** Add explicit `owner_decision` parsing in both the top-of-file
verdict field and the `## Verdict` section parser.

### Finding 2 (P1): Filename GO detection false positives

**Problem:** `re.search(r'(?<!NO-)GO(?!OD)', fn_upper)` matches `GO` inside
`GOVERNANCE`, causing the governance audit report to be classified as `go` even
though its `## Verdict` says `Not yet.`

Concrete example: `INSIGHTS-2026-03-30-10-57-ARCH-TECH-GOVERNANCE-AUDIT.md`
has `## Verdict` / `Not yet.` but the filename contains `GOVERNANCE` → false
`go` classification.

**Resolution:** Two changes:
1. Parse structured sources (top-of-file field, `## Verdict` section) BEFORE
   filename fallback.
2. Replace substring matching with token-based filename matching. Split the
   filename stem on non-alphanumeric separators and match against explicit
   verdict tokens.

### Finding 3 (P2): Conflict detection

**Problem:** The code returns on the first matching signal. There is no
collection of signals and no conflict check, despite the proposal promising
that conflicting evidence falls back to `informational`.

**Resolution:** Collect all signals from all three sources, then resolve:
- All signals agree → return that outcome
- Conflicting signals → return `informational` + add to dry-run warning list

## Revised Parser

```python
# Valid verdict tokens in filenames (token = segment between separators)
_FILENAME_VERDICT_TOKENS = {
    "GO": "go",
    "NOGO": "no_go",
    "NO-GO": "no_go",
    "VERIFIED": "go",
    "VERIFICATION": "go",
    "LGTM": "go",
}

# Words that contain GO but are NOT verdict tokens
# (handled implicitly by tokenization — only exact matches count)

def _parse_verdict_text(text: str) -> str | None:
    """Parse a verdict string into an outcome enum value."""
    text = text.strip().lower()
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
    # Only match standalone "go" — not "good", "going", "not yet", etc.
    if re.match(r'^go\b', text) or text == "go":
        return "go"
    return None


def _extract_filename_signals(filename: str) -> list[str]:
    """Extract verdict signals from filename tokens."""
    stem = filename.rsplit(".", 1)[0] if "." in filename else filename
    # Split on non-alphanumeric (preserving NO-GO as a unit via pre-processing)
    normalized = stem.upper().replace("NO-GO", "NOGO")
    tokens = re.split(r'[^A-Z0-9]+', normalized)
    
    signals = []
    for token in tokens:
        if token == "NOGO":
            signals.append("no_go")
        elif token in ("GO", "VERIFIED", "VERIFICATION", "LGTM"):
            signals.append("go")
        # GOVERNANCE, GOOD, GOALS etc. are NOT matched — they never appear
        # as exact tokens in _FILENAME_VERDICT_TOKENS
    return signals


def extract_outcome(content: str, filename: str) -> tuple[str, list[str]]:
    """Extract outcome using structured fields first, filename fallback last.
    
    Returns (outcome, warnings) where warnings lists conflict descriptions.
    """
    signals: list[tuple[str, str]] = []  # (source, outcome)
    warnings: list[str] = []
    
    # --- Source 1: Top-of-file verdict field (first 30 lines) ---
    top = "\n".join(content.split("\n")[:30])
    verdict_match = re.search(
        r'(?:^|\n)\s*\*?\*?[Vv]erdict\*?\*?\s*[:=]\s*(.+)',
        top,
    )
    if verdict_match:
        parsed = _parse_verdict_text(verdict_match.group(1))
        if parsed:
            signals.append(("top_field", parsed))
    
    # --- Source 2: ## Verdict section heading (any position) ---
    verdict_section = re.search(
        r'^##\s+[Vv]erdict\s*\n+(.+)',
        content,
        re.MULTILINE,
    )
    if verdict_section:
        parsed = _parse_verdict_text(verdict_section.group(1))
        if parsed:
            signals.append(("section", parsed))
    
    # --- Source 3: Filename tokens (fallback) ---
    fn_signals = _extract_filename_signals(filename)
    for sig in fn_signals:
        signals.append(("filename", sig))
    
    # --- Resolution ---
    if not signals:
        return "informational", warnings
    
    # Deduplicate outcomes
    unique_outcomes = set(outcome for _, outcome in signals)
    
    if len(unique_outcomes) == 1:
        return unique_outcomes.pop(), warnings
    
    # Conflict: structured sources (top_field, section) take priority over filename
    structured = [(src, out) for src, out in signals if src != "filename"]
    if structured:
        structured_outcomes = set(out for _, out in structured)
        if len(structured_outcomes) == 1:
            # Structured sources agree; filename disagrees → use structured
            return structured_outcomes.pop(), warnings
    
    # True conflict between structured sources, or all-filename conflict
    warnings.append(
        f"Conflicting verdict signals in {filename}: "
        + ", ".join(f"{src}={out}" for src, out in signals)
    )
    return "informational", warnings
```

## Key Design Decisions

1. **Structured before filename:** Top-of-file `Verdict:` field and `## Verdict`
   section are checked first. Filename tokens are a fallback only.

2. **Token-based filename matching:** The stem is split on non-alphanumeric
   separators. Only exact tokens like `GO`, `NOGO`, `VERIFIED` match. Words
   like `GOVERNANCE`, `GOOD`, `GOALS` are never matched because they are not
   in the token set.

3. **`owner_decision` explicitly parsed:** Both `_parse_verdict_text` (used for
   structured fields and sections) and the resolution logic handle
   `owner_decision` as a first-class outcome.

4. **Conflict resolution hierarchy:**
   - All signals agree → return that outcome
   - Structured sources agree, filename disagrees → use structured
   - Structured sources conflict → return `informational` + warning
   - Only filename signals and they conflict → return `informational` + warning

5. **Dry-run warning list:** The function returns `(outcome, warnings)`. Any
   file with conflicting signals appears in the dry-run output for human review.

## Regression Test: GOVERNANCE Audit Filename

```python
def test_governance_audit_not_classified_as_go():
    """INSIGHTS-2026-03-30-10-57-ARCH-TECH-GOVERNANCE-AUDIT.md
    has ## Verdict / 'Not yet.' — must NOT return 'go'."""
    content = "# Architecture Audit\n\n## Verdict\n\nNot yet.\n\nDetails..."
    filename = "INSIGHTS-2026-03-30-10-57-ARCH-TECH-GOVERNANCE-AUDIT.md"
    outcome, warnings = extract_outcome(content, filename)
    assert outcome == "informational"  # "Not yet." is not a verdict token
    assert not warnings  # No conflict — section parsed, no filename match
```

## Updated Test Plan

Parser tests (all from v3 plus additions):

1. Final GO report mentioning prior NO-GO → `go` (from top-of-file Verdict: GO)
2. NO-GO report → `no_go`
3. Report with "Decision Needed From Owner" but no verdict → `informational`
4. **True owner-decision with `Verdict: owner_decision` → `owner_decision`** (P1 fix)
5. Informational session wrap (no verdict field) → `informational`
6. Filename-only GO (`*-REREVIEW-GO.md`) with no body verdict → `go`
7. Deterministic primary SPEC/WI: same result across multiple runs
8. Decimal SPEC ID extraction: `SPEC-245.1` found
9. **GOVERNANCE audit filename → `informational`** (P1 fix, regression test)
10. **Structured NO-GO overrides filename GO token → `no_go`** (P1 fix)
11. **Conflicting structured signals → `informational` + warning** (P2 fix)
12. **`Verdict: owner_decision` in `## Verdict` section → `owner_decision`** (P1 fix)
13. **Filename with VERIFICATION token → `go`** (existing reports use this)

## Prerequisite

GroundTruth `redact_content()` must include Agent Red key format patterns
(`ar_live_`, `ar_user_`, `ar_spa_plat_`, `pk_live_`). This is shared with
WI-3142 and will be implemented first.

## Files Changed

| File | Change |
|------|--------|
| `scripts/backfill_lo_reports.py` | Revised outcome parser with signal collection + conflict resolution |
| `tests/unit/test_lo_report_backfill.py` | 13 parser tests including regression tests for GOVERNANCE and owner_decision |

## Review Questions for Codex

None — all 3 NO-GO conditions addressed.
