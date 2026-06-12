NEW
author_identity: claude
author_harness_id: B
author_session_context_id: 28d30cb5-bfc4-4a97-acca-57d36d002533
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: 1m
author_metadata_source: prime-builder session; bridge-author-metadata/current.json

# Stage 3 - Advisory-Router Approval-Staged Intake (Stop-the-Leak)

bridge_kind: prime_proposal
Document: gtkb-backlog-triage-and-hygiene-stage-3-stop-the-leak
Version: 001
Date: 2026-06-11 UTC

Project: PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001
Work Item: WI-4469
Project Authorization: PAUTH-PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001-BACKLOG-TRIAGE-AND-HYGIENE-BOUNDED-IMPLEMENTATION-AUTHORIZATION

target_paths: ["scripts/advisory_backlog_router.py", "scripts/hygiene/advisory_candidate_promote.py", "platform_tests/scripts/test_advisory_candidate_promote.py", "platform_tests/scripts/test_advisory_backlog_router.py"]

No backlog mutation at GO time: this proposal authorizes (a) redirecting the advisory-router's output to an approval-staging surface and (b) adding a deterministic promotion tool plus tests. Real `work_items` rows are created ONLY by the `--apply` promotion path, which runs AFTER bridge GO AND a separate per-batch owner AskUserQuestion, with an explicit approved-id batch file and a deterministic batch hash. `groundtruth.db` is intentionally NOT in target_paths.

## Claim

The advisory-router (`scripts/advisory_backlog_router.py`) is the source of the backlog leak Stage 2 disposed. On every Stop event it creates one OPEN `work_items` row per `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-*.md` advisory (and per bridge `ADVISORY` entry), with `origin=hygiene`, `source_spec_id=GOV-STANDING-BACKLOG-001`, `resolution_status=open`. Most advisories are informational; they accumulated as the 749-item `retire_candidate_unapproved_noise` platform cohort Stage 2 just disposed (bridge `gtkb-backlog-triage-and-hygiene-stage-2-router-corpus-disposition` VERIFIED@-007). Because the router runs on a Stop hook, the leak is ongoing: every LO session that drops an advisory refills the pool.

Stage 3 stops the leak at the source by changing the router from auto-promote to **approval-staged intake** (owner AUQ, 2026-06-11): the router stages advisories on an approval surface, and they enter the active backlog ONLY after explicit owner/triage per-batch approval. The promotion tool is the deterministic-service counterpart to Stage 2's disposition tool — Stage 2 gates the corpus OUTPUT (dispose accumulated noise); Stage 3 gates the corpus INPUT (nothing enters the active backlog unapproved).

## Owner Decisions / Input

- **AskUserQuestion (2026-06-11, this session):** owner selected **"Approval-staged intake"** as the Stage 3 leak-fix strategy from a 4-option AUQ (classify-and-suppress / severity-gated / approval-staged / pull-not-push digest). The router creates candidate/pending rows (not `open`); they become active backlog items only after explicit owner/triage approval. Recorded in `memory/pending-owner-decisions.md` (detected_via: ask_user_question). This is the implementation-strategy authorization for Stage 3.
- **`DELIB-20261667` D5 (charter):** "Include stop-the-leak stage. The new detector script also serves as the regression scaffold the Stage 3 stop-the-leak surface can extend."
- **PAUTH carve-out:** `PAUTH-...-BOUNDED-IMPLEMENTATION-AUTHORIZATION` `forbidden_operations` includes `advisory_router_source_change_without_stage3_bridge_go` — i.e., the advisory-router source change IS permitted WITH this Stage 3 bridge GO. `allowed_mutation_classes` are `source_addition`, `test_addition`, `script_addition`; `scope_summary` covers "Stages 0-6 tooling/code"; `owner_decision_deliberation_id = DELIB-20261667`; active, expires 2026-08-31; WI-4469 is an active project member.
- **Per-batch promotion AUQ is NOT collected by this proposal's GO.** Each `--apply` batch (≤ 50 candidates) requires its own AskUserQuestion at execution time (APPROVE / REFINE / REJECT), captured into the approved-batch file's `auq_id`.

## Requirement Sufficiency

Existing requirements sufficient. The behavior is constrained by `GOV-STANDING-BACKLOG-001` (backlog authority; the active backlog is governed known work), `.claude/rules/backlog-approval-state.md` (approval-state separation: backlog presence is not implementation/active authority), and `DELIB-20261667` D5 (stop-the-leak charter). The owner AUQ fixed the strategy (approval-staged intake). No new or revised requirement is required before implementation.

