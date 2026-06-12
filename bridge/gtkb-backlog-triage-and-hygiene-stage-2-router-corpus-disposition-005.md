NEW
author_identity: claude
author_harness_id: B
author_session_context_id: 28d30cb5-bfc4-4a97-acca-57d36d002533
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: 1m
author_metadata_source: prime-builder session; bridge-author-metadata/current.json

# Implementation Report - Stage 2 Router-Corpus Disposition (WI-4456)

bridge_kind: implementation_report
Document: gtkb-backlog-triage-and-hygiene-stage-2-router-corpus-disposition
Version: 005
Date: 2026-06-11 UTC
Responds to: bridge/gtkb-backlog-triage-and-hygiene-stage-2-router-corpus-disposition-004.md (GO)

Project: PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001
Work Item: WI-4456
Project Authorization: PAUTH-PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001-BACKLOG-TRIAGE-AND-HYGIENE-BOUNDED-IMPLEMENTATION-AUTHORIZATION

target_paths: ["scripts/hygiene/router_corpus_dispose.py", "platform_tests/scripts/test_router_corpus_dispose.py"]

## Summary

The GO'd Stage 2 proposal (`-003`, GO at `-004`) is implemented within the declared target paths: a deterministic, read-only-by-default disposition tool plus its pytest suite. No `groundtruth.db` mutation occurred during implementation; the `--apply` mutation path is deferred to per-batch owner AskUserQuestion approval (each ≤ 50 ids, with an explicit approved-id batch file + deterministic batch hash), exactly as the GO'd proposal specifies. `groundtruth.db` is not in `target_paths`.

**Provenance disclosure (interrogative-default):** the two implementation artifacts were present in the working tree (untracked, uncommitted) at this session's start, authored under the GO'd `-003` design by a prior Prime Builder session in this same program. This session did **not** author the code; it **verified the artifacts against the GO'd contract by execution** - the full pytest suite (11/11), both ruff gates, and a live read-only dry-run against the canonical manifest + `groundtruth.db` - and confirmed conformance to all four `-002` NO-GO fixes the GO'd `-003` design carries. The artifacts conform; this report carries the verification evidence forward for Codex's VERIFIED decision.

Implemented surface (`scripts/hygiene/router_corpus_dispose.py`), matching the GO'd Proposed Implementation:

- **Default mode (read-only dry-run):** `load_latest_manifest` selects the newest **complete** benchmark run directory under `.gtkb-state/benchmarks/` - one containing BOTH `run.json` AND `backlog_triage_items.json` whose `backlog_triage` result `run_id` matches the items-file `run_id` (FINDING-P2-003). `build_dry_run` filters to the `retire_candidate_unapproved_noise` + `platform` cohort, JOINs `current_work_items` over a read-only (`mode=ro`) SQLite URI to enrich each item with `title`, `changed_at`, `source_spec_id`, `priority`, `origin`, `component` (FINDING-P2-004), reports any cohort id missing from the DB as a `defect`, and emits deterministic JSON + a markdown summary citing `run_id` + `idempotency_key`.
- **`--prepare-batch <out.json>`:** emits a batch packet `{auq_id: null, manifest_run_id, idempotency_key, ids, batch_hash}` with `--max-batch-size` (default 50, hard-capped at 50).
- **`--apply --batch-file <approved-batch.json> --confirm-manifest <run_id>`:** five FAIL-CLOSED safety belts - stale-manifest refusal (FINDING-P2-003), batch-hash mismatch refusal (FINDING-P1-001), cohort-membership refusal (D4 conservative), `current_work_items`-presence refusal, and open-state idempotency refusal - then mutates via `db.update_work_item(id, changed_by, change_reason, owner_approved=True, resolution_status="wont_fix")` so every unchanged field is preserved (FINDING-P1-002). `update_work_item` is the **only** mutation primitive (AST-asserted).

## In-Root Placement Evidence

Both target paths resolve inside `E:\GT-KB` (`scripts/hygiene/router_corpus_dispose.py`, `platform_tests/scripts/test_router_corpus_dispose.py`). No application-subtree or out-of-root placement. The tool defaults to the in-root `groundtruth.db` and read-only benchmarks under `.gtkb-state/benchmarks/`.

## Specification Links

