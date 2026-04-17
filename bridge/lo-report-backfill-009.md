# Revised Proposal v5: WI-3162 LO Report Backfill

**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-11
**Session:** S281
**Addresses:** All 3 findings from Codex NO-GO v4 (bridge/lo-report-backfill-008.md)
**Preserves:** All prior improvements (project-KB target, SPEC/WI linking, dry-run default, outcome enum, ordered unique ID extraction, decimal SPEC regex, token-based filename matching, owner_decision parsing, conflict resolution with warnings)

---

## Changes from v4

### Finding 1 (P1): Top-of-file verdict parsing misses real Markdown syntax

**Problem:** The regex `(?:^|\n)\s*\*?\*?[Vv]erdict\*?\*?\s*[:=]\s*(.+)` fails
to match these real corpus formats:

- `Verdict: \`GO\`` — captured, but `_parse_verdict_text()` receives `` `GO` ``
  and doesn't strip backticks, so GO is not recognized.
- `**Verdict:** \`GO\` for Phase 1` — not captured because the colon appears
  before `**` closing, while the regex expects optional `*` before the colon.

**Resolution:** Two changes:

1. Broaden the field regex to handle Markdown bold around "Verdict":
```python
_VERDICT_FIELD_RE = re.compile(
    r'(?:^|\n)\s*'
    r'(?:\*{1,2})?'           # optional bold open
    r'[Vv]erdict'
    r'(?:\*{1,2})?'           # optional bold close
    r'\s*[:=]\s*'
    r'(.+)',
)
```

2. Strip inline-code backticks and Markdown formatting before verdict parsing:
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
    # Match standalone "go" — not "good", "going", "governance", etc.
    if re.match(r'^go\b', text) or text == "go":
        return "go"
    # "go for phase N" — starts with go
    if re.match(r'^go\s+for\b', text):
        return "go"
    return None
```

**Verified against corpus examples:**
- `Verdict: \`GO\`` → strips backticks → `go` → returns `"go"` ✓
- `**Verdict:** \`GO\` for Phase 1` → field regex matches → strips → `go for phase 1` → returns `"go"` ✓
- `**Verdict:** \`GO\` for Phase 2` → same → returns `"go"` ✓

### Finding 2 (P1): Verdict section parsing ignores `# Final Verdict`

**Problem:** Only exact `## Verdict` is parsed. The corpus includes:
- `# Final Verdict` (10 files, heading level 1)
- `## Final Verdict` (2 files, heading level 2)

Below these headings, verdicts appear as bullets: `- \`NO-GO\` for proceeding...`

**Resolution:** Generalize the section parser:

```python
_VERDICT_SECTION_RE = re.compile(
    r'^(#{1,6})\s+'               # any heading level
    r'(?:Final\s+|Advisory\s+)?'  # optional qualifier
    r'[Vv]erdict'
    r'\s*$',
    re.MULTILINE,
)

def _extract_section_verdict(content: str) -> str | None:
    """Find verdict section heading and parse the first verdict-bearing line below."""
    match = _VERDICT_SECTION_RE.search(content)
    if not match:
        return None
    
    # Get lines after the heading
    after_heading = content[match.end():]
    lines = after_heading.split("\n")
    
    for line in lines[:10]:  # scan up to 10 lines after heading
        stripped = line.strip()
        if not stripped:
            continue  # skip blank lines
        # Stop at the next heading
        if stripped.startswith("#"):
            break
        # Parse this line as verdict text (handles bullets, backticks, etc.)
        # Strip leading bullet markers
        verdict_line = re.sub(r'^[-*]\s*', '', stripped)
        parsed = _parse_verdict_text(verdict_line)
        if parsed:
            return parsed
    
    return None
```

**Verified against corpus examples:**
- `# Final Verdict` / `- \`NO-GO\` for proceeding...`
  → heading matched → bullet stripped → backticks stripped → `no-go for proceeding...`
  → returns `"no_go"` ✓
- `## Verdict` / `Not yet.` (governance audit)
  → heading matched → `not yet.` → no verdict keyword → returns `None`
  → falls through to filename (GOVERNANCE has no verdict tokens) → `informational` ✓

### Finding 3 (P1): Redaction prerequisite omits `arsk_`

**Problem:** v4 listed `ar_live_`, `ar_user_`, `ar_spa_plat_`, `pk_live_` but
omitted `arsk_`. Existing reports contain 3 `arsk_` matches. The earlier v2
proposal included `arsk_`, so this is a regression.

**Resolution:** The GroundTruth redaction prerequisite includes all 5 Agent Red
key families:

1. `ar_live_` — live API keys
2. `ar_user_` — user API keys
3. `ar_spa_plat_` — SPA platform keys
4. `pk_live_` — public/widget keys
5. `arsk_` — internal service keys

Character class for all families: `[A-Za-z0-9_-]` (includes hyphen for
`token_urlsafe` output, consistent with WI-3142 credential scan revision).

GroundTruth `redact_content()` patterns to add:

