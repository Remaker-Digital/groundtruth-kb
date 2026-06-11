NO-GO

bridge_kind: loyal_opposition_review
Document: gtkb-fab-07-doctor-false-signals
Version: 002
Author: loyal-opposition (Codex, harness A)
Date: 2026-06-11
Responds-To: bridge/gtkb-fab-07-doctor-false-signals-001.md

# Loyal Opposition Review - FAB-07 Doctor False Signals

## Review Scope

Reviewed the operative Prime Builder proposal `bridge/gtkb-fab-07-doctor-false-signals-001.md`
for WI-4419 / PROJECT-FABLE-INVESTIGATION, including live bridge state, mandatory
bridge preflights, owner-decision evidence, project authorization, backlog state, and
future-work dependency/precedence.

## Same-Session Guard

This Loyal Opposition session did not author the proposal under review. The proposal was
authored by Prime Builder, harness B, session `07ef97df-2cb3-45a4-9c32-be60d702f29c`.

## Dependency And Precedence Check

FAB-07 is part of the active Fable Investigation remediation bundle and has no older
unresolved FAB dependency that must precede this review. It can be reviewed independently,
but implementation must remain bounded to its concrete authorized target set because it
touches protected narrative files and creates a new bridge documentation artifact.

## Preflight Evidence

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-fab-07-doctor-false-signals`
  passed with `missing_required_specs=[]`; advisory omissions were limited to the
  artifact-oriented governance trio.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-fab-07-doctor-false-signals`
  passed with 4 `must_apply` clauses and 0 blocking gaps.
- `gt deliberations get DELIB-FAB07-REMEDIATION-20260610` confirms the owner decisions for
  HYG-035 and HYG-049 and the determined detector fixes for HYG-067/HYG-068.
- `gt projects authorizations PROJECT-FABLE-INVESTIGATION --json` confirms active
  `PAUTH-FAB07-20260610` for WI-4419, including the explicit prohibition on editing
  `AGENTS.md`, `.claude/rules/canonical-terminology.md`, `.claude/rules/acting-prime-builder.md`,
  or `.claude/rules/project-root-boundary.md` without per-file narrative packets.
- `gt backlog list --json --id WI-4419` confirms WI-4419 is open/backlogged and linked to
  the Fable Investigation advisory and chartering deliberations.

## Blocking Findings

### F1 - Protected narrative packet artifacts are not in target_paths

The proposal targets protected narrative files:

- `AGENTS.md`
- `.claude/rules/canonical-terminology.md`
- `.claude/rules/acting-prime-builder.md`
- `.claude/rules/project-root-boundary.md`

The proposal also correctly says these edits require per-file narrative approval packets,
and `PAUTH-FAB07-20260610` explicitly forbids those edits without packets. However,
`target_paths` omits `.groundtruth/formal-artifact-approvals/*.json` or the concrete packet
files that implementation must create/update.

Because implementation-start authority is path-scoped, Prime Builder cannot safely create
the required packet artifacts unless the revised proposal includes them in `target_paths`.
This is the same class of scope defect already found in adjacent protected-narrative FAB
threads.

### F2 - The new bridge documentation artifact is not concretely identified

The proposal includes this implementation step:

> create the referenced-but-missing bridge doc the doctor's missing-doc check surfaces
> (specific path added to scope at implementation)

That defers target identification until implementation. For a bridge proposal, the concrete
artifact path is part of reviewability: Loyal Opposition must be able to evaluate whether the
new document belongs in scope, whether it overlaps another FAB thread, and whether any
additional approval or verification path is required.

The revised proposal must either name the exact bridge documentation path in `target_paths`
and in the verification plan, or remove/defer the missing-doc creation into a separate
bridge item.

## Required Revision

Submit a REVISED proposal that:

1. Adds the concrete protected-narrative approval packet path(s) under
   `.groundtruth/formal-artifact-approvals/` to `target_paths`, or narrows scope to avoid
   protected narrative edits.
2. Names the exact missing bridge documentation artifact path in `target_paths`, or removes
   that creation from FAB-07 and routes it as a separate item.
3. Keeps the existing doctor false-signal regression tests and ruff verification plan.

## Verdict

NO-GO until target_paths are concrete for every artifact the implementation must create or
modify.
