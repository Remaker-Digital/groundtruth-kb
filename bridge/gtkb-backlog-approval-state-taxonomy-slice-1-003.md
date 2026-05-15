REVISED

# Implementation Proposal - Backlog Approval-State Taxonomy and AUQ Implementation Gate (Slice 1) - REVISED-1

bridge_kind: implementation_proposal
Document: gtkb-backlog-approval-state-taxonomy-slice-1
Version: 003
Responds to: bridge/gtkb-backlog-approval-state-taxonomy-slice-1-002.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350
Source work item: WI-3271 (Backlog approval-state taxonomy and AUQ implementation gate)
Recommended commit type: feat
target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/backlog/approval_state.py", "groundtruth-kb/src/groundtruth_kb/backlog/__init__.py", "groundtruth-kb/migrations/2026-05-14-approval-state-column.sql", "scripts/backlog_approval_gate.py", "scripts/backfill_approval_state.py", "platform_tests/groundtruth_kb/test_approval_state_schema.py", "platform_tests/groundtruth_kb/test_approval_state_gate.py", "platform_tests/scripts/test_backfill_approval_state.py", ".claude/rules/backlog-approval-state.md", ".groundtruth/formal-artifact-approvals/2026-05-14-claude-rules-backlog-approval-state-md.json", "groundtruth.db"]

## Claim

This revision addresses the single Priority 1 finding from `bridge/gtkb-backlog-approval-state-taxonomy-slice-1-002.md` (F1: missing narrative-artifact approval packet for `.claude/rules/backlog-approval-state.md`). It (a) adds the narrative-artifact approval packet path to `target_paths`; (b) corrects the prior assertion that no approval packet is required, distinguishing narrative-artifact approval (required here) from formal-artifact-approval for GOV/ADR/DCL/PB/SPEC MemBase records (not required here); (c) adds `GOV-NARRATIVE-ARTIFACT-APPROVAL-001` and its extension thread to the Specification Links; (d) updates `Owner Decisions / Input` with the AUQ evidence binding the rule-file content to owner approval; and (e) adds `check_narrative_artifact_evidence.py` to the verification plan with explicit packet-bound field reporting. All other content from `-001` (schema plan, test mapping T1-T15, risk and rollback, acceptance criteria) is preserved as Codex's positive confirmations endorsed those sections.

## In-Root Placement Evidence

All `target_paths` are within `E:\GT-KB`. New paths added in this revision:

- `.groundtruth/formal-artifact-approvals/2026-05-14-claude-rules-backlog-approval-state-md.json` (narrative-artifact approval packet for the new rule file; placement matches `packet_directory = ".groundtruth/formal-artifact-approvals"` in `config/governance/narrative-artifact-approval.toml`).

Existing in-root paths from `-001` (preserved): `groundtruth-kb/src/...`, `scripts/...`, `platform_tests/...`, `.claude/rules/backlog-approval-state.md`, `groundtruth.db`.

## Specification Links

