# Risk and Blast Radius — ChromaDB Vector Continuity Backfill

**Investigation run:** 20260528T002632Z
**Bridge thread:** `gtkb-chromadb-vector-continuity-v1-cut-scoping`
**Work item:** WI-3395

## 1. Risk Enumeration

### Risk 1 — Embedding-model version drift

**Description:** The pre-cut ChromaDB was indexed with embedding model M1. If the post-cut ChromaDB is initialized with a different model M2, then HIST-prefixed chunks (which carry M1-vectors) and current chunks (M2-vectors) live in incompatible vector spaces. Semantic similarity scores become unreliable across the HIST/current boundary.

**Mitigation:** The design contract mandates an `--embedding-model-version-pin` parameter that refuses backfill if source and target embedding models differ. Pre-cut and post-cut substrates must use the same embedding model, OR a separate "re-embed-then-backfill" workflow must be designed (out of scope for the initial backfill design; would be a follow-on slice).

**Residual risk:** if the owner decides to ALSO upgrade the embedding model at the v1.0 cut, this design's backfill cannot proceed cleanly. The decision must be sequenced: either (a) backfill BEFORE any model upgrade, or (b) accept that history-mode search has lower-quality embeddings until a separate re-embed migration runs.

**Severity:** P1 if model upgrade is intended; P3 if held constant.

### Risk 2 — `HIST-` prefix collision

**Description:** If a future canonical DELIB ID is named `DELIB-HIST-...` for some unrelated reason, an identifier conflict could emerge.

**Mitigation:** The HIST- prefix attaches to the WHOLE ID (`HIST-DELIB-0003`), not to a component. A future canonical ID `DELIB-HIST-...` would become `HIST-DELIB-HIST-...` under the convention, which is unambiguous. Document this in the canonical-terminology glossary alongside the HIST- prefix entry.

**Residual risk:** if a future operation auto-strips a leading `HIST-` token, it could accidentally turn `HIST-DELIB-0003` into `DELIB-0003`, colliding with the post-cut canonical space. This is an implementation defensiveness concern: the search API should treat `HIST-` as part of the canonical ID, never as a strippable prefix.

**Severity:** P3 with appropriate defensive coding.

### Risk 3 — Storage cost doubling

**Description:** Adding HIST-prefixed copies of every pre-cut chunk approximately doubles the ChromaDB substrate's storage. Current substrate is 136 MB; post-backfill substrate would be roughly 272 MB (a small absolute cost but a noteworthy percentage).

**Mitigation:** Acceptable. 136 MB additional storage is negligible for the data-historical value preserved. The backfill could be marked as "one-time" — no ongoing growth from the HIST- pool except for new pre-cut content added after the cut (which shouldn't happen by definition).

**Residual risk:** future ChromaDB collection additions (if non-deliberation collections appear) would need parallel decisions about HIST- handling. Document the pattern as a precedent.

**Severity:** P3.

### Risk 4 — Derived-index integrity (BM25 / hybrid search)

**Description:** If GT-KB adds any non-vector derived indexes (e.g., BM25 keyword indexes, hybrid search engines) in the future that themselves embed DELIB IDs in their persistence layer, those indexes would need parallel HIST- handling.

**Mitigation:** The backfill contract scopes only to ChromaDB. Future derived indexes should be designed with HIST- awareness from the start. Add to the canonical-terminology glossary that "any GT-KB index storing DELIB IDs must honor the HIST- prefix convention for pre-cut content."

**Residual risk:** unknown future indexes adopt incompatible conventions. The design choice creates a precedent that future indexes should follow.

**Severity:** P3 with proactive canonical-terminology entry.

### Risk 5 — Stash-like reflog object loss (parallel to WI-3394)

**Description:** The broken-blob investigation under WI-3394 found that ChromaDB-adjacent state can suffer git object loss (the lifecycle.py blob in a stash). If `.groundtruth-chroma/` is git-tracked (which it shouldn't be — it's gitignored runtime state per typical convention), the same defect class could appear in the future.

**Mitigation:** `.groundtruth-chroma/` should remain gitignored. The backfill design treats it as runtime substrate, not version-controlled artifact. The backfill script's manifest file (under `.gtkb-state/chromadb-backfill/<run_id>/manifest.json`) IS evidence — that should be tracked (under `.gtkb-state/` per `.claude/rules/project-root-boundary.md`'s sandbox-output exception, OR under `independent-progress-assessments/` per the WI-3394 pattern).

