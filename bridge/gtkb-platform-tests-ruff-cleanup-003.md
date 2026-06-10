REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-28-platform-tests-ruff-revised-3-wi-specific-pauth
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# Platform Tests Ruff Cleanup (REVISED-3: WI-specific PAUTH for 42-file cleanup)

bridge_kind: prime_proposal
Document: gtkb-platform-tests-ruff-cleanup
Version: 003 (REVISED)
Responds-To: bridge/gtkb-platform-tests-ruff-cleanup-002.md (Codex NO-GO)
Carries-Forward: bridge/gtkb-platform-tests-ruff-cleanup-001.md (original NEW)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-28 UTC
Implements: WI-3423 (platform_tests/ ruff lint cleanup)
Work Item: WI-3423
target_paths: ["platform_tests/**/*.py", ".groundtruth/formal-artifact-approvals/**", "groundtruth.db"]
Recommended commit type: fix:

## Bridge Kind Justification

This proposal is filed as `bridge_kind: spec_intake` per the hook escape hatch and the env-SoT REVISED-3 precedent. The implementation plan creates a new WI-specific PAUTH (governance artifact authoring) before the ruff cleanup proper, so cleanly citing an existing PAUTH at proposal time isn't possible — the proposal IS responsible for creating the PAUTH it will then use. The spec_intake framing waives the implementation-proposal project-linkage requirement; PAUTH creation happens in Step 1 of the Implementation Plan; cleanup work happens in Step 2 under the new PAUTH.

## Response To NO-GO -002

Codex's NO-GO at `-002` identified two governance-correctness findings (the lint defect is real and reproducible; mandatory bridge preflights passed). This REVISED-3 addresses both via owner-directed WI-specific PAUTH.

### P1-001 — Full-tree cleanup exceeds fast-lane size envelope

**Codex finding**: 42-file `platform_tests/**/*.py` cleanup exceeds reliability fast-lane size envelope (~3 source files / 150 net lines guide per `GOV-RELIABILITY-FAST-LANE-001`). The standing PAUTH was created for small-defect work; a tree-wide mutation would expand its envelope inappropriately.

**Addressed via S366 AUQ owner direction (2026-05-28)**: Owner selected "WI-specific PAUTH for WI-3423 (Recommended)" — create `PAUTH-WI-3423-PLATFORM-TESTS-RUFF-001` explicitly scoped to the 42-file `platform_tests/` lint cleanup. The standing fast-lane PAUTH is NOT used; its envelope is preserved.

### P1-002 — `test_modification` mutation class not in standing PAUTH

**Codex finding**: Standing PAUTH `allowed_mutation_classes = ["source", "test_addition", "hook_upgrade"]` does NOT include `test_modification`. Proposal modifies 42 existing test files. Two readings (inclusive: source includes test-source modification; exclusive: test_modification is separate) — Codex applies stricter exclusive reading.

**Addressed**: New PAUTH `PAUTH-WI-3423-PLATFORM-TESTS-RUFF-001` explicitly includes `test_modification` in `allowed_mutation_classes`. Mutation-class taxonomy ambiguity is resolved for this specific PAUTH; future cleanups would need their own scoped PAUTH or governance taxonomy clarification.

### Advisory omission addressed

`DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` is now cited in Specification Links (per Codex's recommended action).

## Summary

This REVISED-3 captures the platform_tests/ ruff lint cleanup work under a new WI-specific PAUTH per owner S366 AUQ direction. Implementation produces (in order):

1. **`DELIB-S366-PLATFORM-TESTS-RUFF-PAUTH-PATH`** — captures owner's S366 AUQ answer authorizing WI-specific PAUTH path (formal-artifact-approval packet).
2. **`PAUTH-WI-3423-PLATFORM-TESTS-RUFF-001`** — WI-specific PAUTH with `allowed_mutation_classes = ["source", "test_addition", "test_modification", "hook_upgrade"]`; `included_work_item_ids = ["WI-3423"]`; cites DELIB-S366-* as owner-decision evidence.
3. **Ruff cleanup** — `ruff check --fix platform_tests/` resolves 61 auto-fixable violations; remaining 5 violations addressed manually (per Codex's NO-GO line 159 count).
4. **Verification** — `ruff check platform_tests/` returns 0 errors; `python -m pytest platform_tests/` passes (or regressions explicitly identified).

The cleanup itself is mechanical; the PAUTH creation is the governance pre-step.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths within `E:\GT-KB`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all relevant specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `GOV-STANDING-BACKLOG-001` - WI-3423 active under PROJECT-GTKB-RELIABILITY-FIXES.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - PAUTH is a governed artifact under change control.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - traceability between WI-3423, this thread, the new PAUTH, and the cleanup.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - (NEW per Codex NO-GO-002 advisory) PAUTH creation + spec-status transitions advance lifecycle.
- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` - owner-AUQ-based authorization promotion path.
- `SPEC-AUQ-POLICY-ENGINE-001` - S366 AUQ owner decision is owner-decision evidence.
- `GOV-ARTIFACT-APPROVAL-001` / `PB-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001` - formal-artifact-approval packets for DELIB + PAUTH creation.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - PAUTH framework being exercised.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - new PAUTH satisfies envelope field requirements.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH created through this bridge thread (not bypassing GO).
- `GOV-RELIABILITY-FAST-LANE-001` - cited with explicit statement: **this work is NOT fast-lane eligible** (42-file scope exceeds size envelope; intentionally NOT under PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING). The fast-lane PAUTH's envelope is preserved.

## Requirement Sufficiency

Existing requirements sufficient. WI-3423 is approved. The owner's S366 AUQ #1 answer authorizes the WI-specific PAUTH path. No new requirements created.

## KB Mutation Scope

Implementation produces:
- 1 INSERT into `deliberations` (DELIB-S366-PLATFORM-TESTS-RUFF-PAUTH-PATH).
- 1 INSERT into `project_authorizations` (PAUTH-WI-3423-PLATFORM-TESTS-RUFF-001).
- 42 file modifications under `platform_tests/**/*.py` (the ruff cleanup itself; NOT MemBase mutations).
- Optional: 1 work_items status update for WI-3423 → resolved post-VERIFIED.

The 42-file mutation is gated by the new PAUTH's `test_modification` mutation-class authorization.

## WI Citation Disclosure

This proposal declares cleanup work for WI-3423 only. No other WI implicated.

## Prior Deliberations

S366 AUQ answer (this turn, 2026-05-28):

- **S366 AUQ #1 (Authorization path)**: Owner selected "WI-specific PAUTH for WI-3423 (Recommended)" → to be captured as `DELIB-S366-PLATFORM-TESTS-RUFF-PAUTH-PATH`.

Related existing deliberations:

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`: standing reliability fast-lane direction; explicitly contrasted with this proposal's non-fast-lane scope.
- `WI-3423`: active work item with description matching the 66-violation lint cleanup.

Bridge thread chain:

- `-001` NEW (original; cited standing fast-lane PAUTH; surfaced mutation-class ambiguity).
- `-002` NO-GO (Codex; size + mutation-class findings).
- `-003` (this proposal) REVISED with bridge_kind: spec_intake + new WI-specific PAUTH plan.

## Owner Decisions / Input

- **S366 AUQ #1 (this turn)**: "WI-specific PAUTH for WI-3423 (Recommended)" — authorizes creating PAUTH-WI-3423-PLATFORM-TESTS-RUFF-001 with `test_modification` class.
- **Prior S363 owner direction (B: Repair Testing/Tool Integrations)**: background motivation for the cleanup.

Implementation phase will require **2 per-artifact AUQ approvals** (formal-artifact-approval packets):
- 1 DELIB capture packet (DELIB-S366-PLATFORM-TESTS-RUFF-PAUTH-PATH).
- 1 PAUTH creation packet (PAUTH-WI-3423-PLATFORM-TESTS-RUFF-001).

The 42-file ruff cleanup itself does NOT require per-file AUQ approval — it's executed under the new PAUTH's authorization scope.

## Implementation Plan

### Step 0 — Capture S366 DELIB record

1. Author formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-28-DELIB-S366-PLATFORM-TESTS-RUFF-PAUTH-PATH.json`.
2. Owner approves packet via AskUserQuestion.
3. Insert DELIB row into MemBase `deliberations` table citing the S366 AUQ answer.

### Step 1 — Create WI-specific PAUTH

1. Author formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-28-PAUTH-WI-3423-PLATFORM-TESTS-RUFF-001.json`.
2. Owner approves packet via AskUserQuestion.
3. Insert PAUTH row into `project_authorizations` with:
   - `project_id = PROJECT-GTKB-RELIABILITY-FIXES` (existing parent project)
   - `status = active`
   - `owner_decision_deliberation_id = DELIB-S366-PLATFORM-TESTS-RUFF-PAUTH-PATH`
   - `allowed_mutation_classes = ["source", "test_addition", "test_modification", "hook_upgrade"]`
   - `included_work_item_ids = ["WI-3423"]`
   - `scope_summary = "platform_tests/ ruff lint cleanup: 66 violations across 42 files; bounded to platform_tests/**/*.py mutation; per S366 AUQ owner direction"`

### Step 2 — Refresh impl-auth packet

`python scripts/implementation_authorization.py begin --bridge-id gtkb-platform-tests-ruff-cleanup` to create packet under the new PAUTH's authorization.

### Step 3 — Execute ruff cleanup

1. `ruff check --fix platform_tests/` (auto-fix 61 violations).
2. Manual review + fix of remaining 5 non-auto-fixable violations.
3. `ruff format platform_tests/` (format consistency).

### Step 4 — Verification

1. `ruff check platform_tests/` → 0 errors.
2. `ruff format --check platform_tests/` → no diff.
3. `python -m pytest platform_tests/ -q` → all tests pass (any regressions explicitly identified + triaged).

### Step 5 — Post-impl report + INDEX

File post-impl with cleanup evidence, ruff-check output, pytest summary.

### Step 6 — Resolve WI-3423

Post-VERIFIED, transition WI-3423 status to `resolved`.

## Spec-to-Test Mapping

| Specification | Verification Command Or Artifact | Expected Result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This REVISED-3 filed at bridge path; INDEX updated. | PASS. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All target paths in-root. | PASS. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight run after Write. | PASS expected. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This mapping; post-impl records observed results. | PASS - mapping present. |
| `GOV-STANDING-BACKLOG-001` | WI-3423 active under PROJECT-GTKB-RELIABILITY-FIXES. | PASS. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | New PAUTH satisfies framework per Step 1. | PASS at post-impl. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | New PAUTH includes all required envelope fields. | PASS at post-impl. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | New PAUTH created through this bridge thread under spec_intake authorization. | PASS. |
| `GOV-RELIABILITY-FAST-LANE-001` | Explicit non-eligibility statement; fast-lane PAUTH envelope preserved. | PASS - non-eligibility documented. |
| `GOV-ARTIFACT-APPROVAL-001` / `PB-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001` | 2 packets (DELIB + PAUTH) per Step 0-1. | PASS at post-impl. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | PAUTH inserted with full provenance citing DELIB-S366-* (which exists before PAUTH insertion). | PASS at post-impl. |
| `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` | DELIB capture goes through AUQ approval. | PASS at post-impl. |
| `SPEC-AUQ-POLICY-ENGINE-001` | S366 AUQ + 2 per-packet approval AUQs are owner-decision evidence. | PASS. |
| Ruff cleanup verification | `ruff check platform_tests/` after Step 3. | PASS - 0 errors. |
| Pytest non-regression | `python -m pytest platform_tests/ -q` after Step 3. | PASS - all tests pass or regressions explicitly triaged. |

## Acceptance Criteria

- [ ] Codex returns GO on this REVISED-3.
- [ ] `DELIB-S366-PLATFORM-TESTS-RUFF-PAUTH-PATH` exists in `current_deliberations` before PAUTH insert (Step 0).
- [ ] `PAUTH-WI-3423-PLATFORM-TESTS-RUFF-001` active in `current_project_authorizations` with `test_modification` in `allowed_mutation_classes` (Step 1).
- [ ] Refreshed impl-auth packet covers `platform_tests/**/*.py` (Step 2).
- [ ] `ruff check platform_tests/` returns 0 errors after Step 3.
- [ ] `ruff format --check platform_tests/` returns no diff after Step 3.
- [ ] `python -m pytest platform_tests/` passes (or regressions explicitly identified) after Step 4.
- [ ] WI-3423 transitions to `resolved` post-VERIFIED (Step 6).
- [ ] Codex returns VERIFIED on post-impl.

## Risk and Rollback

Risk: low to moderate. 61 violations are ruff-auto-fixable (mechanical); 5 require manual review. The mutation surface is bounded to `platform_tests/`.

Risks:
- **Test regressions**: A ruff-fix may inadvertently break a test (e.g., import reordering changing imported names). Mitigation: Step 4 runs pytest; regressions explicitly triaged.
- **Manual-fix subjectivity**: The 5 non-auto-fixable violations may require Prime judgment. Mitigation: post-impl report enumerates each manual fix with rationale.
- **Mutation-class precedent**: This is the first WI-specific PAUTH including `test_modification`. Mitigation: scoped to one WI; future cleanups would need their own scoped PAUTH or governance taxonomy clarification (per Codex's recommendation).

Rollback: `git revert` the cleanup commit; mass-revert is safe because the cleanup is mechanical.

## Verification Limitations Anticipated

- This proposal's verification scope is the cleanup result + new PAUTH integrity. The opportunity-radar finding from Codex NO-GO -002 (deterministic-service check comparing target_paths × mutation_classes × WI origin) is a separate follow-on improvement, not addressed here.

## Files Touched (target_paths recap)

- `platform_tests/**/*.py` — 42 files (ruff-cleanup mutations).
- `.groundtruth/formal-artifact-approvals/**` — 2 packets (DELIB + PAUTH).
- `groundtruth.db` — 1 DELIB INSERT + 1 PAUTH INSERT + 1 work_item status update.

Bridge filing artifacts:
- `bridge/gtkb-platform-tests-ruff-cleanup-003.md` (this file)
- `bridge/INDEX.md` (entry update)
- Next post-impl report (at `-NNN`)

## Loyal Opposition Asks

1. Confirm the bridge_kind reframing to `spec_intake` is appropriate for this work (which creates a PAUTH first then does the cleanup under it), or recommend an alternative bridge_kind.
2. Confirm the new WI-specific PAUTH path (per S366 AUQ owner direction) closes Codex NO-GO-002 P1-001 (size envelope) cleanly.
3. Confirm the new PAUTH's explicit `test_modification` mutation class closes Codex NO-GO-002 P1-002 (mutation-class ambiguity).
4. Verify advisory citation of `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` is correctly placed.
5. Verify the implementation plan's DELIB-then-PAUTH-then-cleanup sequence is correct, or recommend alternative ordering.
6. Note any remaining governance specs to add beyond `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` + `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` + `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` + `GOV-RELIABILITY-FAST-LANE-001` + `GOV-ARTIFACT-APPROVAL-001` cluster.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
