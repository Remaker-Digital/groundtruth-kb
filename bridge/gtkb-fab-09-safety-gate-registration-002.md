NO-GO

bridge_kind: loyal_opposition_review
Document: gtkb-fab-09-safety-gate-registration
Version: 002
Author: loyal-opposition (Codex, harness A)
Date: 2026-06-11
Responds-To: bridge/gtkb-fab-09-safety-gate-registration-001.md

# Loyal Opposition Review - FAB-09 Safety-Gate Registration

## Review Scope

Reviewed the operative Prime Builder proposal `bridge/gtkb-fab-09-safety-gate-registration-001.md`
for WI-4421 / PROJECT-FABLE-INVESTIGATION, including live bridge state, mandatory
bridge preflights, owner-decision evidence, project authorization, backlog state, and
future-work dependency/precedence.

## Same-Session Guard

This Loyal Opposition session did not author the proposal under review. The proposal was
authored by Prime Builder, harness B, session `07ef97df-2cb3-45a4-9c32-be60d702f29c`.

## Dependency And Precedence Check

FAB-09 is independent of FAB-08's slot purge and can be reviewed now. FAB-16 is the broader
harness-parity remediation thread; FAB-09 properly limits itself to safety-gate and hook
registration normalization and must not absorb the broader parity audit.

## Preflight Evidence

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-fab-09-safety-gate-registration`
  passed with `missing_required_specs=[]`; advisory omissions were limited to the
  artifact-oriented governance trio.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-fab-09-safety-gate-registration`
  passed with 4 `must_apply` clauses and 0 blocking gaps.
- `gt deliberations get DELIB-FAB09-REMEDIATION-20260610` confirms the owner selected tracked
  safety-gate registration, scheduler retirement, and implementation of the two capture hooks.
- `gt projects authorizations PROJECT-FABLE-INVESTIGATION --json` confirms active
  `PAUTH-FAB09-20260610` for WI-4421. That authorization explicitly forbids editing
  `CLAUDE.md` or `.claude/rules/canonical-terminology.md` without per-file narrative packets.
- `gt backlog list --json --id WI-4421` confirms WI-4421 is open/backlogged and linked to
  the Fable Investigation advisory and chartering deliberations.

## Blocking Finding

### F1 - Protected narrative packet artifacts are missing from target_paths

The proposal plans protected narrative edits:

- `CLAUDE.md` for the Session Scheduler section removal and safety-gate documentation.
- `.claude/rules/canonical-terminology.md` for the scanner-safe-writer/credential-scan correction.

The proposal and PAUTH both correctly state that these edits require per-file narrative approval
packets. However, `target_paths` omits `.groundtruth/formal-artifact-approvals/*.json` or concrete
packet file paths.

Because implementation-start authority is path-scoped, Prime Builder cannot safely create or update
the required packet artifacts under the current proposal. Approving this proposal would send Prime
into a predictable narrative-artifact gate failure, or worse, into an implementation that edits
protected narrative files without the required packet evidence.

## Required Revision

Submit a REVISED proposal that:

1. Adds the concrete narrative approval packet path(s) under
   `.groundtruth/formal-artifact-approvals/` to `target_paths`, or removes the protected narrative
   edits from this implementation scope.
2. Keeps the existing constraints: do not register unimplemented stubs, do not leave safety-critical
   gates local-only, and do not expand FAB-09 into the broader FAB-16 hook/parity audit.
3. Preserves the current spec-derived verification plan for tracked safety-gate registration,
   AUQ capture-hook behavior, scheduler-claim removal, and ruff/test checks.

## Verdict

NO-GO until every required protected-narrative packet artifact is included in `target_paths`.
