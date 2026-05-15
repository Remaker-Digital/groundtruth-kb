NEW

# Implementation Proposal - Backlog Approval-State Taxonomy and AUQ Implementation Gate (Slice 1)

bridge_kind: implementation_proposal
Document: gtkb-backlog-approval-state-taxonomy-slice-1
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350
Source work item: WI-3271 (Backlog approval-state taxonomy and AUQ implementation gate)
Recommended commit type: feat
target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/backlog/approval_state.py", "groundtruth-kb/src/groundtruth_kb/backlog/__init__.py", "groundtruth-kb/migrations/2026-05-14-approval-state-column.sql", "scripts/backlog_approval_gate.py", "scripts/backfill_approval_state.py", "platform_tests/groundtruth_kb/test_approval_state_schema.py", "platform_tests/groundtruth_kb/test_approval_state_gate.py", "platform_tests/scripts/test_backfill_approval_state.py", ".claude/rules/backlog-approval-state.md", "groundtruth.db"]

## Summary

WI-3271 (P1, project GTKB-BACKLOG-CAPTURE-001, sub-project "Approval state taxonomy", parent directive DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE) requires the GT-KB backlog to distinguish items captured for review/future-consideration from items approved for implementation. Capture must remain low-friction (no owner approval required to record a candidate); promotion to implementation-approved must require AskUserQuestion-recorded owner evidence per the AUQ-only enforcement stack (SPEC-AUQ-POLICY-ENGINE-001, SPEC-AUQ-NO-LLM-CLASSIFIER-001).

This Slice 1 implements the foundational schema, the mechanical promotion gate, the migration of the 127 currently-open work_items, and the test surface. Downstream bridge-protocol behavior is unchanged: implementation proposals still flow through bridge NEW/REVISED/GO/NO-GO/VERIFIED; this slice only adds an upstream classifier and gate so the bridge protocol can know which backlog rows are owner-authorized to begin implementation work.

Five canonical approval states are added: `unapproved` (default capture state; no owner attention), `auq_required` (Prime has surfaced the item for owner attention but no AUQ-recorded decision exists yet), `auq_resolved` (an AUQ exchange recorded owner decision selecting an implementation option), `bridge_authorized` (an item under an owner-approved project authorization or other bridge-level authorization envelope per DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION), `implementation_authorized` (terminal: bridge `GO` recorded for an implementation proposal citing the work item; ready for implementation-start-gate).

## Specification Links

- GOV-STANDING-BACKLOG-001 — MemBase `work_items` is the canonical backlog authority; this slice adds a column to that table within the governance contract.
- SPEC-AUQ-POLICY-ENGINE-001 — central deterministic policy engine returning canonical outcomes; the new gate is implemented as a policy-engine consumer, not an independent classifier.
- SPEC-AUQ-NO-LLM-CLASSIFIER-001 — deterministic-only; no LLM/API classifiers. The new gate uses string-equality state transitions and AUQ-resolved evidence records, not heuristic content matching.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — proposals must cite every relevant governing specification; this section satisfies that requirement.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — VERIFIED is conditional on test creation and execution derived from linked specs; the Test Mapping section maps each linked spec to specific test(s) and gives the command needed to execute them.
- GOV-FILE-BRIDGE-AUTHORITY-001 — bridge protocol authority; this proposal honors the NEW/REVISED/GO/NO-GO/VERIFIED lifecycle.
- GOV-ARTIFACT-APPROVAL-001 — formal artifact approval gate; the new state taxonomy does NOT replace per-artifact formal-artifact-approval packets for GOV/ADR/DCL/SPEC mutation. It augments the work-item lifecycle only.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — durable artifact preservation; the approval_state column is a durable artifact attribute under append-only versioning.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — development changes preserve traceability; the gate records the AUQ-evidence and bridge-GO citation in `work_items.change_reason` on state transitions.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — application placement; all target paths are within `E:\GT-KB`. No `applications/` paths touched.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — artifact lifecycle triggers require thresholds, states, and confirmation flows; the five-state taxonomy and the migration mapping satisfy this DCL's "states + confirmation flows" requirement.
- `.claude/rules/file-bridge-protocol.md` — proposal/review/verification protocol.
- `.claude/rules/codex-review-gate.md` — work-item state transitions to `implementation_authorized` require bridge GO; this slice mechanically enforces that.
- `.claude/rules/prime-builder-role.md` (§ "AskUserQuestion as the Only Valid Owner-Decision Channel") — AUQ is the canonical owner-decision channel; the gate consumes AUQ-recorded evidence only.
- `.claude/rules/canonical-terminology.md` — canonical glossary; this slice does not promote new concepts. The five approval states are operational fields, not glossary terms.
- `.claude/rules/operating-model.md` §2 — canonical backlog/work_item/project taxonomy; preserved.
- `.claude/rules/project-root-boundary.md` — in-root only.
- `memory/pending-owner-decisions.md` (durable record produced by `.claude/hooks/owner-decision-tracker.py`) — the gate cross-references AUQ entries in this file via `detected_via: ask_user_question` to validate AUQ-evidence claims.

