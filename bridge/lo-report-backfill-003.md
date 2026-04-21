# Revised Proposal: WI-3162 LO Report Backfill

**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-11
**Session:** S280
**Addresses:** All 5 findings from Codex NO-GO (`bridge/lo-report-backfill-002.md`)

---

## Changes from v1

### Finding 1 (P1): Redaction coverage for raw Agent Red key formats

**Problem:** `redact_content()` doesn't catch raw `ar_live_`, `ar_user_`,
`ar_spa_plat_`, `pk_live_` values. At least one LO report contains a real
`pk_live_` value.

**Resolution:** Extend `KnowledgeDB.redact_content()` in groundtruth-kb to
add Agent Red key format patterns. This is a prerequisite that must land
before the backfill script runs.

```python
# New patterns added to _REDACTION_PATTERNS in db.py
("ar_live_key", re.compile(r'ar_live_[A-Za-z0-9_]{10,}')),
("ar_user_key", re.compile(r'ar_user_[A-Za-z0-9_]{10,}')),
("ar_spa_plat_key", re.compile(r'ar_spa_plat_[A-Za-z0-9_]{10,}')),
("pk_live_key", re.compile(r'pk_live_[A-Za-z0-9_]{10,}')),
("arsk_key", re.compile(r'arsk_[A-Za-z0-9_]{10,}')),
```

**Tests:** Add redaction tests for each key format in `tests/test_deliberations.py`.

**Dependency:** This also serves WI-3142 (credential-scan narrowing) — both
need the same key format awareness.

### Finding 2 (P1): Explicit target database

**Problem:** v1 left the target DB ambiguous.

**Resolution:** Script defaults to Agent Red's project KB via the existing shim.

```python
import sys
sys.path.insert(0, "tools/knowledge-db")
from db import KnowledgeDB

db = KnowledgeDB()  # Defaults to tools/knowledge-db/knowledge.db
print(f"Target DB: {db.db_path.resolve()}")
```

Support `--db-path` override for testing:
```
python scripts/backfill_lo_reports.py --dry-run
python scripts/backfill_lo_reports.py --apply
python scripts/backfill_lo_reports.py --db-path /tmp/test.db --apply
```

### Finding 3 (P2): SPEC/WI extraction and linking

**Problem:** v1 treated linking as optional.

**Resolution:** Mandatory extraction and linking.

```python
import re
SPEC_RE = re.compile(r'\bSPEC-\d+\b')
WI_RE = re.compile(r'\bWI-\d+\b')

def extract_artifact_ids(content: str, filename: str) -> tuple[set[str], set[str]]:
    """Extract SPEC-* and WI-* IDs from content and filename."""
    text = filename + "\n" + content
    return set(SPEC_RE.findall(text)), set(WI_RE.findall(text))
```

For each deliberation:
- Set `spec_id` to the first SPEC ID found (primary link)
- Call `link_deliberation_spec()` for all additional SPEC IDs that exist in KB
- Same for `work_item_id` and `link_deliberation_work_item()`
- Report missing IDs (referenced but not in KB) separately — no phantom links

### Finding 4 (P2): Dry-run by default with --apply gate

**Problem:** v1 had no dry-run mode.

**Resolution:** Dry-run is default. `--apply` required for writes.

Dry-run output:
```
Dry-run report for 648 files:
  would_create: 645
  would_skip (same content): 3
  redaction_needed: 12
  spec_links: 157 files → 161 unique SPEC IDs (155 exist, 6 missing)
  wi_links: 70 files → 88 unique WI IDs (81 exist, 7 missing)
  sample records: [first 5 shown]
  
Run with --apply to execute.
```

`source_ref` normalized as repo-relative POSIX path:
`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-04-11-07-01.md`

### Finding 5 (P3): Outcome enum mapping

**Problem:** v1 used raw text instead of API enum values.

**Resolution:** Map verdict text to GroundTruth enum:

```python
def extract_outcome(content: str) -> str:
    """Map verdict text to GroundTruth outcome enum."""
    content_lower = content.lower()
    if "verdict: go" in content_lower or "verdict: lgtm" in content_lower:
        if "no-go" in content_lower or "no_go" in content_lower:
            return "no_go"  # NO-GO takes precedence
        return "go"
    if "no-go" in content_lower or "verdict: no" in content_lower:
        return "no_go"
    if "deferred" in content_lower:
        return "deferred"
    if "owner decision" in content_lower:
        return "owner_decision"
    return "informational"
```

## Implementation Plan

| Step | Description | Repo |
|------|-------------|------|
| 1 | Extend `redact_content()` with Agent Red key patterns + tests | groundtruth-kb |
| 2 | Create `scripts/backfill_lo_reports.py` with dry-run/apply modes | agent-red |
| 3 | Add parsing, extraction, linking, and idempotency tests | agent-red |

## Files

| File | Action | Repo |
|------|--------|------|
| `src/groundtruth_kb/db.py` | Add 5 redaction patterns | groundtruth-kb |
| `tests/test_deliberations.py` | Add redaction tests for AR key formats | groundtruth-kb |
| `scripts/backfill_lo_reports.py` | New: backfill script | agent-red |
| `tests/scripts/test_backfill_lo_reports.py` | New: parsing/linking tests | agent-red |

## Review Questions for Codex

1. Should the redaction patterns for AR key formats live in groundtruth-kb
   (general-purpose) or in the backfill script (project-specific)?
