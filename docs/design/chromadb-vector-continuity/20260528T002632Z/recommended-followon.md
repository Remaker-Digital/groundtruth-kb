# Recommended Follow-On — ChromaDB Vector Continuity Implementation Path

**Investigation run:** 20260528T002632Z
**Bridge thread:** `gtkb-chromadb-vector-continuity-v1-cut-scoping`
**Work item:** WI-3395
**Status:** design recommendations; all referenced specs/projects/proposals are CANDIDATES pending owner approval per `GOV-CHAT-DERIVED-SPEC-APPROVAL-001`.

## 1. Owner Decisions Needed Before Implementation

The design contract requires owner decisions on the following questions before any implementation bridge can be filed:

### Decision Q1 — Backfill sequencing relative to v1.0 cut

Three viable orderings:

- **(a) Backfill BEFORE the v1.0 cut**, while pre-cut substrate is still authoritative. Pros: no risk of pre-cut data drift during backfill; backfill runs against the canonical source. Cons: requires the post-cut ChromaDB target to be designed and initialized before the v1.0 cut event.
- **(b) Backfill AT the v1.0 cut event**, as a single atomic operation. Pros: cleanest provenance ("v1.0 cut includes vector continuity by definition"). Cons: ties the cut event to backfill completion, adding cycle time.
- **(c) Backfill AFTER the v1.0 cut**, against a snapshot of the pre-cut substrate. Pros: cut event ships independently. Cons: requires snapshot management; risk of post-cut content appearing in the HIST- pool by accident.

**Recommended:** option (a) — backfill before cut. The pre-cut substrate is stable; the post-cut target can be a fresh ChromaDB collection.

### Decision Q2 — Default search mode

- **(a) HIST + current mixed (current contract default)** — recall is maximized; new sessions see historical context automatically.
- **(b) Current-only by default; HIST opt-in** — minimizes consumer-assumption breakage; protects against accidental over-recall.

**Recommended:** option (a) — mixed default. The DA's reason-of-existence (rationale recall) argues for default availability. Consumers that want current-only have explicit `--scope current` opt-out.

### Decision Q3 — PROJECT-V1-RELEASE-STRATEGY-PREP creation

Per the parent S347 strategy work, a host project for v1.0-prep work would simplify WI grouping. WI-3395 (this scoping), the future implementation WIs, and any sibling v1.0-prep WIs would all belong here.

**Recommended:** create PROJECT-V1-RELEASE-STRATEGY-PREP with WI-3395 as the first member. The standing-authorization model from PROJECT-GTKB-RELIABILITY-FIXES could be reused: a single PAUTH-PROJECT-V1-RELEASE-STRATEGY-PREP-STANDING covers all v1.0-prep work by membership.

### Decision Q4 — Substrate-agnostic vs ChromaDB-specific

Should the design assume ChromaDB indefinitely, or be substrate-agnostic (allowing future migration to a different vector store)?

**Recommended:** substrate-specific (ChromaDB) for now. Substrate-agnostic generality is YAGNI until a second substrate is on the roadmap. Document the substrate-coupling as a design choice in the implementation post-impl report.

### Decision Q5 — Candidate-requirement promotion

The design contract surfaces 5 candidate requirements (`CANDIDATE-SPEC-CHROMADB-VECTOR-CONTINUITY-001` etc.). Should these be promoted to formal SPECs?

**Recommended:** promote all 5 via a single chat-derived spec intake batch. The candidates are tightly coupled; piecemeal promotion would scatter context.

## 2. Recommended Follow-On Bridge Threads

### Thread 1 — Formal Spec Promotion

**Bridge ID candidate:** `gtkb-chromadb-vector-continuity-spec-intake-001`

**bridge_kind:** `spec_intake`

**Scope:** convert the 5 CANDIDATE specs in `design-contract.md` §7 into formal `SPEC-CHROMADB-...` records in MemBase under the chat-derived spec approval workflow. No implementation code yet.

**Sequencing:** after WI-3395 VERIFIED and after owner-decision Q3 (PROJECT-V1-RELEASE-STRATEGY-PREP creation).

### Thread 2 — Backfill Script Implementation

**Bridge ID candidate:** `gtkb-chromadb-backfill-script-slice-1-001`

**bridge_kind:** `implementation_proposal`

**Scope:** implement the backfill script per the contract (with `--dry-run` default, embedding-model-version-pin, idempotent/resumable semantics, manifest output).