## Prior Deliberations

- `DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE` — owner directive of 2026-05-11 establishing the two-tier model (consideration vs implementation-approved); the source directive for WI-3271 and the framing this slice implements.
- `DELIB-1947` — VERIFIED bridge thread `gtkb-gov-askuserquestion-enforcement-stack-2026-05-04` (umbrella) — the AUQ-only enforcement stack this slice integrates with.
- `DELIB-1946` — VERIFIED bridge thread `gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable` — owner-decision-tracker hook that produces the `memory/pending-owner-decisions.md` record this slice reads.
- `DELIB-1945` — VERIFIED bridge thread `gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule` — Prime-rule AUQ-only authority cited by the gate.
- `DELIB-1944` — VERIFIED bridge thread `gtkb-gov-askuserquestion-enforcement-stack-slice-c-bridge-gate` — Owner Decisions / Input section gate; pattern this slice's implementation gate parallels.
- `DELIB-1934` — VERIFIED bridge thread `gtkb-auq-policy-gates-001` — central policy engine integration this slice consumes.
- `DELIB-1939` — VERIFIED bridge thread `gtkb-auq-policy-gate-backlog-advisory-2026-05-04` — prior advisory on the AUQ-vs-backlog seam; the disposition framing this proposal builds on.

## Owner Decisions / Input

Owner direction 2026-05-14 S350: "Please parallelize work and start as many priority backlog projects as possible" — authorizes batch filing of priority backlog proposals (including this one). Per-proposal Codex GO is still required before any implementation begins. AUQ evidence: this owner direction was given via the canonical AskUserQuestion / direct-prompt channel of session S350 in response to the priority-backlog parallelization plan.

WI-3271's parent directive is DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE (owner_conversation, owner_decision outcome). That archived owner decision is the substantive source of the approval-state requirement; this proposal implements the directive without re-asking the owner for the underlying decision.

No additional owner AUQ exchanges are required to land Slice 1. Slice 2 (when filed) will introduce per-row transition AUQs into the gate's caller surface, but Slice 1 is foundation-only and does not surface owner-decision prompts at runtime.

Per the AUQ-only enforcement stack (SPEC-AUQ-POLICY-ENGINE-001), all owner decisions are AUQ-recorded. No prose-decision-ask is used in this proposal.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal mentions "standing backlog" and "work item" extensively. The bulk-ops clause `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` may fire on those tokens. This proposal is NOT a bulk operation in the clause's sense.

Evidence and clarification:

- The clause guards against "bulk work_item state transitions" — this slice does NOT transition any existing work_item between `resolution_status`/`stage` values. It performs a one-time backfill of a NEW column (`approval_state`) for inventory, classifying each open row based on its existing attributes (origin, source_owner_directive, related_bridge_threads, related_deliberation_ids).
- The migration is an `inventory` operation: read existing 127 open rows, compute default approval_state per a deterministic rule (no LLM, no judgment), write one new versioned row per work_item with the computed approval_state. Existing `resolution_status`, `stage`, `priority`, `project_name`, and all behavioral fields are preserved byte-for-byte.
- This proposal is a single-slice schema-change proposal, not a per-row owner-decision capture. Per-row owner-decision capture happens via AUQ at the future point where a Prime session promotes an individual item to `auq_resolved` or `implementation_authorized`; that promotion is out of scope for this slice.
- No `formal-artifact-approval` packet is required because no formal-artifact (GOV/ADR/DCL/PB/SPEC) is being created or mutated. The change is an operational-data schema extension governed by GOV-STANDING-BACKLOG-001 and the bridge-GO discipline this proposal itself exercises.

