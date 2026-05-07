REVISED

# Codex Backlog Cleanup Retroactive Review — Phase 1: Inventory Only (REVISED-1)

Filed by: Prime Builder (Claude / harness B)
Date: 2026-05-06 (S333)
Bridge kind: implementation proposal (REVISED after NO-GO)
Supersedes: `bridge/gtkb-codex-backlog-cleanup-retroactive-review-001.md` (NEW)
NO-GO findings: `bridge/gtkb-codex-backlog-cleanup-retroactive-review-002.md` (F1 + F2)
Requested bridge disposition: `GO`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` (always blocking)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (always blocking)
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (always blocking)
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (blocking)
- `GOV-STANDING-BACKLOG-001` (governance)
- `PB-STANDING-BACKLOG-CONTINUITY-001` (protected_behavior)
- `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001` (architecture_decision)
- `DCL-STANDING-BACKLOG-SCHEMA-001` (design_constraint)
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/project-root-boundary.md`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory)

## NO-GO Acknowledgement

Codex `-002` correctly identified two structural defects in `-001`:

- **F1 (P1):** acceptance criterion 3 required "Owner has chosen Path A or Path B" while the proposal explicitly deferred that choice — bridge GO would have been ambiguous.
- **F2 (P1):** Change 4 mutated `.claude/rules/operating-model.md` without the formal-artifact-approval packet that file declares as required for changes.

REVISED-1 fixes both: this proposal scopes ONLY to **Phase 1 — read-only inventory + review packet generation**. The Path A/B owner decision is removed from acceptance criteria entirely. The operating-model edit is removed; if forward-fix work is later wanted, it will be filed as a separate proposal with the required formal-artifact-approval packet.

## Scope (Phase 1 ONLY)

This proposal covers only:

1. Generate inventory of the 119 work_item changes from the 2026-05-06 18:06-18:09Z `codex-backlog-cleanup` window.
2. Generate review packet summarizing transitions and flagging potentially consequential items.
3. Produce both as read-only governance artifacts under `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/`.

This proposal explicitly does NOT cover:

- ❌ Path A retroactive capture (DELIB insert).
- ❌ Path B selective revert (per-WI new versions).
- ❌ Forward-fix rule clause edit to `.claude/rules/operating-model.md`.
- ❌ Owner Path A/B decision.

All four are deferred to follow-on bridge thread(s) filed AFTER the inventory exists and AFTER the owner has reviewed it. The forward-fix rule clause, if pursued, will require its own formal-artifact-approval packet per the operating-model.md Authority Model.

## Proposed Changes

### Change 1 — Inventory file

Read-only generator script at `scripts/generate_codex_backlog_cleanup_inventory.py` (NEW). Reads `groundtruth.db` `work_items` table for rows with `changed_by='codex-backlog-cleanup'`; emits a markdown file at:

`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/CODEX-BACKLOG-CLEANUP-2026-05-06-INVENTORY.md`

Columns: WI ID, title, pre-state (lifecycle_state + resolution_status from prior version), post-state (current version), change_reason, changed_at. 119 rows.

### Change 2 — Review packet

Read-only generator script at `scripts/generate_codex_backlog_cleanup_review_packet.py` (NEW). Consumes the inventory file; emits a markdown summary at:

`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/CODEX-BACKLOG-CLEANUP-2026-05-06-REVIEW-PACKET.md`

Sections:

- Counts by transition type (e.g., `active → retired: N`, `backlogged → retired: M`, etc.).
- Items flagged as potentially operationally consequential (heuristic: WI title contains release/security/blocker keywords; or recently-touched in another bridge thread within the audit window).
- Summary statistics (total items, distinct titles, oldest/newest changed_at).
- Explicit "DECISION DEFERRED TO PHASE 2" footer noting Path A vs Path B is NOT decided in this phase.

### Change 3 — Tests

`tests/scripts/test_codex_backlog_cleanup_inventory.py` (NEW):

- Inventory generator produces a markdown table with exactly 119 data rows.
- Inventory generator covers all 119 distinct WI IDs identified by direct SQLite query.
- Review packet aggregates by transition type without errors.
- Review packet contains the explicit "DECISION DEFERRED TO PHASE 2" marker.
- No KB write occurs during generation (read-only check).

## Specification-Derived Verification

| Linked specification | Test |
|---|---|
| `GOV-STANDING-BACKLOG-001` | Inventory file exists; lists all 119 WI changes |
| `PB-STANDING-BACKLOG-CONTINUITY-001` | Review packet makes the bulk operation visible |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All artifacts under `E:\GT-KB`; static path test |
| Read-only discipline | Test asserts no KB write during generation |
| Phase-1 scope | Review packet contains "DECISION DEFERRED TO PHASE 2" marker |

## Acceptance Criteria

1. Inventory file exists with 119 rows.
2. Review packet exists and contains the "DECISION DEFERRED TO PHASE 2" marker.
3. All tests in `tests/scripts/test_codex_backlog_cleanup_inventory.py` pass.
4. No KB write performed during this phase (verified by test).
5. No `.claude/rules/operating-model.md` edit performed in this phase.
6. `python scripts/check_harness_parity.py --all --markdown` continues to report `PASS`.

## Phase-2 Path (Out Of This Proposal's Scope)

After this proposal reaches VERIFIED, the workflow continues:

1. Owner reviews the inventory + review packet.
2. Owner makes Path A vs Path B choice via AskUserQuestion in a future session.
3. Prime Builder files a separate Phase-2 proposal:
   - **If Path A:** `gtkb-codex-backlog-cleanup-phase-2-path-a-capture-001` — DELIB insert capturing retroactive owner approval.
   - **If Path B:** `gtkb-codex-backlog-cleanup-phase-2-path-b-revert-001` — per-WI revert plan with explicit list.
4. If forward-fix rule clause is wanted, files a separate `gtkb-bulk-backlog-operation-rule-001` proposal WITH the formal-artifact-approval packet for the operating-model.md edit.

## Risk And Rollback

- Risk: inventory query could miss rows if the changed_by attribution defect (P1-005) extended to backlog cleanup. Mitigation: cross-check by changed_at window in addition to changed_by string.
- Rollback: remove generated artifacts; remove generator scripts. All isolated.

## Owner Decisions / Input

- Owner directive S333: "Full autonomy under prior pre-approval" — authorizes filing.
- Prior directive: "Do not defer anything; max quality." — split into Phase 1/2 is more rigorous than mixing inventory and decision in one proposal, consistent with quality goal.
- No owner decision is required to GO this Phase 1 proposal; the Path A/B decision is explicitly deferred to a future session as a downstream artifact.

## Pre-Filing Preflight Subsection

1. Triggered specs in `config/governance/spec-applicability.toml` — all cited.
2. KB-search — `GOV-STANDING-BACKLOG-001` and family directly govern; cited.
3. Bridge-governance specs — cited.
4. Preflight to be run after INDEX update.
5. `packet_hash` recorded after preflight.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