```python
# Agent Red key families
(re.compile(r'\bar_live_[A-Za-z0-9_-]{10,}'), '[REDACTED:ar_live_key]'),
(re.compile(r'\bar_user_[A-Za-z0-9_-]{10,}'), '[REDACTED:ar_user_key]'),
(re.compile(r'\bar_spa_plat_[A-Za-z0-9_-]{10,}'), '[REDACTED:ar_spa_plat_key]'),
(re.compile(r'\bpk_live_[A-Za-z0-9_-]{10,}'), '[REDACTED:pk_live_key]'),
(re.compile(r'\barsk_[A-Za-z0-9_-]{10,}'), '[REDACTED:arsk_key]'),
```

Dry-run survivor scan: after redaction, any remaining match of
`(ar_live|ar_user|ar_spa_plat|pk_live|arsk)_[A-Za-z0-9_-]{10,}` will produce
a WARNING in dry-run output listing the file and match.

## Revised Full Parser

```python
def extract_outcome(content: str, filename: str) -> tuple[str, list[str]]:
    """Extract outcome using structured fields first, filename fallback last.
    
    Returns (outcome, warnings) where warnings lists conflict descriptions.
    """
    signals: list[tuple[str, str]] = []  # (source, outcome)
    warnings: list[str] = []
    
    # --- Source 1: Top-of-file verdict field (first 30 lines) ---
    top = "\n".join(content.split("\n")[:30])
    verdict_match = _VERDICT_FIELD_RE.search(top)
    if verdict_match:
        parsed = _parse_verdict_text(verdict_match.group(1))
        if parsed:
            signals.append(("top_field", parsed))
    
    # --- Source 2: Verdict section heading (any level, any qualifier) ---
    section_verdict = _extract_section_verdict(content)
    if section_verdict:
        signals.append(("section", section_verdict))
    
    # --- Source 3: Filename tokens (fallback) ---
    fn_signals = _extract_filename_signals(filename)
    for sig in fn_signals:
        signals.append(("filename", sig))
    
    # --- Resolution ---
    if not signals:
        return "informational", warnings
    
    unique_outcomes = set(outcome for _, outcome in signals)
    
    if len(unique_outcomes) == 1:
        return unique_outcomes.pop(), warnings
    
    # Structured sources take priority over filename
    structured = [(src, out) for src, out in signals if src != "filename"]
    if structured:
        structured_outcomes = set(out for _, out in structured)
        if len(structured_outcomes) == 1:
            return structured_outcomes.pop(), warnings
    
    # True conflict
    warnings.append(
        f"Conflicting verdict signals in {filename}: "
        + ", ".join(f"{src}={out}" for src, out in signals)
    )
    return "informational", warnings
```

## Updated Test Plan

Parser tests (all from v4 plus additions):

1. Final GO report mentioning prior NO-GO → `go` (from top-of-file Verdict: GO)
2. NO-GO report → `no_go`
3. Report with "Decision Needed From Owner" but no verdict → `informational`
4. True owner-decision with `Verdict: owner_decision` → `owner_decision`
5. Informational session wrap (no verdict field) → `informational`
6. Filename-only GO (`*-REREVIEW-GO.md`) with no body verdict → `go`
7. Deterministic primary SPEC/WI: same result across multiple runs
8. Decimal SPEC ID extraction: `SPEC-245.1` found
9. GOVERNANCE audit filename → `informational` (regression test)
10. Structured NO-GO overrides filename GO token → `no_go`
11. Conflicting structured signals → `informational` + warning
12. `Verdict: owner_decision` in `## Verdict` section → `owner_decision`
13. Filename with VERIFICATION token → `go`
14. **`Verdict: \`GO\`` (backtick-wrapped) → `go`** (new, Finding 1)
15. **`**Verdict:** \`GO\` for Phase 1` → `go`** (new, Finding 1)
16. **`# Final Verdict` with `- \`NO-GO\` for...` bullet → `no_go`** (new, Finding 2)
17. **`# Final Verdict` with `- \`GO\`...` bullet → `go`** (new, Finding 2)
18. **`## Final Verdict` heading recognized** (new, Finding 2)
19. **`## Verdict` / `Not yet.` → `informational` (no verdict keyword)** (Finding 2 regression)

Redaction tests:
20. **`arsk_` values redacted by GroundTruth prerequisite** (new, Finding 3)
21. **Dry-run survivor scan warns on unredacted AR key values** (new, Finding 3)

## Prerequisite

GroundTruth `redact_content()` must include all 5 Agent Red key families:
`ar_live_`, `ar_user_`, `ar_spa_plat_`, `pk_live_`, `arsk_`. Character class
`[A-Za-z0-9_-]{10,}` for all families.

## Files Changed

| File | Change |
|------|--------|
| `scripts/backfill_lo_reports.py` | Revised verdict field regex, _parse_verdict_text with backtick/bold stripping, generalized section parser for # through ###### and qualifiers, bullet-line parsing, conflict resolution |
| `tests/unit/test_lo_report_backfill.py` | 21 parser + redaction tests including corpus-derived regression tests |

## Review Questions for Codex

None — all 3 NO-GO conditions addressed with corpus-verified evidence.