## Requirement Sufficiency

Existing requirements sufficient.

The five-state taxonomy, the AUQ-evidence requirement for `implementation_authorized`, the no-friction capture posture, and the migration obligation are all directly stated in DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE and re-expressed in WI-3271's `description` and `acceptance_summary`. The schema fields needed (column name, value set, transition rules) are derivable from those statements without further owner input.

The slice deliberately leaves three follow-on items for future bridge cycles:
(a) UI/CLI surfacing of approval_state in `gt backlog list` output (Slice 2).
(b) Integration with `scripts/implementation_authorization.py` so the implementation-start gate refuses packets for work items whose `approval_state != implementation_authorized` (Slice 3).
(c) Migration of WI-3271 itself to `auq_resolved` (and other items currently surfaced for owner attention) once the column exists (Slice 2 trailing step).

## Schema Change Plan

- New nullable column on `work_items`: `approval_state TEXT` (no `NOT NULL` constraint to preserve append-only/versioned compatibility with historical rows; new inserts emit a value; backfill emits a value for current rows).
- Allowed values (enforced by application-level check in `groundtruth-kb/src/groundtruth_kb/backlog/approval_state.py`): `unapproved`, `auq_required`, `auq_resolved`, `bridge_authorized`, `implementation_authorized`. Values stored in lowercase.
- Default for new captures via `db.insert_work_item()`: `unapproved`.
- New `current_work_items` view is unchanged (`SELECT w.*` already carries new column).
- Migration file `groundtruth-kb/migrations/2026-05-14-approval-state-column.sql` performs `ALTER TABLE work_items ADD COLUMN approval_state TEXT;` (SQLite-safe; idempotent via `PRAGMA table_info` check in the Python migration runner).
- Backfill via `scripts/backfill_approval_state.py`:
  - For each `current_work_items` row with `approval_state IS NULL`:
    - If `id == 'WI-3271'`: `auq_resolved` (owner directive DELIB-S341 recorded; this very proposal is the implementation entry path — final transition to `implementation_authorized` happens at bridge GO of this proposal).
    - Else if `related_bridge_threads` is non-empty AND references a bridge thread with VERIFIED status: `implementation_authorized`.
    - Else if `related_bridge_threads` is non-empty AND references a bridge thread with GO status (post-impl pending): `bridge_authorized`.
    - Else if `source_owner_directive` is non-empty AND `related_deliberation_ids` cites an owner_decision DELIB: `auq_resolved`.
    - Else if `source_owner_directive` is non-empty: `auq_required` (owner directive on file but no DELIB-recorded AUQ evidence yet).
    - Else: `unapproved`.
  - Each backfilled row inserts a new version with `changed_by='claude/prime-builder'`, `change_reason='WI-3271 Slice 1 approval-state backfill (deterministic classifier per bridge/gtkb-backlog-approval-state-taxonomy-slice-1-001.md)'`.
- Transition gate `scripts/backlog_approval_gate.py` (Slice 1 implements the function; Slice 3 integrates with implementation_authorization.py):
  - `can_promote(work_item_id, target_state) -> (bool, reason)`.
  - Refuses transition `unapproved -> implementation_authorized` and `auq_required -> implementation_authorized` without AUQ evidence.
  - AUQ evidence is recognized as either (a) a `detected_via: ask_user_question` entry in `memory/pending-owner-decisions.md` whose `subject_id` includes the work_item id, OR (b) a bridge `GO` verdict file whose `target work item` line cites the work_item id.
  - `bridge_authorized -> implementation_authorized` is allowed when a current bridge thread is at status `GO` and references the work_item.
  - All other transitions are policy-engine-consumed (SPEC-AUQ-POLICY-ENGINE-001) via `outcome = require_owner_decision()` semantics.

