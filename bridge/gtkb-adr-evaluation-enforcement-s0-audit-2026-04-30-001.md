NEW

# Bridge Proposal — GTKB ADR-Evaluation Enforcement S0 (Audit Script)

**Status:** NEW (version 001)
**Author:** Prime Builder (Claude, S324 2026-04-30)
**Document name:** `gtkb-adr-evaluation-enforcement-s0-audit-2026-04-30`
**Parent scoping bridge:** `bridge/gtkb-adr-evaluation-enforcement-2026-04-30-006.md` (Codex GO; clean, no blocking findings)
**Trigger:** Owner direction "Please begin S0 (audit script) sub-bridge" following the parent scoping bridge GO. S0 is the first slice in the ADR-evaluation-enforcement program (S0–S6 per parent bridge §"Program Structure").

**Owner pre-approval:** Yes for the program-level scope per the parent scoping bridge's S324 AskUserQuestion authorization. This implementation bridge requires its own Codex GO before implementation per `.claude/rules/codex-review-gate.md`.

---

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification Linkage Gate:

**Parent program authorization:**
- `bridge/gtkb-adr-evaluation-enforcement-2026-04-30-005.md` (REVISED-2 of the parent scoping bridge) — defines S0 deliverable: "groundtruth-kb/scripts/audit_adr_dcl_metadata.py produces structured report on tags/source_paths/assertions population per ADR/DCL; identifies records needing backfill; recommends concern_tags normalization decision."
- `bridge/gtkb-adr-evaluation-enforcement-2026-04-30-006.md` (Codex GO on the parent) — confirms S0 has no upstream dependencies and is ready to file.

**Governance specs / records that constrain this work:**
- `.claude/rules/codex-review-gate.md` — protocol authority requiring this bridge for the new script + test files
- `.claude/rules/file-bridge-protocol.md` — bridge structure and verdict workflow
- `.claude/rules/project-root-boundary.md` — all changes inside `E:\GT-KB`; specifically under `groundtruth-kb/`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — spec-linkage gate (this proposal complies)
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED gate requires spec-derived test mapping (covered in §Specification-Derived Verification)
- `DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001` — meta-rule that governance constraints must be mechanically enforced; this script is the data layer that future S2 backfill + S3 validator will consume

**Existing pattern references:**
- `groundtruth-kb/scripts/audit_types.py` — existing audit-pattern script in the same directory (parses mypy output, produces categorized markdown report). S0 follows the same shape: read input, categorize, produce structured report.
- `groundtruth-kb/scripts/audit_docstrings.py` — sibling audit script.

**Rule files that constrain this work:**
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/project-root-boundary.md`

---

## Proposed Changes

### Change 1 — `groundtruth-kb/scripts/audit_adr_dcl_metadata.py` (new)

A standalone Python script that reads `groundtruth.db` (canonical KB) and emits a structured audit report on the metadata population state of all ADR and DCL specifications.

**Behavior:**
- Connects to `groundtruth.db` via `sqlite3` (read-only).
- Queries the `specifications` table for the latest version per `id` where `type IN ('architecture_decision', 'design_constraint')`.
- For each row, computes per-field population:
  - `tags`: populated if non-empty JSON list with at least 1 element
  - `source_paths`: populated if non-empty JSON list with at least 1 element
  - `assertions`: populated if non-empty JSON list with at least 1 element
- Computes per-type aggregates (count populated / count missing / coverage percentage).
- For records missing `source_paths`, lists the record IDs (the principal backfill target identified in the parent scoping bridge's audit preview).
- For populated `tags` values, builds a frequency histogram across all values, distinguishing:
  - Theme tags (recurring across many records: `design-constraint`, `mechanical-enforcement`, etc.)
  - Topic tags (specific to a workstream: `smart-poller`, `session-startup`, etc.)
- Emits the recommendation for the S2 `concern_tags` normalization decision based on observed tag distribution: either "use existing tags as concern_tags" (cheap, lossy) or "normalize to a closed concern_tags taxonomy" (expensive, more deterministic).

**CLI surface:**
```
usage: audit_adr_dcl_metadata.py [-h] [--db PATH] [--format {json,markdown}]
                                  [--output PATH] [--frozen-timestamp ISO]

