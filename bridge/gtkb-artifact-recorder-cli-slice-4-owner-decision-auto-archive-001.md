NEW
author_identity: Claude
author_harness_id: B
author_session_context_id: 2026-05-30T15-01-39Z-prime-builder-s373
author_model: claude-opus-4-7
author_model_version: 1m
author_model_configuration: reasoning=explanatory

Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-PARALLEL-BATCH-GT-BRIDGE-PROPOSE-CLI
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-3263

# Implementation Proposal (Slice 4) - GTKB-ARTIFACT-RECORDER-CLI - Owner-Decision Auto-Archive Integration

**Document:** `gtkb-artifact-recorder-cli-slice-4-owner-decision-auto-archive`
**Status:** `NEW`
**Version:** 001
**Date:** 2026-05-30
**Author:** Prime Builder (Claude Code, harness B)
**Session:** S373
**Recommended commit type:** `feat:` (adds new helper module + tests + env-gated integration call; net-new capability with default-off rollout)

target_paths:
- groundtruth-kb/src/groundtruth_kb/owner_decision/__init__.py
- groundtruth-kb/src/groundtruth_kb/owner_decision/auto_archive.py
- .claude/hooks/owner-decision-tracker.py
- platform_tests/owner_decision/__init__.py
- platform_tests/owner_decision/test_auto_archive.py
- platform_tests/hooks/test_owner_decision_tracker.py
- bridge/gtkb-artifact-recorder-cli-slice-4-owner-decision-auto-archive-001.md
- bridge/INDEX.md

## Claim

Slice 4 closes the empirically-quantified ~3x gap between AUQ-resolution detection
(601 cumulative resolutions tracked in `memory/pending-owner-decisions.md`) and
canonical Deliberation Archive archival (200 source_type=owner_conversation
deliberations, 127 in the last 30 days). The proposed work adds an in-process
auto-archive helper that invokes the Slice 1 `record_deliberation` service when
the owner-decision-tracker detects a resolved AUQ that crosses the capture
threshold per the deliberation protocol.

Classification is deterministic (no LLM) per `SPEC-AUQ-NO-LLM-CLASSIFIER-001`.
Rollout is env-gated default-off (`GTKB_AUQ_AUTO_ARCHIVE=1` opt-in) so the
integration ships without changing default tracker behavior; the env gate flips
to default-on only after observation-period evidence supports it (a follow-on
Slice 4-B if needed).

