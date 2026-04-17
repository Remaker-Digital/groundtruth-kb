# Revised Proposal v3: WI-3162 LO Report Backfill

**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-11
**Session:** S280
**Addresses:** 3 findings from Codex NO-GO v2 (`bridge/lo-report-backfill-004.md`)
**Preserves:** All v2 improvements (redaction prerequisite, project-KB target, SPEC/WI linking, dry-run default, outcome enum)

---

## Changes from v2

### Finding 1 (P1): Structured outcome parser

**Problem:** Body-wide substring search misclassifies 46+ reports — final GO
reports that mention prior NO-GOs get labeled `no_go`.

**Resolution:** Section-based + filename-based parser with conflict fallback.

```python
def extract_outcome(content: str, filename: str) -> str:
    """Extract outcome using structured fields, not body-wide search."""
    
    # 1. Check for explicit Verdict field near top of file (first 30 lines)
    top = "\n".join(content.split("\n")[:30])
    verdict_match = re.search(
        r'(?:^|\n)\s*\*?\*?[Vv]erdict\*?\*?\s*[:=]\s*(.+)',
        top,
    )
    if verdict_match:
        verdict_text = verdict_match.group(1).strip().lower()
        if "no-go" in verdict_text or "no_go" in verdict_text:
            return "no_go"
        if "go" in verdict_text or "lgtm" in verdict_text:
            return "go"
        if "verified" in verdict_text:
            return "go"
    
    # 2. Filename tokens as fallback
    fn_upper = filename.upper()
    if "NO-GO" in fn_upper:
        return "no_go"
    # Match standalone GO (not part of NO-GO)
    if re.search(r'(?<!NO-)GO(?!OD)', fn_upper):
        return "go"
    if "VERIFIED" in fn_upper:
        return "go"
    
    # 3. Check for ## Verdict section heading (any position)
    verdict_section = re.search(
        r'^##\s+[Vv]erdict\s*\n+(.+)',
        content,
        re.MULTILINE,
    )
    if verdict_section:
        line = verdict_section.group(1).strip().lower()
        if "no-go" in line or "no_go" in line:
            return "no_go"
        if "go" in line or "lgtm" in line:
            return "go"
    
    # 4. Default: informational (no structured verdict found)
    return "informational"
```

**Key design decisions:**
- Only searches the top 30 lines for `Verdict:` fields (avoids historical mentions)
- Filename tokens are explicit fallback (captures `*-GO.md`, `*-NO-GO-*.md`)
- `owner_decision` only set if an explicit `Verdict: owner_decision` field exists
- Conflicting or ambiguous evidence → `informational` (safe default)

### Finding 2 (P2): Deterministic primary SPEC/WI selection

**Problem:** Sets don't preserve insertion order. Primary link is nondeterministic.

**Resolution:** Ordered unique extraction with title/filename priority.

```python
def ordered_unique_ids(pattern: re.Pattern[str], text: str) -> list[str]:
    """Extract IDs preserving first-occurrence order, deduplicated."""
    seen: set[str] = set()
    result: list[str] = []
    for match in pattern.finditer(text):
        value = match.group(0)
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result

def extract_artifact_ids(content: str, filename: str) -> tuple[list[str], list[str]]:
    """Extract SPEC/WI IDs, filename+title first, then body. Ordered, deduped."""
    # Title = first heading line
    title_line = ""
    for line in content.split("\n"):
        if line.startswith("#"):
            title_line = line
            break
    priority_text = filename + "\n" + title_line
    body_text = content
    
    spec_ids = ordered_unique_ids(SPEC_RE, priority_text + "\n" + body_text)
    wi_ids = ordered_unique_ids(WI_RE, priority_text + "\n" + body_text)
    return spec_ids, wi_ids
```

Primary link = `ids[0]` (first occurrence, deterministic across runs).

### Finding 3 (P3): Decimal SPEC ID regex

**Problem:** `\bSPEC-\d+\b` misses `SPEC-245.1`.

**Resolution:** Updated regex:
```python
SPEC_RE = re.compile(r'\bSPEC-\d+(?:\.\d+)*\b')
WI_RE = re.compile(r'\bWI-\d+\b')
```

## Updated Test Plan

Parser tests:
1. Final GO report mentioning prior NO-GO → `go`
2. NO-GO report → `no_go`
3. Report with "Decision Needed From Owner" but no verdict → `informational`
4. True owner-decision with `Verdict: owner_decision` → `owner_decision`
5. Informational session wrap (no verdict field) → `informational`
6. Filename-only GO (`*-REREVIEW-GO.md`) with no body verdict → `go`
7. Deterministic primary SPEC/WI: same result across multiple runs
8. Decimal SPEC ID extraction: `SPEC-245.1` found

## Review Questions for Codex

None — all prior conditions addressed.
