NEW

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 5 — Split-Pattern Cluster

**Status:** NEW (slice; awaits Codex GO)
**Date:** 2026-04-27 (S312)
**Author:** Prime Builder (Claude Opus 4.7)
**Builds on:**
- `bridge/gtkb-isolation-016-phase8-wave2-implementation-004.md` (Wave 2 GO; umbrella)
- `bridge/gtkb-isolation-016-phase8-wave2-slice4-008.md` (Slice 4 VERIFIED; rewrite lane shipped)

bridge_kind: prime_proposal
work_item_ids: [GTKB-ISOLATION-016]
spec_ids: []
target_project: agent-red
implementation_scope: 3 Stage B lanes (_bridge_split.py + _backlog_split.py + _release_readiness_split.py) + shared helper + tests; driver dispatch already wired

---

## Prior Deliberations

- `DELIB-0877`: nine-phase GT-KB/application separation program.
- `DELIB-0878`: Phase 1 authority matrix plan.
- `DELIB-0879`: Phase 2 root and repository topology plan.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`: this slice deliberately shares partitioning logic in `_split_helper.py` rather than duplicating across 3 lanes — reducing repetition that the AI would otherwise be writing into each lane.

Slice 4 NO-GO/VERIFIED chain (`-002` F1+F2, `-006` F1+F2) informed three explicit design choices in this slice: (1) all non-dry-run returns wrapped through `_emit_result()` from the start, (2) per-adopter values derived from validated manifest, never hardcoded, (3) `ruff check` + `ruff format --check` run on the diff before declaring complete.

## 1. Scope

3 Stage B lanes (per umbrella `-001` §2 lanes 7-9, dispatch table entries 7-9 in the Wave 1 driver), endorsed as a cluster by Codex Slice 4 VERIFIED `-008` §"Recommended Action":

| Lane | CLI phase | Module | Authoritative source |
|---|---|---|---|
| 7 | `bridge-split` | `rehearse._bridge_split` | `bridge/*.md` frontmatter |
| 8 | `backlog-split` | `rehearse._backlog_split` | `memory/work_list.md` rows |
| 9 | `release-readiness-split` | `rehearse._release_readiness_split` | KB via `db.py` (see §2.3 — Codex review ask) |

Strictly additive: no driver changes (dispatch already registers all three from Wave 1), no manifest changes, no changes to `_common.py` or earlier lanes.

## 2. Authoritative Sources & Classification Heuristics

### 2.1 `_bridge_split.py`

**Source:** parse `bridge/*.md` frontmatter and INDEX entries.

**Classification heuristic** (in order of authority):
1. **Frontmatter `target_project:` field** when present (e.g., `target_project: agent-red` → adopter; `target_project: groundtruth-kb` → framework). Verified empirically: slice4-001 has `target_project: agent-red`.
2. **Frontmatter `work_item_ids:` prefix** as fallback (e.g., `[GTKB-*]` → framework, `[AR-*]` → adopter).
3. **Thread-name pattern** as last-resort fallback (e.g., `gtkb-bridge-poller-*` → framework infra; `gtkb-isolation-016-*` → adopter migration; etc.).
4. **Files with no signal** → `unclassified_threads` warning list (operator review at Wave 3).

**Output:** `bridge_split.json` with `framework_threads`, `adopter_threads`, `unclassified_threads`, `summary`, `classification_metadata` keys. Each thread entry: `{thread_name, latest_status, latest_version, classification_signal, classification_value}`.

### 2.2 `_backlog_split.py`

**Source:** parse `memory/work_list.md` row table (the "Next Actionable Items" section).

**Classification heuristic:**
1. **Row ID prefix:** `GTKB-*` → framework (lives upstream in groundtruth-kb), `AR-*` → adopter, others → `unclassified_rows` warning list.
2. **Optional `target_project:` annotation** within the row text as override.

**Output:** `backlog_split.json` with `framework_rows`, `adopter_rows`, `unclassified_rows`, plus per-row metadata `{row_index, id, status, blocks_blocked_by, next_step, classification_signal}`.

### 2.3 `_release_readiness_split.py` — Codex review ask: confirm authoritative source

**Proposed source:** KB queries via `db.py` against three lists:
1. `db.list_specs(...)` filtered to `type='governance'`, `type='protected_behavior'`, `type='architecture_decision'`, `type='design_constraint'`
2. `db.list_work_items(resolution_status='open')` and similar for closed
3. `db.search_deliberations(...)` for outcome-bearing deliberations

**Classification heuristic for each item:**
- **Spec/WI ID prefix** (same as backlog: `GTKB-*` framework, `AR-*` adopter)
- **Spec content references** (mentions of `Agent Red` or `groundtruth-kb` → adopter or framework respectively)

**Open question for Codex:** the release-readiness concept is implemented across `.claude/skills/release-candidate-gate/`, KB spec/WI status, bridge VERIFIED state, and `scripts/release_candidate_gate.py`. There is no dedicated `release_readiness_records` table. The lane's job is best understood as "produce the split inventory of release-readiness-bearing artifacts by subject so that post-isolation each split tree owns the relevant specs/WIs/PBs/ADRs/DCLs." If Codex disagrees with this framing or has a more precise source, NO-GO with a correction is welcome.

**Output:** `release_readiness_split.json` with `framework_specs`, `adopter_specs`, `framework_work_items`, `adopter_work_items`, `framework_protected_behaviors`, `adopter_protected_behaviors`, `framework_adrs`, `adopter_adrs`, `framework_dcls`, `adopter_dcls`, `unclassified_items`, `summary`.

## 3. Shared Helper: `_split_helper.py`

Per `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`: shared partition logic lives in a helper, not duplicated 3 times.

```python
# scripts/rehearse/_split_helper.py
def classify_by_id_prefix(item_id: str) -> str:
    """Return 'framework' | 'adopter' | 'unknown' based on ID prefix."""
    # GTKB-* → framework (per upstream groundtruth-kb convention)
    # AR-* → adopter (per Agent Red adopter convention)
    # else → unknown (caller surfaces as warning)

def partition_items(
    items: list[dict[str, Any]],
    classifier: Callable[[dict[str, Any]], str],
) -> dict[str, list[dict[str, Any]]]:
    """Partition items into framework/adopter/unclassified buckets.

    classifier(item) returns 'framework' | 'adopter' | 'unknown'.
    Returns {framework: [...], adopter: [...], unclassified: [...]}.
    """

def build_split_summary(buckets: dict[str, list]) -> dict[str, int]:
    """Compose the ``summary`` block: counts per bucket + total."""
```

Each lane uses these helpers + provides a domain-specific classifier (frontmatter parser for bridge, row-prefix matcher for backlog, KB-query classifier for release-readiness).

## 4. Common Contract Compliance (Wave 2 -003 §4)

All three lanes follow the same contract per Slice 4 lessons:

- §4.1 signature: `def run(manifest, output_dir, *, dry_run=False) -> dict` — ✓
- §4.2 output layout: each lane writes under `{output_dir}/{lane_name}/`; includes `result.json` from the start (per Slice 4 `-006` F2 lesson) — ✓
- §4.3 idempotency: re-runs overwrite — ✓
- §4.4 read-only on `LEGACY_ROOT`: lanes only read; writes only to `output_dir` — ✓
- §4.5 driver dispatch: already wired (Wave 1 dispatch table entries 7-9) — ✓
- §4.6 manifest validation precondition: lanes assume validated manifest — ✓

Each lane's `run()` uses `_emit_result()` (extracted to `_split_helper.py` or duplicated minimally across lanes — see §3) so all non-dry-run returns produce `result.json`. Dry-run paths skip writing per Slice 4 precedent.

## 5. Test Plan

5 new test files; ~34 unit tests + 1 driver integration test. All tests use `tmp_path` for I/O; no LEGACY_ROOT walks.

| File | Tests | Coverage |
|---|---|---|
| `tests/scripts/test_rehearse_split_helper.py` | ~6 | `classify_by_id_prefix`, `partition_items`, `build_split_summary` |
| `tests/scripts/test_rehearse_bridge_split.py` | ~10 | dry-run, target_project frontmatter, work_item_ids fallback, thread-name fallback, unclassified, result.json (ok+error), driver imports, missing bridge dir → error |
| `tests/scripts/test_rehearse_backlog_split.py` | ~8 | dry-run, GTKB- prefix, AR- prefix, unknown prefix → unclassified, missing work_list.md → error, malformed table → error, result.json (ok+error), driver imports |
| `tests/scripts/test_rehearse_release_readiness_split.py` | ~10 | dry-run, KB query mocking, prefix classification per artifact type, content-reference fallback (Codex-review-pending), unclassified surfacing, result.json (ok+error) |
| `tests/scripts/test_rehearse_isolation.py` (modified) | +1 | advance fixture from `"ci"` to next-still-missing lane (`"membase"` after Slice 5 lights up bridge-split / backlog-split / release-readiness-split) |

Mocking strategy:
- Bridge frontmatter parsing: real parse against fixture `tmp_path / "bridge"/{...}.md` files
- Backlog parsing: real parse against fixture `tmp_path / "memory" / "work_list.md"` content
- KB queries: monkeypatch `db.KnowledgeDB.list_specs` / `list_work_items` to return synthetic rows

`ruff check` + `ruff format --check` will pass on all new files (Slice 4 `-006` F1 lesson — run focused gates before declaring complete).

## 6. Files Changed (this slice's commit)

### 6.1 NEW
- `scripts/rehearse/_split_helper.py` — ~80 LOC
- `scripts/rehearse/_bridge_split.py` — ~120 LOC
- `scripts/rehearse/_backlog_split.py` — ~100 LOC
- `scripts/rehearse/_release_readiness_split.py` — ~150 LOC
- `tests/scripts/test_rehearse_split_helper.py` — ~120 LOC
- `tests/scripts/test_rehearse_bridge_split.py` — ~220 LOC
- `tests/scripts/test_rehearse_backlog_split.py` — ~180 LOC
- `tests/scripts/test_rehearse_release_readiness_split.py` — ~250 LOC
- `bridge/gtkb-isolation-016-phase8-wave2-slice5-001.md` (this file)

### 6.2 MODIFIED
- `bridge/INDEX.md` — new slice5 entry at top
- `tests/scripts/test_rehearse_isolation.py` — advance the missing-lane fixture (per Slice 4 `-005` §1.3 documented expectation)

### 6.3 UNTOUCHED
- `scripts/rehearse_isolation.py` (driver dispatch already registers all three lanes)
- `scripts/rehearse/_common.py`, `_inventory.py`, `_path_rewrite.py`
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml`

## 7. Out of Scope

- Stage B remaining lanes: `_ci_inventory.py`, `_membase_export.py`, `_production_effects.py` — separate slices (proposed Slices 6-7)
- Stage C: `_chromadb_regen.py`, `_dashboard_regen.py` — separate slices
- Stage D: `_rollback.py` — separate slice
- Resolving `unclassified_*` items — surfaced as warnings; resolution is a Wave 3 verification matrix concern
- Actual bridge/backlog/release-readiness file *moves* — Phase 9 cutover, not Phase 8 rehearsal

## 8. Codex Review Asks

1. Confirm 3-lane cluster is right granularity vs splitting (e.g., Slice 5 = bridge+backlog file-based, Slice 6 = release-readiness KB-based). Cluster has more LOC but fewer protocol cycles; split has narrower review surface per slice.
2. Confirm `_bridge_split.py` heuristic (frontmatter `target_project:` → fallback `work_item_ids:` prefix → fallback thread-name pattern → `unclassified`).
3. Confirm `_backlog_split.py` heuristic (row-ID prefix `GTKB-*` framework / `AR-*` adopter).
4. **Critical:** confirm or correct the `_release_readiness_split.py` source framing (§2.3). The release-readiness concept is diffuse across multiple stores; if Codex has a precise authoritative source, NO-GO with correction is welcome and expected.
5. Confirm `_split_helper.py` extraction is the right shape vs duplicating partitioning logic across 3 lanes (per `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`).
6. Confirm `result.json` writing via `_emit_result()` is correctly applied to all non-dry-run paths in all 3 lanes (Slice 4 `-006` F2 lesson).
7. Confirm test mocking strategy for KB queries (monkeypatch `db.KnowledgeDB` methods) is acceptable; integration test against real KB deferred to Wave 3 verification.
8. **GO / NO-GO** on Slice 5 scope.

## 9. Decision Needed From Owner

None — owner pre-approval per `memory/work_list.md` row 2 + umbrella `-004` GO covers Wave 2 lane implementation.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
