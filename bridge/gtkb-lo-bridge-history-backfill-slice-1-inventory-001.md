Status: NEW
Author: prime-builder (claude harness B)
Date: 2026-05-14
Session: S350
Source: WI-3162 (Backfill existing LO reports and bridge history)
Recommended commit type: docs
target_paths: ["scripts/inventory_lo_bridge_history_backfill.py", "tests/scripts/test_inventory_lo_bridge_history_backfill.py", "bridge/gtkb-lo-bridge-history-backfill-slice-1-inventory-*.md", ".gtkb-state/lo-bridge-history-backfill/inventory-manifest.json", ".gtkb-state/lo-bridge-history-backfill/inventory-summary.md"]

## Summary

WI-3162 (priority P2, project `GTKB-LO-REPORT-BACKFILL`, source spec `SPEC-2098`) requires backfilling historical Loyal Opposition reports and bridge thread histories into the Deliberation Archive (DA). The corpus is large: 3,218 bridge files and 829 LO reports on disk (size >= 100 B). Live DA snapshot at proposal time records 716 `lo_review` rows (712 unique source_refs) and 1,316 `bridge_thread` rows (1,086 unique source_refs, of which 357 are compressed wildcard `bridge/...-*.md` entries). A naive exact-path comparison shows 119 LO files and 2,490 bridge files without a same-path DA row, but many of the bridge files are subsumed by compressed-thread wildcard entries and many of the older files may be intentionally excluded per `SPEC-DA-HARVEST-EXCLUSION` (size threshold, redaction-survivor failure, content-hash idempotence, etc.).

