# Backlog Approval State Retirement Rule

## Purpose

Work-item `approval_state` is retired. It grants and denies nothing and is not
an implementation, review, priority or permission predicate.

## Canonical Authority

The current execution-project row has one field named `authorization`, with
value `authorized` or `not authorized`. The owner's direction sets work
ordering through `gt projects set-authorization`; authorization is distinct
from activation. Programs have no authorization value. The standing intake
project is permanently `not authorized`.

Each work item has exactly one execution-project parent. Owner dispatch is
sufficient direction for the assigned bridge action. Immediately before a NEW
proposal, check that current parent's authorization. A later authorization
change does not invalidate an already initiated chain.

Dispatched implementation still needs its current formal specification, scoped
proposal, independent Loyal Opposition GO, linked executable test and test-plan
phase, and matching claim for the next bridge action. These are review,
evidence and concurrency requirements; they do not create authorization.
Claiming an action gives no ownership of a work item or chain.

Individual work items do not have an approval state. A work item may be
tracked, prioritized, reviewed, or linked to its parent project without becoming
an independent approval authority. It inherits authorization from that project.

## Legacy Data

Historical material may mention `approval_state`. Preserve formal history;
do not retain or recreate a runtime compatibility dependency on the retired
field. Historical labels establish neither current membership nor Git
terminality.

Do not backfill, promote, or transition `approval_state` as a governance step.
Do not introduce new directives, skills, helper behavior, tests, or startup
surfaces that treat a work-item approval state as live authority.

## Enforcement

Any live gate that accepts or rejects work based on `approval_state` is
defective. Correct it at the appropriate native domain or bridge boundary.
Do not replace it with an authorization check on every action: project
authorization is checked for NEW proposals, while initiated chains continue
under their current review and claim requirements.

Source: `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`.
