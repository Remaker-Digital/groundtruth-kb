# Gap Analysis — Identifier Reset Without Vector Backfill

**Investigation run:** 20260528T002632Z
**Bridge thread:** `gtkb-chromadb-vector-continuity-v1-cut-scoping`
**Work item:** WI-3395
**Source:** Finding 3 of `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-27-08-52-V1-RELEASE-STRATEGY-REVIEW.md`

## 1. The Gap In One Sentence

The `memory/v1-release-strategy-deliberation-S347.md` §8.4 Option A mitigation (a one-time text identifier-translation manifest) handles textual citation continuity but does **not** handle ChromaDB vector retrieval continuity, because the 20,224 embedded chunks in `.groundtruth-chroma/` are mechanically bound to old DELIB IDs via both their chunk-ID prefix AND their `delib_id` metadata field.

## 2. Concrete Failure Modes (Without Backfill)

### Failure Mode 1 — Stale-history search returns empty

**Scenario:** After v1.0 cut + DELIB-ID reset, a session asks `gt deliberations search "v1 release strategy"` to recall prior reasoning.

**Without backfill:** the query returns matches against post-cut DELIB IDs only (a few session entries from immediately after the cut). Pre-cut reasoning is invisible to semantic retrieval. The 9-month accumulation of owner decisions, LO reviews, and architectural rationale that established GT-KB's current shape becomes unreachable except via text grep against bridge files / memory files (with no semantic ranking, no relevance scoring, no concept matching).

**Severity:** P0 for any session that depends on cross-cutting decision context. The Deliberation Archive's reason-of-existence (per `ADR-0001` three-tier memory architecture) is rationale recall; losing 99%+ of the recall surface defeats the architecture.

### Failure Mode 2 — Citation-translation-manifest works for citations, fails for queries

**Scenario:** A post-cut bridge proposal cites `DELIB-S347-V1-RELEASE-STRATEGY-CHOICES-2026-05-13` in its Prior Deliberations section. The text-translation manifest maps this to (e.g.) `HIST-DELIB-V1-RELEASE-STRATEGY-CHOICES-2026-05-13`.

**Without backfill:** the citation TEXT is correct (the manifest translated it), but `gt deliberations search "HIST-DELIB-V1-RELEASE-STRATEGY-CHOICES-2026-05-13"` returns no result because no ChromaDB chunk has that ID prefix or metadata. Codex's review (which uses `search_deliberations` to verify cited DELIB references exist) would flag the citation as unverifiable.

**Severity:** P1 — surface-level breakage of every post-cut proposal that cites pre-cut DELIBs. Mitigation by manual citation expansion would convert the bridge review from a semantic check to a brittle text check.

### Failure Mode 3 — Bridge Prior Deliberations seeder cannot suggest historical context

**Scenario:** `proposal_autoload.py` in the bridge-propose helper seeds the Prior Deliberations section from glossary terms + semantic search. After cut, semantic-search hits only new DELIB IDs.

**Without backfill:** newly-filed proposals lack historical-decision context in their Prior Deliberations sections. Each proposal becomes context-isolated; sessions repeat decisions that were already made (re-deliberation defect that the Deliberation Archive exists to prevent).

**Severity:** P1 — degradation of the bridge-propose helper's core value-add.

### Failure Mode 4 — LO advisory references lose context

**Scenario:** A Loyal Opposition report cites the design rationale behind a current implementation by querying historical DELIBs.

**Without backfill:** LO can find current DELIBs but not the originating ones. LO reports become shallower; alternatives-considered analysis loses precedent.

**Severity:** P2 — degradation of LO report depth.

### Failure Mode 5 — Quantification of provenance loss

**Without backfill, the following citation surface is mechanically invalidated for retrieval:**

| Subtree | Citations | Retrieval status post-cut |
|---|---:|---|
| `bridge/` | 11,132 | unverifiable via semantic search |
| `independent-progress-assessments/` | 7,197 | unverifiable via semantic search |
| `memory/` | 232 | unverifiable via semantic search |
| `.claude/rules/` | 70 | unverifiable via semantic search |
| **Total** | **18,631** | (citation hits across ~16,500 files) |

**Severity:** P0 in aggregate. The accumulated provenance surface is the project's reasoning memory.

## 3. What the Text Translation Manifest DOES Handle

To be fair to the v1-release-strategy-deliberation Option A mitigation, the text manifest correctly addresses:

- **Textual citation lookup** — `DELIB-XXXX` references in markdown files can be human-translated via the manifest.
- **Audit-trail readability** — humans following commit messages or bridge files can map old IDs to new ones.
- **Git history continuity** — commit messages remain readable.
- **External references** — owner-shared notes, training material, etc., can be updated by manifest lookup.

These are real benefits. The gap is the additional dimension (semantic retrieval) that the manifest doesn't address.

## 4. The Architectural Tension

The deeper issue: the Deliberation Archive's value proposition (per `SPEC-2098`) is **semantic** rationale recall. Text citations are the surface; embedded-vector search is the substrate. Resetting IDs disconnects the surface from the substrate unless the substrate is migrated in parallel.

This isn't a defect in the Option A choice — it's a previously-unrecognized consequence. The S347 strategy doc accurately framed the identifier-reset blast radius but didn't enumerate the vector-substrate dimension (verified: `grep [Cc]hroma|vector|semantic.*history|HIST-` on `memory/v1-release-strategy-deliberation-S347.md` returns zero matches).

## 5. The Implementation Question

The text manifest IS doable mechanically without a backfill: it's a `sed`-style global find-replace plus a published mapping table.

The vector backfill is harder because:
- 20,224 chunks need re-embedding (or re-keying without re-embedding, if the embedding-model version is held constant).
- The chunk-ID format (`<delib_id>::v1::chunk-N`) embeds the DELIB ID in the chunk ID itself. Re-keying requires either (a) duplicating chunks with new IDs and old metadata, or (b) re-indexing.
- The metadata `delib_id` field must be updated in parallel with the chunk-ID prefix.
- The 136 MB SQLite file would approximately double in size if HIST-prefixed copies are added alongside post-cut entries.

## 6. Gap Severity Summary

| Dimension | Text-manifest only | Text-manifest + vector backfill |
|---|---|---|
| Citation readability | adequate | adequate |
| Semantic search of pre-cut DELIBs | broken | restored |
| Bridge Prior Deliberations seeder | degraded | functional |
| LO advisory context recall | degraded | functional |
| Project decision history accessibility | text-grep only | semantic-search restored |
| Storage footprint | unchanged | ~2× ChromaDB substrate |
| Implementation complexity | low | medium (one-time backfill script) |
| Operational risk post-cut | high (re-deliberation defect class) | low |

**Conclusion:** the vector backfill closes a real gap in the Option A mitigation. The cost (one-time backfill complexity + ~136 MB storage doubling) is small relative to the value preserved (~18,631 citation hits remain semantically retrievable).

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