This slice produces an **inventory manifest only**. It enumerates every on-disk historical file, classifies each by `eligible_for_harvest` / `already_harvested` / `excluded_per_spec` (with the precise exclusion reason), and writes a single JSON manifest plus a human-readable markdown summary under `.gtkb-state/lo-bridge-history-backfill/`. It records a single DA row of `source_type='session_harvest'` capturing the inventory-completion fact. **No backfill mutation occurs in Slice 1.** The actual harvest of unharvested-but-eligible files is a separate proposal (Slice 2) authored after owner reviews the manifest.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 — file bridge as live workflow authority
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — mandatory specification linkage
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — mandatory spec-derived tests
- GOV-STANDING-BACKLOG-001 — standing backlog governance (WI-3162 selection authority)
- SPEC-DA-HARVEST-INCLUSION — DA harvest inclusion criteria
- SPEC-DA-HARVEST-EXCLUSION — DA harvest exclusion criteria
- SPEC-DA-RETROACTIVE-SWEEP — retroactive back-harvest idempotence
- SPEC-DA-THREAD-COMPRESSION — one DELIB per bridge thread (compressed wildcard form)
- SPEC-DA-COVERAGE-METRIC — DA bridge-thread coverage metric
- SPEC-DA-MECHANICAL-ENFORCE — session-wrap fails LOUD on harvest failure
- SPEC-DA-DOCTOR-CHECK — doctor's bridge-thread coverage check
- SPEC-2098 — Deliberation Archive feature spec (parent of WI-3162)
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — applications/* placement convention (project-root boundary)
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — artifact-oriented governance (inventory IS an artifact)
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — artifact-as-record-of-decision
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — artifact lifecycle triggers
- GOV-ARTIFACT-APPROVAL-001 — formal artifact approval (informational; no MemBase mutation in this slice)
- `.claude/rules/deliberation-protocol.md` — harvest protocol (when to archive)
- `.claude/rules/file-bridge-protocol.md` — bridge protocol (this proposal's form)
- `.claude/rules/codex-review-gate.md` — Loyal Opposition review gate
- `.claude/rules/project-root-boundary.md` — root-boundary discipline (manifest output stays in-root)

## Prior Deliberations

- DELIB-1868 (Bridge thread `gtkb-da-harvest-catchup`, 4 versions, GO) — preceding catchup work that established the harvest infrastructure currently in `scripts/harvest_session_deliberations.py` and `scripts/retroactive_harvest_bridge_threads.py`. This proposal extends the inventory side of that pattern; the actual harvest engine already exists.
- DELIB-1917 (Bridge thread `gtkb-isolation-017-citation-backfill`, 6 versions, VERIFIED) — exemplar of a backfill thread that landed under modern bridge discipline (slice-based, inventory-first, owner-approved).
- DELIB-1916 (Bridge thread `gtkb-codex-backlog-cleanup-retroactive-review`, 6 versions, VERIFIED) and DELIB-1627 (Loyal Opposition Review — Codex Backlog Cleanup Phase 1 Inventory) — direct precedent for the inventory-first pattern this slice adopts: Phase 1 was inventory-only, Phase 2+ was mutation.
- DELIB-1896 (Bridge thread `gtkb-da-read-surface-correction-phase-1-glossary-backfill`, 10 versions, VERIFIED) — another DA-adjacent backfill thread; underwent multiple NO-GO rounds before VERIFIED, evidence that backfill scoping is non-trivial.
- DCL-RETROACTIVE-LINKAGE-OBLIGATION-001 — past approved/verified implementations without spec linkage must receive retroactive coverage. This slice's inventory makes that gap visible without yet mutating.
- DCL-RETROACTIVE-TRIAD-COMPLETENESS-001 — historical approvals require complete spec/test/implementation triads. Inventory surfaces which files contribute to the triad gap.
- DELIB-S321-TRIAD-COMPLETENESS — S321 owner directive on triad completeness; inventory is the visibility precondition.

## Owner Decisions / Input

Owner direction 2026-05-14 S350: "Please parallelize work and start as many priority backlog projects as possible" + "Please continue filing more backlog work" authorizes batch NEW filing of priority backlog proposals. Per-proposal Codex GO required before implementation. Channel: AskUserQuestion (DECISION-0583 — AUQ-resolved batch authorization).

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is NOT a bulk-mutation operation against MemBase, the standing backlog, or any other governed record set. Although the bridge proposal text references the standing backlog (`GOV-STANDING-BACKLOG-001`) for selection authority (WI-3162) and references work items, specifications, and deliberations in the inventory methodology, the operative deliverable is a SINGLE `inventory` manifest file plus a SINGLE markdown summary plus a SINGLE DA `session_harvest` record marking the inventory complete. No MemBase work_items rows are inserted, updated, retired, or reordered. No specifications are promoted or retired. No deliberations are inserted other than the single inventory-completion record (and that record is itself an audit artifact governed by the existing harvest scripts, not a new formal-artifact-approval class). The downstream Slice 2 backfill mutation — which IS a bulk operation against the DA — is a separate proposal that requires its own owner approval and its own Codex review GO. The `formal-artifact-approval` packet workflow per `GOV-ARTIFACT-APPROVAL-001` does NOT apply to this slice because no canonical artifact (GOV / ADR / DCL / PB / SPEC / narrative-artifact) is created or modified. Tokens for clause-preflight scope evidence: `inventory`, `formal-artifact-approval`.

## Requirement Sufficiency

Existing requirements sufficient. The applicable specifications (SPEC-DA-HARVEST-INCLUSION, SPEC-DA-HARVEST-EXCLUSION, SPEC-DA-RETROACTIVE-SWEEP, SPEC-DA-THREAD-COMPRESSION, SPEC-DA-COVERAGE-METRIC, SPEC-DA-MECHANICAL-ENFORCE, SPEC-DA-DOCTOR-CHECK, SPEC-2098, GOV-STANDING-BACKLOG-001, and the bridge-protocol governance set) collectively constrain inclusion/exclusion criteria and the audit-trail requirement. No new specification capture is required for this slice; if Slice 2 reveals classification ambiguity not covered by the existing exclusion specs, that slice's proposal will surface the gap as a candidate SPEC update.

## Inventory Methodology

The inventory script enumerates two file classes and emits one row per file.

**Class A: Loyal Opposition reports.** Glob `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-*.md`. Per `collect_lo_reports()` in `scripts/harvest_session_deliberations.py`, the existing harvest excludes files smaller than 100 bytes; the inventory MUST reproduce that exclusion verbatim. Other LO-dropbox files (advisories, runbooks, methodology reviews) are excluded from Class A but recorded in a separate `other_lo_dropbox` category for owner visibility.

**Class B: Bridge files.** Glob `bridge/*.md`, excluding `INDEX.md` and `README.md`. For each file, classify against the active `bridge/INDEX.md` via `parse_bridge_index()` (per `scripts/harvest_session_deliberations.py`):
- Files whose thread has `VERIFIED` or `GO` or `NO-GO` status receive the same outcome encoding the existing harvest applies.
- Files whose thread is not in `bridge/INDEX.md` (orphans) are tagged `orphan` with the thread stem recorded.

**Classification rules (per file):**

1. `already_harvested` — a current `deliberations` row exists where `source_ref` matches one of:
   - exact path (`bridge/{filename}` or `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/{filename}`); OR
   - compressed wildcard `bridge/{thread-stem}-*.md` for that file's thread (per `SPEC-DA-THREAD-COMPRESSION`).
   The check uses content-hash comparison against the current DA row when an exact-path match exists; if the on-disk hash differs from the harvested hash, the file is reclassified as `eligible_for_harvest` with reason `content_drift_since_harvest`.

2. `excluded_per_spec` — the file matches one of the existing harvest exclusion criteria:
   - `size_under_100_bytes` (per `collect_lo_reports()` and `collect_bridge_threads()` short-circuit).
   - `ar_key_survivor` (per `_AR_KEY_SURVIVOR_RE` in `harvest_session_deliberations.py`; runs the same redaction simulation as the live harvest).
   - `not_index_resolvable_and_thread_compressed` (a bridge file whose thread is already represented by a `bridge/{thread-stem}-*.md` compressed DA row).
   Each exclusion records the offending spec ID (or short rule name when the spec ID is implicit in the script).

3. `eligible_for_harvest` — file fails neither `already_harvested` nor `excluded_per_spec`. Slice 2 will harvest these.

**Output shape.** Two files written to `.gtkb-state/lo-bridge-history-backfill/`:

- `inventory-manifest.json` — JSON array, one record per file: `{ path, thread_stem, file_class, size_bytes, sha256, classification, classification_reason, current_da_row_id, current_da_content_hash, mtime, index_status }`. Plus a `_meta` block: `{ generated_at, gt_repo_root, da_snapshot_counts, script_sha256, on_disk_counts }`.
- `inventory-summary.md` — human-readable summary: counts by class and classification, top exclusion reasons, sample 10 rows from each classification bucket, list of orphan bridge thread stems.

A single DA row is inserted of `source_type='session_harvest'` with `source_ref='.gtkb-state/lo-bridge-history-backfill/inventory-manifest.json'`, recording the inventory-completion fact (manifest content hash + generated_at + WI-3162 reference). The existing `harvest_session_deliberations.py` upsert API handles the DA write under content-hash idempotence per `SPEC-DA-RETROACTIVE-SWEEP`.

## Implementation Plan

1. Add `scripts/inventory_lo_bridge_history_backfill.py`:
   - Imports `parse_bridge_index`, `_AR_KEY_SURVIVOR_RE`, `_simulate_redaction`, `extract_thread_stem` from existing harvest scripts (via `importlib` per the established `_load_retroactive_module` pattern).
   - Enumerates Class A and Class B files.
   - Classifies each per the rules above.
   - Writes `inventory-manifest.json` and `inventory-summary.md` under `.gtkb-state/lo-bridge-history-backfill/`.
   - Inserts the single `session_harvest` DA row.
   - Supports `--dry-run` (default, no DA mutation, manifest still written) and `--apply` (writes DA row).
   - Read-only against `groundtruth.db` in dry-run mode (uses `sqlite3.connect(...).execute('SELECT ...')` for the DA-row presence checks).
2. Add `tests/scripts/test_inventory_lo_bridge_history_backfill.py` exercising the test mapping below.
3. Run the inventory in dry-run mode and attach `inventory-summary.md` to the post-implementation report.
4. On Codex GO, run in `--apply` mode and commit manifest, summary, and DA row.

The script is governed by `ADR-ISOLATION-APPLICATION-PLACEMENT-001`: all outputs stay within `E:\GT-KB`; `.gtkb-state/` is the canonical runtime evidence directory.

## Test Mapping

Tests are derived from the linked specifications. All tests live in `tests/scripts/test_inventory_lo_bridge_history_backfill.py`.

| Test | Specification(s) covered |
|------|---------------------------|
| `test_classification_already_harvested_exact_path` | SPEC-DA-HARVEST-INCLUSION, SPEC-DA-RETROACTIVE-SWEEP |
| `test_classification_already_harvested_compressed_wildcard` | SPEC-DA-THREAD-COMPRESSION, SPEC-DA-RETROACTIVE-SWEEP |
| `test_classification_content_drift_reclassified_eligible` | SPEC-DA-RETROACTIVE-SWEEP (content-hash idempotence) |
| `test_exclusion_size_under_100_bytes` | SPEC-DA-HARVEST-EXCLUSION |
| `test_exclusion_ar_key_survivor` | SPEC-DA-HARVEST-EXCLUSION, GOV-FILE-BRIDGE-AUTHORITY-001 (credential safety) |
| `test_exclusion_thread_compressed_supersedes_file_level` | SPEC-DA-THREAD-COMPRESSION |
| `test_eligible_classification_default` | SPEC-DA-HARVEST-INCLUSION |
| `test_inventory_manifest_schema_complete` | SPEC-DA-COVERAGE-METRIC (per-file evidence) |
| `test_inventory_deterministic_for_same_inputs` | SPEC-DA-RETROACTIVE-SWEEP (idempotence) |
| `test_orphan_bridge_thread_recorded` | GOV-FILE-BRIDGE-AUTHORITY-001 (full audit trail) |
| `test_dry_run_writes_no_da_row` | SPEC-DA-MECHANICAL-ENFORCE (no silent mutation) |
| `test_apply_inserts_single_session_harvest_row` | SPEC-DA-MECHANICAL-ENFORCE, SPEC-DA-HARVEST-INCLUSION |

Tests run via `python -m pytest tests/scripts/test_inventory_lo_bridge_history_backfill.py -v`. Fixtures use a sandbox `bridge/` and `independent-progress-assessments/` plus an in-memory `sqlite3` DA replica to avoid mutating the real `groundtruth.db` during tests.

## Risk and Rollback

**Risks:**

1. Classification regression against existing harvest semantics. Mitigated by importing shared logic from `harvest_session_deliberations.py` and `retroactive_harvest_bridge_threads.py` (not re-implementing).
2. DA row pollution (a wrong-shape `session_harvest` row would appear in future searches). Mitigated by dry-run-default + Codex review of the manifest before `--apply`.
3. Manifest file growth (~3,000 file rows). Mitigated by JSON-array shape and `.gtkb-state/` placement (runtime evidence, not canonical state).

**Rollback:**

- Inventory artifacts are evidence-only; deletion is safe. `rm .gtkb-state/lo-bridge-history-backfill/inventory-manifest.json` plus `rm .gtkb-state/lo-bridge-history-backfill/inventory-summary.md` reverts the file system.
- The single DA `session_harvest` row is append-only; rollback uses the standard DA supersede pattern via a follow-up bridge with explicit owner approval.

## Acceptance Criteria

1. `scripts/inventory_lo_bridge_history_backfill.py` enumerates all bridge files (excluding `INDEX.md`, `README.md`) and all `INSIGHTS-*.md` LO reports >= 100 B.
2. Each file is classified exactly once into `already_harvested`, `excluded_per_spec`, or `eligible_for_harvest` with a recorded `classification_reason`.
3. `inventory-manifest.json` is deterministic for fixed inputs (same DA snapshot + same on-disk content => byte-identical manifest after sorting).
4. `inventory-summary.md` reports counts by class, top 5 exclusion reasons, and the orphan thread list.
5. A single `session_harvest` DA row is inserted under `--apply` referencing the manifest by content hash and citing WI-3162 in `change_reason`.
6. The full test suite in `tests/scripts/test_inventory_lo_bridge_history_backfill.py` passes (12 tests).
7. Mandatory preflight gates pass: applicability preflight `preflight_passed: true`; clause preflight exit 0.

## Verification Plan

Spec-derived verification carried into the post-implementation report:

1. `python -m pytest tests/scripts/test_inventory_lo_bridge_history_backfill.py -v` — all 12 tests PASS.
2. `python scripts/inventory_lo_bridge_history_backfill.py --dry-run --output-dir .gtkb-state/lo-bridge-history-backfill/` — produces manifest + summary; no DA mutation.
3. `python scripts/inventory_lo_bridge_history_backfill.py --apply --output-dir .gtkb-state/lo-bridge-history-backfill/` — manifest + summary + single DA row.
4. `sqlite3 groundtruth.db "SELECT source_type, source_ref, change_reason FROM current_deliberations WHERE source_ref LIKE '.gtkb-state/lo-bridge-history-backfill/%';"` — exactly one row, citing WI-3162.
5. Re-run `--apply`; content-hash idempotence => zero new rows (per `SPEC-DA-RETROACTIVE-SWEEP`).
6. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-lo-bridge-history-backfill-slice-1-inventory` — `preflight_passed: true`.
7. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-lo-bridge-history-backfill-slice-1-inventory` — exit 0.

## Applicability Preflight

- packet_hash: `sha256:22138d41bf0f6b6ed26d19e26724088450ace1ee8ad11ec32a557decbfd885f9`
- bridge_document_name: `gtkb-lo-bridge-history-backfill-slice-1-inventory`
- content_source: `pending_content`
- content_file: `bridge/gtkb-lo-bridge-history-backfill-slice-1-inventory-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited |
|------|----------|-------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | yes |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | yes |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | yes |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | yes |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | yes |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | yes |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | yes |

Clause preflight (`scripts/adr_dcl_clause_preflight.py`) returned exit 0, all 5 must_apply clauses had evidence found: `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`, `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING`, `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`. Blocking gaps: 0.

End of proposal.
