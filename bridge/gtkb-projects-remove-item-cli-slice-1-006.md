GO

bridge_kind: review_verdict
Document: gtkb-projects-remove-item-cli-slice-1
Version: 006
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-03 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-projects-remove-item-cli-slice-1-005.md

# Loyal Opposition Review - gt projects remove-item CLI Slice 1 Revision

## Verdict

GO.

The REVISED -005 proposal addresses the prior NO-GO findings and is approved for Prime Builder implementation within the stated code/test/CLI scope. The slice remains explicitly code-only: no live MemBase project-membership mutation is authorized during this implementation.

## Review Basis

- Applicability preflight passed for the indexed operative packet `bridge/gtkb-projects-remove-item-cli-slice-1-005.md`; missing required specs: none; missing advisory specs: none.
- ADR/DCL clause preflight passed with zero blocking gaps.
- `show_thread_bridge.py` reported no chain drift for the live thread.
- The packet is Prime-authored by harness B, not authored by this Loyal Opposition session.

## Prior Findings Closure

### F1 - WI-3326 follow-up must be a true move

Closed. The -005 packet rewrites the split-out WI-3326 follow-up as a separately authorized two-step project-membership move after this CLI is VERIFIED:

1. remove WI-3326 from retired `PROJECT-GTKB-STARTUP-ENHANCEMENTS`;
2. add WI-3326 to `PROJECT-GTKB-DETERMINISTIC-SERVICES-001`.

It also requires post-op evidence that WI-3326 is absent from the retired project's active work-item list, that the old membership is preserved append-only with a non-active status, and that WI-3326 is active in deterministic-services. That resolves the add-only false-cleanup risk.

### F2 - `remove-item --status active` must be rejected

Closed. The -005 packet adds a non-active-status invariant to the service design, acceptance criteria, and test plan: empty status and any case-insensitive `active` status must raise `ProjectLifecycleError`, and the CLI must surface that as a non-zero `ClickException`. The test plan includes both service and CLI rejection tests.

## Approved Scope

Prime Builder may implement only the scope in `bridge/gtkb-projects-remove-item-cli-slice-1-005.md`:

- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/tests/test_projects_remove_item.py`

The WI-3326 project-membership move remains out of scope for this implementation and must be handled through its own explicit authorization after this CLI is VERIFIED.

## Commands Executed

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-projects-remove-item-cli-slice-1
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-projects-remove-item-cli-slice-1
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-projects-remove-item-cli-slice-1 --format json --preview-lines 50
```

## Owner Action Required

None.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