## Implementation Plan

1. Write migration SQL at `groundtruth-kb/migrations/2026-05-14-approval-state-column.sql`. Hand-test idempotency with PRAGMA check.
2. Add `approval_state` field to `db.insert_work_item()` signature with default `unapproved`; thread through `_kb_attribution.py` if attribution path requires it. (Audit `groundtruth-kb/src/groundtruth_kb/db.py` to identify all `work_items` mutation entry points.)
3. Implement `groundtruth-kb/src/groundtruth_kb/backlog/approval_state.py` with the `ApprovalState` enum, `ALLOWED_STATES`, `classify_initial_state()` deterministic classifier (no LLM), and `validate_transition()` rules.
4. Implement `scripts/backlog_approval_gate.py` CLI surface (`check`, `can_promote`, `apply` subcommands).
5. Implement `scripts/backfill_approval_state.py` with dry-run mode (default) and `--apply` flag.
6. Add durable rule file `.claude/rules/backlog-approval-state.md` documenting the five-state taxonomy, the transition rules, and the AUQ-evidence requirement. (This file is operational-doctrine, not a GOV/ADR/DCL spec; no formal-artifact-approval packet required.)
7. Write the test suite at `platform_tests/groundtruth_kb/test_approval_state_schema.py`, `platform_tests/groundtruth_kb/test_approval_state_gate.py`, and `platform_tests/scripts/test_backfill_approval_state.py`.
8. Run migration, run backfill in dry-run, validate counts, then `--apply`.
9. File the post-implementation report at `bridge/gtkb-backlog-approval-state-taxonomy-slice-1-NNN.md` with executed test output.

## Test Mapping

