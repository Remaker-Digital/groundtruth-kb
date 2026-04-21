# Implementation Proposal: DA Harvest Coverage Remediation

**Status:** NEW
**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-17
**Parent scope:** `bridge/gtkb-da-harvest-coverage-002.md` (Codex GO with 7 conditions + 5 findings)
**Target repos:** Agent Red (retroactive sweep script, project-local) + `groundtruth-kb` (doctor check, ongoing policy enforcement)

## Scope Confirmed

- **Agent Red project-local:** retroactive sweep script + call-site wiring in `scripts/harvest_session_deliberations.py` (F5 resolution).
- **GT-KB product:** doctor check extension + coverage metric helper + optional CLI subcommand. Propagated to adopter projects via template inheritance.
- **Out of scope:** raw transcript ingestion (per condition 7); any rewrite of existing `lo_review` entries.

## Discharge of Codex Findings

### F1 — Thread-level compression (not file-level)

Current `collect_bridge_threads()` at `scripts/harvest_session_deliberations.py:254-288` produces one DELIB per bridge file. The implementation ships a **new** function `collect_compressed_bridge_threads()` that produces one DELIB per thread.

**Thread-compression algorithm:**

```python
def collect_compressed_bridge_threads(index_path: Path, bridge_dir: Path) -> list[ThreadRecord]:
    """
    Authoritative grouping source is bridge/INDEX.md Document: entries.
    Orphan files (not in active INDEX) grouped by strict prefix + hyphen-delimited segment match.
    """
    # Phase 1: active threads from INDEX
    active_threads = parse_index_document_entries(index_path)  # [(name, [version_files])]
    for name, files in active_threads:
        yield ThreadRecord(
            thread_name=name,
            source_ref=f"bridge/{name}-*.md",
            versions=files,  # preserves INDEX order (latest first)
            active=True,
        )

    # Phase 2: orphan files (on-disk but not in active INDEX)
    all_files = {f for f in bridge_dir.glob("*.md") if f.name != "INDEX.md"}
    indexed_files = {f for _, files in active_threads for f in files}
    orphans = all_files - indexed_files
    orphan_threads = group_orphans_by_strict_prefix(orphans)
    for name, files in orphan_threads:
        yield ThreadRecord(
            thread_name=name,
            source_ref=f"bridge/{name}-*.md",
            versions=sorted(files),
            active=False,
        )
```

**Strict-prefix grouping rule (addresses F2 collision risk):**

Two files belong to the same orphan thread IFF their filenames match pattern `<thread-name>-NNN.md` where `<thread-name>` is the common prefix BEFORE the final `-NNN` segment, AND `<thread-name>` is not itself a prefix of another active-INDEX thread name.

**Collision examples tested (condition 1, ≥3 required):**

1. **Prefix-overlap: `gtkb-start-here-adopter-rewrite` vs `gtkb-start-here-adopter-rewrite-implementation`.** Both are in active INDEX as distinct `Document:` entries, so Phase 1 handles them correctly without any prefix math. For a hypothetical orphan version file `gtkb-start-here-adopter-rewrite-implementation-999.md` that escapes INDEX, the strict-prefix rule correctly groups it with `-implementation-*`, not with the base `-rewrite-*`.
2. **Multi-version depth: `groundtruth-db-migration-001.md` through `-025.md`.** All 25 files share prefix `groundtruth-db-migration` before the `-NNN` segment. The algorithm correctly collapses to one thread.
3. **Cross-project naming: `gtkb-phase-a-metrics-collector` vs `gtkb-phase-a-*` (hypothetical future sibling threads).** If a new `gtkb-phase-a-something` thread appears, orphan grouping after INDEX retirement of either thread must not merge them. Test: create `gtkb-phase-a-x-001.md` and `gtkb-phase-a-y-001.md` → algorithm produces 2 threads, not 1 (the differentiator is the full thread-name-before-`-NNN`, so `gtkb-phase-a-x` ≠ `gtkb-phase-a-y`).
4. **Session-id vs thread-id conflation: `s133-live-test-migration` — this is a filename but also matches session prefix pattern.** Guard: only files in `bridge/` directory are processed; memory topic files with `s<NN>-` prefix are out of scope.

Collision tests land in `tests/test_harvest_thread_compression.py`.

### F2 — INDEX as authoritative active grouping — IMPLEMENTED

Algorithm above uses `parse_index_document_entries(index_path)` as Phase 1. Phase 2 only processes files NOT represented in INDEX. No prefix-only grouping for active threads.

### F3 — `methodology_review` source-type — DECIDED

