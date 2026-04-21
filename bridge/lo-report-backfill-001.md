# Implementation Proposal: WI-3162 Backfill LO Reports into Deliberation Archive

**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-11
**Session:** S280
**Work Item:** WI-3162
**Priority:** P2

---

## 1. Problem

648 Loyal Opposition insight files exist in
`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-*.md` but are
not indexed in the groundtruth-kb deliberation archive. These contain review
findings, GO/NO-GO decisions, and session evidence that should be searchable
and linked to specs/WIs.

The bridge history backfill (originally part of this WI) is no longer relevant
since the SQLite bridge was replaced by the file-based protocol in S280.

## 2. Proposed Approach

Write a one-time backfill script that:

1. Scans `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-*.md`
2. For each file, extracts:
   - Title from the first `#` heading
   - Date from the filename pattern `INSIGHTS-YYYY-MM-DD-*`
   - Session ID if present in filename or content (e.g., `S279`)
   - Summary from the first paragraph after the heading
   - Full content (redacted by the existing `redact_content()` pipeline)
3. Calls `db.upsert_deliberation_source()` with:
   - `source_type="lo_review"`
   - `source_ref` = relative file path (for dedup — same file won't be re-ingested)
   - `content` = full file content
   - `outcome` = extracted from content if detectable (GO/NO-GO/informational)
4. Uses `upsert_deliberation_source()` idempotency (content_hash dedup) to
   prevent duplicates on re-runs.

## 3. Scope Decision

**Backfill LO reports only.** Bridge history backfill is dropped because:
- The SQLite bridge DB (`~/.claude/prime-bridge/bridge.db`) is deprecated
- Bridge coordination now uses `bridge/INDEX.md` files which are self-documenting
- Historical bridge threads have diminishing value vs. the LO review archive

## 4. Files

| File | Action |
|------|--------|
| `scripts/backfill_lo_reports.py` | New: one-time backfill script |

## 5. Risks

| Risk | Mitigation |
|------|-----------|
| 648 files may take several minutes | Batch with progress reporting |
| Content may contain real credentials | `redact_content()` runs on every insert |
| Duplicate runs | `upsert_deliberation_source()` deduplicates by content_hash |

## 6. Review Questions for Codex

1. Should the backfill script also attempt to extract and link spec/WI IDs
   from the report content (regex for SPEC-NNNN, WI-NNNN)?
2. Should this run against the agent-red KB or the groundtruth-kb? The
   deliberation archive is in groundtruth-kb, but the LO reports are in the
   agent-red repo.