This advances the GTKB-ARTIFACT-RECORDER-CLI program by automating a recurring
plumbing surface that today produces ~3-line AI-mediated archive calls per
in-scope owner decision. Per `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`,
repetitive plumbing belongs in services. WI-3263 is the standing authorization
work-item for the ARTIFACT-RECORDER-CLI advance; its title ("file the scoping
bridge proposal per its Next step field") is narrowly stale because the Slice 0
scoping was filed and reached GO at `-004` before being superseded at `-005`;
the broader PAUTH scope text explicitly lists "ARTIFACT-RECORDER-CLI advance"
which Slice 4 continues.

## Requirement Sufficiency

Existing requirements sufficient. The governing surface
(`SPEC-AUQ-POLICY-ENGINE-001`, `SPEC-AUQ-NO-LLM-CLASSIFIER-001`,
`SPEC-2098`, `GOV-ARTIFACT-APPROVAL-001`, the deliberation-protocol rule,
the prime-builder role rule's AUQ-only enforcement clause, and
`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`) collectively articulate the
behavior contract Slice 4 implements. No new requirements or specifications
need owner approval before implementation.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001
- GOV-ARTIFACT-APPROVAL-001
- PB-ARTIFACT-APPROVAL-001
- ADR-ARTIFACT-FORMALIZATION-GATE-001
- DCL-ARTIFACT-APPROVAL-HOOK-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- GOV-STANDING-BACKLOG-001
- SPEC-AUQ-POLICY-ENGINE-001
- SPEC-AUQ-NO-LLM-CLASSIFIER-001
- SPEC-2098
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE
- DELIB-0874
- DELIB-0835
- file bridge protocol rule (.claude/rules/file-bridge-protocol.md)
- codex review gate rule (.claude/rules/codex-review-gate.md)
- deliberation protocol rule (.claude/rules/deliberation-protocol.md)
- prime-builder role rule (.claude/rules/prime-builder-role.md)
- canonical terminology rule (.claude/rules/canonical-terminology.md)
- project root boundary rule (.claude/rules/project-root-boundary.md)
- operating model rule (.claude/rules/operating-model.md)

## Prior Deliberations

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — parent owner-decision establishing the active-pursuit mandate; names GTKB-ARTIFACT-RECORDER-CLI as the first concrete manifestation.
- `DELIB-S350-BATCH7-GT-BRIDGE-PROPOSE-CLI` — current owner-approval evidence for PAUTH covering this work; deterministic-services parallel batch amended scope.
- `DELIB-1934 v1` — VERIFIED bridge thread `gtkb-auq-policy-gates-001` (10 versions); the AUQ policy engine spec implementation precedent.
- `DELIB-1888 v1` — VERIFIED bridge thread `gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001` (10 versions); the tracker's last substantive design refinement.
- `DELIB-2138 v1` — VERIFIED bridge thread `gtkb-artifact-recorder-cli-slice-1-deliberations-record` (8 versions); Slice 1 establishes the `record_deliberation` in-process service this work reuses.
- `DELIB-2136 v1` — VERIFIED bridge thread `gtkb-artifact-recorder-cli-slice-2-spec-record` (6 versions); Slice 2 establishes the create-only spec-record service pattern.
- `DELIB-2226 v1` — VERIFIED bridge thread `gtkb-artifact-recorder-cli-slice-3-scoping` (5 versions); Slice 3 establishes governed versioning via `gt spec update`.
- `DELIB-0835` — formal-artifact-approval/audit-trail owner decision; directly constrains the approval-packet behavior the existing CLI preserves and which this slice reuses unchanged.
- `DELIB-0874` — artifact-oriented governance broader framing; the deterministic-services principle extends this.

No retrieved deliberation waives formal approval evidence or requires LLM-based classification. The auto-archive path preserves both invariants by reusing the existing `record_deliberation` service (which constructs/validates packets in-process) and a deterministic frozen-set classifier (no LLM dependency).

## Owner Decisions / Input

This proposal depends on the following owner authorizations and AskUserQuestion answers:

1. **Owner AUQ at this session (2026-05-30, S373)** — Continuation track selection for GTKB-ARTIFACT-RECORDER-CLI. The owner selected the "File Slice 4: owner-decision packet recording" option from a four-option AUQ presented after Slices 1-3 were confirmed VERIFIED, with the description: "Would add `gt owner-decision record` (or extend `gt deliberations record`) so AUQ outcomes auto-archive as structured DELIB records with packets". This proposal implements that selection via the integration path (the CLI exists from Slice 1; the missing piece is hook-side auto-invocation), with the empirical ~3x gap surfaced in the same turn before drafting.

2. **`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` (2026-04-27, S312)** — Owner decision establishing the active-pursuit mandate for plumbing-to-service work. Repeated owner-decision archival is itself a plumbing surface; the AUQ-resolution-to-DELIB pipeline is the bias case this principle was articulated to address.

3. **`DELIB-S350-BATCH7-GT-BRIDGE-PROPOSE-CLI` (2026-05-15, S350)** — Owner-approval evidence for the PAUTH covering this work (`PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-PARALLEL-BATCH-GT-BRIDGE-PROPOSE-CLI`). Allowed mutation classes: `hook_upgrade`, `cli_extension`, `test_addition`, `spec_status_promotion`. Slice 4's planned changes fit the first three classes exactly.

No further owner decisions are required before VERIFIED. The env-gated default-off rollout means landing this slice has zero default behavior change; an explicit owner decision to set `GTKB_AUQ_AUTO_ARCHIVE=1` (or to flip the default in a follow-on) is a separate later decision.

## Scope

### In scope

1. **Helper module: `groundtruth-kb/src/groundtruth_kb/owner_decision/auto_archive.py`** (new). Exposes:
   - `DecisionForArchive` (frozen dataclass): the subset of tracker `DecisionEntry` fields needed for archival (decision_id, question, options, answer, resolved_at, session_id, detected_via).
   - `should_auto_archive(decision) -> tuple[bool, str]`: deterministic classification. Returns `(False, reason)` for non-AUQ-detected, unresolved, empty-answer, or out-of-scope-content decisions; returns `(True, "in-scope owner decision")` otherwise. The out-of-scope pattern set is a frozen tuple constant in the module.
   - `archive_decision(decision, *, config=None, dry_run=False) -> dict`: builds a temp content file under `.tmp/`, calls `record_deliberation` from `cli_deliberations_record` in-process with `source_type="owner_conversation"`, `outcome="owner_decision"`, cleans up the temp file in a finally block.

2. **Package init: `groundtruth-kb/src/groundtruth_kb/owner_decision/__init__.py`** (new). Empty package marker plus a `__all__` listing the public surface.

3. **Hook integration: `.claude/hooks/owner-decision-tracker.py`** (modified). At the resolve-decision append point, add an env-gated call that builds a `DecisionForArchive` from the existing `DecisionEntry`, calls `should_auto_archive`, and if positive calls `archive_decision`. Failures are caught and appended to a JSONL failure log; the notepad-tier write remains the load-bearing record. The env gate `GTKB_AUQ_AUTO_ARCHIVE` defaults to `0` so default tracker behavior is unchanged.

4. **Tests: `platform_tests/owner_decision/__init__.py` (new)** and **`platform_tests/owner_decision/test_auto_archive.py` (new)**:
   - `test_in_scope_resolved_decision_archives` — DecisionForArchive with detected_via=ask_user_question, non-empty answer, in-scope text → archive_decision returns a DELIB id.
   - `test_unresolved_decision_skipped` — empty resolved_at → should_auto_archive returns (False, "unresolved").
   - `test_out_of_scope_answer_skipped` — answer of acknowledgement-only text → should_auto_archive returns (False, "out-of-scope content").
   - `test_non_auq_decision_skipped` — detected_via not equal to "ask_user_question" → should_auto_archive returns (False, "not an AUQ").
   - `test_idempotency_same_decision_id_no_double_archive` — calling archive_decision twice with same decision_id returns the existing DELIB id (relies on `record_deliberation`'s existing source_ref+content_hash idempotency).
   - `test_classification_is_deterministic` — should_auto_archive returns same result on repeated calls with same input.
   - `test_archive_decision_uses_record_deliberation_service` — patches `record_deliberation` to verify the request shape (source_type=owner_conversation, outcome=owner_decision, auq_id=decision_id).

5. **Failure log path**: tracker uses `.gtkb-state/owner-decision-auto-archive/failures.jsonl` for graceful-degradation auditing. Tested via a tracker-side test (added to existing `platform_tests/hooks/test_owner_decision_tracker.py` — one new test).

### Out of scope

- Changing the env gate default from `0` to `1` (deferred to a Slice 4-B observation-period proposal).
- New CLI subcommand of the form the AUQ described as an alternative; the integration path is sufficient and avoids surface duplication.
- Modifying `record_deliberation` itself (the Slice 1 service is reused unchanged).
- Doctor health check for auto-archive rate (deferred; if the env gate stays off, no health check is required).
- ChromaDB indexing changes (none; reused unchanged via `record_deliberation`).
- Backfilling the ~401 historical AUQ resolutions that were tracked but never archived (a separate question; archival of historical state requires owner direction).

## Test Plan

### Spec-to-test mapping

| Spec | Verifying step |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | Applicability preflight PASS + this thread reaches VERIFIED through INDEX. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Applicability preflight reports `missing_required_specs: []`. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | This Spec-to-test mapping + targeted pytest run executed against the implementation in the post-impl report. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | All new files land under `E:\GT-KB`; tests assert helper output paths stay in-root. |
| GOV-ARTIFACT-APPROVAL-001 | `test_archive_decision_uses_record_deliberation_service` asserts approval-packet construction is unchanged (reused via `record_deliberation`). |
| PB-ARTIFACT-APPROVAL-001 | Same as above; the approval-packet protected-artifact pathway is preserved. |
| ADR-ARTIFACT-FORMALIZATION-GATE-001 | The gate hook continues to fire on raw API paths because the helper uses the governed `record_deliberation` service which already integrates with the gate. |
| DCL-ARTIFACT-APPROVAL-HOOK-001 | Helper does not bypass the hook; verified by test using a fake `record_deliberation` that simulates hook-blocked write. |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | Helper output is a structured DELIB record, not a notepad entry — satisfied by the integration call site. |
| ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 | Same as above. |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | Reuses `record_deliberation`'s existing lifecycle handling. |
| GOV-STANDING-BACKLOG-001 | WI-3263 is the standing-backlog item this slice advances; no bulk-ops; the cited PAUTH's `included_work_item_ids` covers WI-3263. |
| SPEC-AUQ-POLICY-ENGINE-001 | Classification is deterministic (no LLM); verified by `test_classification_is_deterministic` and `test_out_of_scope_answer_skipped`. |
| SPEC-AUQ-NO-LLM-CLASSIFIER-001 | Helper imports no LLM/embedding code; classification uses frozen-set membership and string normalization only. Verified by import-time test asserting `import groundtruth_kb.owner_decision.auto_archive` does not transitively import any LLM module. |
| SPEC-2098 | Deliberation Archive write path is preserved via `record_deliberation` reuse; no schema change. |

### Commands

```text
$env:PYTHONPATH='groundtruth-kb/src'; uv run --with pytest --with pytest-timeout --with click python -m pytest platform_tests/owner_decision/test_auto_archive.py platform_tests/hooks/test_owner_decision_tracker.py -q --tb=short
$env:PYTHONPATH='groundtruth-kb/src'; uv run --with ruff ruff check groundtruth-kb/src/groundtruth_kb/owner_decision/ platform_tests/owner_decision/
$env:PYTHONPATH='groundtruth-kb/src'; uv run --with ruff ruff format --check groundtruth-kb/src/groundtruth_kb/owner_decision/ platform_tests/owner_decision/
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-artifact-recorder-cli-slice-4-owner-decision-auto-archive
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-artifact-recorder-cli-slice-4-owner-decision-auto-archive
```

Expected: all PASS; preflight reports `missing_required_specs: []`; clause preflight exit 0; pytest passes (7 new tests + 1 added to tracker test file).

## Acceptance Criteria

- [ ] `groundtruth-kb/src/groundtruth_kb/owner_decision/__init__.py` and `auto_archive.py` exist with the public surface described in §Scope.
- [ ] `.claude/hooks/owner-decision-tracker.py` integrates the env-gated call at the resolve point; default behavior unchanged when `GTKB_AUQ_AUTO_ARCHIVE` is unset or `0`.
- [ ] `platform_tests/owner_decision/test_auto_archive.py` covers all 7 cases listed in §Scope-Tests; one additional test added to `platform_tests/hooks/test_owner_decision_tracker.py` covering the failure-log path.
- [ ] All test commands in §Test Plan-Commands PASS.
- [ ] Applicability preflight PASS; clause preflight exit 0.
- [ ] Helper module imports no LLM or embedding library; verified by the import-time test.

## Risk + Rollback

### Risk

- **Hook startup cost.** The helper imports `cli_deliberations_record` and `config` lazily inside the env-gated branch so default-off tracker invocations pay zero additional import cost.
- **Auto-archive failures could mask owner-decision visibility.** Mitigated: failures are caught, logged to `.gtkb-state/owner-decision-auto-archive/failures.jsonl`, and DO NOT block the tracker's notepad-tier write. The notepad-tier `memory/pending-owner-decisions.md` write remains the load-bearing record.
- **Out-of-scope classifier could miss new owner decision classes.** Mitigated: the frozen-set in-scope predicate is conservative (excludes only explicit acknowledgement-only short-noise content); when in doubt, the classifier defaults to archive (in-scope), so the risk is over-archive (manageable) rather than under-archive.
- **Worktree-root resolution.** The helper writes temp files under `.tmp/`; the worktree root is resolved deterministically via the same path resolver the existing `record_deliberation` service uses.

### Rollback

`git revert <commit-sha>` reverts source + tests. The env gate default-off rollout means even if the integration ships and is buggy, only sessions with `GTKB_AUQ_AUTO_ARCHIVE=1` see the bug. Tracker hook reverts to its pre-Slice-4 behavior on revert (notepad-only).

## Coupling with Other In-Flight Threads

(Refreshed against live `bridge/INDEX.md` at 2026-05-30, S373.)

- `gtkb-artifact-recorder-cli-slice-1-deliberations-record-008`: **VERIFIED**. The `record_deliberation` in-process service this Slice 4 reuses unchanged.
- `gtkb-artifact-recorder-cli-slice-2-spec-record-006`: **VERIFIED**. Adjacent service pattern; informs the in-process governed-service shape used here.
- `gtkb-artifact-recorder-cli-slice-3-scoping-005`: **VERIFIED**. `gt spec update` governed versioning; demonstrates the LO-acceptable pattern for service-style additions to the recorder family.
- `gtkb-generate-approval-packet-cli-012`: **VERIFIED**. Sibling thread covering approval-packet auto-generation; informs the approval-packet handling reused via `record_deliberation`.
- `gtkb-artifact-recorder-cli-scoping-advance-003`: **WITHDRAWN**. The S350 duplicate-of-existing-thread caught by Codex; this Slice 4 explicitly does NOT propose new CLI surface to avoid the same failure mode.

## Loyal Opposition Asks

1. Confirm the env-gated default-off rollout addresses the "behavior change" risk class without requiring an explicit owner decision-archive event before landing.
2. Confirm the `should_auto_archive` classifier's out-of-scope predicate is conservative enough (defaults to archive when in doubt).
3. Confirm the test plan's spec-to-test mapping is complete; flag any unmapped Specification Links citation.
4. Confirm the helper-imports-no-LLM assertion is testable as described; suggest an alternative if the import-time check has a known false-negative path.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
