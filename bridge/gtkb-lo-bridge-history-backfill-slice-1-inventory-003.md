REVISED
author_identity: Codex
author_harness_id: A
author_session_context_id: 019e425a-79e8-7351-80bc-38c73b0b9429
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop default reasoning

# Implementation Proposal - LO Bridge History Backfill Slice 1 Inventory

bridge_kind: prime_proposal
Version: 003 (REVISED after NO-GO at -002)
Author: Prime Builder (Codex harness A)
Date: 2026-05-20 UTC
Source: WI-3162 (Backfill existing LO reports and bridge history)
Recommended commit type: feat
target_paths: ["scripts/inventory_lo_bridge_history_backfill.py", "platform_tests/scripts/test_inventory_lo_bridge_history_backfill.py", "bridge/gtkb-lo-bridge-history-backfill-slice-1-inventory-*.md", ".gtkb-state/lo-bridge-history-backfill/inventory-manifest.json", ".gtkb-state/lo-bridge-history-backfill/inventory-summary.md"]

## Summary

WI-3162 requires backfilling historical Loyal Opposition reports and bridge thread histories into the Deliberation Archive (DA). Slice 1 is now strictly an inventory-only slice. It creates an inventory script, tests, a deterministic JSON manifest, and a human-readable summary under `.gtkb-state/lo-bridge-history-backfill/`.

Slice 1 does not write `groundtruth.db`, does not insert Deliberation Archive rows, does not mutate MemBase/work_items/specifications, and does not perform any harvest/backfill mutation. The later harvest or audit-row work remains a separate Slice 2 proposal after the owner and Loyal Opposition can inspect the inventory output.

## Revision History

- **003 (REVISED)** - Addresses the Loyal Opposition NO-GO at `bridge/gtkb-lo-bridge-history-backfill-slice-1-inventory-002.md`.
  - F1: Chose the strict inventory-only scope. All DA `session_harvest` row insertion, `--apply`, and `groundtruth.db` mutation language was removed from Slice 1.
  - F2: Defined manifest determinism precisely. `inventory-manifest.json` is byte-identical for fixed inputs; volatile `generated_at` and run clock evidence live only in `inventory-summary.md`.
  - F3: Changed recommended commit type from `docs` to `feat` because the slice adds a script and tests.
  - Corrected the test target path to the established GT-KB platform lane: `platform_tests/scripts/test_inventory_lo_bridge_history_backfill.py`.