## Specification Links

- `GOV-STANDING-BACKLOG-001` - **Primary.** The active backlog is the governed view of known work; Stage 3 ensures router output does not enter it without approval.
- `.claude/rules/backlog-approval-state.md` - the candidate->approved promotion mirrors the approval-state ladder (presence is not authority; approval is explicit, evidence-bearing).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - the promotion tool IS the deterministic service; the AI's only marginal input is the owner APPROVE/REFINE/REJECT decision per batch.
- `GOV-08` - KB is the single source of truth; promotion creates `work_items` via the canonical `db.insert_work_item` API only.
- `SPEC-1662` (GOV-18, measurement quality) - the Stage 0 detector whose regression scaffold Stage 3 extends (D5).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all Stage 3 changes are in-root under `E:\GT-KB`.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - filed under `bridge/` with a `NEW` `bridge/INDEX.md` entry; append-only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all relevant cross-cutting specs here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the Spec-Derived Verification Plan maps linked specs to executable tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project / Work Item / Project Authorization metadata present above.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner AUQ authorized the strategy; per-batch promotion AUQs gate each `--apply`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - durable-artifact discipline; the candidate surface preserves advisory provenance until promotion or rejection.

## Prior Deliberations

- `DELIB-20261667` - owner decision chartering this project (D1-D5; D5 = stop-the-leak).
- 2026-06-11 owner AUQ (this session) - approval-staged intake strategy selection (recorded in `memory/pending-owner-decisions.md`; to be archived as an owner-conversation deliberation in session wrap per `.claude/rules/deliberation-protocol.md`).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - Stage 3's promotion tool is the deterministic service.
- `bridge/gtkb-backlog-triage-and-hygiene-stage-2-router-corpus-disposition-007.md` (VERIFIED) - Stage 2's disposition tool; Stage 3 reuses its 3-mode + batch-hash + per-batch-AUQ pattern (the symmetric intake counterpart).
- `bridge/gtkb-backlog-triage-and-hygiene-stage-0-analyzer-011.md` (VERIFIED) - the Stage 0 backlog-triage detector whose regression scaffold Stage 3 extends (D5).
- Deliberation Archive semantic search on 2026-06-11 for "advisory router stop the leak / intake policy / router-generated noise" returned no prior decisions; this is the first treatment of the router intake-gating design.

## Backlog Visibility

`GOV-STANDING-BACKLOG-001` bulk-ops clause (`CLAUSE-VISIBILITY-BULK-OPS`): the `--apply` promotion path performs bulk-class creation of `work_items`. Visibility is satisfied by three artifacts per batch, symmetric with Stage 2: (1) the `--prepare-batch` output (the inventory of candidates that will be promoted, with enrichment); (2) the dry-run JSON + markdown review packet served inside the per-batch AskUserQuestion; (3) the durable `change_reason` on every promoted `work_items` row embedding the `auq_id` + `batch_hash` (append-only audit trail). Per D2/D5 of `DELIB-20261667`, each batch (≤ 50) requires its own per-batch owner AskUserQuestion at execution time.

## Scope and Boundaries

In scope: (1) redirect `scripts/advisory_backlog_router.py` output from OPEN `work_items` rows to an append-only approval-staging surface (`.gtkb-state/advisory-candidates/candidates.jsonl`); (2) a new deterministic promotion tool `scripts/hygiene/advisory_candidate_promote.py` (read-only dry-run by default; opt-in `--apply` under per-batch owner AUQ); (3) pytest at `platform_tests/scripts/test_advisory_candidate_promote.py` and `platform_tests/scripts/test_advisory_backlog_router.py`.

Out of scope: any modification of core `groundtruth-kb/src/groundtruth_kb/db.py` (a new `resolution_status` or active-backlog-query change is NOT within the PAUTH `allowed_mutation_classes` and is deferred to the rejected-alternative below); the 749 already-disposed items (Stage 2); promotion/disposition of the pre-existing candidate accumulation (handled by Stage 2 + the first promotion batches); deploy/push.

## Proposed Implementation

**IP-1 - Router redirect to approval-staging (`scripts/advisory_backlog_router.py`; authorized via the PAUTH advisory_router carve-out + this Stage 3 GO).**

