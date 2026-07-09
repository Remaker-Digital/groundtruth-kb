WITHDRAWN

# Duplicate Withdrawal - WI-4870 retired-project PAUTH GO-thread quarantine

bridge_kind: operational_state_change
Document: gtkb-wi4870-retired-project-pauth-go-quarantine
Version: 002
Date: 2026-07-06 UTC
Responds-To: `bridge/gtkb-wi4870-retired-project-pauth-go-quarantine-001.md`

## Disposition

Prime Builder withdraws this later WI-4870 proposal because it duplicates the
older live `NEW` thread `bridge/gtkb-wi4870-auto-retire-stranded-go-pauth-001.md`.
The older thread remains the canonical review target for WI-4870.

This withdrawal does not retire WI-4870, does not supersede the Harness Parity
Phase 2 PAUTH, and does not mutate project, work-item, source, test, or
configuration state. It closes only the duplicate bridge thread
`gtkb-wi4870-retired-project-pauth-go-quarantine` so Loyal Opposition has a
single actionable WI-4870 review target.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - `WITHDRAWN` is an accepted bridge status and the numbered bridge file chain remains the audit trail.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this notice cites the governing bridge authority for the lifecycle closure.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - this notice includes a spec-derived verification table for the withdrawal action.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the active Phase 2 PAUTH is preserved on the older WI-4870 proposal.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - no implementation proceeds from this withdrawal.

## Duplicate Evidence

- `bridge/gtkb-wi4870-auto-retire-stranded-go-pauth-001.md` is the older live `NEW` proposal for WI-4870 and covers the retired-project PAUTH / stranded GO-thread failure.
- `bridge/gtkb-wi4870-retired-project-pauth-go-quarantine-001.md` is a later overlapping `NEW` proposal for the same work item.
- `gt bridge threads --wi WI-4870 --json --compact` reported both threads as latest `NEW` before this withdrawal.

## Owner Decisions / Input

No new owner decision is required. This is an append-only duplicate cleanup that
preserves the older live WI-4870 proposal and removes no artifact from the audit
trail.

## Specification-Derived Verification

| Specification / rule | Verification evidence | Observed result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | File this notice as `bridge/gtkb-wi4870-retired-project-pauth-go-quarantine-002.md` through the governed helper path. | Prior `-001` remains preserved; latest state for this duplicate thread becomes `WITHDRAWN`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run `python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-propose-drafts/gtkb-wi4870-retired-project-pauth-go-quarantine-002.md --json` before publication. | Expected clean required-spec result for a withdrawal notice. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Confirm `gt bridge threads --wi WI-4870 --json --compact` after publication. | Older WI-4870 implementation proposal remains live for LO review. |

## Recommended Commit Type

`docs`
