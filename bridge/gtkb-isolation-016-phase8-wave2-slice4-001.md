NEW

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 4 — `_path_rewrite.py` Implementation

**Status:** NEW (slice; awaits Codex GO)
**Date:** 2026-04-27 (S312)
**Author:** Prime Builder (Claude Opus 4.7)
**Builds on:**
- `bridge/gtkb-isolation-016-phase8-wave2-implementation-004.md` (Wave 2 GO; umbrella)
- `bridge/gtkb-isolation-016-phase8-wave2-slice3-006.md` (Slice 3 VERIFIED; driver wired up)

bridge_kind: implementation_slice
work_item_ids: [GTKB-ISOLATION-016]
spec_ids: []
target_project: agent-red
implementation_scope: scripts/rehearse/_path_rewrite.py + tests; driver dispatch already wired

---

## Prior Deliberations

- `DELIB-0877`: nine-phase GT-KB/application separation program (origin of the isolation work).
- `DELIB-0878`: Phase 1 authority matrix plan — defines the classification source (`gt project classify-tree`) that this lane consumes.
- `DELIB-0879`: Phase 2 root and repository topology plan — sibling planning record.
- `DELIB-0023`: Loyal Opposition repo-boundary assessment (early framing).

No prior bridge thread proposed `_path_rewrite.py`; this is the first slice that lights it up. The umbrella (`gtkb-isolation-016-phase8-wave2-implementation-004`) GO'd Wave 2 lanes 2-11 implementation in any order after Slice 3.

## 1. Scope

Single Stage B leaf lane (`scripts/rehearse/_path_rewrite.py`). Computes the path-rewrite mapping from current paths → `applications/Agent_Red/<path>` for adopter-owned content. Produces the git-filter-repo argument list referenced by the manifest's `git_filter_command_template` placeholder `<agent-red-paths-from-_path_rewrite>`.

Does NOT modify the driver (`scripts/rehearse_isolation.py`), `_common.py`, `_inventory.py`, the manifest, or any existing tests. Strictly additive.

## 2. Authoritative Source

`gt project classify-tree`, invoked as `python -m groundtruth_kb.cli project classify-tree --dir <legacy_root> --max-depth <N> --format json --output <path>`.

Output JSON schema (verified empirically against `groundtruth-kb` v0.6.1):

```json
{
  "generated": "ISO timestamp",
  "gt_kb_version": "0.6.1",
  "gt_kb_head": "...",
  "target_tree": "E:\\GT-KB",
  "target_head": "...",
  "total_paths_classified": 6335,
  "owner_decision_pending_rows": 3,
  "rows": [
    {
      "path": "src/foo.py",
      "ownership": "adopter-owned" | "gt-kb-managed" | "gt-kb-scaffolded" | "shared-structured" | "legacy-exception",
      "upgrade_policy": "...",
      "adopter_divergence_policy": "...",
      "notes": "...",
      "owner_decision_pending": false,
      "record_id": "..."
    }
  ]
}
```

Per Slice 2 -003 F3 reframing: `_path_rewrite.py` consumes operational data from this source, NOT from the runtime manifest's `surface_treatments` table (which is audit metadata only).

## 3. Algorithm

1. **Subprocess invoke** `python -m groundtruth_kb.cli project classify-tree --dir <LEGACY_ROOT> --max-depth 10 --format json --output <output_dir>/path_rewrite/classification.json` (max-depth 10 matches CLI default; no `--ignore-glob` in v1).
2. **Read** classification.json from disk.
3. **Partition rows** by `ownership` and `owner_decision_pending`:
   - `owner_decision_pending == true` → `unresolved_paths` (regardless of ownership; surface as warning, do not auto-rewrite)
   - `ownership == "adopter-owned"` → emit `{source: path, target: f"applications/Agent_Red/{path}", record_id, ownership}` to `rewrites`
   - `ownership in {"gt-kb-managed", "gt-kb-scaffolded"}` → emit to `keep_at_root` (these stay at GT-KB root post-isolation)
   - `ownership == "shared-structured"` → emit to `shared_paths` (no rewrite; ownership remains shared post-isolation per the matrix plan)
   - `ownership == "legacy-exception"` → emit to `legacy_exceptions` warning list (explicit unresolved adoption debt; surface for owner decision)
   - any other ownership value → emit to `warnings` ("unknown ownership label X for path Y") and skip the row
4. **Compose git-filter-repo arguments**: for each `rewrites` entry, emit one line: `--path <source> --path-rename <source>:<target>`.
5. **Write outputs** (under `{output_dir}/path_rewrite/`):
   - `path_rewrite.json` — main artifact (schema in §5)
   - `git_filter_args.txt` — one line per rewrite, ready for git filter-repo
   - `result.json` — standard sub-script result per Wave 2 -003 §4.1
6. **Return result dict** with status `ok` (lane completed; warnings may be present for unresolved/legacy rows) or `error` (classify-tree subprocess failed, classification JSON malformed, or output writes failed).

