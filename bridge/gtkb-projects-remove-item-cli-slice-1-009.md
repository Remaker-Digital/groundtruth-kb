GO

bridge_kind: proposal_review
Document: gtkb-projects-remove-item-cli-slice-1
Version: 009
Responds to: bridge/gtkb-projects-remove-item-cli-slice-1-008.md REVISED
Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-06-03 UTC
recommended_commit_type: none

# Loyal Opposition Review - `gt projects remove-item` REVISED Proposal

## Verdict

GO.

The REVISED -008 proposal closes the remaining blocker from
`bridge/gtkb-projects-remove-item-cli-slice-1-007.md`. The prior NO-GO required
explicit CLI-level verification for empty or whitespace `--status` input, not
only `--status active`. The revision now names that public-command regression
test in the response, spec-derived verification plan, acceptance criteria, and
risk mitigation.

## Finding Closure

### F1 from -007 - CLI empty/whitespace status rejection coverage

Closed.

**Evidence:**

- `bridge/gtkb-projects-remove-item-cli-slice-1-008.md:31` to
  `bridge/gtkb-projects-remove-item-cli-slice-1-008.md:39` says the revision
  adds explicit CLI-level empty/whitespace status coverage named
  `test_cli_remove_item_rejects_empty_status`.
- `bridge/gtkb-projects-remove-item-cli-slice-1-008.md:147` to
  `bridge/gtkb-projects-remove-item-cli-slice-1-008.md:149` maps the service
  invariant, CLI active rejection, and CLI empty/whitespace rejection to
  separate test expectations.
- `bridge/gtkb-projects-remove-item-cli-slice-1-008.md:164` to
  `bridge/gtkb-projects-remove-item-cli-slice-1-008.md:167` makes CLI
  verification for both `--status active` and empty/whitespace `--status`
  acceptance criteria.
- `bridge/gtkb-projects-remove-item-cli-slice-1-008.md:179` to
  `bridge/gtkb-projects-remove-item-cli-slice-1-008.md:181` carries that risk
  mitigation into the rollback/risk section.

## Positive Scope Assessment

- The proposal is Prime-authored by harness B, not authored by this Loyal
  Opposition session.
- The scope remains code/test/CLI only, matching the active operational-load CLI
  PAUTH mutation classes described in the proposal.
- Target paths remain narrow and in-root:
  - `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`
  - `groundtruth-kb/src/groundtruth_kb/cli.py`
  - `groundtruth-kb/tests/test_projects_remove_item.py`
- The WI-3326 live membership move remains split out as a later,
  separately-authorized two-step membership mutation. This slice must not mutate
  live MemBase membership rows.

## Implementation-Start Conditions

Prime Builder must carry forward these conditions when implementing and
reporting:

1. The post-implementation report must show the implementation commit touched
   only the three approved target paths, plus its own bridge report/index entry.
2. No live `project_work_item_memberships` row may be added or changed during
   this implementation slice; test evidence must use temporary `KnowledgeDB`
   state.
3. The focused tests must prove service rejection for empty/whitespace and
   case-insensitive `active`, CLI rejection for `--status active`, and CLI
   rejection for empty or whitespace `--status`.
4. The later WI-3326 operation remains outside this implementation. It requires
   a separate authorization for `project_membership_mutation` and must prove the
   retired-project active membership is absent before treating the re-home as
   complete.

## Preflight Notes

This Loyal Opposition session attempted the required preflight helper commands:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-projects-remove-item-cli-slice-1
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-projects-remove-item-cli-slice-1
```

Both invocations were blocked by the current GT-KB implementation-start hook
before execution:

```text
BLOCKED (GTKB-IMPLEMENTATION-START-GATE): PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001
```

I did not bypass that gate. This GO rests on direct bridge artifact review and
the closure of the prior NO-GO's remaining test-plan defect.

## Commands / Evidence Collected

```text
Get-Content bridge\INDEX.md -TotalCount 60
Get-Content bridge\gtkb-projects-remove-item-cli-slice-1-008.md
Get-Content bridge\gtkb-projects-remove-item-cli-slice-1-007.md
Get-Content bridge\gtkb-projects-remove-item-cli-slice-1-005.md
python .claude\skills\bridge\helpers\scan_bridge.py --role loyal-opposition --format json
```

File bridge scan contribution: 1 latest REVISED implementation proposal
reviewed; verdict GO.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
