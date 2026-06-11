GO

bridge_kind: loyal_opposition_review
Document: gtkb-fab-08-slot-leak-fix
Version: 002
Author: loyal-opposition (Codex, harness A)
Date: 2026-06-11
Responds-To: bridge/gtkb-fab-08-slot-leak-fix-001.md

# Loyal Opposition Review - FAB-08 Slot Leak Fix

## Review Scope

Reviewed the operative Prime Builder proposal `bridge/gtkb-fab-08-slot-leak-fix-001.md`
for WI-4420 / PROJECT-FABLE-INVESTIGATION, including live bridge state, mandatory
bridge preflights, owner-decision evidence, project authorization, backlog state, and
future-work dependency/precedence.

## Same-Session Guard

This Loyal Opposition session did not author the proposal under review. The proposal was
authored by Prime Builder, harness B, session `07ef97df-2cb3-45a4-9c32-be60d702f29c`.

## Dependency And Precedence Check

FAB-08 is the correct predecessor to the separate Agent_Red `application.toml` backfill:
`DELIB-FAB08-REMEDIATION-20260610` explicitly routes HYG-022 to a later Agent-Red-scoped
bridge after the `_test_*` purge clears the doctor noise. No later FAB item should absorb
the slot-leak purge before this proposal lands.

## Preflight Evidence

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-fab-08-slot-leak-fix`
  passed with `missing_required_specs=[]`; the advisory omissions were limited to the
  artifact-oriented governance trio. The `applications/_test_*/**` parent-dir warning is a
  glob-shape warning, not a scope blocker: live `_test_*` directories exist under
  `applications/`.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-fab-08-slot-leak-fix`
  passed with 3 `must_apply` clauses and 0 blocking gaps.
- `gt deliberations get DELIB-FAB08-REMEDIATION-20260610` confirms the owner selected
  fix + purge + doctor auto-clean for HYG-053, and deferred HYG-022 to a separate
  Agent-Red-scoped bridge.
- `gt projects authorizations PROJECT-FABLE-INVESTIGATION --json` confirms active
  `PAUTH-FAB08-20260610` for WI-4420, allowing source/test/file-deletion/config changes
  and forbidding deletion of non-`_test_*` application slots, real application relocation,
  and Agent_Red `application.toml` backfill in this thread.
- `gt backlog list --json --id WI-4420` confirms WI-4420 is open/backlogged and linked to
  the Fable Investigation advisory and chartering deliberations.

## Review Notes

The proposal states the observed leak count as 229, matching the source investigation. A live
workspace count during this review found 234 `applications/_test_*` directories, which supports
the proposal's claim that the leak is active. This is not a blocker because the target scope is
pattern-bounded to `applications/_test_*/**`; the implementation report should record the live
count it purged and must not delete any non-`_test_*` application slot.

## Implementation Constraints

- Keep HYG-022 out of this implementation. Agent_Red `application.toml` backfill remains a
  separate Agent-Red-scoped bridge item.
- Delete only `applications/_test_*` skeletons. Do not relocate or delete real application
  subtrees.
- Preserve the verification intent that `_force_rmtree` still fails loudly enough in tests to
  prevent future silent cleanup failures.
- The implementation report must state the actual live `_test_*` count purged, because the
  count is no longer exactly the investigation's 229.

## Verdict

GO for implementation within the proposal's scoped paths and the constraints above.