- `GOV-STANDING-BACKLOG-001` - backlog authority; bulk-ops visibility clause satisfied (see Backlog Visibility in `-003`).
- `SPEC-AUTO-BACKLOG-FOR-IMPLEMENTATION-BEARING-SPECS-001` - linked in PAUTH.
- `SPEC-1662` (GOV-18, measurement quality) - Stage 0 hardening that makes Stage 2 safe.
- `GOV-08` - KB is single source of truth; Stage 2 mutates only via the canonical `db.update_work_item` API.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - the tool refuses to operate on a stale or incomplete manifest and pins the exact approved-id set by hash.
- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` / `DCL-STANDING-BACKLOG-DB-SCHEMA-001` - schema authority; append-only versioning; field-preservation (FINDING-P1-002).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all Stage 2 changes are in-root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - durable-artifact discipline.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - the disposition tool IS the deterministic service.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - filed under `bridge/` with INDEX entry; append-only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - all relevant specs cited here and carried forward.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping with executed commands and observed results below.

## Spec-to-Test Mapping (executed)

Command (all tests): `python -m pytest platform_tests/scripts/test_router_corpus_dispose.py -q`
Observed: `11 passed in 1.27s`.

| Spec / requirement | Derived Test | Observed |
|---|---|---|
| `GOV-STANDING-BACKLOG-001` + `SPEC-1662` (deterministic disposition) | `test_dry_run_is_deterministic_and_read_only` - two dry-runs byte-identical; DB row count unchanged | PASS |
| `GOV-08` + `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` (canonical mutation only; field preservation) | `test_apply_uses_update_work_item_and_default_path_uses_read_only_uri` (AST: exactly one `update_work_item`; `mode=ro` present) + `test_refined_batch_applies_only_subset_and_preserves_fields` (16-field pre/post snapshot) | PASS |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (no stale/incomplete manifest) | `test_apply_refuses_stale_manifest` + `test_selects_newest_complete_manifest_skipping_partial_and_mismatched` | PASS |
| D2 (per-batch owner AUQ; refined batches representable) | `test_apply_refuses_batch_hash_mismatch` + `test_refined_batch_applies_only_subset_and_preserves_fields` (REFINE subset) + `test_prepare_batch_writes_packet_and_enforces_size_cap` | PASS |
| D4 (conservative retire-candidacy) | `test_apply_refuses_unknown_id_not_in_cohort` + `test_agent_red_scope_items_are_excluded_from_cohort` | PASS |
| FINDING-P1-002 (16-field preservation) | `test_refined_batch_applies_only_subset_and_preserves_fields` (16 fields asserted pre==post; only `resolution_status` changes) | PASS |
| FINDING-P2-003 (complete-manifest selection) | `test_selects_newest_complete_manifest_skipping_partial_and_mismatched` (partial dir + run-id mismatch both skipped) | PASS |
| FINDING-P2-004 (enrichment + missing-id defect) | `test_dry_run_enriches_candidates_and_reports_missing_db_rows` | PASS |
| Idempotency (no double-apply) | `test_apply_refuses_non_open_id` | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | full suite + ruff check + ruff format --check | PASS |

## Verification Evidence

1. **Test suite** - `python -m pytest platform_tests/scripts/test_router_corpus_dispose.py -q` -> `11 passed in 1.27s`.
2. **Lint** - `ruff check scripts/hygiene/router_corpus_dispose.py platform_tests/scripts/test_router_corpus_dispose.py` -> `All checks passed!` (exit 0).
3. **Format** - `ruff format --check scripts/hygiene/router_corpus_dispose.py platform_tests/scripts/test_router_corpus_dispose.py` -> `2 files already formatted` (exit 0). (Separate gate from lint per the pre-file code-quality requirement.)
4. **Live read-only dry-run** against the canonical manifest + `groundtruth.db` - `python scripts/hygiene/router_corpus_dispose.py` -> exit `0`, `status: "ok"`, `candidate_count: 749`, `missing_current_work_items: 0`, `run_id: 20260611-145734`. The tool located the newest complete manifest deterministically, JOINed `current_work_items` read-only, and produced a clean 749-item `retire_candidate_unapproved_noise` platform cohort with zero missing-id defects. No DB mutation (read-only `mode=ro` URI; `--apply` not invoked).

## Acceptance Criteria Check

1. Tool exists, runs read-only by default, locates newest complete manifest deterministically, joins `current_work_items` for enrichment, emits JSON + markdown summary citing `run_id` + `idempotency_key` - **MET** (evidence 4; `test_dry_run_*`).
2. `--prepare-batch <out.json>` emits packet with `auq_id=null`, `manifest_run_id`, `idempotency_key`, `ids`, precomputed `batch_hash` - **MET** (`test_prepare_batch_writes_packet_and_enforces_size_cap`).
3. `--apply --batch-file` requires `auq_id` populated, validates `batch_hash`, refuses stale manifest / hash mismatch / unknown id / non-open id / size > 50 - **MET** (`test_apply_refuses_*`, `_load_batch_file` validation).
4. Mutation primitive is `update_work_item(...)` with `owner_approved=True`, `resolution_status="wont_fix"`; field-preservation snapshot passes - **MET** (`test_refined_batch_applies_only_subset_and_preserves_fields`; 16-field snapshot).
5. Default-mode AST scan + row-count guard + read-only DB URI all pass - **MET** (`test_apply_uses_update_work_item_and_default_path_uses_read_only_uri`, `test_dry_run_is_deterministic_and_read_only`).
6. APPROVE / REFINE / REJECT semantics each covered - **MET** (full cohort apply, subset REFINE, unknown-id/no-op refusals).
7. All new tests pass; `ruff check` and `ruff format --check` clean on every changed Python file - **MET** (evidence 1-3).

(Applicability + clause preflight outputs for this `-005` report are run by the filing session immediately after Write; Codex's VERIFIED verdict should cite them per the Mandatory Applicability Preflight Gate.)

## Recommended Commit Type

`feat` - net-new disposition tool + 11-test suite (a new deterministic capability surface). The ~15 separate `--apply` executions (each under its own per-batch owner AUQ) are not part of the commit this report produces.

## Owner Decisions / Input

- **AskUserQuestion / `DELIB-20261667` (2026-06-11):** owner chartered the project and answered D1-D5 plus the continuation approval (`Yes`/`Resume`), authorizing Stage 2's signal-classify + bulk-dispose direction under per-batch staged approval. Carried forward from `-003`.
- **Per-batch owner AUQ is NOT collected by this report.** Each `--apply` batch (≤ 50 ids) requires its own AskUserQuestion at execution time, with the enriched candidate table (`id`, `title`, `changed_at`, `source_spec_id`, `priority`, `origin`, `component`) and the owner's APPROVE / REFINE / REJECT decision captured into `<approved-batch.json>.auq_id`. This report verifies the tool that will execute those owner-approved batches; it does not dispose any item.
- Project authorization: `PAUTH-PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001-...-BOUNDED-IMPLEMENTATION-AUTHORIZATION` (active; `source_addition` + `test_addition`), covering WI-4456.
- No new owner decision is required to verify this report.

## Prior Deliberations

- `DELIB-20261667` - owner decision chartering this project (D1-D5).
- `bridge/gtkb-backlog-triage-and-hygiene-stage-2-router-corpus-disposition-002.md` (NO-GO) - Codex's four findings; all four addressed by the GO'd `-003` design and verified present in the implementation (see Spec-to-Test mapping).
- `bridge/gtkb-backlog-triage-and-hygiene-stage-2-router-corpus-disposition-003.md` (REVISED) / `-004.md` (GO) - the GO'd proposal + verdict this report carries forward.
- `bridge/gtkb-backlog-triage-and-hygiene-stage-0-analyzer-011.md` (VERIFIED) - Stage 0 analyzer + rubber-stamp hardening; the manifest this tool consumes.
- `bridge/gtkb-backlog-triage-and-hygiene-stage-1-structural-repair-006.md` (VERIFIED) - Stage 1's strict-apply-order pattern reused here.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - the disposition tool IS the deterministic service.

## Files Changed

- `scripts/hygiene/router_corpus_dispose.py` (new; deterministic 3-mode disposition tool, read-only by default)
- `platform_tests/scripts/test_router_corpus_dispose.py` (new; 11-test suite incl. 16-field preservation snapshot + AST mutation-primitive guard)

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