## 4. Output Layout

```
{output_dir}/path_rewrite/
├── classification.json      # raw classify-tree output (operator-traceable evidence)
├── path_rewrite.json        # main artifact: rewrites + skipped + warnings
├── git_filter_args.txt      # composed --path / --path-rename arguments
└── result.json              # standard sub-script result dict
```

## 5. `path_rewrite.json` Schema

```json
{
  "schema_version": 1,
  "generated_at": "2026-04-27T01:50:00Z",
  "source_root": "E:/GT-KB",
  "target_namespace": "applications/Agent_Red",
  "classification_source": "{output_dir}/path_rewrite/classification.json",
  "classification_metadata": {
    "gt_kb_version": "0.6.1",
    "gt_kb_head": "3b5a527",
    "target_head": "391316a1",
    "total_paths_classified": 6335
  },
  "summary": {
    "rewrites_count": 3619,
    "keep_at_root_count": 13,
    "shared_paths_count": 1047,
    "legacy_exceptions_count": 3,
    "unresolved_count": 3,
    "unknown_ownership_count": 0,
    "total_classified": 6335
  },
  "rewrites": [
    {"source": "src/foo.py", "target": "applications/Agent_Red/src/foo.py", "record_id": "...", "ownership": "adopter-owned"}
  ],
  "keep_at_root": [
    {"path": ".claude/hooks/assertion-check.py", "ownership": "gt-kb-managed", "record_id": "hook.assertion-check"}
  ],
  "shared_paths": [
    {"path": "...", "ownership": "shared-structured", "record_id": "..."}
  ],
  "legacy_exceptions": [
    {"path": "groundtruth.db", "ownership": "legacy-exception", "record_id": "...", "notes": "..."}
  ],
  "unresolved_paths": [
    {"path": "...", "owner_decision_pending": true, "ownership": "...", "notes": "..."}
  ]
}
```

## 6. `git_filter_args.txt` Shape

One rewrite per line. Newline-terminated.

```
--path src/foo.py --path-rename src/foo.py:applications/Agent_Red/src/foo.py
--path src/bar.py --path-rename src/bar.py:applications/Agent_Red/src/bar.py
...
```

This file content can be concatenated and fed to `git filter-repo` directly when Phase 9 (productization) implements the cutover. Slice 4 only generates the arguments; it does NOT execute git filter-repo.

## 7. Common Contract Compliance

Per Wave 2 -003 §4 contracts (still binding):

- §4.1 signature: `def run(manifest: dict, output_dir: Path, *, dry_run: bool = False) -> dict` — ✓
- §4.2 output layout: `{output_dir}/path_rewrite/` — ✓
- §4.3 idempotency: re-runs with same `output_dir` overwrite (timestamps in summary indicate the latest) — ✓
- §4.4 read-only on LEGACY_ROOT: lane only writes under `output_dir`; classify-tree itself is documented READ-ONLY by the GT-KB CLI; output_dir validation already enforced upstream by driver — ✓
- §4.5 driver dispatch wire-up: already registered as `("rewrite", "rehearse._path_rewrite", "run")` in `DISPATCH_TABLE` line 49 of `scripts/rehearse_isolation.py` — ✓
- §4.6 manifest validation precondition: lane assumes manifest passed `load_manifest(wave=2)` validation (driver enforces) — ✓

## 8. Test Plan

`tests/scripts/test_rehearse_path_rewrite.py` (new file). 13 unit tests + 1 driver integration test.

### 8.1 Subprocess mocking strategy

All tests `monkeypatch` `subprocess.run` to return synthetic classification JSON written to the specified `--output` path. Tests do NOT invoke the real classify-tree (which would walk LEGACY_ROOT — slow + brittle in CI). The driver-level integration test (Test 14) also uses the mock.

### 8.2 Test list

| # | Test | Coverage |
|---|---|---|
| 1 | `test_run_dry_run_returns_skipped` | Per common contract; no subprocess called |
| 2 | `test_run_invokes_classify_tree_subprocess` | Verifies subprocess call shape (args contain `--dir`, `--format json`, `--output`) |
| 3 | `test_run_produces_rewrites_for_adopter_owned` | Happy path: 1 adopter-owned row → 1 rewrite entry |
| 4 | `test_run_skips_gt_kb_managed_in_rewrites` | gt-kb-managed → keep_at_root, NOT rewrites |
| 5 | `test_run_emits_shared_structured_to_shared_paths` | shared-structured → shared_paths |
| 6 | `test_run_emits_legacy_exception_to_warnings` | legacy-exception → legacy_exceptions list + warning string |
| 7 | `test_run_emits_unresolved_paths_when_pending` | owner_decision_pending=true → unresolved_paths regardless of ownership |
| 8 | `test_run_writes_path_rewrite_json` | Main artifact written; schema_version=1; summary counts correct |
| 9 | `test_run_writes_git_filter_args_file` | One line per rewrite; format `--path X --path-rename X:Y\n` |
| 10 | `test_run_target_path_format_correct` | `src/foo.py` → `applications/Agent_Red/src/foo.py` (forward slashes) |
| 11 | `test_run_returns_error_when_classify_tree_fails` | Mocked non-zero exit → status='error', no artifact files written beyond classification.json (or none) |
| 12 | `test_run_returns_error_when_classification_malformed` | Mocked invalid JSON → status='error' |
| 13 | `test_run_unknown_ownership_emits_warning` | Synthetic row with ownership="future-label" → warnings list + skip |
| 14 | `test_driver_dispatches_path_rewrite_lane_with_module_now_present` | Calls `_dispatch("rewrite", ...)` and asserts status != 'skipped' (lane is now implemented) |