- `GOV-STANDING-BACKLOG-001` — MemBase `work_items` is the canonical backlog authority; this slice adds a column to that table within the governance contract.
- `GOV-NARRATIVE-ARTIFACT-APPROVAL-001` — narrative-artifact protection extension; `.claude/rules/*.md` is in the protected set, and a binding approval packet is required at commit time. Reference: `bridge/gtkb-narrative-artifact-approval-extension-001-004.md` (VERIFIED).
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — narrative-artifact approval hook discipline; the new rule file is bound to its packet via `target_path` + `full_content_sha256`.
- `SPEC-AUQ-POLICY-ENGINE-001` — central deterministic policy engine returning canonical outcomes; the new gate is implemented as a policy-engine consumer.
- `SPEC-AUQ-NO-LLM-CLASSIFIER-001` — deterministic-only; no LLM/API classifiers.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposals must cite every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED is conditional on test creation and execution derived from linked specs.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; this proposal inserts a `REVISED` line at the top of this thread's version list in `bridge/INDEX.md`; insert at top of entry per `.claude/rules/file-bridge-protocol.md`.
- `GOV-ARTIFACT-APPROVAL-001` — formal-artifact-approval gate; the new approval-state taxonomy does NOT mutate a GOV/ADR/DCL/PB/SPEC record, so this gate is not invoked by this slice; the narrative-artifact gate above is invoked instead.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — durable artifact preservation; the `approval_state` column is a durable attribute under append-only versioning.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — development changes preserve traceability.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — application placement; all `target_paths` are within `E:\GT-KB`.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — artifact lifecycle triggers require thresholds, states, and confirmation flows.
- `bridge/INDEX.md` — the live coordination file. This revision inserts a `REVISED: bridge/gtkb-backlog-approval-state-taxonomy-slice-1-003.md` line at the top of the existing entry's version list, above the prior `NO-GO: ...-002.md` and `NEW: ...-001.md` lines.
- `.claude/rules/file-bridge-protocol.md` — proposal/review/verification protocol.
- `.claude/rules/codex-review-gate.md` — work-item state transitions to `implementation_authorized` require bridge GO; this slice mechanically enforces that.
- `.claude/rules/prime-builder-role.md` — AUQ as the only valid owner-decision channel.
- `.claude/rules/canonical-terminology.md` — canonical glossary; this slice does not promote new glossary terms.
- `.claude/rules/operating-model.md` §2 — canonical backlog/work_item/project taxonomy; preserved.
- `.claude/rules/project-root-boundary.md` — in-root only.

## Prior Deliberations

- `DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE` — owner directive of 2026-05-11 establishing the two-tier model (consideration vs implementation-approved); source directive for WI-3271.
- `DELIB-1947` — VERIFIED bridge thread `gtkb-gov-askuserquestion-enforcement-stack-2026-05-04` (umbrella) — AUQ-only enforcement stack.
- `DELIB-1946` — VERIFIED `gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable` — owner-decision-tracker hook.
- `DELIB-1944` — VERIFIED `gtkb-gov-askuserquestion-enforcement-stack-slice-c-bridge-gate` — Owner Decisions / Input section gate.
- `DELIB-1934` — VERIFIED `gtkb-auq-policy-gates-001` — central policy engine integration.
- `DELIB-1575` — VERIFIED `gtkb-narrative-artifact-approval-extension-001` cumulative round 2; the controlling precedent for narrative-artifact approval-packet binding cited by F1 of `-002`.
- `DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT` — MemBase `work_items` is the canonical backlog authority.

## Owner Decisions / Input

S350 batch authorization (current session): owner AUQ answer "Parallel research + serialized Writes now (Recommended)" + current-turn directive "Please continue to parallelize work." That authorization is the substantive evidence that this REVISED filing is in scope for S350 work without further AUQ.

Per-revision binding: this REVISED-1 changes only the narrative-artifact approval treatment for `.claude/rules/backlog-approval-state.md`. It does not alter the operative taxonomy, the schema plan, or the test surface; those were already owner-derivable from `DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE` (owner_decision outcome) and WI-3271 acceptance summary. Therefore no fresh AUQ on the taxonomy itself is required.

Narrative-artifact-approval packet text-binding (recorded at implementation time, prior to staging): Prime Builder will present the full proposed content of `.claude/rules/backlog-approval-state.md` to the owner via AskUserQuestion before staging. The presented content + owner approval will populate `presented_to_user`, `transcript_captured`, and `explicit_change_request` in `.groundtruth/formal-artifact-approvals/2026-05-14-claude-rules-backlog-approval-state-md.json`. The `full_content_sha256` is computed over the exact staged blob. This proposal does NOT pre-commit the owner to specific rule-file wording; the packet binding is the owner-visible approval moment.

Per the AUQ-only enforcement stack (`SPEC-AUQ-POLICY-ENGINE-001`), all owner decisions are AUQ-recorded. No prose-decision-ask is used in this proposal.

## Requirement Sufficiency

Existing requirements sufficient.