options:
  -h, --help               show this help message and exit
  --db PATH                Path to groundtruth.db. Default: E:\GT-KB\groundtruth.db
  --format {json,markdown} Output format. Default: json
  --output PATH            Write report to file instead of stdout.
  --frozen-timestamp ISO   Freeze the report's "generated_at" timestamp for
                           deterministic test snapshots. Default: now (UTC).
```

**Output schema (JSON; markdown is a structured rendering of the same data):**
```json
{
  "schema_version": 1,
  "generated_at": "2026-04-30T05:30:00Z",
  "db_path": "E:\\GT-KB\\groundtruth.db",
  "totals": {
    "architecture_decision": {"total": 18, "with_tags": 15, "with_source_paths": 4, "with_assertions": 8},
    "design_constraint":     {"total": 31, "with_tags": 28, "with_source_paths": 12, "with_assertions": 24}
  },
  "missing_source_paths": [
    {"id": "ADR-001", "type": "architecture_decision"},
    {"id": "ADR-002", "type": "architecture_decision"},
    ...  // 37-record list per the parent bridge audit preview
  ],
  "tags_histogram": [
    {"tag": "design-constraint", "count": 14, "category": "theme"},
    {"tag": "mechanical-enforcement", "count": 8, "category": "theme"},
    {"tag": "smart-poller", "count": 4, "category": "topic"},
    ...
  ],
  "concern_tags_normalization_recommendation": {
    "decision": "use_existing_tags|normalize_to_taxonomy",
    "rationale": "...",
    "evidence": {"theme_tag_count": ..., "topic_tag_count": ..., "ambiguous_count": ...}
  },
  "records_needing_backfill_count": 37
}
```

**Determinism:** records sorted by `id` ascending; tags histogram sorted by `(category, -count, tag)`; tag categorization uses a documented heuristic (theme tags appear in >= 3 records OR contain explicit theme markers like `design-constraint`, `mechanical-enforcement`, `governance`; topic tags otherwise). This is documented inline in the script.

**Risk:** Low. Pure read of `groundtruth.db`; no DB writes. Read-only access via `sqlite3.connect(db_path, uri=True)` with `mode=ro` query parameter.

### Change 2 — `tests/scripts/test_audit_adr_dcl_metadata.py` (new)

Unit tests covering:
1. **Idempotency:** Running the script twice with the same `--frozen-timestamp` against a fixed test fixture DB produces byte-identical output. Test fixture: a minimal SQLite DB with 3 ADRs + 3 DCLs covering populated/empty cases.
2. **Population computation:** With known fixture data, asserts `totals` counts match expected values for each per-field population (with_tags, with_source_paths, with_assertions).
3. **Missing-source_paths list:** With fixture containing 2 records lacking source_paths, asserts `missing_source_paths` list contains exactly those 2 IDs in sorted order.
4. **Tags histogram + categorization:** With fixture containing tags `["theme-tag", "topic-tag", "theme-tag"]` (theme appears 2x, topic 1x), asserts histogram correctly categorizes per the documented heuristic.
5. **Format snapshot — JSON:** Snapshot test of the JSON output for a fixed fixture state (frozen timestamp).
6. **Format snapshot — markdown:** Snapshot test of the markdown rendering for the same fixture state.
7. **Read-only DB access:** Asserts the script does not write to the DB file (modification time unchanged after run).
8. **CLI: `--output` flag:** Asserts file is written when `--output` is provided.
9. **CLI: missing DB:** Asserts graceful error when `--db` path doesn't exist.

**Test infrastructure:** uses `tmp_path` pytest fixture for isolated DB creation. Test DB seeded via `sqlite3` module directly (no `groundtruth_kb` API dependency for test isolation).

**Risk:** Low. Tests-only file in `tests/scripts/`.

### Change 3 — Sample report (NOT committed; generated for review evidence)

For Codex's review, a sample report against the live `groundtruth.db` will be included in the post-implementation report. Not part of the committed scope.

---

## Specification-Derived Verification

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification-Derived Verification Gate:

**Spec-to-test mapping:**

| Linked spec / driver | Test / verification | Command |
|---|---|---|
| Parent S0 deliverable: "produces structured report on tags/source_paths/assertions population per ADR/DCL" | Tests 2, 3 (population computation + missing-list correctness) | `pytest tests/scripts/test_audit_adr_dcl_metadata.py -k "population or missing" -q` |
| Parent S0 deliverable: "identifies records needing backfill" | Test 3 (missing-source_paths list) | `pytest tests/scripts/test_audit_adr_dcl_metadata.py::test_missing_source_paths_list_correct -q` |
| Parent S0 deliverable: "recommends concern_tags normalization decision" | Test 4 (tags histogram + categorization) | `pytest tests/scripts/test_audit_adr_dcl_metadata.py -k "histogram or categorization" -q` |
| Idempotency check (parent S0 test surface) | Test 1 (idempotency) | `pytest tests/scripts/test_audit_adr_dcl_metadata.py::test_idempotency -q` |
| Report format snapshot (parent S0 test surface) | Tests 5, 6 (JSON + markdown snapshot) | `pytest tests/scripts/test_audit_adr_dcl_metadata.py -k "snapshot" -q` |
| Read-only DB safety | Test 7 (DB mtime unchanged) | `pytest tests/scripts/test_audit_adr_dcl_metadata.py::test_read_only_db_access -q` |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This proposal's Specification Links section + bridge-compliance-gate hook approval | bridge-compliance-gate hook check on this proposal Write (already passed) |
| Project root boundary | All edited paths inside `E:\GT-KB`/`groundtruth-kb/` | manual verification, see §Project Root Boundary Compliance |
| Code quality (ruff) | ruff clean on the new script + test file | `python -m ruff check groundtruth-kb/scripts/audit_adr_dcl_metadata.py tests/scripts/test_audit_adr_dcl_metadata.py` |

**Execution commands (planned for post-impl report):**
```bash
python -m ruff check groundtruth-kb/scripts/audit_adr_dcl_metadata.py tests/scripts/test_audit_adr_dcl_metadata.py
pytest tests/scripts/test_audit_adr_dcl_metadata.py -q
python groundtruth-kb/scripts/audit_adr_dcl_metadata.py --format markdown
python groundtruth-kb/scripts/audit_adr_dcl_metadata.py --format json --output /tmp/audit-sample.json
```

The release-gate command (`python scripts/release_candidate_gate.py --skip-frontend`) is NOT part of S0's verification surface because the release-gate has known infrastructure issues per the parent bridge's S6 prerequisite (timeout + suite duration mismatch). S0 does not depend on the release-gate; per-test verification via `pytest` is sufficient for this slice.

---

## Project Root Boundary Compliance

Per `.claude/rules/project-root-boundary.md` Mandatory Project Root Boundary Gate:

- All edited files inside `E:\GT-KB`:
  - `groundtruth-kb/scripts/audit_adr_dcl_metadata.py` (new)
  - `tests/scripts/test_audit_adr_dcl_metadata.py` (new)
- All cited specifications inside `E:\GT-KB` or `groundtruth.db` at the project root.
- All read targets are inside `E:\GT-KB`:
  - `groundtruth.db` (read-only)
- No external paths referenced.

---

## Pre-GO Drift Disposition

Clean fresh implementation. No source-code edits exist in the worktree for this slice. All implementation will be authored after Codex GO per the standard codex-review-gate flow.

---

## Implementation Sequence (planned for after Codex GO)

1. Author `groundtruth-kb/scripts/audit_adr_dcl_metadata.py` per the CLI + output schema specified above.
2. Author `tests/scripts/test_audit_adr_dcl_metadata.py` with the 9 test cases listed in Change 2.
3. Run `python -m ruff check` on both files — expect clean.
4. Run `pytest tests/scripts/test_audit_adr_dcl_metadata.py` — expect 9 passed.
5. Generate a sample report against the live `groundtruth.db` for the post-implementation report's evidence section: `python groundtruth-kb/scripts/audit_adr_dcl_metadata.py --format markdown` (markdown for human review).
6. Stage `groundtruth-kb/scripts/audit_adr_dcl_metadata.py` + `tests/scripts/test_audit_adr_dcl_metadata.py` (no other files).
7. Commit with scoped message referencing this bridge thread.
8. File post-impl report; include the sample report from step 5 as evidence.

---

## Rollback Notes

If post-impl reveals an unexpected issue:
- Revert the single commit via `git revert <sha>` — covers 2 files (script + test).
- The bridge thread itself is append-only audit history.

The risk surface is small (read-only script; tests-only fixture). A clean revert restores the prior state with no migration needed.

---

## Decision Needed From Owner

This implementation bridge does not require an owner decision. Standard Codex GO/NO-GO flow applies.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
