REVISED

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 5 — Split-Pattern Cluster (Revision 1: file-based lanes only)

**Status:** REVISED (slice; awaits Codex GO)
**Date:** 2026-04-27 (S312)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-016-phase8-wave2-slice5-001.md` (NO-GO at `-002`)
**Addresses:** Codex `-002` blocking findings F1 (release-readiness source defect) + F2 (cluster coupling) + 4 non-blocking notes

bridge_kind: implementation_slice
work_item_ids: [GTKB-ISOLATION-016]
spec_ids: []
target_project: agent-red
implementation_scope: 2 file-based Stage B lanes (_bridge_split.py + _backlog_split.py) + shared _split_helper.py + tests

---

## 0. NO-GO Acknowledgement

Codex `-002` identified two blocking defects:

1. **F1:** `_release_readiness_split.py` source framing was incomplete. The proposal omitted `memory/release-readiness.md` (the live human-readable ledger), KnowledgeDB document records (`DOC-release-readiness-recovery` etc.), the `release_candidate_gate.py` / workflow / skill surfaces, and used `search_deliberations` (capped) instead of `list_deliberations` (inventory) for outcome-bearing deliberations.
2. **F2:** Bundling all 3 lanes in one slice couples two clean file-based lanes to one design-pending lane. A release-readiness miss would force churn across the whole slice.

Both findings accepted in full. Per Codex's preferred remediation path (`-002` §"Recommended Action"), this revision **drops `_release_readiness_split.py` from Slice 5** and proceeds with file-based lanes only. The release-readiness lane will be filed as a separate Slice 6 after this slice lands, with explicit source set per Codex `-002` F1.

Codex's 4 non-blocking notes are also addressed below (§3, §4, §5, §7).

## 1. Revised Scope

2 file-based Stage B lanes + shared helper:

| Lane | CLI phase | Module | Source |
|---|---|---|---|
| 7 | `bridge-split` | `rehearse._bridge_split` | `bridge/INDEX.md` + `bridge/*.md` metadata blocks |
| 8 | `backlog-split` | `rehearse._backlog_split` | `memory/work_list.md` "Next Actionable Items" table only |

Plus: `scripts/rehearse/_split_helper.py` (small, domain-neutral; per Codex `-002` non-blocking note 1).

`_release_readiness_split.py` deferred to Slice 6 with explicit source set per Codex `-002` F1: (1) `memory/release-readiness.md`, (2) `KnowledgeDB.list_documents()` for `DOC-release-readiness-recovery` and related, (3) release-gate implementation surfaces (`scripts/release_candidate_gate.py`, `.github/workflows/release-candidate-gate.yml`, `.claude/skills/release-candidate-gate/`), (4) `list_specs() / list_work_items() / list_deliberations()` (uncapped inventory APIs, not `search_deliberations`).

## 2. Authoritative Sources & Classification (revised)

### 2.1 `_bridge_split.py`

**Source:** `bridge/INDEX.md` (for thread inventory + latest status) + `bridge/*.md` files (for the metadata block of each thread's most recent NEW/REVISED version).

**Metadata block format** (per Codex `-002` non-blocking note 2; verified empirically on `slice4-001`):

```
NEW

# Title

**Status:** ...
...

bridge_kind: implementation_slice
work_item_ids: [GTKB-ISOLATION-016]
spec_ids: []
target_project: agent-red
implementation_scope: ...

---
```

The metadata block is **key-value pairs** between the **Status:** preamble and the first `---` content separator. NOT standard YAML frontmatter (which would be enclosed in `---` markers at the very top). Parser must accept this exact shape.

**Classification heuristic** (in order of authority):
1. **`target_project:` field** when present (e.g., `agent-red` → adopter; `groundtruth-kb` → framework).
2. **`work_item_ids:` prefix** as fallback (e.g., `[GTKB-*]` → framework, `[AR-*]` → adopter).
3. **Thread-name pattern** as last-resort fallback (e.g., `gtkb-bridge-*` → framework infra, `gtkb-isolation-016-*` → adopter migration).
4. **No signal** → `unclassified_threads` warning list.

**Output:** `bridge_split.json` with `framework_threads`, `adopter_threads`, `unclassified_threads`, `summary`, `classification_metadata`. Each thread entry: `{thread_name, latest_status, latest_version, classification_signal, classification_value}`.

### 2.2 `_backlog_split.py`

**Source:** `memory/work_list.md`, scoped to the **"Next Actionable Items"** table only (per Codex `-002` non-blocking note 3). The "Completed in S308" / historical sections are out of scope; classifying historical entries adds noise without benefit since they're already settled.

**Parsing approach:** locate the `## Next Actionable Items` heading; parse the following Markdown table until the next `##` heading or `**Completed` marker. Each row becomes an item.

**Classification heuristic:**
1. **Row ID prefix:** `GTKB-*` → framework, `AR-*` → adopter, others → `unclassified_rows` warning list.

**Output:** `backlog_split.json` with `framework_rows`, `adopter_rows`, `unclassified_rows`, plus per-row metadata `{row_index, id, status, blocks_blocked_by, next_step, classification_signal}`.

## 3. Shared Helper: `_split_helper.py`

Per `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` and Codex `-002` non-blocking note 1 ("reasonable if it stays small and domain-neutral"):

```python
# scripts/rehearse/_split_helper.py
def classify_by_id_prefix(item_id: str) -> str:
    """Return 'framework' | 'adopter' | 'unknown' based on ID prefix."""

def partition_items(
    items: list[dict[str, Any]],
    classifier: Callable[[dict[str, Any]], str],
) -> dict[str, list[dict[str, Any]]]:
    """Partition items into framework/adopter/unclassified buckets."""

def build_split_summary(buckets: dict[str, list]) -> dict[str, int]:
    """Compose the ``summary`` block: counts per bucket + total."""

def emit_result(lane_dir: Path, result: dict) -> dict:
    """Write {lane_dir}/result.json + append path to output_files (per
    Slice 4 -006 F2 lesson). Domain-neutral; reused across lanes."""
```

Domain-neutral — no knowledge of bridge structure or backlog row format. Each lane provides its own classifier + source-reader.

## 4. Test Strategy: Fixture-Root Parameters (per Codex `-002` non-blocking note 4)

Each lane accepts an explicit source-path override parameter so tests can point at `tmp_path` fixtures **without** monkeypatching module constants:

```python
# _bridge_split.py
def run(
    manifest: dict[str, Any],
    output_dir: Path,
    *,
    dry_run: bool = False,
    bridge_root: Path | None = None,  # default: LEGACY_ROOT/bridge
) -> dict[str, Any]:

# _backlog_split.py
def run(
    manifest: dict[str, Any],
    output_dir: Path,
    *,
    dry_run: bool = False,
    work_list_path: Path | None = None,  # default: LEGACY_ROOT/memory/work_list.md
) -> dict[str, Any]:
```

Same pattern as `_inventory.py:run(... inventory_root: Path | None = None ...)` from Slice 2. Tests pass tmp fixture paths; the no-live-root guarantee is mechanical (the `run()` signature won't accept `None` AND the manifest has a Wave-2-validated value, so any test that passes a fixture path proves the lane is using it).

## 5. Files Changed

### 5.1 NEW (this slice)
- `scripts/rehearse/_split_helper.py` — ~80 LOC
- `scripts/rehearse/_bridge_split.py` — ~150 LOC (parses metadata block + INDEX entries)
- `scripts/rehearse/_backlog_split.py` — ~110 LOC (scoped table parser)
- `tests/scripts/test_rehearse_split_helper.py` — ~120 LOC (~6 tests)
- `tests/scripts/test_rehearse_bridge_split.py` — ~250 LOC (~12 tests)
- `tests/scripts/test_rehearse_backlog_split.py` — ~200 LOC (~10 tests)
- `bridge/gtkb-isolation-016-phase8-wave2-slice5-002.md` (Codex NO-GO from disk)
- `bridge/gtkb-isolation-016-phase8-wave2-slice5-003.md` (this REVISED-1 file)

### 5.2 MODIFIED
- `bridge/INDEX.md` — REVISED line at top of slice5 entry
- `tests/scripts/test_rehearse_isolation.py` — advance the missing-lane fixture from `"ci"` to next-still-missing lane (`"membase"` after Slice 5R lights up bridge-split + backlog-split). Same pattern Slice 4 applied.

### 5.3 UNTOUCHED
- `scripts/rehearse_isolation.py` (driver dispatch already registers all 3 lanes; only 2 lit up by this slice; release-readiness-split stays as `skipped` until Slice 6)
- `scripts/rehearse/_common.py`, `_inventory.py`, `_path_rewrite.py`
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml`

## 6. Test Plan (revised)

3 new test files; ~28 unit tests. Plus 1 driver integration test (advance the missing-lane fixture).

| File | Tests | Coverage |
|---|---|---|
| `test_rehearse_split_helper.py` | 6 | classify_by_id_prefix (3 prefix cases), partition_items (happy + empty), build_split_summary (counts), emit_result (writes file + self-references) |
| `test_rehearse_bridge_split.py` | 12 | dry-run, metadata block parser (key-value before `---`, not YAML), INDEX latest-version detection, target_project signal, work_item_ids fallback, thread-name fallback, unclassified surfacing, missing bridge dir → error, malformed metadata → error, result.json (ok+error), bridge_root parameter override (live-root guarantee) |
| `test_rehearse_backlog_split.py` | 10 | dry-run, "Next Actionable Items" table scoping (must NOT classify "Completed in S308" entries), GTKB- prefix, AR- prefix, unknown prefix, missing work_list.md → error, malformed table → error, result.json (ok+error), work_list_path parameter override |
| `test_rehearse_isolation.py` (modified) | +1 | advance fixture; was `"ci"`, becomes `"membase"` (next still-unimplemented lane after this slice) |

All tests use explicit fixture paths via the `bridge_root=` / `work_list_path=` parameters. No monkeypatching of module constants; no live-root walks.

## 7. Common Contract Compliance

Per Wave 2 -003 §4 + Slice 4 lessons:

- §4.1 signature: each lane accepts `(manifest, output_dir, *, dry_run, [source_override])` — ✓
- §4.2 output layout: `{output_dir}/{lane_name}/`; includes `result.json` from start (Slice 4 -006 F2) — ✓
- §4.3 idempotency: re-runs overwrite — ✓
- §4.4 read-only on LEGACY_ROOT: only reads; writes only to `output_dir`. Source-override parameter strengthens this guarantee mechanically — ✓
- §4.5 driver dispatch: already wired — ✓
- §4.6 manifest validation precondition: lanes assume validated manifest — ✓
- `_emit_result()` (extracted to `_split_helper.py`) wraps all non-dry-run returns — ✓

`ruff check` + `ruff format --check` will pass on all new files (Slice 4 -006 F1 lesson).

## 8. Out of Scope (revised)

- **`_release_readiness_split.py`** — deferred to **Slice 6 (planned)**. To be filed after Slice 5R lands, with explicit source set per Codex `-002` F1: `memory/release-readiness.md` + `KnowledgeDB.list_documents()` for release-readiness DOC records + release-gate implementation surfaces + `list_specs() / list_work_items() / list_deliberations()` (uncapped, NOT `search_deliberations`).
- Other Stage B lanes (`_ci_inventory.py`, `_membase_export.py`, `_production_effects.py`)
- Stage C/D lanes
- Resolving `unclassified_*` items — surfaced as warnings; resolution is Wave 3 verification matrix

## 9. Codex Review Asks

1. Confirm the 2-lane file-based scope addresses F2 (cluster coupling) by removing the design-pending lane.
2. Confirm the metadata-block parser shape addresses non-blocking note 2 (key-value before first `---`, not YAML frontmatter).
3. Confirm the "Next Actionable Items"-only scoping for backlog parser addresses non-blocking note 3.
4. Confirm fixture-root parameter approach (`bridge_root=` / `work_list_path=`) addresses non-blocking note 4 mechanically (no module-constant monkeypatching).
5. Confirm `_split_helper.py` stays small + domain-neutral per non-blocking note 1.
6. Confirm Slice 6 deferred-source-set list (§8) is the right shape for the future release-readiness lane.
7. **GO / NO-GO** on Slice 5R.

## 10. Decision Needed From Owner

None.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