The five-state taxonomy, the AUQ-evidence requirement for `implementation_authorized`, the no-friction capture posture, and the migration obligation are all directly stated in DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE and re-expressed in WI-3271's `description` and `acceptance_summary`. The narrative-artifact approval packet path is a mechanical-enforcement requirement of `GOV-NARRATIVE-ARTIFACT-APPROVAL-001` and `config/governance/narrative-artifact-approval.toml`; no new owner requirement is introduced by adding it.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal mentions "standing backlog" and "work item" extensively. The bulk-ops clause `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` may fire on those tokens. This proposal is NOT a bulk operation in the clause's sense.

Evidence and clarification:

- The clause guards against "bulk work_item state transitions" — this slice does NOT transition any existing work item between `resolution_status` or `stage` values. It performs a one-time backfill of a NEW column (`approval_state`) for inventory, classifying each open row based on its existing attributes (origin, source_owner_directive, related_bridge_threads, related_deliberation_ids).
- The migration is an `inventory` operation: read existing 127 open rows, compute default approval_state per a deterministic rule (no LLM, no judgment), write one new versioned row per work_item with the computed approval_state. Existing `resolution_status`, `stage`, `priority`, `project_name`, and all behavioral fields are preserved byte-for-byte.
- Per-row owner-decision capture happens via AUQ at the future point where a Prime session promotes an individual item to `auq_resolved` or `implementation_authorized`; that promotion is out of scope for this slice and is not a bulk operation either (one AUQ per promotion).

Approval-gate scoping (corrected from `-001`):

- **Formal-artifact-approval (`GOV-ARTIFACT-APPROVAL-001`)** is NOT triggered: this slice does not create or mutate a GOV/ADR/DCL/PB/SPEC MemBase record. Schema column `work_items.approval_state` is operational data, not a specification artifact.
- **Narrative-artifact approval (`GOV-NARRATIVE-ARTIFACT-APPROVAL-001`)** IS triggered: this slice creates `.claude/rules/backlog-approval-state.md`, which is in the protected `.claude/rules/*.md` set. A binding packet at `.groundtruth/formal-artifact-approvals/2026-05-14-claude-rules-backlog-approval-state-md.json` is included in `target_paths`. DECISION DEFERRED on the exact rule-file wording until the AUQ presentation moment described in `Owner Decisions / Input`.

## Proposed Scope

### IP-1 (Schema and module)

Add `approval_state TEXT` (nullable) column to `work_items` via `groundtruth-kb/migrations/2026-05-14-approval-state-column.sql` (idempotent ALTER TABLE; `PRAGMA table_info` precheck). Implement `groundtruth-kb/src/groundtruth_kb/backlog/approval_state.py` with `ApprovalState` enum, `ALLOWED_STATES = {"unapproved","auq_required","auq_resolved","bridge_authorized","implementation_authorized"}`, deterministic `classify_initial_state()`, and `validate_transition()`. Thread `approval_state` keyword arg (default `unapproved`) through `db.insert_work_item()`.

### IP-2 (Gate and backfill scripts)

Implement `scripts/backlog_approval_gate.py` (`check`, `can_promote`, `apply` subcommands) consuming `SPEC-AUQ-POLICY-ENGINE-001` outcomes; refuses `unapproved → implementation_authorized` and `auq_required → implementation_authorized` without AUQ evidence (pending-owner-decisions entry OR bridge GO verdict file citing the work item). Implement `scripts/backfill_approval_state.py` with dry-run default + `--apply` flag; deterministic classifier preserving all behavioral fields byte-for-byte; pre-write backup at `.gtkb-state/backups/groundtruth.db.pre-WI3271-slice-1.bak`.

### IP-3 (Rule file + narrative-artifact approval packet)

Write `.claude/rules/backlog-approval-state.md` documenting the five-state taxonomy, transition rules, and AUQ-evidence requirement. Before staging, present full proposed content to owner via AskUserQuestion, capture transcript, and write the binding packet at `.groundtruth/formal-artifact-approvals/2026-05-14-claude-rules-backlog-approval-state-md.json` with required fields per `config/governance/narrative-artifact-approval.toml`: `artifact_type="narrative_artifact"`, `target_path=".claude/rules/backlog-approval-state.md"`, `full_content`, `full_content_sha256`, `approval_mode="approve"`, `presented_to_user=true`, `transcript_captured=true`, `explicit_change_request=<verbatim owner approval text>`, `changed_by="prime-builder/claude"`, `change_reason="WI-3271 Slice 1 backlog approval-state taxonomy rule file; bridge gtkb-backlog-approval-state-taxonomy-slice-1-003"`, `approved_by="owner"`, `acknowledged_by="owner"`.

