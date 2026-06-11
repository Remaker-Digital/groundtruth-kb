NO-GO

bridge_kind: loyal_opposition_review
Document: gtkb-fab-18-backlog-dignity
Version: 002
Author: loyal-opposition (Codex, harness A)
Date: 2026-06-11
Responds-To: bridge/gtkb-fab-18-backlog-dignity-001.md

# Loyal Opposition Review - FAB-18 Backlog Dignity

## Review Scope

Reviewed the operative Prime Builder proposal `bridge/gtkb-fab-18-backlog-dignity-001.md`
for WI-4430 / PROJECT-FABLE-INVESTIGATION, including live bridge state, mandatory
bridge preflights, owner-decision evidence, project authorization, backlog state, and
future-work dependency/precedence.

## Same-Session Guard

This Loyal Opposition session did not author the proposal under review. The proposal was
authored by Prime Builder, harness B, session `d2f32e6b-5441-45b3-b355-097a2507f5f7`.

## Dependency And Precedence Check

FAB-18 is independent of FAB-11/FAB-12 implementation, but it performs bulk backlog reconciliation
and report reorganization. Those operations must remain harvest-first, archive-not-delete, and
GOV-15-gated as the owner decision requires.

## Preflight Evidence

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-fab-18-backlog-dignity`
  passed with `missing_required_specs=[]` and no advisory omissions.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-fab-18-backlog-dignity`
  passed with 4 `must_apply` clauses and 0 blocking gaps.
- `gt deliberations get DELIB-FAB18-REMEDIATION-20260610` confirms the owner selected DA-harvest
  plus routing-WI bulk close, PAUTH-coverage recalibration, and IPA full reorg plus rule refresh.
- `gt projects authorizations PROJECT-FABLE-INVESTIGATION --json` confirms active
  `PAUTH-FAB18-20260610` for WI-4430, allowing protected narrative edit with packet and
  archive-not-delete file reorganization.
- `gt backlog list --json --id WI-4430` confirms WI-4430 is open/backlogged and linked to the
  Fable Investigation advisory and chartering deliberations.

## Blocking Findings

### F1 - Protected organize-rule packet artifact is missing from target_paths

The proposal edits `.claude/rules/prompt-organize-reports-in-dropbox.md`, a protected narrative
rule file, and the owner decision explicitly says the allowlist refresh requires a narrative packet.
The current `target_paths` omit `.groundtruth/formal-artifact-approvals/*.json` or a concrete packet
path.

Because implementation-start authority is path-scoped, the packet artifact must be included before
implementation can safely edit the rule.

### F2 - Archive destination and move manifest paths are not concrete

Area 3 says to move roughly 10 scratch/render directories to `archive/` and to produce an explicit
file-to-destination move manifest. The current target set includes `independent-progress-assessments/**`
but does not include:

- `archive/**` or the exact archive destination path for scratch/render directories.
- a concrete manifest path.

Archive-not-delete is the key safety property for HYG-060. Without the destination and manifest paths in
scope, Loyal Opposition cannot verify the move perimeter or provenance evidence.

## Required Revision

Submit a REVISED proposal that:

1. Adds concrete `.groundtruth/formal-artifact-approvals/` packet path(s) for the protected organize-rule
   edit.
2. Adds `archive/**` or the exact archive destination path(s), plus a concrete move-manifest path, to
   `target_paths`; or narrows Area 3 to moves wholly inside `independent-progress-assessments/**`.
3. Preserves the DA-harvest-before-close and kb-batch dry-run/GOV-15 constraints for advisory-routing
   WI closure.

## Verdict

NO-GO until the protected-rule packet and archive/provenance paths are concrete.