**Residual risk:** if `.groundtruth-chroma/` were ever accidentally added to git tracking, the substrate becomes susceptible to broken-link defects. Periodic verification that `.gitignore` excludes `.groundtruth-chroma/` is appropriate.

**Severity:** P4 (preventable by .gitignore hygiene).

### Risk 6 — Backfill script bug corrupts target substrate

**Description:** A backfill implementation bug could write malformed chunks to the post-cut ChromaDB target (e.g., truncated embeddings, missing metadata, ID collisions with post-cut canonical chunks).

**Mitigation:**
- The backfill script's `--dry-run` mode must be the default; live mode requires explicit `--live` or similar.
- The rollback method must be verified by unit test before any live run.
- Pre-cut substrate is read-only (the source); even a worst-case bug cannot damage the pre-cut data.
- Post-cut substrate at backfill time is empty or freshly-initialized; rollback is trivial.

**Residual risk:** if the backfill runs AFTER significant post-cut content has accumulated, rollback becomes more complex (the rollback method must filter precisely on `backfill_source_run_id`). Sequence the backfill BEFORE significant post-cut work begins.

**Severity:** P2 manageable with sequencing discipline + test coverage.

### Risk 7 — Search-API consumer assumptions break

**Description:** Existing consumers of `search_deliberations` (CLI, proposal_autoload, bridge skill docs) may assume the result set is "current-context only" and not be prepared for HIST- entries appearing.

**Mitigation:**
- Default mode preserves CURRENT-ONLY behavior IF the post-cut decision is "history is opt-in only"; OR
- Default mode mixes HIST + current IF the post-cut decision is "history is part of the default surface."
- Either choice is defensible. The design-contract default (mixed) optimizes for not-forgetting-history; the consumer-compatibility argument favors current-only default.

**Residual risk:** consumer assumptions become a follow-on bridge-thread discussion. Capture this as a candidate requirement to be confirmed before implementation.

**Severity:** P2 — needs owner decision before implementation; not a structural risk.

## 2. Blast-Radius Summary

| Risk | Severity | Mitigation Available | Pre-Implementation Decision Required |
|---|---|---|---|
| Embedding-model drift | P1-P3 | version-pin parameter | Yes — sequence backfill relative to model upgrade |
| HIST- prefix collision | P3 | defensive coding + glossary | No — already mitigated |
| Storage cost doubling | P3 | acceptable | No |
| Derived-index integrity | P3 | future-proof precedent | No (informational) |
| `.groundtruth-chroma/` gitignore | P4 | .gitignore hygiene | No — already in place |
| Backfill bug corrupts target | P2 | dry-run default + sequencing | Yes — sequencing |
| Consumer assumption breakage | P2 | default-mode decision | Yes — owner decision on default |

**Aggregate severity:** the implementation is medium-risk (P2 dominant), addressable with sequencing discipline + dry-run defaults + explicit owner decisions on the default search mode.

## 3. Non-Risks (Affirmative Confirmations)

- **Source substrate integrity:** the backfill reads-only against `.groundtruth-chroma/` and `groundtruth.db`. Worst-case implementation bug cannot damage pre-cut data.
- **Bridge protocol independence:** the backfill is a one-time operation, not a bridge dispatch mechanism. The cross-harness event-driven trigger is unaffected.
- **Session-startup independence:** session-start hooks do not consume ChromaDB directly (per current-state-analysis.md §4); backfill timing relative to session-start is unconstrained.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