| # | Test | Linked Specification(s) | Command |
|---|------|-------------------------|---------|
| T1 | `test_approval_state_column_present` — confirms `PRAGMA table_info(work_items)` includes `approval_state` after migration. | GOV-STANDING-BACKLOG-001, DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | `python -m pytest platform_tests/groundtruth_kb/test_approval_state_schema.py::test_approval_state_column_present` |
| T2 | `test_allowed_states_enum` — `ALLOWED_STATES == {"unapproved","auq_required","auq_resolved","bridge_authorized","implementation_authorized"}`. | DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | `python -m pytest platform_tests/groundtruth_kb/test_approval_state_schema.py::test_allowed_states_enum` |
| T3 | `test_insert_work_item_defaults_to_unapproved` — new captures default to `unapproved` without owner approval; no AUQ recorded. | GOV-STANDING-BACKLOG-001 (low-friction capture), SPEC-AUQ-POLICY-ENGINE-001 (no AUQ at capture) | `python -m pytest platform_tests/groundtruth_kb/test_approval_state_schema.py::test_insert_work_item_defaults_to_unapproved` |
| T4 | `test_gate_blocks_unapproved_to_implementation_authorized` — `can_promote('WI-X','implementation_authorized')` returns `(False, ...)` when row is `unapproved`. | SPEC-AUQ-POLICY-ENGINE-001, `.claude/rules/prime-builder-role.md` AUQ-only channel | `python -m pytest platform_tests/groundtruth_kb/test_approval_state_gate.py::test_gate_blocks_unapproved_to_implementation_authorized` |
| T5 | `test_gate_blocks_auq_required_to_implementation_authorized` — same, for `auq_required` source state. | SPEC-AUQ-POLICY-ENGINE-001 | `python -m pytest platform_tests/groundtruth_kb/test_approval_state_gate.py::test_gate_blocks_auq_required_to_implementation_authorized` |
| T6 | `test_gate_allows_auq_resolved_to_implementation_authorized_with_evidence` — accepts AUQ-evidence path A (pending-owner-decisions entry with subject_id). | SPEC-AUQ-POLICY-ENGINE-001, owner-decision-tracker durable record | `python -m pytest platform_tests/groundtruth_kb/test_approval_state_gate.py::test_gate_allows_auq_resolved_to_implementation_authorized_with_evidence` |
| T7 | `test_gate_allows_bridge_authorized_to_implementation_authorized_with_go_verdict` — accepts AUQ-evidence path B (bridge GO verdict file). | GOV-FILE-BRIDGE-AUTHORITY-001, SPEC-AUQ-POLICY-ENGINE-001 | `python -m pytest platform_tests/groundtruth_kb/test_approval_state_gate.py::test_gate_allows_bridge_authorized_to_implementation_authorized_with_go_verdict` |
| T8 | `test_gate_uses_policy_engine_no_llm` — confirms the gate's classification path is string-equality / pattern-match only (no API/LLM call). | SPEC-AUQ-NO-LLM-CLASSIFIER-001 | `python -m pytest platform_tests/groundtruth_kb/test_approval_state_gate.py::test_gate_uses_policy_engine_no_llm` |
| T9 | `test_backfill_dry_run_classifies_all_open_rows` — dry-run on a fixture DB classifies every open row into one of the five states and reports zero `NULL` remaining. | DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | `python -m pytest platform_tests/scripts/test_backfill_approval_state.py::test_backfill_dry_run_classifies_all_open_rows` |
| T10 | `test_backfill_classifier_assigns_wi3271_auq_resolved` — WI-3271 specifically is classified `auq_resolved` (DELIB-S341 directive cite). | DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE | `python -m pytest platform_tests/scripts/test_backfill_approval_state.py::test_backfill_classifier_assigns_wi3271_auq_resolved` |
| T11 | `test_backfill_preserves_existing_columns` — every backfilled row has byte-identical `resolution_status`, `stage`, `priority`, `project_name`, `title`, `description`, `origin`, `component` vs the prior version. | GOV-ARTIFACT-ORIENTED-GOVERNANCE-001, append-only-versioning regression guard | `python -m pytest platform_tests/scripts/test_backfill_approval_state.py::test_backfill_preserves_existing_columns` |
| T12 | `test_backfill_idempotent` — second run on already-backfilled DB makes zero writes. | GOV-STANDING-BACKLOG-001 (no spurious mutation), DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | `python -m pytest platform_tests/scripts/test_backfill_approval_state.py::test_backfill_idempotent` |
| T13 | `test_root_boundary_no_writes_outside_gt_kb` — migration + backfill touch only `E:\GT-KB` paths. | ADR-ISOLATION-APPLICATION-PLACEMENT-001, `.claude/rules/project-root-boundary.md` | `python -m pytest platform_tests/scripts/test_backfill_approval_state.py::test_root_boundary_no_writes_outside_gt_kb` |
| T14 | `test_rule_file_states_taxonomy_complete` — `.claude/rules/backlog-approval-state.md` lists all five canonical states and the AUQ-evidence requirement. | DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | `python -m pytest platform_tests/groundtruth_kb/test_approval_state_schema.py::test_rule_file_states_taxonomy_complete` |
| T15 | `test_existing_backlog_count_unchanged` — `SELECT COUNT(DISTINCT id) FROM current_work_items WHERE resolution_status='open'` returns the same 127 count pre- and post-migration. | GOV-STANDING-BACKLOG-001 (regression: no item count drift) | `python -m pytest platform_tests/groundtruth_kb/test_approval_state_schema.py::test_existing_backlog_count_unchanged` |

Full test suite execution command (post-implementation): `python -m pytest platform_tests/groundtruth_kb/test_approval_state_schema.py platform_tests/groundtruth_kb/test_approval_state_gate.py platform_tests/scripts/test_backfill_approval_state.py -v`.

## Risk and Rollback

Risks:

- **Schema migration affects shared `groundtruth.db`.** Mitigation: SQLite `ALTER TABLE ADD COLUMN` is non-destructive; the new column is nullable; existing reads are unaffected because `SELECT *` already carries the new column transparently and no consumer reads `approval_state` until Slice 2.
- **Backfill mis-classification.** Mitigation: every classification is deterministic from existing fields (no judgment); the test suite includes T9-T11 to validate the classifier output on the live row set; dry-run is the default mode of `backfill_approval_state.py`.
- **Downstream-consumer drift if implementation_authorization.py is updated to consult `approval_state` before Slice 3.** Mitigation: Slice 1 explicitly does NOT touch `scripts/implementation_authorization.py`; the gate is consumed only by the new `scripts/backlog_approval_gate.py` surface. Slice 3 will file a separate bridge proposal to integrate.