**Decision: map `methodology_review` to `report`.**

Rationale: `report` is already in GT-KB's supported source-type contract (`src/groundtruth_kb/db.py:4214-4221`). The one existing `methodology_review` row (`DELIB-0712`) will be the only special case; we re-classify it to `report` during retroactive sweep with `source_ref` annotation preserving the original type. No GT-KB validation change. No CLI docs change.

Implementation note in retroactive sweep: emit a LOG line "DELIB-0712 re-typed from methodology_review to report (F3 resolution)".

### F4 — Warning baseline contract — DEFINED

**Two-phase rollout:**

**Phase A (pre-baseline):** retroactive sweep emits warnings for historical artifacts (e.g., unparseable LO verdicts). These warnings are collected but do NOT trigger ALARM. Script exit code 0 if no new insert failures; 1 if new inserts fail; 2 reserved for future use. Warning count is emitted as machine-readable JSON at end of run.

**Phase B (post-baseline):** after retroactive sweep completes and warning baseline is established:
- `scripts/harvest_session_deliberations.py` gains `--baseline-warnings-file <path>` flag.
- Wrap-hook ALARM only on warnings NOT present in baseline, or on non-zero exit.
- Baseline file is git-tracked (`scripts/harvest_warning_baseline.json`) with content-hash per warning for stability.

**Loud-wrap rollout:** flag-gated via `--loud-wrap` until baseline clean. Default: silent. After baseline established (tracked by a date-stamped JSON), flip default to loud.

Machine-readable output:

```json
{
  "exit_status": "ok",
  "new_inserts": 127,
  "skipped_existing": 45,
  "warning_count": 2,
  "warnings_new_vs_baseline": 0,
  "warnings_above_baseline": [],
  "thread_coverage_pct": 94.2
}
```

### F5 — Product vs project script ownership — DECIDED

**Agent Red project-local:**
- `scripts/retroactive_harvest_bridge_threads.py` — one-time sweep, not shipped in GT-KB adopter templates.
- Extension to existing `scripts/harvest_session_deliberations.py` for ongoing thread-level harvest — stays project-local per Agent Red's history-specific baseline.

**GT-KB product:**
- Extension to `gt project doctor` with `_check_da_harvest_coverage()` — checks adopter's DA-vs-INDEX coverage ratio against a configurable threshold (default ≥95%).
- New helper in `src/groundtruth_kb/reporting/` (or existing reporting module) to compute `thread_coverage_pct`.
- Optional CLI subcommand `gt da coverage` for ad-hoc inspection.
- No harvest script shipped in GT-KB — adopters provide their own, consistent with the "harvest script is project-local" pattern already in place.

Rationale: harvest policy varies by project history. Ownership-clarity principle: GT-KB enforces the shape of the output (coverage metric, doctor check); project owns the shape of the input (what to harvest, warning baseline).

## Dry-Run Output Schema (condition 2)

```json
{
  "summary": {
    "candidate_threads": 138,
    "existing_delib_matches": 62,
    "new_inserts_planned": 76,
    "skip_reasons": {
      "empty_thread": 2,
      "redaction_sensitive": 0,
      "content_hash_dupe": 0
    },
    "warning_count": 12,
    "warnings_by_type": {
      "unparseable_verdict": 8,
      "missing_session_id": 4
    },
    "coverage_before_pct": 8.1,
    "coverage_after_pct_projected": 91.6
  },
  "sample_inserts": [
    {
      "thread_name": "groundtruth-db-migration",
      "versions": 25,
      "latest_status": "VERIFIED",
      "summary_preview": "25-version bridge thread covering migration from SQLite-at-tools/knowledge-db/knowledge.db to root groundtruth.db. Final status VERIFIED 2026-03-20. ..."
    },
    {
      "thread_name": "gtkb-docs-memory-architecture-alignment",
      "versions": 4,
      "latest_status": "VERIFIED",
      "summary_preview": "Step-2-only GO; editplan thread continues work. ..."
    },
    {
      "thread_name": "gtkb-azure-enterprise-readiness-taxonomy",
      "versions": 8,
      "latest_status": "VERIFIED",
      "summary_preview": "Azure taxonomy doc + incident + remediation. Final VERIFIED after clean revert of Azure commit 98563fc. ..."
    }
  ]
}
```

Owner reviews the dry-run output before authorizing the live-insert run.

## Source-Ref Convention (condition 3)

All compressed bridge threads use `source_ref = "bridge/{thread-name}-*.md"`. Wildcard is intentional — represents the full version set. `upsert_deliberation_source()` keys on `(source_ref, content_hash)` so the wildcard doesn't cause duplicates; content_hash stability ensures idempotence across re-runs.

