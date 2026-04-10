# Deliberation Archive — Implementation Proposal

**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-10
**Status:** Proposal — pending Codex review
**Target:** groundtruth-kb v0.3.0

---

## 1. Problem Statement

Our pipeline produces structured decision records (specs, WIs, tests) but loses the reasoning that informed those decisions. When a spec's `change_reason` says "Phase 4 remediation per Codex review," the 3-round review cycle — the findings, the rejected alternatives, the owner's business constraints — is not linked to the spec in any searchable way.

This deliberation context exists in three places today:
- **Bridge messages** — structured but transient, not indexed against specs
- **CODEX-INSIGHT-DROPBOX reports** — flat markdown files, not cross-referenced
- **Session transcripts** — lost when context compresses between sessions

The gap matters because:
1. Decision archaeology is expensive (manual scanning of reports and bridge logs)
2. Cross-project knowledge transfer requires re-deriving decisions from first principles
3. Loyal Opposition reviews cannot reference prior deliberation patterns
4. Due diligence reviewers see decisions but not the reasoning behind them

---

## 2. Architecture Decision: Build vs. Adopt

### Decision

Build a `deliberations` table in groundtruth-kb with optional ChromaDB semantic search. Do not adopt MemPalace or other external deliberation tools.

### Context

MemPalace (github.com/milla-jovovich/mempalace, 39K stars, MIT license) solves a general version of this problem: store conversation transcripts in ChromaDB, search semantically. It scores 96.6% on LongMemEval using raw verbatim storage with no LLM extraction.

### Why Not Adopt

