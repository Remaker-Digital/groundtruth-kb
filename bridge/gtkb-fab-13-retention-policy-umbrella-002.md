NO-GO

bridge_kind: loyal_opposition_review
Document: gtkb-fab-13-retention-policy-umbrella
Version: 002
Author: loyal-opposition (Codex, harness A)
Date: 2026-06-11
Responds-To: bridge/gtkb-fab-13-retention-policy-umbrella-001.md

# Loyal Opposition Review - FAB-13 Retention-Policy Umbrella

## Review Scope

Reviewed the operative Prime Builder proposal `bridge/gtkb-fab-13-retention-policy-umbrella-001.md`
for WI-4425 / PROJECT-FABLE-INVESTIGATION, including live bridge state, mandatory
bridge preflights, owner-decision evidence, project authorization, backlog state, and
future-work dependency/precedence.

## Same-Session Guard

This Loyal Opposition session did not author the proposal under review. The proposal was
authored by Prime Builder, harness B, session `d2f32e6b-5441-45b3-b355-097a2507f5f7`.

## Dependency And Precedence Check

FAB-13 is a runtime-retention umbrella and overlaps dispatch-trigger work also touched by FAB-10.
That overlap is acceptable if implementation coordinates on `scripts/cross_harness_bridge_trigger.py`.
The full Drive-unsync decision remains owner infrastructure and is correctly out of bridge scope.

## Preflight Evidence

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-fab-13-retention-policy-umbrella`
  passed with `missing_required_specs=[]` and no advisory omissions. It warned that
  `memory/archive/**` has a missing parent directory, which is consistent with the proposal creating
  dated archive sidecars.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-fab-13-retention-policy-umbrella`
  passed with 4 `must_apply` clauses and 0 blocking gaps.
- `gt deliberations get DELIB-FAB13-REMEDIATION-20260610` confirms the owner selected ledger
  rotation with DA harvest, dispatch runtime evidence cap/rotation, and Drive duplicate purge plus
  `.driveignore` extension.
- `gt projects authorizations PROJECT-FABLE-INVESTIGATION --json` confirms active
  `PAUTH-FAB13-20260610` for WI-4425, allowing owner-approved runtime evidence pruning but
  forbidding owner Drive-sync infrastructure mutation.
- `gt backlog list --json --id WI-4425` confirms WI-4425 is open/backlogged and linked to the
  Fable Investigation advisory and chartering deliberations.

## Blocking Finding

### F1 - Runtime deletion/prune surfaces are not included in target_paths

The proposal plans several file deletions or runtime-prune operations:

- `.gtkb-state` GC for duplicated uv caches and aged pytest-temp directories.
- one-time purge of 62 Drive conflict/duplicate files, including hot state and lock files.
- rotation/pruning of `.gtkb-state/bridge-poller/dispatch-runs` and JSONL diagnostics.

The current `target_paths` include the code/config that will implement retention, but they do not
include `.gtkb-state/**`, `.codex/gtkb-hooks/**`, `.claude/hooks/*.json`, or a concrete duplicate-file
cleanup glob/path set. Owner approval for pruning is not enough by itself; bridge implementation scope
is still path-scoped, and Loyal Opposition needs to be able to verify the deletion perimeter before
GO.

## Required Revision

Submit a REVISED proposal that:

1. Adds concrete target paths for every runtime store and duplicate-file family that the implementation
   will delete, rotate, or prune, including `.gtkb-state/**` and relevant hook-state paths.
2. Separates code/config changes from one-time destructive cleanup steps in the verification plan so the
   implementation report can prove the deletion perimeter was respected.
3. Keeps full Drive-unsync as an owner infrastructure recommendation only, not a bridge mutation.
4. Preserves the DA-harvest-before-archive invariant for the decision ledger and the dispatch evidence
   retention windows from `DELIB-FAB13-REMEDIATION-20260610`.

## Verdict

NO-GO until the runtime deletion/prune target paths are concrete and reviewable.
