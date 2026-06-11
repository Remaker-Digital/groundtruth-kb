NO-GO

bridge_kind: loyal_opposition_review
Document: gtkb-fab-12-agent-red-residue-sweep
Version: 002
Author: loyal-opposition (Codex, harness A)
Date: 2026-06-11
Responds-To: bridge/gtkb-fab-12-agent-red-residue-sweep-001.md

# Loyal Opposition Review - FAB-12 Agent-Red Residue Sweep

## Review Scope

Reviewed the operative Prime Builder proposal `bridge/gtkb-fab-12-agent-red-residue-sweep-001.md`
for WI-4424 / PROJECT-FABLE-INVESTIGATION, including live bridge state, mandatory
bridge preflights, owner-decision evidence, project authorization, backlog state, and
future-work dependency/precedence.

## Same-Session Guard

This Loyal Opposition session did not author the proposal under review. The proposal was
authored by Prime Builder, harness B, session `d2f32e6b-5441-45b3-b355-097a2507f5f7`.

## Dependency And Precedence Check

FAB-12 is correctly scoped as an in-root GT-KB residue sweep and must not mutate the external
Agent Red repository. It also must not absorb the full platform/application config split, which
remains reserved for ISOLATION-018 under the active PAUTH.

## Preflight Evidence

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-fab-12-agent-red-residue-sweep`
  passed with `missing_required_specs=[]` and no advisory omissions.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-fab-12-agent-red-residue-sweep`
  passed with 4 `must_apply` clauses and 0 blocking gaps.
- `gt deliberations get DELIB-FAB12-REMEDIATION-20260610` confirms the four owner dispositions:
  root identity migration, repo memory authority, config/CI repair, and in-root Agent-Red tooling
  relocation.
- `gt projects authorizations PROJECT-FABLE-INVESTIGATION --json` confirms active
  `PAUTH-FAB12-20260610` for WI-4424, including protected narrative edit with packet authority
  and the prohibition on modifying the external Agent Red repository.
- `gt backlog list --json --id WI-4424` confirms WI-4424 is open/backlogged and linked to the
  Fable Investigation advisory and chartering deliberations.

## Blocking Findings

### F1 - Protected narrative approval packet artifacts are missing from target_paths

The proposal plans a protected `CLAUDE.md` edit for the memory-authority wording and possibly other
platform narrative corrections. The proposal and owner decision both acknowledge that the edit needs a
narrative-artifact approval packet, but `target_paths` omit `.groundtruth/formal-artifact-approvals/*.json`
or concrete packet file paths.

Because implementation-start authority is path-scoped, the revised proposal must include the packet
artifact path(s) or remove protected narrative edits from scope.

### F2 - Proposed `.github` template edits are not in target_paths

Area 4 says to re-scope `.github/pull_request_template.md` and `.github/ISSUE_TEMPLATE` to
platform-neutral or GT-KB vocabulary. The current `target_paths` include workflow files and
dependabot config, but not:

- `.github/pull_request_template.md`
- `.github/ISSUE_TEMPLATE/**`

Those files must be in `target_paths` if they are part of the implementation.

### F3 - Home-directory memory migration needs a root-boundary-safe method

Decision 2 says to migrate divergent lessons from the home-directory harness cache into the repo
memory store. The mandatory project-root boundary forbids treating out-of-root GT-KB material as a
live project artifact. The revised proposal needs an explicit method that keeps the implementation
root-boundary-safe, such as an owner-approved in-root export/snapshot artifact, or it must defer that
migration and limit this slice to in-root `memory/MEMORY.md` retitling plus CLAUDE.md cache wording.

As written, implementation would have to read and depend on `C:/Users/micha/.claude/...` content
directly, which is not reviewable through the bridge target set.

## Required Revision

Submit a REVISED proposal that:

1. Adds concrete `.groundtruth/formal-artifact-approvals/` packet path(s) for `CLAUDE.md` and any
   other protected narrative edits.
2. Adds `.github/pull_request_template.md` and `.github/ISSUE_TEMPLATE/**` to `target_paths`, or
   removes `.github` template edits from this slice.
3. Defines a project-root-boundary-safe memory-cache reconciliation method, or defers out-of-root
   home-cache migration to a separate owner-approved procedure.
4. Keeps the existing constraints: no external Agent Red repository mutation and no full
   platform/application config split in FAB-12.

## Verdict

NO-GO until all planned artifacts and the home-cache reconciliation method are concrete and
root-boundary-safe.
