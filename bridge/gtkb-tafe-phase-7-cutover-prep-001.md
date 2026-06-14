NEW

bridge_kind: implementation_proposal
Document: gtkb-tafe-phase-7-cutover-prep
Version: 001
Author: Prime Builder (Claude, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 6b377e3a-f3d6-453f-bf33-9f3b0631595b
author_model: claude-opus-4-7
author_model_version: 4.7
author_model_configuration: 1M context, explanatory style
Date: 2026-06-14 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-6-7-CUTOVER-WI-4508-4509-4510
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4510

target_paths: ["groundtruth-kb/src/groundtruth_kb/tafe_cutover_evidence.py", "groundtruth-kb/src/groundtruth_kb/tafe_bridge_ingestion.py", "groundtruth-kb/src/groundtruth_kb/tafe_index_completeness.py", "groundtruth-kb/src/groundtruth_kb/tafe_index_sync.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "bridge/INDEX.md", "groundtruth-kb/tests/test_tafe_cutover_evidence.py", "groundtruth-kb/tests/test_tafe_bridge_ingestion.py", "platform_tests/scripts/test_bridge_index_document_header_consistency.py"]

# TAFE Phase 7 Cutover Preparation: Sync-Lag Closure + Lost-Slug Investigation + INDEX Slug-Prefix Normalization

## Problem

WI-4509 (cutover-evidence gathering) is VERIFIED at `bridge/gtkb-wi4509-cutover-evidence-006.md` (Codex harness A). A live re-run of `gt flow cutover-evidence --json` in this session confirms the tool is correctly non-mutating against `bridge/INDEX.md` (PRE/POST SHA-256 identical; tool reports `mutated: false`), but the evidence packet is decisively not cutover-clean.

Owner standing directive (this session, recorded as AUQ answer): "If evidence shows ANY mismatch, recommend NOT cutting over." The deeper analysis at `.gtkb-state/tmp/wi4509-cutover-analysis-2026-06-14.md` decomposes the mismatches into four classes:

1. 6 `shadow_instance_missing` records on live Prime-actionable threads (pure swarm lag; self-healing on read).
2. 4 paired `instance_status_mismatch + latest_status_token_mismatch` on recently-VERIFIED threads (same self-healing pattern).
3. 5 lost-from-TAFE slugs that are still in live INDEX (genuine defects): `gtkb-adr-dcl-clause-test-enforcement`, `gtkb-claude-code-bridge-status-thread-automation`, `gtkb-core-spec-intake`, `gtkb-project-completion-scanner-addressing-thread-fix`, `gtkb-role-enhancement`.
4. 1 slug-prefix defect in `bridge/INDEX.md` itself: `Document: sp1-dispatch-reliability-prime-handoff` (no `gtkb-` prefix) paired with file path `bridge/gtkb-sp1-dispatch-reliability-prime-handoff-001.md`. TAFE's parser takes the Document header literally, producing both an `extra_block` ("sp1-...") and a paired `lost_block` ("gtkb-sp1-...").

A fifth class (628 of 634 `lost_blocks` that are truly absent from INDEX due to historical archival) is governance scope and is intentionally NOT addressed in this slice. It is a policy decision about whether TAFE retains history INDEX archives; it does not block cutover technically.

This slice closes classes 1-4 so the next `gt flow cutover-evidence --json` run reports cutover-clean with respect to those classes, leaving only the (out-of-scope) governance question about class 5.

This slice does NOT initiate WI-4510 cutover. WI-4510's deliverable (file the cutover bridge proposal with owner-AUQ gate) is unchanged. PAUTH `forbidden_operations` includes `cutover`; this slice stays within `source`, `test_addition`, `config`.

## Specification Links

- SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA - TAFE umbrella; cutover-clean predicate is part of Phase-7 acceptance.
- SPEC-TAFE-R3 - flow lifecycle and instance state correctness.
- SPEC-TAFE-R7 - observability evidence (cutover-evidence is the canonical Phase-7 evidence surface).
- GOV-FILE-BRIDGE-AUTHORITY-001 - INDEX.md remains canonical; this slice does NOT change that.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - durable artifacts, append-only, machine-verifiable predicates.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - artifact-first development bias.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - capture-threshold discipline for artifact mutation.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal's linkage gate.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - verification mandate this proposal honors.

## Prior Deliberations

- `bridge/gtkb-wi4509-cutover-evidence-006.md` - Codex VERIFIED verdict (harness A) on WI-4509 cutover-evidence gathering. Verdict explicitly notes: "WI-4510 remains owner-gated; this verdict does not authorize cutover, deployment, generated-view authority changes, or formal spec promotion."
- `DELIB-20263195` - Owner AUQ 2026-06-13 authorizing full TAFE INDEX cutover sequence (WI-4508 -> 4509 -> 4510). PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-6-7-CUTOVER-WI-4508-4509-4510 was created under this authorization.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D3-20260612` - TAFE project formation (Step 5); WI-4510 was created here as "File bridge proposal for TAFE-authoritative cutover; requires LO review + owner AUQ approval (D11). Not auto-promoted."
- `bridge/gtkb-wi4509-cutover-evidence-005.md` - Prime Builder REVISED report (harness B) closing the F1 finding from -004 (WI-4496 dependency rewire via governed API to WI-4509 v2 with `depends_on_work_items: WI-4508`).
- `bridge/gtkb-wi4509-cutover-evidence-004.md` - Codex NO-GO (harness A) on Prime's initial -003 NEW report. F1 was the only blocking finding: WI-4509 still depended on the SUPERSEDED WI-4496.
- `bridge/gtkb-wi4509-cutover-evidence-003.md` - Prime Builder NEW (harness B) post-implementation report.
- `bridge/gtkb-wi4509-cutover-evidence-002.md` - Codex GO (harness A) of original -001 proposal.
- `bridge/gtkb-wi4509-cutover-evidence-001.md` - Prime Builder NEW (harness B) original proposal: implement read-only `gt flow cutover-evidence` and document Phase-7 evidence shape.

## Owner Decisions / Input

- Owner standing directive 2026-06-13 (`DELIB-20263195`): the WI-4508 -> WI-4509 -> WI-4510 sequence is authorized; WI-4510 retains its closing owner-AUQ gate.
- Owner this session 2026-06-14 (AUQ answer recorded in session transcript): authorized "File Phase-7 prep NEW (A+B+C slice)" after reviewing the deeper-breakdown analysis at `.gtkb-state/tmp/wi4509-cutover-analysis-2026-06-14.md`. The owner-selected option was Item A among the four offered (Item A = file Phase-7 prep NEW; Item B = file WI-4510 NEW with explicit override; Item C = stand down zero-mutations; Item D = answer governance question D first).
- This proposal does NOT request a cutover decision. WI-4510 governance is unchanged; the cutover-AUQ remains owner-gated when WI-4510's own cutover proposal is filed.

## Scope: Three Items

### Item A. Sync-lag closure - make cutover-evidence idempotent

Current behavior: `gt flow cutover-evidence --json` performs first-touch shadow-population DURING the query. Today's run showed `action_distribution: {created: 6, updated: 4, unchanged: 318}` and `replan_instances_written: 10` / `replan_artifacts_written: 26`. This means a first invocation always reports `contention_zero: False` even when the system is healthy.

Proposed design: add a deterministic pre-pass `gt flow shadow-sync` (or equivalent) that populates shadow records from live INDEX, so a subsequent `gt flow cutover-evidence --json` reports `contention_zero: true` without mutating shadow during the read. Cutover-clean predicate becomes meaningful: `contention_zero AND no fidelity_mismatches AND no true-defect lost_blocks AND no extra_blocks`.

Files: `groundtruth-kb/src/groundtruth_kb/tafe_index_sync.py` (or `tafe_bridge_ingestion.py`), `groundtruth-kb/src/groundtruth_kb/cli.py` (subcommand wiring), `groundtruth-kb/tests/test_tafe_cutover_evidence.py` (regression).

Acceptance: second invocation of `gt flow cutover-evidence --json` against a freshly-populated shadow reports `contention_zero: true` and `replan_instances_written: 0`.

### Item B. 5-slug lost-from-TAFE investigation

These five slugs exist in live `bridge/INDEX.md` but TAFE shadow has dropped them:

- gtkb-adr-dcl-clause-test-enforcement
- gtkb-claude-code-bridge-status-thread-automation
- gtkb-core-spec-intake
- gtkb-project-completion-scanner-addressing-thread-fix
- gtkb-role-enhancement

Candidate causes:

(a) Bridge thread merge, rename, or status transition (e.g., earlier WITHDRAWN then re-opened) that TAFE pruned but INDEX retained.
(b) Initial-sync filter condition that skipped these classes (e.g., excluded slugs whose Document line was older than some threshold).
(c) Shadow corruption recovery dropped them.

Deliverables:

- Diagnostic note in the post-implementation report explaining which case applies.
- Fix that prevents the class. If the cause is identifiable, a single targeted fix; if not, a defensive `tafe shadow-rebuild` subcommand that idempotently re-ingests from live INDEX.
- Test that asserts these 5 slugs reappear in shadow after the fix.

Files: `groundtruth-kb/src/groundtruth_kb/tafe_index_completeness.py`, `groundtruth-kb/src/groundtruth_kb/tafe_bridge_ingestion.py`, `groundtruth-kb/tests/test_tafe_cutover_evidence.py`.

Acceptance: post-fix, `gt flow cutover-evidence --json` reports the 5 named slugs in `present_count`, not in `lost_blocks`.

### Item C. INDEX slug-prefix normalization

The defect: `bridge/INDEX.md` contains `Document: sp1-dispatch-reliability-prime-handoff` but the file path on the next line is `bridge/gtkb-sp1-dispatch-reliability-prime-handoff-001.md`. The Document header is missing the canonical `gtkb-` prefix that the filename root carries.

Two-part fix:

(1) One-off correction: amend that one `Document:` line to `gtkb-sp1-dispatch-reliability-prime-handoff` to match the filename. This is a single-line edit to `bridge/INDEX.md`.

(2) Doctor check: `_check_bridge_index_document_header_consistency` (or similar) that asserts every `Document: <slug>` line in INDEX has a slug equal to the slug-root of its corresponding `<status>: bridge/<slug>-NNN.md` lines. WARN severity initially; promotable to FAIL after one clean run cycle.

Files: `bridge/INDEX.md` (single-line edit), `groundtruth-kb/src/groundtruth_kb/project/doctor.py` (new check), `platform_tests/scripts/test_bridge_index_document_header_consistency.py` (regression).

Acceptance: post-fix, `extra_blocks: []` and the sp1 slug no longer appears in `lost_blocks`.

## Test Plan

### Specification-derived test mapping

| Linked Specification | Test(s) created or identified | Coverage shape |
|---|---|---|
| SPEC-TAFE-R3 | groundtruth-kb/tests/test_tafe_cutover_evidence.py::test_shadow_sync_recovers_dropped_slugs | Asserts the 5-slug class (Item B) is restored after fix |
| SPEC-TAFE-R7 | groundtruth-kb/tests/test_tafe_cutover_evidence.py::test_cutover_evidence_contention_zero_after_shadow_sync | Asserts Item A makes second-call contention_zero=True |
| GOV-FILE-BRIDGE-AUTHORITY-001 | platform_tests/scripts/test_bridge_index_document_header_consistency.py::test_all_document_headers_match_slug_root | Asserts Item C: every INDEX Document line equals its bridge file slug-root |
| SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA | groundtruth-kb/tests/test_tafe_cutover_evidence.py::test_cutover_evidence_clean_after_prep | End-to-end: with all three items implemented, cutover-evidence reports cutover-clean (excluding the 628-class governance question) |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | (this proposal's verification gate) | Each linked spec has at least one mapped test executed |

### Execution commands (post-impl)

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb/tests/test_tafe_cutover_evidence.py -q --tb=short
groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb/tests/test_tafe_bridge_ingestion.py -q --tb=short
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_bridge_index_document_header_consistency.py -q --tb=short
groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/tafe_cutover_evidence.py groundtruth-kb/src/groundtruth_kb/tafe_bridge_ingestion.py groundtruth-kb/src/groundtruth_kb/tafe_index_completeness.py groundtruth-kb/src/groundtruth_kb/cli.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/tafe_cutover_evidence.py groundtruth-kb/src/groundtruth_kb/tafe_bridge_ingestion.py groundtruth-kb/src/groundtruth_kb/tafe_index_completeness.py groundtruth-kb/src/groundtruth_kb/cli.py
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli flow shadow-sync   # Item A new subcommand if (1)-design chosen
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli flow cutover-evidence --json   # expect contention_zero=True, 0 fidelity_mismatches for the 10 named slugs, 0 extra_blocks, no sp1 / 5-slug entries in lost_blocks
```

### Acceptance Criteria

1. Second invocation of `gt flow cutover-evidence --json` returns `contention_zero: true`.
2. The 6 `shadow_instance_missing` slugs from this session's evidence are present in TAFE shadow with correct status.
3. The 4 paired `instance_status_mismatch + latest_status_token_mismatch` slugs from this session's evidence are resolved.
4. The 5 lost-from-TAFE slugs (`gtkb-adr-dcl-clause-test-enforcement`, `gtkb-claude-code-bridge-status-thread-automation`, `gtkb-core-spec-intake`, `gtkb-project-completion-scanner-addressing-thread-fix`, `gtkb-role-enhancement`) appear in `present_count`, not `lost_blocks`.
5. The sp1 INDEX slug-prefix defect is fixed; `extra_blocks: []`; doctor check `_check_bridge_index_document_header_consistency` PASS.
6. The only remaining `lost_blocks` are the 628-class historical archival drift (deferred to governance question D in the analysis).

## Requirement Sufficiency

Existing requirements sufficient. SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA + SPEC-TAFE-R3 + SPEC-TAFE-R7 + GOV-FILE-BRIDGE-AUTHORITY-001 together constrain the scope. No new specifications proposed.

## Recommended Commit Type

`fix:` - the slice fixes three pre-cutover defects (sync-lag self-healing-during-read, lost-slug shadow recovery, INDEX slug-prefix mismatch). Code changes are repair-class plus a new diagnostic subcommand; no net-new product capability.

## Risk and Rollback

- Risk A1: Adding `gt flow shadow-sync` changes CLI surface. Mitigation: additive (no removal); semver-compatible. Rollback: revert subcommand wiring.
- Risk A2: The shadow-sync pre-pass may interact with concurrent dispatched workers also touching TAFE shadow. Mitigation: use existing TAFE write-lock; idempotent insertion.
- Risk B1: The 5-slug fix may require a one-off shadow backfill. Mitigation: backfill is idempotent and append-only; existing shadow records are not mutated.
- Risk C1: Editing `bridge/INDEX.md` `Document:` line is a one-line mutation. Concurrent bridge writers may conflict. Mitigation: use the same `atomic_index_update` path bridge writes use today.
- Risk C2: The doctor check may flag historical INDEX entries with the same defect. Mitigation: WARN-only initially; FAIL promotion after a clean cycle.
- WI-4510 cutover is NOT initiated by this slice; INDEX.md remains canonical authority throughout.

## Out of Scope

- WI-4510 governed cutover itself (separate later thread; retains owner-AUQ gate).
- Governance question D: should TAFE retain history INDEX archives (current behavior, ~628 lost_blocks) or prune in lockstep with INDEX archival? Recommend filing a separate AUQ when WI-4510's cutover proposal is being drafted.
- Any formal SPEC promotion. PAUTH forbids `formal_spec_promotion`.
- Any commit, push, or deployment in the post-impl report. The author will leave changes in the working tree per dispatched-worker discipline.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