- **001 (NEW)** - Initial inventory/backfill proposal.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - file bridge as live workflow authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - mandatory specification linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - mandatory spec-derived tests.
- `GOV-STANDING-BACKLOG-001` - standing backlog governance and WI-3162 selection authority.
- `SPEC-DA-HARVEST-INCLUSION` - DA harvest inclusion criteria used for inventory classification.
- `SPEC-DA-HARVEST-EXCLUSION` - DA harvest exclusion criteria used for inventory classification.
- `SPEC-DA-RETROACTIVE-SWEEP` - retroactive back-harvest idempotence; this slice inventories eligible/idempotent candidates without mutating DA.
- `SPEC-DA-THREAD-COMPRESSION` - one DELIB per bridge thread in compressed wildcard form; inventory must recognize compressed coverage.
- `SPEC-DA-COVERAGE-METRIC` - DA bridge-thread coverage metric; manifest supplies per-file evidence.
- `SPEC-DA-MECHANICAL-ENFORCE` - harvest failure must be loud; this slice keeps mutation disabled and observable.
- `SPEC-DA-DOCTOR-CHECK` - doctor's bridge-thread coverage check informs the coverage summary.
- `SPEC-2098` - Deliberation Archive feature spec and parent of WI-3162.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - root-boundary discipline; all outputs stay under `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - inventory is a durable artifact with traceable evidence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - concrete backlog/coverage findings are preserved as artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - inventory output is a lifecycle input for later Slice 2 decisions.
- `.claude/rules/deliberation-protocol.md` - DA harvest protocol reference.
- `.claude/rules/file-bridge-protocol.md` - bridge protocol form and lifecycle.
- `.claude/rules/codex-review-gate.md` - Loyal Opposition review gate.
- `.claude/rules/project-root-boundary.md` - all generated outputs stay in-root.

## Prior Deliberations

- `DELIB-1868` - preceding DA harvest catchup work that established the harvest infrastructure now used as reference context.
- `DELIB-1917` - isolation citation backfill verified under modern bridge discipline; precedent for slice-based inventory before mutation.
- `DELIB-1916` and `DELIB-1627` - backlog cleanup inventory-first precedent: Phase 1 inventory only, later phases perform mutation.
- `DELIB-1896` - DA read-surface correction/glossary backfill, a DA-adjacent backfill thread with multiple NO-GO rounds before verification.
- `DCL-RETROACTIVE-LINKAGE-OBLIGATION-001` and `DCL-RETROACTIVE-TRIAD-COMPLETENESS-001` - historical triad/linkage gaps require visibility before mutation.

No prior deliberation rejects an inventory-first slice. The revision adopts the safest scope from the NO-GO: produce evidence only, then propose mutation separately.

## Owner Decisions / Input

Owner direction from 2026-05-14 S350 authorized batch NEW filing of priority backlog proposals. Per-proposal Loyal Opposition GO remains required before implementation. No new owner input is required for this revision because the NO-GO offered a safe strict-inventory option and this proposal adopts it.

## Scope Boundary

In scope for Slice 1:

- Add `scripts/inventory_lo_bridge_history_backfill.py`.
- Add `platform_tests/scripts/test_inventory_lo_bridge_history_backfill.py`.
- Generate `.gtkb-state/lo-bridge-history-backfill/inventory-manifest.json`.
- Generate `.gtkb-state/lo-bridge-history-backfill/inventory-summary.md`.
- File the post-implementation bridge report.

Out of scope for Slice 1:

- Any `groundtruth.db` write.
- Any Deliberation Archive insert/update/upsert, including `session_harvest` rows.
- Any MemBase `work_items` mutation.
- Any spec promotion/retirement.
- Any actual backfill/harvest mutation.
- Any formal artifact approval packet.

All outputs are in-root under `E:\GT-KB`: the script under `E:\GT-KB\scripts\`, tests under `E:\GT-KB\platform_tests\scripts\`, inventory evidence under `E:\GT-KB\.gtkb-state\lo-bridge-history-backfill\`, and bridge files under `E:\GT-KB\bridge\`.

## Inventory Methodology

The inventory script enumerates two file classes and emits one row per file.

**Class A: Loyal Opposition reports.** Glob `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-*.md`. The existing harvest excludes files smaller than 100 bytes; the inventory reproduces that exclusion. Other LO-dropbox files are recorded separately in an `other_lo_dropbox` summary bucket for visibility, but they are not Class A harvest candidates.

**Class B: Bridge files.** Glob `bridge/*.md`, excluding `INDEX.md` and `README.md`. For each file, classify against the live `bridge/INDEX.md` and against current Deliberation Archive source references.

**Classification rules:**

1. `already_harvested` - a current deliberation source reference matches the exact path, or a compressed wildcard `bridge/{thread-stem}-*.md` covers that bridge file's thread per `SPEC-DA-THREAD-COMPRESSION`.
2. `excluded_per_spec` - the file matches an existing exclusion rule such as `size_under_100_bytes`, redaction-survivor/credential-safety exclusion, or thread-level compressed coverage that supersedes file-level harvest.
3. `eligible_for_harvest` - the file is neither already covered nor excluded. Slice 2 may propose mutation for this set after review.

If an exact-path DA row exists but its stored content hash differs from the current file hash, the file is classified as `eligible_for_harvest` with reason `content_drift_since_harvest`.

## Output Shape

`inventory-manifest.json` is byte-stable for fixed inputs. It contains deterministic sorted JSON with:

- `_meta`: `schema_version`, `gt_repo_root`, `da_snapshot_counts`, `script_sha256`, `on_disk_counts`.
- `records`: one object per file with `path`, `thread_stem`, `file_class`, `size_bytes`, `sha256`, `classification`, `classification_reason`, `current_da_row_id`, `current_da_content_hash`, and `index_status`.

The manifest intentionally excludes volatile `generated_at` and filesystem `mtime`. `inventory-summary.md` may include `generated_at`, command line, and human-readable run context because it is an explanatory report, not the byte-identical idempotence artifact.

## Implementation Plan

1. Add `scripts/inventory_lo_bridge_history_backfill.py`.
   - Enumerate Class A and Class B files.
   - Read DA source references using read-only SQLite queries against `groundtruth.db`.
   - Reuse or mirror existing harvest redaction/exclusion helpers where practical.
   - Classify each file per the methodology.
   - Write the deterministic manifest and summary under `.gtkb-state/lo-bridge-history-backfill/`.
   - Provide a no-mutation CLI surface only; no `--apply` mode exists in Slice 1.
2. Add `platform_tests/scripts/test_inventory_lo_bridge_history_backfill.py`.
3. Run the inventory command against the live checkout.
4. File a post-implementation report with manifest counts and verification output.

## Test Mapping

| Test | Specification(s) covered |
|------|---------------------------|
| `test_classification_already_harvested_exact_path` | `SPEC-DA-HARVEST-INCLUSION`, `SPEC-DA-RETROACTIVE-SWEEP` |
| `test_classification_already_harvested_compressed_wildcard` | `SPEC-DA-THREAD-COMPRESSION`, `SPEC-DA-RETROACTIVE-SWEEP` |
| `test_classification_content_drift_reclassified_eligible` | `SPEC-DA-RETROACTIVE-SWEEP` |
| `test_exclusion_size_under_100_bytes` | `SPEC-DA-HARVEST-EXCLUSION` |
| `test_exclusion_redaction_survivor` | `SPEC-DA-HARVEST-EXCLUSION`, `GOV-FILE-BRIDGE-AUTHORITY-001` |
| `test_eligible_classification_default` | `SPEC-DA-HARVEST-INCLUSION` |
| `test_inventory_manifest_schema_complete` | `SPEC-DA-COVERAGE-METRIC` |
| `test_manifest_byte_stable_for_fixed_inputs` | `SPEC-DA-RETROACTIVE-SWEEP` |
| `test_manifest_excludes_generated_at_and_mtime` | `SPEC-DA-RETROACTIVE-SWEEP` |
| `test_summary_records_generated_at_outside_manifest` | `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` |
| `test_orphan_bridge_thread_recorded` | `GOV-FILE-BRIDGE-AUTHORITY-001` |
| `test_inventory_does_not_write_deliberation_archive` | `SPEC-DA-MECHANICAL-ENFORCE` |

Tests use sandbox bridge/LO-report fixtures and a temporary SQLite DA replica. They must not mutate the real `groundtruth.db`.

## Acceptance Criteria

1. The script enumerates all bridge files (excluding `INDEX.md`, `README.md`) and all `INSIGHTS-*.md` LO reports with size >= 100 bytes.
2. Each file is classified exactly once into `already_harvested`, `excluded_per_spec`, or `eligible_for_harvest` with a recorded reason.
3. `inventory-manifest.json` is byte-identical for fixed DA snapshot and on-disk content.
4. The manifest excludes volatile `generated_at` and filesystem `mtime`.
5. `inventory-summary.md` reports counts by class and classification, top exclusion reasons, and orphan bridge thread stems.
6. The script performs no `groundtruth.db` writes and creates no DA rows.
7. The spec-derived test lane passes.
8. Mandatory preflight gates pass.

## Verification Plan

1. `python -m pytest platform_tests/scripts/test_inventory_lo_bridge_history_backfill.py -q --tb=short` - all tests pass.
2. `python scripts/inventory_lo_bridge_history_backfill.py --output-dir .gtkb-state/lo-bridge-history-backfill/` - produces manifest and summary only.
3. Run the inventory command twice against fixed sandbox inputs in tests; manifest bytes match.
4. Query `groundtruth.db` before and after the live inventory run for source refs under `.gtkb-state/lo-bridge-history-backfill/`; row count remains unchanged.
5. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-lo-bridge-history-backfill-slice-1-inventory` - `preflight_passed: true`.
6. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-lo-bridge-history-backfill-slice-1-inventory` - exit 0.

## NO-GO Resolution

- F1 resolved by adopting strict inventory scope and removing all Slice 1 DA-write behavior.
- F2 resolved by defining byte-identical determinism over `inventory-manifest.json` only and excluding volatile fields from that artifact.
- F3 resolved by changing recommended commit type to `feat`.

End of revised proposal.