- Replace `insert_wi_for_advisory` (which calls `db.insert_work_item(... resolution_status="open")`) with `stage_advisory_candidate`, which appends one record per unhandled advisory to an append-only candidate store `.gtkb-state/advisory-candidates/candidates.jsonl`. Each record carries: `source` ("dropbox"/"bridge"), `source_key`, `relative_path`, `proposed_title`, `description`, `priority`, `severity_token`, `related_bridge_threads`, `advisory_date`, `staged_at`, and `status="staged"`.
- Extend the idempotency check: an advisory is "already handled" when its `source_key` is (a) already present in the candidate store (any status), OR (b) already present in a `work_items` row's `related_deliberation_ids` (the existing promoted-row check). This prevents re-staging across runs and prevents re-staging an already-promoted advisory.
- The router no longer writes `work_items` rows. Net effect: the active backlog stops accumulating router output; advisories wait on the candidate surface for approval.

**IP-2 - Deterministic promotion tool (`scripts/hygiene/advisory_candidate_promote.py`; script_addition). Three modes, mirroring the Stage 2 disposition tool:**

- **Default (read-only dry-run):** read the candidate store, filter `status="staged"`, emit deterministic JSON (`{candidate_count, candidates:[{source_key, proposed_title, priority, severity_token, source, relative_path, ...}], ...}`) + a markdown summary (counts by priority/source, first 10 titles).
- **`--prepare-batch <out.json>`:** select the first N staged candidates (N owner-configurable, default 50, hard-capped at 50 per the kb-batch convention); emit `{auq_id: null, source_keys: [...], batch_hash: sha256(sorted source_keys + auq_id), prepared_at}`.
- **`--apply --batch-file <approved-batch.json>`:** FAIL-CLOSED safety belts: (1) re-compute `batch_hash` -> refuse on mismatch; (2) each `source_key` must be present in the candidate store with `status="staged"` -> refuse on unknown/non-staged (idempotency); (3) `auq_id` non-empty -> refuse otherwise; (4) batch size ≤ 50 -> refuse otherwise. For each APPROVED candidate, create a real `work_items` row via `db.insert_work_item(... resolution_status="open", origin="hygiene", component="backlog", source_spec_id="GOV-STANDING-BACKLOG-001", approval_state="auq_resolved", related_deliberation_ids=<source_key>, change_reason=f"Stage 3 promotion; approved by {auq_id}; batch_hash {hash}; per DELIB-20261667 D5.")`, then mark the candidate record `status="promoted"`. A REFINE (subset batch-file) promotes only the named subset. REJECT marks named candidates `status="rejected"` (never promoted, never re-staged).

**IP-3 - Regression scaffold + tests (`platform_tests/scripts/test_advisory_candidate_promote.py`, `platform_tests/scripts/test_advisory_backlog_router.py`; test_addition; D5).**

- Router tests: the router stages candidates and creates ZERO `work_items` rows; idempotency across reruns; an already-promoted `source_key` is not re-staged.
- Promotion tests: dry-run is deterministic + does not mutate the DB; `--prepare-batch` enforces the size cap and emits `auq_id=null`; `--apply` refuses batch-hash mismatch / unknown source_key / non-staged / size > 50; APPROVE promotes (creates an OPEN `work_items` row carrying `auq_id`+`batch_hash` in `change_reason`); REFINE promotes only the subset; REJECT promotes nothing and marks rejected; double-apply is refused (idempotency).
- The promotion tool's mutation primitive is `db.insert_work_item` (AST-asserted as the only `work_items` writer), and the default path is read-only.

## Rejected Alternative (documented per the interrogative default)

