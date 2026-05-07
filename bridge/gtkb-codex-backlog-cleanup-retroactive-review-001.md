NEW

# Codex Backlog Cleanup Retroactive Review Implementation Proposal

Filed by: Prime Builder (Claude / harness B)
Date: 2026-05-06 (S333)
Bridge kind: implementation proposal
Requested bridge disposition: `GO`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` (always blocking)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (always blocking)
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (always blocking)
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (blocking)
- `GOV-STANDING-BACKLOG-001` (governance) — standing-backlog governance contract; bulk backlog operations should be visible.
- `PB-STANDING-BACKLOG-CONTINUITY-001` (protected_behavior)
- `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001` (architecture_decision)
- `DCL-STANDING-BACKLOG-SCHEMA-001` (design_constraint)
- `.claude/rules/operating-model.md` §1 — backlog reordering is interactive; bulk-retire requires visibility.
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/project-root-boundary.md`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory)

## Claim

On 2026-05-06 18:06-18:09Z (≈11:06 PT, ~3-min window prior to the
current Claude session start), `codex-backlog-cleanup` modified 119
distinct work_items in MemBase. Sample inspection shows the operation
mostly transitioned items to `lifecycle_state='resolved'` /
`resolution_status='retired'` with a uniform `change_reason`:
"Clean up unified backlog: remove obsolete/conflicting/duplicative
active items and clarify complementary work."

S333 audit could not locate:

- A bridge thread filed under `codex-backlog-cleanup` or any related name.
- A `.groundtruth/formal-artifact-approvals/*.json` packet referencing the cleanup.
- Per-item explicit owner approval evidence.

`memory/work_list.md` does mention the operation incidentally: "no formal
GOV/SPEC mutation was made in this backlog cleanup pass." That suggests
the operation was deliberate and tracked, but the audit trail is thin.

Per `GOV-STANDING-BACKLOG-001` and `.claude/rules/operating-model.md`,
backlog reordering is interactive but bulk-retire of 119 items is
arguably broader than routine reordering.

## Proposed Changes

### Change 1 — Inventory the 119 changes

Generate a CSV (or markdown table) at
`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/CODEX-BACKLOG-CLEANUP-2026-05-06-INVENTORY.md`
listing each WI's `id`, `title`, `pre-state`, `post-state`, and
`change_reason` from MemBase. Read-only; no mutation.

### Change 2 — Owner-visible review packet

Generate a review packet summarizing:

- Counts by transition (e.g., `active → retired: N`, `active → resolved: M`).
- Any items that were promoted (e.g., out of `backlogged`).
- Any items that look operationally consequential (e.g., release-blocking, security, recently-touched).
- A flag list of items that may warrant owner reconsideration.

Filed at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/CODEX-BACKLOG-CLEANUP-2026-05-06-REVIEW-PACKET.md`.

### Change 3 — Owner sign-off path

Two acceptable resolution paths, owner choice:

- **Path A (retroactive capture):** If owner confirms the cleanup was
  authorized (e.g., via prior session transcript or implicit standing-
  backlog reordering authority), insert
  `DELIB-S333-CODEX-BACKLOG-CLEANUP-RETROACTIVE-CAPTURE` with
  `source_type='owner_conversation'`, `outcome='owner_decision'`, and the
  119-item inventory linked.
- **Path B (rollback):** If owner identifies items that should not have
  been retired, prepare per-item REVERT proposals (each WI gets a new
  version flipping back to its pre-cleanup state); append-only discipline
  preserved.

Path determination requires owner AskUserQuestion at review time. This
proposal does NOT pre-determine the path; it scopes the inventory and
review-packet preparation only.

### Change 4 — Forward-fix: bulk-operation governance gap

Add to `.claude/rules/operating-model.md` §1 (or appropriate section):

"Bulk backlog operations affecting more than N work_items in a single
operation (suggested threshold: 25) should be filed as a bridge proposal
with the inventory enumerated. Routine per-item reordering remains
exempt. The intent is to prevent silent bulk transitions that bypass the
audit trail."

The threshold is configurable; LO review may adjust.

## Specification-Derived Verification

Spec-to-test mapping per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`:

| Linked specification | Test |
|---|---|
| `GOV-STANDING-BACKLOG-001` | Inventory file exists; lists all 119 WI changes from the 2026-05-06 18:06-18:09Z window. |
| `PB-STANDING-BACKLOG-CONTINUITY-001` | No items lost; the inventory + review packet make the bulk operation visible. |
| `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001` | Forward-fix rule clause added to `.claude/rules/operating-model.md`. |
| Append-only discipline | If Path B is chosen, REVERT versions are filed as new versions, not UPDATEs. |

## Acceptance Criteria

1. Inventory file exists with 119 WI rows (pre/post state and change_reason).
2. Review packet summarizes by transition type and flags potentially consequential items.
3. Owner has chosen Path A or Path B (this proposal explicitly defers the choice to LO/owner review).
4. Forward-fix rule clause added to `.claude/rules/operating-model.md`.
5. `python scripts/check_harness_parity.py --all --markdown` continues to report `PASS`.

## Risk And Rollback

- Risk: 119 reverts (Path B) could be disruptive if some items SHOULD have been retired. Mitigation: per-item review at owner level before any revert; bulk-revert is not authorized by this proposal.
- Risk: Forward-fix rule clause could mistake a legitimate bulk operation for a violation. Mitigation: threshold is configurable; LO review may adjust; the rule is informational/governance, not a blocking gate.
- Rollback: Path A capture is append-only DELIB; rollback is documenting reversal. Path B reverts are per-item with their own audit trail. Rule clause is text-only edit; revert is trivial.

## Owner Decisions / Input

- Owner directive S333: "I believe these are all acceptable. Do not defer anything." — authorizes the inventory + review-packet scope.
- Owner directive S333: "I give you pre-approval to make changes wherever required in order for you to complete this review." — authorizes inventory generation.
- The Path A vs Path B choice is explicitly DEFERRED to a subsequent owner AskUserQuestion at review time, because the choice depends on owner-side knowledge of the cleanup's authorization that the audit could not derive from artifacts alone.
- No new owner approval requested by this proposal beyond standard Loyal Opposition `GO`/`NO-GO` on the inventory + review-packet preparation scope.

## Pre-Filing Preflight Subsection

Per `.claude/rules/file-bridge-protocol.md`:

1. Triggered specs in `config/governance/spec-applicability.toml` — all cited above.
2. KB-search — `GOV-STANDING-BACKLOG-001` and family directly govern; cited.
3. Bridge-governance specs — cited.
4. Preflight to be run after INDEX entry filed.
5. `packet_hash` recorded after preflight.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
