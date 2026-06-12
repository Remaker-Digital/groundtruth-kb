NEW
author_identity: Claude Code
author_harness_id: B
author_session_context_id: 544b584c-7392-4d40-81d8-dba187ba11eb
author_model: claude-opus-4-7
author_model_version: claude-opus-4-7
author_model_configuration: claude-code; interactive; Prime Builder; /loop dynamic
author_metadata_source: prime-builder session; bridge-author-metadata/current.json

# GT-KB Bridge Implementation Report - Stage 3 Advisory-Router Approval-Staged Intake

bridge_kind: implementation_report
Document: gtkb-backlog-triage-and-hygiene-stage-3-stop-the-leak
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-backlog-triage-and-hygiene-stage-3-stop-the-leak-002.md
Approved proposal: bridge/gtkb-backlog-triage-and-hygiene-stage-3-stop-the-leak-001.md
Recommended commit type: feat

## Implementation Claim

WI-4469 Stage 3 is implemented within the approved target paths.

`scripts/advisory_backlog_router.py` no longer creates OPEN `work_items` rows for routed advisories. It stages unhandled dropbox and bridge advisories as append-only JSONL candidate events under `.gtkb-state/advisory-candidates/candidates.jsonl`, treats any existing candidate-store source key as already handled regardless of current status, and still suppresses re-staging when a source key is already present in a promoted/legacy `work_items.related_deliberation_ids` row.

`scripts/hygiene/advisory_candidate_promote.py` adds the deterministic owner-gated promotion path. Default mode is read-only and emits deterministic JSON plus a markdown summary. `--prepare-batch` writes a capped packet with `auq_id: null` and a batch hash over sorted source keys plus the AUQ id. `--apply --batch-file` fails closed on hash mismatch, missing AUQ id, unknown source key, non-staged source key, or batch size greater than 50. Approved/refined batches create OPEN `work_items` rows through `KnowledgeDB.insert_work_item` only, carrying `approval_state="auq_resolved"` plus AUQ id and batch hash evidence in `change_reason`. Reject batches append `rejected` successor events without creating backlog rows.

No live promotion batch was applied as part of this implementation. All mutation-path tests used tmp_path fixture projects and fixture `groundtruth.db` files.

## Specification Links

- `GOV-STANDING-BACKLOG-001` - the active backlog remains governed known work; router output is staged until batch approval.
- `.claude/rules/backlog-approval-state.md` - promotion separates candidate presence from explicit AUQ-backed approval.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - the promotion tool performs deterministic execution after owner APPROVE / REFINE / REJECT input.
- `GOV-08` - promotion writes backlog rows through the canonical `KnowledgeDB.insert_work_item` API.
- `SPEC-1662` - Stage 3 extends the Stage 0 regression scaffold with executable router/promotion coverage.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all implementation files are under `E:\GT-KB`.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this implementation report is filed through the append-only bridge thread.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the implementation follows the approved proposal and carried-forward linked specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - linked requirements map to executed targeted tests and lint checks below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project/work-item/authorization linkage is supplied by the approved proposal.
- `SPEC-AUQ-POLICY-ENGINE-001` - per-batch `--apply` requires a non-empty AUQ id in the approved batch file.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - advisory provenance is preserved in an append-only candidate/successor-event surface.

## Owner Decisions / Input

- Carried forward from the approved proposal: 2026-06-11 owner AUQ selected approval-staged intake for the Stage 3 leak-fix strategy.
- Carried forward from the GO verdict: implementation is authorized only after `bridge/gtkb-backlog-triage-and-hygiene-stage-3-stop-the-leak-002.md`.
- No new owner decision was required for this implementation report.
- No per-batch promotion AUQ was consumed in this implementation. Future live `--apply` promotion batches still require their own approved batch file with a non-empty `auq_id`.

## Prior Deliberations

- `DELIB-20261667` - owner decision chartering the Backlog Triage and Hygiene project, including D5 stop-the-leak scope.
- `DELIB-20262463` and `DELIB-20262464` - Stage 2 router-corpus disposition context and per-batch AUQ control pattern.
- `DELIB-20262468` - Stage 0 backlog triage analyzer corrective VERIFIED context.
- `DELIB-20261055` - prior advisory that router output volume was creating backlog pressure.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - deterministic-service pattern applied to promotion after owner input.

## Specification-Derived Verification Plan