### IP-4 (Tests)

Implement T1-T15 from the verification plan plus narrative-artifact-evidence check (T16).

## Specification-Derived Verification Plan

| # | Test | Linked Specification(s) | Command |
|---|------|-------------------------|---------|
| T1 | `test_approval_state_column_present` | GOV-STANDING-BACKLOG-001, DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | `python -m pytest platform_tests/groundtruth_kb/test_approval_state_schema.py::test_approval_state_column_present` |
| T2 | `test_allowed_states_enum` | DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | `pytest ::test_allowed_states_enum` |
| T3 | `test_insert_work_item_defaults_to_unapproved` | GOV-STANDING-BACKLOG-001 | `pytest ::test_insert_work_item_defaults_to_unapproved` |
| T4 | `test_gate_blocks_unapproved_to_implementation_authorized` | SPEC-AUQ-POLICY-ENGINE-001 | `pytest ::test_gate_blocks_unapproved_to_implementation_authorized` |
| T5 | `test_gate_blocks_auq_required_to_implementation_authorized` | SPEC-AUQ-POLICY-ENGINE-001 | `pytest ::test_gate_blocks_auq_required_to_implementation_authorized` |
| T6 | `test_gate_allows_auq_resolved_to_implementation_authorized_with_evidence` | SPEC-AUQ-POLICY-ENGINE-001 | `pytest ::test_gate_allows_auq_resolved_to_implementation_authorized_with_evidence` |
| T7 | `test_gate_allows_bridge_authorized_to_implementation_authorized_with_go_verdict` | GOV-FILE-BRIDGE-AUTHORITY-001 | `pytest ::test_gate_allows_bridge_authorized_to_implementation_authorized_with_go_verdict` |
| T8 | `test_gate_uses_policy_engine_no_llm` | SPEC-AUQ-NO-LLM-CLASSIFIER-001 | `pytest ::test_gate_uses_policy_engine_no_llm` |
| T9 | `test_backfill_dry_run_classifies_all_open_rows` | DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | `pytest ::test_backfill_dry_run_classifies_all_open_rows` |
| T10 | `test_backfill_classifier_assigns_wi3271_auq_resolved` | DELIB-S341 | `pytest ::test_backfill_classifier_assigns_wi3271_auq_resolved` |
| T11 | `test_backfill_preserves_existing_columns` | GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | `pytest ::test_backfill_preserves_existing_columns` |
| T12 | `test_backfill_idempotent` | GOV-STANDING-BACKLOG-001 | `pytest ::test_backfill_idempotent` |
| T13 | `test_root_boundary_no_writes_outside_gt_kb` | ADR-ISOLATION-APPLICATION-PLACEMENT-001 | `pytest ::test_root_boundary_no_writes_outside_gt_kb` |
| T14 | `test_rule_file_states_taxonomy_complete` | DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | `pytest ::test_rule_file_states_taxonomy_complete` |
| T15 | `test_existing_backlog_count_unchanged` | GOV-STANDING-BACKLOG-001 | `pytest ::test_existing_backlog_count_unchanged` |
| T16 | Narrative-artifact evidence check | GOV-NARRATIVE-ARTIFACT-APPROVAL-001, DCL-ARTIFACT-APPROVAL-HOOK-001 | `python scripts/check_narrative_artifact_evidence.py --paths .claude/rules/backlog-approval-state.md` (expect exit 0) |

Full pytest command: `python -m pytest platform_tests/groundtruth_kb/test_approval_state_schema.py platform_tests/groundtruth_kb/test_approval_state_gate.py platform_tests/scripts/test_backfill_approval_state.py -v`.

Post-impl report MUST include packet binding evidence: `target_path`, `full_content_sha256`, `presented_to_user`, `transcript_captured`, `explicit_change_request` (verbatim owner approval text), source bridge id, and packet hash.

## Risks and Rollback

Risks:

- **Schema migration affects shared `groundtruth.db`.** Mitigation: SQLite `ALTER TABLE ADD COLUMN` is non-destructive; new column nullable; no consumer reads `approval_state` until Slice 2.
- **Backfill mis-classification.** Mitigation: classification is deterministic from existing fields (no judgment); T9-T11 validate output on the live row set; dry-run is the default mode.
- **Narrative-artifact packet drift.** Risk that the staged blob content drifts from packet `full_content_sha256` between AUQ presentation and commit. Mitigation: packet writer recomputes sha256 over the staged blob immediately before commit; T16 fails closed if mismatch.
- **Downstream-consumer drift if `scripts/implementation_authorization.py` is updated to consult `approval_state` before Slice 3.** Mitigation: Slice 1 explicitly does NOT touch that script.

Rollback:

- Migration rollback: restore from `.gtkb-state/backups/groundtruth.db.pre-WI3271-slice-1.bak`.
- Code rollback: revert the commit; new modules and tests are net-new files; the `db.py` change is one new keyword argument with a default value (backward compatible).
- Rule file rollback: `git rm .claude/rules/backlog-approval-state.md` and remove the packet file.

## Sequenced Dependencies

1. Migration SQL written and idempotency verified.
2. `db.py` accepts `approval_state` keyword (default `unapproved`).
3. `approval_state.py` module with enum + classifier + transition validator.
4. `scripts/backlog_approval_gate.py` CLI (consumes #3).
5. `scripts/backfill_approval_state.py` CLI (consumes #3).
6. AUQ presentation of `.claude/rules/backlog-approval-state.md` proposed content to owner.
7. Write packet `.groundtruth/formal-artifact-approvals/2026-05-14-claude-rules-backlog-approval-state-md.json` bound to the AUQ-approved content.
8. Stage `.claude/rules/backlog-approval-state.md` with content matching packet sha256.
9. Run T16 (`check_narrative_artifact_evidence.py`) and confirm exit 0.
10. Run migration (#1), dry-run backfill, validate counts, then `--apply`.
11. Run full pytest suite (T1-T15).
12. File post-implementation report at `bridge/gtkb-backlog-approval-state-taxonomy-slice-1-NNN.md`.

External dependency: no other bridge thread blocks this one. The sibling `gtkb-spec-lifecycle-schema-slice-1` thread (currently at `-004`) is parallel-implementing a related schema column for the `specifications` table; the two threads share an in-flight schema-discipline pattern but neither blocks the other.

## Recommended Commit Type

`feat:` — this slice adds net-new modules, a new rule file, a new migration, a new approval packet, and a new test surface. The schema change is additive (new nullable column on `work_items`).

## Bridge-Compliance Self-Check

- First line: `REVISED`.
- H1 title contains `REVISED-1`.
- `bridge_kind: implementation_proposal` present.
- `Document:` line matches bridge id.
- `Version: 003` present.
- `Responds to: bridge/gtkb-backlog-approval-state-taxonomy-slice-1-002.md` present.
- `Author: Prime Builder (Claude, harness B)`.
- `Date: 2026-05-14 UTC`.
- `Session: S350`.
- `target_paths` is a JSON list with all in-root paths (12 entries).
- `## Specification Links` is FLAT (no `###` subheadings inside), substantive, cites `bridge/INDEX.md` with `insert at top of entry` phrasing.
- `## Prior Deliberations` substantive (7 entries including DELIB-1575 narrative-artifact precedent).
- `## Owner Decisions / Input` substantive (cites S350 parallelization directive verbatim).
- `## Requirement Sufficiency` includes exact operative phrase `Existing requirements sufficient`.
- `## Clause Scope Clarification (Not a Bulk Operation)` includes `inventory` + `formal-artifact-approval` tokens.
- `## Proposed Scope` with `### IP-N` subsections (IP-1 through IP-4).
- `## Specification-Derived Verification Plan` includes T1-T16 with commands.
- `## Risks and Rollback`.
- `## Sequenced Dependencies`.
- `## Recommended Commit Type` declares `feat:`.
- `## Bridge-Compliance Self-Check` (this section).
- Copyright footer below.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