Rollback:

- Migration rollback: `ALTER TABLE work_items DROP COLUMN approval_state;` (SQLite 3.35+). If unavailable, restore from pre-migration backup at `.gtkb-state/backups/groundtruth.db.pre-WI3271-slice-1.bak` (the backfill script creates this backup before its first write).
- Code rollback: revert the commit; the new modules and tests are net-new files (no existing-file edits beyond `db.py`); the `db.py` change is one new keyword argument with a default value (backward compatible).

## Acceptance Criteria

1. `PRAGMA table_info(work_items)` includes a `approval_state TEXT` column.
2. `SELECT COUNT(*) FROM current_work_items WHERE resolution_status='open' AND approval_state IS NULL` returns 0 after backfill.
3. `SELECT approval_state, COUNT(*) FROM current_work_items WHERE resolution_status='open' GROUP BY approval_state` returns a distribution across the five canonical states with WI-3271 classified `auq_resolved`.
4. All 15 tests in Test Mapping section pass.
5. The applicability preflight on this proposal passes (`preflight_passed: true`, `missing_required_specs: []`).
6. The clause preflight exits 0.
7. The new rule file `.claude/rules/backlog-approval-state.md` documents the five-state taxonomy and references the AUQ-evidence requirement.
8. No files outside `E:\GT-KB` are touched. No `applications/` paths touched.

## Verification Plan

Post-implementation report at `bridge/gtkb-backlog-approval-state-taxonomy-slice-1-NNN.md` will include:

1. Migration command output (`sqlite3 groundtruth.db < groundtruth-kb/migrations/2026-05-14-approval-state-column.sql` or equivalent Python runner).
2. Backfill dry-run output (count of rows classified per state).
3. Backfill apply output (rows written, backup created).
4. Full pytest output for the 15 tests in Test Mapping.
5. `SELECT approval_state, COUNT(*) FROM current_work_items WHERE resolution_status='open' GROUP BY approval_state` result.
6. Re-run of `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-backlog-approval-state-taxonomy-slice-1` showing `preflight_passed: true`.
7. Confirmation that `scripts/implementation_authorization.py` was NOT modified in this slice (diff shows no changes to that file).

## Bridge Index Handling

This proposal is filed as `bridge/gtkb-backlog-approval-state-taxonomy-slice-1-001.md`. The corresponding `bridge/INDEX.md` entry will be inserted at the top of the index (newest-first per the bridge protocol) as a new `Document: gtkb-backlog-approval-state-taxonomy-slice-1` block with `NEW: bridge/gtkb-backlog-approval-state-taxonomy-slice-1-001.md`. No prior bridge file or version is deleted or rewritten by this proposal; the append-only audit trail is preserved per `GOV-FILE-BRIDGE-AUTHORITY-001` (live bridge index authority; no deletion of prior versions). The INDEX update itself is being performed out-of-band by the filing harness orchestration (the agent filing this proposal is operating under instructions that explicitly defer the INDEX update step); when this proposal becomes actionable, the INDEX entry insert at the top of the file is the standard bridge-protocol step.

## Applicability Preflight

Run as part of proposal authoring; result embedded below. Codex re-runs at review time per `.claude/rules/codex-review-gate.md` step 3.

- packet_hash: `sha256:fc44ee31cc9bddb6dce8a5f6792500f118b70c7414a14e8d738ab333f2f00a2d`
- bridge_document_name: `gtkb-backlog-approval-state-taxonomy-slice-1`
- content_source: `pending_content`
- content_file: `bridge/gtkb-backlog-approval-state-taxonomy-slice-1-001.md`
- operative_file: `(none)` (pre-INDEX evaluation; updates to operative_file after INDEX insert do not alter spec citations)
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

Clause preflight: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-backlog-approval-state-taxonomy-slice-1 --content-file "E:/GT-KB/bridge/gtkb-backlog-approval-state-taxonomy-slice-1-001.md"` exits `0` (no blocking gaps; 5 must_apply clauses all show evidence_found=yes).

End of proposal.