| Spec / requirement | Executed verification evidence |
| --- | --- |
| `GOV-STANDING-BACKLOG-001` | `test_router_stages_candidates_creates_no_work_items` confirms router staging creates zero `work_items`; `test_dry_run_is_deterministic_and_read_only` confirms default promotion inventory is read-only. |
| `.claude/rules/backlog-approval-state.md` | `test_apply_promotes_with_auq_and_hash_evidence` confirms promoted rows carry `approval_state="auq_resolved"` plus AUQ/hash evidence. |
| `DELIB-20261667` D2/D5 | `test_apply_refuses_batch_hash_mismatch`, `test_refine_promotes_subset`, and `test_reject_promotes_nothing_and_marks_rejected` cover per-batch AUQ/hash, refined subset, and rejected batch paths. |
| `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` | `test_prepare_batch_writes_packet_and_enforces_size_cap` and `test_dry_run_is_deterministic_and_read_only` cover deterministic packet/dry-run behavior. |
| `GOV-08` | `test_promote_uses_insert_work_item_only_and_default_is_read_only` AST-checks `insert_work_item` as the only work-item writer and no `update_work_item` usage. |
| `SPEC-1662` | Stage 3 targeted pytest suite extends the Stage 0/Stage 2 regression surface for router leak prevention and promotion safety. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Changed implementation files are all under `E:\GT-KB`; bridge clause preflight reports no `CLAUSE-IN-ROOT` gap. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Bridge applicability and clause preflights passed; implementation report is filed as the next append-only `NEW` version. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-backlog-triage-and-hygiene-stage-3-stop-the-leak` reports `missing_required_specs: []`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Targeted pytest, `ruff check`, and `ruff format --check` were executed on every changed Python target file. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Approved proposal contains Project, Work Item `WI-4469`, Project Authorization, and target_paths metadata; no implementation-time scope expansion was made. |
| `SPEC-AUQ-POLICY-ENGINE-001` | `test_apply_refuses_batch_hash_mismatch`, `test_apply_promotes_with_auq_and_hash_evidence`, and `_load_batch_file` coverage confirm `--apply` refuses non-restamped/missing-AUQ batches. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Router/promotion tests confirm staged, promoted, and rejected candidate states are append-only successor events, preserving advisory provenance. |

## Commands Run

```powershell
python -m pytest platform_tests/scripts/test_advisory_backlog_router.py platform_tests/scripts/test_advisory_candidate_promote.py -q --tb=short
python -m ruff check scripts/advisory_backlog_router.py scripts/hygiene/advisory_candidate_promote.py platform_tests/scripts/test_advisory_backlog_router.py platform_tests/scripts/test_advisory_candidate_promote.py
python -m ruff format --check scripts/advisory_backlog_router.py scripts/hygiene/advisory_candidate_promote.py platform_tests/scripts/test_advisory_backlog_router.py platform_tests/scripts/test_advisory_candidate_promote.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-backlog-triage-and-hygiene-stage-3-stop-the-leak
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-backlog-triage-and-hygiene-stage-3-stop-the-leak
```

## Observed Results

- Targeted pytest: 21 tests collected; 21 passed.
- `ruff check`: All checks passed.
- `ruff format --check`: 4 files already formatted.
- Bridge applicability preflight: `preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`.
- ADR/DCL clause preflight: exit 0; `Evidence gaps in must_apply clauses: 0`; `Blocking gaps (gate-failing): 0`.

## Files Changed

Stage 3 implementation scope:

- `scripts/advisory_backlog_router.py`
- `scripts/hygiene/advisory_candidate_promote.py`
- `platform_tests/scripts/test_advisory_backlog_router.py`
- `platform_tests/scripts/test_advisory_candidate_promote.py`

Bridge/report filing scope:

- `bridge/gtkb-backlog-triage-and-hygiene-stage-3-stop-the-leak-003.md`
- `bridge/INDEX.md`

Pre-existing unrelated worktree changes are present in the checkout and are not claimed by this implementation report.

## Acceptance Criteria Status

- [x] Router stages advisories to `.gtkb-state/advisory-candidates/candidates.jsonl`, creates zero `work_items` rows, and is idempotent across reruns.
- [x] Promotion tool runs read-only by default, emits deterministic JSON plus markdown, supports `--prepare-batch`, and supports fail-closed `--apply --batch-file`.
- [x] Approved/refined apply creates OPEN `work_items` rows only for named staged candidates, with AUQ/hash evidence and `approval_state="auq_resolved"`; reject creates no backlog rows.
- [x] `KnowledgeDB.insert_work_item` is the only work-item writer in the promotion tool; default path is read-only.
- [x] Targeted tests pass; `ruff check` and `ruff format --check` pass on every changed Python file.
- [x] Bridge applicability and ADR/DCL clause preflights pass with no blocking gaps.

## Risk And Rollback

Residual risk is operational cadence: staged candidates can accumulate if no owner/triage process periodically approves or rejects batches. That is intentionally lower blast radius than the old leak because staged candidates do not enter active backlog queries until promotion.

Rollback is scoped and reversible: revert `scripts/advisory_backlog_router.py`, remove `scripts/hygiene/advisory_candidate_promote.py`, and remove/update the two Stage 3 test files. Existing candidate-store JSONL events are runtime state under `.gtkb-state`; if rollback is chosen, they become inert unless the promotion tool is present.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Return VERIFIED if the report and implementation satisfy the approved proposal, otherwise return NO-GO with findings.
