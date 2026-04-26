NO-GO

# Codex Review - ADR-ISOLATION-APPLICATION-PLACEMENT Governance Proposal

**Date:** 2026-04-26
**Reviewed proposal:** `bridge/gtkb-adr-isolation-application-placement-001.md`
**Decision:** NO-GO

## Claim

The proposed ADR content and Phase 9 supersession mechanism are directionally acceptable, but the proposal cannot be approved as written because its implementation order requires a single atomic commit spanning two independent Git repositories.

## Blocking Finding

### 1. Single-commit execution plan crosses repository boundaries

The proposal's implementation order says:

- "Atomic change set (one commit, multiple file changes)"
- insert the ADR upstream in `groundtruth-kb`
- annotate the Agent Red local Phase 9 plan
- file an Agent Red bridge revision
- update Agent Red `bridge/INDEX.md`
- make a "Single commit with scoped message capturing all four mechanical actions"

Live repository checks show these are not one repository:

- `E:\GT-KB` resolves to Git top-level `E:/GT-KB`
- `E:\GT-KB` remote is `https://github.com/Remaker-Digital/agent-red-customer-engagement.git`
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb` resolves to Git top-level `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb`
- `groundtruth-kb` remote is `https://github.com/Remaker-Digital/groundtruth-kb.git`

Because the ADR insertion belongs in upstream `groundtruth-kb` while the Phase 9 plan annotation, bridge revision, and `bridge/INDEX.md` update belong in Agent Red, the proposed "single commit" is mechanically impossible as a Git operation.

## Evidence

- `bridge/gtkb-adr-isolation-application-placement-001.md` section 5 proposes one atomic commit containing upstream ADR insertion plus Agent Red local artifacts.
- `git -C E:\GT-KB rev-parse --show-toplevel` returned `E:/GT-KB`.
- `git -C E:\GT-KB remote -v` returned `origin https://github.com/Remaker-Digital/agent-red-customer-engagement.git`.
- `git -C E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb rev-parse --show-toplevel` returned `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb`.
- `git -C E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb remote -v` returned `origin https://github.com/Remaker-Digital/groundtruth-kb.git`.
- The Phase 9 plan contradiction is real: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` lines 93-99 state that `gt project init` creates an application root that is not a subdirectory of the GT-KB product root.

## Impact

Approving the proposal as written would authorize an execution plan that cannot be completed faithfully. It would also blur audit boundaries between the upstream platform repository and the Agent Red adopter repository, which matters because the ADR is a formal upstream artifact while the bridge and Phase 9 annotations are local adopter/governance artifacts.

## Recommended Action

Revise section 5 to use coordinated cross-repo sequencing instead of a single atomic commit. A reviewable shape would be:

1. In upstream `groundtruth-kb`, insert and commit `ADR-ISOLATION-APPLICATION-PLACEMENT-001` with its formal approval packet.
2. In Agent Red, annotate the Phase 9 plan with a `SUPERSEDED-BY` notice citing the upstream ADR commit or artifact ID.
3. In Agent Red, file the ISOLATION-016 `-013` revision citing the upstream ADR.
4. In Agent Red, update `bridge/INDEX.md`.
5. Record the upstream commit hash or durable ADR reference in the Agent Red bridge revision so the cross-repo dependency is auditable.

## Non-Blocking Notes

- The ADR decision text in section 2 is adequate for the owner-directed Option B path.
- The proposed strikethrough plus `SUPERSEDED-BY` annotation at the exact Phase 9 paragraph is the right local supersession mechanism.
- Keeping the prior Phase 9 plan-review bridge thread VERIFIED is acceptable because the later ADR would supersede a specific plan assumption rather than retroactively changing the original review result.
- The ISOLATION-016 `-013` reconciliation should remain blocked until the upstream ADR exists or the revised bridge filing explicitly treats it as a pending dependency.

## Decision Needed From Owner

None from Mike for this review. Prime Builder needs to revise the implementation order so it matches the actual repository boundaries.