Existing 59 `bridge_thread` entries use this convention already (verified in DA schema).

## Doctor Denominator (condition 4)

**Numerator:** count of DELIBs where `source_ref` matches `bridge/<thread-name>-*.md` AND the thread is in active INDEX.

**Denominator:** count of `Document:` entries in active `bridge/INDEX.md` whose latest version status is `VERIFIED`. Scope-GO-only and implementation-GO-only threads are excluded from denominator — they are in-flight and don't yet have complete thread content to harvest.

**Coverage formula:** `thread_coverage_pct = (numerator / denominator) * 100`.

**Thresholds:**
- Default doctor check: WARN if coverage < 95%; ERROR if coverage < 80%.
- Overridable via `.claude/canonical-terminology.toml` or equivalent project config (separate from the canonical-terminology file; TBD if same file or new).

## Idempotence Tests (condition 5)

`tests/test_retroactive_harvest_idempotent.py`:
- Run retroactive script twice back-to-back in a temp-copy of Agent Red's DA.
- Assert: second run produces zero new inserts, zero errors.
- Assert: content_hash of affected rows unchanged between runs.

## Loud-Failure Tests (condition 6)

`tests/test_harvest_loud_failure.py`:
- Simulate harvest script exit code 1 → wrap hook emits ALARM.
- Simulate warning above baseline → wrap hook emits ALARM.
- Simulate warning within baseline → wrap hook does NOT emit ALARM.
- Simulate exit 0 with no warnings → wrap hook emits OK.

## Raw Transcripts Excluded (condition 7)

Explicit assertion in selector logic: `scripts/harvest_session_deliberations.py` does not read `~/.claude/projects/<hash>/*.jsonl` files. Any future work on transcript ingestion is a separate bridge.

## Phase Plan

**Phase 1 — Spec recording.** 7 specs in GT-KB MemBase (from scope bridge inventory).

**Phase 2 — Retroactive script (Agent Red).**
- `scripts/retroactive_harvest_bridge_threads.py` with `--dry-run` default and `--execute` flag.
- Parses current INDEX + enumerates orphan files.
- Uses `upsert_deliberation_source()` from GT-KB for idempotent insert.
- Emits JSON output per schema above.

**Phase 3 — Owner review of dry-run.** Prime runs `--dry-run`, posts summary + 5 sample inserts to owner for verification before live execution.

**Phase 4 — Live retroactive execution.** With owner approval, run `--execute`. Capture JSON output. Post-sweep coverage metric.

**Phase 5 — Ongoing harvest extensions.**
- New thread-level collector in `scripts/harvest_session_deliberations.py`.
- Deprecate file-level collector (flag-gated removal after two sessions of thread-level success).
- Baseline warnings file.

**Phase 6 — GT-KB doctor + helper.**
- `_check_da_harvest_coverage()` in `src/groundtruth_kb/project/doctor.py`.
- Coverage helper in reporting module.
- Tests per conditions 5 and 6.

**Phase 7 — Loud-wrap rollout.** Flag-gated at first; flip default after baseline stable.

**Phase 8 — Post-implementation report.** Evidence: coverage before/after, test pass, doctor output on Agent Red.

## Verification Approach

- Pytest for thread-compression unit tests (4 collision cases).
- Pytest for idempotence test.
- Pytest for loud-failure tests.
- Live retroactive run with dry-run output reviewed by owner.
- Pre-merge: `gt project doctor` on Agent Red reports coverage ≥95% and no harvest-related ERROR flags.
- Post-merge: next session-wrap uses new thread-level harvest; wrap-hook emits machine-readable JSON; wrap reports OK or ALARM based on baseline comparison.

## Timeline

- 2026-04-17 late PM: this bridge filed NEW. Codex review.
- 2026-04-18 AM: on GO, Phase 2–3. Dry-run posted to owner.
- 2026-04-18 PM: owner approves; Phase 4 live execution.
- 2026-04-19: Phases 5–7.
- 2026-04-20: Phase 8 post-impl + Codex VERIFIED.

## Rollback

- Retroactive inserts are append-only; a rollback would be a separate "archive" pass that marks affected rows as superseded. Not needed if dry-run approved.
- GT-KB doctor extension is additive; flag can disable.
- Wrap-hook loud-mode is flag-gated.

## Next Steps After Codex GO

1. Phase 1: spec recording.
2. Phase 2: retroactive script draft.
3. Phase 3: dry-run posted to owner for approval (separate decision gate).
4. Remaining phases per plan.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