Test 14 belongs in `tests/scripts/test_rehearse_isolation.py` (driver test file) since it exercises the dispatcher. The other 13 belong in the new `test_rehearse_path_rewrite.py`.

### 8.3 Test fixtures

- `_synth_classification(rows)` helper: composes the classification JSON shape with given rows; written by mocked subprocess to specified output path
- `tmp_path` for `output_dir` (pytest fixture; resolves under `C:/temp/...` on Windows or `/tmp/...` on Linux — both match the M2 sandbox allowlist patterns added in Slice 1)

### 8.4 Performance expectation

13 unit tests with mocked subprocess: < 2 seconds combined. Combined run with all rehearse tests (92 + 13 = 105) should remain under 1 second since the new tests don't walk filesystem.

## 9. Files Changed (this slice's commit)

### 9.1 NEW
- `scripts/rehearse/_path_rewrite.py` — ~150 LOC
- `tests/scripts/test_rehearse_path_rewrite.py` — ~280 LOC (13 tests + helpers)
- `bridge/gtkb-isolation-016-phase8-wave2-slice4-001.md` (this file)

### 9.2 MODIFIED
- `bridge/INDEX.md` — new "Document: gtkb-isolation-016-phase8-wave2-slice4" entry inserted at top
- `tests/scripts/test_rehearse_isolation.py` — append 1 new test (Test 14 above) for driver-level integration

### 9.3 UNTOUCHED
- `scripts/rehearse_isolation.py` (driver dispatch already registers this lane)
- `scripts/rehearse/_common.py`
- `scripts/rehearse/_inventory.py`
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml`
- All 92 existing rehearse tests

## 10. Out of Scope

- Actually invoking classify-tree against the live root (mocked in tests; only operator-driven `--execute` runs it for real)
- Running git filter-repo (Phase 9 cutover, not Phase 8 rehearsal)
- Resolving `unresolved_paths` / `legacy_exceptions` (Wave 3 verification matrix surfaces these for owner decision)
- Other Stage B lanes (`_ci_inventory.py`, `_membase_export.py`, `_bridge_split.py`, `_backlog_split.py`, `_release_readiness_split.py`, `_production_effects.py` — separate slices)
- Stage C lanes (`_chromadb_regen.py`, `_dashboard_regen.py`)
- Stage D lane (`_rollback.py`)

## 11. Codex Review Asks

1. Confirm subprocess invocation (`python -m groundtruth_kb.cli project classify-tree`) is the right mechanism vs direct Python import of `groundtruth_kb` internals. Subprocess decouples from GT-KB private API surface and matches the "external authoritative source" pattern; direct import would tighten coupling but be faster. Either is implementable.
2. Confirm `path_rewrite.json` schema partitions (rewrites / keep_at_root / shared_paths / legacy_exceptions / unresolved_paths) cover all five `ownership` values plus the `owner_decision_pending` orthogonal flag.
3. Confirm the read of `target_namespace = "applications/Agent_Red"` from a hard-coded constant (matches manifest `target_root`) is acceptable, or whether the lane should derive it from `manifest["target_root"]` minus `manifest["legacy_root"]` to avoid string drift.
4. Confirm test mocking of subprocess is acceptable; integration test against real classify-tree deferred to Wave 3 verification matrix.
5. Confirm `legacy-exception` and `unresolved_paths` get warning treatment (status remains `ok`) rather than `error` status. Rationale: lane succeeded at classifying; the classifications themselves contain unresolved entries that the operator/owner must address before cutover. Slice's job is to surface, not to gate.
6. Confirm the `--max-depth 10` value matches the classify-tree default and is sufficient for full Agent Red tree coverage. (Empirical: 6335 rows at depth 2 already exceed total file count, suggesting depth flag interacts with the classifier in a non-tree-walk way — but verifying this is Codex review territory.)
7. **GO / NO-GO** on Slice 4 scope.

## 12. Decision Needed From Owner

None — owner pre-approval per `memory/work_list.md` row 2 + umbrella `-004` GO covers Wave 2 lane implementation in dependency-correct order.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