**target_paths (proposed):**
- `groundtruth-kb/src/groundtruth_kb/chromadb_backfill.py` (new module)
- `groundtruth-kb/src/groundtruth_kb/cli.py` (extend with `gt deliberations backfill` subcommand)
- `groundtruth-kb/tests/test_chromadb_backfill.py` (new test module)
- `.gtkb-state/chromadb-backfill/` (runtime evidence; gitignored per existing convention)

**Sequencing:** after Thread 1 (formal specs landed).

### Thread 3 — Search-API Scope Modes

**Bridge ID candidate:** `gtkb-deliberations-search-scope-modes-slice-1-001`

**bridge_kind:** `implementation_proposal`

**Scope:** extend `search_deliberations` and the `gt deliberations search` CLI with `scope=default|current|history` parameter; surface `original_id` in result metadata.

**target_paths (proposed):**
- `groundtruth-kb/src/groundtruth_kb/db.py` (extend `search_deliberations`)
- `groundtruth-kb/src/groundtruth_kb/cli.py` (extend `gt deliberations search` command)
- `groundtruth-kb/tests/test_db.py` (extend test coverage)

**Sequencing:** parallelizable with Thread 2; can land before or after backfill script.

### Thread 4 — Backfill Execution

**Bridge ID candidate:** `gtkb-chromadb-vector-continuity-backfill-execution-001`

**bridge_kind:** `implementation_proposal`

**Scope:** execute the backfill script in dry-run, then live, against the v1.0 cut substrates. File a post-impl report with the embedding-count parity check and the representative-query semantic-match check.

**Sequencing:** after Threads 2 and 3 reach VERIFIED.

## 3. Sequencing Diagram

```
[Owner Decisions Q1-Q5 captured]
    ↓
[WI-3395 VERIFIED]  ← this scoping
    ↓
[Thread 1: spec_intake]  ← formal specs land
    ↓
[Thread 2: backfill script]  ←┐
[Thread 3: search-API modes]  ←┴── parallel
    ↓
[Thread 4: backfill execution]
    ↓
[v1.0 Cut Event ready]
```

## 4. Candidate Requirement Wording (Pending Spec Intake)

The following are CANDIDATE requirements only. They MUST be promoted via the chat-derived spec approval workflow before any implementation proposal cites them as governing specs.

**CANDIDATE-SPEC-CHROMADB-VECTOR-CONTINUITY-001 (working title):**
> "Pre-cut ChromaDB deliberation chunks must be preserved across any DELIB-ID reset (e.g., a v1.0 identifier-reset cut) with HIST- prefix on both chunk IDs and `delib_id` metadata. The original (pre-cut) ID must be retrievable from the `original_id` metadata field."

**CANDIDATE-SPEC-CHROMADB-BACKFILL-API-001 (working title):**
> "The backfill script must be idempotent, resumable, dry-run-default, embedding-model-version-pinned, and must not mutate the source substrate."

**CANDIDATE-SPEC-DELIB-SEARCH-MODES-001 (working title):**
> "search_deliberations must support `scope` ∈ {default, current, history} where default returns mixed HIST+current results, current returns post-cut results only, and history returns HIST- results only."

**CANDIDATE-SPEC-DELIB-ORIGINAL-ID-METADATA-001 (working title):**
> "Every HIST-prefixed ChromaDB chunk must carry an `original_id` metadata field containing the pre-cut canonical DELIB ID."

**CANDIDATE-SPEC-EMBEDDING-MODEL-PARITY-001 (working title):**
> "The backfill operation must refuse to proceed if the source ChromaDB embedding model version differs from the target. Embedding-model migration is a separate workflow."

## 5. What Is Explicitly NOT Recommended

- **Skipping the formal spec intake and implementing directly.** The design contract is a starting point, not a substitute for owner-approved specs. Per `GOV-CHAT-DERIVED-SPEC-APPROVAL-001`, candidate requirements remain candidates until owner approval.
- **Substrate-agnostic abstraction in the first slice.** YAGNI applies; ChromaDB-specific implementation simplifies the initial work.
- **Re-embedding pre-cut chunks with a new embedding model.** This would be a separate, larger migration; out of scope for the continuity backfill.
- **Merging this design contract directly into `memory/v1-release-strategy-deliberation-S347.md`.** The S347 doc is a strategic-context artifact; this design contract is implementation-level. Cross-reference via the bridge audit trail rather than text merge.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