**`work_items`-candidate-rows model** (router creates rows with `resolution_status="candidate"`; `get_open_work_items`/`gt backlog list` modified to exclude it). REJECTED for this slice because it requires modifying core `groundtruth-kb/src/groundtruth_kb/db.py` (a new `resolution_status` value + the active-backlog query) — `source_modification` of a core platform file, which is NOT in the PAUTH `allowed_mutation_classes` (`source_addition`/`test_addition`/`script_addition`) and would require an owner-approved authorization expansion. It also has broader blast radius (every active-backlog reader: `get_open_work_items`, dashboard, KPIs, and the Stage 2 tool's `OPEN_STATES`). The additive staging surface realizes the SAME owner-chosen strategy (nothing enters the active backlog unapproved) within the bounded authorization. If the owner prefers candidates to be queryable as `work_items` rows, that is a follow-up AUQ + authorization expansion + a separate db.py slice.

## Spec-Derived Verification Plan

| Spec / requirement | Derived test | Command |
|---|---|---|
| `GOV-STANDING-BACKLOG-001` (router output does not enter the active backlog) | `test_router_stages_candidates_creates_no_work_items` | `python -m pytest platform_tests/scripts/test_advisory_backlog_router.py -q` |
| `.claude/rules/backlog-approval-state.md` (explicit, evidence-bearing promotion) | `test_apply_promotes_with_auq_and_hash_evidence` (promoted row `change_reason` carries `auq_id`+`batch_hash`) | `python -m pytest platform_tests/scripts/test_advisory_candidate_promote.py -q` |
| `DELIB-20261667` D2/D5 (per-batch AUQ; refined/rejected batches) | `test_apply_refuses_hash_mismatch` + `test_refine_promotes_subset` + `test_reject_promotes_nothing` | same |
| `GOV-08` (canonical mutation only) | `test_promote_uses_insert_work_item_only_and_default_is_read_only` (AST + row-count guard) | same |
| Idempotency | `test_already_promoted_source_key_not_restaged` + `test_double_apply_refused` | both files |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | full suites + `ruff check` AND `ruff format --check` on every changed Python file | `python -m pytest ...` ; `ruff check ...` ; `ruff format --check ...` |

## Acceptance Criteria

1. The router stages advisories to `.gtkb-state/advisory-candidates/candidates.jsonl` and creates ZERO `work_items` rows; idempotent across reruns.
2. `advisory_candidate_promote.py` runs read-only by default, emits deterministic JSON + markdown, and supports `--prepare-batch` (auq_id=null, batch_hash) and `--apply --batch-file` with the five fail-closed safety belts.
3. `--apply` creates OPEN `work_items` rows ONLY for approved candidates, with `auq_id`+`batch_hash` in `change_reason` and `approval_state="auq_resolved"`; REJECT promotes nothing; REFINE promotes only the subset.
4. `insert_work_item` is the only `work_items` writer in the promotion tool (AST-asserted); default path is read-only.
5. All new tests pass; `ruff check` and `ruff format --check` clean on every changed Python file.
6. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-backlog-triage-and-hygiene-stage-3-stop-the-leak` reports `missing_required_specs: []`; `python scripts/adr_dcl_clause_preflight.py --bridge-id ...` reports no blocking gaps.

## Risk and Rollback

- **Risk - advisories staged but never promoted accumulate on the candidate surface.** Mitigation: the candidate store is runtime state under `.gtkb-state/` (not canonical backlog); a future owner triage cadence promotes/rejects in batches. Unlike the old behavior, accumulation no longer pollutes the active backlog or the Stage 0 classifier.
- **Risk - a genuinely high-signal advisory waits in staging.** Mitigation: the dry-run surfaces severity/priority so the owner can prioritize P0/P1 candidates first; the candidate record preserves full provenance.
- **Risk - the router change drops an advisory.** Mitigation: append-only candidate store + idempotency by `source_key`; tests assert no advisory is lost across reruns. Rollback: revert the router change (restores prior auto-promote) and the candidate store is inert.
- **Risk - promotion creates a malformed `work_items` row.** Mitigation: promotion uses the canonical `insert_work_item` with fixed origin/component/source_spec_id; tests assert the created row shape. Rollback: per-item `update_work_item(..., resolution_status="wont_fix")` (append-only).

## Recommended Routing

Claude/Codex (deterministic source + script + tests). The intellectual care is in: (a) the router idempotency extension (staged OR promoted); (b) the promotion tool's batch-hash + staged-state safety belts (reused from Stage 2); (c) the candidate-store append-only schema. No protected-narrative surface; no core db.py change.

## Recommended Commit Type

`feat` - net-new approval-staging surface + promotion tool + tests, plus the carved-out router redirect. The per-batch `--apply` promotion executions occur separately under their own owner AUQs and are not part of the commit this stage produces.

## Bridge Protocol Compliance

Filed at `bridge/gtkb-backlog-triage-and-hygiene-stage-3-stop-the-leak-001.md` with a matching `NEW` status line inserted at the top of this Document's version list in `bridge/INDEX.md`; append-only (no prior version deleted or rewritten). `GOV-FILE-BRIDGE-AUTHORITY-001` honored; `bridge/INDEX.md` remains the canonical workflow queue. The implementation-start packet will be minted from the GO against the PAUTH under `script_addition` / `test_addition` plus the `advisory_router_source_change` carve-out.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
