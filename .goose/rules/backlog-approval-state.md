<!--
THIS FILE IS A PROJECTION, NOT CANONICAL.
Projected from the neutral harness baseline by the GT-KB projection engine.
Do not edit here: change the baseline (.harness-baseline-configuration) and re-project with
`gt harness project goose`. If a needed change cannot be made through
the baseline and re-projection, file a work item against the projector
(GOV-HARNESS-NEUTRAL-BASELINE-001 obligation 6).
-->
# Backlog Approval State Retirement Rule

## Purpose

MemBase work-item `approval_state` is historical compatibility metadata only.
It is not implementation authority, review authority, startup priority authority,
or a text-edit bypass.

## Canonical Authority

Implementation authority is project-level:

1. The work item's single parent project has `activation-status: authorized`.
2. A live bridge `GO` approves the specific implementation proposal.
3. A matching live work-intent claim opens the Prime Builder write path.

Individual work items do not have an approval state. A work item may be
tracked, prioritized, reviewed, or linked to its parent project without becoming
an independent approval authority. It inherits authorization from that project.

## Legacy Data

Historical rows may still carry legacy `approval_state` values. Tools may read
or preserve those values for backward compatibility and audit continuity, but
must not derive authorization, priority, or permission from them.

Do not backfill, promote, or transition `approval_state` as a governance step.
Do not introduce new directives, skills, helper behavior, tests, or startup
surfaces that treat a work-item approval state as live authority.

## Enforcement

Any live gate that accepts or rejects implementation based on `approval_state`
is obsolete and must be replaced by the parent project's `activation-status`,
bridge `GO`, and live work-intent claim.