1. **Maturity risk.** MemPalace is 5 days old. Open bugs include data loss on upgrade (#469), shell injection in hooks (#110), MCP write failures (#526, #538), and macOS installation failures (#561). Our PB-DATA-INTEGRITY standard requires proven data durability.

2. **Adapter overhead.** MemPalace stores unstructured blobs. Our gap is *structured*: deliberations linked to specs and WIs. Adopting MemPalace would require building a linking adapter on top, maintaining compatibility across MemPalace versions, and working around its assumptions (conversation-centric mining, palace metaphor, AAAK compression — none of which apply to our use case).

3. **The useful part is ChromaDB.** MemPalace's core retrieval mechanism is ChromaDB's default embeddings on raw text. The palace structure (wings, rooms, closets) is standard metadata filtering. We can use ChromaDB directly for the same retrieval quality without the abstraction layer.

4. **Fit for purpose.** We need ~200 lines of Python that extend an existing, proven codebase (groundtruth-kb). A general-purpose tool adds dependency management, upgrade risk, and adaptation cost for capabilities we don't need.

### Consequences

- We own the implementation and its maintenance
- No external dependency beyond `chromadb` (which MemPalace also depends on)
- If a better structured deliberation tool emerges, our data is portable (text + metadata, standard schema)
- We can revisit this decision if MemPalace matures and demonstrates a capability we can't match cost-effectively

### Rejected Alternatives

| Alternative | Reason for Rejection |
|------------|---------------------|
| MemPalace adoption | Immature, adapter overhead, general-purpose for a specific problem |
| Store deliberations as KB documents | Documents lack structured spec/WI linking and semantic search |
| Store deliberations in bridge messages only | Bridge is transient coordination, not an archive; no semantic search |
| No deliberation archive | Leaves the pipeline gap unaddressed; impedes cross-project knowledge transfer |

---

## 3. Specification: Deliberation Archive

### 3.1 Schema

New table in groundtruth-kb SQLite database:

```sql
CREATE TABLE deliberations (
    id          TEXT    NOT NULL,
    version     INTEGER NOT NULL,
    spec_id     TEXT,                    -- FK to specifications.id (nullable)
    work_item_id TEXT,                   -- FK to work_items.id (nullable)
    source_type TEXT    NOT NULL,        -- lo_review | proposal | owner_conversation | report | session_harvest
    source_ref  TEXT,                    -- bridge message_id, file path, thread_id, or session_id
    title       TEXT    NOT NULL,        -- Short summary for listing
    summary     TEXT    NOT NULL,        -- 2-5 sentence distillation of the deliberation
    content     TEXT    NOT NULL,        -- Full deliberation text
    participants TEXT,                   -- JSON array: ["prime", "codex", "owner"]
    outcome     TEXT,                    -- go | no_go | deferred | owner_decision | informational
    session_id  TEXT,                    -- Session ID (e.g., "S277") for temporal context
    changed_by  TEXT    NOT NULL,
    changed_at  TEXT    NOT NULL,
    change_reason TEXT  NOT NULL,
    UNIQUE(id, version)
);

CREATE INDEX idx_deliberations_spec_id ON deliberations(spec_id);
CREATE INDEX idx_deliberations_work_item_id ON deliberations(work_item_id);
CREATE INDEX idx_deliberations_source_type ON deliberations(source_type);
CREATE INDEX idx_deliberations_session_id ON deliberations(session_id);

CREATE VIEW current_deliberations AS
SELECT d.* FROM deliberations d
INNER JOIN (SELECT id, MAX(version) AS max_v FROM deliberations GROUP BY id) m
ON d.id = m.id AND d.version = m.max_v;
```

### 3.2 ChromaDB Integration

A companion ChromaDB collection provides semantic search over deliberation content:

```
Collection: deliberations
  - id: deliberation ID
  - document: content field (full text)
  - metadata: {spec_id, work_item_id, source_type, outcome, session_id, participants}
```

ChromaDB uses its default embedding model (all-MiniLM-L6-v2) — the same model that produces MemPalace's 96.6% LongMemEval score. No API key required. Runs locally.

The ChromaDB collection is a **search index**, not the source of truth. The SQLite table is canonical. ChromaDB can be rebuilt from SQLite at any time.

### 3.2.1 Content Richness Policy

The value of semantic search depends directly on the richness of the indexed content. MemPalace's key finding — 96.6% recall from raw verbatim text vs. lower scores from LLM-extracted summaries — applies here. Sparse content produces sparse search results.

**Rule: The `content` field stores verbatim source text, not summaries.**

The `summary` field (2-5 sentences) exists for listing and scanning. The `content` field stores the full, unabridged source material. Specifically:

| Source Type | What Goes in `content` | Expected Size |
|-------------|----------------------|---------------|
| `lo_review` | Complete review text: all findings, severity ratings, evidence paths, rejected alternatives, GO/NO-GO reasoning. For multi-round reviews, all rounds concatenated with round markers. | 500-5,000 words |
| `proposal` | Full implementation proposal: approach, alternatives considered, constraints, file touchpoints, sequencing. Not just "I propose to fix X" — the full reasoning. | 300-2,000 words |
| `owner_conversation` | Verbatim owner statements that contain reasoning, constraints, priorities, or business context. Not the entire session transcript — the segments where decisions were explained. | 100-1,000 words |
| `report` | Complete post-implementation report: what changed, what was tested, what gaps remain, commit references, test results. | 300-2,000 words |
| `session_harvest` | Key reasoning segments from prior session: decision points, rejected approaches, owner directives with context. Extracted by the harvest hook. | 200-1,500 words |

**Anti-patterns to avoid:**
- Storing only the `summary` in `content` (defeats the purpose of the archive)
- Truncating review rounds ("see round 1 above" — include the actual text)
- Omitting rejected alternatives ("we considered X but chose Y" without explaining why X was rejected)
- Stripping context ("phone OTP required" without "because unverified callers waste agent time and create support liability")

**ChromaDB chunking:** For deliberations exceeding 2,000 words, the content is split into overlapping chunks (512 tokens, 64-token overlap) and indexed as multiple ChromaDB documents sharing the same deliberation ID. Search results are deduplicated by deliberation ID, returning the highest-scoring chunk's score.

**Storage impact:** At ~2,000 words average per deliberation and ~500 deliberations per project, the raw content is ~1M words (~5MB text, ~50MB ChromaDB with embeddings). This is negligible relative to the KB's current ~40MB SQLite database.

### 3.3 Python API

New methods on `KnowledgeDB`:

```python
# Store a deliberation
db.insert_deliberation(
    id="DELIB-0042",
    spec_id="SPEC-1879",                    # optional
    work_item_id="WI-3030",                 # optional
    source_type="lo_review",                # required
    source_ref="bridge:msg-4462577a",       # optional
    title="SPEC-1879 Phase 4 review: phone verification gate",
    summary="3-round Codex review. Round 1: phone_verified gate missing (P1), "
            "escalation_sent always True (P1), no adaptive messaging (P1). "
            "Round 2: gate added but tier bypass found. Round 3: GO.",
    content="""Round 1 (NO-GO): Three P1 findings.
(1) phone_verified gate missing — escalation proceeds with unverified phone number.
Widget sends phone to escalation handler without checking verification status.
File: src/chat/escalation.py line 142. (2) escalation_sent always True —
EscalationManager.send() sets escalation_sent=True before checking delivery result,
meaning failed escalations are marked as sent. Repeat escalation is suppressed even
when the first one failed. File: src/chat/escalation_manager.py line 89.
(3) No adaptive messaging — all customers see "We'll call you at {phone}" even when
phone is not verified. Should show email-only escalation for unverified customers.
File: src/chat/templates/escalation_offer.py line 34.

Round 2 (NO-GO): Gate added but tier bypass found. phone_verified gate correctly
blocks unverified phones, but enterprise tier customers skip the gate via
tier_overrides config. This contradicts SPEC-1879 which requires verification
for all tiers. Evidence: src/chat/escalation.py line 155, tier_overrides dict.

Round 3 (GO): All three P1s resolved. phone_verified gate enforced for all tiers,
escalation_sent tracks actual delivery status, adaptive messaging shows
email/phone/generic based on verification state. 12 tests (was 6). Shopify mock
fixtures updated for new escalation flow. No remaining concerns.""",
    participants='["prime", "codex"]',
    outcome="go",
    session_id="S270",
    changed_by="prime",
    change_reason="Archive Phase 4 deliberation for SPEC-1879"
)

# Semantic search
results = db.search_deliberations(
    query="why do we require phone OTP before escalation",
    limit=5
)
# Returns: list of {id, spec_id, title, summary, content, score}

# Structured query
results = db.list_deliberations(spec_id="SPEC-1879")
results = db.list_deliberations(source_type="lo_review", session_id="S270")
results = db.list_deliberations(work_item_id="WI-3030")

# Get deliberations for a spec (complements get_tests_for_spec)
deliberations = db.get_deliberations_for_spec("SPEC-1879")
```

### 3.4 Source Types

| Source Type | When Created | Content |
|-------------|-------------|---------|
| `lo_review` | When Codex completes a review cycle | Full review findings, severity ratings, GO/NO-GO reasoning |
| `proposal` | When Prime sends an implementation proposal | Proposed approach, alternatives considered, constraints |
| `owner_conversation` | When owner provides reasoning for a decision | Business context, priorities, constraints, motivations |
| `report` | When a post-implementation report is created | What changed, what was tested, what gaps remain |
| `session_harvest` | At session end, via session-init hook on next session | Key reasoning segments extracted from prior session |

### 3.5 Session Harvest Hook

A new session-initialization hook extracts deliberation context from the previous session:

**Trigger:** Session start (after assertion-check hook, before bridge sweep)

**Behavior:**
1. Read the prior session's wrap-up prompt from `session_prompts` table
2. Read the prior session's bridge messages (sent and received)
3. Read any new CODEX-INSIGHT-DROPBOX reports since last harvest
4. For each artifact that contains deliberation (proposals, reviews, owner decisions):
   - Extract the spec_id/work_item_id it relates to
   - Create a deliberation record linking the reasoning to the decision
   - Index in ChromaDB for semantic search
5. Report: "Session harvest: N deliberations archived from S{prev}"

**What gets harvested:**
- Bridge threads with `expected_response: go_no_go` or `advisory_review`
- Loyal Opposition reports with P0-P2 findings
- Owner messages that contain decision language (GOV-09 patterns)
- Post-implementation reports sent via bridge

**What does NOT get harvested:**
- Routine status updates
- Bridge liveness checks
- System/protocol messages

### 3.6 Codex Access

Both Prime Builder and Loyal Opposition must have full read/write access:

**Writing:** Codex stores deliberations when:
- Completing a review (source_type: `lo_review`)
- Producing an insight report (source_type: `report`)
- Recording a decision rationale (source_type: `owner_conversation`)

**Reading:** Codex searches deliberations when:
- Reviewing an implementation proposal ("has a similar pattern been reviewed before?")
- Evaluating architecture compliance ("what was the original rationale for this ADR?")
- Checking for recurring findings ("have we flagged this class of issue before?")

**Access mechanism:** The `KnowledgeDB` Python API. Both agents already use `db.py`. No new access pattern required. Codex calls `db.search_deliberations()` and `db.insert_deliberation()` the same way it calls `db.list_specs()` and `db.get_tests_for_spec()`.

---

## 4. Implementation Plan

### Phase 1: Schema + API (groundtruth-kb)

| Item | Detail |
|------|--------|
| Add `deliberations` table to SCHEMA_SQL | Append-only, same pattern as all other tables |
| Add `current_deliberations` view | Standard latest-version view |
| Add ChromaDB as optional dependency | `chromadb>=0.5.0,<0.7` in `[project.optional-dependencies]` |
| Implement `insert_deliberation()` | Writes to SQLite + ChromaDB collection |
| Implement `search_deliberations()` | ChromaDB semantic search, returns with SQLite metadata |
| Implement `list_deliberations()` | Structured query by spec_id, work_item_id, source_type, session_id |
| Implement `get_deliberations_for_spec()` | Convenience method mirroring `get_tests_for_spec()` |
| Tests | Unit tests for CRUD, search relevance, spec linking |

### Phase 2: Session Harvest Hook (Agent Red)

| Item | Detail |
|------|--------|
| Create `.claude/hooks/session-harvest.py` | Runs at session start, after assertion-check |
| Bridge thread harvester | Extract deliberation from completed review threads |
| Report harvester | Index new CODEX-INSIGHT-DROPBOX reports |
| Owner conversation harvester | Extract decision context from session prompts |
| Deduplication | Skip already-harvested sources (track via source_ref) |

### Phase 3: Backfill + Validation

| Item | Detail |
|------|--------|
| Backfill from CODEX-INSIGHT-DROPBOX | Index existing ~60 insight reports |
| Backfill from bridge history | Index completed review threads with GO/NO-GO outcomes |
| Validate search quality | Test with known queries ("why OTP?", "why Cosmos?", "why append-only?") |
| Codex integration test | Verify Codex can search and write deliberations via bridge |

### Estimated Scope

| Phase | Effort | New Dependencies |
|-------|--------|-----------------|
| Phase 1 | ~150-200 lines Python, ~50 lines SQL, ~200 lines tests | chromadb (optional) |
| Phase 2 | ~100-150 lines Python hook | None (uses existing bridge + KB APIs) |
| Phase 3 | ~50 lines backfill script, manual validation | None |

---

## 5. Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| ChromaDB adds ~50MB to install footprint | Make it optional; SQLite-only mode works without semantic search |
| Deliberation content could contain sensitive info | Same access controls as specs/tests; no external API calls |
| Harvest hook adds session start latency | Bound to 30s max; skip if no new sources since last harvest |
| ChromaDB index diverges from SQLite | Rebuild command: `db.rebuild_deliberation_index()` |
| Over-harvesting creates noise | Source type filtering + outcome field enable focused queries |

---

## 6. Success Criteria

1. `db.search_deliberations("why do we require phone OTP")` returns the SPEC-1879 review thread as the top result
2. `db.get_deliberations_for_spec("SPEC-1879")` returns all review rounds, the proposal, and the owner decision
3. Codex can search deliberations during a review and reference prior patterns
4. Session harvest runs automatically and indexes new deliberation artifacts
5. Backfill captures the ~60 existing Loyal Opposition reports
6. No regression in session start time (harvest completes in <30s)

---

## 7. Codex Review Questions

1. **Schema design:** Does the `deliberations` table schema capture the right fields? Is anything missing that would be needed for cross-project deliberation transfer?
2. **Source types:** Are the 5 source types (lo_review, proposal, owner_conversation, report, session_harvest) sufficient? Should bridge threads be a separate source type?
3. **Search architecture:** Is ChromaDB with default embeddings (all-MiniLM-L6-v2) the right search layer, or should we consider a different embedding model for deliberation text?
4. **Codex integration:** Does the proposed access pattern (same KnowledgeDB API) work for the Loyal Opposition workflow? Are there access patterns Codex needs that aren't covered?
5. **Session harvest scope:** Is the harvest hook harvesting the right artifacts? Is it missing anything? Is it harvesting too much?
6. **Build vs. adopt:** Given the analysis in Section 2, do you concur with the decision to build rather than adopt MemPalace? If not, what specific capabilities would justify the adoption risk?

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
